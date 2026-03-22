# Jia Tech MES 系统 - 模块设计规格

## 1. 模块概述（Odoo 风格）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Jia Tech MES 模块架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    基础模块（必需）                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │   base   │ │   base    │ │   base    │ │   base    │ │   base   │     │  │
│  │  │   user   │ │   lang    │ │   config  │ │   module  │ │   audit  │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                         核心 MES 模块                                     │  │
│  │                                                                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │   mes    │ │   mes    │ │   mes    │ │   mes    │ │   mes    │      │  │
│  │  │   wip    │ │   mm    │ │   ras    │ │   edc    │ │  tcard   │      │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                      质量与维护模块                                       │  │
│  │                                                                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                  │  │
│  │  │   mes    │ │   mes    │ │   mes    │ │   mes    │                  │  │
│  │  │   spc    │ │   pms    │ │   alm    │ │   qms    │                  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘                  │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. 核心 ORM 架构

### 2.1 基础模型（Odoo 风格）

```python
# 所有 MES 模型的基础模型
from jiatech_mes.orm import Model, fields, api
from jiatech_mes.orm.fields import Field

class BaseModel(Model):
    """所有模型的抽象基础模型。"""
    
    _abstract = True
    
    id = fields.Id()
    create_date = fields.Datetime(
        string='创建时间',
        readonly=True,
        index=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        string='创建人',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='最后更新时间',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='最后更新人',
        readonly=True,
    )


class MesModel(BaseModel):
    """带日志的 MES 模型基础类。"""
    
    _abstract = True
    
    active = fields.Boolean(
        string='有效',
        default=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        default=lambda self: self.env.company,
    )
    
    def _log_init(self, partial=True):
        """日志模型初始化。"""
        pass
    
    def _register_hook(self):
        """注册模型钩子。"""
        pass
```

### 2.2 模型注册表

```python
# ORM 模型注册表
class Registry:
    """所有模型的中央注册表。"""
    
    _registries: dict[str, 'Registry'] = {}
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.models: dict[str, type['BaseModel']] = {}
        self._sql_tables: dict = {}
        self._depends: dict = {}
    
    def __getitem__(self, name: str) -> type['BaseModel']:
        return self.models[name]
    
    def register_model(self, model_class: type['BaseModel']):
        """注册模型类。"""
        if model_class._name:
            self.models[model_class._name] = model_class
    
    def get_models(self) -> list[type['BaseModel']]:
        """获取所有已注册模型。"""
        return list(self.models.values())
```

## 3. 模块规格

### 3.1 基础模块（mes_base）

**目的**：所有模块的核心基础设施

```python
# 模块定义
class MesBaseModule:
    """提供核心功能的基础模块。"""
    
    name = 'mes_base'
    version = '1.0.0'
    description = '核心 MES 功能'
    depends = []
    
    def register(self, registry: Registry):
        """注册模块模型。"""
        registry.register_model(UserModel)
        registry.register_model(CompanyModel)
        registry.register_model(SequenceModel)
```

### 3.2 WIP 模块（mes_wip）

**包结构（Odoo 风格）**：
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

**模型定义**：

```python
# mes_wip/models/lot.py
class LotModel(MesModel):
    """生产批次模型。"""
    
    _name = 'mes.wip.lot'
    _description = '生产批次'
    _table = 'mes_wip_lot'
    _order = 'create_date desc'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='批次号',
        required=True,
        copy=False,
        readonly=True,
        index=True,
    )
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('created', '已创建'),
        ('in_progress', '进行中'),
        ('held', '暂停'),
        ('completed', '已完成'),
        ('closed', '已关闭'),
        ('scrapped', '已报废'),
    ], string='状态', default='draft', readonly=True, index=True)
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='产品',
        required=True,
        tracking=True,
    )
    
    quantity = fields.Float(
        string='数量',
        digits=(15, 3),
        required=True,
        tracking=True,
    )
    
    uom_id = fields.Many2one(
        'mes.uom',
        string='计量单位',
        required=True,
        default=lambda self: self.env.ref('mes_uom.piece'),
    )
    
    route_id = fields.Many2one(
        'mes.wip.route',
        string='生产工艺路线',
    )
    
    bom_id = fields.Many2one(
        'mes.mm.bom',
        string='物料清单',
    )
    
    move_ids = fields.One2many(
        'mes.wip.lot.operation',
        'lot_id',
        string='操作',
    )
    
    history_ids = fields.One2many(
        'mes.wip.lot.history',
        'lot_id',
        string='历史',
        readonly=True,
    )
    
    # 计算字段
    remaining_qty = fields.Float(
        string='剩余数量',
        compute='_compute_remaining',
        store=True,
    )
    
    progress = fields.Float(
        string='进度 %',
        compute='_compute_progress',
        store=True,
    )
    
    # SQL 约束
    _sql_constraints = [
        ('qty_positive', 'CHECK(quantity > 0)', '数量必须为正数！'),
    ]
    
    # 生命周期方法
    @api.model
    def create(self, vals):
        """创建带自动生成名称的新批次。"""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mes.wip.lot')
        return super().create(vals)
    
    @api.depends('move_ids.state', 'move_ids.quantity')
    def _compute_remaining(self):
        """计算剩余数量。"""
        for lot in self:
            done_qty = sum(
                lot.move_ids.filtered(
                    lambda m: m.state == 'done'
                ).mapped('quantity')
            )
            lot.remaining_qty = lot.quantity - done_qty
    
    @api.depends('move_ids.state')
    def _compute_progress(self):
        """计算完成进度。"""
        for lot in self:
            if not lot.move_ids:
                lot.progress = 0
            else:
                done = len(lot.move_ids.filtered(lambda m: m.state == 'done'))
                total = len(lot.move_ids)
                lot.progress = (done / total) * 100 if total else 0
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """验证数量。"""
        for lot in self:
            if lot.quantity <= 0:
                raise ValidationError(_("数量必须为正数！"))
    
    @api.onchange('product_id')
    def _onchange_product(self):
        """产品变更时更新批次。"""
        if self.product_id:
            self.route_id = self.product_id.route_id
            self.bom_id = self.product_id.bom_id
            self.uom_id = self.product_id.uom_id
    
    # 动作方法
    def action_create(self):
        """从草稿创建批次。"""
        self.write({'state': 'created'})
        return True
    
    def action_start(self):
        """开始批次生产。"""
        self.ensure_one()
        if self.state != 'created':
            raise UserError(_("批次必须处于'已创建'状态！"))
        self.write({'state': 'in_progress'})
        return True
    
    def action_hold(self):
        """暂停批次。"""
        self.ensure_one()
        return self.write({'state': 'held'})
    
    def action_resume(self):
        """从暂停恢复批次。"""
        self.ensure_one()
        self.write({'state': 'in_progress'})
        return True
    
    def action_complete(self):
        """完成批次生产。"""
        self.ensure_one()
        if self.remaining_qty > 0:
            raise UserError(_("无法完成仍有剩余数量的批次！"))
        self.write({'state': 'completed'})
        return True
    
    def action_close(self):
        """关闭批次。"""
        self.write({'state': 'closed'})
        return True
    
    def action_scrapped(self):
        """报废批次。"""
        self.write({'state': 'scrapped', 'active': False})
        return True
    
    # 记录集操作
    def track_in(self, operation_id, equipment_id=None):
        """入站到工序。"""
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
        """从工序出站。"""
        for lot in self:
            for move in lot.move_ids.filtered(lambda m: m.state == 'in_progress'):
                move.write({'state': 'done'})
        return True


class RouteModel(MesModel):
    """生产工艺路线模型。"""
    
    _name = 'mes.wip.route'
    _description = '生产工艺路线'
    _table = 'mes_wip_route'
    
    name = fields.Char(string='路线名称', required=True)
    code = fields.Char(string='编码', required=True, index=True)
    operation_ids = fields.One2many(
        'mes.wip.route.operation',
        'route_id',
        string='工序',
        copy=True,
    )
    active = fields.Boolean(default=True)


class RouteOperationModel(MesModel):
    """路线工序模型。"""
    
    _name = 'mes.wip.route.operation'
    _description = '路线工序'
    _table = 'mes_wip_route_operation'
    
    name = fields.Char(string='工序名称', required=True)
    sequence = fields.Integer(string='顺序', default=10)
    route_id = fields.Many2one(
        'mes.wip.route',
        string='路线',
        required=True,
        ondelete='cascade',
    )
    workcenter_id = fields.Many2one(
        'mes.ras.workcenter',
        string='工作中心',
    )
    time_cycle = fields.Float(string='周期时间（分钟）')
    yield_rate = fields.Float(string='期望良率 %', default=100)
```

### 3.3 MM 模块（mes_mm）

```python
# mes_mm/models/product.py
class ProductModel(MesModel):
    """产品模型。"""
    
    _name = 'mes.mm.product'
    _description = '产品'
    _table = 'mes_mm_product'
    
    name = fields.Char(string='产品名称', required=True)
    code = fields.Char(string='产品编码', required=True, index=True)
    type = fields.Selection([
        ('stockable', '库存产品'),
        ('consumable', '消耗品'),
        ('service', '服务'),
    ], string='产品类型', default='stockable')
    
    uom_id = fields.Many2one(
        'mes.uom',
        string='计量单位',
        required=True,
    )
    
    route_id = fields.Many2one(
        'mes.wip.route',
        string='生产工艺路线',
    )
    
    bom_id = fields.Many2one(
        'mes.mm.bom',
        string='物料清单',
    )
    
    tracking = fields.Selection([
        ('none', '不追踪'),
        ('lot', '按批次'),
        ('serial', '按序列号'),
    ], string='追踪', default='lot')


class StockQuantModel(MesModel):
    """库存数量模型。"""
    
    _name = 'mes.mm.stock.quant'
    _description = '库存数量'
    _table = 'mes_mm_stock_quant'
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='产品',
        required=True,
        index=True,
    )
    
    lot_id = fields.Many2one(
        'mes.wip.lot',
        string='批次',
        ondelete='cascade',
    )
    
    location_id = fields.Many2one(
        'mes.mm.location',
        string='库位',
        required=True,
    )
    
    quantity = fields.Float(
        string='数量',
        digits=(15, 3),
        required=True,
    )
    
    # 计算虚拟数量
    virtual_available = fields.Float(
        string='可用数量',
        compute='_compute_virtual',
    )
    
    @api.depends('quantity', 'location_id.reserved_qty')
    def _compute_virtual(self):
        """计算可用数量。"""
        for quant in self:
            quant.virtual_available = quant.quantity - quant.location_id.reserved_qty
```

### 3.4 SPC 模块（mes_spc）

```python
# mes_spc/models/spc_job.py
class SpcJobModel(MesModel):
    """SPC 任务模型。"""
    
    _name = 'mes.spc.job'
    _description = 'SPC 任务'
    _table = 'mes_spc_job'
    
    name = fields.Char(string='任务名称', required=True)
    
    product_id = fields.Many2one(
        'mes.mm.product',
        string='产品',
    )
    
    parameter_id = fields.Many2one(
        'mes.spc.parameter',
        string='参数',
        required=True,
    )
    
    chart_type = fields.Selection([
        ('xbar_r', 'X-bar R 图'),
        ('xbar_s', 'X-bar S 图'),
        ('imr', 'I-MR 图'),
        ('p', 'P 图'),
        ('np', 'NP 图'),
        ('c', 'C 图'),
        ('u', 'U 图'),
    ], string='图表类型', required=True)
    
    rule_ids = fields.Many2many(
        'mes.spc.rule',
        string='SPC 规则',
        default=lambda self: self.env.ref('mes_spc.rule_default'),
    )
    
    upper_spec_limit = fields.Float(string='规格上限')
    lower_spec_limit = fields.Float(string='规格下限')
    upper_control_limit = fields.Float(string='控制上限')
    lower_control_limit = fields.Float(string='控制下限')
    
    sample_size = fields.Integer(string='样本大小', default=5)
    subgroup_count = fields.Integer(string='子组数量', default=20)
    
    active = fields.Boolean(default=True)


class SpcDataModel(MesModel):
    """SPC 数据点模型。"""
    
    _name = 'mes.spc.data'
    _description = 'SPC 数据'
    _table = 'mes_spc_data'
    
    job_id = fields.Many2one(
        'mes.spc.job',
        string='SPC 任务',
        required=True,
        ondelete='cascade',
    )
    
    measurement_time = fields.Datetime(
        string='测量时间',
        default=fields.Datetime.now,
    )
    
    sample_value = fields.Float(string='样本值', required=True)
    
    subgroup_avg = fields.Float(string='子组平均值')
    subgroup_range = fields.Float(string='子组极差')
    
    equipment_id = fields.Many2one(
        'mes.ras.equipment',
        string='设备',
    )
    
    operator_id = fields.Many2one(
        'res.users',
        string='操作员',
    )
    
    state = fields.Selection([
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('ooc', '超出控制'),
    ], string='状态', default='pending')
    
    # 计算状态
    is_ooc = fields.Boolean(
        string='超出控制',
        compute='_compute_ooc',
    )
    
    @api.depends('sample_value', 'job_id.upper_control_limit', 'job_id.lower_control_limit')
    def _compute_ooc(self):
        """检查数据点是否超出控制。"""
        for data in self:
            job = data.job_id
            if job.upper_control_limit and data.sample_value > job.upper_control_limit:
                data.is_ooc = True
            elif job.lower_control_limit and data.sample_value < job.lower_control_limit:
                data.is_ooc = True
            else:
                data.is_ooc = False
```

## 4. 模块清单格式

```python
# __manifest__.py（Odoo 风格）
{
    'name': 'MES WIP 模块',
    'version': '1.0.0',
    'category': '制造',
    'summary': '在制品管理',
    'description': """
        在制品（WIP）管理模块
        ======================
        
        此模块提供：
        - 批次追踪和管理
        - 工艺路线定义和执行
        - 入站/出站操作
        - 生产进度监控
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.odoo123.com',
    
    'depends': [
        'mes_base',
        'mes_mm',
        'mes_ras',
    ],
    
    'data': [
        # 安全
        'security/ir.model.access.csv',
        
        # 视图
        'views/lot_views.xml',
        'views/route_views.xml',
        'views/menu.xml',
        
        # 报表
        'report/lot_report.xml',
    ],
    
    'demo': [
        'demo/lot_demo.xml',
        'demo/route_demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': '专有',
    
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

## 5. 模块依赖

```python
# 依赖图
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

## 6. 模块加载顺序

```python
# 加载顺序（拓扑排序）
LOAD_ORDER = [
    # 第一阶段：基础
    'mes_base',
    
    # 第二阶段：核心模块
    'mes_mm',
    'mes_ras',
    'mes_wip',
    
    # 第三阶段：数据采集
    'mes_edc',
    
    # 第四阶段：质量
    'mes_spc',
    'mes_pms',
    'mes_alm',
    'mes_qms',
]
```

## 7. 模块间通信

```python
# 领域事件（Odoo 风格）
class LotCreatedEvent:
    """批次创建时触发的事件。"""
    
    _name = 'mes.wip.lot.created'
    _namespace = 'mes.wip'
    
    def __init__(self, lot_id, product_id, quantity):
        self.lot_id = lot_id
        self.product_id = product_id
        self.quantity = quantity
        self.timestamp = datetime.now()


# 发布事件
class LotModel(MesModel):
    
    @api.model
    def create(self, vals):
        lot = super().create(vals)
        
        # 发布领域事件
        self.env['bus.bus'].sendone(
            'mes.wip.lot',
            LotCreatedEvent(
                lot_id=lot.id,
                product_id=lot.product_id.id,
                quantity=lot.quantity,
            )
        )
        
        return lot


# 监听事件
class SpcModule:
    """监听批次事件的 SPC 模块。"""
    
    def _register_hooks(self):
        """注册事件监听器。"""
        self.env['bus.bus'].add_listener(
            'mes.wip.lot.created',
            self._on_lot_created,
        )
    
    def _on_lot_created(self, event):
        """处理批次创建事件。"""
        # 触发 SPC 采样
        self.env['mes.spc.job'].action_trigger_sampling(
            product_id=event.product_id,
        )
```

## 相关文档

- [技能定义](./skill_zh_CN.md) - 开发所需专业技能
- [架构文档](./architecture_zh_CN.md) - 系统架构设计
- [编码规范](./coding-standards_zh_CN.md) - 代码标准和最佳实践
- [开发路线图](./roadmap_zh_CN.md) - 12 个月开发计划
- [Agent 定义](./agent_zh_CN.md) - AI 代理和自动化工作流
