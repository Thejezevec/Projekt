import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from modely.models import Project, Task, Comment, Tag
from datetime import timedelta
from django.utils.timezone import now

User = get_user_model()

@pytest.mark.django_db
def test_dashboard_view(client):
    """Test, že dashboard je dostupný pouze pro přihlášené uživatele"""
    user = User.objects.create_user(username="testuser", password="testpassword")
    
    # Test if the dashboard is accessible only to logged-in users.
    client.login(username="testuser", password="testpassword")

    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert b"Welcome" in response.content  #  Verify the page contains "Welcome"

@pytest.mark.django_db
def test_dashboard_redirect_if_not_logged_in(client):
    #Test if an unauthenticated user is redirected to the login page.
    """Test, že nepřihlášený uživatel je přesměrován na login"""
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302  # 302 = přesměrování
    assert response.url.startswith(reverse("login"))  # Přesměrování na login

@pytest.mark.django_db
def test_project_detail_view(client):
    #Test if the project detail page displays correctly.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")

    client.login(username="testuser", password="testpassword")

    response = client.get(reverse("project_detail", args=[project.id]))
    assert response.status_code == 200
    assert b"Test Project" in response.content

@pytest.mark.django_db
def test_create_project_redirect_if_not_logged_in(client):
    #Test if an unauthenticated user cannot create a project.
    response = client.post(reverse("create_project"), {
        "name": "Unauthorized Project",
        "description": "Should not be created",
    })
    
    assert response.status_code == 302  
    assert not Project.objects.filter(name="Unauthorized Project").exists()


@pytest.mark.django_db
def test_create_project_view(client):
    #Test if an authenticated user can create a new project.
    user = User.objects.create_user(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("create_project"), {
        "name": "New Project",
        "description": "This is a test project",
    })

    assert response.status_code == 302  # Očekáváme přesměrování po úspěšném vytvoření projektu
    assert Project.objects.filter(name="New Project").exists()  # Ověříme, že projekt byl vytvořen

@pytest.mark.django_db
def test_add_empty_comment_to_task(client):
    #Test if an empty comment cannot be added to a task.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")
    task = Task.objects.create(
        name="Test Task", 
        description="Task Desc", 
        project=project, 
        deadline=now() + timedelta(days=7)
    )
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("add_comment_to_task", args=[task.id]), {
        "text": ""  
    })

    assert response.status_code == 200  
    assert not Comment.objects.exists()  


@pytest.mark.django_db
def test_create_task_view(client):
    #Test if an authenticated user can create a new task.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("create_task", args=[project.id]), {
        "name": "New Task",
        "description": "Test Task Description",
        "priority": 2,
        "status": "new",
        "deadline": (now() + timedelta(days=7)).isoformat(),
    })

    assert response.status_code == 302
    assert Task.objects.filter(name="New Task").exists()

@pytest.mark.django_db
def test_add_comment_to_task_view(client):
    #Test if a comment can be added to a task.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")
    task = Task.objects.create(
        name="Test Task", 
        description="Task Desc", 
        project=project, 
        deadline=now() + timedelta(days=7)
    )
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("add_comment_to_task", args=[task.id]), {
        "text": "Test comment"
    })

    assert response.status_code == 302
    assert Comment.objects.filter(text="Test comment").exists()

@pytest.mark.django_db
def test_add_empty_tag_to_task(client):
    #Test if an empty tag cannot be added to a task.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")
    task = Task.objects.create(
        name="Test Task", 
        description="Task Desc", 
        project=project, 
        deadline=now() + timedelta(days=7)
    )
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("add_tag_to_task", args=[task.id]), {
        "new_tag": ""  
    })

    assert response.status_code == 200  
    assert not Tag.objects.exists()  


@pytest.mark.django_db
def test_add_tag_to_task_view(client):
    #Test if a tag can be added to a task.
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Test Project", description="A test project")
    task = Task.objects.create(
        name="Test Task", 
        description="Task Desc", 
        project=project, 
        deadline=now() + timedelta(days=7)
    )
    client.login(username="testuser", password="testpassword")

    response = client.post(reverse("add_tag_to_task", args=[task.id]), {
        "new_tag": "Important"
    })

    assert response.status_code == 302
    assert Tag.objects.filter(name="Important").exists()
