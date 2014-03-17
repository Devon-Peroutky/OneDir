OneDir
======
OneDir (pronounced "wonder") will be a system that allows users to keep copies of a file system on their local machines and on a server. Changes made in one place will automatically (in the background) be synchronized on all machines storing copies of the files. Initially the system will be target to run on machines running version 12.04 LTS of Ubuntu.)

OneDir server software will run on a particular server computer, and a "local user" (a person who owns the files on a local machine) will be able to create a password-protected account on that machine. Once an account is created, all files in specific directory, ~/onedir (i.e. the subdirectory onedir under the local user's home directory) will be kept synchronized. This means that when the local user changes anything in the directory tree rooted at ~/onedir on the local machine, that change will promptly be reflected in the files stored for that user on the server machine. Also, additional local machines might be connected to the server using that account, and changes on the server will then be promptly reflected on each of these other local machines.

On the local machine, the local user will be required to start the local machine's OneDir services that run in the background. (Implementation note for students: this can be as simple as starting a Python program in the background). Also, the local user will in some way be able to interact with the server as follows:

create a new account with a user-id and password
turn automatic synchronization on and off
change the password associated with the user-id
We anticipate later adding the the ability to share files among OneDir users who are using the same server.

A second kind of user, an admin user, will be able to run a program on the server to do operations like the following:

get information about the OneDir users registered with this server
see information about the number and size of files stored, in total and per user
remove a user's account, and optionally the user's files
change a user's password
see information about the history of connections involving synchronization (a kind of "traffic report log")
Other operations may be added later.

Also, some user on the server machine will be required to start the OneDir server software before any interactions with local machines can take place, and before the admin user can carry out any of the operations listed above.

Development constraints:

All code must be written in Python, with Ubuntu 12.04 LTS as the target platform at the end of the project.
Any database needs should use SQLite as an embedded database on the same machine the program using the database is running. We do not anticipate the need for running a separate database server in addition to the OneDir server.
When appropriate, JSON should be considered for passing or storing certain kinds of information.
Setting up and starting both the client and server software should be simple and quick to do.
Security issues matter to the customer, and specific security related issues may be brought up later in the project.
