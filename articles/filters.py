import django_filters
from .models import Tag, Article
from django import forms

class ArticleFilter(django_filters.FilterSet):
    # Filter by title if it contains the given string, case insensitive
    title = django_filters.CharFilter(lookup_expr='icontains')
    # Choos what tags the articles should have
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name', 
        to_field_name='name',
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        conjoined=True,
    )
    # Check the box to show only NEW and ACCEPTED articles
    status_showable = django_filters.CharFilter(
        field_name='status',
        method='status_filter',
        widget=forms.CheckboxInput,
    )

    def status_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'in'])
        if (value == 'True'):
            return queryset.filter(**{lookup: [Article.Status.NEW, Article.Status.ACCEPTED]})
        return queryset
    
    class Meta:
        model = Article
        fields = ['status_showable']