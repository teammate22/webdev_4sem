from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from core.models import (
    Car,
    Driver,
    Image,
    Order,
    OrderService,
    OrderStatus,
    Payment,
    Review,
    Service,
    Tariff,
)
from core.tasks import recalculate_driver_ratings


class Command(BaseCommand):
    """
    Наполняет базу демонстрационными данными Ridee.

    Args:
        BaseCommand: Базовая команда Django.
    Returns:
        Command: Команда для создания демо-данных.
    """

    help = 'Создаёт демонстрационные данные для защиты проекта Ridee.'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Добавляет аргументы команды.

        Args:
            parser: Парсер аргументов management command.
        Returns:
            None: Метод настраивает parser.
        """
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие демо-данные перед созданием новых.',
        )

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        """
        Создаёт пользователей, водителей, заказы, оплаты и отзывы.

        Args:
            *args: Позиционные аргументы команды.
            **options: Опции команды.
        Returns:
            None: Метод изменяет базу данных.
        """
        if options.get('reset'):
            self._reset_demo_data()

        statuses = self._create_statuses()
        tariffs = self._create_tariffs()
        services = self._create_services()
        clients = self._create_clients()
        drivers = self._create_drivers()
        orders = self._create_orders(
            clients=clients,
            drivers=drivers,
            tariffs=tariffs,
            statuses=statuses,
        )
        self._attach_services(orders=orders, services=services)
        self._create_payments(orders=orders)
        self._create_reviews(orders=orders)
        rating_result = recalculate_driver_ratings()

        self.stdout.write(self.style.SUCCESS(
            'Демо-данные готовы: '
            f'клиентов={len(clients)}, '
            f'водителей={len(drivers)}, '
            f'заказов={len(orders)}, '
            f'пересчёт рейтингов={rating_result}.'
        ))

    def _reset_demo_data(self) -> None:
        """
        Удаляет данные, созданные командой ранее.

        Args:
            self: Экземпляр команды.
        Returns:
            None: Метод очищает демо-данные.
        """
        User.objects.filter(username__startswith='demo_').delete()
        Tariff.objects.filter(name__in=self._tariff_names()).delete()
        Service.objects.filter(name__in=self._service_names()).delete()
        OrderStatus.objects.filter(name__in=self._status_names()).delete()

    def _create_statuses(self) -> dict[str, OrderStatus]:
        """
        Создаёт статусы заказов.

        Args:
            self: Экземпляр команды.
        Returns:
            dict[str, OrderStatus]: Статусы по названию.
        """
        return {
            name: OrderStatus.objects.get_or_create(name=name)[0]
            for name in self._status_names()
        }

    def _create_tariffs(self) -> list[Tariff]:
        """
        Создаёт тарифы поездок.

        Args:
            self: Экземпляр команды.
        Returns:
            list[Tariff]: Список тарифов.
        """
        prices = [
            Decimal('290.00'),
            Decimal('430.00'),
            Decimal('650.00'),
            Decimal('950.00'),
            Decimal('1250.00'),
        ]

        return [
            Tariff.objects.update_or_create(
                name=name,
                defaults={'price': prices[index]},
            )[0]
            for index, name in enumerate(self._tariff_names())
        ]

    def _create_services(self) -> list[Service]:
        """
        Создаёт дополнительные услуги.

        Args:
            self: Экземпляр команды.
        Returns:
            list[Service]: Список услуг.
        """
        return [
            Service.objects.update_or_create(
                name=name,
                defaults={'price': Decimal(str(80 + index * 35))},
            )[0]
            for index, name in enumerate(self._service_names())
        ]

    def _create_clients(self) -> list[User]:
        """
        Создаёт клиентов.

        Args:
            self: Экземпляр команды.
        Returns:
            list[User]: Список пользователей-клиентов.
        """
        names = [
            ('ivan_sokolov', 'Иван', 'Соколов'),
            ('maria_volkova', 'Мария', 'Волкова'),
            ('pavel_orlov', 'Павел', 'Орлов'),
            ('elena_morozova', 'Елена', 'Морозова'),
            ('dmitry_ivanov', 'Дмитрий', 'Иванов'),
            ('olga_nikolaeva', 'Ольга', 'Николаева'),
            ('kirill_frolov', 'Кирилл', 'Фролов'),
            ('anna_belova', 'Анна', 'Белова'),
            ('sergey_makarov', 'Сергей', 'Макаров'),
            ('natalia_krylova', 'Наталья', 'Крылова'),
        ]

        return [
            User.objects.update_or_create(
                username=f'demo_client_{username}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@example.com',
                },
            )[0]
            for username, first_name, last_name in names
        ]

    def _create_drivers(self) -> list[Driver]:
        """
        Создаёт водителей и автомобили.

        Args:
            self: Экземпляр команды.
        Returns:
            list[Driver]: Список водителей.
        """
        names = [
            ('alex_petrov', 'Алексей', 'Петров', 'Свободен', 'Toyota', 'Camry'),
            ('denis_egorov', 'Денис', 'Егоров', 'Свободен', 'Kia', 'K5'),
            ('roman_smirnov', 'Роман', 'Смирнов', 'На линии', 'Hyundai', 'Solaris'),
            ('maxim_kuzmin', 'Максим', 'Кузьмин', 'Свободен', 'Skoda', 'Octavia'),
            ('artem_lebedev', 'Артём', 'Лебедев', 'Занят', 'Volkswagen', 'Polo'),
            ('nikita_antonov', 'Никита', 'Антонов', 'На линии', 'Nissan', 'Teana'),
            ('igor_titov', 'Игорь', 'Титов', 'Свободен', 'Renault', 'Logan'),
            ('vadim_gusev', 'Вадим', 'Гусев', 'Занят', 'Mercedes-Benz', 'E-Class'),
            ('stepan_borisov', 'Степан', 'Борисов', 'На линии', 'BMW', '5 Series'),
            ('oleg_fedorov', 'Олег', 'Фёдоров', 'Свободен', 'Geely', 'Coolray'),
        ]

        drivers = []

        for index, (username, first_name, last_name, status, brand, model) in enumerate(names, start=1):
            user = User.objects.update_or_create(
                username=f'demo_driver_{username}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@example.com',
                },
            )[0]
            driver = Driver.objects.update_or_create(
                user=user,
                defaults={
                    'rating': 5.0,
                    'status': status,
                    'profile_url': f'https://ridee.local/drivers/{index}/',
                },
            )[0]
            car = Car.objects.update_or_create(
                driver=driver,
                defaults={
                    'brand': brand,
                    'model': model,
                    'number': f'А{100 + index}АА777',
                    'color': ['Чёрный', 'Белый', 'Серый', 'Синий'][index % 4],
                },
            )[0]
            Image.objects.update_or_create(
                car=car,
                defaults={'image': f'cars/demo_car_{index}.jpg'},
            )
            drivers.append(driver)

        return drivers

    def _create_orders(
        self,
        clients: list[User],
        drivers: list[Driver],
        tariffs: list[Tariff],
        statuses: dict[str, OrderStatus],
    ) -> list[Order]:
        """
        Создаёт заказы.

        Args:
            clients: Пользователи-клиенты.
            drivers: Водители.
            tariffs: Тарифы.
            statuses: Статусы заказов.
        Returns:
            list[Order]: Список заказов.
        """
        routes = [
            ('Тверская улица, 1', 'Арбат, 12'),
            ('Казанский вокзал', 'ВДНХ'),
            ('Парк Горького', 'Москва-Сити'),
            ('Сокол', 'Китай-город'),
            ('Белорусский вокзал', 'Лужники'),
            ('Охотный ряд', 'Павелецкая'),
            ('Курская', 'Савёловская'),
            ('Таганская', 'Парк Победы'),
            ('Комсомольская площадь', 'Сретенка'),
            ('Проспект Мира', 'Бауманская'),
            ('Новослободская', 'Красные ворота'),
            ('Щукинская', 'Динамо'),
            ('Аэропорт', 'Речной вокзал'),
            ('Университет', 'Киевская'),
            ('Тульская', 'Коломенская'),
            ('Митино', 'Строгино'),
            ('Ясенево', 'Калужская'),
            ('Преображенская площадь', 'Черкизовская'),
            ('Планерная', 'Химки'),
            ('Люблино', 'Марьино'),
        ]
        status_cycle = [
            'Выполнен',
            'Создан',
            'Выполнен',
            'Отменён',
            'Выполнен',
            'Ожидает водителя',
        ]
        orders = []

        for index, (from_address, to_address) in enumerate(routes, start=1):
            order = Order.objects.update_or_create(
                from_address=from_address,
                to_address=to_address,
                defaults={
                    'client': clients[(index - 1) % len(clients)],
                    'driver': drivers[(index - 1) % len(drivers)],
                    'tariff': tariffs[(index - 1) % len(tariffs)],
                    'status': statuses[status_cycle[(index - 1) % len(status_cycle)]],
                    'price': Decimal(str(450 + index * 95)),
                },
            )[0]
            orders.append(order)

        return orders

    def _attach_services(self, orders: list[Order], services: list[Service]) -> None:
        """
        Добавляет к заказам дополнительные услуги.

        Args:
            orders: Список заказов.
            services: Список услуг.
        Returns:
            None: Метод создаёт связи заказов и услуг.
        """
        for index, order in enumerate(orders):
            OrderService.objects.get_or_create(
                order=order,
                service=services[index % len(services)],
            )
            if index % 3 == 0:
                OrderService.objects.get_or_create(
                    order=order,
                    service=services[(index + 2) % len(services)],
                )

    def _create_payments(self, orders: list[Order]) -> None:
        """
        Создаёт оплаты заказов.

        Args:
            orders: Список заказов.
        Returns:
            None: Метод создаёт оплаты.
        """
        for index, order in enumerate(orders):
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'method': 'card' if index % 2 == 0 else 'cash',
                    'status': 'paid' if order.status and order.status.name == 'Выполнен' else 'pending',
                },
            )

    def _create_reviews(self, orders: list[Order]) -> None:
        """
        Создаёт отзывы для выполненных заказов.

        Args:
            orders: Список заказов.
        Returns:
            None: Метод создаёт отзывы.
        """
        comments = [
            'Водитель приехал быстро, поездка прошла комфортно.',
            'Чистый автомобиль и аккуратное вождение.',
            'Маршрут выбран удачно, всё понравилось.',
            'Хороший сервис, буду пользоваться ещё.',
            'Вежливый водитель и приятная поездка.',
        ]

        for index, order in enumerate(orders):
            if not order.status or order.status.name != 'Выполнен':
                continue

            Review.objects.update_or_create(
                order=order,
                defaults={
                    'rating': 4 + (index % 2),
                    'comment': comments[index % len(comments)],
                },
            )

    def _status_names(self) -> list[str]:
        """
        Возвращает названия статусов.

        Args:
            self: Экземпляр команды.
        Returns:
            list[str]: Названия статусов.
        """
        return [
            'Создан',
            'Ожидает водителя',
            'Выполняется',
            'Выполнен',
            'Отменён',
        ]

    def _tariff_names(self) -> list[str]:
        """
        Возвращает названия тарифов.

        Args:
            self: Экземпляр команды.
        Returns:
            list[str]: Названия тарифов.
        """
        return ['Эконом', 'Комфорт', 'Комфорт+', 'Бизнес', 'Минивэн']

    def _service_names(self) -> list[str]:
        """
        Возвращает названия услуг.

        Args:
            self: Экземпляр команды.
        Returns:
            list[str]: Названия услуг.
        """
        return [
            'Детское кресло',
            'Багаж',
            'Перевозка животного',
            'Встреча с табличкой',
            'Тихая поездка',
            'Помощь с багажом',
            'Кондиционер',
            'Зарядка для телефона',
            'Бизнес-подача',
            'Ожидание 15 минут',
        ]
