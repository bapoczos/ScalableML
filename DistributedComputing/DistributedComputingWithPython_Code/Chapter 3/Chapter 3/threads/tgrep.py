from collections import defaultdict
from threading import Thread
from queue import Queue


def cat(f, case_insensitive, q):
    if case_insensitive:
        line_processor = lambda l: l.lower()
    else:
        line_processor = lambda l: l

    for line in f:
        q.put(line_processor(line))
    q.put(None)


def grep(substring, case_insensitive, inq, outq):
    if case_insensitive:
        substring = substring.lower()
    while True:
        text = inq.get()
        if text is None:
            outq.put((substring, None))
        else:
            outq.put((substring, text.count(substring)))
        inq.task_done()


def count(inq):
    totals = defaultdict(int)
    while True:
        substring, i = inq.get()
        if i is None:
            print(substring, totals[substring])
        else:
            totals[substring] += i
        inq.task_done()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store_true',
                        dest='case_insensitive')
    parser.add_argument('patterns', type=str, nargs='+',)
    parser.add_argument('infile', type=argparse.FileType('r'))

    args = parser.parse_args()

    inputq = Queue()
    outputq = Queue()
    thread_queues = []
    for pattern in args.patterns:
        q = Queue()
        t = Thread(target=grep,
                   kwargs={'substring': pattern,
                           'case_insensitive': args.case_insensitive,
                           'inq': inputq,
                           'outq': outputq})
        t.daemon = True
        t.start()

    counter = Thread(target=count,
                     kwargs={'inq': outputq})
    counter.daemon = True
    counter.start()

    cat(args.infile, args.case_insensitive, inputq)
    inputq.join()
    outputq.join()
