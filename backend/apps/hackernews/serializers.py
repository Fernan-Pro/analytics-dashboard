from rest_framework import serializers

from hackernews.models import HackerNewsStory


class HackerNewsStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HackerNewsStory
        fields = [
            "id",
            "hn_id",
            "title",
            "points",
            "comments",
            "author",
            "url",
            "created_at",
            "fetched_at",
        ]
        read_only_fields = fields