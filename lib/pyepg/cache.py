#!/usr/bin/env python
#
# pyepg/cache.py - Configuration
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
import os
import sqlite3 as sqlite

# PyEPG
import pyepg.conf as conf
import pyepg.log  as log

# ###########################################################################
# Config/State
# ###########################################################################

CACHE_PATH       = None
CACHE_DB_VERSION = 1
CACHE_DB_CONN    = None
CACHE_DB_DATA    = {
  'uri_map' : {},
  'channel' : {},
  'brand'   : {},
  'series'  : {},
  'episode' : {},
}

PYEPG_USER_AGENT = 'PyEPG URL Fetcher/Cacher'

# ###########################################################################
# Cache API
# ###########################################################################

# Initialise
def init ( path ):
  global CACHE_PATH
  CACHE_PATH = path
  
  # Create path
  if not os.path.exists(path):
    os.makedirs(path)

  # Initialise database
  db_init(path)

# Create MD5 of an object
def md5 ( obj ):
  import md5
  tmp = md5.new()
  tmp.update(str(obj))
  return tmp.hexdigest()

# ###########################################################################
# DB
# ###########################################################################

# Run SQL
def db_sql ( sql, conn = None ):

  # Default
  if conn is None: conn = CACHE_DB_CONN

  # Execute

# Create database
def db_init ( path ):
  
  # Check version
  db_conn = None
  db_ver  = None
  db_path = os.path.join(path, 'cache.db')
  try:
    if os.path.exists(db_path):
      db_conn = sqlite.connect(db_path)
      sql = 'select value from metadata where key="version"'
      cur = db_conn.cursor()
      cur.execute(sql)
      res = cur.fetchall()
      if res: db_ver = int(res[0][0])
  except Exception, e:
    log.error('failed to check DB version: %s' % str(e))

  # Invalid version
  if db_ver != CACHE_DB_VERSION:

    # Initialise
    if db_conn:
      db_conn.close()
      os.unlink(db_path)
    db_conn = sqlite.connect(db_path)
    cur = db_conn.cursor()

    # Metadata table
    sql = 'create table metadata (key text, value text)'
    cur.execute(sql)
    sql = 'insert into metadata values ("version", "%d")' % CACHE_DB_VERSION
    cur.execute(sql)

    # URI mappings
    sql = 'create table uri_map (uri_virt text, uri_real text)'
    cur.execute(sql)

    # Brand table
    sql = 'create table brand (uri text, title text, summary text)'
    cur.execute(sql)

    # Series table
    sql = 'create table series (uri text, title text, summary text, number int)'
    cur.execute(sql)

    # Commit
    db_conn.commit()

  # Done
  global CACHE_DB_CONN
  CACHE_DB_CONN = db_conn

# ###########################################################################
# File fetching
# ###########################################################################

#
# Fetch a file from the cache
#
def _get_file ( name, ttl = None ):
  import time
  log.debug('cache: get file %s' % name, 3)
  ok    = False
  data  = None
  meta  = None
  valid = False
  path  = CACHE_PATH + os.path.sep + name

  # Default TTL
  if ttl is None: ttl = conf.get('default_cache_ttl', 7*86400)

  # Check age
  if os.path.exists(path) and os.path.exists(path + '.meta'):
    log.debug('cache: %s in cache' % name, 4)
    st   = os.stat(path)
    meta = eval(open(path + '.meta').read())
    data = open(path).read()

    # OK
    if (st.st_mtime + ttl) > time.time():
      log.debug('cache: %s ttl ok' % name, 4)
      ok = True
    
    # TTL passed
    else:
      log.debug('cache: %s ttl expired' % name, 4)

    # Validate
    if 'md5' in meta and meta['md5'] == md5(data):
      log.debug('cache: %s md5 ok' % name, 4)
      valid = True
    else:
      log.debug('cache: %s md5 mismatch' % name)

  # Return data
  return (data, meta, ttl, valid)

#
# Fetch a file from the cache (only return data)
#
def get_file ( name, ttl = None ):
  ret = None
  (data, meta, ttl, valid) = _get_file(name, ttl)
  if data and meta and ttle and valid:
    ret = data
  return ret

#
# Put file in the cache
#
def put_file ( name, data, imeta = {} ):
  log.debug('cache: put file %s' % name, 3)
  ret = None

  # Fix meta (use lower case keys)
  meta = {}
  for k in imeta: meta[k.lower()] = imeta[k]

  # Add MD5
  if 'md5' not in meta:
    meta['md5'] = md5(data)

  # Store
  path = CACHE_PATH + os.path.sep + name
  if not os.path.exists(os.path.dirname(path)):
    os.makedirs(os.path.dirname(path))
  open(path, 'w').write(data)
  open(path + '.meta', 'w').write(repr(meta))
  log.debug('cache: file %s stored' % name)

#
# Touch a file in the cache (update TTL)
#
def touch_file ( name ):
  log.debug('cache: touch %s' % name)
  path = CACHE_PATH + os.path.sep + name
  if os.path.exists(path):
    os.utime(path, None)

# ###########################################################################
# URL fetching
# ###########################################################################

#
# Fetch a URL
#
# @param cache If True attempt to retrieve/store the data in the local cache
# @param ttl   If local cache file is newer than ttl, don't bother to check
#              remote object at all
# @param conn  Persistent connection (created externally)
def get_url ( url, cache = True, ttl = 0, conn = None ):
  import urllib2, urlparse
  log.debug('cache: get url %s' % url, 3)
  ret = None

  # Create directories
  urlp = urlparse.urlparse(url)
  path = urlp.netloc + os.path.sep + urlp.path[1:]
  http = urlp.scheme in [ 'http', 'https' ]

  # Don't cache dynamic requests
  if urlp.params or urlp.query: cache = False

  # Create request
  req  = urllib2.Request(url)
  req.add_header('User-Agent', PYEPG_USER_AGENT)

  # Check cache
  if cache:
    (data, meta, ttl, md5) = _get_file(path, ttl=ttl)

    # OK
    if data and meta and md5:

      # Check remote headers
      if not ttl:
        head = {}

        # Fetch remote headers
        if http and conn:
          log.debug('cache: use persistent connection', 5)
          conn.request('GET', url, None, {'User-Agent':PYEPG_USER_AGENT})
          h = conn.getresponse().getheaders()
          for (k,v) in h: head[k.lower()] = v
        else:
          req.get_method = lambda: 'HEAD'
          up   = urllib2.urlopen(req, timeout=60.0)
          head = up.headers

        # Static page unmodded
        if 'last-modified' in head and 'last-modified' in meta and\
          head['last-modified'] == meta['last-modified']:
          log.debug('cache: last-modified matches', 4)
          ret = data

          # Update timestamp
          touch_file(path)

      # OK
      else:
        ret = data

  # Fetch
  if not ret:
    log.debug('cache: fetch remote', 1)
    head = {}
    if http and conn:
      log.debug('cache: use persistent connection', 5)
      conn.request('GET', url, None, {'User-Agent':PYEPG_USER_AGENT})
      r   = conn.getresponse()
      for (k,v) in r.getheaders(): head[k.lower()] = v
      ret = r.read()
    else:
      req.get_method = lambda: 'GET'
      up   = urllib2.urlopen(req, timeout=60.0)
      ret  = up.read()
      head = up.headers

    # Store
    if cache:
      put_file(path, ret, head)
  
  return ret

#
# Get PyEPG hosted data
#
def get_data ( name, ttl = None ):
  url = conf.get('data_url', 'http://cloud.github.com/downloads/adamsutton/PyEPG')
  return get_url(url + '/' + name, True, ttl)

# ###########################################################################
# EPG data
# ###########################################################################

# Get object
def get_object ( uri, type, db = True ):
  ret = None
  if type in CACHE_DB_DATA and uri in CACHE_DB_DATA[type]:
    ret = CACHE_DB_DATA[type][uri]
  else:
    sql = 'select * from %s' % type
    #cur = CACHE_DB_CONN.cursor()
    #cur.execute(sql)
    #res = cur.fetchall()
    #if res: res = res[0] 
    # TODO
  return ret

# Put object
def put_object ( uri, obj, type, db = True ):
  if type in CACHE_DB_DATA:
    CACHE_DB_DATA[type][obj.uri] = obj


# Get channel
def get_channel ( uri ):
  return get_object(uri, 'channel', False)

# Get brand
def get_brand ( uri ):
  return get_object(uri, 'brand')

# Get series
def get_series ( uri ):
  return get_object(uri, 'series')
  
# Get episode
def get_episode ( uri ):
  return get_object(uri, 'episode', False)

# Put channel
def put_channel ( uri, channel ):
  put_object(uri, channel, 'channel', False)

# Put brand
def put_brand ( uri, brand ):
  put_object(uri, brand, 'brand')

# Put series
def put_series ( uri, series ):
  put_object(uri, series, 'series')

# Put episode
def put_episode ( uri, episode ):
  put_object(uri, episode, 'episode', False)


# ###########################################################################
# Editor
# ###########################################################################
