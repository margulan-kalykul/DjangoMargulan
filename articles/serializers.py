from rest_framework import serializers
from .models import Article, Tag, Comment, Status


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['id', 'author', 'text', 'updated_at']
        read_only = fields
        # extra_kwargs = {'password': {'read_only': True}}


class CommentCreateSerializer(serializers.ModelSerializer):
    # article_id = serializers.IntegerField()
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['author', 'text', 'article']


class ArticleDetailsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        exclude = ['created_at', 'status']


class ArticleListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'tags', 'author', 'image', 'created_at']


class ArticleWithCommentsSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True)

    class Meta:
        model = Article
        exclude = ['created_at', 'status', ]


class ArticleCreationSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["tags"].choices = [tag.id for tag in Tag.objects.all()]

    class Meta:
        model = Article
        fields = ['title', 'tags', 'author', 'text', 'image']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'tags', 'text', 'image']
        # extra_kwargs = {'tags': {'required': False}, 'title': {'required': False}}

