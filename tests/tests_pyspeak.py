""" Test suite for the utils.py file. """

# system
import os
import sys
# pyspeak
from pyspeak.commandline import execute
# nose
from nose.tools import with_setup
from nose.tools import raises
from nose.tools import assert_equal
from nose.tools import assert_not_equal


@SystemExit
def test_info():
    sys.argv = ['pyspeak', '-v']
    execute()
