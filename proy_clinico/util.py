from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from applications.security.models import AuditUser

""" Valida que una cédula ecuatoriana sea válida según el algoritmo del módulo 10.
 - Debe tener exactamente 10 dígitos numéricos.
 - Los dos primeros dígitos deben representar una provincia válida (01–24 o 30).
 - El último dígito debe coincidir con el dígito verificador calculado.  """
def valida_cedula(value):
    cedula = str(value)

    if not cedula.isdigit():
        raise ValidationError('La cédula debe contener solo números.')

    if len(cedula) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos.')

    provincia = int(cedula[:2])
    if provincia < 1 or (provincia > 24 and provincia != 30):
        raise ValidationError('El código de provincia en la cédula no es válido.')

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        digito = int(cedula[i])
        producto = digito * coeficientes[i]
        if producto > 9:
            producto -= 9
        total += producto

    digito_verificador = (10 - (total % 10)) % 10

    if digito_verificador != int(cedula[9]):
        raise ValidationError('La cédula ingresada no es válida.')

def cedula_valida(cedula):
    """
    Valida una cédula ecuatoriana usando el algoritmo del módulo 10.
    """
    if len(cedula) != 10 or not cedula.isdigit():
        return False

    provincia = int(cedula[:2])
    if provincia < 1 or (provincia > 24 and provincia != 30):
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        mult = int(cedula[i]) * coeficientes[i]
        total += mult - 9 if mult > 9 else mult

    digito_verificador = (10 - total % 10) % 10
    return digito_verificador == int(cedula[9])
""" 
    Valida un RUC ecuatoriano (13 dígitos) para:
    - Personas naturales con cédula + 001
    - Sociedades privadas (tercer dígito = 9)
    - Sociedades públicas (tercer dígito = 6)
    - RUCs emitidos a extranjeros con estructura numérica válida
"""
def valida_ruc(value):

    ruc = str(value)

    if not ruc.isdigit():
        raise ValidationError("El RUC debe contener solo números.")

    if len(ruc) != 13:
        raise ValidationError("El RUC debe tener exactamente 13 dígitos.")

    tercer_digito = int(ruc[2])

    # Persona natural: cédula válida + 001
    if ruc.endswith("001"):
        cedula = ruc[:10]
        if cedula_valida(cedula):
            return
        raise ValidationError("El RUC no es válido: la cédula contenida no es válida.")

    # Sociedades públicas o privadas
    if tercer_digito in [6, 9]:
        return  # Estructura válida, no se aplica módulo 10 aquí

    # RUC de extranjeros u otros
    if 0 <= tercer_digito <= 9:
        return  # Se acepta como estructuralmente válido

    raise ValidationError("El RUC ingresado no es válido para personas naturales, sociedades o extranjeros.")

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def save_audit(request, model, action):
    user = request.user
    # Obtain client ip address
    client_address = ip_client_address(request)
    # Registro en tabla Auditora BD
    auditusuariotabla = AuditUser(usuario=user,
                                  tabla=model.__class__.__name__,
                                  registroid=model.id,
                                  accion=action,
                                  fecha=timezone.now().date(),
                                  hora=timezone.now().time(),
                                  estacion=client_address)
    auditusuariotabla.save()
# Obtener el IP desde donde se esta accediendo
def ip_client_address(request):
    try:
        # case server externo
        client_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        # case localhost o 127.0.0.1
        client_address = request.META['REMOTE_ADDR']

    return client_address
