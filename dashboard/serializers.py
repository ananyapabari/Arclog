from rest_framework import serializers

from habits.models import Habit
from journal.models import JournalEntry
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'status',
            'priority',
            'category',
            'due_date',
            'is_recurring',
            'recurrence_type',
            'recurrence_interval',
            'created_at',
        ]


class HabitSerializer(serializers.ModelSerializer):
    completion_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id',
            'name',
            'frequency',
            'recurrence_interval',
            'target_count',
            'unit',
            'is_active',
            'completion_rate',
            'created_at',
        ]


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = [
            'id',
            'date',
            'title',
            'mood',
            'energy_level',
            'productivity_score',
            'created_at',
        ]
