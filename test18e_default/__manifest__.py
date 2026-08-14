##############################################################################
#
#    Copyright (C) 2023  jeo Software  (http://www.jeosoft.com.ar)
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
#   le agregamos esto
##############################################################################

{
    "name": "test18e",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Test for v18 EE",
    "author": "jeo Software",
    "website": "http://github.com/jobiols/cl-test",
    "license": "AGPL-3",
    "depends": [],
    "installable": True,
    # manifest version, if omitted it is backward compatible
    "env-ver": "2",
    # if Enterprise it installs in a different directory than community
    "odoo-license": "EE",
    # Config to write in odoo.conf
    "config": [
        "workers = 0",
        "admin_password = admin",
    ],
    "port": "8069",
    "git-repos": [
        "https://github.com/jobiols/cl-test.git -b 18.0e",
        "git@github.com:quilsoft-org/demo-multi-fiscal-position.git",

        "https://github.com/ingadhoc/account-financial-tools.git l10n-ar/account-financial-tools",
        "https://github.com/ingadhoc/account-payment.git l10n-ar/account-payment",
        "https://github.com/ingadhoc/odoo-argentina.git l10n-ar/odoo-argentina",
        "https://github.com/ingadhoc/argentina-sale.git l10n-ar/argentina-sale",
        "https://github.com/ingadhoc/account-invoicing.git l10n-ar/account-invoicing",
        "https://github.com/ingadhoc/odoo-argentina-ee.git l10n-ar/odoo-argentina-ee",
        "https://github.com/ingadhoc/stock.git l10n-ar/stock",

        "https://github.com/ingadhoc/aeroo_reports.git l10n-ar/aeroo_reports",
        "https://github.com/ingadhoc/sale.git l10n-ar/sale",

        "https://github.com/adhoc-cicd/oca-server-tools l10n-ar/oca-server-tools",
        "https://github.com/adhoc-cicd/oca-stock-logistics-workflow.git l10n-ar/oca-stock-logistics-workflow",
        "https://github.com/adhoc-cicd/oca-web.git l10n-ar/oca-web",
        "https://github.com/adhoc-cicd/oca-sale-workflow.git l10n-ar/oca-sale-workflow"

    ],
    # list of images to use in the form 'name image-url'
    "docker-images": [
        "odoo jobiols/odoo-ent:18.0e",
        "postgres postgres:18-alpine",
    ],
}
