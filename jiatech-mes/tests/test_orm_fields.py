"""Tests for ORM fields."""

import pytest
from jiatech_mes.orm.fields import Field, Char, Integer, Float, Boolean, Selection


class TestField:
    """Test cases for base Field class."""
    
    def test_field_has_required_attributes(self):
        """Test that Field has required attributes."""
        field = Field(string='Test Field')
        assert hasattr(field, 'string')
        assert field.string == 'Test Field'
    
    def test_field_has_default_values(self):
        """Test that Field has correct default values."""
        field = Field()
        assert field.readonly is False
        assert field.required is False
        assert field.index is False


class TestCharField:
    """Test cases for Char field."""
    
    def test_char_field_creation(self):
        """Test Char field creation."""
        field = Char(string='Name', required=True)
        assert field.string == 'Name'
        assert field.required is True
    
    def test_char_field_has_size(self):
        """Test Char field has size attribute."""
        field = Char(string='Code', size=10)
        assert hasattr(field, 'size')
        assert field.size == 10


class TestIntegerField:
    """Test cases for Integer field."""
    
    def test_integer_field_creation(self):
        """Test Integer field creation."""
        field = Integer(string='Count', default=0)
        assert field.string == 'Count'
        assert field.default == 0


class TestFloatField:
    """Test cases for Float field."""
    
    def test_float_field_creation(self):
        """Test Float field creation."""
        field = Float(string='Price', digits=(10, 2))
        assert field.string == 'Price'
        assert hasattr(field, 'digits')
        assert field.digits == (10, 2)


class TestBooleanField:
    """Test cases for Boolean field."""
    
    def test_boolean_field_creation(self):
        """Test Boolean field creation."""
        field = Boolean(string='Active', default=True)
        assert field.string == 'Active'
        assert field.default is True


class TestSelectionField:
    """Test cases for Selection field."""
    
    def test_selection_field_creation(self):
        """Test Selection field creation."""
        field = Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
        ], string='State')
        assert field.string == 'State'
        assert len(field.selection) == 2
    
    def test_selection_field_has_selection_list(self):
        """Test Selection field has selection list."""
        field = Selection([('a', 'A'), ('b', 'B')])
        assert hasattr(field, 'selection')
        assert field.selection == [('a', 'A'), ('b', 'B')]
