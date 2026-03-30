from django.db import models
from polls.models import Poll, Vote


class PollAnalytics(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE, related_name='analytics')
    view_count = models.PositiveIntegerField(default=0)
    unique_voters = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Analytics for Poll {self.poll_id}"


class VoteEvent(models.Model):
    """Stores enriched per-vote analytics data."""
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, related_name='event')
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)