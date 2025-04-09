from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import TrackingRequest, TrackedEntity
from auditlog.models import LogEntry

@receiver(post_save, sender=TrackingRequest)
def log_tracking_request(sender, instance, created, **kwargs):
    if created:
        LogEntry.objects.log_action(
            user_id=instance.requester.pk,
            content_type_id=None,
            object_id=None,
            object_repr=f"Tracking request created: {instance.warrant_id}",
            action_flag=1,
            change_message=f"New tracking request for {instance.entities.count()} entities"
        )

from sentinel.celery import app

@app.task(name='tracking.cleanup_old_data')
def cleanup_old_data():
    """Clean up tracking data older than retention period"""
    retention_days = settings.TRACKING_SETTINGS.get('DATA_RETENTION_DAYS', 30)
    cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)
    
    # Delete completed requests older than retention period
    old_requests = TrackingRequest.objects.filter(
        status=TrackingRequest.Status.COMPLETED,
        end_date__lt=cutoff_date
    )
    request_count = old_requests.count()
    old_requests.delete()
    
    # Delete orphaned tracked entities
    orphaned_entities = TrackedEntity.objects.filter(
        trackingrequest__isnull=True,
        last_updated__lt=cutoff_date
    )
    entity_count = orphaned_entities.count()
    orphaned_entities.delete()
    
    return {
        'deleted_requests': request_count,
        'deleted_entities': entity_count
    }
