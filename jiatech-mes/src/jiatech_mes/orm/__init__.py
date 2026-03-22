"""Jia Tech MES ORM - Object Relational Mapping.

This module provides the Odoo-inspired ORM framework including:
- BaseModel: Base class for all models
- MetaModel: Metaclass for model registration
- Recordset: Collection of model records
- Environment: Database access context
"""

from jiatech_mes.orm.models import BaseModel, Model, AbstractModel, TransientModel
from jiatech_mes.orm.fields import Field, Id, Char, Integer, Float, Boolean
from jiatech_mes.orm.fields import Date, Datetime, Text, Html
from jiatech_mes.orm.fields import Many2one, One2many, Many2many, Selection
from jiatech_mes.orm.fields import Binary, Reference, Monetary
from jiatech_mes.orm import api
from jiatech_mes.orm import environment
from jiatech_mes.orm import registry
from jiatech_mes.orm import recordset

__all__ = [
    # Models
    "BaseModel",
    "Model",
    "AbstractModel",
    "TransientModel",
    # Fields
    "Field",
    "Id",
    "Char",
    "Integer",
    "Float",
    "Boolean",
    "Date",
    "Datetime",
    "Text",
    "Html",
    "Many2one",
    "One2many",
    "Many2many",
    "Selection",
    "Binary",
    "Reference",
    "Monetary",
    # API
    "api",
    "environment",
    "registry",
    "recordset",
]
