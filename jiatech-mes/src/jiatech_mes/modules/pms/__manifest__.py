{
    'name': 'MES PMS Module',
    'version': '1.0.0',
    'category': 'Maintenance',
    'summary': 'Preventive Maintenance Scheduling',
    'description': """
        Preventive Maintenance Scheduling (PMS) Module
        ============================================
        
        This module provides:
        
        - Maintenance request management
        - Preventive maintenance scheduling
        - Maintenance team management
        - Maintenance cause tracking
        - Resolution tracking
        - Spare parts management
        - Maintenance metrics and KPIs
        
        Integrates with RAS for equipment maintenance.
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.odoo123.com',
    
    'depends': [
        'mes_base',
        'mes_ras',
    ],
    
    'data': [],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
}
