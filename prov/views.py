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
import plotly.graph_objects as go
from django.urls import reverse

def dashboard2(request):
    proveedores = Proveedor.objects.all()

    # Datos útiles
    total_proveedores = proveedores.count()
    proveedores_ordenados = proveedores.order_by('-created')[:5]
    proveedores_nuevos = [proveedor.empresa for proveedor in proveedores_ordenados]

    # Gráfico 1: Distribución de proveedores por empresa
    empresas = [proveedor.empresa for proveedor in proveedores]
    empresa_count = {}
    for empresa in empresas:
        if empresa in empresa_count:
            empresa_count[empresa] += 1
        else:
            empresa_count[empresa] = 1

    fig1 = go.Figure(data=[go.Pie(labels=list(empresa_count.keys()), values=list(empresa_count.values()))])
    fig1.update_layout(title='Distribución de proveedores por empresa')

    # Gráfico 2: Crecimiento de proveedores a lo largo del tiempo
    fechas = [proveedor.created.date() for proveedor in proveedores]
    fechas_unicas = list(set(fechas))
    fechas_unicas.sort()

    proveedores_crecimiento = []
    proveedores_cumulativos = 0
    for fecha in fechas_unicas:
        proveedores_dia = fechas.count(fecha)
        proveedores_cumulativos += proveedores_dia
        proveedores_crecimiento.append(proveedores_cumulativos)

    fig2 = go.Figure(data=[go.Scatter(x=fechas_unicas, y=proveedores_crecimiento, mode='lines')])
    fig2.update_layout(title='Crecimiento de proveedores a lo largo del tiempo', xaxis_title='Fecha', yaxis_title='Número de proveedores')

    # Renderizar el dashboard
    return render(request, 'prov/dashboard2.html', {
        'total_proveedores': total_proveedores,
        'proveedores_nuevos': proveedores_nuevos,
        'fig1': fig1.to_html(full_html=False, default_height=500),
        'fig2': fig2.to_html(full_html=False, default_height=500)
    })

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
            return redirect('listar_proveedor')
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

#CARGA MASIVA PROVEEDOR
@login_required
def carga_masiva_prov(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'prov/carga_masiva_prov.html'
    return render(request,template_name,{'profiles':profiles})

@login_required
def import_file(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('carga_masiva')
    row_num = 0
    columns = ['Nombre','Apellido','Celular','Empresa','Descripcion','Correo']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    for row in range(1):
        row_num += 1
        for col_num in range(6):
            if col_num == 0:
                ws.write(row_num, col_num, 'ej: Nombre' , font_style)
            if col_num == 1:                           
                ws.write(row_num, col_num, 'Apellido' , font_style)
            if col_num == 2:                           
                ws.write(row_num, col_num, 'Celular' , font_style)
            if col_num == 3:                           
                ws.write(row_num, col_num, 'Empresa' , font_style)
            if col_num == 4:                           
                ws.write(row_num, col_num, 'Descripcion' , font_style)
            if col_num == 5:                           
                ws.write(row_num, col_num, 'Correo' , font_style)
    wb.save(response)
    return response  

@login_required
def carga_masiva_saveprov(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')

    if request.method == 'POST':
        #try:
        print(request.FILES['myfile'])
        data = pd.read_excel(request.FILES['myfile'])
        df = pd.DataFrame(data)
        acc = 0
        for item in df.itertuples():
            #capturamos los datos desde excel
            nombre = str(item[1])            
            apellido = str(item[2])
            celular = int(item[3])            
            empresa = str(item[4])
            descripcion = str(item[5])
            correo = str(item[6])
            producto_save = Proveedor(
                nombre = nombre,            
                apellido = apellido,
                celular = celular,            
                empresa = empresa,
                descripcion = descripcion,   
                correo = correo,      
                )
            producto_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('carga_masiva_prov')    
#####################################