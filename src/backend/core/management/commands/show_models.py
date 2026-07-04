"""
Management command to show all models from specific domains.

Usage:
    python manage.py show_models
    python manage.py show_models --domain assessment
    python manage.py show_models --domain submissions
    python manage.py show_models --domain mentorship
    python manage.py show_models --all
"""
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Show all models from specific domains'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain name (assessment, submissions, mentorship)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all models from all domains'
        )

    def handle(self, *args, **options):
        domain = options.get('domain')
        show_all = options.get('all')

        domains = ['assessment', 'submissions', 'mentorship']

        if domain:
            domains = [domain]
        elif not show_all:
            self.stdout.write(self.style.WARNING(
                'Use --domain <name> or --all\n'
                'Available domains: assessment, submissions, mentorship'
            ))
            return

        for domain_name in domains:
            self.show_domain_models(domain_name)

    def show_domain_models(self, domain_name: str):
        """Show all models for a specific domain."""
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 60}'))
        self.stdout.write(self.style.SUCCESS(f'DOMAIN: {domain_name.upper()}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 60}\n'))

        
        models = apps.get_app_config(domain_name).get_models()

        for model in models:
            model_name = model.__name__
            table_name = model._meta.db_table

            self.stdout.write(self.style.MIGRATE_HEADING(f'\n📦 {model_name}'))
            self.stdout.write(f'   Table: {table_name}')
            self.stdout.write(f'   App: {model._meta.app_label}')

            
            try:
                count = model.objects.count()
                self.stdout.write(self.style.SUCCESS(f'   Records: {count}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   Error counting: {e}'))

            
            self.stdout.write(self.style.MIGRATE_LABEL('   Fields:'))
            for field in model._meta.get_fields():
                field_type = field.__class__.__name__
                if hasattr(field, 'related_model') and field.related_model:
                    self.stdout.write(f'     - {field.name}: {field_type} → {field.related_model.__name__}')
                else:
                    self.stdout.write(f'     - {field.name}: {field_type}')

            
            try:
                records = model.objects.all()[:3]
                if records:
                    self.stdout.write(self.style.MIGRATE_LABEL('   Sample records:'))
                    for record in records:
                        self.stdout.write(f'     • {record}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   Error fetching records: {e}'))