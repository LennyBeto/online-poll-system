import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from polls.models import Poll, Option


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username='tester', password='pass123')
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user


@pytest.fixture
def poll(db, auth_client):
    _, user = auth_client
    p = Poll.objects.create(question="Best language?", created_by=user)
    Option.objects.create(poll=p, text="Python", order=0)
    Option.objects.create(poll=p, text="Go", order=1)
    return p


@pytest.mark.django_db
class TestPollAPI:
    def test_list_polls(self, api_client, poll):
        response = api_client.get('/api/polls/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_create_poll_authenticated(self, auth_client, db):
        client, _ = auth_client
        data = {
            "question": "New poll?",
            "options": [{"text": "Yes"}, {"text": "No"}]
        }
        response = client.post('/api/polls/', data, format='json')
        assert response.status_code == 201
        assert response.data['question'] == "New poll?"

    def test_create_poll_unauthenticated(self, api_client, db):
        data = {
            "question": "New poll?",
            "options": [{"text": "Yes"}, {"text": "No"}]
        }
        response = api_client.post('/api/polls/', data, format='json')
        assert response.status_code == 401

    def test_vote_on_poll(self, api_client, poll):
        option = poll.options.first()
        response = api_client.post(f'/api/polls/{poll.id}/vote/', {'option_id': option.id})
        assert response.status_code == 201

    def test_duplicate_vote_prevented(self, api_client, poll):
        option = poll.options.first()
        api_client.post(f'/api/polls/{poll.id}/vote/', {'option_id': option.id})
        response = api_client.post(f'/api/polls/{poll.id}/vote/', {'option_id': option.id})
        assert response.status_code == 400

    def test_get_results(self, api_client, poll):
        response = api_client.get(f'/api/polls/{poll.id}/results/')
        assert response.status_code == 200
        assert 'total_votes' in response.data