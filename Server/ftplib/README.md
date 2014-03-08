This is still early in development, and a lot more is to come.  

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
 * Use server_conf.sh to setup sever, navigate to testing folder and lanch server.py as root

##### Other Notes:
* I have been doing a lot of restructuring, the files right now are more templates then actually functional
* I will have working code up again soon
* The server should still work, just the cleint is not configured to talk to it anymore


I have now tested it on: (before restructuring)

| Server                        | Client                         |
| :---------------------------: | :----------------------------: |
| Arch Linux                    | Arch Linux                     |
| Ubuntu Sever LTS 12.04  (vm)  | Ubuntu Desktop LTS 12.04 (vm)  |


