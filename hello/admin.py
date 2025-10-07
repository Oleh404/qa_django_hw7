from django.contrib import admin
from .models import Task, SubTask, Category, Status


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ("title", "description", "status", "deadline")
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "short_title", "status", "deadline", "created_at")
    list_filter = ("status", "deadline", "created_at", "categories")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    filter_horizontal = ("categories",)

    inlines = [SubTaskInline]

    @admin.display(description="Title")
    def short_title(self, obj: Task) -> str:
        t = obj.title or ""
        return t if len(t) <= 10 else f"{t[:10]}…"


@admin.action(description="Mark selected subtasks as Done")
def make_subtasks_done(modeladmin, request, queryset):
    updated = queryset.update(status=Status.DONE)
    modeladmin.message_user(request, f"Updated {updated} subtasks to Done.")


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "deadline", "task")
    list_filter = ("status", "deadline", "task")
    search_fields = ("title", "description", "task__title")
    actions = [make_subtasks_done]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
