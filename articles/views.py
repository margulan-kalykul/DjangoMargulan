from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from .models import Article, Tag

@csrf_exempt
def createArticle(request):
    try:
        title = request.POST["title"]
        author = request.POST["author"]
        text = request.POST["article"]
        tags = request.POST["tags"].split(sep=' ')
    except:
        return render(
            request,
            "polls/index.html",
            {
                "error": "Didn't complete the form"
            },
        )
    else:
        new_article = Article.objects.create(title=title, author=author, text=text)
        
        for tag in tags:
            new_tag = Tag.objects.get_or_create(name=tag)[0]
            new_tag.articles.add(new_article)

        context = {}
        return render(request, "polls/index.html", context)


@csrf_exempt
def deleteArticle(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")