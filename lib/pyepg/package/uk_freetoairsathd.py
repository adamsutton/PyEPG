#!/usr/bin/env python
#
# platform/uk_freetoairsathd.py - Free to air Sattelite channel list
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
import os, sys, re, string

# PyEPG
import pyepg.log                as log
import pyepg.cache              as cache
import pyepg.conf               as conf
from pyepg.model import Channel

# ###########################################################################
# Global data
# ###########################################################################

# Channel data
CHANNELS = None

# ###########################################################################
# Functions
# ###########################################################################

# Process region data file
def process_region_data ( data ):
  ret = {}
  exp = re.compile('\[(.*)\]')
  chn = None
  for l in data.splitlines():
    r = exp.search(l)
    if r:
      chn = r.group(1).encode('utf8')
      ret[chn] = {}
      continue
    if not chn: continue
    p         = map(string.strip, l.split(':'))
    if len(p) != 2: continue
    if p[0] == 'Default':
      ret[chn][p[0]] = [p[1]]
    else:
      ret[chn][p[0]] = map(lambda x: x.strip().upper(), p[1].split(','))
  return ret

# Find regional entry
def find_regional ( chn, pc, chns, regions, default = None ):
  ret   = None
  pc    = pc.replace(' ', '').upper()
  title = chn.title

  # Fix title
  plusN     = ''
  hd        = ''
  r         = re.search('( \+\d+)$', title)
  if r:
    plusN = r.group(1)
    title = title.replace(plusN, '')
  if ' HD' in title:
    hd    = ' HD'
    title = title.replace(' HD', '')

  # Valid?
  if title not in regions: return None
  regions = regions[title]

  # Set default
  if not default and 'Default' in regions:
    default = regions['Default'][0]

  # Search
  reg = None
  while pc:
    for k in regions:
      if pc in regions[k]: reg = k
    pc = pc[:-1]

  # Found
  if reg:
    t = title + ' ' + reg + hd + plusN
    for c in chns:
      if c.title == t:
        ret = c
        break
  if not ret and default:
    t = title + ' ' + default + hd + plusN
    for c in chns:
      if c.title == t:
        ret = c
        break
  
  # Done
  return ret

# Get the raw channel list
def _channels ():

  # Fetch remote data
  log.info('fetch free to air channel info')
  chn_data = cache.get_data('uk_satellite_channels.csv', ttl=86400*7)
  reg_data = cache.get_data('uk_satellite_regions.csv', ttl=86400*7)

  # Channels list
  log.info('processing channel list')
  regional = []
  chns     = []
  for l in chn_data.splitlines()[1:]:
    p = l.strip().split(',')
    if len(p) < 9: continue
    try:
      c = Channel()
      c.extra['stream']                = [ (int(p[0]), p[1]) ] 
      c.uri                            = p[2]
      c.title                          = p[3]
      c.extra['freesat_number']        = int(p[4])
      c.number = c.extra['sky_number'] = int(p[5])
      c.hd                             = p[6] == '1'
      c.radio                          = p[8] == '1'
      if (p[10])
        c.image                        = p[10]
      else
        c.image                        = p[9]

      # Skip
      if not c.uri: continue

      # Already included
      if c in chns:
        for t in chns:
          if t == c:
            t.extra['stream'].extend(c.extra['stream'])
            break
        continue

      # Regional channel
      if p[7] == '1': 
        regional.append(c)

      # Store
      elif c.extra['stream'][0][0]:
        chns.append(c)

    except Exception, e:
      log.error('failed to process [%s] [e=%s]' % (l, str(e)))

  # Process regional channels
  regions = process_region_data(reg_data)
  pc      = conf.get('postcode', '')
  for c in regional:
    t = find_regional(c, pc, chns, regions)
    if t: 
      c.uri             = t.uri
      c.extra['stream'] = t.extra['stream']
      chns.insert(0, c)

  # Filter duplicates
  ret = []
  for c in chns:
    if c not in ret:
      ret.append(c)

  return ret

# ###########################################################################
# API
# ###########################################################################

# Get channel list
# Note: the access is a bit of a hack
def channels ( filt = None ):
  global CHANNELS

  # Fetch
  if CHANNELS is None:
    chns = []
    for c in _channels():
      if c.number: chns.append(c)
    CHANNELS = chns
  ret = CHANNELS

  # Filter
  if filt is not None:  
    ret = set()
    for c in CHANNELS:
      if c in filt: ret.add(c)

  # Done
  return ret

# Package name
def title ():
  return 'UK Free to Air Satellite HD'

# Config ID
def id ():
  return 'uk_freetoairsathd'

# TODO: Move postcode here!
def config ():
  pass

# ###########################################################################
# Editor
# ###########################################################################
