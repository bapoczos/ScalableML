# RUN these first in your terminal!

# sudo rabbitmqctl add_user myguest myguestpwd
# sudo rabbitmqctl set_permissions -p / myguest "." "." ".*"

# Goal: Receive one message from the publisher, print it, and then quit

import asyncio
import aio_pika

# we will use and event loop in the main function
async def main(loop):
    
    # connection through localhost
    connection = await aio_pika.connect_robust(
        "amqp://myguest:myguestpwd@RabbitMQLB-8e09cd48a60c9a1e.elb.us-east-2.amazonaws.com/", loop=loop
    )

    async with connection:
        
        # set up a routing key. It should be the same as the publisher's key
        queue_name = "test_queue"

        # Creating channel
        channel = await connection.channel()    # type: aio_pika.Channel

        # Declaring queue
        queue = await channel.declare_queue(
            queue_name,
            auto_delete=True
        )   # type: aio_pika.Queue

        # This is how we can async receive messages from the queue
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    # print the message we received
                    print(f'message received: {message.body}')

                    if queue.name in message.body.decode():
                        print('queue name: '+queue.name)
                        break # We want to receive only one message, then we quit


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))

loop.close()

