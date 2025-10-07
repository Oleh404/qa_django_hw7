from django.db import models


class Status(models.TextChoices):
    NEW = "new", "New"
    IN_PROGRESS = "in_progress", "In progress"
    PENDING = "pending", "Pending"
    BLOCKED = "blocked", "Blocked"
    DONE = "done", "Done"


class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    title = models.CharField("Название", max_length=200, unique=True)
    description = models.TextField("Описание", blank=True)
    categories = models.ManyToManyField(
        Category,
        verbose_name="Категории",
        related_name="tasks",
        blank=True,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "task_manager_task"
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class SubTask(models.Model):
    title = models.CharField("Название подзадачи", max_length=200, unique=True)
    description = models.TextField("Описание подзадачи", blank=True)
    task = models.ForeignKey(
        Task,
        verbose_name="Основная задача",
        related_name="subtasks",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        db_table = "task_manager_subtask"
        verbose_name = "SubTask"
        verbose_name_plural = "SubTasks"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
