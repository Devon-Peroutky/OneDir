__author__ = 'rupali'
# assume you are the admin
# prompt user for username and password
# call "add_user" command from client.py to create a new user
# note to self: never delete the admin
from client import *

# def __init__(self):
#     #self.o = OneDirFtpClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
#     self.client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())

def main(self):
    """
    Prompts a new user through the creation of a non-admin account.
    """
    client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
    username = raw_input("Welcome new user! Enter in your desired username:")
    check = check_user_available(username)
    while not check:
        username = raw_input("Sorry, that username is taken. Please enter another username.")
        check = check_user_available(username)
    pw = raw_input("Username available! Please enter in a desired password:")
    pw_check = raw_input("Please re-enter your password:")
    while not pw == pw_check:
        pw = raw_input("Passwords do not match. Please enter a desired password:")
        pw_check = raw_input("Please re-enter your password:")
    self.client.user_add(username, pw, False)

def check_user_available(self, username):
    """
    Helper method to check that a desired username is not already taken.
    """
    users = self.client.get_user_list
    if username not in users:
        return True
    else:
        return False

if __name__ == "__main__":
    main()