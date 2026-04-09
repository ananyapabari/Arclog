from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.serializers import HabitSerializer, JournalEntrySerializer, TaskSerializer
from dashboard.services import calculate_productivity_score, generate_rule_based_insights
from habits.models import Habit
from journal.models import JournalEntry
from tasks.models import Task


class TaskListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Task.objects.filter(user=request.user).order_by('-created_at')[:100]
        return Response(TaskSerializer(queryset, many=True).data)


class HabitListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Habit.objects.filter(user=request.user).order_by('-created_at')[:100]
        return Response(HabitSerializer(queryset, many=True).data)


class JournalListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = JournalEntry.objects.filter(user=request.user).order_by('-date')[:100]
        return Response(JournalEntrySerializer(queryset, many=True).data)


class ProductivitySummaryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        score = calculate_productivity_score(user=request.user, on_date=today)
        insights = generate_rule_based_insights(user=request.user)

        return Response(
            {
                'date': str(today),
                'score': score,
                'insights': insights,
            }
        )
