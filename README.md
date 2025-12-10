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
- MySQL 8.0 o superior
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

1. **Crear la base de datos en MySQL:**

```sql
CREATE DATABASE eventsoft CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'eventsoft_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON eventsoft.* TO 'eventsoft_user'@'localhost';
FLUSH PRIVILEGES;
```

2. **Crear archivo `.env` en la raíz del proyecto:**

```env
# Configuración de Django
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos MySQL
DB_NAME=eventsoft
DB_USER=eventsoft_user
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=3306

# Email (opcional para desarrollo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion

# Brevo API (opcional, para envío de emails en producción)
# BREVO_API_KEY=tu_api_key_de_brevo
```

> ⚠️ **Importante:** Nunca subas el archivo `.env` al repositorio. Ya está incluido en `.gitignore`.

### 🔄 Paso 5: Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 👤 Paso 6: Crear Super Usuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario administrador.

### ▶️ Paso 7: Ejecutar el Servidor de Desarrollo

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
