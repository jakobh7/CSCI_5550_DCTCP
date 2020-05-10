import sys
import argparse
import threading
import random
from socket import *

class DCTCPSocket(socket):

    def __init__(self, *args, **kwargs):
        super(DCTCPSocket, self).__init__(AF_INET,SOCK_DGRAM)
        self.rcvQueue = []
        self.queue = []
        self.cwnd = 1
        self.ssThreshold = 2
        self.ecn = 0
        self.connectionAddress = (0,0)
        self.messageSize = 1024
        self.SequenceNum = random.randint(1,100)
        self.AckNum = random.randint(1,100)
        self.DuplicateAcks = 0

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
        return message[headerEnd::]

    def splitMessage(self, message):
        headerSize = 100

        if len(message) > (self.messageSize-headerSize):
            numPackets = int(len(message)/(self.messageSize-headerSize)) + 1
            print(numPackets)

            for packet in range(numPackets):
                packetStart = (self.messageSize-headerSize)*packet
                packetEnd = (self.messageSize-headerSize)*(packet+1)
                datagram = message[packetStart:packetEnd]

                finalFlag = 0
                if packet==(numPackets-1):
                    finalFlag = 1
                ######queue is a 5 tuple (sentFlag, ackedFlag, packetSequenceNum, packetData, finalFlag)
                self.queue.append([False, False, self.SequenceNum+1, datagram, finalFlag])

                self.SequenceNum = self.SequenceNum + len(datagram)

        else:
            finalFlag = 1
            self.queue.append([False, False, self.SequenceNum+1, message, finalFlag])
            self.SequenceNum = self.SequenceNum + len(message)

        return self.queue


    def checkSent(self, sentFlag):
        return sentFlag == True

    ###This is probably unnecessary/overcomplicated
    def threadedRecieve(self):
       message, clientAddress = self.recvfrom(2048)
       print("Message: ", message.decode(), " Address: ", clientAddress)
       self.rcvQueue.append((clientAddress,message.decode()))

    def listen(self, num):
        listener_thread = threading.Thread(target=self.threadedRecieve)
        listener_thread.daemon = True

        try:
            listener_thread.start()
        except (KeyboardInterrupt,SystemExit):
            self.close()

    def check_connection_message(self, message):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(message)
        return int(synFlag) == 1
    def getAckNum(self, message):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(message)
        return int(ackNum)
    def getSeqNum(self, message):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(message)
        return int(seqNum)
    def getFinFlag(self, message):
        seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(message)
        return int(finFlag)



    def accept(self):
        looking_for_connection = True
        while looking_for_connection:
            if(len(self.rcvQueue)>0):
                pair = self.rcvQueue.pop()
                print("Checking connection message for pair: ", pair[1])
                if(self.check_connection_message(pair[1])):
                     print("Valid connection message")
                     self.connectionAddress = pair[0]
                     self.AckNum = self.getSeqNum(pair[1])+1
                     looking_for_connection = False

        self.sendto(self.setHeader(self.SequenceNum,self.AckNum,1,0,0).encode(),self.connectionAddress)

        message, address = self.recvfrom(self.messageSize)
        if self.getAckNum(message.decode()) == (self.SequenceNum + 1):
            print("Synched Ack to: ",  self.getAckNum(message.decode()))
        else:
            print("Synching issue: Acked to {}, last sequence num {}, next sequence num {}",self.getAckNum(message.decode()),self.SequenceNum,(self.SequenceNum + 1))

        return self, self.connectionAddress

    def connect(self,address):
        self.connectionAddress = address
        self.sendto(self.setHeader(self.SequenceNum,0,1,0,0).encode(), self.connectionAddress)
        message, address = self.recvfrom(self.messageSize)
        self.AckNum = self.getSeqNum(message.decode())+1
        self.sendto(self.setHeader(self.SequenceNum,self.AckNum,0,0,0).encode(), self.connectionAddress)

    def send(self, message):
        self.splitMessage(message)
        while len(self.queue) > 0:
            for i in range(min(self.cwnd, len(self.queue))):
                ###queue is a 4 tuple (sentFlag, ackedFlag, packetSequenceNum, packetData, finalFlag) for ease of use
                if not self.checkSent(self.queue[i][0]):
                    self.sendto((self.setHeader(self.queue[i][2],self.AckNum,0,self.queue[i][4],0) + self.queue[i][3].decode()).encode(), self.connectionAddress)
                    self.queue[i][0] = True

            ackMess, address = self.recvfrom(self.messageSize)
            ackNum = self.getAckNum(ackMess.decode())

            for i in range(min(self.cwnd, len(self.queue))):
                if (self.queue[i][2] + len(self.queue[i][3])) == ackNum:
                    self.queue[i][1] = True

            #check if first element in the queue has been acked
            if not self.queue[0][1]:
                print("Missed Ack for next packet. SequenceNum ",self.queue[0][2],", Recieved Ack for ", ackNum)
                self.DuplicateAcks += 1
                if self.DuplicateAcks > 3:
                    self.queue[0][0] = False
            else:
                self.queue.pop(0)


    def recv(self, messageSize):
        finalFlag = 0
        data = ""
        while (finalFlag == 0):
            message, address = self.recvfrom(self.messageSize)
            self.rcvQueue.append(message.decode())

            for mes in range(len(self.rcvQueue)):
                incomingSequenceNum = self.getSeqNum(self.rcvQueue[mes])
                if incomingSequenceNum == self.AckNum:
                    nextData = self.rcvQueue.pop(mes)
                    seqNum, ackNum, synFlag, finFlag, ECN = self.parseHeader(nextData)
                    messageData = self.removeHeader(nextData)
                    data = data + messageData
                    self.AckNum += len(messageData)
                    self.sendto(self.setHeader(self.SequenceNum,self.AckNum,0,finFlag,0).encode(), self.connectionAddress)

                    finalFlag = int(finFlag)


        return data.encode()
