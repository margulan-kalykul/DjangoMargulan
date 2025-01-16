from django import forms
from .models import Article, Tag

class ArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use a checkbox for selecting multiple tags
        required=False)
    
    class Meta:
        model = Article
        fields = ['title', 'text', 'author', 'tags', 'image']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["tags"].queryset = Tag.objects.all()