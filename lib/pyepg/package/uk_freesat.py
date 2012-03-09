#!/usr/bin/env python
#
# platform/uk_freesat.py - Freesat
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
This will basically provide a fairly comprehensive list of all the channels
available free to air in the UK on Astra/Eurobird satellite
"""

# ###########################################################################
# Imports
# ###########################################################################

# System
import os, sys, re

# PyEPG
import uk_freesathd

# ###########################################################################
# Global data
# ###########################################################################

# Channel data
CHANNELS = None

# ###########################################################################
# API
# ###########################################################################

# Get channel list
# Note: the access is a bit of a hack
def channels ( filt = None ):
  global CHANNELS


  # Get ALL channels
  if CHANNELS is None:
    chns = []
    for c in uk_freesathd.channels():
      if not c.hd: chns.append(c)
    CHANNELS = chns
  ret = CHANNELS

  # Filter
  if filt is not None:
    ret = []
    for c in CHANNELS:
      if c in filt: ret.append(c)

  # Done
  return ret

def title ():
  return 'Freesat'

def id ():
  return 'uk_freesat'

# ###########################################################################
# Editor
# ###########################################################################
