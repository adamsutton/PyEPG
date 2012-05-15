#!/usr/bin/env python
#
# Python setup script for pyepg

# Imports
import os, sys
from distutils.core import setup

# Directories
dist_dir   = os.path.abspath(os.path.dirname(__file__))
root_dir   = os.path.abspath(os.path.join(dist_dir, '..'))
lib_dir    = os.path.join(root_dir, 'lib')
script_dir = os.path.join(root_dir, 'scripts')

# Auto build module list
mods = []
for p, ds, fs in os.walk(lib_dir):
  if '__init__.py' in fs:
    m = p.replace(lib_dir + '/', '').replace('/', '.')
    mods.append(m)

# Setup
setup(
  name             = 'pyepg',
  version          = '0.0.1',
  author           = 'Adam Sutton',
  author_email     = 'dev@adamsutton.me.uk',
  url              = 'https://github.com/adamsutton/PyEPG',
  description      = 'Python based TV Electronic Programme Guide grabber',
  long_description = 'Python based TV Electronic Programme Guide grabber. Takes influence from xmltv, but tries to extend for a much richer format. Currently only supports UK.',
  packages         = mods,
  package_dir      = { '' : 'lib' },
  scripts          = [ 'scripts/pyepg' ],
)
