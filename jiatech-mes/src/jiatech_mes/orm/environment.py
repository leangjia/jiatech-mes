"""Jia Tech MES Environment Module.

This module provides the Environment class which manages
the database access context for recordsets.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from jiatech_mes.orm.registry import Registry
    from jiatech_mes.orm.recordset import Recordset
    from jiatech_mes.orm.models import BaseModel

_logger = logging.getLogger(__name__)


class Environment:
    """Environment for database access context.
    
    The Environment stores all contextual data for ORM operations:
    - cr: Database cursor
    - uid: Current user ID
    - context: Context dictionary
    - su: Superuser mode flag
    
    Environments are created from a Registry and should not be
    instantiated directly.
    
    Attributes:
        cr: Database cursor
        uid: Current user ID
        context: Context dictionary
        su: Superuser mode (bypasses access rights)
    
    Example:
        env = registry.env(uid=1)
        partners = env['res.partner'].browse([1, 2, 3])
        partners.write({'name': 'Updated Name'})
    """
    
    __slots__ = ('_cr', '_uid', '_context', '_su', '_registry', '_cache', '_protected')
    
    def __init__(
        self,
        cr: Any,
        uid: int,
        context: dict[str, Any] | None = None,
        su: bool = False,
        registry: Registry | None = None,
    ) -> None:
        self._cr = cr
        self._uid = uid
        self._context = dict(context) if context else {}
        self._su = su
        self._registry = registry
        self._cache: dict[str, Any] = {}
        self._protected: set[str] = set()
    
    @property
    def cr(self) -> Any:
        """Database cursor."""
        return self._cr
    
    @property
    def uid(self) -> int:
        """Current user ID."""
        return self._uid
    
    @property
    def context(self) -> dict[str, Any]:
        """Context dictionary."""
        return self._context
    
    @context.setter
    def context(self, value: dict[str, Any]) -> None:
        """Set context dictionary."""
        self._context = dict(value)
    
    @property
    def su(self) -> bool:
        """Superuser mode flag."""
        return self._su
    
    @property
    def registry(self) -> Registry:
        """Model registry."""
        return self._registry
    
    @property
    def user(self) -> Recordset:
        """Current user as a recordset."""
        return self['res.users'].browse(self._uid)
    
    @property
    def company(self) -> Recordset:
        """Current company as a recordset."""
        company_id = self._context.get('allowed_company_ids', [1])[0]
        return self['res.company'].browse(company_id)
    
    @property
    def lang(self) -> str:
        """Current language code."""
        return self._context.get('lang', 'en_US')
    
    def __getitem__(self, model_name: str) -> Recordset:
        """Get a recordset for the given model name.
        
        Args:
            model_name: The model name (e.g., 'res.partner')
            
        Returns:
            A new Recordset for the model
            
        Example:
            partners = env['res.partner']
        """
        if self._registry is None:
            raise RuntimeError("Environment has no registry")
        
        from jiatech_mes.orm.recordset import Recordset
        
        model = self._registry[model_name]
        return Recordset(model, self, ids=[])
    
    def __call__(self, **context: Any) -> Environment:
        """Return a new environment with updated context.
        
        Args:
            **context: Context values to update
            
        Returns:
            New Environment with merged context
            
        Example:
            new_env = env(lang='fr_FR', tz='Europe/Paris')
        """
        new_context = {**self._context, **context}
        return Environment(
            cr=self._cr,
            uid=self._uid,
            context=new_context,
            su=self._su,
            registry=self._registry,
        )
    
    def sudo(self, user_id: int | bool = True) -> Environment:
        """Return environment with different user.
        
        Args:
            user_id: User ID to switch to, or True for superuser
            
        Returns:
            New Environment with different user
            
        Example:
            admin_env = env.sudo(1)  # Switch to admin
            super_env = env.sudo()    # Switch to superuser
        """
        if user_id is True:
            return Environment(
                cr=self._cr,
                uid=1,
                context=self._context,
                su=True,
                registry=self._registry,
            )
        elif user_id is False:
            return self
        else:
            return Environment(
                cr=self._cr,
                uid=user_id,
                context=self._context,
                su=False,
                registry=self._registry,
            )
    
    def ref(self, xml_id: str, raise_if_not_found: bool = True) -> Recordset | None:
        """Get record by external ID.
        
        Args:
            xml_id: External ID (e.g., 'base.main_company')
            raise_if_not_found: Raise error if not found
            
        Returns:
            Recordset for the record or None
        """
        if '.' not in xml_id:
            module, name = 'base', xml_id
        else:
            module, name = xml_id.split('.', 1)
        
        if self._registry is None:
            return None
        
        try:
            cr = self._cr
            cr.execute(
                "SELECT id, model FROM ir_model_data WHERE module=%s AND name=%s",
                (module, name)
            )
            result = cr.fetchone()
            
            if result:
                res_id, model = result
                return self[model].browse(res_id)
            
            if raise_if_not_found:
                raise ValueError(f"External ID not found: {xml_id}")
            return None
        except Exception as e:
            _logger.warning("Error resolving ref '%s': %s", xml_id, e)
            if raise_if_not_found:
                raise
            return None
    
    def is_superuser(self) -> bool:
        """Check if current user is superuser."""
        return self._su
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        if self._su:
            return True
        return self._uid == 1
    
    def is_system(self) -> bool:
        """Check if current user has system access."""
        if self._su:
            return True
        return self.user._is_system()
    
    def clear_cache(self, *model_names: str) -> None:
        """Clear cached data for models.
        
        Args:
            *model_names: Model names to clear cache for
        """
        if not model_names:
            self._cache.clear()
        else:
            for name in model_names:
                self._cache.pop(name, None)
    
    def clear_recordset_cache(self) -> None:
        """Clear all recordset caches."""
        self._cache.clear()
    
    def protected(self, field_name: str) -> None:
        """Mark field as protected during computation."""
        self._protected.add(field_name)
    
    def is_protected(self, field_name: str) -> bool:
        """Check if field is protected."""
        return field_name in self._protected
    
    def unprotect(self, field_name: str) -> None:
        """Remove protection from field."""
        self._protected.discard(field_name)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Environment(cr={self._cr}, uid={self._uid}, su={self._su})"


class environment:
    """Alias for Environment class."""
    
    def __new__(cls, *args: Any, **kwargs: Any) -> Environment:
        return Environment(*args, **kwargs)
