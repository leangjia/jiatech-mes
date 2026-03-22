"""Jia Tech MES QMS Module - Quality Management System.

This module provides models for:
- mes.qms.defect: Defect tracking and classification
- mes.qms.ncr: Non-Conformance Report management
- mes.qms.inspection: Inspection plans and execution
- mes.qms.quality.team: Quality team management
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesDefectCategory(AbstractModel):
    """MES Defect Category model.
    
    Defines categories for classifying defects.
    """
    
    _name = 'mes.qms.defect.category'
    _description = 'Defect Category'
    _table = 'mes_qms_defect_category'
    
    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code', required=True, index=True)
    
    description = fields.Text(string='Description')
    
    defect_type = fields.Selection([
        ('product', 'Product Defect'),
        ('process', 'Process Defect'),
        ('material', 'Material Defect'),
        ('equipment', 'Equipment Defect'),
        ('other', 'Other'),
    ], string='Defect Type', required=True)
    
    severity_levels = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('cosmetic', 'Cosmetic'),
    ], string='Severity Levels', default='minor')
    
    parent_id = fields.Many2one('mes.qms.defect.category', string='Parent Category')
    child_ids = fields.One2many('mes.qms.defect.category', 'parent_id', string='Child Categories')
    
    active = fields.Boolean(string='Active', default=True)
    
    sequence = fields.Integer(string='Sequence', default=10)


class MesDefect(AbstractModel):
    """MES Defect model.
    
    Tracks defects found during production or inspection.
    """
    
    _name = 'mes.qms.defect'
    _description = 'Defect'
    _table = 'mes_qms_defect'
    
    name = fields.Char(string='Defect Name')
    code = fields.Char(string='Defect Code', required=True, index=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('root_caused', 'Root Caused'),
        ('corrective_pending', 'Corrective Action Pending'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', index=True)
    
    priority = fields.Selection([
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], string='Priority', default='medium', index=True)
    
    severity = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('cosmetic', 'Cosmetic'),
    ], string='Severity', default='minor')
    
    category_id = fields.Many2one('mes.qms.defect.category', string='Category', required=True)
    
    product_id = fields.Many2one('mes.product', string='Product')
    lot_id = fields.Many2one('mes.lot', string='Lot')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    workcenter_id = fields.Many2one('mes.workcenter', string='Work Center')
    
    defect_location = fields.Char(string='Defect Location')
    
    quantity_affected = fields.Integer(string='Quantity Affected', default=1)
    
    description = fields.Text(string='Defect Description', required=True)
    
    detected_stage = fields.Selection([
        ('incoming', 'Incoming Inspection'),
        ('production', 'In Production'),
        ('assembly', 'Assembly'),
        ('testing', 'Testing'),
        ('final_inspection', 'Final Inspection'),
        ('packing', 'Packing'),
        ('field', 'Field'),
    ], string='Detected Stage')
    
    detected_by = fields.Many2one('res.users', string='Detected By')
    detected_date = fields.Datetime(string='Detected Date', default=fields.Datetime.now)
    
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    assigned_date = fields.Datetime(string='Assigned Date')
    
    root_cause = fields.Text(string='Root Cause')
    root_cause_category = fields.Selection([
        ('man', 'Man (Human)'),
        ('machine', 'Machine (Equipment)'),
        ('method', 'Method (Process)'),
        ('material', 'Material'),
        ('measurement', 'Measurement'),
        ('environment', 'Environment'),
    ], string='Root Cause Category')
    
    corrective_action = fields.Text(string='Corrective Action')
    preventive_action = fields.Text(string='Preventive Action')
    
    ncr_id = fields.Many2one('mes.qms.ncr', string='Related NCR')
    
    cost_impact = fields.Float(string='Cost Impact', digits=(15, 2))
    
    image_ids = fields.One2many('mes.qms.defect.image', 'defect_id', string='Images')
    
    attachment_ids = fields.One2many('mes.qms.defect.attachment', 'defect_id', string='Attachments')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    closed_by = fields.Many2one('res.users', string='Closed By')
    closed_date = fields.Datetime(string='Closed Date')
    
    active = fields.Boolean(string='Active', default=True)
    
    remark = fields.Text(string='Remark')
    
    @api.model
    def create(self, vals):
        """Create defect with auto-generated code."""
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('mes.qms.defect') or 'DEF-0001'
        return super().create(vals)
    
    def action_report(self) -> bool:
        """Report the defect."""
        for defect in self:
            defect.write({'state': 'reported'})
        return True
    
    def action_investigate(self) -> bool:
        """Start investigation."""
        for defect in self:
            defect.write({
                'state': 'investigating',
                'assigned_date': fields.Datetime.now(),
            })
        return True
    
    def action_root_cause(self) -> bool:
        """Record root cause."""
        for defect in self:
            defect.write({'state': 'root_caused'})
        return True
    
    def action_corrective(self) -> bool:
        """Mark corrective action pending."""
        for defect in self:
            defect.write({'state': 'corrective_pending'})
        return True
    
    def action_close(self) -> bool:
        """Close the defect."""
        for defect in self:
            defect.write({
                'state': 'closed',
                'closed_by': self.env.uid,
                'closed_date': fields.Datetime.now(),
            })
        return True
    
    def action_reject(self) -> bool:
        """Reject the defect."""
        for defect in self:
            defect.write({'state': 'rejected'})
        return True
    
    def action_create_ncr(self) -> bool:
        """Create NCR from defect."""
        for defect in self:
            ncr_vals = {
                'defect_id': defect.id,
                'product_id': defect.product_id.id,
                'lot_id': defect.lot_id.id,
                'quantity': defect.quantity_affected,
                'description': defect.description,
            }
            ncr = self.env['mes.qms.ncr'].create(ncr_vals)
            defect.write({'ncr_id': ncr.id})
        return True


class MesNcr(AbstractModel):
    """MES Non-Conformance Report model.
    
    Manages NCR workflow from detection to closure.
    """
    
    _name = 'mes.qms.ncr'
    _description = 'Non-Conformance Report'
    _table = 'mes_qms_ncr'
    
    name = fields.Char(string='NCR Number')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('disposition_pending', 'Disposition Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', index=True)
    
    ncr_type = fields.Selection([
        ('material', 'Material Non-Conformance'),
        ('process', 'Process Non-Conformance'),
        ('product', 'Product Non-Conformance'),
        ('supplier', 'Supplier Issue'),
        ('customer', 'Customer Complaint'),
    ], string='NCR Type', required=True)
    
    severity = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    ], string='Severity', default='minor')
    
    priority = fields.Selection([
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ], string='Priority', default='normal')
    
    defect_id = fields.Many2one('mes.qms.defect', string='Related Defect')
    
    product_id = fields.Many2one('mes.product', string='Product')
    lot_id = fields.Many2one('mes.lot', string='Lot')
    
    quantity = fields.Integer(string='Quantity Affected', default=1)
    quantity_rejected = fields.Integer(string='Quantity Rejected', default=0)
    quantity_accepted = fields.Integer(string='Quantity Accepted', default=0)
    
    description = fields.Text(string='Description', required=True)
    
    detected_by = fields.Many2one('res.users', string='Detected By')
    detected_date = fields.Datetime(string='Detected Date', default=fields.Datetime.now)
    
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    assigned_date = fields.Datetime(string='Assigned Date')
    
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    review_date = fields.Datetime(string='Review Date')
    review_comments = fields.Text(string='Review Comments')
    
    disposition = fields.Selection([
        ('accept', 'Accept As Is'),
        ('rework', 'Rework'),
        ('repair', 'Repair'),
        ('scrap', 'Scrap'),
        ('return', 'Return to Supplier'),
        ('concession', 'Use Under Concession'),
        ('downgrade', 'Downgrade'),
    ], string='Disposition', index=True)
    
    disposition_by = fields.Many2one('res.users', string='Disposition By')
    disposition_date = fields.Datetime(string='Disposition Date')
    disposition_reason = fields.Text(string='Disposition Reason')
    
    scrap_value = fields.Float(string='Scrap Value', digits=(15, 2))
    rework_cost = fields.Float(string='Rework Cost', digits=(15, 2))
    total_cost = fields.Float(string='Total Cost', compute='_compute_cost')
    
    corrective_action = fields.Text(string='Corrective Action')
    corrective_due_date = fields.Date(string='Corrective Due Date')
    corrective_completion_date = fields.Date(string='Corrective Completion Date')
    corrective_verified_by = fields.Many2one('res.users', string='Verified By')
    
    preventive_action = fields.Text(string='Preventive Action')
    
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    supplier_ncr_number = fields.Char(string='Supplier NCR Number')
    
    customer_id = fields.Many2one('res.partner', string='Customer')
    customer_notification_required = fields.Boolean(string='Customer Notification Required')
    customer_notification_date = fields.Datetime(string='Customer Notification Date')
    
    containment_action = fields.Text(string='Containment Action')
    containment_completion_date = fields.Date(string='Containment Completion Date')
    
    impact_analysis = fields.Text(string='Impact Analysis')
    
    recurrence_count = fields.Integer(string='Recurrence Count', default=0)
    is_recurring = fields.Boolean(string='Is Recurring', compute='_compute_recurring')
    
    attachment_ids = fields.One2many('mes.qms.ncr.attachment', 'ncr_id', string='Attachments')
    
    action_ids = fields.One2many('mes.qms.ncr.action', 'ncr_id', string='Actions')
    action_count = fields.Integer(string='Action Count', compute='_compute_action_count')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    closed_by = fields.Many2one('res.users', string='Closed By')
    closed_date = fields.Datetime(string='Closed Date')
    
    closure_comments = fields.Text(string='Closure Comments')
    
    active = fields.Boolean(string='Active', default=True)
    
    remark = fields.Text(string='Remark')
    
    @api.depends('scrap_value', 'rework_cost')
    def _compute_cost(self) -> None:
        """Compute total cost."""
        for ncr in self:
            ncr.total_cost = (ncr.scrap_value or 0) + (ncr.rework_cost or 0)
    
    @api.depends('recurrence_count')
    def _compute_recurring(self) -> None:
        """Check if NCR is recurring."""
        for ncr in self:
            ncr.is_recurring = ncr.recurrence_count > 1
    
    @api.depends('action_ids')
    def _compute_action_count(self) -> None:
        """Compute action count."""
        for ncr in self:
            ncr.action_count = len(ncr.action_ids)
    
    @api.model
    def create(self, vals):
        """Create NCR with auto-generated name."""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mes.qms.ncr') or 'NCR-0001'
        return super().create(vals)
    
    def action_submit(self) -> bool:
        """Submit NCR for review."""
        for ncr in self:
            ncr.write({'state': 'submitted'})
        return True
    
    def action_review(self) -> bool:
        """Start review process."""
        for ncr in self:
            ncr.write({
                'state': 'under_review',
                'review_date': fields.Datetime.now(),
                'reviewer_id': self.env.uid,
            })
        return True
    
    def action_disposition(self) -> bool:
        """Request disposition."""
        for ncr in self:
            ncr.write({
                'state': 'disposition_pending',
                'disposition_by': self.env.uid,
                'disposition_date': fields.Datetime.now(),
            })
        return True
    
    def action_approve(self) -> bool:
        """Approve NCR."""
        for ncr in self:
            ncr.write({'state': 'approved'})
        return True
    
    def action_execute_disposition(self) -> bool:
        """Execute disposition."""
        for ncr in self:
            if ncr.disposition == 'scrap':
                ncr.write({'quantity_rejected': ncr.quantity})
            elif ncr.disposition == 'accept':
                ncr.write({'quantity_accepted': ncr.quantity})
            ncr.write({'state': 'in_progress'})
        return True
    
    def action_complete(self) -> bool:
        """Complete disposition."""
        for ncr in self:
            ncr.write({'state': 'completed'})
        return True
    
    def action_close(self) -> bool:
        """Close NCR."""
        for ncr in self:
            ncr.write({
                'state': 'closed',
                'closed_by': self.env.uid,
                'closed_date': fields.Datetime.now(),
            })
        return True
    
    def action_reject(self) -> bool:
        """Reject NCR."""
        for ncr in self:
            ncr.write({'state': 'rejected'})
        return True
    
    def action_cancel(self) -> bool:
        """Cancel NCR."""
        for ncr in self:
            ncr.write({'state': 'cancelled'})
        return True


class MesInspectionType(AbstractModel):
    """MES Inspection Type model.
    
    Defines types of inspections.
    """
    
    _name = 'mes.qms.inspection.type'
    _description = 'Inspection Type'
    _table = 'mes_qms_inspection_type'
    
    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Type Code', required=True, index=True)
    
    description = fields.Text(string='Description')
    
    inspection_method = fields.Selection([
        ('visual', 'Visual Inspection'),
        ('dimensional', 'Dimensional Inspection'),
        ('functional', 'Functional Test'),
        ('non_destructive', 'Non-Destructive Test'),
        ('chemical', 'Chemical Analysis'),
        ('material', 'Material Testing'),
    ], string='Inspection Method', required=True)
    
    applicable_stages = fields.Selection([
        ('incoming', 'Incoming'),
        ('in_process', 'In Process'),
        ('final', 'Final'),
        ('shipping', 'Shipping'),
    ], string='Applicable Stages', default='in_process')
    
    requires_calibration = fields.Boolean(string='Requires Calibration')
    calibration_frequency = fields.Integer(string='Calibration Frequency (days)')
    
    sampling_plan_id = fields.Many2one('mes.qms.sampling.plan', string='Sampling Plan')
    
    active = fields.Boolean(string='Active', default=True)
    
    sequence = fields.Integer(string='Sequence', default=10)


class MesSamplingPlan(AbstractModel):
    """MES Sampling Plan model.
    
    Defines sampling plans for inspections.
    """
    
    _name = 'mes.qms.sampling.plan'
    _description = 'Sampling Plan'
    _table = 'mes_qms_sampling_plan'
    
    name = fields.Char(string='Plan Name', required=True)
    code = fields.Char(string='Plan Code', required=True)
    
    type = fields.Selection([
        ('aql', 'AQL Based'),
        ('continuous', 'Continuous'),
        ('zero', 'Zero Acceptance'),
    ], string='Plan Type', required=True, default='aql')
    
    severity_level = fields.Integer(string='Severity Level', default=1)
    inspection_level = fields.Selection([
        ('general_i', 'General I'),
        ('general_ii', 'General II'),
        ('general_iii', 'General III'),
        ('special_s1', 'Special S1'),
        ('special_s2', 'Special S2'),
        ('special_s3', 'Special S3'),
        ('special_s4', 'Special S4'),
    ], string='Inspection Level', default='general_ii')
    
    aql_level = fields.Float(string='AQL Level', default=1.0)
    
    sample_size = fields.Integer(string='Sample Size')
    
    acceptance_number = fields.Integer(string='Acceptance Number (Ac)')
    rejection_number = fields.Integer(string='Rejection Number (Re)')
    
    active = fields.Boolean(string='Active', default=True)


class MesInspection(AbstractModel):
    """MES Inspection model.
    
    Manages inspection plans and execution.
    """
    
    _name = 'mes.qms.inspection'
    _description = 'Inspection'
    _table = 'mes_qms_inspection'
    
    name = fields.Char(string='Inspection Name')
    code = fields.Char(string='Inspection Code', index=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', index=True)
    
    inspection_type = fields.Selection([
        ('incoming', 'Incoming Inspection'),
        ('in_process', 'In-Process Inspection'),
        ('final', 'Final Inspection'),
        ('first_article', 'First Article Inspection (FAI)'),
        ('audit', 'Quality Audit'),
        ('audit_internal', 'Internal Audit'),
        ('audit_supplier', 'Supplier Audit'),
    ], string='Inspection Type', required=True)
    
    type_id = fields.Many2one('mes.qms.inspection.type', string='Inspection Type Reference')
    
    product_id = fields.Many2one('mes.product', string='Product')
    product_tmpl_id = fields.Many2one('mes.product.template', string='Product Template')
    
    lot_id = fields.Many2one('mes.lot', string='Lot')
    quantity = fields.Integer(string='Lot Quantity')
    
    sampling_plan_id = fields.Many2one('mes.qms.sampling.plan', string='Sampling Plan')
    sample_size = fields.Integer(string='Sample Size')
    
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional Pass'),
        ('pending', 'Pending'),
    ], string='Result', index=True)
    
    inspector_id = fields.Many2one('res.users', string='Inspector')
    inspection_date = fields.Datetime(string='Inspection Date')
    
    quantity_inspected = fields.Integer(string='Quantity Inspected', default=0)
    quantity_passed = fields.Integer(string='Quantity Passed', default=0)
    quantity_failed = fields.Integer(string='Quantity Failed', default=0)
    
    item_ids = fields.One2many('mes.qms.inspection.item', 'inspection_id', string='Inspection Items')
    item_count = fields.Integer(string='Item Count', compute='_compute_item_stats')
    pass_count = fields.Integer(string='Pass Count', compute='_compute_item_stats')
    fail_count = fields.Integer(string='Fail Count', compute='_compute_item_stats')
    
    ncr_ids = fields.One2many('mes.qms.ncr', 'inspection_id', string='NCRs')
    ncr_count = fields.Integer(string='NCR Count', compute='_compute_ncr_count')
    
    equipment_ids = fields.Many2many(
        'mes.equipment',
        'mes_qms_inspection_equipment_rel',
        'inspection_id',
        'equipment_id',
        string='Inspection Equipment',
    )
    
    workcenter_id = fields.Many2one('mes.workcenter', string='Work Center')
    
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (min)', compute='_compute_duration')
    
    remarks = fields.Text(string='Remarks')
    
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Datetime(string='Approved Date')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    attachment_ids = fields.One2many('mes.qms.inspection.attachment', 'inspection_id', string='Attachments')
    
    active = fields.Boolean(string='Active', default=True)
    
    is_first_article = fields.Boolean(string='First Article Inspection')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self) -> None:
        """Compute inspection duration."""
        for inspection in self:
            if inspection.start_time and inspection.end_time:
                delta = inspection.end_time - inspection.start_time
                inspection.duration = delta.total_seconds() / 60
            else:
                inspection.duration = 0
    
    @api.depends('item_ids')
    def _compute_item_stats(self) -> None:
        """Compute item statistics."""
        for inspection in self:
            inspection.item_count = len(inspection.item_ids)
            inspection.pass_count = len(inspection.item_ids.filtered(lambda i: i.result == 'pass'))
            inspection.fail_count = len(inspection.item_ids.filtered(lambda i: i.result == 'fail'))
    
    @api.depends('ncr_ids')
    def _compute_ncr_count(self) -> None:
        """Compute NCR count."""
        for inspection in self:
            inspection.ncr_count = len(inspection.ncr_ids)
    
    @api.model
    def create(self, vals):
        """Create inspection with auto-generated code."""
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('mes.qms.inspection') or 'INS-0001'
        return super().create(vals)
    
    def action_plan(self) -> bool:
        """Plan the inspection."""
        for inspection in self:
            inspection.write({'state': 'planned'})
        return True
    
    def action_start(self) -> bool:
        """Start inspection."""
        for inspection in self:
            inspection.write({
                'state': 'in_progress',
                'start_time': fields.Datetime.now(),
                'inspection_date': fields.Datetime.now(),
                'inspector_id': self.env.uid,
            })
        return True
    
    def action_complete(self) -> bool:
        """Complete inspection."""
        for inspection in self:
            inspection.write({
                'state': 'completed',
                'end_time': fields.Datetime.now(),
            })
        return True
    
    def action_approve(self) -> bool:
        """Approve inspection."""
        for inspection in self:
            inspection.write({
                'state': 'approved',
                'approved_by': self.env.uid,
                'approved_date': fields.Datetime.now(),
            })
        return True
    
    def action_reject(self) -> bool:
        """Reject inspection."""
        for inspection in self:
            inspection.write({'state': 'rejected'})
        return True
    
    def action_create_ncr(self) -> bool:
        """Create NCR from inspection."""
        for inspection in self:
            failed_items = inspection.item_ids.filtered(lambda i: i.result == 'fail')
            for item in failed_items:
                ncr_vals = {
                    'ncr_type': 'product',
                    'product_id': inspection.product_id.id,
                    'lot_id': inspection.lot_id.id,
                    'quantity': len(failed_items),
                    'description': f"Inspection failed: {item.name}",
                }
                self.env['mes.qms.ncr'].create(ncr_vals)
        return True


class MesInspectionItem(AbstractModel):
    """MES Inspection Item model.
    
    Defines inspection checklist items.
    """
    
    _name = 'mes.qms.inspection.item'
    _description = 'Inspection Item'
    _table = 'mes_qms_inspection_item'
    
    name = fields.Char(string='Item Name', required=True)
    code = fields.Char(string='Item Code')
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    inspection_id = fields.Many2one('mes.qms.inspection', string='Inspection', required=True)
    
    requirement = fields.Text(string='Requirement')
    
    inspection_method = fields.Selection([
        ('visual', 'Visual'),
        ('measurement', 'Measurement'),
        ('test', 'Test'),
        ('document_review', 'Document Review'),
    ], string='Inspection Method', default='visual')
    
    specification = fields.Char(string='Specification')
    tolerance_min = fields.Float(string='Min Tolerance')
    tolerance_max = fields.Float(string='Max Tolerance')
    
    measured_value = fields.Float(string='Measured Value', digits=(15, 4))
    uom_id = fields.Many2one('mes.uom', string='Unit')
    
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('na', 'Not Applicable'),
    ], string='Result', index=True)
    
    is_critical = fields.Boolean(string='Critical Item', default=False)
    
    remarks = fields.Text(string='Remarks')
    
    defect_id = fields.Many2one('mes.qms.defect', string='Related Defect')
    
    recorded_by = fields.Many2one('res.users', string='Recorded By')
    recorded_date = fields.Datetime(string='Recorded Date', default=fields.Datetime.now)
    
    attachment_ids = fields.One2many('mes.qms.inspection.item.attachment', 'item_id', string='Attachments')
    
    @api.onchange('measured_value', 'tolerance_min', 'tolerance_max')
    def _onchange_measured_value(self) -> None:
        """Auto-determine result based on measurement."""
        for item in self:
            if item.measured_value is not None:
                if item.tolerance_min is not None and item.measured_value < item.tolerance_min:
                    item.result = 'fail'
                elif item.tolerance_max is not None and item.measured_value > item.tolerance_max:
                    item.result = 'fail'
                else:
                    item.result = 'pass'


class MesQualityTeam(AbstractModel):
    """MES Quality Team model.
    
    Manages quality team members and roles.
    """
    
    _name = 'mes.qms.quality.team'
    _description = 'Quality Team'
    _table = 'mes_qms_quality_team'
    
    name = fields.Char(string='Team Name', required=True)
    code = fields.Char(string='Team Code')
    
    team_leader_id = fields.Many2one('res.users', string='Team Leader')
    
    member_ids = fields.One2many('mes.qms.quality.team.member', 'team_id', string='Members')
    
    responsible_area = fields.Selection([
        ('production', 'Production'),
        ('warehouse', 'Warehouse'),
        ('assembly', 'Assembly'),
        ('testing', 'Testing'),
        ('packing', 'Packing'),
        ('all', 'All Areas'),
    ], string='Responsible Area')
    
    active = fields.Boolean(string='Active', default=True)
    
    remark = fields.Text(string='Remark')


class MesQualityTeamMember(AbstractModel):
    """MES Quality Team Member model.
    
    Links users to quality teams with specific roles.
    """
    
    _name = 'mes.qms.quality.team.member'
    _description = 'Quality Team Member'
    _table = 'mes_qms_quality_team_member'
    
    team_id = fields.Many2one('mes.qms.quality.team', string='Team', required=True)
    
    user_id = fields.Many2one('res.users', string='User', required=True)
    
    role = fields.Selection([
        ('leader', 'Team Leader'),
        ('inspector', 'Inspector'),
        ('engineer', 'Quality Engineer'),
        ('auditor', 'Auditor'),
        ('technician', 'Technician'),
    ], string='Role', required=True)
    
    specialization = fields.Char(string='Specialization')
    
    certification_ids = fields.One2many('mes.qms.certification', 'member_id', string='Certifications')
    
    active = fields.Boolean(string='Active', default=True)
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    
    remark = fields.Text(string='Remark')


class MesCertification(AbstractModel):
    """MES Certification model.
    
    Tracks certifications for quality personnel.
    """
    
    _name = 'mes.qms.certification'
    _description = 'Certification'
    _table = 'mes_qms_certification'
    
    name = fields.Char(string='Certification Name', required=True)
    code = fields.Char(string='Certification Code')
    
    member_id = fields.Many2one('mes.qms.quality.team.member', string='Member', required=True)
    
    certification_type = fields.Selection([
        ('iso', 'ISO Certification'),
        ('quality', 'Quality Inspector'),
        ('safety', 'Safety'),
        ('technical', 'Technical'),
        ('internal', 'Internal Auditor'),
        ('lead_auditor', 'Lead Auditor'),
    ], string='Type', required=True)
    
    issuing_authority = fields.Char(string='Issuing Authority')
    
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    
    certificate_number = fields.Char(string='Certificate Number')
    
    is_valid = fields.Boolean(string='Valid', compute='_compute_valid')
    
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('expiry_date')
    def _compute_valid(self) -> None:
        """Check if certification is still valid."""
        for cert in self:
            if cert.expiry_date:
                cert.is_valid = cert.expiry_date >= fields.Date.today()
            else:
                cert.is_valid = True


class MesNcrAction(AbstractModel):
    """MES NCR Action model.
    
    Tracks actions taken for NCR resolution.
    """
    
    _name = 'mes.qms.ncr.action'
    _description = 'NCR Action'
    _table = 'mes_qms_ncr_action'
    
    name = fields.Char(string='Action Name', required=True)
    
    ncr_id = fields.Many2one('mes.qms.ncr', string='NCR', required=True)
    
    action_type = fields.Selection([
        ('containment', 'Containment'),
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('verification', 'Verification'),
    ], string='Action Type', required=True)
    
    description = fields.Text(string='Description')
    
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    
    due_date = fields.Date(string='Due Date')
    completion_date = fields.Date(string='Completion Date')
    
    state = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('overdue', 'Overdue'),
    ], string='State', default='open', index=True)
    
    is_verified = fields.Boolean(string='Verified')
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Datetime(string='Verified Date')
    
    effectiveness = fields.Selection([
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('ineffective', 'Ineffective'),
    ], string='Effectiveness')
    
    remark = fields.Text(string='Remark')
    
    def action_start(self) -> bool:
        """Start action."""
        for action in self:
            action.write({'state': 'in_progress'})
        return True
    
    def action_complete(self) -> bool:
        """Complete action."""
        for action in self:
            action.write({
                'state': 'completed',
                'completion_date': fields.Date.today(),
            })
        return True
    
    def action_verify(self) -> bool:
        """Verify action."""
        for action in self:
            action.write({
                'state': 'verified',
                'is_verified': True,
                'verified_by': self.env.uid,
                'verified_date': fields.Datetime.now(),
            })
        return True
