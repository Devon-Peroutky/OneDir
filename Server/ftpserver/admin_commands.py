import sys
sys.path.insert(0, '../sql')
from sql_manager import TableManager


"""
These commands will be automatically added into the server for 
client server com. 
Same for user_commands.
"""
def args_strip(args):
    return str(args).split('/')[-1]

def get_path(args):
    path = str(args).split('/')[:-1]
    return '/'.join(path)



def record_data(user=None, cwd=None, database=None, table=None, args=None):
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
    sys.exit(0)

def void_test():
    return 1   

def list_tusers():
    with TableManager('Users.db', 'users') as t:
        return [str(x) for x in t.pull()]
    return ['0']

def outside_func():
    return 'x';

def void_inside():
    return outside_func()

def void_useradd(database, table, cwd, args):
    args = args_strip(args)
    args = args.split(' ')
    cwd = str(cwd)
    un = args[0]
    pw = args[1]
    push = [un, pw,'%s/%s' % (cwd[1:], un), 'elradfmw', 'Wecome %s' % un, 'Bye %s' % un]
    with TableManager(database, table) as t:
        t.quick_push(push)
    return '%s added to database' % un
