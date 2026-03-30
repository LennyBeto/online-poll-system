from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Poll(models.Model):
    question = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='polls'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_votes = models.PositiveIntegerField(default=0)  # denormalized cache
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return self.question

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def status(self):
        if not self.is_active:
            return 'inactive'
        if self.is_expired:
            return 'expired'
        return 'active'


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    vote_count = models.PositiveIntegerField(default=0)  # denormalized cache
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        indexes = [models.Index(fields=['poll', 'order'])]

    def __str__(self):
        return f"{self.poll.question[:30]} → {self.text}"


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    voter_ip = models.GenericIPAddressField()
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One vote per IP per poll
        unique_together = [['poll', 'voter_ip']]
        indexes = [
            models.Index(fields=['poll', 'voter_ip']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Vote on {self.poll.id} from {self.voter_ip}"