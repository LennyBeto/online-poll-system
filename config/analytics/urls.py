from django.urls import path
from .views import PollAnalyticsView, PollTimelineView, DashboardView, ExportPollView

urlpatterns = [
    path('poll/<int:poll_id>/', PollAnalyticsView.as_view()),
    path('poll/<int:poll_id>/timeline/', PollTimelineView.as_view()),
    path('poll/<int:poll_id>/export/', ExportPollView.as_view()),
    path('dashboard/', DashboardView.as_view()),
]