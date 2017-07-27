"""
increback
(c) 2008-2014, 2017. Iñaki Silanes
"""

# Our libs:
from libib import core, logworks

# Functions:
def main():
    """Execute this when called as stand-alone."""
    
    # Get command-line options:
    opts = core.parse_args()

    # Logger object:
    logger = logworks.Logger(opts.log_conf, opts.no_colors)

    # General variables in centralized Data() object:
    data = core.Data(opts, logger=logger)

    # Perform backup of each element:
    for  item in data.items:
        # Check destination is mounted:
        data.check_dest_dir_mounted(item)

        # Skip if backup done today:
        if data.is_backup_done_for(item):
            citem = "[{item}]".format(item=item)
            citem = data.msg.name_color(citem)
            print("Item {item} already backed up. Skipping...".format(item=citem))
            continue

        # Build rsync command(s) and run:
        sync = core.Sync(data, item)
        sync.run(opts)


# If called as stand-alone:
if __name__ == "__main__":
    main()
