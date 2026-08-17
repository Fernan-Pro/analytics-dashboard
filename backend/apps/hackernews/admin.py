from django.contrib import admin

from hackernews.models import HackerNewsStory


@admin.register(HackerNewsStory)
class HackerNewsStoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "points", "comments", "created_at")
    list_filter = ("author",)
    search_fields = ("title", "author")
    date_hierarchy = "created_at"
    ordering = ("-created_at", "-points")