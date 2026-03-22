"""Jia Tech MES TCard Module - Route Card/Process Card Management.

This module provides models for:
- mes.tcard: Route card definitions
- mes.tcard.line: Card line items
- mes.tcard.step: Execution steps
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesTcard(AbstractModel):
    """MES TCard (Route Card) model.
    
    Represents a route card for production tracking.
    
    Attributes:
        name: Card name
        lot_id: Associated production lot
        state: Card state
        step_ids: Execution steps
    """
    
    _name = 'mes.tcard'
    _description = 'Route Card'
    _table = 'mes_tcard'
    
    name = fields.Char(string='Card Name', required=True)
    
    lot_id = fields.Many2one('mes.lot', string='Production Lot', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft')
    
    route_id = fields.Many2one('mes.route', string='Route', related='lot_id.route_id')
    
    product_id = fields.Many2one('mes.product', string='Product', related='lot_id.product_id')
    product_qty = fields.Float(string='Quantity', related='lot_id.product_qty')
    
    step_ids = fields.One2many('mes.tcard.step', 'tcard_id', string='Steps', copy=True)
    
    current_step_id = fields.Many2one('mes.tcard.step', string='Current Step')
    
    step_count = fields.Integer(string='Total Steps', compute='_compute_step_count')
    completed_step_count = fields.Integer(string='Completed Steps', compute='_compute_step_count')
    
    progress_percent = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    
    date_start = fields.Datetime(string='Start Date')
    date_finish = fields.Datetime(string='Finish Date')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    company_id = fields.Many2one('res.company', string='Company', related='lot_id.company_id')
    
    note = fields.Text(string='Notes')
    
    @api.depends('step_ids')
    def _compute_step_count(self) -> None:
        """Compute step counts."""
        for card in self:
            card.step_count = len(card.step_ids)
            card.completed_step_count = len(
                card.step_ids.filtered(lambda s: s.state == 'done')
            )
    
    @api.depends('step_count', 'completed_step_count')
    def _compute_progress(self) -> None:
        """Compute progress percentage."""
        for card in self:
            if card.step_count > 0:
                card.progress_percent = (
                    card.completed_step_count / card.step_count * 100
                )
            else:
                card.progress_percent = 0.0
    
    def action_start(self) -> bool:
        """Start the route card."""
        for card in self:
            if card.state != 'draft':
                continue
            card.write({
                'state': 'in_progress',
                'date_start': fields.Datetime.now(),
            })
            first_step = card.step_ids.sorted('sequence')[0] if card.step_ids else None
            if first_step:
                card.write({'current_step_id': first_step.id})
                first_step.action_start()
        return True
    
    def action_complete(self) -> bool:
        """Complete the route card."""
        for card in self:
            if card.state != 'in_progress':
                continue
            card.write({
                'state': 'done',
                'date_finish': fields.Datetime.now(),
            })
        return True
    
    def action_cancel(self) -> bool:
        """Cancel the route card."""
        for card in self:
            card.write({'state': 'cancelled'})
        return True
    
    def action_reset(self) -> bool:
        """Reset to draft."""
        for card in self:
            card.write({'state': 'draft', 'date_start': None, 'date_finish': None})
            card.step_ids.write({'state': 'pending'})
        return True


class MesTcardStep(AbstractModel):
    """MES TCard Step model.
    
    Represents a single step in a route card.
    
    Attributes:
        name: Step name
        tcard_id: Parent route card
        sequence: Step sequence
        operation_id: Associated route operation
    """
    
    _name = 'mes.tcard.step'
    _description = 'Route Card Step'
    _table = 'mes_tcard_step'
    
    name = fields.Char(string='Step Name', required=True)
    
    tcard_id = fields.Many2one('mes.tcard', string='Route Card', required=True)
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    operation_id = fields.Many2one('mes.route.operation', string='Route Operation')
    
    workcenter_id = fields.Many2one(
        'mes.workcenter',
        string='Work Center',
        related='operation_id.workcenter_id',
    )
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('skip', 'Skipped'),
    ], string='State', default='pending')
    
    instruction = fields.Html(string='Work Instructions')
    
    check_item_ids = fields.Many2many(
        'mes.tcard.checkitem',
        'mes_tcard_step_check_rel',
        'step_id',
        'checkitem_id',
        string='Check Items',
    )
    
    check_result_ids = fields.One2many('mes.tcard.checkresult', 'step_id', string='Check Results')
    
    data_item_ids = fields.Many2many(
        'mes.edc.item',
        'mes_tcard_step_edc_rel',
        'step_id',
        'item_id',
        string='Data Items',
    )
    
    data_result_ids = fields.One2many('mes.edc.data', 'step_id', string='Data Results')
    
    duration_expected = fields.Float(string='Expected Duration (min)')
    duration_actual = fields.Float(string='Actual Duration (min)', readonly=True)
    
    date_start = fields.Datetime(string='Start Time')
    date_end = fields.Datetime(string='End Time')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    lot_id = fields.Many2one('mes.lot', string='Lot', related='tcard_id.lot_id')
    
    remark = fields.Text(string='Remark')
    
    def action_start(self) -> bool:
        """Start the step."""
        for step in self:
            if step.state not in ('pending', 'ready'):
                continue
            step.write({
                'state': 'in_progress',
                'date_start': fields.Datetime.now(),
            })
        return True
    
    def action_done(self) -> bool:
        """Complete the step."""
        for step in self:
            if step.state != 'in_progress':
                continue
            step.write({
                'state': 'done',
                'date_end': fields.Datetime.now(),
            })
            self._move_to_next_step()
        return True
    
    def action_skip(self) -> bool:
        """Skip the step."""
        for step in self:
            step.write({'state': 'skip'})
            self._move_to_next_step()
        return True
    
    def _move_to_next_step(self) -> None:
        """Move to the next step."""
        for step in self:
            next_steps = step.tcard_id.step_ids.filtered(
                lambda s: s.sequence > step.sequence and s.state == 'pending'
            ).sorted('sequence')
            if next_steps:
                next_steps[0].write({'state': 'ready'})
                step.tcard_id.write({'current_step_id': next_steps[0].id})
            else:
                step.tcard_id.action_complete()


class MesTcardCheckitem(AbstractModel):
    """MES TCard Check Item model.
    
    Defines items to check during step execution.
    """
    
    _name = 'mes.tcard.checkitem'
    _description = 'Check Item'
    _table = 'mes_tcard_checkitem'
    
    name = fields.Char(string='Item Name', required=True)
    
    check_type = fields.Selection([
        ('ok_ng', 'OK/NG'),
        ('value', 'Value Input'),
        ('yes_no', 'Yes/No'),
        ('count', 'Count'),
    ], string='Check Type', default='ok_ng')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    required = fields.Boolean(string='Required', default=True)
    
    min_value = fields.Float(string='Min Value')
    max_value = fields.Float(string='Max Value')
    
    uom_id = fields.Many2one('mes.uom', string='Unit')
    
    instruction = fields.Text(string='Instruction')


class MesTcardCheckresult(AbstractModel):
    """MES TCard Check Result model.
    
    Stores check item results.
    """
    
    _name = 'mes.tcard.checkresult'
    _description = 'Check Result'
    _table = 'mes_tcard_checkresult'
    
    step_id = fields.Many2one('mes.tcard.step', string='Step', required=True)
    
    checkitem_id = fields.Many2one('mes.tcard.checkitem', string='Check Item', required=True)
    
    result = fields.Selection([
        ('ok', 'OK'),
        ('ng', 'NG'),
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Result')
    
    value = fields.Char(string='Value')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    check_time = fields.Datetime(string='Check Time', default=fields.Datetime.now)
    
    remark = fields.Text(string='Remark')


class MesTcardTemplate(AbstractModel):
    """MES TCard Template model.
    
    Defines templates for route cards.
    """
    
    _name = 'mes.tcard.template'
    _description = 'Route Card Template'
    _table = 'mes_tcard_template'
    
    name = fields.Char(string='Template Name', required=True)
    code = fields.Char(string='Template Code', required=True)
    
    route_id = fields.Many2one('mes.route', string='Route')
    
    step_ids = fields.One2many('mes.tcard.template.step', 'template_id', string='Steps', copy=True)
    
    active = fields.Boolean(string='Active', default=True)
    
    company_id = fields.Many2one('res.company', string='Company')


class MesTcardTemplateStep(AbstractModel):
    """MES TCard Template Step model."""
    
    _name = 'mes.tcard.template.step'
    _description = 'Template Step'
    _table = 'mes_tcard_template_step'
    
    name = fields.Char(string='Step Name', required=True)
    
    template_id = fields.Many2one('mes.tcard.template', string='Template', required=True)
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    operation_id = fields.Many2one('mes.route.operation', string='Route Operation')
    
    instruction = fields.Html(string='Work Instructions')
    
    checkitem_ids = fields.Many2many(
        'mes.tcard.checkitem',
        'mes_tcard_template_step_check_rel',
        'step_id',
        'checkitem_id',
        string='Check Items',
    )
    
    data_item_ids = fields.Many2many(
        'mes.edc.item',
        'mes_tcard_template_step_edc_rel',
        'step_id',
        'item_id',
        string='Data Items',
    )
    
    duration_expected = fields.Float(string='Expected Duration (min)')
