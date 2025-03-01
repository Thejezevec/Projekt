from django.test import TestCase

import pytest
from django.contrib.auth import get_user_model
from modely.models import Project, ProjectMembership

User = get_user_model()

@pytest.mark.django_db
def test_create_project():
    project = Project.objects.create(name="Test project", description="Test description")
    assert project.name == "Test project"
    assert project.description == "Test description"

@pytest.mark.django_db
def test_project_membership():
    user = User.objects.create_user(username="testuser", password="testpassword")
    project = Project.objects.create(name="Project for test")
    membership = ProjectMembership.objects.create(user=user, project=project, role="worker")

    assert membership.user == user
    assert membership.project == project
    assert membership.role == "worker"