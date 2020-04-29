import sys
import argparse
import socket

class DCTCPSocket(socket.socket):

    def __init__(self, *args, **kwargs):
        super(DCTCPSocket, self).__init__(*args, **kwargs)
        self.cwnd = []
        self.ecn = 0

    def checkCwnd(self):
        self.getsockopt(socket.IPPROTO_TCP, socket.SO_RCVBUF)
