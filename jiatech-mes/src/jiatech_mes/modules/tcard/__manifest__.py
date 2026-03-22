{
    'name': 'MES TCard Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Route Card Management',
    'description': """
        Route Card (TCard) Module
        ==========================
        
        This module provides:
        
        - Route card (traveler) management
        - Step-by-step operation tracking
        - Check item definitions
        - Check result recording
        - Route card templates
        - Sign-off workflow
        
        Supports production routing and documentation.
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.odoo123.com',
    
    'depends': [
        'mes_base',
        'mes_wip',
        'mes_ras',
    ],
    
    'data': [],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
}
