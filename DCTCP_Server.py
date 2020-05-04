import sys
import argparse
import socket
from DCTCP import DCTCPSocket

serverPort = 12000

##read in arguments and assigning variables
parser = argparse.ArgumentParser(description='Read in Port Number')
parser.add_argument('-P','-serverPort',default=58000,type=int,help='Port Number for server to Serve on')

args = parser.parse_args()
serverPort = args.P


##setup the socket as a TCP Stream
serverSocket = DCTCPSocket()
##bind the port to the server name
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)

##loop to listen for messages
print("Serving on port ", serverPort)
while True:
    connectionSocket, addr = serverSocket.accept()

    sentence = connectionSocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()

    print("Sending message: ", capitalizedSentence)
    connectionSocket.send(capitalizedSentence.encode())

    connectionSocket.close()
