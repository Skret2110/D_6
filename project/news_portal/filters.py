import django_filters
from django.forms import DateInput
from django_filters import FilterSet, NumberFilter
from .models import News


class NewsFilter(FilterSet):
    #date = NumberFilter(field_name='publish', lookup_expr='lte')

    class Meta:
        model = News
        #publish.lookup_expr='lt'

        fields = {
            'name': ['exact'],
            #'publish': ['lt'],
            'post': ['exact'],
            'description': ['exact'],
        }

    date = django_filters.DateFilter(
        field_name="publish",
        lookup_expr='lte',
        label='Date',
        widget=DateInput(attrs={'type': 'date'},),

    )

