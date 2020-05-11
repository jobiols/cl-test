# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------
#
#    Copyright (C) 2016  jeo Software  (http://www.jeo-soft.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------------
from openerp import models, fields


class mails_to_send(models.Model):
    """ define los templates de mail para enviar después de cada clase
    """
    _name = 'mails.to.send'
    _order = 'class_no'

    product_id = fields.Many2one(
            'product.product',
            'Producto'
    )

    class_no = fields.Integer(
            'Nro clase'
    )

    template_id = fields.Many2one(
            'email.template',
            'Plantilla de mail',
            domain="[('model_id','=','curso.registration')]"
    )
