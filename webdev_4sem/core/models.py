from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Avg, Sum


class Driver(models.Model):
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
    
    def is_new(self):
      return self.created_at >= timezone.now() - timezone.timedelta(days=7)

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.username


class Car(models.Model):
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
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.number})"


class Image(models.Model):
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
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return f"Фото для {self.car}"


class Tariff(models.Model):
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
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return self.name


class OrderStatus(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.name


class Service(models.Model):
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
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"

    def __str__(self):
        return self.name

# Создание модельного менеджера
class OrderManager(models.Manager):
    def active(self):
        return self.filter(status__name="Выполняется")
    
class Order(models.Model):
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

    def is_recent(self):
      return self.created_at >= timezone.now() - timezone.timedelta(days=1)
    
    def get_absolute_url(self):
      return reverse('order_detail', args=[str(self.id)])

    def total_price(self):
        services_total = sum(service.price for service in self.services.all())
        return self.price + services_total
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Услуга заказа"
        verbose_name_plural = "Услуги заказа"

    def __str__(self):
        return f"{self.order} — {self.service}"


class Payment(models.Model):
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
    def mark_as_paid(self):
      self.status = "paid"
      self.paid_at = timezone.now()
      self.save()

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self):
        return f"Оплата заказа №{self.order.id}"


class Review(models.Model):
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
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв к заказу №{self.order.id}"
