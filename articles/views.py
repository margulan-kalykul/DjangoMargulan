from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser, MultiPartParser

from .models import Article
from .forms import ArticleForm
from .filters import ArticleFilter
from .serializers import ArticleSerializer


# Create a new article
@csrf_exempt
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        # Validate the form
        if form.is_valid():
            article = form.save()
            serializer = ArticleSerializer(article)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'indent': 4})

    form = ArticleForm()
    return render(
        request,
        "polls/create.html",
        {
            "form": form,
            "error": "Didn't complete the form"
        },
    )
# Show all articles
# @api_view(['GET'])
def articles_list(request):
    if request.method == "GET":
        articles = Article.objects.prefetch_related('tags').all()
        filterset = ArticleFilter(request.GET, queryset=articles)
        serializer = ArticleSerializer(filterset.queryset, many=True)
        return render(request, "polls/articles.html", {"filterset": filterset})
        # return JsonResponse(serializer.data, safe=False, json_dumps_params={'indent': 4})
    # TODO: Finish joining this with create method
    # if request.method == "POST":
    #     data = JSONParser().parse(request)
    #     serializer = ArticleSerializer(data=data)
    # context = {
    #     "filterset": filterset
    # }
    # html = render(
    #     request,
    #     "polls/articles.html",
    #     context
    # )
    # return html


# Show article details
def article_details(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return HttpResponse("404 article doesn't exist")
    return render(
        request,
        "polls/details.html",
        {
            "article": article
        },
    )

# Update article
def update_article(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return HttpResponse(status=404)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        # Validate the form
        if form.is_valid():
            article = form.save()
            return HttpResponseRedirect(reverse('articleList'))
    else:
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
def delete_article(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)
    except Http404:
        return HttpResponse("404 article doesn't exist")
    article.delete()
    return HttpResponseRedirect(reverse('articleList'))
        

# Delete all articles
@csrf_exempt
def delete_articles(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")