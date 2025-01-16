import django_filters
from .models import Tag
from django import forms

class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name', 
        to_field_name='name',
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        conjoined=True,
    )