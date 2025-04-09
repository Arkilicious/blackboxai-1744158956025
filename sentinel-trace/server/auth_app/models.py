from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        ANALYST = 'ANALYST', _('Analyst')
        FIELD_OFFICER = 'FIELD_OFFICER', _('Field Officer')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FIELD_OFFICER,
    )
    cac_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        permissions = [
            ("can_request_tracking", "Can request tracking operations"),
            ("can_approve_tracking", "Can approve tracking requests"),
            ("can_access_sensitive_data", "Can access sensitive evidence"),
        ]
