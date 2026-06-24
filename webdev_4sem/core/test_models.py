from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Driver, Order, OrderStatus, Service, Tariff


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_user = User.objects.create_user(
            username='client_user',
            first_name='Иван',
            last_name='Петров',
        )
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
        cls.service_one = Service.objects.create(
            name='Багаж',
            price=Decimal('120.00'),
        )
        cls.service_two = Service.objects.create(
            name='Детское кресло',
            price=Decimal('100.00'),
        )

    def test_order_total_price_includes_services(self):
        order = Order.objects.create(
            client=self.client_user,
            driver=self.driver,
            tariff=self.tariff,
            status=self.done_status,
            from_address='Тверская 1',
            to_address='Арбат 2',
            price=Decimal('500.00'),
        )
        order.services.set([self.service_one, self.service_two])

        self.assertEqual(order.total_price(), Decimal('720.00'))

    def test_driver_str_returns_full_name(self):
        self.assertEqual(str(self.driver), 'Анна Федорова')

    def test_order_manager_active_returns_running_orders(self):
        active_order = Order.objects.create(
            client=self.client_user,
            driver=self.driver,
            tariff=self.tariff,
            status=self.active_status,
            from_address='Тверская 1',
            to_address='Арбат 2',
            price=Decimal('500.00'),
        )
        Order.objects.create(
            client=self.client_user,
            driver=self.driver,
            tariff=self.tariff,
            status=self.done_status,
            from_address='Садовая 3',
            to_address='ВДНХ',
            price=Decimal('700.00'),
        )

        self.assertQuerySetEqual(Order.objects.active(), [active_order])
