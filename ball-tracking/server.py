#!/usr/bin/env python
import socket
from threading import Thread
from socketserver import ThreadingMixIn

TCP_IP = 'localhost'
# TCP_IP = socket.gethostbyaddr("your-ec2-public_ip")[0]
TCP_PORT = 60001
BUFFER_SIZE = 1024

print('TCP_IP=%s' % TCP_IP)
print('TCP_PORT=%s' % TCP_PORT)

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        # print("\t* New thread started for "+ip+":"+str(port))

    def run(self):
        f = open('braccetto_copy.jpg','wb')
        while True:
            data = self.sock.recv(BUFFER_SIZE)
            if not data:
                f.close()
                self.sock.close()
                print("\t * Received file!")
                break
            f.write(data)

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []

while True:
    tcpsock.listen(5)
    # print("Waiting for incoming connections...")
    (conn, (ip,port)) = tcpsock.accept()
    print(" + Incoming connection from %s:%s" % (ip,port))
    newthread = ClientThread(ip,port,conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
