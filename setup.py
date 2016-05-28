#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='preprocessing',
      version='dev',
      description='Data preprocessing for statistical analysis',
      author='Juan Casse',
      author_email='jcasse@chla.usc.edu',
      packages = ['preprocessing', 'preprocessing.src'],
      include_package_data = True,
     )
