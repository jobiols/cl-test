##############################################################################
#
#    OpenERP, Open Source Management Solution.
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>...
#
##############################################################################
from datetime import datetime, timedelta

#from openerp.osv import osv
from odoo import models


class CursoInvoice(models.Model):
    """ Wizard para generar las facturas
    """
    _name = 'curso.invoice'

    def create_invoice(self, invoice_data):
        product_id = invoice_data.get('curso_id').product
        date_invoice = datetime.strptime(invoice_data.get('date_invoice'), '%Y-%m-%d')
        date_due = (date_invoice + timedelta(days=10))

        invoice_lines = []
        invoice_line = {
            'name': '[{}] {}'.format(invoice_data.get('instance_code'),
                                     product_id.name.encode('utf-8')),
            'sequence': 5,
            'invoice_id': False,
            'account_id': 88,  # venta de cursos
            #            'account_analytic_id': 4,
            'price_unit': product_id.list_price,
            'quantity': 1.0,
        }
        invoice_line_id = self.env['account.invoice.line'].create(invoice_line)
        invoice_lines.append(invoice_line_id)

        if invoice_data.get('discount') != 0:
            razon = invoice_data.get('disc_desc', 'No hay razón').encode('utf-8')
            descuento = 100 * invoice_data.get('discount')
            invoice_line = {
                'name': '{} {}%'.format(razon, descuento),
                'sequence': 5,
                'invoice_id': False,
                'account_id': 88,  # venta de cursos
                #                'account_analytic_id': 4,
                'price_unit': product_id.list_price * invoice_data.get('discount'),
                'quantity': -1.0,
            }
            invoice_line_id = self.env['account.invoice.line'].create(invoice_line)
            invoice_lines.append(invoice_line_id)

        new_invoice = {
            'date_due': date_due.strftime('%Y-%m-%d'),
            'date_invoice': date_invoice.strftime('%Y-%m-%d'),
            'name': '{} C{:.0f}'.format(invoice_data.get('instance_code'),
                                        invoice_data.get('quota')),
            'type': 'out_invoice',
            'reference': '{} C{:.0f}'.format(invoice_data.get('instance_code'),
                                             invoice_data.get('quota')),
            'account_id': 11,
            'partner_id': invoice_data.get('partner_id').id,
            'journal_id': 29,
            'invoice_line': [(6, 0, invoice_lines)],
            'currency_id': 20,  # commission.invoice.currency_id.id,
            'comment': 'generado automáticamente',
            'fiscal_position': invoice_data.get(
                    'partner_id').property_account_position.id,
            'company_id': invoice_data.get('company_id').id,
            'user_id': self.env.user
        }
        invoice_id = self.env['account.invoice'].create(new_invoice)
        return invoice_id

    def button_gen_invoice(self):
        """ Generar facturas en borrador de todos los alumnos que están cursando.
            proceso:
            Seleccionamos las inscripciones que cumplen con:
                estado confirmada
                fecha_inicio.dia in [1..today.dia]
                importe del producto != 0
                no existe una factura para el curso de la inscripción y la fecha fecha_inicio
                    Chequeamos cuantas facturas se hicieron con los siguientes criterios
                        partner_id = el de la inscripción
                        instance_code = el instance code del curso

                    si la cantidad es menor que la cantidad de cuotas
                        crear una factura.

                dia del mes date.strftime('%d')
        """
        # Revisamos la tabla de cuotas, me traigo las que estan pendientes
        register_pool = self.pool.get('curso.quota')
        records = register_pool.search([('invoice_id', '=', False),
                                        ('date', '<=', datetime.utcnow())])
        for quote in records:
            if quote:
                # crear invoice data dict
                id = {}
                id['date_invoice'] = quote.date
                id['instance_code'] = quote.curso_inst
                id['partner_id'] = quote.registration_id.partner_id
                id['quota'] = quote.quota
                id['curso_id'] = quote.registration_id.curso_id
                id['company_id'] = quote.registration_id.curso_id.company_id
                id['discount'] = quote.registration_id.discount / 100
                if quote.registration_id.disc_desc:
                    id['disc_desc'] = quote.registration_id.disc_desc
                id['historic_price'] = quote.list_price

                invoice_id = self.create_invoice(id)
                r = register_pool.search([('id', '=', quote.id)])
                register_pool.write({'invoice_id': invoice_id})

        return True
