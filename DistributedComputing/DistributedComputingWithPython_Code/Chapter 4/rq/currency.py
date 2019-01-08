import urllib.request


URL = 'http://finance.yahoo.com/d/quotes.csv?s={}=X&f=p'


def get_rate(pair, url_tmplt=URL):
    # raise Exception('Booo!')

    with urllib.request.urlopen(url_tmplt.format(pair)) as res:
        body = res.read()
    return (pair, float(body.strip()))
