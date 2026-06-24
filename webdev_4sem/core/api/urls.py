"""
Маршруты API приложения Ridee.

Args:
    None: Модуль не принимает аргументы.
Returns:
    list: URL-шаблоны DRF router.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DriverViewSet,
    OrderViewSet,
    ReviewViewSet,
    TariffViewSet,
    TestEmailAPIView,
    TestSentryAPIView,
)


app_name = 'api'

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('drivers', DriverViewSet, basename='drivers')
router.register('tariffs', TariffViewSet, basename='tariffs')
router.register('reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('test-email/', TestEmailAPIView.as_view(), name='test-email'),
    path('test-sentry/', TestSentryAPIView.as_view(), name='test-sentry'),
]

urlpatterns += router.urls
