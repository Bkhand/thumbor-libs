#!/usr/bin/python
# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/


from pymongo import MongoClient
from bson.objectid import ObjectId
from thumbor.loaders import LoaderResult
import gridfs
import urllib.request, urllib.parse, urllib.error
#from thumbor.utils import logger

def __conn__(self):
    #server_api = ServerApi('1', strict=True)
    client = MongoClient(self.config.MONGO_ORIGIN_URI)
    #client = MongoClient(server_api=server_api)
    db = client[self.config.MONGO_ORIGIN_SERVER_DB]
    storage = self.config.MONGO_ORIGIN_SERVER_COLLECTION
    return client, db, storage


async def load(context, path):
    client, db, storage = __conn__(context)
    words2 = path.split("/")
    images = gridfs.GridFS(db, collection=storage)
    result = LoaderResult()
    if ObjectId.is_valid(words2[0]):
        if images.exists(ObjectId(words2[0])):
            contents = images.get(ObjectId(words2[0])).read()
            result.successful = True
            result.buffer = contents
        else:
            result.error = LoaderResult.ERROR_NOT_FOUND
            result.successful = False
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False
    return result
