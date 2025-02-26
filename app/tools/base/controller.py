# app/tools/base/controller.py
class BaseController:
    def __init__(self, service):
        self.service = service

# app/tools/base/service.py
class BaseService:
    def __init__(self, repository):
        self.repository = repository

# app/tools/base/repository.py
class BaseRepository:
    def __init__(self, db):
        self.db = db