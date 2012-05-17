#!/usr/bin/env python
#
# series.py - Series info
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

class Series ( Object ):
  
  def __init__ ( self ):
    Object.__init__(self)
    self.brand         = None
    self.title         = None
    self.summary       = None
    self.number        = None
    self.image         = None
    self.thumb         = None
    self.genres        = None
    self.episode_count = None

  def __str__ ( self ):
    ret = self.uri
    if self.title:
      ret = ret + ' ' + self.title
    if self.summary:
      ret = ret + ' ' + self.summary
    return ret
