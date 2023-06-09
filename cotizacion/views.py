from django.shortcuts import render
from product.models import Producto
from cotizacion.models import Cotizacion,ItemCot
from gestioncliente.models import Cliente
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from registration.models import Profile
from datetime import date
from django.http import HttpResponse,HttpResponseNotAllowed
from django.http import HttpResponse
from io import BytesIO
from zipfile import ZipFile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from datetime import date
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import tempfile
import os
import io
import pandas as pd
import plotly.graph_objects as go

# Create your views here.
def dashboard5(request):
    cotizaciones = Cotizacion.objects.all()

    # Datos útiles
    total_cotizaciones = cotizaciones.count()
    cotizaciones_recientes = cotizaciones.order_by('-fecha')[:5]
    cotizaciones_clientes = [cotizacion.cliente.nombre1 for cotizacion in cotizaciones_recientes]

    # Gráfico 1: Distribución de cotizaciones por cliente
    clientes = [cotizacion.cliente.nombre1 for cotizacion in cotizaciones]
    cliente_count = {}
    for cliente in clientes:
        if cliente in cliente_count:
            cliente_count[cliente] += 1
        else:
            cliente_count[cliente] = 1

    fig1 = go.Figure(data=[go.Pie(labels=list(cliente_count.keys()), values=list(cliente_count.values()))])
    fig1.update_layout(title='Distribución de cotizaciones por cliente')

    # Gráfico 2: Número de cotizaciones por mes
    cotizaciones_df = pd.DataFrame(cotizaciones.values('fecha'))
    cotizaciones_df['mes'] = cotizaciones_df['fecha'].dt.month_name()
    cotizaciones_por_mes = cotizaciones_df['mes'].value_counts().sort_index()

    fig2 = go.Figure(data=[go.Bar(x=cotizaciones_por_mes.index, y=cotizaciones_por_mes.values)])
    fig2.update_layout(title='Número de cotizaciones por mes', xaxis_title='Mes', yaxis_title='Número de cotizaciones')

    # Renderizar el dashboard
    return render(request, 'dashboard_5.html', {
        'total_cotizaciones': total_cotizaciones,
        'cotizaciones_clientes': cotizaciones_clientes,
        'fig1': fig1.to_html(full_html=False, default_height=500),
        'fig2': fig2.to_html(full_html=False, default_height=500)
    })


def crear_cotizacion(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        producto_id = request.POST.get('producto')
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad'))
        descripcion = request.POST.get('descripcion')
        fecha = date.today()
        orden_cotizacion = Cotizacion.objects.create(cliente=cliente,fecha=fecha)
        orden_cotizacion.save()
        item = ItemCot.objects.create(orden_cotizacion=orden_cotizacion, producto=producto, cantidad=cantidad,descripcion=descripcion)
        item.save() 
        return redirect('ver_cotizacion', orden_id=orden_cotizacion.id)
    clientes = Cliente.objects.all() 
    productos = Producto.objects.all()
    messages.add_message(request, messages.INFO, 'Se ha creado su cotización!')
    return render(request, 'crear_cotizacion.html', {'clientes': clientes, 'productos': productos})


def ver_cotizacion(request, orden_id):
    orden = get_object_or_404(Cotizacion, id=orden_id)
    return render(request, 'ver_cotizacion.html', {'orden': orden})


def eliminar_cotizacion(request, orden_id):
    orden = get_object_or_404(Cotizacion, id=orden_id)
    orden.delete()
    messages.add_message(request, messages.INFO, 'Se ha eliminado su cotización!')
    return redirect('listar_cotizacion')

def listar_cotizacion(request):
    busqueda = request.GET.get("buscar")
    filtro_id = request.GET.get("filtro_id")
    ordenes = Cotizacion.objects.all()

    if busqueda:
        ordenes = ordenes.filter(cliente__nombre1__icontains=busqueda)

    if filtro_id:
        try:
            filtro_id = int(filtro_id)
            ordenes = ordenes.filter(id=filtro_id)
        except ValueError:
            return redirect('listar_cotizacion')

    return render(request, 'listar_cotizacion.html', {'ordenes': ordenes, 'buscar': busqueda, 'filtro_id': filtro_id})

def ola(request, orden_id):
    if request.method == 'POST':
        orden = get_object_or_404(Cotizacion, id=orden_id)
        print("alo")
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))
        producto = get_object_or_404(Producto, id=producto_id)
        print("XD")
        item = ItemCot.objects.create(orden_cotizacion=orden, producto=producto, cantidad=cantidad)
        messages.add_message(request, messages.INFO, 'Se ha agregado producto a su cotización!')
        return redirect('ver_cotizacion', orden_id=orden.id)
    else:
        orden = get_object_or_404(Cotizacion, id=orden_id)
        print("LLEGA ACA")
        productos = Producto.objects.all()
        return render(request, 'ola.html', {'orden': orden, 'productos': productos})
    

def eliminar(request, item_id):
    item = get_object_or_404(ItemCot, id=item_id)
    orden_id = item.orden_cotizacion.id
    item.delete()
    messages.add_message(request, messages.INFO, 'Se ha eliminado producto a su cotización!')
    return redirect('ver_cotizacion', orden_id=orden_id)


def eliminar_producto(request, cotizacion_id, producto_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    producto = get_object_or_404(ItemCot, id=producto_id, cotizacion=cotizacion)

    if request.method == 'POST':
        producto.delete()
        return redirect('ver_cotizacion', cotizacion_id=cotizacion.id)

    return render(request, 'eliminar_producto.html', {'cotizacion': cotizacion, 'producto': producto})


def cotizacion_main(request):
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.group_id != 1:
        messages.add_message(request, messages.INFO, 'Intenta ingresar a una area para la que no tiene permisos')
        return redirect('check_group_main')
    template_name = 'cotizacion_main.html'
    return render(request,template_name,{'profile':profile})


def generar_reporte_cotizaciones(request, filtro_id=None):
    filtro_id = request.GET.get("filtro_id")
    filtro_nombre = request.GET.get("filtro_nombre")
    cotizaciones = Cotizacion.objects.all()

    if filtro_id:
        try:
            cotizacion = cotizaciones.get(id=filtro_id)
        except Cotizacion.DoesNotExist:
            return HttpResponse("No se encontró una cotización con ese ID.")

        cotizaciones = [cotizacion]

    if filtro_nombre:
        cotizaciones = cotizaciones.filter(cliente__nombre1__icontains=filtro_nombre)

    if not filtro_id and not filtro_nombre:
        return HttpResponse("Debe especificar al menos un filtro.")

    if filtro_id:
        # Crear el archivo PDF en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte_cotizaciones.pdf"'

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

            data = [['ID', 'Cliente', 'Producto', 'Cantidad', 'Precio Unitario', 'Total']]
            for cotizacion in cotizaciones:
                for item in cotizacion.items.all():
                    data.append([
                        str(cotizacion.id),
                        str(cotizacion.cliente),
                        item.producto.nombre,
                        str(item.cantidad),
                        str(item.producto.precio),
                        str(item.subtotal)
                    ])

            table = Table(data)
            table.setStyle(style_table)

            elements.append(Paragraph('Informe de Cotizaciones', styles['Heading1']))
            elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph('Listado de cotizaciones:', styles['Heading3']))
            elements.append(table)

            document.build(elements)

        # Leer el contenido del archivo temporal y devolverlo como respuesta
        with open(temp_file.name, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')

        # Establecer el encabezado de descarga del archivo adjunto
        response['Content-Disposition'] = 'attachment; filename="reporte_cotizaciones.pdf"'

        # Eliminar el archivo temporal después de enviarlo
        os.remove(temp_file.name)

        return response 
    
def enviar_correo_cotizacion(request):
    if request.method == 'POST':
        filtro_id = request.POST.get('filtro_id')
        cotizacion = None

        if filtro_id:
            try:
                filtro_id = int(filtro_id)
                cotizacion = Cotizacion.objects.filter(id=filtro_id).first()
            except ValueError:
                return redirect('listar_cotizacion')

        if cotizacion:
            cliente = cotizacion.cliente
            asunto = f'Cotización {cotizacion.id}'
            contenido = f'Estimado cliente,\n\nAdjuntamos la cotización con ID {cotizacion.id}.'

            # Generar el archivo PDF en un objeto de tipo BytesIO
            pdf_buffer = io.BytesIO()
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

            data = [['ID', 'Cliente', 'Producto', 'Cantidad', 'Precio Unitario', 'Total']]
            for item in cotizacion.items.all():
                data.append([
                    str(cotizacion.id),
                    str(cotizacion.cliente),
                    item.producto.nombre,
                    str(item.cantidad),
                    str(item.producto.precio),
                    str(item.subtotal)
                ])

            table = Table(data)
            table.setStyle(style_table)

            elements.append(Paragraph('Informe de Cotizaciones', styles['Heading1']))
            elements.append(Paragraph('Fecha: ' + date.today().strftime('%d/%m/%Y'), style_paragraph))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph('Listado de cotizaciones:', styles['Heading3']))
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
                [cliente.correo_electronico],
            )

            # Adjuntar el archivo PDF al correo electrónico especificando el nombre personalizado
            nombre_archivo = f'reporte_cotizacion_{cotizacion.id}.pdf'
            email.attach(nombre_archivo, pdf_content, 'application/pdf')

            # Enviar el correo electrónico
            email.send()

            return render(request, 'confirmacion_correo.html', {'cotizacion': cotizacion})
        else:
            return HttpResponse('No se encontró la cotización correspondiente al ID proporcionado.')
    else:
        return HttpResponseNotAllowed(['POST'])