from django.contrib import admin
from .models import (
    Driver,
    Car,
    Image,
    Tariff,
    OrderStatus,
    Service,
    Order,
    OrderService,
    Payment,
    Review
)
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path


# =========================
# INLINE-МОДЕЛИ
# =========================

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1


# =========================
# DRIVER
# =========================

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'status', 'created_at')
    raw_id_fields = ('user',)
    list_filter = ('status',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)

# =========================
# CAR
# =========================

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'brand', 'model', 'number')
    raw_id_fields = ('driver',)
    list_display_links = ('id', 'brand')
    search_fields = ('brand', 'model', 'number')
    inlines = [ImageInline]


# =========================
# TARIFF
# =========================

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)


# =========================
# ORDER STATUS
# =========================

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


# =========================
# SERVICE
# =========================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)


# =========================
# ORDER
# =========================

def get_pdf_font_name():
    font_path = Path('C:/Windows/Fonts/arial.ttf')

    if not font_path.exists():
        return 'Helvetica'

    font_name = 'Arial'

    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    return font_name


def export_orders_pdf(modeladmin, request, queryset):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="orders.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setFont(get_pdf_font_name(), 12)

    y = 800

    for order in queryset:
        pdf.drawString(100, y, f"Заказ {order.id} | Цена: {order.price} ₽")
        y -= 20

    pdf.save()

    return response

export_orders_pdf.short_description = "Экспорт в PDF"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'driver',
        'formatted_price',
        'status',
        'created_at'
    )
    list_display_links = ('id', 'client')
    list_filter = ('status', 'tariff')
    search_fields = (
        'client__username',
        'driver__user__username'
    )
    date_hierarchy = 'created_at'
    raw_id_fields = ('client', 'driver')
    inlines = [OrderServiceInline]
    readonly_fields = ('created_at',)
    actions = [export_orders_pdf]

    @admin.display(description='Стоимость')
    def formatted_price(self, obj):
        return f'{obj.price} ₽'


# =========================
# PAYMENT
# =========================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method')
    readonly_fields = ('paid_at',)
    raw_id_fields = ('order',)


# =========================
# REVIEW
# =========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('comment',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('order',)
