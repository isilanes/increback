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

% increback.py -h

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

parser.add_argument("-d", "--delete",
        help="Try to find old backups to delete. Default: perform a backup.",
        action="store_true",
        default=False)

o = parser.parse_args()

#--------------------------------------------------------------------------------#

# rsync-command stuff object:
R = core.Rsync()
R.verbosity = o.verbosity

# Make dry runs more verbose:
if o.dryrun:
    R.verbosity += 1

#--------------------------------------------------------------------------------#

# General variables:
rsync = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
user  = os.environ['LOGNAME']                      # username of script user
home  = os.environ['HOME']                         # your home dir
conf_dir = '{0}/.increback'.format(home)           # configuration dir
logfile = '{0}/.LOGs/increback.log'.format(home)   # log file
mxback  = 240                                      # max number of days to go back 

# Read configurations:
if o.verbosity > 0:
    print("Reading config files...")
    
cfg = core.read_config(conf_dir, o)

if o.delete:
    # Determine if any to delete:
    if o.verbosity > 1:
        print("Finding out deletable dirs...")
    core.find_deletable(cfg)
else:
    # Build rsync command:
    if o.verbosity > 0: 
        print("Building rsync command...")
        
    rsync = core.build_rsync(rsync, cfg, o, conf_dir)
    
    # Find last available dir (whithin specified limit) to hardlink to when unaltered:
    if o.verbosity > 0: 
        print("Determining last 'linkable' dir...")
        
    last_dir = core.find_last_dir(cfg,mxback,o.verbosity)
    
    if o.verbosity > 0:
        print(" -> '{0}'".format(last_dir))
        
    # Make backup:
    if o.verbosity > 0:
        print("Doing actual backup...")
    
    success = core.backup(cfg, rsync, last_dir, o)

    # Final message:
    if not o.dryrun and success:
        print('Sucess!')
