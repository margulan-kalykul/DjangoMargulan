from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from .models import Article, Tag

@csrf_exempt
def createArticle(request):
    try:
        title = request.POST["title"]
        author  = request.POST["author"]
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
        all_tags = [tag.tag for tag in Tag.objects.all()]
        all_tag_ids = [tag.id for tag in Tag.objects.all()]
        for tag in tags:
            if tag not in all_tags:
                new_tag = Tag.objects.create(tag=tag)
            else:
                for i in range(len(all_tags)):
                    if all_tags[i] == tag:
                        new_tag = Tag.objects.get(pk=all_tag_ids[i])
                        break
            new_tag.articles.add(new_article)

        context = {}
        return render(request, "polls/index.html", context)


@csrf_exempt
def deleteArticle(request):
    Article.objects.all().delete()
    return HttpResponse("Emptied")