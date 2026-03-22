{
    'name': 'MES SPC Module',
    'version': '1.0.0',
    'category': 'Quality',
    'summary': 'Statistical Process Control',
    'description': """
        Statistical Process Control (SPC) Module
        =======================================
        
        This module provides:
        
        - SPC parameter configuration
        - Control chart types (X-bar R, I-MR, P, etc.)
        - SPC rule definitions (Western Electric rules)
        - Real-time data collection
        - Out of control (OOC) detection
        - Control limit calculations
        - SPC alarm generation
        - Capability studies (Cpk, Ppk)
        
        Integrates with EDC for real-time monitoring.
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.odoo123.com',
    
    'depends': [
        'mes_base',
        'mes_edc',
    ],
    
    'data': [],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
}
