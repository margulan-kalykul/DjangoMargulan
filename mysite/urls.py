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
from django.urls import path
from articles import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/', views.createArticle, name="create"),
    path('deleteArticle/<int:id>/', views.deleteArticle, name="deleteArticle"),
    path('delete/', views.deleteArticles, name="delete"),
    path('update/<int:id>/', views.updateArticle, name="update"),
    path('article/<int:id>', views.articleDetails, name="article"),
    path('articles/', views.articlesList, name="articleList"),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:  # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
