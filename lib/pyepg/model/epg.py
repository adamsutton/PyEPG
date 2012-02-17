#!/usr/bin/env python
#
# epg.py - EPG info
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

# Note: there is some redundancy in the data storage, this makes
# access for the formatters quicker at a slight cost to entry during
# grabbing

class EPG:
  
  def __init__ ( self ):
    self.brands   = set()
    self.series   = set()
    self.episodes = set()
    self.schedule = {}

  def get_channels ( self ):
    return self.schedule.keys()

  def get_brands ( self ):  
    return self.brands

  def get_series ( self ):
    return self.series

  def get_episodes ( self ):
    return self.episodes

  def get_schedule ( self, channel = None ):
    ret = None
    if channel:
      if channel in self.schedule:
        ret = self.schedule[channel]
    else:
      ret = self.schedule
    return ret

  def add_entry ( self, entry ):
    c = entry.channel
    if c not in self.schedule:
      self.schedule[c] = []
    self.schedule[c].append(entry)
    e = entry.episode
    b = e.brand
    s = e.series
    if b: self.brands.add(b)
    if s: self.series.add(s)
    self.episodes.add(e)

  def get_sched_count ( self ):
    sc = 0
    for c in self.schedule:
      sc = sc + len(self.schedule[c])
    return sc
