import urllib.request
import Pyro4


URL = 'http://finance.yahoo.com/d/quotes.csv?s={}=X&f=p'


@Pyro4.expose(instance_mode="percall")
class Worker(object):
    def get_rate(self, pair, url_tmplt=URL):
        with urllib.request.urlopen(url_tmplt.format(pair)) as res:
            body = res.read()
        return (pair, float(body.strip()))


# Create a Pyro daemon which will run our code.
daemon = Pyro4.Daemon(host='ubuntu1')
uri = daemon.register(Worker)
Pyro4.locateNS().register('MyWorker', uri)

# Sit in an infinite loop accepting connections
print('Accepting connections')
try:
    daemon.requestLoop()
except KeyboardInterrupt:
    daemon.shutdown()
print('All done')
