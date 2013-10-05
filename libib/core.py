# coding=utf-8

import os
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

def read_config(conf_dir, opts):
    '''
    Read the configuration file.
    '''
    
    conf_file = '{0}/{1}.conf'.format(conf_dir, opts.config)
    
    props = {}
    with open(conf_file,'r') as f:
        for line in f:
            aline = line.replace('\n','').split('=')
            props[aline[0]] = '='.join(aline[1:])
        
    return props

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

def find_deletable(cfg):
    '''
    Find old, deletable, backups.
    '''

    # Deleting all that stuff, as I don't understand it :^)
    print('Functionality not yet implemented.')

#--------------------------------------------------------------------------------#

class Rsync(object):
    '''
    Objects that hold all info about a rsync command.
    '''

    def __init__(self):
        self.verbosity = 0
        self.dryrun = False
        self.rsync_base = 'rsync -rltou --delete --delete-excluded ' # base rsync command to use
