from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Project, Task, Comment, Tag, ProjectMembership

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
    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
    if not membership:
        return render(request, "myproject/no_access.html")  

    subprojects = Project.objects.filter(parent_project=project)
    tasks = project.tasks.all()
    members = ProjectMembership.objects.filter(project=project)  

    return render(request, "myproject/project_detail.html", {
        "project": project,
        "subprojects": subprojects,
        "tasks": tasks,
        "members": members,
        "membership": membership
    })

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
            ProjectMembership.objects.create(user=request.user, project=project, role='leader')
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "myproject/create_project.html", {"form": form})


class InviteUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    role = forms.ChoiceField(choices=ProjectMembership.ROLE_CHOICES, label="Role")

@login_required
def invite_user_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()

    if not membership or not membership.is_admin_or_leader():
        return render(request, "myproject/no_access.html")

    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            role = form.cleaned_data["role"]

            if not ProjectMembership.objects.filter(user=user, project=project).exists():
                ProjectMembership.objects.create(user=user, project=project, role=role)
                messages.success(request, f"User {user.username} added to project.")
            else:
                messages.error(request, "User is already in this project.")

            return redirect("project_detail", project_id=project.id)
    else:
        form = InviteUserForm()

    return render(request, "myproject/invite_user.html", {"form": form, "project": project})    
