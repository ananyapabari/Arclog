from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from .models import UserProfile


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('dashboard:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully!')
        return response


class LoginView(LoginView):
    """User login view"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')


class LogoutView(View):
    """User logout view"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully!')
        return redirect('users:login')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully!')
        return redirect('users:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user profile or create one
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        context['profile'] = profile
        context['total_tasks'] = user.tasks.count()
        context['completed_tasks'] = user.tasks.filter(status='completed').count()
        context['journal_entries'] = user.journal_entries.count()
        context['habits'] = user.habits.count()
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """User profile edit view"""
    model = UserProfile
    fields = ['bio', 'location', 'birth_date', 'theme_preference', 'email_notifications']
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings view"""
    template_name = 'users/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle settings updates"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update theme preference
        theme = request.POST.get('theme_preference')
        if theme:
            profile.theme_preference = theme
            profile.save()
            messages.success(request, 'Settings updated successfully!')
        
        return redirect('users:settings')