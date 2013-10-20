# coding=utf-8

import os
import sys
import json
import datetime
import subprocess as sp

#--------------------------------------------------------------------------------#

def gimme_date(offset=0):
    day   = datetime.date.today()
    delta = datetime.timedelta(days=offset)
    day   = day + delta
    date  = day.strftime('%Y.%m.%d')
    
    return date

#--------------------------------------------------------------------------------#

class Rsync(object):
    '''
    Objects that hold all info about a rsync command.
    '''

    def __init__(self, data):
        self.dryrun = False
        self.rsync_base = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
        self.exclude_general = os.path.join(data.conf_dir, "global.excludes")
        self.exclude_particular = '{0.conf_dir}/{0.opts.config}.excludes'.format(data)
        self.cmd = '' # final command
        self.data = data

    def build_cmd(self):
        '''
        Build a the rsync command line.
        '''

        if self.data.verbosity > 0:
            print("Building rsync command...")

        self.cmd  = self.rsync_base
        self.cmd += ' --exclude-from={0} '.format(self.exclude_general)
        if os.path.isfile(self.exclude_particular):
            self.cmd += ' --exclude-from={0} '.format(self.exclude_particular)
        
        if self.data.verbosity > 0:
            self.cmd += ' -vh --progress '

        if self.data.link_dir:
            pass

        if 'rsyncopts' in self.data.J:
            self.cmd += self.data.J['rsyncopts']

        # Link-dir:
        self.cmd += ' --link-dest={0} '.format(self.data.link_dir)

        # From-dir:
        self.cmd += ' {0}/ '.format(self.data.J['fromdir'])

        # To-dir:
        todir = os.path.join(self.data.J['todir'], gimme_date())
        self.cmd += ' {0}/ '.format(todir)

        if self.data.verbosity > 1:
            print(self.cmd)

    def run(self, opts):
        if opts.dryrun:
            print("Actual backup would go here...")
        else:
            if opts.verbosity > 0:
                print("Doing actual backup...")
                s = sp.Popen(self.cmd,shell=True)
                s.communicate()

#--------------------------------------------------------------------------------#

class Data(object):
    '''
    Class to hold all miscellaneous general data.
    '''

    def __init__(self, opts):
        h  = os.environ['HOME']
        self.home = h                                      # your home dir
        self.user = os.environ['LOGNAME']                  # username of script user
        self.conf_dir = '{0}/.increback'.format(h)         # configuration dir
        self.logfile = '{0}/.LOGs/increback.log'.format(h) # log file
        self.mxback  = 240                                 # max number of days to go back
        self.opts = opts # command-line options passed via argparse
        fn = '{0}.json'.format(self.opts.config)
        self.conf_file = os.path.join(self.conf_dir, fn)
        self.link_dir = None
        self.verbosity = opts.verbosity

    def read_conf(self):
        '''
        Read the config file.
        '''
        
        if self.verbosity > 0:
            string = "Reading config... [ {0} ]".format(self.conf_file)
            print(string)

        try:
            with open(self.conf_file) as f:
                self.J = json.load(f)
        except:
            print("Could not load config file [ {0} ]".format(self.conf_file))
            sys.exit()
        
    def find_last_linkable_dir(self):
        '''
        Find last available dir into which rsync will hardlink unmodified files.
        '''

        if self.verbosity > 0:
            print("Determining last linkable dir..."),
        
        todir = self.J['todir']

        for i in range(1, self.J["max_days_back"] + 1):
            gdi = gimme_date(-i)
            dir = os.path.join(todir, gdi)
            if os.path.isdir(dir):
                if self.verbosity > 0:
                    string = '  [ {0} ]'.format(dir)
                print(string)

                # If a match was found, exit early:
                self.link_dir = dir
                break

        if not self.link_dir and self.verbosity > 0:
            print(' [ None ]')
