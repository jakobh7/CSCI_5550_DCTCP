import sys
import argparse
import threading
from socket import *

class DCTCPSocket(socket):

    def __init__(self, *args, **kwargs):
        super(DCTCPSocket, self).__init__(AF_INET,SOCK_DGRAM)
        self.cwnd = []
        self.ecn = 0
        self.connectionAddress = (0,0)

    #def checkCwnd(self):
    #    self.getsockopt(socket.IPPROTO_TCP, socket.SO_SNDBUF)
    def threadedRecieve(self):
       message, clientAddress = self.recvfrom(2048)
       print("Message: ", message, " Address: ", clientAddress)
       self.cwnd.append((clientAddress,message))

    def listen(self, num):
        listener_thread = threading.Thread(target=self.threadedRecieve)
        listener_thread.daemon = True

        try:
            listener_thread.start()
            ##print("Server listening at {} on port {}".format(self.))
        except (KeyboardInterrupt,SystemExit):
            self.close()

    def accept(self):
        looking_for_connection = True
        while looking_for_connection:
            for i in range(len(self.cwnd)):
                print(self.cwnd[i])
                if(check_connection_message(self.cwnd[i])):
                    self.connectionAddress = self.cwnd[i][0]
                    self.SequenceNum = 0
                    self.AcknowledgementNum = getAckNum(self.cwnd[i])
                    looking_for_connection = False
