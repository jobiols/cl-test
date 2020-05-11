# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tienda Nube Connection',
    'version': '13.0.1.3',
    'category': 'Tools',
    'summary': 'Conexion con tienda nube',
    'author': 'jeo Software',
    'depends': [
        'curso'
    ],
    'data': [
        'views/product_view.xml',
        'views/woo_categ_view.xml',
        'security/ir.model.access.csv'
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
