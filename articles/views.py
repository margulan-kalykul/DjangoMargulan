from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from .models import Article, Tag
from .forms import ArticleForm
from django.db import connection
from .filters import ArticleFilter


@csrf_exempt
def createArticle(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        # Validate the form
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/articles/')
    else:
        form = ArticleForm()

    return render(
        request,
        "polls/index.html",
        {
            "form": form,
            "error": "Didn't complete the form"
        },
    )


def updateArticle(request, id):
    article = get_object_or_404(Article, pk=id)
    # print(article)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        # Validate the form
        # print(form)
        if form.is_valid():
            form.save()
            # print(form)
            return HttpResponseRedirect('/articles/')
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "polls/update.html",
        {
            "id": id,
            "form": form,
            "error": "Didn't complete the form"
        },
    )


def articleDetails(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except Http404 as e:
        return HttpResponse("404 article doesn't exist")
    return render(
        request,
        "polls/details.html",
        {
            "article": article
        },
    )


def articlesList(request):
    # TODO: Read about django n+1 problem
    # articles = Article.objects.prefetch_related('tags').all()
    filterset = ArticleFilter(request.GET, queryset=Article.objects.prefetch_related('tags').all())
    # print(articles.query)
    # print(connection.queries)
    context = {
        "filterset": filterset
    }
    html = render(
        request,
        "polls/articles.html",
        context
    )
    # print(connection.queries)
    # print(len(connection.queries))
    return html


def deleteArticle(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except Http404 as e:
        return HttpResponse("404 article doesn't exist")
    article.delete()
    return HttpResponseRedirect('/articles/')
        

@csrf_exempt
def deleteArticles(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")