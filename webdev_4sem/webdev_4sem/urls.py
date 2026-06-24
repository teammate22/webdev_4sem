"""
URL configuration for webdev_4sem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  

    path('orders/<int:pk>/pdf/', views.order_pdf, name='order_pdf'),

    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),

    path('silk/', include('silk.urls', namespace='silk')),

    path('api/', include('core.api.urls')),

    path('orders/', views.orders_list, name='orders_list'),

    path('drivers/', views.drivers_list, name='drivers_list'),

    path('services/', views.services_list, name='services_list'),

    path('tariffs/', views.tariffs_list, name='tariffs_list'),

    path('orders/create/', views.order_create, name='order_create'),

    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    path('orders/<int:pk>/edit/', views.order_update, name='order_update'),

    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),

    path('test/', views.test_queries, name='test_queries'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
