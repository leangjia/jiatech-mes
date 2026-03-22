"""Tests for ORM API decorators."""

import pytest
from jiatech_mes.orm.api import api, model, depends, onchange, constrains


class TestApiDecorator:
    """Test cases for @api decorator."""
    
    def test_api_decorator_exists(self):
        """Test that @api decorator exists."""
        assert callable(api)
    
    def test_model_decorator_exists(self):
        """Test that @model decorator exists."""
        assert callable(model)
    
    def test_depends_decorator_exists(self):
        """Test that @depends decorator exists."""
        assert callable(depends)
    
    def test_onchange_decorator_exists(self):
        """Test that @onchange decorator exists."""
        assert callable(onchange)
    
    def test_constrains_decorator_exists(self):
        """Test that @constrains decorator exists."""
        assert callable(constrains)


class TestModelDecorator:
    """Test cases for @model decorator."""
    
    def test_model_decorator_marks_function(self):
        """Test that @model decorator marks a function correctly."""
        
        @model
        def my_model_method(self):
            return True
        
        assert hasattr(my_model_method, '_api')
        assert my_model_method._api == 'model'


class TestDependsDecorator:
    """Test cases for @depends decorator."""
    
    def test_depends_decorator_accepts_fields(self):
        """Test that @depends decorator accepts field names."""
        
        @depends('name', 'value')
        def my_method(self):
            return True
        
        assert hasattr(my_method, '_depends')
        assert 'name' in my_method._depends
        assert 'value' in my_method._depends


class TestOnchangeDecorator:
    """Test cases for @onchange decorator."""
    
    def test_onchange_decorator_marks_function(self):
        """Test that @onchange decorator marks a function correctly."""
        
        @onchange('field_a')
        def my_method(self):
            return True
        
        assert hasattr(my_method, '_onchange')
        assert 'field_a' in my_method._onchange


class TestConstrainsDecorator:
    """Test cases for @constrains decorator."""
    
    def test_constrains_decorator_accepts_fields(self):
        """Test that @constrains decorator accepts field names."""
        
        @constrains('name', 'value')
        def my_method(self):
            pass
        
        assert hasattr(my_method, '_constrains')
        assert 'name' in my_method._constrains
        assert 'value' in my_method._constrains
