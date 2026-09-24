"""
Vistas para la gestión de pagos y procesamiento con PayPal
"""
import json
import requests
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.db.models import Count, Sum, Q, F
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator as csrf_method_decorator
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

# Importaciones para PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import os

from applications.doctor.models import Pago, DetallePago, Atencion, ServiciosAdicionales
from applications.doctor.forms.pago import (
    DetallePagoForm, PayPalPaymentForm, 
    PagoSearchForm, PagoStatusUpdateForm
)


# Configuración PayPal desde settings
PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET
PAYPAL_MODE = settings.PAYPAL_MODE
PAYPAL_API_URL = settings.PAYPAL_API_URL


class PayPalService:
    """Servicio para manejar la integración con PayPal"""
    
    @staticmethod
    def get_access_token():
        """Obtiene el token de acceso de PayPal"""
        try:
            url = f"{PAYPAL_API_URL}/v1/oauth2/token"
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
            }
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                url, 
                headers=headers, 
                data=data,
                auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                timeout=30  # Agregar timeout
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                print(f"Error obteniendo token PayPal: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error obteniendo token PayPal: {e}")
            return None
    
    @staticmethod
    def create_payment(pago):
        """Crea un pago en PayPal"""
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return None, "No se pudo obtener token de PayPal. Verifica las credenciales."
            
            url = f"{PAYPAL_API_URL}/v1/payments/payment"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            # Verificar que el pago tenga datos válidos
            if not pago.atencion or not pago.atencion.paciente:
                return None, "El pago debe estar asociado a una atención y paciente válidos"
            
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"http://127.0.0.1:8000{reverse('doctor:pago_paypal_success')}",
                    "cancel_url": f"http://127.0.0.1:8000{reverse('doctor:pago_paypal_cancel')}"
                },
                "transactions": [{
                    "item_list": {
                        "items": []
                    },
                    "amount": {
                        "currency": "USD",
                        "total": str(pago.monto_total)
                    },
                    "description": f"Pago médico #{pago.id} - Paciente: {pago.atencion.paciente.nombre_completo}"
                }]
            }
            
            # Agregar detalles de servicios
            detalles = pago.detalles.all()
            if detalles.exists():
                # Si hay detalles específicos, agregarlos
                for detalle in detalles:
                    payment_data["transactions"][0]["item_list"]["items"].append({
                        "name": detalle.servicio_adicional.nombre_servicio,
                        "sku": str(detalle.servicio_adicional.id),
                        "price": str(detalle.precio_unitario),
                        "currency": "USD",
                        "quantity": detalle.cantidad
                    })
            else:
                # Si no hay detalles, agregar un item genérico
                payment_data["transactions"][0]["item_list"]["items"].append({
                    "name": "Consulta Médica",
                    "sku": "CONSULTA",
                    "price": str(pago.monto_total),
                    "currency": "USD",
                    "quantity": 1
                })
            
            response = requests.post(url, headers=headers, data=json.dumps(payment_data), timeout=30)
            
            if response.status_code == 201:
                payment_response = response.json()
                # Buscar URL de aprobación
                approval_url = None
                for link in payment_response.get('links', []):
                    if link.get('rel') == 'approval_url':
                        approval_url = link.get('href')
                        break
                
                return payment_response, approval_url
            else:
                error_detail = response.text
                print(f"Error PayPal: {response.status_code} - {error_detail}")
                return None, f"Error PayPal {response.status_code}: {error_detail[:100]}..."
                
        except Exception as e:
            print(f"Excepción en create_payment: {str(e)}")
            return None, f"Error creando pago PayPal: {str(e)}"
    
    @staticmethod
    def execute_payment(payment_id, payer_id):
        """Ejecuta un pago aprobado en PayPal"""
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return False
            
            url = f"{PAYPAL_API_URL}/v1/payments/payment/{payment_id}/execute"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            execute_data = {
                "payer_id": payer_id
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(execute_data), timeout=30)
            
            if response.status_code == 200:
                payment_response = response.json()
                # Verificar que el pago fue aprobado
                return payment_response.get('state') == 'approved'
            else:
                print(f"Error ejecutando pago PayPal: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error ejecutando pago PayPal: {str(e)}")
            return False
    
    @staticmethod
    def get_payment_details(payment_id):
        """Obtiene los detalles de un pago desde PayPal"""
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return None
            
            url = f"{PAYPAL_API_URL}/v1/payments/payment/{payment_id}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo detalles de pago PayPal: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error obteniendo detalles de pago PayPal: {str(e)}")
            return None


@method_decorator(login_required, name='dispatch')
class PagoListView(ListView):
    """Vista para listar todos los pagos"""
    model = Pago
    template_name = 'doctor/pagos/lista_pagos.html'
    context_object_name = 'pagos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Pago.objects.select_related('atencion__paciente').order_by('-fecha_creacion')
        
        # Filtros de búsqueda
        form = PagoSearchForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('paciente'):
                queryset = queryset.filter(
                    atencion__paciente__nombres__icontains=form.cleaned_data['paciente']
                )
            if form.cleaned_data.get('estado'):
                queryset = queryset.filter(estado=form.cleaned_data['estado'])
            if form.cleaned_data.get('fecha_desde'):
                queryset = queryset.filter(fecha_creacion__gte=form.cleaned_data['fecha_desde'])
            if form.cleaned_data.get('fecha_hasta'):
                queryset = queryset.filter(fecha_creacion__lte=form.cleaned_data['fecha_hasta'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PagoSearchForm(self.request.GET)
        return context


@method_decorator(login_required, name='dispatch')
class PagoDetailView(DetailView):
    """Vista para ver detalles de un pago"""
    model = Pago
    template_name = 'doctor/pagos/detalle_pago.html'
    context_object_name = 'pago'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener detalles del pago con servicios relacionados
        context['detalles'] = self.object.detalles.select_related('servicio_adicional').all()
        
        # Formularios para PayPal y actualización de estado
        context['paypal_form'] = PayPalPaymentForm()
        context['status_form'] = PagoStatusUpdateForm(instance=self.object)
        
        # Otros pagos del mismo paciente (excluyendo el actual)
        paciente = self.object.atencion.paciente
        context['otros_pagos'] = Pago.objects.filter(
            atencion__paciente=paciente
        ).exclude(id=self.object.id).select_related(
            'atencion__paciente'
        ).order_by('-fecha_creacion')[:5]
        
        return context



@login_required
def agregar_detalle_pago_view(request, pago_id):
    """Vista para agregar múltiples servicios adicionales a un pago"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    if request.method == 'POST':
        # Verificar si recibimos datos de múltiples servicios
        servicios_data = request.POST.get('servicios_data')
        
        if servicios_data:
            try:
                # Procesar múltiples servicios
                servicios = json.loads(servicios_data)
                servicios_agregados = 0
                total_agregado = Decimal('0.00')
                
                for servicio_data in servicios:
                    # Validar datos del servicio
                    servicio_id = servicio_data.get('id')
                    cantidad = int(servicio_data.get('cantidad', 1))
                    precio = Decimal(str(servicio_data.get('precio', 0)))
                    
                    # Obtener el servicio adicional
                    try:
                        servicio_adicional = ServiciosAdicionales.objects.get(
                            id=servicio_id,
                            activo=True
                        )
                        
                        # Verificar que no sea un medicamento ni consulta médica
                        if (servicio_adicional.nombre_servicio.startswith('Medicamento:') or 
                            'Consulta Médica' in servicio_adicional.nombre_servicio):
                            continue
                        
                        # Crear el detalle del pago
                        detalle = DetallePago(
                            pago=pago,
                            servicio_adicional=servicio_adicional,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=precio * cantidad,
                            descuento_porcentaje=Decimal('0.00'),
                            aplica_seguro=False
                        )
                        detalle.save()
                        
                        servicios_agregados += 1
                        total_agregado += detalle.subtotal
                        
                    except ServiciosAdicionales.DoesNotExist:
                        continue
                
                if servicios_agregados > 0:
                    messages.success(
                        request, 
                        f'{servicios_agregados} servicio(s) agregado(s) al pago exitosamente. '
                        f'Monto agregado: ${total_agregado}. Nuevo total: ${pago.monto_total}'
                    )
                else:
                    messages.warning(request, 'No se pudo agregar ningún servicio al pago.')
                    
                return redirect('doctor:detalle_pago', pk=pago.id)
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                messages.error(request, 'Error al procesar los servicios seleccionados.')
                
        else:
            # Procesar formulario individual (mantenemos compatibilidad)
            form = DetallePagoForm(request.POST)
            if form.is_valid():
                detalle = form.save(commit=False)
                detalle.pago = pago
                detalle.save()
                
                messages.success(
                    request, 
                    f'Servicio "{detalle.servicio_adicional.nombre_servicio}" agregado al pago exitosamente. '
                    f'Nuevo total: ${pago.monto_total}'
                )
                return redirect('doctor:detalle_pago', pk=pago.id)
    else:
        form = DetallePagoForm()
    
    # Obtener servicios adicionales disponibles (excluyendo medicamentos y consulta médica)
    servicios_disponibles = ServiciosAdicionales.objects.filter(
        activo=True
    ).exclude(
        nombre_servicio__startswith='Medicamento:'
    ).exclude(
        nombre_servicio__icontains='Consulta Médica'
    ).order_by('nombre_servicio')
    
    # Preparamos los datos para JSON, usando el nombre de campo correcto 'costo_servicio'
    servicios_list = list(
        servicios_disponibles.values(
            "id", "nombre_servicio", "costo_servicio", "descripcion"
        )
    )

    # Renombramos 'costo_servicio' a 'precio' para que coincida con el JavaScript
    for servicio in servicios_list:
        servicio["precio"] = servicio.pop("costo_servicio")

    servicios_json = json.dumps(servicios_list, cls=DjangoJSONEncoder)
    
    context = {
        'form': form,
        'pago': pago,
        'servicios_disponibles': servicios_disponibles,
        'servicios_json': servicios_json,  # Pasar el JSON al contexto
        'title': f'Agregar Detalle - Pago #{pago.id}'
    }
    return render(request, 'doctor/pagos/agregar_detalle.html', context)


@login_required
@require_POST
def eliminar_detalle_pago_view(request, detalle_id):
    """Vista para eliminar un detalle de pago y devolver JSON"""
    try:
        detalle = get_object_or_404(DetallePago, id=detalle_id)
        pago = detalle.pago
        
        # Guardar el subtotal antes de eliminar para restar del total
        subtotal_eliminado = detalle.subtotal
        
        # Eliminar el detalle (las signals se encargarán de recalcular el total)
        detalle.delete()
        
        # Refrescar el pago desde la base de datos para obtener el total actualizado
        pago.refresh_from_db()

        return JsonResponse({
            'success': True, 
            'nuevo_total': str(pago.monto_total),
            'subtotal_eliminado': str(subtotal_eliminado)
        })

    except DetallePago.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El detalle no existe.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def iniciar_pago_paypal_view(request, pago_id):
    """Vista para iniciar el proceso de pago con PayPal"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    if pago.estado != 'pendiente':
        messages.error(request, 'Este pago ya no está disponible para procesar')
        return redirect('doctor:detalle_pago', pk=pago.id)
    
    # Verificar que el pago tenga un monto válido
    if pago.monto_total <= 0:
        messages.error(request, 'El pago debe tener un monto mayor a $0.00')
        return redirect('doctor:detalle_pago', pk=pago.id)
    
    # Usar la API real de PayPal
    try:
        payment_response, approval_url = PayPalService.create_payment(pago)
        
        if payment_response and approval_url:
            # Guardar el ID de pago de PayPal
            pago.referencia_externa = payment_response.get('id')
            pago.metodo_pago = 'paypal'
            pago.save()
            
            # Redirigir al usuario a PayPal para aprobar el pago
            return redirect(approval_url)
        else:
            error_msg = approval_url if approval_url else "Error desconocido"
            messages.error(request, f'Error al crear el pago en PayPal: {error_msg}')
            return redirect('doctor:detalle_pago', pk=pago.id)
            
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('doctor:detalle_pago', pk=pago.id)


@login_required
def pago_paypal_success_view(request, payment_id=None, pago_id=None):
    """Vista de éxito para pagos PayPal"""
    
    # Obtener parámetros de PayPal
    payment_id_get = request.GET.get('paymentId') or payment_id
    payer_id = request.GET.get('PayerID')
    
    if not payment_id_get:
        messages.error(request, 'ID de pago no encontrado')
        return redirect('doctor:lista_pagos')
    
    try:
        # Buscar el pago por referencia externa (PayPal payment ID)
        pago = Pago.objects.get(referencia_externa=payment_id_get)
        
        if payer_id:
            # Si tenemos PayerID, ejecutar el pago en PayPal
            success = PayPalService.execute_payment(payment_id_get, payer_id)
            
            if success:
                # Actualizar el estado del pago
                pago.estado = 'pagado'
                pago.fecha_pago = timezone.now()
                pago.save()
                
                messages.success(request, f'¡Pago completado exitosamente! ID: {payment_id_get}')
                return redirect('doctor:detalle_pago', pk=pago.id)
            else:
                pago.estado = 'fallido'
                pago.save()
                messages.error(request, 'Error al ejecutar el pago en PayPal')
                return redirect('doctor:detalle_pago', pk=pago.id)
        else:
            # Para retrocompatibilidad con la simulación (si se usa pago_id)
            if pago_id:
                pago = get_object_or_404(Pago, id=pago_id)
                pago.estado = 'pagado'
                pago.fecha_pago = timezone.now()
                pago.save()
                
                messages.success(request, f'¡Pago completado exitosamente! ID: {payment_id_get}')
                return redirect('doctor:detalle_pago', pk=pago.id)
            else:
                messages.error(request, 'Información de pago incompleta')
                return redirect('doctor:lista_pagos')
        
    except Pago.DoesNotExist:
        messages.error(request, 'Pago no encontrado')
        return redirect('doctor:lista_pagos')
    except Exception as e:
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('doctor:lista_pagos')


@login_required
def pago_paypal_cancel_view(request):
    """Vista de cancelación para pagos PayPal"""
    payment_id = request.GET.get('paymentId')
    
    if payment_id:
        try:
            # Buscar el pago por referencia externa (PayPal payment ID)
            pago = Pago.objects.get(referencia_externa=payment_id)
            pago.estado = 'cancelado'
            pago.save()
            
            messages.warning(request, f'Pago cancelado. ID: {payment_id}')
            return redirect('doctor:detalle_pago', pk=pago.id)
        except Pago.DoesNotExist:
            messages.warning(request, 'Pago cancelado')
    else:
        messages.info(request, 'Pago cancelado por el usuario')
    
    return redirect('doctor:lista_pagos')


@login_required
@require_POST
def actualizar_estado_pago_view(request, pago_id):
    """Vista para actualizar manualmente el estado de un pago"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    form = PagoStatusUpdateForm(request.POST, instance=pago)
    if form.is_valid():
        form.save()
        messages.success(request, f'Estado del pago actualizado a: {pago.get_estado_display()}')
    else:
        messages.error(request, 'Error actualizando el estado del pago')
    
    return redirect('doctor:detalle_pago', pk=pago.id)


@login_required
def dashboard_pagos_view(request):
    """Dashboard con estadísticas de pagos"""
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import datetime, timedelta
    import calendar
    
    # Estadísticas básicas
    total_pagos = Pago.objects.count()
    pagos_pendientes = Pago.objects.filter(estado='pendiente').count()
    pagos_pagados = Pago.objects.filter(estado='pagado').count()
    pagos_cancelados = Pago.objects.filter(estado='cancelado').count()
    total_recaudado = Pago.objects.filter(estado='pagado').aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    
    # Datos para gráficos - últimos 12 meses
    now = timezone.now()
    meses_labels = []
    ingresos_mensuales = []
    
    for i in range(11, -1, -1):
        fecha = now - timedelta(days=30 * i)
        mes_nombre = calendar.month_name[fecha.month][:3]  # Primeras 3 letras del mes
        meses_labels.append(f"{mes_nombre} {fecha.year}")
        
        # Calcular ingresos del mes
        inicio_mes = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if fecha.month == 12:
            fin_mes = inicio_mes.replace(year=fecha.year + 1, month=1) - timedelta(days=1)
        else:
            fin_mes = inicio_mes.replace(month=fecha.month + 1) - timedelta(days=1)
        
        ingresos_mes = Pago.objects.filter(
            estado='pagado',
            fecha_pago__range=[inicio_mes, fin_mes]
        ).aggregate(Sum('monto_total'))['monto_total__sum'] or 0
        
        ingresos_mensuales.append(float(ingresos_mes))
    
    # Pagos recientes
    pagos_recientes = Pago.objects.select_related('atencion__paciente').order_by('-fecha_creacion')[:5]
    
    # Otros pagos del paciente (para el template de detalle)
    otros_pagos = []
    
    context = {
        'total_pagos': total_pagos,
        'pagos_pendientes': pagos_pendientes,
        'pagos_pagados': pagos_pagados,
        'pagos_cancelados': pagos_cancelados,
        'total_recaudado': total_recaudado,
        'pagos_recientes': pagos_recientes,
        'meses_labels': json.dumps(meses_labels),
        'ingresos_mensuales': json.dumps(ingresos_mensuales),
        'otros_pagos': otros_pagos,
    }
    
    return render(request, 'doctor/pagos/dashboard.html', context)


@login_required
def test_paypal_connection_view(request):
    """Vista para probar la conexión con PayPal"""
    try:
        access_token = PayPalService.get_access_token()
        if access_token:
            messages.success(request, '✅ Conexión con PayPal exitosa! Token obtenido correctamente.')
        else:
            messages.error(request, '❌ Error al conectar con PayPal. Verifica las credenciales.')
    except Exception as e:
        messages.error(request, f'❌ Error de conexión: {str(e)}')
    
    return redirect('doctor:dashboard_pagos')


@login_required
def generar_recibo_pdf_view(request, pago_id):
    """Vista para generar y descargar el recibo en PDF"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    # Crear el HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_pago_{pago.id}.pdf"'
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4F46E5')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#6B7280')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Contenido del PDF
    story = []
    
    # Encabezado
    story.append(Paragraph("RECIBO DE PAGO MÉDICO", title_style))
    story.append(Spacer(1, 12))
    
    # Información del recibo
    recibo_data = [
        ['Número de Recibo:', f'#{pago.id}'],
        ['Fecha de Emisión:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ['Estado del Pago:', pago.get_estado_display()],
        ['Descripción:', f'Pago médico - Atención #{pago.atencion.id}' if pago.atencion else 'Pago médico'],
    ]
    
    if pago.fecha_pago:
        recibo_data.append(['Fecha de Pago:', pago.fecha_pago.strftime('%d/%m/%Y %H:%M')])
    
    if pago.metodo_pago:
        recibo_data.append(['Método de Pago:', pago.get_metodo_pago_display()])
    
    if pago.referencia_externa:
        recibo_data.append(['Referencia:', pago.referencia_externa])
    
    recibo_table = Table(recibo_data, colWidths=[2*inch, 3*inch])
    recibo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(recibo_table)
    story.append(Spacer(1, 20))
    
    # Información del paciente
    story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
    
    paciente_data = [
        ['Nombre:', pago.atencion.paciente.nombre_completo],
        ['Documento:', pago.atencion.paciente.cedula_ecuatoriana],
        ['Fecha de Atención:', pago.atencion.fecha_atencion.strftime('%d/%m/%Y %H:%M')],
        ['Motivo de Consulta:', pago.atencion.motivo_consulta[:100] + '...' if len(pago.atencion.motivo_consulta) > 100 else pago.atencion.motivo_consulta],
    ]
    
    if pago.atencion.paciente.telefono:
        paciente_data.append(['Teléfono:', pago.atencion.paciente.telefono])
    
    # Manejar múltiples diagnósticos (ManyToMany)
    diagnosticos = pago.atencion.diagnostico.all()
    if diagnosticos.exists():
        diagnosticos_texto = ', '.join([diag.descripcion for diag in diagnosticos])
        paciente_data.append(['Diagnóstico(s):', diagnosticos_texto[:100] + '...' if len(diagnosticos_texto) > 100 else diagnosticos_texto])
    
    
    paciente_table = Table(paciente_data, colWidths=[2*inch, 3*inch])
    paciente_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
    ]))
    
    story.append(paciente_table)
    story.append(Spacer(1, 20))
    
    # Detalles del pago
    story.append(Paragraph("DETALLES DEL PAGO", subtitle_style))
    
    # Encabezados de la tabla de detalles
    detalle_data = [['Servicio', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
    detalles = pago.detalles.all()
    total_cantidad = 0
    
    if detalles.exists():
        for detalle in detalles:
            detalle_data.append([
                detalle.servicio_adicional.nombre_servicio,
                str(detalle.cantidad),
                f'${detalle.precio_unitario:.2f}',
                f'${detalle.subtotal:.2f}'
            ])
            total_cantidad += detalle.cantidad
    else:
        detalle_data.append([
            'Consulta Médica General',
            '1',
            f'${pago.monto_total:.2f}',
            f'${pago.monto_total:.2f}'
        ])
        total_cantidad = 1
    
    # Fila de total
    detalle_data.append(['', '', 'TOTAL:', f'${pago.monto_total:.2f}'])
    
    detalle_table = Table(detalle_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1*inch])
    detalle_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Contenido
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Servicios alineados a la izquierda
        ('ALIGN', (1, 1), (-1, -2), 'CENTER'),  # Números centrados
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9FAFB')]),
        
        # Fila de total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, -1), (1, -1), 'RIGHT'),
        ('ALIGN', (2, -1), (-1, -1), 'CENTER'),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#4F46E5')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#6B7280')),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(detalle_table)
    story.append(Spacer(1, 30))
    
    # Pie de página con información adicional
    footer_text = f"""
    <para align="center">
    <b>Sistema de Gestión Médica</b><br/>
    Este recibo es un comprobante oficial del pago realizado.<br/>
    Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}
    </para>
    """
    
    story.append(Paragraph(footer_text, normal_style))
    
    # Generar el PDF
    doc.build(story)
    
    # Obtener el valor del buffer y cerrar
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
