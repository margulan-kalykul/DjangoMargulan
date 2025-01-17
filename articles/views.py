from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from .models import Article
from .forms import ArticleForm
from .filters import ArticleFilter


# Create a new article
@csrf_exempt
def createArticle(request):
    new_article: Article | None = None
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        # Validate the form
        if form.is_valid():
            form.save()
            print("It's actually created")
            return HttpResponseRedirect('/articles/')
    else:
        form = ArticleForm()

    print("It's None")
    return render(
        request,
        "polls/create.html",
        {
            "form": form,
            "error": "Didn't complete the form"
        },
    )


# Update article
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


# Show article details
def articleDetails(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except Http404:
        return HttpResponse("404 article doesn't exist")
    return render(
        request,
        "polls/details.html",
        {
            "article": article
        },
    )


# Show all articles
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


# Delete given article
def deleteArticle(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except Http404:
        return HttpResponse("404 article doesn't exist")
    article.delete()
    return HttpResponseRedirect('/articles/')
        

# Delete all articles
@csrf_exempt
def deleteArticles(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")