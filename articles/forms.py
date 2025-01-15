from django import forms
from .models import Article, Tag

class ArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use a checkbox for selecting multiple tags
        required=False)
    class Meta:
        model = Article
        fields = '__all__'
    # title = forms.CharField(max_length=200)
    # text = forms.CharField()
    # author = forms.CharField(max_length=100)
    # image = forms.ImageField()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["tags"].queryset = Tag.objects.all()