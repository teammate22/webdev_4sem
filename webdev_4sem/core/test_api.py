from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count
from django.test import TestCase

from core.api.serializers import DriverSerializer, OrderSerializer
from core.models import Driver, Order, OrderStatus, Tariff


class APITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_user = User.objects.create_user(username='client_user')
        cls.driver_user = User.objects.create_user(
            username='driver_user',
            first_name='Анна',
            last_name='Федорова',
        )
        cls.driver = Driver.objects.create(
            user=cls.driver_user,
            rating=4.8,
            status='Свободен',
        )
        cls.tariff = Tariff.objects.create(
            name='Комфорт',
            price=Decimal('400.00'),
        )
        cls.active_status = OrderStatus.objects.create(name='Выполняется')
        cls.done_status = OrderStatus.objects.create(name='Выполнен')
        cls.order = Order.objects.create(
            client=cls.client_user,
            driver=cls.driver,
            tariff=cls.tariff,
            status=cls.done_status,
            from_address='Тверская 1',
            to_address='Арбат 2',
            price=Decimal('500.00'),
        )

    def test_order_serializer_validate_price_rejects_zero(self):
        serializer = OrderSerializer(
            instance=self.order,
            data={'price': 0},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_order_serializer_rejects_second_active_order_for_driver(self):
        Order.objects.create(
            client=self.client_user,
            driver=self.driver,
            tariff=self.tariff,
            status=self.active_status,
            from_address='Пушкинская 1',
            to_address='Киевский вокзал',
            price=Decimal('600.00'),
        )
        serializer = OrderSerializer(data={
            'client': self.client_user.id,
            'driver': self.driver.id,
            'tariff': self.tariff.id,
            'status': self.active_status.id,
            'from_address': 'Садовая 3',
            'to_address': 'ВДНХ',
            'price': '700.00',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('driver', serializer.errors)

    def test_orders_list_api_returns_success(self):
        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, 200)

    def test_order_detail_api_returns_success(self):
        response = self.client.get(f'/api/orders/{self.order.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.order.id)

    def test_driver_serializer_orders_count_uses_annotation(self):
        driver = Driver.objects.annotate(
            orders_count=Count('order'),
        ).get(pk=self.driver.pk)
        data = DriverSerializer(driver).data

        self.assertEqual(data['orders_count'], 1)
