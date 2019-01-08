#!/usr/bin/env python3.5
#PBS -J 0-99
#PBS -V
import argparse
import getpass
import os
import socket
import sys


ENV_VARS = ('MYVAR1', 'MYVAR2')

if 'PBS_ENVIRONMENT' in os.environ:
    # raw_cid has the form integer[].server
    raw_cid = os.environ['PBS_ARRAY_ID']
    cid = int(raw_cid.split('[')[0])
    pid = int(os.environ['PBS_ARRAY_INDEX'])
else:
    parser = argparse.ArgumentParser()
    parser.add_argument('--clusterid', type=int)
    parser.add_argument('--processid', type=int)
    args = parser.parse_args()

    cid = args.clusterid
    pid = args.processid

print('I am process {} of cluster {}'
      .format(pid, cid))
print('Running on {}'
      .format(socket.gethostname()))
print('$CWD = {}'
      .format(os.getcwd()))
print('$USER = {}'
      .format(getpass.getuser()))

undefined = []
for v in ENV_VARS:
    if v in os.environ:
        print('{} = {}'
              .format(v, os.environ[v]))
    else:
        print('Error: {} undefined'
              .format(v))
        undefined.append(v)
if undefined:
    sys.exit(1)
sys.exit(0)
