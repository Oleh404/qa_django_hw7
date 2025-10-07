from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import ExtractIsoWeekDay
import django_filters.rest_framework as filters

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import Task, SubTask, Category, Status
from .serializers import (
    TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer,
    SubTaskCreateSerializer, CategorySerializer
)

class TaskFilter(filters.FilterSet):
    deadline_after = filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ["status"]

class SubTaskFilter(filters.FilterSet):
    deadline_after = filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = SubTask
        fields = ["status"]

class TaskListCreateView(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Task.objects.all().order_by("-created_at")

        weekday = self.request.query_params.get("weekday")
        if weekday:
            day_map = {
                "mon": 1, "monday": 1, "понедельник": 1, "понеділок": 1,
                "tue": 2, "tuesday": 2, "вторник": 2, "вівторок": 2,
                "wed": 3, "wednesday": 3, "среда": 3, "середа": 3,
                "thu": 4, "thursday": 4, "четверг": 4, "четвер": 4,
                "fri": 5, "friday": 5, "пятница": 5, "п'ятниця": 5,
                "sat": 6, "saturday": 6, "суббота": 6, "субота": 6,
                "sun": 7, "sunday": 7, "воскресенье": 7, "неділя": 7,
            }
            key = weekday.strip().lower()
            num = day_map.get(key) or day_map.get(key[:3])
            if num:
                qs = qs.annotate(dow=ExtractIsoWeekDay("deadline")).filter(dow=num)
        return qs

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return TaskCreateSerializer
        return TaskListSerializer


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all().prefetch_related("subtasks", "categories")

    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return TaskDetailSerializer
        return TaskCreateSerializer

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

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubTaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = SubTask.objects.select_related("task").all().order_by("-created_at")

        task_title = self.request.query_params.get("task_title")
        if task_title:
            qs = qs.filter(task__title__icontains=task_title.strip())
        return qs


class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.select_related("task").all()
    serializer_class = SubTaskCreateSerializer



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        count = Task.objects.filter(categories=category).count()
        return Response({"category_id": category.pk, "tasks": count})