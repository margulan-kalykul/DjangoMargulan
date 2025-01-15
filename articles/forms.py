from django import forms
from .models import Tag

class ArticleForm(forms.Form):
    title = forms.CharField(max_length=200)
    text = forms.CharField()
    author = forms.CharField(max_length=100)
    tags = forms.ChoiceField(choices=[])
    # image = forms.ImageField(default="https://freesvg.org/img/Website-No-Image-Icon.png")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = [(tag.id, tag.name) for tag in Tag.objects.all()]