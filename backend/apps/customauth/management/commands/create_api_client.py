from django.core.management.base import BaseCommand
from apps.customauth.models import APIClient


class Command(BaseCommand):
    help = 'Create a new API client for frontend applications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name of the API client'
        )
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            choices=['web', 'mobile', 'internal', 'partner'],
            help='Type of client application'
        )
        parser.add_argument(
            '--description',
            type=str,
            default='',
            help='Description of the client'
        )
        parser.add_argument(
            '--rate-limit',
            type=int,
            default=1000,
            help='Rate limit (requests per hour)'
        )

    def handle(self, *args, **options):
        name = options['name']
        client_type = options['type']
        description = options['description']
        rate_limit = options['rate_limit']

        # Check if client already exists
        if APIClient.objects.filter(name=name).exists():
            self.stdout.write(
                self.style.ERROR(f'Client "{name}" already exists!')
            )
            return

        # Create client
        client = APIClient.objects.create(
            name=name,
            client_type=client_type,
            description=description,
            rate_limit=rate_limit
        )

        self.stdout.write(
            self.style.SUCCESS(f'✓ API Client created successfully!')
        )
        self.stdout.write(f'\nClient Details:')
        self.stdout.write(f'  Name: {client.name}')
        self.stdout.write(f'  Type: {client.get_client_type_display()}')
        self.stdout.write(f'  Client ID: {client.id}')
        self.stdout.write(f'  API Key: {client.api_key}')
        self.stdout.write(f'  Rate Limit: {client.rate_limit} requests/hour')
        self.stdout.write(f'\nUse in requests:')
        self.stdout.write(f'  Header 1: X-API-Key: {client.api_key}')
        self.stdout.write(f'  Header 2: X-Client-ID: {client.id}')
        self.stdout.write(
            self.style.WARNING('\n⚠ Store the API key securely. It cannot be recovered if lost!')
        )
