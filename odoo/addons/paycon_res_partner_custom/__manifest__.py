{
    'name': "Custom Paycon Res Partner",
    'version': '14.0',
    'description': "Specific implementation for Paycon Challenge",
    'author': "Lukas S. Machado",
    'category': 'Category',
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'views/res_partner_view.xml',
        'data/res_partner_category_data.xml',
        'wizards/wizard_generate_demo_contacts_view.xml',
        'security/ir.model.access.csv',
    ],
}