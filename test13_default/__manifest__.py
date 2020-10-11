##############################################################################
#
#    Copyright (C) 2020  jeo Software  (http://www.jeosoft.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your optiogitn) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'test13e',
    'version': '13.0.0.0.0',
    'category': 'Tools',
    'summary': "Test for v13 EE",
    'author': "jeo Software",
    'website': 'http://github.com/jobiols/module-repo',
    'license': 'AGPL-3',
    'depends': [
    ],
    'data': [
    ],
    'installable': True,
    'application': True,

    'CPUs': '1',
    'limit_request': '8196',
    'limit_memory_soft': '640000000',
    'limit_memory_hard': '760000000',
    'limit_time_cpu': '6000',
    'limit_time_real': '12000',

    # Here begins odoo-env manifest configuration
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # manifest version, if omitted it is backward compatible
    'env-ver': '2',

    # if Enterprise it installs in a different directory than community
    'odoo-license': 'EE',

    # port where odoo starts serving pages
    'port': '8069',

    # list of url repos to install in the form 'repo-url directory'
    'git-repos': [
        # proyecto
        'https://github.com/jobiols/cl-test.git -b 13.0e',
        'https://github.com/jobiols/jeo-enterprise.git',

        # contiene standard depends
        'https://github.com/jobiols/odoo-addons.git',

        # Adhoc para localizacion
        'https://github.com/ingadhoc/odoo-argentina.git',
        'https://github.com/ingadhoc/miscellaneous',
        'https://github.com/ingadhoc/account-financial-tools',
        'https://github.com/ingadhoc/sale',
        'https://github.com/ingadhoc/product',
        'https://github.com/ingadhoc/argentina-sale',
        'https://github.com/ingadhoc/account-payment',
        'https://github.com/ingadhoc/stock',
        
        # oca para localizacion
        'https://github.com/oca/web',

        # adicionales oca
        'https://github.com/oca/account-analytic.git',
        'https://github.com/jobiols/project.git',
    ],

    # list of images to use in the form 'name image-url'
    'docker-images': [
        'odoo jobiols/odoo-ent:13.0e',
        'postgres postgres:10.1-alpine',
        'nginx nginx'
    ]
}
