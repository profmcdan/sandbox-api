from datetime import datetime, time

import django_filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class DateFilter(django_filters.FilterSet):
    start = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    end = django_filters.DateFilter(field_name="created_at", method="filter_end")

    def __init__(self, start_field="created_at", end_field="created_at", **kwargs):
        super().__init__(**kwargs)
        self.start = django_filters.DateFilter(
            field_name=start_field, lookup_expr="gte"
        )
        self.end = django_filters.DateFilter(field_name=end_field, method="filter_end")

    def filter_end(self, queryset, name, value):
        end_date = datetime.combine(value, time.max)
        f = {f"{name}__lte": end_date}
        return queryset.filter(**f)


# reusable list of query parameters for dashboards / stats
DATE_RANGE_AND_CURRENCY_PARAMS = [
    OpenApiParameter(
        name="start",
        description="Start date (YYYY-MM-DD)",
        type=OpenApiTypes.DATE,
        required=False,
    ),
    OpenApiParameter(
        name="end",
        description="End date (YYYY-MM-DD)",
        type=OpenApiTypes.DATE,
        required=False,
    ),
    OpenApiParameter(
        name="currency",
        description="Currency ID",
        type=str,
        required=False,
    ),
]

# Extended version including optional "year"
DATE_RANGE_CURRENCY_YEAR_PARAMS = DATE_RANGE_AND_CURRENCY_PARAMS + [
    OpenApiParameter(
        name="year",
        description="Year for filtering (YYYY)",
        type=OpenApiTypes.STR,  # can also use OpenApiTypes.INT
        required=False,
    ),
]

SUB_ACCOUNT_STATS_PARAMS = DATE_RANGE_CURRENCY_YEAR_PARAMS + [
    OpenApiParameter(
        name="is_branch",
        description="For branch or non branch wallet",
        type=OpenApiTypes.BOOL,  # can also use OpenApiTypes.INT
        required=False,
    ),
]
