# tasks/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView 

from .models import Task
from .serializers import TaskSerializer, TaskAssignSerializer, UserSerializer

class IsStaffUser(permissions.BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a staff member
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
# 1. API to create and view tasks
class TaskListCreateView(APIView):

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Staff required for POST (create), Authenticated for GET (list).
        DRF runs these checks *before* calling the get() or post() methods.
        """
        if self.request.method == 'POST':
            # For creating tasks, user must be logged in AND be a staff member
            return [permissions.IsAuthenticated(), IsStaffUser()]
        # For listing tasks (GET), user only needs to be logged in
        return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to list all tasks.
        Equivalent to the 'List' part of ListCreateAPIView.
        """

        tasks = Task.objects.prefetch_related('assigned_to').all()

        serializer = TaskSerializer(tasks, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new task.
        Equivalent to the 'Create' part of ListCreateAPIView.
        """

        serializer = TaskSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                created_task = serializer.save()
                print(f"New task created with ID: {created_task.id}") # For debugging

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                
                return Response({"detail": "An error occurred while saving the task."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. API to assign a task to a user
class AssignTaskView(views.APIView):
    """
    Assign a task to one or more users. (POST)
    Requires staff privileges.
    URL: /api/tasks/<task_id>/assign/
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    serializer_class = TaskAssignSerializer # Used for input validation

    def post(self, request, task_id):
        """Assign users to the specified task."""
        task = get_object_or_404(Task, pk=task_id)
        serializer = TaskAssignSerializer(data=request.data)

        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            users_to_assign = User.objects.filter(id__in=user_ids)

            # Use add() to append users without removing existing ones
            # Use set() if you want to replace all existing assignments with the new list
            task.assigned_to.add(*users_to_assign)
            # Or: task.assigned_to.set(users_to_assign) # To replace existing

            task.save() # Save the task to update relations

            # Return the updated task details
            output_serializer = TaskSerializer(task)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. API to get tasks for a specific user
class UserTasksListView(generics.ListAPIView):
    """
    Fetch all tasks assigned to a particular user. (GET)
    URL: /api/users/<user_id>/tasks/
    Staff users can view tasks for any user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the tasks
        assigned to the user determined by the user_id portion of the URL.
        """
        target_user_id = self.kwargs['user_id']
        requesting_user = self.request.user

        # Check permissions: Staff can see anyone's tasks, others only their own.
        if not requesting_user.is_staff and requesting_user.id != target_user_id:
            raise PermissionDenied("You do not have permission to view these tasks.")

        target_user = get_object_or_404(User, pk=target_user_id)

        return target_user.tasks.all()
