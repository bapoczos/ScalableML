import json
import socket
import random
import time
from mergesort import sort, merge


ARRAY_LENGTH = 1000000
# Get host IP. It does not always work so one should be careful with this.
HOST = socket.gethostbyname(socket.gethostname())
PORT = 50007


if __name__ == '__main__':
    sequence = list(range(ARRAY_LENGTH))
    random.shuffle(sequence)

    n = 4

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    s.listen(n)
    print('Waiting for clients...')

    workers = []
    for i in range(n):
        conn, addr = s.accept()
        workers.append((conn, addr))

    t0 = time.time()

    l = len(sequence) // n
    subseqs = [sequence[i * l:(i + 1) * l] for i in range(n - 1)]
    subseqs.append(sequence[(n - 1) * l:])

    for i, (conn, addr) in enumerate(workers):
        conn.sendto(json.dumps(subseqs[i]).encode('utf-8'), addr)

    partials = []
    for i, (conn, addr) in enumerate(workers):
        arraystring = ''
        while True:
            data = conn.recv(4096).decode()  # Receives data in chunks
            arraystring += data  # Adds data to array string
            if ']' in data:  # When end of data is received
                break
        partials.append(json.loads(arraystring))
    conn.close()

    result = partials[0]
    for partial in partials[1:]:
        result = merge(result, partial)

    dt = time.time() - t0
    print('Socket-based mergesort took %.02fs' % (dt))

    # Do the same thing locally and compare the times.
    t0 = time.time()
    truth = sort(sequence)
    dt = time.time() - t0
    print('Local mergesort took %.02fs' % (dt))

    # Final sanity checks.
    assert result == truth
    assert result == sorted(sequence)
