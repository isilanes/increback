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
        self.data = data


    # Public methods:
    def run(self, opts):
        """Do run."""

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
        todir = os.path.join(self.data.dest_dir_for(item), gimme_date())
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
        self.conf_dir = '{h}/.increback'.format(h=h)         # configuration dir
        self.opts = opts # command-line options passed via argparse
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

    def link_dirs_for(self, item):
        """Return N last available dirs into which rsync will hardlink unmodified files (max N=20), for 'item'."""

        # Use amount specified in options, or 20, whichever is lowest:
        N = self.opts.nlink
        if N > 20:
            N = 20

        if self.verbosity > 0:
            print("Determining last linkable dirs (up to {n} days back):".format(n=self.max_days_back_for(item)))
        
        link_dirs = []
        for i in range(1, self.max_days_back_for(item)+1):
            gdi = gimme_date(-i)
            path = os.path.join(self.dest_dir_for(item), gdi)
            if os.path.isdir(path):
                if self.verbosity > 0:
                    string = '  {d} '.format(d=path)
                print(string)

                # Add path to list:
                link_dirs.append(path)

                # If N matches found already, exit early:
                if len(link_dirs) >= N:
                    break

        return link_dirs

    def check_dest_dir_mounted(self):
        """Check whether destination directory is mounted."""

        if not self.is_dest_dir_mounted:
            string = '[ERROR] Destination dir {s.dest_dir} not present!'.format(s=self)
            print(string)
            sys.exit()

    def max_days_back_for(self, item):
        """Maximum amount of days to go back looking for linkable directories."""

        return self.conf[item]["max_days_back"]

    def dest_dir_for(self, item):
        """Base destination directory for making the backup, for 'item'."""

        return self.conf[item]["todir"]


    # Public properties:
    @property
    def is_dest_dir_mounted(self):
        """Whether destination directory is mounted or not."""

        return os.path.isdir(self.dest_dir)

    @property
    def conf_file(self):
        """Full path to selected configuration file."""

        if self.opts.config:
            return os.path.join(self.conf_dir, "{c}.json".format(c=self.opts.config))
        else:
            return os.path.join(self.conf_dir, "conf.json")

    @property
    def items(self):
        """List of items of which we are going to make a backup."""

        return [item for item, iconf in self.conf.items() if "active" in iconf and iconf["active"]]

