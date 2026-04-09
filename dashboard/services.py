from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from habits.models import Habit, HabitCompletion
from journal.models import JournalEntry
from tasks.models import Task


MOOD_BONUS = {
    'very_happy': 40,
    'happy': 34,
    'excited': 36,
    'grateful': 38,
    'motivated': 35,
    'neutral': 22,
    'tired': 16,
    'anxious': 14,
    'stressed': 12,
    'sad': 10,
    'frustrated': 8,
    'very_sad': 5,
}


def sync_due_habit_completions(user, on_date=None):
    """Ensure placeholder habit completion rows exist for all due habits on a date."""
    target_date = on_date or timezone.now().date()
    habits = Habit.objects.filter(user=user, is_active=True, is_archived=False)

    created_count = 0
    for habit in habits:
        completion = habit.ensure_completion_for(target_date)
        if completion and not completion.completed and completion.quantity == 0:
            # Count only rows created by this sync call.
            if completion.created_at.date() == target_date:
                created_count += 1

    return created_count


def _task_component(user, today):
    due_today = Task.objects.filter(user=user, due_date__date=today)
    total_due = due_today.count()
    if total_due == 0:
        return 100

    completed_today = due_today.filter(status='completed').count()
    return round((completed_today / total_due) * 100)


def _habit_component(user, today):
    active_habits = Habit.objects.filter(user=user, is_active=True, is_archived=False)

    due_habit_ids = [habit.id for habit in active_habits if habit.is_due_on(today)]
    total_due = len(due_habit_ids)
    if total_due == 0:
        return 100

    completed_due = HabitCompletion.objects.filter(
        habit_id__in=due_habit_ids,
        date=today,
        completed=True,
    ).count()

    return round((completed_due / total_due) * 100)


def _journal_component(user, today):
    entry = JournalEntry.objects.filter(user=user, date=today).first()
    if not entry:
        return 0

    presence_score = 60
    mood_score = MOOD_BONUS.get(entry.mood, 20)
    return min(100, presence_score + mood_score)


def calculate_productivity_score(user, on_date=None):
    """Compute weighted productivity score from tasks, habits, and journal data."""
    today = on_date or timezone.now().date()

    task_score = _task_component(user, today)
    habit_score = _habit_component(user, today)
    journal_score = _journal_component(user, today)

    overall_score = round((task_score * 0.5) + (habit_score * 0.3) + (journal_score * 0.2))

    return {
        'overall': max(0, min(100, overall_score)),
        'task_score': task_score,
        'habit_score': habit_score,
        'journal_score': journal_score,
    }


def get_basic_smart_reminders(user, limit=5):
    """Return lightweight in-app reminders without external notification services."""
    now = timezone.now()
    today = now.date()

    reminders = []

    upcoming_tasks = Task.objects.filter(
        user=user,
        status__in=['pending', 'in_progress'],
        due_date__isnull=False,
        due_date__date=today,
    ).order_by('due_date')[:limit]

    for task in upcoming_tasks:
        reminders.append({
            'type': 'task',
            'message': f'Task due today: {task.title}',
            'time': task.due_date,
        })

    if len(reminders) < limit:
        pending_habit_count = HabitCompletion.objects.filter(
            habit__user=user,
            habit__is_active=True,
            date=today,
            completed=False,
        ).count()
        if pending_habit_count:
            reminders.append({
                'type': 'habit',
                'message': f'{pending_habit_count} habits still pending today.',
                'time': None,
            })

    return reminders[:limit]


def build_weekly_productivity_trends(user, days=7):
    """Return day-wise task/habit/journal trend metrics for recent days."""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    labels = []
    task_completion = []
    habit_completion = []
    journal_presence = []

    current = start_date
    while current <= end_date:
        labels.append(current.strftime('%a'))

        due_tasks = Task.objects.filter(user=user, due_date__date=current)
        due_count = due_tasks.count()
        done_count = due_tasks.filter(status='completed').count()
        task_completion.append(round((done_count / due_count) * 100) if due_count else 100)

        active_habits = Habit.objects.filter(user=user, is_active=True, is_archived=False)
        due_habits = [habit.id for habit in active_habits if habit.is_due_on(current)]
        due_habit_count = len(due_habits)
        done_habits = HabitCompletion.objects.filter(
            habit_id__in=due_habits,
            date=current,
            completed=True,
        ).count()
        habit_completion.append(round((done_habits / due_habit_count) * 100) if due_habit_count else 100)

        journal_presence.append(100 if JournalEntry.objects.filter(user=user, date=current).exists() else 0)
        current += timedelta(days=1)

    return {
        'labels': labels,
        'task_completion': task_completion,
        'habit_completion': habit_completion,
        'journal_presence': journal_presence,
    }


def generate_rule_based_insights(user):
    """Generate non-ML insights from user behavior patterns."""
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    insights = []

    habit_days = set(
        HabitCompletion.objects.filter(
            habit__user=user,
            date__gte=month_ago,
            completed=True,
        ).values_list('date', flat=True)
    )

    productive_days = set(
        Task.objects.filter(
            user=user,
            completed_at__date__gte=month_ago,
            status='completed',
        ).values_list('completed_at__date', flat=True)
    )

    overlap_days = len(habit_days.intersection(productive_days))
    if productive_days and (overlap_days / len(productive_days)) >= 0.6:
        insights.append('You are more productive on days you complete habits.')

    overdue_count = Task.objects.filter(
        user=user,
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress'],
    ).count()
    if overdue_count >= 5:
        insights.append('Your productivity drops when tasks are overdue. Consider clearing old pending tasks first.')

    recent_journal_mood = JournalEntry.objects.filter(
        user=user,
        date__gte=today - timedelta(days=14),
    ).values_list('mood', flat=True)
    low_mood = {'very_sad', 'sad', 'frustrated', 'stressed'}
    if recent_journal_mood and sum(1 for mood in recent_journal_mood if mood in low_mood) >= 5:
        insights.append('Recent journal mood trends are low. Try lighter task loads and small habit wins this week.')

    if not insights:
        insights.append('Great consistency so far. Keep balancing tasks, habits, and journal reflections.')

    return insights
