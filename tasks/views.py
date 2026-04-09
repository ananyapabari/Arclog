from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Task, TaskComment, TaskAttachment


class TaskListView(LoginRequiredMixin, ListView):
    """List view for tasks"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        context['category_choices'] = Task.CATEGORY_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Detail view for tasks"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create view for tasks"""
    model = Task
    fields = ['title', 'description', 'category', 'priority', 'due_date', 'tags']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for tasks"""
    model = Task
    fields = ['title', 'description', 'category', 'priority', 'status', 'due_date', 'tags']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for tasks"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


class TaskCompleteView(LoginRequiredMixin, DetailView):
    """Mark task as complete"""
    model = Task
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        task.mark_completed()
        messages.success(request, f'Task "{task.title}" marked as completed!')
        return redirect('tasks:task_list')


class TaskCommentView(LoginRequiredMixin, CreateView):
    """Add comment to task"""
    model = TaskComment
    fields = ['content']
    template_name = 'tasks/task_comments.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.task = get_object_or_404(Task, pk=self.kwargs['pk'], user=self.request.user)
        messages.success(self.request, 'Comment added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.kwargs['pk']})


class TaskFilterAPIView(LoginRequiredMixin, ListView):
    """API view for task filtering"""
    
    def get(self, request, *args, **kwargs):
        tasks = Task.objects.filter(user=request.user)
        
        # Apply filters
        status = request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)
        
        category = request.GET.get('category')
        if category:
            tasks = tasks.filter(category=category)
        
        priority = request.GET.get('priority')
        if priority:
            tasks = tasks.filter(priority=priority)
        
        # Serialize tasks
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'category': task.category,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat(),
            })
        
        return JsonResponse({'tasks': data})