# Standard libs:
import os
import sys
import json
import datetime
import argparse
import subprocess as sp

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

    parser.add_argument("--nlink",
            help="How many previous backups (at most) to use for linking. Default: 10.",
            type=int,
            default=10)


    return parser.parse_args(args)

def gimme_date(offset=0):
    """Return YYYY.MM.DD string with today's date + 'offset' days."""

    day = datetime.date.today()
    delta = datetime.timedelta(days=offset)
    day = day + delta
    date = day.strftime('%Y.%m.%d')
    
    return date


# Classes:
class Rsync(object):
    """Objects that hold all info about a rsync command."""

    # Constructor:
    def __init__(self, data):
        self.dryrun = False
        self.rsync_base = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
        self.exclude_general = os.path.join(data.conf_dir, "global.excludes")
        self.exclude_particular = '{d.conf_dir}/{d.opts.config}.excludes'.format(d=data)
        self.cmd = '' # final command
        self.data = data


    # Public methods:
    def build_cmd(self):
        """Build a the rsync command line."""

        if self.data.verbosity > 0:
            print("Building rsync command...")

        self.cmd  = self.rsync_base
        self.cmd += ' --exclude-from={s.exclude_general} '.format(s=self)
        if os.path.isfile(self.exclude_particular):
            self.cmd += ' --exclude-from={s.exclude_particular} '.format(s=self)
        
        if self.data.verbosity > 0:
            self.cmd += ' -vh --progress '

        if 'rsyncopts' in self.data.conf:
            self.cmd += self.data.conf['rsyncopts']

        # Link-dirs:
        for link_dir in self.data.link_dirs:
            self.cmd += ' --link-dest={d} '.format(d=link_dir)

        # From-dir:
        self.cmd += ' {d}/ '.format(d=self.data.conf['fromdir'])

        # To-dir:
        todir = os.path.join(self.data.dest_dir, gimme_date())
        self.cmd += ' {d}/ '.format(d=todir)

        if self.data.verbosity > 1:
            print(self.cmd)

    def run(self, opts):
        """Do run."""

        if opts.dryrun:
            print("Actual backup would go here...")
        else:
            if opts.verbosity > 0:
                print("Doing actual backup...")
                proc = sp.Popen(self.cmd, shell=True)
                proc.communicate()

class Data(object):
    """Class to hold all miscellaneous general data."""

    # Constructor:
    def __init__(self, opts):
        h = os.environ['HOME']
        self.home = h                                        # your home dir
        self.user = os.environ['LOGNAME']                    # username of script user
        self.conf_dir = '{h}/.increback'.format(h=h)         # configuration dir
        self.logfile = '{h}/.LOGs/increback.log'.format(h=h) # log file
        self.mxback  = 240                                   # max number of days to go back
        self.opts = opts # command-line options passed via argparse
        fn = '{c}.json'.format(c=self.opts.config)
        self.conf_file = os.path.join(self.conf_dir, fn)
        self.link_dirs = []
        self.verbosity = opts.verbosity
        
        # Make dry runs more verbose:
        if opts.dryrun:
            self.verbosity += 1


    # Public methods:
    def read_conf(self):
        """Read the config file."""
        
        if self.verbosity > 0:
            string = "Reading config... [ {s.conf_file} ]".format(s=self)
            print(string)

        try:
            with open(self.conf_file) as f:
                self.conf = json.load(f)
        except:
            print("Could not load config file [ {s.conf_file} ]".format(s=self))
            sys.exit()
        
    def find_last_linkable_dirs(self):
        """Find N last available dirs into which rsync will hardlink unmodified files (max N=20)."""

        # Use amount specified in options, or 20, whichever is lowest:
        N = self.opts.nlink
        if N > 20:
            N = 20

        if self.verbosity > 0:
            print("Determining last linkable dirs (up to {s.max_days_back} days back):".format(s=self))
        
        self.link_dirs = []
        for i in range(1, self.max_days_back+1):
            gdi = gimme_date(-i)
            dir = os.path.join(self.dest_dir, gdi)
            if os.path.isdir(dir):
                if self.verbosity > 0:
                    string = '  {d} '.format(d=dir)
                print(string)

                # If N matches found already, exit early:
                self.link_dirs.append(dir)
                if len(self.link_dirs) >= N:
                    break

        if not self.link_dirs and self.verbosity > 0:
            print(' [ None ]')

    def check_dest_dir_mounted(self):
        """Check whether destination directory is mounted."""

        if not self.is_dest_dir_mounted:
            string = '[ERROR] Destination dir {s.dest_dir} not present!'.format(s=self)
            print(string)
            sys.exit()



    # Public properties:
    @property
    def is_dest_dir_mounted(self):
        """Whether destination directory is mounted or not."""

        return os.path.isidir(self.dest_dir)

    @property
    def dest_dir(self):
        """Base destination directory for making the backup."""

        return self.conf["todir"]

    @property
    def max_days_back(self):
        """Maximum amount of days to go back looking for linkable directories."""

        return self.conf["max_days_back"]
