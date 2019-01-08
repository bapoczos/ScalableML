#!/usr/bin/env python3.5
"""
Simple example showing how to catch signals in Python
"""
import json
import os
import signal
import sys


# Path to the file we use to store state. Note that we assume
# $HOME to be defined, which is far from being an obvious
# assumption!
STATE_FILE = os.path.join(os.environ['HOME'],
                          '.checkpoint.json')


class Checkpointer:
    def __init__(self, state_path=STATE_FILE):
        """
        Read the state file, if present, and initialize from that.
        """
        self.state = {}
        self.state_path = state_path
        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                self.state.update(json.load(f))
        return

    def save(self):
        print('Saving state: {}'.format(self.state))
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f)
        return

    def eviction_handler(self, signum, frame):
        """
        This is the function that gets called when a signal is trapped.
        """
        self.save()

        # Of course, using sys.exit is a bit brutal. We can do better.
        print('Quitting')
        sys.exit(0)
        return


if __name__ == '__main__':
    import time

    print('This is process {}'.format(os.getpid()))

    ckp = Checkpointer()
    print('Initial state: {}'.format(ckp.state))

    # Catch SIGQUIT
    signal.signal(signal.SIGQUIT, ckp.eviction_handler)

    # Get a value from the state.
    i = ckp.state.get('i', 0)
    try:
        while True:
            i += 1
            ckp.state['i'] = i
            print('Updated in-memory state: {}'.format(ckp.state))
            time.sleep(1)
    except KeyboardInterrupt:
        ckp.save()
