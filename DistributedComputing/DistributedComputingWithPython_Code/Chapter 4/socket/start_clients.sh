#!/bin/bash
N=4

echo "Starting ${N} worker(s) on ${HOST}."
for i in `seq 1 ${N}`;
do
    python3.5 ./client.py &
done

trap "kill 0" SIGINT SIGTERM EXIT
wait
