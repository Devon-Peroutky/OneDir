__author__ = 'rupali'
# assume you are the admin
# prompt user for username and password
# call "add_user" command from client.py to create a new user
# note to self: never delete the admin
from client import *
from getpass import getpass


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
    client.change_user_password(username, pw)


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