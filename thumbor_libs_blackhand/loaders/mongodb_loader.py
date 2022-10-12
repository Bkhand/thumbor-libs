# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from thumbor.loaders import LoaderResult
import gridfs
import urllib.request, urllib.parse, urllib.error


def __conn__(self):
    #server_api_mode = ServerApi('1', strict=True)
    #client = MongoClient(self.config.MONGO_ORIGIN_URI)  #,server_api=server_api_mode)
    #db = client[self.config.MONGO_ORIGIN_SERVER_DB]
    #storage = self.config.MONGO_ORIGIN_SERVER_COLLECTION
    #return db, storage


    if urllib.parse.quote_plus(self.config.MONGO_ORIGIN_SERVER_USER):
        password = urllib.parse.quote_plus(self.config.MONGO_ORIGIN_SERVER_PASSWORD)
        user = urllib.parse.quote_plus(self.config.MONGO_ORIGIN_SERVER_USER)
        uri = 'mongodb://'+ user +':' + password + '@' + self.config.MONGO_ORIGIN_SERVER_HOST + '/?authSource=' + self.config.MONGO_ORIGIN_SERVER_DB
    else:
        uri = 'mongodb://'+ self.config.MONGO_ORIGIN_SERVER_HOST
    client = MongoClient(uri)  #,server_api=server_api_mode)
    db = client[self.config.MONGO_ORIGIN_SERVER_DB]
    storage = self.config.MONGO_ORIGIN_SERVER_COLLECTION
    return db, storage


async def load(context, path):
    db, storage = __conn__(context)
    correctPath = path.split("/")
    images = gridfs.GridFS(db, collection=storage)
    result = LoaderResult()
    if ObjectId.is_valid(correctPath[0]):
        if images.exists(ObjectId(correctPath[0])):
            contents = images.get(ObjectId(correctPath[0])).read()
            result.successful = True
            result.buffer = contents
        else:
            result.error = LoaderResult.ERROR_NOT_FOUND
            result.successful = False
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
    return result
