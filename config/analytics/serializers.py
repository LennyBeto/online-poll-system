from rest_framework import serializers
from .models import PollAnalytics, VoteEvent
from polls.models import Poll


class PollAnalyticsSerializer(serializers.ModelSerializer):
    poll_question = serializers.CharField(source='poll.question', read_only=True)
    total_votes = serializers.IntegerField(source='poll.total_votes', read_only=True)

    class Meta:
        model = PollAnalytics
        fields = ['poll_question', 'total_votes', 'view_count',
                  'unique_visitors', 'completion_rate', 'updated_at']


class VoteTimelineSerializer(serializers.Serializer):
    date = serializers.DateField()
    votes = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    total_polls = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    active_polls = serializers.IntegerField()
    top_polls = serializers.ListField()