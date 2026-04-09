from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class JournalEntry(models.Model):
    """Journal entry model for daily reflections and mood tracking"""
    
    MOOD_CHOICES = [
        ('very_happy', 'Very Happy'),
        ('happy', 'Happy'),
        ('neutral', 'Neutral'),
        ('sad', 'Sad'),
        ('very_sad', 'Very Sad'),
        ('stressed', 'Stressed'),
        ('anxious', 'Anxious'),
        ('excited', 'Excited'),
        ('grateful', 'Grateful'),
        ('motivated', 'Motivated'),
        ('tired', 'Tired'),
        ('frustrated', 'Frustrated'),
    ]
    
    WEATHER_CHOICES = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='neutral')
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, blank=True)
    
    # Productivity metrics
    energy_level = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Energy level from 1-10"
    )
    productivity_score = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Productivity score from 1-10"
    )
    
    # Tags and hashtags
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy settings
    is_private = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']  # One entry per user per day
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'mood']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.get_mood_display()}"
    
    def clean(self):
        """Validate the journal entry"""
        if self.date > timezone.now().date():
            raise ValidationError("Cannot create journal entry for future dates.")
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    @property
    def word_count(self):
        """Return word count of the content"""
        return len(self.content.split())
    
    @property
    def mood_emoji(self):
        """Return emoji representation of mood"""
        mood_emojis = {
            'very_happy': '😄',
            'happy': '😊',
            'neutral': '😐',
            'sad': '😢',
            'very_sad': '😭',
            'stressed': '😰',
            'anxious': '😟',
            'excited': '🤩',
            'grateful': '🙏',
            'motivated': '💪',
            'tired': '😴',
            'frustrated': '😤',
        }
        return mood_emojis.get(self.mood, '😐')
    
    def get_mood_color(self):
        """Return Bootstrap color class for mood"""
        colors = {
            'very_happy': 'success',
            'happy': 'success',
            'neutral': 'secondary',
            'sad': 'warning',
            'very_sad': 'danger',
            'stressed': 'danger',
            'anxious': 'warning',
            'excited': 'primary',
            'grateful': 'info',
            'motivated': 'primary',
            'tired': 'secondary',
            'frustrated': 'danger',
        }
        return colors.get(self.mood, 'secondary')


class JournalTemplate(models.Model):
    """Templates for journal entries to help users get started"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_content = models.TextField(help_text="Template with placeholders like {date}, {mood}")
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JournalPrompt(models.Model):
    """Daily prompts to inspire journal entries"""
    CATEGORY_CHOICES = [
        ('reflection', 'Reflection'),
        ('gratitude', 'Gratitude'),
        ('goals', 'Goals'),
        ('relationships', 'Relationships'),
        ('creativity', 'Creativity'),
        ('wellness', 'Wellness'),
        ('career', 'Career'),
        ('learning', 'Learning'),
    ]
    
    prompt_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'prompt_text']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.prompt_text[:50]}..."


class JournalEntryAttachment(models.Model):
    """File attachments for journal entries"""
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='journal_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} - {self.entry.date}"