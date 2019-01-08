import json
import socket
from mergesort import sort
# HOST will only be OK if we start client on the same machine, otherwise pass
# it some other way.
from server import HOST, PORT


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


# Receives arraystring in chunks
arraystring = ''
print('Receiving data...')
while 1:
    data = s.recv(4096).decode()  # Receives data in chunks
    # print data
    arraystring += data  # Adds data to array string
    if ']' in data:  # When end of data is received
        break
array = json.loads(arraystring)
print('Data received, sorting array... ')


# Sorts the array which it is allocated
array = sort(array)
print('Array sorted, sending data...')


# Converts array into string to be sent back to server
arraystring = json.dumps(array).encode('utf-8')
s.sendall(arraystring)  # Sends array string
print('Data sent.')

s.close()
