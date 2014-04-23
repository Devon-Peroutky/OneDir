__author__ = 'rupali'
from client import *
from getpass import getpass

#use set_password from client.py
def main(self, ip, username, password, root_dir):
    """
    Prompts a current user through changing their password
    """
    #client = OneDirFtpClient(socket.gethostbyname(ip, username, password, root_dir))
    #username = raw_input("Please enter in your username:") #can be removed if there's a get_current_user() method somewhere I didn't see
    #check = check_user(username)
    #while not check:
    #    username = raw_input("Entered username not valid. Please enter a valid username:")
    #current_pw = "dummy" #need to access database to get user's current pw
    verify_pw = getpass("Please enter in your current password:")
    #while not current_pw == verify_pw:
    #    verify_pw = getpass("Incorrect password entry. Please enter current valid password:")
    new_pw = raw_input("Enter in your desired new password:")
    verify_new_pw = raw_input("Re-enter your desired new password:")
    while not new_pw == verify_new_pw:
        print("The new passwords you entered do not match. Please enter in the same password twice to change it.")
        new_pw = raw_input("Enter in your desired new password:")
        verify_new_pw = raw_input("Re-enter your desired new password:")
    client.change_user_password(username, new_pw)


def check_user(self, username):
    """
    Helper method to check that the entered username is a valid username.
    """
    users = self.client.get_user_list
    if username in users:
        return True
    else:
        return False

if __name__ == "__main__":
    main()