from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from polls.models import Poll, Vote, Option
import json


class PollAnalyticsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, poll_id):
        poll = Poll.objects.prefetch_related('options', 'votes').get(pk=poll_id)
        options_data = [
            {
                'option': o.text,
                'votes': o.vote_count,
                'percentage': round((o.vote_count / poll.total_votes * 100), 2) if poll.total_votes else 0,
            }
            for o in poll.options.all()
        ]
        return Response({
            'poll_id': poll.id,
            'question': poll.question,
            'total_votes': poll.total_votes,
            'view_count': poll.view_count,
            'status': poll.status,
            'options': options_data,
        })


class PollTimelineView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, poll_id):
        timeline = (
            Vote.objects.filter(poll_id=poll_id)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(votes=Count('id'))
            .order_by('date')
        )
        return Response(list(timeline))


class DashboardView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        total_polls = Poll.objects.count()
        active_polls = Poll.objects.filter(is_active=True).count()
        total_votes = sum(Poll.objects.values_list('total_votes', flat=True))
        top_polls = Poll.objects.order_by('-total_votes')[:5].values('id', 'question', 'total_votes')
        return Response({
            'total_polls': total_polls,
            'active_polls': active_polls,
            'total_votes': total_votes,
            'top_polls': list(top_polls),
        })


class ExportPollView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, poll_id):
        poll = Poll.objects.prefetch_related('options').get(pk=poll_id)
        fmt = request.query_params.get('format', 'json')
        data = {
            'poll': poll.question,
            'total_votes': poll.total_votes,
            'options': [
                {'text': o.text, 'votes': o.vote_count} for o in poll.options.all()
            ],
        }
        if fmt == 'csv':
            import csv
            from django.http import HttpResponse
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="poll_{poll_id}.csv"'
            writer = csv.DictWriter(response, fieldnames=['text', 'votes'])
            writer.writeheader()
            writer.writerows(data['options'])
            return response
        return Response(data)