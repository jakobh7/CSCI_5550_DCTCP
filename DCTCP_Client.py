import sys
import getopt
import argparse
import socket
from DCTCP import DCTCPSocket

serverName = 'localhost'
serverPort = 12000

##read in arguments and assigning variables
parser = argparse.ArgumentParser(description='Read in Port Number')
parser.add_argument('-N','-serverName',default='localhost',help='Name or IP of server to connect to')
parser.add_argument('-P','-serverPort',default=58000,type=int,help='Port Number of Server to connect to')

args = parser.parse_args()
serverPort = args.P
serverName = args.N

##Create socket connection to server
clientSocket = DCTCPSocket()
#clientSocket.checkCwnd()
clientSocket.connect((serverName,serverPort))

print("Connected to Socket: ", serverName, ":", serverPort)

##sending and recieving messages from the server
sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)

##display and close up
print('From Server: ', modifiedSentence.decode())
clientSocket.close()
