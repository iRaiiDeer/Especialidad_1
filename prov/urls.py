from django.urls import path
from prov import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

prov_urlpatterns = [
    path('proveedor/',views.proveedor_main,name="proveedor_main"),
    path('agregar_proveedor/',views.agregar_proveedor,name="agregar_proveedor"),
    path('listar_proveedor/',views.listar_proveedor,name="listar_proveedor"),
    path('actualizar_proveedor/<id>/',views.actualizar_proveedor,name="actualizar_proveedor"),
    path('eliminar_proveedor/<id>/',views.eliminar_proveedor,name="eliminar_proveedor"),

    path('generar_reporte_prov/', views.generar_reporte_prov, name='generar_reporte_prov'),

    path('carga_masiva_prov/',views.carga_masiva_prov,name="carga_masiva_prov"),
    path('carga_masiva_saveprov/',views.carga_masiva_saveprov,name="carga_masiva_saveprov"),
    path('import_file/',views.import_file,name="import_file"),
    path('dashboard2/', views.dashboard2, name='dashboard2'),
]