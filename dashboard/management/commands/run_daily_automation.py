from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.services import get_basic_smart_reminders, sync_due_habit_completions
from tasks.models import Task


class Command(BaseCommand):
    help = 'Run recurring generation and basic reminder pipeline for all users.'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        generated_tasks = 0
        synced_habit_rows = 0
        reminder_count = 0

        completed_recurring_tasks = Task.objects.filter(
            is_recurring=True,
            status='completed',
            recurrence_type__in=['daily', 'weekly', 'monthly', 'custom'],
            due_date__isnull=False,
        ).select_related('user')

        for task in completed_recurring_tasks:
            if task.due_date and task.due_date.date() <= today:
                next_task = task.generate_next_instance()
                if next_task:
                    generated_tasks += 1

        users = {task.user for task in completed_recurring_tasks}
        for user in users:
            synced_habit_rows += sync_due_habit_completions(user=user, on_date=today)
            reminder_count += len(get_basic_smart_reminders(user=user))

        self.stdout.write(self.style.SUCCESS('Automation run complete'))
        self.stdout.write(f'Generated recurring tasks: {generated_tasks}')
        self.stdout.write(f'Synced habit completion rows: {synced_habit_rows}')
        self.stdout.write(f'Reminder candidates prepared: {reminder_count}')
