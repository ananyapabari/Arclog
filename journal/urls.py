from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.JournalListView.as_view(), name='journal_list'),
    path('create/', views.JournalCreateView.as_view(), name='journal_create'),
    path('<int:pk>/', views.JournalDetailView.as_view(), name='journal_detail'),
    path('<int:pk>/edit/', views.JournalUpdateView.as_view(), name='journal_update'),
    path('<int:pk>/delete/', views.JournalDeleteView.as_view(), name='journal_delete'),
    path('calendar/', views.JournalCalendarView.as_view(), name='journal_calendar'),
    path('export/', views.JournalExportView.as_view(), name='journal_export'),
    path('templates/', views.JournalTemplateView.as_view(), name='journal_templates'),
    path('prompts/', views.JournalPromptView.as_view(), name='journal_prompts'),
]




