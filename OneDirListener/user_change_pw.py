__author__ = 'rupali'
from client import *
from getpass import getpass


#use set_password from client.py
def main(ip, username, password, root_dir):
    """
    Prompts a current user through changing their password.
    """
    client = OneDirFtpClient(ip, username, password, root_dir)
    verify_pw = getpass("Please enter in your current password:")
    while not password == verify_pw:
        verify_pw = getpass("Incorrect password entry. Please enter current valid password:")
    new_pw = raw_input("Enter in your desired new password:")
    verify_new_pw = raw_input("Re-enter your desired new password:")
    while not new_pw == verify_new_pw:
        print("The new passwords you entered do not match. Please enter in the same password twice to change it.")
        new_pw = raw_input("Enter in your desired new password:")
        verify_new_pw = raw_input("Re-enter your desired new password:")
    client.set_password(password, new_pw)


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