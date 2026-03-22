"""Tests for ORM models."""

import pytest
from jiatech_mes.orm.models import BaseModel, Model, AbstractModel


class TestBaseModel:
    """Test cases for BaseModel."""
    
    def test_base_model_is_abstract(self):
        """Test that BaseModel is marked as abstract."""
        assert BaseModel._abstract is True
    
    def test_base_model_has_id_field(self):
        """Test that BaseModel has an id field."""
        assert hasattr(BaseModel, 'id')
    
    def test_base_model_has_create_date_field(self):
        """Test that BaseModel has create_date field."""
        assert hasattr(BaseModel, 'create_date')
    
    def test_base_model_has_write_date_field(self):
        """Test that BaseModel has write_date field."""
        assert hasattr(BaseModel, 'write_date')


class TestModel:
    """Test cases for Model."""
    
    def test_model_is_not_abstract_by_default(self):
        """Test that Model is not abstract by default."""
        assert Model._abstract is False
    
    def test_model_has_table_name(self):
        """Test that Model has a table name."""
        assert hasattr(Model, '_table')


class TestAbstractModel:
    """Test cases for AbstractModel."""
    
    def test_abstract_model_is_abstract(self):
        """Test that AbstractModel is marked as abstract."""
        assert AbstractModel._abstract is True
    
    def test_abstract_model_does_not_create_table(self):
        """Test that AbstractModel doesn't have a table by default."""
        assert not hasattr(AbstractModel, '_table')
