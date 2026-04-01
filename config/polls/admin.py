from django.contrib import admin
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_by', 'total_votes', 'status', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question']
    inlines = [OptionInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['poll', 'option', 'ip_address', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['poll', 'option', 'voter', 'ip_address', 'created_at']