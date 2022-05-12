from django.shortcuts import render
from django.http import JsonResponse

from research_funding import database, helpers

import datetime

def projects_per_researcher(request):
    researcher_project_list = database.mariadb_select_all(
        'SELECT * FROM projects_per_researcher',[])
    for researcher_projects in researcher_project_list:
        researcher_projects['project_titles'] = researcher_projects['project_titles'].split(',')
        researcher_projects['age'] = helpers.age_from_birth_date(researcher_projects['birth_date'])
        
    return render(request, 'research_funding/researcher/projects.html', {'researcher_project_list': researcher_project_list})

def inactive_researchers(request):
    researchers = database.mariadb_select_all(
        '''
        WITH inactive_project AS
            (SELECT project.id FROM
             project LEFT OUTER JOIN deliverable
             ON project.id = deliverable.project_id
             WHERE deliverable.title IS NULL)
        SELECT person.first_name,
               person.last_name,
               COUNT(participates.project_id) AS project_count
        FROM researcher
        INNER JOIN person
        INNER JOIN researcher_participates_in_project AS participates
        INNER JOIN inactive_project
        ON researcher.id = person.id
        AND researcher.id = participates.researcher_id
        AND inactive_project.id = participates.project_id
        GROUP BY researcher.id
        HAVING COUNT(participates.project_id) >= 5
        ORDER BY COUNT(participates.project_id) DESC
        ''', []
    )

    return render(request, 'research_funding/researcher/inactive.html', {'researchers': researchers })

def young_researchers(request):
    researchers = database.mariadb_select_all(
        '''
        WITH young_researcher AS
            (SELECT researcher.id,
                    person.first_name,
                    person.last_name,
                    person.birth_date
             FROM researcher INNER JOIN person
             ON researcher.id = person.id
             WHERE ADDDATE(person.birth_date, 365*40) > CURRENT_DATE())
        SELECT young_researcher.*,
               COUNT(active_project.id) AS project_count
        FROM young_researcher
        INNER JOIN active_project
        INNER JOIN researcher_participates_in_project AS participates
        ON participates.researcher_id = young_researcher.id
        AND participates.project_id = active_project.id
        GROUP BY young_researcher.id
        ORDER BY COUNT(active_project.id) DESC
        ''', []
    )

    for researcher in researchers:
        researcher['age'] = helpers.age_from_birth_date(researcher['birth_date'])
    
    return render(request, 'research_funding/researcher/young.html', {'researchers': researchers })
    
def scientific_field_index(request):
    scientific_fields = database.mariadb_select_all(
        '''
        SELECT scientific_field.title,
               scientific_field.description,
               COUNT(relates.project_id) AS project_count
        FROM scientific_field
        LEFT OUTER JOIN project_relates_to_scientific_field AS relates
        ON relates.scientific_field_title = scientific_field.title
        GROUP BY scientific_field.title
        ORDER BY COUNT(relates.project_id) DESC
        ''', []
    )

    return render(request, 'research_funding/scientific_field/index.html', {'scientific_fields': scientific_fields })

def scientific_field_projects_and_researchers(request, title_slug):
    title_lowercase = title_slug.replace('-', ' ')
    title = title_lowercase[0].upper() + title_lowercase[1:]

    scientific_field = database.mariadb_select_one(
        '''
        SELECT title, description
        FROM scientific_field
        WHERE title = %s
        ''', title
    )
    
    projects_researchers_list = database.mariadb_select_all(
        '''
        SELECT relates.scientific_field_title,
               project.id AS project_id,
               project.title AS project_title,
               project.start_date AS project_start_date,
               ADDDATE(project.start_date, project.duration) AS project_end_date,
               researcher.id AS researcher_id,
               person.first_name AS researcher_first_name,
               person.last_name AS researcher_last_name
        FROM project
        INNER JOIN researcher
        INNER JOIN person
        INNER JOIN researcher_participates_in_project AS participates
        INNER JOIN project_relates_to_scientific_field AS relates
        ON  participates.researcher_id = researcher.id
        AND participates.researcher_id = person.id
        AND participates.project_id = project.id
        AND relates.project_id = project.id
        WHERE relates.scientific_field_title = %s
        AND ADDDATE(project.start_date, project.duration) >= CURRENT_DATE()
        ''', title)

    project_researchers = {};
    for pr in projects_researchers_list:
        project_id = pr['project_id'];
        if project_id not in project_researchers:
            project_researchers[project_id] = {
                'project_id': pr['project_id'],
                'project_title': pr['project_title'],
                'project_start_date': pr['project_start_date'],
                'project_end_date': pr['project_end_date'],
                'researchers': []
            }
        project_researchers[project_id]['researchers'].append(
            {
                'id': pr['researcher_id'],
                'first_name': pr['researcher_first_name'],
                'last_name': pr['researcher_last_name']
            }
        )

    return render(request, 'research_funding/scientific_field/projects_and_researchers.html', {'project_researchers': project_researchers.values(),
               'scientific_field': scientific_field })

def common_fields(request):
    fields = database.mariadb_select_all(
        '''
        SELECT sf1.title AS first_field,
               sf2.title AS second_field,
               COUNT(relates1.project_id) AS project_count
        FROM scientific_field AS sf1
        INNER JOIN scientific_field AS sf2
        INNER JOIN project_relates_to_scientific_field AS relates1
        INNER JOIN project_relates_to_scientific_field AS relates2
        ON relates1.project_id = relates2.project_id
        AND relates1.scientific_field_title = sf1.title
        AND relates2.scientific_field_title = sf2.title
        WHERE sf1.title < sf2.title
        GROUP BY sf1.title, sf2.title
        ORDER BY COUNT(relates1.project_id) DESC
        LIMIT 3
        ''', [])

    return render(request, 'research_funding/scientific_field/common_fields.html', {'fields': fields})

def managers_highest_funding(request):
    managers_organizations = database.mariadb_select_all(
        '''
        SELECT person.first_name,
               person.last_name,
               project.managing_organization_name AS organization,
               SUM(project.funding_amount) as funding_amount
        FROM manager
        INNER JOIN project
        INNER JOIN person
        ON manager.id = project.manager_id
        AND manager.id = person.id
        GROUP BY manager.id, project.managing_organization_name
        ORDER BY SUM(project.funding_amount) DESC
        LIMIT 5
        ''', [])

    return render(request, 'research_funding/manager/highest_funding.html', {'managers_organizations': managers_organizations})

def project_search_json(request, pattern):
    projects = database.mariadb_select_all(
        '''
        SELECT project.id, project.title FROM project
        WHERE project.title LIKE %s

        '''
        , f'%{pattern}%')

    return JsonResponse({'result': projects})

def project_search_form(request):
    managers = database.mariadb_select_all(
        '''
        SELECT manager.id,
               person.first_name,
               person.last_name
        FROM manager
        INNER JOIN person
        ON manager.id = person.id
        '''
        , [])
    
    return render(request, 'research_funding/project/search_form.html', { 'managers': managers })

def home(request):
    return render(request, 'research_funding/home.html', {})
