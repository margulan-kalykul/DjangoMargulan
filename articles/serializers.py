from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Article, Tag, Comment, Status, Author
from django.contrib.auth.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


# class AuthorShowSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', ]


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['id', 'author', 'text', 'updated_at']
        read_only = fields
        # extra_kwargs = {'password': {'read_only': True}}


class CommentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'text', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    # article_id = serializers.IntegerField()
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['author', 'text', 'article']


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


class ArticleDetailsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        exclude = ['created_at', 'status']


class ArticleListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.CharField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'tags', 'author', 'image', 'created_at']


class ArticleWithCommentsSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True)

    class Meta:
        model = Article
        exclude = ['created_at', 'status', ]


class ArticleCreationSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Article
        fields = ['title', 'tags', 'author', 'text']


class ArticleUpdateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Article
        fields = ['title', 'tags', 'text']
        # extra_kwargs = {'tags': {'required': False}, 'title': {'required': False}}


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['username', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
