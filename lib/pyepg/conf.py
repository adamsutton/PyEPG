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

CONF_PATH = None
CONFIG    = {}

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ( path, override ):
  global CONFIG, CONF_PATH
  CONF_PATH = path
  conf = []

  # Load config file
  for l in open(path):
    i = l.find('#')
    if i != -1:
      l = l[:i]
    l = l.strip()
    if not l: continue
    p = map(string.strip, l.split(':'))
    if len(p) == 2: conf.append(p)

  # Add overrides
  for k in override:
    conf.append((k, override[k]))

  # Process
  for i in conf:
    k = i[0]
    v = i[1]

    # Try eval value
    try:
      v = eval(v)
    except: pass

    # Special array
    if k.endswith('[]'):
      if k not in CONFIG: CONFIG[k] = [ v ]
      else: CONFIG[k].append(v)

    # Normal
    else:
      CONFIG[k] = v

# Save configuration
def save ( path = None ):
  from datetime import datetime
  
  # Default
  if not path: path = CONF_PATH

  # Save
  fp = open(path, 'w')
  fp.write('# PyEPG configuration\n')
  fp.write('#   generated %s\n' % datetime.now())
  fp.write('')
  for k in CONFIG:

    # Special array
    if k.endswith('[]'):
      for v in CONFIG[k]:
        fp.write('%s: %s\n' % (k, repr(v)))
    
    # Normal
    else:
      fp.write('%s: %s\n' % (k, repr(CONFIG[k])))

# Get configuration value
def get ( key, default = None ):
  ret = default
  if key in CONFIG:
    ret = CONFIG[key]
  return ret

# Set configuration value
def set ( key, value ):
  global CONFIG
  CONFIG[key] = value

# ###########################################################################
# Editor
# ###########################################################################
