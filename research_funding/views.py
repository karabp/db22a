from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.template import loader
from django.urls import reverse

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

def project_search_results_json(request):
    try:
        project_title_term = request.GET['project_title']
        manager_id = request.GET['manager_id']
        program_name = request.GET['program_name']
        department_name = request.GET['department_name']
        start_date_min = request.GET['start_date_min']
        start_date_max = request.GET['start_date_max']
        duration_min = request.GET['duration_min']
        duration_max = request.GET['duration_max']
    except KeyError:
        raise Http404("Searching requires search terms.\nValid search terms are 'program_name' and 'department_name' ('*' for all programs), 'manager_id' ('*' for all managers) and 'project_title' (empty for all projects), 'start_date_min', 'start_date_max', 'duration_min' and 'duration_max'")

    manager_glob = manager_id == '*'
    if manager_glob:
        manager_id = 0
    program_glob = program_name == '*' or department_name == '*'
    if program_glob:
        program_name = ''
        department_name = ''

    start_date_min_glob = False
    start_date_max_glob = False
    duration_min_glob = False
    duration_max_glob = False
    try:
        start_date_min = datetime.date.fromisoformat(start_date_min)
    except ValueError:
        start_date_min_glob = True
        start_date_min = datetime.date.today()
    try:
        start_date_max = datetime.date.fromisoformat(start_date_max)
    except ValueError:
        start_date_max_glob = True
        start_date_max = datetime.date.today()
    try:
        duration_min = int(duration_min)
    except ValueError:
        duration_min_glob = True
        duration_min = 0
    try:
        duration_max = int(duration_max)
    except ValueError:
        duration_max_glob = True
        duration_max = 0
        
    projects = database.mariadb_select_all(
        '''
        SELECT project.id,
               project.title,
               project.start_date,
               project.duration,
               project.funding_program_name AS program_name,
               project.funding_program_department_name AS department_name,
               person.first_name AS manager_first_name,
               person.last_name AS manager_last_name
        FROM project INNER JOIN person
        ON project.manager_id = person.id
        WHERE project.title LIKE %s
        AND (%s OR project.manager_id = %s)
        AND (%s OR project.funding_program_name = %s)
        AND (%s OR project.funding_program_department_name = %s)
        AND (%s OR project.start_date >= %s)
        AND (%s OR project.start_date <= %s)
        AND (%s OR ADDDATE(project.start_date, INTERVAL %s MONTH) 
                   <= ADDDATE(project.start_date, project.duration))
        AND (%s OR ADDDATE(project.start_date, INTERVAL %s MONTH) 
                   >= ADDDATE(project.start_date, project.duration))
        '''
        , (f'%{project_title_term}%', manager_glob, manager_id,
                                      program_glob, program_name,
                                      program_glob, department_name,
                                      start_date_min_glob, start_date_min,
                                      start_date_max_glob, start_date_max,
                                      duration_min_glob, duration_min,
                                      duration_max_glob, duration_max))

    for project in projects:
        project['link'] = reverse('project_details', kwargs={'id': project['id']})
    
    return JsonResponse({'project_title_term': project_title_term, 'results': projects})

def project_search_javascript(request):
    start_date_limits = database.mariadb_select_one(
        '''
        SELECT MIN(project.start_date) AS min,
               MAX(project.start_date) AS max
        FROM project
        '''
        , [])

    response = HttpResponse(content_type='application/javascript')
    t = loader.get_template('research_funding/project/search_form.js')
    response.write(t.render({ 'start_date_limits': start_date_limits }))
    return response

def project_search_form(request):
    start_date_limits = database.mariadb_select_one(
        '''
        SELECT MIN(project.start_date) AS min,
               MAX(project.start_date) AS max
        FROM project
        '''
        , [])

    managers = database.mariadb_select_all(
        '''
        SELECT manager.id,
               person.first_name,
               person.last_name
        FROM manager
        INNER JOIN person
        ON manager.id = person.id
        ORDER BY last_name ASC, first_name ASC
        '''
        , [])

    programs = database.mariadb_select_all(
        '''
        SELECT program.name,
               program.department_name
        FROM program
        ORDER BY department_name ASC, name ASC
        '''
        , [])
    
    return render(request, 'research_funding/project/search_form.html', { 'managers': managers, 'programs': programs, 'start_date_limits': start_date_limits })

def home(request):
    return render(request, 'research_funding/home.html', {})

def project_details(request, id):
    project = database.mariadb_select_one(
        '''
        SELECT project.id,
               project.title,
               project.abstract,
               project.start_date,
               project.funding_amount,
               ADDDATE(project.start_date, project.duration) AS end_date,
               project.review_date,
               project.review_grade,
               organization.name AS organization_name,
               organization.acronym AS organization_acronym,
               organization.type AS organization_type,
               reviewer.first_name AS reviewer_first_name,
               reviewer.last_name AS reviewer_last_name,
               scientific_lead.first_name AS scientific_lead_first_name,
               scientific_lead.last_name AS scientific_lead_last_name,
               manager.first_name AS manager_first_name,
               manager.last_name AS manager_last_name
        FROM project
        INNER JOIN person AS reviewer
        INNER JOIN person AS manager
        INNER JOIN person AS scientific_lead
        INNER JOIN organization
        ON project.reviewer_id = reviewer.id
        AND project.manager_id = manager.id
        AND project.scientific_lead_id = scientific_lead.id
        AND organization.name = project.managing_organization_name
        WHERE project.id = %s
        '''
        , id)

    scientific_fields = database.mariadb_select_all(
        '''
        SELECT scientific_field.title
        FROM scientific_field
        INNER JOIN project_relates_to_scientific_field AS relates
        ON relates.scientific_field_title = scientific_field.title
        WHERE relates.project_id = %s
        ''', id)

    scientific_field_titles = [sf['title'] for sf in scientific_fields]

    researchers = database.mariadb_select_all(
        '''
        SELECT person.first_name,
               person.last_name
        FROM person
        INNER JOIN researcher_participates_in_project AS participates
        ON participates.researcher_id = person.id
        WHERE participates.project_id = %s
        ORDER BY person.last_name ASC, person.first_name ASC
        ''', id)

    researcher_names = [r['last_name'] + ' ' + r['first_name'] for r in researchers]

    deliverables = database.mariadb_select_all(
        '''
        SELECT deliverable.title,
               deliverable.delivery_date
        FROM deliverable
        WHERE deliverable.project_id = %s
        ORDER BY deliverable.delivery_date ASC
        ''', id)

    return render(request, 'research_funding/project/details.html', { 'project': project, 'scientific_field_titles': scientific_field_titles, 'researcher_names': researcher_names, 'deliverables': deliverables })

def managers_dual_role(request):
    people = database.mariadb_select_all(
        '''
        SELECT * FROM dual_role_people
        ''', [])

    return render(request, 'research_funding/manager/dual_role.html', { 'people': people })
