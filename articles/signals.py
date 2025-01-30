from django.dispatch import receiver
from .models import Article
from django.db.models.signals import post_save
from .tasks import check_text


# @receiver(post_save, sender=Article)
# def chatgpt_check(sender, instance, created, **kwargs):
#     if instance.status != Article.Status.NEW:
#         return
#     # if not created:
#     #     return
#     text = instance.title + "\n" + instance.text
#     check_text.delay(text)
