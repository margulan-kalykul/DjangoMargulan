from django.contrib import admin
from .models import Article, Tag, Comment, Author

# Register your models here.
admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Author)
