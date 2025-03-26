
from django.urls import path
from .views import (
    TaskListCreateView,
    AssignTaskView,
    UserTasksListView   
)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:task_id>/assign/', AssignTaskView.as_view(), name='task-assign'),
    path('users/<int:user_id>/tasks/', UserTasksListView.as_view(), name='user-task-list')
]