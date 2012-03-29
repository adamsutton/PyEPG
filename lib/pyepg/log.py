#!/usr/bin/env python
#
# pyepg/log.py - Logging routines
#
# Copyright (C) 2012 Adam Sutton <dev@adamsutton.me.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
"""

# ###########################################################################
# Imports
# ###########################################################################

# System
import sys, time
from threading import Lock

# PyEPG
import pyepg.conf as conf

# ###########################################################################
# Data
# ###########################################################################

global LOG_INIT, LOG_DEBUG
LOG_INIT  = 0
LOG_DEBUG = None
LOG_LOCK  = Lock()

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ():
  global LOG_INIT, LOG_DEBUG
  LOG_INIT  = time.time()
  LOG_DEBUG = conf.get('debug_level', None)

# Output
def out ( pre, msg, **dargs ):
  global LOG_LOCK
  tm = '%0.2f' % (time.time() - LOG_INIT)
  with LOG_LOCK:
    print >>sys.stderr, '%8s - %-6s:' % (tm, pre.lower()),
    try:
      if 'pprint' in dargs and dargs['pprint']:
        import pprint
        pprint.pprint(msg, sys.stderr)
      else:
        print >>sys.stderr, msg
    except:
      print >>sys.stderr, ''

# Debug
def debug ( msg, lvl=0, **dargs ):
  if LOG_DEBUG is not None and lvl <= LOG_DEBUG:
    out('DEBUG', msg, **dargs)

# Info
def info  ( msg, **dargs ):
  out('INFO', msg, **dargs)

# Warning
def warn  ( msg, **dargs ):
  out('WARN', msg, **dargs)

# Error
def error ( msg, **dargs ):
  out('ERROR', msg, **dargs)

# ###########################################################################
# Editor
# ###########################################################################
