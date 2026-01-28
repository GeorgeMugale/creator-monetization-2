"""
Tests for management commands.
"""
import pytest
from io import StringIO
from django.core.management import call_command
from apps.customauth.models import APIClient


@pytest.mark.django_db
class TestCreateAPIClientCommand:
    """Test create_api_client management command."""

    def test_create_api_client_success(self):
        """Test successfully creating API client."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Test Client',
            '--type', 'web',
            '--description', 'Test Description',
            '--rate-limit', '500',
            stdout=out
        )
        
        assert APIClient.objects.filter(name='Test Client').exists()
        client = APIClient.objects.get(name='Test Client')
        assert client.client_type == 'web'
        assert client.description == 'Test Description'
        assert client.rate_limit == 500
        assert client.api_key.startswith('sk_')
        assert 'API Client created successfully' in out.getvalue()

    def test_create_api_client_default_rate_limit(self):
        """Test creating API client with default rate limit."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Test Client',
            '--type', 'web',
            stdout=out
        )
        
        client = APIClient.objects.get(name='Test Client')
        assert client.rate_limit == 1000  # Default

    def test_create_api_client_web_type(self):
        """Test creating web type API client."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Web App',
            '--type', 'web',
            stdout=out
        )
        
        client = APIClient.objects.get(name='Web App')
        assert client.client_type == 'web'

    def test_create_api_client_mobile_type(self):
        """Test creating mobile type API client."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Mobile App',
            '--type', 'mobile',
            stdout=out
        )
        
        client = APIClient.objects.get(name='Mobile App')
        assert client.client_type == 'mobile'

    def test_create_api_client_internal_type(self):
        """Test creating internal type API client."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Internal Service',
            '--type', 'internal',
            stdout=out
        )
        
        client = APIClient.objects.get(name='Internal Service')
        assert client.client_type == 'internal'

    def test_create_api_client_partner_type(self):
        """Test creating partner type API client."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Partner API',
            '--type', 'partner',
            stdout=out
        )
        
        client = APIClient.objects.get(name='Partner API')
        assert client.client_type == 'partner'

    def test_create_duplicate_api_client_fails(self):
        """Test creating duplicate client fails."""
        out_err = StringIO()
        
        # Create first client
        call_command(
            'create_api_client',
            '--name', 'Test Client',
            '--type', 'web',
            stdout=StringIO()
        )
        
        # Try to create duplicate
        call_command(
            'create_api_client',
            '--name', 'Test Client',
            '--type', 'web',
            stdout=out_err
        )
        
        output = out_err.getvalue()
        assert 'already exists' in output

    def test_create_api_client_missing_required_args(self):
        """Test command fails without required arguments."""
        with pytest.raises(SystemExit):
            call_command('create_api_client')

    def test_create_api_client_generates_unique_keys(self):
        """Test created clients have unique API keys."""
        call_command(
            'create_api_client',
            '--name', 'Client 1',
            '--type', 'web',
            stdout=StringIO()
        )
        
        call_command(
            'create_api_client',
            '--name', 'Client 2',
            '--type', 'web',
            stdout=StringIO()
        )
        
        client1 = APIClient.objects.get(name='Client 1')
        client2 = APIClient.objects.get(name='Client 2')
        
        assert client1.api_key != client2.api_key

    def test_create_api_client_output_contains_details(self):
        """Test command output contains client details."""
        out = StringIO()
        
        call_command(
            'create_api_client',
            '--name', 'Output Test',
            '--type', 'web',
            '--rate-limit', '2000',
            stdout=out
        )
        
        output = out.getvalue()
        assert 'Output Test' in output
        assert 'API Key:' in output
        assert '2000 requests/hour' in output

    def test_create_multiple_api_clients(self):
        """Test creating multiple API clients."""
        for i in range(3):
            call_command(
                'create_api_client',
                '--name', f'Client {i}',
                '--type', 'web',
                stdout=StringIO()
            )
        
        assert APIClient.objects.count() == 3

    def test_create_api_client_with_long_name(self):
        """Test creating API client with long name."""
        long_name = 'A' * 200
        
        out = StringIO()
        call_command(
            'create_api_client',
            '--name', long_name,
            '--type', 'web',
            stdout=out
        )
        
        client = APIClient.objects.get(name=long_name)
        assert client.name == long_name

    def test_create_api_client_is_active_by_default(self):
        """Test created client is active by default."""
        call_command(
            'create_api_client',
            '--name', 'Active Test',
            '--type', 'web',
            stdout=StringIO()
        )
        
        client = APIClient.objects.get(name='Active Test')
        assert client.is_active is True

    def test_command_with_description(self):
        """Test command with description."""
        description = 'This is a test client for the API'
        
        call_command(
            'create_api_client',
            '--name', 'Described Client',
            '--type', 'web',
            '--description', description,
            stdout=StringIO()
        )
        
        client = APIClient.objects.get(name='Described Client')
        assert client.description == description

    def test_command_with_different_rate_limits(self):
        """Test command with various rate limits."""
        rate_limits = [100, 500, 1000, 5000, 10000]
        
        for idx, limit in enumerate(rate_limits):
            call_command(
                'create_api_client',
                '--name', f'Rate Limit {idx}',
                '--type', 'web',
                '--rate-limit', str(limit),
                stdout=StringIO()
            )
        
        for idx, limit in enumerate(rate_limits):
            client = APIClient.objects.get(name=f'Rate Limit {idx}')
            assert client.rate_limit == limit
