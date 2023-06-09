from django.urls import path
from gestioncliente import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from gestioncliente import views
gestioncliente_urlpatterns = [

    path('clientes_main/',views.clientes_main,name="clientes_main"),
    path('agregar_cliente/',views.agregar_cliente,name="agregar_cliente"),
    path('listar_cliente/',views.listar_cliente,name="listar_cliente"),
    path('actualizar_cliente/<id>/',views.actualizar_cliente,name="actualizar_cliente"),
    path('eliminar_cliente/<id>/',views.eliminar_cliente,name="eliminar_cliente"),
    path('reporte/', views.generar_reporte, name='generar_reporte'),


    path('carga_masiva_cliente/',views.carga_masiva_cliente,name="carga_masiva_cliente"),
    path('cliente_carga_masiva_save/',views.cliente_carga_masiva_save,name="cliente_carga_masiva_save"),
    path('import_file_cliente/',views.import_file_cliente,name="import_file_cliente"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generar_reporte_cliente/', views.generar_reporte_cliente, name='generar_reporte_cliente'),
    
    ]