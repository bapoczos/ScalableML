import celery
import urllib.request


app = celery.Celery('currency',
                    broker='amqp://yippy',
                    backend='redis://yippy')


URL = 'http://finance.yahoo.com/d/quotes.csv?s={}=X&f=p'


@app.task
def get_rate(pair, url_tmplt=URL):
    # raise Exception('Booo!')

    with urllib.request.urlopen(url_tmplt.format(pair)) as res:
        body = res.read()
    return (pair, float(body.strip()))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('pairs', type=str, nargs='+')
    args = parser.parse_args()

    results = [get_rate.delay(pair) for pair in args.pairs]
    for result in results:
        try:
            pair, rate = result.get(timeout=1)
        except:
            print('Ops! Got an exception.')
        else:
            print(pair, rate)
