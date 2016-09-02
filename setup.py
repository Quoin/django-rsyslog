#!/usr/bin/env python

from distutils.core import setup

setup(name='django-rsyslog',
      version='1.0',
      description='Python log handler and formatters for Rsyslog',
      author='Ben Keith',
      author_email='bkeith@quoininc.com',
      url='https://www.quoininc.com',
      packages=['django_rsyslog'],
      install_requires=['python_json_logger==0.1.5']
     )
