#!/usr/bin/env python3.5
import random
import time
import gevent
from mergesort import sort, merge


def purge(xs, fromys):
    return [y for y in fromys if y not in xs]


def merger(partials):
    merged = []
    failed = []
    terminated = []
    while partials or terminated:
        terminated += [p for p in partials if p.ready()]
        partials = purge(terminated, partials)

        failed += [p for p in partials if p.failed()]
        if failed:
            raise Exception('%d tasks failed' % (len(failed)))
        partials = purge(failed, partials)

        if len(terminated) >= 1:
            sublist = terminated.pop(0).result
            if not merged:
                merged = sublist
            else:
                merged = merge(merged, sublist)
        gevent.sleep(0)
    return merged


# Create a list of 1,000,000 elements in random order.
N = 1000000
sequence = list(range(N))
random.shuffle(sequence)

t0 = time.time()

# Split the sequence in a number of chunks and process those
# independently.
n = 4
l = len(sequence) // n
subseqs = [sequence[i * l:(i + 1) * l] for i in range(n - 1)]
subseqs.append(sequence[(n - 1) * l:])

# Ask the Celery workers to sort each sub-sequence.
# Use a group to run the individual independent tasks as a unit of work.
partials = [sort.delay(seq) for seq in subseqs]

# Merge all the individual sorted sub-lists into our final result.
m = gevent.spawn(merger, partials)
gevent.joinall([m, ])
result = m.value

dt = time.time() - t0
print('Distributed mergesort took %.02fs' % (dt))

# Do the same thing locally and compare the times.
t0 = time.time()
truth = sort(sequence)
dt = time.time() - t0
print('Local mergesort took %.02fs' % (dt))

# Final sanity checks.
try:
    assert result == truth
except:
    print(result)
    raise
assert result == sorted(sequence)
