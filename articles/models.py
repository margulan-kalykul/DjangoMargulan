from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField(default='Default text')
    author = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, related_name='articles')
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'"{self.title}" by {self.author}'
