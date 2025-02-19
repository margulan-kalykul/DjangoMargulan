from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import status, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated
import rest_framework.serializers

from articles.authentications import RoleAuthentication
from articles.services import article_service, comment_service
from .permissions import HasRole
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction

from .models import Article, Comment, Status
from .filters import ArticleFilter
from .serializers import ArticleDetailsSerializer, ArticleCreationSerializer, CommentListSerializer, \
    ArticleListSerializer, \
    CommentCreateSerializer, ArticleUpdateSerializer, CommentDetailsSerializer, \
    CommentUpdateSerializer, ImageUploadSerializer, RegistrationSerializer, \
    TokenObtainWithGroupSerializer
from .tasks import check_text
from django.core.cache import cache
from rest_framework.serializers import ModelSerializer


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
        service = article_service.ArticleListService()
        exclude_fields = None
        if self.action == 'list':
            exclude_fields = ['text']
        return service.execute(exclude_fields)

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
    
    def get_object(self):
        pk = self.kwargs.get('articles_pk')
        if pk is None:
            raise Exception('Article id is not given.')
        service = article_service.ArticleRetrieveService()
        article = service.execute(pk)
        self.check_object_permissions(self.request, article)
        return article
    
    # def list(self, request, *args, **kwargs):
    #     serialized_articles = cache.get("articles")
    #     if serialized_articles is None:
    #         articles = super().list(request, *args, **kwargs)
    #         serializer = self.get_serializer(articles)
    #         serialized_articles = serializer.data
    #         cache.set("articles", serialized_articles, timeout=60*10)
    #     return Response(serialized_articles)
            
    def retrieve(self, request, pk, *args, **kwargs):
        serialized_article = cache.get(f"articles-{pk}")
        if serialized_article is None:
            article = self.get_object()
            serializer = self.get_serializer(article)
            serialized_article = serializer.data
            cache.set(f"articles-{pk}", serialized_article, timeout=60*10)
        return Response(serialized_article)

    def partial_update(self, request, pk, *args, **kwargs):
        return self.update(request, pk, *args, partial=True, **kwargs)
    
    def update(self, request, pk, *args, **kwargs):
        # Get variable that decides if the update is partial or not
        partial = kwargs.get('partial')
        if partial is None:
            partial = False
        # Validation
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Make an entity from request.data
        article_entity = article_service.ArticleEntity(**serializer.validated_data)
        # Perform update
        update_service = article_service.ArticleUpdateService()
        update_service.execute(pk, article_entity)
        # Get new updated article
        retrieve_service = article_service.ArticleRetrieveService()
        article = retrieve_service.execute(pk)
        # Serialize it and return
        serializer = self.get_serializer(article)
        return Response(serializer.data)
            
    def create(self, request, *args, **kwargs):
        # Validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Make an entity from request.data
        article_entity = article_service.ArticleEntity(user_id=request.user.id, **serializer.validated_data)
        # Perform create and get the newly created article
        create_service = article_service.ArticleCreateService()
        article = create_service.execute(article_entity)
        # Serialize the article and return
        serializer = self.get_serializer(article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], parser_classes=[MultiPartParser])
    def upload_image(self, request, pk=None, *args, **kwargs):
        return self.update(request, pk, *args, partial=True, **kwargs)
    

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
        service = comment_service.CommentListService()
        return service.execute(int(self.kwargs.get('articles_pk')))

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
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        if pk is None:
            raise Exception('Article id is not given.')
        service = comment_service.CommentRetrieveService()
        comment = service.execute(pk)
        self.check_object_permissions(self.request, comment)
        return comment

    def partial_update(self, request, pk, *args, **kwargs):
        return self.update(request, pk, *args, partial=True, **kwargs)
    
    def update(self, request, pk, *args, **kwargs):
        # Get variable that decides if the update is partial or not
        partial = kwargs.get('partial')
        if partial is None:
            partial = False
        # Set comment as new
        request.data['status'] = Status.NEW
        # Validation
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Make an entity from request.data
        comment_entity = comment_service.CommentEntity(
            article=serializer.validated_data.get('article'),
            user=serializer.validated_data.get('user'),
            text=serializer.validated_data.get('text')
        )
        # Perform update
        update_service = comment_service.CommentUpdateService()
        update_service.execute(pk, comment_entity)
        # Get new updated comment
        retrieve_service = comment_service.CommentRetrieveService()
        comment = retrieve_service.execute(pk)
        # Serialize it and return
        serializer = self.get_serializer(comment, partial=partial)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data['article'] = int(self.kwargs.get('articles_pk'))
        request.data['user'] = request.user.id
        # Validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Make an entity from request.data
        comment_entity = comment_service.CommentEntity(
            article=serializer.validated_data.get('article'),
            user=serializer.validated_data.get('user'),
            text=serializer.validated_data.get('text')
        )
        # Perform create and get the newly created comment
        create_service = comment_service.CommentCreateService()
        comment = create_service.execute(comment_entity)
        # Serialize the comment and return
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
