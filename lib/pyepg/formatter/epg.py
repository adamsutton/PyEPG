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
from pyepg.xml import Document, Element

# ###########################################################################
# Configuration
# ###########################################################################

PYEPG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'
PYEPG_ENCODING    = 'utf8'

# ###########################################################################
# Output
# ###########################################################################

# Channel
def out_channel ( xml, chn ):
  ele = Element('channel', id=chn.uri)
  ele.addChild(Element('name', chn.title))
  if chn.image:
    ele.addChild(Element('image', chn.image))
  if chn.radio:
    ele.addChild(Element('radio'))
  # TODO: extra metadata
  xml.addChild(ele)

# Brand
def out_brand ( xml, brand ):
  ele = Element('brand', id=brand.uri)
  if brand.title:
    ele.addChild(Element('title', brand.title))
  if brand.summary:
    ele.addChild(Element('summary', brand.summary))
  if brand.series_count:
    ele.addChild(Element('series_count', brand.series_count))
  if brand.image:
    ele.addChild(Element('image', brand.image))
  if brand.thumb:
    ele.addChild(Element('thumb', brand.thumb))
  xml.addChild(ele)

# Series
def out_series ( xml, series ):
  ele = Element('series', id=series.uri)
  if series.brand:
    ele.addAttribute('brand', series.brand.uri)
  if series.title:
    ele.addChild(Element('title', series.title))
  if series.summary:
    ele.addChild(Element('summary', series.summary))
  if series.image:
    ele.addChild(Element('image', series.image))
  if series.thumb:
    ele.addChild(Element('thumb', series.thumb))
  if series.number is not None:
    ele.addChild(Element('number', series.number))
  else:
    log.warn('no series number for %s' % series.uri)
  if series.episode_count:
    ele.addChild(Element('episode_count', series.episode_count))
  xml.addChild(ele)

# Episode
def out_episode ( xml, eps ):
  ele = Element('episode', id=eps.uri)
  if eps.brand:
    ele.addAttribute('brand', eps.brand.uri)
  if eps.series:
    ele.addAttribute('series', eps.series.uri)
  # TODO: re-think this!
  ele.addChild(Element('title', eps.get_title()))
  st = eps.get_subtitle()
  if st:
    ele.addChild(Element('subtitle', st))
  su = eps.get_summary()
  if su:
    ele.addChild(Element('summary', su))
  if eps.number:
    ele.addChild(Element('number', eps.number))
  if eps.part_num:
    ele.addChild(Element('part-number', eps.part_num))
  if eps.part_cnt:
    ele.addChild(Element('part-count', eps.part_cnt))
  if eps.film:
    ele.addChild(Element('film'))
  for g in eps.get_genres():
    ele.addChild(Element('genre', g))
  cs = eps.get_credits()
  if cs:
    cre = Element('credits')
    for r in cs:
      for p in cs[r]:
        if p.role == 'actor' and p.character:
          cre.addChild(Element('actor', p.name, character=p.character))
        else:
          cre.addChild(Element(r, p.name))
    ele.addChild(cre)
  if eps.year and eps.film:
    ele.addChild(Element('date', eps.year))
  if eps.baw:
    ele.addChild(Element('blackandwhite'))

  # TODO: images
  #if eps.image:
  #  ele.addChild(Element('image', eps.image))
  #if eps.thumb:
  #  ele.addChild(Element('thumb', eps.thumb))

  # TODO: HD (as in showing on HD channel)

  xml.addChild(ele)

# Broadcast
def out_broadcast ( xml, bcast ):
  f   = bcast.start.strftime(PYEPG_TIME_FORMAT)
  t   = bcast.stop.strftime(PYEPG_TIME_FORMAT)

  ele = Element('broadcast', episode=bcast.episode.uri, start=f, stop=t)

  if bcast.hd:
    ele.addChild(Element('hd'))
  if bcast.widescreen or bcast.hd:
    ele.addChild(Element('widescreen'))
  # TODO: quality and aspect ratio
  if bcast.new:
    ele.addChild(Element('new'))
  if bcast.premiere:
    ele.addChild(Element('premiere'))
  if bcast.repeat:
    ele.addChild(Element('repeat'))
  if bcast.subtitled:
    ele.addChild(Element('subtitles', type='teletext'))
  if bcast.signed:
    ele.addChild(Element('subtitles', type='deaf-signed'))
  # TODO: audio described
  # TODO: certification and ratings
  # TODO: image

  xml.addChild(ele)

# Schedule
def out_schedule ( xml, sched, channel ):

  # Output broadcasts
  ele = Element('schedule', channel=channel.uri)
  for b in sched:
    out_broadcast(ele, b)
  xml.addChild(ele)

# ###########################################################################
# Formatter API
# ###########################################################################

# Output EPG
def format ( epg, out ):

  # Start XML document
  xml = Document('epg', 'pyepg.dtd', '1.0', PYEPG_ENCODING)
  xml.begin(out)

  # Channels
  for c in epg.get_channels():
    out_channel(xml, c)

  # Brands
  for b in epg.get_brands():
    out_brand(xml, b)

  # Series
  for s in epg.get_series():
    out_series(xml, s)

  # Episodes
  for e in epg.get_episodes():
    out_episode(xml, e)

  # Schedules
  sc = epg.get_schedule()
  for c in sc:
    out_schedule(xml, sc[c], c)

  # Done
  xml.end()
