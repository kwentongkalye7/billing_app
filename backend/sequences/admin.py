from django.contrib import admin

from .models import Sequence


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ("code", "prefix", "current_value", "reset_rule", "updated_at")
    search_fields = ("code", "name")
