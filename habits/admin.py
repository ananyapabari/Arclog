from django.contrib import admin

from .models import Habit, HabitCompletion, HabitStreak, HabitReminder


class HabitCompletionInline(admin.TabularInline):
	model = HabitCompletion
	extra = 0
	readonly_fields = ['created_at', 'updated_at']


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
	list_display = ['name', 'user', 'category', 'frequency', 'is_active', 'start_date']
	list_filter = ['category', 'frequency', 'is_active', 'is_archived', 'start_date']
	search_fields = ['name', 'description', 'user__username']
	readonly_fields = ['created_at', 'updated_at', 'current_streak', 'longest_streak', 'completion_rate']
	inlines = [HabitCompletionInline]

	fieldsets = (
		('Basic Information', {
			'fields': ('user', 'name', 'description', 'category', 'frequency')
		}),
		('Target & Tracking', {
			'fields': ('target_count', 'unit', 'color')
		}),
		('Scheduling', {
			'fields': ('start_date', 'end_date', 'reminder_time', 'reminder_enabled')
		}),
		('Status', {
			'fields': ('is_active', 'is_archived')
		}),
		('Statistics', {
			'fields': ('current_streak', 'longest_streak', 'completion_rate'),
			'classes': ('collapse',)
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user')


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
	list_display = ['habit', 'date', 'completed', 'quantity', 'created_at']
	list_filter = ['completed', 'date', 'created_at']
	search_fields = ['habit__name', 'notes']
	readonly_fields = ['created_at', 'updated_at']

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('habit')


@admin.register(HabitStreak)
class HabitStreakAdmin(admin.ModelAdmin):
	list_display = ['habit', 'start_date', 'end_date', 'length', 'is_active']
	list_filter = ['is_active', 'start_date']
	search_fields = ['habit__name']
	readonly_fields = ['created_at']

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('habit')


@admin.register(HabitReminder)
class HabitReminderAdmin(admin.ModelAdmin):
	list_display = ['habit', 'reminder_time', 'is_enabled', 'created_at']
	list_filter = ['is_enabled', 'created_at']
	search_fields = ['habit__name', 'message']
	readonly_fields = ['created_at']

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('habit')