#!/usr/bin/env python
#
# pyepg/format/epg.py - PyEPG format
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
This format is somewhat similar to that used by Press Association (I think)
though slightly different to account for the specific requirements I have
and to streamline things where data is repeated.
"""

# ###########################################################################
# Imports
# ###########################################################################

import pyepg.log as log

# ###########################################################################
# Configuration
# ###########################################################################

PYEPG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'

# ###########################################################################
# Output
# ###########################################################################

# Format string
def str_format ( s ):
  s = s.replace('&', '&amp;')
  s = s.encode('utf8')
  return s

# Header
def out_header ( out ):
  print >>out, '<?xml version="1.0" encoding="utf8"?>'
  print >>out, '<!DOCTYPE epg SYSTEM "pyepg.dtd">'
  print >>out, '<epg>'

# Footer
def out_footer ( out ):
  print >>out, '</epg>'

# Channel
def out_channel ( out, chn ):
  print >>out, '  <channel id="%s">' % chn.uri
  print >>out, '    <name>%s</name>' % chn.title
  # TODO: icon?
  print >>out, '  </channel>'

# Brand
def out_brand ( out, brand ):
  print >>out, '  <brand id="%s">' % brand.uri
  if brand.title:
    print >>out, '    <title>%s</title>' % str_format(brand.title)
  if brand.summary:
    print >>out, '    <summary>%s</summary>' % str_format(brand.summary)
  # TODO: series count
  # TODO: icon
  print >>out, '  </brand>'

# Series
def out_series ( out, series ):
  print >>out, '  <series id="%s">' % series.uri
  if series.title:
    print >>out, '    <title>%s</title>' % str_format(series.title)
  if series.summary:
    print >>out, '    <summary>%s</summary>' % str_format(series.summary)
  if series.number is not None:
    print >>out, '    <number>%d</number>' % series.number
  else:
    log.warn('no series number for %s' % series.uri)
  # TODO: episode count
  print >>out, '  </series>'

# Episode
def out_episode ( out, eps ):
  b = s = ''
  if eps.brand:  b = ' brand="%s"' % eps.brand.uri
  if eps.series: s = ' series="%s"' % eps.series.uri
  print >>out, '  <episode id="%s"%s%s>' % (eps.uri, b, s)
  print >>out, '    <title>%s</title>' % str_format(eps.get_title())
  st = eps.get_subtitle()
  if st:
    print >>out, '    <subtitle>%s</subtitle>' % str_format(st)
  su = eps.get_summary()
  if eps.number:
    print >>out, '    <number>%d</number>' % eps.number
  if su:
    print >>out, '    <summary>%s</summary>' % str_format(su)
  for g in eps.get_genres():
    print >>out, '    <genre>%s</genre>' % g
  cs = eps.get_credits()
  if cs:
    print >>out, '    <credits>'
    for r in cs:
      for p in cs[r]:
        try:
          print >>out, '      <%s>%s</%s>' % (r, str_format(p.name), r)
        except Exception, e:
          print e
          try:
            log.debug(repr(p.name))
          except: pass
          try:
            log.debug(repr(str_format(p.name)))
          except: pass
    print >>out, '    </credits>'
  if eps.year and eps.film:
    print >>out, '    <date>%d</date>' % eps.year
  if eps.baw:
    print >>out, '    <blackandwhite />'
  # TODO: icon
  # TODO: hd (as in showing on HD channel at same time)
  print >>out, '  </episode>'
  
# Broadcast
def out_broadcast ( out, bcast ):
  # TODO: specify format!
  f = bcast.start.strftime(PYEPG_TIME_FORMAT)
  t = bcast.stop.strftime(PYEPG_TIME_FORMAT)
  e = bcast.episode.uri
  print >>out, '    <broadcast episode="%s" start="%s" stop="%s">' % (e, f, t)
  if bcast.hd:
    print >>out, '      <hd />'
  if bcast.widescreen or bcast.hd:
    print >>out, '      <widescreen />'
  # TODO: quality and aspect ratio
  if bcast.new:
    print >>out, '      <new />'
  if bcast.premiere:
    print >>out, '      <premiere />'
  if bcast.repeat:
    print >>out, '      <repeat />'
  if bcast.subtitled:
    print >>out, '      <subtitles type="teletext" />'
  if bcast.signed:
    print >>out, '      <subtitles type="deaf-signed" />'
  # TODO: audio described
  # TODO: certification and ratings
  # TODO: image
  print >>out, '    </broadcast>'

# Schedule
def out_schedule ( out, sched, channel ):
  
  # Output broadcasts
  print '  <schedule channel="%s">' % channel.uri
  for b in sched:
    out_broadcast(out, b)
  print '  </schedule>'

# ###########################################################################
# Formatter API
# ###########################################################################

# Output EPG
def format ( epg, out ):
  
  # Header
  out_header(out)

  # Channels
  for c in epg.get_channels():
    out_channel(out, c)

  # Brands
  for b in epg.get_brands():
    out_brand(out, b)

  # Series
  for s in epg.get_series():
    out_series(out, s)

  # Episodes
  for e in epg.get_episodes():
    out_episode(out, e)

  # Schedules
  sc = epg.get_schedule()
  for c in sc:
    out_schedule(out, sc[c], c)

  # Footer
  out_footer(out)
