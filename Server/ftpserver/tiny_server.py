import socket, sys

# Since pyftplib can only accept commands.  This can be used when it needs to issue them. 
# It is tiny, and can run in the background of a users machine
# Will need to be more then this, but still should be fairly small


def main(HOST='', PORT=50007):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print 'Connected by', addr
        while True: 
            data = conn.recv(1024)
            print repr(data) 
            if str(data) == 'shutdown':
                sys.exit(0)
            if not data:
                break
            else:
                conn.sendall(data)
        conn.close()


if __name__ == '__main__':
    main()  
