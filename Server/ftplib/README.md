##### Requirements:
* pyftpdlib
* Right now sever is only setup for port 21
 
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
 * Use server_conf.sh to setup sever
 * Navigate to testing folder and lanch start_server.sh as root
 
#####Other Notes:
* Fairly stable. Noticed inactivity causes some issues.  Not hard to handle though. 
* This is only a client server! We still need something that can handle admin commands! 
* I still need to do an ubuntu to ubuntu test. 

| Server                        | Client                         |
| :---------------------------: | :----------------------------: |
| Ubuntu Server LTS 12.04  (vm)  | Arch Linux                     |



