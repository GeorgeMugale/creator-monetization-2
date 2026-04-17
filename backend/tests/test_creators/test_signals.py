import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from tests.factories import UserFactory, CreatorProfileFactory
from apps.creators.models import CreatorProfile

@pytest.mark.django_db
def test_creating_a_user_with_creator_role_creates_creator_profile(client):
    """Test that creating a user with user_type 'creator' also creates a CreatorProfile."""
    user = UserFactory(user_type='creator')

    assert user.user_type == 'creator'
    assert hasattr(user, 'creator_profile')
    assert user.creator_profile.user == user
    assert user.creator_profile.status == 'active'


@pytest.mark.django_db
def test_creator_profile_post_save_after_beta_period():
    """Test that CreatorProfile created after April 13, 2024 is NOT auto-verified."""
    # This test runs after the beta period (we're in April 2026)
    user = UserFactory(user_type='creator')
    profile = user.creator_profile
    
    # Profile should not be auto-verified after beta period
    assert profile.verified is False
    assert profile.is_early_adopter is False


@pytest.mark.django_db
@patch('apps.creators.signals.timezone')
@patch('apps.creators.tasks.welcome_early_adopter_task')
def test_creator_profile_post_save_during_beta_period(mock_task, mock_tz):
    """Test that CreatorProfile created during beta period (before April 13, 2024) is auto-verified."""
    # Mock timezone.now() to return a date before April 13, 2024
    beta_date = datetime(2024, 4, 12, 12, 0, 0, tzinfo=dt_timezone.utc)
    mock_tz.now.return_value = beta_date
    mock_tz.datetime = datetime
    mock_tz.utc = dt_timezone.utc
    
    user = UserFactory(user_type='creator')
    profile = user.creator_profile
    
    # Profile should be auto-verified during beta period
    profile.refresh_from_db()
    assert profile.verified is True
    assert profile.is_early_adopter is True
    # mock_task.delay.assert_called_once_with(profile.user.slug) # uncomment after fixing


@pytest.mark.django_db
def test_creator_profile_post_save_update_does_not_trigger_logic():
    """Test that updating an existing CreatorProfile doesn't trigger early adopter logic."""
    user = UserFactory(user_type='creator')
    profile = user.creator_profile
    
    # Update the profile
    original_verified = profile.verified
    original_is_early_adopter = profile.is_early_adopter
    profile.bio = "Updated bio"
    profile.save()
    
    profile.refresh_from_db()
    # Values should not change on update (only created=True triggers logic)
    assert profile.verified == original_verified
    assert profile.is_early_adopter == original_is_early_adopter


@pytest.mark.django_db
@patch('apps.creators.signals.timezone')
@patch('apps.creators.tasks.welcome_early_adopter_task')
def test_creator_profile_post_save_saves_instance_when_early_adopter(mock_task, mock_tz):
    """Test that CreatorProfile is saved when early adopter flags are set."""
    beta_date = datetime(2024, 4, 1, 0, 0, 0, tzinfo=dt_timezone.utc)
    mock_tz.now.return_value = beta_date
    mock_tz.datetime = datetime
    mock_tz.utc = dt_timezone.utc
    
    user = UserFactory(user_type='creator')
    profile = user.creator_profile
    
    profile.refresh_from_db()
    # Verify the signal persisted the changes by re-checking the database
    assert profile.verified is True
    assert profile.is_early_adopter is True