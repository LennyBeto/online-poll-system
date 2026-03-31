from celery import shared_task
from django.utils import timezone
from .models import Poll


@shared_task
def close_expired_polls():
    """Mark expired polls as inactive. Run periodically via Celery Beat."""
    expired = Poll.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    )
    count = expired.update(is_active=False)
    return f"Closed {count} expired polls."