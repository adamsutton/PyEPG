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

# ###########################################################################
# Config/State
# ###########################################################################

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

# ###########################################################################
# Cache API
# ###########################################################################

# Initialise
def init ( path ):
  
  # Create path
  if not os.path.exists(path):
    os.makedirs(path)

  # Initialise database
  db_init(path)

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
