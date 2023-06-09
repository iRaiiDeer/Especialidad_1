from django.urls import path
from product import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

product_urlpatterns = [

    path('ejemplos_main/',views.ejemplos_main,name="ejemplos_main"),
    path('agregar_producto/',views.agregar_producto,name="agregar_producto"),
    #path('productos/', listar_producto, name='listar_productos'),
    path('listar_producto/',views.listar_producto,name="listar_producto"),
    path('actualizar_producto/<id>/',views.actualizar_producto,name="actualizar_producto"),
    path('eliminar_producto/<id>/',views.eliminar_producto,name="eliminar_producto"),

    path('ejemplos_carga_masiva/',views.ejemplos_carga_masiva,name="ejemplos_carga_masiva"),
    path('ejemplos_carga_masiva_save/',views.ejemplos_carga_masiva_save,name="ejemplos_carga_masiva_save"),
    path('import_file/',views.import_file,name="import_file"),
    path('generar_reporte_prod/', views.generar_reporte_prod, name='generar_reporte_prod'),
    path('dashboard1/', views.dashboard1, name='dashboard1'),
]

