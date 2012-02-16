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

import datetime

# ###########################################################################
# Config
# ###########################################################################

XMLTV_TIME_FORMAT = '%Y%m%d%H%M%S %z'
XMLTV_ENCODING    = 'utf8'

# ###########################################################################
# Output routines
# ###########################################################################

def print_channel ( c, out ):
  print >>out, '  <channel id="%s">' % c.uri
  print >>out, '    <display-name>%s</display-name>' % c.title
  print >>out, '  </channel>'

def print_episode ( e, out ):
  t1  = e.start.strftime(XMLTV_TIME_FORMAT)
  t2  = e.stop.strftime(XMLTV_TIME_FORMAT)
  print >>out, '  <programme start="%s" stop="%s" channel="%s">'\
               % (t1, t2, e.channel.uri)
  e = e.episode
  t = e.get_title()
  if t:
    t = t.encode(XMLTV_ENCODING)
    print >>out, '    <title>%s</title>' % t
  s = e.get_subtitle()
  if s:
    s = s.encode(XMLTV_ENCODING)
    print >>out, '    <sub-title>%s</sub-title>' % s
  d = e.get_summary()
  if d:
    d = d.encode(XMLTV_ENCODING)
    print >>out, '    <desc>%s</desc>' % d
  n = e.get_number()
  if n:
    print >>out, '    <episode-num system="xmltv_ns">%d.%d.%d</episode-num>'\
                 % (n[0], n[1], n[2])
  print >>out, '  </programme>'

def print_header ( out ): 
  gen_date      = str(datetime.datetime.now())
  gen_src_url   = 'http://atlas.metabroadcast.com/3.0'
  gen_src_name  = 'Atlas Metabroadcast System'
  gen_info_url  = ''
  gen_info_name = 'PyEPG Atlas Grabber'
  print >>out, '<?xml version="1.0" encoding="%s"?>' % XMLTV_ENCODING
  print >>out, '<!DOCTYPE tv SYSTEM "xmltv.dtd">'
  print >>out, ''
  print >>out, ('<tv date="%s" source-info-url="%s" source-info-name="%s" '\
        + ' generator-info-name="%s" generator-info-url="%s">')\
        % (gen_date, gen_src_url, gen_src_name, gen_info_name, gen_info_url)

def print_footer (out):
  return >>out, '</tv>\n'

# ###########################################################################
# Formatter API
# ###########################################################################

def format ( epg, out ):
  print_header(out)
  for c in epg.get_channels():
    print_channel(c, out)
  sched = epg.get_schedule()
  for c in sched:
    for e in sched[c]:
      print_episode(e, out)
  print_footer(out)

# ###########################################################################
# Editor
# ###########################################################################
