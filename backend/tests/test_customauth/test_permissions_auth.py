"""
Tests for authentication utilities and permissions.
"""
import pytest
from rest_framework.test import APIRequestFactory
from apps.customauth.permissions import IsCreator, IsAdminUser, IsStaffUser
from utils.authentication import APIKeyAuthentication, ClientIdentificationMiddleware
from tests.factories import UserFactory, StaffUserFactory, AdminUserFactory, APIClientFactory


@pytest.mark.django_db
class TestIsCreatorPermission:
    """Test IsCreator permission class."""

    def test_creator_has_permission(self):
        """Test creator user has permission."""
        user = UserFactory(user_type='creator')
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsCreator()
        assert permission.has_permission(request, None) is True

    def test_staff_denied_permission(self):
        """Test staff user is denied."""
        user = StaffUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsCreator()
        assert permission.has_permission(request, None) is False

    def test_admin_denied_permission(self):
        """Test admin user is denied."""
        user = AdminUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsCreator()
        assert permission.has_permission(request, None) is False

    def test_unauthenticated_denied(self):
        """Test unauthenticated user is denied."""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = None
        
        permission = IsCreator()
        assert permission.has_permission(request, None) is None


@pytest.mark.django_db
class TestIsAdminUserPermission:
    """Test IsAdminUser permission class."""

    def test_creator_denied_permission(self):
        """Test creator is denied."""
        user = UserFactory(user_type='creator')
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsAdminUser()
        assert permission.has_permission(request, None) is False

    def test_staff_has_permission(self):
        """Test staff user has permission."""
        user = StaffUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsAdminUser()
        assert permission.has_permission(request, None) is True

    def test_admin_has_permission(self):
        """Test admin user has permission."""
        user = AdminUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsAdminUser()
        assert permission.has_permission(request, None) is True

    def test_unauthenticated_denied(self):
        """Test unauthenticated user is denied."""
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = None
        
        permission = IsAdminUser()
        assert permission.has_permission(request, None) is None


@pytest.mark.django_db
class TestIsStaffUserPermission:
    """Test IsStaffUser permission class."""

    def test_creator_denied_permission(self):
        """Test creator is denied."""
        user = UserFactory(user_type='creator')
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsStaffUser()
        assert permission.has_permission(request, None) is False

    def test_staff_has_permission(self):
        """Test staff user has permission."""
        user = StaffUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsStaffUser()
        assert permission.has_permission(request, None) is True

    def test_superuser_has_permission(self):
        """Test superuser has permission."""
        user = AdminUserFactory()
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        
        permission = IsStaffUser()
        assert permission.has_permission(request, None) is True


@pytest.mark.django_db
class TestAPIKeyAuthentication:
    """Test APIKeyAuthentication class."""

    def test_authenticate_with_valid_api_key(self):
        """Test authentication with valid API key."""
        client = APIClientFactory(is_active=True)
        factory = APIRequestFactory()
        request = factory.get(
            '/',
            HTTP_X_API_KEY=client.api_key
        )
        
        auth = APIKeyAuthentication()
        result = auth.authenticate(request)
        
        # Should return None (continue with JWT auth) but set client on request
        assert result is None
        assert hasattr(request, 'client')
        assert request.client.id == client.id

    def test_authenticate_with_invalid_api_key(self):
        """Test authentication fails with invalid API key."""
        factory = APIRequestFactory()
        request = factory.get('/', HTTP_X_API_KEY='invalid_key')
        
        auth = APIKeyAuthentication()
        
        with pytest.raises(Exception):  # AuthenticationFailed
            auth.authenticate(request)

    def test_authenticate_with_inactive_client(self):
        """Test authentication fails with inactive client."""
        client = APIClientFactory(is_active=False)
        factory = APIRequestFactory()
        request = factory.get(
            '/',
            HTTP_X_API_KEY=client.api_key
        )
        
        auth = APIKeyAuthentication()
        
        with pytest.raises(Exception):  # AuthenticationFailed
            auth.authenticate(request)

    def test_authenticate_without_api_key(self):
        """Test authentication returns None without API key."""
        factory = APIRequestFactory()
        request = factory.get('/')
        
        auth = APIKeyAuthentication()
        result = auth.authenticate(request)
        
        assert result is None

    def test_authenticate_header(self):
        """Test authenticate_header method."""
        auth = APIKeyAuthentication()
        factory = APIRequestFactory()
        request = factory.get('/')
        
        header = auth.authenticate_header(request)
        assert header == 'X-API-Key'


@pytest.mark.django_db
class TestClientIdentificationMiddleware:
    """Test ClientIdentificationMiddleware."""

    def test_middleware_identifies_client_by_api_key(self):
        """Test middleware identifies client by API key."""
        client = APIClientFactory(is_active=True)
        
        class DummyRequest:
            META = {'HTTP_X_API_KEY': client.api_key}
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        assert hasattr(request, 'client')
        assert request.client.id == client.id

    def test_middleware_identifies_client_by_id(self):
        """Test middleware identifies client by client ID."""
        client = APIClientFactory(is_active=True)
        
        class DummyRequest:
            META = {'HTTP_X_CLIENT_ID': str(client.id)}
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        assert hasattr(request, 'client')
        assert request.client.id == client.id

    def test_middleware_prefers_api_key_over_id(self):
        """Test middleware prefers API key over client ID."""
        client1 = APIClientFactory(is_active=True)
        client2 = APIClientFactory(is_active=True)
        
        class DummyRequest:
            META = {
                'HTTP_X_API_KEY': client1.api_key,
                'HTTP_X_CLIENT_ID': str(client2.id)
            }
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        # Should use API key first
        assert request.client.id == client1.id

    def test_middleware_without_client_info(self):
        """Test middleware when no client info provided."""
        class DummyRequest:
            META = {}
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        # Should not set client attribute
        assert not hasattr(request, 'client')

    def test_middleware_with_inactive_client(self):
        """Test middleware doesn't set inactive client."""
        client = APIClientFactory(is_active=False)
        
        class DummyRequest:
            META = {'HTTP_X_API_KEY': client.api_key}
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        assert not hasattr(request, 'client')

    def test_middleware_with_nonexistent_client_id(self):
        """Test middleware doesn't set client for nonexistent ID."""
        import uuid
        
        class DummyRequest:
            META = {'HTTP_X_CLIENT_ID': str(uuid.uuid4())}
        
        class GetResponse:
            def __call__(self, request):
                return None
        
        middleware = ClientIdentificationMiddleware(GetResponse())
        request = DummyRequest()
        
        middleware(request)
        
        assert not hasattr(request, 'client')
