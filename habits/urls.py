from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    path('', views.HabitListView.as_view(), name='habit_list'),
    path('create/', views.HabitCreateView.as_view(), name='habit_create'),
    path('<int:pk>/', views.HabitDetailView.as_view(), name='habit_detail'),
    path('<int:pk>/edit/', views.HabitUpdateView.as_view(), name='habit_update'),
    path('<int:pk>/delete/', views.HabitDeleteView.as_view(), name='habit_delete'),
    path('<int:pk>/complete/', views.HabitCompleteView.as_view(), name='habit_complete'),
    path('<int:pk>/streak/', views.HabitStreakView.as_view(), name='habit_streak'),
    path('calendar/', views.HabitCalendarView.as_view(), name='habit_calendar'),
    path('api/stats/', views.HabitStatsAPIView.as_view(), name='habit_stats_api'),
]




