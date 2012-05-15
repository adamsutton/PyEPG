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

CONF_READY = False
CONF_PATH  = None
CONF_OVER  = {}
CONF_DATA     = {}

# ###########################################################################
# Functions
# ###########################################################################

# Initialise
def init ( path, override ):
  global CONF_DATA, CONF_OVER, CONF_PATH, CONF_READY
  try:
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
      if len(p) == 2: conf.append((p[0], p[1], False))

    # Add overrides
    for k in override:
      conf.append((k, override[k], True))

    # Process
    for i in conf:
      (k, v, o) = i

      # Try eval value
      try:
        v = eval(v)
      except: pass

      # Special array
      if k.endswith('[]'):
        if o:
          if k in CONF_OVER: CONF_OVER[k] = [ v ]
          else:              CONF_OVER[k].append(v)
        else:
          if k not in CONF_DATA: CONF_DATA[k] = [ v ]
          else:                  CONF_DATA[k].append(v)

      # Normal
      else:
        if o: CONF_OVER[k] = v
        else: CONF_DATA[k] = v
        CONF_DATA[k] = v

    # Done
    CONF_READY = True
  except: pass

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
  for k in CONF_DATA:

    # Special array
    if k.endswith('[]'):
      for v in CONF_DATA[k]:
        fp.write('%s: %s\n' % (k, repr(v)))
    
    # Normal
    else:
      fp.write('%s: %s\n' % (k, repr(CONF_DATA[k])))

# Get configuration value
def get ( key, default = None ):
  ret = default
  if key in CONF_OVER:
    ret = CONF_OVER[key]
    if key.endswith('[]') and key in data:
      ret = CONF_DATA[key].extend(ret)
  elif key in CONF_DATA:
    ret = CONF_DATA[key]
  return ret

# Set configuration value
def set ( key, value ):
  global CONF_DATA
  CONF_DATA[key] = value
  if key in CONF_OVER:
    del CONF_OVER[key]

# Check configuration is ready
def ready ():
  global CONF_READY
  return CONF_READY

# ###########################################################################
# Editor
# ###########################################################################
