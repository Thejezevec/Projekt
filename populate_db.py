import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from modely.models import User, Project, Task, Comment, Tag, ProjectMembership

def create_test_data():
    print(" Generování testovacích dat...")

    users = [
        User.objects.create_user(username=f"user{i}", password="test1234")
        for i in range(1, 6)
    ]
    admin = User.objects.create_superuser(username="admin", password="admin1234")

    print(f" Vytvořeno {len(users)} uživatelů + 1 admin.")

    projects = [
        Project.objects.create(name=f"Project {i}", description=f"Description for Project {i}")
        for i in range(1, 4)
    ]

    print(f" Vytvořeno {len(projects)} projektů.")

    tag_names = ["Bug", "Feature", "High Priority", "Low Priority", "Refactoring"]
    tags = [Tag.objects.create(name=tag_name) for tag_name in tag_names]

    print(f" Vytvořeno {len(tags)} tagů.")

    priorities = [1, 2, 3]
    statuses = ["new", "in_progress", "completed"]

    tasks = []
    for i in range(1, 10):
        project = random.choice(projects)
        assigned_user = random.choice(users) if random.random() > 0.3 else None  
        task = Task.objects.create(
            name=f"Task {i}",
            description=f"Description for Task {i}",
            assigned_user=assigned_user,
            project=project,
            created_at=timezone.now(),
            deadline=timezone.now() + timedelta(days=random.randint(1, 30)),
            priority=random.choice(priorities),
            status=random.choice(statuses),
        )
        task.tags.add(*random.sample(tags, k=random.randint(1, 3)))  
        tasks.append(task)

    print(f" Vytvořeno {len(tasks)} úkolů.")

    comments = []
    for task in tasks:
        for _ in range(random.randint(0, 3)):  
            comment = Comment.objects.create(
                task=task,
                author=random.choice(users),
                text=f"Comment for {task.name}",
                created_at=timezone.now() - timedelta(days=random.randint(0, 10)),
            )
            comments.append(comment)

    print(f" Vytvořeno {len(comments)} komentářů.")

    for project in projects:
        members = random.sample(users, k=random.randint(2, 5))  
        for user in members:
            role = random.choice(["worker", "admin", "leader"])
            ProjectMembership.objects.create(user=user, project=project, role=role)

    print(" Testovací data úspěšně vygenerována!")

if __name__ == "__main__":
    create_test_data()
