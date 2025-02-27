from django import forms
from modely.models import Task

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "status", "priority", "deadline", "assigned_user"]
