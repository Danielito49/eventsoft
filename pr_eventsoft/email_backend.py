"""
Backend de email personalizado para usar Brevo API.
Usa requests directamente para llamar a api.brevo.com
(que está en la whitelist de PythonAnywhere free tier).
"""

import requests
import json
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class BrevoEmailBackend(BaseEmailBackend):
    """
    Backend de email que usa la API REST de Brevo para enviar correos.
    Usa api.brevo.com directamente (en la whitelist de PythonAnywhere).
    """
    
    # URL de la API de Brevo (en la whitelist de PythonAnywhere)
    API_URL = "https://api.brevo.com/v3/smtp/email"
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'BREVO_API_KEY', '')
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.default_from_name = getattr(settings, 'DEFAULT_FROM_NAME', 'EventSoft')
    
    def send_messages(self, email_messages):
        """
        Envía uno o más mensajes de email y retorna el número de mensajes enviados.
        """
        if not email_messages:
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                if self._send(message):
                    num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return num_sent
    
    def _send(self, message):
        """
        Envía un mensaje individual usando la API REST de Brevo.
        """
        try:
            # Preparar headers
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json"
            }
            
            # Preparar destinatarios
            to_list = [{"email": recipient} for recipient in message.to]
            
            # Preparar el remitente - extraer email limpio
            from_email = message.from_email or self.default_from_email
            # Si el from_email tiene formato "Nombre <email@domain.com>", extraer solo el email
            if '<' in from_email and '>' in from_email:
                from_email = from_email.split('<')[1].split('>')[0]
            
            # Determinar si el contenido es HTML
            html_content = None
            text_content = None
            
            # Verificar si tiene contenido alternativo (HTML)
            if hasattr(message, 'alternatives') and message.alternatives:
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        html_content = content
                        break
            
            # Si el cuerpo parece HTML, usarlo como HTML
            if message.body and ('<html' in message.body.lower() or '<div' in message.body.lower() or '<p>' in message.body.lower()):
                html_content = message.body
            else:
                text_content = message.body
            
            # Construir el payload
            payload = {
                "sender": {
                    "name": self.default_from_name,
                    "email": from_email
                },
                "to": to_list,
                "subject": message.subject
            }
            
            # Agregar contenido (HTML o texto)
            if html_content:
                payload["htmlContent"] = html_content
            if text_content:
                payload["textContent"] = text_content
            
            # Agregar CC si existe
            if message.cc:
                payload["cc"] = [{"email": cc} for cc in message.cc]
            
            # Agregar BCC si existe
            if message.bcc:
                payload["bcc"] = [{"email": bcc} for bcc in message.bcc]
            
            # Enviar la petición a la API de Brevo
            response = requests.post(
                self.API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            # Verificar respuesta
            if response.status_code in [200, 201, 202]:
                return True
            else:
                error_msg = f"Error Brevo API: {response.status_code} - {response.text}"
                if not self.fail_silently:
                    raise Exception(error_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            if not self.fail_silently:
                raise Exception(f"Error de conexión con Brevo API: {e}")
            return False
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
