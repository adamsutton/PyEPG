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

# ###########################################################################
# Data
# ###########################################################################

LOG_INIT  = 0
LOG_DEBUG = 0
LOG_PATH  = None

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ():
  global LOG_INIT
  LOG_INIT = time.time()

# Output
def out ( pre, msg ):
  tm = '%0.2f' % (time.time() - LOG_INIT)
  print >>sys.stderr, '%8s - %-5s: %s' % (tm, pre.lower(), msg)

# Debug
def debug ( lvl, msg ):
  out('DEBUG', msg)

# Info
def info  ( msg ):
  out('INFO', msg)

# Warning
def warn  ( msg ):
  out('WARN', msg)

# Error
def error ( msg ):
  out('ERROR', msg)

# ###########################################################################
# Editor
# ###########################################################################
