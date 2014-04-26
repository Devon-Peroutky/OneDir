__author__ = 'rupali'
# assume you are the admin
# prompt user for username and password
# call "add_user" command from client.py to create a new user
# note to self: never delete the admin
from client import *
from getpass import getpass
import json
from uuid import getnode as get_mac

def main(ip, port, username=None, password=None): #connect with client.py after Justin pushes; use OneDirAdminClient to create new user with temp pw, then proceed to change pw
    #OneDirNoAuthClient - coming soon! (requires IP and port number); request username. If accepted, temp pw will be issued. If username is not accepted, error thrown.
    """
    Prompts a new user through the creation of a non-admin account.
    """
    #client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
    client = OneDirNoAuthClient(ip, port)
    nickname = get_mac()
    if not username: #paramaters not passed in
        username = raw_input("Welcome new user! Enter in your desired username: ")
        temppw = None
        while password is None:
            try:
                temppw = client.user_sign_up(username)
                #print "Username is available! Here is your temporary password:", password
            except KeyError:
                username = raw_input("Sorry, that username is taken. Please enter another username: ")
        password = getpass("Username available! Please enter in a desired password:")
        pw_check = getpass("Please re-enter your password:")
        while not password == pw_check:
            password = getpass("Passwords do not match. Please enter a desired password:")
            pw_check = getpass("Please re-enter your password:")
        root_dir = raw_input("Please type in the file path for the directory where you would like to watch for changes:")
        while not os.path.exists(root_dir):
            root_dir = raw_input("Invalid file path entered. Enter a valid path to a directory where you would like to watch for changes:")
        #json needs: username, root_dir, nick, is_syncing: True, password
        # nickname = get_mac()
        data = {"username": username, "root_dir": root_dir, "nick": nickname, "is_syncing": True, "password": pw}
        path = os.path.expanduser('~') + '/.onedirlistener/client.json'
        with open(path, 'w') as filename:
            json.dump(data, filename)
        ftpclient = OneDirFtpClient(ip, port, username, nickname, password, root_dir)
        ftpclient.set_password(password, temppw)
    else: #parameters passed in
        temppw = None
        try:
            temppw = client.user_sign_up(username)
            root_dir = os.path.expanduser('~') + '/OneDirServer'
            print 'The default root directory is: %s/OneDirServer' % os.path.expanduser('~')
            ret = False
            while True:
                yes = ['y', 'ye', 'yes']
                no = ['n', 'no']
                rep = raw_input('Would you like to use this: [Y/n]')
                rep = rep.lower()
                rep = rep.strip(' ')
                if rep in yes + no + ['']:
                    ret = rep in yes + ['']
                    break
                else:
                    prompt = 'Input not understood: please enter yes or no.'
                    print prompt
            if not ret:
                for i in range(3):
                    root_dir = raw_input('Please enter path to where you want the server file to go: ')
                    if os.path.isdir(root_dir):
                        try:
                            os.rmdir(root_dir)
                            os.mkdir(root_dir)
                            return root_dir
                        except OSError:
                            print 'Sorry, not an empty directory. Try again.'
                    else:
                        try:
                            os.mkdir(root_dir)
                            return root_dir
                        except OSError:
                            print 'Sorry, path not valid. Try again.'
                    if i == 2:
                        print 'Too many tries. Aborting.'
                        sys.exit(1)
            data = {"username": username, "root_dir": root_dir, "nick": nickname, "is_syncing": True, "password": password}
            path = os.path.expanduser('~') + '/.onedirlistener/client.json'
            with open(path, 'w') as filename:
                json.dump(data, filename)
            ftpclient = OneDirFtpClient(ip, port, username, nickname, password, root_dir)
            ftpclient.set_password(password, temppw)
        except KeyError:
            print "Sorry, the entered username is taken."

# def check_user_available(self, username):
#     """
#     Helper method to check that a desired username is not already taken.
#     """
#     users = self.client.get_user_list
#     if username not in users:
#         return True
#     else:
#         return False

if __name__ == "__main__":
    main()