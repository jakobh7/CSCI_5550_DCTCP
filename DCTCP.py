import sys
import argparse
import threading
from socket import *

class DCTCPSocket(socket):

    def __init__(self, *args, **kwargs):
        super(DCTCPSocket, self).__init__(AF_INET,SOCK_DGRAM)
        self.rcvwnd = []
        self.cwnd = []
        self.cwnd_size = 1
        self.ecn = 0
        self.connectionAddress = (0,0)

    def setHeader(self, Seq, Ack, Syn, Fin, ECN):
       return "<h>Seq={},Ack={},Syn={},Fin={},ECN={}</h>".format(Seq,Ack,Syn,Fin,ECN)

    def parseHeader(self, message):
        start = message.find('<h>')
        end = message.find('</h>')
        headerString = message[start+3:end]

        headerList = headerString.split(',')

        seqNum=0
        ackNum=0
        synFlag=0
        finFlag=0
        ECN = 0

        for header in range(len(headerList)):
            item = headerList[header].split('=')
            if item[0] == "Seq":
                seqNum = item[1]
            elif item[0] == "Ack":
                ackNum = item[1]
            elif item[0] == "Syn":
                synFlag = item[1]
            elif item[0] == "Fin":
                finFlag = item[1]
            elif item[0] == "ECN":
                ECN = item[1]

        return seqNum, ackNum, synFlag, finFlag, ECN

    def removeHeader(self, message):
        headerEnd = message.find('</h>')+4


    #def checkCwnd(self):
    #    self.getsockopt(socket.IPPROTO_TCP, socket.SO_SNDBUF)
    def threadedRecieve(self):
       message, clientAddress = self.recvfrom(2048)
       print("Message: ", message.decode(), " Address: ", clientAddress)
       self.rcvwnd.append((clientAddress,message.decode()))

    def listen(self, num):
        listener_thread = threading.Thread(target=self.threadedRecieve)
        listener_thread.daemon = True

        try:
            listener_thread.start()
            ##print("Server listening at {} on port {}".format(self.))
        except (KeyboardInterrupt,SystemExit):
            self.close()

    def check_connection_message(self, pair):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(pair[1])
        return synFlag == "1"

    def getAckNum(self, pair):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(pair[1])
        return ackNum
    def getSeqNum(self, pair):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(pair[1])
        return seqNum

    def accept(self):
        looking_for_connection = True
        while looking_for_connection:
                if(len(self.rcvwnd)>0):
                    pair = self.rcvwnd.pop()
                    print("Checking connection message for pair: ", pair)
                    if(self.check_connection_message(pair)):
                         print("Valid connection message")
                         self.connectionAddress = pair[0]
                         self.SequenceNum = 0
                         self.AcknowledgementNum = self.getSeqNum(pair)+1
                         looking_for_connection = False

        self.sendto(self.setHeader(self.SequenceNum,self.AcknowledgementNum,1,0,0).encode(),self.connectionAddress)


        return self, self.connectionAddress

    def connect(self,address):
        self.connectionAddress = address
        self.sendto(self.setHeader(0,0,1,0,0).encode(), self.connectionAddress)
        message, address = self.recvfrom()

    def send(self, message):
        print(message)
        self.sendto(message, self.connectionAddress)

    def recv(self, messageSize):
        print(messageSize)
        return self.recvfrom(messageSize)[0]
