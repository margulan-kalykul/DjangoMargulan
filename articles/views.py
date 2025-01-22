from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, mixins, viewsets
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.request import Request

from .models import Article, Comment
from .filters import ArticleFilter
from .serializers import ArticleDetailsSerializer, ArticleCreationSerializer, CommentListSerializer, \
    ArticleListSerializer, \
    ArticleWithCommentsSerializer, CommentCreateSerializer, ArticleUpdateSerializer, CommentDetailsSerializer, \
    CommentUpdateSerializer


class ArticleViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    # Base serializer class
    serializer_class = ArticleListSerializer
    # queryset = Article.objects.all()

    def get_queryset(self):
        queryset = Article.objects.prefetch_related('tags').all()
        if self.action == 'list':
            queryset = queryset.defer('text')
        return queryset

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return ArticleListSerializer
            case 'create':
                return ArticleCreationSerializer
            case 'retrieve':
                return ArticleDetailsSerializer
            case 'update' | 'partial_update':
                return ArticleUpdateSerializer
            case _:
                return ArticleListSerializer

    # def list(self, request, *args, **kwargs):
    #     # print(self.get_queryset())
    #     return ArticleListSerializer
    #     response = super().list(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the create method
    #     # return ArticleCreationSerializer
    #     return response

    # def create(self, request, *args, **kwargs):
    #     return ArticleCreationSerializer
    #     return super().create(request, *args, **kwargs)
    
    # def retrieve(self, request, *args, **kwargs):
    #     # print(self.action)
    #     return ArticleDetailsSerializer
    #     response = super().retrieve(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the update and partial_update methods
    #     # return ArticleUpdateSerializer
    #     return response
    
    # def update(self, request, *args, **kwargs):
    #     return ArticleUpdateSerializer
    #     return super().update(request, *args, **kwargs)
    
    # def partial_update(self, request, *args, **kwargs):
    #     return ArticleUpdateSerializer
    #     return super().partial_update(request, *args, **kwargs)
    
    # def destroy(self, request, *args, **kwargs):
    #     return ArticleDetailsSerializer
    #     return super().destroy(request, *args, **kwargs)
    

class CommentViewSet(viewsets.ModelViewSet):

    # Base serializer class
    # serializer_class = CommentListSerializer
    # queryset = Comment.objects.all()

    def get_queryset(self):
        article_id = self.kwargs.get('articles_pk')
        return Comment.objects.filter(article_id=article_id)

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return CommentListSerializer
            case 'create':
                return CommentCreateSerializer
            case 'retrieve':
                return CommentDetailsSerializer
            case 'update':
                return CommentUpdateSerializer
            case 'partial_update':
                return CommentUpdateSerializer
            case 'destroy':
                return CommentDetailsSerializer
            case _:
                return CommentListSerializer

    # def list(self, request, *args, **kwargs):
    #     return CommentListSerializer
    #     # r: Request = request
    #     # print(self.get_queryset())
    #     # self.queryset = Comment.objects.filter(article_id=kwargs['article'])
    #     response = super().list(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the create method
    #     # return CommentCreateSerializer
    #     return response

    # def create(self, request, *args, **kwargs):
    #     return CommentCreateSerializer
    #     return super().create(request, *args, **kwargs)
    
    # def retrieve(self, request, *args, **kwargs):
    #     return CommentDetailsSerializer
    #     response = super().retrieve(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the update and partial_update methods
    #     # return CommentUpdateSerializer
    #     return response
    
    # def update(self, request, *args, **kwargs):
    #     return CommentUpdateSerializer
    #     return super().update(request, *args, **kwargs)
    
    # def partial_update(self, request, *args, **kwargs):
    #     return CommentUpdateSerializer
    #     return super().partial_update(request, *args, **kwargs)
    
    # def destroy(self, request, *args, **kwargs):
    #     return CommentDetailsSerializer
    #     return super().destroy(request, *args, **kwargs)


# # Form to create a new article and list of all articles
# class ArticlesList(generics.GenericAPIView,
#                    mixins.ListModelMixin):
#     queryset = Article.objects.prefetch_related('tags').all()
#     serializer_class = ArticleListSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ArticleFilter

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request):
#         serializer = ArticleCreationSerializer(data=request.data)
#         # Validate the form
#         if serializer.is_valid():
#             print("Is valid")
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # Show article details
# class ArticleDetail(generics.GenericAPIView,
#                     mixins.RetrieveModelMixin,
#                     mixins.DestroyModelMixin):
#     queryset = Article.objects.prefetch_related('tags').all()
#     serializer_class = ArticleDetailsSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ArticleFilter

#     def get_article(self, pk):
#         try:
#             return get_object_or_404(Article, pk=pk)
#         except Http404:
#             raise Http404
        
#     # def retrieve(self, request, *args, **kwargs):
#     #     article = self.get_object()
#     #     serializer = ArticleDetailsSerializer(article)  # SmallCommentSerializer(article)
#     #     # test = SmallCommentSerializer(article)
#     #     # print(test.data)
#     #     return Response(serializer.data)

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    
#     def put(self, request, article_id):
#         article = self.get_article(pk=article_id)
#         serializer = ArticleUpdateSerializer(article, data=request.data)
#         # serializer = ArticleCreationSerializer(article, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             article=serializer.save()
#             updated_serializer = ArticleDetailsSerializer(article)
#             return Response(updated_serializer.data)
    
#     def patch(self, request, article_id):
#         article = self.get_article(pk=article_id)
#         serializer = ArticleUpdateSerializer(article, data=request.data, partial=True)
#         if serializer.is_valid(raise_exception=True):
#             article = serializer.save()
#             updated_serializer = ArticleDetailsSerializer(article)
#             return Response(updated_serializer.data)
    
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(self, request, *args, **kwargs)
    

# # Show list of comments on an article
# class CommentList(generics.GenericAPIView,
#                   mixins.ListModelMixin):
#     queryset = Comment.objects.all()
#     serializer_class = CommentListSerializer

#     def get(self, request, *args, **kwargs):
#         article_id = kwargs['article_id']
#         self.queryset = self.queryset.filter(article_id=article_id)
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         article_id = kwargs['article_id']
#         request.data.update( {'article': article_id} )
#         serializer = CommentCreateSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             new_comment = serializer.save()
#             new_serializer = CommentListSerializer(new_comment)
#             print(new_serializer.data)
#             return Response(new_serializer.data, status=status.HTTP_201_CREATED)


# # Show specific comment
# class CommentDetails(generics.GenericAPIView,
#                      mixins.RetrieveModelMixin,
#                      mixins.DestroyModelMixin):
#     queryset = Comment.objects.all()
#     serializer_class = CommentListSerializer
#     # filter_backends = [DjangoFilterBackend]
#     # filterset_class = ArticleFilter
#     lookup_field = 'id'
#     lookup_url_kwarg = "comment_id"

#     def get_comment(self, pk):
#         try:
#             return get_object_or_404(Comment, pk=pk)
#         except Http404:
#             raise Http404
        
#     def get_queryset(self):
#         article_id = self.kwargs['article_id']
#         return Comment.objects.filter(article_id=article_id)

#     def get(self, request, article_id, comment_id, *args, **kwargs):
#         self.queryset = Comment.objects.filter(article_id=article_id)
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, article_id, comment_id):
#         comment = self.get_comment(pk=comment_id)
#         serializer = CommentListSerializer(comment, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             updated_comment = serializer.save()
#             updated_serializer = CommentListSerializer(updated_comment)
#             print(updated_serializer.data)
#             return Response(updated_serializer.data)
        
#     def patch(self, request, article_id, comment_id):
#         comment = self.get_comment(pk=comment_id)
#         serializer = CommentListSerializer(comment, data=request.data, partial=True)
#         if serializer.is_valid(raise_exception=True):
#             comment = serializer.save()
#             updated_serializer = CommentListSerializer(comment)
#             return Response(updated_serializer.data)
    
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

