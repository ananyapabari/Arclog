from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import JournalEntry, JournalTemplate, JournalPrompt


class JournalListView(LoginRequiredMixin, ListView):
    """List view for journal entries"""
    model = JournalEntry
    template_name = 'journal/journal_list.html'
    context_object_name = 'entries'
    paginate_by = 20
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user).order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mood_choices'] = JournalEntry.MOOD_CHOICES
        return context


class JournalDetailView(LoginRequiredMixin, DetailView):
    """Detail view for journal entries"""
    model = JournalEntry
    template_name = 'journal/journal_detail.html'
    context_object_name = 'entry'
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)


class JournalCreateView(LoginRequiredMixin, CreateView):
    """Create view for journal entries"""
    model = JournalEntry
    fields = ['date', 'title', 'content', 'mood', 'weather', 'energy_level', 'productivity_score', 'tags']
    template_name = 'journal/journal_form.html'
    success_url = reverse_lazy('journal:journal_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Journal entry created successfully!')
        return super().form_valid(form)
    
    def get_initial(self):
        return {'date': timezone.now().date()}


class JournalUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for journal entries"""
    model = JournalEntry
    fields = ['date', 'title', 'content', 'mood', 'weather', 'energy_level', 'productivity_score', 'tags']
    template_name = 'journal/journal_form.html'
    success_url = reverse_lazy('journal:journal_list')
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Journal entry updated successfully!')
        return super().form_valid(form)


class JournalDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for journal entries"""
    model = JournalEntry
    template_name = 'journal/journal_confirm_delete.html'
    success_url = reverse_lazy('journal:journal_list')
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Journal entry deleted successfully!')
        return super().delete(request, *args, **kwargs)


class JournalCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view for journal entries"""
    template_name = 'journal/journal_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get journal entries for the calendar
        entries = JournalEntry.objects.filter(user=user)
        
        # Format entries for FullCalendar
        calendar_events = []
        for entry in entries:
            calendar_events.append({
                'title': entry.title or 'Untitled Entry',
                'start': entry.date.isoformat(),
                'url': reverse_lazy('journal:journal_detail', kwargs={'pk': entry.pk}),
                'color': self.get_mood_color(entry.mood),
            })
        
        context['calendar_events'] = calendar_events
        return context
    
    def get_mood_color(self, mood):
        """Get color for mood"""
        colors = {
            'very_happy': '#28a745',
            'happy': '#20c997',
            'neutral': '#6c757d',
            'sad': '#ffc107',
            'very_sad': '#dc3545',
            'stressed': '#fd7e14',
            'anxious': '#e83e8c',
            'excited': '#007bff',
            'grateful': '#17a2b8',
            'motivated': '#6f42c1',
            'tired': '#6c757d',
            'frustrated': '#dc3545',
        }
        return colors.get(mood, '#6c757d')


class JournalExportView(LoginRequiredMixin, ListView):
    """Export journal entries"""
    model = JournalEntry
    template_name = 'journal/journal_export.html'
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user).order_by('-date')


class JournalTemplateView(LoginRequiredMixin, ListView):
    """List journal templates"""
    model = JournalTemplate
    template_name = 'journal/journal_templates.html'
    context_object_name = 'templates'


class JournalPromptView(LoginRequiredMixin, ListView):
    """List journal prompts"""
    model = JournalPrompt
    template_name = 'journal/journal_prompts.html'
    context_object_name = 'prompts'
    
    def get_queryset(self):
        return JournalPrompt.objects.filter(is_active=True)