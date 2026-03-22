{
    'name': 'MES QMS Module',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quality Management System',
    'description': """
        Quality Management System (QMS) Module
        ======================================
        
        This module provides comprehensive quality management functionality:
        
        - Defect Tracking: Record, classify, and track defects throughout production
        - NCR Management: Full Non-Conformance Report workflow with disposition
        - Inspection: Inspection plans, FAI, and quality audits
        - Quality Teams: Manage quality personnel and certifications
        
        Features:
        - Multi-level defect categorization
        - Automated NCR creation from defects
        - Configurable inspection types and sampling plans
        - First Article Inspection (FAI) support
        - Quality team and certification management
        - Integration with SPC for statistical quality control
    """,
    
    'author': 'Jia Tech',
    'website': 'https://www.jiatech.com',
    
    'depends': [
        'mes_base',
        'mes_spc',
    ],
    
    'data': [
    ],
    
    'demo': [
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'Proprietary',
    
    'images': [
    ],
    
    'hooks': {
    },
}
