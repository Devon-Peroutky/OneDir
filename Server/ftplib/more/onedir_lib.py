# There is a fairly high chance that we need to put pyftpdlibs copyright onto this
# I believe this may qualify as modifications, or significant portions of the code

import os
import sys
import hashlib
import subprocess
from copy import deepcopy
from pyftpdlib.handlers import *
from pyftpdlib.authorizers import DummyAuthorizer, AuthorizerError, AuthenticationFailed
from sql.sql_manager import TableManager

# TODO
# Don't forget to push changes of sql_manager ... and fix tests if any broke. 
# TODO

# use_sendfile
# when True uses sendfile() system call to send a file resulting in faster uploads (from server to client). Works on UNIX only and requires pysendfile module to be installed separately: http://code.google.com/p/pysendfile/ New in version 0.7.0


# TODO ... this is a mess right now... it is unlikely you will be able to use it until i clean a bunch of stuff up. 
# it works though


class SharesError(Exception):
    """
    Ensures that shares gets set
    """
    pass


user_shares = None
users_database = None


def set_shares(database_name):  # TODO checks and stuffs
    global user_shares
    user_shares = database_name


proto_cmds['TEST'] =     {
                            'auth': True,
                            'help': 'Syntax: TEST (Random Testing)',
                            'perm': None,
                            'arg' : True
                         }                         

proto_cmds['SHUTDOWN'] = {
                            'auth': True,
                            'help': 'Syntax: SHUTDOWN (Shutdowns server)',
                            'perm': 'M',
                            'arg' : False
                         }

proto_cmds['WHOAMI'] =   {
                            'auth': True,
                            'help': 'Syntax: WHOAMI (Username)',
                            'perm': None,
                            'arg' : False
                         }

proto_cmds['CHECKSUM'] = {
                            'auth': True,
                            'help': 'Syntax: CHECKSUM <sp> filename (Files sha224 checksum)',
                            'perm': 'r',
                            'arg' : True
                         }

# EXAMPLE because this was hard to figure out, sending a list
proto_cmds['JLIST'] =    {
                            'auth': True,
                            'help': 'not important',
                            'perm': None,
                            'arg' : False
                         }


class OneDirHandler(FTPHandler):
    def __init__(self, conn, server, ioloop=None):
        FTPHandler.__init__(self, conn, server, ioloop=None)
        if not user_shares:
            raise SharesError('Before Lanching server, set shares database') 
        self.shares = deepcopy(user_shares) 

    ###{{{ Start: Defining Commands }}}###

    def ftp_TEST(self, line):  # TODO delete, only for testing
        self.respond('200 %s' % self.username)

    def ftp_SHUTDOWN(self, line):
        """
        Shutdowns server
        FTP.voidcmd('shutdown')
        """
        self.respond('200 Sever Shutting Down')
        sys.exit(0)

    def ftp_WHOAMI(self, line):
        """
        This is more of an example of how to get the username then a useful function
        FTP.voidcmd('whoami')
        """
        self.respond('200 %s' % self.username)

    def ftp_CHECKSUM(self, filename):  # TODO handle arguments checking 
        """
        Returns the checksum of a file.
        Eventually I want to switch to being able to get any checksum you want not just sha224
        FTP.retrlines('checksum filename', callback) 
        """
        checksum = [hashlib.sha224(open(filename, 'rb').read()).digest()]
        producer = BufferedIteratorProducer(iter(checksum))
        self.push_dtp_data(producer, isproducer=True, cmd='CHECKSUM')
        return filename

    def ftp_JLIST(self, line): # TODO example delete later
        """
        This kind of sucks that this is that hard.
        But it works.

        To catch it. 
        cb = [] 
        def callback(line):
            global cb
            cb += [cb]
        FTP.retrlines('jlist', callback) 
        the values are in cb now   
        """
        to_send = ['one\n', 'two\n', 'three\n'] # a list of strings (it has to be strings)... ending in \n
        i_send = iter(to_send) # now an iterator
        producer = BufferedIteratorProducer(i_send)
        self.push_dtp_data(producer, isproducer=True, cmd='JLIST')
        return line 

    ###{{{ End: Defining Commands }}}###

    ###{{{ Start: Commands Actually Meant to be Ovewritten }}}###

    def on_login(self, username):  #TODO This will do even more but this is a good first step
        """
        
        """
        # open user_shares db, find the shares... go through and mount them one at a time... this
        # this is just a hard coded examle it needs a file system in place
        cwd = os.getcwd()
        command = 'mount --bind %s/server/one/shared_folder/ %s/server/two/' % (cwd, cwd)
        command = command.split(' ')
        subprocess.Popen(command)

    def on_logout(self, username): # TODO like otherone still hardcoded
        """
        This is only called if 
        FTP.quit()... FTP.close() does not do it!!!! 
        SO THE CLIENT NEEDS TO USE 'with'!!! 
        """
        cwd = os.getcwd()
        command = 'umount %s/server/one/shared_folder/' % cwd
        command = command.split(' ') 
        subprocess.Popen(command) 

    ###{{{ End: Commands Actually Meant to be Ovewritten }}}###


class OneDirAuthorizer(DummyAuthorizer):
    """
    Overriding the Authorizer to suit our needs.
    """
    def __init__(self, database_name, table_name):
        self.users = TableManager(database_name, table_name)
        global users_database
        users_database = (database_name, table_name)
        # [START: The names of the in table] 
        # More can exist, but these are needed for this class the names are changeable
        self.username = 'username'
        self.password = 'password'
        self.home_dir = 'dir'
        self.perm = 'perm'
        self.msg_login = 'login'
        self.msg_quit = 'quit'
        # [End: The names of the in table]
        self._validate_table()

    def _validate_table(self): 
        """
        Checks that the table has the required information to validate a user 
        """
        must_have = [self.username, self.password, self.home_dir, self.perm, self.msg_login, self.msg_quit]
        for col in must_have:
            if not col in self.users.table_col_names:
                msg = 'Table missing column: %s -- The required columns are: %s' % (col, str(must_have))
                raise ValueError(msg)

    ###{{{ Begin: Remove Methods }}}###
    
    def add_user(self, username, password, homedir, perm='', msg_login='', msg_quit=''):
        """
        We will check Database for Users.  
        """
        pass

    def remove_user(self, username):
        """
        We will check Database for Users
        """
        pass

    def override_perm(self, username, directory, prem, recursive=False): 
        """
        If we have too, we can override this one, but it don't think it is needed
        """
        pass 
   
    ###{{{ End: Remove Methods }}}### 
    
    ###{{{ Begin: Overrides }}}###
    
    def validate_authentication(self, username, password, handler):
        """
        Modified to check the database for usernames and passwords instead of a dict. 
        """
        msg = "Authentication failed."
        if not self.has_user(username):
            if username == 'anonymous':
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        if username != 'anonymous': 
            self.users.connect()
            user_pw = self.users.pull_where(self.username, str(username), '=', [self.password])[0][0]
            self.users.disconnect()
            if user_pw != password:
                raise AuthenticationFailed(user_pw)
       
    def get_home_dir(self, username):
        """
        Returns the home dir from the database
        """
        self.users.connect()
        home_dir = unicode(self.users.pull_where(self.username, str(username), '=', [self.home_dir])[0][0])
        self.users.disconnect()
        return home_dir

    def has_user(self, username):
        """
        Check database for user
        """
        self.users.connect()
        user_list = self.users.pull_where(self.username, str(username), '=', [self.username])
        self.users.disconnect()
        if len(user_list) == 0:
            return False
        elif len(user_list) == 1:
            return True
        else:
            raise AuthorizerError('Oh no, there seems to be two of you.  That is not allowed') 

    def has_perm(self, username, perm, path=None):
        """
        I have removed the operms from this, we can bring it back if needed 
        """
        user_perm = self.get_perms(username)
        return perm in user_perm

    def get_perms(self, username): # TODO note: I think 'M' will only be given to admin everyone else gets all execept 'M' 
        """
        Return current user permissions.
        """
        self.users.connect()
        user_perm = unicode(self.users.pull_where(self.username, str(username), '=', [self.perm])[0][0])
        self.users.disconnect()
        return user_perm        

    def get_msg_login(self, username):
        """
        This is not really needed, but seems nice.
        """
        self.users.connect()
        login = unicode(self.users.pull_where(self.username, str(username), '=', [self.msg_login])[0][0])    
        self.users.disconnect()
        return login
        
    def get_msg_quit(self, username):
        """
        This is not really needed, but seems nice.
        """
        self.users.connect()
        quit_msg = unicode(self.users.pull_where(self.username, str(username), '=', [self.msg_quit])[0][0])
        self.users.disconnect()
        return quit_msg

    ###{{{ END: Overrides }}}###
