# tasks/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read-only)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email'] 

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    # To show user details instead of just IDs when reading
    assigned_to = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'status', 'task_type',
            'created_at', 'updated_at', 'completed_at', 'assigned_to'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'assigned_to'] 

class TaskAssignSerializer(serializers.Serializer):
    """Serializer specifically for assigning tasks"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of user IDs to assign the task to."
    )

    def validate_user_ids(self, value):
        """Check if all user IDs exist."""
        existing_user_ids = User.objects.filter(id__in=value).values_list('id', flat=True)
        non_existent_ids = set(value) - set(existing_user_ids)
        if non_existent_ids:
            raise serializers.ValidationError(f"Users with IDs {list(non_existent_ids)} do not exist.")
        return value