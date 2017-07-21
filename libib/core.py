# Standard libs:
import os
import sys
import glob
import json
import datetime
import argparse
import subprocess as sp

# Functions:
def parse_args(args=sys.argv[1:]):
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

    parser.add_argument("--nlink",
            help="How many previous backups (at most) to use for linking. Default: 10.",
            type=int,
            default=10)


    return parser.parse_args(args)

def timestamp(day=datetime.date.today(), offset=0):
    """Return timestamp string (YYYY.MM.DD), for day 'day' (default, today).
    Optionally, add 'offset' days of offset (e.g. offset=1 means tomorrow).
    """
    delta = datetime.timedelta(days=offset)

    return (day + delta).strftime('%Y.%m.%d')


# Classes:
class Rsync(object):
    """Objects that hold all info about a rsync command."""

    # Constructor:
    def __init__(self, data, item):
        self.data = data
        self.item = item
        self.dryrun = False
        self.rsync_base = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use


    # Public methods:
    def run(self, opts):
        """Do run."""

        if self.data.link_dirs_for(self.item):
            print("Determining last linkable dirs for [ music ]:".format(item=self.item))
            for ldir in self.data.link_dirs_for(self.item):
                print(ldir)

        for item in self.items:
            if opts.dryrun:
                print("Actual backup would go here...")
                print(self.cmd(item))
            else:
                if opts.verbosity > 0:
                    print("Doing actual backup...")
                    proc = sp.Popen(self.cmd(item), shell=True)
                    proc.communicate()

    def excludes_for(self, item):
        """Excludes for particular item 'item'."""

        return os.path.join(self.data.conf_dir, "{i}.excludes".format(i=item))

    def has_particular_excludes(self, item):
        """Return True if 'item' has particular excludes. False otherwise."""

        return os.path.isfile(self.excludes_for(item))

    def cmd(self, item):
        """rsync command line."""

        cmd = self.rsync_base
        cmd += ' --exclude-from={s.exclude_general} '.format(s=self)
        if self.has_particular_excludes(item):
            cmd += ' --exclude-from={e} '.format(e=self.excludes_for(item))
        
        if self.data.verbosity > 0:
            cmd += ' -vh --progress '

        # Link-dirs:
        for link_dir in self.data.link_dirs_for(item):
            cmd += ' --link-dest={d} '.format(d=link_dir)

        # From-dir:
        cmd += ' {d}/ '.format(d=self.data.conf[item]['fromdir'])

        # To-dir:
        todir = os.path.join(self.data.dest_dir_for(item), timestamp())
        cmd += ' {d}/ '.format(d=todir)

        return cmd


    # Public properties:
    @property
    def items(self):
        """List of items of which we are going to make a backup."""

        return self.data.items

    @property
    def exclude_general(self):
        """Excludes for any item."""

        return os.path.join(self.data.conf_dir, "global.excludes")

class Data(object):
    """Class to hold all miscellaneous general data."""

    # Constructor:
    def __init__(self, opts):
        h = os.environ['HOME']
        self.conf_dir = '{h}/.increback'.format(h=h) # configuration dir
        self.opts = opts # command-line options passed via argparse
        self.verbosity = opts.verbosity
        
        # Make dry runs more verbose:
        if opts.dryrun:
            self.verbosity += 1

        # Cache vars:
        self.__link_dirs_for = {}


    # Public methods:
    def read_conf(self):
        """Read the config file."""
        
        if self.verbosity > 0:
            msg = "Reading configuration from: {s.conf_file}".format(s=self)
            print(msg)

        try:
            with open(self.conf_file) as f:
                self.conf = json.load(f)
        except:
            print("Could not load config file [ {s.conf_file} ]".format(s=self))
            sys.exit()
        
    def link_dirs_for(self, item):
        """Return N last available dirs into which rsync will hardlink unmodified files (max N=20), for 'item'."""

        if not item in self.__link_dirs_for:
            patt = os.path.join(self.dest_dir_for(item), "????.??.??")
            self.__link_dirs_for[item] = sorted(glob.glob(patt), reverse=True)[:self.max_link_dirs_for(item)]

        return self.__link_dirs_for[item]

    def check_dest_dir_mounted(self, item):
        """Check whether destination directory is mounted."""

        if not self.is_dest_dir_mounted_for(item):
            msg = '[ERROR] Destination dir {d} not present!'.format(d=self.dest_dir_for(item))
            print(msg)
            sys.exit()

    def max_link_dirs_for(self, item):
        """Maximum amount of linkable directories for 'item'.
        Use amount specified in options, or 20, whichever is lowest.
        """
        return min(20, self.opts.nlink)

    def dest_dir_for(self, item):
        """Base destination directory for making the backup, for 'item'."""

        return self.conf[item]["todir"]

    def is_dest_dir_mounted_for(self, item):
        """Whether destination directory is mounted or not, for item 'item'."""

        return os.path.isdir(self.dest_dir_for(item))


    # Public properties:
    @property
    def conf_file(self):
        """Full path to selected configuration file."""

        if self.opts.config:
            return self.opts.config
        else:
            return os.path.join(self.conf_dir, "conf.json")

    @property
    def items(self):
        """List of items of which we are going to make a backup."""

        return [item for item, iconf in self.conf.items() if "active" in iconf and iconf["active"]]

