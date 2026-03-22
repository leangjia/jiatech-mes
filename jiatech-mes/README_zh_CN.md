# Jia Tech MES - 制造执行系统

[![Python版本](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React版本](https://img.shields.io/badge/React-18.2-green.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-orange.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

Jia Tech MES 是一款基于 Odoo 18 架构灵感的专有制造执行系统，采用 Python + FastAPI + React 技术栈，专为半导体和电子制造业设计。

## 功能特性

### 核心框架（Odoo 风格）

- **自定义 ORM 框架** - 元类驱动的模型注册系统
- **Recordset 模式** - Odoo 风格的可链式操作
- **Environment 模式** - 数据库上下文封装
- **API 装饰器** - `@model`, `@depends`, `@onchange`, `@constrains`
- **字段系统** - 基于描述符的字段实现
- **模块系统** - 基于插件架构的模块管理

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      MetaModel (元类)                       │
│                  自动模型注册与发现                          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       BaseModel                             │
│         _name, _table, _inherit, _fields, _constraints     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        Recordset                            │
│   lot_records.browse([1,2,3]).filtered(...).write(...)    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       Environment                            │
│         env['mes.wip.lot'].browse([]).sudo(user_id)       │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, TypeScript, Ant Design, Zustand |
| 后端 | Python 3.10+, FastAPI, SQLAlchemy 2.x |
| ORM | 自定义 ORM (Odoo 风格) |
| 数据库 | PostgreSQL 16, Redis |
| 消息队列 | RabbitMQ, Kafka |
| 容器化 | Docker, Kubernetes |
| 监控 | Prometheus, Grafana |
| 测试 | pytest, pytest-asyncio |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 16
- Redis

### 安装

```bash
# 克隆项目
git clone https://github.com/leangjia/jiatech-mes.git
cd jiatech-mes

# 安装后端依赖
pip install -e ".[dev]"

# 安装前端依赖
cd frontend
npm install
npm run build
```

### 启动服务

```bash
# 启动后端服务器
jiatech server start --port 8000

# 或使用 CLI
jiatech db init      # 初始化数据库
jiatech db migrate   # 运行迁移
jiatech db seed      # 加载演示数据
jiatech server start # 启动服务

# 前端开发模式
cd frontend
npm run dev
```

## 模块列表

| 模块 | 模型 | 描述 | 状态 |
|------|------|------|------|
| **orm** | - | ORM 框架核心 | ✅ 完成 |
| **base** | ResCompany, ResUsers, ResPartner | 基础数据 | ✅ 完成 |
| **wip** | MesLot, MesWorkorder, MesRoute | 在制品管理 | ✅ 完成 |
| **mm** | MesProduct, MesBom, MesStock | 物料管理 | ✅ 完成 |
| **ras** | MesEquipment, MesWorkcenter | 资源管理 | ✅ 完成 |
| **edc** | MesEdcItem, MesEdcCollection | 数据采集 | ✅ 完成 |
| **tcard** | MesTcard, MesTcardStep | 工艺卡管理 | ✅ 完成 |
| **spc** | MesSpcParameter, MesSpcAlarm | 统计过程控制 | ✅ 完成 |
| **pms** | MesMaintenanceRequest, MesSchedule | 预防性维护 | ✅ 完成 |
| **alm** | MesAlarm, MesAlarmAction | 报警管理 | ✅ 完成 |
| **qms** | MesNcr, MesInspection, MesDefect | 质量管理 | ✅ 完成 |

## 项目结构

```
jiatech-mes/
├── src/jiatech_mes/          # Python 源代码
│   ├── orm/                   # ORM 框架核心
│   │   ├── models.py          # BaseModel, Model, AbstractModel
│   │   ├── fields.py          # 字段类型定义
│   │   ├── api.py             # API 装饰器
│   │   ├── environment.py     # 数据库上下文
│   │   ├── recordset.py       # 记录集操作
│   │   └── registry.py        # 模型注册表
│   ├── modules/               # MES 功能模块
│   │   ├── base/              # 基础模块
│   │   ├── wip/               # 在制品管理
│   │   ├── mm/                # 物料管理
│   │   ├── ras/               # 资源管理
│   │   ├── edc/               # 数据采集
│   │   ├── tcard/             # 工艺卡
│   │   ├── spc/               # SPC
│   │   ├── pms/               # 设备维护
│   │   ├── alm/               # 报警管理
│   │   └── qms/               # 质量管理
│   ├── api/                   # FastAPI 接口
│   └── cli/                   # CLI 命令行工具
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── components/         # React 组件
│   │   ├── pages/             # 页面组件
│   │   ├── hooks/             # React Hooks
│   │   └── types/             # TypeScript 类型
├── migrations/                # Alembic 数据库迁移
│   └── versions/              # 迁移版本
├── tests/                     # 单元测试
├── alembic.ini               # Alembic 配置
└── pyproject.toml            # Python 项目配置
```

## CLI 命令

```bash
# 服务器管理
jiatech server start [--host] [--port] [--reload]  # 启动服务器
jiatech server status                              # 查看状态
jiatech server stop                                # 停止服务器
jiatech server restart                              # 重启服务器

# 数据库管理
jiatech db init [--force] [--demo]                 # 初始化数据库
jiatech db migrate [--version] [--dry-run]        # 运行迁移
jiatech db rollback [--steps]                      # 回滚迁移
jiatech db seed [--modules]                        # 加载演示数据
jiatech db backup [--path] [--compress]            # 备份数据库
jiatech db restore <backup_file> [--force]         # 恢复数据库
jiatech db info                                    # 查看数据库信息

# 模块管理
jiatech module list                                # 列出所有模块
jiatech module info <module_name>                  # 模块详情
jiatech module install <module_name>               # 安装模块
jiatech module uninstall <module_name>             # 卸载模块
jiatech module upgrade <module_name>               # 升级模块
```

## ORM API 示例

```python
from jiatech_mes.orm import Model, fields, api

class MesLot(Model):
    _name = 'mes.wip.lot'
    _description = '生产批次'
    _table = 'mes_lot'
    
    name = fields.Char(string='批次号', required=True)
    state = fields.Selection([
        ('pending', '待生产'),
        ('in_progress', '生产中'),
        ('done', '已完成'),
    ], string='状态', default='pending')
    product_id = fields.Many2one('mes.mm.product', string='产品')
    quantity = fields.Float(string='数量', digits=(10, 2))
    
    @api.model
    def create_lot(self, product_id, quantity):
        """创建新批次"""
        return self.create({
            'product_id': product_id,
            'quantity': quantity,
            'state': 'pending',
        })
    
    @api.depends('quantity')
    def _compute_display_name(self):
        for lot in self:
            lot.display_name = f"{lot.name} ({lot.quantity})"

# 使用示例
lot = env['mes.wip.lot'].create({
    'name': 'LOT-2024-001',
    'product_id': 1,
    'quantity': 100,
})

# 链式操作
lots = env['mes.wip.lot'].search([
    ('state', '=', 'pending')
]).filtered(lambda l: l.quantity > 50)

lots.write({'state': 'in_progress'})
```

## 开发指南

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用 TypeScript 严格模式
- 所有模块必须包含 `__manifest__.py`
- 使用 API 装饰器定义业务逻辑
- 编写单元测试覆盖核心功能

### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_orm_models.py -v

# 生成覆盖率报告
pytest tests/ --cov=jiatech_mes --cov-report=html
```

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run build

# 代码检查
npm run lint
```

## 开发计划

| 阶段 | 时间 | 重点 |
|------|------|------|
| 第一阶段 | 2026 Q1 | 基础框架与 ORM |
| 第二阶段 | 2026 Q2 | 核心 MES 模块 (WIP, MM, RAS) |
| 第三阶段 | 2026 Q3 | 质量与维护 (SPC, PMS, ALM) |
| 第四阶段 | 2026 Q4 | 高级功能与发布 |

## 文档

| 文档 | 描述 |
|------|------|
| [architecture.md](architecture.md) | 系统架构设计 |
| [modules.md](modules.md) | 模块详细规格 |
| [coding-standards.md](coding-standards.md) | 编码规范 |
| [roadmap.md](roadmap.md) | 开发路线图 |

## 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

专有许可证 - Jia Tech Corporation

## 联系方式

- 网站: https://www.jiatech.com
- 文档: https://docs.jiatech.com
- GitHub: https://github.com/leangjia/jiatech-mes
