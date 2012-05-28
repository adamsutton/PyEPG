#!/usr/bin/env python
#
# pyepg/xml.py - XML formatting functions
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

# ###########################################################################
# Imports
# ###########################################################################

# ###########################################################################
# Classes
# ###########################################################################

class Element:

  def __init__ ( self, name, cdata = None, **attrs ):
    self._name     = name
    self._cdata    = cdata
    self._attrs    = attrs
    self._children = []
    self._out      = None
    self._indent   = 0
    self._encoding = None
    self._empty    = True

  def setCData ( self, cdata ):
    assert(self._out is None)
    self._cdata = cdata

  def addAttribute ( self, key, val ):
    assert(self._out is None)
    self._attrs[key] = val

  def addChild ( self, ele ):
    if self._out is None:
      self._children.append(ele)
    else:
      if not self._cdata and self._empty:
        self._out.write('>')
      if self._empty:
        self._out.write('\n')
      self._empty = False
      ele.begin(self._out, self._indent + 1, self._encoding)
      ele.end()

  def begin ( self, out, indent = 0, encoding = 'utf8' ):
    self._out      = out
    self._indent   = indent
    self._encoding = encoding
    self._out.write('%s<%s' % ('  ' * indent, self._name))
    for k in self._attrs:
      self._out.write(' %s="%s"' % (k, self._format(self._attrs[k])))
    if self._children or self._cdata:
      self._out.write('>')
    if self._cdata:
      self._out.write(self._format(self._cdata))
    if self._children:
      self._out.write('\n')
      self._empty = False
    for c in self._children:
      c.begin(out, indent + 1, encoding)
      c.end()

  def end ( self ):
    if self._cdata or not self._empty:
      if not self._empty: self._out.write('  ' * self._indent)
      self._out.write('</%s>\n' % self._name)
    else:
      self._out.write('/>\n')
    self._out = None

  def _format ( self, data ):
    s = str(data)
    s = s.replace('&', '&amp;')
    try:
      s = s.encode(self._encoding)
    except: pass
    return s

class Document ( Element ):

  def __init__ ( self, root, dtd, version, encoding, **attrs ):
    Element.__init__(self, root, **attrs)
    self._version  = version
    self._encoding = encoding
    self._dtd      = dtd

  def begin ( self, fp ):
    fp.write('<?xml version="%s" encoding="%s" ?>\n' % (self._version, self._encoding))
    fp.write('<!DOCTYPE %s SYSTEM "%s" ?>\n' % (self._name, self._dtd))
    Element.begin(self, fp, 0, self._encoding)

# ###########################################################################
# Editor
#
# vim:sts=2:ts=2:sw=2:et
# ###########################################################################
