#!/usr/bin/env python3
import argparse
import subprocess


def terminate(proc, timeout=.5):
    """
    Perform a two-step termination of process `proc`: send a SIGTERM
    and, after `timeout` seconds, send a SIGKILL. This should give
    `proc` enough time to do any necessary cleanup.
    """
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
    return


parser = argparse.ArgumentParser()
parser.add_argument('N', type=int)
args = parser.parse_args()

workers = []
for _ in range(args.N):
    workers.append(subprocess.Popen(['rqworker',
                                     '-u', 'redis://yippy']))

try:
    running = [w for w in workers if w.poll() is None]
    while running:
        proc = running.pop(0)
        try:
            proc.wait(timeout=1.)
        except subprocess.TimeoutExpired:
            running.append(proc)
except KeyboardInterrupt:
    for w in workers:
        terminate(w)
