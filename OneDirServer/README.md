##server_lib 
This is just a quick, overview of the commands that you have at your disposal from the server side.  I am adding this because I have noticed that I keep forgetting to add commands to ../OneDirListener/client.py.  If you see a command is missing let me know.

### Site Commands
#### Admin only:
useradd  - add a user to the database
userdel - delete a user from the database
getlog - returns the server log file
userlist - list the users and some general info on them
changepw - resets user password
#### Client and Admin:
Deactiv - deactivate your account
sync - get a list of your last actions on the server
setpw - set your password
gettime - get server time (import that you use this for maintaining time, between client server com.)
setflag - adds a flag in your command db, with two option one word arguments. (For syncing)
whoami - returns username:nickname if nick name not set username:ip
iam - set your nick name setting nick name is useful for distiguishing which computer is doing the sync'ing
#### No Auth Required Commands:
signup - create new users.  Returns password for user you just created

### All FTP Commands
[Wiki FTP Command List](http://en.wikipedia.org/wiki/List_of_FTP_commands)

