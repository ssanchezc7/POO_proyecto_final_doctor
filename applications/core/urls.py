from django.urls import path
from applications.core.views.paciente import paciente_find, PacienteListView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView
from applications.core.views.tipo_sangre import (
    TipoSangreListView, TipoSangreCreateView, 
    TipoSangreUpdateView, TipoSangreDeleteView
)
from applications.core.views.tipo_medicamento import (
    TipoMedicamentoListView, TipoMedicamentoCreateView,
    TipoMedicamentoUpdateView, TipoMedicamentoDeleteView
)
from applications.core.views.marca_medicamento import (
    MarcaMedicamentoListView, MarcaMedicamentoCreateView,
    MarcaMedicamentoUpdateView, MarcaMedicamentoDeleteView
)
from applications.core.views.medicamento import (
    MedicamentoListView, MedicamentoCreateView,
    MedicamentoUpdateView, MedicamentoDeleteView
)
from applications.core.views.especialidad import (
    EspecialidadListView, EspecialidadCreateView,
    EspecialidadUpdateView, EspecialidadDeleteView
)
from applications.core.views.diagnostico import (
    DiagnosticoListView, DiagnosticoCreateView,
    DiagnosticoUpdateView, DiagnosticoDeleteView
)
from applications.core.views.cargo import (
    CargoListView, CargoCreateView, CargoUpdateView, CargoDeleteView
)
from applications.core.views.empleado import (
    EmpleadoListView, EmpleadoCreateView, EmpleadoUpdateView, EmpleadoDeleteView
)
from applications.core.views.doctor import (
    DoctorListView, DoctorCreateView, DoctorUpdateView, DoctorDeleteView
)
from applications.core.views.tipo_gasto import (
    TipoGastoListView, TipoGastoCreateView,
    TipoGastoUpdateView, TipoGastoDeleteView
)
from applications.core.views.gasto_mensual import (
    GastoMensualListView, GastoMensualCreateView,
    GastoMensualUpdateView, GastoMensualDeleteView
)

app_name='core' # define un espacio de nombre para la aplicacion
urlpatterns = [
    # Rutas para vistas relacionadas con Pacientes
    path('paciente_find/', paciente_find, name="paciente_find"),
    path('paciente_list/', PacienteListView.as_view(), name="paciente_list"),
    path('paciente_create/', PacienteCreateView.as_view(), name="paciente_create"),
    path('paciente_update/<int:pk>/', PacienteUpdateView.as_view(), name='paciente_update'),
    path('paciente_delete/<int:pk>/', PacienteDeleteView.as_view(), name='paciente_delete'),
    
    # Rutas para Tipos de Sangre
    path('tipo_sangre_list/', TipoSangreListView.as_view(), name="tipo_sangre_list"),
    path('tipo_sangre_create/', TipoSangreCreateView.as_view(), name="tipo_sangre_create"),
    path('tipo_sangre_update/<int:pk>/', TipoSangreUpdateView.as_view(), name='tipo_sangre_update'),
    path('tipo_sangre_delete/<int:pk>/', TipoSangreDeleteView.as_view(), name='tipo_sangre_delete'),

    # Rutas para Tipos de Medicamento
    path('tipo_medicamento_list/', TipoMedicamentoListView.as_view(), name="tipo_medicamento_list"),
    path('tipo_medicamento_create/', TipoMedicamentoCreateView.as_view(), name="tipo_medicamento_create"),
    path('tipo_medicamento_update/<int:pk>/', TipoMedicamentoUpdateView.as_view(), name='tipo_medicamento_update'),
    path('tipo_medicamento_delete/<int:pk>/', TipoMedicamentoDeleteView.as_view(), name='tipo_medicamento_delete'),

    # Rutas para Marcas de Medicamento
    path('marca_medicamento_list/', MarcaMedicamentoListView.as_view(), name="marca_medicamento_list"),
    path('marca_medicamento_create/', MarcaMedicamentoCreateView.as_view(), name="marca_medicamento_create"),
    path('marca_medicamento_update/<int:pk>/', MarcaMedicamentoUpdateView.as_view(), name='marca_medicamento_update'),
    path('marca_medicamento_delete/<int:pk>/', MarcaMedicamentoDeleteView.as_view(), name='marca_medicamento_delete'),

    # Rutas para Medicamentos
    path('medicamento_list/', MedicamentoListView.as_view(), name="medicamento_list"),
    path('medicamento_create/', MedicamentoCreateView.as_view(), name="medicamento_create"),
    path('medicamento_update/<int:pk>/', MedicamentoUpdateView.as_view(), name='medicamento_update'),
    path('medicamento_delete/<int:pk>/', MedicamentoDeleteView.as_view(), name='medicamento_delete'),

    # Rutas para Especialidades Médicas
    path('especialidad_list/', EspecialidadListView.as_view(), name="especialidad_list"),
    path('especialidad_create/', EspecialidadCreateView.as_view(), name="especialidad_create"),
    path('especialidad_update/<int:pk>/', EspecialidadUpdateView.as_view(), name='especialidad_update'),
    path('especialidad_delete/<int:pk>/', EspecialidadDeleteView.as_view(), name='especialidad_delete'),

    # Rutas para Diagnósticos
    path('diagnostico_list/', DiagnosticoListView.as_view(), name="diagnostico_list"),
    path('diagnostico_create/', DiagnosticoCreateView.as_view(), name="diagnostico_create"),
    path('diagnostico_update/<int:pk>/', DiagnosticoUpdateView.as_view(), name='diagnostico_update'),
    path('diagnostico_delete/<int:pk>/', DiagnosticoDeleteView.as_view(), name='diagnostico_delete'),

    # Rutas para Cargos
    path('cargo_list/', CargoListView.as_view(), name="cargo_list"),
    path('cargo_create/', CargoCreateView.as_view(), name="cargo_create"),
    path('cargo_update/<int:pk>/', CargoUpdateView.as_view(), name='cargo_update'),
    path('cargo_delete/<int:pk>/', CargoDeleteView.as_view(), name='cargo_delete'),

    # Rutas para Empleados
    path('empleado_list/', EmpleadoListView.as_view(), name="empleado_list"),
    path('empleado_create/', EmpleadoCreateView.as_view(), name="empleado_create"),
    path('empleado_update/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('empleado_delete/<int:pk>/', EmpleadoDeleteView.as_view(), name='empleado_delete'),

    # Rutas para Doctores
    path('doctor_list/', DoctorListView.as_view(), name="doctor_list"),
    path('doctor_create/', DoctorCreateView.as_view(), name="doctor_create"),
    path('doctor_update/<int:pk>/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctor_delete/<int:pk>/', DoctorDeleteView.as_view(), name='doctor_delete'),

    # Rutas para Tipos de Gasto
    path('tipo_gasto_list/', TipoGastoListView.as_view(), name="tipo_gasto_list"),
    path('tipo_gasto_create/', TipoGastoCreateView.as_view(), name="tipo_gasto_create"),
    path('tipo_gasto_update/<int:pk>/', TipoGastoUpdateView.as_view(), name='tipo_gasto_update'),
    path('tipo_gasto_delete/<int:pk>/', TipoGastoDeleteView.as_view(), name='tipo_gasto_delete'),

    # Rutas para Gastos Mensuales
    path('gasto_mensual_list/', GastoMensualListView.as_view(), name="gasto_mensual_list"),
    path('gasto_mensual_create/', GastoMensualCreateView.as_view(), name="gasto_mensual_create"),
    path('gasto_mensual_update/<int:pk>/', GastoMensualUpdateView.as_view(), name='gasto_mensual_update'),
    path('gasto_mensual_delete/<int:pk>/', GastoMensualDeleteView.as_view(), name='gasto_mensual_delete'),

]