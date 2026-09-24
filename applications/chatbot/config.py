"""
Configuración específica para el chatbot médico
"""

# Configuración de la API de Gemini
GEMINI_CONFIG = {
    'model_name': 'gemini-pro',
    'temperature': 0.7,
    'max_tokens': 1000,
    'timeout': 30,  # segundos
}

# Configuración de respuestas del chatbot
CHATBOT_RESPONSES = {
    'welcome_message': """
¡Hola! Soy tu asistente médico virtual. Puedo ayudarte con:

• **Información de pacientes** - Buscar datos, historial médico
• **Consulta de citas** - Horarios, estados, programación
• **Datos de doctores** - Especialidades, disponibilidad
• **Especialidades médicas** - Lista de especialidades disponibles
• **Medicamentos** - Stock, precios, información
• **Información médica web** - Búsqueda de información sobre medicamentos
• **Estadísticas** - Reportes de la clínica
• **Diagnósticos** - Información sobre enfermedades

**Ejemplos de consultas:**
- "¿Cuántos pacientes tengo registrados?"
- "Busca información del paciente con cédula 1234567890"
- "¿Qué citas tengo hoy?"
- "¿Qué especialidades tenemos disponibles?"
- "¿Cuántos doctores hay por especialidad?"
- "Para qué sirve el paracetamol"
- "¿Qué es la amoxicilina?"
- "Muestra estadísticas de este mes"
- "¿Cuál es el stock del medicamento X?"
    """,
    
    'error_message': 'Lo siento, hubo un error al procesar tu consulta. Por favor intenta nuevamente.',
    'no_data_message': 'No se encontraron datos para tu consulta.',
    'processing_message': 'Procesando tu consulta...',
}

# Configuración de comandos especiales
SPECIAL_COMMANDS = {
    'help': ['ayuda', 'help', 'comandos'],
    'clear': ['limpiar', 'clear', 'borrar'],
    'stats': ['estadisticas', 'stats', 'reportes'],
    'patients': ['pacientes', 'patients'],
    'appointments': ['citas', 'appointments', 'consultas'],
    'doctors': ['doctores', 'doctors', 'medicos'],
    'medications': ['medicamentos', 'medications', 'medicina'],
}

# Configuración de patrones de reconocimiento
RECOGNITION_PATTERNS = {
    'cedula': r'\b\d{10}\b',
    'phone': r'\b\d{7,10}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    'time': r'\b\d{1,2}:\d{2}\b',
}
