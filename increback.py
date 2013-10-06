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

import os
import argparse
import libib.core as core

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

# rsync-command stuff object:
R = core.Rsync(D)

# Make dry runs more verbose:
if o.dryrun:
    D.verbosity += 1

#--------------------------------------------------------------------------------#

###rsync = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
###user  = os.environ['LOGNAME']                      # username of script user
###home  = os.environ['HOME']                         # your home dir
###conf_dir = '{0}/.increback'.format(home)           # configuration dir
###logfile = '{0}/.LOGs/increback.log'.format(home)   # log file
###mxback  = 240                                      # max number of days to go back 

# Read configurations:
D.read_conf()

###if R.verbosity > 0:
###    string = "Reading config... [{0}]".format(D.conf_dir)
###    print(string)
###cfg = core.read_config(conf_dir, o)

# Find last available dir (whithin specified limit) to hardlink to when unaltered:
D.find_last_linkable_dir()
###if o.verbosity > 0: 
###    print("Determining last 'linkable' dir...")
###last_dir = core.find_last_dir(cfg,mxback,o.verbosity)
    
exit()
# Build rsync command:
if o.verbosity > 0: 
    print("Building rsync command...")
    
rsync = core.build_rsync(rsync, cfg, o, conf_dir)

# Make backup:
if o.verbosity > 0:
    print("Doing actual backup...")

success = core.backup(cfg, rsync, last_dir, o)

# Final message:
if not o.dryrun and success:
    print('Sucess!')
