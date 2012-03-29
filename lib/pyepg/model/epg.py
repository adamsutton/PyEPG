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

# SYS libs
from threading import Lock

# PyEPG libs
import pyepg.log as log

# Note: there is some redundancy in the data storage, this makes
# access for the formatters quicker at a slight cost to entry during
# grabbing

class EPG:
  
  def __init__ ( self ):
    self.brands   = set()
    self.series   = set()
    self.episodes = set()
    self.schedule = {}
    self._lock    = Lock()

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

  def get_sched_count ( self ):
    sc = 0
    for c in self.schedule:
      sc = sc + len(self.schedule[c])
    return sc

  def add_broadcast ( self, entry ):
    with self._lock:
      c = entry.channel

      # TODO: Hacks
      if entry.episode.media not in [ 'audio', None ]:
        c.radio = False

      # Setup schedule
      if c not in self.schedule:
        self.schedule[c] = []

      # Add entry
      self.schedule[c].append(entry)

      # Extra internal lists
      e = entry.episode
      b = e.brand
      s = e.series
      if b: self.brands.add(b)
      if s: self.series.add(s)
      self.episodes.add(e)

  # This sorts the broadcasts and fixes any overlaps (where possible)
  def finish ( self ):
    def tsort ( x, y ):
      r = cmp(x.start, y.start)
      if not r:
        r = cmp(x.stop, y.stop)
      return r
    for c in self.schedule:
      self.schedule[c].sort(cmp=tsort)
      p = None
      for i in self.schedule[c]:
        if p and p.stop > i.start:
          log.debug('epg - schedule overlap detected')
          if (p.stop - i.start).total_seconds() < 600:
            log.debug('epg - assume multi-provider discrepancy, will correct')
            p.stop = i.start
          else:
            log.warn('epg - uncorrectable schedule overlap detected %s' % p.stop)
        p = i
