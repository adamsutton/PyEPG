#!/usr/bin/env python
#
# pyepg/grabber/xmtlv.py - XMLTV "importer"
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
import os, sys, urllib2, json, re
import pprint, datetime, time
from threading import Thread

# PyEPG
import pyepg.log   as log
import pyepg.conf  as conf
import pyepg.cache as cache
import pyepg.util  as util
from pyepg.model import Channel, Broadcast, Brand, Series, Episode, Person
import pyepg.model.genre as genre

# ###########################################################################
# XMLTV Util
# ###########################################################################

def xmltv_grabbers ():
  ret  = {}
  from subprocess import Popen, PIPE
  cmd  = '/usr/bin/tv_find_grabbers'
  if not os.path.exists(cmd): cmd = os.path.basename(cmd)
  proc = Popen(cmd, stdout=PIPE)
  if not proc.wait():
    for l in proc.communicate()[0].splitlines():
      p = l.strip().split('|')
      ret[p[0]] = p[1]
  return ret

def xmltv_configure ( cmd ):

  # Import
  if cmd == '__import__':
    print '  Enter file path:',
    conf.set('xmltv_import_path', sys.stdin.readline().strip())
    # TODO: validation
  
  # Pass to command
  else:
    from subprocess import Popen, PIPE
    # TODO: should check config is supported?
    proc = Popen([cmd, '--configure'])
    proc.wait()

# ###########################################################################
# Grabber API
# ###########################################################################

# Grab specified data
def grab ( epg, channels, start, stop ):
  pass

# Get a list of the support packages
def packages (): return []

# Get a list of available channels
def channels (): return []

# Configure
def configure ():
  from pyepg.main import get_select
  print ''
  print 'XMLTV Configuration:'
  print '-' * 60

  # Find available grabbers
  grabbers = xmltv_grabbers()
  keys     = [ '__import__' ]
  keys.extend(grabbers.keys())
  
  # Select grabber
  idx      = get_select('Select XMLTV grabber:', keys)
  conf.set('xmltv_grabber', keys[idx])

  # Configure the grabber
  xmltv_configure(keys[idx])

# ###########################################################################
# Editor
# ###########################################################################
