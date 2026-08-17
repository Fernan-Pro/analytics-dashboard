from rest_framework import serializers

from github.models import GitHubTrend


class GitHubTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubTrend
        fields = [
            "id",
            "repo_name",
            "stars",
            "forks",
            "language",
            "description",
            "url",
            "trending_date",
            "created_at",
        ]
        read_only_fields = fields