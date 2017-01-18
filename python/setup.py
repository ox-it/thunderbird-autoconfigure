#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name='oxtbac',
      version='0.1',
      description='Oxford Thunderbird Auto-configuration',
      author='Alexander Dutton',
      author_email='alexander.dutton@oucs.ox.ac.uk',
      packages=['oxtbac'],
      package_data={'oxtbac': ['oxtbac.wsgi']},
     )
