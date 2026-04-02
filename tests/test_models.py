import pytest
from django.contrib.auth.models import User
from polls.models import Poll, Option, Vote


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='pass123')


@pytest.fixture
def poll(db, user):
    p = Poll.objects.create(question="Favorite color?", created_by=user)
    Option.objects.create(poll=p, text="Red", order=0)
    Option.objects.create(poll=p, text="Blue", order=1)
    return p


@pytest.mark.django_db
class TestPollModel:
    def test_poll_creation(self, poll):
        assert poll.question == "Favorite color?"
        assert poll.options.count() == 2
        assert poll.status == 'active'
        assert poll.total_votes == 0

    def test_option_percentage_zero_votes(self, poll):
        option = poll.options.first()
        assert option.percentage == 0.0

    def test_option_percentage_with_votes(self, poll):
        option = poll.options.first()
        option.vote_count = 3
        option.save()
        poll.total_votes = 10
        poll.save()
        assert option.percentage == 30.0

    def test_vote_uniqueness(self, poll, db):
        option = poll.options.first()
        Vote.objects.create(poll=poll, option=option, ip_address='1.2.3.4')
        with pytest.raises(Exception):
            Vote.objects.create(poll=poll, option=option, ip_address='1.2.3.4')