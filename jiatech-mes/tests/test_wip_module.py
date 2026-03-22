"""Tests for WIP Module - Lot model."""

import pytest
from jiatech_mes.modules.wip.models.mes_lot import MesLot, MesRoute, MesRouteOperation


class TestMesLot:
    """Test cases for MesLot model."""
    
    def test_lot_model_has_name_field(self):
        """Test that MesLot has a name field."""
        assert hasattr(MesLot, 'name')
    
    def test_lot_model_has_state_field(self):
        """Test that MesLot has a state field."""
        assert hasattr(MesLot, 'state')
    
    def test_lot_model_has_quantity_field(self):
        """Test that MesLot has a quantity field."""
        assert hasattr(MesLot, 'quantity')
    
    def test_lot_model_has_product_id_field(self):
        """Test that MesLot has product_id field."""
        assert hasattr(MesLot, 'product_id')
    
    def test_lot_model_has_state_selection(self):
        """Test that MesLot state has correct values."""
        state_field = MesLot._fields.get('state')
        assert state_field is not None
        assert hasattr(state_field, 'selection')
        selections = dict(state_field.selection)
        assert 'draft' in selections
        assert 'created' in selections
        assert 'in_progress' in selections
        assert 'completed' in selections


class TestMesRoute:
    """Test cases for MesRoute model."""
    
    def test_route_model_has_name_field(self):
        """Test that MesRoute has a name field."""
        assert hasattr(MesRoute, 'name')
    
    def test_route_model_has_code_field(self):
        """Test that MesRoute has a code field."""
        assert hasattr(MesRoute, 'code')
    
    def test_route_model_has_operation_ids_field(self):
        """Test that MesRoute has operation_ids field."""
        assert hasattr(MesRoute, 'operation_ids')


class TestMesRouteOperation:
    """Test cases for MesRouteOperation model."""
    
    def test_operation_model_has_name_field(self):
        """Test that MesRouteOperation has a name field."""
        assert hasattr(MesRouteOperation, 'name')
    
    def test_operation_model_has_sequence_field(self):
        """Test that MesRouteOperation has a sequence field."""
        assert hasattr(MesRouteOperation, 'sequence')
    
    def test_operation_model_has_route_id_field(self):
        """Test that MesRouteOperation has route_id field."""
        assert hasattr(MesRouteOperation, 'route_id')
    
    def test_operation_model_has_time_cycle_field(self):
        """Test that MesRouteOperation has time_cycle field."""
        assert hasattr(MesRouteOperation, 'time_cycle')
