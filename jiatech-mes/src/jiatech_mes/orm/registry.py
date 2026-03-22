"""Jia Tech MES Registry Module.

This module provides the Registry class which manages model
registration and database operations.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from jiatech_mes.orm.environment import Environment

_logger = logging.getLogger(__name__)


class Registry:
    """Model registry for managing registered models.
    
    The registry maintains a mapping of model names to model classes
    and provides methods for database operations.
    
    Attributes:
        db_name: Database name
        models: Dictionary of registered models
        
    Example:
        registry = Registry('jiatech_mes')
        ModelClass = registry['res.partner']
    """
    
    def __init__(self, db_name: str | None = None) -> None:
        self.db_name = db_name or 'default'
        self.models: dict[str, type] = {}
        self._custom: dict[str, type] = {}
        self._loaded: bool = False
        self._init: bool = False
    
    def __getitem__(self, model_name: str) -> type:
        """Get model class by name.
        
        Args:
            model_name: The model name
            
        Returns:
            The model class
            
        Raises:
            KeyError: If model not found
        """
        if model_name not in self.models:
            if model_name in self._custom:
                return self._custom[model_name]
            raise KeyError(f"Model not found: {model_name}")
        return self.models[model_name]
    
    def __contains__(self, model_name: str) -> bool:
        """Check if model is registered."""
        return model_name in self.models or model_name in self._custom
    
    def __iter__(self) -> iter:
        """Iterate over model names."""
        return iter(self.models)
    
    def __len__(self) -> int:
        """Number of registered models."""
        return len(self.models)
    
    def register(self, model_class: type) -> None:
        """Register a model class.
        
        Args:
            model_class: The model class to register
        """
        if not hasattr(model_class, '_name'):
            _logger.warning(
                "Cannot register class %s: missing _name attribute",
                model_class.__name__
            )
            return
        
        model_name = model_class._name
        
        if model_name in self.models:
            _logger.warning(
                "Model %s already registered, skipping",
                model_name
            )
            return
        
        self.models[model_name] = model_class
        _logger.debug("Registered model: %s", model_name)
    
    def unregister(self, model_name: str) -> None:
        """Unregister a model.
        
        Args:
            model_name: The model name to unregister
        """
        if model_name in self.models:
            del self.models[model_name]
            _logger.debug("Unregistered model: %s", model_name)
    
    def add_custom_model(self, model_name: str, model_class: type) -> None:
        """Add a custom model (for dynamic models).
        
        Args:
            model_name: The model name
            model_class: The model class
        """
        self._custom[model_name] = model_class
    
    def get_model(self, model_name: str) -> type | None:
        """Get model class or None if not found.
        
        Args:
            model_name: The model name
            
        Returns:
            The model class or None
        """
        return self.models.get(model_name) or self._custom.get(model_name)
    
    def load(self, cr: Any, model_classes: list[type]) -> None:
        """Load and initialize models.
        
        Args:
            cr: Database cursor
            model_classes: List of model classes to load
        """
        for model_class in model_classes:
            self.register(model_class)
            model_class._register_setup()
        
        self._loaded = True
        _logger.info("Loaded %d models", len(self.models))
    
    def init_model(self, cr: Any) -> None:
        """Initialize models (create tables).
        
        Args:
            cr: Database cursor
        """
        if self._init:
            return
        
        for model_name, model_class in self.models.items():
            if getattr(model_class, '_abstract', True):
                continue
            if getattr(model_class, '_transient', False):
                continue
            
            try:
                self._create_table(cr, model_class)
            except Exception as e:
                _logger.error(
                    "Error creating table for %s: %s",
                    model_name, e
                )
        
        self._init = True
    
    def _create_table(self, cr: Any, model_class: type) -> None:
        """Create database table for model.
        
        Args:
            cr: Database cursor
            model_class: The model class
        """
        table_name = model_class._table or model_class._name.replace('.', '_')
        
        cr.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name = %s", 
                   (table_name,))
        if cr.fetchone():
            return
        
        columns = ['id SERIAL PRIMARY KEY']
        
        for field_name, field in model_class._fields.items():
            if field_name == 'id':
                continue
            if not getattr(field, 'store', True):
                continue
            
            col_type = self._get_column_type(field)
            col_def = f'"{field_name}" {col_type}'
            
            if getattr(field, 'required', False):
                col_def += ' NOT NULL'
            if getattr(field, 'index', False):
                col_def += ' INDEX'
            
            columns.append(col_def)
        
        sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        cr.execute(sql)
        
        _logger.debug("Created table: %s", table_name)
    
    def _get_column_type(self, field: Any) -> str:
        """Get SQL column type for field.
        
        Args:
            field: The field instance
            
        Returns:
            SQL type string
        """
        field_type = getattr(field, '_internal_type', None) or getattr(field, '_type', 'text')
        
        type_mapping = {
            'char': 'VARCHAR(255)',
            'varchar': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'float': 'NUMERIC',
            'numeric': 'NUMERIC',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'timestamp': 'TIMESTAMP',
            'html': 'TEXT',
            'selection': 'VARCHAR(255)',
            'binary': 'BYTEA',
            'monetary': 'NUMERIC',
            'id': 'INTEGER',
        }
        
        if field_type == 'many2one':
            return 'INTEGER'
        
        return type_mapping.get(field_type, 'TEXT')
    
    def create_environment(
        self,
        cr: Any,
        uid: int = 1,
        context: dict | None = None,
        su: bool = False,
    ) -> Environment:
        """Create an environment from this registry.
        
        Args:
            cr: Database cursor
            uid: User ID
            context: Context dictionary
            su: Superuser mode
            
        Returns:
            New Environment instance
        """
        from jiatech_mes.orm.environment import Environment
        return Environment(cr, uid, context, su, self)
    
    def process_delegation(self, cr: Any, model_name: str) -> None:
        """Process model delegation (_inherits).
        
        Args:
            cr: Database cursor
            model_name: The model name
        """
        model = self.get_model(model_name)
        if not model:
            return
        
        inherits = getattr(model, '_inherits', {})
        
        for parent_model, field_name in inherits.items():
            parent_table = self.get_model(parent_model)
            if not parent_table:
                continue
            
            table_name = model._table or model_name.replace('.', '_')
            
            sql = f"""
                ALTER TABLE {table_name}
                ADD COLUMN IF NOT EXISTS {field_name} INTEGER
                REFERENCES {parent_table._table or parent_model.replace('.', '_')}
            """
            cr.execute(sql)
    
    def update_schema(self, cr: Any) -> None:
        """Update database schema for all models.
        
        Args:
            cr: Database cursor
        """
        for model_name, model_class in self.models.items():
            if getattr(model_class, '_abstract', True):
                continue
            self._update_table(cr, model_class)
    
    def _update_table(self, cr: Any, model_class: type) -> None:
        """Update database table for model.
        
        Args:
            cr: Database cursor
            model_class: The model class
        """
        table_name = model_class._table or model_class._name.replace('.', '_')
        
        cr.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            (table_name,)
        )
        existing_columns = {row[0] for row in cr.fetchall()}
        
        for field_name, field in model_class._fields.items():
            if field_name in existing_columns:
                continue
            if not getattr(field, 'store', True):
                continue
            
            col_type = self._get_column_type(field)
            sql = f'ALTER TABLE {table_name} ADD COLUMN "{field_name}" {col_type}'
            
            try:
                cr.execute(sql)
                _logger.debug("Added column %s to %s", field_name, table_name)
            except Exception as e:
                _logger.error("Error adding column %s: %s", field_name, e)
    
    def check_health(self, cr: Any) -> dict[str, Any]:
        """Check registry health.
        
        Args:
            cr: Database cursor
            
        Returns:
            Dictionary with health status
        """
        return {
            'status': 'ok',
            'models': len(self.models),
            'db_name': self.db_name,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Registry('{self.db_name}', {len(self.models)} models)"


class MultiRegistry:
    """Registry manager for multiple databases.
    
    This class manages separate registries for different databases.
    """
    
    def __init__(self) -> None:
        self._registries: dict[str, Registry] = {}
    
    def get(self, db_name: str) -> Registry:
        """Get or create registry for database.
        
        Args:
            db_name: Database name
            
        Returns:
            Registry for the database
        """
        if db_name not in self._registries:
            self._registries[db_name] = Registry(db_name)
        return self._registries[db_name]
    
    def delete(self, db_name: str) -> None:
        """Delete registry for database.
        
        Args:
            db_name: Database name
        """
        if db_name in self._registries:
            del self._registries[db_name]
    
    def list(self) -> list[str]:
        """List all registered databases."""
        return list(self._registries.keys())
    
    def __contains__(self, db_name: str) -> bool:
        """Check if database has a registry."""
        return db_name in self._registries


_default_registry = MultiRegistry()


def get_default_registry() -> Registry:
    """Get the default registry."""
    return _default_registry.get('default')


def set_default_registry(db_name: str) -> Registry:
    """Set and get the default registry."""
    return _default_registry.get(db_name)
