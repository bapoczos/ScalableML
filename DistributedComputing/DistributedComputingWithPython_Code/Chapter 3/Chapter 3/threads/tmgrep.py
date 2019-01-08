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
            outq.put(None)
        else:
            outq.put(text.count(substring))
        inq.task_done()


def count(substring, inq):
    n = 0
    while True:
        i = inq.get()
        if i is None:
            print(substring, n)
        else:
            n += i
        inq.task_done()


def fanout(inq, outqs):
    while True:
        data = inq.get()
        for outq in outqs:
            outq.put(data)
        inq.task_done()


def start_grep_workers(patterns, case_insensitive, queues):
    for i, (inq, outq) in enumerate(queues):
        t = Thread(target=grep,
                   kwargs={'substring': patterns[i],
                           'case_insensitive': args.case_insensitive,
                           'inq': inq,
                           'outq': outq})
        t.daemon = True
        t.start()
    return


def start_fanout_worker(inq, outqs):
    t = Thread(target=fanout,
               kwargs={'inq': inq,
                       'outqs': outqs})
    t.daemon = True
    t.start()
    return


def start_count_workers(patterns, inqs):
    for i, inq in enumerate(inqs):
        t = Thread(target=count,
                   kwargs={'substring': patterns[i],
                           'inq': inq})
        t.daemon = True
        t.start()
    return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store_true',
                        dest='case_insensitive')
    parser.add_argument('patterns', type=str, nargs='+',)
    parser.add_argument('infile', type=argparse.FileType('r'))

    args = parser.parse_args()

    in_queue = Queue()
    worker_queues = [(Queue(), Queue()) for _ in args.patterns]

    start_grep_workers(args.patterns,
                       args.case_insensitive,
                       worker_queues)
    start_fanout_worker(in_queue, [qs[0] for qs in worker_queues])
    start_count_workers(args.patterns, [qs[1] for qs in worker_queues])

    cat(args.infile, args.case_insensitive, in_queue)

    in_queue.join()
    for inq, outq in worker_queues:
        inq.join()
        outq.join()
