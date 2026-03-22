"""Jia Tech MES PMS Module - Preventive Maintenance System.

This module provides models for:
- mes.maintenance.request: Maintenance requests
- mes.maintenance.schedule: Maintenance schedules
- mes.maintenance.team: Maintenance teams
- mes.spare.part: Spare parts management
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesMaintenanceRequest(AbstractModel):
    """MES Maintenance Request model.
    
    Represents a maintenance request/work order.
    
    Attributes:
        name: Request name
        equipment_id: Equipment to maintain
        request_type: Type of maintenance
        state: Request state
    """
    
    _name = 'mes.maintenance.request'
    _description = 'Maintenance Request'
    _table = 'mes_maintenance_request'
    
    name = fields.Char(string='Request Name', required=True)
    
    request_code = fields.Char(string='Request Code')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ], string='State', default='draft')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Emergency'),
    ], string='Priority', default='1')
    
    request_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('predictive', 'Predictive'),
        ('autonomous', 'Autonomous'),
        ('emergency', 'Emergency'),
        ('inspection', 'Inspection'),
    ], string='Request Type', required=True, default='corrective')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment', required=True)
    
    location = fields.Char(string='Location', related='equipment_id.location')
    
    schedule_id = fields.Many2one('mes.maintenance.schedule', string='Schedule')
    
    cause_id = fields.Many2one('mes.maintenance.cause', string='Failure Cause')
    resolution_id = fields.Many2one('mes.maintenance.resolution', string='Resolution')
    
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now)
    
    scheduled_date_start = fields.Datetime(string='Scheduled Start')
    scheduled_date_end = fields.Datetime(string='Scheduled End')
    
    actual_date_start = fields.Datetime(string='Actual Start')
    actual_date_end = fields.Datetime(string='Actual End')
    
    duration = fields.Float(string='Duration (hours)', compute='_compute_duration', store=True)
    
    team_id = fields.Many2one('mes.maintenance.team', string='Maintenance Team')
    user_id = fields.Many2one('res.users', string='Assigned To')
    
    request_user_id = fields.Many2one('res.users', string='Request By')
    
    description = fields.Text(string='Problem Description')
    solution = fields.Text(string='Solution')
    
    lot_id = fields.Many2one('mes.lot', string='Related Lot')
    
    spare_part_ids = fields.One2many('mes.maintenance.spare.part', 'request_id', string='Spare Parts Used')
    spare_cost = fields.Float(string='Spare Parts Cost', compute='_compute_cost', store=True)
    
    labor_cost = fields.Float(string='Labor Cost')
    total_cost = fields.Float(string='Total Cost', compute='_compute_cost', store=True)
    
    company_id = fields.Many2one('res.company', string='Company')
    
    active = fields.Boolean(string='Active', default=True)
    
    close_date = fields.Datetime(string='Close Date')
    close_user_id = fields.Many2one('res.users', string='Closed By')
    
    remark = fields.Text(string='Remarks')
    
    @api.depends('actual_date_start', 'actual_date_end')
    def _compute_duration(self) -> None:
        """Compute maintenance duration."""
        for request in self:
            if request.actual_date_start and request.actual_date_end:
                delta = request.actual_date_end - request.actual_date_start
                request.duration = delta.total_seconds() / 3600.0
            else:
                request.duration = 0.0
    
    @api.depends('spare_part_ids', 'labor_cost')
    def _compute_cost(self) -> None:
        """Compute total cost."""
        for request in self:
            request.spare_cost = sum(sp.partner_price for sp in request.spare_part_ids)
            request.total_cost = request.spare_cost + request.labor_cost
    
    def action_submit(self) -> bool:
        """Submit the request."""
        for request in self:
            request.write({'state': 'submitted'})
        return True
    
    def action_approve(self) -> bool:
        """Approve the request."""
        for request in self:
            request.write({'state': 'pending'})
        return True
    
    def action_assign(self, user_id: int, team_id: int | None = None) -> bool:
        """Assign the request."""
        for request in self:
            vals = {'state': 'pending', 'user_id': user_id}
            if team_id:
                vals['team_id'] = team_id
            request.write(vals)
        return True
    
    def action_start(self) -> bool:
        """Start maintenance."""
        for request in self:
            request.write({
                'state': 'in_progress',
                'actual_date_start': fields.Datetime.now(),
            })
        return True
    
    def action_done(self) -> bool:
        """Complete maintenance."""
        for request in self:
            request.write({
                'state': 'done',
                'actual_date_end': fields.Datetime.now(),
                'close_date': fields.Datetime.now(),
                'close_user_id': self.env.uid,
            })
        return True
    
    def action_cancel(self) -> bool:
        """Cancel the request."""
        for request in self:
            request.write({'state': 'cancelled'})
        return True
    
    def action_hold(self) -> bool:
        """Put on hold."""
        for request in self:
            request.write({'state': 'on_hold'})
        return True


class MesMaintenanceSchedule(AbstractModel):
    """MES Maintenance Schedule model.
    
    Defines preventive maintenance schedules.
    """
    
    _name = 'mes.maintenance.schedule'
    _description = 'Maintenance Schedule'
    _table = 'mes_maintenance_schedule'
    
    name = fields.Char(string='Schedule Name', required=True)
    
    schedule_code = fields.Char(string='Schedule Code')
    
    active = fields.Boolean(string='Active', default=True)
    
    equipment_ids = fields.Many2many(
        'mes.equipment',
        'mes_maintenance_schedule_equipment_rel',
        'schedule_id',
        'equipment_id',
        string='Equipment',
    )
    
    maintenance_type = fields.Selection([
        ('time', 'Time Based'),
        ('usage', 'Usage Based'),
        ('inspection', 'Inspection Based'),
    ], string='Schedule Type', required=True, default='time')
    
    interval_number = fields.Integer(string='Interval', default=1)
    interval_unit = fields.Selection([
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)'),
        ('hour', 'Hour(s)'),
        ('cycle', 'Cycle(s)'),
    ], string='Interval Unit', default='month')
    
    duration = fields.Float(string='Expected Duration (hours)')
    
    team_id = fields.Many2one('mes.maintenance.team', string='Default Team')
    user_id = fields.Many2one('res.users', string='Default Technician')
    
    request_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('predictive', 'Predictive'),
        ('inspection', 'Inspection'),
    ], string='Maintenance Type', default='preventive')
    
    next_date = fields.Date(string='Next Maintenance Date')
    
    last_date = fields.Date(string='Last Maintenance Date')
    
    request_id = fields.Many2one('mes.maintenance.request', string='Last Request')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    note = fields.Text(string='Notes')


class MesMaintenanceTeam(AbstractModel):
    """MES Maintenance Team model."""
    
    _name = 'mes.maintenance.team'
    _description = 'Maintenance Team'
    _table = 'mes_maintenance_team'
    
    name = fields.Char(string='Team Name', required=True)
    
    leader_id = fields.Many2one('res.users', string='Team Leader')
    
    member_ids = fields.Many2many(
        'res.users',
        'mes_maintenance_team_member_rel',
        'team_id',
        'user_id',
        string='Members',
    )
    
    active = fields.Boolean(string='Active', default=True)
    
    company_id = fields.Many2one('res.company', string='Company')
    
    request_ids = fields.One2many('mes.maintenance.request', 'team_id', string='Requests')


class MesMaintenanceCause(AbstractModel):
    """MES Maintenance Cause model.
    
    Defines failure causes for root cause analysis.
    """
    
    _name = 'mes.maintenance.cause'
    _description = 'Failure Cause'
    _table = 'mes_maintenance_cause'
    
    name = fields.Char(string='Cause Name', required=True)
    
    code = fields.Char(string='Cause Code')
    
    parent_id = fields.Many2one('mes.maintenance.cause', string='Parent Cause')
    
    child_ids = fields.One2many('mes.maintenance.cause', 'parent_id', string='Child Causes')
    
    active = fields.Boolean(string='Active', default=True)


class MesMaintenanceResolution(AbstractModel):
    """MES Maintenance Resolution model.
    
    Defines resolution types.
    """
    
    _name = 'mes.maintenance.resolution'
    _description = 'Resolution'
    _table = 'mes_maintenance_resolution'
    
    name = fields.Char(string='Resolution Name', required=True)
    
    code = fields.Char(string='Resolution Code')
    
    active = fields.Boolean(string='Active', default=True)


class MesSparePart(AbstractModel):
    """MES Spare Part model.
    
    Defines spare parts inventory.
    """
    
    _name = 'mes.spare.part'
    _description = 'Spare Part'
    _table = 'mes_spare_part'
    
    name = fields.Char(string='Part Name', required=True)
    
    code = fields.Char(string='Part Code', required=True, index=True)
    
    product_id = fields.Many2one('mes.product', string='Related Product')
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure')
    
    qty_on_hand = fields.Float(string='Qty On Hand', digits=(16, 3))
    qty_reserved = fields.Float(string='Qty Reserved', digits=(16, 3))
    qty_available = fields.Float(string='Qty Available', compute='_compute_qty', digits=(16, 3))
    
    min_qty = fields.Float(string='Min Stock Level', digits=(16, 3))
    max_qty = fields.Float(string='Max Stock Level', digits=(16, 3))
    reorder_qty = fields.Float(string='Reorder Quantity', digits=(16, 3))
    
    location_id = fields.Many2one('mes.stock.location', string='Storage Location')
    
    standard_cost = fields.Float(string='Standard Cost')
    partner_price = fields.Float(string='Partner Price')
    
    active = fields.Boolean(string='Active', default=True)
    
    company_id = fields.Many2one('res.company', string='Company')
    
    @api.depends('qty_on_hand', 'qty_reserved')
    def _compute_qty(self) -> None:
        """Compute available quantity."""
        for part in self:
            part.qty_available = part.qty_on_hand - part.qty_reserved


class MesMaintenanceSparePart(AbstractModel):
    """MES Maintenance Spare Part usage model.
    
    Tracks spare parts used in maintenance.
    """
    
    _name = 'mes.maintenance.spare.part'
    _description = 'Maintenance Spare Part'
    _table = 'mes_maintenance_spare_part'
    
    request_id = fields.Many2one('mes.maintenance.request', string='Maintenance Request', required=True)
    
    spare_part_id = fields.Many2one('mes.spare.part', string='Spare Part', required=True)
    
    quantity = fields.Float(string='Quantity', digits=(16, 3), required=True)
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure')
    
    partner_price = fields.Float(string='Unit Price', related='spare_part_id.partner_price')
    
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', digits=(16, 2))
    
    remark = fields.Text(string='Remarks')
    
    @api.depends('quantity', 'partner_price')
    def _compute_subtotal(self) -> None:
        """Compute subtotal."""
        for record in self:
            record.price_subtotal = record.quantity * record.partner_price


class MesMaintenanceMetric(AbstractModel):
    """MES Maintenance Metrics model.
    
    Tracks equipment maintenance KPIs.
    """
    
    _name = 'mes.maintenance.metric'
    _description = 'Maintenance Metric'
    _table = 'mes_maintenance_metric'
    
    name = fields.Char(string='Metric Name', required=True)
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    metric_date = fields.Date(string='Date', default=fields.Date.today)
    
    mtbf = fields.Float(string='MTBF (hours)', help='Mean Time Between Failures')
    mttr = fields.Float(string='MTTR (hours)', help='Mean Time To Repair')
    
    uptime_percent = fields.Float(string='Uptime %')
    downtime_hours = fields.Float(string='Downtime (hours)')
    
    maintenance_cost = fields.Float(string='Maintenance Cost')
    
    total_requests = fields.Integer(string='Total Requests')
    completed_requests = fields.Integer(string='Completed')
    cancelled_requests = fields.Integer(string='Cancelled')
    
    company_id = fields.Many2one('res.company', string='Company')
