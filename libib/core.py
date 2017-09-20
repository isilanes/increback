# Standard libs:
import os
import sys
import glob
import json
import logging
import datetime
import argparse
import subprocess as sp

# Our libs:
from logworks import logworks

# Constants:
HOME = os.environ["HOME"]
DEFAULT_CONF_DIR = os.path.join(HOME, ".increback")
DEFAULT_CONF_FILENAME = "conf.json"

# Functions:
def parse_args(args=sys.argv[1:]):
    """Parse command line arguments and return result."""

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config",
            help="Configuration file. Default: {f}.".format(f=os.path.join(DEFAULT_CONF_DIR, DEFAULT_CONF_FILENAME)),
            default=None)

    parser.add_argument("--log-conf",
            help="Logger configuration file. Default: None.",
            default=None)

    parser.add_argument("-v", "--verbose",
            dest="verbosity",
            help="Increase verbosity level by 1. Default: 0 (no output)",
            action="count",
            default=0)

    parser.add_argument("-y", "--dry-run",
            help="Dry run: do nothing, just tell what would be done. Default: real run.",
            action="store_true",
            default=False)

    parser.add_argument("--nlink",
            help="How many previous backups (at most) to use for linking. Default: 10.",
            type=int,
            default=10)

    parser.add_argument("--no-colors",
            help="Do not use color output in console. Default: use colors.",
            action="store_true",
            default=False)


    return parser.parse_args(args)

def timestamp(day=datetime.date.today(), offset=0):
    """Return timestamp string (YYYY.MM.DD), for day 'day' (default, today).
    Optionally, add 'offset' days of offset (e.g. offset=1 means tomorrow).
    """
    delta = datetime.timedelta(days=offset)

    return (day + delta).strftime('%Y.%m.%d')


# Classes:
class Base(object):
    """Generic superclass."""

    # Constructor:
    def __init__(self, logger):
        self.logger = logger


    # Public methods:
    def info(self, msg):
        """Output 'msg' message with logger object as info, or just print if none."""

        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

    def error(self, msg):
        """Output 'msg' message with logger object as error, or just print if none."""

        if self.logger:
            self.logger.error(msg)
        else:
            print(msg)

class Sync(Base):
    """Objects that hold all info about a rsync command."""
    
    RSYNC_BASE = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use

    # Constructor:
    def __init__(self, data, item, logger=None):
        super().__init__(logger)

        self.data = data
        self.item = item


    # Public methods:
    def run(self, opts):
        """Do run."""

        colored_item = self.logger.with_name_color("[{s.item}]".format(s=self))
        self.info("Determining last linkable dirs for {item}:".format(item=colored_item))
        if self.data.link_dirs_for(self.item):
            for ldir in self.data.link_dirs_for(self.item):
                self.info(ldir)

        if opts.dry_run:
            self.info("Actual backup would go here...")
            self.info(self.cmd(self.item))
        else:
            self.info("Doing actual backup...")
            proc = sp.Popen(self.cmd(self.item), shell=True)
            proc.communicate()

    def excludes_for(self, item):
        """Excludes for particular item 'item'."""

        return os.path.join(self.data.conf_dir, "{i}.excludes".format(i=item))

    def has_particular_excludes(self, item):
        """Return True if 'item' has particular excludes. False otherwise."""

        return os.path.isfile(self.excludes_for(item))

    def cmd(self, item):
        """rsync command line."""

        cmd = self.RSYNC_BASE
        cmd += ' --exclude-from={s.exclude_general} '.format(s=self)
        if self.has_particular_excludes(item):
            cmd += ' --exclude-from={e} '.format(e=self.excludes_for(item))
        
        #if self.data.verbosity > 0:
            #cmd += ' -vh --progress '

        # Link-dirs:
        for link_dir in self.data.link_dirs_for(item):
            cmd += ' --link-dest={d} '.format(d=link_dir)

        # From-dir:
        cmd += ' {d}/ '.format(d=self.data.from_dir_for(item))

        # To-dir:
        cmd += ' {d}/ '.format(d=self.data.backup_dir_for(item))

        return cmd


    # Public properties:
    @property
    def exclude_general(self):
        """Excludes for any item."""

        return os.path.join(self.data.conf_dir, "global.excludes")

class Data(Base):
    """Class to hold all miscellaneous general data."""

    # Constructor:
    def __init__(self, opts, logger=None):
        super().__init__(logger)

        self.opts = opts # command-line options passed via argparse

        self.conf_dir = DEFAULT_CONF_DIR
        self.timestamp = timestamp()
        
        # Make dry runs more verbose:
        #if opts.dry_run:
            #self.verbosity += 1

        # Cache vars:
        self.__link_dirs_for = {}
        
        # Read configuration:
        self.conf = self.read_conf()
        if not self.conf:
            sys.exit()


    # Public methods:
    def read_conf(self):
        """Read the config file."""
        
        fname = self.logger.with_name_color(self.conf_file)
        msg = "Reading configuration from [ {f} ]".format(f=fname)
        self.logger.info(msg)

        try:
            with open(self.conf_file) as f:
                return json.load(f)
        except:
            self.logger.error("Could not load config file [ {f} ]".format(f=fname))
            return None
        
    def link_dirs_for(self, item):
        """Return N last available dirs into which rsync will hardlink unmodified files (max N=20), for 'item'."""

        if not item in self.__link_dirs_for:
            patt = os.path.join(self.dest_dir_for(item), "????.??.??")
            self.__link_dirs_for[item] = sorted(glob.glob(patt), reverse=True)[:self.max_link_dirs_for(item)]

        return self.__link_dirs_for[item]

    def check_dest_dir_mounted(self, item):
        """Check whether destination directory is mounted."""

        if not self.is_dest_dir_mounted_for(item):
            colored_dir = self.logger.with_name_color(self.dest_dir_for(item))
            msg = 'Destination dir {d} not present!'.format(d=colored_dir)
            self.error(msg)
            sys.exit()

    def max_link_dirs_for(self, item):
        """Maximum amount of linkable directories for 'item'.
        Use amount specified in options, or 20, whichever is lowest.
        """
        return min(20, self.opts.nlink)

    def dest_dir_for(self, item):
        """Base destination directory for making the backup, for 'item'."""

        return self.conf["items"][item]["todir"]

    def from_dir_for(self, item):
        """Base origin directory for making the backup, for 'item'."""

        return self.conf["items"][item]["fromdir"]

    def backup_dir_for(self, item):
        """Directory where backup will be made, for 'item'."""

        return os.path.join(self.dest_dir_for(item), self.timestamp)

    def is_dest_dir_mounted_for(self, item):
        """Whether destination directory is mounted or not, for item 'item'."""

        return os.path.isdir(self.dest_dir_for(item))

    def is_backup_done_for(self, item):
        """Whether today's backup has been done for item 'item'."""

        return os.path.isdir(self.backup_dir_for(item))


    # Public properties:
    @property
    def conf_file(self):
        """Full path to selected configuration file."""

        if self.opts.config:
            return self.opts.config
        else:
            return os.path.join(self.conf_dir, DEFAULT_CONF_FILENAME)

    @property
    def items(self):
        """List of items of which we are going to make a backup."""

        return [item for item, iconf in self.conf["items"].items() if "active" in iconf and iconf["active"]]

