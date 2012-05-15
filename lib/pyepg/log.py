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
import os, sys, time, pprint, syslog
from threading import Lock

# PyEPG
import pyepg.conf as conf

# ###########################################################################
# Data
# ###########################################################################

global LOG_INIT, LOG_PATH, LOG_SYSLOG, LOG_DEBUG, LOG_LOCK, LOG_PRIO
LOG_INIT   = 0
LOG_PATH   = None
LOG_SYSLOG = None
LOG_DEBUG  = None
LOG_LOCK   = Lock()

# Priority mappings
LOG_PRIO   = {
  'DEBUG' : syslog.LOG_DEBUG,
  'WARN'  : syslog.LOG_WARNING,
  'ERROR' : syslog.LOG_ERR,
}

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ( path = None, syslog = False, level = -1 ):
  global LOG_INIT, LOG_PATH, LOG_SYSLOG, LOG_DEBUG
  LOG_INIT   = time.time()
  LOG_SYSLOG = syslog
  LOG_DEBUG  = level

  # Check we can write to file
  if path:
    try:
      dirp = os.path.dirname(path)
      if dirp and not os.path.isdir(dirp):
        os.makedirs(dirp)
      open(path, 'a')
      LOG_PATH = path
    except Exception, e:
      error('failed to create log file [path=%s, e=%s]' % (path, e))

# Output
def out ( pre, msg, **dargs ):
  global LOG_LOCK
  tm = '%0.2f' % (time.time() - LOG_INIT)
  with LOG_LOCK:
    try:
      if 'pprint' in dargs and dargs['pprint']:
        msg = pprint.pformat(msg)
    except: pass

    # Output to stderr, file
    out = '%8s - %-6s: %s' % (tm, pre.lower(), msg)
    print >>sys.stderr, out
    if LOG_PATH:
      open(LOG_PATH, 'a').write(out + '\n')

    # Output to syslog
    if LOG_SYSLOG:
      pri = syslog.LOG_INFO
      if pre in LOG_PRIO: pri = LOG_PRIO[pre]
      syslog.syslog(pri, msg)

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
