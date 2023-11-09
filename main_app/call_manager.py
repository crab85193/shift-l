import os
from twilio.rest import Client

class CallManager:
    def __init__(self):
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.__client = Client(account_sid, auth_token)

    def call(self, message, phone_number):
        _twiml = f'<Response><Say>{message}</Say></Response>'
        _from  = os.environ.get("FROM_PHONE_NUMBER")
        _to    = f"+81{phone_number[1:]}"

        call = self.__client.calls.create(twiml=_twiml, to=_to, from_=_from)

        print(call.sid)