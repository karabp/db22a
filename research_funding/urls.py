from django.urls import path

from . import views

urlpatterns = [
    path('researcher/projects', views.projects_per_researcher, name='projects_per_researcher'),
    path('researcher/young', views.young_researchers, name='young_researchers'),
    path('researcher/inactive', views.inactive_researchers, name='inactive_researchers'),
    path('scientific-field', views.scientific_field_index, name='scientific_field_index'),
    path('scientific-field/<slug:title_slug>/projects-and-researchers', views.scientific_field_projects_and_researchers, name='scientific_field_projects_and_researchers'),
    path('scientific-field/pairs', views.common_fields, name='scientific_field_pairs'),
    path('manager/highest-funding', views.managers_highest_funding, name='managers_highest_funding'),
    path('project/search/<pattern>', views.project_search_json, name='project_search_json'),
    path('project/search', views.project_search_form, name='project_search_form'),
]
