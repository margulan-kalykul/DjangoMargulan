from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//', task_serializer='json',
    accept_content=['json'], backend='rpc://')

@app.task
def add(x, y):
    return x + y

# Launch using: celery -A <module> worker -l info -P gevent
# Launch RabbitMQ using: docker run -d -p 5672:5672 rabbitmq