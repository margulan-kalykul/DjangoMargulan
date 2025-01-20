from rest_framework import serializers
from .models import Article, Tag, Comment, Status


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ArticleWithCommentsSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(max_length=200)
    # text = serializers.CharField()
    # author = serializers.CharField(max_length=100)
    # tags = TagSerializer(many=True)
    # image = serializers.ImageField(allow_null=True, allow_empty_file=True)
    # status = serializers.CharField()
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()
    comments = CommentSerializer(many=True)

    class Meta:
        model = Article
        fields = '__all__'


class ArticleCreationSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["tags"].choices = [tag.id for tag in Tag.objects.all()]

    class Meta:
        model = Article
        fields = ['title', 'tags', 'author', 'text', 'image']
