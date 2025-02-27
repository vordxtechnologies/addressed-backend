from abc import ABC, abstractmethod
from typing import Any, Dict
from app.core.logging.logging_config import logger

class BaseToolService(ABC):
    def __init__(self):
        self.logger = logger

    @abstractmethod
    async def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute the tool's main functionality"""
        pass

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Return the tool's name"""
        pass