from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Task, Status
from .serializers import TaskSerializer


class TaskCreateView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskListView(ListAPIView):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer


class TaskDetailView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskStatsView(APIView):
    def get(self, request):
        total = Task.objects.count()
        rows = Task.objects.values("status").annotate(count=Count("id"))
        by_status = {r["status"]: r["count"] for r in rows}
        overdue = Task.objects.filter(
            Q(deadline__lt=timezone.now()) & ~Q(status=Status.DONE)
        ).count()
        return Response({"total": total, "by_status": by_status, "overdue": overdue})
