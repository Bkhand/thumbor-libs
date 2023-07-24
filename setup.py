# -*- coding: utf-8 -*-
# Blackhand library for Thumbor
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license


from distutils.core import setup

setup(
    name = "thumbor_libs_blackhand",
    version = "0.3.1",
    description = "libs thumbor",
    author = "Bertrand Thill",
    author_email = "github@blackhand.org",
    keywords = ["thumbor", "fallback", "images", "nfs", "mongodb"],
    license = 'GNU',
    url = 'https://github.com/Bkhand/thumbor_libs_blackhand',
    packages=[
        'thumbor_libs_blackhand',
        'thumbor_libs_blackhand.mongodb',
        'thumbor_libs_blackhand.loaders',
        'thumbor_libs_blackhand.url_signers',
        'thumbor_libs_blackhand.metrics',
        'thumbor_libs_blackhand.storages',
        'thumbor_libs_blackhand.result_storages'
    ],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: French',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3.9',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    package_dir = {"thumbor_libs_blackhand": "thumbor_libs_blackhand"},
    install_requires=['thumbor>=7.1.0','pymongo>=4.2.0'],
    long_description = """\
This module enable mongodb support and fallback for thumbor.
"""
)