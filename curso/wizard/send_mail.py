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
from openerp import models, fields, api


class send_mail(models.TransientModel):
    """ Wizard para validar el envio de un mail """
    _name = 'curso.send_mail'
    _description = "Validar el envio de un mail"

    template = fields.Many2one(
            'email.template', u'Confirmación de inscripción',
            help=u'Plantilla de mail que se enviará',
    )

    @api.onchange('template')
    def _get_default_template(self):
        for rec in self:
            template = self.env['email.template'].search(
                    [('id', '=', self._context.get('template'))]
            )
            rec.template = template

    def button_send_mail(self):
        for rec in self:
            if rec.template:
                rec.template.send_mail(self._context.get('registration'))
