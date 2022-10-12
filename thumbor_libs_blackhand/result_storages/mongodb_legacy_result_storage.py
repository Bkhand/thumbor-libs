# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
import bson
import time
import urllib.request, urllib.parse, urllib.error
import re
from datetime import datetime, timedelta
from io import StringIO
from thumbor.result_storages import BaseStorage
from thumbor.utils import logger
from bson.binary import Binary
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sys import getsizeof


class Storage(BaseStorage):
    @property
    def is_auto_webp(self):
        return self.context.config.AUTO_WEBP and self.context.request.accepts_webp


    def __conn__(self):
        #server_api = ServerApi('1', strict=True)
        #client = MongoClient(self.context.config.MONGO_RESULT_STORAGE_URI) #, server_api=server_api)
        #db = client[self.context.config.MONGO_RESULT_STORAGE_SERVER_DB]
        #storage = self.context.config.MONGO_RESULT_STORAGE_SERVER_COLLECTION
        #return db, storage

        password = urllib.parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_PASSWORD)
        user = urllib.parse.quote_plus(self.context.config.MONGO_RESULT_STORAGE_SERVER_USER)
        if not self.context.config.MONGO_RESULT_STORAGE_SERVER_REPLICASET:
          uri = 'mongodb://'+ user +':' + password + '@' + self.context.config.MONGO_RESULT_STORAGE_SERVER_HOST + '/?authSource=' + self.context.config.MONGO_RESULT_STORAGE_SERVER_DB
        else:
          uri = 'mongodb://'+ user +':' + password + '@' + self.context.config.MONGO_RESULT_STORAGE_SERVER_HOST + '/?authSource=' + self.context.config.MONGO_RESULT_STORAGE_SERVER_DB + "&replicaSet=" + self.context.config.MONGO_RESULT_STORAGE_SERVER_REPLICASET + "&readPreference=" + self.context.config.MONGO_RESULT_STORAGE_SERVER_READ_PREFERENCE
        client = MongoClient(uri)
        db = client[self.context.config.MONGO_RESULT_STORAGE_SERVER_DB]
        storage = self.context.config.MONGO_RESULT_STORAGE_SERVER_COLLECTION
        return db, storage


    def get_max_age(self):
        default_ttl = self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
        if self.context.request.max_age == 0:
            return self.context.request.max_age
        return default_ttl


    def get_key_from_request(self):
        path = "result:%s" % self.context.request.url
        return path


    async def put(self, image_bytes):
        db, storage = self.__conn__()
        key = self.get_key_from_request()
        max_age = self.get_max_age()
        result_ttl = self.get_max_age()
        ref_img = ''
        ref_img = re.findall(r'/[a-zA-Z0-9]{24}(?:$|/)', key)
        if ref_img:
            ref_img2 = ref_img[0].replace('/','')
        else:
            ref_img2 = 'undef'

        if self.is_auto_webp:
            content_t = 'webp'
        else:
            content_t = 'default'
        doc = {
            'path': key,
            'created_at': datetime.utcnow(),
            'data': Binary(image_bytes),
            'content-type': content_t,
            'ref_id': ref_img2
            }
        doc_cpm = dict(doc)

        try:
            self.context.config.MONGO_RESULT_STORAGE_MAXCACHESIZE
            maxs = self.context.config.MONGO_RESULT_STORAGE_MAXCACHESIZE
        except:
            maxs = 16000000

        amd = getsizeof(bytes)
        if  amd > maxs:
            logger.warning(u"OVERSIZE %s: %s > %s pas de mise en cache possible", key, amd, maxs)
            return None
        else:
            db[storage].insert_one(doc_cpm)
            return key

        #if result_ttl > 0:
        #        ref = datetime.utcnow() + timedelta(
        #            seconds=result_ttl
        #        )
        #        doc_cpm['expire'] = ref
        #db[storage].insert_one(doc_cpm)
        #return key


    async def get(self):
        db, storage = self.__conn__()
        key = self.get_key_from_request()
        logger.debug("[RESULT_STORAGE] image not found at %s", key)

        #if self.is_auto_webp:
        #    result = db.storage.find_one({'path': key }) #, 'content-type': "webp"})
        #else:
        result = db[storage].find_one({'path': key }) #, 'content-type': "default"})

        if not result:
            return None
        tosend = result['data']
        return tosend
