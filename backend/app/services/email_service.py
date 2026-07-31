"""
Email notification service for ECES
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for user registration notifications"""
    
    def __init__(self):
        # Email configuration (can be set via environment variables)
        self.smtp_server = os.getenv("ECES_SMTP_SERVER", "smtp.isprambiente.it")
        self.smtp_port = int(os.getenv("ECES_SMTP_PORT", "587"))
        self.smtp_username = os.getenv("ECES_SMTP_USERNAME", "")
        self.smtp_password = os.getenv("ECES_SMTP_PASSWORD", "")
        self.from_email = os.getenv("ECES_FROM_EMAIL", "eces@isprambiente.it")
        self.admin_email = os.getenv("ECES_ADMIN_EMAIL", "davide.licheri@isprambiente.it")
        
        # Enable/disable email notifications
        self.email_enabled = os.getenv("ECES_EMAIL_ENABLED", "false").lower() == "true"
    
    def send_registration_notification(self, user_data: dict) -> bool:
        """Send email notification for new user registration"""
        if not self.email_enabled:
            logger.info(f"Email disabled - Would notify: New user {user_data['username']} registered")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.admin_email
            msg['Subject'] = f"ECES - Nuova Registrazione Utente: {user_data['full_name']}"
            
            # Email body
            body = f"""
Ciao Davide,

Un nuovo utente si è registrato nel sistema ECES:

👤 Nome Completo: {user_data['full_name']}
📧 Email: {user_data['email']}
🏢 Dipartimento: {user_data.get('department', 'Non specificato')}
👨‍💻 Username: {user_data['username']}
🕐 Data Registrazione: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}
🔒 Ruolo Assegnato: Viewer (accesso in sola lettura)

Il nuovo utente ha attualmente accesso in sola lettura al sistema.
Puoi modificare i suoi permessi dall'interfaccia di amministrazione utenti.

🌐 Accedi al pannello admin: http://localhost:3001
👑 Login come Super Admin per gestire i ruoli utenti

---
Sistema ECES - EURING Code Evolution System
ISPRA - DG SINA
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                
                logger.info(f"Registration notification sent for user: {user_data['username']}")
                return True
            else:
                logger.warning("SMTP credentials not configured - email not sent")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send registration notification: {e}")
            return False
    
    def send_role_change_notification(self, user_data: dict, old_role: str, new_role: str) -> bool:
        """Send email notification for role changes"""
        if not self.email_enabled:
            logger.info(f"Email disabled - Would notify: Role change for {user_data['username']}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_data['email']
            msg['Cc'] = self.admin_email
            msg['Subject'] = f"ECES - Aggiornamento Permessi Account"
            
            # Role descriptions
            role_descriptions = {
                'viewer': 'Visualizzazione (sola lettura)',
                'user': 'Utente standard (riconoscimento e conversione)',
                'admin': 'Amministratore (gestione avanzata)',
                'super_admin': 'Super Amministratore (accesso completo)'
            }
            
            # Email body
            body = f"""
Ciao {user_data['full_name']},

I tuoi permessi nel sistema ECES sono stati aggiornati:

👤 Account: {user_data['username']}
📧 Email: {user_data['email']}

🔄 Modifica Permessi:
   Ruolo Precedente: {role_descriptions.get(old_role, old_role)}
   Nuovo Ruolo: {role_descriptions.get(new_role, new_role)}

🕐 Data Modifica: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}

🌐 Accedi al sistema: http://localhost:3001

Se hai domande sui tuoi nuovi permessi, contatta l'amministratore del sistema.

---
Sistema ECES - EURING Code Evolution System
ISPRA - DG SINA
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                
                logger.info(f"Role change notification sent for user: {user_data['username']}")
                return True
            else:
                logger.warning("SMTP credentials not configured - email not sent")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send role change notification: {e}")
            return False

    def send_contact_request_notification(
        self, owner_email: str, owner_full_name: str,
        requester_username: str, alias_id: int, message: Optional[str] = None
    ) -> bool:
        """
        Notifica il proprietario di una richiesta di contatto per eventi non
        condivisi legati a un anello (HANDOFF.md, punti 9-10, migrazione 003,
        tabella contact_requests). L'identita' del proprietario NON viene mai
        comunicata al richiedente da nessun'altra parte del sistema -- questa
        email e' l'unico posto in cui il proprietario stesso viene informato,
        e solo lui decide se condividere il dato e/o rivelarsi (due decisioni
        indipendenti, vedi contact_requests.shared / identity_revealed).
        """
        if not self.email_enabled:
            logger.info(
                f"Email disabled - Would notify: contact request for alias {alias_id} "
                f"from {requester_username} to {owner_email}"
            )
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = owner_email
            msg['Subject'] = "ECES - Richiesta di contatto per un tuo record archiviato"

            custom_message = f"\nMessaggio dal richiedente:\n\"{message}\"\n" if message else ""

            body = f"""
Ciao {owner_full_name},

L'utente '{requester_username}' ha richiesto di essere messo in contatto con te riguardo ad alcuni eventi che hai archiviato in ECES per l'anello con alias interno #{alias_id} (l'anello reale non viene mai esposto ad altri utenti).
{custom_message}
Puoi decidere autonomamente e in modo indipendente:
  1. Se condividere questi dati con '{requester_username}' (renderli visibili a lui specificamente)
  2. Se rivelare o meno la tua identita' a '{requester_username}'

Nessuna delle due scelte e' obbligatoria, e sono indipendenti tra loro: puoi condividere il dato restando anonimo, o viceversa.

🌐 Accedi a ECES per rispondere alla richiesta: http://localhost:3001

---
Sistema ECES - EURING Code Evolution System
ISPRA - DG SINA
"""

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()

                logger.info(f"Contact request notification sent for alias {alias_id}")
                return True
            else:
                logger.warning("SMTP credentials not configured - email not sent")
                return False

        except Exception as e:
            logger.error(f"Failed to send contact request notification: {e}")
            return False

# Global email service instance
email_service = EmailService()