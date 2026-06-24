from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Avg, Sum


class Driver(models.Model):
    """
    Профиль водителя сервиса.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Driver: Экземпляр модели водителя.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    rating = models.FloatField(
        default=5.0,
        verbose_name="Рейтинг"
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Статус водителя"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    profile_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на профиль"
    )
    
    def is_new(self) -> bool:
      """
      Проверяет, был ли водитель создан за последние 7 дней.

      Args:
          self: Экземпляр водителя.
      Returns:
          bool: True, если водитель новый, иначе False.
      """
      return self.created_at >= timezone.now() - timezone.timedelta(days=7)

    class Meta:
        """
        Метаданные модели водителя.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Водитель"
        verbose_name_plural = "Водители"
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Возвращает человекочитаемое имя водителя.

        Args:
            self: Экземпляр водителя.
        Returns:
            str: Полное имя пользователя или username.
        """
        full_name = self.user.get_full_name()
        return full_name or self.user.username


class Car(models.Model):
    """
    Автомобиль, закреплённый за водителем.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Car: Экземпляр модели автомобиля.
    """

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        verbose_name="Водитель"
    )
    brand = models.CharField(
        max_length=100,
        verbose_name="Марка"
    )
    model = models.CharField(
        max_length=100,
        verbose_name="Модель"
    )
    number = models.CharField(
        max_length=20,
        verbose_name="Госномер"
    )
    color = models.CharField(
        max_length=50,
        verbose_name="Цвет"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        """
        Метаданные модели автомобиля.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self) -> str:
        """
        Возвращает название автомобиля с госномером.

        Args:
            self: Экземпляр автомобиля.
        Returns:
            str: Марка, модель и госномер автомобиля.
        """
        return f"{self.brand} {self.model} ({self.number})"


class Image(models.Model):
    """
    Изображение автомобиля.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Image: Экземпляр модели изображения.
    """

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        verbose_name="Автомобиль"
    )
    image = models.ImageField(
        upload_to="cars/",
        verbose_name="Изображение"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )

    class Meta:
        """
        Метаданные модели изображения.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        """
        Возвращает подпись изображения.

        Args:
            self: Экземпляр изображения.
        Returns:
            str: Текстовая подпись изображения автомобиля.
        """
        return f"Фото для {self.car}"


class Tariff(models.Model):
    """
    Тариф поездки.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Tariff: Экземпляр модели тарифа.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название тарифа"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена за поездку"
    )

    class Meta:
        """
        Метаданные модели тарифа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self) -> str:
        """
        Возвращает название тарифа.

        Args:
            self: Экземпляр тарифа.
        Returns:
            str: Название тарифа.
        """
        return self.name


class OrderStatus(models.Model):
    """
    Статус заказа.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        OrderStatus: Экземпляр модели статуса заказа.
    """

    name = models.CharField(
        max_length=50,
        verbose_name="Статус"
    )

    class Meta:
        """
        Метаданные модели статуса заказа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self) -> str:
        """
        Возвращает название статуса.

        Args:
            self: Экземпляр статуса.
        Returns:
            str: Название статуса заказа.
        """
        return self.name


class Service(models.Model):
    """
    Дополнительная услуга для заказа.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Service: Экземпляр модели услуги.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название услуги"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Цена"
    )

    class Meta:
        """
        Метаданные модели дополнительной услуги.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"

    def __str__(self) -> str:
        """
        Возвращает название услуги.

        Args:
            self: Экземпляр услуги.
        Returns:
            str: Название дополнительной услуги.
        """
        return self.name

# Создание модельного менеджера
class OrderManager(models.Manager):
    """
    Менеджер заказов с дополнительными QuerySet-методами.

    Args:
        models.Manager: Базовый менеджер Django.
    Returns:
        OrderManager: Экземпляр менеджера заказов.
    """

    def active(self) -> models.QuerySet:
        """
        Возвращает заказы со статусом "Выполняется".

        Args:
            self: Экземпляр менеджера.
        Returns:
            QuerySet: Активные заказы.
        """
        return self.filter(status__name="Выполняется")
    
class Order(models.Model):
    """
    Заказ поездки в сервисе Ridee.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Order: Экземпляр модели заказа.
    """

    objects = OrderManager()
    # Использование модельного менеджера (Order.objects.active())
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        # user = User.objects.get(username="ivan")
        # user_orders = user.orders.all() --- использование related_name для получения всех заказов клиента
        verbose_name="Клиент"
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Водитель"
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Тариф"
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Статус"
    )
    from_address = models.CharField(
        max_length=255,
        verbose_name="Адрес отправления"
    )
    to_address = models.CharField(
        max_length=255,
        verbose_name="Адрес назначения"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Стоимость"
    )
    services = models.ManyToManyField(
        Service,
        through='OrderService',
        verbose_name="Дополнительные услуги"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    receipt = models.FileField(
        upload_to='receipts/',
        null=True,
        blank=True,
        verbose_name='Файл чека'
    )

    def is_recent(self) -> bool:
      """
      Проверяет, был ли заказ создан за последние сутки.

      Args:
          self: Экземпляр заказа.
      Returns:
          bool: True, если заказ недавний, иначе False.
      """
      return self.created_at >= timezone.now() - timezone.timedelta(days=1)
    
    def get_absolute_url(self) -> str:
      """
      Возвращает URL детальной страницы заказа.

      Args:
          self: Экземпляр заказа.
      Returns:
          str: Абсолютный URL заказа внутри сайта.
      """
      return reverse('order_detail', args=[str(self.id)])

    def total_price(self) -> Decimal:
        """
        Считает итоговую стоимость заказа с учётом услуг.

        Args:
            self: Экземпляр заказа.
        Returns:
            Decimal: Стоимость заказа плюс сумма дополнительных услуг.
        """
        services_total = sum(service.price for service in self.services.all())
        return self.price + services_total
    
    class Meta:
        """
        Метаданные модели заказа.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Возвращает номер заказа.

        Args:
            self: Экземпляр заказа.
        Returns:
            str: Текстовое представление заказа.
        """
        return f"Заказ №{self.id}"


class OrderService(models.Model):
    """
    Связь заказа и дополнительной услуги.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        OrderService: Экземпляр связи заказа и услуги.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        """
        Метаданные связи заказа и услуги.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Услуга заказа"
        verbose_name_plural = "Услуги заказа"

    def __str__(self) -> str:
        """
        Возвращает описание услуги в заказе.

        Args:
            self: Экземпляр связи заказа и услуги.
        Returns:
            str: Заказ и связанная услуга.
        """
        return f"{self.order} — {self.service}"


class Payment(models.Model):
    """
    Оплата заказа.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Payment: Экземпляр модели оплаты.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ"
    )
    METHOD_CHOICES = [
      ('card', 'Банковская карта'),
      ('cash', 'Наличные'),
    ]
    STATUS_CHOICES = [
      ('pending', 'Ожидает'),
      ('paid', 'Оплачено'),
      ('canceled', 'Отменено'),
    ]
    method = models.CharField(
      max_length=50,
      choices=METHOD_CHOICES,
      verbose_name="Способ оплаты"
    )
    status = models.CharField(
      max_length=50,
      choices=STATUS_CHOICES,
      default='pending',
      verbose_name="Статус оплаты"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата оплаты"
    )
    def mark_as_paid(self) -> None:
      """
      Помечает оплату как выполненную и сохраняет дату оплаты.

      Args:
          self: Экземпляр оплаты.
      Returns:
          None: Метод изменяет и сохраняет текущий объект.
      """
      self.status = "paid"
      self.paid_at = timezone.now()
      self.save()

    class Meta:
        """
        Метаданные модели оплаты.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self) -> str:
        """
        Возвращает подпись оплаты.

        Args:
            self: Экземпляр оплаты.
        Returns:
            str: Текстовое представление оплаты.
        """
        return f"Оплата заказа №{self.order.id}"


class Review(models.Model):
    """
    Отзыв о заказе.

    Args:
        models.Model: Базовая модель Django.
    Returns:
        Review: Экземпляр модели отзыва.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ"
    )
    rating = models.IntegerField(
        verbose_name="Оценка"
    )
    comment = models.TextField(
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата отзыва"
    )

    class Meta:
        """
        Метаданные модели отзыва.

        Args:
            None: Класс настроек не принимает аргументы.
        Returns:
            None: Используется Django для настройки модели.
        """

        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Возвращает подпись отзыва.

        Args:
            self: Экземпляр отзыва.
        Returns:
            str: Текстовое представление отзыва.
        """
        return f"Отзыв к заказу №{self.order.id}"
