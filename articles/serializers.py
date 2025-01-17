from rest_framework import serializers
from .models import Article, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

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
