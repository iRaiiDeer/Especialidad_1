from django.urls import path
from ventas import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

ventas_urlpatterns = [
    path('venta_main/',views.venta_main,name="venta_main"),

    path('crear_venta/', views.crear_venta, name='crear_venta'),
    path('ver_venta/<int:venta_id>/', views.ver_venta, name='ver_venta'),
    path('listar_ventas/', views.listar_ventas, name='listar_ventas'),
    # path('agregar_item/<int:venta_id>/', views.agregar_item, name='agregar_item'),
    # path('eliminar_item/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('ventas/<int:venta_id>/agregar_item/', views.agregar_item, name='agregar_item'),
    path('ventas/<int:venta_id>/eliminar_item/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('ventas/generar-reporte/', views.generar_reporte_ventas, name='generar_reporte_ventas'),
    path('eliminar_venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('dashboard6/', views.dashboard6, name='dashboard6'),
]