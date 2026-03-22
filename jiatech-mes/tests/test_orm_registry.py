"""Tests for ORM registry."""

import pytest
from jiatech_mes.orm.registry import Registry


class TestRegistry:
    """Test cases for Registry class."""
    
    def test_registry_creation(self):
        """Test Registry creation with database name."""
        registry = Registry('test_db')
        assert registry.db_name == 'test_db'
    
    def test_registry_stores_models(self):
        """Test that Registry stores models."""
        registry = Registry('test_db')
        assert hasattr(registry, 'models')
        assert isinstance(registry.models, dict)
    
    def test_registry_register_model(self):
        """Test registering a model."""
        registry = Registry('test_db')
        
        class TestModel:
            _name = 'test.model'
        
        registry.register_model(TestModel)
        assert 'test.model' in registry.models
        assert registry.models['test.model'] == TestModel
    
    def test_registry_get_model(self):
        """Test getting a model from registry."""
        registry = Registry('test_db')
        
        class TestModel:
            _name = 'test.model'
        
        registry.register_model(TestModel)
        model = registry['test.model']
        assert model == TestModel
    
    def test_registry_get_all_models(self):
        """Test getting all registered models."""
        registry = Registry('test_db')
        
        class Model1:
            _name = 'model.1'
        
        class Model2:
            _name = 'model.2'
        
        registry.register_model(Model1)
        registry.register_model(Model2)
        
        models = registry.get_models()
        assert len(models) == 2
        assert Model1 in models
        assert Model2 in models
    
    def test_registry_tracks_depends(self):
        """Test that Registry tracks dependencies."""
        registry = Registry('test_db')
        assert hasattr(registry, '_depends')
        assert isinstance(registry._depends, dict)
    
    def test_registry_sql_tables(self):
        """Test that Registry has SQL tables dict."""
        registry = Registry('test_db')
        assert hasattr(registry, '_sql_tables')
        assert isinstance(registry._sql_tables, dict)
