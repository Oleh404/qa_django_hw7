from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import (
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TaskStatsView,
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView,
    CategoryViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("api/tasks/", TaskListCreateView.as_view(), name="task-list"),
    path("api/tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"),
    path("api/tasks/stats/", TaskStatsView.as_view(), name="task-stats"),

    path("api/subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("api/subtasks/<int:pk>/", SubTaskDetailUpdateDeleteView.as_view(),
         name="subtask-detail-update-delete"),

    path("api/", include(router.urls)),
]
