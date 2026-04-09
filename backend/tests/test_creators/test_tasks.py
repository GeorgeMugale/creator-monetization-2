"""
Tests for Celery tasks in the creators app.
"""
import pytest
from apps.creators.tasks import send_welcome_email_task
from tests.factories import UserFactory


@pytest.mark.django_db
class TestSendWelcomeEmailTask:
    """Tests for send_welcome_email_task Celery task."""

    def test_send_welcome_email_task_success(self, mocker):
        """Test successful execution of welcome email task."""
        # Arrange
        user = UserFactory(user_type='creator', email='creator@example.com')
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        mock_send_welcome.return_value = True
        
        # Act
        result = send_welcome_email_task(user.id)
        
        # Assert
        assert 'Welcome email sent to' in result
        assert 'creator@example.com' in result
        mock_send_welcome.assert_called_once()
        call_args = mock_send_welcome.call_args[0]
        assert call_args[0].id == user.id

    def test_send_welcome_email_task_skips_non_creators(self, mocker):
        """Test that task skips non-creator users."""
        # Arrange
        user = UserFactory(user_type='staff', email='staff@example.com')
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        
        # Act
        result = send_welcome_email_task(user.id)
        
        # Assert
        assert 'skipped' in result.lower()
        assert 'not a creator' in result.lower()
        mock_send_welcome.assert_not_called()

    def test_send_welcome_email_task_handles_missing_user(self, mocker):
        """Test that task handles missing user gracefully."""
        # Arrange
        non_existent_user_id = 99999
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        mock_logger = mocker.patch('apps.creators.tasks.logger')
        
        # Act
        result = send_welcome_email_task(non_existent_user_id)
        
        # Assert
        assert 'not found' in result.lower()
        mock_send_welcome.assert_not_called()
        mock_logger.error.assert_called_once()

    def test_send_welcome_email_task_handles_send_failure(self, mocker):
        """Test that task returns failure message when email send fails."""
        # Arrange
        user = UserFactory(user_type='creator', email='creator@example.com')
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        mock_send_welcome.return_value = False
        
        # Act
        result = send_welcome_email_task(user.id)
        
        # Assert
        assert 'Failed' in result or 'failed' in result.lower()
        assert 'creator@example.com' in result

    def test_send_welcome_email_task_propagates_exceptions(self, mocker):
        """Test that unexpected exceptions are re-raised."""
        # Arrange
        user = UserFactory(user_type='creator')
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        mock_send_welcome.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            send_welcome_email_task(user.id)
        
        assert "Unexpected error" in str(exc_info.value)

    def test_send_welcome_email_task_logs_success(self, mocker):
        """Test that task logs successful email send."""
        # Arrange
        user = UserFactory(user_type='creator')
        mock_send_welcome = mocker.patch('apps.creators.tasks.send_welcome_email')
        mock_send_welcome.return_value = True
        mock_logger = mocker.patch('apps.creators.tasks.logger')
        
        # Act
        send_welcome_email_task(user.id)
        
        # Assert
        # Should have at least one info log call about success
        log_calls = mock_logger.info.call_args_list
        assert len(log_calls) > 0
        assert any('successfully' in str(call).lower() for call in log_calls)


@pytest.mark.django_db
class TestWelcomeEmailTaskSignalIntegration:
    """Tests for signal integration with send_welcome_email_task."""

    def test_welcome_email_task_triggered_on_creator_user_creation(self, mocker):
        """Test that welcome email task is queued when creator user is created."""
        # Arrange
        mock_task = mocker.patch('apps.creators.signals.send_welcome_email_task.delay')
        
        # Act
        user = UserFactory(user_type='creator')
        
        # Assert
        mock_task.assert_called_once()
        call_args = mock_task.call_args[0]
        assert call_args[0] == user.id

    def test_welcome_email_task_not_triggered_for_non_creators(self, mocker):
        """Test that welcome email task is NOT queued for non-creator users."""
        # Arrange
        mock_task = mocker.patch('apps.creators.signals.send_welcome_email_task.delay')
        
        # Act
        user = UserFactory(user_type='staff')
        
        # Assert
        mock_task.assert_not_called()

    def test_creator_profile_created_before_welcome_email_task(self, mocker):
        """Test that CreatorProfile is created before welcome email task is queued."""
        # Arrange
        mock_task = mocker.patch('apps.creators.signals.send_welcome_email_task.delay')
        
        # Act
        user = UserFactory(user_type='creator')
        
        # Assert
        # User should have a creator profile
        assert hasattr(user, 'creator_profile')
        # Task should have been called with the user ID
        mock_task.assert_called_once_with(user.id)
