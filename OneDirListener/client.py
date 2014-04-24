import os
from ftplib import *
from OneDirListener.callbacks import CallBack


__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/29/14'


class OneDirNoAuthClient(object):
    def __init__(self, host, port):
        self.ftp = FTP()
        self.ftp.connect(host, port)
    
    def user_sign_up(self, username):
        """
        Signs up an new users. 
        @return:  The password if the sign up was successful.
        @raises KeyError: If the username is taken.
        """
        rep = self.ftp.sendcmd('site signup %s' % username)
        rep = rep.split(' ')
        if rep[1] == 'False':
            raise KeyError('Username taken')
        else:
            return rep[1]

    def disconnect(self):
        self.ftp.close() 


class OneDirFtpClient(FTP):
    """
    Adds commands, to FTP, and modifies them so that file/folder names/paths are in
    the form that they exist on the server.
    """
    
    def __init__(self, host, port, user, nick, password, root_dir):
        """
        Right now, I do not know if the the listener splits the path from the file
        @param host: The host ip address
        @param user: The username
        @param password:  The user's password
        @param root_dir: The local directory of the OneDir files
        """
        FTP.__init__(self)
        self.connect(host, port)
        self.login(user, password)
        self.i_am(nick)
        self.root_dir = root_dir
        self.__file_names = []
        self.__folder_names = []
        self.__list_holder = []

    def cd(self, dir_name):
        """
        Changes the directory.
        @param dir_name: The directory to change into
        """
        server_dir = os.path.relpath(dir_name, self.root_dir)
        return self.cwd(server_dir)

    def list_dir(self, dir_name=None):
        """
        Creates a list of files and folder contained in a directory
        @param dir_name:
            The name of the directory to create list from,
            Default=None,
            None will print the current directory
        """
        if not dir_name:
            return self.nlst()
        else:
            server_dir = os.path.relpath(dir_name, self.root_dir)
            return self.nlst(server_dir)

    def mkdir(self, dir_name):
        """
        Creates a folder on the server.
        @param dir_name:
            This may include a path.
            The name of the directory to create
            WARNING: Without a path, this assumes it is already in the correct directory.
        """
        if not len(dir_name.split('/')) == 1:
            dir_name = os.path.relpath(dir_name, self.root_dir)
        return self.mkd(dir_name)

    def upload(self, filename):
        """
        Uploads a file onto the server.
        @param filename: The filename with the path to the file.
        """
        tmp = os.path.split(filename)
        server_path = os.path.relpath(tmp[0], self.root_dir)
        server_file = tmp[1]
        cwd = self.pwd()
        self.cwd(server_path)
        to_return = self.storbinary('STOR %s' % server_file, open(filename, 'rb'))
        lr = self.lastresp
        self.cwd(cwd)
        self.lastresp = lr
        return to_return

    def download(self, filename):
        """
        Downloads the file into this directory
        @param filename: The full path to the file that needs to be changed.
        """
        server_file = os.path.relpath(filename, self.root_dir)
        with open(filename, 'wb') as w:
            return self.retrbinary('retr %s' % server_file, lambda x: w.write(x))

    def move(self, from_move, to_move):
        """
        Move or Rename a file or folder.
        @param from_move: The starting location of the file or folder.
        @param to_move: The ending location of the file or folder.
        """
        from_server = os.path.relpath(from_move, self.root_dir)
        to_server = os.path.relpath(to_move, self.root_dir)
        return self.rename(from_server, to_server)

    def move_from(self, path):
        server_path = os.path.relpath(path, self.root_dir)
        return self.sendcmd('RNFR %s' % server_path)

    def move_to(self, path):
        server_path = os.path.relpath(path, self.root_dir)
        return self.sendcmd('RNTO %s' % server_path)

    def delete_file(self, filename):
        """
        Deletes a file.
        @param filename: The full path of where the file existed before it was deleted
        """
        on_server = os.path.relpath(filename, self.root_dir)
        return self.delete(on_server)

    def delete_folder(self, folder_name):
        """
        Deletes a folder from the server.
        @param folder_name: The path and folder name to delete
        """
        on_server = os.path.relpath(folder_name, self.root_dir)
        x = self.__delete_folder(on_server)
        self.cwd('/')
        return x

    def gettime(self):
        time = self.sendcmd('site gettime')
        time = time.split(' ')[-1]
        return time

    def sync(self, timestamp):
        """
        NOTE: You should call get time right after using this. 
        @param timestamp: The last time that the server and the client sync'd
        @return: a list of tuples of commands sent the the server
        """
        helper = CallBack()
        self.retrlines('site sync %s' % timestamp, helper.general_list)
        for i in range(len(helper.store_list)):
            helper.store_list[i] = eval(helper.store_list[i])
        return helper.store_list

    def deactivate_account(self):
        """
        Deactivates the account on the server.
        """
        self.sendcmd('site deactiv')

    def set_password(self, new_pw, old_pw):
        """
        Changes the users password. Won't deactivate session.
        No need to log out and back in.  
        @param new_pw: plain text new password.
        @param old_pw: plain text old password. 
        """
        self.sendcmd('site setpw %s %s' % (new_pw, old_pw))

    def set_sync_flag(self, arg, arg_two=None):  # Untested
        """ 
        Sets a flag in the information returned by the sync method 
        """
        if arg_two:
            self.sendcmd('site setflag %s %s' % (arg, arg_two))
        else:
            self.sendcmd('site setflag %s' % arg)

    def who_am_i(self):  # Untested
        """
        @returns: username:nick_name
        """
        rep = self.sendcmd('site whoami')
        rep = rep.split(' ')
        return rep[1]
    
    def i_am(self, nick_name):  # Untested
        """
        Sets the nickname of a user and the server. 
        This probably will be required later. 
        """
        self.sendcmd('site iam %s' % nick_name)
    
    def __delete_folder(self, server_path):
        """ 
        Recursive folder deleter, do not call.
        """
        self.cwd(server_path)
        server_path = server_path.split('/')[-1]
        helper = CallBack()
        self.dir(helper.file_folder_separator)
        for f in helper.folders:
            self.__delete_folder(f)
        for f in helper.files:
            self.delete(f)
        self.cwd('..')
        x = self.rmd(server_path)
        return x

    def report(self, folder=None):
        if folder:
            self.cwd(folder)
        helper = CallBack()
        self.dir(helper.general_list)
        self.cwd('/')
        return helper.store_list


class OneDirAdminClient(OneDirFtpClient):
    def user_add(self, username, password, is_admin=False):
        """
        Adds a user the servers database. 
        @param username: The username of the person you want to add.
        @param password: A plain text password.
        @param is_admin: True if user needs admin privileges
        """
        command = "site useradd %s %s %s"
        if is_admin:
            command = command % (username, password, '1')
        else:
            command = command % (username, password, '0')
        self.sendcmd(command)
    
    def user_del(self, username):
        """
        Completely deletes a user from the server.
        @param username: The username to delete.
        """
        self.sendcmd('site userdel' % username)

    def get_log(self):
        """
        Download the server log file into the current directory.
        """
        log_loc = self.sendcmd('site getlog')
        log_loc = log_loc.split(' ')[1]
        filename = 'server.log'
        with open(filename, 'wb') as w:
            return self.retrbinary('retr %s' % log_loc, lambda x: w.write(x))

    def get_user_list(self):
        """
        @return: A list of user on the server.
        """
        helper = CallBack()
        self.retrlines('site userlist', helper.general_list)
        for i in range(len(helper.store_list)):
            helper.store_list[i] = eval(helper.store_list[i])
        return helper.store_list

    def change_user_password(self, username, password):
        """
        Changes a users password
        @param username: the user who needs password change
        @param password: the password to change it too.
        """
        self.sendcmd('site changepw %s %s' % (username, password))
