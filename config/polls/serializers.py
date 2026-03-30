from rest_framework import serializers
from .models import Poll, Option, Vote


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'order']


class OptionResultSerializer(serializers.ModelSerializer):
    votes = serializers.IntegerField(source='vote_count')
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ['id', 'text', 'votes', 'percentage']

    def get_percentage(self, obj):
        total = obj.poll.total_votes
        if not total:
            return 0.0
        return round((obj.vote_count / total) * 100, 2)


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    status = serializers.ReadOnlyField()
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Poll
        fields = [
            'id', 'question', 'description', 'options',
            'created_by', 'created_at', 'expires_at',
            'is_active', 'total_votes', 'view_count', 'status',
        ]
        read_only_fields = ['created_at', 'total_votes', 'view_count']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for i, option_data in enumerate(options_data):
            Option.objects.create(poll=poll, order=i, **option_data)
        return poll

    def validate_options(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("A poll must have at least 2 options.")
        if len(value) > 10:
            raise serializers.ValidationError("A poll can have at most 10 options.")
        return value


class VoteSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()

    def validate_option_id(self, value):
        poll = self.context.get('poll')
        if not Option.objects.filter(poll=poll, id=value).exists():
            raise serializers.ValidationError("Invalid option for this poll.")
        return value


class PollResultsSerializer(serializers.ModelSerializer):
    results = OptionResultSerializer(source='options', many=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'total_votes', 'results', 'created_at', 'expires_at']