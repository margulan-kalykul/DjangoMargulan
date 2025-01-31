"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from articles import views
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

articles_router = DefaultRouter()
articles_router.register(r'articles', views.ArticleViewSet, basename='articles')
# articles_router.register(r'articles/(?P<article_id>[^/.]+)/comments', views.CommentViewSet, basename='comments')
comments_router = NestedDefaultRouter(articles_router, r'articles', lookup='articles')
comments_router.register(r'comments', views.CommentViewSet, basename='article-comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest/', include('rest_framework.urls')),
    *articles_router.urls,
    *comments_router.urls,
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
] + debug_toolbar_urls()

# if not settings.TESTING:
#     urlpatterns = [
#         *urlpatterns,
#     ] + debug_toolbar_urls()

if settings.DEBUG:  # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
