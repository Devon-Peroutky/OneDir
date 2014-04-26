from pyftpdlib.log import logger
import os, inspect, sys 
from shutil import rmtree
from hash_chars import gen_hash, gen_salt
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import _strerror, FTPHandler, BufferedIteratorProducer
from sql_manager import TableManager, TableAdder, TableRemover
from datetime import datetime
from string import letters
from random import choice
from copy import deepcopy

__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '04/14/14'


class handler(FTPHandler):
    """
    This handles all the commands called to server, and user logins.
    """
    
    def __init__(self, conn, server, ioloop=None):
        FTPHandler.__init__(self, conn, server, ioloop)
        self.__add_proto_cmds()
        self.users = TableManager(container.get_acc_db(), container.get_acc_table())
        self.me = self.__dict__['remote_ip']
 
    def __add_proto_cmds(self):
        """
        For defining any SITE commands.
        """
        self.proto_cmds['SITE USERADD'] = {'auth': True, 'help': "SITE USERADD  <args>", 'perm': 'M', 'arg': True}
        self.proto_cmds['SITE USERDEL'] = {'auth': True, 'help': "SITE USERDEL  <args>", 'perm': 'M', 'arg': True}
        self.proto_cmds['SITE DEACTIV'] = {'auth': True, 'help': "SITE DEACTIV ", 'perm': 'e', 'arg':False}
        self.proto_cmds['SITE SYNC'] = {'auth':True, 'help':"SITE SYNC", 'perm':'r', 'arg':True}      
        self.proto_cmds['SITE GETLOG'] = {'auth':True, 'help':"SITE SYNC", 'perm':'M', 'arg':False}
        self.proto_cmds['SITE USERLIST'] = {'auth':True, 'help':"SITE USERLIST", 'perm':'M', 'arg':False}
        self.proto_cmds['SITE CHANGEPW'] = {'auth':True, 'help':'SITE CHANGEPW <args>', 'perm':'M', 'arg':True}
        self.proto_cmds['SITE SETPW'] = {'auth':True, 'help':'SITE SETPW <args>', 'perm':'e', 'arg':True}
        self.proto_cmds['SITE GETTIME'] = {'auth':True, 'help':'SITE GETTIME', 'perm':'r', 'arg':False}
        self.proto_cmds['SITE SETFLAG'] = {'auth':True, 'help':'SITE SETFLAG', 'perm':'e', 'arg':True}
        self.proto_cmds['SITE WHOAMI'] = {'auth':True, 'help':'SITE WHOAMI', 'perm':'r', 'arg':False}
        self.proto_cmds['SITE IAM'] = {'auth':True, 'help':'SITE IAM', 'perm':'e', 'arg':True}
        self.proto_cmds['SITE SIGNUP'] ={'auth':False, 'help':'SITE SIGNUP <args>', 'perm':'', 'arg':True}        

    def ftp_SITE_USERADD(self, line):
        """
        Admin command: Add user to database. 
        @param line: Is a single string representing 5 args. see __user_add. 
        """
        try:
            args = self.__strip_path_to_list(line)
            msg = "Expected 3 Args: text, int, txt, txt. Recieved: %s" % ' '.join(args)
            if not len(args) == 3:
                raise AttributeError(msg + ' ' + str(len(args)))
            args[1] = int(args[1])
            if not (args[1] == 0 or args[1] == 1):
                raise AttributeError(msg)
            rep = self.__user_add(args[0], int(args[1]), args[2])
            self.respond('200 %s' % rep)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 ' + why)

    def ftp_SITE_USERDEL(self, line):  
        """
        Admin Command: Removes a user from the database, 
        and removes their directoy from the file system.
        @param line: represents the username.  see __user_remove.
        """
        try:
            args = self.__strip_path_to_list(line)
            if not len(args) == 1:
                raise AttributeError('Expecting single arg. Not: %s.' % str(args))
            rep = self.__user_remove(args[0])
            self.respond('200 %s' % rep)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 ' + why)

    def ftp_SITE_DEACTIV(self, line):
        """
        User Command: deactivate profile, delete everything.
        @param line: none
        """
        username = self.__dict__['username']
        self.__user_remove(username)
        self.ftp_QUIT(line)

    def ftp_SITE_SYNC(self, line):
        """
        User Commad: Gets a list of files that needs syncing.
        @param line: represents the user id. (not username)
        @return: a list of files that need to be synced.  
        """
        try:
            time = self.__strip_path_to_list(line)
            if not len(time) == 1:
                raise AttributeError('Expecting a single arg')
            ret = self.__sync(time[0])
            ret = [str(x) + '\n' for x in ret]
            ret = iter(ret)
            producer = BufferedIteratorProducer(ret)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 ' + why)
        else:
            self.push_dtp_data(producer, isproducer=True, cmd='SITE SYNC')
            return line
    
    def ftp_SITE_GETLOG(self, line):
        """
        Admin Command: Gets the location of the log file. 
        @param line: none. (all ftp_ commands have a param regardless if they use it)
        @return:  The location of the log file on the server. 
        """
        try:
            log = deepcopy(container.get_log_file())
            log = log.split('/')[-1]
            self.respond('200 %s' % log)
        except:
            err = sys.exec_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)

    def ftp_SITE_USERLIST(self, line):
        """  
        Admin Command: Get lists of users.
        @param line: none
        @return: a list of users  
        """ 
        try:
            ret = self.__user_list()
            ret = [str(x) + '\n' for x in ret]
            ret = iter(ret)
            producer = BufferedIteratorProducer(ret)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 ' + why)
        else:
            self.push_dtp_data(producer, isproducer=True, cmd='SITE USERLIST')
            return line
    
    def ftp_SITE_CHANGEPW(self, line):
        """
        Admin Command: Change user password.
        @param line: username
        @param line: new password
        """
        try:
            args = self.__strip_path_to_list(line)
            if not len(args) == 2:
                msg = 'Expecting: username, new password. Not: %s' % str(args)
                raise AttributeError(msg)
            ret = self.__admin_change_password(args[0], args[1])
            self.respond('200 %s' % ret) 
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)

    def ftp_SITE_SETPW(self, line):
        """
        User Command: Change their own password.
        @param line: old password.
        @param line: new password. 
        """
        try:
            args = self.__strip_path_to_list(line)
            if not len(args) == 2:
                msg = 'Expecting: old password, new password.' 
                raise AttributeError(msg)
            ret = self.__user_change_password(args[0], args[1])
            self.respond('200 %s' % ret)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)

    def ftp_SITE_GETTIME(self, line):
        try:
            the_time = self.__get_time()
            self.respond('200 %s' % the_time)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)

    def ftp_SITE_SETFLAG(self, line):
        try:
            args = self.__strip_path_to_list(line)
            if not (len(args) > 0 and len(args) <= 2):
                msg = 'Need 1 or 2 args. Recieved: %s' % str(len(args))
                raise AttributeError(msg)
            else:
                ret = self.__set_flag(args)
                ret = 'a'
                self.respond('200 %s' % ret)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)
    
    def ftp_SITE_WHOAMI(self, line):
        try:
            ret = '%s:%s' % (str(self.__dict__['username']), self.me)
            self.respond('200 %s' % ret)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)
    
    def ftp_SITE_IAM(self, line):
        try:
            arg = self.__strip_path_to_list(line)
            if not len(arg) == 1:
                msg = 'Expecting single arg. Recieved: %s' % str(arg)
                raise AttributeError(msg)
            self.me = arg[0]
            self.respond('200 You are now know as: %s:%s' % (str(self.__dict__['username']), arg[0]))
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 %s' % why)

    def ftp_SITE_SIGNUP(self, line):
        try:
            arg = self.__strip_path_to_list(line)
            if not len(arg) == 1:
                msg = 'Expecting a single arg. Recieved : %s' % str(arg)
                raise AttributeError(msg)
            rep = self.__sign_up(arg[0])
            self.respond('200 %s' % rep)
        except:
            err = sys.exc_info()[1]
            why = _strerror(err)
            self.respond('550 ' + why)

    def __strip_path_to_list(self, line):
        """ 
        Private: do not call 
        @param line: a line recieved by an ftp_ command
        @return: a cleaned up list of the arguments passed in the line.
        """
        args = str(line).split(' ')
        args[0] = args[0].split('/')[-1]
        return args

    def __user_add(self, name, status, password): 
        """ 
        Private: do not call 
        @param name: A unique username
        @param status: A 0/1 integer. user=0/admin=1
        @param password: A already salted password.
        @param salt: The salt used on the password.
        """
        self.users.connect()
        check = self.users.pull_where('name', name, '=', ['status'])
        if not len(check) == 0:
            self.users.disconnect()
            raise AttributeError("'%s' name taken." % name)
        salt = gen_salt()
        password = gen_hash(str(password), salt)
        args = [name, status, password, salt, 'welcome', 'goodbye']
        self.users.quick_push(args)
        self.users.disconnect()
        ta = TableAdder(container.get_shares_db(), name)
        ta.add_column('time')
        ta.add_column('ip')
        ta.add_column('cmd')
        ta.add_column('line')
        ta.add_column('arg')
        ta.commit()
        del ta
        user_dir = "%s/%s" % (container.get_root_dir(), name)
        os.mkdir(user_dir)
        return 'User added.'

    def __user_remove(self, username):
        """ 
        Private: do not call 
        @param user_name: The name of the user to remove.
        """
        username = str(username)
        self.users.connect()
        self.users.delete_where('name', username, '=')
        self.users.disconnect()
        tr = TableRemover(container.get_shares_db(), username)
        user_dir = '%s/%s' % (container.get_root_dir(), username)
        rmtree(user_dir)
        return '%s deleted' % username

    def __sync(self, the_time):  
        """ 
        Private: do not call 
        @param time: The last time that the server was synced.
        """
        username = str(self.__dict__['username'])
        with TableManager(container.get_shares_db(), username) as tm:
            values = tm.pull_where('time', the_time, '>=')
        return values 

    def pre_process_command(self, line, cmd, arg):
        """
        Override Method: Add user logging.
        Should provide better info then override the 'log' method. 
        """
        FTPHandler.pre_process_command(self, line, cmd, arg)
        exclude = ['USER', 'TYPE', 'PASS', 'QUIT', 'PASV', 'SITE', 'PWD', 'LIST']
        if not cmd in exclude:
            self.__update_user_actions(line, cmd, arg)   

    def __update_user_actions(self, line, cmd, arg):  
        """
        Private: Do not call.
        In most cases the cmd and arg will be the easiest way to duplicate a cmd. 
        However, in some cases the full line will be needed.
        @param line: The line that was passed to the server
        @param cmd: The command for the server to call.
        @param arg: The argument for the commands. 
        """
        username = str(self.__dict__['username'])
        if username:
            try:
                line = str(line) 
                cmd = str(cmd)
                args = str(arg)
                when = self.__get_time()
                ip = str(self.me)
                with TableManager(container.get_shares_db(), username) as tm:
                    tm.quick_push([when, ip, cmd, line, args])
            except NameError:  # Thrown when deleting a user
                pass
    
    def __user_list(self):
        """
        Private: Do not call.
        @return: a list of users and some basic info about them.
        """
        self.users.connect()
        users = self.users.pull(col_list=['name', 'status', 'welcome', 'goodbye'])
        self.users.disconnect()
        users = [str(x) for x in users]
        return users

    def __admin_change_password(self, username, password):
        """
        Private: Do not call.
        @username: The name of the user to change the password of.
        @password: The plain text password.
        """
        self.users.connect()
        salt = self.users.pull_where('name', username, '=', ['salt'])
        if not len(salt) == 1:
            msg = 'User %s not found.' % username
            self.users.disconnect()
            raise AttributeError(msg)
        else:
            password = gen_hash(password, salt[0][0])
            self.users.update_where('name', str(username), 'password', password)
            self.users.disconnect()
            return 'Password Changed'        

    def __user_change_password(self, old_pw, new_pw):
        """
        Private: Do not call.
        @param old_pw: the old password.
        @param new_pw: the new password.
        """
        username = str(self.__dict__['username'])
        self.users.connect()
        check = self.users.pull_where('name', username, '=', ['password','salt'])[0]
        old_pw = gen_hash(old_pw, check[1])
        if not old_pw == check[0]:
            self.users.disconnect()
            msg = 'Wrong old password'
            raise AttributeError(msg)
        else:
            new_pw = gen_hash(new_pw, check[1])
            self.users.update_where('name', username, 'password', new_pw)
            self.users.disconnect()
            return 'Password Changed'
        
    def __get_time(self):
        """
        Private: Do not call.
        @return: the time on the server to the microsecond.
        @format: %Y%m%d%H%M%S%f = yyyymmddhhmmssmmnnmm - hours 24 hour clock
        """        
        x = datetime.now()
        return x.strftime('%Y%m%d%H%M%S%f')
        
    def __set_flag(self, *args):
        """
        Private: Do not call.
        A NOOP would also work for this task but no args.
        @param args: 1 to 2 args to set
        """
        args = args[0]
        if len(args) == 1:
            self.__update_user_actions(args[0], 'FLAG', args[0])
        else:
            self. __update_user_actions(args[0], 'FLAG', args[1])
        return 'Flag set'      
    
    def __sign_up(self, name): 
        """ 
        Private: do not call 
        @param name: A unique username
        @return: If signup works returns password, else 'False'
        """
        self.users.connect()
        check = self.users.pull_where('name', name, '=', ['status'])
        if not len(check) == 0:
            return 'False'
        plain = ''.join(choice(letters) for i in range(10))
        salt = gen_salt()
        password = gen_hash(str(plain), salt)
        args = [name, 0, password, salt, 'welcome', 'goodbye']
        self.users.quick_push(args)
        self.users.disconnect()
        ta = TableAdder(container.get_shares_db(), name)
        ta.add_column('time')
        ta.add_column('ip')
        ta.add_column('cmd')
        ta.add_column('line')
        ta.add_column('arg')
        ta.commit()
        del ta
        user_dir = "%s/%s" % (container.get_root_dir(), name)
        os.mkdir(user_dir)
        return plain


    ###{{{ Begin: Overrides }}}###
    
    # The following methods are designed to be overriden
    # I have not found a use for them just yet, however
    # I am going to leave them here as a reminder. 

    def on_connect(self):
        """
        As of right now, I don't think this is needed. 
        """
        pass

    def on_disconnect(self):
        """
        As of right now, I don't think this is needed.
        """
        pass

    def on_login(self, username):
        """
        Manages file shares. 
        """
        pass

    def on_login_failed(self, username, password):
        """
        As of right now, I don't think this is needed.
        """
        pass

    def on_logout(self, username):
        """
        Maybe put a marker as gone?
        """
        pass

    def on_file_sent(self, filename):
        """
        Checks for shares associated with the file. 
        """
        pass
    
    def on_file_recieved(self, filename):
        """
        Checks for shares associated with the file.
        """
        pass

    def on_incomplete_file_sent(self, filename):
        """
        Marks the file for resend?
        """
        pass
    
    def on_incomplete_file_recieved(self, filename):
        """
        Deletes the file left over part of the file?
        """
        os.remove(filename)
    
    ###{{{ END: Overrides ]}}}###

class authorizer(DummyAuthorizer):
    """
    Overriding the Authorizer to suit our needs.
    """

    def __init__(self):
        self.users = TableManager(container.get_acc_db(), container.get_acc_table())
        self.username = 'name'
        self.status = 'status'
        self.password = 'password'
        self.salt = 'salt'
        self.welcome = 'welcome'
        self.goodbye = 'goodbye'

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
        Modified to check the database for username and passwords instead of a dict.
        """
        msg = "Authentication failed."
        if not self.has_user(username):
            if username == 'anonymous':
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        if username != 'anonymous':
            self.users.connect()
            user_pw = self.users.pull_where(self.username, str(username), '=', [self.password])[0][0]
            user_salt = self.users.pull_where(self.username, str(username), '=', [self.salt])[0][0]
            self.users.disconnect()
            password = gen_hash(password, user_salt)
            if user_pw != password:
                raise AuthenticationFailed(user_pw)

    def get_home_dir(self, username):
        """
        Returns the home dir from the database
        """
        homedir = container.get_root_dir()
        if not self.has_perm(username, 'M'):
            homedir = '%s/%s' % (homedir, username)    
        homedir = unicode(homedir)
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
        user_perm = unicode(self.users.pull_where(self.username, str(username), '=', [self.status])[0][0])
        self.users.disconnect()
        if user_perm:
            return 'elradfmwM'
        else:
            return 'elradfmw'

    def get_msg_login(self, username): 
        """
        This is not really needed, but seems nice.
        """
        self.users.connect()
        login = unicode(self.users.pull_where(self.username, str(username), '=', [self.welcome])[0][0])
        self.users.disconnect()
        return login
        
    def get_msg_quit(self, username): 
        """
        This is not really needed, but seems nice.
        """
        self.users.connect()
        try:
            quit_msg = unicode(self.users.pull_where(self.username, str(username), '=', [self.goodbye])[0][0])
        except IndexError:
            quit_msg = 'Your account has now been deactivated'
        self.users.disconnect()
        return quit_msg

    ###{{{ END: Overrides }}}###


class container(object):
    """
    This class is designed to hold a single instance of the information that handler and authorizer
    need in order to function correctly. It also handles the checking of that information.  Though it 
    is possible to set the variables directly, it is not recommended. 
    """
    
    __accounts_db = None
    __accounts_table = None
    __shares_db = None
    __root_dir = None
    __log_file = None

    def __init__(self):
        """ Do not call. """
        raise Exception('Static class. No __init__')

    @staticmethod
    def set_acc_db(accounts_db, table_name):
        """
        @param accounts_db: The name of the sqlite3 database that holds the user accounts.
        """
        if not os.path.exists(accounts_db):
            raise AttributeError("The database %s not found." % accounts_db)
        with TableManager(accounts_db, table_name) as tm:
            account_columns = ['name', 'status', 'password', 'salt', 'welcome', 'goodbye']
            for col in account_columns:
                if not col in tm.table_col_names:
                    msg = 'Table missing column: %s -- The required columns are: %s' % (col, str(must_have))
                    raise AttributeError(msg)
        container.__accounts_db = accounts_db
        container.__accounts_table = table_name 
                
    @staticmethod
    def set_shares_db(shares_db):
        """
        @param shares_db: the table that holds the users shares.
        """
        if os.path.exists(shares_db):
            container.__shares_db = shares_db
        else:
            raise AttributeError("The database %s not found." % shares_db)

    @staticmethod
    def set_root_dir(root_dir):
        """
        @param root_dir: sets the root directory for the server.
        """
        if os.path.exists(root_dir):
            container.__root_dir = root_dir 
        else:
            raise AttributeError("%s not in file system." % root_dir)


    @staticmethod
    def set_log_file(filename): 
        """
        @param filename: the full path to the logfile.
        """
        if container.__root_dir == None:
            raise AttributeError('Please set root did before log file.')
        else:
            if not os.path.exists(filename):
                with open(filename, 'w'):
                    pass
            container.__log_file = filename

    @staticmethod
    def get_acc_db():
        """
        @return: the name of of the accounts database.
        """
        return container.__accounts_db

    @staticmethod
    def get_acc_table():
        """
        @return: the name of the accounts table.
        """
        return container.__accounts_table

    @staticmethod
    def get_shares_db():
        """
        @return: the name of the shares database.
        """
        return container.__shares_db

    @staticmethod
    def get_root_dir():
        """
        @return: the name of the root dir.
        """
        return container.__root_dir
    
    @staticmethod
    def get_log_file():  
        """
        @return: the path to the logfile.
        """
        return container.__log_file
