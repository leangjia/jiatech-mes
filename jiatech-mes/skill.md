# Jia Tech MES System - Skills Definition

## 1. Overview

This document defines the specialized skills required for developing the Jia Tech MES (Manufacturing Execution System). Inspired by Odoo 18's elegant architecture, our system leverages Python's advanced features for a clean, extensible design.

## 2. Core Technology Stack

### 2.1 Backend Development

| Skill | Level | Description |
|-------|-------|-------------|
| **Python 3.11+** | Expert | Primary language, type hints, dataclasses, metaclasses |
| **FastAPI** | Expert | Modern async web framework with OpenAPI auto-generation |
| **Custom ORM** | Expert | Odoo-inspired ORM with metaclass-driven model registration |
| **SQLAlchemy 2.x** | Advanced | SQL toolkit with async support (core DB layer) |
| **PostgreSQL** | Expert | Primary database, advanced features (JSON, partitioning, pgvector) |
| **Redis** | Advanced | Caching, session management, distributed locks |
| **RabbitMQ** | Advanced | Message queue for async operations |
| **Pydantic 2.x** | Expert | Data validation, settings management |

### 2.2 Python Advanced Features (Odoo-Inspired)

| Feature | Level | Description |
|---------|-------|-------------|
| **Metaclasses** | Expert | Model registration, declarative patterns |
| **Descriptors** | Advanced | Custom field implementation |
| **Decorators** | Expert | API decorators (@model, @depends, @onchange, @constrains) |
| **Context Managers** | Advanced | Transaction management, resource cleanup |
| **DataClasses/Frozen** | Advanced | Immutable DTOs, value objects |
| **Protocols** | Advanced | Structural typing, interface definition |
| **Generators** | Advanced | Memory-efficient iteration |

### 2.3 Frontend Development

| Skill | Level | Description |
|-------|-------|-------------|
| **TypeScript 5.x** | Expert | Type-safe JavaScript development |
| **React 18** | Expert | UI framework with hooks and concurrent features |
| **Next.js 14** | Advanced | Full-stack framework, App Router |
| **Ant Design 5.x** | Advanced | Enterprise UI component library |
| **ECharts 5.x** | Advanced | Data visualization, SPC charts |
| **Tailwind CSS** | Intermediate | Utility-first CSS framework |

### 2.4 DevOps & Infrastructure

| Skill | Level | Description |
|-------|-------|-------------|
| **Docker** | Expert | Containerization, multi-stage builds |
| **Kubernetes** | Advanced | Orchestration, Helm charts |
| **CI/CD** | Advanced | GitLab CI, pipeline automation |
| **Prometheus + Grafana** | Intermediate | Monitoring and observability |
| **ELK Stack** | Intermediate | Logging and analysis |

## 3. MES Domain Skills

### 3.1 Odoo-Inspired ORM Design

#### Model Definition Skills

```python
# Odoo-style Model Pattern
from jiatech_mes.orm import Model, fields, api

class LotModel(Model):
    """Lot management model with metaclass-driven registration."""
    
    _name = 'mes.lot'
    _description = 'Manufacturing Lot'
    _table = 'mes_lot'
    _order = 'create_date desc'
    
    # Fields
    lot_id = fields.Char(string='Lot ID', required=True, index=True)
    state = fields.Selection([
        ('created', 'Created'),
        ('active', 'Active'),
        ('held', 'On Hold'),
        ('completed', 'Completed'),
    ], default='created', group_expand='_group_expand_states')
    
    product_id = fields.Many2one('mes.product', string='Product')
    quantity = fields.Float(string='Quantity', digits=(15, 3))
    route_id = fields.Many2one('mes.route', string='Route')
    
    # Computed fields
    remaining_qty = fields.Float(
        compute='_compute_remaining',
        store=True,
        readonly=True
    )
    
    # Related fields
    product_name = fields.Char(related='product_id.name', readonly=True)
    
    # Lifecycle hooks
    @api.model
    def create(self, vals):
        vals['lot_id'] = self._generate_lot_id()
        return super().create(vals)
    
    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.route_id = self.product_id.route_id
    
    @api.depends('quantity', 'product_id')
    def _compute_remaining(self):
        for record in self:
            record.remaining_qty = record.quantity - record.output_qty
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity must be positive")
```

#### Recordset Pattern

```python
# Odoo-style Recordset Operations
class LotModel(Model):
    
    @api.model
    def get_active_lots(self):
        """Return recordset of active lots."""
        return self.search([('state', '=', 'active')])
    
    def action_track_in(self):
        """Recordset method with implicit iteration."""
        for lot in self:
            lot.write({
                'state': 'active',
                'track_in_time': fields.Datetime.now(),
            })
        return True
    
    def action_hold(self):
        """Batch operations on recordsets."""
        return self.write({'state': 'held'})
    
    @api.model
    def process_batch(self, lot_ids):
        """Batch processing with recordsets."""
        lots = self.browse(lot_ids)
        active_lots = lots.filtered(lambda l: l.state == 'active')
        active_lots.action_track_in()
```

### 3.2 MES Module Implementation Skills

#### WIP Module

| Skill | Description |
|-------|-------------|
| **Model Registration** | Metaclass-driven model registry |
| **Recordset Operations** | Chainable CRUD on recordsets |
| **Computed Fields** | @depends decorator for reactive fields |
| **Onchange Methods** | UI-driven computed values |
| **Constraint Validation** | @constrains for business rules |
| **Workflow Actions** | Action methods on recordsets |

#### MM Module (Material Management)

| Skill | Description |
|-------|-------------|
| **Stock Quantities** | Virtual quantities calculation |
| **BOM Explosion** | Recursive product structure |
| **Lot/Serial Tracking** | Traceability by lot |
| **Reservation System** | Material allocation |

#### EDC Module

| Skill | Description |
|-------|-------------|
| **Real-time Collection** | SECS/GEM, OPC-UA integration |
| **Data Validation** | Threshold checking |
| **Event Publishing** | Async event queue |

### 3.3 Custom ORM Framework

```python
# Custom ORM Architecture (Odoo-inspired)
class BaseModel(metaclass=MetaModel):
    """Base model with metaclass-driven registration."""
    
    _name: str | None = None
    _table: str | None = None
    _auto: bool = True
    _abstract: bool = False
    _inherit: str | list[str] = ()
    _order: str = 'id'
    
    # Internal fields
    id: int
    create_date: datetime
    write_date: datetime
    create_uid: int
    write_uid: int
    
    # ORM Methods
    @classmethod
    def browse(cls, ids: list[int]) -> Recordset:
        """Return a recordset from IDs."""
        return Recordset(cls, ids)
    
    @classmethod
    def search(
        cls,
        domain: list,
        offset: int = 0,
        limit: int | None = None,
        order: str | None = None
    ) -> Recordset:
        """Search records by domain."""
        pass
    
    @classmethod
    def create(cls, vals: dict) -> Recordset:
        """Create new record."""
        pass
    
    def write(self, vals: dict) -> bool:
        """Update record."""
        pass
    
    def unlink(self) -> bool:
        """Delete record."""
        pass
    
    def read(self, fields: list[str] | None = None) -> list[dict]:
        """Read record fields."""
        pass


class MetaModel(type):
    """Metaclass for model registration."""
    
    _registry: dict[str, type['BaseModel']] = {}
    
    def __new__(meta, name, bases, attrs):
        cls = super().__new__(meta, name, bases, attrs)
        
        if getattr(cls, '_name') and not getattr(cls, '_abstract', False):
            meta._registry[cls._name] = cls
        
        return cls
```

## 4. Architecture Skills

### 4.1 Design Patterns (Odoo-Inspired)

| Pattern | Application |
|---------|-------------|
| **Metaclass Registration** | Auto model discovery and registry |
| **Decorator API** | Non-invasive feature addition |
| **Environment Pattern** | Context encapsulation (cr, uid, context) |
| **Recordset Pattern** | Collection operations |
| **Active Record** | Object-Relation mapping |
| **Repository Pattern** | Data access abstraction |
| **Service Layer** | Business logic encapsulation |

### 4.2 System Design

| Skill | Description |
|-------|-------------|
| **Modular Architecture** | Plugin-based module system |
| **Event-Driven** | Async event handling |
| **Clean Architecture** | Layer separation |
| **CQRS** | Read/write separation |

## 5. Quality Assurance Skills

### 5.1 Testing (Odoo-Inspired)

| Type | Tools | Target |
|------|-------|--------|
| **Unit Testing** | pytest, unittest | 80%+ |
| **Recordset Tests** | Mock recordset behavior | Core ORM |
| **HTTP Tests** | TestClient | API endpoints |
| **Integration Testing** | Testcontainers | DB integration |
| **E2E Testing** | Playwright | Critical flows |

### 5.2 Code Quality

| Tool | Purpose |
|------|---------|
| **Ruff** | Linting, formatting |
| **Mypy** | Type checking |
| **Black** | Code formatting |
| **Pre-commit** | Git hooks |

## 6. Advanced Python Patterns

### 6.1 Descriptor Pattern for Fields

```python
# Custom field descriptor
class FieldDescriptor:
    """Descriptor for model fields."""
    
    def __init__(self, field_name: str, field_type: type):
        self.field_name = field_name
        self.field_type = field_type
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._values.get(self.field_name)
    
    def __set__(self, obj, value):
        obj._values[self.field_name] = value
        obj._modified.add(self.field_name)
```

### 6.2 Context Manager for Transactions

```python
# Transaction context manager
from contextlib import contextmanager

@contextmanager
def transaction(registry, db_name: str):
    """Database transaction context manager."""
    cr = registry.cursor()
    try:
        yield cr
        cr.commit()
    except Exception:
        cr.rollback()
        raise
    finally:
        cr.close()
```

### 6.3 Environment Pattern

```python
# Environment pattern (Odoo-inspired)
class Environment:
    """Encapsulates database context."""
    
    def __init__(
        self,
        cr: Cursor,
        uid: int,
        context: dict,
        su: bool = False
    ):
        self.cr = cr
        self.uid = uid
        self.context = frozendict(context)
        self.su = su
        self._cache: dict = {}
    
    def __getitem__(self, model_name: str) -> type[BaseModel]:
        """Get model class from registry."""
        return self.registry[model_name]
    
    def __call__(self, model_name: str) -> Recordset:
        """Get empty recordset for model."""
        return self[model_name].browse([])
    
    def sudo(self, user_id: int | None = None) -> 'Environment':
        """Switch to different user context."""
        if user_id is None:
            return self
        return Environment(self.cr, user_id, self.context)
    
    @property
    def registry(self) -> Registry:
        """Get model registry."""
        return Registry.get(self.cr.db_name)
```

## 7. Skill Development Roadmap

### Phase 1: Foundation (Month 1-2)
- Python 3.11+ proficiency with type hints
- Custom ORM framework development
- Metaclass-driven model registration
- PostgreSQL advanced features

### Phase 2: Core MES (Month 3-6)
- WIP module with Odoo-style recordsets
- MM module with stock operations
- RAS equipment management
- EDC data collection

### Phase 3: Advanced Features (Month 7-9)
- SPC rule engine
- PMS maintenance scheduling
- ALM notification system
- Advanced analytics

### Phase 4: Integration & Optimization (Month 10-12)
- ERP/WMS integration
- Performance optimization
- Scalability improvements
- Security hardening

## 8. Skill Assessment Criteria

| Level | Criteria |
|-------|----------|
| **Expert** | Can design and implement ORM patterns; mentor others |
| **Advanced** | Can implement complex features using patterns |
| **Intermediate** | Can implement standard features with guidance |
| **Beginner** | Learning fundamentals |

## 9. Skill Matrix Template

```
| Skill Area               | Required | Current | Gap      | Development Plan |
|--------------------------|----------|---------|----------|------------------|
| Python 3.11+             | Expert   | Adv     | Expert   | Training + PRs   |
| Custom ORM Design        | Expert   | Beg     | Expert   | Workshop + Labs  |
| Metaclass/Descriptor     | Expert   | Int     | Expert   | Deep Study       |
| PostgreSQL               | Expert   | Adv     | Expert   | Self-study       |
| React/TypeScript         | Adv      | Int     | Adv      | Workshop + Labs  |
| MES Domain               | Expert   | Int     | Expert   | Project work     |
```
