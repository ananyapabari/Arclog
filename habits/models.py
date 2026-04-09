from datetime import timedelta

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Habit(models.Model):
	CATEGORY_CHOICES = [
		('health', 'Health'),
		('fitness', 'Fitness'),
		('learning', 'Learning'),
		('mindfulness', 'Mindfulness'),
		('productivity', 'Productivity'),
		('personal', 'Personal'),
		('other', 'Other'),
	]

	FREQUENCY_CHOICES = [
		('daily', 'Daily'),
		('weekly', 'Weekly'),
		('monthly', 'Monthly'),
		('custom', 'Custom'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='personal')
	frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
	recurrence_interval = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(365)])
	target_count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
	unit = models.CharField(max_length=50, blank=True, default='times')
	color = models.CharField(max_length=20, blank=True, default='#007bff')
	start_date = models.DateField(default=timezone.now)
	end_date = models.DateField(null=True, blank=True)
	reminder_time = models.TimeField(null=True, blank=True)
	reminder_enabled = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_archived = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.name

	@property
	def current_streak(self):
		today = timezone.now().date()
		streak = 0
		current_date = today

		while True:
			completion = HabitCompletion.objects.filter(habit=self, date=current_date, completed=True).first()
			if completion:
				streak += 1
				current_date -= timedelta(days=1)
			else:
				break

		return streak

	@property
	def longest_streak(self):
		longest = 0
		current = 0
		completions = HabitCompletion.objects.filter(habit=self, completed=True).order_by('date')

		previous_date = None
		for completion in completions:
			if previous_date and completion.date == previous_date + timedelta(days=1):
				current += 1
			else:
				current = 1
			previous_date = completion.date
			longest = max(longest, current)

		return longest

	@property
	def completion_rate(self):
		total = HabitCompletion.objects.filter(habit=self).count()
		if not total:
			return 0
		completed = HabitCompletion.objects.filter(habit=self, completed=True).count()
		return round((completed / total) * 100, 1)

	def is_due_on(self, date_value):
		"""Determine whether this habit is scheduled for a given date."""
		if date_value < self.start_date:
			return False
		if self.end_date and date_value > self.end_date:
			return False
		if not self.is_active or self.is_archived:
			return False

		days_from_start = (date_value - self.start_date).days
		if self.frequency == 'daily':
			return days_from_start % self.recurrence_interval == 0
		if self.frequency == 'weekly':
			return days_from_start % (7 * self.recurrence_interval) == 0
		if self.frequency == 'monthly':
			return days_from_start % (30 * self.recurrence_interval) == 0
		if self.frequency == 'custom':
			return days_from_start % self.recurrence_interval == 0
		return False

	def ensure_completion_for(self, date_value):
		"""Create a placeholder completion row for due dates if missing."""
		if not self.is_due_on(date_value):
			return None
		completion, _ = HabitCompletion.objects.get_or_create(
			habit=self,
			date=date_value,
			defaults={
				'completed': False,
				'quantity': 0,
			},
		)
		return completion


class HabitCompletion(models.Model):
	habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
	date = models.DateField()
	completed = models.BooleanField(default=True)
	quantity = models.PositiveIntegerField(default=0)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-date', '-created_at']
		unique_together = ['habit', 'date']

	def __str__(self):
		return f'{self.habit.name} - {self.date}'


class HabitStreak(models.Model):
	habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='streaks')
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	length = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-start_date']

	def __str__(self):
		return f'{self.habit.name} streak ({self.length})'


class HabitReminder(models.Model):
	habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='reminders')
	reminder_time = models.TimeField()
	is_enabled = models.BooleanField(default=True)
	message = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.habit.name} reminder at {self.reminder_time}'
