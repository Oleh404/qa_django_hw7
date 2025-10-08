from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import ExtractIsoWeekDay

import django_filters.rest_framework as dj_filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, viewsets, decorators, response, status, generics
from rest_framework import filters as drf_filters
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Task, SubTask, Category, Status
from .serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskDetailSerializer,
    SubTaskCreateSerializer,
    CategorySerializer,
    TaskSerializer,
    SubTaskSerializer,
)
from .permissions import IsOwnerOrReadOnly
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer

from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class TaskFilter(dj_filters.FilterSet):
    deadline_after = dj_filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = dj_filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = Task
        fields = ["status"]


class SubTaskFilter(dj_filters.FilterSet):
    deadline_after = dj_filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="gte")
    deadline_before = dj_filters.IsoDateTimeFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = SubTask
        fields = ["status"]


class TaskListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "deadline"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Task.objects.select_related("owner")
            .prefetch_related("categories")
            .all()
            .order_by("-created_at")
        )

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
        return TaskCreateSerializer if self.request.method.upper() == "POST" else TaskListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Task.objects.select_related("owner").prefetch_related("subtasks", "categories")

    def get_serializer_class(self):
        return TaskDetailSerializer if self.request.method.upper() == "GET" else TaskCreateSerializer


class TaskStatsView(ListAPIView):

    def get(self, request, *args, **kwargs):
        total = Task.objects.count()
        rows = Task.objects.values("status").annotate(count=Count("id"))
        by_status = {r["status"]: r["count"] for r in rows}
        overdue = Task.objects.filter(
            Q(deadline__lt=timezone.now()) & ~Q(status=Status.DONE)
        ).count()
        return Response({"total": total, "by_status": by_status, "overdue": overdue})


class SubTaskListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = SubTaskCreateSerializer

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = SubTaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "deadline"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = SubTask.objects.select_related("task", "owner").all().order_by("-created_at")
        task_title = self.request.query_params.get("task_title")
        if task_title:
            qs = qs.filter(task__title__icontains=task_title.strip())
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = SubTask.objects.select_related("task", "owner").all()
    serializer_class = SubTaskCreateSerializer


class MyTasksView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).order_by("-created_at")


class MySubTasksView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubTaskSerializer

    def get_queryset(self):
        return SubTask.objects.filter(owner=self.request.user).order_by("-created_at")


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        count = Task.objects.filter(categories=category).count()
        return Response({"category_id": category.pk, "tasks": count})


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-id")
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [drf_filters.OrderingFilter]
    ordering_fields = ["id", "deadline"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

class SubTaskViewSet(viewsets.ModelViewSet):
    queryset = SubTask.objects.select_related("task").all().order_by("-id")
    serializer_class = SubTaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [drf_filters.OrderingFilter]
    ordering_fields = ["id", "deadline"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(detail=False, methods=["get"], url_path="my", permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            data = self.get_serializer(page, many=True).data
            return self.get_paginated_response(data)
        return response.Response(self.get_serializer(qs, many=True).data)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and isinstance(response.data, dict):
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            if refresh:
                response.set_cookie(
                    key="refresh",
                    value=refresh,
                    httponly=True,
                    samesite="Lax",
                    secure=False,
                    max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
                )
            if access:
                response.set_cookie(
                    key="access",
                    value=access,
                    httponly=True,
                    samesite="Lax",
                    secure=False,
                    max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
                )
        return response


class LogoutView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "Missing refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Already invalidated"}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user