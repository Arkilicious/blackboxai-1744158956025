from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction
from .models import TrackingRequest, TrackedEntity
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def setup_periodic_tasks(sender, **kwargs):
    """Initialize periodic cleanup tasks after migrations"""
    if sender.name == 'tracking':
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        try:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=24 * 60,  # Daily
                period=IntervalSchedule.MINUTES,
            )
            
            PeriodicTask.objects.update_or_create(
                name='cleanup_old_tracking_data',
                defaults={
                    'interval': schedule,
