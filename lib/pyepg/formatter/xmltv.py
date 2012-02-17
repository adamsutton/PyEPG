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
  s   = e
  e   = s.episode
  t1  = s.start.strftime(XMLTV_TIME_FORMAT)
  t2  = s.stop.strftime(XMLTV_TIME_FORMAT)
  print >>out, '  <programme start="%s" stop="%s" channel="%s">'\
               % (t1, t2, s.channel.uri)

  # Title
  t = e.get_title()
  if t:
    t = t.encode(XMLTV_ENCODING)
    print >>out, '    <title>%s</title>' % t
  st = e.get_subtitle()
  if st:
    st = st.encode(XMLTV_ENCODING)
    print >>out, '    <sub-title>%s</sub-title>' % st

  # Description
  d = e.get_summary()
  if d:
    d = d.encode(XMLTV_ENCODING)
    print >>out, '    <desc>%s</desc>' % d
  
  # Credits
  credits = e.get_credits()
  if credits:
    print >>out, '    <credits>'
    for r in [ 'director', 'presenter', 'actor', 'commentator', 'guest' ]:
      if r in credits:
        for p in credits[r]:
          n = p.name.encode(XMLTV_ENCODING)
          print >>out, '      <%s>%s</%s>' % (r, n, r)
    print >>out, '    </credits>'

  # Date
  if e.year is not None:
    print >>out, '    <date>%d</date>' % e.year

  # Genres
  for g in e.get_genres():
    print >>out, '    <category>%s</category>' % g

  # Episode number
  n = e.get_number()
  if n:
    ns = n[0]
    if ns is None: ns = 0
    ne = n[1]
    print >>out, '    <episode-num system="xmltv_ns">%d.%d.0</episode-num>' % (ns, ne)
  
  # Video metadata
  print >>out, '    <video>'
  if e.baw:
    print >>out, '      <colour>no</colour>'
  if s.widescreen or s.hd:
    print >>out, '      <aspect>16:9</aspect>'
  if s.hd:
    print >>out, '      <quality>HDTV</quality>'
  else:
    print >>out, '      <quality>SDTV</quality>'
  print >>out, '    </video>'

  # History
  if s.repeat:
    print >>out, '    <previously-shown />'
  if s.premiere:
    print >>out, '    <premiere />'
  if s.new:
    print >>out, '    <new />'

  # ???
  if s.subtitled:
    print >>out, '    <subtitles type="teletext" />'
  if s.signed:
    print >>out, '    <subtitles type="deaf-signed" />'

  # TODO: Certification

  # TODO: Ratings

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
  print >>out, '</tv>\n'

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
