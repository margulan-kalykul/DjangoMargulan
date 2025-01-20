from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article
from .forms import ArticleForm
from .filters import ArticleFilter
from .serializers import ArticleSerializer, ArticleCreationSerializer


# Form to create a new article and list of all articles
class ArticlesList(generics.GenericAPIView,
                   mixins.ListModelMixin):
    queryset = Article.objects.prefetch_related('tags').all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    # TODO: Resolve creation problem
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
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter

    def get_article(pk):
        try:
            return get_object_or_404(Article, pk=pk)
        except Http404:
            raise Http404

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def post(self, request, pk):
        article = self.get_article(pk)
        serializer = ArticleCreationSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)
