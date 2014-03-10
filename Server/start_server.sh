#!/bin/bash

# I wrote this script in lieu of writing to your /fstab which we will have to do for a real server
# In layman's terms, for a mount folder to presist after reboot, the fstab has to be modified to include the new mount
# The fstab is an important file, and I don't want to mess with yours... (just yet) :)
# So instead, this checks if the folders are still mounted, and remounts them if needed.
# Also launches the server for ease of use


if [ `whoami` == "root" ]
then
        ISMOUNTED=`cat /proc/mounts | grep testing_server | wc -l`
        if [ $ISMOUNTED == 0 ] 
        then 
            `mount --bind $(pwd)/user2/shared_folder/ $(pwd)/user1/shared_folder/`
        fi
            `python2.7 server.py` 
else
    echo 'This needs to be run as root (sudo)'
fi
