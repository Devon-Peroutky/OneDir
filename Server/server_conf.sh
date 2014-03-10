#!/bin/bash

# Justin Jansen
# 3/7/14

# This needs root access, be careful with it.
# It calls: 
# rm -r -f $MYPATH
# Which will delete everything in the folder $MYPATH
# The folder $MYPATH is dynamical generated.  
# It assumes that the file is in /path/to/onedir/Server
# So it drops back to /path/to/ and starts creating files there
# If this script has been moved from /path/to/onedir/Server to lets say /home/usersname (aka ~/)
# Then the files are being created in your root directory... WHICH WILL BE ALLOWED BECAUSE THIS NEEDS ROOT ACCESS
# You don't want to be messing around there
# It is safest to leave this program in /path/to/onedir/Server and just run it from there

if [ `whoami` == "root" ]
then 

    if [ "$1" == "make" ]
    then
        # Create a root folder
        `mkdir ../../testing_server`
        MYPATH=`readlink -f ../../testing_server`
        `mkdir $MYPATH/sql`
        
        # Copy sever into root folder
        `cp sql/sql_manager.py $MYPATH/sql/.`
        `cp start_server.sh $MYPATH/.`
        `sed 's/Server.sql.sql_manager/sql.sql_manager/g' ftplib/ftplibserver.py > $MYPATH/server.py`
        `touch $MYPATH/sql/__init__.py`

        # Create a few directories
        `mkdir $MYPATH/user1`;
        `mkdir $MYPATH/user1/upload_to`;
        `mkdir $MYPATH/user1/download_from`;
        `mkdir $MYPATH/user1/shared_folder`;        
        `mkdir $MYPATH/user2`;
        `mkdir $MYPATH/user2/shared_folder`;

        # Create a file to test downloading, add some text to it
        `touch $MYPATH/user1/download_from/to_download.txt`;
        `echo "This is some text in to_download.txt" >> $MYPATH/user1/download_from/to_download.txt`;
        
        # In USER2: create a file to share, add some text to it
        `touch $MYPATH/user2/shared_folder/shared_file.txt`;
        `echo "This is text shared_file.txt" >> $MYPATH/user2/shared_folder/shared_file.txt`;

        # Share the files between the two users, This is why this script needs root
        `mount --bind $MYPATH/user2/shared_folder/ $MYPATH/user1/shared_folder/`
        
        # Sets up the database
        `python2.7 test_server_db.py`
        `mv Users.db $MYPATH/.`
       
        # Creates a server map
        touch server_map.txt
        `find $MYPATH >> server_map.txt`
        `python2.7 map_fixer.py $MYPATH server_map.txt`
        `mv server_map.txt $MYPATH/.`        
   
        # Read Write permission because this was created as root, dont really need it but... it's nice
        `chmod -R a+rw $MYPATH`
      
        echo "Server ready. Navigate to $MYPATH and run python server.py to start using it."
    
    elif [ "$1" == "delete" ]
    then 
        MYPATH=`readlink -f ../../testing_server`
            
        # un-link the shared folder
        `umount $MYPATH/user1/shared_folder`

        # delete everything
        `rm -r -f $MYPATH`

        echo "All files in $MYPATH have been deleted"
    
    else
        echo "Command line arguments are 'make' or 'delete'"
    fi

else 
    echo "This program need to be run as root (sudo)"
    echo "Command line arguments are 'make' or 'delete'"
fi

