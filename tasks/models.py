from django.db import models

# tasks/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(BaseModel):
    """Represents a task in the system."""

    class TaskStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
      

    class TaskType(models.TextChoices):
        BUG = 'BUG', 'Bug Fix'
        FEATURE = 'FEATURE', 'New Feature'
        IMPROVEMENT = 'IMPROVEMENT', 'Improvement'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING
    )
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.OTHER
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ManyToManyField(
        User,
        related_name='tasks',
        blank=True  # A task might be created before assignment
    )


    # automatically set the completed_at field when status changes to COMPLETED
    def save(self, *args, **kwargs):
        if self.status == self.TaskStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.TaskStatus.COMPLETED:
            self.completed_at = None # reset if status changes from COMPLETED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at'] 
