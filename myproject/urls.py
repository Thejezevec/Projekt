"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from modely import views as modely_views
from taskapp import views as taskapp_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path("", modely_views.login_view, name="login"),
    path("register/", modely_views.register_view, name="register"),
    path("logout/", modely_views.logout_view, name="logout"),
    path("dashboard/", modely_views.dashboard_view, name="dashboard"),
    path("project/<int:project_id>/", modely_views.project_detail_view, name="project_detail"),
    path("project/new/", modely_views.create_project_view, name="create_project"),
    path("project/<int:project_id>/task/new/", taskapp_views.create_task_view, name="create_task"),
    path("task/<int:task_id>/", taskapp_views.task_detail_view, name="task_detail"),
    path("task/<int:task_id>/claim/", taskapp_views.claim_task_view, name="claim_task"),
    path('task/<int:task_id>/add_tag/', taskapp_views.add_tag_to_task, name='add_tag_to_task'),
    path('task/<int:task_id>/add_comment/', taskapp_views.add_comment_to_task, name='add_comment_to_task'),
    path("task/<int:task_id>/edit/", taskapp_views.edit_task_view, name="edit_task"),
    path("project/<int:project_id>/invite/", modely_views.invite_user_view, name="invite_user"),

]