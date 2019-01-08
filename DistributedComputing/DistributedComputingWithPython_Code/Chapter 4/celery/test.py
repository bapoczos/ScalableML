import celery


app = celery.Celery('test',
                    broker='amqp://yippy',
                    backend='redis://yippy')


@app.task
def echo(message):
    return message
