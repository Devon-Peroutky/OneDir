I had several servers in here, they have all been merged into the best one.

The server handles all the tpyicals things already, with a few extras for demos. 

I have modified the authenticator to read from a database instead loading every user into before the server starts. 
There is a better option, but it seems like we will not be allowed to use it. 

I made a command creator also for this server. All you have to do is create a function in either user_commands.py or admin_commands.py and the creator will automatically include it as a server command.  Harder then it sounds. For details read the top of command_creater.py.  More command types can be created as needed. 

I also have figured out how to share folder mostly painlessly. But I have not got around to doing so.  

There is still an issue with connections timing out after longer periods of inactivity. That will have to be handled on the client in. 

Big obstical with this still.  Is there server can not call the client the client can only call the server.  There seems to be a few lighter python classes that we can use to manage that though. The client will need a listener. 

The server can be sped up by:
* use_sendfile:
* when True uses sendfile() system call to send a file resulting in faster uploads (from server to client). Works on UNIX only and requires pysendfile module to be installed separately: http://code.google.com/p/pysendfile/ New in version 0.7.0
* it is not slow at all though.  
* i just keep forgetting to implement it. 


I still need to do an ubuntu to ubuntu test. 

| Server                        | Client                         |
| :---------------------------: | :----------------------------: |
| Ubuntu Server LTS 12.04  (vm)  | Arch Linux                     |



