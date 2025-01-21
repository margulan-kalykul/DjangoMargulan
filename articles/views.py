from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, mixins
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import Article, Comment
from .filters import ArticleFilter
from .serializers import ArticleDetailsSerializer, ArticleCreationSerializer, CommentListSerializer, ArticleListSerializer, \
    ArticleWithCommentsSerializer, CommentCreateSerializer


# Form to create a new article and list of all articles
class ArticlesList(generics.GenericAPIView,
                   mixins.ListModelMixin):
    queryset = Article.objects.prefetch_related('tags').all()
    serializer_class = ArticleListSerializer
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
    serializer_class = ArticleDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter

    def get_article(self, pk):
        try:
            return get_object_or_404(Article, pk=pk)
        except Http404:
            raise Http404
        
    # def retrieve(self, request, *args, **kwargs):
    #     article = self.get_object()
    #     serializer = ArticleDetailsSerializer(article)  # SmallCommentSerializer(article)
    #     # test = SmallCommentSerializer(article)
    #     # print(test.data)
    #     return Response(serializer.data)

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
    serializer_class = CommentListSerializer

    # def set_comments(self, pk):
    #     """
    #     Sets the queryset to needed comments
    #     """
    #     self.queryset = Comment.objects.filter(article_id=pk)

    def get(self, request, pk, *args, **kwargs):
        self.queryset = self.queryset.filter(article_id=pk)
        return self.list(request, *args, **kwargs)

    # TODO: Deal with the problem with 'article_id' and 'article'. 
    # When changing data['article'] = pk to data['article_id'] = pk data includes both of them and doesn't work properly.
    def post(self, request, pk):
        data = request.data.copy()
        data['article'] = pk
        print(data)
        serializer = CommentCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Show specific comment
class CommentDetails(generics.GenericAPIView,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = ArticleFilter

    def get_comment(self, pk):
        try:
            return get_object_or_404(Comment, pk=pk)
        except Http404:
            raise Http404

    def get(self, request, *args, **kwargs):
    # def get(self, request, apk, cpk):
        print(self.get_object())
        # return Response(self.get_comment(pk=cpk))
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, pk):
        comment = self.get_comment(pk=pk)
        # data = request.data.copy()
        # data['pk'] = cpk
        serializer = CommentListSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

