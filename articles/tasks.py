# Create your tasks here

from .models import Article
from celery import shared_task
from .serializers import ArticleUpdateSerializer, ArticleCreationSerializer
from .secret_keys import OPENAI_API
import openai
from django.db import transaction

@shared_task
def check_text(article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Exception as e:
        raise e
    text = article.text
    query = f"""
    Check the text provided if it contains any mentions of terrorism. If it does return this single string - 
    "REJECTED" (without quotes).
    If it does not then return single string - 
    "ACCEPTED" (without quotes).
    The text provided: 
    {text}
    """
    openai.api_key = OPENAI_API
    messages = [{"role": "system", "content": "You are a intelligent assistant."}]
    if text:
        messages.append(
            {
                "role": "user", 
                "content": query,
            },
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    answer: str = chat.choices[0].message.content

    if answer == Article.Status.ACCEPTED:
        status = Article.Status.ACCEPTED
    elif answer == Article.Status.REJECTED:
        status = Article.Status.REJECTED
    with transaction.atomic():
        article.status = status
        article.save(update_fields=['status', 'updated_at'])

@shared_task
def create_article(data):
    serializer = ArticleCreationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    check_text(instance.title + ".\n" + instance.text, instance.id)
    return ArticleCreationSerializer(instance).data

@shared_task
def update_article(pk, data, partial):
    instance = Article.objects.get(pk=pk)
    instance.status = Article.Status.NEW
    serializer = ArticleUpdateSerializer(instance, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    if getattr(instance, '_prefetched_objects_cache', None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
        instance._prefetched_objects_cache = {}
    check_text(instance.title + ".\n" + instance.text, instance.id)
    return ArticleUpdateSerializer(instance).data
