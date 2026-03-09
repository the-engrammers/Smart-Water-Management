# Email Service using SendGrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self, api_key=None, from_email=None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.from_email = from_email or os.getenv('SENDGRID_FROM_EMAIL')
        self.sg = SendGridAPIClient(self.api_key)

    def send_email(self, to_email, subject, content):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content
        )
        response = self.sg.send(message)
        return response.status_code
