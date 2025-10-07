# hello/urls.py
from django.urls import path
from .views import hello
from .api import (
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TaskStatsView,
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView,
    CategoryListCreateView,
    CategoryDetailUpdateView,
)

urlpatterns = [
    path("hello/<str:name>/", hello, name="hello"),

    path("api/tasks/", TaskListCreateView.as_view(), name="task-list"),
    path("api/tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"),
    path("api/tasks/stats/", TaskStatsView.as_view(), name="task-stats"),

    path("api/subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("api/subtasks/<int:pk>/", SubTaskDetailUpdateDeleteView.as_view(), name="subtask-detail-update-delete"),

    path("api/categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("api/categories/<int:pk>/", CategoryDetailUpdateView.as_view(), name="category-detail-update"),
]
