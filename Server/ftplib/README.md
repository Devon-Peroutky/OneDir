This is still very early in developement and it can not do too much:
In the email I sent, I told you that this only works with two computers running linux. 
Which I am sure would suck for those who don't own to computers running linux.  

So I found a fix:
The problem with trying to run things through Virtualbox, was that I was trying to port forward everything.
The solution was to give each virtual machine its own ip address and don't worry about any forwarding. 

To do this go to your VM settings
Network
Attach To: Bridge Adapter
OK

Load your machine and type ifconfig to get your ip
it should be under
eth0
    inet addr:x.x.x.x

if your machine complains about not having ifconfig
use:  ip addr
but that should not be a problem with Ubuntu machines

I have now tested it on:
Server:
    Arch Linux
    Ubuntu Sever LTS 12.04
Client:
    Arch Linux
    Ubunutu Desktop LTS 12.04

