#!/usr/bin/env python
#
# Search for TV/Radio logos
#

import os, sys, string, urllib2, re

url_base = 'http://www.lyngsat-logo.com'

# Find a icon
def find_icon ( url, name ):
  ret = None
  print >>sys.stderr, 'Checking for %s @ %s' % (name, url)
  exp   = re.compile('<img src="../icon/(.*?)"')
  up    = urllib2.urlopen(url)
  lines = up.readlines()

  # Setup
  name   = name.lower()
  search = [ name, name.replace(' +1', ''), name.replace(' tv', ''),\
             name.replace(' tv', '').replace(' +1', '') ]

  # Search
  for n in search:
    p     = None
    for l in lines:
      if name in l.lower():
        r = exp.search(l)
        if not r and p:
          r = exp.search(p)
        if r:
          ret = url_base + '/logo/' + r.group(1).replace('.gif', '.jpg')
          print >>sys.stderr, '  found logo %s' % ret
          return ret
      p = l

  return None

# Open file
ip = sys.stdin
if len(sys.argv) > 1:
  ip = open(sys.argv[1])

# Ignore header
print ip.readline().strip()

# Process each channel
for l in ip:
  l      = l.strip()
  chn    = map(lambda x: x.strip(), l.split(','))
  radio  = chn[7] == '1'
  sname  = chn[1]
  stitle = chn[2]
  icon   = None
  if len(chn) >= 9: icon = chn[8]

  # Ignore
  if icon:
    print l
    continue
  
  # Find
  check = [ stitle, sname ]
  done  = set()
  for t in check:
    if not t: continue
    if t in done: continue
    u = url_base
    if radio:
      u = u + '/radio'
    else:
      u = u + '/tv'
    
    # A-Z
    if t.lower()[0] in string.lowercase:
      u = u + '/%s.html' % t.lower()[0]
  
    # Number
    else:
      u = u + '/num.html'

    # Find
    icon = find_icon(u, t)

    # Done
    if icon: break

  # Found
  if not icon:
    print l
    print >>sys.stderr, '  NO ICON: %s' % stitle
    continue

  # Add missing fields
  if len(chn) < 9:
    s.extend(['']*(9-len(chn)))
  chn[8] = icon
  print ','.join(chn)
