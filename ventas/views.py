import json
import pandas as pd
import xlwt
#nuevas importaciones 30-05-2022
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from registration.models import Profile

#fin nuevas importaciones 30-05-2022

from django.db.models import Count, Avg, Q
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import (
	api_view, authentication_classes, permission_classes)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Venta, ItemVenta, Cliente
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import date
from reportlab.lib.pagesizes import letter
from django.http import JsonResponse
import plotly.graph_objs as go


def dashboard6(request):
    # Obtener todas las ventas
    ventas = Venta.objects.all()

    # Gráfico de barras: Cantidad de ventas por cliente
    clientes = [venta.cliente.nombre1 for venta in ventas]
    labels = sorted(list(set(clientes)))
    values = [clientes.count(cliente) for cliente in labels]

    fig1 = go.Figure(data=go.Bar(x=labels, y=values))
    fig1.update_layout(title='Cantidad de ventas por cliente')

    # Gráfico de pastel: Distribución de total de ventas

    totales = [venta.total for venta in ventas]
    labels2 = ['Menor a 10000', '10000 a 25000', 'Mayor a 25000']
    values2 = [
        len([total for total in totales if total < 10000]),
        len([total for total in totales if 10000 <= total <= 25000]),
        len([total for total in totales if total>25000])
        ]

    fig2 = go.Figure(data=[go.Pie(labels=labels2, values=values2)])
    fig2.update_layout(title='Distribución de total de ventas')

    # Datos útiles
    cantidad_ventas = len(ventas)
    venta_mas_reciente = max(ventas, key=lambda venta: venta.fecha_venta)
    venta_mas_antigua = min(ventas, key=lambda venta: venta.fecha_venta)

    context = {
        'plot_div1': fig1.to_html(full_html=False),
        'plot_div2': fig2.to_html(full_html=False),
        'cantidad_ventas': cantidad_ventas,
        'venta_mas_reciente': venta_mas_reciente,
        'venta_mas_antigua': venta_mas_antigua,
    }

    return render(request, 'ventas/dashboard_6.html', context)

def crear_venta(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        cliente = get_object_or_404(Cliente, id=cliente_id)
    
        productos = Producto.objects.all()
        total = 0
        venta = Venta.objects.create(cliente=cliente, total=0)

        for producto in productos:
            cantidad = int(request.POST.get(f'cantidad_{producto.id}', 0))

            if cantidad > 0 and cantidad <= producto.stock:
                subtotal = producto.precio * cantidad
                total += subtotal
                producto.stock -= cantidad
                producto.save()

                ItemVenta.objects.create(venta=venta, producto=producto, cantidad=cantidad, subtotal=subtotal)

        venta.total = total
        venta.save()

        return redirect('ver_venta', venta_id=venta.id)
    else:
        clientes = Cliente.objects.all()
        productos = Producto.objects.all()
        return render(request, 'ventas/crear_venta.html', {'clientes': clientes, 'productos': productos})


def listar_ventas(request):
    venta_id = request.GET.get('venta_id')
    buscar = request.GET.get('buscar')

    if venta_id:
        ventas = Venta.objects.filter(id=venta_id)
        numero_ventas = ventas.count()
    elif buscar:
        ventas = Venta.objects.filter(Q(id__icontains=buscar))
        numero_ventas = ventas.count()
    else:
        ventas = Venta.objects.all()
        numero_ventas = ventas.count()

    return render(request, 'ventas/listar_ventas.html', {'ventas': ventas, 'numero_ventas': numero_ventas})




def ver_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'ventas/ver_venta.html', {'venta': venta})


def listar_ventas(request):
    busqueda = request.GET.get("buscar")
    filtro_id = request.GET.get("filtro_id")
    ventas = Venta.objects.all()

    if busqueda:
        ventas = ventas.filter(cliente_nombre1_icontains=busqueda)

    if filtro_id:
        try:
            filtro_id = int(filtro_id)
            ventas = ventas.filter(id=filtro_id)
        except ValueError:
            return redirect('listar_ventas')

    numero_ventas = ventas.count()
    return render(request, 'ventas/listar_ventas.html', {'ventas': ventas, 'numero_ventas': numero_ventas})



def agregar_item(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, id=producto_id)

        if cantidad > 0 and cantidad <= producto.stock:
            subtotal = producto.precio * cantidad
            producto.stock -= cantidad
            producto.save()

            ItemVenta.objects.create(venta=venta, producto=producto, cantidad=cantidad, subtotal=subtotal)

    productos = Producto.objects.all()
    return render(request, 'ventas/agregar_item.html', {'venta': venta, 'productos': productos})


def eliminar_item(request, venta_id, item_id):
    venta = get_object_or_404(Venta, id=venta_id)
    item = get_object_or_404(ItemVenta, id=item_id)

    producto = item.producto
    producto.stock += item.cantidad
    producto.save()

    item.delete()

    return redirect('ver_venta', venta_id=venta.id)

def venta_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'ventas/venta_main.html'
    return render(request,template_name,{'profile':profile})

def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    items_venta = venta.items.all()

    for item_venta in items_venta:
        item_venta.actualizar_stock_eliminacion()

    venta.delete()

    return redirect('listar_ventas')

def generar_reporte_ventas(request):
    filtro_id = request.GET.get("filtro_id")
    filtro_nombre = request.GET.get("filtro_nombre")
    ventas = Venta.objects.all()

    if filtro_id:
        try:
            venta = ventas.get(id=filtro_id)
        except Venta.DoesNotExist:
            return HttpResponse("No se encontró una venta con ese ID.")

        ventas = [venta]

    if filtro_nombre:
        ventas = ventas.filter(cliente_nombre1_icontains=filtro_nombre)

    if not filtro_id and not filtro_nombre:
        return HttpResponse("Debe especificar al menos un filtro.")

    if filtro_id:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

        document = SimpleDocTemplate(response, pagesize=letter)
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

        data = [['ID','Producto', 'Cantidad', 'Total']]
        for venta in ventas:
            for item in venta.items.all():
                data.append([
                    str(venta.id),
                    str(venta.cliente),
                    item.producto.nombre,
                    str(item.cantidad),
                    str(item.producto.precio),
                    str(item.subtotal)
                ])

        table = Table(data)
        table.setStyle(style_table)

        elements.append(Paragraph('Informe de Ventas', styles['Heading1']))
        elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('Listado de ventas:', styles['Heading3']))
        elements.append(table)

        document.build(elements)

        return response