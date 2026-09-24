from django.urls import path

from applications.doctor.views.atencion_medica import AtencionListView, AtencionCreateView, AtencionUpdateView, \
    AtencionDeleteView, AtencionDetailJSONView
from applications.doctor.views.horario_atencion import (
    HorarioAtencionListView,
    HorarioAtencionCreateView,
    HorarioAtencionUpdateView,
    HorarioAtencionDeleteView
)
from applications.doctor.views.cita_medica import (
    CitaMedicaListView,
    CitaMedicaCreateView,
    CitaMedicaUpdateView,
    CitaMedicaDeleteView,
    CitaMedicaCalendarioView,
    AjaxCalendarioDatosView,
    AjaxHorariosDisponiblesView,
    AjaxCrearCitaView
)
from applications.doctor.views.servicios_adicionales import (
    ServiciosAdicionalesListView,
    ServiciosAdicionalesCreateView,
    ServiciosAdicionalesUpdateView,
    ServiciosAdicionalesDeleteView
)
from applications.doctor.views.pagos import (
    PagoListView,
    PagoDetailView,
    agregar_detalle_pago_view,
    iniciar_pago_paypal_view,
    pago_paypal_success_view,
    pago_paypal_cancel_view,
    actualizar_estado_pago_view,
    eliminar_detalle_pago_view,
    dashboard_pagos_view,
    test_paypal_connection_view,
    generar_recibo_pdf_view
)

app_name='doctor' # define un espacio de nombre para la aplicacion
urlpatterns = [
    # Rutas  para vistas relacionadas con Doctor
    path('atencion_list/', AtencionListView.as_view(), name="atencion_list"),
    path('atencion_create/', AtencionCreateView.as_view(), name="atencion_create"),
    path('atencion_update/<int:pk>/', AtencionUpdateView.as_view(), name="atencion_update"),
    path('atencion_delete/<int:pk>/', AtencionDeleteView.as_view(), name="atencion_delete"),
    path('atencion_detail/<int:pk>/', AtencionDetailJSONView.as_view(), name="atencion_detail_json"),
    
    # Rutas para Horarios de Atención
    path('horario_atencion_list/', HorarioAtencionListView.as_view(), name="horario_atencion_list"),
    path('horario_atencion_create/', HorarioAtencionCreateView.as_view(), name="horario_atencion_create"),
    path('horario_atencion_update/<int:pk>/', HorarioAtencionUpdateView.as_view(), name='horario_atencion_update'),
    path('horario_atencion_delete/<int:pk>/', HorarioAtencionDeleteView.as_view(), name='horario_atencion_delete'),
    
    # Rutas para Citas Médicas
    path('cita_medica_list/', CitaMedicaListView.as_view(), name="cita_medica_list"),
    path('cita_medica_create/', CitaMedicaCreateView.as_view(), name="cita_medica_create"),
    path('cita_medica_update/<int:pk>/', CitaMedicaUpdateView.as_view(), name="cita_medica_update"),
    path('cita_medica_delete/<int:pk>/', CitaMedicaDeleteView.as_view(), name="cita_medica_delete"),
    path('cita_medica_calendario/', CitaMedicaCalendarioView.as_view(), name="cita_medica_calendario"),
    
    # Rutas para Servicios Adicionales
    path('servicios_adicionales_list/', ServiciosAdicionalesListView.as_view(), name="servicios_adicionales_list"),
    path('servicios_adicionales_create/', ServiciosAdicionalesCreateView.as_view(), name="servicios_adicionales_create"),
    path('servicios_adicionales_update/<int:pk>/', ServiciosAdicionalesUpdateView.as_view(), name='servicios_adicionales_update'),
    path('servicios_adicionales_delete/<int:pk>/', ServiciosAdicionalesDeleteView.as_view(), name='servicios_adicionales_delete'),
    
    # Rutas AJAX para Citas Médicas
    path('ajax/calendario-datos/', AjaxCalendarioDatosView.as_view(), name="ajax_calendario_datos"),
    path('ajax/horarios-disponibles/', AjaxHorariosDisponiblesView.as_view(), name="ajax_horarios_disponibles"),
    path('ajax/crear-cita/', AjaxCrearCitaView.as_view(), name="ajax_crear_cita"),
    
    # Rutas para Gestión de Pagos
    path('pagos/', PagoListView.as_view(), name="lista_pagos"),
    path('pagos/dashboard/', dashboard_pagos_view, name="dashboard_pagos"),
    path('pagos/<int:pk>/', PagoDetailView.as_view(), name="detalle_pago"),
    path('pagos/<int:pago_id>/agregar-detalle/', agregar_detalle_pago_view, name="agregar_detalle_pago"),
    path('pagos/detalle/<int:detalle_id>/eliminar/', eliminar_detalle_pago_view, name="confirmar_eliminar_detalle"),
    path('pagos/<int:pago_id>/actualizar-estado/', actualizar_estado_pago_view, name="actualizar_estado_pago"),
    path('pagos/<int:pago_id>/recibo-pdf/', generar_recibo_pdf_view, name="generar_recibo_pdf"),
    
    # Rutas para PayPal
    path('pagos/<int:pago_id>/paypal/', iniciar_pago_paypal_view, name="procesar_pago_paypal"),
    path('pagos/paypal/success/', pago_paypal_success_view, name="pago_paypal_success"),
    path('pagos/paypal/cancel/', pago_paypal_cancel_view, name="pago_paypal_cancel"),
    path('pagos/paypal/test/', test_paypal_connection_view, name="test_paypal_connection"),
]