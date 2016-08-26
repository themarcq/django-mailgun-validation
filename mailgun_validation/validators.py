from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from django.utils.encoding import force_text
from mailgun_validation.exceptions import MailgunException
import requests

class EmailValidator(object):
    messages = {
        'not_valid':  _('Not a valid email address'),
        'hint': _('Did you mean'),
    }
    code = 'invalid'

    def __init__(self, message=None, code=None, api_key=None):
        self.api_key = api_key
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        value = force_text(value)
        
        if self.api_key is None:
            raise MailgunException('No API key was provided.')
            
        self.validate_address(value)

    def validate_address(self, email):
        response = requests.get(
            "https://api.mailgun.net/v2/address/validate",
            auth=("api", self.api_key),
            params={"address": email}
        )
        if response.ok:
            response_data = response.json()
            if not response['is_valid']:
                hint = response.get('did_you_mean', False)
                if not hint:
                    raise ValidationError(self.messages['not_valid'], code=self.code)
                else:
                    raise ValidationError("{} {}?".format(self.messages['hint'], hint))
        else:
            raise MailgunException('Problems with the Mailgun web service')


api_key = None
if hasattr(settings, 'MAILGUN_API_KEY'):
    api_key = settings.MAILGUN_API_KEY

validate_email = EmailValidator(api_key=api_key)
