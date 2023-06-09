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
import plotly.graph_objects as go

from django.shortcuts import render, redirect
from .forms import ProductoForm
from .models import Producto
from django.contrib import messages


def dashboard1(request):

    # Obtener todos los productos
    productos = Producto.objects.all()

    # Gráfico de barras: Stock por producto
    nombres_productos = [producto.nombre for producto in productos]
    stock_productos = [producto.stock for producto in productos]

    fig1 = go.Figure(data=go.Bar(x=nombres_productos, y=stock_productos))
    fig1.update_layout(title='Stock por producto')

    # Gráfico de pastel: Distribución de precios de los productos
    precios = [producto.precio for producto in productos]
    labels2 = ['<10000', '10000-20000', '20000-25000', '25000-35000', '>35000']
    values2 = [
        len([precio for precio in precios if precio < 10000]),
        len([precio for precio in precios if 10000 <= precio < 20000]),
        len([precio for precio in precios if 20000 <= precio < 25000]),
        len([precio for precio in precios if 25000 <= precio < 35000]),
        len([precio for precio in precios if precio >= 35000])
    ]

    fig2 = go.Figure(data=[go.Pie(labels=labels2, values=values2)])
    fig2.update_layout(title='Distribución de precios de los productos')

    # Datos útiles
    cantidad_productos = len(productos)
    producto_mas_caro = max(productos, key=lambda producto: producto.precio)
    producto_mas_barato = min(productos, key=lambda producto: producto.precio)

    context = {
        'plot_div1': fig1.to_html(full_html=False),
        'plot_div2': fig2.to_html(full_html=False),
        'cantidad_productos': cantidad_productos,
        'producto_mas_caro': producto_mas_caro,
        'producto_mas_barato': producto_mas_barato,
    }

    return render(request, 'product/dashboard1.html',context)

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

def generar_reporte_prod(request):
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
from django.shortcuts import render, redirect
from .forms import ProductoForm
from .models import Producto
from django.contrib import messages

def agregar_producto(request):
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.add_message(request, messages.SUCCESS, 'Producto creado!')
            return redirect(to="listar_producto")
    else:
        formulario = ProductoForm()

    proveedores = Proveedor.objects.all()
    data = {
        'form': formulario,
        'proveedores': proveedores,
    }

    return render(request, 'product/agregar.html', data)



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
    proveedores = Proveedor.objects.all()  # Obtén la lista de proveedores
    data = {
        'form': ProductoForm(instance=producto),
        'proveedores': proveedores,  # Pasa la lista de proveedores al contexto
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_producto")
    messages.add_message(request, messages.INFO, 'Producto actualizado!')
    return render(request, 'product/modificar.html', data)

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
    columns = ['Nombre Producto','Precio','Descripcion','Talla','Categoria','Stock']
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
                ws.write(row_num, col_num, 'ej: producto' , font_style)
            if col_num == 1:                           
                ws.write(row_num, col_num, '10000' , font_style)
            if col_num == 2:                           
                ws.write(row_num, col_num, 'Polera de diseñador...' , font_style)
            if col_num == 3:                           
                ws.write(row_num, col_num, 'xs,s,m,l,xl' , font_style)
            if col_num == 4:                           
                ws.write(row_num, col_num, '1,2,3...' , font_style)
            if col_num == 5:                           
                ws.write(row_num, col_num, 'Digite el stock' , font_style)
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
            stock = int(item[6])
            producto_save = Producto(
                nombre = nombre,            
                precio = precio,
                descripcion = descripcion,            
                talla = talla,
                categoria_id = categoria_id,   
                stock = stock,      
                )
            producto_save.save()
        messages.add_message(request, messages.INFO, 'Carga masiva finalizada, se importaron '+str(acc)+' registros')
        return redirect('ejemplos_carga_masiva')    
#####################################