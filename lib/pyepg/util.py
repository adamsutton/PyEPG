#!/usr/bin/env python
#
# pyepg/util.py - Utility functions
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

from datetime import tzinfo, timedelta

# Numeric words
NUMBERS = {
  'one'       : 1,
  'two'       : 2,
  'three'     : 3,
  'four'      : 4,
  'five'      : 5,
  'six'       : 6,
  'seven'     : 7,
  'eight'     : 8,
  'nine'      : 9,
  'ten'       : 10,
  'eleven'    : 11,
  'twelve'    : 12,
  'thirteen'  : 13,
  'fourteen'  : 14,
  'fifteen'   : 15,
  'sixteen'   : 16,
  'seventeen' : 17,
  'eighteen'  : 18,
  'nineteen'  : 19,
  'twenty'    : 20,
  'thirty'    : 30,
  'forty'     : 40,
  'fifty'     : 50,
  'sixty'     : 60,
  'seventy'   : 70,
  'eighty'    : 80,
  'ninety'    : 90,
  'hundred'   : 100,
  'thousand'  : 1000,
  'million'   : 1000**2,
  'billion'   : 1000**3,
}

# ###########################################################################
# Functions
# ###########################################################################

# Convert string to number
# 
# Note: this works for normal integers stored as a string, i.e. "1", "2"
# but also textual representations of numbers "Twenty One"
#
# Note: this won't work with ALL representations, only sensible ones
def str2num ( s ):
  ret = None

  # Try simple numeric conversion
  try:
    ret = int(s)
  except: pass

  # Parse textual numbers
  if not ret:
    s  = s.lower().replace('-', ' ')
    pt = s.split(' ')
    ct = []

    # Parse strings
    for p in pt:
      if p in NUMBERS: ct.append(NUMBERS[p])
      elif p in [ 'and' ]: pass
      else: return None

    # Interpret numbers
    r = 0
    ct.reverse()
    t = None
    for c in ct:
      if c in [ 100, 1000, 1000**2, 1000**3 ]:
        if t: t = t * c
        else: t = c
      elif t:
        r = r + (c * t)
        t = None
      else:
        r = r + c
    ret = r
  return ret

#
# Timezone
#
class TimeZoneSimple ( tzinfo ):
  def __init__ ( self, of = None ):
    if of is not None:
      self.of = of
  def utcoffset ( self, dt ):
    return timedelta(minutes=self.of)
  def dst ( self, dt ):
    return timedelta(0)
  def tzname ( self, dt ):
    r = ''
    if self.of >= 0: r = '+'
    else:            r = '-'
    r = r + '%02d%02d' % (self.of / 60, self.of % 60)
    return r
  def __cmp__ ( self, other ):
    return cmp(self.of, other.of)

#
# Chunk an array into an array of smaller arrays
#
def chunk ( items, num ):
  ret = []
  t   = []
  for i in items:
    t.append(i)
    if len(t) == num:
      ret.append(t)
      t = []
  if t: ret.append(t)
  return ret

#
# Chunk into an equal number of sub arrays
#
def chunk2 ( items, num ):
  from math import ceil
  num = min(len(items), num)
  ret = []
  per = int(ceil(len(items) / float(num)))
  for i in range(num):
    t = []
    for j in range(per):
      if items: t.append(items.pop())
    ret.append(t)
  return ret

# ###########################################################################
# Testing
# ###########################################################################

if __name__ == '__main__':
  import sys
  print str2num(sys.argv[1])
