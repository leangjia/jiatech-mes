# Jia Tech MES System - Planning Documents

## Overview

This directory contains the comprehensive planning documents for developing Jia Tech's proprietary Manufacturing Execution System (MES). Inspired by Odoo 18's elegant architecture, our system combines modern Python features with a clean, extensible design for semiconductor and electronic manufacturing operations.

## Document Index

| Document | Description |
|----------|-------------|
| [skill.md](skill.md) | Skills definition and competency requirements |
| [agent.md](agent.md) | AI agent architecture and automation workflows |
| [architecture.md](architecture.md) | System architecture design (Odoo-inspired) |
| [modules.md](modules.md) | Module design specifications |
| [coding-standards.md](coding-standards.md) | Coding standards and best practices |
| [roadmap.md](roadmap.md) | Development timeline and milestones |

## Quick Summary

### System Overview

Jia Tech MES is an **Odoo-inspired** manufacturing execution system featuring:

- **Custom ORM Framework** - Metaclass-driven model registration
- **Recordset Pattern** - Odoo-style chainable operations
- **Environment Pattern** - Database context encapsulation
- **API Decorators** - @model, @depends, @onchange, @constrains
- **Field System** - Descriptor-based field implementation
- **Module System** - Plugin-based architecture with manifests

### Core Design Patterns (Odoo-Inspired)

```
┌─────────────────────────────────────────────────────────────┐
│                      MetaModel (Metaclass)                    │
│              Auto model registration & discovery              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       BaseModel                               │
│    _name, _table, _inherit, _fields, _constraints           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        Recordset                             │
│  lot_records.browse([1,2,3]).filtered(...).write(...)      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       Environment                            │
│         env['mes.wip.lot'].browse([]).sudo(user_id)         │
└─────────────────────────────────────────────────────────────┘
```

### Development Timeline

| Phase | Period | Focus |
|-------|--------|-------|
| Phase 1 | Q1 2026 | Foundation & Custom ORM Framework |
| Phase 2 | Q2 2026 | Core MES Modules (WIP, MM, RAS) |
| Phase 3 | Q3 2026 | Quality & Maintenance (SPC, PMS, ALM) |
| Phase 4 | Q4 2026 | Advanced Features & Release |

### Key Modules

| Module | Model | Description |
|--------|-------|-------------|
| WIP | `mes.wip.lot` | Lot tracking, TrackIn/Out, state management |
| MM | `mes.mm.product` | Material management, inventory, BOM |
| RAS | `mes.ras.equipment` | Equipment management, capacity |
| EDC | `mes.edc.collection` | Equipment data collection |
| SPC | `mes.spc.job` | Statistical process control |
| PMS | `mes.pms.schedule` | Preventive maintenance scheduling |
| ALM | `mes.alm.alarm` | Alarm management and notifications |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Ant Design |
| Backend | Python 3.11+, FastAPI |
| ORM | Custom ORM (Odoo-inspired), SQLAlchemy 2.x |
| Database | PostgreSQL 16, Redis |
| Messaging | RabbitMQ, Kafka |
| Container | Docker, Kubernetes |
| Monitoring | Prometheus, Grafana, Jaeger |
| Testing | pytest, pytest-asyncio |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Kubernetes
- PostgreSQL 16
- Redis

### Project Structure

```
jiatech-mes/
├── skill.md              # Team skills & competencies
├── agent.md              # Agent architecture
├── architecture.md       # System design (Odoo-inspired)
├── modules.md            # Module specifications
├── coding-standards.md   # Development guidelines
└── roadmap.md           # Project timeline
```

### Odoo-Inspired Features

| Feature | Odoo | Jia Tech MES |
|---------|------|--------------|
| Model Registration | MetaModel | Custom MetaModel |
| ORM | osv.Model | BaseModel |
| Fields | fields.* | fields.* (same) |
| Decorators | @api.* | @api.* (same) |
| Environment | self.env | self.env (same) |
| Recordsets | self.browse() | self.browse() (same) |
| Modules | __manifest__.py | __manifest__.py (same) |
| Database | PostgreSQL | PostgreSQL |

## Documentation

### For Developers
- Read [coding-standards.md](coding-standards.md) for development guidelines
- Read [architecture.md](architecture.md) for system design
- Read [modules.md](modules.md) for module specifications

### For Project Managers
- Read [roadmap.md](roadmap.md) for project timeline
- Read [skill.md](skill.md) for team capabilities

### For Architects
- Read [architecture.md](architecture.md) for detailed architecture
- Read [agent.md](agent.md) for agent workflows

## License

Proprietary - Jia Tech Corporation
