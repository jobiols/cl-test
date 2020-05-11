# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------
#
#    Copyright (C) 2017  jeo Software  (http://www.jeosoft.com.ar)
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


class add_recover(models.TransientModel):
    """ Wizard para agregar una clase de recuperatorio """

    _name = 'curso.add_recover'
    _description = __doc__

    # este campo sirve solo para disparar el onchange
    # para que funcione tiene que estar en la vista (con invisible =1 para que no se vea )
    dummy = fields.Integer(
    )

    lecture_id = fields.Many2one(
            'curso.lecture',
            required=True,
    )

    @api.onchange('dummy')
    def onchange_dummy(self):
        """ Esta funcion se dispara al crearse este modelo transitorio """

        # traer del contexto la id de la alumna
        alumna_id = self._context.get('active_ids')[0]
        partner_id = self.env['res.partner'].browse(alumna_id)

        # obtener una lista de ids de clases a recuperar
        assistance_obj = self.env['curso.assistance']
        recover_ids = assistance_obj.get_recover_ids(partner_id)

        return {'domain': {'lecture_id': [('id', 'in', recover_ids)]}}

    def button_add_recover(self):
        """ En la ficha de la alumna se oprime el botón agregar recuperatorio
            y se le agrega una clase que se elige de una lista, aparecerán
            solo las clases que la alumna deba recuperar. Para generar esta
            lista se analizan las clases que están en estado absent y se
            buscan las clases de posible recuperatorio para dichas clases.

            La clase aregada aparecerá en color verde en estado programmed y
            funcionará como una clase original a los efectos de dar el
            presente, Salvo que tendrá tildada la casilla Recuperatorio.
            La clase original que estaba en estado absent se pasa a estado
            to_recover

            Se genera una factura por $130 para el cobro de la clase de
            recuperatorio. La proxima vez que se abra esta vista se verá la
            leyenda "Nos debe $130"
        """
        for rec in self:
            #  obtener el id de la alumna que viene en el contexto
            ids = self._context.get('active_ids')
            partner_id = self.env['res.partner'].browse(ids[0])
            assistance_obj = self.env['curso.assistance']
            assistance_obj.add_atendee(partner_id, rec.lecture_id,
                                       recover=True)
            # generar la factura
            rec.lecture_id.curso_id.do_invoice(
                    130,
                    rec.lecture_id.curso_id.curso_instance,
                    rec.lecture_id.seq,
                    partner_id)
