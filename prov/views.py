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
from prov.models import Proveedor
from .forms import ProveedorForm


############
from datetime import date
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.template import Context
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

from django.urls import reverse



@login_required
def listar_proveedor(request):
    busqueda = request.GET.get("buscar")
    proveedores = Proveedor.objects.all()

    if busqueda:
        proveedores = proveedores.filter(nombre__icontains=busqueda)

    if 'generar_reporte_prov' in request.GET:
        return redirect(reverse('generar_reporte_prov') + '?buscar=' + busqueda)
    
    return render(request, 'prov/listar_proveedor.html', {'proveedores': proveedores, 'buscar': busqueda})

@login_required
def generar_reporte_prov(request):
    busqueda = request.GET.get("buscar")
    Proveedores = Proveedor.objects.all()
    if busqueda:
        Proveedores = Proveedores.filter(nombre__icontains=busqueda)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_proveedores.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    data = []
    data.append(['Nombre', 'Apellido', 'Celular', 'Empresa', 'Descripcion'])
    for proveedor in Proveedores:
        data.append([proveedor.nombre, proveedor.apellido, proveedor.celular, proveedor.empresa, proveedor.descripcion])
    # Crear los estilos de tabla y párrafo
    styles = getSampleStyleSheet()
    style_table = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
    ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), '#EEEEEE'),
    ('COLWIDTHS', (0, 0), (-1, -1), 60),  # Ajusta el ancho de todas las columnas
    ])
    style_paragraph = ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        spaceBefore=6,
        spaceAfter=6,
    )

    # Crear la tabla con los datos y aplicar estilos
    table = Table(data)
    table.setStyle(style_table)

    # Agregar la tabla al documento
    elements = [Paragraph('Informe de Proveedores', styles['Heading1'])]
    elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
    elements.append(Paragraph('Listado de Proveedores:', styles['Heading3']))
    elements.append(table)

    doc.build(elements)

    return response

















@login_required
def proveedor_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'prov/proveedor_main.html'
    return render(request,template_name,{'profile':profile})
@login_required
def agregar_proveedor(request):
    data = {
        'form': ProveedorForm()
    }
    if request.method == 'POST':
        formulario = ProveedorForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.add_message(request, messages.INFO, 'Proveedor creado!')
    return render(request, 'prov/agregar_proveedor.html',data)


@login_required
def actualizar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    data ={
        'form': ProveedorForm(instance=proveedor)
    }
    if request.method == 'POST':
        formulario = ProveedorForm(data=request.POST,instance=proveedor)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_proveedor")
    messages.add_message(request, messages.INFO, 'proveedor actualizado!')
    return render(request, 'prov/actualizar_proveedor.html',data)

@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    proveedor.delete()
    messages.add_message(request, messages.INFO, 'proveedor eliminado!')
    return redirect(to="listar_proveedor")