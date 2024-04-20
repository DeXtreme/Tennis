from django.core.exceptions import PermissionDenied

def is_account_active(info, **kwargs):
    error_msg = "This account is inactive"
    if info.context.user.is_active:
        return True

    raise PermissionDenied(error_msg)

