from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Order, Driver, Service, Tariff
from django.db.models import Count, Avg, Sum, Q
from .forms import OrderForm
from django.core.cache import cache
from django.db.models import F
from reportlab.pdfgen import canvas
from django.http import HttpRequest, HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# contains/icontains
def search_orders(request: HttpRequest) -> HttpResponse:
    """
    Ищет заказы по адресу отправления.

    Args:
        request: HTTP-запрос с GET-параметром q.
    Returns:
        HttpResponse: Страница со списком найденных заказов.
    """

    query = request.GET.get('q')

    orders = Order.objects.all()

    if query:
        orders = orders.filter(from_address__icontains=query)

    return render(request, 'orders_list.html', {'orders': orders})
    # Order.objects.filter(from_address__contains="Москва") - поиск по точному совпадению
    # Order.objects.filter(from_address__icontains="москва") - поиск без учёта регистра

# values() и values_list()
def orders_values(request: HttpRequest) -> HttpResponse:
    """
    Демонстрирует получение словарей через values().

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Тестовая страница с данными заказов.
    """

    data = Order.objects.values('id', 'price')

    return render(request, 'test.html', {'data': data})

def orders_values_list(request: HttpRequest) -> HttpResponse:
    """
    Демонстрирует получение кортежей через values_list().

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Тестовая страница с данными заказов.
    """

    data = Order.objects.values_list('id', 'price')

    return render(request, 'test.html', {'data': data})

# count(), exists(), update(), delete()
def test_queries(request: HttpRequest) -> HttpResponse:
    """
    Показывает безопасные тестовые ORM-запросы.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Тестовая страница с количеством заказов.
    """

    count = Order.objects.count()

    exists = Order.objects.exists()

    cheap_orders_count = Order.objects.filter(price__lt=100).count()

    very_cheap_orders_count = Order.objects.filter(price__lt=50).count()

    return render(request, 'test.html', {
        'count': count,
        'exists': exists,
        'cheap_orders_count': cheap_orders_count,
        'very_cheap_orders_count': very_cheap_orders_count,
    })

# кеширование данных
def orders_cached(request: HttpRequest) -> HttpResponse:
    """
    Возвращает список заказов с использованием локального кеша.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница со списком заказов.
    """
    orders = cache.get('orders_list')

    if not orders:
        orders = list(Order.objects.all())  # QuerySet превращаем в list
        cache.set('orders_list', orders, 60)  # сохраняем в кеш на 60 секунд

    return render(request, 'orders_list.html', {'orders': orders})

# F-выражение
def increase_driver_rating(request: HttpRequest, driver_id: int) -> HttpResponse:
    """
    Увеличивает рейтинг водителя через F-выражение.

    Args:
        request: HTTP-запрос пользователя.
        driver_id: Идентификатор водителя.
    Returns:
        HttpResponse: Редирект на список водителей.
    """
    Driver.objects.filter(id=driver_id).update(rating=F('rating') + 1)
    return redirect('drivers_list')

def user_orders_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """
    Показывает заказы конкретного пользователя.

    Args:
        request: HTTP-запрос пользователя.
        user_id: Идентификатор пользователя.
    Returns:
        HttpResponse: Страница с заказами пользователя.
    """
    user = get_object_or_404(User, id=user_id)

    # related_name использование
    orders = user.orders.all()

    return render(request, 'orders.html', {'orders': orders})


def filtered_orders_view(request: HttpRequest) -> HttpResponse:
    """
    Демонстрирует фильтрацию, исключение и сортировку заказов.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница с отфильтрованными заказами.
    """

    # lookup-выражение (пример использования __)
    orders = Order.objects.filter(price__gt=1000)

    # фильтрация по связанному полю (пример использования __)
    Order.objects.filter(driver__user__username="alex")

    # exclude()
    orders = orders.exclude(status__name="Отменён")

    # order_by()
    orders = orders.order_by('-price')

    return render(request, 'orders.html', {'orders': orders})

def aggregation_view(request: HttpRequest) -> HttpResponse:
    """
    Демонстрирует агрегатные запросы по водителям и заказам.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница со статистикой.
    """

    # 1. Количество заказов у водителей
    drivers = Driver.objects.annotate(order_count=Count('order'))

    # 2. Средний рейтинг
    avg_rating = Driver.objects.aggregate(avg_rating=Avg('rating'))

    # 3. Сумма заказов по водителю
    drivers_income = Driver.objects.annotate(
        total_income=Sum('order__price')
    )

    return render(request, 'stats.html', {
        'drivers': drivers,
        'avg_rating': avg_rating,
        'drivers_income': drivers_income
    })

# CRUD операции для модели Order
def orders_list(request: HttpRequest) -> HttpResponse:
    """
    Показывает список заказов и выполняет поиск по связанным данным.

    Args:
        request: HTTP-запрос с необязательным GET-параметром q.
    Returns:
        HttpResponse: Страница списка заказов.
    """

    query = request.GET.get('q', '').strip()

    orders = Order.objects.select_related(
        'client',
        'driver',
        'status',
        'tariff'
    ).order_by('-created_at')

    if query:
        query_variants = {
            query,
            query.lower(),
            query.upper(),
            query.capitalize(),
            query.title(),
        }
        search_filter = Q()

        for value in query_variants:
            search_filter |= (
                Q(from_address__icontains=value) |
                Q(to_address__icontains=value) |
                Q(client__username__icontains=value) |
                Q(client__first_name__icontains=value) |
                Q(client__last_name__icontains=value) |
                Q(driver__user__username__icontains=value) |
                Q(driver__user__first_name__icontains=value) |
                Q(driver__user__last_name__icontains=value) |
                Q(tariff__name__icontains=value) |
                Q(status__name__icontains=value)
            )

        orders = orders.filter(search_filter)

    return render(request, 'pages/orders_list.html', {
        'orders': orders,
        'query': query,
    })

def order_create(request: HttpRequest) -> HttpResponse:
    """
    Создаёт новый заказ через HTML-форму.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница формы или редирект на созданный заказ.
    """

    if request.method == "POST":

        form = OrderForm(request.POST, request.FILES)

        if form.is_valid():
            order = form.save()
            return redirect('order_detail', pk=order.pk)

    else:
        form = OrderForm()

    return render(request, 'pages/order_form.html', {
        'form': form,
        'title': 'Создание заказа'
    })


def order_update(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Редактирует существующий заказ через HTML-форму.

    Args:
        request: HTTP-запрос пользователя.
        pk: Идентификатор заказа.
    Returns:
        HttpResponse: Страница формы или редирект на обновлённый заказ.
    """

    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":

        form = OrderForm(request.POST, request.FILES, instance=order)

        if form.is_valid():
            form.save()
            return redirect('order_detail', pk=order.pk)

    else:
        form = OrderForm(instance=order)

    return render(request, 'pages/order_form.html', {
        'form': form,
        'title': 'Редактирование заказа'
    })


def order_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаляет заказ после подтверждения.

    Args:
        request: HTTP-запрос пользователя.
        pk: Идентификатор заказа.
    Returns:
        HttpResponse: Страница подтверждения или редирект на список заказов.
    """
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order.delete()
        return redirect('orders_list')

    return render(request, 'order_confirm_delete.html', {'order': order})

# frontend

def home(request: HttpRequest) -> HttpResponse:
    """
    Показывает главную страницу с виджетами и статистикой.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Главная страница проекта.
    """

    orders_count = Order.objects.count()

    drivers_count = Driver.objects.count()

    avg_price = Order.objects.aggregate(
        Avg('price')
    )['price__avg']

    latest_orders = Order.objects.select_related(
        'client',
        'driver',
        'status',
        'tariff'
    ).order_by('-created_at')[:5]

    top_drivers = Driver.objects.select_related(
        'user'
    ).prefetch_related(
        'car_set__image_set'
    ).annotate(
        order_count=Count('order')
    ).order_by('-rating', '-order_count')[:5]

    popular_services = Service.objects.annotate(
        order_count=Count('orderservice')
    ).order_by('-order_count', 'name')[:5]

    popular_tariffs = Tariff.objects.annotate(
        order_count=Count('order'),
        total_income=Sum('order__price')
    ).order_by('-order_count', 'name')[:5]

    tariff_options = [
        {
            'id': tariff.id,
            'name': tariff.name,
            'price': float(tariff.price),
        }
        for tariff in Tariff.objects.order_by('price')
    ]

    return render(request, 'pages/home.html', {

        'orders_count': orders_count,

        'drivers_count': drivers_count,

        'avg_price': round(avg_price or 0, 2),

        'latest_orders': latest_orders,

        'top_drivers': top_drivers,

        'popular_services': popular_services,

        'popular_tariffs': popular_tariffs,

        'tariff_options': tariff_options,
    })


def drivers_list(request: HttpRequest) -> HttpResponse:
    """
    Показывает список водителей с рейтингом и количеством заказов.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница списка водителей.
    """

    drivers = Driver.objects.select_related(
        'user'
    ).prefetch_related(
        'car_set__image_set'
    ).annotate(
        order_count=Count('order')
    ).order_by('-rating', '-order_count')

    return render(request, 'pages/drivers_list.html', {
        'drivers': drivers
    })


def services_list(request: HttpRequest) -> HttpResponse:
    """
    Показывает список дополнительных услуг.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница списка услуг.
    """

    services = Service.objects.annotate(
        order_count=Count('orderservice')
    ).order_by('-order_count', 'name')

    return render(request, 'pages/services_list.html', {
        'services': services
    })


def tariffs_list(request: HttpRequest) -> HttpResponse:
    """
    Показывает список тарифов и статистику по заказам.

    Args:
        request: HTTP-запрос пользователя.
    Returns:
        HttpResponse: Страница списка тарифов.
    """

    tariffs = Tariff.objects.annotate(
        order_count=Count('order'),
        total_income=Sum('order__price')
    ).order_by('-order_count', 'name')

    return render(request, 'pages/tariffs_list.html', {
        'tariffs': tariffs
    })


def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Показывает детальную страницу заказа.

    Args:
        request: HTTP-запрос пользователя.
        pk: Идентификатор заказа.
    Returns:
        HttpResponse: Страница с подробной информацией о заказе.
    """

    order = get_object_or_404(

        Order.objects.select_related(
            'client',
            'driver',
            'tariff',
            'status'
        ).prefetch_related(
            'services'
        ),

        pk=pk
    )

    return render(request, 'pages/order_detail.html', {
        'order': order
    })

# pdf

def get_pdf_font_name() -> str:
    """
    Возвращает имя шрифта для генерации PDF.

    Args:
        None: Функция не принимает аргументы.
    Returns:
        str: Зарегистрированное имя шрифта ReportLab.
    """
    font_path = Path('C:/Windows/Fonts/arial.ttf')

    if not font_path.exists():
        return 'Helvetica'

    font_name = 'Arial'

    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    return font_name


def order_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Генерирует PDF-файл с информацией о заказе.

    Args:
        request: HTTP-запрос пользователя.
        pk: Идентификатор заказа.
    Returns:
        HttpResponse: PDF-файл заказа.
    """

    order = get_object_or_404(Order, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    p = canvas.Canvas(response)
    font_name = get_pdf_font_name()

    p.setFont(font_name, 16)
    p.drawString(100, 800, f"Заказ №{order.id}")

    p.setFont(font_name, 12)
    p.drawString(100, 770, f"Клиент: {order.client.username}")
    p.drawString(100, 750, f"Откуда: {order.from_address}")
    p.drawString(100, 730, f"Куда: {order.to_address}")
    p.drawString(100, 710, f"Цена: {order.price} ₽")
    p.drawString(100, 690, f"Статус: {order.status}")

    p.showPage()
    p.save()

    return response
