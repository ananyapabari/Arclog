from django.contrib import admin
from .models import Task
# from .models import TaskComment, TaskAttachment
# TODO: TaskComment and TaskAttachment models not yet implemented


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['category', 'priority', 'status', 'is_recurring', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category', 'priority', 'status')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'is_recurring', 'recurrence_type', 'recurrence_interval')
        }),
        ('Tracking', {
            'fields': ('estimated_duration', 'actual_duration', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# @admin.register(TaskComment)
# class TaskCommentAdmin(admin.ModelAdmin):
#     list_display = ['task', 'user', 'content', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['content', 'task__title', 'user__username']
#     readonly_fields = ['created_at', 'updated_at']
#     
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('task', 'user')


# @admin.register(TaskAttachment)
# class TaskAttachmentAdmin(admin.ModelAdmin):
#     list_display = ['filename', 'task', 'uploaded_by', 'uploaded_at']
#     list_filter = ['uploaded_at']
#     search_fields = ['filename', 'task__title', 'uploaded_by__username']
#     readonly_fields = ['uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'uploaded_by')