from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Status(models.TextChoices):
    NEW = "new", "New"
    IN_PROGRESS = "in_progress", "In progress"
    PENDING = "pending", "Pending"
    BLOCKED = "blocked", "Blocked"
    DONE = "done", "Done"


class CategoryQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db).alive()


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                condition=Q(is_deleted=False),
                name="uniq_category_name_ci_not_deleted",
            )
        ]

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return self.name

    pass


class Task(models.Model):
    title = models.CharField("Название", max_length=200, unique=True)
    description = models.TextField("Описание", blank=True)
    categories = models.ManyToManyField(
        "Category",
        blank=True,
        related_name="tasks",
        verbose_name="Категории",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="tasks",
        null=True, blank=True,
    )

    class Meta:
        db_table = "task_manager_task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-id"]

    def __str__(self):
        return self.title


class SubTask(models.Model):
    title = models.CharField("Название подзадачи", max_length=200, unique=True)
    description = models.TextField("Описание подзадачи", blank=True)
    task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="subtasks", verbose_name="Основная задача"
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="subtasks",
        null=True, blank=True,
    )

    class Meta:
        db_table = "task_manager_subtask"
        verbose_name = "Подзадача"
        verbose_name_plural = "Подзадачи"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.task_id}: {self.title}"
