# Create your tasks here

from .models import Article
from celery import shared_task
from .serializers import ImageUploadSerializer, ArticleUpdateSerializer, ArticleCreationSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
import time

@shared_task
def add(x, y):
    return x + y

@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def create_article(data):
    serializer = ArticleCreationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return instance.id

# TODO: Make a check by chatgpt in the task
@shared_task
def update_article(pk, data, partial):
    # print("Started saving")
    # time.sleep(15)
    instance = Article.objects.get(pk=pk)
    instance.status = Article.Status.NEW
    serializer = ArticleUpdateSerializer(instance, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    if getattr(instance, '_prefetched_objects_cache', None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
        instance._prefetched_objects_cache = {}
    # print("Finished saving")
