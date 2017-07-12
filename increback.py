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

I use this script from the command line.
"""

# Our libs:
from libib import core

# Functions:
def main():
    """Execute this when called as stand-alone."""
    
    # Get command-line options:
    opts = core.read_args()

    # General variables in centralized Data() object:
    data = core.Data(opts)

    # Read configurations:
    data.read_conf()

    # Check destination is mounted:
    #data.check_dest_dir_mounted()

    # Find last available dirs to hardlink to when unaltered:
    #data.find_last_linkable_dirs()
        
    # Build rsync command(s) and run:
    R = core.Rsync(data)
    R.run(opts)


# If called as stand-alone:
if __name__ == "__main__":
    main()
