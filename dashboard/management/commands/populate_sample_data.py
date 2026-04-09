from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import MotivationalQuote
from tasks.models import Task
from journal.models import JournalEntry
from habits.models import Habit, HabitCompletion
from django.utils import timezone
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create motivational quotes
        self.create_quotes()
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        # Create sample tasks
        self.create_sample_tasks(admin_user)
        
        # Create sample journal entries
        self.create_sample_journals(admin_user)
        
        # Create sample habits
        self.create_sample_habits(admin_user)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
    
    def create_quotes(self):
        """Create motivational quotes"""
        quotes_data = [
            {
                'quote': 'The way to get started is to quit talking and begin doing.',
                'author': 'Walt Disney',
                'category': 'motivation'
            },
            {
                'quote': 'Don\'t be afraid to give up the good to go for the great.',
                'author': 'John D. Rockefeller',
                'category': 'success'
            },
            {
                'quote': 'Innovation distinguishes between a leader and a follower.',
                'author': 'Steve Jobs',
                'category': 'leadership'
            },
            {
                'quote': 'The future belongs to those who believe in the beauty of their dreams.',
                'author': 'Eleanor Roosevelt',
                'category': 'dreams'
            },
            {
                'quote': 'Success is not final, failure is not fatal: it is the courage to continue that counts.',
                'author': 'Winston Churchill',
                'category': 'perseverance'
            },
            {
                'quote': 'The only way to do great work is to love what you do.',
                'author': 'Steve Jobs',
                'category': 'passion'
            },
            {
                'quote': 'Life is what happens to you while you\'re busy making other plans.',
                'author': 'John Lennon',
                'category': 'life'
            },
            {
                'quote': 'The way to get started is to quit talking and begin doing.',
                'author': 'Walt Disney',
                'category': 'action'
            },
        ]
        
        for quote_data in quotes_data:
            MotivationalQuote.objects.get_or_create(
                quote=quote_data['quote'],
                defaults={
                    'author': quote_data['author'],
                    'category': quote_data['category'],
                    'is_active': True
                }
            )
        
        self.stdout.write('Created motivational quotes')
    
    def create_sample_tasks(self, user):
        """Create sample tasks"""
        tasks_data = [
            {
                'title': 'Complete project proposal',
                'description': 'Finish the quarterly project proposal for the marketing team',
                'category': 'work',
                'priority': 'high',
                'status': 'pending',
                'due_date': timezone.now() + timedelta(days=2)
            },
            {
                'title': 'Buy groceries',
                'description': 'Get milk, bread, eggs, and vegetables for the week',
                'category': 'personal',
                'priority': 'medium',
                'status': 'pending',
                'due_date': timezone.now() + timedelta(days=1)
            },
            {
                'title': 'Study Python Django',
                'description': 'Complete the Django tutorial and build a sample project',
                'category': 'study',
                'priority': 'high',
                'status': 'in_progress',
                'due_date': timezone.now() + timedelta(days=7)
            },
            {
                'title': 'Exercise for 30 minutes',
                'description': 'Go for a run or do a workout session',
                'category': 'health',
                'priority': 'medium',
                'status': 'completed',
                'completed_at': timezone.now() - timedelta(hours=2)
            },
            {
                'title': 'Call mom',
                'description': 'Check in with family and catch up',
                'category': 'personal',
                'priority': 'low',
                'status': 'pending',
                'due_date': timezone.now() + timedelta(days=3)
            },
            {
                'title': 'Review budget',
                'description': 'Go through monthly expenses and plan next month',
                'category': 'finance',
                'priority': 'medium',
                'status': 'pending',
                'due_date': timezone.now() + timedelta(days=5)
            }
        ]
        
        for task_data in tasks_data:
            Task.objects.get_or_create(
                user=user,
                title=task_data['title'],
                defaults=task_data
            )
        
        self.stdout.write('Created sample tasks')
    
    def create_sample_journals(self, user):
        """Create sample journal entries"""
        moods = ['happy', 'neutral', 'excited', 'grateful', 'motivated', 'tired']
        
        for i in range(7):  # Last 7 days
            date = timezone.now().date() - timedelta(days=i)
            
            JournalEntry.objects.get_or_create(
                user=user,
                date=date,
                defaults={
                    'title': f'Day {7-i} Reflection',
                    'content': f'Today was a productive day. I worked on various tasks and made good progress. The weather was nice and I felt {random.choice(moods)}.',
                    'mood': random.choice(moods),
                    'weather': random.choice(['sunny', 'cloudy', 'rainy']),
                    'energy_level': random.randint(6, 10),
                    'productivity_score': random.randint(7, 10),
                    'tags': 'reflection, productivity, daily'
                }
            )
        
        self.stdout.write('Created sample journal entries')
    
    def create_sample_habits(self, user):
        """Create sample habits"""
        habits_data = [
            {
                'name': 'Drink 8 glasses of water',
                'description': 'Stay hydrated throughout the day',
                'category': 'health',
                'frequency': 'daily',
                'target_count': 8,
                'unit': 'glasses',
                'color': '#007bff'
            },
            {
                'name': 'Read for 30 minutes',
                'description': 'Read books or articles to expand knowledge',
                'category': 'learning',
                'frequency': 'daily',
                'target_count': 30,
                'unit': 'minutes',
                'color': '#28a745'
            },
            {
                'name': 'Exercise',
                'description': 'Physical activity for health and fitness',
                'category': 'fitness',
                'frequency': 'daily',
                'target_count': 1,
                'unit': 'session',
                'color': '#dc3545'
            },
            {
                'name': 'Meditate',
                'description': 'Practice mindfulness and meditation',
                'category': 'mindfulness',
                'frequency': 'daily',
                'target_count': 10,
                'unit': 'minutes',
                'color': '#6f42c1'
            }
        ]
        
        for habit_data in habits_data:
            habit, created = Habit.objects.get_or_create(
                user=user,
                name=habit_data['name'],
                defaults=habit_data
            )
            
            if created:
                # Create some completion records for the last few days
                for i in range(5):
                    completion_date = timezone.now().date() - timedelta(days=i)
                    completed = random.choice([True, True, True, False])  # 75% completion rate
                    
                    HabitCompletion.objects.get_or_create(
                        habit=habit,
                        date=completion_date,
                        defaults={
                            'completed': completed,
                            'quantity': habit.target_count if completed else 0,
                            'notes': f'Completed on {completion_date}' if completed else ''
                        }
                    )
        
        self.stdout.write('Created sample habits')




