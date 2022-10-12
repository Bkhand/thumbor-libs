# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/
import re
import gridfs
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta
from io import StringIO
from thumbor.storages import BaseStorage
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi



class Storage(BaseStorage):

    def __conn__(self):
        server_api = ServerApi('1', strict=True)       
        client = MongoClient(self.context.config.MONGO_STORAGE_URI, server_api=server_api)        
        db = client[self.context.config.MONGO_STORAGE_DB]
        storage = db[self.context.config.MONGO_STORAGE_COLLECTION]
        return db, storage

    async def put(self, path, file_bytes):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        doc = {
            'path': tpath,
            'created_at': datetime.utcnow()
        }
        doc_with_crypto = dict(doc)
        if self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            if not self.context.server.security_key:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
            doc_with_crypto['crypto'] = self.context.server.security_key
        fs = gridfs.GridFS(db)
        file_data = fs.put(file_bytes, **doc)
        doc_with_crypto['file_id'] = file_data
        db.storage.insert_one(doc_with_crypto)
        return  tpath

    async def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            pass
        tpath = self.truepath(path)
        db, storage = self.__conn__()
        pasplit = path.split("/")
        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
        crypto = storage.find_one({'path': tpath})
        crypto['crypto'] = self.context.server.security_key
        db.storage.update({'path': tpath}, crypto)
        return pasplit[0]

    async def put_detector_data(self, path, data):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        pasplit = path.split("/")
        db.storage.update({'path': tpath}, {"$set": {"detector_data": data}})
        return pasplit[0]

    def truepath(self, path):
        pasplit = path.split("/")       
        if  pasplit[0]:
            pasplitf = re.search('^[a-z0-9A-Z]+', pasplit[0]).group(0)
            return  pasplitf
        else:
            return False

    def get_crypto(self, path):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        crypto = db.storage.find_one({'path': tpath})
        if crypto:
            return crypto.get('crypto')
        else:
            return None

    async def get_detector_data(self, path):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        doc = db.storage.find_one({'path': tpath})
        if doc:
            return doc.get('detector_data')
        else:
            return None

    async def get(self, path):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        stored = db.storage.find_one({'path': tpath})
        if not stored:
            return None
        # if self.__is_expired(stored):
            #self.remove(path)
        #    return None
        fs = gridfs.GridFS(db)
        contents = fs.get(stored['file_id']).read()
        return bytes(contents)

    async def exists(self, path):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        #stored = db.storage.find_one({'path': tpath})
        if tpath:
            stored = db.storage.find_one({'path': tpath})
            if not stored or self.__is_expired(stored):
                return False
            else:
                return True 
        else:
            return False

    def remove(self, path):
        db, storage = self.__conn__()
        tpath = self.truepath(path)
        if not self.exists(tpath):
            pass
        fs = gridfs.GridFS(db)
        stored = db.storage.find_one({'path': tpath})
        try:
            fs.delete(stored['file_id'])
            db.storage.remove({'path': tpath })
        except:
            pass

    def __is_expired(self, stored):
        timediff = datetime.utcnow() - stored.get('created_at')
        return timediff > timedelta(seconds=self.context.config.STORAGE_EXPIRATION_SECONDS)
