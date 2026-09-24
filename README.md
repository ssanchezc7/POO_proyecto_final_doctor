# App Security

Sistema web de gestión clínica y seguridad desarrollado con Django para administrar usuarios, pacientes, médicos, servicios, pagos, diagnósticos y un asistente chatbot integrado con Gemini.

## Descripción general

Este proyecto está orientado a la gestión de una clínica o consultorio médico, con módulos para:

- Seguridad y autenticación de usuarios
- Administración de pacientes, médicos y especialidades
- Citas, pagos y servicios adicionales
- Diagnósticos, gastos y medicamentos
- Asistente virtual con IA usando Gemini
- Gestión de archivos multimedia y documentación

## Stack tecnológico

- Python 3.10+
- Django 5.2.1
- PostgreSQL
- HTML/CSS/JavaScript
- Bootstrap / templates personalizados
- Channels para funcionalidad real-time
- Gemini AI / Google Generative AI
- ReportLab y WeasyPrint para reportes
- Django REST no requerido, pero el proyecto usa vistas tradicionales del framework

## Requisitos previos

Antes de iniciar, asegúrate de tener instalado:

- Python 3.10 o superior
- pip
- PostgreSQL
- Git
- Entorno virtual recomendado (`venv` o `conda`)

## Instalación

1. Clona el repositorio:

```bash
git clone <url-del-repositorio>
cd app_security
```

2. Crea y activa un entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

En Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables (o ajústalas según tu entorno local):

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
GEMINI_API_KEY=tu_api_key_gemini
DB_ENGINE=django.db.backends.postgresql
DB_NAME=medicos
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_password_app
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_CLIENT_SECRET=tu_paypal_secret
PAYPAL_MODE=sandbox
```

> El proyecto ya tiene valores por defecto en `proy_clinico/settings.py`, pero se recomienda configurar un `.env` real para evitar secretos sensibles en el código.

## Migraciones y base de datos

Antes de ejecutar la aplicación, crea la base de datos en PostgreSQL y luego aplica las migraciones:

```bash
python manage.py migrate
```

Si necesitas un superusuario para acceder al panel administrativo:

```bash
python manage.py createsuperuser
```

## Ejecución del proyecto

Inicia el servidor de desarrollo:

```bash
python manage.py runserver
```

Luego abre en tu navegador:

```text
http://127.0.0.1:8000/
```

## Estructura del proyecto

```text
app_security/
├── applications/
│   ├── chatbot/
│   ├── core/
│   ├── doctor/
│   └── security/
├── media/
├── proy_clinico/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
├── templates/
├── manage.py
├── requirements.txt
├── README.md
└── .env
```

## Funcionalidades principales

- Autenticación y gestión de usuarios
- CRUD de módulos clínicos
- Administración de especialidades, pacientes y médicos
- Generación de reportes y documentación
- Integración con pagos PayPal
- Chatbot inteligente con Gemini
- Soporte de archivos multimedia y uploads

## Comandos útiles

Crear migraciones:

```bash
python manage.py makemigrations
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Ejecutar tests:

```bash
python manage.py test
```

## Consideraciones

- En entorno de producción, configura `DEBUG=False` y un `SECRET_KEY` real.
- No compartas credenciales ni tokens en repositorios públicos.
- Revisa el archivo `proy_clinico/settings.py` para personalizar host, emails y servicios externos.

## Licencia

Este proyecto no especifica una licencia en el repositorio actual.

## Autor / mantenimiento

Ajusta esta sección con el nombre del equipo, cliente o responsable del proyecto si corresponde.
