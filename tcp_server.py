# -*- coding: utf-8 -*-
"""
William Frazier
TCP Server
CS655
First Programming Assignment
"""

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port

port_num = int(sys.argv[1])


hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)  


server_address = (IPAddr, port_num)

print('Starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(5)

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = sock.accept()
    try:
       print('Connection from:', client_address)

       # Receive the data in small chunks and retransmit it
       while True:
           data = connection.recv(16)
           print('Received "%s"' % data.decode())
           if data:
               print('Sending data back to the client...')
               connection.sendall(data)
           else:
               print('No more data from', client_address)
               break
            
    finally:
        # Clean up the connection
        connection.close()

