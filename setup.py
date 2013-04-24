# -*- coding: utf-8 -*-
""" PySpeak setup.py script """

# PySpeak
from pyspeak import __version__

# system
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from os.path import join, dirname


setup(
    name=__version__,
    version='0.1.0',
    description='Python Speech Recognition, Voice Recognition, Text-to-Speech and Voice Command Engine',
    author='John Wyles',
    author_email='john@johnwyles.com',
    packages=['pyspeak','pyspeak.test'],
    url='https://github.com/johnwyles/pyspeak',
    long_description=open('README.txt').read(),
    install_requires=[''],
    test_suite='pyspeak.test',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
      ],
)
