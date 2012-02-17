#!/usr/bin/env python
#
# pyepg/conf.py - Configuration
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

import string

# ###########################################################################
# Data
# ###########################################################################

CONFIG = { 'channels' : set() }

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ( path, override ):
  global CONFIG
  conf = []

  # Load config file
  print path
  for l in open(path):
    i = l.find('#')
    if i != -1:
      l = l[:i]
    l = l.strip()
    if not l: continue
    p = map(string.strip, l.split('='))
    if len(p) == 2: conf.append(p)

  # Add overrides
  for k in override:
    conf.append((k, override[k]))

  # Process
  for i in conf:

    # Channel
    if i[0] == 'channel':
      CONFIG['channels'].add(i[1])
    
    # Other
    else:
      v = i[1]
      try:
        v = eval(v)
      except: pass
      CONFIG[i[0]] = v

  import pprint
  pprint.pprint(CONFIG)

# Get configuration value
def get ( key, default = None ):
  ret = default
  if key in CONFIG:
    ret = CONFIG[key]
  return ret

# ###########################################################################
# Editor
# ###########################################################################
