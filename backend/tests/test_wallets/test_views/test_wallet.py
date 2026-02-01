import pytest

@pytest.marker.django_db
class TestWalletViews:
    """Tests for wallet views"""

    def test_get_user_wallet(self, api_client, user_factory):
        """Test getting current user's wallet"""
        api_client.force_authenticate(user=user_factory)
        response = api_client.get("/api/v1/wallets/me/")
        assert response.status_code == 200
        assert "id" in response.data
        assert "balance" in response.data
        assert "is_active" in response.data
        assert "currency" in response.data

    def test_get_wallet_kyc(self, api_client, wallet_kyc_factory):
        """Test getting current user's wallet KYC"""
        api_client.force_authenticate(user=wallet_kyc_factory.wallet.creator.user)
        response = api_client.get("/api/v1/wallets/kyc/")
        assert response.status_code == 200
        assert "id_document_type" in response.data
        assert "id_document_number" in response.data
        assert "bank_name" in response.data
        

    def test_get_wallet_transactions(self, api_client, wallet_transaction_factory):
        """Test getting current users tips"""
        api_client.force_authenticate(user=wallet_transaction_factory.wallet.creator.user)
        response = api_client.get("/api/v1/wallets/transactions/")
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        transaction = response.data[0]
        assert "amount" in transaction
        assert "transaction_type" in transaction
        assert "status" in transaction
        assert "reference" in transaction
       
