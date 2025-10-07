# hello/api.py
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView,
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Task, SubTask, Category, Status
from .serializers import (
    TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer,
    SubTaskCreateSerializer, CategoryCreateSerializer
)

class TaskCreateView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

class TaskListView(ListAPIView):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskListSerializer

class TaskDetailView(RetrieveAPIView):
    queryset = Task.objects.all().prefetch_related("subtasks", "categories")
    serializer_class = TaskDetailSerializer

class TaskStatsView(APIView):
    def get(self, request):
        total = Task.objects.count()
        rows = Task.objects.values("status").annotate(count=Count("id"))
        by_status = {r["status"]: r["count"] for r in rows}
        overdue = Task.objects.filter(Q(deadline__lt=timezone.now()) & ~Q(status=Status.DONE)).count()
        return Response({"total": total, "by_status": by_status, "overdue": overdue})


class SubTaskListCreateView(ListCreateAPIView):
    queryset = SubTask.objects.select_related("task").all().order_by("-created_at")
    serializer_class = SubTaskCreateSerializer

class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.select_related("task").all()
    serializer_class = SubTaskCreateSerializer


class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategoryCreateSerializer

class CategoryDetailUpdateView(RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
