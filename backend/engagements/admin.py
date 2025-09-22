from django.contrib import admin

from .models import Engagement


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "type", "status", "start_date", "last_generated_period")
    list_filter = ("type", "status")
    search_fields = ("title", "client__name", "summary")
