from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Article, Tag
from .forms import ArticleForm
from django.db import connection


@csrf_exempt
def createArticle(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        # Validate the form
        if form.is_valid():
            form.save()
            # title = form.cleaned_data["title"]
            # author = form.cleaned_data["author"]
            # text = form.cleaned_data["text"]
            # tags = form.cleaned_data["tags"]

            # new_article = Article.objects.create(title=title, author=author, text=text)
            # for tag in tags:
            #     new_tag = Tag.objects.get_or_create(name=tag)[0]
            #     new_tag.articles.add(new_article)

            return HttpResponse("Thank you for submitting the form")
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


def articlesList(request):
    articles = Article.objects.prefetch_related('tags').all()
    print(articles.query)
    print(connection.queries)
    context = {
        "articles": articles,
    }
    html = render(
        request,
        "polls/articles.html",
        context
    )
    print(connection.queries)
    print(len(connection.queries))
    return html
        

@csrf_exempt
def deleteArticle(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")