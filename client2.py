import socket
import time

HOST = input("Enter host name: ")
PORT = int(input("Enter port number: "))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #sentence = input("Enter you input: ")
    #connection phase
    probes = input("Enter number of probes: ") #asking for # of probes
    mselection = 2 #setting mode-selection incorrectly for later while loop
    size = 2 #setting size incorrectly for later while loop
    delay = -1 #setting delay to incorrect value for later while loop
    buffsize = 32768 #setting maximum buffer size just because 
    while mselection != 0 and mselection != 1: #will loop until one of the two
        mselection = int(input("rtt - 0, tput - 1: ")) #asking for rtt or tput
        
    while size != 1 and size != 200 and size != 400 and size != 800 and size != 1000 and size != 2000 and size != 4000 and size != 8000 and size != 16000 and size != 32000: #will loop until a valid entry
        if mselection == 0: #possible sizes for rtt
            measurement = "rtt"
            while size != 1 and size != 200 and size != 400 and size != 800 and size != 1000: #will loop until valid
                size = int(input("Enter a size of 1, 200, 400, 800, or 1000: "))

        elif mselection == 1: #possible sizes for tput
            measurement = "tput"
            while size != 1000 and size != 2000 and size != 4000 and size != 8000 and size != 16000 and size != 32000: #will loop until valid
                size = int(input("Enter a size of 1000, 2000, 4000, 8000, 16000, or 32000 bytes: "))

        else:
            print("not valid")
            
    while delay == -1: #loop until valid
        delay = float(input("Enter the delay: ")) #enter a valid delay, which can be a float
        
    fsentence = "s " + measurement + " " + str(size) + " " + str(probes) + " " + str(delay) + " 0\n" #making CSP message
    s.sendall(fsentence.encode()) #sent
    data = s.recv(buffsize) #receive
    print('Received: ', data.decode()) 
    if data.decode() != "200 OK: Ready": #if correct response from server then proceed
        print("404 ERROR: Invalid Connection Setup Message") #else exit
        s.close()
        exit()

    #measurement phase
    res = [] #results
    x = range(0, int(probes)) #list for probes
    for probe in x: #looping for probes
        payload = ['.'] * size #arbitrary character of SIZE
        payload = ''.join(payload) #now its a string
        
        fsentence2 = "m " + str(payload) + " " + str(int(probe)) +"\n" #making MP message
        t1 = time.perf_counter() #time 1
        s.sendall(fsentence2.encode()) #send encoded message
        data = s.recv(buffsize).decode() #receive decoded message 
        t2 = time.perf_counter() #time 2
        rtt = t2 - t1 #round trip time
 
        if mselection == 0: #add rtt to results
            res.append(rtt)
            #print("rtt: ", rtt)

        elif mselection == 1: #add tput to results
            tput = size/rtt
            res.append(tput)
            #print("tput: ", tput)
        
    #connection termination phase

    termin = "t" + "\n" #making CTP message
    s.sendall(termin.encode()) #sending it
    data = s.recv(buffsize).decode() #receive correct response from server?
    if data != "200 OK: Closing Connection": #nop
        print("Error 404: Invalid Connection Termination Message")
    elif data == "200 OK: Closing Connection": #yep
        print("Understood, closing as well") #want to see this so I don't have anxiety
        print(res) #print result
        s.close() #close and exit
        exit()
    else: #hope this isn't ever used
        print("oop")
    s.close() #just close and exit anyway
    exit()

