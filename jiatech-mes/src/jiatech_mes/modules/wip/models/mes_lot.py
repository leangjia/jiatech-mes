"""Jia Tech MES WIP Module - Work In Progress Management.

This module provides models for:
- mes.lot: Manufacturing lots/production orders
- mes.route: Production routes/operations
- mes.workcenter: Work center definitions
- mes.bom: Bills of materials
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesLot(AbstractModel):
    """MES Lot/Production Order model.
    
    Represents a manufacturing lot or production order in the MES system.
    
    Attributes:
        name: Lot/production order number
        product_id: Product being manufactured
        product_qty: Planned quantity
        product_uom_id: Unit of measure
        state: Current state (draft, confirmed, in_progress, done, cancelled)
        company_id: Manufacturing company
        date_planned_start: Planned start date
        date_planned_finished: Planned completion date
        date_start: Actual start date
        date_finished: Actual completion date
    """
    
    _name = 'mes.lot'
    _description = 'Production Lot'
    _table = 'mes_lot'
    
    name = fields.Char(string='Lot/Order Name', required=True, index=True)
    description = fields.Text(string='Description')
    
    product_id = fields.Many2one(
        'mes.product',
        string='Product',
        required=True,
    )
    product_qty = fields.Float(
        string='Planned Quantity',
        digits=(16, 3),
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        'mes.uom',
        string='Unit of Measure',
        required=True,
        default=lambda self: self.env.ref('mes.uom_unit'),
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', index=True)
    
    company_id = fields.Many2one('res.company', string='Company', required=True)
    
    date_planned_start = fields.Datetime(string='Planned Start')
    date_planned_finished = fields.Datetime(string='Planned Finish')
    date_start = fields.Datetime(string='Actual Start', readonly=True)
    date_finished = fields.Datetime(string='Actual Finish', readonly=True)
    
    bom_id = fields.Many2one('mes.bom', string='Bill of Materials')
    route_id = fields.Many2one('mes.route', string='Production Route')
    
    workorder_ids = fields.One2many('mes.workorder', 'lot_id', string='Work Orders')
    move_raw_ids = fields.One2many('mes.move', 'lot_id', string='Raw Material Moves')
    move_finished_ids = fields.One2many('mes.move', 'lot_id', string='Finished Product Moves')
    
    user_id = fields.Many2one('res.users', string='Responsible')
    team_id = fields.Many2one('mes.team', string='Production Team')
    
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Very Urgent'),
    ], string='Priority', default='0')
    
    active = fields.Boolean(string='Active', default=True)
    
    note = fields.Html(string='Notes')
    
    @api.onchange('product_id', 'product_qty')
    def _onchange_product(self) -> None:
        """Update BOM and route when product changes."""
        if self.product_id and self.product_id.bom_ids:
            self.bom_id = self.product_id.bom_ids[0]
            if self.bom_id and self.bom_id.route_ids:
                self.route_id = self.bom_id.route_ids[0]
    
    def action_confirm(self) -> bool:
        """Confirm the production order."""
        for lot in self:
            if lot.state != 'draft':
                continue
            lot.write({'state': 'confirmed'})
        return True
    
    def action_start(self) -> bool:
        """Start the production order."""
        for lot in self:
            if lot.state != 'confirmed':
                continue
            lot.write({
                'state': 'in_progress',
                'date_start': fields.Datetime.now(),
            })
        return True
    
    def action_done(self) -> bool:
        """Finish the production order."""
        for lot in self:
            if lot.state != 'in_progress':
                continue
            lot.write({
                'state': 'done',
                'date_finished': fields.Datetime.now(),
            })
        return True
    
    def action_cancel(self) -> bool:
        """Cancel the production order."""
        for lot in self:
            if lot.state in ('done', 'cancelled'):
                continue
            lot.write({'state': 'cancelled'})
        return True
    
    def action_draft(self) -> bool:
        """Reset to draft state."""
        for lot in self:
            lot.write({'state': 'draft'})
        return True


class MesWorkorder(Model):
    """MES Work Order model.
    
    Represents a single operation in a production route.
    
    Attributes:
        name: Work order name
        lot_id: Parent production lot
        workcenter_id: Work center
        operation_id: Route operation
        state: Current state
    """
    
    _name = 'mes.workorder'
    _description = 'Work Order'
    _table = 'mes_workorder'
    
    name = fields.Char(string='Work Order Name', required=True)
    
    lot_id = fields.Many2one('mes.lot', string='Production Lot', required=True)
    workcenter_id = fields.Many2one('mes.workcenter', string='Work Center', required=True)
    operation_id = fields.Many2one('mes.route.operation', string='Operation')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State', default='pending')
    
    planned_start = fields.Datetime(string='Planned Start')
    planned_end = fields.Datetime(string='Planned End')
    actual_start = fields.Datetime(string='Actual Start', readonly=True)
    actual_end = fields.Datetime(string='Actual End', readonly=True)
    
    duration_expected = fields.Float(string='Expected Duration (minutes)')
    duration = fields.Float(string='Actual Duration (minutes)', readonly=True)
    
    cycle_count = fields.Integer(string='Number of Cycles', default=1)
    capacity = fields.Float(string='Capacity per Cycle', default=1.0)
    
    user_id = fields.Many2one('res.users', string='Operator')
    team_id = fields.Many2one('mes.team', string='Team')
    
    lot_id_id = fields.Integer(string='Lot ID', related='lot_id.id')
    
    def action_start(self) -> bool:
        """Start the work order."""
        for wo in self:
            if wo.state not in ('pending', 'ready'):
                continue
            wo.write({
                'state': 'in_progress',
                'actual_start': fields.Datetime.now(),
            })
        return True
    
    def action_done(self) -> bool:
        """Finish the work order."""
        for wo in self:
            if wo.state != 'in_progress':
                continue
            wo.write({
                'state': 'done',
                'actual_end': fields.Datetime.now(),
            })
        return True
    
    def action_cancel(self) -> bool:
        """Cancel the work order."""
        for wo in self:
            wo.write({'state': 'cancel'})
        return True


class MesWorkcenter(Model):
    """MES Work Center model.
    
    Represents a manufacturing work center/machine.
    
    Attributes:
        name: Work center name
        code: Work center code
        capacity: Number of parallel operations
        time_efficiency: Time efficiency factor
    """
    
    _name = 'mes.workcenter'
    _description = 'Work Center'
    _table = 'mes_workcenter'
    
    name = fields.Char(string='Work Center Name', required=True)
    code = fields.Char(string='Code', required=True, index=True)
    
    capacity = fields.Float(string='Capacity', default=1.0)
    time_efficiency = fields.Float(string='Efficiency Factor', default=100.0)
    
    time_start = fields.Float(string='Setup Time (minutes)', default=0.0)
    time_stop = fields.Float(string='Teardown Time (minutes)', default=0.0)
    
    costs_hour = fields.Float(string='Cost per Hour')
    costs_hour_account = fields.Char(string='Cost Account')
    
    routing_line_ids = fields.One2many(
        'mes.route.operation',
        'workcenter_id',
        string='Operations',
    )
    
    resource_id = fields.Many2one('mes.resource', string='Resource')
    company_id = fields.Many2one('res.company', string='Company')
    
    active = fields.Boolean(string='Active', default=True)


class MesRoute(Model):
    """MES Production Route model.
    
    Represents a manufacturing route/process flow.
    
    Attributes:
        name: Route name
        code: Route code
        operation_ids: Operations in the route
        workcenter_ids: Required work centers
    """
    
    _name = 'mes.route'
    _description = 'Production Route'
    _table = 'mes_route'
    
    name = fields.Char(string='Route Name', required=True)
    code = fields.Char(string='Code', required=True, index=True)
    
    operation_ids = fields.One2many(
        'mes.route.operation',
        'route_id',
        string='Operations',
        copy=True,
    )
    
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company')


class MesRouteOperation(Model):
    """MES Route Operation model.
    
    Represents a single operation in a route.
    
    Attributes:
        name: Operation name
        route_id: Parent route
        workcenter_id: Required work center
        sequence: Operation sequence
        time_cycle: Standard time per cycle (minutes)
    """
    
    _name = 'mes.route.operation'
    _description = 'Route Operation'
    _table = 'mes_route_operation'
    
    name = fields.Char(string='Operation Name', required=True)
    route_id = fields.Many2one('mes.route', string='Route', required=True)
    workcenter_id = fields.Many2one('mes.workcenter', string='Work Center', required=True)
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    time_cycle = fields.Float(string='Cycle Time (minutes)')
    time_efficiency = fields.Float(string='Efficiency %', default=100.0)
    
    batch = fields.Boolean(string='Batch Production')
    batch_size = fields.Integer(string='Batch Size', default=1)
    
    instruction = fields.Html(string='Work Instructions')
    
    active = fields.Boolean(string='Active', default=True)


class MesTeam(Model):
    """MES Production Team model."""
    
    _name = 'mes.team'
    _description = 'Production Team'
    _table = 'mes_team'
    
    name = fields.Char(string='Team Name', required=True)
    leader_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.Many2many(
        'res.users',
        'mes_team_member_rel',
        'team_id',
        'user_id',
        string='Members',
    )
    active = fields.Boolean(string='Active', default=True)


class MesResource(Model):
    """MES Resource model."""
    
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
    
    active = fields.Boolean(string='Active', default=True)
