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
    path('manager/dual-role', views.managers_dual_role, name='managers_dual_role'),
    path('project/search/results-json', views.project_search_results_json, name='project_search_results_json'),
    path('project/search/javascript', views.project_search_javascript, name='project_search_javascript'),
    path('project/search', views.project_search_form, name='project_search_form'),
    path('', views.home, name='home'),
    path('project/details/<int:id>', views.project_details, name='project_details'),
    path('organization/biannual-report', views.organizations_by_biannual_project_count, name='organization_biannual_report'),
]
