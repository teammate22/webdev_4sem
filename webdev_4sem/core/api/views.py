from django.conf import settings
from django.db.models import Count, QuerySet
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.models import Driver, Order, Review, Tariff

from .filters import OrderFilter
from .serializers import (
    DriverSerializer,
    OrderSerializer,
    ReviewSerializer,
    TariffSerializer,
)


class OrderViewSet(ReadOnlyModelViewSet):
    """
    Read-only API для заказов.

    Args:
        ReadOnlyModelViewSet: Базовый read-only ViewSet DRF.
    Returns:
        OrderViewSet: Экземпляр ViewSet для заказов.
    """

    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_serializer_context(self) -> dict[str, object]:
        """
        Передаёт request в context сериализатора.

        Args:
            self: Экземпляр ViewSet.
        Returns:
            dict[str, object]: Контекст сериализатора.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self) -> QuerySet:
        """
        Возвращает оптимизированный QuerySet заказов.

        Args:
            self: Экземпляр ViewSet.
        Returns:
            QuerySet: Заказы со связанными объектами.
        """
        return Order.objects.select_related(
            'client',
            'driver',
            'tariff',
            'status',
        ).prefetch_related(
            'services',
        ).order_by('-created_at')


class DriverViewSet(ReadOnlyModelViewSet):
    """
    Read-only API для водителей.

    Args:
        ReadOnlyModelViewSet: Базовый read-only ViewSet DRF.
    Returns:
        DriverViewSet: Экземпляр ViewSet для водителей.
    """

    serializer_class = DriverSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает водителей с количеством заказов.

        Args:
            self: Экземпляр ViewSet.
        Returns:
            QuerySet: Водители с аннотированным orders_count.
        """
        return Driver.objects.select_related(
            'user',
        ).annotate(
            orders_count=Count('order'),
        ).order_by('-rating', '-orders_count')


class TariffViewSet(ReadOnlyModelViewSet):
    """
    Read-only API для тарифов.

    Args:
        ReadOnlyModelViewSet: Базовый read-only ViewSet DRF.
    Returns:
        TariffViewSet: Экземпляр ViewSet для тарифов.
    """

    serializer_class = TariffSerializer
    queryset = Tariff.objects.order_by('price', 'name')


class ReviewViewSet(ReadOnlyModelViewSet):
    """
    Read-only API для отзывов.

    Args:
        ReadOnlyModelViewSet: Базовый read-only ViewSet DRF.
    Returns:
        ReviewViewSet: Экземпляр ViewSet для отзывов.
    """

    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related(
        'order',
    ).order_by('-created_at')


class TestSentryAPIView(APIView):
    """
    Тестовый endpoint для проверки отправки ошибок в Sentry.

    Args:
        APIView: Базовый класс DRF для API-представлений.
    Returns:
        TestSentryAPIView: Представление, которое выбрасывает исключение.
    """

    def get(
        self,
        request: Request,
        *args: object,
        **kwargs: object,
    ) -> None:
        """
        Выбрасывает тестовое исключение для Sentry.

        Args:
            request: HTTP-запрос DRF.
            *args: Позиционные аргументы маршрута.
            **kwargs: Именованные аргументы маршрута.
        Returns:
            None: Метод всегда завершается исключением.
        """
        raise RuntimeError('Test Sentry exception from Ridee API.')


class TestEmailAPIView(APIView):
    """
    Тестовый endpoint для проверки отправки email через Mailhog.

    Args:
        APIView: Базовый класс DRF для API-представлений.
    Returns:
        TestEmailAPIView: Представление для отправки тестового письма.
    """

    def get(
        self,
        request: Request,
        *args: object,
        **kwargs: object,
    ) -> Response:
        """
        Отправляет тестовое письмо через настроенный SMTP backend.

        Args:
            request: HTTP-запрос DRF.
            *args: Позиционные аргументы маршрута.
            **kwargs: Именованные аргументы маршрута.
        Returns:
            Response: JSON-ответ с количеством отправленных писем.
        """
        sent_count = send_mail(
            subject='Тестовое письмо Ridee',
            message='Это тестовое письмо отправлено из Django через Mailhog.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['student@example.com'],
            fail_silently=False,
        )

        return Response(
            {
                'status': 'ok',
                'sent_count': sent_count,
                'detail': 'Тестовое письмо отправлено в Mailhog.',
            }
        )
