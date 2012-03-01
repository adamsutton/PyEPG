#!/usr/bin/env python
#
# pyepg/main.py - Main processing function
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
import os, sys, datetime

# PyEPG
import pyepg.log             as log
import pyepg.conf            as conf
import pyepg.cache           as cache
import pyepg.grabber.atlas   as grabber
from pyepg.model import EPG

# ###########################################################################
# Helpers
# ###########################################################################

# Import module
def _import ( fmt, n ):
  return __import__(fmt % n, globals(), locals(), [n])

# ###########################################################################
# Run
# ###########################################################################

def main ( conf_root = None , conf_over = {}, conf_path = None ):

  # Defaults
  if conf_root is None:
    conf_root = os.path.expanduser('~/.pyepg')
  if conf_path is None:
    conf_path = os.path.join(conf_root, 'config')
  cache_path = os.path.join(conf_root, 'cache')

  # Load configuration
  conf.init(conf_path, conf_over)

  # Initialise log
  log.init()

  # Initialise the cache
  cache.init(cache_path) 

  # Initialise EPG
  epg = EPG()

  # Get config
  channels = conf.get('channel[]', [])
  days     = conf.get('days', 7)
  today    = datetime.datetime.today()

  # Get grabber/formatter
  grabber   = _import('pyepg.grabber.%s',   conf.get('grabber', 'atlas'))
  formatter = _import('pyepg.formatter.%s', conf.get('formatter', 'epg'))

  # Get EPG
  grabber.grab(epg, channels, today, today + datetime.timedelta(days=days))

  # Output
  formatter.format(epg, sys.stdout)

  # Stats
  log.info('')
  log.info('Statistics:')
  log.info('--------------------------------------')
  log.info('Channel  Count: %d' % len(epg.get_channels()))
  log.info('Brand    Count: %d' % len(epg.get_brands()))
  log.info('Series   Count: %d' % len(epg.get_series()))
  log.info('Episode  Count: %d' % len(epg.get_episodes()))
  log.info('Schedule Count: %d' % epg.get_sched_count())

# ###########################################################################
# Configure the system
# ###########################################################################

# Get available formatters
def get_formatters ():
  import pyepg.formatter
  ret = []
  for f in os.listdir(pyepg.formatter.__path__[0]):
    if '__init__' in f: continue
    if not f.endswith('.py'): continue 
    f = f.replace('.py', '')
    mod = _import('pyepg.formatter.%s', f)
    ret.append((f, mod))
  return ret

# Get grabbers
def get_grabbers ():
  import pyepg.grabber
  ret = []
  for f in os.listdir(pyepg.grabber.__path__[0]):
    if '__init__' in f: continue
    if not f.endswith('.py'): continue 
    f = f.replace('.py', '')
    mod = _import('pyepg.grabber.%s', f)
    ret.append((f, mod))
  return ret
    
# Configure system
def configure ( conf_root = None, conf_over = {}, conf_path = None ):

  # Defaults
  if conf_root is None:
    conf_root = os.path.expanduser('~/.pyepg')
  if conf_path is None:
    conf_path = os.path.join(conf_root, 'config')

  # Load configuration
  conf.init(conf_path, conf_over)
  print 'System Configuration'
  print '-' * 60

  # Number of days to grab
  days = conf.get('days', 7)
  while True:
    print 'Days to grab [%d]: ' % days,
    t = sys.stdin.readline().strip()
    if not t: break
    try:
      days = int(t)
      break
    except: pass
  conf.set('days', days)

  # Grabber
  grabbers = get_grabbers()
  if not grabbers:
    log.error('no grabbers available')
    sys.exit(1)
  s = 0
  if len(grabbers) > 1:
    print ''
    print 'Select grabber:'
    for i in range(len(grabbers)):
      print '  %2d - %s' % (i+1, grabbers[i][0])
    while s < 1 or s > len(grabbers):
      print 'select [1-%d]: ' % len(grabbers),
      try:
        s = int(sys.stdin.readline())
      except KeyboardInterrupt: sys.exit(1)
      except: pass
    s = s - 1
  print ''
  print 'Grabber: %s' % grabbers[s][0]
  grabber = grabbers[s][1]

  # Formatter
  formatters = get_formatters()
  if not formatters:
    log.error('no formatters available')
    sys.exit(1)
  s = 0
  if len(formatters) > 1:
    print ''
    print 'Select formatter:'
    for i in range(len(formatters)):
      print '  %2d - %s' % (i+1, formatters[i][0])
    while s < 1 or s > len(formatters):
      print 'select [1-%d]: ' % len(formatters),
      try:
        s = int(sys.stdin.readline())
      except KeyboardInterrupt: sys.exit(1)
      except: pass
    s = s - 1
  print ''
  print 'Formatter: %s' % formatters[s][0]
  formatter = formatters[s][1]

  # Channels
  # TODO: need something better here
  print ''
  print 'Channel Configuration'
  print '-' * 60
  print '  loading channel data...'
  conf_chns  = conf.get('channel[]', [])
  new_chns   = []
  avail_chns = grabbers[s][1].channels()
  if not avail_chns:
    log.error('No channels available')
    sys.exit(1)
  print ''
  auto = None
  for c in avail_chns:
    d = 'no'
    if c.uri in conf_chns: d = 'yes'
    if auto is None:
      s = None
      while s is None:
        print '  %s [%s] (yes/no/all/skip)? ' % (c.title, d),
        t = sys.stdin.readline().strip().lower()
        if not t: t = d
        if t in [ 'y', 'yes' ]: s = True
        if t in [ 'n', 'no'  ]: s = False
        if t in [ 'all', 'skip' ]:
          auto = (t == 'all')
          break
    if auto: s = True
    if s: new_chns.append(c.uri)
  conf.set('channel[]', new_chns)

  
  # Grabber/Formatter config
  if hasattr(grabber, 'configure'):
    grabber.configure()
  if hasattr(formatter, 'configure'):
    formatter.configure()

  # Save
  conf.save(conf_path)

# ###########################################################################
# Editor
# ###########################################################################
