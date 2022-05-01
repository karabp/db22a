from django.shortcuts import render
from research_funding import database
import datetime

def projects_per_researcher(request):
    researcher_project_list = database.mariadb_select_all(
        'SELECT * FROM projects_per_researcher',[])
    for researcher_projects in researcher_project_list:
        researcher_projects['project_titles'] = researcher_projects['project_titles'].split(',')
        researcher_projects['age'] = datetime.date.today().year - researcher_projects['birth_date'].year
        
    return render(request, 'research_funding/projects_per_researcher.html', {'researcher_project_list': researcher_project_list})
