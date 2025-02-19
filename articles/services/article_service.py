from dataclasses import dataclass
from typing import Iterable
from datetime import datetime
from django.db.models import QuerySet
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from articles.models import Article, User
from articles.tasks import check_text


@dataclass
class ArticleEntity:
    title: str | None = None
    user_id: int | None = None
    text: str | None = None
    tags: list[int] | None = None
    image: str | None = None
    status: str | None = None
    

class ArticleService(object):
    _service = None

    def __new__(cls):
        if cls._service is None:
            cls._service = object.__new__(cls)
        return cls._service
    
    def fetch_all(self, exclude_fields: list[str]=None) -> QuerySet:
        queryset = Article.objects.prefetch_related('tags').select_related('user').all()
        if exclude_fields is not None:
            for field in exclude_fields:
                queryset = queryset.defer(field)
        return queryset
    
    def fetch(self, pk) -> Article:
        obj = get_object_or_404(Article, pk=pk)
        return obj
    
    def update(self, pk, data: ArticleEntity):
        with transaction.atomic():
            article = self.fetch(pk)
            fields = []
            if data.title is not None:
                article.title = data.title
                fields.append('title')
            if data.text is not None:
                article.text = data.text
                fields.append('text')
            if data.image is not None:
                article.image = data.image
                fields.append('image')
            article.status = Article.Status.NEW
            fields.append('status')
            article.save(update_fields=fields)
            if data.tags is not None:
                article.tags.set(data.tags)
            transaction.on_commit(lambda: self._post_process(article.pk))
    
    def create(self, data: ArticleEntity) -> Article:
        with transaction.atomic():
            new_article = Article.objects.create(
                title=data.title,
                user_id=data.user_id,
                text=data.text
            )
            new_article.tags.set(data.tags)
            return new_article
        
    def _post_process(self, pk=None):
        # Delete cache and check the text
        cache.delete("articles")
        if pk is not None:
            cache.delete(f"articles-{pk}")
            check_text.delay(pk)


class ArticleListService(ArticleService):
    def execute(self, exclude_fields=None) -> QuerySet:
        return self.fetch_all(exclude_fields)
        # serialized_articles = cache.get("articles")
        # if serialized_articles is None:
        #     articles = self.fetch_all(show_text)
        #     serializer = self.get_serializer(articles)
        #     serialized_articles = serializer.data
        #     cache.set("articles", serialized_articles, timeout=60*10)
        # return Response(serialized_articles)


class ArticleRetrieveService(ArticleService):
    def execute(self, pk) -> Article:
        return self.fetch(pk)
    

class ArticleUpdateService(ArticleService):
    def execute(self, pk, data: ArticleEntity):
        with transaction.atomic():
            self.update(pk, data)
            transaction.on_commit(lambda: self._post_process(pk))


class ArticleCreateService(ArticleService):
    def execute(self, data: ArticleEntity) -> Article:
        new_article = self.create(data)
        self._post_process(new_article.pk)
        return self.fetch(new_article.pk)
