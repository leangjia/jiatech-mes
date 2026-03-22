"""Jia Tech MES ORM Models.

This module provides the Odoo-inspired ORM models including:
- BaseModel: Abstract base for all models
- Model: Standard persistent model
- AbstractModel: Abstract model (no table)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from jiatech_mes.orm.api import Environment
    from jiatech_mes.orm.fields import Field

_logger = logging.getLogger(__name__)


class BaseModel:
    """Abstract base model for all Odoo-style models.
    
    This class provides the foundation for ORM functionality including:
    - Automatic model registration via metaclass
    - Field management
    - CRUD operations
    - Recordset operations
    
    Attributes:
        _name: Unique model name (e.g., 'res.users')
        _description: Human-readable description
        _table: Database table name
        _rec_name: Field to use for display name
        _order: Default ordering
        _inherit: Parent models to inherit from
        _inherits: Dict of inherited models
        _abstract: If True, no database table created
        _transient: If True, transient model (auto-cleanup)
    
    Example:
        class ResUsers(BaseModel):
            _name = 'res.users'
            _description = 'Users'
            
            name = fields.Char(string='Name', required=True)
            login = fields.Char(string='Login', required=True)
    """
    
    _name: ClassVar[str | None] = None
    _description: ClassVar[str | None] = None
    _table: ClassVar[str | None] = None
    _rec_name: ClassVar[str] = 'name'
    _order: ClassVar[str] = 'id'
    _inherit: ClassVar[str | list[str] | tuple[str, ...]] = ()
    _inherits: ClassVar[dict[str, str]] = {}
    _abstract: ClassVar[bool] = True
    _transient: ClassVar[bool] = False
    _auto: ClassVar[bool] = True
    _log_access: ClassVar[bool] = True
    
    _fields: ClassVar[dict[str, Field]] = {}
    _defaults: ClassVar[dict[str, Any]] = {}
    _constraints: ClassVar[list[tuple]] = []
    _sql_constraints: ClassVar[list[tuple[str, str, str]]] = []
    
    __slots__: ClassVar[list[str]] = ['id', '_values', '_modified', '_env', '_parent_store']
    
    def __init__(self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} is a model class, not an instance. "
            f"Use env['{self._name}'] to get a recordset."
        )
    
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Prevent direct instantiation of model classes."""
        if cls is Model or cls._name is None:
            raise NotImplementedError(
                f"{cls.__name__} is a model class, not an instance."
            )
        return super().__new__(cls)
    
    @classmethod
    def _build_model(cls, registry: Any, cr: Any) -> type[BaseModel]:
        """Build the model class for registry."""
        _logger.debug("Building model: %s", cls._name)
        return cls
    
    @classmethod
    def _register_setup(cls) -> None:
        """Register fields and setup the model class."""
        if not hasattr(cls, '_original_module'):
            cls._original_module = cls.__module__
        
        for attr_name in dir(cls):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(cls, attr_name)
            if hasattr(attr, '_field_definition'):
                attr._field_name = attr_name
                cls._fields[attr_name] = attr
    
    @classmethod
    def fields_get(cls, cr: Any = None, uid: int = None, context: dict | None = None) -> dict:
        """Get field definitions."""
        result = {}
        for name, field in cls._fields.items():
            result[name] = {
                'type': getattr(field, 'type', 'unknown'),
                'string': getattr(field, 'string', ''),
                'help': getattr(field, 'help', ''),
                'readonly': getattr(field, 'readonly', False),
                'required': getattr(field, 'required', False),
                'index': getattr(field, 'index', False),
                'store': getattr(field, 'store', True),
            }
        return result
    
    def read(self, cr: Any, uid: int, ids: list[int], fields: list[str] | None = None, 
             context: dict | None = None, load: str = '_classic_read') -> list[dict]:
        """Read record values from database."""
        raise NotImplementedError("Subclass must implement read()")
    
    def create(self, cr: Any, uid: int, vals: dict, context: dict | None = None) -> int:
        """Create a new record."""
        raise NotImplementedError("Subclass must implement create()")
    
    def write(self, cr: Any, uid: int, ids: list[int], vals: dict, 
              context: dict | None = None) -> bool:
        """Update records with values."""
        raise NotImplementedError("Subclass must implement write()")
    
    def unlink(self, cr: Any, uid: int, ids: list[int], 
               context: dict | None = None) -> bool:
        """Delete records from database."""
        raise NotImplementedError("Subclass must implement unlink()")
    
    def search(self, cr: Any, uid: int, domain: list, offset: int = 0, 
               limit: int | None = None, order: str | None = None, 
               context: dict | None = None, count: bool = False) -> list[int] | int:
        """Search for records matching domain."""
        raise NotImplementedError("Subclass must implement search()")
    
    def browse(self, cr: Any, uid: int, ids: list[int] | int, 
               context: dict | None = None) -> Any:
        """Return a recordset for the given ids."""
        raise NotImplementedError("Subclass must implement browse()")
    
    def default_get(self, cr: Any, uid: int, fields: list[str] | None = None, 
                    context: dict | None = None) -> dict:
        """Get default values for fields."""
        result = {}
        for name, default in self._defaults.items():
            if fields is None or name in fields:
                if callable(default):
                    result[name] = default(self, cr, uid, context)
                else:
                    result[name] = default
        return result
    
    def _compute_display_name(self) -> str:
        """Compute display name for the record."""
        if hasattr(self, 'display_name'):
            return self.display_name
        if hasattr(self, 'name'):
            return str(self.name)
        return str(self.id)
    
    def name_get(self, cr: Any, uid: int, ids: list[int], 
                 context: dict | None = None) -> list[tuple[int, str]]:
        """Return name for each record id."""
        result = []
        for record in self.browse(cr, uid, ids, context):
            result.append((record.id, record._compute_display_name()))
        return result
    
    def copy(self, cr: Any, uid: int, id: int, default: dict | None = None, 
             context: dict | None = None) -> int:
        """Duplicate the record."""
        raise NotImplementedError("Subclass may implement copy()")
    
    def exists(self, cr: Any, uid: int, ids: list[int], 
               context: dict | None = None) -> list[int]:
        """Return only records that exist in database."""
        raise NotImplementedError("Subclass may implement exists()")
    
    def check_recursion(self, cr: Any, uid: int, ids: list[int], 
                        parent: str = 'parent_id', 
                        context: dict | None = None) -> bool:
        """Check for recursion in parent-child relationship."""
        raise NotImplementedError("Subclass may implement check_recursion()")
    
    def _check_company(self, cr: Any, uid: int, ids: list[int], 
                       context: dict | None = None) -> bool:
        """Check company constraint for records."""
        return True
    
    def _check_m2m_recursion(self, cr: Any, uid: int, ids: list[int], 
                             name: str, 
                             context: dict | None = None) -> bool:
        """Check many2many recursion."""
        return True


class Model(BaseModel):
    """Standard persistent model.
    
    This model creates a database table and persists records.
    Use this for regular business objects.
    
    Example:
        class ResPartner(Model):
            _name = 'res.partner'
            _description = 'Partners'
            
            name = fields.Char(string='Name', required=True)
            email = fields.Char(string='Email')
    """
    
    _abstract = False
    _transient = False
    
    id: int


class AbstractModel(BaseModel):
    """Abstract model without database table.
    
    This model does not create a database table.
    Use this for mixins and abstract base classes.
    
    Example:
        class MailThread(AbstractModel):
            _abstract = False  # We want to inherit functionality
            
            message_ids = fields.One2many('mail.message', 'res_id')
            
            def send_message(self, message):
                # Implementation
                pass
    """
    
    _abstract = True
    _transient = False


class TransientModel(BaseModel):
    """Transient model with automatic cleanup.
    
    This model creates a database table that is automatically
    cleaned up by the vacuum system.
    
    Example:
        class AccountMoveReversal(TransientModel):
            _name = 'account.move.reverse'
            _description = 'Move Reversal'
            _transient = True
            
            move_id = fields.Many2one('account.move', required=True)
            reason = fields.Text(string='Reason')
    """
    
    _abstract = False
    _transient = True
