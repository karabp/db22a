from django.core.management.base import BaseCommand, CommandError
from research_funding.database import mariadb_execute_script
import os.path

class Command(BaseCommand):
    help = '(Re)creates the database'

    def add_arguments(self, parser):
        #parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        for file in [('drop-schema.sql', False),
                     ('create-schema.sql', False),
                     ('triggers/project_reviewer_cannot_work_for_managing_organization.sql', True),
                     ('views/projects_per_researcher.sql', True),
                     ('views/active_projects.sql', True)]:
            count = mariadb_execute_script(*file)
            self.stdout.write(self.style.SUCCESS(f'Successfully executed {count} statements from file \'{file[0]}\''))
                
        self.stdout.write(self.style.SUCCESS('Successfully (re)created the database.'))
