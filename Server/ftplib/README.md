This is still early in development, and a lot more is to come.  

##### Requirements:
* pyftpdlib
* Sever needs a file on it called 'transfer_file'
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

##### Other Notes:
I added my SqlManager to this:
* It is based on my hw4 *crawler.py* SqlManager, but in theory better
* It is still UNTESTED 
* You should not use SqlManager itself, instead use:
   * TableAdder, for adding a new table
   * TableManager, for manipulating tables.  
* If there are any methods you think we need and you don't want to write them let me know and I will


I have now tested it on:

| Server                        | Client                         |
| :---------------------------: | :----------------------------: |
| Arch Linux                    | Arch Linux                     |
| Ubuntu Sever LTS 12.04  (vm)  | Ubunutu Desktop LTS 12.04 (vm) |


