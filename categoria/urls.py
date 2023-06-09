from django.urls import path
from categoria import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

categoria_urlpatterns = [


    path('agregar_categoria/',views.agregar_categoria,name="agregar_categoria"),
    path('listar_categoria/',views.listar_categoria,name="listar_categoria"),
    path('modificar_categoria/<id>/',views.modificar_categoria,name="modificar_categoria"),
    path('eliminar_categoria/<id>/',views.eliminar_categoria,name="eliminar_categoria"),

    path('carga_masiva_categoria/',views.carga_masiva_categoria,name="carga_masiva_categoria"),
    path('categoria_carga_masiva_save/',views.categoria_carga_masiva_save,name="categoria_carga_masiva_save"),
    path('import_file_categoria/',views.import_file_categoria,name="import_file_categoria"),

    path('generar_reporte_cat/', views.generar_reporte_cat, name='generar_reporte_cat'),


]