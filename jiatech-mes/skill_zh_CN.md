# Jia Tech MES 系统 - 技能定义

## 1. 概述

本文档定义了开发 Jia Tech MES（制造执行系统）所需的专业技能。受 Odoo 18 优雅架构的启发，我们的系统利用 Python 的高级特性实现简洁、可扩展的设计。

## 2. 核心技术栈

### 2.1 后端开发

| 技能 | 等级 | 描述 |
|------|-------|------|
| **Python 3.11+** | 专家 | 主要语言，类型提示，数据类，元类 |
| **FastAPI** | 专家 | 现代异步 Web 框架，OpenAPI 自动生成 |
| **自定义 ORM** | 专家 | Odoo 风格 ORM，元类驱动的模型注册 |
| **SQLAlchemy 2.x** | 高级 | SQL 工具包，支持异步（核心数据库层） |
| **PostgreSQL** | 专家 | 主数据库，高级特性（JSON，分区，pgvector） |
| **Redis** | 高级 | 缓存，会话管理，分布式锁 |
| **RabbitMQ** | 高级 | 消息队列用于异步操作 |
| **Pydantic 2.x** | 专家 | 数据验证，设置管理 |

### 2.2 Python 高级特性（Odoo 风格）

| 特性 | 等级 | 描述 |
|------|-------|------|
| **元类** | 专家 | 模型注册，声明式模式 |
| **描述符** | 高级 | 自定义字段实现 |
| **装饰器** | 专家 | API 装饰器（@model, @depends, @onchange, @constrains）|
| **上下文管理器** | 高级 | 事务管理，资源清理 |
| **数据类/冻结** | 高级 | 不可变 DTO，值对象 |
| **协议** | 高级 | 结构化类型，接口定义 |
| **生成器** | 高级 | 内存高效迭代 |

### 2.3 前端开发

| 技能 | 等级 | 描述 |
|------|-------|------|
| **TypeScript 5.x** | 专家 | 类型安全的 JavaScript 开发 |
| **React 18** | 专家 | UI 框架，hooks 和并发特性 |
| **Next.js 14** | 高级 | 全栈框架，App Router |
| **Ant Design 5.x** | 高级 | 企业级 UI 组件库 |
| **ECharts 5.x** | 高级 | 数据可视化，SPC 图表 |
| **Tailwind CSS** | 中级 | 工具优先 CSS 框架 |

### 2.4 DevOps 与基础设施

| 技能 | 等级 | 描述 |
|------|-------|------|
| **Docker** | 专家 | 容器化，多阶段构建 |
| **Kubernetes** | 高级 | 编排，Helm 图表 |
| **CI/CD** | 高级 | GitLab CI，流水线自动化 |
| **Prometheus + Grafana** | 中级 | 监控和可观测性 |
| **ELK Stack** | 中级 | 日志和分析 |

## 3. MES 领域技能

### 3.1 Odoo 风格 ORM 设计

#### 模型定义技能

```python
# Odoo 风格模型模式
from jiatech_mes.orm import Model, fields, api

class LotModel(Model):
    """批次管理模型，元类驱动注册。"""
    
    _name = 'mes.lot'
    _description = '生产批次'
    _table = 'mes_lot'
    _order = 'create_date desc'
    
    # 字段
    lot_id = fields.Char(string='批次号', required=True, index=True)
    state = fields.Selection([
        ('created', '已创建'),
        ('active', '活动中'),
        ('held', '暂停'),
        ('completed', '已完成'),
    ], default='created', group_expand='_group_expand_states')
    
    product_id = fields.Many2one('mes.product', string='产品')
    quantity = fields.Float(string='数量', digits=(15, 3))
    route_id = fields.Many2one('mes.route', string='工艺路线')
    
    # 计算字段
    remaining_qty = fields.Float(
        compute='_compute_remaining',
        store=True,
        readonly=True
    )
    
    # 关联字段
    product_name = fields.Char(related='product_id.name', readonly=True)
    
    # 生命周期钩子
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
                raise ValidationError("数量必须为正数")
```

#### 记录集模式

```python
# Odoo 风格记录集操作
class LotModel(Model):
    
    @api.model
    def get_active_lots(self):
        """返回活动批次记录集。"""
        return self.search([('state', '=', 'active')])
    
    def action_track_in(self):
        """记录集方法，隐式迭代。"""
        for lot in self:
            lot.write({
                'state': 'active',
                'track_in_time': fields.Datetime.now(),
            })
        return True
    
    def action_hold(self):
        """批量操作记录集。"""
        return self.write({'state': 'held'})
    
    @api.model
    def process_batch(self, lot_ids):
        """使用记录集批量处理。"""
        lots = self.browse(lot_ids)
        active_lots = lots.filtered(lambda l: l.state == 'active')
        active_lots.action_track_in()
```

### 3.2 MES 模块实现技能

#### WIP 模块

| 技能 | 描述 |
|------|------|
| **模型注册** | 元类驱动的模型注册表 |
| **记录集操作** | 记录集上的链式 CRUD |
| **计算字段** | @depends 装饰器用于响应式字段 |
| **Onchange 方法** | UI 驱动的计算值 |
| **约束验证** | @constrains 用于业务规则 |
| **工作流操作** | 记录集上的动作方法 |

#### MM 模块（物料管理）

| 技能 | 描述 |
|------|------|
| **库存数量** | 虚拟数量计算 |
| **BOM 展开** | 递归产品结构 |
| **批次/序列追踪** | 按批次追溯 |
| **预留系统** | 物料分配 |

#### EDC 模块

| 技能 | 描述 |
|------|------|
| **实时采集** | SECS/GEM, OPC-UA 集成 |
| **数据验证** | 阈值检查 |
| **事件发布** | 异步事件队列 |

### 3.3 自定义 ORM 框架

```python
# 自定义 ORM 架构（Odoo 风格）
class BaseModel(metaclass=MetaModel):
    """元类驱动注册的基础模型。"""
    
    _name: str | None = None
    _table: str | None = None
    _auto: bool = True
    _abstract: bool = False
    _inherit: str | list[str] = ()
    _order: str = 'id'
    
    # 内部字段
    id: int
    create_date: datetime
    write_date: datetime
    create_uid: int
    write_uid: int
    
    # ORM 方法
    @classmethod
    def browse(cls, ids: list[int]) -> Recordset:
        """从 ID 返回记录集。"""
        return Recordset(cls, ids)
    
    @classmethod
    def search(
        cls,
        domain: list,
        offset: int = 0,
        limit: int | None = None,
        order: str | None = None
    ) -> Recordset:
        """按域搜索记录。"""
        pass
    
    @classmethod
    def create(cls, vals: dict) -> Recordset:
        """创建新记录。"""
        pass
    
    def write(self, vals: dict) -> bool:
        """更新记录。"""
        pass
    
    def unlink(self) -> bool:
        """删除记录。"""
        pass
    
    def read(self, fields: list[str] | None = None) -> list[dict]:
        """读取记录字段。"""
        pass


class MetaModel(type):
    """模型注册的元类。"""
    
    _registry: dict[str, type['BaseModel']] = {}
    
    def __new__(meta, name, bases, attrs):
        cls = super().__new__(meta, name, bases, attrs)
        
        if getattr(cls, '_name') and not getattr(cls, '_abstract', False):
            meta._registry[cls._name] = cls
        
        return cls
```

## 4. 架构技能

### 4.1 设计模式（Odoo 风格）

| 模式 | 应用 |
|------|------|
| **元类注册** | 自动模型发现和注册表 |
| **装饰器 API** | 非侵入式功能添加 |
| **环境模式** | 上下文封装（cr, uid, context）|
| **记录集模式** | 集合操作 |
| **活动记录** | 对象-关系映射 |
| **仓储模式** | 数据访问抽象 |
| **服务层** | 业务逻辑封装 |

### 4.2 系统设计

| 技能 | 描述 |
|------|------|
| **模块化架构** | 基于插件的模块系统 |
| **事件驱动** | 异步事件处理 |
| **清洁架构** | 分层分离 |
| **CQRS** | 读写分离 |

## 5. 质量保证技能

### 5.1 测试（Odoo 风格）

| 类型 | 工具 | 目标 |
|------|------|------|
| **单元测试** | pytest, unittest | 80%+ |
| **记录集测试** | 模拟记录集行为 | 核心 ORM |
| **HTTP 测试** | TestClient | API 端点 |
| **集成测试** | Testcontainers | 数据库集成 |
| **端到端测试** | Playwright | 关键流程 |

### 5.2 代码质量

| 工具 | 用途 |
|------|------|
| **Ruff** | 代码检查，格式化 |
| **Mypy** | 类型检查 |
| **Black** | 代码格式化 |
| **Pre-commit** | Git 钩子 |

## 6. 高级 Python 模式

### 6.1 字段描述符模式

```python
# 自定义字段描述符
class FieldDescriptor:
    """模型字段描述符。"""
    
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

### 6.2 事务上下文管理器

```python
# 事务上下文管理器
from contextlib import contextmanager

@contextmanager
def transaction(registry, db_name: str):
    """数据库事务上下文管理器。"""
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

### 6.3 环境模式

```python
# 环境模式（Odoo 风格）
class Environment:
    """封装数据库上下文。"""
    
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
        """从注册表获取模型类。"""
        return self.registry[model_name]
    
    def __call__(self, model_name: str) -> Recordset:
        """获取模型的空记录集。"""
        return self[model_name].browse([])
    
    def sudo(self, user_id: int | None = None) -> 'Environment':
        """切换到不同用户上下文。"""
        if user_id is None:
            return self
        return Environment(self.cr, user_id, self.context)
    
    @property
    def registry(self) -> Registry:
        """获取模型注册表。"""
        return Registry.get(self.cr.db_name)
```

## 7. 技能发展路线图

### 第一阶段：基础（第 1-2 月）
- Python 3.11+ 类型提示熟练
- 自定义 ORM 框架开发
- 元类驱动的模型注册
- PostgreSQL 高级特性

### 第二阶段：核心 MES（第 3-6 月）
- Odoo 风格记录集的 WIP 模块
- 库存操作的 MM 模块
- RAS 设备管理
- EDC 数据采集

### 第三阶段：高级特性（第 7-9 月）
- SPC 规则引擎
- PMS 维护调度
- ALM 通知系统
- 高级分析

### 第四阶段：集成与优化（第 10-12 月）
- ERP/WMS 集成
- 性能优化
- 可扩展性改进
- 安全加固

## 8. 技能评估标准

| 等级 | 标准 |
|------|------|
| **专家** | 能够设计和实现 ORM 模式；指导他人 |
| **高级** | 能够使用模式实现复杂功能 |
| **中级** | 能够在指导下实现标准功能 |
| **初级** | 学习基础知识 |

## 9. 技能矩阵模板

```
| 技能领域              | 必需   | 当前  | 差距    | 发展计划 |
|----------------------|--------|-------|---------|----------|
| Python 3.11+         | 专家   | 高级  | 专家    | 培训 + PR |
| 自定义 ORM 设计       | 专家   | 初级  | 专家    | 工作坊 + 实验 |
| 元类/描述符           | 专家   | 中级  | 专家    | 深度学习 |
| PostgreSQL           | 专家   | 高级  | 专家    | 自学 |
| React/TypeScript     | 高级   | 中级  | 高级    | 工作坊 + 实验 |
| MES 领域             | 专家   | 中级  | 专家    | 项目工作 |
```

## 相关文档

- [架构文档](./architecture_zh_CN.md) - 系统架构设计
- [模块设计](./modules_zh_CN.md) - MES 模块规格
- [编码规范](./coding-standards_zh_CN.md) - 代码标准和最佳实践
- [开发路线图](./roadmap_zh_CN.md) - 12 个月开发计划
- [Agent 定义](./agent_zh_CN.md) - AI 代理和自动化工作流
