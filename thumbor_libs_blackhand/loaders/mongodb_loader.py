#!/usr/bin/python
# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/

# OFFLINE MITIG-

from bson.objectid import ObjectId
import gridfs
import urllib
from thumbor.loaders import LoaderResult
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def __conn__(self):

    uri = urllib.parse.quote_plus(self.context.config.MONGO_ORIGIN_URI)
    server_api = ServerApi('1', strict=True)
    client = MongoClient(self.context.config.MONGO_ORIGIN_URI, server_api=server_api)        
    db = client[sself.config.MONGO_ORIGIN_SERVER_DB]
    return db

async def load(context, path):
    db = __conn__(context)
    words2 = path.split("/")
    storage = context.config.MONGO_ORIGIN_SERVER_COLLECTION
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
