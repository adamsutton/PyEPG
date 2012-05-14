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
# Imports
# ###########################################################################

# System
import os, sys, datetime
from optparse import OptionParser

# Local
lib_path = os.path.join(os.path.dirname(sys.argv[0]), 'lib')
sys.path.append(os.path.abspath(lib_path))
import pyepg.main as pyepg


# ###########################################################################
# Run
# ###########################################################################

if __name__ == '__main__':

  # Comand line
  optp = OptionParser()
  pyepg.options(optp)
  (opts,args) = optp.parse_args()
  
  # Configure
  if 'configure' in args:
    pyepg.configure(opts, args)

  # Run
  else:
    pyepg.main(opts, args)
