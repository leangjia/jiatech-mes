"""Jia Tech MES base module.

This module provides core functionality including:
- res.company: Company/Organization
- res.users: User accounts
- res.partner: Partners and contacts
- res.currency: Currency definitions
"""

from jiatech_mes.modules.base.models.res_partner import (
    ResCompany,
    ResUsers,
    ResPartner,
    ResGroups,
    ResCurrency,
    ResCountry,
    ResCountryState,
    ResPartnerTitle,
    ResPartnerCategory,
)

__all__ = [
    'ResCompany',
    'ResUsers',
    'ResPartner',
    'ResGroups',
    'ResCurrency',
    'ResCountry',
    'ResCountryState',
    'ResPartnerTitle',
    'ResPartnerCategory',
]
