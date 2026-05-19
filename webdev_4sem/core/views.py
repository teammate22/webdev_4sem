from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Order, Driver
from django.db.models import Count, Avg, Sum, Q
from .forms import OrderForm
from django.core.cache import cache
from django.db.models import F
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# contains/icontains
def search_orders(request):

    query = request.GET.get('q')

    orders = Order.objects.all()

    if query:
        orders = orders.filter(from_address__icontains=query)

    return render(request, 'orders_list.html', {'orders': orders})
    # Order.objects.filter(from_address__contains="Москва") - поиск по точному совпадению
    # Order.objects.filter(from_address__icontains="москва") - поиск без учёта регистра

# values() и values_list()
def orders_values(request):

    data = Order.objects.values('id', 'price')

    return render(request, 'test.html', {'data': data})

def orders_values_list(request):

    data = Order.objects.values_list('id', 'price')

    return render(request, 'test.html', {'data': data})

# count(), exists(), update(), delete()
def test_queries(request):

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
def orders_cached(request):
    orders = cache.get('orders_list')

    if not orders:
        orders = list(Order.objects.all())  # QuerySet превращаем в list
        cache.set('orders_list', orders, 60)  # сохраняем в кеш на 60 секунд

    return render(request, 'orders_list.html', {'orders': orders})

# F-выражение
def increase_driver_rating(request, driver_id):
    Driver.objects.filter(id=driver_id).update(rating=F('rating') + 1)
    return redirect('drivers_list')

def user_orders_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # related_name использование
    orders = user.orders.all()

    return render(request, 'orders.html', {'orders': orders})


def filtered_orders_view(request):

    # lookup-выражение (пример использования __)
    orders = Order.objects.filter(price__gt=1000)

    # фильтрация по связанному полю (пример использования __)
    Order.objects.filter(driver__user__username="alex")

    # exclude()
    orders = orders.exclude(status__name="Отменён")

    # order_by()
    orders = orders.order_by('-price')

    return render(request, 'orders.html', {'orders': orders})

def aggregation_view(request):

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
def orders_list(request):

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

def order_create(request):

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


def order_update(request, pk):

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


def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order.delete()
        return redirect('orders_list')

    return render(request, 'order_confirm_delete.html', {'order': order})

# frontend

def home(request):

    orders_count = Order.objects.count()

    drivers_count = Driver.objects.count()

    avg_price = Order.objects.aggregate(
        Avg('price')
    )['price__avg']

    latest_orders = Order.objects.select_related(
        'client',
        'driver',
        'status'
    ).order_by('-created_at')[:5]

    return render(request, 'pages/home.html', {

        'orders_count': orders_count,

        'drivers_count': drivers_count,

        'avg_price': round(avg_price or 0, 2),

        'latest_orders': latest_orders
    })


def order_detail(request, pk):

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

def get_pdf_font_name():
    font_path = Path('C:/Windows/Fonts/arial.ttf')

    if not font_path.exists():
        return 'Helvetica'

    font_name = 'Arial'

    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    return font_name


def order_pdf(request, pk):

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
