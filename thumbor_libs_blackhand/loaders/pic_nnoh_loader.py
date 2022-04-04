#!/usr/bin/python
# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/

# OFFLINE

#from thumbor.loaders import file_loader, http_loader
from thumbor.loaders import http_loader
from thumbor_ftvnum_libs.loaders import pic_nn_loader
from tornado.concurrent import return_future


@return_future
def load(context, path, callback):
    if (path.find('http') != -1):
      http_loader.load(context, path, callback)
    else:
      pic_nn_loader.load(context, path, callback)

