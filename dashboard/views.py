from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.auth.models import User

from tasks.models import Task
from journal.models import JournalEntry
from habits.models import Habit, HabitCompletion
from dashboard.models import MotivationalQuote, UserQuote
from dashboard.services import (
    build_weekly_productivity_trends,
    calculate_productivity_score,
    generate_rule_based_insights,
    get_basic_smart_reminders,
    sync_due_habit_completions,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with productivity overview"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # Keep habit completions in sync for due habits each day.
        sync_due_habit_completions(user=user, on_date=today)
        
        # Task statistics
        context['today_tasks'] = Task.objects.filter(
            user=user,
            due_date__date=today
        ).count()
        
        context['completed_tasks'] = Task.objects.filter(
            user=user,
            due_date__date=today,
            status='completed'
        ).count()
        
        context['overdue_tasks'] = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # Habit statistics
        context['total_habits'] = Habit.objects.filter(user=user, is_active=True).count()
        context['completed_habits_today'] = HabitCompletion.objects.filter(
            habit__user=user,
            date=today,
            completed=True
        ).count()
        
        # Journal statistics
        context['journal_streak'] = self.get_journal_streak(user)
        context['has_journal_today'] = JournalEntry.objects.filter(
            user=user,
            date=today
        ).exists()
        
        # Recent activities
        context['recent_tasks'] = Task.objects.filter(user=user).order_by('-created_at')[:5]
        context['recent_journals'] = JournalEntry.objects.filter(user=user).order_by('-date')[:3]
        
        # Motivational quote
        context['daily_quote'] = self.get_daily_quote(user)

        # Productivity scoring + lightweight in-app reminders
        score_data = calculate_productivity_score(user=user, on_date=today)
        context['productivity_score'] = score_data['overall']
        context['productivity_score_breakdown'] = score_data
        context['smart_reminders'] = get_basic_smart_reminders(user=user)
        
        return context
    
    def get_journal_streak(self, user):
        """Calculate current journaling streak"""
        today = timezone.now().date()
        streak = 0
        
        for i in range(365):  # Check up to a year
            check_date = today - timedelta(days=i)
            if JournalEntry.objects.filter(user=user, date=check_date).exists():
                streak += 1
            else:
                break
                
        return streak
    
    def get_daily_quote(self, user):
        """Get today's motivational quote"""
        today = timezone.now().date()
        
        # Check if user has already seen a quote today
        seen_quotes = UserQuote.objects.filter(
            user=user,
            date_seen=today
        ).values_list('quote_id', flat=True)
        
        # Get a random quote that user hasn't seen today
        quote = MotivationalQuote.objects.filter(
            is_active=True
        ).exclude(
            id__in=seen_quotes
        ).order_by('?').first()
        
        if not quote:
            # If all quotes seen today, get any random quote
            quote = MotivationalQuote.objects.filter(is_active=True).order_by('?').first()
        
        if quote:
            # Mark quote as seen
            UserQuote.objects.get_or_create(
                user=user,
                quote=quote,
                date_seen=today
            )
            return quote
        
        return None


class AnalyticsView(LoginRequiredMixin, TemplateView):
    """Analytics dashboard with charts and detailed statistics"""
    template_name = 'dashboard/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Task analytics
        context['task_stats'] = {
            'total_tasks': Task.objects.filter(user=user).count(),
            'completed_tasks': Task.objects.filter(user=user, status='completed').count(),
            'pending_tasks': Task.objects.filter(user=user, status='pending').count(),
            'overdue_tasks': Task.objects.filter(
                user=user,
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
        }
        
        # Habit analytics
        context['habit_stats'] = {
            'total_habits': Habit.objects.filter(user=user).count(),
            'active_habits': Habit.objects.filter(user=user, is_active=True).count(),
            'completed_today': HabitCompletion.objects.filter(
                habit__user=user,
                date=today,
                completed=True
            ).count(),
        }
        
        # Journal analytics
        context['journal_stats'] = {
            'total_entries': JournalEntry.objects.filter(user=user).count(),
            'entries_this_month': JournalEntry.objects.filter(
                user=user,
                date__gte=month_ago
            ).count(),
            'current_streak': self.get_journal_streak(user),
        }

        # Weekly trends and rule-based insights
        context['weekly_trends'] = build_weekly_productivity_trends(user=user, days=7)
        context['insights'] = generate_rule_based_insights(user=user)
        
        return context
    
    def get_journal_streak(self, user):
        """Calculate current journaling streak"""
        today = timezone.now().date()
        streak = 0
        
        for i in range(365):  # Check up to a year
            check_date = today - timedelta(days=i)
            if JournalEntry.objects.filter(user=user, date=check_date).exists():
                streak += 1
            else:
                break
                
        return streak


class TaskStatsAPIView(LoginRequiredMixin, TemplateView):
    """API endpoint for task statistics data"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        days = int(request.GET.get('days', 30))
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get task completion data
        tasks_by_date = Task.objects.filter(
            user=user,
            completed_at__date__range=[start_date, end_date],
            status='completed'
        ).extra(
            select={'day': 'date(completed_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Get task creation data
        created_by_date = Task.objects.filter(
            user=user,
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        data = {
            'labels': [],
            'completed': [],
            'created': []
        }
        
        # Fill in data for all days
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            data['labels'].append(date_str)
            
            # Find completed tasks for this date
            completed_count = next(
                (item['count'] for item in tasks_by_date if item['day'] == current_date), 0
            )
            data['completed'].append(completed_count)
            
            # Find created tasks for this date
            created_count = next(
                (item['count'] for item in created_by_date if item['day'] == current_date), 0
            )
            data['created'].append(created_count)
            
            current_date += timedelta(days=1)
        
        return JsonResponse(data)


class HabitStatsAPIView(LoginRequiredMixin, TemplateView):
    """API endpoint for habit statistics data"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        days = int(request.GET.get('days', 30))
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get habit completion data
        completions = HabitCompletion.objects.filter(
            habit__user=user,
            date__range=[start_date, end_date],
            completed=True
        ).values('habit__name', 'date').annotate(count=Count('id'))
        
        # Group by habit
        habits_data = {}
        for completion in completions:
            habit_name = completion['habit__name']
            if habit_name not in habits_data:
                habits_data[habit_name] = {}
            habits_data[habit_name][completion['date']] = completion['count']
        
        # Prepare data for Chart.js
        data = {
            'labels': [],
            'datasets': []
        }
        
        # Generate date labels
        current_date = start_date
        while current_date <= end_date:
            data['labels'].append(current_date.strftime('%m/%d'))
            current_date += timedelta(days=1)
        
        # Create dataset for each habit
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        color_index = 0
        
        for habit_name, dates in habits_data.items():
            dataset = {
                'label': habit_name,
                'data': [],
                'backgroundColor': colors[color_index % len(colors)],
                'borderColor': colors[color_index % len(colors)],
                'fill': False
            }
            
            current_date = start_date
            while current_date <= end_date:
                dataset['data'].append(dates.get(current_date, 0))
                current_date += timedelta(days=1)
            
            data['datasets'].append(dataset)
            color_index += 1
        
        return JsonResponse(data)


class MoodStatsAPIView(LoginRequiredMixin, TemplateView):
    """API endpoint for mood statistics data"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        days = int(request.GET.get('days', 30))
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get mood data
        moods = JournalEntry.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('mood', 'date').order_by('date')
        
        # Prepare data
        data = {
            'labels': [],
            'datasets': [{
                'label': 'Mood Score',
                'data': [],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'fill': True
            }]
        }
        
        # Mood to number mapping
        mood_scores = {
            'very_sad': 1,
            'sad': 2,
            'frustrated': 3,
            'tired': 4,
            'neutral': 5,
            'anxious': 6,
            'stressed': 7,
            'happy': 8,
            'excited': 9,
            'very_happy': 10,
            'grateful': 9,
            'motivated': 8,
        }
        
        # Fill in data
        current_date = start_date
        while current_date <= end_date:
            data['labels'].append(current_date.strftime('%m/%d'))
            
            # Find mood for this date
            mood_entry = next(
                (entry for entry in moods if entry['date'] == current_date), None
            )
            
            if mood_entry:
                score = mood_scores.get(mood_entry['mood'], 5)
            else:
                score = None  # No entry for this date
            
            data['datasets'][0]['data'].append(score)
            current_date += timedelta(days=1)
        
        return JsonResponse(data)