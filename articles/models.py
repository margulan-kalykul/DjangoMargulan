from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField(default='Default text')
    author = models.CharField(max_length=100)

    def __str__(self):
        return f'"{self.title}" by {self.author}'
    

class Tag(models.Model):
    tag = models.CharField(max_length=100)
    articles = models.ManyToManyField(Article, related_name='tags')

    def __str__(self):
        return self.tag
