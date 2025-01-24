from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view, \
    PolymorphicProxySerializer, inline_serializer
from rest_framework import status, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.request import Request

from .models import Article, Comment
from .filters import ArticleFilter
from .serializers import ArticleDetailsSerializer, ArticleCreationSerializer, CommentListSerializer, \
    ArticleListSerializer, \
    ArticleWithCommentsSerializer, CommentCreateSerializer, ArticleUpdateSerializer, CommentDetailsSerializer, \
    CommentUpdateSerializer, TagSerializer, ImageUploadSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='title',
                description='Find the article where title contains this string (case insensitive)',
                required=False, 
                type=str
            ),
            OpenApiParameter(
                name='status_showable',
                description='If set to true gives only articles with status NEW and ACCEPTED, otherwise REJECTED',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='tags',
                description='Find the article which has these tags',
                required=False,
                type={
                    "type": "array",
                    "items": {"type": "integer"}
                }
            ),
        ],
        description='List of all articles. Filters them using parameters: title, status_showable, tags.',
        request=ArticleCreationSerializer,
        responses={200: ArticleListSerializer}
    ),
    create=extend_schema(
        description='Create new article. Must have "multipart/form-data" as the encoding type.',
        responses={201: ArticleDetailsSerializer}
    ),
)
class ArticleViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    # Base serializer class
    serializer_class = ArticleListSerializer
    # queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter
    parser_classes = [MultiPartParser, JSONParser, FormParser]

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
            case 'upload_image':
                return ImageUploadSerializer
            case _:
                return ArticleListSerializer
            
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        new_serializer = ArticleDetailsSerializer(instance)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def upload_image(self, request, pk=None):
        article = self.get_object()
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            article.image = serializer.validated_data['image']
            article.save()
            return Response({'status': 'image uploaded'})
    

# Resolves warning for the articles_pk parameter generated in the path by the NestedDefaultRouter
articles_pk_resolve_parameters = [OpenApiParameter(
    name='articles_pk',
    required=True,
    location=OpenApiParameter.PATH,
    description="ID of the article to which the comment belongs (comment's article_id)",
    type=int,
)]


@extend_schema_view(
    list=extend_schema(parameters=articles_pk_resolve_parameters),
    create=extend_schema(parameters=articles_pk_resolve_parameters),
    retrieve=extend_schema(parameters=articles_pk_resolve_parameters),
    update=extend_schema(parameters=articles_pk_resolve_parameters),
    partial_update=extend_schema(parameters=articles_pk_resolve_parameters),
    destroy=extend_schema(parameters=articles_pk_resolve_parameters)
)
class CommentViewSet(viewsets.ModelViewSet):
    # Base serializer class
    # serializer_class = CommentListSerializer
    # queryset = Comment.objects.all()

    def get_queryset(self):
        article_id = self.kwargs.get('articles_pk')
        return Comment.objects.filter(article_id=article_id)
        # return Comment.objects.all()

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


    # def get_serializer(self, *args, **kwargs):
    #     return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        request.data['article'] = int(self.kwargs.get('articles_pk'))
        return super().create(request, *args, **kwargs)        
