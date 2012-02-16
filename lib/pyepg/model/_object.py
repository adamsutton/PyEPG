#!/usr/bin/env python
#
# _object.py - Generic object parent to most model objects
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

class Object:
  
  def __init__ ( self ):
    self.uri      = None

  def __str__ ( self ): 
    return self.uri

  def __hash__ ( self ):
    return hash(self.uri)
  
  def __cmp__ ( self, other ):
    return cmp(self.uri, other.uri)
