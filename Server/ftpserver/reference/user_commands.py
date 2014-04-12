import hashlib

# everything must have underscore right now


def args_strip(args):
    """
    This command is not injected into the handler. 
    It is used as a quick way to separate the file path from the argument
    @return: The argument without the file path
    """
    return str(args).split('/')[-1]


def get_path(args):
    """
    This command is not injected into the handler. 
    It is also used to separate the file path from the argument.
    @return: The path without the argument
    """
    path = str(args).split('/')[:-1]
    return '/'.join(path)


def void_need(user, cwd, database, table, args):
    """
    This is a demo of what is returned by the arguments. 
    """
    a = args_strip(args)
    b = get_path(args)
    return "%s %s %s %s %s %s %s" % (user, cwd, database, table, args, a, b)


def string_checksum(args):
    """
    This was fixed! Now it is only one line. 
    """
    return hashlib.sha224(open(args, 'rb').read()).hexdigest() 
