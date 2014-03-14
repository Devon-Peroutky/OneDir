import os, inspect, sys
from command_creator import CommandCreator, NamingError
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import *
sys.path.insert(0, '../sql/')
from sql_manager import TableManager


__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__diate__ = '03/13/14'


cmd_creator = None
users_database = None


def set_command_creator(user_module, admin_module):
    """
    This saves us from having to override a class or two in order to use command creater in 
    OneDirHandler.  It basically is a pre constructor constructor. 
    """
    global cmd_creator
    c = CommandCreator()
    users = inspect.getmembers(user_module, inspect.isfunction)
    for func in users:
        try:
            c.add_cmd(func[1])
        except NamingError:
            pass
    admins = inspect.getmembers(admin_module, inspect.isfunction)
    for func in admins:
        try:
            c.add_cmd(func[1], is_admin=True)
        except NamingError:
            pass
    cmd_creator = c


class OneDirHandler(FTPHandler):
    def __init__(self, conn, server, ioloop=None):
        FTPHandler.__init__(self, conn, server, ioloop=None)
        self.users_database = users_database
        cl = cmd_creator.find_class()
        global proto_cmds
        cmd_creator.create_methods(cl, proto_cmds) 

class OneDirAuthorizer(DummyAuthorizer):
    """
    Overriding the Authorizer to suit our needs.
    """
    def __init__(self, database_name, table_name):
        self.users = TableManager(database_name, table_name)
        global users_database
        users_database = (database_name, table_name)
        self.username = 'username'
        self.password = 'password'
        self.homedir = 'dir'
        self.perm = 'perm'
        self.msg_login = 'login'
        self.msg_quit = 'quit'
        self._validate_table()

    def _validate_table(self): 
        """
        Checks that the table has the required information to validate a user 
        """
        must_have = [self.username, self.password, self.homedir, self.perm, self.msg_login, self.msg_quit]
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
        homedir = unicode(self.users.pull_where(self.username, str(username), '=', [self.homedir])[0][0])
        self.users.disconnect()
        homedir = os.path.realpath(homedir)
        return homedir

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

    def get_perms(self, username): 
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

