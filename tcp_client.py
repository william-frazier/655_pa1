# -*- coding: utf-8 -*-
"""
William Frazier
TCP Client
CS655
First Programming Assignment
"""

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening


port_num = int(sys.argv[2])
host_name = sys.argv[1]

server_address = (host_name, port_num)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    while True:
        # Send data
        print('sending: ', end='')
        message = input()
        if message == 'quit': #type quit to end the connection
            break
        sock.sendall(bytes(message.encode()))
    
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        echo = ''
        while amount_received < amount_expected: #ensure everyhting was echoed
            data = sock.recv(16).decode()
            amount_received += len(data)
            echo += data
        print('received "%s"' % echo)

finally:
    print('closing socket')
    sock.close()
