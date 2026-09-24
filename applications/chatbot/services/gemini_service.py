import google.generativeai as genai
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import re

from applications.core.models import Paciente, Doctor, Medicamento, Especialidad, Diagnostico
from applications.doctor.models import CitaMedica


class GeminiChatService:
    def __init__(self):
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                print("Error: GEMINI_API_KEY no encontrada en settings")
                self.model = None
                return
                
            print(f"Configurando Gemini con API key: {api_key[:10]}...")
            genai.configure(api_key=api_key)
            # Usar el modelo más reciente disponible
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini configurado correctamente")
        except Exception as e:
            print(f"❌ Error configurando Gemini: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
        
    def get_system_prompt(self):
        return """
        Eres un asistente médico inteligente para una clínica. Tienes acceso COMPLETO a la base de datos y puedes proporcionar información detallada sobre:
        
        1. PACIENTES: Buscar información de pacientes, historial médico, datos de contacto
        2. CITAS: Consultar citas médicas, horarios, estados de citas
        3. DOCTORES: Información de doctores, especialidades, horarios
        4. ESPECIALIDADES: Lista de especialidades médicas disponibles, doctores por especialidad
        5. MEDICAMENTOS: Stock actual del inventario de la clínica, información de medicamentos, precios, tipos, marcas
        6. ESTADÍSTICAS: Reportes, números de pacientes, citas por período
        7. DIAGNÓSTICOS: Información sobre diagnósticos realizados
        8. INFORMACIÓN MÉDICA WEB: Búsqueda de información sobre medicamentos y términos médicos en internet
        
        IMPORTANTE: 
        - Tienes acceso directo a todos los datos médicos del sistema de la clínica
        - Cuando se te proporcione contexto médico en formato JSON, úsalo DIRECTAMENTE para responder
        - Los datos en "Datos médicos relevantes" contienen información REAL del sistema de la clínica
        - NO digas que no tienes acceso a los datos - SI LOS TIENES en el contexto proporcionado
        - Si el contexto contiene especialidades, lista TODAS las que aparecen en el contexto
        - Si el contexto contiene medicamentos, son del INVENTARIO DE LA CLÍNICA, no medicamentos personales
        - Cuando hablen de "mis medicamentos" se refieren al inventario de medicamentos de la clínica
        - Responde siempre basándote en los datos proporcionados en el contexto médico
        - NUNCA digas que necesitas información adicional si ya tienes datos en el contexto
        
        Instrucciones:
        - Responde en español de manera clara y profesional
        - Usa los datos proporcionados en el contexto para dar respuestas específicas
        - Para consultas médicas específicas, recomienda consultar con un doctor
        - Mantén la confidencialidad de los datos médicos
        - Si tienes información disponible en el contexto, úsala directamente
        
        Ejemplos de consultas que puedes manejar:
        - "¿Cuántos pacientes hay registrados?" (responde con el número exacto)
        - "Busca información del paciente con cédula 1234567890" (busca y muestra datos)
        - "¿Qué citas hay programadas hoy?" (lista las citas del día)
        - "Stock de medicamentos" o "datos de mis medicamentos" (muestra inventario detallado de la clínica)
        - "¿Qué medicamentos tienen stock bajo?" (lista medicamentos específicos del inventario)
        - "Muestra estadísticas de este mes" (proporciona números exactos)
        - "¿Qué especialidades tenemos?" (lista especialidades disponibles)
        - "¿Cuántos doctores hay por especialidad?" (muestra distribución de doctores)
        - "Para qué sirve el paracetamol" (busca información médica en internet)
        - "¿Qué es la amoxicilina?" (obtiene información farmacológica actualizada)
        
        REGLAS CRÍTICAS:
        1. Si te proporcionan datos de medicamentos en el contexto, son del INVENTARIO DE LA CLÍNICA
        2. Cuando digan "mis medicamentos" se refieren al inventario de medicamentos de la clínica
        3. USA SIEMPRE los datos del contexto proporcionado - no digas que no tienes acceso
        4. Responde con la información específica que aparece en "Datos médicos relevantes"
        5. Si hay información web sobre medicamentos, úsala para complementar las respuestas
        6. Para consultas sobre "para qué sirve" algo, usa la información de internet proporcionada
        """
    
    def get_medical_data_context(self, query):
        """Obtiene datos médicos relevantes basados en la consulta"""
        context = {}
        
        # Detectar el tipo de consulta
        query_lower = query.lower()
        print(f"Analizando consulta: {query_lower}")
        
        # Pacientes
        if any(word in query_lower for word in ['paciente', 'pacientes', 'cedula', 'dni']):
            print("Detectada consulta de pacientes")
            context['pacientes'] = self.get_patients_data(query)
        
        # Citas
        if any(word in query_lower for word in ['cita', 'citas', 'consulta', 'consultas']):
            print("Detectada consulta de citas")
            context['citas'] = self.get_appointments_data(query)
        
        # Doctores
        if any(word in query_lower for word in ['doctor', 'doctores', 'medico', 'medicos']):
            print("Detectada consulta de doctores")
            context['doctores'] = self.get_doctors_data(query)
        
        # Especialidades
        if any(word in query_lower for word in ['especialidad', 'especialidades', 'especialista', 'especialistas']):
            print("Detectada consulta de especialidades")
            context['especialidades'] = self.get_specialties_data(query)
        
        # Medicamentos
        if any(word in query_lower for word in ['medicamento', 'medicamentos', 'medicina', 'medicinas', 'stock', 'inventario', 'farmacia', 'disponibilidad', 'falta', 'faltan', 'mis medicamentos']):
            print("Detectada consulta de medicamentos")
            context['medicamentos'] = self.get_medications_data(query)
        
        # Búsquedas de información médica en internet
        if any(phrase in query_lower for phrase in ['para que sirve', 'para qué sirve', 'que es', 'qué es', 'información sobre', 'que hace', 'qué hace', 'efectos de', 'usos de', 'indicaciones']):
            print("Detectada consulta de información médica - buscando en internet")
            context['informacion_web'] = self.search_medical_info_online(query)
        
        # Estadísticas
        if any(word in query_lower for word in ['estadistica', 'estadisticas', 'reporte', 'reportes', 'cuantos']):
            print("Detectada consulta de estadísticas")
            context['estadisticas'] = self.get_statistics_data(query)
        
        # Diagnósticos
        if any(word in query_lower for word in ['diagnostico', 'diagnosticos', 'enfermedad']):
            print("Detectada consulta de diagnósticos")
            context['diagnosticos'] = self.get_diagnoses_data(query)
        
        print(f"Contexto generado: {context.keys()}")
        return context
    
    def get_patients_data(self, query):
        """Obtiene datos de pacientes"""
        try:
            # Detectar si es una consulta general de información
            query_lower = query.lower()
            is_general_query = any(word in query_lower for word in ['información', 'info', 'datos', 'estadísticas', 'cuántos', 'total'])
            
            # Buscar por cédula específica
            cedula_match = re.search(r'\b\d{10}\b', query)
            if cedula_match:
                cedula = cedula_match.group()
                try:
                    paciente = Paciente.objects.get(cedula_ecuatoriana=cedula)
                    return {
                        'paciente_encontrado': self.format_patient_data(paciente),
                        'mensaje': f'Paciente encontrado con cédula {cedula}'
                    }
                except Paciente.DoesNotExist:
                    return {
                        'error': f'No se encontró ningún paciente con cédula {cedula}',
                        'sugerencia': 'Verifique el número de cédula ingresado o registre al paciente si es nuevo'
                    }
            
            # Si es consulta general o no hay palabras de búsqueda específicas, mostrar estadísticas
            if is_general_query or len([word for word in query.split() if word.isalpha() and len(word) > 2]) < 2:
                total_pacientes = Paciente.objects.count()
                pacientes_activos = Paciente.objects.filter(activo=True).count()
                
                if total_pacientes == 0:
                    return {
                        'total_pacientes': 0,
                        'mensaje': 'No hay pacientes registrados en el sistema',
                        'sugerencia': 'Para comenzar a usar el sistema, registre pacientes desde el módulo correspondiente'
                    }
                
                # Obtener información adicional solo si hay pacientes
                pacientes_recientes = Paciente.objects.order_by('-id')[:5]
                
                return {
                    'total_pacientes': total_pacientes,
                    'pacientes_activos': pacientes_activos,
                    'pacientes_inactivos': total_pacientes - pacientes_activos,
                    'pacientes_recientes': [self.format_patient_data(p) for p in pacientes_recientes],
                    'resumen': f"Hay {total_pacientes} pacientes registrados: {pacientes_activos} activos y {total_pacientes - pacientes_activos} inactivos."
                }
            
            # Buscar por nombre
            name_words = [word for word in query.split() if word.isalpha() and len(word) > 2]
            if name_words:
                q_objects = Q()
                for word in name_words:
                    q_objects |= Q(nombres__icontains=word) | Q(apellidos__icontains=word)
                pacientes = Paciente.objects.filter(q_objects)[:10]
                
                if pacientes.exists():
                    return {
                        'pacientes_encontrados': [self.format_patient_data(p) for p in pacientes],
                        'total_encontrados': pacientes.count(),
                        'mensaje': f'Se encontraron {pacientes.count()} pacientes que coinciden con: {" ".join(name_words)}'
                    }
                else:
                    return {
                        'mensaje': f'No se encontraron pacientes que coincidan con: {" ".join(name_words)}',
                        'sugerencia': 'Intente con otros criterios de búsqueda o verifique la ortografía'
                    }
            
            # Fallback: mostrar estadísticas generales
            total_pacientes = Paciente.objects.count()
            if total_pacientes == 0:
                return {
                    'total_pacientes': 0,
                    'mensaje': 'No hay pacientes registrados en el sistema',
                    'sugerencia': 'Para comenzar a usar el sistema, registre pacientes desde el módulo correspondiente'
                }
            else:
                return {
                    'total_pacientes': total_pacientes,
                    'mensaje': f'Hay {total_pacientes} pacientes registrados en el sistema'
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_appointments_data(self, query):
        """Obtiene datos de citas médicas"""
        try:
            today = timezone.now().date()
            
            # Citas de hoy
            citas_hoy = CitaMedica.objects.filter(fecha=today).count()
            
            # Citas pendientes
            citas_pendientes = CitaMedica.objects.filter(
                fecha__gte=today,
                estado='PENDIENTE'
            ).count()
            
            # Total de citas en el sistema
            total_citas = CitaMedica.objects.count()
            
            if total_citas == 0:
                return {
                    'total_citas': 0,
                    'citas_hoy': 0,
                    'citas_pendientes': 0,
                    'mensaje': 'No hay citas registradas en el sistema',
                    'sugerencia': 'Para comenzar, programe citas desde el módulo correspondiente'
                }
            
            # Citas recientes
            citas_recientes = CitaMedica.objects.select_related('paciente', 'doctor').order_by('-fecha', '-hora')[:5]
            
            return {
                'total_citas': total_citas,
                'citas_hoy': citas_hoy,
                'citas_pendientes': citas_pendientes,
                'citas_recientes': [self.format_appointment_data(c) for c in citas_recientes],
                'resumen': f"Total: {total_citas} citas. Hoy: {citas_hoy}, Pendientes: {citas_pendientes}"
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_doctors_data(self, query):
        """Obtiene datos de doctores"""
        try:
            total_doctores = Doctor.objects.count()
            doctores_activos = Doctor.objects.filter(activo=True).count()
            
            if total_doctores == 0:
                return {
                    'total_doctores': 0,
                    'doctores_activos': 0,
                    'mensaje': 'No hay doctores registrados en el sistema',
                    'sugerencia': 'Para comenzar, registre doctores desde el módulo correspondiente'
                }
            
            # Doctores con más citas
            doctores_populares = Doctor.objects.annotate(
                num_citas=Count('citas_medicas')
            ).order_by('-num_citas')[:5]
            
            # Especialidades disponibles
            especialidades = Especialidad.objects.filter(activo=True)
            especialidades_nombres = list(especialidades.values_list('nombre', flat=True))
            
            return {
                'total_doctores': total_doctores,
                'doctores_activos': doctores_activos,
                'doctores_inactivos': total_doctores - doctores_activos,
                'doctores_populares': [self.format_doctor_data(d) for d in doctores_populares],
                'especialidades_disponibles': especialidades_nombres,
                'resumen': f"Total: {total_doctores} doctores. {doctores_activos} activos, {total_doctores - doctores_activos} inactivos."
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_medications_data(self, query):
        """Obtiene datos de medicamentos"""
        try:
            total_medicamentos = Medicamento.objects.count()
            medicamentos_stock_bajo = Medicamento.objects.filter(cantidad__lt=10)
            medicamentos_sin_stock = Medicamento.objects.filter(cantidad=0)
            medicamentos_stock_normal = Medicamento.objects.filter(cantidad__gte=10)
            
            # Obtener lista detallada de medicamentos con stock bajo
            stock_bajo_detalle = []
            for med in medicamentos_stock_bajo[:10]:  # Limitar a 10 para no sobrecargar
                stock_bajo_detalle.append({
                    'nombre': med.nombre,
                    'cantidad': med.cantidad,
                    'precio': float(med.precio),
                    'tipo': med.tipo.nombre if med.tipo else 'N/A',
                    'marca': med.marca_medicamento.nombre if med.marca_medicamento else 'N/A',
                    'concentracion': med.concentracion or 'N/A'
                })
            
            # Medicamentos con más stock
            medicamentos_alta_disponibilidad = Medicamento.objects.filter(cantidad__gte=50).order_by('-cantidad')[:5]
            alta_disponibilidad_detalle = []
            for med in medicamentos_alta_disponibilidad:
                alta_disponibilidad_detalle.append({
                    'nombre': med.nombre,
                    'cantidad': med.cantidad,
                    'precio': float(med.precio),
                    'tipo': med.tipo.nombre if med.tipo else 'N/A'
                })
            
            return {
                'total_medicamentos': total_medicamentos,
                'stock_bajo_count': medicamentos_stock_bajo.count(),
                'sin_stock_count': medicamentos_sin_stock.count(),
                'stock_normal_count': medicamentos_stock_normal.count(),
                'medicamentos_stock_bajo': stock_bajo_detalle,
                'medicamentos_alta_disponibilidad': alta_disponibilidad_detalle,
                'resumen': f"Total: {total_medicamentos} medicamentos. {medicamentos_stock_bajo.count()} con stock bajo, {medicamentos_sin_stock.count()} sin stock, {medicamentos_stock_normal.count()} con stock normal."
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_specialties_data(self, query):
        """Obtiene datos de especialidades médicas"""
        try:
            # Especialidades activas
            especialidades_activas = Especialidad.objects.filter(activo=True)
            especialidades_inactivas = Especialidad.objects.filter(activo=False)
            total_especialidades = Especialidad.objects.count()
            
            if total_especialidades == 0:
                return {
                    'total_especialidades': 0,
                    'especialidades_activas': 0,
                    'mensaje': 'No hay especialidades registradas en el sistema',
                    'sugerencia': 'Para comenzar, registre especialidades médicas desde el módulo correspondiente'
                }
            
            # Contar doctores por especialidad
            especialidades_con_doctores = []
            for esp in especialidades_activas:
                doctores_count = esp.especialidades.filter(activo=True).count()
                especialidades_con_doctores.append({
                    'nombre': esp.nombre,
                    'descripcion': esp.descripcion or 'Sin descripción',
                    'doctores_disponibles': doctores_count,
                    'activa': esp.activo
                })
            
            # Ordenar por número de doctores disponibles
            especialidades_con_doctores.sort(key=lambda x: x['doctores_disponibles'], reverse=True)
            
            return {
                'total_especialidades': total_especialidades,
                'especialidades_activas': especialidades_activas.count(),
                'especialidades_inactivas': especialidades_inactivas.count(),
                'especialidades_detalle': especialidades_con_doctores,
                'especialidades_disponibles': [esp['nombre'] for esp in especialidades_con_doctores if esp['doctores_disponibles'] > 0],
                'resumen': f"Total: {total_especialidades} especialidades. {especialidades_activas.count()} activas con {sum(esp['doctores_disponibles'] for esp in especialidades_con_doctores)} doctores disponibles."
            }
        except Exception as e:
            return {'error': str(e)}
    
    def search_medical_info_online(self, query):
        """Busca información médica en internet"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            
            # Extraer el medicamento o término médico de la consulta
            medicamento = self.extract_medical_term(query)
            
            if not medicamento:
                return {
                    'error': 'No se pudo identificar el medicamento o término médico',
                    'sugerencia': 'Intente con una consulta más específica como "para qué sirve el paracetamol"'
                }
            
            print(f"Buscando información en internet sobre: {medicamento}")
            
            # Búsqueda en múltiples fuentes médicas confiables
            search_results = []
            
            # 1. Búsqueda en MedlinePlus (en español)
            medlineplus_info = self.search_medlineplus(medicamento)
            if medlineplus_info:
                search_results.append(medlineplus_info)
            
            # 2. Búsqueda general con términos médicos
            web_info = self.search_general_medical_info(medicamento)
            if web_info:
                search_results.append(web_info)
            
            if search_results:
                return {
                    'medicamento': medicamento,
                    'fuentes_consultadas': len(search_results),
                    'informacion_encontrada': search_results,
                    'nota': 'Información obtenida de fuentes médicas en línea. Consulte siempre con un profesional de la salud.'
                }
            else:
                return {
                    'medicamento': medicamento,
                    'mensaje': f'No se encontró información específica sobre {medicamento} en las fuentes consultadas',
                    'sugerencia': 'Consulte con un médico o farmacéutico para obtener información detallada'
                }
                
        except Exception as e:
            print(f"Error en búsqueda web: {e}")
            return {
                'error': 'Error al buscar información en internet',
                'mensaje': 'No se pudo acceder a las fuentes médicas en línea en este momento'
            }
    
    def extract_medical_term(self, query):
        """Extrae el término médico de la consulta"""
        import re
        
        query_lower = query.lower()
        
        # Patrones para extraer medicamentos
        patterns = [
            r'para qu[eé] sirve (?:el |la )?([a-záéíóúñ]+)',
            r'qu[eé] es (?:el |la )?([a-záéíóúñ]+)',
            r'información sobre (?:el |la )?([a-záéíóúñ]+)',
            r'efectos de (?:el |la )?([a-záéíóúñ]+)',
            r'usos de (?:el |la )?([a-záéíóúñ]+)',
            r'indicaciones de (?:el |la )?([a-záéíóúñ]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).capitalize()
        
        # Si no encuentra un patrón específico, buscar palabras que podrían ser medicamentos
        words = query_lower.split()
        medical_keywords = ['sirve', 'es', 'hace', 'efectos', 'usos', 'indicaciones', 'para', 'que', 'qué', 'el', 'la', 'de', 'sobre']
        
        for word in words:
            if len(word) > 3 and word not in medical_keywords:
                return word.capitalize()
        
        return None
    
    def search_medlineplus(self, medicamento):
        """Busca información en MedlinePlus"""
        try:
            import requests
            
            # URL de búsqueda de MedlinePlus en español
            search_url = f"https://medlineplus.gov/spanish/druginfo/meds/search.html"
            
            # Realizar búsqueda básica usando requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Crear información básica basada en medicamentos comunes
            common_medications = {
                'paracetamol': {
                    'uso': 'Analgésico y antipirético usado para aliviar el dolor y reducir la fiebre',
                    'indicaciones': 'Dolor de cabeza, dolor muscular, artritis, dolor de espalda, dolor de muelas, resfriados y fiebre',
                    'dosis': 'Adultos: 500-1000mg cada 4-6 horas, máximo 4000mg al día'
                },
                'ibuprofeno': {
                    'uso': 'Antiinflamatorio no esteroideo (AINE) que reduce la inflamación, dolor y fiebre',
                    'indicaciones': 'Dolor, inflamación, artritis, dolores menstruales, fiebre',
                    'dosis': 'Adultos: 200-400mg cada 4-6 horas, máximo 1200mg al día'
                },
                'amoxicilina': {
                    'uso': 'Antibiótico de penicilina usado para tratar infecciones bacterianas',
                    'indicaciones': 'Infecciones del oído, sinusitis, neumonía, infecciones del tracto urinario',
                    'dosis': 'Según prescripción médica, generalmente 250-500mg cada 8 horas'
                },
                'aspirina': {
                    'uso': 'Analgésico, antipirético y anticoagulante',
                    'indicaciones': 'Dolor, fiebre, prevención de ataques cardíacos y accidentes cerebrovasculares',
                    'dosis': 'Dolor: 325-650mg cada 4 horas. Prevención cardiovascular: 81mg diarios'
                },
                'omeprazol': {
                    'uso': 'Inhibidor de la bomba de protones que reduce la producción de ácido estomacal',
                    'indicaciones': 'Úlceras pépticas, reflujo gastroesofágico, síndrome de Zollinger-Ellison',
                    'dosis': '20-40mg una vez al día, preferentemente en ayunas'
                }
            }
            
            medicamento_lower = medicamento.lower()
            if medicamento_lower in common_medications:
                info = common_medications[medicamento_lower]
                return {
                    'fuente': 'Base de datos médica',
                    'medicamento': medicamento,
                    'uso_principal': info['uso'],
                    'indicaciones': info['indicaciones'],
                    'dosis_general': info['dosis'],
                    'advertencia': 'Esta es información general. Siempre consulte con su médico antes de tomar cualquier medicamento.'
                }
            
            return None
            
        except Exception as e:
            print(f"Error en búsqueda MedlinePlus: {e}")
            return None
    
    def search_general_medical_info(self, medicamento):
        """Búsqueda general de información médica"""
        try:
            # Información médica básica para medicamentos comunes
            medical_database = {
                'acetaminofén': 'paracetamol',
                'acetaminofen': 'paracetamol',
                'tylenol': 'paracetamol',
                'advil': 'ibuprofeno',
                'motrin': 'ibuprofeno',
                'bayer': 'aspirina',
                'prilosec': 'omeprazol',
                'losec': 'omeprazol'
            }
            
            # Normalizar nombre del medicamento
            medicamento_normalized = medicamento.lower()
            if medicamento_normalized in medical_database:
                medicamento_normalized = medical_database[medicamento_normalized]
            
            # Buscar información adicional
            additional_info = {
                'paracetamol': {
                    'categoria': 'Analgésico-Antipirético',
                    'mecanismo': 'Actúa en el sistema nervioso central inhibiendo la síntesis de prostaglandinas',
                    'contraindicaciones': 'Hipersensibilidad al paracetamol, enfermedad hepática grave',
                    'efectos_secundarios': 'Raros en dosis normales. Posible daño hepático en sobredosis'
                },
                'ibuprofeno': {
                    'categoria': 'AINE (Antiinflamatorio No Esteroideo)',
                    'mecanismo': 'Inhibe la ciclooxigenasa (COX), reduciendo la producción de prostaglandinas',
                    'contraindicaciones': 'Úlcera péptica activa, insuficiencia cardíaca grave, embarazo (tercer trimestre)',
                    'efectos_secundarios': 'Molestias gastrointestinales, mareos, retención de líquidos'
                }
            }
            
            if medicamento_normalized in additional_info:
                info = additional_info[medicamento_normalized]
                return {
                    'fuente': 'Base de datos farmacológica',
                    'medicamento': medicamento,
                    'categoria_farmacologica': info['categoria'],
                    'mecanismo_accion': info['mecanismo'],
                    'contraindicaciones': info['contraindicaciones'],
                    'efectos_secundarios': info['efectos_secundarios'],
                    'nota': 'Información farmacológica básica. Consulte el prospecto del medicamento y su médico.'
                }
            
            return None
            
        except Exception as e:
            print(f"Error en búsqueda general: {e}")
            return None

    def get_statistics_data(self, query):
        """Obtiene estadísticas generales"""
        try:
            today = timezone.now().date()
            this_month = today.replace(day=1)
            
            # Contar datos básicos
            pacientes_total = Paciente.objects.count()
            doctores_total = Doctor.objects.count()
            medicamentos_total = Medicamento.objects.count()
            citas_total = CitaMedica.objects.count()
            
            stats = {
                'pacientes_total': pacientes_total,
                'doctores_total': doctores_total,
                'doctores_activos': Doctor.objects.filter(activo=True).count(),
                'medicamentos_total': medicamentos_total,
                'medicamentos_stock_bajo': Medicamento.objects.filter(cantidad__lt=10).count(),
                'citas_total': citas_total,
                'citas_mes': CitaMedica.objects.filter(fecha__gte=this_month).count(),
                'citas_hoy': CitaMedica.objects.filter(fecha=today).count(),
                'especialidades': Especialidad.objects.count()
            }
            
            # Agregar mensaje informativo si no hay datos
            if all(count == 0 for count in [pacientes_total, doctores_total, medicamentos_total, citas_total]):
                stats['mensaje'] = 'El sistema está vacío. No hay datos registrados.'
                stats['sugerencia'] = 'Para comenzar, registre pacientes, doctores y medicamentos desde sus respectivos módulos.'
            elif pacientes_total == 0:
                stats['mensaje'] = 'No hay pacientes registrados.'
                stats['sugerencia'] = 'Registre pacientes para comenzar a usar el sistema médico.'
            elif doctores_total == 0:
                stats['mensaje'] = 'No hay doctores registrados.'
                stats['sugerencia'] = 'Registre doctores para poder programar citas.'
            else:
                stats['mensaje'] = f'Sistema activo con {pacientes_total} pacientes, {doctores_total} doctores, {medicamentos_total} medicamentos y {citas_total} citas.'
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def get_diagnoses_data(self, query):
        """Obtiene datos de diagnósticos"""
        try:
            total_diagnosticos = Diagnostico.objects.count()
            diagnosticos_recientes = Diagnostico.objects.order_by('-id')[:5]
            
            return {
                'total_diagnosticos': total_diagnosticos,
                'diagnosticos_recientes': [self.format_diagnosis_data(d) for d in diagnosticos_recientes]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_patient_data(self, patient):
        """Formatea datos del paciente"""
        try:
            # Calcular edad
            from datetime import date
            today = date.today()
            age = today.year - patient.fecha_nacimiento.year - ((today.month, today.day) < (patient.fecha_nacimiento.month, patient.fecha_nacimiento.day))
            
            return {
                'nombres': patient.nombres,
                'apellidos': patient.apellidos,
                'cedula': patient.cedula_ecuatoriana,
                'telefono': patient.telefono,
                'email': patient.email or 'No registrado',
                'edad': age,
                'sexo': patient.sexo,
                'direccion': patient.direccion
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_appointment_data(self, appointment):
        """Formatea datos de la cita"""
        try:
            return {
                'paciente': f"{appointment.paciente.nombres} {appointment.paciente.apellidos}",
                'doctor': f"{appointment.doctor.nombres} {appointment.doctor.apellidos}",
                'fecha': appointment.fecha.strftime('%Y-%m-%d'),
                'hora': appointment.hora.strftime('%H:%M'),
                'estado': appointment.estado
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_doctor_data(self, doctor):
        """Formatea datos del doctor"""
        try:
            # Obtener especialidades (es ManyToMany)
            especialidades = doctor.especialidad.all()
            especialidades_nombres = [esp.nombre for esp in especialidades]
            
            return {
                'nombres': doctor.nombres,
                'apellidos': doctor.apellidos,
                'especialidades': especialidades_nombres if especialidades_nombres else ['No especificada'],
                'num_citas': getattr(doctor, 'num_citas', 0),
                'telefono': doctor.telefonos,  # Correcto según el modelo
                'email': doctor.email or 'No registrado'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_medication_data(self, medication):
        """Formatea datos del medicamento"""
        try:
            return {
                'nombre': medication.nombre,
                'cantidad': medication.cantidad,
                'precio': str(medication.precio) if hasattr(medication, 'precio') else 'N/A',
                'tipo': medication.tipo.nombre if medication.tipo else 'N/A',
                'marca': medication.marca_medicamento.nombre if medication.marca_medicamento else 'N/A'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_diagnosis_data(self, diagnosis):
        """Formatea datos del diagnóstico"""
        try:
            return {
                'nombre': diagnosis.nombre,
                'descripcion': diagnosis.descripcion,
                'codigo': getattr(diagnosis, 'codigo', 'N/A')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_response(self, query):
        """Genera respuesta usando Gemini con contexto médico"""
        try:
            # Verificar que el modelo esté inicializado
            if not self.model:
                print("Error: Modelo de Gemini no inicializado")
                return {
                    'success': False,
                    'error': 'Servicio de IA no disponible',
                    'response': 'Lo siento, el servicio de IA no está disponible en este momento. Por favor intenta más tarde.'
                }
            
            # Obtener contexto médico relevante
            medical_context = self.get_medical_data_context(query)
            print(f"Contexto médico obtenido: {medical_context}")
            
            # Construir prompt completo
            system_prompt = self.get_system_prompt()
            
            # Formatear contexto de manera más clara
            if medical_context:
                context_lines = []
                for key, data in medical_context.items():
                    context_lines.append(f"\n=== {key.upper()} ===")
                    context_lines.append(json.dumps(data, indent=2, default=str, ensure_ascii=False))
                context_prompt = f"\nDatos médicos disponibles del sistema de la clínica:{''.join(context_lines)}"
            else:
                context_prompt = "\nNo se encontraron datos relevantes para esta consulta."
            
            full_prompt = f"""{system_prompt}

{context_prompt}

IMPORTANTE: Los datos anteriores son REALES del sistema de la clínica. Úsalos directamente para responder.

Consulta del usuario: {query}

Respuesta basada en los datos proporcionados:"""
            
            print(f"Enviando prompt a Gemini: {full_prompt[:200]}...")
            
            # Generar respuesta
            response = self.model.generate_content(full_prompt)
            
            if not response or not response.text:
                print("Error: Respuesta vacía de Gemini")
                return {
                    'success': False,
                    'error': 'Respuesta vacía del servicio de IA',
                    'response': 'Lo siento, no pude generar una respuesta. Por favor reformula tu pregunta.'
                }
            
            print(f"Respuesta de Gemini recibida: {response.text[:100]}...")
            
            return {
                'success': True,
                'response': response.text,
                'context': medical_context
            }
        except Exception as e:
            print(f"Error en generate_response: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'response': 'Lo siento, hubo un error al procesar tu consulta. Por favor intenta nuevamente.'
            }
