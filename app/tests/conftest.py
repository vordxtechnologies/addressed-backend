import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database.firestore.client import db
from app.infrastructure.database.redis.client import redis_client
import os
import json

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_firebase_token():
    return {
        "uid": "test_user_id",
        "email": "test@example.com",
        "name": "Test User"
    }

@pytest.fixture
def mock_db(monkeypatch):
    class MockFirestore:
        def collection(self, name):
            return self
        
        def document(self, id):
            return self
        
        def get(self):
            return None
        
        def set(self, data):
            return None
            
    monkeypatch.setattr("app.infrastructure.database.firestore.client.db", MockFirestore())

@pytest.fixture
def mock_redis(monkeypatch):
    class MockRedis:
        def __init__(self):
            self.data = {}
            
        def get(self, key):
            return self.data.get(key)
            
        def setex(self, key, exp, value):
            self.data[key] = value
            
    monkeypatch.setattr("app.infrastructure.database.redis.client.redis_client", MockRedis()) 