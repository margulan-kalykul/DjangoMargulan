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
@api_view(['GET', ])
def article_details(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        # return render(
        #     request,
        #     "polls/details.html",
        #     {
        #         "article": article
        #     },
        # )
        return Response(serializer.data)


# Update article
@api_view(['GET', 'POST'])
def update_article(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        # Validate the form
        if form.is_valid():
            article = form.save()
            return HttpResponseRedirect(reverse('articles'))
    elif request.method == 'GET':
        form = ArticleForm(instance=article)
        serializer = ArticleSerializer(article)
        return render(
            request,
            "polls/update.html",
            {
                "pk": pk,
                "form": form,
                "error": "Didn't complete the form"
            },
        )


# Delete given article
@api_view(['DELETE'])
def delete_article(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return Response(status=status.HTTP_404_NOT_FOUND)

    article.delete()
    return HttpResponseRedirect(reverse('articles'))
        

# Delete all articles
@api_view(['DELETE'])
def delete_articles(request):
    Article.objects.all().delete()
    return Response({"message": "All articles are deleted"})
