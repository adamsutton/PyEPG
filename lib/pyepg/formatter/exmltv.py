#!/usr/bin/env python
#
# pyepg/formatter/exmltv.py - "Extended" XMLTV output
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
import sys

# Format string
def xmltv_fmt ( s ):
  ret = s.replace('&', '&amp;')
  try:
    ret = ret.encode(XMLTV_ENCODING)
  except Exception, e: pass
  return ret

# Output channel
def print_channel ( c, out, extended ):
  print >>out, '  <channel id="%s">' % c.uri
  print >>out, '    <display-name>%s</display-name>' % xmltv_fmt(c.title)
  if c.image:
    print >>out, '    <icon src="%s"/>' % c.image
  print >>out, '  </channel>'

# Output episode
def print_episode ( e, out, extended ):
  s   = e
  e   = s.episode
  t1  = s.start.strftime(XMLTV_TIME_FORMAT)
  t2  = s.stop.strftime(XMLTV_TIME_FORMAT)
  print >>out, '  <programme start="%s" stop="%s" channel="%s">'\
               % (t1, t2, s.channel.uri)

  # Brand
  if extended:
    print >>out, '    <uri>%s</uri>' % e.uri
    if e.brand is not None:
      print >>out, '    <brand-uri>%s</brand-uri>' % e.brand.uri
    if e.series is not None:
      print >>out, '    <season-uri>%s</season-uri>' % e.series.uri

  # Title
  t = e.get_title()
  if t:
    print >>out, '    <title>%s</title>' % xmltv_fmt(t)
  st = e.get_subtitle()
  if st:
    print >>out, '    <sub-title>%s</sub-title>' % xmltv_fmt(st)

  # Description
  d = e.get_summary()
  if d:
    print >>out, '    <desc>%s</desc>' % xmltv_fmt(d)
  
  # Credits
  credits = e.get_credits()
  if credits:
    print >>out, '    <credits>'
    for r in [ 'director', 'presenter', 'actor', 'commentator', 'guest' ]:
      if r in credits:
        for p in credits[r]:
          print >>out, '      <%s>%s</%s>' % (r, xmltv_fmt(p.name), r)
    print >>out, '    </credits>'

  # Date
  if e.year is not None:
    print >>out, '    <date>%d</date>' % e.year

  # Genres
  for g in e.get_genres():
    print >>out, '    <category>%s</category>' % g

  # Episode number
  if extended:
    en = ec = sn = sc = pn = pc = 0
    if e.brand  and e.brand.series_count is not None:
      sc = e.brand.series_count
    if e.series and e.series.number is not None:
      sn = e.series.number
    if e.series and e.series.episode_count is not None:
      ec = e.series.episode_count
    if e.number is not None:
      en = e.number
    if en or sn or pn:
      print >>out, '    <episode-num system="pyepg">%d/%d.%d/%d.%d/%d</episode-num>' % (sn, sc, en, ec, 0, 0)
  else:
    n = e.get_number()
    if n:
      ns = n[0]
      if ns is None: ns = 0
      else: ns = ns - 1
      ne = n[1] - 1
      print >>out, '    <episode-num system="xmltv_ns">%d.%d.0</episode-num>' % (ns, ne)
  
  # Video metadata
  print >>out, '    <video>'
  if e.baw:
    print >>out, '      <colour>no</colour>'
  if s.aspect is not None:
    print >>out, '      <aspect>%s</aspect>' % s.aspect
  elif s.widescreen or s.hd:
    print >>out, '      <aspect>16:9</aspect>'
  if s.hd:
    print >>out, '      <quality>HDTV</quality>'
  else:
    print >>out, '      <quality>SDTV</quality>'
  if s.lines:
    print >>out, '      <lines>%d</lines>' % s.lines
  print >>out, '    </video>'

  # History
  if s.repeat:
    print >>out, '    <previously-shown />'
  if s.premiere:
    print >>out, '    <premiere />'
  if s.new:
    print >>out, '    <new />'

  # Hearing / Visually impaired
  if s.subtitled:
    print >>out, '    <subtitles type="teletext" />'
  if s.signed:
    print >>out, '    <subtitles type="deaf-signed" />'
  if s.audio_desc and extended:
    print >>out, '    <audio-described />'

  # TODO: Certification

  # TODO: Ratings

  print >>out, '  </programme>'

def print_header ( out, extended ): 
  gen_date      = str(datetime.datetime.now())
  # TODO: need a way to figure this out properly
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

def print_footer (out, extended):
  print >>out, '</tv>\n'

# ###########################################################################
# Formatter API
# ###########################################################################

def format ( epg, out, extended = True ):
  print_header(out, extended)
  for c in epg.get_channels():
    print_channel(c, out, extended)
  sched = epg.get_schedule()
  for c in sched:
    for e in sched[c]:
      print_episode(e, out, extended)
  print_footer(out, extended)

# ###########################################################################
# Editor
# ###########################################################################
