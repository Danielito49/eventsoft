# 🚀 Guía de Despliegue - EventSoft en PythonAnywhere

Esta guía te llevará paso a paso para desplegar EventSoft en PythonAnywhere (100% gratis).

---

## 📋 Pre-requisitos

1. Cuenta en [PythonAnywhere](https://www.pythonanywhere.com/) (plan gratuito)
2. Cuenta en [GitHub](https://github.com/) con el proyecto subido
3. Tu proyecto local funcionando correctamente

---

## 🔧 Paso 1: Preparar el Repositorio en GitHub

### 1.1 Asegúrate de que `.gitignore` excluye archivos sensibles
El archivo `.gitignore` ya está configurado para excluir `.env` y otros archivos sensibles.

### 1.2 Sube los cambios a GitHub
```bash
git add .
git commit -m "Preparar proyecto para producción"
git push origin main
```

---

## 🌐 Paso 2: Crear cuenta en PythonAnywhere

1. Ve a [www.pythonanywhere.com](https://www.pythonanywhere.com/)
2. Click en "Pricing & signup"
3. Selecciona "Create a Beginner account" (GRATIS)
4. Completa el registro

---

## 💻 Paso 3: Clonar el Proyecto

### 3.1 Abre una consola Bash
1. En el dashboard de PythonAnywhere, ve a **Consoles**
2. Click en **Bash** para abrir una nueva consola

### 3.2 Clona tu repositorio
```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd eventsoft-django
```

### 3.3 Crea un entorno virtual
```bash
mkvirtualenv --python=/usr/bin/python3.10 eventsoft-env
```

### 3.4 Instala las dependencias
```bash
pip install -r requirements.txt
```

**Nota:** Si `mysqlclient` da problemas, PythonAnywhere ya tiene las dependencias del sistema instaladas.

---

## 🗄️ Paso 4: Configurar la Base de Datos MySQL

### 4.1 Crear la base de datos
1. Ve a **Databases** en el menú de PythonAnywhere
2. Configura tu contraseña de MySQL (anótala)
3. Crea una nueva base de datos: `TU_USUARIO$eventsoft`

### 4.2 Anota los datos de conexión
- **Host:** `TU_USUARIO.mysql.pythonanywhere-services.com`
- **Usuario:** `TU_USUARIO`
- **Base de datos:** `TU_USUARIO$eventsoft`

---

## ⚙️ Paso 5: Configurar Variables de Entorno

### 5.1 Crea el archivo .env en PythonAnywhere
En la consola Bash:
```bash
cd ~/eventsoft-django
nano .env
```

### 5.2 Agrega el contenido (reemplaza los valores):
```
SECRET_KEY=genera-una-clave-segura-aqui-muy-larga-12345
DEBUG=False
ALLOWED_HOSTS=TU_USUARIO.pythonanywhere.com

MYSQL_DATABASE=TU_USUARIO$eventsoft
MYSQL_USER=TU_USUARIO
MYSQL_PASSWORD=TU_PASSWORD_MYSQL
MYSQL_HOST=TU_USUARIO.mysql.pythonanywhere-services.com
MYSQL_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=daviladani888@gmail.com
EMAIL_HOST_PASSWORD=hbqp ctml okwd wueg
DEFAULT_FROM_EMAIL=daviladani888@gmail.com
```

Guarda con `Ctrl+O`, Enter, luego `Ctrl+X` para salir.

### 5.3 Genera una SECRET_KEY segura
En la consola Python de PythonAnywhere:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
Copia el resultado y úsalo en tu `.env`

---

## 🔄 Paso 6: Migraciones y Archivos Estáticos

### 6.1 Activa el entorno virtual
```bash
workon eventsoft-env
cd ~/eventsoft-django
```

### 6.2 Ejecuta las migraciones
```bash
python manage.py migrate
```

### 6.3 Crea un superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6.4 Recolecta archivos estáticos
```bash
python manage.py collectstatic --noinput
```

---

## 🌍 Paso 7: Configurar la Web App

### 7.1 Crear la aplicación web
1. Ve a **Web** en el menú de PythonAnywhere
2. Click en **Add a new web app**
3. Click **Next** (aceptar el dominio gratuito)
4. Selecciona **Manual configuration**
5. Selecciona **Python 3.10**
6. Click **Next**

### 7.2 Configurar el Virtualenv
En la sección "Virtualenv":
- Ingresa: `/home/TU_USUARIO/.virtualenvs/eventsoft-env`
- Click en el check ✓

### 7.3 Configurar el código fuente
En la sección "Code":
- **Source code:** `/home/TU_USUARIO/eventsoft-django`
- **Working directory:** `/home/TU_USUARIO/eventsoft-django`

### 7.4 Editar el archivo WSGI
Click en el enlace del archivo WSGI (algo como `/var/www/TU_USUARIO_pythonanywhere_com_wsgi.py`)

**Borra todo el contenido** y reemplázalo con:

```python
import os
import sys
from dotenv import load_dotenv

# Ruta al proyecto
path = '/home/TU_USUARIO/eventsoft-django'
if path not in sys.path:
    sys.path.append(path)

# Cargar variables de entorno
load_dotenv(os.path.join(path, '.env'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'pr_eventsoft.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Importante:** Reemplaza `TU_USUARIO` con tu nombre de usuario de PythonAnywhere.

---

## 📁 Paso 8: Configurar Archivos Estáticos y Media

### 8.1 En la sección "Static files" de la Web App:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/TU_USUARIO/eventsoft-django/staticfiles` |
| `/media/` | `/home/TU_USUARIO/eventsoft-django/media` |

Click en cada fila para agregar estas rutas.

---

## 🔄 Paso 9: Recargar la Aplicación

1. Ve arriba de la página de Web
2. Click en el botón verde **Reload**
3. Visita `https://TU_USUARIO.pythonanywhere.com`

---

## ✅ Verificación

Si todo está bien, deberías ver tu aplicación EventSoft funcionando.

### Posibles problemas:

1. **Error 500:** Revisa los logs de error en la sección "Web" → "Error log"
2. **CSS/JS no carga:** Verifica la configuración de Static files
3. **Base de datos no conecta:** Verifica las credenciales en `.env`

---

## 🔄 Actualizaciones Futuras

Cuando hagas cambios en tu código local:

```bash
# En tu PC local
git add .
git commit -m "Descripción del cambio"
git push origin main

# En la consola Bash de PythonAnywhere
cd ~/eventsoft-django
git pull origin main
workon eventsoft-env
python manage.py migrate  # Si hay cambios en modelos
python manage.py collectstatic --noinput  # Si hay cambios en static
```

Luego ve a **Web** y click en **Reload**.

---

## 📞 Soporte

- [Documentación de PythonAnywhere](https://help.pythonanywhere.com/)
- [Foro de PythonAnywhere](https://www.pythonanywhere.com/forums/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

¡Felicitaciones! 🎉 Tu EventSoft está ahora en producción.
