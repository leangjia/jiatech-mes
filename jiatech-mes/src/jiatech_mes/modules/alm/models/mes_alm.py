"""Jia Tech MES ALM Module - Alarm Management.

This module provides models for:
- mes.alarm: Alarm definitions
- mes.alarm.action: Alarm actions
- mes.alarm.notification: Alarm notifications
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesAlarm(AbstractModel):
    """MES Alarm model.
    
    Represents an alarm definition.
    
    Attributes:
        name: Alarm name
        code: Alarm code
        severity: Alarm severity level
        equipment_id: Related equipment
    """
    
    _name = 'mes.alarm'
    _description = 'Alarm'
    _table = 'mes_alarm'
    
    name = fields.Char(string='Alarm Name', required=True)
    
    code = fields.Char(string='Alarm Code', required=True, index=True)
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity', default='warning', required=True)
    
    alarm_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('process', 'Process'),
        ('quality', 'Quality'),
        ('safety', 'Safety'),
        ('system', 'System'),
    ], string='Alarm Type', required=True, default='equipment')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    equipment_category_id = fields.Many2one('mes.equipment.category', string='Equipment Category')
    
    active = fields.Boolean(string='Active', default=True)
    
    description = fields.Text(string='Description')
    
    cause = fields.Text(string='Possible Cause')
    
    recommended_action = fields.Text(string='Recommended Action')
    
    auto_clear = fields.Boolean(string='Auto Clear', default=False)
    auto_clear_time = fields.Integer(string='Auto Clear Time (minutes)', default=0)
    
    priority = fields.Integer(string='Priority', default=10)
    
    color = fields.Integer(string='Color Index', default=0)
    
    company_id = fields.Many2one('res.company', string='Company')


class MesAlarmHistory(AbstractModel):
    """MES Alarm History model.
    
    Stores alarm events/history.
    
    Attributes:
        alarm_id: Alarm definition
        equipment_id: Equipment that triggered alarm
        severity: Alarm severity
        state: Alarm state
    """
    
    _name = 'mes.alarm.history'
    _description = 'Alarm History'
    _table = 'mes_alarm_history'
    
    name = fields.Char(string='Alarm Name', related='alarm_id.name')
    
    alarm_id = fields.Many2one('mes.alarm', string='Alarm', required=True)
    
    code = fields.Char(string='Alarm Code', related='alarm_id.code')
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity')
    
    alarm_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('process', 'Process'),
        ('quality', 'Quality'),
        ('safety', 'Safety'),
        ('system', 'System'),
    ], string='Alarm Type')
    
    state = fields.Selection([
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('cleared', 'Cleared'),
    ], string='State', default='active')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    
    lot_id = fields.Many2one('mes.lot', string='Production Lot')
    
    message = fields.Text(string='Alarm Message')
    
    alarm_time = fields.Datetime(string='Alarm Time', default=fields.Datetime.now)
    
    acknowledged_by = fields.Many2one('res.users', string='Acknowledged By')
    acknowledged_time = fields.Datetime(string='Acknowledged Time')
    
    resolved_by = fields.Many2one('res.users', string='Resolved By')
    resolved_time = fields.Datetime(string='Resolved Time')
    
    cleared_by = fields.Many2one('res.users', string='Cleared By')
    cleared_time = fields.Datetime(string='Cleared Time')
    
    resolution = fields.Text(string='Resolution')
    
    duration = fields.Float(string='Duration (minutes)', compute='_compute_duration')
    
    action_ids = fields.One2many('mes.alarm.action', 'history_id', string='Actions Taken')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('alarm_time', 'resolved_time')
    def _compute_duration(self) -> None:
        """Compute alarm duration."""
        for history in self:
            if history.alarm_time and history.resolved_time:
                delta = history.resolved_time - history.alarm_time
                history.duration = delta.total_seconds() / 60.0
            else:
                history.duration = 0.0
    
    def action_acknowledge(self) -> bool:
        """Acknowledge the alarm."""
        for history in self:
            history.write({
                'state': 'acknowledged',
                'acknowledged_by': self.env.uid,
                'acknowledged_time': fields.Datetime.now(),
            })
            self._create_action('acknowledge')
        return True
    
    def action_resolve(self, resolution: str = '') -> bool:
        """Resolve the alarm."""
        for history in self:
            history.write({
                'state': 'resolved',
                'resolved_by': self.env.uid,
                'resolved_time': fields.Datetime.now(),
                'resolution': resolution,
            })
            self._create_action('resolve')
        return True
    
    def action_clear(self) -> bool:
        """Clear the alarm."""
        for history in self:
            history.write({
                'state': 'cleared',
                'cleared_by': self.env.uid,
                'cleared_time': fields.Datetime.now(),
            })
        return True
    
    def _create_action(self, action_type: str) -> None:
        """Create action record."""
        for history in self:
            self.env['mes.alarm.action'].create({
                'history_id': history.id,
                'action_type': action_type,
                'user_id': self.env.uid,
                'action_time': fields.Datetime.now(),
            })


class MesAlarmAction(AbstractModel):
    """MES Alarm Action model.
    
    Records actions taken on alarms.
    """
    
    _name = 'mes.alarm.action'
    _description = 'Alarm Action'
    _table = 'mes_alarm_action'
    
    history_id = fields.Many2one('mes.alarm.history', string='Alarm History', required=True)
    
    action_type = fields.Selection([
        ('acknowledge', 'Acknowledge'),
        ('resolve', 'Resolve'),
        ('comment', 'Comment'),
        ('escalate', 'Escalate'),
        ('transfer', 'Transfer'),
    ], string='Action Type', required=True)
    
    user_id = fields.Many2one('res.users', string='Performed By', required=True)
    
    action_time = fields.Datetime(string='Action Time', default=fields.Datetime.now)
    
    note = fields.Text(string='Notes')
    
    to_user_id = fields.Many2one('res.users', string='To User')
    to_team_id = fields.Many2one('mes.team', string='To Team')


class MesAlarmRule(AbstractModel):
    """MES Alarm Rule model.
    
    Defines rules for alarm generation.
    """
    
    _name = 'mes.alarm.rule'
    _description = 'Alarm Rule'
    _table = 'mes_alarm_rule'
    
    name = fields.Char(string='Rule Name', required=True)
    
    active = fields.Boolean(string='Active', default=True)
    
    condition_type = fields.Selection([
        ('spc', 'SPC Alarm'),
        ('equipment', 'Equipment State'),
        ('process', 'Process Parameter'),
        ('schedule', 'Scheduled'),
    ], string='Condition Type', required=True)
    
    alarm_id = fields.Many2one('mes.alarm', string='Alarm', required=True)
    
    spc_job_id = fields.Many2one('mes.spc.job', string='SPC Job')
    
    equipment_id = fields.Many2one('mes.equipment', string='Equipment')
    equipment_state_id = fields.Many2one('mes.equipment.state', string='Equipment State')
    
    parameter_id = fields.Many2one('mes.spc.parameter', string='Parameter')
    
    condition = fields.Char(string='Condition')
    
    delay_seconds = fields.Integer(string='Delay (seconds)', default=0)
    
    auto_action = fields.Selection([
        ('none', 'None'),
        ('notify', 'Notify'),
        ('email', 'Email'),
        ('sms', 'SMS'),
    ], string='Auto Action', default='none')
    
    notify_user_ids = fields.Many2many(
        'res.users',
        'mes_alarm_rule_user_rel',
        'rule_id',
        'user_id',
        string='Notify Users',
    )
    
    notify_team_ids = fields.Many2many(
        'mes.team',
        'mes_alarm_rule_team_rel',
        'rule_id',
        'team_id',
        string='Notify Teams',
    )
    
    company_id = fields.Many2one('res.company', string='Company')


class MesAlarmNotification(AbstractModel):
    """MES Alarm Notification model.
    
    Stores alarm notifications.
    """
    
    _name = 'mes.alarm.notification'
    _description = 'Alarm Notification'
    _table = 'mes_alarm_notification'
    
    history_id = fields.Many2one('mes.alarm.history', string='Alarm History', required=True)
    
    channel = fields.Selection([
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('wechat', 'WeChat'),
    ], string='Channel', required=True)
    
    recipient_ids = fields.Many2many(
        'res.users',
        'mes_alarm_notification_user_rel',
        'notification_id',
        'user_id',
        string='Recipients',
    )
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ], string='State', default='pending')
    
    subject = fields.Char(string='Subject')
    message = fields.Text(string='Message')
    
    sent_time = fields.Datetime(string='Sent Time')
    read_time = fields.Datetime(string='Read Time')
    
    error_message = fields.Text(string='Error Message')
    
    create_date = fields.Datetime(string='Create Date', readonly=True)


class MesAlarmEscalation(AbstractModel):
    """MES Alarm Escalation model.
    
    Defines alarm escalation paths.
    """
    
    _name = 'mes.alarm.escalation'
    _description = 'Alarm Escalation'
    _table = 'mes_alarm_escalation'
    
    name = fields.Char(string='Escalation Name', required=True)
    
    active = fields.Boolean(string='Active', default=True)
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity', required=True)
    
    escalation_level = fields.Integer(string='Escalation Level', default=1)
    
    time_threshold = fields.Integer(string='Time Threshold (minutes)', required=True)
    
    action_type = fields.Selection([
        ('notify', 'Notify'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('assign', 'Assign'),
        ('close', 'Auto Close'),
    ], string='Action', required=True)
    
    user_id = fields.Many2one('res.users', string='Assign To')
    team_id = fields.Many2one('mes.team', string='Assign To Team')
    
    company_id = fields.Many2one('res.company', string='Company')
