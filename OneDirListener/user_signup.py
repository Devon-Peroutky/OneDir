__author__ = 'rupali'
# assume you are the admin
# prompt user for username and password
# call "add_user" command from client.py to create a new user
# note to self: never delete the admin
from client import *
from getpass import getpass
import json
from uuid import getnode as get_mac

def main(ip, port): #connect with client.py after Justin pushes; use OneDirAdminClient to create new user with temp pw, then proceed to change pw
    #OneDirNoAuthClient - coming soon! (requires IP and port number); request username. If accepted, temp pw will be issued. If username is not accepted, error thrown.
    """
    Prompts a new user through the creation of a non-admin account.
    """
    #client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
    client = OneDirNoAuthClient(ip, port)
    username = raw_input("Welcome new user! Enter in your desired username:")
    password = None
    while password is None:
        try:
            password = client.user_sign_up(username)
            #print "Username is available! Here is your temporary password:", password
        except KeyError:
            username = raw_input("Sorry, that username is taken. Please enter another username.")
    pw = getpass("Username available! Please enter in a desired password:")
    pw_check = getpass("Please re-enter your password:")
    while not pw == pw_check:
        pw = getpass("Passwords do not match. Please enter a desired password:")
        pw_check = getpass("Please re-enter your password:")
    root_dir = raw_input("Please type in the file path for the directory where you would like to watch for changes:")
    while not os.path.exists(root_dir):
        root_dir = raw_input("Invalid file path entered. Enter a valid path to a directory where you would like to watch for changes:")
    #json needs: username, root_dir, nick, is_syncing: True, password
    nickname = get_mac()
    data = {"username": username, "root_dir": root_dir, "nick": nickname, "is_syncing": True, "password": pw}
    path = os.path.expanduser('~') + '/.onedirlistener/client.json'
    with open(path, 'w') as file:
        json.dump(data, file)
    ftpclient = OneDirFtpClient(ip, port, username, nickname, password, root_dir)
    ftpclient.set_password(pw, password)

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