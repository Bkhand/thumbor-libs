#!/usr/bin/python
# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/

# OFFLINE

import urllib
from thumbor.loaders import http_loader
from thumbor_ftvnum_libs.loaders import pic_nn_loader
from tornado.concurrent import return_future
from thumbor.loaders import LoaderResult

@return_future
def load(context, path, callback):
    def callback_wrapper(result):
        if result.successful:
            callback(result)
        else:
            # If file_loader failed try http_loader
            if (path.find('http') != -1):
                http_loader.load(context, path, callback)
            else:
                result = LoaderResult()
                result.error = LoaderResult.ERROR_NOT_FOUND
                result.successful = False
                callback(result)

    # First attempt to load with file_loader
    pic_nn_loader.load(context, path, callback_wrapper)
