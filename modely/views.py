from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Project, Task
from django import forms

def login_view(request):            #login
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, 'myproject/login.html', {"form": form})

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        UserModel = get_user_model()
        if username and UserModel.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This user name is already in use")
        return username


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "myproject/register.html", {"form": form})

def logout_view(request):           #logout
    logout(request)
    return redirect ("login")


@login_required
def dashboard_view(request):
    return render(request, "myproject/dashboard.html")

@login_required
def dashboard_view(request):
    user = request.user
    projects = user.projects.filter(parent_project__isnull=True)
    return render(request, "myproject/dashboard.html", {"projects": projects, "user": user})

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    subprojects = Project.objects.filter(parent_project=project)
    tasks = project.tasks.all()
    return render(request, "myproject/project_detail.html", {"project": project, "subprojects": subprojects, "tasks": tasks})

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "parent_project"]

@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            request.user.projects.add(project)
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "myproject/create_project.html", {"form": form})

    
