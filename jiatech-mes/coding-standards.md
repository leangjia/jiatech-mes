# Jia Tech MES System - Coding Standards

## 1. Overview

This document defines the coding standards and best practices for the Jia Tech MES system using Python. All developers must follow these guidelines to ensure code quality, consistency, and maintainability.

## 2. Project Structure

### 2.1 Root Project Structure

```
jiatech-mes/
├── src/
│   ├── api/                    # FastAPI routes and dependencies
│   │   ├── routes/
│   │   └── deps.py
│   ├── core/                   # Core configurations
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/                 # SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/                # Pydantic schemas
│   │   └── __init__.py
│   ├── services/               # Business logic
│   │   └── __init__.py
│   ├── repositories/           # Data access layer
│   │   └── __init__.py
│   ├── utils/                  # Utility functions
│   │   └── __init__.py
│   └── main.py                 # Application entry point
├── tests/                      # Test files
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── migrations/                 # Alembic migrations
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 2.2 Module Structure (per service)

```
jiatech_mes.wip/
├── __init__.py
├── main.py                 # Service entry point
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── lots.py
│   │   └── routes.py
│   └── deps.py             # Dependency injection
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

## 3. Python Coding Standards

### 3.1 Naming Conventions

#### Classes and Modules

```python
# ✅ Good: PascalCase for classes, snake_case for modules
class LotService:
    pass

class LotState(Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"

# ✅ Good: snake_case for modules and functions
# lot_service.py
# track_in_lot()

# ❌ Bad: camelCase, unclear names
class lotService:  # ❌
    pass

class lot_state:  # ❌
    pass
```

#### Functions and Methods

```python
# ✅ Good: snake_case, verb-noun pattern
def track_in(lot_id: str, request: TrackInRequest) -> LotOperation:
    pass

def find_lots_by_state(state: LotState) -> List[Lot]:
    pass

def get_lot_by_id(lot_id: str) -> Optional[Lot]:
    pass

# ❌ Bad: unclear verbs, inconsistent patterns
def ti(lot_id):  # ❌
    pass

def get(state):  # ❌
    pass
```

#### Variables

```python
# ✅ Good: snake_case, descriptive names
lot_id: str
start_time: datetime
active_lots: List[Lot]

# ❌ Bad: abbreviations, single letters
lot_id = "L001"  # ✓ This is fine as it's clear
i = 0  # ❌
```

#### Constants

```python
# ✅ Good: SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEZONE = "Asia/Shanghai"
API_RATE_LIMIT = 1000

# ❌ Bad: magic numbers, lowercase
max = 3  # ❌
default_tz = "Asia/Shanghai"  # ❌
```

#### Database Tables and Columns

```sql
-- ✅ Good: SNAKE_CASE, descriptive
CREATE TABLE wip_lot (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL UNIQUE,
    lot_state VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP
);

-- ❌ Bad: unclear abbreviations
CREATE TABLE wip_l (
    id SERIAL,
    st VARCHAR(20),
    ct TIMESTAMP
);
```

### 3.2 Code Formatting

#### Indentation and Spacing

```python
# ✅ Good: 4 spaces, consistent spacing
def process_order(order: Order) -> None:
    if order is None:
        raise ValueError("Order cannot be null")
    
    for item in order.items:
        validate_item(item)
        process_item(item)


# ❌ Bad: tabs, inconsistent spacing
def process_order(order):
	if(order==None):
		raise ValueError("Order cannot be null")
	for item in order.items:
	validate_item(item)
```

#### Line Length

- Maximum line length: **120 characters**
- Use line breaks for long function signatures
- Break chained method calls one per line

```python
# ✅ Good: breaking long lines
active_lots = (
    lot_repository
    .filter_by(state=LotState.ACTIVE, owner_id=owner_id)
    .all()
)

# ✅ Good: parentheses for long lines
result = some_function(
    arg1="value1",
    arg2="value2",
    arg3="value3",
)

# ❌ Bad: single long line
active_lots = lot_repository.filter_by(state=LotState.ACTIVE, owner_id=owner_id).all()
```

### 3.3 Documentation

#### Module Documentation

```python
"""WIP (Work In Progress) module for lot management.

This module provides functionality for:
- Lot creation and tracking
- TrackIn/TrackOut operations
- Lot state management

Example:
    >>> from jiatech_mes.wip.services import LotService
    >>> service = LotService()
    >>> lot = service.create_lot(CreateLotRequest(...))
"""

from .models import Lot
```

#### Class Documentation

```python
class LotService:
    """Service for managing Work In Progress (WIP) lots.
    
    This service provides operations for:
    - Lot creation and tracking
    - TrackIn/TrackOut operations
    - Lot state management
    
    Attributes:
        repository: LotRepository instance for data access
        event_publisher: EventPublisher for domain events
    """
    
    def __init__(
        self,
        repository: LotRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher
```

#### Function Documentation

```python
def track_in(
    lot_id: str,
    request: TrackInRequest,
    current_user: User,
) -> LotOperation:
    """Track in a lot to a specific operation.
    
    Performs the following validations:
    - Lot must exist and be in CREATED or ACTIVE state
    - Operation must be valid for the lot's route
    - Equipment must be available
    
    Args:
        lot_id: The lot identifier
        request: The track-in request containing operation and equipment info
        current_user: The user performing the operation
        
    Returns:
        The created lot operation record
        
    Raises:
        LotNotFoundError: If lot does not exist
        InvalidOperationError: If operation is not valid
        EquipmentUnavailableError: If equipment is not available
        
    Example:
        >>> request = TrackInRequest(
        ...     operation_id="OP-001",
        ...     equipment_id="EQP-001",
        ... )
        >>> operation = track_in("LOT-001", request, user)
    """
    ...
```

### 3.4 Exception Handling

#### Custom Exceptions

```python
# ✅ Good: specific, descriptive exceptions
class MesException(Exception):
    """Base exception for MES errors."""
    
    def __init__(self, message: str, code: str = "MES_ERROR") -> None:
        super().__init__(message)
        self.code = code


class LotNotFoundError(MesException):
    """Raised when a lot is not found."""
    
    def __init__(self, lot_id: str) -> None:
        super().__init__(
            message=f"Lot not found: {lot_id}",
            code="LOT_NOT_FOUND",
        )
        self.lot_id = lot_id


class InvalidOperationError(MesException):
    """Raised when an operation is invalid."""
    
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message=message, code="INVALID_OPERATION")
        self.details = details or {}
```

#### Exception Handling Patterns

```python
# ✅ Good: specific catches, proper logging
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
            raise MesSystemError("DATABASE_ERROR", "Failed to track in lot") from e
```

### 3.5 Logging

```python
# ✅ Good: structured logging with structlog
import structlog

logger = structlog.get_logger()

class LotService:
    async def process(self, lot_id: str) -> None:
        logger.info("processing_lot", lot_id=lot_id)
        
        try:
            # operations
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

# ❌ Bad: f-strings for sensitive data, wrong log levels
logger.info(f"User login: {username} {password}")  # ❌
logger.debug(f"Processing payment: amount={amount}")  # ❌
```

### 3.6 Type Hints

```python
# ✅ Good: comprehensive type hints
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

# ✅ Good: using modern union syntax
def process(data: str | None) -> dict[str, Any]:
    pass

# ✅ Good: TypeAlias for complex types
from typing import TypeAlias

LotFilter: TypeAlias = Dict[str, Any]
LotList: TypeAlias = List[Lot]
```

### 3.7 Async/Await

```python
# ✅ Good: async for I/O operations
from typing import AsyncIterator

class LotRepository:
    async def get_by_lot_id(self, lot_id: str) -> Optional[Lot]:
        """Get lot by ID asynchronously."""
        result = await self.session.execute(
            select(Lot).where(Lot.lot_id == lot_id)
        )
        return result.scalar_one_or_none()
    
    async def list_lots(
        self,
        state: Optional[LotState] = None,
    ) -> List[Lot]:
        """List lots with optional filtering."""
        query = select(Lot)
        if state:
            query = query.where(Lot.state == state)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def iterate_lots(self) -> AsyncIterator[Lot]:
        """Iterate over all lots asynchronously."""
        result = await self.session.execute(select(Lot))
        for lot in result.scalars():
            yield lot
```

### 3.8 Immutability

```python
# ✅ Good: frozen dataclasses for DTOs
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class LotDTO:
    """Immutable DTO for lot data."""
    lot_id: str
    lot_state: str
    product_id: str
    quantity: float
    created_time: datetime

# ✅ Good: using.copy() for mutable data
def update_lot_data(lot: dict, updates: dict) -> dict:
    new_lot = lot.copy()
    new_lot.update(updates)
    return new_lot
```

## 4. FastAPI Standards

### 4.1 REST API Design

#### URL Structure

```python
# ✅ Good: resource-oriented, consistent
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

# ❌ Bad: verbs in URL, inconsistent
@router.get("/getLots")           # ❌
@router.post("/createLot")         # ❌
@router.post("/lotTrackIn")        # ❌
```

#### Router Structure

```python
# ✅ Good: clean, focused router
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

### 4.2 Schema Design

```python
# ✅ Good: comprehensive validation with Pydantic
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
    """Request schema for creating a lot."""
    
    product_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Product identifier",
        examples=["PROD-001"],
    )
    
    quantity: Decimal = Field(
        ...,
        gt=0,
        max_digits=15,
        decimal_places=3,
        description="Lot quantity",
    )
    
    route_id: int = Field(
        ...,
        gt=0,
        description="Route identifier",
    )
    
    components: list[CreateLotComponentRequest] = Field(
        default_factory=list,
        description="Lot components",
    )
    
    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        if not v.startswith("PROD-"):
            raise ValueError("Product ID must start with 'PROD-'")
        return v


class LotDTO(BaseModel):
    """Response schema for lot data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    lot_id: str
    lot_state: LotState
    product_id: str
    quantity: Decimal
    created_time: datetime
    updated_time: Optional[datetime] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    model_config = ConfigDict(generic_json=True)
    
    data: list[T]
    page: int
    size: int
    total_elements: int
    total_pages: int
```

### 4.3 Dependency Injection

```python
# ✅ Good: dependency injection
from fastapi import Depends, HTTPException, status
from typing import Annotated

async def get_lot_service() -> LotService:
    """Dependency to get lot service instance."""
    return LotService(
        repository=LotRepository(session=get_db_session()),
        event_publisher=EventPublisher(),
    )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Dependency to get current authenticated user."""
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
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# Usage
@router.get("/{lot_id}")
async def get_lot(
    lot_id: str,
    service: Annotated[LotService, Depends(get_lot_service)],
) -> LotDTO:
    lot = await service.get_by_lot_id(lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return LotDTO.model_validate(lot)
```

### 4.4 Error Handling

```python
# ✅ Good: consistent error responses
from fastapi import HTTPException, status

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    success: bool = False
    error: ErrorDetail


class ErrorDetail(BaseModel):
    """Error detail model."""
    
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

## 5. Database Standards

### 5.1 SQLAlchemy Models

```python
# ✅ Good: SQLAlchemy 2.0 style models
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
    """WIP Lot model."""
    
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
    
    # Relationships
    route: Mapped["Route"] = relationship(back_populates="lots")
    operations: Mapped[list["LotOperation"]] = relationship(
        back_populates="lot",
        cascade="all, delete-orphan",
    )
```

### 5.2 Repository Pattern

```python
# ✅ Good: repository with async support
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class LotRepository:
    """Repository for lot data access."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_lot_id(self, lot_id: str) -> Optional[Lot]:
        """Get lot by lot_id."""
        stmt = select(Lot).where(Lot.lot_id == lot_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, lot_id: int) -> Optional[Lot]:
        """Get lot by primary key."""
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
        """List lots with optional filtering."""
        stmt = select(Lot)
        
        if state:
            stmt = stmt.where(Lot.lot_state == state)
        if product_id:
            stmt = stmt.where(Lot.product_id == product_id)
        
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count(self, state: Optional[str] = None) -> int:
        """Count lots with optional filtering."""
        stmt = select(func.count(Lot.id))
        if state:
            stmt = stmt.where(Lot.lot_state == state)
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def save(self, lot: Lot) -> Lot:
        """Save or update a lot."""
        self.session.add(lot)
        await self.session.flush()
        await self.session.refresh(lot)
        return lot
    
    async def delete(self, lot: Lot) -> None:
        """Delete a lot."""
        await self.session.delete(lot)
        await self.session.flush()
```

### 5.3 Migrations (Alembic)

```bash
# ✅ Good: Alembic migration structure
# migrations/versions/2026_03_22_0001_create_wip_tables.py

"""Create WIP tables for lot management.

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
    # Create wip_lot table
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
    
    # Create indexes
    op.create_index('idx_wip_lot_state', 'wip_lot', ['lot_state'])
    op.create_index('idx_wip_lot_product', 'wip_lot', ['product_id'])
    op.create_index('idx_wip_lot_created', 'wip_lot', ['created_time'])


def downgrade() -> None:
    op.drop_index('idx_wip_lot_created', table_name='wip_lot')
    op.drop_index('idx_wip_lot_product', table_name='wip_lot')
    op.drop_index('idx_wip_lot_state', table_name='wip_lot')
    op.drop_table('wip_lot')
```

## 6. Testing Standards

### 6.1 Test Structure

```python
# ✅ Good: clear test structure with pytest
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from jiatech_mes.wip.services import LotService
from jiatech_mes.wip.schemas import CreateLotRequest, LotDTO
from jiatech_mes.wip.exceptions import LotNotFoundError


class TestLotService:
    """Test suite for LotService."""
    
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_publisher(self) -> AsyncMock:
        """Create mock event publisher."""
        return AsyncMock()
    
    @pytest.fixture
    def lot_service(
        self,
        mock_repository,
        mock_event_publisher,
    ) -> LotService:
        """Create service with mocked dependencies."""
        return LotService(
            repository=mock_repository,
            event_publisher=mock_event_publisher,
        )
    
    @pytest.fixture
    def sample_lot(self) -> MagicMock:
        """Create sample lot."""
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
        """Should successfully track in lot with valid request."""
        # Arrange
        lot_id = "LOT-001"
        request = TrackInRequest(
            operation_id="OP-001",
            equipment_id="EQP-001",
        )
        
        mock_repository.get_by_lot_id.return_value = sample_lot
        mock_repository.save.return_value = sample_lot
        
        # Act
        result = await lot_service.track_in(lot_id, request)
        
        # Assert
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
        """Should raise exception when lot not found."""
        # Arrange
        lot_id = "INVALID"
        request = TrackInRequest(
            operation_id="OP-001",
            equipment_id="EQP-001",
        )
        
        mock_repository.get_by_lot_id.return_value = None
        
        # Act & Assert
        with pytest.raises(LotNotFoundError) as exc_info:
            await lot_service.track_in(lot_id, request)
        
        assert lot_id in str(exc_info.value)
```

### 6.2 Test Coverage Requirements

| Component | Coverage Target |
|-----------|-----------------|
| Services layer | 80%+ |
| Repository layer | N/A (integration tests) |
| API routes | 70%+ |
| Complex business logic | 90%+ |
| Utility classes | 80%+ |

### 6.3 Integration Tests

```python
# ✅ Good: integration test with testcontainers
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
    """Create test database."""
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
    """Should create and retrieve lot."""
    # Setup
    async_session = sessionmaker(
        test_db,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    # Test
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

## 7. Git Standards

### 7.1 Branch Naming

```
feature/MES-123-lot-tracking
bugfix/MES-456-fix-trackin-error
hotfix/MES-789-critical-security-fix
release/v1.0.0
chore/update-dependencies
```

### 7.2 Commit Messages

```
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Formatting, missing semicolons, etc
refactor: Code refactoring
test:     Adding tests
chore:    Maintenance tasks

# Examples
feat(wip): add lot track_in operation

- Validate equipment availability before track_in
- Create lot operation record
- Publish track_in event for downstream services

Closes MES-123

fix(alm): correct alarm escalation timeout calculation

The escalation timeout was being calculated incorrectly when
crossing timezone boundaries. This fix ensures consistent
calculation based on UTC.

Fixes MES-456
```

### 7.3 Pull Request Guidelines

```markdown
## Summary
Brief description of changes.

## Changes
- Change 1
- Change 2

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines (ruff, black)
- [ ] Tests pass
- [ ] Type hints complete
- [ ] Documentation updated
- [ ] No lint warnings
```

## 8. Code Review Checklist

### 8.1 Functionality
- [ ] Code accomplishes the intended purpose
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs or infinite loops

### 8.2 Design
- [ ] Follows SOLID principles
- [ ] Appropriate design patterns used
- [ ] No code duplication
- [ ] Proper separation of concerns

### 8.3 Performance
- [ ] No N+1 query problems
- [ ] Proper use of async/await
- [ ] Efficient algorithms used
- [ ] Indexes properly defined

### 8.4 Security
- [ ] No SQL injection vulnerabilities (use parameterized queries)
- [ ] Input validation present
- [ ] Sensitive data not logged
- [ ] Proper authorization checks

### 8.5 Maintainability
- [ ] Code is readable and well-documented
- [ ] Type hints are complete
- [ ] Unit tests cover core functionality
- [ ] Proper module structure
