from django.utils import timezone
from rest_framework import serializers
from .models import Task, SubTask, Category


class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ["id", "title", "description", "status", "deadline", "created_at", "task"]
        read_only_fields = ["id", "created_at"]


class SubTaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    class Meta:
        model = SubTask
        fields = ["id", "title", "description", "status", "deadline", "created_at"]


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def _ensure_unique(self, name: str, instance=None):
        qs = Category.objects.filter(name__iexact=name)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"name": "Category with this name already exists."})

    def create(self, validated_data):
        self._ensure_unique(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get("name", instance.name)
        self._ensure_unique(name, instance=instance)
        return super().update(instance, validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "created_at", "categories"]
        read_only_fields = ["id", "created_at"]

    def validate_deadline(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    categories = serializers.StringRelatedField(many=True)
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "created_at", "categories", "subtasks"]


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "created_at", "categories"]
        read_only_fields = ["id", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "is_deleted", "deleted_at")
        read_only_fields = ("is_deleted", "deleted_at")

    def validate_name(self, value):
        value = value.strip()
        qs = Category.all_objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.filter(is_deleted=False).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value