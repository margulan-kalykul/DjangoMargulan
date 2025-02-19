from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser
from rest_framework_simplejwt.tokens import Token

from .models import Article, Tag, Comment, User


class TokenObtainWithGroupSerializer(TokenObtainPairSerializer):
    # pass
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        token = super().get_token(user)
        token['groups'] = [group.name for group in user.groups.all()]
        return token


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', ]


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['id', 'user', 'text', 'updated_at']
        read_only = fields
        # extra_kwargs = {'password': {'read_only': True}}


class CommentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'text', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    # article_id = serializers.IntegerField()
    class Meta:
        model = Comment
        # exclude = ['created_at', 'status']
        fields = ['user', 'text', 'article']


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


class ArticleDetailsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    user = UserShowSerializer()

    class Meta:
        model = Article
        exclude = ['created_at', 'status']


class ArticleListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Article
        fields = ['id', 'title', 'tags', 'user', 'image', 'created_at']


class ArticleWithCommentsSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True)

    class Meta:
        model = Article
        exclude = ['created_at', 'status', ]


class ArticleCreationSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField(child=serializers.IntegerField())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    # tags = serializers.SerializerMethodField()

    # def get_tags(self, obj):
    #     return [tag.id for tag in obj.tags.all()]

    class Meta:
        model = Article
        fields = ['title', 'tags', 'text']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField(child=serializers.IntegerField())
    # tags = serializers.PrimaryKeyRelatedField(
    #     queryset=Article.objects.prefetch_related('tags').select_related('user').defer('text').all(),
    #     many=True
    # )

    class Meta:
        model = Article
        fields = ['title', 'tags', 'text']
        # extra_kwargs = {'tags': {'required': False}, 'title': {'required': False}}


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()


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
