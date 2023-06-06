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
    ventas = Venta.objects.all()
    # Obtener el número de ventas
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