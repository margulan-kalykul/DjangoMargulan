import openai
from django.dispatch import receiver
from .models import Article
from django.db.models.signals import post_save
from .secret_keys import OPENAI_API


openai.api_key = OPENAI_API
messages = [{"role": "system", "content": "You are a intelligent assistant."}]


@receiver(post_save, sender=Article)
def chatgpt_check(sender, instance, created, **kwargs):
    print("Received")
    if not created:
        return
    text = instance.text
    article_id = instance.id
    query = f"""
    Check the text provided if it contains any mentions of terrorism. If it does return this single string - 
    "REJECTED" (without quotes).
    If it does not then return single string - 
    "ACCEPTED" (without quotes).
    The text provided: 
    {text}
    """
    if text:
        messages.append(
            {
                "role": "user", 
                "content": query,
            },
        )
        chat = openai.ChatCompletion.create(
            model="gpt-4o-mini", messages=messages
        )
    answer: str = chat.choices[0].message.content
    print(answer)

    if answer == Article.Status.ACCEPTED:
        accepted_article = Article.objects.get(pk=article_id)
        accepted_article.status = Article.Status.ACCEPTED
        accepted_article.save()
    elif answer == Article.Status.REJECTED:
        rejected_article = Article.objects.get(pk=article_id)
        rejected_article.status = Article.Status.REJECTED
        rejected_article.save()
    else:
        print(answer)
