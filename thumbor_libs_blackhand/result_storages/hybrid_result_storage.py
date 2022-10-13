# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# libvips

from  urllib import request, parse, error
from motor.motor_tornado import MotorGridFSBucket
from pymongo.errors import PyMongoError
from thumbor_libs_blackhand.mongodb.pool_result_storage import MongoConnector
from datetime import datetime, timedelta
from thumbor.result_storages import BaseStorage, ResultStorageResult
from thumbor.engines import BaseEngine
from thumbor.utils import logger
from bson.binary import Binary
from uuid import uuid4
import pytz
import re
import os


class Storage(BaseStorage):

    def __init__(self, context):
        BaseStorage.__init__(self, context)
        self.database, self.storage = self.__conn__()
        super(Storage, self).__init__(context)


    def __conn__(self):
        '''Return the MongoDB params.
        :returns: MongoDB DB and Collection
        :rtype: pymongo.database.Database, pymongo.database.Collection
        '''

        password = parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_PASSWORD)
        user = parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_USER)
        if not self.context.config.MONGO_RESULT_STORAGE_SERVER_REPLICASET:
          uri = ('mongodb://'+ user +':' + password + '@' + self.context.config.MONGO_RESULT_STORAGE_SERVER_HOSTS
                  + '/?authSource=' + self.context.config.MONGO_RESULT_STORAGE_SERVER_DB)
        else:
          uri = ('mongodb://'+ user +':' + password + '@' + self.context.config.MONGO_RESULT_STORAGE_SERVER_HOSTS
                  + '/?authSource=' + self.context.config.MONGO_RESULT_STORAGE_SERVER_DB
                  + "&replicaSet=" + self.context.config.MONGO_RESULT_STORAGE_SERVER_REPLICASET
                  + "&readPreference=" + self.context.config.MONGO_RESULT_STORAGE_SERVER_READ_PREFERENCE)

        db_name = self.context.config.MONGO_RESULT_STORAGE_SERVER_DB
        col_name = self.context.config.MONGO_RESULT_STORAGE_SERVER_COLLECTION
        password = parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_PASSWORD)
        user = parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_USER)
        host = None
        port = None
        try:
            uri = self.context.config.MONGO_RESULT_STORAGE_URI
        except AttributeError:
            pass

        try:
            host = self.context.config.MONGO_RESULT_STORAGE_SERVER_HOST
            port = self.context.config.MONGO_RESULT_STORAGE_SERVER_PORT
        except AttributeError:
            pass

        mongo_conn = MongoConnector(
            db_name=db_name,
            col_name=col_name,
            uri=uri,
            host=host,
            port=port,
        )

        database = mongo_conn.db_conn
        storage = mongo_conn.col_conn

        return database, storage


    @property
    def is_auto_webp(self):
        return self.context.config.AUTO_WEBP and self.context.request.accepts_webp

    @property
    def is_auto_webp(self):
        '''Return if webp.
        :return: If the file is a webp
        :rettype: boolean
        '''

        return self.context.config.AUTO_WEBP \
            and self.context.request.accepts_webp

    def get_key_from_request(self):
        '''Return a path key for the current request url.
        :return: The storage key for the current url
        :rettype: string
        '''

        path = f"result:{self.context.request.url}"

        if self.is_auto_webp:
            return f'{path}/webp'

        return path


    def get_max_age(self):

        return self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS

    async def put(self, image_bytes):
        #db, storage = self.__conn__()
        key = self.get_key_from_request()
        max_age = self.get_max_age()
        result_ttl = self.get_max_age()
        CACHE_PATH = self.context.config.CACHE_PATH
        mkpath = (CACHE_PATH + '/' + datetime.now().strftime('%Y') + '/' 
                  + datetime.now().strftime('%m') + '/' + datetime.now().strftime('%d') 
                  + '/' + datetime.now().strftime('%H'))
        self.ensure_dir(mkpath)

        #os.makedirs(mkpath)
        ref_img = ''
        ref_img = re.findall(r'/[a-zA-Z0-9]{24}(?:$|/)', key)
        if ref_img:
            ref_img2 = ref_img[0].replace('/','')
        else:
            ref_img2 = 'undef'


        if self.context.config.get("MONGO_STORE_METADATA", False):
            metadata = dict(self.context.headers)
        else:
            metadata = {}

        cache_id = str(uuid4())
        endingpath= mkpath + "/" + cache_id
        doc = {
            'path': key,
            'created_at': datetime.utcnow(),
            'data': "",
            'metadata': metadata,
            'content_type': BaseEngine.get_mimetype(image_bytes),
            'ref_id': ref_img2,
            'content_length' : len(image_bytes),
            'cache_path': mkpath,
            'cache_id' : cache_id
            }
        doc_cpm = dict(doc)

        fichier = open(endingpath, "wb")
        fichier.write(Binary(image_bytes))
        fichier.close()

        await self.storage.insert_one(doc_cpm)
        #return self.context.request.url
        return key


    async def get(self):

        key = self.get_key_from_request()
        logger.debug("[RESULT_STORAGE] image not found at %s", key)
 
        try:
            cache_path = self.context.config.CACHE_PATH
        except AttributeError:
            raise

        age = datetime.utcnow() - timedelta(
            seconds=self.get_max_age()
        )
        stored = await self.storage.find_one({
            'path': key,
            'created_at': {
                '$gte': age
            },
        }, {
            'ref_id': True,
            'created_at': True,
            'metadata': True,
            'content_type': True,
            'data' : True,
            'content_length': True,
            'cache_path' : True,
            'cache_id' : True,
        })


        if not stored:
            return None
        metadata = stored['metadata']
        metadata['LastModified'] = stored['created_at'].replace(
            tzinfo=pytz.utc
        )
        metadata['Cache-Control'] = "max-age=60,public"
        metadata['ContentLength'] = stored['content_length']
        metadata['ContentType'] = stored['content_type']
        cachefile = stored['cache_path'] + "/" + stored['cache_id']

        fichier = open(cachefile, "rb")
        tosend = fichier.read()
        fichier.close()

        return ResultStorageResult(
            buffer=tosend,
            metadata=metadata,
            successful=True
        )
