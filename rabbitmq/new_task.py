import sys
import pika

# Establishing connection with RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(
    queue='task_queue', # We can't redefine existing queue with new parameters
    durable=True, # Makes the queue durable. Queue will survive even if RabbitMQ falls.
)

# Schedule tasks to our work queue
message = ' '.join(sys.argv[1:]) or "Hello world!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message, 
    # Marks our messages as persistent
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    )
)
print(f" [x] Sent {message}")

# Gently closing the connection
connection.close()
