from django.urls import path
from .views import hello
from .api import (
    TaskCreateView, TaskListView, TaskDetailView, TaskStatsView
)

urlpatterns = [
    path("", hello, name="hello_default"),
    path("<str:name>/", hello, name="hello_named"),

    path("api/tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("api/tasks/", TaskListView.as_view(), name="task-list"),
    path("api/tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("api/tasks/stats/", TaskStatsView.as_view(), name="task-stats"),
]
