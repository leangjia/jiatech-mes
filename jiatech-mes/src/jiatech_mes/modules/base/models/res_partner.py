"""Jia Tech MES Base Models.

This module provides base models for core functionality:
- res.company: Company/Organization
- res.users: User accounts
- res.currency: Currency definitions
- res.lang: Language definitions
"""

from __future__ import annotations

from jiatech_mes.orm import Model, fields, api


class ResCompany(Model):
    """Company model.
    
    Represents a company/organization in the system.
    
    Attributes:
        name: Company name
        partner_id: Associated partner
        currency_id: Primary currency
        street, city, state_id, country_id: Address
    """
    
    _name = 'res.company'
    _description = 'Companies'
    _table = 'res_company'
    
    name = fields.Char(string='Company Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    logo = fields.Binary(string='Logo')
    
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char(string='ZIP')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)


class ResUsers(Model):
    """Users model.
    
    Represents user accounts in the system.
    
    Attributes:
        name: User's name
        login: Login name
        password: Password (hashed)
        email: Email address
        company_id: Default company
        company_ids: Authorized companies
    """
    
    _name = 'res.users'
    _description = 'Users'
    _table = 'res_users'
    _rec_name = 'login'
    
    name = fields.Char(string='Name', required=True)
    login = fields.Char(string='Login', required=True, index=True)
    password = fields.Char(string='Password')
    email = fields.Char(string='Email')
    
    company_id = fields.Many2one('res.company', string='Default Company', required=True)
    company_ids = fields.Many2many(
        'res.company',
        'res_users_company_rel',
        'user_id',
        'company_id',
        string='Authorized Companies',
    )
    
    active = fields.Boolean(string='Active', default=True)
    lang = fields.Char(string='Language', default='en_US')
    tz = fields.Char(string='Timezone', default='UTC')
    
    login_date = fields.Datetime(string='Last Login', readonly=True)
    create_date = fields.Datetime(string='Create Date', readonly=True)
    write_date = fields.Datetime(string='Write Date', readonly=True)
    
    signature = fields.Html(string='Signature')
    image_1920 = fields.Binary(string='Avatar')
    
    share = fields.Boolean(string='Share', readonly=True, default=False)
    
    groups_id = fields.Many2many(
        'res.groups',
        'res_users_groups_rel',
        'uid',
        'gid',
        string='Groups',
    )
    
    @api.model
    def _is_system(self) -> bool:
        """Check if user has system access."""
        return self.env.is_superuser()
    
    @api.model
    def _is_admin(self) -> bool:
        """Check if user is admin."""
        return self.env.uid == 1


class ResPartner(Model):
    """Partner model.
    
    Represents partners (contacts, customers, suppliers).
    
    Attributes:
        name: Partner name
        email, phone, website: Contact info
        customer_rank, supplier_rank: Partner classification
    """
    
    _name = 'res.partner'
    _description = 'Partners'
    _table = 'res_partner'
    
    name = fields.Char(string='Name', required=True, index=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    
    ref = fields.Char(string='Reference', index=True)
    email = fields.Char(string='Email', index=True)
    email_normalized = fields.Char(string='Normalized Email')
    
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    
    website = fields.Char(string='Website')
    
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char(string='ZIP')
    
    function = fields.Char(string='Job Position')
    title = fields.Many2one('res.partner.title', string='Title')
    category_id = fields.Many2many(
        'res.partner.category',
        'res_partner_category_rel',
        'partner_id',
        'category_id',
        string='Tags',
    )
    
    user_id = fields.Many2one('res.users', string='Salesperson')
    user_ids = fields.Many2many('res.users', string='Users')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    customer_rank = fields.Integer(string='Customer Rank', default=0)
    supplier_rank = fields.Integer(string='Supplier Rank', default=0)
    
    is_company = fields.Boolean(string='Is Company', default=False)
    individual = fields.Boolean(string='Individual', compute='_compute_individual')
    
    active = fields.Boolean(string='Active', default=True)
    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Invoice Address'),
        ('delivery', 'Delivery Address'),
        ('other', 'Other Address'),
        ('private', 'Private Address'),
    ], string='Address Type', default='contact')
    
    parent_id = fields.Many2one('res.partner', string='Related Company')
    child_ids = fields.One2many('res.partner', 'parent_id', string='Contacts')
    
    commercial_partner_id = fields.Many2one(
        'res.partner',
        string='Commercial Entity',
        compute='_compute_commercial',
        store=True,
    )
    
    credit_limit = fields.Float(string='Credit Limit')
    total_invoiced = fields.Monetary(
        string='Total Invoiced',
        currency_field='currency_id',
        compute='_compute_totals',
    )
    currency_id = fields.Many2one('res.currency', string='Currency')
    
    message_partner_ids = fields.Many2many(
        'res.partner',
        'mail_message_res_partner_rel',
        'res_partner_id',
        'message_id',
        string='Followers',
    )
    
    @api.depends('name', 'parent_id.name')
    def _compute_display_name(self) -> None:
        """Compute display name."""
        for partner in self:
            if partner.parent_id and not partner.is_company:
                partner.display_name = f"{partner.parent_id.name} / {partner.name}"
            else:
                partner.display_name = partner.name
    
    @api.depends('is_company', 'parent_id')
    def _compute_individual(self) -> None:
        """Compute if partner is individual."""
        for partner in self:
            partner.individual = not partner.is_company and not partner.parent_id
    
    @api.depends('parent_id')
    def _compute_commercial(self) -> None:
        """Compute commercial entity."""
        for partner in self:
            if partner.parent_id:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id
            else:
                partner.commercial_partner_id = partner
    
    def _compute_totals(self) -> None:
        """Compute total invoiced amount."""
        for partner in self:
            partner.total_invoiced = 0.0


class ResGroups(Model):
    """Groups model.
    
    Represents user groups for access control.
    """
    
    _name = 'res.groups'
    _description = 'Access Groups'
    _table = 'res_groups'
    
    name = fields.Char(string='Group Name', required=True)
    users = fields.Many2many(
        'res.users',
        'res_users_groups_rel',
        'gid',
        'uid',
        string='Users',
    )
    model_access = fields.One2many('ir.model.access', 'group_id', string='Access Controls')
    rule_ids = fields.One2many('ir.rule', 'groups', string='Rules')


class ResCurrency(Model):
    """Currency model.
    
    Represents currencies for monetary fields.
    """
    
    _name = 'res.currency'
    _description = 'Currencies'
    _table = 'res_currency'
    
    name = fields.Char(string='Currency Name', required=True)
    symbol = fields.Char(string='Symbol', required=True)
    rate = fields.Float(string='Rate', digits=(16, 6))
    inverse_rate = fields.Float(
        string='Inverse Rate',
        digits=(16, 6),
        compute='_compute_inverse_rate',
    )
    
    rounding = fields.Float(string='Rounding Factor', default=0.01)
    decimal_places = fields.Integer(string='Decimal Places', default=2)
    
    active = fields.Boolean(string='Active', default=True)
    
    position = fields.Selection([
        ('after', 'After Amount'),
        ('before', 'Before Amount'),
    ], string='Symbol Position', default='after')
    
    currency_unit_label = fields.Char(string='Currency Unit')
    currency_subunit_label = fields.Char(string='Subunit')
    
    @api.depends('rate')
    def _compute_inverse_rate(self) -> None:
        """Compute inverse rate."""
        for currency in self:
            if currency.rate:
                currency.inverse_rate = 1.0 / currency.rate
            else:
                currency.inverse_rate = 1.0


class ResCountry(Model):
    """Country model."""
    
    _name = 'res.country'
    _description = 'Countries'
    _table = 'res_country'
    
    name = fields.Char(string='Country Name', required=True)
    code = fields.Char(string='Country Code', required=True, size=2)
    
    address_format = fields.Text(
        string='Address Format',
        default='%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s',
    )
    
    phone_code = fields.Char(string='Phone Prefix')
    
    state_ids = fields.One2many('res.country.state', 'country_id', string='States')
    
    vat_label = fields.Char(string='Vat Label')


class ResCountryState(Model):
    """Country State model."""
    
    _name = 'res.country.state'
    _description = 'Country States'
    _table = 'res_country_state'
    
    name = fields.Char(string='State Name', required=True)
    code = fields.Char(string='State Code', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    
    address_format = fields.Text(string='Address Format')


class ResPartnerTitle(Model):
    """Partner Title model."""
    
    _name = 'res.partner.title'
    _description = 'Partner Titles'
    _table = 'res_partner_title'
    
    name = fields.Char(string='Title', required=True)
    shortcut = fields.Char(string='Abbreviation')


class ResPartnerCategory(Model):
    """Partner Category model."""
    
    _name = 'res.partner.category'
    _description = 'Partner Tags'
    _table = 'res_partner_category'
    
    name = fields.Char(string='Tag Name', required=True)
    parent_id = fields.Many2one('res.partner.category', string='Parent Tag')
    child_ids = fields.One2many('res.partner.category', 'parent_id', string='Child Tags')
    complete_name = fields.Char(string='Full Name', compute='_compute_complete_name')
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self) -> None:
        """Compute complete tag name."""
        for tag in self:
            if tag.parent_id:
                tag.complete_name = f"{tag.parent_id.complete_name} / {tag.name}"
            else:
                tag.complete_name = tag.name
