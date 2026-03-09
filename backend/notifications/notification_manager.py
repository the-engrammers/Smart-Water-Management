# Notification Manager
from .sms_service import SMSService
from .email_service import EmailService

class NotificationManager:
    def __init__(self, user_prefs):
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.user_prefs = user_prefs  # Dict: user_id -> {sms, email, ...}

    def send_alert(self, user_id, message, subject, severity):
        prefs = self.user_prefs.get(user_id, {})
        results = {}
        if prefs.get('sms'):
            results['sms'] = self.sms_service.send_sms(prefs['sms'], message)
        if prefs.get('email'):
            results['email'] = self.email_service.send_email(prefs['email'], subject, message)
        # Add more channels as needed
        return results
