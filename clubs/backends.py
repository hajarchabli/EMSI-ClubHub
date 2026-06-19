from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate using email instead of username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username
        if email is None:
            email = kwargs.get(User.EMAIL_FIELD)
        if not email:
            return None
        from django.db.models import Q
        try:
            # Match either by email or username to be robust
            user = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()
            if user is None:
                return None
        except Exception:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
