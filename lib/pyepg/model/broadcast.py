#!/usr/bin/env python
#
# broadcast.py - Broadcast entry
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

class Broadcast:
  
  def __init__ ( self ):
    self.channel    = None
    self.episode    = None
    self.start      = None
    self.stop       = None
    self.hd         = False
    self.lines      = None
    self.widescreen = False
    self.aspect     = None
    self.premiere   = False
    self.new        = False
    self.repeat     = False
    self.signed     = False
    self.subtitled  = False
    self.audio_desc = False
    self.followedby = None

  def __cmp__ ( self, other ):
    ret = cmp(self.channel, other.channel)
    if not ret:
      ret = cmp(self.start, self.stop)
    return ret
