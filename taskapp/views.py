from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from modely.models import Project, Task
from django.contrib.auth.decorators import login_required
import datetime

class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )


    class Meta:
        model = Task
        fields = ["name", "description", "assigned_user", "deadline", "priority", "status"]

    

@login_required
def create_task_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            if not task.assigned_user:
                task.assigned_user = request.user
            task.save()
            return redirect("project_detail", project_id=project.id)
    else:
        form = TaskForm()

    return render(request, "myproject/create_task.html", {"form": form, "project":project})

@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "myproject/task_detail.html", {"task": task})

@login_required
def claim_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.assigned_user = request.user
    task.save()
    return redirect("task_detail", task_id=task.id)

    
    




# Create your views here.
