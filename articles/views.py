from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, mixins
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import Article, Comment
from .filters import ArticleFilter
from .serializers import ArticleSerializer, ArticleCreationSerializer, CommentSerializer, ArticleWithCommentsSerializer


# Form to create a new article and list of all articles
class ArticlesList(generics.GenericAPIView,
                   mixins.ListModelMixin):
    queryset = Article.objects.prefetch_related('tags').all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request):
        serializer = ArticleCreationSerializer(data=request.data)
        # Validate the form
        if serializer.is_valid():
            print("Is valid")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Show article details
class ArticleDetail(generics.GenericAPIView,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin):
    queryset = Article.objects.prefetch_related('tags').all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter

    def get_article(self, pk):
        try:
            return get_object_or_404(Article, pk=pk)
        except Http404:
            raise Http404
        
    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = ArticleWithCommentsSerializer(article)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, pk):
        article = self.get_article(pk=pk)
        serializer = ArticleCreationSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)
    

# Show list of comments on an article
class CommentList(generics.GenericAPIView,
                  mixins.ListModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Show specific comment
class CommentDetails(generics.GenericAPIView,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = ArticleFilter

    def get_comment(self, pk):
        try:
            return get_object_or_404(Comment, pk=pk)
        except Http404:
            raise Http404

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, pk):
        comment = self.get_comment(pk=pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

