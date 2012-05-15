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
# URL fetching
# ###########################################################################

#
# Fetch a URL
#
# @param cache If True attempt to retrieve/store the data in the local cache
# @param ttl   If local cache file is newer than ttl, don't bother to check
#              remote object at all
def get_url ( url, cache = True, ttl = 0 ):
  global CACHE_PATH
  import urllib2, urlparse, time
  log.debug('cache: get url %s' % url, 1)
  ret = None

  # Create directories
  urlp = urlparse.urlparse(url)
  path = os.path.join(CACHE_PATH, 'url', urlp.netloc, urlp.path[1:])
  head = path + '.head'

  # Don't cache dynamic requests
  if urlp.params or urlp.query: cache = False

  # Create request
  req  = urllib2.Request(url)
  req.add_header('User-Agent', 'PyEPG URL Fetcher/Cacher')

  # File exists (check header)
  if os.path.exists(path) and cache:
    try:
      ok   = False
      st   = os.stat(path)
      meta = eval(open(head).read())

      # TTL?
      if (st.st_mtime + ttl) > time.time():
        log.debug('cache: ttl still valid', 2)
        ok = True

      # Check modification time
      else:
      
        # Fetch remote headers
        req.get_method = lambda: 'HEAD'
        up   = urllib2.urlopen(req)

        # Static page unmodded
        if 'last-modified' in up.headers and 'last-modified' in meta and\
          up.headers['last-modified'] == meta['last-modified']:
          log.debug('cache: last-modified matches', 2)
          ok = True

        # Update timestamp
        os.utime(path, None)

      # Use local
      if ok:
        tmp = open(path).read()
      
        # Validate object
        if 'md5' in meta and meta['md5'] == md5(tmp):
          log.debug('cache: local data ok', 1)
          ret = tmp
        else:
          log.debug('cache: local md5 mismatch', 2)

    except Exception, e:
      log.error('cache: local failure [e=%s]' % e)

  # Fetch
  if not ret:
    log.debug('cache: fetch remote', 1)
    req.get_method = lambda: 'GET'
    up   = urllib2.urlopen(req)
    ret  = up.read()

    if cache:
      meta = {}
      for k in up.headers:
        meta[k.lower()] = up.headers[k]
      meta['md5'] = md5(ret)
      if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
      open(path, 'w').write(ret)
      open(head, 'w').write(repr(meta))
  
  return ret

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

# Fetch file from cache
def get_file ( path, maxage = None ):
  import time
  log.debug('cache: get file %s' % path, 1)
  ret = None
  p   = os.path.join(CACHE_PATH, 'files', path)
  if os.path.isfile(p):
    s = os.stat(p)
    if (maxage is None) or ((time.time() - s.st_mtime) < maxage):
      ret = open(p).read()
  if not ret: log.debug('cache: not available', 1)
  return ret

# Store file
def put_file ( path, data ):
  log.debug('cache: put file %s' % path, 1)
  p = os.path.join(CACHE_PATH, 'files', path)
  d = os.path.dirname(p)
  if not os.path.isdir(d): os.makedirs(d)
  open(p, 'w').write(data)

# ###########################################################################
# Editor
# ###########################################################################
