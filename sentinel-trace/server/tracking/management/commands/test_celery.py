from django.core.management.base import BaseCommand
from tracking.signals import cleanup_old_data
from celery import current_app
import json

class Command(BaseCommand):
    help = 'Test Celery setup by running the cleanup task manually'

    def handle(self, *args, **options):
        # Test direct function call
        self.stdout.write("Running cleanup directly...")
        result = cleanup_old_data()
        self.stdout.write(f"Direct result: {json.dumps(result, indent=2)}")

        # Test Celery task
        self.stdout.write("\nRunning cleanup via Celery...")
        task = current_app.send_task('tracking.cleanup_old_data')
        result = task.get(timeout=30)
        self.stdout.write(f"Celery result: {json.dumps(result, indent=2)}")

        self.stdout.write(self.style.SUCCESS("Celery test completed successfully"))
