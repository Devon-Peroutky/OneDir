import os
from ftplib import *
from copy import deepcopy


__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/29/14'


class OneDirFtpClient(FTP):
    """
    Adds commands, to FTP, and modifies them so that file/folder names/paths are in
    the form that they exist on the server.
    """

    def __init__(self, host, user, password, root_dir, timeout=None):
        """
        Right now, I do not know if the the listener splits the path from the file
        @param host: The host ip address
        @param user: The username
        @param password:  The user's password
        @param root_dir: The local directory of the OneDir files
        @param timeout:  The amount of time till the connection cuts itself off. Default=None
        """
        FTP.__init__(self, host, user, password, '', timeout)
        self.root_dir = root_dir
        self.__file_names = []
        self.__folder_names = []

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
        return self.__delete_folder(on_server)

    def __delete_folder(self, server_path):
        """ 
        Recursive folder deleter, do not call.
        """
        self.cwd(server_path)
        self.dir(self.__file_folder_callback)
        files = self.__save_file_names()
        folders = self.__save_folder_names()
        for f in folders:
            self.__delete_folder(f)
        for f in files:
            self.delete(f)
        self.cwd('..')
        return self.rmd(server_path)

    def __file_folder_callback(self, line):
        """
        A callback for separating files from folders, do not call.
        """
        if not len(line) == 0:
            if not line[0] == 'd':
                self.__file_names += [line.split(' ')[-1]]
            else:
                self.__folder_names += [line.split(' ')[-1]]

    def __save_file_names(self):
        """
        To be used after file_folder_callback, do not call.
        """
        file_names = deepcopy(self.__file_names)
        self.__file_names = []
        return file_names

    def __save_folder_names(self):
        """
        To be used after file_folder_callback, do not call.
        """
        folder_name = deepcopy(self.__folder_names)
        self.__file_names = []
        return folder_name