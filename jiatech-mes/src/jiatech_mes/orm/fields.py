"""Jia Tech MES ORM Fields.

This module provides Odoo-inspired field types including:
- Basic: Char, Text, Integer, Float, Boolean
- Date/Time: Date, Datetime
- Relational: Many2one, One2many, Many2many, Selection
- Special: Html, Binary, Reference
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)

F = TypeVar('F', bound='Field')


class Field:
    """Base class for all field types.
    
    Fields are descriptors that provide a clean API for accessing
    and modifying model attributes.
    
    Attributes:
        type: Field type name (e.g., 'char', 'integer')
        string: Human-readable label
        help: Help text for the field
        required: If True, field is required
        readonly: If True, field is read-only
        index: If True, create database index
        store: If True, store field value in database
        compute: Name of compute method
        inverse: Name of inverse (set) method
        related: Related field path
        default: Default value or callable
        copy: If True, copy field value on record duplication
        states: State-dependent field attributes
        groups: Comma-separated list of group xml_ids
        company_dependent: If True, value depends on company
    
    Example:
        class ResPartner(Model):
            name = fields.Char(
                string='Name',
                required=True,
                index=True,
                size=255,
            )
            active = fields.Boolean(
                string='Active',
                default=True,
            )
    """
    
    _field_definition: bool = True
    _type: str = 'unknown'
    _relational: bool = False
    
    def __init__(
        self,
        string: str | None = None,
        help: str | None = None,
        required: bool = False,
        readonly: bool = False,
        index: bool = False,
        store: bool = True,
        default: Callable[[], Any] | Any | None = None,
        copy: bool = True,
        states: dict[str, list[tuple[str, Any]]] | None = None,
        groups: str | None = None,
        company_dependent: bool = False,
        tracking: int | bool = False,
        compute: str | None = None,
        inverse: str | None = None,
        related: str | None = None,
        search: str | None = None,
    ) -> None:
        self.string = string or ''
        self.help = help or ''
        self.required = required
        self.readonly = readonly
        self.index = index
        self.store = store
        self.default = default
        self.copy = copy
        self.states = states or {}
        self.groups = groups
        self.company_dependent = company_dependent
        self.tracking = tracking
        self.compute = compute
        self.inverse = inverse
        self.related = related
        self.search = search
        
        self.name: str | None = None
        self._field_name: str | None = None
        self._model: type | None = None
    
    def __set_name__(self, owner: type, name: str) -> None:
        """Called when field is assigned to a class attribute."""
        self.name = name
        self._field_name = name
        self._model = owner
        
        if not hasattr(owner, '_fields'):
            owner._fields = {}
        owner._fields[name] = self
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Get field value from instance."""
        if obj is None:
            return self
        return obj._values.get(self.name, _NOT_SET)
    
    def __set__(self, obj: Any, value: Any) -> None:
        """Set field value on instance."""
        obj._values[self.name] = value
        obj._modified.add(self.name)
    
    def __delete__(self, obj: Any) -> None:
        """Delete field value from instance."""
        if self.name in obj._values:
            del obj._values[self.name]
            obj._modified.add(self.name)
    
    def get_description(self) -> dict[str, Any]:
        """Return field description for introspection."""
        return {
            'type': self._type,
            'string': self.string,
            'help': self.help,
            'required': self.required,
            'readonly': self.readonly,
            'index': self.index,
            'store': self.store,
            'copy': self.copy,
            'company_dependent': self.company_dependent,
            'tracking': self.tracking,
        }


class _NOT_SET:
    """Sentinel value for unset fields."""
    pass


class Id(Field):
    """ID field - special field for record ID.
    
    This field is automatically added to all models and
    represents the primary key of the record.
    """
    _type = 'id'
    _internal_type = 'integer'
    store = True
    readonly = True
    
    def __init__(self) -> None:
        super().__init__(string='ID', readonly=True, store=True)


class Char(Field):
    """Character field - single line text.
    
    Attributes:
        size: Maximum length of the string
        trim: If True, trim whitespace
        translate: If True, field is translatable
    """
    _type = 'char'
    _internal_type = 'varchar'
    
    def __init__(
        self,
        string: str | None = None,
        size: int | None = None,
        trim: bool = True,
        translate: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.size = size
        self.trim = trim
        self.translate = translate


class Text(Field):
    """Text field - multi-line text.
    
    Attributes:
        translate: If True, field is translatable
    """
    _type = 'text'
    _internal_type = 'text'
    
    def __init__(
        self,
        string: str | None = None,
        translate: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.translate = translate


class Integer(Field):
    """Integer field - whole number.
    
    Attributes:
        group_operator: SQL group operator ('sum', 'avg', etc.)
    """
    _type = 'integer'
    _internal_type = 'integer'
    
    def __init__(
        self,
        string: str | None = None,
        group_operator: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.group_operator = group_operator


class Float(Field):
    """Float field - floating point number.
    
    Attributes:
        digits: Tuple of (precision, scale) for DECIMAL
        group_operator: SQL group operator
    """
    _type = 'float'
    _internal_type = 'numeric'
    
    def __init__(
        self,
        string: str | None = None,
        digits: tuple[int, int] | None = None,
        group_operator: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.digits = digits
        self.group_operator = group_operator


class Boolean(Field):
    """Boolean field - True/False value."""
    _type = 'boolean'
    _internal_type = 'boolean'
    
    def __init__(
        self,
        string: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)


class Date(Field):
    """Date field - calendar date (no time).
    
    Example:
        birthday = fields.Date(string='Birthday')
    """
    _type = 'date'
    _internal_type = 'date'
    
    @staticmethod
    def today() -> str:
        """Return today's date as string."""
        from datetime import date
        return date.today().isoformat()
    
    @staticmethod
    def to_date(value: str | Any) -> Any:
        """Convert value to date."""
        if not value:
            return None
        if isinstance(value, str):
            from datetime import date
            return date.fromisoformat(value)
        return value


class Datetime(Field):
    """Datetime field - date and time.
    
    Example:
        create_date = fields.Datetime(string='Created on', readonly=True)
    """
    _type = 'datetime'
    _internal_type = 'timestamp'
    
    @staticmethod
    def now() -> str:
        """Return current datetime as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @staticmethod
    def to_datetime(value: str | Any) -> Any:
        """Convert value to datetime."""
        if not value:
            return None
        if isinstance(value, str):
            from datetime import datetime
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value


class Html(Field):
    """HTML field - HTML content.
    
    Attributes:
        sanitize: If True, sanitize HTML
        sanitize_tags: If True, remove unsafe tags
        strip_style: If True, remove style attributes
        strip_classes: If True, remove class attributes
    """
    _type = 'html'
    _internal_type = 'html'
    
    def __init__(
        self,
        string: str | None = None,
        sanitize: bool = True,
        sanitize_tags: bool = True,
        sanitize_attributes: bool = True,
        strip_style: bool = False,
        strip_classes: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.sanitize = sanitize
        self.sanitize_tags = sanitize_tags
        self.sanitize_attributes = sanitize_attributes
        self.strip_style = strip_style
        self.strip_classes = strip_classes


class Selection(Field):
    """Selection field - dropdown/picklist.
    
    Attributes:
        selection: List of (value, label) tuples or callable
        selection_add: Extension to parent selection
    
    Example:
        state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ], string='State')
    """
    _type = 'selection'
    _internal_type = 'selection'
    
    def __init__(
        self,
        selection: list[tuple[str, str]] | Callable | None = None,
        string: str | None = None,
        selection_add: list[tuple[str, str]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.selection = selection or []
        self.selection_add = selection_add or []


class Many2one(Field):
    """Many2one field - foreign key relationship.
    
    Attributes:
        comodel_name: Target model name
        ondelete: Cascade behavior ('cascade', 'restrict', 'set null')
        auto_join: If True, join in search
        delegate: If True, inherit fields from target
    
    Example:
        partner_id = fields.Many2one(
            'res.partner',
            string='Partner',
            required=True,
        )
    """
    _type = 'many2one'
    _internal_type = 'many2one'
    _relational = True
    
    def __init__(
        self,
        comodel_name: str,
        string: str | None = None,
        ondelete: str | None = None,
        auto_join: bool = False,
        delegate: bool = False,
        context: dict | None = None,
        domain: list | str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.comodel_name = comodel_name
        self.ondelete = ondelete
        self.auto_join = auto_join
        self.delegate = delegate
        self.context = context or {}
        self.domain = domain or []


class One2many(Field):
    """One2many field - inverse of many2one.
    
    Attributes:
        comodel_name: Target model name
        inverse_name: Foreign key field in target model
        limit: Maximum records to fetch
    
    Example:
        line_ids = fields.One2many(
            'sale.order.line',
            'order_id',
            string='Order Lines',
        )
    """
    _type = 'one2many'
    _internal_type = 'one2many'
    _relational = True
    
    def __init__(
        self,
        comodel_name: str,
        inverse_name: str,
        string: str | None = None,
        limit: int | None = None,
        context: dict | None = None,
        domain: list | str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.comodel_name = comodel_name
        self.inverse_name = inverse_name
        self.limit = limit
        self.context = context or {}
        self.domain = domain or []


class Many2many(Field):
    """Many2many field - many-to-many relationship.
    
    Attributes:
        comodel_name: Target model name
        relation: Relation table name
        column1: Column referencing this model
        column2: Column referencing target model
    
    Example:
        tag_ids = fields.Many2many(
            'res.partner.category',
            'res_partner_res_partner_category_rel',
            'partner_id',
            'category_id',
            string='Tags',
        )
    """
    _type = 'many2many'
    _internal_type = 'many2many'
    _relational = True
    
    def __init__(
        self,
        comodel_name: str,
        relation: str | None = None,
        column1: str | None = None,
        column2: str | None = None,
        string: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.comodel_name = comodel_name
        self.relation = relation
        self.column1 = column1
        self.column2 = column2
        self.limit = limit


class Binary(Field):
    """Binary field - binary data (file, image, etc.).
    
    Attributes:
        maxsize: Maximum file size in bytes
        attachment: If True, store as ir_attachment
    """
    _type = 'binary'
    _internal_type = 'binary'
    
    def __init__(
        self,
        string: str | None = None,
        maxsize: int | None = None,
        attachment: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.maxsize = maxsize
        self.attachment = attachment


class Reference(Field):
    """Reference field - polymorphic reference.
    
    Attributes:
        selection: Callable returning list of (model, name) tuples
    
    Example:
        ref = fields.Reference([
            ('res.partner', 'Partner'),
            ('res.company', 'Company'),
        ], string='Reference')
    """
    _type = 'reference'
    _internal_type = 'reference'
    
    def __init__(
        self,
        selection: Callable | list[tuple[str, str]] | None = None,
        string: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.selection = selection or []


class Monetary(Field):
    """Monetary field - currency amount.
    
    Attributes:
        currency_field: Name of currency field
    
    Example:
        amount = fields.Monetary(
            string='Amount',
            currency_field='currency_id',
        )
    """
    _type = 'monetary'
    _internal_type = 'numeric'
    
    def __init__(
        self,
        string: str | None = None,
        currency_field: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(string=string, **kwargs)
        self.currency_field = currency_field


fields = type('fields', (), {
    name: cls
    for name, cls in globals().items()
    if isinstance(cls, type) and issubclass(cls, Field) and cls is not Field
})()

fields.__all__ = [
    'Field', 'Id', 'Char', 'Text', 'Integer', 'Float', 'Boolean',
    'Date', 'Datetime', 'Html', 'Selection', 'Many2one', 'One2many',
    'Many2many', 'Binary', 'Reference', 'Monetary',
]
