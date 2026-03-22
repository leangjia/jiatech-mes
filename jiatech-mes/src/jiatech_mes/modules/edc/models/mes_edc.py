"""Jia Tech MES EDC Module - Equipment Data Collection.

This module provides models for:
- mes.edc.item: Data collection item definitions
- mes.edc.collection: Data collection sessions
- mes.edc.data: Collected data points
- mes.edc.rule: Collection rules
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesEdcItem(AbstractModel):
    """MES EDC Item model.
    
    Defines what data to collect from equipment.
    
    Attributes:
        name: Item name
        code: Item code
        data_type: Type of data (numeric, text, etc.)
        equipment_id: Associated equipment
    """
    
    _name = 'mes.edc.item'
    _description = 'EDC Item'
    _table = 'mes_edc_item'
    
    name = fields.Char(string='Item Name', required=True)
    code = fields.Char(string='Item Code', required=True, index=True)
    
    data_type = fields.Selection([
        ('numeric', 'Numeric'),
        ('text', 'Text'),
        ('boolean', 'Boolean'),
        ('selection', 'Selection'),
        ('datetime', 'Date/Time'),
    ], string='Data Type', default='numeric', required=True)
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    equipment_category_id = fields.Many2one('mes.equipment.category', string='Equipment Category')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure')
    
    minimum_value = fields.Float(string='Minimum Value')
    maximum_value = fields.Float(string='Maximum Value')
    
    default_value = fields.Char(string='Default Value')
    
    required = fields.Boolean(string='Required', default=False)
    
    input_type = fields.Selection([
        ('text', 'Text Input'),
        ('number', 'Number Input'),
        ('select', 'Dropdown'),
        ('checkbox', 'Checkbox'),
        ('datetime', 'Date/Time Picker'),
    ], string='Input Type', default='number')
    
    selection_values = fields.Text(string='Selection Values (JSON)')
    
    active = fields.Boolean(string='Active', default=True)
    
    help_text = fields.Text(string='Help Text')
    
    parameter_id = fields.Many2one('mes.spc.parameter', string='SPC Parameter')


class MesEdcCollection(AbstractModel):
    """MES EDC Collection model.
    
    Represents a data collection session/event.
    
    Attributes:
        name: Collection name
        collection_type: Type of collection
        equipment_id: Equipment being collected from
        lot_id: Associated lot
    """
    
    _name = 'mes.edc.collection'
    _description = 'EDC Collection'
    _table = 'mes_edc_collection'
    
    name = fields.Char(string='Collection Name', required=True)
    
    collection_type = fields.Selection([
        ('manual', 'Manual Entry'),
        ('automatic', 'Automatic'),
        ('semi_auto', 'Semi-Automatic'),
    ], string='Collection Type', default='manual', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    lot_id = fields.Many2one('mes.lot', string='Production Lot')
    workorder_id = fields.Many2one('mes.workorder', string='Work Order')
    
    operation_id = fields.Many2one('mes.route.operation', string='Operation')
    
    collection_time = fields.Datetime(string='Collection Time')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    data_item_ids = fields.Many2many(
        'mes.edc.item',
        'mes_edc_collection_item_rel',
        'collection_id',
        'item_id',
        string='Data Items',
    )
    
    data_ids = fields.One2many('mes.edc.data', 'collection_id', string='Collected Data')
    
    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one('res.company', string='Company')


class MesEdcData(AbstractModel):
    """MES EDC Data model.
    
    Stores individual collected data points.
    
    Attributes:
        collection_id: Parent collection
        item_id: Data item definition
        value: Collected value
    """
    
    _name = 'mes.edc.data'
    _description = 'EDC Data'
    _table = 'mes_edc_data'
    
    collection_id = fields.Many2one('mes.edc.collection', string='Collection', required=True)
    
    item_id = fields.Many2one('mes.edc.item', string='Data Item', required=True)
    
    value = fields.Char(string='Value')
    numeric_value = fields.Float(string='Numeric Value')
    
    sample_time = fields.Datetime(string='Sample Time', default=fields.Datetime.now)
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    lot_id = fields.Many2one('mes.lot', string='Production Lot')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    is_abnormal = fields.Boolean(string='Abnormal', default=False)
    abnormal_reason = fields.Text(string='Abnormal Reason')
    
    remark = fields.Text(string='Remark')


class MesEdcRule(AbstractModel):
    """MES EDC Collection Rule model.
    
    Defines when and how to collect data.
    """
    
    _name = 'mes.edc.rule'
    _description = 'EDC Collection Rule'
    _table = 'mes_edc_rule'
    
    name = fields.Char(string='Rule Name', required=True)
    code = fields.Char(string='Rule Code', required=True)
    
    active = fields.Boolean(string='Active', default=True)
    
    collection_mode = fields.Selection([
        ('time_based', 'Time Based'),
        ('event_based', 'Event Based'),
        ('quantity_based', 'Quantity Based'),
    ], string='Collection Mode', default='time_based')
    
    interval_minutes = fields.Integer(string='Interval (minutes)', default=60)
    
    trigger_event = fields.Char(string='Trigger Event')
    
    quantity_trigger = fields.Float(string='Quantity Trigger')
    
    item_ids = fields.Many2many(
        'mes.edc.item',
        'mes_edc_rule_item_rel',
        'rule_id',
        'item_id',
        string='Data Items',
    )
    
    equipment_ids = fields.Many2many(
        'mes.equipment',
        'mes_edc_rule_equipment_rel',
        'rule_id',
        'equipment_id',
        string='Equipment',
    )
    
    equipment_category_ids = fields.Many2many(
        'mes.equipment.category',
        'mes_edc_rule_category_rel',
        'rule_id',
        'category_id',
        string='Equipment Categories',
    )
    
    company_id = fields.Many2one('res.company', string='Company')


class MesEdcMapping(AbstractModel):
    """MES EDC Equipment Mapping model.
    
    Maps EDC items to equipment parameters.
    """
    
    _name = 'mes.edc.mapping'
    _description = 'EDC Mapping'
    _table = 'mes_edc_mapping'
    
    name = fields.Char(string='Mapping Name', required=True)
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment', required=True)
    
    item_id = fields.Many2one('mes.edc.item', string='EDC Item', required=True)
    
    equipment_param = fields.Char(string='Equipment Parameter')
    
    address = fields.Char(string='Address/Register')
    
    protocol = fields.Selection([
        ('secsgem', 'SECS/GEM'),
        ('opcua', 'OPC-UA'),
        ('modbus', 'Modbus'),
        ('custom', 'Custom'),
    ], string='Protocol', default='custom')
    
    active = fields.Boolean(string='Active', default=True)
