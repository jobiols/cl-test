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
from datetime import datetime, timedelta

import babel.dates
from openerp import models, fields, api
from openerp.exceptions import Warning

from . import html_filter


class curso_registration(models.Model):
    _name = 'curso.registration'
    _inherit = 'curso.registration'
    _order = 'create_date desc'
    _description = 'Inscripcion en cursos'

    create_date = fields.Date(
        u'Creación',
        readonly=True
    )
    date_closed = fields.Date(
        u'Fecha de cierre',
        readonly=True
    )
    date_open = fields.Date(
        u'Fecha de inscripción',
        readonly=True
    )
    discount = fields.Float(
        u'Descuento (%)',
        digits=(2, 2)
    )
    disc_desc = fields.Char(
        u'Razon del descuento',
        size=128,
        select=True
    )
    nb_register = fields.Integer(
        u'Number of Participants',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=1
    )
    state = fields.Selection(
        [('draft', u'Interesada'),
         ('cancel', u'Cancelado'),
         ('confirm', u'Cursando'),
         ('done', u'Cumplido'),
         ('signed', u'Señado')], 'Estado',
        track_visibility='onchange',
        size=16, readonly=True, default='draft'
    )
    reply_to = fields.Char(
        related='curso_id.reply_to',
        string='Reply-to Email',
        size=128,
        readonly=True
    )
    curso_begin_date = fields.Date(
        related='curso_id.date_begin',
        string="Inicio",
        readonly=True
    )
    email = fields.Char(
        related='partner_id.email',
        string='Email',
        size=128,
        readonly=True
    )
    phone = fields.Char(
        related='partner_id.mobile',
        string='Telefono',
        size=128,
        readonly=True
    )
    curso_state = fields.Selection(
        related='curso_id.state',
        string=u'Estado del curso',
        readonly=True
    )
    curso_begin_day = fields.Char(
        compute='_compute_curso_begin_day',
        string='Dia'
    )
    source = fields.Selection([
        ('none', 'Sin descuento'),
        ('normal', 'Descuento normal'),
        ('groupon', 'Descuento groupon'),
    ],
        'Origen', required=True,
        default='none'
    )
    curso_id = fields.Many2one(
        'curso.curso',
        'Curso',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    partner_id = fields.Many2one(
        'res.partner',
        u'Alumna',
        required=True,
        states={'done': [('readonly', True)]}
    )
    user_id = fields.Many2one(
        'res.users',
        'User',
        states={'done': [('readonly', True)]}
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='curso_id.company_id',
        store=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    quota_id = fields.One2many(
        'curso.quota',
        'registration_id',
        'Cuotas'
    )
    log_ids = fields.One2many(
        'mail.message',
        'res_id',
        'Logs',
        domain=[('model', '=', _name)]
    )

    @api.depends('curso_begin_date')
    def _compute_curso_begin_day(self):
        for rec in self:
            try:
                init = datetime.strptime(rec.curso_begin_date, "%Y-%m-%d")
            except:
                weekday = '???'
            else:
                weekday = babel.dates.format_datetime(
                    init, format='EEE', locale=self.env.context['lang'])

            rec.curso_begin_day = weekday.capitalize()

    def button_reg_sign(self):
        """ La alumna seña el curso, eso la confirma en el mismo
        """
        for reg in self:
            # poner la alumna como cliente
            reg.partner_id.write({'customer': True})

            # generarle las cuotas
            reg.button_gen_quotes()

            # si el curso no tiene clases las creamos
            # TODO esto habria que chequearlo en otro lado y antes
            if len(reg.curso_id.lecture_ids) == 0:
                reg.curso_id.button_generate_lectures()

            # señar la inscripción pasando al estado señada
            res = reg.sign_registration()

            # generar las asistencias
            for lec in reg.curso_id.lecture_ids:
                lec.button_generate_assistance()

            context = self._context.copy()
            context['template'] = reg.curso_id.email_registration_id.id
            context['registration'] = reg.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar mail de confirmación',
            'res_model': 'curso.send_mail',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

    def sign_registration(self):
        for rec in self:
            rec.curso_id.message_post(
                body=(u'Nueva seña para el curso: %s.') % (
                    rec.partner_id.name or '',),
                subtype="curso.mt_curso_registration"
            )
            rec.state = 'signed'

    @api.constrains('curso_id', 'state', 'nb_register')
    def _check_seats_limit(self):
        for rec in self:
            if rec.curso_id.register_max and \
                    rec.curso_id.register_avail < (
                    rec.nb_register if rec.state == 'draft' else 0):
                raise Warning('No hay mas vacantes.!')

            if rec.curso_id.state == 'cancel':
                raise Warning('No se puede registrar una alumna en un curso '
                              'cancelado')

    def button_gen_quotes(self):
        """ Generar las cuotas que la alumna deberá pagar
        """

        def calculate_invoice_date(sourcedate, months):
            return sourcedate + timedelta(days=30 * (months))

        for rec in self:
            date = datetime.strptime(rec.curso_begin_date, '%Y-%m-%d')
            for quota in range(1, rec.curso_id.product.no_quotes + 1):
                quota_data = {
                    'registration_id': rec.id,
                    'date': calculate_invoice_date(date, quota - 1),
                    'quota': quota,
                    'list_price': rec.curso_id.product.list_price
                }
                rec.env['curso.quota'].create(quota_data)

    # TODO Aca estan los mails después de cada clase. Hay que arreglarlo
    def try_send_mail_by_lecture(self):
        for rec in self:
            # en que clase estoy
            lecture = 1

            # que mail tengo que enviarle en esta clase
            # por ahora traigo el de la clase 1
            template = False
            for reg in rec.curso_id.product.email_classes_ids:
                a = reg.class_no
                template = reg.template_id
                break

            if template:
                template.send_mail(rec.id)

    def get_mail_footer_html(self):
        html = html_filter.html_filter()
        return html.default_footer()

    def get_html(self):
        get_agenda = [{'date': datetime}, {'schedule': '10:00 a 12:00'},
                      {'topic': 'ojos esfumados'}]
        ret = """
                <table>
                    <tbody>
                        <tr>
                            <th>Fecha</th>
                            <th>Dia</th>
                            <th>Horario programado</th>
                            <th>Contenido de la clase</th>
                        </tr>
                        <tr>
                            <td>${lecture.date}</td>
                            <td>${lecture.weekday}</td>
                            <td>${lecture.schedule_id.name}</td>
                            <td>${lecture.name}</td>
                        </tr>
                    </tbody>
                </table>
                """
        return ''

    def get_formatted_begin_date(self):
        date = datetime.strptime(self.curso_begin_date, '%Y-%m-%d')
        return date.strftime('%A %d/%m/%Y').capitalize().decode('utf-8',
                                                                'ignore')

    def get_formatted_begin_time(self):
        return self.curso_id.diary_ids[0].schedule.formatted_start_time

    def button_reg_cancel(self):
        """ Cancela una inscripción de una alumna a un curso,
            Elimina todas las cuotas
            Elimina todas las asistencias, poniendolas en Abandonado.
        """
        # Eliminar todas las cuotas pendientes para no seguir cobrandole
        for reg in self:
            quota_obj = self.env['curso.quota']
            quotas = quota_obj.search([('invoice_id', '=', None),
                                       ('registration_id', '=', reg.id)])
            for rg in quotas:
                rg.unlink()

            # Poner las asistencias en Abandonado
            assists = self.env['curso.assistance'].search([
                ('partner_id', '=', reg.partner_id.id),
                ('state', '=', 'programmed')
            ])
            for assist in assists:
                assist.state = 'abandoned'

            # cambiar el estado a cancelado
            self.state = 'cancel'

    def diary_table_html(self):
        """ Calendario de clases """
        html = html_filter.html_filter()
        return html.diary_table()

    # TODO poner los descuentos en una tabla de configuracion DUPLICADO!!
    @api.onchange('source')
    def _compute_source(self):
        for rec in self:
            if rec.source == 'groupon':
                rec.discount = 73.42
                rec.disc_desc = 'Descuento groupon'
            if rec.source == 'normal':
                rec.discount = 33.333333
                rec.disc_desc = 'Descuento normal'
