#!/usr/bin/python
import smtplib

class Emailer(object):
    def __init__(self, emailAddress, username):
        self.server = 'smtp.gmail.com'
        self.port = 587
 
        self.sender = 'onedir.16@gmail.com'
        self.password = 'onedir16'
        self.recipient = emailAddress
        self.subject = 'Gmail SMTP Test'
        self.body = "Hello! You have just registered for a OneDir account with the username: " + str(username) + ". If this is not you, then respond to this email, describe the problem, and we will handle the rest!" 
 
    def sendEmail(self):
        self.body = "" + self.body + ""
        self.headers = ["From: " + self.sender,
                   "Subject: " + self.subject,
                   "To: " + self.recipient,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        self.headers = "\r\n".join(self.headers)

        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(self.sender, self.password)
 
        session.sendmail(self.sender, self.recipient, self.headers+"\r\n\r\n"+self.body)
        session.quit()

def main():
    e = Emailer('devonperoutky@gmail.com')
    e.sendEmail()

if __name__ == '__main__':
    main()
