from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DashboardWidget(models.Model):
    """User's dashboard widget preferences"""
    WIDGET_TYPES = [
        ('task_summary', 'Task Summary'),
        ('habit_tracker', 'Habit Tracker'),
        ('mood_chart', 'Mood Chart'),
        ('productivity_chart', 'Productivity Chart'),
        ('recent_journal', 'Recent Journal Entries'),
        ('upcoming_tasks', 'Upcoming Tasks'),
        ('streak_counter', 'Streak Counter'),
        ('quote_of_day', 'Quote of the Day'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    is_visible = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'widget_type']
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_widget_type_display()}"


class UserSettings(models.Model):
    """User's application settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='app_settings')
    
    # Dashboard settings
    dashboard_layout = models.CharField(max_length=20, default='grid', choices=[
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
    ])
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    task_reminders = models.BooleanField(default=True)
    habit_reminders = models.BooleanField(default=True)
    journal_reminders = models.BooleanField(default=True)
    
    # Privacy settings
    share_analytics = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=False)
    
    # UI preferences
    theme = models.CharField(max_length=10, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ])
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ])
    
    # Timezone
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Settings"


class MotivationalQuote(models.Model):
    """Daily motivational quotes"""
    quote = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.quote[:50]}... - {self.author}"


class UserQuote(models.Model):
    """Track which quotes users have seen"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_quotes')
    quote = models.ForeignKey(MotivationalQuote, on_delete=models.CASCADE)
    date_seen = models.DateField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'quote', 'date_seen']
    
    def __str__(self):
        return f"{self.user.username} saw quote on {self.date_seen}"