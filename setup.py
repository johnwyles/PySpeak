#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pyspeak',
      version='0.1.0',
      description='Python Speech Recognition, Voice Recognition, Text-to-Speech and Voice Command Engine.',
      author='John Wyles',
      author_email='john@johnwyles.com',
      url='https://github.com/johnwyles/pyspeak',
      license='3-clause BSD',
      long_description=open('./docs/README.rst').read(),
      platforms='any',
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 1 - Planning'],
      packages=['pyspeak'])
      #requires=['stuff'],
      #scripts=['bin/x'],
      #data_files=[('file', ['dest']),],
