from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker
from store.models import Collection # it violates dependency rule, but no walkaround

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(context):
        return api_client.post('/store/collections/', context)
    return do_create_collection

@pytest.fixture
def authenticate_client(api_client):
    def do_authenticate_client(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate_client

@pytest.mark.django_db # allows the test modify db
class TestCreateCollection:
    # @pytest.mark.skip # skip this test
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # AAA (Arrange, Act, Assert)
        # Arrange

        # Act
        response = create_collection({'title': 'a'})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, create_collection, authenticate_client):
        authenticate_client()

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, create_collection, authenticate_client):
        authenticate_client(True)

        response = create_collection({'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, create_collection, authenticate_client):
        authenticate_client(True)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        # Arrange
        collection = baker.make(Collection)
        # Act
        response = api_client.get(f'/store/collections/{collection.id}/')
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0,
        }