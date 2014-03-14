
There are two servers in this folder.  They are both built on pyftplib, but they demonstrate different things. 

#### FTP Lib Server 

##### Files:
* This Folder
 * ftpdlibserver.py
 * test_server.py
 * conf_template.py
* In onedir/Server
 * map_fixer.py
 * server_conf.sh
 * start_server.sh
 * test_server_db.py 

#####Other Notes:
* Fairly stable. Noticed inactivity causes some issues.  Not hard to handle though. 
* Use server_conf.sh to setup sever
* Navigate to testing folder and lanch start_server.sh as root
 
#### Command Server 

#####Files:
* command_server.py
* demo_command_server.py

#### Both 

##### Requirements:
* pyftpdlib
* Right now severs is only setup for port 21
 
##### Setup:
* Two computers running linux
    * Launch the server with sudo 
    * Client can be run as normal user
* Two VM running linux  
    * If using Virtualbox
        * Go to settings
        * Network
        * Attach To: 
        * Switch to Bridge Adapter
        * Log into machine type ifconfig to get ip addy
    * Launch the server with sudo 
    * Client can be run as normal user

I still need to do an ubuntu to ubuntu test. 

| Server                        | Client                         |
| :---------------------------: | :----------------------------: |
| Ubuntu Server LTS 12.04  (vm)  | Arch Linux                     |



