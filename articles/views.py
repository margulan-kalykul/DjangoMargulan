from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view, \
    PolymorphicProxySerializer, inline_serializer
import jwt
from rest_framework import status, generics, mixins, viewsets, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, SAFE_METHODS, IsAuthenticated

from articles.authentications import RoleAuthentication
from .permissions import HasRole, IsReader, IsModerator, HasCorrectPermissions
from mysite.settings import SECRET_KEY
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser, Permission, Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction, DatabaseError, IntegrityError

from .models import Article, Comment, User
from .filters import ArticleFilter
from .serializers import ArticleDetailsSerializer, ArticleCreationSerializer, CommentListSerializer, \
    ArticleListSerializer, \
    ArticleWithCommentsSerializer, CommentCreateSerializer, ArticleUpdateSerializer, CommentDetailsSerializer, \
    CommentUpdateSerializer, TagSerializer, ImageUploadSerializer, UserSerializer, RegistrationSerializer, \
    TokenObtainWithGroupSerializer
from .tasks import check_text
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny, ]
    serializer_class = TokenObtainWithGroupSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User has registered"}, status=status.HTTP_201_CREATED)


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
        description='Create new article.',
        responses={201: ArticleDetailsSerializer}
    ),
)
class ArticleViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    authentication_classes = [RoleAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    # Base serializer class
    serializer_class = ArticleListSerializer
    # queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'user__username']
    ordering_fields = ['title']
    ordering = ['id']
    # parser_classes = [MultiPartParser, JSONParser, FormParser]

    def get_queryset(self):
        queryset = Article.objects.prefetch_related('tags').select_related('user').all()
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
            
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), HasRole(['author', 'moderator'])]
        elif self.action in ['create', 'update', 'partial_update', 'delete', 'upload_image']:
            return [IsAuthenticated(), HasRole(['author'])]
        return super().get_permissions()
            
    def retrieve(self, request, pk, *args, **kwargs):
        article = cache.get(f"articles-{pk}")
        self.check_object_permissions(request, article)
        if article is None:
            article = self.get_object()
            serializer = ArticleDetailsSerializer(article)
            article = serializer.data
            cache.set(f"articles-{pk}", article, timeout=60*10)
        return Response(article)

    def post_process(self, pk=None):
        cache.delete("articles")
        if pk is not None:
            cache.delete(f"articles-{pk}")
            check_text.delay(pk)

    def partial_update(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.status = Article.Status.NEW
            serializer = ArticleUpdateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            transaction.on_commit(lambda: self.post_process(pk))
            return Response(serializer.data)
    
    def update(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.status = Article.Status.NEW
            serializer = ArticleUpdateSerializer(instance, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            transaction.on_commit(lambda: self.post_process(pk))
            return Response(serializer.data)
            
    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        with transaction.atomic():
            serializer = ArticleCreationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            new_serializer = ArticleDetailsSerializer(instance)
            transaction.on_commit(lambda: self.post_process())
            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], parser_classes=[MultiPartParser])
    def upload_image(self, request, pk=None):
        with transaction.atomic():
            article = self.get_object()
            serializer = ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            article.image = serializer.validated_data['image']
            article.save()
            transaction.on_commit(lambda: self.post_process(pk))
            return Response(serializer.data)
    

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
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [RoleAuthentication, ]

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
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), HasRole(['author', 'moderator'])]
        elif self.action in ['create', 'update', 'partial_update', 'delete', 'upload_image']:
            return [IsAuthenticated(), HasRole(['author'])]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        request.data['article'] = int(self.kwargs.get('articles_pk'))
        return super().create(request, *args, **kwargs)        
