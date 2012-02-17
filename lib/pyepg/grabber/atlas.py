#!/usr/bin/env python
#
# pyepg/grabber/atlas.py - PyEPG Atlas (metabroadcast.com) grabber
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

# PyEPG
import pyepg.log   as log
import pyepg.conf  as conf
import pyepg.cache as cache
import pyepg.util  as util
from pyepg.model import Channel, Broadcast, Brand, Series, Episode, Person
import pyepg.model.genre as genre

# ###########################################################################
# Atlas API
# ###########################################################################

# Fetch raw data from atlas
def atlas_fetch ( url ):
  url  = 'http://atlas.metabroadcast.com/3.0/' + url
  log.info('fetch %s' % url)
  up   = urllib2.urlopen(url)
  data = up.read()
  log.info('decode json')
  jdata = json.loads(data)
  log.debug(jdata, pprint=True)
  return jdata
  
# Get content data
def atlas_fetch_content ( uri, key = None ):
  url = 'content.json?uri=%s' % uri
  if key:
    url = url + '&apiKey=%s' % key
  return atlas_fetch(url)

# Parse time
def atlas_p_time ( tm ):
  # TODO: all times are Zulu?
  ret = datetime.datetime.strptime(tm, '%Y-%m-%dT%H:%M:%SZ')
  ret = ret.replace(tzinfo=util.TimeZoneSimple(0))
  return ret

# ###########################################################################
# Data fetch routines
# ###########################################################################

#
# Fetch (and validate) content
#
def get_content ( uri, type ):
  ret = None
  try:
    data = atlas_fetch_content(uri)
    if 'contents' in data:
      for c in data['contents']:
        if 'type' in c and c['type'] == type:
          ret = c 
          break
  except Exception, e:
    log.error(str(e))
  return ret

#
# Fetch brand
#
def get_brand ( uri, data = None ):
  log.info('get_brand(%s)' % uri)

  # Check the cache
  ret = cache.get_brand(uri)

  # Get remote
  if ret is None:
    try:
      if not data or data.keys() == ['uri'] :
        data = get_content(uri, 'brand')
      if data:
        ret = process_brand(data)
    except: pass

    # Put in cache
    if ret: cache.put_brand(uri, ret)
  return ret

#
# Fetch series
#
def get_series ( uri, data = None ):
  log.info('get_series(%s)' % uri)

  # Check cache
  ret = cache.get_series(uri)
  
  # Get remote
  if ret is None:
    try:
      if not data or data.keys() == [ 'uri' ]:
        data = get_content(uri, 'series')
      if data:
        ret = process_series(data)
    except: pass

    # Cache
    if ret: cache.put_series(uri, ret)

  return ret

# 
# Get episode
#
def get_episode ( uri, data ):
  log.info('get_episode(%s)' % uri)
  
  # Check cache
  ret = cache.get_episode(uri)

  # Process
  if ret is None:
    ret = process_episode(data)
  
    # Cache
    if ret: cache.put_episode(uri, ret)

  return ret

#
# Get channel
#
def get_channel ( uri, data ):
  log.info('get_channel(%s)' % uri)

  # Check cache
  ret = cache.get_channel(uri)

  # Process
  if ret is None: 
    ret = process_channel(data)
    
    # Cache
    if ret: cache.put_channel(uri, ret)

  return ret

#
# Convert generes
#
GENRE_MAP = {
  'http://ref.atlasapi.org/genres/atlas/comedy'        : genre.COMEDY,
  'http://ref.atlasapi.org/genres/atlas/childrens'     : genre.CHILDRENS,
  'http://ref.atlasapi.org/genres/atlas/drama'         : genre.DRAMA,
  'http://ref.atlasapi.org/genres/atlas/learning'      : genre.LEARNING,
  'http://ref.atlasapi.org/genres/atlas/music'         : genre.MUSIC,
  'http://ref.atlasapi.org/genres/atlas/news'          : genre.NEWS,
  'http://ref.atlasapi.org/genres/atlas/factual'       : genre.FACTUAL,
  'http://ref.atlasapi.org/genres/atlas/sports'        : genre.SPORTS,
  'http://ref.atlasapi.org/genres/atlas/lifestyle'     : genre.LIFESTYLE,
  'http://ref.atlasapi.org/genres/atlas/animals'       : genre.ANIMALS,
  'http://ref.atlasapi.org/genres/atlas/entertainment' : genre.ENTERTAINMENT,
  'http://ref.atlasapi.org/genres/atlas/film'          : genre.FILM,
  'http://ref.atlasapi.org/genres/atlas/animation'     : genre.ANIMATION,
  'http://pressassociation.com/genres/2000'            : genre.NEWS,
  'http://pressassociation.com/genres/2F02'            : genre.NEWS,
  'http://pressassociation.com/genres/2F03'            : genre.NEWS,
  'http://pressassociation.com/genres/2F04'            : genre.NEWS,
  'http://pressassociation.com/genres/2F05'            : genre.NEWS,
  'http://pressassociation.com/genres/2F06'            : genre.NEWS,
  'http://pressassociation.com/genres/9000'            : genre.FACTUAL,
  'http://pressassociation.com/genres/3100'            : genre.ENTERTAINMENT,
  'http://pressassociation.com/genres/1000'            : genre.FILM,
  'http://pressassociation.com/genres/1400'            : genre.COMEDY,
  'http://pressassociation.com/genres/5000'            : genre.CHILDRENS,
}
def get_genres ( gs ):
  ret = set()
  for g in gs:
    if g in GENRE_MAP:
      ret.add(GENRE_MAP[g])
  return ret

# ###########################################################################
# Process
# ###########################################################################

# Process channel
def process_channel ( data ):
  ret = None
  try:
    c = Channel()
    c.uri     = data['channel_uri']
    c.title   = data['channel_title']
    c.shortid = data['channel_key']
    ret = c
  except Exception, e:
    log.error(str(e))
  return ret

# Process brand
def process_brand ( data ):
  ret = None
  try:
    b = Brand()
    b.uri   = data['uri']
    if 'title'       in data: b.title   = data['title']
    if 'description' in data: b.summary = data['description']
    if 'genres'      in data: b.genres  = get_genres(data['genres'])
    ret = b
  except Exception, e:
    log.error(str(e))
  return ret

# Process series
def process_series ( data ):
  ret = None
  try:
    s = Series()
    s.uri = data['uri']
    if 'title'         in data: s.title   = data['title']
    if 'description'   in data: s.summary = data['description']
    if 'series_number' in data: s.number  = data['series_number']
    if 'genres'        in data: s.genres  = get_genres(data['genres'])
    if s.title:
      r = re.search('Series (.*)', s.title)
      if r:
        s.title = None
        if s.number is None:
          s.number = util.str2num(r.group(1))
    ret = s
  except Exception, e:
    log.error(str(e))
  return ret

# Process credits
def process_people ( data ):
  ret = {}
  for d in data:
    if 'role' in d and 'name' in d:
      p = Person()
      p.uri  = d['uri']
      p.name = d['name']
      p.role = d['role']
      if p.role not in ret:
        ret[p.role] = [ p ]
      else:
        ret[p.role].append(p)
  return ret
 
# Process episode
def process_episode ( data ):
  ret = None
  try:
    e = Episode()
    e.uri   = data['uri']
    if 'title'          in data: e.title   = data['title']
    if 'description'    in data: e.summary = data['description']
    if 'episode_number' in data: e.number  = data['episode_number']
    if 'genres'         in data: e.genres  = get_genres(data['genres'])

    # Brand/Series
    c_uri = None
    s_uri = None
    if 'container' in data and 'uri' in data['container']:
      c_uri = data['container']['uri']
    if 'series_summary' in data and 'uri' in data['series_summary']:
      s_uri = data['series_summary']['uri']
    if c_uri and c_uri != s_uri:
      e.brand  = get_brand(c_uri, data['container'])
    if s_uri:
      e.series = get_series(s_uri, data['series_summary'])

    # Film?
    if 'specialization' in data:
      e.film = data['specialization'] == 'film'
      if 'year' in data:
        e.year = int(data['year'])

    # Black and White?
    if 'black_and_white' in data:
      e.baw = data['black_and_white']

    # People
    # TODO: caching
    if 'people' in data:
      e.credits = process_people(data['people'])

    # Title
    if e.title:
      r = re.search('^Episode (\d+)$', e.title)
      if r:
        e.title = None
        if e.number is None: 
          e.number = util.str2num(r.group(1))
      elif re.search('^\d+/\d+/\d+$', e.title):
        e.title = None

    # OK
    ret = e
    log.info('episode = %s' % e)
 
  except Exception, e:
    log.error(str(e))
  return ret

# Process schedule
def process_schedule ( epg, sched ):
  chn = None

  # Get channel
  if 'channel_uri' in sched:
    chn = get_channel(sched['channel_uri'], sched)

  # Process items
  p = None
  if chn and 'items' in sched:
    for i in sched['items']:
      
      # Get episode
      e = get_episode(i['uri'], i)
      if not e: continue

      # Create schedule
      s = Broadcast()
      s.channel = chn
      s.episode = e
      bc = i['broadcasts'][0]

      # Timing
      s.start = atlas_p_time(bc['transmission_time'])
      s.stop  = atlas_p_time(bc['transmission_end_time'])

      # Zero-length (followed by entry)
      if s.start == s.stop:
        if p: p.followedby = e
        continue
        
      # Metadata
      if 'high_definition' in bc:
        s.hd         = bc['high_definition']
      if 'widescreen' in bc:
        s.widescreen = bc['widescreen']
      if 'premiere' in bc:
        s.premiere   = bc['premiere']
      if 'new_series' in bc:
        s.new        = bc['new_series']
      if 'repeat' in bc:
        s.repeat     = bc['repeat']
      if 'signed' in bc:
        s.signed     = bc['signed']
      if 'subtitled' in bc:
        s.subtitled  = bc['subtitled']
      if 'audio_described' in bc:
        s.audio_desc = bc['audio_described']

      # Add
      epg.add_broadcast(s)
      p = s

# ###########################################################################
# Grabber API
# ###########################################################################

# Grab specified data
def grab ( epg, channels, start, stop ):

  # Config
  key     = conf.get('atlas_apikey', None)
  pubs    = conf.get('atlas_publishers', [ 'pressassociation.com' ])
  anno    = [ 'broadcasts', 'extended_description', 'series_summary',\
              'brand_summary', 'people' ]
  csize   = conf.get('atlas_channel_chunk', len(channels))
  tsize   = conf.get('atlas_time_chunk',    stop-start)

  # Time
  tm_from = time.mktime(start.timetuple())
  tm_to   = time.mktime(stop.timetuple())

  # URL base
  url = 'schedule.json?publisher=%s' % (','.join(pubs))
  if key:  url = url + '&apiKey=' + key
  if anno: url = url + '&annotations=' + ','.join(anno)

  # By time
  while tm_from < tm_to:
    u = url + '&from=%d&to=%d' % (tm_from, min(tm_from + tsize, tm_to))

    # For each channel chunk
    for chns in util.chunk(channels, csize):

      # Fetch data
      u     = u + '&channel=' + ','.join(chns)
      data  = atlas_fetch(u)

      # Processs
      if 'schedule' in data:
        for c in data['schedule']:
          process_schedule(epg, c)

    # Update
    tm_from = tm_from + tsize

# ###########################################################################
# Editor
# ###########################################################################
