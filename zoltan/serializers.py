# zoltan/serializers.py
from rest_framework import serializers
from .models import Opportunity

class OpportunitySerializer(serializers.ModelSerializer):
    # Adding a custom formatted time string to display on API consumers
    time_since_scraped = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'company', 'location', 'apply_url', 'source', 'date_scraped', 'time_since_scraped']

    def get_time_since_scraped(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.date_scraped
        if delta.days > 0:
            return f"{delta.days} days ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} hours ago"
        return "Just now"