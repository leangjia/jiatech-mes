{
    'name': 'MES WIP Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Work In Progress Management',
    'description': """
        Work In Progress (WIP) Management Module
        ========================================
        
        This module provides:
        
        - Lot tracking and management
        - Work order management
        - Route definition and execution
        - TrackIn/TrackOut operations
        - Production progress monitoring
        - Resource allocation
        
        Integrates with MM (Material Management) and RAS (Resource Management).
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.jiatech.com',
    
    'depends': [
        'mes_base',
        'mes_mm',
        'mes_ras',
    ],
    
    'data': [],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
}
