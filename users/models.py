from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with productivity tracking fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def total_tasks_completed(self):
        """Calculate total completed tasks for this user"""
        from tasks.models import Task
        return Task.objects.filter(user=self.user, status='completed').count()

    @property
    def current_streak(self):
        """Calculate current journaling streak"""
        from journal.models import JournalEntry
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        streak = 0
        
        # Check consecutive days backwards from today
        for i in range(365):  # Check up to a year
            check_date = today - timedelta(days=i)
            if JournalEntry.objects.filter(user=self.user, date=check_date).exists():
                streak += 1
            else:
                break
                
        return streak

    @property
    def longest_streak(self):
        """Calculate longest journaling streak"""
        from journal.models import JournalEntry
        from django.utils import timezone
        from datetime import timedelta
        
        entries = JournalEntry.objects.filter(user=self.user).order_by('date')
        if not entries.exists():
            return 0
            
        longest_streak = 0
        current_streak = 1
        
        for i in range(1, len(entries)):
            prev_date = entries[i-1].date
            curr_date = entries[i].date
            
            if (curr_date - prev_date).days == 1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
                
        return max(longest_streak, current_streak)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save the profile when the user is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()