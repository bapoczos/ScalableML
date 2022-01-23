import celery

# First we setup a connection to the message broker:

# Make sure that the 'myguest' user exists with 'myguestpwd' on the RabbitMQ server and your load balancer has been set up correctly.
# My load balancer address is'RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com'. 
# Below you will need to change it to your load balancer's address.

app = celery.Celery('test',
                        broker='amqp://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com',
                        backend='amqp://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com')

# Let us use the @app.task decorator on our echo function. It will allow us to call echo.delay() on the server remotely

@app.task
def echo(message):
    return 'Response from worker: '+message

#run this code with "celery -A test worker --loglevel=info". 

#Then this machine will become a worker, and will be able to run the app task, i.e. the echo function, whenever the broker requests it.

# The echo function will be run by these commands on a remote machine:

# from test import echo
# res = echo.delay('Python rocks!'); print(type(res)); print(res)
# res.result