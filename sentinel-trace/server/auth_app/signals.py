from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from auditlog.models import LogEntry

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        LogEntry.objects.log_action(
            user_id=instance.pk,
            content_type_id=None,
            object_id=None,
            object_repr=f"New user created: {instance.username}",
            action_flag=1,
            change_message="User account created"
        )

@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            changes = []
            for field in ['username', 'email', 'role', 'is_active']:
                if getattr(old_user, field) != getattr(instance, field):
                    changes.append(f"{field} changed from {getattr(old_user, field)} to {getattr(instance, field)}")
            
            if changes:
                LogEntry.objects.log_action(
                    user_id=instance.pk,
                    content_type_id=None,
                    object_id=None,
                    object_repr=f"User {instance.username} updated",
                    action_flag=2,
                    change_message=", ".join(changes)
                )
        except User.DoesNotExist:
            pass
