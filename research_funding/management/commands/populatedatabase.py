from django.core.management.base import BaseCommand, CommandError
from research_funding import mock
from research_funding.database import mariadb_create_connection, mariadb_insert_many, mariadb_select_all

import random

class Command(BaseCommand):
    help = '(Re)populates the database'

    def add_arguments(self, parser):
        parser.add_argument('--seed', nargs=1, type=int, help='an integer seed to pass to the prng (default: use system defaults)')

    def handle(self, *args, **options):
        seed = options['seed']

        if seed:
            random.seed(seed[0])

        organization_n = 500
        university_n = 0
        research_center_n = 0
        company_n = 0
        connection = mariadb_create_connection()

        organization_ids = []
        
        try:
            with connection.cursor() as cursor:
                for _ in range(organization_n):
                    (o, ps) = mock.generate_organization()

                    while o[0] in organization_ids:
                        (o, ps) = mock.generate_organization()

                    organization_ids.append(o[0])

                    if o[1] == 'university':
                        university_n += 1
                    elif o[1] == 'company':
                        company_n += 1
                    else:
                        research_center_n += 1
                    
                    cursor.execute("INSERT INTO organization VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", o)
                    
                    cursor.executemany("INSERT INTO organization_phone VALUES (%s, %s)", [(o[0], p) for p in ps])

                connection.commit()
        finally:
            connection.close()

        self.stdout.write(self.style.SUCCESS(f'Successfully created {organization_n} organizations: {university_n} universities, {research_center_n} research centers and {company_n} companies.'))
            
        department_n = 20
        department_ids = []
        for _ in range(department_n):
            department = mock.generate_department()

            mariadb_insert_many("INSERT INTO department VALUES (%s)", [department])
            department_ids.append(department)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {department_n} departments.'))

        program_n = 50
        program_ids = []
        for _ in range(program_n):
            program = mock.generate_program(department_ids)

            mariadb_insert_many("INSERT INTO program VALUES (%s, %s)", [program])
            program_ids.append(program)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {program_n} programs.'))
                            
        people_n = 1000
            
        for _ in range(people_n):
            person = mock.generate_person()

            mariadb_insert_many("INSERT INTO person VALUES (NULL, %s, %s, %s, %s)", [person])

        self.stdout.write(self.style.SUCCESS(f'Successfully created {people_n} people.'))
            
        person_ids_dict = mariadb_select_all('SELECT id FROM person', [])
        person_ids = [p['id'] for p in person_ids_dict]

        partition = mock.partition_persons(person_ids)
        researcher_ids = partition[0]
        manager_ids = partition[1]

        researchers = mock.generate_researchers(researcher_ids, organization_ids)
        researcher_and_organization_ids = [(r[0], r[1]) for r in researchers]
        
        mariadb_insert_many("INSERT INTO researcher VALUES (%s, %s, %s)", researchers)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(researcher_ids)} researchers.'))

        mariadb_insert_many("INSERT INTO manager VALUES (%s)", manager_ids)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(manager_ids)} managers.'))

        project_n = 1000
        
        for _ in range(project_n):
            project = mock.generate_project(researcher_and_organization_ids, manager_ids, program_ids, organization_ids)

            mariadb_insert_many("INSERT INTO project VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [project])

        self.stdout.write(self.style.SUCCESS(f'Successfully created {project_n} projects.'))

        project_ids_dict = mariadb_select_all('SELECT id FROM project', []);
        project_ids = [p['id'] for p in project_ids_dict]
        
        participation_n = 10000
        participations = []
        for _ in range(participation_n):
            participation = mock.generate_participation(researcher_ids, project_ids)

            if participation in participations:
                continue

            participations.append(participation)

        mariadb_insert_many("INSERT INTO researcher_participates_in_project VALUES (%s, %s)", participations)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(participations)} participation relationships between researchers and projects.'))

        fields_n = 30
        field_ids = []
        fields = []
        for _ in range(fields_n):
            field = mock.generate_scientific_field()

            if field[0] in field_ids:
                continue

            field_ids.append(field[0])
            fields.append(field)

        mariadb_insert_many("INSERT INTO scientific_field VALUES (%s, %s)", fields)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(fields)} scientific fields.'))

        project_participation_in_fields = mock.generate_project_participations_in_fields(project_ids, field_ids)

        mariadb_insert_many("INSERT INTO project_relates_to_scientific_field VALUES (%s, %s)", project_participation_in_fields)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(project_participation_in_fields)} associations between projects and scientific fields.'))

        projects = mariadb_select_all('SELECT id, start_date, duration FROM project', []);

        deliverables = mock.generate_project_deliverables(projects)

        mariadb_insert_many("INSERT INTO deliverable VALUES (%s, %s, %s, %s)", deliverables)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(deliverables)} project deliverables.'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully populated the database!'))
