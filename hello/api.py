# hello/api.py
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import ExtractIsoWeekDay
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView,
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Task, SubTask, Category, Status
from .serializers import (
    TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer,
    SubTaskCreateSerializer, CategoryCreateSerializer
)

class SubTaskPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 5

class TaskCreateView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

class TaskListView(ListAPIView):
    serializer_class = TaskListSerializer

    def get_queryset(self):
        qs = Task.objects.all().order_by("-created_at")

        weekday = self.request.query_params.get("weekday")
        if not weekday:
            return qs

        day_map = {
            "mon": 1, "monday": 1,
            "tue": 2, "tuesday": 2,
            "wed": 3, "wednesday": 3,
            "thu": 4, "thursday": 4,
            "fri": 5, "friday": 5,
            "sat": 6, "saturday": 6,
            "sun": 7, "sunday": 7,
            "понедельник": 1,
            "вторник": 2,
            "среда": 3,
            "четверг": 4,
            "пятница": 5,
            "суббота": 6,
            "воскресенье": 7,
            "понеділок": 1,
            "вівторок": 2,
            "середа": 3,
            "четвер": 4,
            "п'ятниця": 5,
            "субота": 6,
            "неділя": 7,
        }
        key = weekday.strip().lower()
        num = day_map.get(key) or day_map.get(key[:3])

        if num:
            qs = (
                qs.annotate(dow=ExtractIsoWeekDay("deadline"))
                  .filter(dow=num)
            )
        return qs


class TaskDetailView(RetrieveAPIView):
    queryset = Task.objects.all().prefetch_related("subtasks", "categories")
    serializer_class = TaskDetailSerializer

class TaskStatsView(APIView):
    def get(self, request):
        total = Task.objects.count()
        rows = Task.objects.values("status").annotate(count=Count("id"))
        by_status = {r["status"]: r["count"] for r in rows}
        overdue = Task.objects.filter(
            Q(deadline__lt=timezone.now()) & ~Q(status=Status.DONE)
        ).count()
        return Response({"total": total, "by_status": by_status, "overdue": overdue})


class SubTaskListCreateView(ListCreateAPIView):
    serializer_class = SubTaskCreateSerializer
    pagination_class = SubTaskPagination

    def get_queryset(self):
        qs = SubTask.objects.select_related("task").all().order_by("-created_at")

        task_title = self.request.query_params.get("task_title")
        status = self.request.query_params.get("status")

        if task_title:
            qs = qs.filter(task__title__icontains=task_title.strip())

        if status:
            st = status.strip().lower()
            allowed = {s for s, _ in Status.choices}
            if st in allowed:
                qs = qs.filter(status=st)

        return qs


class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.select_related("task").all()
    serializer_class = SubTaskCreateSerializer


class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategoryCreateSerializer

class CategoryDetailUpdateView(RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
