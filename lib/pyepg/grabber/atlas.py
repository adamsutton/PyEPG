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
from threading import Thread

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
  jdata = {}
  url   = 'http://atlas.metabroadcast.com/3.0/' + url
  log.debug('fetch %s' % url, 0)
  
  # Can fail occasionally - give more than 1 attempt
  for i in range(5):
    try:
      data = cache.get_url(url, cache=False)
      log.debug('decode json', 1)
      jdata = json.loads(data)
      log.debug(jdata, 1, pprint=True)
      break
    except Exception, e:
      log.warn('failed to fetch %s [e=%s]' % (url, e))
      pass
    time.sleep(i+1.0) # increase delay each time
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
  log.debug('get_brand(%s)' % uri, 2)

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
  log.debug('get_series(%s)' % uri, 2)

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
  log.debug('get_episode(%s)' % uri, 2)

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
  log.debug('get_channel(%s)' % uri, 2)

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
    if 'title' in data:
      c.title = data['title'].encode('utf8')
    elif 'channel_title' in data:
      c.title = data['channel_title'].encode('utf8')
    if 'uri' in data:
      c.uri   = data['uri']
    elif 'channel_uri' in data:
      c.uri   = data['channel_uri']
    if 'channel_key' in data:
      c.shortid = data['channel_key']
    elif 'id' in data:
      c.shortid = data['id']
    if 'broadcaster' in data and 'key' in data['broadcaster']:
      c.publisher.append(data['broadcaster']['key'])
    if 'media_type' in data:
      c.radio = data['media_type'] == 'audio'
    c.hd      = 'HD' in c.title
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
  # TODO: caching
  ret = {}
  for d in data:
    if 'role' in d and 'name' in d:
      p = Person()

      # Extract
      p.uri  = d['uri']
      p.name = d['name']
      p.role = d['role']
      if 'character' in d:
        p.character = d['character']

      # Process (PA has some strange ideas)
      if p.character:
        if p.character in [ 'Presenter', 'Host', 'Commentator' ]:
          p.role      = 'presenter'
          p.character = None
        elif p.character in [ 'Narrator', 'Reader' ]:
          p.role      = 'narrator'
          p.character = None
        elif 'Guest' in p.character or\
             p.character in [ 'Contributor', 'Performer' ]:
          p.role      = 'guest'
          p.character = None

      # Some atlas mappings (simplifications)
      if p.role in [ 'commentator', 'reporter' ]:
        p.role = 'presenter'
      if p.role in [ 'export', 'participant' ]:
        p.role = 'guest'

      # Store
      if p.role not in ret:
        ret[p.role] = [ p ]
      else:
        ret[p.role].append(p)
  return ret

# Process episode
def process_episode ( data ):
  e = Episode()
  e.uri   = data['uri']
  if 'title'          in data: e.title   = data['title']
  if 'description'    in data: e.summary = data['description']
  if 'episode_number' in data: e.number  = data['episode_number']
  if 'genres'         in data: e.genres  = get_genres(data['genres'])

  # Media type (ignore virtual entries)
  if 'schedule_only' not in data or not data['schedule_only']:
    if 'media_type'     in data: e.media   = data['media_type']

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
    # complete the link
    if e.series and e.brand:
      e.series.brand = e.brand

  # Film?
  if 'specialization' in data:
    e.film = data['specialization'] == 'film'
    if 'year' in data:
      e.year = int(data['year'])

  # Black and White?
  if 'black_and_white' in data:
    e.baw = data['black_and_white']

  # People
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
  log.debug('episode = %s' % e, 3)
  return e

# Process schedule
def process_schedule ( epg, chn, sched ):
  p = None

  # Process items
  for i in sched:

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
      s.hd         = chn.hd and bc['high_definition']
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

    # Special fields (Note: not valid outside of UK?)
    if s.widescreen or s.hd: s.aspect = '16:9'
    if s.hd: s.lines = 1080
    else:    s.lines = 576

    # Add
    epg.add_broadcast(s)
    p = s

#
# Overlay two publisher entries
#
def publisher_overlay ( a, b, pubs ):
  pa   = a['publisher']['key']
  pb   = b['publisher']['key']
  log.debug('publishers a=%s, b=%s' % (pa, pb), 5)
  ia   = -1
  ib   = -1
  try:
    ia = pubs.index(pa)
  except: pass
  try:
    ib = pubs.index(pb)
  except: pass
  def _overlay ( a, b ):
    if type(b) == dict:
      for k in b:
        if k not in a:
          a[k] = b[k]
        else:
          a[k] = _overlay(a[k], b[k])
      return a
    elif type(b) == list:
      for i in range(len(b)):
        if i < len(a):
          a[i] = _overlay(a[i], b[i])
        else:
          a.append(b[i])
      return a
    else:
      return b
  ret = None
  if ib > ia:
    log.debug('prefer publisher a', 5)
    ret = _overlay(b, a)
  else:
    log.debug('prefer publisher b', 5)
    ret = _overlay(a, b)
  return ret

# Process publisher overlap
#
def process_publisher_overlay ( sched, pubs ):
  ret = []
  s   = sched
  g   = []
  for i in range(len(s)):
    if i in g: continue
    g.append(i)
    a = s[i]
    t = []
    for j in range(i, len(s)):
      if j in g: continue
      b = s[j]
      if a['broadcasts'][0]['transmission_time'] == b['broadcasts'][0]['transmission_time']:
        t.append(b)
        g.append(j)
    for k in t:
      a = publisher_overlay(a, k, pubs)
    ret.append(a)
  return ret

# Get title mappings
def get_title_map ():
  ret  = {}
  data = cache.get_file('atlas/title_map.csv')
  if data:
    for l in data.splitlines():
      p = map(lambda x: x.strip(), l.split(','))
      if len(p) == 2 and p[1]:
        ret[p[0]] = p[1]
  return ret

# Fetch channel metadata
def _load_channels ():
  ret = []
  log.info('get atlas channel list')

  # Check cache (only update monthly)
  data = cache.get_file('atlas/channels.json', 31*86400)
  print data

  # Fetch
  if not data:
    log.info('fetcing remote data')
    data = []

    # URL setup
    limit    = 50
    offset   = 0
    url_root = ('channels.json?limit=%d' % limit) + '&offset=%d'

    # Query
    while True:
      temp   = atlas_fetch(url_root % offset)
      offset = offset + limit
      if 'channels' not in temp: break
      if not temp['channels']: break
      data.append(temp)

    # Store
    if data:
      cache.put_file('atlas/channels.json', json.dumps(data))

  # Unpack
  else:
    data = json.loads(data)

  # Channel title mappings
  title_map = get_title_map()

  # Process
  for i in data:
    if 'channels' in i:
      for c in i['channels']:
        c = get_channel(c['uri'], c)
        if c:
          if c.title in title_map:
            log.debug('atlas: title %s -> %s' % (c.title, title_map[c.title]), 2)
            c.title = title_map[c.title]
          ret.append(c)

  log.info('  channel list grabbed')
  return ret

# Load channels
def load_channels ():
  ret = set()
  log.info('get atlas channel list')

  # Process
  data = cache.get_data('atlas_channels.csv')
  if data:
    for l in data.splitlines():
      p = map(lambda x: x.strip(), l.split(','))
      if len(p) < 3: continue
      c = Channel()
      c.uri       = p[0]
      c.shortid   = p[1]
      c.publisher = [ p[3] ]
      ret.add(c)
  return ret


# Filter the channels
def filter_channels ( channels ):
  chns       = []
  atlas_chns = load_channels()
  for t in channels:
    ok = False
    for c in atlas_chns:
      if c.uri == t.uri:
        t.shortid   = c.shortid
        t.publisher = c.publisher
        chns.append(t)
        ok = True
        break

    if not ok:
      log.warn('unable to find EPG info for %s' % t.uri)
  return chns

# Group channels by primary publisher
def group_channels_by_pub ( chns ):
  ret = {}
  for c in chns:
    p = None
    if c.publisher: p = c.publisher[0]
    if p not in ret:
      ret[p] = []
    ret[p].append(c)
  return ret

# ###########################################################################
# Grab thread
# ###########################################################################

class GrabThread ( Thread ):

  def __init__ ( self, idx, epg, channels, start, stop ):
    Thread.__init__(self)
    self._idx   = idx
    self._epg   = epg
    self._chns  = channels
    self._start = start
    self._stop  = stop

  def run ( self ):

    # Config
    key    = conf.get('atlas_apikey', None)
    p_pubs = conf.get('atlas_primary_publishers',\
                      [ 'bbc.co.uk', 'itv.com' 'tvblob.com',\
                        'channel4.com' ])
    s_pubs = conf.get('atlas_secondary_publishers',\
                      [ 'pressassociation.com' ])
    anno   = [ 'broadcasts', 'extended_description', 'series_summary',\
               'brand_summary', 'people' ]
    csize  = conf.get('atlas_channel_chunk', len(self._chns))
    tsize  = conf.get('atlas_time_chunk',    self._stop - self._start)

    # Time
    tm_from = time.mktime(self._start.timetuple())
    tm_to   = time.mktime(self._stop.timetuple())

    # URL base
    url = 'schedule.json?'
    url = url + 'annotations=' + ','.join(anno)
    if key:  url = url + '&apiKey=' + key

    # Channel at a time
    for c in self._chns:
      log.info('atlas - thread %3d fetch   %s' % (self._idx, c.title))
      sched = []

      # By time
      tf = tm_from
      while tf < tm_to:
        tt = min(tf + tsize, tm_to)
        a  = (time.strftime('%Y-%m-%d %H:%M', time.localtime(tf)),\
              time.strftime('%Y-%m-%d %H:%M', time.localtime(tt)))
        #log.info('atlas -     period %s to %s' % a)

        # For each publisher
        pubs = set(c.publisher)
        pubs.intersection_update(p_pubs)
        pubs.update(s_pubs)
        for p in pubs:
          #log.info('atlas -       publisher %s' % p)
          u = url + '&from=%d&to=%d' % (tf, tt)
          u = u + '&publisher=' + p
          u = u + '&channel_id=' + c.shortid

          # Fetch data
          data  = atlas_fetch(u)

          # Processs
          if 'schedule' in data:
            for s in data['schedule']:
              if 'items' in s:
                sched.extend(s['items'])

        # Update
        tf = tf + tsize

      # Process overlays
      log.info('atlas - thread %3d process %s' % (self._idx, c.title))
      sched = process_publisher_overlay(sched, pubs)

      # Process into EPG
      process_schedule(self._epg, c, sched)

# ###########################################################################
# Grabber API
# ###########################################################################

# Grab specified data
def grab ( epg, channels, start, stop ):

  # Filter the channel list (only include those we have listing for)
  channels = filter_channels(channels)
  days     = (stop - start).total_seconds() / 86400
  channels = sorted(channels, cmp=lambda a,b: cmp(a.number,b.number))
  log.info('atlas - epg grab %d channels for %d days' % (len(channels), days))

  # Config
  thread_count = conf.get('atlas_thread_limit',  32)
  if thread_count <= 0:
    thread_count = len(channels)
  else:
    thread_count = min(thread_count, len(channels))

  # Split channels (for thread)
  threads = []
  for chns in util.chunk2(channels, thread_count):

    # Create thread
    t = GrabThread(len(threads), epg, chns, start, stop)
    t.setDaemon(True)
    threads.append(t)

    log.info('atlas - thread %3d' % len(threads))
    for c in chns: log.info('atlas -   %s' % c.title)

  # Start threads
  for t in threads: t.start()

  # Wait for all threads to complete
  while threads:
    wait = True
    for i in range(len(threads)):
      if not threads[i].isAlive():
        log.info('atlas - thread %3d complete (%3d/%3d remain)'\
                 % (threads[i]._idx, len(threads)-1, thread_count))
        threads.pop(i)
        wait = False
        break
    if wait: time.sleep(1.0)

# Get a list of the support packages
def packages ():
  from pyepg.package\
  import uk_freetoairsathd, uk_freetoairsat, uk_freesathd, uk_freesat
  return [ uk_freesathd, uk_freesat, uk_freetoairsathd, uk_freetoairsat ]

# Get a list of available channels
def channels ():
  return load_channels()

# Configure
def configure ():
  print ''
  print 'Atlas Configuration'
  print '-' * 60

  # API key
  apikey = conf.get('atlas_apikey', '')
  print ''
  print 'API Key [%s]: ' % apikey,
  apikey = sys.stdin.readline().strip()
  if apikey: conf.set('atlas_apikey', apikey)

  # Publishers to be used
  p_pubs = [ 'bbc.co.uk', 'five.tv', 'channel4.com', 'itv.com', 'tvblob.com' ]
  s_pubs = [ 'pressassociation.com' ]
  conf.set('atlas_primary_publishers',   conf.get('atlas_primary_publishers', p_pubs))
  conf.set('atlas_secondary_publishers', conf.get('atlas_secondary_publishers', s_pubs))

  # Hidden settings
  conf.set('atlas_channel_chunk', conf.get('atlas_channel_chunk', 32))
  conf.set('atlas_time_chunk',    conf.get('atlas_time_chunk', 86400))

# ###########################################################################
# Editor
# ###########################################################################
