"""Test fixtures and configuration for Jia Tech MES."""

import pytest
from typing import Generator

from jiatech_mes.orm.models import BaseModel, Model, AbstractModel
from jiatech_mes.orm.environment import Environment
from jiatech_mes.orm.registry import Registry


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.data: dict[str, dict[int, dict]] = {}
        self.next_id: dict[str, int] = {}
    
    def create_table(self, table_name: str) -> None:
        """Create a mock table."""
        if table_name not in self.data:
            self.data[table_name] = {}
            self.next_id[table_name] = 1
    
    def insert(self, table_name: str, values: dict) -> int:
        """Insert a record and return its ID."""
        self.create_table(table_name)
        record_id = self.next_id[table_name]
        self.next_id[table_name] += 1
        self.data[table_name][record_id] = {'id': record_id, **values}
        return record_id
    
    def update(self, table_name: str, record_id: int, values: dict) -> bool:
        """Update a record."""
        if table_name in self.data and record_id in self.data[table_name]:
            self.data[table_name][record_id].update(values)
            return True
        return False
    
    def select(self, table_name: str, record_id: int) -> dict | None:
        """Select a record by ID."""
        return self.data.get(table_name, {}).get(record_id)
    
    def select_all(self, table_name: str) -> list[dict]:
        """Select all records from a table."""
        return list(self.data.get(table_name, {}).values())
    
    def delete(self, table_name: str, record_id: int) -> bool:
        """Delete a record."""
        if table_name in self.data and record_id in self.data[table_name]:
            del self.data[table_name][record_id]
            return True
        return False


@pytest.fixture
def mock_db() -> Generator[MockDatabase, None, None]:
    """Provide a mock database for testing."""
    db = MockDatabase()
    yield db
    db.data.clear()


@pytest.fixture
def mock_env(mock_db: MockDatabase) -> Environment:
    """Provide a mock environment for testing."""
    registry = Registry('test')
    env = Environment(registry, uid=1, cr=mock_db, context={})
    return env


class TestModel(Model):
    """Test model for unit testing."""
    
    _name = 'test.model'
    _table = 'test_model'
    
    name = None
    value = None
    
    def _register_hook(self) -> None:
        pass
