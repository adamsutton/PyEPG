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
from pyepg.model import EPG, Channel

# ###########################################################################
# Helpers
# ###########################################################################

#
# Import module
#
def _import ( fmt, n ):
  return __import__(fmt % n, globals(), locals(), [n])

#
# Default Configuration options
#
def options ( optp ):
  optp.add_option('-c', '--config', default=None,
                  help='Specify alternative configuration file')
  optp.add_option('--confdir', default=None,
                  help='Specify alternative configuration directory')
  optp.add_option('-o', '--option', default=[], action='append',
                  help='Specify configuration option')
  optp.add_option('-f', '--formatter', default=None,
                  help='Specify formatter')
  optp.add_option('-d', '--debug', default=None, type='int',
                  help='Enable debug')
  optp.add_option('--days', default=None, type='int',
                  help='Specify number of days to grab')

#
# Setup
#
def setup ( opts = {}, args = [], conf_path = None ):
  conf_root = None
  conf_over = {}

  # Process command line
  if hasattr(opts, 'options'):
    for o in opts.option:
      p = o.split('=')
      if len(p) == 2:
        conf_over[p[0]] = p[1]
  if hasattr(opts, 'days') and opts.days is not None:
    conf_over['days'] = opts.days
  if hasattr(opts, 'debug') and opts.debug is not None:
    conf_over['debug_level'] = opts.debug
  if hasattr(opts, 'formatter') and opts.formatter is not None:
    conf_over['formatter'] = opts.formatter
  if hasattr(opts, 'config') and opts.config is not None:
    conf_path = opts.config
  if hasattr(opts, 'confdir') and opts.confdir is not None:
    conf_root = opts.confdir

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

#
# Get current grabber
#
def get_grabber():
  return _import('pyepg.grabber.%s', conf.get('grabber', 'atlas'))

#
# Get grabbers
#
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

#
# Get current formatter
# 
def get_formatter():
  return _import('pyepg.formatter.%s', conf.get('formatter', 'epg'))

#
# Get available formatters
#
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

#
# Get current package
#
def get_package ():
  ret     = None
  package = conf.get('package', None)
  if package:
    ret = _import('pyepg.package.%s', package)
  return ret

#
# Get current channel set
#
def get_channels ( package = None ):

  # Get defaults
  if package is None: package = get_package()

  # Map channels
  channels = map(lambda x: Channel(x), conf.get('channel[]', []))
  if package:
    channels = package.channels(channels)

  return channels

#
# Fix missing plusN channels
#
def fix_plus_n ( epg, channels ):
  import re
  from copy     import copy
  from datetime import timedelta

  epg_chns = epg.get_channels()
  exp      = re.compile('(\+\d+)$')
  fix      = []

  # Find potential candidates for a fix
  for c in channels:
    if c not in epg_chns:
      r = exp.search(c.uri)
      if r:
        os  = int(r.group(1))
        uri = c.uri.replace(r.group(1), '')
        for c1 in channels:
          if uri == c1.uri:
            fix.append((c, os, c1))
            break

  # Fix the channels
  for (plus, offset, base) in fix:
    sched = epg.get_schedule(base)
    if not sched: continue
    log.info('pyepg - fix missing plusN channel %s' % plus.title)
    for e in sched:
      n         = copy(e)
      n.channel = plus
      n.start   = n.start + timedelta(minutes=offset)
      n.stop    = n.stop  + timedelta(minutes=offset)
      epg.add_broadcast(n)

# ###########################################################################
# Run
# ###########################################################################

def main ( opts, args, conf_path = None ):

  # Setup
  setup(opts, args, conf_path)

  # Initialise EPG
  epg = EPG()

  # Get config
  days     = conf.get('days', 7)
  today    = datetime.datetime.today()

  # Get grabber/formatter
  grabber   = get_grabber()
  formatter = get_formatter()

  # Channels
  channels  = get_channels()

  # Get EPG
  log.info('grabbing EPG for %d days' % days)
  grabber.grab(epg, channels, today, today + datetime.timedelta(days=days))

  # Attempt to deal with missing +N channels
  fix_plus_n(epg, channels)

  # Finish the EPG (will tidy it up)
  epg.finish()

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

# Get select
def get_select ( msg, options ):
  idx = -1
  if len(options) == 1: return 0
  print msg
  for i in range(len(options)):
    print '  %2d. %s' % (i+1, options[i])
  while True:
    print '  select (1-%d): ' % len(options),
    try:
      t = int(sys.stdin.readline().strip())
      if t > 0 and t <= len(options):
        idx = t - 1
        break
    except ValueError: pass
  return idx
    
# Configure system
def configure ( opts, args, conf_path = None ):

  #
  # Setup
  #

  setup(opts, args, conf_path)

  #
  # Global
  #

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

  # Postcode
  print '\nPostcode (for regional TV) [%s]: ' % conf.get('postcode', ''),
  pc = sys.stdin.readline().strip()
  if pc:
    conf.set('postcode', pc)

  #
  # Grabber
  #

  grabbers = get_grabbers()
  if not grabbers:
    log.error('no grabbers available')
    sys.exit(1)
  options = map(lambda x: x[0], grabbers)
  idx     = get_select('\nSelect grabber:', options)
  grabber = grabbers[idx][1]
  conf.set('grabber', grabbers[idx][0])
  print ''
  print 'Grabber: %s' % grabbers[idx][0]

  #
  # Formatter
  #

  formatters = get_formatters()
  if not formatters:
    log.error('no formatters available')
    sys.exit(1)
  options   = map(lambda x: x[0], formatters)
  idx       = get_select('\nSelect formatter:', options)
  formatter = formatters[idx][1]
  conf.set('formatter', formatters[idx][0])
  print ''
  print 'Formatter: %s' % formatters[idx][0]

  #
  # Grabber/Formatter config
  #

  if hasattr(grabber, 'configure'):
    grabber.configure()
  if hasattr(formatter, 'configure'):
    formatter.configure()

  #
  # Channels
  #
  channels = []

  print ''
  print 'Channel Configuration'
  print '-' * 60

  # Get packages
  packages  = grabber.packages()
  options   = []
  options.extend(['Skip'])
  options.extend(map(lambda x: x.title(), packages))
  idx       = get_select('Select Platform:', options)

  # Platform
  if idx:
    idx      = idx - 1
    package = packages[idx]
    conf.set('package', package.id())

    # Exclusions
    a = None
    while a not in [ 'y', 'n', 'yes', 'no' ]:
      print '\nWould you like to add exclusions (y/n)? ',
      a = sys.stdin.readline().strip().lower()
    
    # Get
    if a in [ 'y', 'yes' ]:
      for c in package.channels():
        a = None
        while a not in [ 'y', 'n', 'yes', 'no' ]:
          print '\n  %s (y/n)? ' % c.title,
          a = sys.stdin.readline().strip().lower()
        if a in [ 'y', 'yes' ]: channels.append(c.title)

    # Store
    channels = []
    for c in package.channels():
      channels.append(c.uri)
    conf.set('channel[]', channels)
        
  #
  # Save
  #
  conf.save()

# ###########################################################################
# Editor
# ###########################################################################
