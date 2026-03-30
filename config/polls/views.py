from django.db import transaction
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer, PollResultsSerializer
from analytics.models import PollAnalytics


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.filter(is_active=True).prefetch_related('options')
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active']
    search_fields = ['question', 'description']
    ordering_fields = ['created_at', 'total_votes']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Poll.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[])
    def vote(self, request, pk=None):
        poll = self.get_object()

        if poll.is_expired or not poll.is_active:
            return Response({'error': 'This poll is closed.'}, status=status.HTTP_400_BAD_REQUEST)

        voter_ip = get_client_ip(request)
        if Vote.objects.filter(poll=poll, voter_ip=voter_ip).exists():
            return Response({'error': 'You have already voted on this poll.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VoteSerializer(data=request.data, context={'poll': poll})
        serializer.is_valid(raise_exception=True)
        option_id = serializer.validated_data['option_id']

        with transaction.atomic():
            option = Option.objects.select_for_update().get(id=option_id)
            option.vote_count += 1
            option.save(update_fields=['vote_count'])

            Poll.objects.filter(pk=poll.pk).update(total_votes=poll.total_votes + 1)

            Vote.objects.create(
                poll=poll,
                option=option,
                voter_ip=voter_ip,
                user=request.user if request.user.is_authenticated else None,
            )

        # Invalidate cache
        cache.delete(f'poll_results_{poll.pk}')
        return Response({'message': 'Vote cast successfully.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[])
    def results(self, request, pk=None):
        poll = self.get_object()
        cache_key = f'poll_results_{poll.pk}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        serializer = PollResultsSerializer(poll)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[])
    def has_voted(self, request, pk=None):
        poll = self.get_object()
        voter_ip = get_client_ip(request)
        voted = Vote.objects.filter(poll=poll, voter_ip=voter_ip).exists()
        return Response({'has_voted': voted})