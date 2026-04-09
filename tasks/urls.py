from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task_complete'),
    path('<int:pk>/comments/', views.TaskCommentView.as_view(), name='task_comments'),
    path('api/filter/', views.TaskFilterAPIView.as_view(), name='task_filter_api'),
]




