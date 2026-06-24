from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Driver, Order, OrderStatus, Tariff


class FilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_user = User.objects.create_user(username='client_user')
        cls.driver_user = User.objects.create_user(username='driver_user')
        cls.driver = Driver.objects.create(
            user=cls.driver_user,
            rating=4.8,
            status='Свободен',
        )
        cls.economy = Tariff.objects.create(
            name='Эконом',
            price=Decimal('250.00'),
        )
        cls.business = Tariff.objects.create(
            name='Бизнес',
            price=Decimal('800.00'),
        )
        cls.status = OrderStatus.objects.create(name='Создан')
        cls.cheap_order = Order.objects.create(
            client=cls.client_user,
            driver=cls.driver,
            tariff=cls.economy,
            status=cls.status,
            from_address='Тверская 1',
            to_address='Арбат 2',
            price=Decimal('400.00'),
        )
        cls.expensive_order = Order.objects.create(
            client=cls.client_user,
            driver=cls.driver,
            tariff=cls.business,
            status=cls.status,
            from_address='Садовая 3',
            to_address='ВДНХ',
            price=Decimal('1200.00'),
        )

    def test_order_filter_min_price(self):
        response = self.client.get('/api/orders/', {'min_price': '1000'})
        ids = [item['id'] for item in response.json()]

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expensive_order.id, ids)
        self.assertNotIn(self.cheap_order.id, ids)

    def test_order_filter_tariff(self):
        response = self.client.get('/api/orders/', {'tariff': self.economy.id})
        ids = [item['id'] for item in response.json()]

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.cheap_order.id, ids)
        self.assertNotIn(self.expensive_order.id, ids)
