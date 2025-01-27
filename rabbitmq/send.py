import pika

# Establishing connection with RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Create a queue named 'hello'
channel.queue_declare(queue='hello')

# Establish default exchange
channel.basic_publish(exchange='',
                      routing_key='hello', # Name of the queue
                      body='Hello world!')
print(" [x] Sent the 'Hello world!'")

# Gently closing the connection
connection.close()
