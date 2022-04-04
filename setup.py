#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licensed under the GNU/GPL license:
# https://fsf.org/

from distutils.core import setup

setup(
    name = "thumbor-libs",
    version = "0.0.1",
    description = "libs thumbor",
    author = "Bertrand Thill",
    author_email = "github@blackhand.org",
    keywords = ["thumbor", "fallback", "images", "nfs", "mongodb"],
    license = 'MIT',
    url = 'https://github.com/Bkhand/thumbor-libs',
    packages=[
        'thumbor-_libs',
        'thumbor-libs.loaders',
        'thumbor-libs.url_signers',
        'thumbor-libs.metrics',
        'thumbor-libs.storages',
        'thumbor-libs.result_storages'
    ],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    package_dir = {"thumbor-libs": "thumbor-libs"},
    install_requires=['thumbor>=7.0.7','pymongo>=3.11.3'],
    long_description = """\
This module test support for file.
"""
)