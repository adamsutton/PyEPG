#!/usr/bin/env python
#
# schedule.py - Schedule entry
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

class Schedule:
  
  def __init__ ( self ):
    self.channel = None
    self.episode = None
    self.start   = None
    self.stop    = None

  def __cmp__ ( self, other ):
    ret = cmp(self.channel, other.channel)
    if not ret:
      ret = cmp(self.start, self.stop)
    return ret
