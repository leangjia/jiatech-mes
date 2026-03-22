"""Jia Tech MES RAS Module - Resource/Equipment Management.

This module provides models for:
- mes.equipment: Equipment definitions
- mes.workcenter: Work center management
- mes.state: Equipment state management
- mes.capacity: Capacity management
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesEquipment(Model):
    """MES Equipment model.
    
    Represents equipment/machines in the manufacturing facility.
    
    Attributes:
        name: Equipment name
        code: Equipment code
        equipment_type: Type of equipment
        state_id: Current equipment state
        workcenter_id: Parent workcenter
    """
    
    _name = 'mes.equipment'
    _description = 'Equipment'
    _table = 'mes_equipment'
    
    name = fields.Char(string='Equipment Name', required=True)
    code = fields.Char(string='Equipment Code', required=True, index=True)
    
    equipment_type = fields.Selection([
        ('machine', 'Machine'),
        ('tool', 'Tool'),
        ('sensor', 'Sensor'),
        ('robot', 'Robot'),
        ('conveyor', 'Conveyor'),
        ('tester', 'Tester'),
        ('packer', 'Packer'),
    ], string='Equipment Type', default='machine', required=True)
    
    workcenter_id = fields.Many2one('mes.workcenter', string='Work Center')
    
    state_id = fields.Many2one('mes.equipment.state', string='Equipment State')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    category_id = fields.Many2one('mes.equipment.category', string='Category')
    
    location = fields.Char(string='Location')
    
    manufacturer = fields.Char(string='Manufacturer')
    model_number = fields.Char(string='Model Number')
    serial_number = fields.Char(string='Serial Number')
    
    date_installed = fields.Date(string='Installation Date')
    date_start_use = fields.Date(string='Start Use Date')
    
    maintenance_ids = fields.One2many('mes.maintenance.request', 'equipment_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    
    production_ids = fields.One2many('mes.lot', 'workorder_ids', string='Production Orders')
    
    capacity = fields.Float(string='Capacity', default=1.0)
    efficiency = fields.Float(string='Efficiency %', default=100.0)
    
    cost_hour = fields.Float(string='Cost per Hour')
    cost_cycle = fields.Float(string='Cost per Cycle')
    
    asset_number = fields.Char(string='Asset Number')
    location_id = fields.Many2one('mes.stock.location', string='Location')
    
    parent_id = fields.Many2one('mes.equipment', string='Parent Equipment')
    child_ids = fields.One2many('mes.equipment', 'parent_id', string='Sub Equipment')
    
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)
    
    note = fields.Text(string='Notes')
    
    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self) -> None:
        """Compute maintenance request count."""
        for equipment in self:
            equipment.maintenance_count = len(equipment.maintenance_ids)


class MesEquipmentCategory(Model):
    """MES Equipment Category model."""
    
    _name = 'mes.equipment.category'
    _description = 'Equipment Category'
    _table = 'mes_equipment_category'
    
    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Code')
    
    equipment_ids = fields.One2many('mes.equipment', 'category_id', string='Equipment')
    equipment_count = fields.Integer(string='Equipment Count', compute='_compute_count')
    
    @api.depends('equipment_ids')
    def _compute_count(self) -> None:
        """Compute equipment count."""
        for category in self:
            category.equipment_count = len(category.equipment_ids)


class MesEquipmentState(Model):
    """MES Equipment State model.
    
    Defines equipment states and their transitions.
    """
    
    _name = 'mes.equipment.state'
    _description = 'Equipment State'
    _table = 'mes_equipment_state'
    
    name = fields.Char(string='State Name', required=True)
    code = fields.Char(string='Code', required=True)
    
    state_type = fields.Selection([
        ('available', 'Available'),
        ('running', 'Running'),
        ('idle', 'Idle'),
        ('down', 'Down'),
        ('maintenance', 'Maintenance'),
    ], string='State Type', required=True)
    
    color = fields.Integer(string='Color Index', default=0)
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    equipment_ids = fields.One2many('mes.equipment', 'state_id', string='Equipment')
    
    is_start_state = fields.Boolean(string='Is Start State')
    is_end_state = fields.Boolean(string='Is End State')
    
    allow_track_in = fields.Boolean(string='Allow Track In', default=True)
    allow_track_out = fields.Boolean(string='Allow Track Out', default=True)


class MesWorkcenter(Model):
    """MES Work Center model.
    
    Represents a manufacturing work center.
    """
    
    _name = 'mes.workcenter'
    _description = 'Work Center'
    _table = 'mes_workcenter'
    
    name = fields.Char(string='Work Center Name', required=True)
    code = fields.Char(string='Code', required=True, index=True)
    
    capacity = fields.Float(string='Capacity', default=1.0)
    time_efficiency = fields.Float(string='Time Efficiency %', default=100.0)
    
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('machine', 'Machine'),
        ('mixed', 'Mixed'),
    ], string='Resource Type', default='machine')
    
    location = fields.Char(string='Location')
    
    time_start = fields.Float(string='Setup Time (min)', default=0.0)
    time_stop = fields.Float(string='Teardown Time (min)', default=0.0)
    
    costs_hour = fields.Float(string='Cost per Hour')
    costs_hour_account = fields.Char(string='Cost Account')
    
    equipment_ids = fields.One2many('mes.equipment', 'workcenter_id', string='Equipment')
    
    team_id = fields.Many2one('mes.team', string='Production Team')
    
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)
    
    resource_id = fields.Many2one('mes.resource', string='Resource')


class MesResource(Model):
    """MES Resource model.
    
    Represents resources (human, machine, material).
    """
    
    _name = 'mes.resource'
    _description = 'Resource'
    _table = 'mes_resource'
    
    name = fields.Char(string='Resource Name', required=True)
    code = fields.Char(string='Code', required=True)
    
    type = fields.Selection([
        ('user', 'Human'),
        ('machine', 'Machine'),
        ('material', 'Material'),
    ], string='Type', required=True, default='machine')
    
    capacity = fields.Float(string='Capacity', default=1.0)
    efficiency = fields.Float(string='Efficiency %', default=100.0)
    
    cost_hour = fields.Float(string='Cost per Hour')
    cost_cycle = fields.Float(string='Cost per Cycle')
    
    calendar_id = fields.Many2one('resource.calendar', string='Working Hours')
    
    active = fields.Boolean(string='Active', default=True)
    
    company_id = fields.Many2one('res.company', string='Company')


class MesResourceCalendar(Model):
    """MES Resource Calendar model.
    
    Defines working hours and availability.
    """
    
    _name = 'resource.calendar'
    _description = 'Working Hours'
    _table = 'resource_calendar'
    
    name = fields.Char(string='Calendar Name', required=True)
    
    attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', string='Attendances')
    
    leave_ids = fields.One2many('resource.calendar.leaves', 'calendar_id', string='Leaves')
    
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)


class MesResourceCalendarAttendance(Model):
    """MES Resource Calendar Attendance model."""
    
    _name = 'resource.calendar.attendance'
    _description = 'Working Time'
    _table = 'resource_calendar_attendance'
    
    name = fields.Char(string='Name')
    
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', required=True)
    
    hour_from = fields.Float(string='Start Hour', required=True)
    hour_to = fields.Float(string='End Hour', required=True)
    
    calendar_id = fields.Many2one('resource.calendar', string='Calendar', required=True)


class MesResourceCalendarLeaves(Model):
    """MES Resource Calendar Leaves model."""
    
    _name = 'resource.calendar.leaves'
    _description = 'Resource Leave'
    _table = 'resource_calendar_leaves'
    
    name = fields.Char(string='Reason', required=True)
    
    date_from = fields.Datetime(string='Start Date', required=True)
    date_to = fields.Datetime(string='End Date', required=True)
    
    calendar_id = fields.Many2one('resource.calendar', string='Calendar')
    
    resource_id = fields.Many2one('mes.resource', string='Resource')


class MesEquipmentCapability(Model):
    """MES Equipment Capability model.
    
    Defines what an equipment can do.
    """
    
    _name = 'mes.equipment.capability'
    _description = 'Equipment Capability'
    _table = 'mes_equipment_capability'
    
    name = fields.Char(string='Capability Name', required=True)
    code = fields.Char(string='Code')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment', required=True)
    
    parameter_id = fields.Many2one('mes.spc.parameter', string='Parameter')
    
    min_value = fields.Float(string='Min Value')
    max_value = fields.Float(string='Max Value')
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure')
    
    active = fields.Boolean(string='Active', default=True)


class MesEquipmentStateTransition(Model):
    """MES Equipment State Transition model."""
    
    _name = 'mes.equipment.state.transition'
    _description = 'State Transition'
    _table = 'mes_equipment_state_transition'
    
    name = fields.Char(string='Transition Name', required=True)
    
    state_from_id = fields.Many2one('mes.equipment.state', string='From State', required=True)
    state_to_id = fields.Many2one('mes.equipment.state', string='To State', required=True)
    
    trigger = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Automatic'),
        ('event', 'Event Triggered'),
    ], string='Trigger', default='manual')
    
    event_id = fields.Many2one('mes.event', string='Event')
    
    condition = fields.Char(string='Condition')


class MesEquipmentEvent(Model):
    """MES Equipment Event model."""
    
    _name = 'mes.equipment.event'
    _description = 'Equipment Event'
    _table = 'mes_equipment_event'
    
    name = fields.Char(string='Event Name', required=True)
    code = fields.Char(string='Code')
    
    event_type = fields.Selection([
        ('alarm', 'Alarm'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('error', 'Error'),
    ], string='Event Type', default='info')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment', required=True)
    
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity', default='low')
    
    message = fields.Text(string='Message')
    
    acknowledged = fields.Boolean(string='Acknowledged', default=False)
    acknowledged_by = fields.Many2one('res.users', string='Acknowledged By')
    acknowledged_time = fields.Datetime(string='Acknowledged Time')
    
    resolved = fields.Boolean(string='Resolved', default=False)
    resolved_by = fields.Many2one('res.users', string='Resolved By')
    resolved_time = fields.Datetime(string='Resolved Time')
