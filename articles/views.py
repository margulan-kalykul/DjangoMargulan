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


class ArticleViewSet(viewsets.ModelViewSet):
    # Base serializer class
    serializer_class = ArticleListSerializer
    queryset = Article.objects.all()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                self.serializer_class = ArticleListSerializer
            case 'create':
                self.serializer_class = ArticleCreationSerializer
            case 'retrieve':
                self.serializer_class = ArticleDetailsSerializer
            case 'update':
                self.serializer_class = ArticleUpdateSerializer
            case 'partial_update':
                self.serializer_class = ArticleUpdateSerializer
            case 'destroy':
                self.serializer_class = ArticleDetailsSerializer
        return super().get_serializer_class()

    # def list(self, request, *args, **kwargs):
    #     # print(self.get_queryset())
    #     self.serializer_class = ArticleListSerializer
    #     response = super().list(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the create method
    #     # self.serializer_class = ArticleCreationSerializer
    #     return response

    # def create(self, request, *args, **kwargs):
    #     self.serializer_class = ArticleCreationSerializer
    #     return super().create(request, *args, **kwargs)
    
    # def retrieve(self, request, *args, **kwargs):
    #     # print(self.action)
    #     self.serializer_class = ArticleDetailsSerializer
    #     response = super().retrieve(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the update and partial_update methods
    #     # self.serializer_class = ArticleUpdateSerializer
    #     return response
    
    # def update(self, request, *args, **kwargs):
    #     self.serializer_class = ArticleUpdateSerializer
    #     return super().update(request, *args, **kwargs)
    
    # def partial_update(self, request, *args, **kwargs):
    #     self.serializer_class = ArticleUpdateSerializer
    #     return super().partial_update(request, *args, **kwargs)
    
    # def destroy(self, request, *args, **kwargs):
    #     self.serializer_class = ArticleDetailsSerializer
    #     return super().destroy(request, *args, **kwargs)
    

class CommentViewSet(viewsets.ModelViewSet):
    # Base serializer class
    serializer_class = CommentListSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        article_id = self.kwargs.get('articles_pk')
        return Comment.objects.filter(article_id=article_id)

    def get_serializer_class(self):
        match self.action:
            case 'list':
                self.serializer_class = CommentListSerializer
            case 'create':
                self.serializer_class = CommentCreateSerializer
            case 'retrieve':
                self.serializer_class = CommentDetailsSerializer
            case 'update':
                self.serializer_class = CommentUpdateSerializer
            case 'partial_update':
                self.serializer_class = CommentUpdateSerializer
            case 'destroy':
                self.serializer_class = CommentDetailsSerializer
        return super().get_serializer_class()

    # def list(self, request, *args, **kwargs):
    #     self.serializer_class = CommentListSerializer
    #     # r: Request = request
    #     # print(self.get_queryset())
    #     # self.queryset = Comment.objects.filter(article_id=kwargs['article'])
    #     response = super().list(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the create method
    #     # self.serializer_class = CommentCreateSerializer
    #     return response

    # def create(self, request, *args, **kwargs):
    #     self.serializer_class = CommentCreateSerializer
    #     return super().create(request, *args, **kwargs)
    
    # def retrieve(self, request, *args, **kwargs):
    #     self.serializer_class = CommentDetailsSerializer
    #     response = super().retrieve(request, *args, **kwargs)
    #     # Set the base serializer class to the one used in the update and partial_update methods
    #     # self.serializer_class = CommentUpdateSerializer
    #     return response
    
    # def update(self, request, *args, **kwargs):
    #     self.serializer_class = CommentUpdateSerializer
    #     return super().update(request, *args, **kwargs)
    
    # def partial_update(self, request, *args, **kwargs):
    #     self.serializer_class = CommentUpdateSerializer
    #     return super().partial_update(request, *args, **kwargs)
    
    # def destroy(self, request, *args, **kwargs):
    #     self.serializer_class = CommentDetailsSerializer
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

