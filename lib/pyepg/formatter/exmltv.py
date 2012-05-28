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

from pyepg._xml import Document, Element
import pyepg.util as util

# ###########################################################################
# Config
# ###########################################################################

XMLTV_TIME_FORMAT = '%Y%m%d%H%M%S %z'
XMLTV_ENCODING    = 'utf8'

# ###########################################################################
# Output routines
# ###########################################################################
import sys

# Output channel
def out_channel ( xml, c, extended = False ):
  ele = Element('channel', id=c.uri)
  ele.addChild(Element('display-name', c.title))
  if c.image:
    ele.addChild(Element('icon', src=c.image))
  xml.addChild(ele)

# Output episode
def out_episode ( xml, e, extended = False ):
  s   = e
  e   = s.episode
  t1  = s.start.strftime(XMLTV_TIME_FORMAT)
  t2  = s.stop.strftime(XMLTV_TIME_FORMAT)
  ele = Element('programme', start=t1, stop=t2, channel=s.channel.uri)

  # Extended attributes
  if extended:
    ele.addChild(Element('uri', e.uri))
    if e.brand is not None:
      ele.addChild(Element('brand-uri', e.brand.uri))
    if e.series is not None:
      ele.addChild(Element('season-uri', e.series.uri))

  # Title/Sub-title
  t  = e.get_title()
  st = e.get_subtitle()
  if t:
    ele.addChild(Element('title', t))
  if st:
    ele.addChild(Element('sub-title', st))

  # Description
  d = e.get_summary()
  if d:
    ele.addChild(Element('desc', d))

  # Credits
  credits = e.get_credits()
  if credits:
    cre = Element('credits')
    for r in [ 'director', 'presenter', 'actor', 'commentator', 'guest' ]:
      if r in credits:
        for p in credits[r]:
          cre.addChild(Element(r, p.name))
    ele.addChild(cre)

  # Date
  if e.year is not None:
    ele.addChild(Element('date', e.year))

  # Genres
  for g in e.get_genres():
    ele.addChild(Element('category', g))

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
    if e.part_num is not None:
      pn = e.part_num
    if e.part_cnt is not None:
      pc = e.part_cnt
    if en or sn or pn:
      cdata = '%d/%d.%d/%d.%d/%d' % (sn, sc, en, ec, pn, pc)
      ele.addChild(Element('episode-num', cdata, system='pyepg'))
  else:
    n = e.get_number()
    if n:
      ns = n[0]
      if ns is None: ns = 0
      else: ns = ns - 1
      ne = n[1] - 1
      cdata = '%d.%d.0' % (ns, ne)
      ele.addChild(Element('episode-num', cdata, system='xmltv_ns'))

  # Video metadata
  vid = Element('video')
  if e.baw:
    vid.addChild(Element('colour', 'no'))
  if s.aspect is not None:
    vid.addChild(Element('aspect', s.aspect))
  elif s.widescreen or s.hd:
    vid.addChild(Element('aspect', '16:9'))
  if s.hd:
    vid.addChild(Element('quality', 'HDTV'))
  else:
    vid.addChild(Element('quality', 'SDTV'))
  if extended and s.lines:
    vid.addChild(Element('lines', s.lines))
  ele.addChild(vid)

  # History
  if s.repeat:
    ele.addChild(Element('previously-shown'))
  if s.premiere:
    ele.addChild(Element('premiere'))
  if s.new:
    ele.addChild(Element('new'))

  # Hearing / Visually impaired
  if s.subtitled:
    ele.addChild(Element('subtitles', type='teletext'))
  if s.signed:
    ele.addChild(Element('subtitles', type='deaf-signed'))
  if s.audio_desc and extended:
    ele.addChild(Element('audio-described'))

  # TODO: Certification

  # TODO: Ratings

  # Done
  xml.addChild(ele)

# ###########################################################################
# Formatter API
# ###########################################################################

def format ( epg, out, extended = True ):

  now   = datetime.datetime.now().replace(tzinfo=util.TimeZoneSimple(0))
  dtd   = 'xmltv.dtd'
  if extended: dtd = 'e' + dtd
  attrs = {
    'date'            : now.strftime(XMLTV_TIME_FORMAT),
    'gen-info-name'   : 'PyEPG XMLTV Output'
    # TODO: other params?
  }
  xml = Document('tv', dtd, '1.0', XMLTV_ENCODING, **attrs)
  xml.begin(out)

  # Channels
  for c in epg.get_channels():
    out_channel(xml, c, extended)

  # Episodes
  sched = epg.get_schedule()
  for c in sched:
    for e in sched[c]:
      out_episode(xml, e, extended)

  # Done
  xml.end()

# ###########################################################################
# Editor
# ###########################################################################
