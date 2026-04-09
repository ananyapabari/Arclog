from django.contrib import admin
from .models import JournalEntry, JournalTemplate, JournalPrompt
# from .models import JournalEntryAttachment
# TODO: JournalEntryAttachment model not yet implemented


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'title', 'mood', 'energy_level', 'productivity_score', 'created_at']
    list_filter = ['mood', 'weather', 'is_private', 'date', 'created_at']
    search_fields = ['title', 'content', 'user__username', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'word_count']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'date', 'title', 'content')
        }),
        ('Mood & Metrics', {
            'fields': ('mood', 'weather', 'energy_level', 'productivity_score')
        }),
        ('Organization', {
            'fields': ('tags', 'is_private')
        }),
        ('Statistics', {
            'fields': ('word_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(JournalTemplate)
class JournalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created_by', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'description', 'template_content']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(JournalPrompt)
class JournalPromptAdmin(admin.ModelAdmin):
    list_display = ['prompt_text', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['prompt_text']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request)


# @admin.register(JournalEntryAttachment)
# class JournalEntryAttachmentAdmin(admin.ModelAdmin):
#     list_display = ['filename', 'entry', 'uploaded_at']
#     list_filter = ['uploaded_at']
#     search_fields = ['filename', 'entry__title']
#     readonly_fields = ['uploaded_at']
#     
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('entry')