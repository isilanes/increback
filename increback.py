"""
increback
(c) 2008-2014,2017, Iñaki Silanes

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
"""

# Standard libs:
import os
import sys
import argparse

# Our libs:
from libib import core

# Functions:
def read_args(args=sys.argv[1:]):
    """Parse command line arguments and return result."""

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


    return parser.parse_args(args)

def main():
    """Execute this when called as stand-alone."""
    
    # Get command-line options:
    opts = read_args()

    # General variables in centralized Data() object:
    data = core.Data(opts)

    # Make dry runs more verbose:
    if opts.dryrun:
        data.verbosity += 1

    #--------------------------------------------------------------------------------#

    # Read configurations:
    data.read_conf()

    # Check destination is mounted:
    if not os.path.isdir(data.J['todir']):
        string = '[ERROR] Destination dir {d} not present!'.format(d=data.J['todir'])
        print(string)
        sys.exit()

    # Find last available dirs (whithin specified limit) to hardlink to when unaltered:
    data.find_last_linkable_dirs(N=10)
        
    # Build rsync command:
    R = core.Rsync(data)
    R.build_cmd()
        
    # Make backup:
    success = R.run(opts)

    # Final message:
    if not opts.dryrun and success:
        print('Sucess!')


# If called as stand-alone:
if __name__ == "__main__":
    main()
