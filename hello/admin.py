from django.contrib import admin
from .models import Category, Task, SubTask


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ("title", "status", "deadline", "description")
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "deadline", "created_at")
    list_filter = ("status", "categories", "created_at")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at",)
    inlines = [SubTaskInline]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "task")
    search_fields = ("title", "description", "task__title")
    autocomplete_fields = ("task",)
    readonly_fields = ("created_at",)
