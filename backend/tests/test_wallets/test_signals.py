import pytest
from tests.factories import UserFactory

@pytest.mark.django_db
def test_creating_a_creator_creates_a_wallet(client):
    """Test that creating a creator also creates a Wallet."""
    user = UserFactory()
    creator_profile = user.creator_profile

    assert hasattr(creator_profile, 'wallet')
    assert creator_profile.wallet.creator == creator_profile
    assert creator_profile.wallet.balance == 0