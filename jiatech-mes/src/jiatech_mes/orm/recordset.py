"""Jia Tech MES Recordset Module.

This module provides the Recordset class which represents a collection
of records from a model.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Iterator

if TYPE_CHECKING:
    from jiatech_mes.orm.environment import Environment
    from jiatech_mes.orm.models import BaseModel

_logger = logging.getLogger(__name__)


class Recordset:
    """Collection of records from a model.
    
    Recordset is the core data structure for ORM operations.
    It behaves like a set of records with lazy loading and
    batch operations.
    
    Attributes:
        _model: The model class
        _env: The environment
        _ids: Record IDs in the set
        _values: Cached field values
        _modified: Set of modified field names
    
    Example:
        partners = env['res.partner'].browse([1, 2, 3])
        partners.write({'name': 'Updated'})
        
        for partner in partners:
            print(partner.name)
    """
    
    __slots__ = ('_model', '_env', '_ids', '_values', '_modified')
    
    def __init__(
        self,
        model: type[BaseModel],
        env: Environment,
        ids: list[int] | tuple[int, ...] | None = None,
    ) -> None:
        self._model = model
        self._env = env
        self._ids = list(ids) if ids else []
        self._values: dict[int, dict[str, Any]] = {}
        self._modified: set[str] = set()
    
    @property
    def env(self) -> Environment:
        """The environment."""
        return self._env
    
    @property
    def model(self) -> type[BaseModel]:
        """The model class."""
        return self._model
    
    @property
    def _name(self) -> str:
        """Model name."""
        return self._model._name
    
    @property
    def ids(self) -> list[int]:
        """Record IDs."""
        return list(self._ids)
    
    def __len__(self) -> int:
        """Number of records in the set."""
        return len(self._ids)
    
    def __bool__(self) -> bool:
        """Check if set is non-empty."""
        return bool(self._ids)
    
    def __iter__(self) -> Iterator[Recordset]:
        """Iterate over individual records."""
        for record_id in self._ids:
            yield self.browse([record_id])
    
    def __getitem__(self, index: int | slice) -> Recordset | Any:
        """Get record by index or slice."""
        if isinstance(index, slice):
            return self.browse(self._ids[index])
        elif isinstance(index, int):
            if index < 0:
                index = len(self._ids) + index
            if 0 <= index < len(self._ids):
                return self.browse([self._ids[index]])
            raise IndexError(f"Recordset index out of range: {index}")
        else:
            raise TypeError(f"Invalid index type: {type(index)}")
    
    def __contains__(self, item: Any) -> bool:
        """Check if record ID is in the set."""
        if isinstance(item, Recordset):
            return item.id in self._ids
        if isinstance(item, int):
            return item in self._ids
        return False
    
    def browse(self, ids: list[int] | int | None = None) -> Recordset:
        """Return a new recordset with the given IDs.
        
        Args:
            ids: Record IDs, or None for empty set
            
        Returns:
            New Recordset
        """
        if ids is None:
            return Recordset(self._model, self._env, [])
        if isinstance(ids, int):
            return Recordset(self._model, self._env, [ids])
        return Recordset(self._model, self._env, list(ids))
    
    def ids(self) -> list[int]:
        """Get list of record IDs."""
        return list(self._ids)
    
    def ensure_one(self) -> Recordset:
        """Ensure recordset contains exactly one record.
        
        Raises:
            ValueError: If not exactly one record
        """
        if len(self._ids) != 1:
            raise ValueError(
                f"Expected singleton: {self._name} ({len(self._ids)} given)"
            )
        return self
    
    @property
    def id(self) -> int | None:
        """Get single record ID, or None if empty/many."""
        if len(self._ids) == 1:
            return self._ids[0]
        return None
    
    @property
    def _id(self) -> int | None:
        """Get single record ID, or None."""
        return self.id
    
    def exists(self) -> Recordset:
        """Return only records that still exist in database.
        
        This checks the database and removes any IDs that no
        longer exist from the recordset.
        """
        if not self._ids:
            return self
        
        if self._env._registry is None:
            return self
        
        self._env.cr.execute(
            f"SELECT id FROM {self._model._table or self._name.replace('.', '_')} "
            f"WHERE id IN %s",
            (tuple(self._ids),)
        )
        existing_ids = [row[0] for row in self._env.cr.fetchall()]
        missing_ids = set(self._ids) - set(existing_ids)
        
        if missing_ids:
            _logger.warning(
                "Recordset contains non-existent IDs: %s", missing_ids
            )
        
        return self.browse(existing_ids)
    
    def filtered(self, func: Callable[[Recordset], bool]) -> Recordset:
        """Filter records by a condition.
        
        Args:
            func: Function that takes a single-record recordset
                  and returns True to keep the record
            
        Returns:
            Filtered recordset
        """
        result = []
        for record in self:
            if func(record):
                result.append(record.id)
        return self.browse(result)
    
    def filtered_domain(self, domain: list) -> Recordset:
        """Filter records by domain expression.
        
        Args:
            domain: Odoo-style domain expression
            
        Returns:
            Filtered recordset
        """
        if not domain:
            return self
        
        ids = self.search(domain).ids
        return self.browse(ids)
    
    def mapped(self, func: str | Callable) -> list[Any]:
        """Map records to values.
        
        Args:
            func: Field name or function to apply to each record
            
        Returns:
            List of values
        """
        if isinstance(func, str):
            return [getattr(record, func, None) for record in self]
        return [func(record) for record in self]
    
    def sorted(self, key: Callable | None = None, reverse: bool = False) -> Recordset:
        """Return sorted recordset.
        
        Args:
            key: Sorting key function, or None for default order
            reverse: If True, sort in descending order
            
        Returns:
            Sorted recordset
        """
        order = self._model._order
        
        if key is None:
            def default_key(rec: Recordset) -> tuple:
                return tuple(getattr(rec, f, None) for f in order.split(','))
            key = default_key
        
        sorted_ids = sorted(self._ids, key=key, reverse=reverse)
        return self.browse(sorted_ids)
    
    def search(self, domain: list, **kwargs: Any) -> Recordset:
        """Search for records matching domain.
        
        Args:
            domain: Odoo-style domain expression
            **kwargs: Additional search parameters
            
        Returns:
            Recordset of matching records
        """
        ids = self._model.search(
            self._env.cr,
            self._env.uid,
            domain,
            **kwargs
        )
        return self.browse(ids)
    
    def create(self, vals: dict | list[dict]) -> Recordset:
        """Create new records.
        
        Args:
            vals: Values for the new record(s)
            
        Returns:
            Recordset containing the new record(s)
        """
        if isinstance(vals, dict):
            vals = [vals]
        
        ids = []
        for vals_dict in vals:
            record_id = self._model.create(
                self._env.cr,
                self._env.uid,
                vals_dict,
                self._env.context,
            )
            ids.append(record_id)
        
        return self.browse(ids)
    
    def write(self, vals: dict) -> bool:
        """Write values to records.
        
        Args:
            vals: Values to update
            
        Returns:
            True if successful
        """
        if not self._ids or not vals:
            return True
        
        return self._model.write(
            self._env.cr,
            self._env.uid,
            self._ids,
            vals,
            self._env.context,
        )
    
    def unlink(self) -> bool:
        """Delete records.
        
        Returns:
            True if successful
        """
        if not self._ids:
            return True
        
        return self._model.unlink(
            self._env.cr,
            self._env.uid,
            self._ids,
            self._env.context,
        )
    
    def read(self, fields: list[str] | None = None) -> list[dict]:
        """Read record values.
        
        Args:
            fields: Field names to read, or None for all
            
        Returns:
            List of dictionaries with field values
        """
        if not self._ids:
            return []
        
        return self._model.read(
            self._env.cr,
            self._env.uid,
            self._ids,
            fields,
            self._env.context,
        )
    
    def read_group(
        self,
        domain: list,
        fields: list[str],
        groupby: list[str],
        offset: int = 0,
        limit: int | None = None,
        orderby: str | None = None,
        lazy: bool = True,
    ) -> list[dict]:
        """Group and aggregate records.
        
        Args:
            domain: Filter domain
            fields: Fields to aggregate
            groupby: Fields to group by
            offset: Result offset
            limit: Result limit
            orderby: Sort order
            lazy: If True, only first groupby applied
            
        Returns:
            List of grouped results
        """
        if self._env._registry is None:
            return []
        
        from jiatech_mes.orm.domain import Domain
        
        domain_obj = Domain(domain)
        cr = self._env.cr
        
        table = self._model._table or self._name.replace('.', '_')
        
        where_clause = domain_obj.to_sql(table, [])
        where_params = domain_obj.to_sql_params()
        
        select_fields = []
        for field in groupby:
            select_fields.append(f"{table}.{field}")
        
        for field in fields:
            select_fields.append(field)
        
        sql = f"""
            SELECT {', '.join(select_fields)}
            FROM {table}
            WHERE {where_clause}
            GROUP BY {', '.join(groupby)}
            ORDER BY {', '.join(groupby)}
            OFFSET %s
        """
        params = where_params + [offset]
        
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        
        cr.execute(sql, params)
        return cr.fetchall()
    
    def default_get(self, fields: list[str] | None = None) -> dict:
        """Get default values for fields.
        
        Args:
            fields: Field names, or None for all
            
        Returns:
            Dictionary of default values
        """
        return self._model.default_get(
            self._env.cr,
            self._env.uid,
            fields,
            self._env.context,
        )
    
    def load(self, fields: list[str], data: list[list]) -> dict:
        """Load data into records.
        
        Args:
            fields: Field names
            data: List of data rows
            
        Returns:
            Dictionary with 'ids' and 'warnings'
        """
        return {'ids': [], 'warnings': []}
    
    def copy_data(self, default: dict | None = None) -> list[dict]:
        """Copy records with optional default values.
        
        Args:
            default: Default values for copied records
            
        Returns:
            List of dictionaries with record values
        """
        result = []
        for record in self:
            vals = record.read()[0]
            vals.pop('id', None)
            if default:
                vals.update(default)
            result.append(vals)
        return result
    
    def copy(self, default: dict | None = None) -> Recordset:
        """Duplicate records.
        
        Args:
            default: Default values for copied records
            
        Returns:
            Recordset with new records
        """
        copies = []
        for record in self:
            vals = record.read()[0]
            vals.pop('id', None)
            if default:
                vals.update(default)
            new_id = self._model.create(
                self._env.cr,
                self._env.uid,
                vals,
                self._env.context,
            )
            copies.append(new_id)
        return self.browse(copies)
    
    def name_get(self) -> list[tuple[int, str]]:
        """Get display names for records.
        
        Returns:
            List of (id, name) tuples
        """
        return self._model.name_get(
            self._env.cr,
            self._env.uid,
            self._ids,
            self._env.context,
        )
    
    def name_create(self, name: str) -> tuple[int, str]:
        """Create a record with the given name.
        
        Args:
            name: Name value
            
        Returns:
            Tuple of (id, name)
        """
        vals = {'name': name}
        new_id = self.create(vals)[0]
        return (new_id.id, name)
    
    def name_search(
        self,
        name: str = '',
        domain: list | None = None,
        operator: str = 'ilike',
        limit: int = 100,
    ) -> list[tuple[int, str]]:
        """Search for records by name.
        
        Args:
            name: Name to search for
            domain: Additional domain
            operator: Search operator
            limit: Maximum results
            
        Returns:
            List of (id, name) tuples
        """
        if domain is None:
            domain = []
        
        domain = domain + [(self._model._rec_name, operator, name)]
        ids = self.search(domain, limit=limit).ids
        return self.browse(ids).name_get()
    
    def display_name(self) -> str | None:
        """Get display name for single record."""
        if len(self._ids) != 1:
            return None
        return self.name_get()[0][1] if self.name_get() else None
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self._name}({self._ids})"
    
    def __str__(self) -> str:
        """String representation."""
        return self.__repr__()
    
    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, Recordset):
            return NotImplemented
        return (
            self._name == other._name and
            self._ids == other._ids and
            self._env == other._env
        )
    
    def __ne__(self, other: Any) -> bool:
        """Check inequality."""
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        """Hash the recordset."""
        return hash((self._name, tuple(self._ids)))
    
    def union(self, *recordsets: Recordset) -> Recordset:
        """Return union of recordsets."""
        all_ids = set(self._ids)
        for rs in recordsets:
            if not isinstance(rs, Recordset):
                raise TypeError(f"Expected Recordset, got {type(rs)}")
            if rs._name != self._name:
                raise ValueError(
                    f"Cannot union different models: {self._name} and {rs._name}"
                )
            all_ids.update(rs._ids)
        return self.browse(list(all_ids))
    
    def intersection(self, *recordsets: Recordset) -> Recordset:
        """Return intersection of recordsets."""
        other_ids = set()
        for rs in recordsets:
            if not isinstance(rs, Recordset):
                raise TypeError(f"Expected Recordset, got {type(rs)}")
            other_ids.update(rs._ids)
        common_ids = set(self._ids) & other_ids
        return self.browse(list(common_ids))
    
    def difference(self, *recordsets: Recordset) -> Recordset:
        """Return difference of recordsets."""
        other_ids = set()
        for rs in recordsets:
            if not isinstance(rs, Recordset):
                raise TypeError(f"Expected Recordset, got {type(rs)}")
            other_ids.update(rs._ids)
        diff_ids = set(self._ids) - other_ids
        return self.browse(list(diff_ids))


class Record:
    """A single record from a recordset.
    
    This class provides a convenient way to work with a single record.
    It wraps a recordset with exactly one record.
    """
    
    def __init__(self, recordset: Recordset) -> None:
        if len(recordset) != 1:
            raise ValueError(
                f"Record requires exactly one record, got {len(recordset)}"
            )
        self._recordset = recordset
    
    @property
    def id(self) -> int:
        """Record ID."""
        return self._recordset.id
    
    def __getattr__(self, name: str) -> Any:
        """Get field value."""
        return getattr(self._recordset[0], name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Set field value."""
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._recordset[0][name] = value
