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
from product.models import Producto
from .forms import ProductoForm
from prov.models import Proveedor
from django.views.generic import View
from .models import Producto
from django.db.models import Q
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.template import Context
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from datetime import date
from django.urls import reverse

@login_required
def listar_producto(request):
    busqueda = request.GET.get("buscar")
    productos = Producto.objects.all()

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    if 'generar_reporte' in request.GET:
        return redirect(reverse('generar_reporte') + '?buscar=' + busqueda)
    
    if not busqueda:
        productos = Producto.objects.all()

    return render(request, 'product/listar.html', {'productos': productos, 'buscar': busqueda})




@login_required

def generar_reporte(request):
    busqueda = request.GET.get("buscar")
    productos = Producto.objects.all()
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    data = []
    data.append(['Nombre', 'Precio', 'Descripción', 'Talla', 'Categoría'])
    for producto in productos:
        data.append([producto.nombre, producto.precio, producto.descripcion, producto.talla, producto.categoria.nombre])
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
    elements = [Paragraph('Informe de Productos', styles['Heading1'])]
    elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
    elements.append(Paragraph('Listado de productos:', styles['Heading3']))
    elements.append(table)

    doc.build(elements)

    return response








@login_required
def ejemplos_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'product/ejemplos_main.html'
    return render(request,template_name,{'profile':profile})

#PRODUCTOS
@login_required
def agregar_producto(request):

    data = {
        'form': ProductoForm()
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.add_message(request, messages.INFO, 'Producto creado!')
    return render(request, 'product/agregar.html',data)



    # profile = Profile.objects.get(user_id=request.user.id)
    # if profile.group_id != 1:
    #     messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
    #     return redirect('check_group_main')
    # template_name = 'ejemplos/agregar.html'
    # return render(request,template_name,{'profile':profile})
#@login_required
#def listar_producto(request):
    #productos = Producto.objects.all()
    #data={
        #'productos': productos
    #}
    #return render(request, 'product/listar.html',data)
@login_required
def actualizar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    data ={
        'form': ProductoForm(instance=producto)
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST,instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_producto")
    messages.add_message(request, messages.INFO, 'Producto actualizado!')
    return render(request, 'product/modificar.html',data)
@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.add_message(request, messages.INFO, 'Producto eliminado!')
    return redirect(to="listar_producto")
#CARGA MASIVA PRODUCTO
@login_required
def ejemplos_carga_masiva(request):
    profiles = Profile.objects.get(user_id = request.user.id)
    if profiles.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'product/ejemplos_carga_masiva.html'
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
    columns = ['Nombre Producto','Precio','Descripcion','Talla','Categoria']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/MM/yyyy'
    for row in range(1):
        row_num += 1
        for col_num in range(5):
            if col_num == 0:
                ws.write(row_num, col_num, 'ej: producto' , font_style)
            if col_num == 1:                           
                ws.write(row_num, col_num, '10000' , font_style)
            if col_num == 2:                           
                ws.write(row_num, col_num, 'Polera de diseñador...' , font_style)
            if col_num == 3:                           
                ws.write(row_num, col_num, 'xs,s,m,l,xl' , font_style)
            if col_num == 4:                           
                ws.write(row_num, col_num, '1,2,3...' , font_style)
    wb.save(response)
    return response  

@login_required
def ejemplos_carga_masiva_save(request):
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
            precio = int(item[2])
            descripcion = str(item[3])            
            talla = str(item[4])
            categoria_id = str(item[5])
            producto_save = Producto(
                nombre = nombre,            
                precio = precio,
                descripcion = descripcion,            
                talla = talla,
                categoria_id = categoria_id,         
                
                )
            producto_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('ejemplos_carga_masiva')    
#####################################