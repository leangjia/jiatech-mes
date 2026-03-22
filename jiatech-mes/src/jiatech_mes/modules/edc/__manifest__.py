{
    'name': 'MES EDC Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Equipment Data Collection',
    'description': """
        Equipment Data Collection (EDC) Module
        ======================================
        
        This module provides:
        
        - Data collection item definitions
        - Collection rule configuration
        - Equipment data mapping
        - Real-time data collection
        - Data validation and rules
        - Collection scheduling
        
        Integrates with equipment for SECS/GEM, OPC-UA protocols.
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
