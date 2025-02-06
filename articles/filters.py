import django_filters
from .models import Tag, Article
from django import forms
from django.db.models import Q


class ArticleFilter(django_filters.FilterSet):
    # Filter by title if it contains the given string, case-insensitive
    title = django_filters.CharFilter(lookup_expr='icontains')

    # Choose what tags the articles should have
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__id',
        to_field_name='id',
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        # conjoined=True,
    )

    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')

    # search = django_filters.CharFilter(method='author_title_filter', label='General search')

    # def author_title_filter(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(title__icontains=value) |
    #         Q(author__username__icontains=value)
    #     )
    
    # Check the box to show only NEW and ACCEPTED articles
    status_showable = django_filters.BooleanFilter(
        field_name='status',
        method='status_filter',
        # widget=forms.CheckboxInput,
    )

    def status_filter(self, queryset, name, value):
        if value:
            return queryset.filter(status__in=[Article.Status.NEW, Article.Status.ACCEPTED])
        return queryset
    
    class Meta:
        model = Article
        fields = ['status_showable']
        # fields = ['status_showable', 'search']
