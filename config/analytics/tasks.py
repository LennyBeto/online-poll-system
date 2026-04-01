from celery import shared_task


@shared_task
def record_vote_analytics(vote_id):
    from polls.models import Vote
    from analytics.models import VoteEvent, PollAnalytics

    try:
        vote = Vote.objects.select_related('poll').get(id=vote_id)
        user_agent = vote.user_agent

        # Simple device detection
        device = 'mobile' if any(x in user_agent.lower() for x in ['mobile', 'android', 'iphone']) else 'desktop'
        browser = 'unknown'
        for b in ['Chrome', 'Firefox', 'Safari', 'Edge']:
            if b.lower() in user_agent.lower():
                browser = b
                break

        VoteEvent.objects.get_or_create(
            vote=vote,
            defaults={'browser': browser, 'device_type': device}
        )

        # Update analytics counters
        analytics, _ = PollAnalytics.objects.get_or_create(poll=vote.poll)
        analytics.view_count += 1
        analytics.save(update_fields=['view_count', 'updated_at'])

    except Exception as e:
        print(f"Analytics error for vote {vote_id}: {e}")