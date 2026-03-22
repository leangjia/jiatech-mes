# Jia Tech MES System - Modules Design Specification

## 1. Module Overview (Odoo-Inspired)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Jia Tech MES Module Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    BASE MODULES (Required)                              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │   base   │ │   base    │ │   base    │ │   base    │ │   base   │     │  │
│  │  │   user   │ │   lang    │ │   config  │ │   module  │ │   audit  │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                         CORE MES MODULES                                │  │
│  │                                                                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │   mes    │ │   mes    │ │   mes    │ │   mes    │ │   mes   │      │  │
│  │  │   wip    │ │   mm    │ │   ras    │ │   edc    │ │  tcard  │      │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                      QUALITY & MAINTENANCE MODULES                      │  │
│  │                                                                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                  │  │
│  │  │   mes    │ │   mes    │ │   mes    │ │   mes    │                  │  │
│  │  │   spc    │ │   pms    │ │   alm    │ │   qms    │                  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘                  │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Core ORM Architecture

### 2.1 Base Models (Odoo-Inspired)

```python
# Base model for all MES models
from jiatech_mes.orm import Model, fields, api
from jiatech_mes.orm.fields import Field

class BaseModel(Model):
    """Abstract base model for all models."""
    
    _abstract = True
    
    id = fields.Id()
    create_date = fields.Datetime(
        string='Created on',
        readonly=True,
        index=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        string='Created by',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='Last Updated on',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated by',
        readonly=True,
    )


class MesModel(BaseModel):
    """Base model for MES models with logging."""
    
    _abstract = True
    
    active = fields.Boolean(
        string='Active',
        default=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    
    def _log_init(self, partial=True):
        """Log model initialization."""
        pass
    
    def _register_hook(self):
        """Register model hooks."""
        pass
```

### 2.2 Model Registry

```python
# ORM Model Registry
class Registry:
    """Central registry for all models."""
    
    _registries: dict[str, 'Registry'] = {}
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.models: dict[str, type['BaseModel']] = {}
        self._sql_tables: dict = {}
        self._depends: dict = {}
    
    def __getitem__(self, name: str) -> type['BaseModel']:
        return self.models[name]
    
    def register_model(self, model_class: type['BaseModel']):
        """Register a model class."""
        if model_class._name:
            self.models[model_class._name] = model_class
    
    def get_models(self) -> list[type['BaseModel']]:
        """Get all registered models."""
        return list(self.models.values())
```

## 3. Module Specifications

### 3.1 Base Module (mes_base)

**Purpose**: Core infrastructure for all modules

```python
# Module definition
class MesBaseModule:
    """Base module providing core functionality."""
    
    name = 'mes_base'
    version = '1.0.0'
    description = 'Core MES functionality'
    depends = []
    
    def register(self, registry: Registry):
        """Register module models."""
        registry.register_model(UserModel)
        registry.register_model(CompanyModel)
        registry.register_model(SequenceModel)
```

### 3.2 WIP Module (mes_wip)

**Package Structure (Odoo-Inspired)**:
```
mes_wip/
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── lot.py              # LotModel
│   ├── route.py            # RouteModel
│   ├── operation.py         # OperationModel
│   ├── lot_operation.py    # LotOperationModel
│   └── lot_history.py      # LotHistoryModel
├── wizards/
│   ├── track_in_wizard.py
│   └── track_out_wizard.py
├── views/
│   ├── lot_views.xml
│   ├── route_views.xml
│   └── lot_templates.xml
├── security/
│   └── ir.model.access.csv
└── data/
    ├── lot_sequence.xml
    └── lot_data.xml
```

**Model Definitions**:

```python
# mes_wip/models/lot.py
class LotModel(MesModel):
    """Manufacturing Lot Model."""
    
    _name = 'mes.wip.lot'
    _description = 'Manufacturing Lot'
    _table = 'mes_wip_lot'
    _order = 'create_date desc'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Lot Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('held', 'On Hold'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('scrapped', 'Scrapped'),
    ], string='State', default='draft', readonly=True, index=True)
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='Product',
        required=True,
        tracking=True,
    )
    
    quantity = fields.Float(
        string='Quantity',
        digits=(15, 3),
        required=True,
        tracking=True,
    )
    
    uom_id = fields.Many2one(
        'mes.uom',
        string='Unit of Measure',
        required=True,
        default=lambda self: self.env.ref('mes_uom.piece'),
    )
    
    route_id = fields.Many2one(
        'mes.wip.route',
        string='Production Route',
    )
    
    bom_id = fields.Many2one(
        'mes.mm.bom',
        string='Bill of Materials',
    )
    
    move_ids = fields.One2many(
        'mes.wip.lot.operation',
        'lot_id',
        string='Operations',
    )
    
    history_ids = fields.One2many(
        'mes.wip.lot.history',
        'lot_id',
        string='History',
        readonly=True,
    )
    
    # Computed fields
    remaining_qty = fields.Float(
        string='Remaining Quantity',
        compute='_compute_remaining',
        store=True,
    )
    
    progress = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('qty_positive', 'CHECK(quantity > 0)', 'Quantity must be positive!'),
    ]
    
    # Lifecycle Methods
    @api.model
    def create(self, vals):
        """Create a new lot with auto-generated name."""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mes.wip.lot')
        return super().create(vals)
    
    @api.depends('move_ids.state', 'move_ids.quantity')
    def _compute_remaining(self):
        """Compute remaining quantity."""
        for lot in self:
            done_qty = sum(
                lot.move_ids.filtered(
                    lambda m: m.state == 'done'
                ).mapped('quantity')
            )
            lot.remaining_qty = lot.quantity - done_qty
    
    @api.depends('move_ids.state')
    def _compute_progress(self):
        """Compute completion progress."""
        for lot in self:
            if not lot.move_ids:
                lot.progress = 0
            else:
                done = len(lot.move_ids.filtered(lambda m: m.state == 'done'))
                total = len(lot.move_ids)
                lot.progress = (done / total) * 100 if total else 0
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate quantity."""
        for lot in self:
            if lot.quantity <= 0:
                raise ValidationError(_("Quantity must be positive!"))
    
    @api.onchange('product_id')
    def _onchange_product(self):
        """Update lot when product changes."""
        if self.product_id:
            self.route_id = self.product_id.route_id
            self.bom_id = self.product_id.bom_id
            self.uom_id = self.product_id.uom_id
    
    # Action Methods
    def action_create(self):
        """Create lot from draft."""
        self.write({'state': 'created'})
        return True
    
    def action_start(self):
        """Start lot production."""
        self.ensure_one()
        if self.state != 'created':
            raise UserError(_("Lot must be in 'Created' state!"))
        self.write({'state': 'in_progress'})
        return True
    
    def action_hold(self):
        """Put lot on hold."""
        self.ensure_one()
        return self.write({'state': 'held'})
    
    def action_resume(self):
        """Resume lot from hold."""
        self.ensure_one()
        self.write({'state': 'in_progress'})
        return True
    
    def action_complete(self):
        """Complete lot production."""
        self.ensure_one()
        if self.remaining_qty > 0:
            raise UserError(_("Cannot complete lot with remaining quantity!"))
        self.write({'state': 'completed'})
        return True
    
    def action_close(self):
        """Close lot."""
        self.write({'state': 'closed'})
        return True
    
    def action_scrapped(self):
        """Scrap lot."""
        self.write({'state': 'scrapped', 'active': False})
        return True
    
    # Recordset Operations
    def track_in(self, operation_id, equipment_id=None):
        """Track in to operation."""
        for lot in self:
            lot.write({
                'move_ids': [(0, 0, {
                    'operation_id': operation_id,
                    'equipment_id': equipment_id,
                    'state': 'in_progress',
                })]
            })
        return True
    
    def track_out(self):
        """Track out from operation."""
        for lot in self:
            for move in lot.move_ids.filtered(lambda m: m.state == 'in_progress'):
                move.write({'state': 'done'})
        return True


class RouteModel(MesModel):
    """Production Route Model."""
    
    _name = 'mes.wip.route'
    _description = 'Production Route'
    _table = 'mes_wip_route'
    
    name = fields.Char(string='Route Name', required=True)
    code = fields.Char(string='Code', required=True, index=True)
    operation_ids = fields.One2many(
        'mes.wip.route.operation',
        'route_id',
        string='Operations',
        copy=True,
    )
    active = fields.Boolean(default=True)


class RouteOperationModel(MesModel):
    """Route Operation Model."""
    
    _name = 'mes.wip.route.operation'
    _description = 'Route Operation'
    _table = 'mes_wip_route_operation'
    
    name = fields.Char(string='Operation Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    route_id = fields.Many2one(
        'mes.wip.route',
        string='Route',
        required=True,
        ondelete='cascade',
    )
    workcenter_id = fields.Many2one(
        'mes.ras.workcenter',
        string='Work Center',
    )
    time_cycle = fields.Float(string='Cycle Time (min)')
    yield_rate = fields.Float(string='Expected Yield %', default=100)
```

### 3.3 MM Module (mes_mm)

```python
# mes_mm/models/product.py
class ProductModel(MesModel):
    """Product Model."""
    
    _name = 'mes.mm.product'
    _description = 'Product'
    _table = 'mes_mm_product'
    
    name = fields.Char(string='Product Name', required=True)
    code = fields.Char(string='Product Code', required=True, index=True)
    type = fields.Selection([
        ('stockable', 'Stockable'),
        ('consumable', 'Consumable'),
        ('service', 'Service'),
    ], string='Product Type', default='stockable')
    
    uom_id = fields.Many2one(
        'mes.uom',
        string='Unit of Measure',
        required=True,
    )
    
    route_id = fields.Many2one(
        'mes.wip.route',
        string='Production Route',
    )
    
    bom_id = fields.Many2one(
        'mes.mm.bom',
        string='Bill of Materials',
    )
    
    tracking = fields.Selection([
        ('none', 'No Tracking'),
        ('lot', 'By Lot'),
        ('serial', 'By Serial'),
    ], string='Tracking', default='lot')


class StockQuantModel(MesModel):
    """Stock Quantity Model."""
    
    _name = 'mes.mm.stock.quant'
    _description = 'Stock Quantity'
    _table = 'mes_mm_stock_quant'
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='Product',
        required=True,
        index=True,
    )
    
    lot_id = fields.Many2one(
        'mes.wip.lot',
        string='Lot',
        ondelete='cascade',
    )
    
    location_id = fields.Many2one(
        'mes.mm.location',
        string='Location',
        required=True,
    )
    
    quantity = fields.Float(
        string='Quantity',
        digits=(15, 3),
        required=True,
    )
    
    # Computed virtual quantity
    virtual_available = fields.Float(
        string='Virtual Available',
        compute='_compute_virtual',
    )
    
    @api.depends('quantity', 'location_id.reserved_qty')
    def _compute_virtual(self):
        """Compute virtual available quantity."""
        for quant in self:
            quant.virtual_available = quant.quantity - quant.location_id.reserved_qty
```

### 3.4 SPC Module (mes_spc)

```python
# mes_spc/models/spc_job.py
class SpcJobModel(MesModel):
    """SPC Job Model."""
    
    _name = 'mes.spc.job'
    _description = 'SPC Job'
    _table = 'mes_spc_job'
    
    name = fields.Char(string='Job Name', required=True)
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='Product',
    )
    
    parameter_id = fields.Many2one(
        'mes.spc.parameter',
        string='Parameter',
        required=True,
    )
    
    chart_type = fields.Selection([
        ('xbar_r', 'X-bar R Chart'),
        ('xbar_s', 'X-bar S Chart'),
        ('imr', 'I-MR Chart'),
        ('p', 'P Chart'),
        ('np', 'NP Chart'),
        ('c', 'C Chart'),
        ('u', 'U Chart'),
    ], string='Chart Type', required=True)
    
    rule_ids = fields.Many2many(
        'mes.spc.rule',
        string='SPC Rules',
        default=lambda self: self.env.ref('mes_spc.rule_default'),
    )
    
    upper_spec_limit = fields.Float(string='USL')
    lower_spec_limit = fields.Float(string='LSL')
    upper_control_limit = fields.Float(string='UCL')
    lower_control_limit = fields.Float(string='LCL')
    
    sample_size = fields.Integer(string='Sample Size', default=5)
    subgroup_count = fields.Integer(string='Subgroup Count', default=20)
    
    active = fields.Boolean(default=True)


class SpcDataModel(MesModel):
    """SPC Data Point Model."""
    
    _name = 'mes.spc.data'
    _description = 'SPC Data'
    _table = 'mes_spc_data'
    
    job_id = fields.Many2one(
        'mes.spc.job',
        string='SPC Job',
        required=True,
        ondelete='cascade',
    )
    
    measurement_time = fields.Datetime(
        string='Measurement Time',
        default=fields.Datetime.now,
    )
    
    sample_value = fields.Float(string='Sample Value', required=True)
    
    subgroup_avg = fields.Float(string='Subgroup Average')
    subgroup_range = fields.Float(string='Subgroup Range')
    
    equipment_id = fields.Many2one(
        'mes.ras.equipment',
        string='Equipment',
    )
    
    operator_id = fields.Many2one(
        'res.users',
        string='Operator',
    )
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ooc', 'Out of Control'),
    ], string='State', default='pending')
    
    # Computed status
    is_ooc = fields.Boolean(
        string='Out of Control',
        compute='_compute_ooc',
    )
    
    @api.depends('sample_value', 'job_id.upper_control_limit', 'job_id.lower_control_limit')
    def _compute_ooc(self):
        """Check if data point is out of control."""
        for data in self:
            job = data.job_id
            if job.upper_control_limit and data.sample_value > job.upper_control_limit:
                data.is_ooc = True
            elif job.lower_control_limit and data.sample_value < job.lower_control_limit:
                data.is_ooc = True
            else:
                data.is_ooc = False
```

## 4. Module Manifest Format

```python
# __manifest__.py (Odoo-style)
{
    'name': 'MES WIP Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Work In Progress Management',
    'description': """
        Work In Progress (WIP) Management Module
        ========================================
        
        This module provides:
        - Lot tracking and management
        - Route definition and execution
        - TrackIn/TrackOut operations
        - Production progress monitoring
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.jiatech.com',
    
    'depends': [
        'mes_base',
        'mes_mm',
        'mes_ras',
    ],
    
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/lot_views.xml',
        'views/route_views.xml',
        'views/menu.xml',
        
        # Reports
        'report/lot_report.xml',
    ],
    
    'demo': [
        'demo/lot_demo.xml',
        'demo/route_demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
    
    'images': [
        'static/description/icon.png',
    ],
    
    'hooks': {
        'pre_init': 'mes_wip.hooks.pre_init',
        'post_init': 'mes_wip.hooks.post_init',
        'uninstall': 'mes_wip.hooks.uninstall',
    },
}
```

## 5. Module Dependencies

```python
# Dependency Graph
DEPENDENCIES = {
    'mes_base': [],
    
    'mes_wip': ['mes_base', 'mes_mm', 'mes_ras'],
    
    'mes_mm': ['mes_base'],
    
    'mes_ras': ['mes_base'],
    
    'mes_edc': ['mes_base', 'mes_ras'],
    
    'mes_spc': ['mes_base', 'mes_edc'],
    
    'mes_pms': ['mes_base', 'mes_ras'],
    
    'mes_alm': ['mes_base'],
    
    'mes_qms': ['mes_base', 'mes_spc'],
}
```

## 6. Module Loading Order

```python
# Loading sequence (topological sort)
LOAD_ORDER = [
    # Phase 1: Foundation
    'mes_base',
    
    # Phase 2: Core Modules
    'mes_mm',
    'mes_ras',
    'mes_wip',
    
    # Phase 3: Data Collection
    'mes_edc',
    
    # Phase 4: Quality
    'mes_spc',
    'mes_pms',
    'mes_alm',
    'mes_qms',
]
```

## 7. Inter-Module Communication

```python
# Domain Events (Odoo-style)
class LotCreatedEvent:
    """Event fired when a lot is created."""
    
    _name = 'mes.wip.lot.created'
    _namespace = 'mes.wip'
    
    def __init__(self, lot_id, product_id, quantity):
        self.lot_id = lot_id
        self.product_id = product_id
        self.quantity = quantity
        self.timestamp = datetime.now()


# Publishing events
class LotModel(MesModel):
    
    @api.model
    def create(self, vals):
        lot = super().create(vals)
        
        # Publish domain event
        self.env['bus.bus'].sendone(
            'mes.wip.lot',
            LotCreatedEvent(
                lot_id=lot.id,
                product_id=lot.product_id.id,
                quantity=lot.quantity,
            )
        )
        
        return lot


# Listening to events
class SpcModule:
    """SPC module that listens to lot events."""
    
    def _register_hooks(self):
        """Register event listeners."""
        self.env['bus.bus'].add_listener(
            'mes.wip.lot.created',
            self._on_lot_created,
        )
    
    def _on_lot_created(self, event):
        """Handle lot created event."""
        # Trigger SPC sampling
        self.env['mes.spc.job'].action_trigger_sampling(
            product_id=event.product_id,
        )
```
