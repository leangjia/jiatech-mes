{
    'name': 'MES ALM Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Alarm Management',
    'description': """
        Alarm Management (ALM) Module
        ==============================
        
        This module provides:
        
        - Alarm configuration and rules
        - Alarm generation and tracking
        - Alarm acknowledgment workflow
        - Alarm resolution tracking
        - Alarm history and analytics
        - Escalation management
        - Notification delivery (email, SMS, in-app)
        
        Integrates with SPC, EDC, and equipment monitoring.
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.jiatech.com',
    
    'depends': [
        'mes_base',
    ],
    
    'data': [],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
}
