from django.db import models

# Create your models here.

class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    apply_url = models.URLField(max_length=500)
    source = models.CharField(max_length=100, default="Web Scraper Engine")
    date_scraped = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

# Append this to your existing zoltan/models.py file

class ScheduleTask(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default="Routine Focus")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{'✓' if self.is_completed else 'X'}]"

# Append this to your zoltan/models.py file

class RoadmapTrack(models.Model):
    """The overarching domain topic, e.g., 'Full-Stack Engineering'"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __blank__(self):
        return self.title


class RoadmapMilestone(models.Model):
    """Specific skill targets inside a track, e.g., 'Master Django Middleware'"""
    track = models.ForeignKey(RoadmapTrack, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    is_mastered = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.track.title} -> {self.title} [{'✓' if self.is_mastered else 'X'}]"

# Ensure these models are saved at the bottom of zoltan/models.py

class InterviewPipeline(models.Model):
    """Tracks company interviews and active rounds."""
    company_name = models.CharField(max_length=255)
    role_title = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default="Scheduled") # e.g., Technical Round, HR Round
    date_scheduled = models.DateTimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company_name} - {self.role_title} ({self.status})"


class InterviewQuestion(models.Model):
    """Core technical assessment questions to practice or review."""
    pipeline = models.ForeignKey(InterviewPipeline, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    topic = models.CharField(max_length=255) # e.g., "Full-Stack", "Digital Logic"
    question_text = models.TextField()
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.topic}] {self.question_text[:50]}"