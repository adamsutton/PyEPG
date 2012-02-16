#!/usr/bin/env python
#
# pyepg/format/test.py - Test formatter
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

import pyepg.log as log

# ###########################################################################
# Config
# ###########################################################################

# ###########################################################################
# Formatter API
# ###########################################################################

def format ( epg, out ):

  for c in epg.get_channels():
    print >>out, '<channel uri="%s">' % c.uri
    print >>out, '  <title>%s</title>' % c.title
    print >>out, '</channel>'
  for b in epg.get_brands():
    print >>out, '<brand uri="%s">' % b.uri
    if b.title:   print >>out, '  <title>%s</title>' % b.title
    if b.summary: print >>out, '  <summary>%s</summary>' % b.summary.encode('utf8')
    print >>out, '</brand>'
  for s in epg.get_series():
    print >>out, '<series uri="%s">' % s.uri
    if s.title:   print >>out, '  <title>%s</title>' % s.title
    if s.summary: print >>out, '  <summary>%s</summary>' % s.summary.encode('utf8')
    if s.number is not None:  print >>out, '  <number>%d</number>' % s.number
    else:
      log.warn('no series number for %s' % s.uri)
    print >>out, '</series>'
  for e in epg.get_episodes():
    b = ''
    if e.brand:  b = ' brand="%s"' % e.brand.uri
    s = ''
    if e.series: s = ' series="%s"' % e.series.uri
    print >>out, '<episode uri="%s"%s%s>' % (e.uri, b, s)
    print >>out, '  <title>%s</title>' % e.get_title()
    st = e.get_subtitle()
    if st: print >>out, '  <subtitle>%s</subtitle>' % st
    if e.number is not None: print >>out, '  <number>%d</number>' % e.number
    print '</episode>'
  sched = epg.get_schedule()
  sc    = 0
  for c in sched:
    for s in sched[c]:
      print >>out, '<schedule channel="%s" episode="%s">' % (s.channel.uri, s.episode.uri)
      print >>out, '  <start>%s</start>' % str(s.start)
      print >>out, '  <stop>%s</stop>' % str(s.stop)
      sc = sc + 1
      print >>out, '</schedule>'
  
  # Stats
  print >>out, 'Channel  Count: %d' % len(epg.get_channels())
  print >>out, 'Brand    Count: %d' % len(epg.get_brands())
  print >>out, 'Series   Count: %d' % len(epg.get_series())
  print >>out, 'Episode  Count: %d' % len(epg.get_episodes())
  print >>out, 'Schedule Count: %d' % sc
