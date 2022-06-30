#!/usr/bin/python
# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the GNU/GPL license:
# https://fsf.org/

from os import fstat
from datetime import datetime
from os.path import join, exists, abspath
from six.moves.urllib.parse import unquote
from tornado.concurrent import return_future
from thumbor.loaders import LoaderResult
from thumbor.utils import logger


async def load(context, path):
    file_path = join(
        context.config.PIC_LOADER_ROOT_PATH.rstrip('/'), path.lstrip('/'))
    file_path = abspath(file_path)
    file_path_two = join(
        context.config.PIC_LOADER_FALLBACK_PATH.rstrip('/'), path.lstrip('/'))
    file_path_two = abspath(file_path_two)
    inside_root_path = file_path.startswith(
        abspath(context.config.PIC_LOADER_ROOT_PATH))
    inside_root_path_two = file_path_two.startswith(
        abspath(context.config.PIC_LOADER_FALLBACK_PATH))
    result = LoaderResult()

    if not inside_root_path:
        if not inside_root_path_two:
          result.error = LoaderResult.ERROR_NOT_FOUND
          result.successful = False
          return result
        pass

    if not exists(file_path):
        file_path = unquote(file_path)

    if not exists(file_path_two):
        file_path_two = unquote(file_path_two)

    if exists(file_path):
        with open(file_path, 'r') as f:
            stats = fstat(f.fileno())
            
            if stats.st_size <= 4:
                logger.warning(u"%s: cette image source est vide...", file_path)
                result.successful = False
                result.error = LoaderResult.ERROR_UPSTREAM
            else:
                result.successful = True
                result.buffer = f.read()

                result.metadata.update(
                    size=stats.st_size,
                    updated_at=datetime.utcfromtimestamp(stats.st_mtime))
    
    elif exists(file_path_two):
         with open(file_path_two, 'r') as f:
            stats = fstat(f.fileno())
            
            if stats.st_size <= 4:
                logger.warning(u"%s: cette image source est vide...", file_path_two)
                result.successful = False
                result.error = LoaderResult.ERROR_UPSTREAM
            else:
                result.successful = True
                result.buffer = f.read()

                result.metadata.update(
                    size=stats.st_size,
                    updated_at=datetime.utcfromtimestamp(stats.st_mtime))
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False

    return result
