from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from articles import views

articles_router = DefaultRouter()
articles_router.register(r'articles', views.ArticleViewSet, basename='articles')
# articles_router.register(r'articles/(?P<article_id>[^/.]+)/comments', views.CommentViewSet, basename='comments')
comments_router = NestedDefaultRouter(articles_router, r'articles', lookup='articles')
comments_router.register(r'comments', views.CommentViewSet, basename='article-comments')

urlpatterns = [
    *articles_router.urls,
    *comments_router.urls
]
