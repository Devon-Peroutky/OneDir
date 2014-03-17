import sys, socket

# see tiny_server.py comments. 

# exit: quits client
# shutdown: quits client and server

def main(host, port=50007):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        mes = raw_input('Say Something: ')
        s.sendall(mes)
        data = s.recv(1024)
        print 'received', repr(data)
        if mes == 'exit' or mes == 'shutdown':
            break 


if __name__ == '__main__':
    try:
        ip = sys.argv[1]
    except IndexError:
        ip = raw_input('Enter ip of connection: ')
    main(ip) 
