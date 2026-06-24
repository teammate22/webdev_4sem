import django_filters

from core.models import Order


class OrderFilter(django_filters.FilterSet):
    """
    Набор фильтров для API заказов.

    Args:
        django_filters.FilterSet: Базовый класс фильтров django-filter.
    Returns:
        OrderFilter: Экземпляр фильтра заказов.
    """

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    tariff = django_filters.NumberFilter(field_name='tariff_id')
    status = django_filters.NumberFilter(field_name='status_id')
    client = django_filters.NumberFilter(field_name='client_id')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        """
        Настройки фильтра заказов.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется django-filter для настройки полей.
        """

        model = Order
        fields = [
            'min_price',
            'max_price',
            'tariff',
            'status',
            'client',
            'created_after',
            'created_before',
        ]
