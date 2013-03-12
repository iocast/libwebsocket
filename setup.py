#!/usr/bin/env python

import sys, os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

classifiers = [
               'Development Status :: 4 - Beta',
               'Intended Audience :: Developers',
               'Intended Audience :: Science/Research',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Scientific/Engineering :: GIS',
               ]

setup(name='libwebsocket',
      version='0.1',
      description='websocket library',
      long_description=read('doc/Readme.txt'),
      author='LibWebSocket (iocast)',
      author_email='iocast@me.com',
      url='',
      
      packages=find_packages(exclude=["doc", "tests"]),
      
      install_requires=[''],
      
      #test_suite = 'tests.test_suite',
      
      zip_safe=False,
      license="MIT",
      classifiers=classifiers
      )
