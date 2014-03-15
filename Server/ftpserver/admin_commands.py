import sys
sys.path.insert(0, '../sql')
from sql_manager import TableManager


# These are direct copies so that you can see they are here
def args_strip(args):
    """
    This command is not injected into the handler. 
    It is used as a quick way to seperate the filepath from the argument
    @return: The arguement without the file path
    """
    return str(args).split('/')[-1]


# These are direct copies so that you can see they are here
def get_path(args):
    """
    This command is not injected into the handler. 
    It is also used to seperate the filepath from the argument.
    @return: The path without the argument
    """
    path = str(args).split('/')[:-1]
    return '/'.join(path)


def record_data(user=None, cwd=None, database=None, table=None, args=None):
    """
    This is another method to help you diagnose the kind of arguments you are recieving.
    From experiance, it is likely that the problem is something is unicode when you are 
    expecting it to be a ascii string. 
    """
    with open('info.txt', 'a') as w:
        w.write('\nStart:')
        if user:
            w.write('\n\t%s' % user)
        if database:
            w.write('\n\t%s' % database)
        if table:
            w.write('\n\t%s' % table)
        if cwd:
            w.write('\n\t%s' % cwd)
        if args:
            w.write('\n\t%s' % args)


def begin_shutdown():
    """
    Shuts the server down. 
    """
    sys.exit(0)


def list_tusers():
    """
    This was writen as a test for a the list command, 
    but I decided to leave it incase it had use later. 
    """
    with TableManager('Users.db', 'users') as t:
        return [str(x) for x in t.pull()]
    return ['0']


def void_useradd(database, table, cwd, args):
    """
    This creates new users.  It should be altred to check for a username ahead of time,
    so that it does not duplicate users. Which could cause issues.  
    This also stores the password as given. Which I believe is bad practice. 
    """
    args = args_strip(args)
    args = args.split(' ')
    cwd = str(cwd)
    un = args[0]
    pw = args[1]
    push = [un, pw,'%s/%s' % (cwd[1:], un), 'elradfmw', 'Wecome %s' % un, 'Bye %s' % un]
    with TableManager(database, table) as t:
        t.quick_push(push)
    return '%s added to database' % un
