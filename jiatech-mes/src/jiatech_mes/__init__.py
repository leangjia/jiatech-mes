"""Jia Tech MES - Manufacturing Execution System.

An Odoo-inspired Python MES framework for Jia Tech.
"""

__version__ = '1.0.0'

from jiatech_mes.orm import (
    BaseModel,
    Model,
    AbstractModel,
    TransientModel,
    Field,
    Char,
    Integer,
    Float,
    Boolean,
    Date,
    Datetime,
    Text,
    Html,
    Many2one,
    One2many,
    Many2many,
    Selection,
    Binary,
    Reference,
    Monetary,
    api,
    environment,
    registry,
    recordset,
)
from jiatech_mes.orm.registry import Registry, get_default_registry

from jiatech_mes.modules.base import *
from jiatech_mes.modules.wip import *
from jiatech_mes.modules.mm import *
from jiatech_mes.modules.ras import *
from jiatech_mes.modules.edc import *
from jiatech_mes.modules.tcard import *

__all__ = [
    '__version__',
    'BaseModel',
    'Model',
    'AbstractModel',
    'TransientModel',
    'Field',
    'Char',
    'Integer',
    'Float',
    'Boolean',
    'Date',
    'Datetime',
    'Text',
    'Html',
    'Many2one',
    'One2many',
    'Many2many',
    'Selection',
    'Binary',
    'Reference',
    'Monetary',
    'api',
    'environment',
    'registry',
    'recordset',
    'Registry',
    'get_default_registry',
]
