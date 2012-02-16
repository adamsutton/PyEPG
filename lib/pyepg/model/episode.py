#!/usr/bin/env python
#
# episode.py - Episode Structure
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

from _object import Object

class Episode ( Object ):
  
  def __init__ ( self ):
    Object.__init__(self)
    self.brand    = None
    self.series   = None
    self.title    = ''
    self.subtitle = ''
    self.number   = None
    self.genres   = set()

  def get_title ( self ):
    if self.brand and self.brand.title:
      return self.brand.title
    if self.series and self.series.title:
      return self.series.title
    return self.title

  def get_subtitle ( self ):
    if self.brand and self.brand.title or self.series and self.series.title:
      return self.title
    return self.subtitle

  def get_summary ( self ):
    if self.summary: return self.summary
    if self.series and self.series.summary: return self.series.summary
    if self.brand  and self.brand.summary: return self.brand.summary
    return None
  
  def get_number ( self ):
    ret = [ 0 ] * 3
    if self.number: ret[2] = self.number
    if self.series and self.series.number: ret[1] = self.series.number
    return ret

  def get_genres ( self ):
    ret = set()
    return ret

  def __str__ ( self ):
    t = self.get_title()
    if t is None: t = ''
    else: t = ' ' + t
    return self.uri + t
