# 🎉 EventSoft - Sistema de Gestión de Eventos Académicos

Sistema web desarrollado en Django para la gestión integral de eventos académicos, permitiendo la administración de proyectos, participantes, evaluadores y asistentes.

![Django](https://img.shields.io/badge/Django-5.2.1-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Descripción del Proyecto

**EventSoft** es una plataforma web diseñada para facilitar la organización y gestión de eventos académicos como congresos, seminarios, ferias de proyectos y conferencias. El sistema permite:

- Crear y gestionar múltiples eventos
- Registrar proyectos con sus respectivos participantes
- Asignar evaluadores para calificar proyectos
- Gestionar asistentes e inscripciones
- Generar certificados automáticamente
- Enviar notificaciones por correo electrónico

---

## 👥 Integrantes del Equipo

| Nombre | Rol |
|--------|-----|
| **Jhonatan Escobar** | Desarrollador |
| **Yeni Rios** | Desarrolladora |
| **Daniel Davila** | Desarrollador |
| **Sergio Castaño** | Desarrollador |
---

## 🎭 Roles del Sistema

### 1. 👑 Super Administrador
- Gestión completa del sistema
- Crear y administrar eventos
- Generar códigos de invitación para administradores de eventos
- Aprobar o rechazar solicitudes de eventos
- Acceso a todos los reportes y estadísticas

### 2. 🏢 Administrador de Evento
- Gestionar un evento específico
- Crear áreas temáticas
- Generar códigos de invitación para evaluadores, participantes y asistentes
- Gestionar inscripciones y aprobar solicitudes
- Configurar fechas y parámetros del evento
- Generar certificados

### 3. 📝 Evaluador
- Evaluar proyectos asignados
- Calificar según rúbricas definidas
- Ver listado de proyectos a evaluar
- Registrar observaciones y comentarios

### 4. 🎓 Participante
- Registrar proyectos en el evento
- Subir documentación del proyecto
- Ver estado de evaluaciones
- Gestionar integrantes del grupo
- Descargar certificados

### 5. 🎫 Asistente
- Inscribirse a eventos
- Ver información del evento
- Confirmar asistencia
- Descargar certificado de asistencia

---

## 🚀 Aplicación Desplegada

### 🌐 URL de Producción

**https://danielito09.pythonanywhere.com**

### 📝 Instrucciones para Ejecución en Línea

1. **Acceder a la aplicación:**
   - Abrir el navegador web
   - Ir a: https://danielito09.pythonanywhere.com

2. **Solicitar acceso como Administrador:**
   - Para obtener credenciales de Super Administrador o crear un evento, contactar a:
   - 📧 **dalejandro@gmail.com**
   - Indicar en el correo el propósito de uso de la plataforma

3. **Flujo básico de uso:**
   
   **Como Super Administrador:**
   - Iniciar sesión → Ir a "Gestión de Eventos" → Crear nuevo evento
   - Generar código de invitación para administrador del evento
   
   **Como Administrador de Evento:**
   - Registrarse usando el código de invitación recibido
   - Configurar áreas del evento
   - Generar códigos para evaluadores, participantes y asistentes
   
   **Como Participante:**
   - Registrarse con código de invitación
   - Registrar proyecto y agregar integrantes
   - Subir documentación
   
   **Como Evaluador:**
   - Registrarse con código de invitación
   - Evaluar proyectos asignados
   
   **Como Asistente:**
   - Registrarse con código de invitación
   - Confirmar asistencia al evento

---

## 💻 Instalación en Entorno de Desarrollo

### 📋 Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 o superior (o XAMPP/WAMP que incluye MySQL)
- Git
- pip (gestor de paquetes de Python)

### 🔧 Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Danielito49/eventsoft.git
cd eventsoft
```

### 🐍 Paso 2: Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 📦 Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 🗄️ Paso 4: Configurar Base de Datos MySQL

#### Opción A: Usar usuario root existente (más fácil para desarrollo)

Si ya tienes MySQL instalado (con XAMPP, WAMP, o instalación directa), solo necesitas crear la base de datos:

1. Abre la terminal de MySQL o phpMyAdmin
2. Ejecuta:
```sql
CREATE DATABASE eventsoft CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Luego usa tu usuario `root` existente en el archivo `.env`.

#### Opción B: Crear un usuario específico (recomendado para producción)

```sql
CREATE DATABASE eventsoft CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'eventsoft_user'@'localhost' IDENTIFIED BY 'MiContraseñaSegura123';
GRANT ALL PRIVILEGES ON eventsoft.* TO 'eventsoft_user'@'localhost';
FLUSH PRIVILEGES;
```

> 💡 En este caso, `MiContraseñaSegura123` es una contraseña **nueva que tú inventas** para el nuevo usuario `eventsoft_user`.

---

### 🔐 Paso 5: Crear archivo de Variables de Entorno (.env)

Crea un archivo llamado `.env` en la raíz del proyecto (donde está `manage.py`).

#### Plantilla del archivo `.env`:

```env
# ============================================
# CONFIGURACIÓN DE DJANGO
# ============================================
SECRET_KEY=django-clave-secreta-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ============================================
MYSQL_DATABASE=eventsoft
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña_de_mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306

# ============================================
# CONFIGURACIÓN DE EMAIL (Opcional)
# ============================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=tu_correo@gmail.com

# Para producción con Brevo (descomentar):
# BREVO_API_KEY=tu_api_key_de_brevo
```

---

### 📖 Explicación de cada Variable de Entorno

#### 🔧 Variables de Django

| Variable | Descripción | Ejemplo | ¿Dónde obtenerla? |
|----------|-------------|---------|-------------------|
| `SECRET_KEY` | Clave secreta para seguridad de Django | `mi-clave-super-secreta-123` | Inventa una cadena larga y aleatoria. Para desarrollo puedes dejar el valor por defecto. |
| `DEBUG` | Modo de depuración | `True` o `False` | Usa `True` para desarrollo local, `False` para producción. |
| `ALLOWED_HOSTS` | Dominios permitidos | `localhost,127.0.0.1` | Lista de hosts separados por coma. |

#### 🗄️ Variables de Base de Datos

| Variable | Descripción | Ejemplo | ¿Dónde obtenerla? |
|----------|-------------|---------|-------------------|
| `MYSQL_DATABASE` | Nombre de la base de datos | `eventsoft` | El nombre que usaste en `CREATE DATABASE`. |
| `MYSQL_USER` | Usuario de MySQL | `root` | Si usas XAMPP/WAMP, generalmente es `root`. Si creaste un usuario nuevo, usa ese nombre. |
| `MYSQL_PASSWORD` | Contraseña del usuario MySQL | `mi_contraseña` | **XAMPP:** Por defecto está vacía (dejar vacío). **WAMP:** Por defecto está vacía. **MySQL instalado:** La contraseña que configuraste al instalar. |
| `MYSQL_HOST` | Servidor de MySQL | `localhost` | Para desarrollo local siempre es `localhost` o `127.0.0.1`. |
| `MYSQL_PORT` | Puerto de MySQL | `3306` | Por defecto es `3306`. XAMPP a veces usa `3307`. Verifica en tu instalación. |

#### 📧 Variables de Email (Opcionales)

| Variable | Descripción | Ejemplo | ¿Dónde obtenerla? |
|----------|-------------|---------|-------------------|
| `EMAIL_HOST` | Servidor SMTP | `smtp.gmail.com` | Depende de tu proveedor de email. |
| `EMAIL_PORT` | Puerto SMTP | `587` | Gmail usa `587`. |
| `EMAIL_HOST_USER` | Tu correo electrónico | `mi_correo@gmail.com` | Tu dirección de email. |
| `EMAIL_HOST_PASSWORD` | Contraseña de aplicación | `xxxx xxxx xxxx xxxx` | **NO es tu contraseña de Gmail.** Ver instrucciones abajo. |
| `DEFAULT_FROM_EMAIL` | Remitente por defecto | `mi_correo@gmail.com` | Mismo correo que `EMAIL_HOST_USER`. |
| `BREVO_API_KEY` | API Key de Brevo | `xkeysib-xxx...` | Solo para producción. Crear cuenta en [brevo.com](https://brevo.com). |

---

### 📧 ¿Cómo obtener la contraseña de aplicación de Gmail?

Gmail no permite usar tu contraseña normal para aplicaciones. Debes crear una "Contraseña de Aplicación":

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Ir a **Seguridad** → **Verificación en 2 pasos** (debe estar activada)
3. Al final de esa página, busca **"Contraseñas de aplicaciones"**
4. Selecciona "Otro" y escribe "EventSoft"
5. Google te dará una contraseña de 16 caracteres (ej: `hbqp ctml okwd wueg`)
6. Esa es la que pones en `EMAIL_HOST_PASSWORD`

> ⚠️ Si no tienes verificación en 2 pasos activada, primero debes activarla.

> 💡 **Para desarrollo:** Puedes omitir la configuración de email. El sistema funcionará pero no enviará correos.

---

### 🔍 ¿Cómo saber mi contraseña de MySQL?

Depende de cómo instalaste MySQL:

| Instalación | Usuario por defecto | Contraseña por defecto |
|-------------|---------------------|------------------------|
| **XAMPP** | `root` | *(vacía - no poner nada)* |
| **WAMP** | `root` | *(vacía - no poner nada)* |
| **MySQL Installer (Windows)** | `root` | La que elegiste durante la instalación |
| **MySQL (Linux)** | `root` | La que configuraste con `mysql_secure_installation` |

**Si no recuerdas tu contraseña de MySQL:**
- En XAMPP/WAMP: Reinstala o usa phpMyAdmin para resetearla
- En MySQL directo: Busca "reset mysql root password" para tu sistema operativo

---

### 📝 Ejemplo de archivo `.env` completo (desarrollo con XAMPP)

```env
# Django
SECRET_KEY=clave-secreta-para-desarrollo-local-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (XAMPP con contraseña vacía)
MYSQL_DATABASE=eventsoft
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Email (opcional - comentado)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=
# EMAIL_HOST_PASSWORD=
# DEFAULT_FROM_EMAIL=
```

> ⚠️ **Importante:** Nunca subas el archivo `.env` al repositorio. Ya está incluido en `.gitignore`.

---

### 🔄 Paso 6: Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 👤 Paso 7: Crear Super Usuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario administrador.

### ▶️ Paso 8: Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en: **http://127.0.0.1:8000**

---

## 📁 Estructura del Proyecto

```
eventsoft/
├── app_admin/              # Módulo de administración general
├── app_administradores/    # Gestión de administradores de eventos
├── app_areas/              # Gestión de áreas temáticas
├── app_asistentes/         # Módulo de asistentes
├── app_evaluadores/        # Módulo de evaluadores
├── app_eventos/            # Gestión de eventos
├── app_participantes/      # Módulo de participantes y proyectos
├── app_usuarios/           # Autenticación y gestión de usuarios
├── media/                  # Archivos subidos (imágenes, documentos)
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── templates/              # Plantillas HTML globales
├── pr_eventsoft/           # Configuración principal del proyecto
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs principales
│   ├── email_backend.py    # Backend personalizado para emails
│   └── wsgi.py             # Configuración WSGI
├── manage.py               # Script de gestión de Django
├── requirements.txt        # Dependencias del proyecto
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Este archivo
```

---

## ✨ Funcionalidades Principales

| Módulo | Funcionalidades |
|--------|----------------|
| **Eventos** | Crear, editar, activar/desactivar eventos, configurar fechas |
| **Áreas** | Gestionar áreas temáticas por evento |
| **Proyectos** | Registro de proyectos, subida de archivos, gestión de integrantes |
| **Evaluaciones** | Asignación de evaluadores, calificación por rúbricas, promedios |
| **Certificados** | Generación automática de certificados en PDF |
| **Invitaciones** | Sistema de códigos de invitación por correo electrónico |
| **Reportes** | Estadísticas y reportes del evento |

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Django 5.2.1
- **Base de Datos:** MySQL 8.0
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Generación de PDFs:** WeasyPrint
- **Códigos QR:** qrcode
- **Email:** Brevo API / SMTP
- **Hosting:** PythonAnywhere

---

## 📧 Configuración de Emails

### Para Desarrollo (SMTP Gmail)
Configura las variables `EMAIL_*` en el archivo `.env`.

### Para Producción (Brevo API)
El sistema usa Brevo (antes SendinBlue) para enviar emails en producción:
1. Crear cuenta en [Brevo](https://www.brevo.com/)
2. Obtener API Key
3. Configurar `BREVO_API_KEY` en las variables de entorno

---

## 🐛 Solución de Problemas Comunes

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté corriendo
# Windows:
net start mysql

# Linux:
sudo systemctl start mysql
```

### Error de migraciones
```bash
# Eliminar migraciones y recrear
python manage.py migrate --fake-initial
```

### Error de dependencias
```bash
# Actualizar pip e instalar de nuevo
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos.

---

## 🤝 Contribuciones

Este es un proyecto académico. Para contribuciones o sugerencias, contactar a los integrantes del equipo.

---

**Desarrollado con ❤️ por el equipo de EventSoft - 2025**
