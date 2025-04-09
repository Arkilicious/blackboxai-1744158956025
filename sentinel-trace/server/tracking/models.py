from django.db import models
from django.core.validators import MinLengthValidator
from auth_app.models import CustomUser

class TrackedEntity(models.Model):
    class EntityType(models.TextChoices):
        PERSON = 'PERSON', 'Person'
        DEVICE = 'DEVICE', 'Device'
        VEHICLE = 'VEHICLE', 'Vehicle'

    identifier_type = models.CharField(max_length=20, choices=[
        ('IMEI', 'IMEI Number'),
        ('PHONE', 'Phone Number'), 
        ('SIM', 'SIM Card'),
        ('MAC', 'MAC Address'),
        ('IP', 'IP Address'),
        ('EMAIL', 'Email'),
        ('SOCIAL', 'Social Media Handle'),
    ])
    identifier_value = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=10, choices=EntityType.choices)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('identifier_type', 'identifier_value')
        verbose_name_plural = "Tracked Entities"

    def __str__(self):
        return f"{self.get_identifier_type_display()}: {self.identifier_value}"

class TrackingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Completed'

    requester = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='requests')
    entities = models.ManyToManyField(TrackedEntity)
    warrant_id = models.CharField(max_length=50, validators=[MinLengthValidator(10)])
    legal_basis = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_requests')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_approve_request", "Can approve tracking requests"),
        ]

    def __str__(self):
        return f"Request #{self.id} - {self.get_status_display()}"
