from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Project, Task, Comment, Tag, ProjectMembership
from django.core.exceptions import ValidationError

def login_view(request):            
    #user login. If the login is successful, the user is redirected to the dashboard.
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
    """
    Custom user registration form.
    Ensures that the username is unique (case-insensitive).
    """
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
    #Handles user registration. If successful, logs in the new user and redirects to the dashboard.
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "myproject/register.html", {"form": form})

def logout_view(request):           #Logs out the user and redirects to the login page.
    logout(request)
    return redirect ("login")



@login_required
def dashboard_view(request):
    """
    Displays the dashboard for the logged-in user, listing projects where they are a member.
    Only top-level projects (without a parent project) are shown.
    """
    user = request.user
    projects = user.projects.filter(parent_project__isnull=True)
    return render(request, "myproject/dashboard.html", {"projects": projects, "user": user})

def project_detail_view(request, project_id):
    """
    Displays the details of a project, including its tasks and members.
    Supports sorting tasks by various attributes.
    """
    project = get_object_or_404(Project, id=project_id)
    members = ProjectMembership.objects.filter(project=project)
    subprojects = Project.objects.filter(parent_project=project)
    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
    
    sort_option = request.GET.get('sort', 'created_at') 

    sort_mapping = {
        'name': 'name',
        'priority': '-priority', 
        'deadline': 'deadline',
        'status': 'status',
        'assigned_user': 'assigned_user__username',
        'created_at': '-created_at',  
    }

    tasks = Task.objects.filter(project=project).order_by(sort_mapping.get(sort_option, '-created_at'))

    return render(request, "myproject/project_detail.html", {
        "project": project,
        "tasks": tasks,
        "members": members,
        "subprojects": subprojects,
        "membership": membership,
        "sort_option": sort_option, 
    })

class ProjectForm(forms.ModelForm):
    #Form for creating a new project.
    class Meta:
        model = Project
        fields = ["name", "description", "parent_project"]

@login_required
def create_project_view(request):
    """
    Handles the creation of a new project.
    The requesting user is automatically assigned as the project leader.
    """
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            ProjectMembership.objects.create(user=request.user, project=project, role='leader')
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "myproject/create_project.html", {"form": form})

def add_project_member(user, project, role):
    """
    Adds a user to a project with the specified role.
    Ensures that only one leader exists per project.
    """
    if role == 'leader':
        if ProjectMembership.objects.filter(project=project, role='leader').exists():
            raise ValidationError("Leader already exists!")
    
    ProjectMembership.objects.create(user=user, project=project, role=role)
    membership, created = ProjectMembership.objects.get_or_create(user=user, project=project)
    membership.role = role
    membership.save()


class InviteUserForm(forms.Form):
    #Form for inviting a user to a project.
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    role = forms.ChoiceField(choices=ProjectMembership.ROLE_CHOICES, label="Role")

@login_required
def invite_user_view(request, project_id):
    """
    Allows project admins and leaders to invite a user to a project.
    Ensures only authorized users can add members.
    """
    project = get_object_or_404(Project, id=project_id)

    # Check if user has permission (must be admin or leader)
    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
    if not membership or not membership.is_admin_or_leader():
        return HttpResponseForbidden("You do not have permission to add users.")

    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            role = form.cleaned_data["role"]

            # Check if user is already in the project
            if ProjectMembership.objects.filter(user=user, project=project).exists():
                messages.error(request, "User is already in this project.")
            else:
                try:
                    add_project_member(user, project, role)
                    messages.success(request, f"User {user.username} was added to project as {role}.")
                except ValidationError as e:
                    messages.error(request, str(e))

            return redirect("project_detail", project_id=project.id)

    else:
        form = InviteUserForm()

    return render(request, "myproject/invite_user.html", {"form": form, "project": project})


def change_project_leader(project, new_leader):
    """
    Changes the project leader by demoting the current leader 
    (if any) and assigning a new one.
    """
    old_leader = ProjectMembership.objects.filter(project=project, role='leader').first()
    
    if old_leader:
        old_leader.role = 'worker'
        old_leader.save()

    add_project_member(new_leader, project, 'leader')
