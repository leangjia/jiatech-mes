"""Jia Tech MES Domain Module.

This module provides Odoo-style domain expression handling
for searching and filtering records.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


class Domain:
    """Odoo-style domain expression.
    
    Domains are used to filter records in search operations.
    They consist of a list of domain terms combined with AND/OR.
    
    Domain format:
        [('field', 'operator', value), ...]
        
    Operators:
        =, !=, <, >, <=, >=: Comparison
        like, ilike: Pattern matching
        in, not in: Value in list
        child_of: Record is child of value
        
    Example:
        domain = Domain([
            ('state', '=', 'draft'),
            ('amount', '>', 100),
        ])
        records = env['account.move'].search(domain)
    """
    
    def __init__(self, domain: list | None = None) -> None:
        self.domain = domain or []
        self._normalize()
    
    def _normalize(self) -> None:
        """Normalize domain to standard format."""
        if not isinstance(self.domain, list):
            self.domain = []
    
    def to_sql(self, table: str, params: list) -> str:
        """Convert domain to SQL WHERE clause.
        
        Args:
            table: Table name
            params: Query parameters list
            
        Returns:
            SQL WHERE clause string
        """
        if not self.domain:
            return "TRUE"
        
        clauses = []
        
        for term in self.domain:
            if term == '&':
                clauses.append("AND")
            elif term == '|':
                clauses.append("OR")
            elif term == '!':
                clauses.append("NOT")
            elif isinstance(term, (list, tuple)):
                clause = self._term_to_sql(table, term, params)
                if clause:
                    clauses.append(clause)
        
        result = " ".join(clauses)
        
        if result.count('(') > result.count(')'):
            result += ')' * (result.count('(') - result.count(')'))
        
        return result
    
    def _term_to_sql(
        self,
        table: str,
        term: tuple,
        params: list,
    ) -> str | None:
        """Convert single domain term to SQL.
        
        Args:
            table: Table name
            term: Domain term tuple
            params: Query parameters list
            
        Returns:
            SQL clause string
        """
        if len(term) < 2:
            return None
        
        field, operator = term[0], term[1]
        value = term[2] if len(term) > 2 else None
        
        if field == 'id':
            field_name = 'id'
        else:
            field_name = f'"{field}"'
        
        op_map = {
            '=': '%s',
            '!=': '%s',
            '<': '%s',
            '>': '%s',
            '<=': '%s',
            '>=': '%s',
            'like': '%s',
            'ilike': '%s',
            'not like': '%s',
            'not ilike': '%s',
            'in': '(%s)',
            'not in': '(%s)',
        }
        
        if operator not in op_map:
            _logger.warning("Unknown operator: %s", operator)
            return None
        
        if operator in ('in', 'not in'):
            if isinstance(value, (list, tuple)):
                placeholders = ','.join(['%s'] * len(value))
                params.extend(value)
                sql_op = 'IN' if operator == 'in' else 'NOT IN'
                return f"{field_name} {sql_op} ({placeholders})"
            else:
                params.append(value)
                sql_op = 'IN' if operator == 'in' else 'NOT IN'
                return f"{field_name} {sql_op} (%s)"
        
        if operator in ('like', 'ilike', 'not like', 'not ilike'):
            if value:
                if operator.startswith('not'):
                    params.append(f'%{value}%')
                    return f"{field_name} NOT LIKE %s"
                else:
                    params.append(f'%{value}%')
                    return f"{field_name} LIKE %s"
            return None
        
        params.append(value)
        return f"{field_name} {operator} {op_map[operator]}"
    
    def to_sql_params(self) -> list:
        """Extract parameters from domain.
        
        Returns:
            List of parameter values
        """
        params = []
        for term in self.domain:
            if isinstance(term, (list, tuple)) and len(term) >= 3:
                value = term[2]
                if isinstance(term[1], str) and term[1] in ('in', 'not in'):
                    if isinstance(value, (list, tuple)):
                        params.extend(value)
                    elif value is not None:
                        params.append(value)
                elif value is not None:
                    params.append(value)
        return params
    
    def __and__(self, other: Domain) -> Domain:
        """Combine domains with AND."""
        if not self.domain:
            return other
        if not other.domain:
            return self
        combined = self.domain + other.domain
        return Domain(combined)
    
    def __or__(self, other: Domain) -> Domain:
        """Combine domains with OR."""
        if not self.domain:
            return other
        if not other.domain:
            return self
        combined = ['|'] + self.domain + other.domain
        return Domain(combined)
    
    def __invert__(self) -> Domain:
        """Negate domain."""
        return Domain(['!'] + self.domain)
    
    def __bool__(self) -> bool:
        """Check if domain is non-empty."""
        return bool(self.domain)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Domain({self.domain!r})"


def domain_encode(value: Any) -> list:
    """Encode a value for use in domain."""
    if isinstance(value, Domain):
        return value.domain
    return value


def domain_eval(domain: list, env: Any) -> bool:
    """Evaluate a domain against an environment.
    
    Args:
        domain: Domain expression
        env: Environment with record values
        
    Returns:
        True if record matches domain
    """
    if not domain:
        return True
    
    result = True
    
    for term in domain:
        if not result:
            break
        
        if term == '&':
            continue
        elif term == '|':
            result = True
            continue
        elif term == '!':
            result = not result
            continue
        
        if isinstance(term, (list, tuple)) and len(term) >= 3:
            field, operator, value = term[0], term[1], term[2]
            field_value = getattr(env, field, None)
            
            op_funcs = {
                '=': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b,
                '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b,
                '>=': lambda a, b: a >= b,
                'in': lambda a, b: a in b if b else False,
                'not in': lambda a, b: a not in b if b else True,
                'like': lambda a, b: b in str(a) if a else False,
                'ilike': lambda a, b: b.lower() in str(a).lower() if a else False,
            }
            
            op_func = op_funcs.get(operator)
            if op_func:
                result = op_func(field_value, value)
    
    return result


class DomainParser:
    """Parse Odoo-style domain expressions."""
    
    OPERATORS = {'=', '!=', '<', '>', '<=', '>=', 'like', 'ilike',
                  'not like', 'not ilike', 'in', 'not in', 'child_of'}
    
    @classmethod
    def parse(cls, domain: list | str) -> Domain:
        """Parse domain expression.
        
        Args:
            domain: Domain list or JSON string
            
        Returns:
            Domain object
        """
        if isinstance(domain, str):
            import json
            try:
                domain = json.loads(domain)
            except json.JSONDecodeError:
                return Domain([])
        
        return Domain(domain)
    
    @classmethod
    def validate(cls, domain: list) -> tuple[bool, str | None]:
        """Validate domain expression.
        
        Args:
            domain: Domain expression
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(domain, list):
            return False, "Domain must be a list"
        
        for i, term in enumerate(domain):
            if term in ('&', '|', '!'):
                continue
            
            if not isinstance(term, (list, tuple)):
                return False, f"Term at index {i} must be a list or tuple"
            
            if len(term) < 2:
                return False, f"Term at index {i} must have at least 2 elements"
            
            if not isinstance(term[0], str):
                return False, f"Field name at index {i} must be a string"
            
            if term[1] not in cls.OPERATORS:
                return False, f"Unknown operator: {term[1]}"
        
        return True, None
