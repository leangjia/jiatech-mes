# Jia Tech MES System - Architecture Design

## 1. Executive Summary

This document outlines the technical architecture for Jia Tech's proprietary Manufacturing Execution System (MES). Inspired by Odoo 18's elegant design, our system combines modern Python features with a clean, extensible architecture for semiconductor and electronic manufacturing operations.

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| **Modularity** | Loose coupling via plugin-based modules |
| **Extensibility** | Odoo-style inheritance and extension |
| **Scalability** | Horizontal scaling with stateless services |
| **Resilience** | Fault tolerance, graceful degradation |
| **Observability** | Comprehensive monitoring and logging |
| **Security** | Zero trust, defense in depth |
| **Automation** | CI/CD, infrastructure as code |

## 3. Architecture Overview (Odoo-Inspired)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │   Web Client     │  │   Mobile App     │  │   Desktop Client         │   │
│  │   (React/TS)     │  │   (React Native) │  │   (PyQt/Tkinter)        │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬───────────┘   │
└────────────┼─────────────────────┼──────────────────────────┼───────────────┘
             │                     │                          │
┌────────────▼─────────────────────▼──────────────────────────▼───────────────┐
│                           API GATEWAY LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      Kong API Gateway                                     │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │  │
│  │  │ Rate Limit  │ │ Auth Filter │ │ Load Balance│ │ Circuit Breaker │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                           ORM SERVICE LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                   Custom ORM Engine (Odoo-style)                        │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │  │
│  │  │ MetaModel  │ │  Recordset │ │Environment  │ │   Field System  │ │  │
│  │  │  Registry  │ │  Operations │ │   Context   │ │   (Descriptors) │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼───────┐           ┌────────▼────────┐          ┌────────▼────────┐
│   DATA LAYER  │           │   EVENT LAYER   │          │  INTEGRATION    │
│               │           │                  │          │     LAYER       │
│ ┌───────────┐ │           │ ┌──────────────┐ │          │ ┌────────────┐  │
│ │ PostgreSQL │ │           │ │   RabbitMQ   │ │          │ │   ERP API  │  │
│ │  (Primary) │ │           │ │              │ │          │ └────────────┘  │
│ └───────────┘ │           │ └──────────────┘ │          │ ┌────────────┐  │
│ ┌───────────┐ │           │ ┌──────────────┐ │          │ │   WMS API  │  │
│ │ Redis     │ │           │ │    Kafka     │ │          │ └────────────┘  │
│ │  (Cache)  │ │           │ │  (Analytics) │ │          │ ┌────────────┐  │
│ └───────────┘ │           │ └──────────────┘ │          │ │ Equipment  │  │
│ ┌───────────┐ │           └──────────────────┘          │ │  (SECS/GEM)│  │
│ │Elasticsearch│ │                                          │ └────────────┘  │
│ │  (Logging) │ │                                          └────────────────┘
│ └───────────┘ │
└───────────────┘
```

## 4. Odoo-Inspired ORM Architecture

### 4.1 Core ORM Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORM Architecture                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      MetaModel (Metaclass)                           │ │
│  │  • Auto model registration                                           │ │
│  │  • Field discovery and cataloging                                    │ │
│  │  • Inheritance handling                                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                           Models                                      │ │
│  │                                                                       │ │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │ │
│  │   │   LotModel   │  │ MaterialModel │  │ EquipmentModel│            │ │
│  │   │   (Model)    │  │   (Model)     │  │    (Model)    │            │ │
│  │   └───────────────┘  └───────────────┘  └───────────────┘            │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                          Recordsets                                    │ │
│  │                                                                       │ │
│  │   lot_records = LotModel.browse([1, 2, 3])                         │ │
│  │   lot_records.filtered(lambda r: r.state == 'active')               │ │
│  │   lot_records.write({'state': 'completed'})                        │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                          Environment                                   │ │
│  │                                                                       │ │
│  │   env = Environment(cr, uid, context)                               │ │
│  │   env['mes.lot'].browse([1, 2])                                     │ │
│  │   env['res.users'].sudo(user_id)                                    │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Model Registry

```python
# Model Registry (Odoo-style)
class Registry:
    """Central model registry per database."""
    
    _registries: dict[str, 'Registry'] = {}
    _lock = threading.RLock()
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.models: dict[str, type[BaseModel]] = {}
        self._init()
    
    @classmethod
    def get(cls, db_name: str) -> 'Registry':
        """Get or create registry for database."""
        with cls._lock:
            if db_name not in cls._registries:
                cls._registries[db_name] = cls(db_name)
            return cls._registries[db_name]
    
    def __getitem__(self, model_name: str) -> type[BaseModel]:
        """Get model class by name."""
        return self.models[model_name]
    
    def register(self, model_class: type[BaseModel]) -> None:
        """Register a model class."""
        if model_class._name:
            self.models[model_class._name] = model_class
```

### 4.3 Recordset Pattern

```python
# Recordset (Odoo-style)
class Recordset:
    """Collection of model records with chainable operations."""
    
    def __init__(self, model: type[BaseModel], ids: list[int]):
        self._model = model
        self._ids = list(ids)
        self._values = {}  # cached values
    
    def __iter__(self):
        for rec_id in self._ids:
            yield Recordset(self._model, [rec_id])
    
    def __len__(self) -> int:
        return len(self._ids)
    
    def filtered(self, func: Callable) -> 'Recordset':
        """Filter records by condition."""
        return Recordset(
            self._model,
            [r.id for r in self if func(r)]
        )
    
    def mapped(self, func: str | Callable) -> list:
        """Map records to values."""
        if isinstance(func, str):
            return [getattr(r, func) for r in self]
        return [func(r) for r in self]
    
    def write(self, vals: dict) -> bool:
        """Update all records in recordset."""
        for record in self:
            record._write(vals)
        return True
    
    def unlink(self) -> bool:
        """Delete all records in recordset."""
        self._model.unlink(self._ids)
        return True
```

### 4.4 Environment Pattern

```python
# Environment (Odoo-style)
class Environment:
    """Database access context."""
    
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
        self._protected: dict = {}
    
    def __getitem__(self, model_name: str) -> type[BaseModel]:
        """Get model class."""
        return self.registry.models[model_name]
    
    def __call__(self, model_name: str) -> Recordset:
        """Get empty recordset."""
        return self[model_name].browse([])
    
    @property
    def registry(self) -> Registry:
        """Get model registry."""
        return Registry.get(self.cr.db_name)
    
    def sudo(self, user_id: int | None = None) -> 'Environment':
        """Execute as different user."""
        if user_id is None:
            return self
        return Environment(self.cr, user_id, self.context)
    
    def ref(self, xmlid: str) -> Recordset:
        """Get record by external ID."""
        module, name = xmlid.split('.')
        # ... implementation
```

### 4.5 Field System (Descriptors)

```python
# Field Descriptor (Odoo-style)
class Field:
    """Base field descriptor."""
    
    def __init__(
        self,
        string: str = None,
        required: bool = False,
        readonly: bool = False,
        default=None,
        help: str = None,
        index: bool = False,
        store: bool = True,
        compute: str = None,
        inverse: str = None,
        related: str = None,
    ):
        self.string = string
        self.required = required
        self.readonly = readonly
        self.default = default
        self.help = help
        self.index = index
        self.store = store
        self.compute = compute
        self.inverse = inverse
        self.related = related
        self.name = None  # set by model
    
    def __get__(self, obj, objtype=None) -> Any:
        if obj is None:
            return self
        return obj._values.get(self.name)
    
    def __set__(self, obj, value) -> None:
        obj._values[self.name] = value
        obj._modified.add(self.name)


class Char(Field):
    type = 'char'
    max_length = None


class Integer(Field):
    type = 'integer'


class Float(Field):
    type = 'float'
    digits: tuple[int, int] = None


class Many2one(Field):
    type = 'many2one'
    relational = True
    
    def __init__(self, comodel_name: str, **kwargs):
        self.comodel_name = comodel_name
        super().__init__(**kwargs)


class One2many(Field):
    type = 'one2many'
    relational = True
    
    def __init__(
        self,
        comodel_name: str,
        inverse_name: str,
        **kwargs
    ):
        self.comodel_name = comodel_name
        self.inverse_name = inverse_name
        super().__init__(**kwargs)


class Many2many(Field):
    type = 'many2many'
    relational = True
    
    def __init__(
        self,
        comodel_name: str,
        relation: str = None,
        column1: str = None,
        column2: str = None,
        **kwargs
    ):
        self.comodel_name = comodel_name
        self.relation = relation
        self.column1 = column1
        self.column2 = column2
        super().__init__(**kwargs)
```

## 5. System Layers

### 5.1 Client Layer

| Client Type | Technology | Use Case |
|-------------|------------|----------|
| **Web Application** | React 18 + TypeScript | Primary user interface |
| **Mobile Application** | React Native | Field operators, supervisors |
| **Desktop Client** | PyQt/Tkinter | Heavy operations, offline mode |
| **Dashboard** | Next.js + ECharts | Executive dashboards |
| **B2B API** | REST/GraphQL | Partner integration |

### 5.2 API Gateway Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kong API Gateway                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Rate Limiter  │    │     CORS        │                    │
│  │   1000 req/min  │    │   Configurable  │                    │
│  └─────────────────┘    └─────────────────┘                    │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   JWT Auth      │    │   Request Log   │                    │
│  │   Validation    │    │   (Tracing)     │                    │
│  └─────────────────┘    └─────────────────┘                    │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Load Balancer   │    │ Circuit Breaker │                    │
│  │ (Round Robin)   │    │ (PyBreaker)     │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 ORM Service Layer

| Component | Description |
|-----------|-------------|
| **MetaModel** | Metaclass for auto model registration |
| **BaseModel** | Base class for all models |
| **Recordset** | Collection operations on records |
| **Environment** | Database context encapsulation |
| **Fields** | Field descriptors (Char, Integer, Many2one, etc.) |
| **API Decorators** | @model, @depends, @onchange, @constrains |

### 5.4 Service Layer (Microservices)

#### Core MES Services

| Service | Port | ORM Models | Description |
|---------|------|-----------|-------------|
| **wip-service** | 8081 | LotModel, RouteModel, OperationModel | Work In Progress |
| **mm-service** | 8082 | MaterialModel, StockModel, BomModel | Material Management |
| **ras-service** | 8083 | EquipmentModel, StateModel | Resource Management |
| **edc-service** | 8084 | DataCollectionModel | Equipment Data Collection |
| **spc-service** | 8085 | SpcJobModel, RuleModel | Statistical Process Control |
| **pms-service** | 8086 | MaintenanceScheduleModel | Preventive Maintenance |
| **alm-service** | 8087 | AlarmModel, ActionRuleModel | Alarm Management |

### 5.5 Data Layer

#### PostgreSQL Schema

```sql
-- Odoo-style table naming
CREATE TABLE mes_lot (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL UNIQUE,
    state VARCHAR(20) NOT NULL DEFAULT 'created',
    product_id INTEGER REFERENCES mes_product(id),
    quantity DECIMAL(15, 3) NOT NULL,
    route_id INTEGER REFERENCES mes_route(id),
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    
    CONSTRAINT uk_mes_lot_lot_id UNIQUE (lot_id)
);

CREATE INDEX idx_mes_lot_state ON mes_lot(state);
CREATE INDEX idx_mes_lot_product ON mes_lot(product_id);
CREATE INDEX idx_mes_lot_created ON mes_lot(create_date);
```

## 6. API Decorators (Odoo-Inspired)

```python
# API Decorators
def model(method):
    """Decorator for model-level methods (no record context)."""
    method._api = 'model'
    return method


def depends(*args):
    """Decorator for computed field dependencies."""
    def decorator(method):
        method._depends = args
        return method
    return decorator


def depends_context(*args):
    """Decorator for context-dependent computed fields."""
    def decorator(method):
        method._depends_context = args
        return method
    return decorator


def constrains(*args):
    """Decorator for constraint validation."""
    def decorator(method):
        method._constrains = args
        return method
    return decorator


def onchange(*args):
    """Decorator for onchange methods."""
    def decorator(method):
        method._onchange = args
        return method
    return decorator


def returns(model, downgrade=None):
    """Decorator for return type specification."""
    def decorator(method):
        method._returns = model
        method._downgrade = downgrade
        return method
    return decorator


# Usage Example
class LotModel(Model):
    
    @api.model
    def get_default_lot(self):
        """Model method (no record)."""
        return self.search([], limit=1)
    
    @api.depends('quantity', 'product_id')
    def _compute_remaining(self):
        """Computed field."""
        for record in self:
            record.remaining_qty = record.quantity - record.output_qty
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """Constraint validation."""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity must be positive")
    
    @api.onchange('product_id')
    def _onchange_product(self):
        """UI onchange handler."""
        if self.product_id:
            return {'warning': {'title': 'Warning', 'message': 'Product changed'}}
```

## 7. Module System (Odoo-Inspired)

### 7.1 Module Manifest

```python
# __manifest__.py
{
    'name': 'MES WIP Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'description': 'Work In Progress Management',
    
    'depends': ['mes_base'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/lot_views.xml',
        'views/route_views.xml',
        'data/lot_sequence.xml',
    ],
    
    'demo': [
        'demo/lot_demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
    
    'hooks': {
        'pre_init': 'pre_init_hook',
        'post_init': 'post_init_hook',
        'uninstall': 'uninstall_hook',
    },
}
```

### 7.2 Module Loading

```python
# Module Loader
class ModuleLoader:
    """Odoo-style module loader."""
    
    def load_modules(self, registry, modules: list[str]):
        """Load modules in dependency order."""
        graph = self._build_graph(modules)
        
        for package in graph:
            self._load_module(registry, package)
    
    def _load_module(self, registry, package):
        """Load single module."""
        # 1. Run pre-migration
        self._migrate_module(package, 'pre')
        
        # 2. Import Python module
        import_module(package.name)
        
        # 3. Load models
        registry.load_models(package)
        
        # 4. Setup models
        registry.setup_models()
        
        # 5. Load data files
        self._load_data(package)
        
        # 6. Run post-migration
        self._migrate_module(package, 'post')
```

## 8. Deployment Architecture

### 8.1 Kubernetes Deployment

```
┌──────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Namespace: mes-orm                                          │  │
│  │                                                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │   ORM Svc  │  │  ORM Svc  │  │  ORM Svc  │           │  │
│  │  │   (Gunicorn)│  │ (Gunicorn)│  │(Gunicorn) │           │  │
│  │  └────────────┘  └────────────┘  └────────────┘           │  │
│  │                                                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Namespace: mes-infra                                        │  │
│  │                                                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │ postgresql │  │   redis   │  │  rabbitmq  │           │  │
│  │  │   (Patroni) │  │           │  │            │           │  │
│  │  └────────────┘  └────────────┘  └────────────┘           │  │
│  │                                                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 9. Event System

```python
# Event Publisher (Odoo-style)
class EventPublisher:
    """Publish domain events."""
    
    def __init__(self, env: Environment):
        self.env = env
    
    def publish(self, event):
        """Publish event to message queue."""
        self.env.cr.post_commit.add(
            lambda: self._do_publish(event)
        )
    
    def _do_publish(self, event):
        """Actually publish event."""
        channel = f"{event._namespace}.{event._name}"
        self.env['bus.bus'].sendone(channel, event)


# Domain Events
class LotTrackInEvent:
    _namespace = 'mes.lot'
    _name = 'track_in'
    
    def __init__(self, lot_id: int, equipment_id: int, operator_id: int):
        self.lot_id = lot_id
        self.equipment_id = equipment_id
        self.operator_id = operator_id
        self.timestamp = datetime.now()
```

## 10. Security Architecture

```python
# Security Model (Odoo-style)
class ResUsers(Model):
    _name = 'res.users'
    _description = 'Users'
    
    name = fields.Char(required=True)
    login = fields.Char(required=True, unique=True)
    password = fields.Char()
    groups_id = fields.Many2many('res.groups')
    
    def check(self, password: str) -> bool:
        """Verify password."""
        return self._crypt_context.verify(password, self.password)
    
    def _compute_session_token(self, sid: str) -> str:
        """Compute session token."""
        # ... implementation
```

## 11. Observability

### 11.1 Logging (Odoo-style)

```python
import logging

_logger = logging.getLogger(__name__)

class LotModel(Model):
    
    @api.model
    def create(self, vals):
        _logger.debug('Creating lot: %s', vals)
        try:
            result = super().create(vals)
            _logger.info('Lot created: %s', result.lot_id)
            return result
        except Exception as e:
            _logger.error('Failed to create lot: %s', str(e))
            raise
```

### 11.2 Monitoring

| Component | Metrics |
|-----------|---------|
| **ORM** | Query count, execution time |
| **Recordsets** | Record operations, cache hits |
| **Environment** | Context switches, sudo calls |
| **Fields** | Compute time, store operations |

## 12. Migration System

```python
# Alembic + Odoo-style migrations
# migrations/versions/2026_03_22_0001_create_lot_table.py

"""Create lot table.

Revision ID: 2026_03_22_0001
Revises: 
Create Date: 2026-03-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision: str = '2026_03_22_0001'
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        'mes_lot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lot_id', sa.String(50), nullable=False),
        sa.Column('state', sa.String(20), nullable=False),
        # ... more columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lot_id'),
    )
    
    op.create_index('idx_mes_lot_state', 'mes_lot', ['state'])


def downgrade() -> None:
    op.drop_index('idx_mes_lot_state', table_name='mes_lot')
    op.drop_table('mes_lot')
```
