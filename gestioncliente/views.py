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
from gestioncliente.models import Cliente
from .forms import ClienteForm
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.platypus.flowables import Spacer



#CLIENTE
@login_required
def clientes_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'gestioncliente/clientes_main.html'
    return render(request,template_name,{'profile':profile})

@login_required
def agregar_cliente(request):
    data = {
        'form': ClienteForm()
    }
    if request.method == 'POST':
        formulario = ClienteForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.add_message(request, messages.INFO, 'cliente creado!')
    return render(request, 'gestioncliente/agregar_cliente.html',data)

@login_required
def listar_cliente(request):
     clientes = Cliente.objects.all()
     data={
         'clientes': clientes
     }
     return render(request, 'gestioncliente/listar_cliente.html',data)
@login_required
def actualizar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    data ={
        'form': ClienteForm(instance=cliente)
    }
    if request.method == 'POST':
        formulario = ClienteForm(data=request.POST,instance=cliente)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_cliente")
    messages.add_message(request, messages.INFO, 'cliente actualizado!')
    return render(request, 'gestioncliente/modificar_cliente.html',data)
@login_required
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    messages.add_message(request, messages.INFO, 'cliente eliminado!')
    return redirect(to="listar_cliente")



def generar_reporte(request):
    # Recopilar los datos necesarios para el informe
    clientes = Cliente.objects.all()
    
    # Crear el archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'
    
    # Generar el contenido del informe en el archivo PDF
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

    # Generar la tabla con los datos de los clientes
    data = [['Nombre', 'Apellido1', 'Apellido2', 'Celular', 'Edad', 'Dirección Postal']]  # Encabezados de la tabla
    for cliente in clientes:
        data.append([cliente.nombre1, cliente.apellido1, cliente.apellido2, cliente.celular, cliente.edad, cliente.direccion_postal])  # Agregar filas de datos

    table = Table(data, style=style_table, hAlign='LEFT')
    table.setStyle(style_table)

    # Crear el objeto Paragraph para el título de la tabla
    titulo_tabla = Paragraph("<b>Datos de los clientes</b>", style_paragraph)

    # Crear el archivo PDF y agregar el contenido
    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, "Informe de Gestión de Clientes")

    # Agregar espacio antes de la tabla
    espacio = Spacer(1, 20)
    espacio.wrapOn(p, 0, 0)
    espacio.drawOn(p, 0, 630)

    # Agregar la tabla al archivo PDF
    table.wrapOn(p, 400, 200)
    table.drawOn(p, 100, 600)

    # Agregar el título de la tabla al archivo PDF
    titulo_tabla.wrapOn(p, 400, 200)
    titulo_tabla.drawOn(p, 100, 680)  # Ajustar coordenadas aquí

    # Agrega aquí otros elementos del informe

    # Finalizar el PDF
    p.showPage()
    p.save()

    return response



#####CARGA MASIVA CLIENTES
@login_required
def carga_masiva_cliente(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'gestioncliente/carga_masiva_clientes.html'
    return render(request,template_name,{'profiles':profiles})

@login_required
def import_file_cliente(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="archivo_importacion.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('carga_masiva')
    row_num = 0
    columns = ['Nombre Cliente']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    for row in range(1):
        row_num += 1
        for col_num in range(1):
            if col_num == 0:
                ws.write(row_num, col_num, 'ej: categoria' , font_style)
    wb.save(response)
    return response  

@login_required
def cliente_carga_masiva_save(request):
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
            cliente_save = Cliente(
                nombre1 = nombre,                   
                )
            cliente_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('carga_masiva_cliente')    