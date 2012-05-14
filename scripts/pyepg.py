#!/usr/bin/env python
#
# pyepg - Front end script for pyepg
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
# Pass to module
# ###########################################################################

# System
import os, sys

# Local
lib_path = os.path.join(os.path.dirname(sys.argv[0]), '..', 'lib')
sys.path.insert(0, os.path.abspath(lib_path))
import pyepg.main as pyepg
pyepg.main()

# ############################################################################
# Editor Configuration
#
# vim:sts=2:ts=2:sw=2:et
# ############################################################################
