#!/usr/bin/python
# coding=utf-8

'''
increback
(c) 2008-2013, Iñaki Silanes

LICENSE

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License (version 2), as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details (http://www.gnu.org/licenses/gpl.txt).

DESCRIPTION

It makes incremental backups with rsync.

USAGE

For usage, run:

$ increback.py -h

I use this script interactively.
'''

import argparse

from libib import core

#------------------------------------------------------------------------------#

# Read arguments:
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config",
        help="Configuration file. Default: None.",
        default=None)

parser.add_argument("-v", "--verbose",
        dest="verbosity",
        help="Increase verbosity level by 1. Default: 0 (no output)",
        action="count",
        default=0)

parser.add_argument("-y", "--dryrun",
        help="Dry run: do nothing, just tell what would be done. Default: real run.",
        action="store_true",
        default=False)

o = parser.parse_args()

#--------------------------------------------------------------------------------#

# General variables in centralized Data() object:
D = core.Data(o)
D.verbosity = o.verbosity

# Make dry runs more verbose:
if o.dryrun:
    D.verbosity += 1

#--------------------------------------------------------------------------------#

# Read configurations:
D.read_conf()

# Find last available dir (whithin specified limit) to hardlink to when unaltered:
D.find_last_linkable_dir()
    
# Build rsync command:
R = core.Rsync(D)
R.build_cmd()
    
# Make backup:
success = R.run(o)

# Final message:
if not o.dryrun and success:
    print('Sucess!')
