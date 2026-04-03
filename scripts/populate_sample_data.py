"""
Run with: python manage.py shell < scripts/populate_sample_data.py
"""
from django.contrib.auth.models import User
from polls.models import Poll, Option

user, _ = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com'})
user.set_password('demo1234')
user.save()

polls_data = [
    {
        "question": "What is your favorite programming language?",
        "options": ["Python", "JavaScript", "Go", "Rust", "TypeScript"]
    },
    {
        "question": "Preferred database?",
        "options": ["PostgreSQL", "MySQL", "MongoDB", "SQLite"]
    },
    {
        "question": "Best frontend framework?",
        "options": ["React", "Vue", "Angular", "Svelte"]
    },
]

for data in polls_data:
    poll = Poll.objects.create(question=data['question'], created_by=user)
    for i, text in enumerate(data['options']):
        Option.objects.create(poll=poll, text=text, order=i)
    print(f"Created: {poll.question}")

print("Sample data loaded!")