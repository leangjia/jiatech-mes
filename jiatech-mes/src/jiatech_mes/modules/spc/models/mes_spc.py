"""Jia Tech MES SPC Module - Statistical Process Control.

This module provides models for:
- mes.spc.job: SPC job configuration
- mes.spc.parameter: SPC parameters
- mes.spc.rule: SPC control rules
- mes.spc.data: SPC data points
- mes.spc.chart: Control chart data
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesSpcParameter(AbstractModel):
    """MES SPC Parameter model.
    
    Defines parameters for SPC monitoring.
    
    Attributes:
        name: Parameter name
        code: Parameter code
        uom_id: Unit of measure
    """
    
    _name = 'mes.spc.parameter'
    _description = 'SPC Parameter'
    _table = 'mes_spc_parameter'
    
    name = fields.Char(string='Parameter Name', required=True)
    code = fields.Char(string='Parameter Code', required=True, index=True)
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    description = fields.Text(string='Description')
    
    active = fields.Boolean(string='Active', default=True)


class MesSpcRule(AbstractModel):
    """MES SPC Control Rule model.
    
    Defines control chart rules for SPC.
    """
    
    _name = 'mes.spc.rule'
    _description = 'SPC Control Rule'
    _table = 'mes_spc_rule'
    
    name = fields.Char(string='Rule Name', required=True)
    code = fields.Char(string='Rule Code', required=True)
    
    rule_number = fields.Integer(string='Rule Number', help='Western Electric rule number (1-8)')
    
    description = fields.Text(string='Description')
    
    violation_type = fields.Selection([
        ('zone_a', 'Zone A Violation'),
        ('zone_b', 'Zone B Violation'),
        ('zone_c', 'Zone C Violation'),
        ('run', 'Run Violation'),
        ('_pattern', 'Pattern Violation'),
    ], string='Violation Type')
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Severity', default='warning')
    
    active = fields.Boolean(string='Active', default=True)
    
    active_rule = fields.Boolean(string='Active by Default', default=True)


class MesSpcJob(AbstractModel):
    """MES SPC Job model.
    
    Defines an SPC monitoring job.
    
    Attributes:
        name: Job name
        chart_type: Type of control chart
        parameter_id: SPC parameter to monitor
    """
    
    _name = 'mes.spc.job'
    _description = 'SPC Job'
    _table = 'mes_spc_job'
    
    name = fields.Char(string='Job Name', required=True)
    code = fields.Char(string='Job Code')
    
    active = fields.Boolean(string='Active', default=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('stopped', 'Stopped'),
    ], string='State', default='draft')
    
    chart_type = fields.Selection([
        ('xbar_r', 'X-bar R Chart'),
        ('xbar_s', 'X-bar S Chart'),
        ('imr', 'Individual Moving Range (I-MR)'),
        ('mr', 'Moving Range (MR)'),
        ('p', 'P Chart'),
        ('np', 'NP Chart'),
        ('c', 'C Chart'),
        ('u', 'U Chart'),
    ], string='Chart Type', required=True, default='imr')
    
    parameter_id = fields.Many2one('mes.spc.parameter', string='Parameter', required=True)
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    product_id = fields.Many2one('mes.product', string='Product')
    
    operation_id = fields.Many2one('mes.route.operation', string='Operation')
    
    sample_size = fields.Integer(string='Sample Size', default=1)
    subgroup_count = fields.Integer(string='Subgroup Count', default=25)
    
    upper_spec_limit = fields.Float(string='USL (Upper Spec Limit)')
    lower_spec_limit = fields.Float(string='LSL (Lower Spec Limit)')
    target_value = fields.Float(string='Target')
    
    upper_control_limit = fields.Float(string='UCL (Upper Control Limit)')
    lower_control_limit = fields.Float(string='LCL (Lower Control Limit)')
    
    control_limit_source = fields.Selection([
        ('auto', 'Auto Calculate'),
        ('manual', 'Manual'),
    ], string='Control Limit Source', default='auto')
    
    sigma_level = fields.Float(string='Sigma Level', default=3.0)
    
    rule_ids = fields.Many2many(
        'mes.spc.rule',
        'mes_spc_job_rule_rel',
        'job_id',
        'rule_id',
        string='Control Rules',
    )
    
    data_ids = fields.One2many('mes.spc.data', 'job_id', string='Data Points')
    data_count = fields.Integer(string='Data Count', compute='_compute_data_count')
    
    center_line = fields.Float(string='Center Line', compute='_compute_control_limits')
    
    ooc_count = fields.Integer(string='OOC Count', compute='_compute_ooc_count')
    ooc_percent = fields.Float(string='OOC %', compute='_compute_ooc_count')
    
    alarm_ids = fields.One2many('mes.spc.alarm', 'job_id', string='Alarms')
    alarm_count = fields.Integer(string='Alarm Count', compute='_compute_alarm_count')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    @api.depends('data_ids')
    def _compute_data_count(self) -> None:
        """Compute data point count."""
        for job in self:
            job.data_count = len(job.data_ids)
    
    @api.depends('data_ids', 'sigma_level')
    def _compute_control_limits(self) -> None:
        """Compute control limits from data."""
        for job in self:
            if not job.data_ids or job.control_limit_source != 'auto':
                continue
            
            values = [d.sample_value for d in job.data_ids if d.sample_value is not None]
            if not values:
                continue
            
            import statistics
            mean = statistics.mean(values)
            if len(values) > 1:
                std_dev = statistics.stdev(values)
            else:
                std_dev = 0
            
            job.center_line = mean
            job.upper_control_limit = mean + (self.sigma_level * std_dev)
            job.lower_control_limit = mean - (self.sigma_level * std_dev)
    
    @api.depends('data_ids', 'upper_control_limit', 'lower_control_limit')
    def _compute_ooc_count(self) -> None:
        """Compute out of control count."""
        for job in self:
            ooc = 0
            for data in job.data_ids:
                if (job.upper_control_limit and data.sample_value > job.upper_control_limit) or \
                   (job.lower_control_limit and data.sample_value < job.lower_control_limit):
                    ooc += 1
            job.ooc_count = ooc
            job.ooc_percent = (ooc / len(job.data_ids) * 100) if job.data_ids else 0.0
    
    @api.depends('alarm_ids')
    def _compute_alarm_count(self) -> None:
        """Compute alarm count."""
        for job in self:
            job.alarm_count = len(job.alarm_ids.filtered(lambda a: a.state == 'active'))
    
    def action_start(self) -> bool:
        """Start SPC monitoring."""
        for job in self:
            job.write({'state': 'running'})
        return True
    
    def action_pause(self) -> bool:
        """Pause SPC monitoring."""
        for job in self:
            job.write({'state': 'paused'})
        return True
    
    def action_stop(self) -> bool:
        """Stop SPC monitoring."""
        for job in self:
            job.write({'state': 'stopped'})
        return True


class MesSpcData(AbstractModel):
    """MES SPC Data Point model.
    
    Stores individual data points for SPC analysis.
    """
    
    _name = 'mes.spc.data'
    _description = 'SPC Data'
    _table = 'mes_spc_data'
    
    name = fields.Char(string='Data Name')
    
    job_id = fields.Many2one('mes.spc.job', string='SPC Job', required=True, index=True)
    
    sample_time = fields.Datetime(string='Sample Time', default=fields.Datetime.now)
    
    sample_value = fields.Float(string='Sample Value', required=True, digits=(16, 6))
    
    subgroup_id = fields.Many2one('mes.spc.subgroup', string='Subgroup')
    subgroup_index = fields.Integer(string='Subgroup Index')
    
    subgroup_avg = fields.Float(string='Subgroup Average', compute='_compute_subgroup_stats')
    subgroup_range = fields.Float(string='Subgroup Range', compute='_compute_subgroup_stats')
    subgroup_std = fields.Float(string='Subgroup Std Dev', compute='_compute_subgroup_stats')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    lot_id = fields.Many2one('mes.lot', string='Production Lot')
    
    operator_id = fields.Many2one('res.users', string='Operator')
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ooc', 'Out of Control'),
    ], string='State', default='pending')
    
    is_ooc = fields.Boolean(string='Out of Control', compute='_compute_ooc')
    is_oos = fields.Boolean(string='Out of Spec', compute='_compute_ooc')
    
    rule_violation_ids = fields.Many2many(
        'mes.spc.rule',
        'mes_spc_data_rule_rel',
        'data_id',
        'rule_id',
        string='Rule Violations',
    )
    
    remark = fields.Text(string='Remark')
    
    @api.depends('subgroup_id')
    def _compute_subgroup_stats(self) -> None:
        """Compute subgroup statistics."""
        for data in self:
            if data.subgroup_id:
                values = [d.sample_value for d in data.subgroup_id.data_ids if d.sample_value]
                if values:
                    import statistics
                    data.subgroup_avg = statistics.mean(values)
                    if len(values) > 1:
                        data.subgroup_range = max(values) - min(values)
                        data.subgroup_std = statistics.stdev(values)
    
    @api.depends('sample_value', 'job_id.upper_control_limit', 'job_id.lower_control_limit',
                 'job_id.upper_spec_limit', 'job_id.lower_spec_limit')
    def _compute_ooc(self) -> None:
        """Check if data point is out of control/spec."""
        for data in self:
            job = data.job_id
            
            data.is_ooc = False
            data.is_ooc = (
                (job.upper_control_limit and data.sample_value > job.upper_control_limit) or
                (job.lower_control_limit and data.sample_value < job.lower_control_limit)
            )
            
            data.is_oos = False
            data.is_oos = (
                (job.upper_spec_limit and data.sample_value > job.upper_spec_limit) or
                (job.lower_spec_limit and data.sample_value < job.lower_spec_limit)
            )
            
            if data.is_ooc:
                data.state = 'ooc'


class MesSpcSubgroup(AbstractModel):
    """MES SPC Subgroup model.
    
    Groups data points into subgroups for analysis.
    """
    
    _name = 'mes.spc.subgroup'
    _description = 'SPC Subgroup'
    _table = 'mes_spc_subgroup'
    
    name = fields.Char(string='Subgroup Name')
    
    job_id = fields.Many2one('mes.spc.job', string='SPC Job', required=True)
    
    sequence = fields.Integer(string='Sequence')
    
    sample_time = fields.Datetime(string='Sample Time', default=fields.Datetime.now)
    
    data_ids = fields.One2many('mes.spc.data', 'subgroup_id', string='Data Points')
    
    subgroup_size = fields.Integer(string='Size', compute='_compute_stats')
    subgroup_avg = fields.Float(string='Average', compute='_compute_stats')
    subgroup_range = fields.Float(string='Range', compute='_compute_stats')
    subgroup_std = fields.Float(string='Std Dev', compute='_compute_stats')
    
    is_ooc = fields.Boolean(string='OOC', compute='_compute_stats')
    
    @api.depends('data_ids')
    def _compute_stats(self) -> None:
        """Compute subgroup statistics."""
        import statistics
        
        for subgroup in self:
            values = [d.sample_value for d in subgroup.data_ids if d.sample_value is not None]
            subgroup.subgroup_size = len(values)
            
            if values:
                subgroup.subgroup_avg = statistics.mean(values)
                if len(values) > 1:
                    subgroup.subgroup_range = max(values) - min(values)
                    subgroup.subgroup_std = statistics.stdev(values)
                
                job = subgroup.job_id
                if job.upper_control_limit or job.lower_control_limit:
                    subgroup.is_ooc = any(
                        (job.upper_control_limit and v > job.upper_control_limit) or
                        (job.lower_control_limit and v < job.lower_control_limit)
                        for v in values
                    )


class MesSpcAlarm(AbstractModel):
    """MES SPC Alarm model.
    
    Stores SPC alarms triggered by rule violations.
    """
    
    _name = 'mes.spc.alarm'
    _description = 'SPC Alarm'
    _table = 'mes_spc_alarm'
    
    name = fields.Char(string='Alarm Name')
    
    job_id = fields.Many2one('mes.spc.job', string='SPC Job', required=True)
    
    alarm_type = fields.Selection([
        ('ooc', 'Out of Control'),
        ('oos', 'Out of Spec'),
        ('rule_violation', 'Rule Violation'),
        ('trend', 'Trend Violation'),
    ], string='Alarm Type', required=True)
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Severity', default='warning')
    
    state = fields.Selection([
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ], string='State', default='active')
    
    data_id = fields.Many2one('mes.spc.data', string='Related Data')
    
    rule_id = fields.Many2one('mes.spc.rule', string='Violated Rule')
    
    message = fields.Text(string='Alarm Message')
    
    alarm_time = fields.Datetime(string='Alarm Time', default=fields.Datetime.now)
    
    acknowledged_by = fields.Many2one('res.users', string='Acknowledged By')
    acknowledged_time = fields.Datetime(string='Acknowledged Time')
    
    resolved_by = fields.Many2one('res.users', string='Resolved By')
    resolved_time = fields.Datetime(string='Resolved Time')
    
    resolution = fields.Text(string='Resolution')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    def action_acknowledge(self) -> bool:
        """Acknowledge the alarm."""
        for alarm in self:
            alarm.write({
                'state': 'acknowledged',
                'acknowledged_by': self.env.uid,
                'acknowledged_time': fields.Datetime.now(),
            })
        return True
    
    def action_resolve(self, resolution: str = '') -> bool:
        """Resolve the alarm."""
        for alarm in self:
            alarm.write({
                'state': 'resolved',
                'resolved_by': self.env.uid,
                'resolved_time': fields.Datetime.now(),
                'resolution': resolution,
            })
        return True


class MesSpcCapability(AbstractModel):
    """MES SPC Capability Study model.
    
    Stores capability analysis results (Cpk, Ppk, etc.).
    """
    
    _name = 'mes.spc.capability'
    _description = 'Capability Study'
    _table = 'mes_spc_capability'
    
    name = fields.Char(string='Study Name', required=True)
    
    job_id = fields.Many2one('mes.spc.job', string='SPC Job', required=True)
    
    study_date = fields.Date(string='Study Date', default=fields.Date.today)
    
    sample_size = fields.Integer(string='Sample Size')
    
    mean = fields.Float(string='Mean')
    std_dev = fields.Float(string='Std Dev')
    
    usl = fields.Float(string='USL')
    lsl = fields.Float(string='LSL')
    target = fields.Float(string='Target')
    
    cp = fields.Float(string='Cp', compute='_compute_capability')
    cpk = fields.Float(string='Cpk', compute='_compute_capability')
    pp = fields.Float(string='Pp', compute='_compute_capability')
    ppk = fields.Float(string='Ppk', compute='_compute_capability')
    
    cpu = fields.Float(string='Cpu', compute='_compute_capability')
    cpl = fields.Float(string='Cpl', compute='_compute_capability')
    
    is_ capable = fields.Boolean(string='Capable', compute='_compute_capability')
    
    remark = fields.Text(string='Remark')
    
    @api.depends('mean', 'std_dev', 'usl', 'lsl')
    def _compute_capability(self) -> None:
        """Compute capability indices."""
        for cap in self:
            if not cap.std_dev or cap.std_dev == 0:
                continue
            
            sigma = cap.std_dev
            six_sigma = 6 * sigma
            
            if cap.usl:
                cap.cpu = (cap.usl - cap.mean) / (3 * sigma)
            if cap.lsl:
                cap.cpl = (cap.mean - cap.lsl) / (3 * sigma)
            
            if cap.usl and cap.lsl:
                cap.cp = (cap.usl - cap.lsl) / six_sigma
                cap.cpk = min(cap.cpu, cap.cpl) if cap.cpu and cap.cpl else 0
            elif cap.usl:
                cap.cp = 0
                cap.cpk = cap.cpu
            elif cap.lsl:
                cap.cp = 0
                cap.cpk = cap.cpl
            else:
                cap.cp = 0
                cap.cpk = 0
            
            cap.pp = cap.cp
            cap.ppk = cap.cpk
            
            cap.is_capable = cap.cpk >= 1.33 if cap.cpk else False
