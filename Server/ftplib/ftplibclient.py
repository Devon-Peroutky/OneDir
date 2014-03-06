__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/06/14'

from ftplib import FTP


"""

Client demo, lacking in a lot of ways but enough
to show that it can do the trick

I was feeling lazy... so i did not write any test cases... i just wrote a main... that you have to 
look at the code to know what is going on.

Also, Sorry about any formatting... I was working on multiple computers at onces... so i switched from 
working in pycharm to working in vim... so i could just work at one computer and ssh into anything that I
needed too. 

"""

class ClientDemo:
    def __init__(self, host, port, username='user', password='12345'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = FTP()

    def connect(self):
        """
        Just connects to the server
        This will have trys and catches and what nots
        """
        self.ftp.connect(self.host, self.port)
        self.ftp.login(self.username, self.password)

    def print_stuff(self):
        """
        Just a breakdown of what we got
        """
        print 'Welcome message', self.ftp.getwelcome()
        print 'Print working Directory', self.ftp.pwd()
        print 'Print Dir', self.ftp.dir()

    def make_dir(self):
        """
        Makes a dir named test
        """
        self.ftp.mkd('test')

    def go_back_a_dir(self):
        """
        Drops back a directory
        """
        self.ftp.cwd('..')

    def go_to_dir(self, path):
        """
        Goes to a directory
        """
        self.ftp.cwd(path)

    def remove_dir(self, path):
        """
        Deletes a directory
        """
        self.ftp.rmd(path)

    def download_file(self):
        """
        Downloads a file and saves it as downloaded_file
        """
        file_name = open('downloaded_file', 'wb')
        self.ftp.retrlines('RETR transfer_file', file_name.write)
        file_name.close()

    def upload_file(self):
        """
        Creates a file named upload_file andUploads it to the server
        """
        text = "This is the text in the file that will will be uploaded onto the sever"
        with open('upload_file', 'w') as w:
            w.write(text)
        self.ftp.storlines("STOR uploaded_file.txt", open('upload_file', 'rb'))

if __name__ == '__main__':
    print 'Make sure you have your sever on! :)'
    addy = raw_input('Input address: ' )
    port = raw_input('Input port... I have the server configured to run on 21: ')
    c = ClientDemo(addy, port)
    c.connect()
    print 'Print stuff'
    c.print_stuff()
    print
    c.make_dir()
    print 'Print Working dir'
    print c.ftp.pwd()
    c.go_back_a_dir()
    print '\n Print working dir'
    print c.ftp.pwd()
    c.go_to_dir('test')
    print '\n Print working dir'
    print c.ftp.pwd()
    c.go_back_a_dir()
    print '\n Print files'
    c.ftp.dir()
    c.remove_dir('test')
    print '\n print files'
    c.ftp.dir()
    c.download_file()
    c.upload_file()
    print '\n print files'
    c.ftp.dir()


