from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from modely.models import Project, Task, Tag, Comment, ProjectMembership
from django.contrib.auth.decorators import login_required
import datetime
from .forms import TaskEditForm

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

    
class TagForm(forms.Form):
    new_tag = forms.CharField(max_length=50, required=False, label="New tag")
    existing_tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(), required=False, label="Choose tag"

    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Write your comment..."})
        }

@login_required
def add_tag_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            new_tag = form.cleaned_data.get("new_tag")
            existing_tag = form.cleaned_data.get("existing_tag")
            if new_tag:
                tag, created = Tag.objects.get_or_create(name=new_tag)
                task.tags.add(tag)
            elif existing_tag:
                task.tags.add(existing_tag)
    return redirect("task_detail", task_id=task.id)


@login_required
def add_comment_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
    return redirect("task_detail", task_id=task.id)

@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comment_form = CommentForm()
    tag_form = TagForm()
    project = task.project
    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
    if not membership:
        return render(request, "myproject/no_access.html")
    can_edit_task = membership.is_admin_or_leader() or task.assigned_user == request.user
    return render(request, "myproject/task_detail.html", {
        "task": task,
        "comment_form": comment_form,
        "tag_form": tag_form,
        "can_edit_task": can_edit_task,
        "can_change_assignment": membership.is_admin_or_leader()
    })

@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    membership = task.project.projectmembership_set.filter(user=request.user).first()
    if not membership or (task.assigned_user != request.user and not membership.is_admin_or_leader()):
        return redirect("task_detail", task_id=task.id)

    if request.method == "POST":
        form = TaskEditForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_detail", task_id=task.id)
    else:
        form = TaskEditForm(instance=task)

    return render(request, "myproject/edit_task.html", {"form": form, "task": task})

# Create your views here.
