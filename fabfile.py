#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Deployment of PySpeak """

# system
import os, re
# fabric
from fabric.api import cd, env, execute, local, run, sudo, prefix
# PySpeak
from pyspeak import __version__


def fast_commit(capture=True):
    """ Fast commit with generic message. """
    env.warn_only = True
    local('git commit -a -m "fast_commit through Fabric"')


def push():
    """ Local git push. """
    local("git push --all")


def deploy():
    """ Commit and push to git servers. """
    execute(fast_commit)
    execute(push)


def reinstall():
    """ Reinstall the project to local virtualenv. """
    local('if [ $(pip freeze | grep PySpeak | wc -w ) -eq 1 ]; then '
          'pip uninstall -q -y PySpeak ; fi')
    local('python setup.py sdist')
    local('pip install -q dist/PySpeak-' + __version__ + '.tar.gz')
    local('rm -rf dist PySpeak.egg-info')


def install():
    """ Install the project. """
    local('python setup.py install')
    local('rm -rf build')


def build_doc():
    """ Build the html documentation. """
    local('cd docs/ && make html')


def clean():
    """ Remove temporary files. """
    local('rm -rf docs/_build/ dist/ *.egg-info/')
    local('find . -name "*.pyc" | xargs rm')


def upload():
    """ Upload Pypi. """
    local("python setup.py sdist upload")


def md2rst(in_file, out_file):
    """ Generate reStructuredText from Makrdown. """
    local("pandoc -f markdown -t rst %s -o %s" % (in_file, out_file))


def readme():
    md2rst('README.md', 'README.txt')

def tests():
    """ Launch tests. """
    local("nosetests")
    # local("coverage html -d /tmp/coverage-projy --omit='projy/docopt.py'")
    # local("coverage erase")
