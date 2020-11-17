# -*- coding: utf-8 -*-
"""
William Frazier
TCP Server pt 2
CS655
First Programming Assignment
"""

import socket
import sys
import time


def valid_msg(data, phase, parsed, measurement_type=0, message_size = 0, current_packet_num = 0):
    """
    So this is an ugly function with too many if statements but I wanted to be
    able to print specific error messages. Returns 0 if the server should
    terminate the connection and 1 otherwise. 
    """    
    
    # This is really ugly but it gives us much more helpful error messages
    # when we break everything out like this.
    # Maybe should have been 2 functions so I'm not overloading but it seemed
    # logical to put this all in one place
    if phase == 's': # startup phase
        if parsed[0] != 's': # the first message needs to begin with 's'
            print("Setup failed, incorrect protocol phase")
            return 0
        elif parsed[1] != 'rtt' and parsed[1] != 'tput': # we only have two types of experiments we can run
           print("Setup failed, invalid measurement type")
           return 0
        elif parsed[1] == 'rtt' and parsed[3] not in ['1', '100', '200', '400', '800', '1000']: # check that message size is valid
           print("Setup failed, invalid payload size for RTT measurements")
           return 0
        elif parsed[1] == 'tput' and parsed[3] not in ['1024', '2048', '4096', '8192', '16384', '32768']: # check that message size is valid
            print("Setup failed, invalid payload size for throughput measurements")
            return 0
        elif int(parsed[2]) < 1: # the number of probes needs to be larger than 0
           print("Setup failed, invalid number of probes declared")
           return 0
        elif data.count(b" ") != 4: #ensure that our spacing is correct
           print("Setup failed, incorrect white space")
           return 0
        elif int(parsed[4]) < 0:
            print("Setup failed, server delay must be 0 or larger")
            return 0
        elif data.count(b'\n') > 1: #more than one \n in the message
            print("Setup failed, incorrect use of newlines")
            return 0
        return 1 # if all checks passed then this is a correct setup message and we return true
    elif phase == 'm': # measurement phase
       if parsed[0] != 'm': #all measurement messages need to start with 'm'
           print("Measurement failed, invalid protocol phase")
           return 0
       elif int(parsed[1]) != current_packet_num + 1: # are sequence numbers ticking up correctly?
           print("Measurement failed, invalid sequence number")
           return 0
       elif data.decode().count(" ") != 2: #ensure that our spacing is correct
           print("Measurement failed, invalid white space")
           return 0
       elif len(parsed[2]) != message_size: #ensure that the payload size that was declared
                                            #matches what was actually sent to the server
           print("Measurement failed, payload is incorrect size")
           return 0
       elif data.count(b'\n') > 1: #more than one \n in the message
           print("Measurement failed, incorrect use of newlines")
           return 0
       return 1 #if all checks pass then this was a correct measurement message



def run_server(local=False):
    """
    This is the main function. It starts up a server and begin listening for
    connections. When a client connects, it ensures that all messages are
    properly formatted or it returns a 404 error. Has a local mode that can be
    set with run_server(local=True) which results in the server running on 
    127.0.0.1:8888.
    """
    
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if local:
        port_num = 8888
        server_address = ('127.0.0.1', port_num) #for local host testing
    else:
        port_num = int(sys.argv[1])
        server_address = (socket.gethostname(), port_num) #for csa1 deployment
    print('Starting up on %s port %s' % server_address) #print out info
        
    # Bind the socket to the port
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(5) # We accept 5 connections in the queue
    
    
    
    
    
    while True: # We want this always looping so we can keep accepting connections
        # Wait for a connection
        print('Waiting for a connection')
        connection, client_address = sock.accept()
        
        
        
        
        try:
           # Intialize some variables to 0 to help us keep track of things:
           current_packet_num = 0 # Variable to keep track of our sequence numbers
           server_delay = 0     # Variable to keep track of server delay in ms
           message_size = 0     # Variable to keep track of expected payload size
           total_probes = 0     # Variable to keep track of when we expect the
                                #sequences of messages to terminate
           print('connection from', client_address) # Who just connected?
           setup = False # Variable to store if we've encountered a setup message
           while True: # Keep checking to see if the client is sending more data
               data = connection.recv(16)
               if data: # If the client is still transmitting
                   while data.decode()[-1] != '\n':
                       data += connection.recv(16)
                   
                    
                    
                   # If here, we have received a message ending with \n.
                   # Let's make the data easier to work with: bytes to string,
                   # then remove the \n, then put it into a list because 
                   # we could end up with different length messages based on 
                   # the value of e.g., the sequence number of a message
                   parsed = data.decode().strip().split() 
                   if setup: # If we have already received a setup message
                       if total_probes == current_packet_num:
                           # We're expecting a termination messaage
                           if data == b't\n': # There is only one correct format
                               connection.sendall(b"200 OK: Closing Connection\n")
                               print("Connection terminating, end of message\n")
                               break
                           # If it's in the wrong format, through a 404 and crash
                           connection.sendall(b"404 ERROR: Invalid Connection Termination Message\n")
                           print("Termination failure, invalid message")
                           break
                       try: # error check, sequence numbers need to be integers
                           int(parsed[1])
                       except:
                           connection.sendall(b"404 ERROR: Invalid Measurement Message\n")
                           print("Sequence number must be an integer")
                           break
                       # Verify that the message fits the standard
                       if valid_msg(data, 'm', parsed, message_size=message_size, current_packet_num=current_packet_num):
                           # If it does, we're here and we begin the server delay
                           time.sleep(server_delay / 1000) # Convert to milliseconds
                           connection.sendall(data)
                           # Update the sequence number we're expecting
                           current_packet_num += 1
                       else: # If the message is formatted incorrectly
                           connection.sendall(b"404 ERROR: Invalid Measurement Message\n")
                           break
                    
                          
                            
                       
                   else: # We have not yet received a setup message
                       if valid_msg(data, 's', parsed): # If correctly formatted:
                           connection.sendall(b"200 OK: Ready\n")
                           # Update these variables to the values stipulated in
                           # the setup message
                           measurement_type = parsed[1]
                           try: # just another error check
                               total_probes = int(parsed[2])
                               message_size = int(parsed[3])
                               server_delay = float(parsed[4])
                           except:
                               connection.sendall(b"404 ERROR: Invalid Connection Setup Message\n")
                               print("Number of probes and message size must be integers and server delay must be a number >= 0")
                               break
                           setup = True # The client has setup the experiment
                           print("Beginning experiment type:", measurement_type)
                           print("Expecting %d messages" % total_probes)
                           print("Expecting payload of size", message_size)
                           print("Include server delay of %d ms" % server_delay)
                       else: # If incorrectly formatted:
                           connection.sendall(b"404 ERROR: Invalid Connection Setup Message\n")
                           break
                       
                        
                        
                        
               else: # We actually don't really hit this if all goes well
                     # but the Internet tells me it's good practice to keep it
                   print('no more data from', client_address)
                   break
                
        finally: # Connection ended successfully or a 404 was thrown
            # Clean up the connection
            connection.close()
            
if __name__ == '__main__':
    # Have the server start automatically when the program is run
    run_server()

