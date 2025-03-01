from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class User(AbstractUser):
    objects = UserManager()
    
    @property
    def projects(self):
        from modely.models import Project  # import uvnitř metody, aby nedošlo k cyklickým importům
        return Project.objects.filter(projectmembership__user=self)

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
    members = models.ManyToManyField(User, through="ProjectMembership", related_name="member_of_projects")

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


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author} on {self.task}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    tags = models.ManyToManyField(Task, related_name="tags", blank=True)

    def __str__(self):
        return self.name

class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('worker', 'Worker'),
        ('leader', 'Project Leader'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'project')
        constraints = [
            models.UniqueConstraint(
                fields=['project'],
                condition=models.Q(role='leader'),
                name='unique_project_leader'
            )
        ]

    def __str__(self):
        return f"{self.user} in {self.project} as {self.get_role_display()}"
    
    def is_admin_or_leader(self):
        return self.role in ['leader', 'admin']
    
@staticmethod
def get_user_role(user, project):
    membership = ProjectMembership.object.filter(user=user, project=project).first()
    return membership.role if membership else None

def is_admin_or_leader(self):
    return self.role in ['leader', 'admin']

from django.core.exceptions import ValidationError

def add_project_member(user, project, role):
    
    if role == 'leader':
        if ProjectMembership.objects.filter(project=project, role='leader').exists():
            raise ValidationError("Tento projekt již má leadera!")

    membership, created = ProjectMembership.objects.get_or_create(user=user, project=project)
    membership.role = role
    membership.save()
