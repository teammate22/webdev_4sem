from decimal import Decimal
from typing import Any

from rest_framework import serializers

from core.models import Driver, Order, Review, Tariff


class TariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор тарифа поездки.

    Args:
        serializers.ModelSerializer: Базовый сериализатор DRF.
    Returns:
        TariffSerializer: Экземпляр сериализатора тарифа.
    """

    class Meta:
        """
        Настройки сериализации тарифа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется DRF для настройки полей.
        """

        model = Tariff
        fields = [
            'id',
            'name',
            'price',
        ]


class DriverSerializer(serializers.ModelSerializer):
    """
    Сериализатор водителя.

    Args:
        serializers.ModelSerializer: Базовый сериализатор DRF.
    Returns:
        DriverSerializer: Экземпляр сериализатора водителя.
    """

    user_username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()

    class Meta:
        """
        Настройки сериализации водителя.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется DRF для настройки полей.
        """

        model = Driver
        fields = [
            'id',
            'user',
            'user_username',
            'full_name',
            'rating',
            'status',
            'profile_url',
            'created_at',
            'orders_count',
        ]

    def get_full_name(self, obj: Driver) -> str:
        """
        Возвращает полное имя водителя.

        Args:
            obj: Экземпляр водителя.
        Returns:
            str: Полное имя пользователя или username.
        """
        return obj.user.get_full_name() or obj.user.username

    def get_orders_count(self, obj: Driver) -> int:
        """
        Возвращает количество заказов водителя.

        Args:
            obj: Экземпляр водителя.
        Returns:
            int: Аннотированное или вычисленное количество заказов.
        """
        return getattr(obj, 'orders_count', obj.order_set.count())


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заказа.

    Args:
        serializers.ModelSerializer: Базовый сериализатор DRF.
    Returns:
        OrderSerializer: Экземпляр сериализатора заказа.
    """

    client_username = serializers.CharField(source='client.username', read_only=True)
    driver_name = serializers.SerializerMethodField()
    tariff_name = serializers.CharField(source='tariff.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    total_price = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        """
        Настройки сериализации заказа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется DRF для настройки полей.
        """

        model = Order
        fields = [
            'id',
            'client',
            'client_username',
            'driver',
            'driver_name',
            'tariff',
            'tariff_name',
            'status',
            'status_name',
            'from_address',
            'to_address',
            'price',
            'total_price',
            'is_owner',
            'created_at',
            'receipt',
        ]

    def get_driver_name(self, obj: Order) -> str | None:
        """
        Возвращает имя назначенного водителя.

        Args:
            obj: Экземпляр заказа.
        Returns:
            str | None: Имя водителя или None.
        """
        return str(obj.driver) if obj.driver else None

    def get_total_price(self, obj: Order) -> Decimal:
        """
        Возвращает итоговую стоимость заказа.

        Args:
            obj: Экземпляр заказа.
        Returns:
            Decimal: Стоимость заказа с учётом дополнительных услуг.
        """
        return obj.total_price()

    def get_is_owner(self, obj: Order) -> bool:
        """
        Проверяет, является ли текущий пользователь владельцем заказа.

        Args:
            obj: Экземпляр заказа.
        Returns:
            bool: True, если request.user является клиентом заказа.
        """
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False

        return obj.client_id == request.user.id

    def validate_price(self, value: Decimal) -> Decimal:
        """
        Проверяет, что цена заказа больше нуля.

        Args:
            value: Проверяемая стоимость заказа.
        Returns:
            Decimal: Валидная стоимость заказа.
        """
        if value <= 0:
            raise serializers.ValidationError('Цена должна быть больше 0.')

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет бизнес-правила заказа.

        Args:
            attrs: Валидируемые данные заказа.
        Returns:
            dict[str, Any]: Валидированные данные заказа.
        """
        driver = attrs.get('driver') or getattr(self.instance, 'driver', None)
        status = attrs.get('status') or getattr(self.instance, 'status', None)

        if driver and status and status.name == 'Выполняется':
            active_orders = Order.objects.filter(
                driver=driver,
                status__name='Выполняется',
            )

            if self.instance:
                active_orders = active_orders.exclude(pk=self.instance.pk)

            if active_orders.exists():
                raise serializers.ValidationError({
                    'driver': 'Водитель не может иметь более одного заказа со статусом "Выполняется".'
                })

        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзыва.

    Args:
        serializers.ModelSerializer: Базовый сериализатор DRF.
    Returns:
        ReviewSerializer: Экземпляр сериализатора отзыва.
    """

    order_title = serializers.SerializerMethodField()

    class Meta:
        """
        Настройки сериализации отзыва.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется DRF для настройки полей.
        """

        model = Review
        fields = [
            'id',
            'order',
            'order_title',
            'rating',
            'comment',
            'created_at',
        ]

    def get_order_title(self, obj: Review) -> str:
        """
        Возвращает краткое название заказа для отзыва.

        Args:
            obj: Экземпляр отзыва.
        Returns:
            str: Название заказа.
        """
        return f'Заказ №{obj.order_id}'
