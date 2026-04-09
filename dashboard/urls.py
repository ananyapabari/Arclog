from django.urls import path
from . import views
from . import api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('api/task-stats/', views.TaskStatsAPIView.as_view(), name='task_stats_api'),
    path('api/habit-stats/', views.HabitStatsAPIView.as_view(), name='habit_stats_api'),
    path('api/mood-stats/', views.MoodStatsAPIView.as_view(), name='mood_stats_api'),
    path('api/v1/tasks/', api_views.TaskListAPI.as_view(), name='api_tasks'),
    path('api/v1/habits/', api_views.HabitListAPI.as_view(), name='api_habits'),
    path('api/v1/journals/', api_views.JournalListAPI.as_view(), name='api_journals'),
    path('api/v1/productivity-summary/', api_views.ProductivitySummaryAPI.as_view(), name='api_productivity_summary'),
]




