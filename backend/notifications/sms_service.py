# SMS Service using Twilio
from twilio.rest import Client
import os

class SMSService:
    def __init__(self, account_sid=None, auth_token=None, from_number=None):
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_FROM_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, to_number, message):
        message = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_number
        )
        return message.sid
