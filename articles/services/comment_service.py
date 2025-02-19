from dataclasses import dataclass
from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from articles.models import Comment, Status
from articles.tasks import check_text


@dataclass
class CommentEntity:
    article: int | None = None
    user: int | None = None
    text: str | None = None
    status: str | None = None


class CommentService(object):
    _service = None

    def __new__(cls):
        if cls._service is None:
            cls._service = object.__new__(cls)
        return cls._service

    def fetch_all(self, article_id) -> QuerySet:
        return Comment.objects.filter(article_id=article_id)

    def fetch(self, pk) -> Comment:
        return Comment.objects.get(pk=pk)

    def update(self, pk, data: CommentEntity):
        with transaction.atomic():
            comment = self.fetch(pk)
            fields = []
            if data.text is not None:
                comment.text = data.text
                fields.append('text')
            comment.status = Status.NEW
            fields.append('status')
            comment.save(update_fields=fields)
            transaction.on_commit(lambda: self.post_process(comment.pk))

    def create(self, data: CommentEntity) -> Comment:
        with transaction.atomic():
            new_comment = Comment.objects.create(
                article=data.article,
                user=data.user,
                text=data.text
            )
            return new_comment

    def post_process(self, pk=None):
        pass


class CommentListService(CommentService):
    def execute(self, article_id) -> QuerySet:
        return self.fetch_all(article_id)


class CommentRetrieveService(CommentService):
    def execute(self, pk) -> Comment:
        return self.fetch(pk)
    

class CommentUpdateService(CommentService):
    def execute(self, pk, data: CommentEntity):
        self.update(pk, data)


class CommentCreateService(CommentService):
    def execute(self, data: CommentEntity) -> Comment:
        return self.create(data)
