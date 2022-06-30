# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/
import bson
import re
import time
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta
from io import StringIO
from thumbor.result_storages import BaseStorage
from thumbor.utils import logger
from bson.binary import Binary
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class Storage(BaseStorage):
    @property
    def is_auto_webp(self):
        return self.context.config.AUTO_WEBP and self.context.request.accepts_webp


    def __conn__(self):
        server_api = ServerApi('1', strict=True)
        client = MongoClient(self.context.config.MONGO_RESULT_STORAGE_URI, server_api=server_api)        
        db = client[self.context.config.MONGO_RESULT_STORAGE_SERVER_DB]
        storage = db[self.context.config.MONGO_RESULT_STORAGE_SERVER_COLLECTION]
        return client, db, storage


    def get_max_age(self):
        default_ttl = self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
        if self.context.request.max_age == 0:
            return self.context.request.max_age
        return default_ttl


    def get_key_from_request(self):
        path = "result:%s" % self.context.request.url
        return path


    async def put(self, image_bytes):
        connection, db, storage = self.__conn__()
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
        if result_ttl > 0:
                ref = datetime.utcnow() + timedelta(
                    seconds=result_ttl
                )
                doc_cpm['expire'] = ref
        storage.insert_one(doc_cpm)
        return key


    async def get(self):
        connection, db, storage = self.__conn__()
        key = self.get_key_from_request()
        logger.debug("[RESULT_STORAGE] image not found at %s", key)
        
        if self.is_auto_webp:
            result = storage.find_one({"path": key, "content-type": "webp"})
        else:
            result = storage.find_one({"path": key, "content-type": "default"})
        
        if not result:
            return None
        
        if result and  await self.__is_expired(result):
            ttl = result.get('path')
            await self.remove(ttl)
            return None
        tosend = result['data']        
        return tosend


    async def remove(self, path):
        connection, db, storage = self.__conn__()
        if self.is_auto_webp:
            try:
                storage.remove({'path': path, "content-type": "webp"})
            except:
                pass
        else:
            try:
                storage.remove({'path': path, "content-type": "default"})
            except:
                pass


    async def __is_expired(self, result):
        timediff = datetime.utcnow() - result.get('created_at')
        return timediff > timedelta(seconds=self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS)
        '''future => db.log_events.createIndex( { "createdAt": 1 }, { expireAfterSeconds: 3600 } )
        db.runCommand( { collMod: <collection or view>, <option1>: <value1>, <option2>: <value2> ... } )
        {keyPattern: <index_spec> || name: <index_name>, expireAfterSeconds: <seconds> }
        {getParameter:1, expireAfterSeconds: 1}
        '''
