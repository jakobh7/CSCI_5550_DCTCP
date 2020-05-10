from DCTCP import DCTCPSocket

testSock = DCTCPSocket()

header = testSock.setHeader(5,10,1,0,0)

print(header)

message = header+"<m>Hello World</m>"

returnedHeader = testSock.parseHeader(message)
returnedMessage = testSock.removeHeader(message)

print("Header: ",returnedHeader)
print("Message: ", returnedMessage)


file = open("template.tex", "r")
fileString = file.read()
fileSeparation = testSock.splitMessage(fileString)
print("cwnd size: ", len(fileSeparation))
print("First Element: ", fileSeparation[0])
print("First Message Length: ", len(fileSeparation[0][3]))
print("Secont Element: ", fileSeparation[1])
print("Last Element: ", fileSeparation[-1])
print("Last Message Length: ", len(fileSeparation[-1][3]))
