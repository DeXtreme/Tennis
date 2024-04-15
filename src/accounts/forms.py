import re
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms

def _validate_unique_username(value: str) -> None:
    if User.objects.filter(username=value).exists():
        raise ValidationError(_("An account with this email address already exists"),
                              code="invalid")
    
class _PasswordField(forms.CharField):
        default_error_messages = {
            "too_short": _("The password must be a minimum of 8 characters long"),
            "no_uppercase": _("The password must contain at least one uppercase character"),
            "no_number": _("The password must contain at least one number")}

        def validate(self,value):
            super().validate(value)
            errors = []
            
            if not len(value) >= 8:
                errors.append(ValidationError(self.error_messages["too_short"], code="too_short"))
            if not re.search(r"[A-Z]", value):
                errors.append(ValidationError(self.error_messages["no_uppercase"], code="no_uppercase"))
            elif not re.search(r"[0-9]", value):
                errors.append(ValidationError(self.error_messages["no_number"], code="no_number"))

            if errors:
                raise ValidationError(errors)
            
class RegisterForm(forms.Form):

    email = forms.EmailField(required=True,
                             help_text=_("Email address"),
                             validators=[_validate_unique_username])
    first_name = forms.CharField(required=True,
                                 max_length=50,
                                 help_text=_("First name"))
    last_name = forms.CharField(required=True,
                                max_length=50,
                                help_text=_("Last name"))
    password = _PasswordField(required=True,
                             help_text="Password")
