# Jia Tech MES 系统 - 编码规范

## 1. 概述

本文档定义了 Jia Tech MES 系统的编码标准和最佳实践。使用 Python 开发时，所有开发人员必须遵循这些准则，以确保代码质量、一致性和可维护性。

## 2. 项目结构

### 2.1 根项目结构

```
jiatech-mes/
├── src/
│   ├── api/                    # FastAPI 路由和依赖
│   │   ├── routes/
│   │   └── deps.py
│   ├── core/                   # 核心配置
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/                 # SQLAlchemy 模型
│   │   └── __init__.py
│   ├── schemas/                # Pydantic 模式
│   │   └── __init__.py
│   ├── services/               # 业务逻辑
│   │   └── __init__.py
│   ├── repositories/           # 数据访问层
│   │   └── __init__.py
│   ├── utils/                  # 工具函数
│   │   └── __init__.py
│   └── main.py                 # 应用入口点
├── tests/                      # 测试文件
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── migrations/                 # Alembic 迁移
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 2.2 模块结构（每个服务）

```
jiatech_mes.wip/
├── __init__.py
├── main.py                 # 服务入口点
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── lots.py
│   │   └── routes.py
│   └── deps.py             # 依赖注入
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── models/
│   ├── __init__.py
│   ├── lot.py
│   └── route.py
├── schemas/
│   ├── __init__.py
│   ├── lot.py
│   └── route.py
├── services/
│   ├── __init__.py
│   ├── lot_service.py
│   └── route_service.py
├── repositories/
│   ├── __init__.py
│   ├── lot_repository.py
│   └── route_repository.py
├── events/
│   ├── __init__.py
│   └── publishers.py
└── exceptions.py
```

## 3. Python 编码标准

### 3.1 命名规范

#### 类和模块

```python
# ✅ 正确：类用 PascalCase，模块用 snake_case
class LotService:
    pass

class LotState(Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"

# ✅ 正确：模块和函数用 snake_case
# lot_service.py
# track_in_lot()

# ❌ 错误：camelCase，不清晰的名称
class lotService:  # ❌
    pass

class lot_state:  # ❌
    pass
```

#### 函数和方法

```python
# ✅ 正确：snake_case，动宾结构
def track_in(lot_id: str, request: TrackInRequest) -> LotOperation:
    pass

def find_lots_by_state(state: LotState) -> List[Lot]:
    pass

def get_lot_by_id(lot_id: str) -> Optional[Lot]:
    pass

# ❌ 错误：动词不清晰，模式不一致
def ti(lot_id):  # ❌
    pass

def get(state):  # ❌
    pass
```

#### 变量

```python
# ✅ 正确：snake_case，描述性名称
lot_id: str
start_time: datetime
active_lots: List[Lot]

# ❌ 错误：缩写，单字母
lot_id = "L001"  # ✓ 这个可以因为它很清晰
i = 0  # ❌
```

#### 常量

```python
# ✅ 正确：SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEZONE = "Asia/Shanghai"
API_RATE_LIMIT = 1000

# ❌ 错误：魔术数字，小写
max = 3  # ❌
default_tz = "Asia/Shanghai"  # ❌
```

#### 数据库表和列

```sql
-- ✅ 正确：SNAKE_CASE，描述性
CREATE TABLE wip_lot (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL UNIQUE,
    lot_state VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP
);

-- ❌ 错误：不清晰的缩写
CREATE TABLE wip_l (
    id SERIAL,
    st VARCHAR(20),
    ct TIMESTAMP
);
```

### 3.2 代码格式化

#### 缩进和空格

```python
# ✅ 正确：4 空格，一致的间距
def process_order(order: Order) -> None:
    if order is None:
        raise ValueError("Order cannot be null")
    
    for item in order.items:
        validate_item(item)
        process_item(item)


# ❌ 错误：制表符，间距不一致
def process_order(order):
	if(order==None):
		raise ValueError("Order cannot be null")
	for item in order.items:
	validate_item(item)
```

#### 行长度

- 最大行长度：**120 个字符**
- 长函数签名使用换行
- 链式方法调用每行一个

```python
# ✅ 正确：断开长行
active_lots = (
    lot_repository
    .filter_by(state=LotState.ACTIVE, owner_id=owner_id)
    .all()
)

# ✅ 正确：括号用于长行
result = some_function(
    arg1="value1",
    arg2="value2",
    arg3="value3",
)

# ❌ 错误：单行长行
active_lots = lot_repository.filter_by(state=LotState.ACTIVE, owner_id=owner_id).all()
```

### 3.3 文档

#### 模块文档

```python
"""WIP（在制品）模块用于批次管理。

此模块提供以下功能：
- 批次创建和追踪
- 入站/出站操作
- 批次状态管理

示例：
    >>> from jiatech_mes.wip.services import LotService
    >>> service = LotService()
    >>> lot = service.create_lot(CreateLotRequest(...))
"""

from .models import Lot
```

#### 类文档

```python
class LotService:
    """管理在制品批次的服务。
    
    此服务提供以下操作：
    - 批次创建和追踪
    - 入站/出站操作
    - 批次状态管理
    
    属性：
        repository: 用于数据访问的 LotRepository 实例
        event_publisher: 用于领域事件的 EventPublisher
    """
    
    def __init__(
        self,
        repository: LotRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher
```

#### 函数文档

```python
def track_in(
    lot_id: str,
    request: TrackInRequest,
    current_user: User,
) -> LotOperation:
    """将批次入站到特定工序。
    
    执行以下验证：
    - 批次必须存在且处于 CREATED 或 ACTIVE 状态
    - 工序必须对批次的工艺路线有效
    - 设备必须可用
    
    参数：
        lot_id: 批次标识符
        request: 包含工序和设备信息的入站请求
        current_user: 执行操作的用户
        
    返回：
        创建的批次操作记录
        
    异常：
        LotNotFoundError: 如果批次不存在
        InvalidOperationError: 如果工序无效
        EquipmentUnavailableError: 如果设备不可用
        
    示例：
        >>> request = TrackInRequest(
        ...     operation_id="OP-001",
        ...     equipment_id="EQP-001",
        ... )
        >>> operation = track_in("LOT-001", request, user)
    """
    ...
```

### 3.4 异常处理

#### 自定义异常

```python
# ✅ 正确：具体、描述性的异常
class MesException(Exception):
    """MES 错误的基类异常。"""
    
    def __init__(self, message: str, code: str = "MES_ERROR") -> None:
        super().__init__(message)
        self.code = code


class LotNotFoundError(MesException):
    """当批次未找到时抛出。"""
    
    def __init__(self, lot_id: str) -> None:
        super().__init__(
            message=f"批次未找到: {lot_id}",
            code="LOT_NOT_FOUND",
        )
        self.lot_id = lot_id


class InvalidOperationError(MesException):
    """当操作无效时抛出。"""
    
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message=message, code="INVALID_OPERATION")
        self.details = details or {}
```

#### 异常处理模式

```python
# ✅ 正确：具体捕获，适当日志
import structlog

logger = structlog.get_logger()

class LotService:
    async def track_in(
        self,
        lot_id: str,
        request: TrackInRequest,
    ) -> LotOperation:
        try:
            await self._validate_request(request)
            lot = await self.repository.get_by_lot_id(lot_id)
            
            if lot is None:
                raise LotNotFoundError(lot_id)
            
            operation = await self._perform_track_in(lot, request)
            await self.repository.save(lot)
            await self.event_publisher.publish(LotTrackInEvent(lot_id=lot_id))
            
            return operation
            
        except LotNotFoundError:
            logger.warning("lot_not_found", lot_id=lot_id)
            raise
        except DatabaseError as e:
            logger.error(
                "database_error_during_track_in",
                lot_id=lot_id,
                error=str(e),
            )
            raise MesSystemError("DATABASE_ERROR", "批次入站失败") from e
```

### 3.5 日志

```python
# ✅ 正确：使用 structlog 的结构化日志
import structlog

logger = structlog.get_logger()

class LotService:
    async def process(self, lot_id: str) -> None:
        logger.info("processing_lot", lot_id=lot_id)
        
        try:
            # 操作
            logger.debug(
                "lot_processed_successfully",
                lot_id=lot_id,
                result=result,
            )
        except Exception as e:
            logger.error(
                "failed_to_process_lot",
                lot_id=lot_id,
                error=str(e),
                exc_info=True,
            )
            raise

# ❌ 错误：f-string 用于敏感数据，错误的日志级别
logger.info(f"User login: {username} {password}")  # ❌
logger.debug(f"Processing payment: amount={amount}")  # ❌
```

### 3.6 类型提示

```python
# ✅ 正确：全面的类型提示
from typing import Optional, List, Dict, Any
from datetime import datetime

def track_in(
    lot_id: str,
    request: TrackInRequest,
) -> LotOperation:
    pass

def find_lots(
    state: Optional[LotState] = None,
    product_id: Optional[str] = None,
) -> List[Lot]:
    pass

def get_lot_by_id(lot_id: str) -> Optional[Lot]:
    pass

# ✅ 正确：使用现代联合语法
def process(data: str | None) -> dict[str, Any]:
    pass

# ✅ 正确：TypeAlias 用于复杂类型
from typing import TypeAlias

LotFilter: TypeAlias = Dict[str, Any]
LotList: TypeAlias = List[Lot]
```

### 3.7 异步/等待

```python
# ✅ 正确：I/O 操作使用 async
from typing import AsyncIterator

class LotRepository:
    async def get_by_lot_id(self, lot_id: str) -> Optional[Lot]:
        """异步按 ID 获取批次。"""
        result = await self.session.execute(
            select(Lot).where(Lot.lot_id == lot_id)
        )
        return result.scalar_one_or_none()
    
    async def list_lots(
        self,
        state: Optional[LotState] = None,
    ) -> List[Lot]:
        """带可选过滤的批次列表。"""
        query = select(Lot)
        if state:
            query = query.where(Lot.state == state)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def iterate_lots(self) -> AsyncIterator[Lot]:
        """异步遍历所有批次。"""
        result = await self.session.execute(select(Lot))
        for lot in result.scalars():
            yield lot
```

### 3.8 不可变性

```python
# ✅ 正确：DTO 使用 frozen dataclasses
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class LotDTO:
    """批次数据的不可变 DTO。"""
    lot_id: str
    lot_state: str
    product_id: str
    quantity: float
    created_time: datetime

# ✅ 正确：可变数据使用 .copy()
def update_lot_data(lot: dict, updates: dict) -> dict:
    new_lot = lot.copy()
    new_lot.update(updates)
    return new_lot
```

## 4. FastAPI 标准

### 4.1 REST API 设计

#### URL 结构

```python
# ✅ 正确：面向资源，一致
from fastapi import APIRouter

router = APIRouter(prefix="/api/wip/lots", tags=["lots"])

@router.get("")                    # GET /api/wip/lots
async def get_lots():
    pass

@router.post("")                   # POST /api/wip/lots
async def create_lot():
    pass

@router.get("/{lot_id}")           # GET /api/wip/lots/{lot_id}
async def get_lot(lot_id: str):
    pass

@router.post("/{lot_id}/track-in") # POST /api/wip/lots/{lot_id}/track-in
async def track_in_lot(lot_id: str):
    pass

# ❌ 错误：URL 中使用动词，不一致
@router.get("/getLots")           # ❌
@router.post("/createLot")         # ❌
@router.post("/lotTrackIn")        # ❌
```

#### 路由结构

```python
# ✅ 正确：清晰、聚焦的路由
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

router = APIRouter(prefix="/api/wip/lots", tags=["lots"])


@router.get("")
async def get_lots(
    page: int = Query(default=0, ge=0),
    size: int = Query(default=20, ge=1, le=100),
    state: str | None = None,
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaginatedResponse[LotDTO]:
    lots = await lot_service.find_lots(
        page=page,
        size=size,
        state=state,
    )
    return PaginatedResponse(
        data=[LotDTO.model_validate(lot) for lot in lots],
        page=page,
        size=size,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_lot(
    request: CreateLotRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LotDTO:
    lot = await lot_service.create(
        data=request,
        created_by=current_user.user_id,
    )
    return LotDTO.model_validate(lot)
```

### 4.2 模式设计

```python
# ✅ 正确：使用 Pydantic 进行全面验证
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class LotState(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    HELD = "HELD"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class CreateLotRequest(BaseModel):
    """创建批次的请求模式。"""
    
    product_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="产品标识符",
        examples=["PROD-001"],
    )
    
    quantity: Decimal = Field(
        ...,
        gt=0,
        max_digits=15,
        decimal_places=3,
        description="批次数量",
    )
    
    route_id: int = Field(
        ...,
        gt=0,
        description="工艺路线标识符",
    )
    
    components: list[CreateLotComponentRequest] = Field(
        default_factory=list,
        description="批次组件",
    )
    
    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        if not v.startswith("PROD-"):
            raise ValueError("产品 ID 必须以 'PROD-' 开头")
        return v


class LotDTO(BaseModel):
    """批次数据的响应模式。"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    lot_id: str
    lot_state: LotState
    product_id: str
    quantity: Decimal
    created_time: datetime
    updated_time: Optional[datetime] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应。"""
    
    model_config = ConfigDict(generic_json=True)
    
    data: list[T]
    page: int
    size: int
    total_elements: int
    total_pages: int
```

### 4.3 依赖注入

```python
# ✅ 正确：依赖注入
from fastapi import Depends, HTTPException, status
from typing import Annotated

async def get_lot_service() -> LotService:
    """获取批次服务实例的依赖。"""
    return LotService(
        repository=LotRepository(session=get_db_session()),
        event_publisher=EventPublisher(),
    )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """获取当前已认证用户的依赖。"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证凭据",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
        )
    
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return user


# 使用
@router.get("/{lot_id}")
async def get_lot(
    lot_id: str,
    service: Annotated[LotService, Depends(get_lot_service)],
) -> LotDTO:
    lot = await service.get_by_lot_id(lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="批次未找到")
    return LotDTO.model_validate(lot)
```

### 4.4 错误处理

```python
# ✅ 正确：一致的错误响应
from fastapi import HTTPException, status

class ErrorResponse(BaseModel):
    """标准错误响应。"""
    
    success: bool = False
    error: ErrorDetail


class ErrorDetail(BaseModel):
    """错误详情模型。"""
    
    code: str
    message: str
    details: dict | None = None


@router.exception_handler(LotNotFoundError)
async def lot_not_found_handler(
    request: Request,
    exc: LotNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error=ErrorDetail(
                code="LOT_NOT_FOUND",
                message=str(exc),
                details={"lot_id": exc.lot_id},
            )
        ).model_dump(),
    )


@router.exception_handler(MesException)
async def mes_exception_handler(
    request: Request,
    exc: MesException,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=str(exc),
            )
        ).model_dump(),
    )
```

## 5. 数据库标准

### 5.1 SQLAlchemy 模型

```python
# ✅ 正确：SQLAlchemy 2.0 风格模型
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String,
    Enum,
    DateTime,
    Numeric,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from typing import Optional


class Base(DeclarativeBase):
    pass


class Lot(Base):
    """WIP 批次模型。"""
    
    __tablename__ = "wip_lot"
    __table_args__ = (
        Index("idx_wip_lot_state", "lot_state"),
        Index("idx_wip_lot_product", "product_id"),
        Index("idx_wip_lot_created", "created_time"),
        {"schema": "wip"},
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    lot_id: Mapped[str] = mapped_column(String(50), unique=True)
    lot_state: Mapped[str] = mapped_column(String(20), default="CREATED")
    product_id: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wip.route.id"))
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
    )
    
    # 关系
    route: Mapped["Route"] = relationship(back_populates="lots")
    operations: Mapped[list["LotOperation"]] = relationship(
        back_populates="lot",
        cascade="all, delete-orphan",
    )
```

### 5.2 仓储模式

```python
# ✅ 正确：带异步支持的仓储
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class LotRepository:
    """批次数据访问的仓储。"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_lot_id(self, lot_id: str) -> Optional[Lot]:
        """按 lot_id 获取批次。"""
        stmt = select(Lot).where(Lot.lot_id == lot_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, lot_id: int) -> Optional[Lot]:
        """按主键获取批次。"""
        stmt = select(Lot).where(Lot.id == lot_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_lots(
        self,
        state: Optional[str] = None,
        product_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Lot]:
        """带可选过滤的批次列表。"""
        stmt = select(Lot)
        
        if state:
            stmt = stmt.where(Lot.lot_state == state)
        if product_id:
            stmt = stmt.where(Lot.product_id == product_id)
        
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count(self, state: Optional[str] = None) -> int:
        """带可选过滤的批次计数。"""
        stmt = select(func.count(Lot.id))
        if state:
            stmt = stmt.where(Lot.lot_state == state)
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def save(self, lot: Lot) -> Lot:
        """保存或更新批次。"""
        self.session.add(lot)
        await self.session.flush()
        await self.session.refresh(lot)
        return lot
    
    async def delete(self, lot: Lot) -> None:
        """删除批次。"""
        await self.session.delete(lot)
        await self.session.flush()
```

### 5.3 迁移（Alembic）

```bash
# ✅ 正确：Alembic 迁移结构
# migrations/versions/2026_03_22_0001_create_wip_tables.py

"""创建批次管理的 WIP 表。

Revision ID: 2026_03_22_0001
Revises: 
Create Date: 2026-03-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '2026_03_22_0001'
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # 创建 wip_lot 表
    op.create_table(
        'wip_lot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lot_id', sa.String(50), nullable=False),
        sa.Column('lot_state', sa.String(20), nullable=False),
        sa.Column('product_id', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lot_id'),
    )
    
    # 创建索引
    op.create_index('idx_wip_lot_state', 'wip_lot', ['lot_state'])
    op.create_index('idx_wip_lot_product', 'wip_lot', ['product_id'])
    op.create_index('idx_wip_lot_created', 'wip_lot', ['created_time'])


def downgrade() -> None:
    op.drop_index('idx_wip_lot_created', table_name='wip_lot')
    op.drop_index('idx_wip_lot_product', table_name='wip_lot')
    op.drop_index('idx_wip_lot_state', table_name='wip_lot')
    op.drop_table('wip_lot')
```

## 6. 测试标准

### 6.1 测试结构

```python
# ✅ 正确：使用 pytest 的清晰测试结构
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from jiatech_mes.wip.services import LotService
from jiatech_mes.wip.schemas import CreateLotRequest, LotDTO
from jiatech_mes.wip.exceptions import LotNotFoundError


class TestLotService:
    """LotService 测试套件。"""
    
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """创建模拟仓储。"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_publisher(self) -> AsyncMock:
        """创建模拟事件发布器。"""
        return AsyncMock()
    
    @pytest.fixture
    def lot_service(
        self,
        mock_repository,
        mock_event_publisher,
    ) -> LotService:
        """使用模拟依赖创建服务。"""
        return LotService(
            repository=mock_repository,
            event_publisher=mock_event_publisher,
        )
    
    @pytest.fixture
    def sample_lot(self) -> MagicMock:
        """创建示例批次。"""
        lot = MagicMock()
        lot.id = 1
        lot.lot_id = "LOT-001"
        lot.lot_state = "ACTIVE"
        lot.product_id = "PROD-001"
        lot.quantity = Decimal("100.000")
        return lot
    
    @pytest.mark.asyncio
    async def test_track_in_successfully(
        self,
        lot_service,
        mock_repository,
        mock_event_publisher,
        sample_lot,
    ) -> None:
        """应该使用有效请求成功入站批次。"""
        # 安排
        lot_id = "LOT-001"
        request = TrackInRequest(
            operation_id="OP-001",
            equipment_id="EQP-001",
        )
        
        mock_repository.get_by_lot_id.return_value = sample_lot
        mock_repository.save.return_value = sample_lot
        
        # 行动
        result = await lot_service.track_in(lot_id, request)
        
        # 断言
        assert result is not None
        assert result.lot_id == lot_id
        mock_repository.save.assert_called_once()
        mock_event_publisher.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_track_in_raises_when_lot_not_found(
        self,
        lot_service,
        mock_repository,
    ) -> None:
        """当批次未找到时应该抛出异常。"""
        # 安排
        lot_id = "INVALID"
        request = TrackInRequest(
            operation_id="OP-001",
            equipment_id="EQP-001",
        )
        
        mock_repository.get_by_lot_id.return_value = None
        
        # 行动和断言
        with pytest.raises(LotNotFoundError) as exc_info:
            await lot_service.track_in(lot_id, request)
        
        assert lot_id in str(exc_info.value)
```

### 6.2 测试覆盖率要求

| 组件 | 覆盖率目标 |
|------|-----------|
| 服务层 | 80%+ |
| 仓储层 | N/A（集成测试）|
| API 路由 | 70%+ |
| 复杂业务逻辑 | 90%+ |
| 工具类 | 80%+ |

### 6.3 集成测试

```python
# ✅ 正确：使用 testcontainers 的集成测试
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from jiatech_mes.main import app
from jiatech_mes.core.database import get_db_session
from jiatech_mes.wip.models import Base, Lot


@pytest_asyncio.fixture
async def test_db():
    """创建测试数据库。"""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/mes_test",
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_lot(test_db):
    """应该创建和检索批次。"""
    # 设置
    async_session = sessionmaker(
        test_db,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    # 测试
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/wip/lots",
            json={
                "product_id": "PROD-001",
                "quantity": "100.000",
                "route_id": 1,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "PROD-001"
```

## 7. Git 标准

### 7.1 分支命名

```
feature/MES-123-lot-tracking
bugfix/MES-456-fix-trackin-error
hotfix/MES-789-critical-security-fix
release/v1.0.0
chore/update-dependencies
```

### 7.2 提交信息

```
# 格式
<类型>(<范围>): <主题>

<正文>

<页脚>

# 类型
feat:     新功能
fix:      错误修复
docs:     文档更改
style:    格式，缺少分号等
refactor: 代码重构
test:     添加测试
chore:    维护任务

# 示例
feat(wip): 添加批次入站操作

- 入站前验证设备可用性
- 创建批次操作记录
- 发布入站事件给下游服务

Closes MES-123

fix(alm): 修正报警升级超时计算

升级超时在跨越时区边界时计算不正确。
此修复确保基于 UTC 的一致计算。

Fixes MES-456
```

### 7.3 Pull Request 指南

```markdown
## 摘要
变更的简要描述。

## 变更
- 变更 1
- 变更 2

## 变更类型
- [ ] 错误修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新

## 测试
如何测试的？

## 检查清单
- [ ] 代码遵循风格指南（ruff, black）
- [ ] 测试通过
- [ ] 类型提示完整
- [ ] 文档已更新
- [ ] 无 lint 警告
```

## 8. 代码评审检查清单

### 8.1 功能性
- [ ] 代码实现预期目的
- [ ] 边界情况已处理
- [ ] 错误处理适当
- [ ] 无明显 bug 或无限循环

### 8.2 设计
- [ ] 遵循 SOLID 原则
- [ ] 使用适当的设计模式
- [ ] 无代码重复
- [ ] 适当关注点分离

### 8.3 性能
- [ ] 无 N+1 查询问题
- [ ] 适当使用 async/await
- [ ] 使用高效算法
- [ ] 索引正确定义

### 8.4 安全性
- [ ] 无 SQL 注入漏洞（使用参数化查询）
- [ ] 存在输入验证
- [ ] 敏感数据不记录日志
- [ ] 适当授权检查

### 8.5 可维护性
- [ ] 代码可读且文档完善
- [ ] 类型提示完整
- [ ] 单元测试覆盖核心功能
- [ ] 适当的模块结构

## 相关文档

- [技能定义](./skill_zh_CN.md) - 开发所需专业技能
- [架构文档](./architecture_zh_CN.md) - 系统架构设计
- [模块设计](./modules_zh_CN.md) - MES 模块规格
- [开发路线图](./roadmap_zh_CN.md) - 12 个月开发计划
- [Agent 定义](./agent_zh_CN.md) - AI 代理和自动化工作流
