## Description ##

It makes incremental backups with rsync.

It creates a fully functional (and apparently, complete) copy of the current state of the directory to back up, that can be traversed, read, and copied from as normal. However, it takes advantage of hard links in Linux to link files unmodified from previous backups. This way the backup is incremental, in the sense that only new and modified files are actually copied, while the rest is linked and does not fill up disk space.

Whichever backup can be deleted and, due to how hard links work, the rest of the backups will not be affected at all.

## Depencencies ##

increback makes use of the logworks lib, by the same author. logworks is distributed with increback, but can be independently obtained from:

    https://github.com/isilanes/logworks

## Usage ##

For usage, run:

    $ python3 increback.py -h

The script expects to read from a configuration file in JSON format (see 'sample.json'). This file should contain a dictionary with two keys: "items" and "colors".

### items ###

One dictionary per item, where the key should be the name of the item (e.g. "photos"), and its value another dictionary with the following keys:

* *active*. Its value should be either "true" (if we want this element to be backed up when the script is run), or "false" (to deactivate backup of this element without having to delete it from the conf).
* *fromdir*. Its value should be a string with the path of the directory we want to back up.
* *todir*. Its value should be a string with the path of the base directory where the backup will be made. Final backup dirs are subdirs of this path, their name being the date of the backup, in YYYY-MM-DD format (e.g., if "todir" is "/mnt/backup/photos/", a backup made today would reside in directory "/mnt/backup/photos/2017-07-24").

### colors ###

Optional values for terminal colors to colorize some outputs. They should be integers in the 31--37, 41--47 ranges, just as regular codes for terminal color printing.

* *error*. The color for the "ERROR" keyword. We suggest "31" (red).
* *name*. The color of some elements that are names (paths to files, item names...).
