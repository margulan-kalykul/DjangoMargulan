import pika
import sys
import os
import time

def main():
    # Establishing connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        # Proper acknowledgement from the worker
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Don't give worker another task until acknowledgement
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue',
                        on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    # Enter a never ending loop
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
