import socket
import time
HOST = '127.0.0.1'
PORT = int(input("Enter the port number: "))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)) #binding
    s.listen() 
    while True: 
        conn, addr = s.accept() #connecting
        print('Connected by', addr)
        probe = 0 #connected
        buffsize = 32768 #using max buffsize so that I don't have to think about an index error or intelligent solution
        while True:
            
            rmess = conn.recv(buffsize).decode() #recieving a message from client
            rmes = rmess.split(" ") #splitting the message by the WS

            if rmes[0] == "s": #checking for connection phase
                if (rmes[1] == "rtt" or rmes[1] == "tput"): #error checking
                    smes = "200 OK: Ready" #setting send-message for no error
                    probemax = int(rmes[3]) -1 #setting max probe size variable
                    delay = float(rmes[4]) #setting delay variable 
                else:
                    smes = "404 Error: Invalid Connection Setup Message" #setting send-message for error found
            elif rmes[0] == "m" and rmes[2] != probemax: #checking for measurement phase
                smes = "200 OK: Ready" #setting send-message for no error 
                rmes[2].replace('\n', '') #removing endline character from number so it can be read properly as an int
                if rmes[2] == probemax: #seems redudant to have an if and else that do the same thing but I don't want to think about this anymore so...
                    smes = rmes[1] #setting send-message as sequence number to send back to client
                elif (len(rmes) != 3 or int(rmes[2]) != probe) and int(rmes[2]) > probemax: #catching errors: message wrong size, incorrect sequence probe number, and sequence probe number somehow larger than maximum possible probe number
                    smes = "404 Error: Invalid Measurement Method" #ruh roh, an error
                else:
                    smes = rmes[1] #setting send-message as sequence number to send back to client
                probe = probe + 1 #iterate probe size for error checking

                time.sleep(delay) #implementing delay variable
            elif rmes[0] == "t\n": #checking for termination phase
                smes = "200 OK: Ready" #setting send-message for no error
                if len(rmes) != 1:
                    smes = "404 Error: Invalid Connection Termination Message" #setting send-message for error
                else:
                    smes = "200 OK: Closing Connection" #setting send-message for no error
            else: #not a phase but an error
                smes = "404 Error: Invalid Message Protocol Selection" #setting send-message for error
                conn.close() #close connection and exit
                exit()

            conn.sendall(smes.encode()) #send the send-message variable
