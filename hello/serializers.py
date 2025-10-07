from rest_framework import serializers
from .models import Task, Category

class TaskSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "deadline", "created_at", "categories"]
        read_only_fields = ["id", "created_at"]
