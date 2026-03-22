"""Jia Tech MES API Module.

This module provides Odoo-inspired API decorators including:
- @model: Mark method as record-level
- @depends: Trigger recompute on field changes
- @onchange: Trigger on UI field changes
- @constrains: Validate constraints
- @api: Combined decorator
"""

from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    pass

C = TypeVar('C', bound=Callable[..., Any])


class ApiDecorators:
    """Container for API decorators.
    
    This class holds the decorator functions that provide
    Odoo-style API functionality.
    """
    
    @staticmethod
    def model(method: C) -> C:
        """Mark method as working on a recordset (not values).
        
        This decorator marks a method as a "record method" that
        operates on self as a recordset rather than individual records.
        
        Example:
            @api.model
            def get_view(self, view_id):
                '''Return view definition.'''
                ...
        """
        @functools.wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            return method(self, *args, **kwargs)
        wrapper._api = 'model'
        return wrapper
    
    @staticmethod
    def depends(*fields: str) -> Callable[[C], C]:
        """Mark computed field as depending on these fields.
        
        This decorator marks a compute method as depending on
        the specified fields. When any of these fields change,
        the computed field will be recalculated.
        
        Args:
            *fields: Field names that this computation depends on
            
        Example:
            @api.depends('list_price', 'standard_price')
            def _compute_margin(self):
                self.margin = self.list_price - self.standard_price
        """
        def decorator(method: C) -> C:
            if not hasattr(method, '_depends'):
                method._depends = []
            method._depends = list(fields)
            
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                return method(self, *args, **kwargs)
            wrapper._depends = list(fields)
            wrapper._api = 'depends'
            return wrapper
        return decorator
    
    @staticmethod
    def onchange(*fields: str) -> Callable[[C], C]:
        """Mark method as onchange handler for these fields.
        
        This decorator marks a method as an onchange handler
        that will be called when any of the specified fields
        change in the UI.
        
        Args:
            *fields: Field names to watch for changes
            
        Example:
            @api.onchange('product_id')
            def _onchange_product(self):
                if self.product_id:
                    self.price = self.product_id.list_price
        """
        def decorator(method: C) -> C:
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                return method(self, *args, **kwargs)
            wrapper._onchange = list(fields)
            wrapper._api = 'onchange'
            return wrapper
        return decorator
    
    @staticmethod
    def constrains(*fields: str) -> Callable[[C], C]:
        """Mark method as a constraint checker.
        
        This decorator marks a method as a constraint that
        will be validated when any of the specified fields change.
        If the constraint fails, raise ValidationError.
        
        Args:
            *fields: Field names to validate
            
        Example:
            @api.constrains('date_start', 'date_end')
            def _check_dates(self):
                if self.date_start > self.date_end:
                    raise ValidationError('Start date must be before end date')
        """
        def decorator(method: C) -> C:
            if not hasattr(method, '_constrains'):
                method._constrains = []
            method._constrains = list(fields)
            
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                return method(self, *args, **kwargs)
            wrapper._constrains = list(fields)
            wrapper._api = 'constrains'
            return wrapper
        return decorator
    
    @staticmethod
    def depends_context(*keys: str) -> Callable[[C], C]:
        """Mark computed field as depending on context values.
        
        Args:
            *keys: Context keys to depend on
            
        Example:
            @api.depends('amount')
            @api.depends_context('currency_id')
            def _compute_amount_currency(self):
                # Recalculate when currency_id changes in context
                ...
        """
        def decorator(method: C) -> C:
            if not hasattr(method, '_depends_context'):
                method._depends_context = []
            method._depends_context = list(keys)
            
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                return method(self, *args, **kwargs)
            wrapper._depends_context = list(keys)
            return wrapper
        return decorator
    
    @staticmethod
    def onchange_depends(*fields: str) -> Callable[[C], C]:
        """Mark computed field as depending on onchange dependencies.
        
        Used to mark fields that should be recalculated when
        the onchange triggers.
        """
        def decorator(method: C) -> C:
            if not hasattr(method, '_onchange_depends'):
                method._onchange_depends = []
            method._onchange_depends = list(fields)
            
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                return method(self, *args, **kwargs)
            wrapper._onchange_depends = list(fields)
            return wrapper
        return decorator
    
    @staticmethod
    def returns(model: str | None, mapper: Callable | None = None) -> Callable[[C], C]:
        """Mark method as returning records of specified model.
        
        Args:
            model: Model name or None for self
            mapper: Optional function for converting values
            
        Example:
            @api.returns('res.partner')
            def find_partner(self, name):
                return self.env['res.partner'].search([('name', '=', name)])
        """
        def decorator(method: C) -> C:
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                result = method(self, *args, **kwargs)
                return result
            wrapper._returns = model
            wrapper._returns_mapper = mapper
            return wrapper
        return decorator
    
    @staticmethod
    def with_context(**context: Any) -> Callable[[C], C]:
        """Execute method with specific context values.
        
        Example:
            @api.with_context(tz='UTC')
            def get_local_time(self):
                ...
        """
        def decorator(method: C) -> C:
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                old_context = self.env.context
                try:
                    self.env.context = {**old_context, **context}
                    return method(self, *args, **kwargs)
                finally:
                    self.env.context = old_context
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_cache(method: C) -> C:
        """Mark method as invalidating cached fields.
        
        After execution, the specified cached fields will be
        recomputed on next access.
        """
        @functools.wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            result = method(self, *args, **kwargs)
            if hasattr(method, '_invalidate_cache'):
                for field_name in method._invalidate_cache:
                    self.env.cache.invalidate(self.env[ self._name], field_name)
            return result
        wrapper._api = 'invalidate_cache'
        return wrapper
    
    @classmethod
    def depends_context_set(cls, *keys: str) -> Callable[[C], C]:
        """Store context values as record fields during method execution."""
        def decorator(method: C) -> C:
            @functools.wraps(method)
            def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
                old_values = {}
                for key in keys:
                    if key in self.env.context:
                        old_values[key] = self.env.context[key]
                try:
                    return method(self, *args, **kwargs)
                finally:
                    for key, value in old_values.items():
                        self.env.context[key] = value
            return wrapper
        return decorator


api = ApiDecorators()


class ApiContext:
    """Context manager for API operations.
    
    Provides context managers for common API patterns.
    """
    
    @staticmethod
    def depends(*fields: str) -> Callable[[C], C]:
        """Mark computed field as depending on fields."""
        return api.depends(*fields)
    
    @staticmethod
    def onchange(*fields: str) -> Callable[[C], C]:
        """Mark onchange handler."""
        return api.onchange(*fields)
    
    @staticmethod
    def constrains(*fields: str) -> Callable[[C], C]:
        """Mark constraint checker."""
        return api.constrains(*fields)
