import json
import pandas as pd
import xlwt
#nuevas importaciones 30-05-2022
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse,HttpResponseNotAllowed
from registration.models import Profile
from ordencompra.models import OrdenCompra, ItemOrden
from product.models import Producto
from prov.models import Proveedor
from django.conf import settings
#fin nuevas importaciones 30-05-2022

from django.db.models import Count, Avg, Q
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import (
	api_view, authentication_classes, permission_classes)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.platypus.flowables import Spacer
from reportlab.pdfgen import canvas
from datetime import date
from datetime import datetime
from django.core.mail import EmailMessage
import tempfile
import os
import io
from django.http import JsonResponse
from io import BytesIO
from .models import *

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.graph_objs as go


def dashboard4(request):
    # Obtener todas las órdenes de compra
    ordenes_compra = OrdenCompra.objects.all()

    # Crear una lista de totales de órdenes de compra
    totales = [orden.calcular_total() for orden in ordenes_compra]

    # Configurar el gráfico de barras para los totales de órdenes de compra
    fig1 = go.Figure(data=go.Bar(x=[f'Orden #{i + 1}' for i in range(len(ordenes_compra))], y=totales))
    fig1.update_layout(title='Total de órdenes de compra')

    # Crear una lista de proveedores y sus respectivas cantidades de órdenes de compra
    proveedores = [orden.proveedor.nombre for orden in ordenes_compra]
    cantidades = [orden.proveedor.ordencompra_set.count() for orden in ordenes_compra]

    # Configurar el gráfico de barras para las cantidades de órdenes de compra por proveedor
    fig2 = go.Figure(data=go.Bar(x=proveedores, y=cantidades))
    fig2.update_layout(title='Cantidad de órdenes de compra por proveedor')

    # Calcular el promedio de totales de órdenes de compra
    promedio_total = sum(totales) / len(totales)

    # Obtener la orden de compra con el total máximo
    orden_max_total = max(ordenes_compra, key=lambda orden: orden.calcular_total())

    # Obtener la orden de compra con el total mínimo
    orden_min_total = min(ordenes_compra, key=lambda orden: orden.calcular_total())

    context = {
        'plot_div1': fig1.to_html(full_html=False),
        'plot_div2': fig2.to_html(full_html=False),
        'promedio_total': promedio_total,
        'orden_max_total': orden_max_total,
        'orden_min_total': orden_min_total
    }

    return render(request, 'ordencompra/dashboard_4.html', context)
def crear_orden_compra(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        producto_id = request.POST.get('producto')
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad'))
        orden_compra = OrdenCompra.objects.create(proveedor=proveedor)
        item = ItemOrden.objects.create(orden_compra=orden_compra, producto=producto, cantidad=cantidad)
        producto.stock += cantidad
        producto.save()
        messages.add_message(request, messages.INFO, 'Se ha creado su orden de compra!')
        return redirect('ver_orden_compra', orden_id=orden_compra.id)
    
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    return render(request, 'ordencompra/crear_orden_compra.html', {'proveedores': proveedores, 'productos': productos})


def ver_orden_compra(request, orden_id):
    orden = get_object_or_404(OrdenCompra, id=orden_id)
    return render(request, 'ordencompra/ver_orden_compra.html', {'orden': orden})


def eliminar_orden_compra(request, orden_id):
    orden = get_object_or_404(OrdenCompra, id=orden_id)
    orden.delete()
    messages.add_message(request, messages.INFO, 'Se ha eliminado su orden de compra!')
    return redirect('listar_ordenes_compra')

def listar_ordenes_compra(request):
    busqueda = request.GET.get("buscar")
    filtro_id = request.GET.get("filtro_id")
    ordenes = OrdenCompra.objects.all()

    if busqueda:
        ordenes = ordenes.filter(id__icontains=busqueda)

    if filtro_id:
        try:
            filtro_id = int(filtro_id)
            ordenes = ordenes.filter(id=filtro_id)
        except ValueError:
            return redirect('listar_ordenes_compra')

    return render(request, 'ordencompra/listar_ordenes_compra.html', {'ordenes': ordenes, 'buscar': busqueda, 'filtro_id': filtro_id})



def agregar_item(request, orden_id):
    if request.method == 'POST':
        orden = get_object_or_404(OrdenCompra, id=orden_id)
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, id=producto_id)
        item = ItemOrden.objects.create(orden_compra=orden, producto=producto, cantidad=cantidad)
        producto.stock += cantidad
        producto.save()
        messages.add_message(request, messages.INFO, 'Se ha añadido su item a la orden de compra!')
        return redirect('ver_orden_compra', orden_id=orden.id)
    else:
        orden = get_object_or_404(OrdenCompra, id=orden_id)
        productos = Producto.objects.all()
        return render(request, 'ordencompra/agregar_item.html', {'orden': orden, 'productos': productos})


def eliminar_item(request, item_id):
    item = get_object_or_404(ItemOrden, id=item_id)
    orden_id = item.orden_compra.id
    item.delete()
    messages.add_message(request, messages.INFO, 'Se ha eliminado su item de la orden de compra!')
    return redirect('ver_orden_compra', orden_id=orden_id)

def order_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ordencompra/order_main.html'
    return render(request,template_name,{'profile':profile})

def editar_item(request, item_id):
    item = get_object_or_404(ItemOrden, id=item_id)

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Actualizar los valores del item
        item.producto = producto
        item.cantidad = cantidad
        item.save()

        # Actualizar el stock del producto
        producto.stock -= item.cantidad
        producto.stock += cantidad
        producto.save()

        return redirect('ver_orden_compra', orden_id=item.orden_compra.id)
    
    productos = Producto.objects.all()
    return render(request, 'ordencompra/editar_item.html', {'item': item, 'productos': productos})
def guardar_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemOrden, id=item_id)
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, id=producto_id)
        item.producto = producto
        item.cantidad = cantidad
        item.save()
        producto.stock += cantidad
        producto.save()
        return redirect('ver_orden_compra', orden_id=item.orden_compra.id)
    else:
        return redirect('listar_ordenes_compra')




def generar_reporte_oc(request, filtro_id=None):
    filtro_id = request.GET.get("filtro_id")
    filtro_nombre = request.GET.get("filtro_nombre")
    ordenes_compra = OrdenCompra.objects.all()

    if filtro_id:
        try:
            orden_compra = ordenes_compra.get(id=filtro_id)
        except OrdenCompra.DoesNotExist:
            return HttpResponse("No se encontró una orden de compra con ese ID.")

        ordenes_compra = [orden_compra]

    if filtro_nombre:
        ordenes_compra = ordenes_compra.filter(proveedor__nombre__icontains=filtro_nombre)

    if not filtro_id and not filtro_nombre:
        return HttpResponse("Debe especificar al menos un filtro.")

    if filtro_id:
        # Crear el archivo PDF en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte_orden_compra.pdf"'

            document = SimpleDocTemplate(temp_file.name, pagesize=letter)
            elements = []

            styles = getSampleStyleSheet()
            style_table = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#EEEEEE'),
            ])
            style_paragraph = ParagraphStyle(
                name='BodyText',
                parent=styles['Normal'],
                spaceBefore=6,
                spaceAfter=6,
            )

            data = [['Proveedor', 'Fecha Creación', 'Producto', 'Cantidad', 'Subtotal']]
            for orden_compra in ordenes_compra:
                for item in orden_compra.items.all():
                    data.append([
                        str(orden_compra.proveedor),
                        orden_compra.fecha_creacion.strftime("%d-%m-%Y"),  # Acortar la fecha de creación
                        item.producto.nombre,
                        str(item.cantidad),
                        str(item.subtotal)
                    ])

            table = Table(data)
            table.setStyle(style_table)

            elements.append(Paragraph('Informe de Orden de Compra', styles['Heading1']))
            elements.append(Paragraph('Fecha: ' + datetime.now().strftime('%d/%m/%Y'), style_paragraph))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph('Detalle de la orden de compra:', styles['Heading3']))
            elements.append(table)

            document.build(elements)

        # Leer el contenido del archivo temporal y devolverlo como respuesta
        with open(temp_file.name, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')

        # Establecer el encabezado de descarga del archivo adjunto
        response['Content-Disposition'] = 'attachment; filename="reporte_orden_compra.pdf"'

        # Eliminar el archivo temporal después de enviarlo
        os.remove(temp_file.name)

        return response

def enviar_correo_oc(request):
    if request.method == 'POST':
        filtro_id = request.POST.get('filtro_id')
        orden_compra = None

        if filtro_id:
            try:
                filtro_id = int(filtro_id)
                orden_compra = OrdenCompra.objects.filter(id=filtro_id).first()
            except ValueError:
                return redirect('listar_orden_compra')

        if orden_compra:
            proveedor = orden_compra.proveedor
            asunto = f'Orden de Compra {orden_compra.id}'
            contenido = f'Estimado proveedor,\n\nAdjuntamos la orden de compra con ID {orden_compra.id}.'

            # Generar el archivo PDF en un objeto de tipo BytesIO
            pdf_buffer = BytesIO()
            document = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            elements = []

            styles = getSampleStyleSheet()
            style_table = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#EEEEEE'),
            ])
            style_paragraph = ParagraphStyle(
                name='BodyText',
                parent=styles['Normal'],
                spaceBefore=6,
                spaceAfter=6,
            )

            data = [['ID', 'Proveedor', 'Producto', 'Cantidad', 'Precio Unitario', 'Total']]
            for item in orden_compra.items.all():
                data.append([
                    str(orden_compra.id),
                    str(orden_compra.proveedor),
                    item.producto.nombre,
                    str(item.cantidad),
                    str(item.producto.precio),
                    str(item.subtotal)
                ])

            table = Table(data)
            table.setStyle(style_table)

            elements.append(Paragraph('Informe de Órdenes de Compra', styles['Heading1']))
            elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph('Listado de órdenes de compra:', styles['Heading3']))
            elements.append(table)

            document.build(elements)

            # Obtener el contenido del objeto BytesIO y establecer el puntero al inicio
            pdf_buffer.seek(0)
            pdf_content = pdf_buffer.getvalue()

            # Crear el mensaje de correo electrónico
            email = EmailMessage(
                asunto,
                contenido,
                'tucorreo@gmail.com',
                [proveedor.correo],
            )

            # Adjuntar el archivo PDF al correo electrónico especificando el nombre personalizado
            nombre_archivo = f'reporte_orden_compra_{orden_compra.id}.pdf'
            email.attach(nombre_archivo, pdf_content, 'application/pdf')

            # Enviar el correo electrónico
        try:
            email.send()
            return render(request, 'confirmacion_correo.html', {'orden_compra': orden_compra})
        except Exception as e:
            # Manejar el error o mostrar un mensaje de error
            print(f"Error al enviar el correo electrónico: {str(e)}")
            return HttpResponse('Error al enviar el correo electrónico.')       