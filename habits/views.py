from datetime import timedelta

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count

from .models import Habit, HabitCompletion


class HabitListView(LoginRequiredMixin, ListView):
	model = Habit
	template_name = 'habits/habit_list.html'
	context_object_name = 'habits'

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user, is_active=True).order_by('-created_at')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		today = timezone.now().date()
		context['today_completions'] = list(
			HabitCompletion.objects.filter(habit__user=self.request.user, date=today).values_list('habit_id', flat=True)
		)
		return context


class HabitDetailView(LoginRequiredMixin, DetailView):
	model = Habit
	template_name = 'habits/habit_detail.html'
	context_object_name = 'habit'

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		habit = self.get_object()
		context['recent_completions'] = HabitCompletion.objects.filter(habit=habit).order_by('-date')[:30]
		return context


class HabitCreateView(LoginRequiredMixin, CreateView):
	model = Habit
	fields = ['name', 'description', 'category', 'frequency', 'recurrence_interval', 'target_count', 'unit', 'color']
	template_name = 'habits/habit_form.html'
	success_url = reverse_lazy('habits:habit_list')

	def form_valid(self, form):
		form.instance.user = self.request.user
		messages.success(self.request, 'Habit created successfully!')
		return super().form_valid(form)


class HabitUpdateView(LoginRequiredMixin, UpdateView):
	model = Habit
	fields = ['name', 'description', 'category', 'frequency', 'recurrence_interval', 'target_count', 'unit', 'color', 'is_active']
	template_name = 'habits/habit_form.html'
	success_url = reverse_lazy('habits:habit_list')

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user)

	def form_valid(self, form):
		messages.success(self.request, 'Habit updated successfully!')
		return super().form_valid(form)


class HabitDeleteView(LoginRequiredMixin, DeleteView):
	model = Habit
	template_name = 'habits/habit_confirm_delete.html'
	success_url = reverse_lazy('habits:habit_list')

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user)

	def delete(self, request, *args, **kwargs):
		messages.success(request, 'Habit deleted successfully!')
		return super().delete(request, *args, **kwargs)


class HabitCompleteView(LoginRequiredMixin, DetailView):
	model = Habit

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user)

	def post(self, request, *args, **kwargs):
		habit = self.get_object()
		today = timezone.now().date()

		completion, created = HabitCompletion.objects.get_or_create(
			habit=habit,
			date=today,
			defaults={'completed': True, 'quantity': habit.target_count}
		)

		if not created:
			completion.completed = not completion.completed
			completion.quantity = habit.target_count if completion.completed else 0
			completion.save()

		status = 'completed' if completion.completed else 'not completed'
		messages.success(request, f'Habit "{habit.name}" marked as {status} for today!')
		return redirect('habits:habit_list')


class HabitStreakView(LoginRequiredMixin, DetailView):
	model = Habit
	template_name = 'habits/habit_streak.html'
	context_object_name = 'habit'

	def get_queryset(self):
		return Habit.objects.filter(user=self.request.user)


class HabitCalendarView(LoginRequiredMixin, TemplateView):
	template_name = 'habits/habit_calendar.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		events = []
		for completion in HabitCompletion.objects.filter(habit__user=self.request.user, completed=True).select_related('habit'):
			events.append({
				'title': completion.habit.name,
				'start': completion.date.isoformat(),
				'url': reverse_lazy('habits:habit_detail', kwargs={'pk': completion.habit.pk}),
				'color': completion.habit.color,
			})
		context['calendar_events'] = events
		return context


class HabitStatsAPIView(LoginRequiredMixin, TemplateView):
	def get(self, request, *args, **kwargs):
		end_date = timezone.now().date()
		days = int(request.GET.get('days', 30))
		start_date = end_date - timedelta(days=days)

		completions = HabitCompletion.objects.filter(
			habit__user=request.user,
			date__range=[start_date, end_date],
			completed=True,
		).values('habit__name', 'date').annotate(count=Count('id'))

		habits_data = {}
		for completion in completions:
			habit_name = completion['habit__name']
			habits_data.setdefault(habit_name, {})[completion['date']] = completion['count']

		data = {'labels': [], 'datasets': []}
		current_date = start_date
		while current_date <= end_date:
			data['labels'].append(current_date.strftime('%m/%d'))
			current_date += timedelta(days=1)

		colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
		for index, (habit_name, dates) in enumerate(habits_data.items()):
			dataset = {
				'label': habit_name,
				'data': [],
				'backgroundColor': colors[index % len(colors)],
				'borderColor': colors[index % len(colors)],
				'fill': False,
			}
			current_date = start_date
			while current_date <= end_date:
				dataset['data'].append(dates.get(current_date, 0))
				current_date += timedelta(days=1)
			data['datasets'].append(dataset)

		return JsonResponse(data)