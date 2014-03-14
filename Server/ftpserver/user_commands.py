import hashlib
# everything must have underscore right now

def args_strip(args):
    return str(args).split('/')[-1]

def get_path(args):
    path = str(args).split('/')[:-1]
    return '/'.join(path)

def void_need(user, cwd, database, table, args):
    a = args_strip(args)
    b = get_path(args) 
    return "%s %s %s %s %s %s %s" % (user, cwd, database, table, args, a, b)

def void_abc(user):
    return user

def string_checksum(args):
    """
    This is a hackish solution, but when the file was written to the server. A extra line was added to it.
    """
    with open(args, 'rb') as r:
        fn = r.read()
    print fn
    fn = fn.splitlines()
    fn = '\n'.join(fn)
    with open(args, 'w') as w:
        w.write(fn)
    return hashlib.sha224(open(args, 'rb').read()).hexdigest() 

