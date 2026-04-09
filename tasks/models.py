from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    """Task model for to-do list functionality"""
    
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('study', 'Study'),
        ('personal', 'Personal'),
        ('health', 'Health'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='personal')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Recurring task fields
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(365)])
    
    # Task estimation and tracking
    estimated_duration = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated duration in minutes")
    actual_duration = models.PositiveIntegerField(blank=True, null=True, help_text="Actual duration in minutes")
    
    # Tags for better organization
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def is_due_today(self):
        """Check if task is due today"""
        if self.due_date:
            return self.due_date.date() == timezone.now().date()
        return False
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def mark_completed(self):
        """Mark task as completed"""
        was_completed = self.status == 'completed'
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        if self.is_recurring and not was_completed:
            self.generate_next_instance()
    
    def mark_pending(self):
        """Mark task as pending"""
        self.status = 'pending'
        self.completed_at = None
        self.save()
    
    def get_priority_color(self):
        """Return Bootstrap color class for priority"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'dark'
        }
        return colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Return Bootstrap color class for status"""
        colors = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')

    def get_recurrence_delta(self):
        """Return timedelta for the current recurrence configuration."""
        if self.recurrence_type == 'daily':
            return timedelta(days=self.recurrence_interval)
        if self.recurrence_type == 'weekly':
            return timedelta(weeks=self.recurrence_interval)
        if self.recurrence_type == 'monthly':
            return timedelta(days=30 * self.recurrence_interval)
        if self.recurrence_type == 'custom':
            return timedelta(days=self.recurrence_interval)
        return None

    def generate_next_instance(self):
        """Create the next recurring task instance when the current one is completed."""
        if not self.is_recurring or self.recurrence_type == 'none' or not self.due_date:
            return None

        recurrence_delta = self.get_recurrence_delta()
        if recurrence_delta is None:
            return None

        next_due_date = self.due_date + recurrence_delta
        existing = Task.objects.filter(
            user=self.user,
            title=self.title,
            due_date=next_due_date,
            is_recurring=True,
            recurrence_type=self.recurrence_type,
            recurrence_interval=self.recurrence_interval,
        ).first()
        if existing:
            return existing

        return Task.objects.create(
            user=self.user,
            title=self.title,
            description=self.description,
            category=self.category,
            priority=self.priority,
            status='pending',
            due_date=next_due_date,
            is_recurring=True,
            recurrence_type=self.recurrence_type,
            recurrence_interval=self.recurrence_interval,
            estimated_duration=self.estimated_duration,
            tags=self.tags,
        )


class TaskComment(models.Model):
    """Comments on tasks for collaboration and notes"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"


class TaskAttachment(models.Model):
    """File attachments for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} - {self.task.title}"