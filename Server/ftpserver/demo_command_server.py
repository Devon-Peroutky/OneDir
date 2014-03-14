from ftplib import FTP

"""
This demos: command_server.py

Like the last server, I have only tested between an Arch Linux Client and Ubuntu Server
"""


cb = []


def callback(line):
    global cb
    cb += [line]


def main(ip):
    ftp = FTP()
    ftp.connect(ip, 21)
    ftp.login('admin', 'admin')
    print
    print "Running Command 'Justin': (200 is the responce code meaning everything is good)"
    print "\tOutput: %s" % ftp.sendcmd('justin')
    print
    print "Running Command 'Uptime': (a bash command that tells how long the computer [the server] has been on"
    ftp.retrlines('uptime', callback)
    print "\tOutput: %s" % cb[0]


if __name__ == '__main__':
    ip = raw_input('Input server ip addy (I am not going to check): ') 
    main(ip)    
