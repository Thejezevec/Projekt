from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class User(AbstractUser):
    objects = UserManager()
    
    projects = models.ManyToManyField("Project", related_name="users")
    
    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_set", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions", blank=True
    )


    def __str__(self):
        return self.username
    
class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    parent_project = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, 

    )

    def __str__(self):
        return self.name
    
class Task(models.Model):
    Priority_list = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    Status_list = [
        ('new', 'New'),
        ('in_progress', 'In_progress'),
        ('Completed', 'completed'),
    ]

    name = models.CharField(max_length= 100)
    description = models.TextField(max_length=600)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    priority = models.IntegerField(choices=Priority_list, default=2)
    status = models.CharField(max_length=25, choices=Status_list, default='new')


def __str__(self):
    return f"{self.name} ({self.get_status_display()})"
