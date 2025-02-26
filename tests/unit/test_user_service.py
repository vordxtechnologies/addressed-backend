import unittest
from unittest.mock import patch
from app.services.user_service import get_user, update_user, delete_user

class TestUserService(unittest.TestCase):

    @patch('app.services.user_service.get_cached_data')
    @patch('app.services.user_service.db.collection')
    def test_get_user(self, mock_db_collection, mock_get_cached_data):
        # Mock Firestore and Redis responses
        mock_get_cached_data.return_value = None
        mock_db_collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": "2023-01-01",
            "updated_at": "2023-01-01"
        }
        
        user = get_user("user123")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, "user123")

    @patch('app.services.user_service.db.collection')
    def test_update_user(self, mock_db_collection):
        user_data = {"name": "Updated User"}
        update_user("user123", user_data)
        mock_db_collection.return_value.document.return_value.update.assert_called_with(user_data)

    @patch('app.services.user_service.db.collection')
    def test_delete_user(self, mock_db_collection):
        delete_user("user123")
        mock_db_collection.return_value.document.return_value.delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()
