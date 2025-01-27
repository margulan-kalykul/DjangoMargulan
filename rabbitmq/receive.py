import pika, sys, os

def main():
    # Establishing connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Ensure a queue named 'hello' exists
    # channel.queue_declare will create only one queue no matter how many times we run it
    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    # callback function is subscribed to the queue 'hello'
    channel.basic_consume(queue='hello',
                        auto_ack=True,
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
