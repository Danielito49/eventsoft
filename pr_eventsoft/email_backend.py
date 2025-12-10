"""
Backend de email personalizado para usar Brevo (SendinBlue) API.
Esto permite usar la API HTTP de Brevo en lugar de SMTP,
lo cual funciona en cuentas gratuitas de PythonAnywhere.
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class BrevoEmailBackend(BaseEmailBackend):
    """
    Backend de email que usa la API de Brevo para enviar correos.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        
        # Configurar la API de Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = getattr(settings, 'BREVO_API_KEY', '')
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
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
        Envía un mensaje individual usando la API de Brevo.
        """
        try:
            # Preparar destinatarios
            to_list = [{"email": recipient} for recipient in message.to]
            
            # Preparar el remitente
            sender = {
                "name": self.default_from_name,
                "email": message.from_email or self.default_from_email
            }
            
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
            
            # Crear el objeto de email
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to_list,
                sender=sender,
                subject=message.subject,
                html_content=html_content,
                text_content=text_content
            )
            
            # Agregar CC si existe
            if message.cc:
                send_smtp_email.cc = [{"email": cc} for cc in message.cc]
            
            # Agregar BCC si existe
            if message.bcc:
                send_smtp_email.bcc = [{"email": bcc} for bcc in message.bcc]
            
            # Enviar el email
            self.api_instance.send_transac_email(send_smtp_email)
            return True
            
        except ApiException as e:
            if not self.fail_silently:
                raise Exception(f"Error al enviar email via Brevo: {e}")
            return False
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
