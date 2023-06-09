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
import plotly.graph_objects as go


from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.template import Context
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from datetime import date
from django.urls import reverse


from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def listar_cliente(request):
    busqueda = request.GET.get("buscar")
    clientes = Cliente.objects.all()

    if busqueda:
        clientes = clientes.filter(nombre1__icontains=busqueda)

    if 'generar_reporte_cliente' in request.GET:
        return redirect(reverse('generar_reporte_cliente') + '?buscar=' + busqueda)
    
    if not busqueda:
        clientes = Cliente.objects.all()

    return render(request, 'gestioncliente/listar_cliente.html', {'clientes': clientes, 'buscar': busqueda})




@login_required

def generar_reporte_cliente(request):
    busqueda = request.GET.get("buscar")
    clientes = Cliente.objects.all()
    if busqueda:
        clientes = clientes.filter(nombre1__icontains=busqueda)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_clientes.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    data = []
    data.append(['Nombre', 'Segundo nombre', 'Apellido', 'Segundo apellido', 'Correo','Celular','Edad', 'Codigo postal'])
    for cliente in clientes:
        data.append([cliente.nombre1, cliente.nombre2, cliente.apellido1, cliente.apellido2, cliente.correo_electronico, cliente.celular, cliente.edad])
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
    elements = [Paragraph('Informe de Clientes', styles['Heading1'])]
    elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
    elements.append(Paragraph('Listado de Clientes:', styles['Heading3']))
    elements.append(table)

    doc.build(elements)

    return response

#CLIENTE
def dashboard(request):
    # Obtener todos los clientes
    clientes = Cliente.objects.all()

    # Grafico de pastel: Distribución de edades de los clientes
    edades = [cliente.edad for cliente in clientes if cliente.edad is not None]
    labels = ['<18', '18-25', '26-35', '36-50', '>50']
    values = [
        len([edad for edad in edades if edad < 18]),
        len([edad for edad in edades if 18 <= edad <= 25]),
        len([edad for edad in edades if 26 <= edad <= 35]),
        len([edad for edad in edades if 36 <= edad <= 50]),
        len([edad for edad in edades if edad > 50])
    ]

    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig1.update_layout(title='Distribución de edades de los clientes')

    # Grafico de barras: Cantidad de clientes por mes de creación
    meses_creacion = [cliente.created.month for cliente in clientes if cliente.created is not None]
    labels2 = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    values2 = [meses_creacion.count(i) for i in range(1, 13)]

    fig2 = go.Figure(data=go.Bar(x=labels2, y=values2))
    fig2.update_layout(title='Cantidad de clientes por mes de creación')

    # Datos útiles
    cantidad_clientes = len(clientes)
    cliente_mas_reciente = max(clientes, key=lambda cliente: cliente.created)
    cliente_mas_antiguo = min(clientes, key=lambda cliente: cliente.created)

    context = {
        'plot_div1': fig1.to_html(full_html=False),
        'plot_div2': fig2.to_html(full_html=False),
        'cantidad_clientes': cantidad_clientes,
        'cliente_mas_reciente': cliente_mas_reciente,
        'cliente_mas_antiguo': cliente_mas_antiguo,
    }

    return render(request, 'gestioncliente/dashboard_3.html', context)

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
            return redirect('listar_cliente')
    return render(request, 'gestioncliente/agregar_cliente.html',data)


def buscar_cliente(request):
    if request.method == 'GET':
        nombre = request.GET.get('nombre')

        # Realizar la búsqueda de clientes por nombre
        clientes = Cliente.objects.filter(nombre__icontains=nombre)

        data = {
            'clientes': clientes,
            'nombre_busqueda': nombre
        }
        return render(request, 'gestioncliente/buscar_cliente.html', data)

    return redirect('listar_cliente')
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