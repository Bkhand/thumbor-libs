#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licensed under the GNU/GPL license:
# https://fsf.org/

from distutils.core import setup

setup(
    name = "thumbor_libs_blackhand",
    version = "0.1.1",
    description = "libs thumbor",
    author = "Bertrand Thill",
    author_email = "github@blackhand.org",
    keywords = ["thumbor", "fallback", "images", "nfs", "mongodb"],
    license = 'MIT',
    url = 'https://github.com/Bkhand/thumbor_libs_blackhand',
    packages=[
        'thumbor_libs_blackhand',
        'thumbor_libs_blackhand.loaders',
        'thumbor_libs_blackhand.url_signers',
        'thumbor_libs_blackhand.metrics',
        'thumbor_libs_blackhand.storages',
        'thumbor_libs_blackhand.result_storages'
    ],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3.9',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    package_dir = {"thumbor_libs_blackhand": "thumbor_libs_blackhand"},
    install_requires=['thumbor>=7.0.10','pymongo>=3.11.3'],
    long_description = """\
This module test support for file.
"""
)