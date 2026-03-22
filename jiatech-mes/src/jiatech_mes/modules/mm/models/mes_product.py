"""Jia Tech MES MM Module - Material Management.

This module provides models for:
- mes.product: Product definitions
- mes.uom: Unit of Measure
- mes.stock: Stock/Inventory management
- mes.bom: Bills of Materials
"""

from __future__ import annotations

from jiatech_mes.orm import Model, TransientModel, AbstractModel, fields, api


class MesProduct(Model):
    """MES Product model.
    
    Represents products that can be manufactured or stored.
    
    Attributes:
        name: Product name
        code: Product code/SKU
        type: Product type (product, consumable, service)
        uom_id: Stock keeping unit of measure
        uom_po_id: Purchase unit of measure
        list_price: Sales price
        standard_price: Standard cost
    """
    
    _name = 'mes.product'
    _description = 'Product'
    _table = 'mes_product'
    
    name = fields.Char(string='Product Name', required=True, index=True)
    code = fields.Char(string='Product Code', index=True)
    
    type = fields.Selection([
        ('product', 'Storable'),
        ('consumable', 'Consumable'),
        ('service', 'Service'),
    ], string='Product Type', default='product', required=True)
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure', required=True)
    uom_po_id = fields.Many2one('mes.uom', string='Purchase UOM', required=True)
    
    list_price = fields.Float(string='Sale Price', digits=(16, 2), default=0.0)
    standard_price = fields.Float(string='Standard Cost', digits=(16, 2), default=0.0)
    
    volume = fields.Float(string='Volume', digits=(16, 4))
    weight = fields.Float(string='Weight', digits=(16, 3))
    weight_net = fields.Float(string='Net Weight', digits=(16, 3))
    
    active = fields.Boolean(string='Active', default=True)
    
    description = fields.Text(string='Description')
    description_sale = fields.Text(string='Sale Description')
    description_purchase = fields.Text(string='Purchase Description')
    
    barcode = fields.Char(string='Barcode', index=True)
    
    company_id = fields.Many2one('res.company', string='Company')
    
    categ_id = fields.Many2one('mes.product.category', string='Category')
    
    bom_ids = fields.One2many('mes.bom', 'product_id', string='Bill of Materials')
    route_ids = fields.Many2many(
        'mes.route',
        'mes_product_route_rel',
        'product_id',
        'route_id',
        string='Routes',
    )
    
    seller_ids = fields.One2many('mes.product.supplier', 'product_id', string='Vendors')
    
    qty_available = fields.Float(
        string='Quantity On Hand',
        compute='_compute_quantities',
        digits=(16, 3),
    )
    virtual_available = fields.Float(
        string='Forecasted Quantity',
        compute='_compute_quantities',
        digits=(16, 3),
    )
    
    image_1920 = fields.Binary(string='Image')
    image_128 = fields.Binary(string='Image 128')
    
    @api.depends()
    def _compute_quantities(self) -> None:
        """Compute stock quantities."""
        for product in self:
            product.qty_available = 0.0
            product.virtual_available = 0.0


class MesProductCategory(Model):
    """MES Product Category model."""
    
    _name = 'mes.product.category'
    _description = 'Product Category'
    _table = 'mes_product_category'
    
    name = fields.Char(string='Category Name', required=True)
    parent_id = fields.Many2one('mes.product.category', string='Parent Category')
    child_ids = fields.One2many('mes.product.category', 'parent_id', string='Child Categories')
    complete_name = fields.Char(string='Full Name', compute='_compute_complete_name')
    
    parent_path = fields.Char(string='Parent Path', index=True)
    
    product_count = fields.Integer(
        string='Products',
        compute='_compute_product_count',
    )
    
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self) -> None:
        """Compute full category name."""
        for categ in self:
            if categ.parent_id:
                categ.complete_name = f"{categ.parent_id.complete_name} / {categ.name}"
            else:
                categ.complete_name = categ.name
    
    def _compute_product_count(self) -> None:
        """Compute product count."""
        for categ in self:
            categ.product_count = 0


class MesUom(Model):
    """MES Unit of Measure model."""
    
    _name = 'mes.uom'
    _description = 'Unit of Measure'
    _table = 'mes_uom'
    
    name = fields.Char(string='Unit Name', required=True)
    code = fields.Char(string='Code', required=True)
    
    category_id = fields.Many2one('mes.uom.category', string='Category', required=True)
    
    factor = fields.Float(string='Factor', default=1.0)
    inverse_factor = fields.Float(
        string='Inverse Factor',
        compute='_compute_inverse',
        digits=(16, 12),
    )
    
    rounding = fields.Float(string='Rounding', default=0.01)
    
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('factor')
    def _compute_inverse(self) -> None:
        """Compute inverse factor."""
        for uom in self:
            if uom.factor:
                uom.inverse_factor = 1.0 / uom.factor
            else:
                uom.inverse_factor = 1.0


class MesUomCategory(Model):
    """MES Unit of Measure Category model."""
    
    _name = 'mes.uom.category'
    _description = 'Unit of Measure Category'
    _table = 'mes_uom_category'
    
    name = fields.Char(string='Category Name', required=True)
    uom_ids = fields.One2many('mes.uom', 'category_id', string='Units')


class MesBom(Model):
    """MES Bill of Materials model."""
    
    _name = 'mes.bom'
    _description = 'Bill of Materials'
    _table = 'mes_bom'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Reference')
    
    product_id = fields.Many2one(
        'mes.product',
        string='Product',
        required=True,
    )
    product_tmpl_id = fields.Many2one('mes.product.template', string='Product Template')
    
    product_qty = fields.Float(
        string='Quantity',
        digits=(16, 3),
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one('mes.uom', string='Unit of Measure', required=True)
    
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit'),
    ], string='BoM Type', default='normal')
    
    routing_id = fields.Many2one('mes.route', string='Routing')
    route_ids = fields.Many2many(
        'mes.route',
        'mes_bom_route_rel',
        'bom_id',
        'route_id',
        string='Routes',
    )
    
    line_ids = fields.One2many(
        'mes.bom.line',
        'bom_id',
        string='BoM Lines',
        copy=True,
    )
    
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)
    
    sequence = fields.Integer(string='Sequence', default=1)
    
    ready_to_produce = fields.Selection([
        ('all_available', 'All components available'),
        ('asap', 'As soon as possible'),
    ], string='Manufacturing Readiness', default='all_available')


class MesBomLine(Model):
    """MES Bill of Materials Line model."""
    
    _name = 'mes.bom.line'
    _description = 'BoM Line'
    _table = 'mes_bom_line'
    
    bom_id = fields.Many2one('mes.bom', string='Parent BoM', required=True)
    
    product_id = fields.Many2one('mes.product', string='Product', required=True)
    
    product_qty = fields.Float(
        string='Quantity',
        digits=(16, 3),
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one('mes.uom', string='Unit of Measure', required=True)
    
    sequence = fields.Integer(string='Sequence', default=1)
    
    cost_share = fields.Float(string='Cost Share %', default=0.0)
    
    attribute_value_ids = fields.Many2many(
        'mes.product.attribute.value',
        'mes_bom_line_attribute_rel',
        'bom_line_id',
        'attribute_value_id',
        string='Attributes',
    )


class MesStockLocation(Model):
    """MES Stock Location model."""
    
    _name = 'mes.stock.location'
    _description = 'Stock Location'
    _table = 'mes_stock_location'
    
    name = fields.Char(string='Location Name', required=True)
    code = fields.Char(string='Code')
    
    complete_name = fields.Char(string='Full Name', compute='_compute_complete_name')
    
    location_id = fields.Many2one('mes.stock.location', string='Parent Location')
    child_ids = fields.One2many('mes.stock.location', 'location_id', string='Child Locations')
    
    parent_path = fields.Char(string='Parent Path', index=True)
    
    is_transit = fields.Boolean(string='Is Transit Location')
    is_view = fields.Boolean(string='Is View')
    
    usage = fields.Selection([
        ('supplier', 'Supplier'),
        ('view', 'View'),
        ('internal', 'Internal'),
        ('customer', 'Customer'),
        ('inventory', 'Inventory'),
        ('production', 'Production'),
    ], string='Location Type', default='internal')
    
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)


class MesStockQuant(Model):
    """MES Stock Quantity model."""
    
    _name = 'mes.stock.quant'
    _description = 'Stock Quant'
    _table = 'mes_stock_quant'
    
    product_id = fields.Many2one('mes.product', string='Product', required=True, index=True)
    location_id = fields.Many2one('mes.stock.location', string='Location', required=True, index=True)
    
    quantity = fields.Float(string='Quantity', digits=(16, 3), default=0.0)
    reserved_quantity = fields.Float(string='Reserved', digits=(16, 3), default=0.0)
    
    lot_id = fields.Many2one('mes.lot', string='Lot/Serial')
    package_id = fields.Many2one('mes.stock.package', string='Package')
    
    owner_id = fields.Many2one('res.partner', string='Owner')
    
    available_quantity = fields.Float(
        string='Available',
        compute='_compute_available',
        digits=(16, 3),
    )
    
    company_id = fields.Many2one('res.company', string='Company')
    in_date = fields.Datetime(string='Incoming Date', readonly=True)
    
    @api.depends('quantity', 'reserved_quantity')
    def _compute_available(self) -> None:
        """Compute available quantity."""
        for quant in self:
            quant.available_quantity = quant.quantity - quant.reserved_quantity


class MesStockMove(Model):
    """MES Stock Move model."""
    
    _name = 'mes.stock.move'
    _description = 'Stock Move'
    _table = 'mes_stock_move'
    
    name = fields.Char(string='Name', required=True)
    
    product_id = fields.Many2one('mes.product', string='Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=(16, 3), default=0.0)
    product_uom_id = fields.Many2one('mes.uom', string='Unit of Measure', required=True)
    
    location_id = fields.Many2one('mes.stock.location', string='Source Location', required=True)
    location_dest_id = fields.Many2one('mes.stock.location', string='Destination', required=True)
    
    state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
    ], string='Status', default='draft', index=True)
    
    lot_id = fields.Many2one('mes.lot', string='Lot/Serial')
    
    origin = fields.Char(string='Source Document')
    
    move_line_ids = fields.One2many('mes.stock.move.line', 'move_id', string='Move Lines')
    
    company_id = fields.Many2one('res.company', string='Company')
    
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    date_expected = fields.Datetime(string='Expected Date')


class MesStockMoveLine(Model):
    """MES Stock Move Line model."""
    
    _name = 'mes.stock.move.line'
    _description = 'Stock Move Line'
    _table = 'mes_stock_move_line'
    
    move_id = fields.Many2one('mes.stock.move', string='Move', required=True)
    
    product_id = fields.Many2one('mes.product', string='Product', required=True)
    product_uom_id = fields.Many2one('mes.uom', string='UOM', required=True)
    
    qty_done = fields.Float(string='Done', digits=(16, 3), default=0.0)
    
    location_id = fields.Many2one('mes.stock.location', string='From')
    location_dest_id = fields.Many2one('mes.stock.location', string='To')
    
    lot_id = fields.Many2one('mes.lot', string='Lot/Serial')
    
    state = fields.Selection([
        ('draft', 'New'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')


class MesProductSupplier(Model):
    """MES Product Supplier model."""
    
    _name = 'mes.product.supplier'
    _description = 'Product Supplier'
    _table = 'mes_product_supplier'
    
    product_id = fields.Many2one('mes.product', string='Product', required=True)
    
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    
    product_name = fields.Char(string='Vendor Product Name')
    product_code = fields.Char(string='Vendor Product Code')
    
    min_qty = fields.Float(string='Minimal Quantity', default=0.0)
    max_qty = fields.Float(string='Maximal Quantity', default=0.0)
    
    price = fields.Float(string='Unit Price', digits=(16, 2))
    currency_id = fields.Many2one('res.currency', string='Currency')
    
    delay = fields.Integer(string='Delivery Lead Time (days)', default=1)
    
    company_id = fields.Many2one('res.company', string='Company')


class MesProductTemplate(Model):
    """MES Product Template model."""
    
    _name = 'mes.product.template'
    _description = 'Product Template'
    _table = 'mes_product_template'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    
    type = fields.Selection([
        ('product', 'Storable'),
        ('consumable', 'Consumable'),
        ('service', 'Service'),
    ], string='Product Type', default='product', required=True)
    
    uom_id = fields.Many2one('mes.uom', string='Unit of Measure', required=True)
    uom_po_id = fields.Many2one('mes.uom', string='Purchase UOM', required=True)
    
    list_price = fields.Float(string='Sale Price', digits=(16, 2), default=0.0)
    standard_price = fields.Float(string='Standard Cost', digits=(16, 2), default=0.0)
    
    categ_id = fields.Many2one('mes.product.category', string='Category')
    
    active = fields.Boolean(string='Active', default=True)
    
    product_variant_ids = fields.One2many('mes.product', 'product_tmpl_id', string='Variants')


class MesStockPackage(Model):
    """MES Stock Package model."""
    
    _name = 'mes.stock.package'
    _description = 'Stock Package'
    _table = 'mes_stock_package'
    
    name = fields.Char(string='Package Name', required=True)
    code = fields.Char(string='Code')
    
    location_id = fields.Many2one('mes.stock.location', string='Location')
    
    quant_ids = fields.One2many('mes.stock.quant', 'package_id', string='Quants')
    
    package_type_id = fields.Many2one('mes.stock.package.type', string='Type')
    
    company_id = fields.Many2one('res.company', string='Company')


class MesStockPackageType(Model):
    """MES Stock Package Type model."""
    
    _name = 'mes.stock.package.type'
    _description = 'Package Type'
    _table = 'mes_stock_package_type'
    
    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Code')
    
    height = fields.Float(string='Height')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    max_weight = fields.Float(string='Max Weight')
