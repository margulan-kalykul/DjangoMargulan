from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField()
    # def __str__(self):
    #     return self.username


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW"
        ACCEPTED = "ACCEPTED"
        REJECTED = "REJECTED"
    title = models.CharField(max_length=200, db_index=True)
    text = models.TextField(default='Default text')
    # author = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles')
    image = models.ImageField(upload_to='saved', null=True, blank=True)
    status = models.CharField(choices=Status, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'"{self.title}" by {self.author}'


class Status(models.TextChoices):
    NEW = "NEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    # author = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(default='Default text')
    status = models.CharField(choices=Status, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author} wrote: "{self.text}"'
