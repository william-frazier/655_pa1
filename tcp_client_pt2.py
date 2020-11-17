# -*- coding: utf-8 -*-
"""
William Frazier
TCP Client pt 2
CS655
First Programming Assignment
"""

import socket
import sys
import time



    
    
def begin_test(sock, measurement_type, num_probes, msg_size):
    """
    This function sends the messages necessary for our test. It's a bit ugly
    but a really simple function.
    """
    
    #construct a message
    payload = b'\x41' * msg_size #message is AAAAAAAAA...
    sqn_num = 1 # the sequence number of the first message is 1
    difference = [] # will store our RTTs
    while sqn_num <= num_probes:
        msg = b'm ' + str(sqn_num).encode() + b' ' + payload + b'\n' #put the message all together
        start = time.time_ns() #start the timer
        sock.sendall(msg)
        sqn_num += 1 #increase the sequence number
        data = b''
        while data != msg:
            data += sock.recv(16)
            if data[:3] == b'404': #if we get a 404 error
                return [-1] #pass this as a flag, unambiguous because RTT can't be negative time
        end = time.time_ns() #stop the timer
        difference.append(end-start) #this array stores time elapsed
    return difference

def average(times):
    """
    Compute the average of numbers in a list.
    """    
    
    total = 0
    for i in times:
        total += i
    return total / len(times)
   
    
    

def run_experiment(measurement_type='rtt', num_probes='100', msg_size='100', server_delay='0'):
    """
    This is the main program. Initiates the conversation and makes calls to run
    experiments as is necessary.
    """
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    port_num = int(sys.argv[2])
    host_name = sys.argv[1]
    
    server_address = (host_name, port_num)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    
    try:
        message = 's ' + measurement_type + ' ' + num_probes + ' ' + msg_size + ' ' + server_delay + '\n'
        print('sending "%s"' % message[:-1])  # Drop the \n because it looks better
        sock.sendall(message.encode())
        # Look for the response, we only accept certain replies
        echo = ''
        valid_response = ["200 OK: Ready\n", "404 ERROR: Invalid Connection Setup Message\n",  "404 ERROR: Invalid Measurement Message\n",  "200 OK: Closing Connection\n",  "404 ERROR: Invalid Connection Termination Message\n"]
        while echo not in valid_response:
            data = sock.recv(16).decode()
            echo += data
            
        print('received "%s"' % echo[:-1]) # did the server accept?
        if echo.split()[0] == '404': #if not
            print("Server returned 404 on connection") 
            return     #go ahead and terminate the conversation
        differences = begin_test(sock, measurement_type, int(num_probes), int(msg_size))
        if differences[0] < 0: # this will only be the case when the server returns a 404 error
                                # see begin_test()
            print("Server returned 404 during measurement")
            return      #go ahead and terminate the conversation
        if measurement_type == 'rtt': #we are measuring two different things in our tests
            print("average delay in milliseconds is:", average(differences) / 10 ** 6) #measure in milliseconds
        else: 
            print("average throughput is:", (int(msg_size) * 8 ) / (average(differences) / 10 ** 9)) #measure in seconds
            # Note that this is bits sent divided by RTT based on what the
            # professor said after lecture 10/1
        sock.sendall(b't\n')
        echo = '' #again, we only accept certain replies
        while echo not in valid_response:
            echo += sock.recv(16).decode()
        print("received termination message '%s'" % echo[:-1])
        if echo.split()[0] == '404': #if server threw an error
            print("Server returned 404 during termination")
    
    finally:
        sock.close()
        print('closing socket', file=sys.stderr)
  

if __name__ == '__main__':
    print("Which experiment would you like to run? [rtt/tput]")
    measurement_type = input()
    print("How many probes would you like to send?")
    num_probes = input()
    if measurement_type == 'rtt':
        print("What message size would you like to use? [1/100/200/400/800/1000]")
        msg_size = input()
    elif measurement_type == 'tput':
        print("What message size would you like to use? [1024/2048/4096/8192/16384/32768]")
        msg_size = input()
    print("What would you like to set the server delay to?")
    server_delay = input()
    print() # Add an empty line for formatting
    
    run_experiment(measurement_type=measurement_type, num_probes=num_probes, msg_size=msg_size, server_delay=server_delay)
        

        
        
        
