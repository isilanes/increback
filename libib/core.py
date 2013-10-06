# coding=utf-8

import os
import json
import Time as T
import subprocess as sp

#--------------------------------------------------------------------------------#

def doit(cmnd, opts):
    '''
    Print and execute command, depending on o.verbosity and o.dryrun.
    cmnd = command to run
    '''
    
    if opts.verbosity > 0:
        print(cmnd)
        
    if not opts.dryrun:
        s = sp.Popen(cmnd,shell=True)
        s.communicate()

#--------------------------------------------------------------------------------#

def backup(config=None, rsync=None, last_dir=None, opts=None):
    '''
    Actually make the backup.
    '''

    success = False

    if config:
        if last_dir:
            rsync = '{0} --link-dest={1}'.format(rsync, last_dir)

        # Actually do it:
        fmt = '{0} {1[FROMDIR]}/ {1[TODIR]}/{2}/'
        cmnd = fmt.format(rsync, config, T.gimme_date())
        doit(cmnd, opts)

        success = True

    else:
        print("Could not back up: no source/destination machine(s) specified!")

    return success

#--------------------------------------------------------------------------------#

def find_last_dir(config=None, maxd=1, verbosity=0):
    '''
    Find last available dir into which rsync will hardlink unmodified files.
    maxd = max number of days we want to move back.
    '''
    
    mmt = config['TODIR']
    
    for i in range(1,maxd+1):
        gdi = T.gimme_date(-i)
        dir = '{0}/{1}'.format(mmt,gdi)
        if verbosity > 1:
            print(dir)
        if os.path.isdir(dir):
            # If a match was found, exit early:
            return dir

    # If arrived so far without a result:
    return None

#--------------------------------------------------------------------------------#

def build_rsync(in_rsync, config, opts, conf_dir):
    '''
    Build a more complete rsync command.
    '''
    
    # Global excludes:
    out_rsync = '{0} --exclude-from={1}/global.excludes '.format(in_rsync, conf_dir)
    
    # Particular excludes:
    pef = '{0}/{1}.excludes'.format(conf_dir, opts.config)
    if os.path.isfile(pef):
        out_rsync = '{0} --exclude-from={1} '.format(out_rsync, pef)
    
    # Verbosity:
    if opts.verbosity > 0:
        out_rsync += ' -vh '
        out_rsync += ' --progress '
    
    # Machine-specific options:
    try:
        out_rsync += ' {0} '.format(config['RSYNCOPS'])
    except:
        pass
    
    return out_rsync

#--------------------------------------------------------------------------------#

class Rsync(object):
    '''
    Objects that hold all info about a rsync command.
    '''

    def __init__(self, data):
        self.dryrun = False
        self.rsync_base = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
        self.data = data

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
        self.max_days_back = 1 # max amount of days back to look for linkable dirs
        self.link_dir = None
        self.verbosity = opts.verbosity

    def read_conf(self):
        '''
        Read the config file.
        '''
        
        if self.verbosity > 0:
            string = "Reading config... [{0}]".format(self.conf_file)
            print(string)

        with open(self.conf_file) as f:
            self.J = json.load(f)
        
    def find_last_linkable_dir(self):
        '''
        Find last available dir into which rsync will hardlink unmodified files.
        '''

        if self.verbosity > 0:
            print("Determining last linkable dir...")
        
        todir = self.J['todir']
        
        for i in range(1, self.max_days_back+1):
            gdi = T.gimme_date(-i)
            dir = '{0}/{1}'.format(todir, gdi)
            if self.verbosity > 1:
                print(dir)
            if os.path.isdir(dir):
                # If a match was found, exit early:
                self.link_dir = dir
                break
