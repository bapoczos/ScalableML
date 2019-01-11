import celery

# First we setup a connection to the message broker:

app = celery.Celery('test',
                        broker='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com')

@app.task
def echo(message):
    return message

#run this code with "celery -A test worker --loglevel=info". 
#Then this machine will become a worker, and will be able to run the app task, i.e. the echo function, whenever the broker requests it.

# The echo function will be run by these commands on a remote machine:

# from test import echo
# res = echo.delay('Python rocks!'); print(type(res)); print(res)
# res.result