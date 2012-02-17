#!/usr/bin/env python
#
# genre.py - Genre info
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

class Genre ( Object ):
  
  def __init__ ( self, uri, title = None ):
    Object.__init__(self)
    if title is None: title = uri
    self.uri   = uri
    self.title = title

  def __str__ ( self ):
    return self.title

# Static list
ANIMALS       = Genre('animals')
ANIMATION     = Genre('animation')
COMEDY        = Genre('comedy')
CHILDRENS     = Genre('childrens')
DRAMA         = Genre('drama')
ENTERTAINMENT = Genre('entertainment')
FACTUAL       = Genre('factual')
FILM          = Genre('film')
LEARNING      = Genre('learning')
LIFESTYLE     = Genre('lifestyle')
MUSIC         = Genre('music')
NEWS          = Genre('news')
SPORTS        = Genre('sports')
