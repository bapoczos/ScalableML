#!/usr/bin/env python3
import argparse
import time
import Pyro4


parser = argparse.ArgumentParser()
parser.add_argument('pairs', type=str, nargs='+')
args = parser.parse_args()


# Retrieve the rates sequentially.
t0 = time.time()
worker = Pyro4.Proxy("PYRONAME:MyWorker")

for pair in args.pairs:
    print(worker.get_rate(pair))
print('Sync calls: %.02f seconds' % (time.time() - t0))

# Retrieve the rates concurrently.
t0 = time.time()
worker = Pyro4.Proxy("PYRONAME:MyWorker")
async_worker = Pyro4.async(worker)

results = [async_worker.get_rate(pair) for pair in args.pairs]
for result in results:
    print(result.value)
print('Async calls: %.02f seconds' % (time.time() - t0))
