# Jia Tech MES 系统 - 系统架构设计

## 1. 执行摘要

本文档概述了嘉科技（Jia Tech）专有制造执行系统（MES）的技术架构。系统以 Odoo 18 的优雅设计为灵感，结合现代 Python 特性，为半导体和电子制造业提供清晰、可扩展的架构。

## 2. 设计原则

| 原则 | 描述 |
|------|------|
| **模块化** | 通过插件式模块实现松耦合 |
| **可扩展性** | Odoo 风格继承和扩展机制 |
| **可伸缩性** | 无状态服务水平扩展 |
| **容错性** | 容错处理、优雅降级 |
| **可观测性** | 全面的监控和日志记录 |
| **安全性** | 零信任、深度防御 |
| **自动化** | CI/CD、基础设施即代码 |

## 3. 架构概览（Odoo 风格）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              客户端层                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │   Web 客户端     │  │   移动端应用     │  │   桌面客户端             │   │
│  │   (React/TS)     │  │   (React Native) │  │   (PyQt/Tkinter)       │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬───────────┘   │
└────────────┼─────────────────────┼──────────────────────────┼───────────────┘
             │                     │                          │
┌────────────▼─────────────────────▼──────────────────────────▼───────────────┐
│                           API 网关层                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      Kong API 网关                                     │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │  │
│  │  │  限流器     │ │  认证过滤   │ │  负载均衡   │ │   熔断器       │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
┌─────────────────────────────────────▼───────────────────────────────────────┐
│                           ORM 服务层                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                   自定义 ORM 引擎（Odoo 风格）                          │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │  │
│  │  │  MetaModel │ │  Recordset │ │ Environment │ │   字段系统      │ │  │
│  │  │  注册表    │ │  操作集    │ │   上下文   │ │   （描述符）    │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       │                             │                             │
┌──────▼───────┐           ┌────────▼────────┐          ┌────────▼────────┐
│   数据层     │           │   事件层         │          │    集成层      │
│              │           │                  │          │                │
│ ┌─────────┐ │           │ ┌──────────────┐ │          │ ┌────────────┐  │
│ │ PostgreSQL│ │           │ │   RabbitMQ   │ │          │ │   ERP API  │  │
│ │ (主库)   │ │           │ └──────────────┘ │          │ └────────────┘  │
│ └─────────┘ │           │ ┌──────────────┐ │          │ ┌────────────┐  │
│ ┌─────────┐ │           │ │    Kafka     │ │          │ │   WMS API  │  │
│ │ Redis   │ │           │ │  (分析)     │ │          │ └────────────┘  │
│ │ (缓存)  │ │           └──────────────────┘          │ ┌────────────┐  │
│ └─────────┘ │                                          │ │  设备接口  │  │
│ ┌─────────┐ │                                          │ │ (SECS/GEM) │  │
│ │Elasticsearch│ │                                        └────────────────┘
│ │ (日志)  │ │
│ └─────────┘ │
└─────────────┘
```

## 4. Odoo 风格 ORM 架构

### 4.1 核心 ORM 组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORM 架构                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      MetaModel（元类）                               │   │
│  │  • 自动模型注册                                                     │   │
│  │  • 字段发现和编目                                                   │   │
│  │  • 继承处理                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐     │
│  │                           模型层                                      │     │
│  │                                                                       │     │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │     │
│  │   │   LotModel   │  │ MaterialModel │  │ EquipmentModel│        │     │
│  │   │   (Model)    │  │   (Model)     │  │    (Model)   │        │     │
│  │   └───────────────┘  └───────────────┘  └───────────────┘        │     │
│  │                                                                       │     │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐     │
│  │                          Recordset（记录集）                          │     │
│  │                                                                       │     │
│  │   lot_records = LotModel.browse([1, 2, 3])                         │     │
│  │   lot_records.filtered(lambda r: r.state == 'active')                │     │
│  │   lot_records.write({'state': 'completed'})                        │     │
│  │                                                                       │     │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐     │
│  │                          Environment（环境）                           │     │
│  │                                                                       │     │
│  │   env = Environment(cr, uid, context)                               │     │
│  │   env['mes.lot'].browse([1, 2])                                   │     │
│  │   env['res.users'].sudo(user_id)                                   │     │
│  │                                                                       │     │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 模型注册表

```python
# 模型注册表（Odoo 风格）
class Registry:
    """每个数据库的中央模型注册表。"""
    
    _registries: dict[str, 'Registry'] = {}
    _lock = threading.RLock()
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.models: dict[str, type[BaseModel]] = {}
        self._init()
    
    @classmethod
    def get(cls, db_name: str) -> 'Registry':
        """获取或创建数据库的注册表。"""
        with cls._lock:
            if db_name not in cls._registries:
                cls._registries[db_name] = cls(db_name)
            return cls._registries[db_name]
    
    def __getitem__(self, model_name: str) -> type[BaseModel]:
        """按名称获取模型类。"""
        return self.models[model_name]
    
    def register(self, model_class: type[BaseModel]) -> None:
        """注册模型类。"""
        if model_class._name:
            self.models[model_class._name] = model_class
```

### 4.3 Recordset 模式

```python
# Recordset（Odoo 风格）
class Recordset:
    """可链式操作的模型记录集合。"""
    
    def __init__(self, model: type[BaseModel], ids: list[int]):
        self._model = model
        self._ids = list(ids)
        self._values = {}  # 缓存值
    
    def __iter__(self):
        for rec_id in self._ids:
            yield Recordset(self._model, [rec_id])
    
    def __len__(self) -> int:
        return len(self._ids)
    
    def filtered(self, func: Callable) -> 'Recordset':
        """按条件过滤记录。"""
        return Recordset(
            self._model,
            [r.id for r in self if func(r)]
        )
    
    def mapped(self, func: str | Callable) -> list:
        """映射记录到值。"""
        if isinstance(func, str):
            return [getattr(r, func) for r in self]
        return [func(r) for r in self]
    
    def write(self, vals: dict) -> bool:
        """更新记录集中的所有记录。"""
        for record in self:
            record._write(vals)
        return True
    
    def unlink(self) -> bool:
        """删除记录集中的所有记录。"""
        self._model.unlink(self._ids)
        return True
```

### 4.4 Environment 模式

```python
# Environment（Odoo 风格）
class Environment:
    """数据库访问上下文。"""
    
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
        """获取模型类。"""
        return self.registry.models[model_name]
    
    def __call__(self, model_name: str) -> Recordset:
        """获取空记录集。"""
        return self[model_name].browse([])
    
    @property
    def registry(self) -> Registry:
        """获取模型注册表。"""
        return Registry.get(self.cr.db_name)
    
    def sudo(self, user_id: int | None = None) -> 'Environment':
        """以不同用户身份执行。"""
        if user_id is None:
            return self
        return Environment(self.cr, user_id, self.context)
```

## 5. 系统层级

### 5.1 客户端层

| 客户端类型 | 技术 | 用途 |
|------------|------|------|
| **Web 应用** | React 18 + TypeScript | 主要用户界面 |
| **移动端应用** | React Native | 现场操作员、主管 |
| **桌面客户端** | PyQt/Tkinter | 重型操作、离线模式 |
| **仪表板** | Next.js + ECharts | 高管仪表板 |
| **B2B API** | REST/GraphQL | 合作伙伴集成 |

### 5.2 API 网关层

| 组件 | 描述 |
|------|------|
| **Kong API 网关** | 统一 API 入口 |
| **限流器** | 1000 请求/分钟 |
| **JWT 认证** | 令牌验证 |
| **CORS 配置** | 跨域资源共享 |

### 5.3 ORM 服务层

| 组件 | 描述 |
|------|------|
| **MetaModel** | 元类自动模型注册 |
| **BaseModel** | 所有模型的基类 |
| **Recordset** | 记录集合操作 |
| **Environment** | 数据库上下文封装 |
| **Fields** | 字段描述符 |
| **API 装饰器** | @model, @depends, @onchange, @constrains |

### 5.4 服务层（微服务）

| 服务 | 端口 | ORM 模型 | 描述 |
|------|------|---------|------|
| **wip-service** | 8081 | LotModel, RouteModel | 在制品管理 |
| **mm-service** | 8082 | MaterialModel, StockModel | 物料管理 |
| **ras-service** | 8083 | EquipmentModel, StateModel | 资源管理 |
| **edc-service** | 8084 | DataCollectionModel | 设备数据采集 |
| **spc-service** | 8085 | SpcJobModel, RuleModel | 统计过程控制 |
| **pms-service** | 8086 | MaintenanceScheduleModel | 预防性维护 |
| **alm-service** | 8087 | AlarmModel, ActionRuleModel | 报警管理 |

## 6. API 装饰器（Odoo 风格）

```python
# API 装饰器
@api.model
def get_default_lot(self):
    """模型方法（无记录上下文）。"""
    return self.search([], limit=1)

@api.depends('quantity', 'product_id')
def _compute_remaining(self):
    """计算字段。"""
    for record in self:
        record.remaining_qty = record.quantity - record.output_qty

@api.constrains('quantity')
def _check_quantity(self):
    """约束验证。"""
    for record in self:
        if record.quantity <= 0:
            raise ValidationError("数量必须为正数")

@api.onchange('product_id')
def _onchange_product(self):
    """UI onchange 处理器。"""
    if self.product_id:
        return {'warning': {'title': '警告', 'message': '产品已更改'}}
```

## 7. 模块系统（Odoo 风格）

### 7.1 模块清单

```python
# __manifest__.py
{
    'name': 'MES WIP 模块',
    'version': '1.0.0',
    'category': '制造',
    'description': '在制品管理',
    
    'depends': ['mes_base'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/lot_views.xml',
        'views/route_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'license': 'Proprietary',
}
```

## 8. 部署架构

### 8.1 Kubernetes 部署

```
┌──────────────────────────────────────────────────────────────────┐
│                      Kubernetes 集群                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 命名空间: mes-orm                                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │   ORM Svc │  │  ORM Svc  │  │  ORM Svc  │           │  │
│  │  └────────────┘  └────────────┘  └────────────┘           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 9. 相关文档

- [架构设计](./architecture.md) - 英文原版
- [模块设计](./modules.md) - 模块详细规格
- [编码规范](./coding-standards.md) - 开发规范
- [开发路线图](./roadmap.md) - 项目计划
- [技能定义](./skill.md) - 团队技能要求
- [智能体定义](./agent.md) - AI 智能体架构

## 10. 许可证

专有许可证 - Jia Tech Corporation
