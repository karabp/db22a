from django.urls import path

from . import views

urlpatterns = [
    path('', views.projects_per_researcher, name='projects_per_researcher'),
]
