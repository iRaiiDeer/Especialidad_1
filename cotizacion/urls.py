
from django.conf.urls import url #importa la función url
from django.urls import path #importa el metodo path
from cotizacion import views #improta los metodos de que se implementan en el views,py de este directorio
from .views import *


cotizacion_urlpatterns = [
    path('crear_cotizacion/',views.crear_cotizacion,name="crear_cotizacion"),
    path('ver_cotizacion/<int:orden_id>/',views.ver_cotizacion,name="ver_cotizacion"),
    path('eliminar_cotizacion/<int:orden_id>/',views.eliminar_cotizacion,name="eliminar_cotizacion"),
    path('listar_cotizacion/',views.listar_cotizacion,name="listar_cotizacion"),
    path('ola/<int:orden_id>/',views.ola,name="ola"),
    path('eliminar/<int:item_id>/',views.eliminar,name="eliminar"),
    path('cotizacion_main/',views.cotizacion_main,name="cotizacion_main"),
    path('generar_reporte_cotizaciones/', views.generar_reporte_cotizaciones, name='generar_reporte_cotizaciones'),
    path('enviar_correo_cotizacion/', views.enviar_correo_cotizacion, name='enviar_correo_cotizacion'),
    path('dashboard5/', views.dashboard5, name='dashboard5'),
]