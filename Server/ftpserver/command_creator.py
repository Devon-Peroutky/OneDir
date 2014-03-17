#
# This is still highly experimental, but working
#
# Command types:
#   void: A command that will run and return a responce string, that would be printed.  FTP.voidcmd() 
#   begin: A command that will send its responce before execution.  FTP.voidcmd()
#   string: A command that will return a string that you can capture.  FTP.retrlines()
#   list: A command that will return a list (of strings) that can be captured.  FTP.retrlines()
#
# To Uses: Functions only! No Methods!
#   Allowed Args:
#       user - Will give you the user who called the command
#       cwd - Will give you the dir that the user is in
#       database - Will give you the name of the user database
#       table - Will give you the name of the user table
#       args - Will give you the args you passed 
#
#   Note: If you pass more then one argument, they will all be passed through args.  So you will have to handle seperating 
#           them in your function 
#   Note: It does not matter what order your arguments are in.
#   Note: If you use the args arguments, the caller has to include the argument
#   Note: To add arguments the OneDirHandler must hold a copy of it. 
#
#   Admins Commands are given the 'M' perm
#   Users Commands are given 'r' prem
#
#   

import sys, inspect
from pyftpdlib.handlers import _strerror, BufferedIteratorProducer


__author__ = 'Justin Jansen'
__status__ = 'Developement'
__data__ = '03/13/14'


void_template = "" \
"""
def ftp_%(cmd)s(self, line):
    try:%(need)s
        my_func = __import__('%(mod)s')
        my_func = my_func.%(func)s(%(arg)s)
        my_func = str(my_func)   
        self.respond('200 ' + my_func)
    except:
        err = sys.exc_info()[1]
        why = _strerror(err)
        self.respond('550 ' + why)
"""


begin_template = "" \
"""
def ftp_%(cmd)s(self, line):
    try: 
        my_func = __import__('%(mod)s')
    except:
        err = sys.exc_info()[1]
        why= _strerror(err)
        self.respond('550' + why)
    else:
        self.respond('200 Beginning: %(cmd)s currently execution unchecked')
        %(need)s
        my_func.%(func)s(%(arg)s) 
"""


string_template = "" \
"""
def ftp_%(cmd)s(self, line):
    try:%(need)s
        my_func = __import__('%(mod)s')
        my_func = my_func.%(func)s(%(arg)s)
        my_func = str(my_func)   
    except:
        err = sys.exc_info()[1]
        why= _strerror(err)
        self.respond('550' + why) 
    else:
        self.push_dtp_data(my_func, cmd='%(cmd)s')
        return line
"""


list_template = "" \
"""
def ftp_%(cmd)s(self, line):
    try:%(need)s
        my_func = __import__('%(mod)s')
        my_func = my_func.%(func)s(%(arg)s)
        my_func = [str(x) + '\\n' for x in my_func]  
        my_func = iter(my_func)
        producer = BufferedIteratorProducer(my_func)
    except:
        err = sys.exc_info()[1]
        why= _strerror(err)
        self.respond('550' + why) 
    else:
        self.push_dtp_data(producer, isproducer=True, cmd='%(cmd)s')
        return line    
"""


class NamingError(Exception):
    """
    Forced into using fairly strict naming pattern.
    """
    pass


class CommandCreator(object):
    """
    Translates methods into the format that they need to be in to run on the server.
    """
    def __init__(self):
        self.templates = ['void', 'string', 'list', 'begin']
        self.methods = []
        
    def add_cmd(self, func, is_admin=False):
        """
        Adds a command into the queque for being added to the server
        """ 
        method = {}
        vals = func.func_name.split('_')
        if vals[0] == 'void':
            method['template'] = void_template
        elif vals[0] == 'string':
            method['template'] = string_template
        elif vals[0] == 'begin':
            method['template'] = begin_template
        else:
            method['template'] = list_template
        method['cmd'] = vals[1].upper()
        if not vals[0] in self.templates:
            msg = "The first part of the function name must be %s" % str(self.templates)
            raise NamingError(msg) 
        if is_admin:
            method['perm'] = 'M'
        else:
            method['perm'] = 'r'
        args = inspect.getargspec(func)[0]
        if 'args' in args:
            method['has_arg'] = True
            method['inst'] = "Syntax %s <sp> args" % method['cmd']
        else:
            method['has_arg'] = False
            method['inst']=  "Syntax %s" % method['cmd']
        made = self.arg_maker(args)
        method['need'] = made[0]
        method['arg'] = made[1]
        method['func'] = func.__name__
        method['mod'] = func.__module__
        self.methods += [method]

    def find_class(self):
        """
        For finding the server.
        """
        stack = inspect.stack()
        frame = stack[1][0]
        return frame.f_locals.get('self', None)

    def create_methods(self, caller, proto_cmds):
        """
        Takes the functions and turns them into methods on the server.  
        """
        self.caller = caller
        for method in self.methods:
            proto_cmds[method['cmd']] = { 'auth':True, 'help':method['inst'], 'perm':method['perm'], 'arg':method['has_arg'] }
            exec(method['template'] % method)
            func_name = 'ftp_%s' % method['cmd']
            setattr(caller.__class__, eval(func_name).__name__, eval(func_name))

    def arg_maker(self, args):
        """
        Used to create and pass extra arguments
        """
        added_lines  = ''
        arg_line = ''
        for arg in args:
            if arg == 'user':
                added_lines += '\n\tuser = self.username'
                arg_line += ' user,'
            if arg == 'cwd':
                added_lines += '\n\tcwd = self.fs.cwd' 
                arg_line += ' cwd,'
            if arg == 'table':
                added_lines += '\n\ttable = self.users_database[1]'
                arg_line += ' table,'
            if arg == 'database':
                added_lines += '\n\tdatabase = self.users_database[0]'
                arg_line += ' database,'
            if arg == 'args':
                arg_line += ' line,'
        arg_line = arg_line[1:-1]
        return (added_lines, arg_line)
