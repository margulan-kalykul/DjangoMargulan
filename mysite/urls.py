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
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles import views
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

# router = DefaultRouter()
# router.register(r'articles_test', views.ArticleViewSet, basename='articles_test')

urlpatterns = [
    path('articles/', views.ArticlesList.as_view(), name="articles"),
    path('articles/<int:pk>/', views.ArticleDetail.as_view(), name="article"),
    # Comment list
    path('articles/<int:article_id>/comments/', views.CommentList.as_view(), name="comments"),
    path('articles/<int:article_id>/comments/<int:comment_id>/', views.CommentDetails.as_view(), name="comment"),
    # path('comments/<int:pk>/', views.CommentDetails.as_view(), name="comment"),
    path('admin/', admin.site.urls),
    path('rest/', include('rest_framework.urls')),
] + debug_toolbar_urls()

# urlpatterns = router.urls + debug_toolbar_urls()

# if not settings.TESTING:
#     urlpatterns = [
#         *urlpatterns,
#     ] + debug_toolbar_urls()

if settings.DEBUG:  # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
