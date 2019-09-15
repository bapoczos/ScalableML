
# coding: utf-8

# In[1]:


import pika


# In[2]:


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


# In[3]:


credentials = pika.PlainCredentials('myguest', 'myguestpwd')
parameters =  pika.ConnectionParameters('PROD-JOB-844fd7d2202ac4da.elb.us-east-2.amazonaws.com', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='hello2')

# channel.basic_consume(callback,queue='hello2', no_ack=True)  # This was the old syntax
channel.basic_consume(queue='hello2', on_message_callback=callback, auto_ack=True)


# In[ ]:


print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

