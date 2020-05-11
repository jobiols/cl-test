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
import operator
from datetime import datetime, timedelta

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning


class curso_curso(models.Model):
    _inherit = 'curso.curso'

    child = fields.Boolean(
        u'Curso Hijo',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help=u"Tildar si el curso es hijo, es decir debe estar insertado en un curso "
             u"mas grande"
    )

    allow_overclass = fields.Boolean(
        u'Permitir sobreclases', readonly=True,
        states={'draft': [('readonly', False)]},
        help=u"Tildar si cuando se generan clases se puede permitir que la clase "
             u"comparta el aula con otra en el mismo horario tener en cuenta que pasará "
             u"lo mismo con los feriados"
    )

    instance = fields.Integer(
        u'Instancia',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    date_begin = fields.Date(
        u'Inicio', readonly=True,
        help=u"La fecha en la que inicia el curso, se puede dejar en blanco si no "
             u"está definida todavia pero se debe ingresar para confirmar el curso",
        states={'draft': [('readonly', False)]}
    )

    date_end = fields.Date(
        u'Fin', readonly=True,
        help=u"La fecha en la que termina el curso, es un campo que se calcula con la fecha de"
             u"la última clase",
        compute="_compute_date_end"
    )
    reply_to = fields.Char(
        u'Mail de respuesta', size=64,
        states={'done': [('readonly', True)]},
        help=u"La dirección de mail del que organiza los cursos, cuando el alumno "
             u"responde el mail que se le envia en automático responderá a esta dirección."
             u"si se deja en blanco la respuesta va a la dirección por defecto"
    )

    note = fields.Text(
        u'Descripción',
        states={'done': [('readonly', True)]}
    )

    parent_curso_id = fields.Many2one(
        'curso.curso',
        u'Curso padre donde se inserta este'
    )

    first_lecture_id = fields.Many2one(
        'curso.lecture',
        u'Clase inicial de este curso'
    )

    user_id = fields.Many2one(
        'res.users',
        string=u'Responsable',
        default=lambda self: self.env.user,
        readonly=False, states={'done': [('readonly', True)]}
    )

    product = fields.Many2one(
        'product.product', u'Producto',
        required=True,
        readonly=True,
        domain="[('tot_hs_lecture','!=','0')]",
        states={'draft': [('readonly', False)]},
        help=u'Producto de donde este curso fue generado'
    )

    email_registration_id = fields.Many2one(
        'email.template',
        u'Confirmación de inscripción',
        required=True,
        help=u'Plantilla de mail que se enviará cada vez que un alumno de este curso '
             u'pase al estado señado.'
    )

    email_recovery_id = fields.Many2one(
        'email.template',
        u'Recuperatorios de clases',
        required=True,
        help=u'Plantilla de mail que se enviará cada vez que un alumno este ausente para permitir recuperar la clase.'
    )

    email_confirmation_id = fields.Many2one(
        'email.template',
        u'Confirmación curso',
        help=u"Si definis una plantilla de mail, cada participante recibirá este "
             u"mail anunciando la confirmación del curso."
    )

    main_speaker_id = fields.Many2one(
        'res.partner',
        u'Profesora',
        required=True,
        states={'done': [('readonly', True)]},
        help=u"La profesora que va a dar el curso."
    )

    secondary_speaker_id = fields.Many2one(
        'res.partner', u'Asistente',
        states={'done': [('readonly', True)]},
        help=u"La asistente del curso."
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'curso.curso'),
        required=False,
        readonly=False,
        states={'done': [('readonly', True)]}
    )

    registration_ids = fields.One2many(
        'curso.registration',
        'curso_id',
        u'Inscripciones',
        states={'done': [('readonly', True)],
                'cancel': [('readonly', True)]}
    )

    lecture_ids = fields.One2many(
        'curso.lecture',
        'curso_id',
        u'Clases',
        help='Las clases que componen este curso'
    )

    diary_ids = fields.One2many(
        'curso.diary',
        'curso_id',
        u'Agenda',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Define los dias y horarios en los que se da el curso'
    )

    state = fields.Selection([
        ('draft', 'Borrador'),  # estado inicial
        ('confirm', 'Confirmado'),  # se publica
        ('in_progress', 'En progreso'),
        # está activo, verifica fechas inicio - fin
        ('done', 'Cumplido'),  # está cumpllido verifica fechas fin
        ('cancel', 'Cancelado')  # está cancelado no se publica
    ],
        'Estado', readonly=True, required=True,
        default='draft',
        help=u"Borrador:   Está recién creado\n"
             u"Confirmado: Se publica en el sitio\n"
             u"Cursando:   Está activo, se verifica que con las fechas de primera y ultima clase\n"
             u"Cumplido:   Terminó la fecha es posterior a la de la ultima clase\n'."
             u"Cancelado:  Desaparece de la publicacion'.")

    tot_hs_lecture = fields.Integer(
        related='product.tot_hs_lecture',
        readonly=True,
        string=u'Tot Hs',
        help=u'Cantidad total de horas cátedra del curso'
    )

    list_price = fields.Float(
        related='product.list_price',
        readonly=True,
        string='Cuota',
        help=u'Es el valor de la cuota, o el total si es solo un pago.'
    )

    hs_lecture = fields.Integer(
        related='product.hs_lecture',
        readonly=True,
        string=u'Hs')

    default_code = fields.Char(
        related='product.default_code',
        readonly=True,
        string=u'Código',
        help=u'Código por defecto del producto'
    )

    no_quotes = fields.Integer(
        related='product.no_quotes',
        readonly=True,
        string='#cuotas',
        help=u'Cantidad de cuotas para pagar el curso'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
        store=True, compute='_compute_country'
    )

    register_max = fields.Integer(
        u'Vacantes max',
        help=u"La cantidd máxima de vacantes del curso."
    )

    register_min = fields.Integer(
        u'Vacantes min',
        help=u"La cantidad mínima de inscripciones en el curso. Si no hay "
             u"suficientes inscripcones no se puede arrancar el curso. (poner 0 para "
             u"ignorar la regla)"
    )

    register_attended = fields.Integer(
        compute='_compute_register',
        string='Egresadas',
        help=u"Cantidad de alumnas que terminó el curso con éxito."
    )

    register_current = fields.Integer(
        compute='_compute_register',
        string='Confirmadas',
        help=u"La cantidad de alumnas que confirmaron pagando (al menos una seña)"
    )

    register_avail = fields.Integer(
        compute='_compute_register',
        string='Vacantes',
        help=u"La cantidad de vacantes que le queda al curso, teniendo en cuenta las "
             u"alumnas que se anotan para recuperar en alguna de las clases"
    )

    register_prospect = fields.Integer(
        compute='_compute_register',
        string='Interesadas',
        help=u"La cantidad de alumnas interesadas que todavía no concretaron"
    )

    register_cancel = fields.Integer(
        compute='_compute_register',
        string='Canceladas',
        help=u"La cantidad de alumnas que cancelaron el curso"
    )

    register_virtual = fields.Integer(
        compute='_compute_register',
        string='Virtuales',
        help=u"La cantidad de alumnas que hay en la clase con mas alumnas",
        store=True
    )

    register_percent = fields.Float(
        compute='_compute_register'
    )

    is_subscribed = fields.Boolean(
        compute='_compute_is_suscribed',
        string='Subscribed'
    )

    classes_per_week = fields.Integer(
        compute='compute_classes_per_week',
        string='Clases por semana',
        help=u"La cantidad de clases por semana"
    )

    curso_instance = fields.Char(
        compute='_compute_instance',
        string='Curso'
    )

    name = fields.Char(
        compute='_compute_name',
        store=True,
        string='Nombre del curso'
    )

    no_lectures = fields.Char(
        compute='_compute_no_lectures',
        string='Clases',
        help=u"La cantidad de clases que tiene el curso"
    )

    address_id = fields.Many2one(
        'res.partner',
        string='Location',
        default=lambda self: self.env.user.company_id.partner_id,
        readonly=False, states={'done': [('readonly', True)]}
    )

    next = fields.Boolean(
        compute='_compute_next',
        search='_search_next',
        help='curso por venir'
    )

    error = fields.Char(
        compute='_compute_error',
        help='Indica si el curso tiene un error',
    )

    @api.depends('lecture_ids')
    def _compute_date_end(self):
        """ obtener la fecha de la ultima clase, cuando termina el curso, si 
            no tiene clases es false 
        """
        for rec in self:
            lects = rec.lecture_ids.search([('curso_id', '=', rec.id)],
                                           order='date desc', limit=1)
            rec.date_end = lects[0].date if lects else False

    @api.depends('register_min', 'register_current', 'register_max', 'next',
                 'state',
                 'registration_ids', 'lecture_ids')
    def _compute_error(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.error = ''
                return

            if rec.state not in ['cancel'] and not rec.date_end:
                rec.error = 'El curso no tiene clases'
                return

            if rec.state not in ['cancel', 'done'] \
                and rec.date_end < datetime.today().strftime('%Y-%m-%d'):
                rec.error = 'Hay que terminar o cancelar este curso'
                return

            if not rec.next and self.state in ['draft', 'confirmed']:
                rec.error = 'Debería estar en estado cursando'
                return

            if rec.register_min and rec.register_min >= rec.register_current:
                rec.error = 'No alcanza mínimo de alumnas'
                return

            if rec.register_max and rec.register_max == rec.register_current:
                rec.error = 'El curso está completo'
                return

            if rec.state in ['in_progress', 'done', 'cancel']:
                domain = [('curso_id', '=', rec.id)]
                for reg in self.registration_ids.search(domain):
                    if reg.state == 'signed':
                        rec.error = 'La alumna (%s) no puede estar en ' \
                                    'estado señada' % reg.partner_id.name
                        return

    def _search_next(self, operator, value):
        return [('date_begin', '>', datetime.today().strftime('%Y-%m-%d'))]

    @api.depends('date_begin')
    def _compute_next(self):
        for rec in self:
            rec.next = rec.date_begin > datetime.today().strftime('%Y-%m-%d')

    @api.constrains('date_begin', 'diary_ids')
    def _check_first_date(self):
        """ Verifica que la fecha de inicio sea el primer dia del diary
            Si no tiene fecha de inicio no chequea nada
        """
        try:
            # fecha de inicio
            dt = datetime.strptime(self.date_begin, '%Y-%m-%d')
            # fecha
            date_begin = dt.strftime('%d/%m/%Y')
            # nombre del dia
            date_begin_day = dt.strftime('%A').decode('utf-8',
                                                      'ignore').capitalize()
            # numero de dia de la semana
            wd_date_no = dt.strftime('%w')

            # diario
            dry = self.diary_ids[0]
            weekday = dry.weekday_name  # nombre del dia
            wd_diary_no = dry.weekday  # código del dia
        except:
            wd_date_no = wd_diary_no = 1

        if int(wd_date_no) != int(wd_diary_no):
            raise ValidationError(
                u"No se puede salvar el curso porque la fecha de inicio "
                u"({}) cae en {} y el primer dia de la agenda es {}.".format(
                    date_begin, date_begin_day, weekday))

    @api.depends('registration_ids.user_id', 'registration_ids.state')
    def _compute_is_suscribed(self):
        """ Determine whether the current user is already subscribed to any 
            event in `self` 
        """
        for rec in self:
            user = rec.env.user
            rec.is_subscribed = any(
                reg.user_id == user and reg.state in ('open', 'done')
                for reg in rec.registration_ids
            )

    @api.depends('register_max', 'registration_ids', 'lecture_ids')
    def _compute_register(self):
        """ Calcula las vacantes
        """
        for rec in self:
            reg_virtual = reg_current = reg_attended = reg_prospect = 0
            reg_cancel = 0
            for registration in rec.registration_ids:
                # las que señaron o pagaron o estan cursando
                if registration.state == 'confirm' or \
                        registration.state == 'signed':
                    reg_current += registration.nb_register
                    # las que terminaron
                elif registration.state == 'done':
                    reg_attended += registration.nb_register
                    # las que estan interesadas
                elif registration.state == 'draft':
                    reg_prospect += registration.nb_register
                    # las que cancelaron
                elif registration.state == 'cancel':
                    reg_cancel += registration.nb_register

            # cada clase de este curso puede tener distinta cantidad de 
            # alumnas porque puede haber gente que recupera, aqui calculamos 
            # la cantidad más grande de alumnas que puede haber en alguna 
            # clase a eso le llamamos la cantidad virtual
            for lec in rec.lecture_ids:
                reg_virtual = max([lec.reg_virtual, reg_virtual])

            rec.register_virtual = reg_virtual
            rec.register_current = reg_current
            rec.register_attended = reg_attended
            rec.register_prospect = reg_prospect
            rec.register_cancel = reg_cancel
            percent = float(reg_virtual) / float(
                rec.register_max) * 100 if rec.register_max != 0 else 0
            rec.register_percent = percent

            # the number of vacants is unlimited if the curso.register_max
            # field is not set. In that case we arbitrary set it to 9999,
            # it is used in the kanban view to special case the display of
            # the 'subscribe' button
            rec.register_avail = rec.register_max - reg_virtual \
                if rec.register_max != 0 else 9999

    def compute_classes_per_week(self):
        """ Calcula la cantidad de clases por semana basado en el diary
        """
        for rec in self:
            diary_obj = self.env['curso.diary']
            qty = diary_obj.search_count([('curso_id', '=', self.id)])
            rec.classes_per_week = qty

    @api.depends('default_code', 'instance')
    def _compute_instance(self):
        for rec in self:
            rec.curso_instance = '{}/{:0>2d}'.format(rec.default_code,
                                                     rec.instance)

    @api.onchange('diary_ids')
    @api.depends('date_begin', 'curso_instance', 'product.name', 'diary_ids')
    def _compute_name(self):
        for rec in self:
            try:
                init = datetime.strptime(rec.date_begin, "%Y-%m-%d")
            except:
                weekday = day_n = month_n = year_n = '?'
            else:
                weekday = init.strftime("%a").capitalize()
                day_n = init.strftime('%d')
                month_n = init.strftime('%m')
                year_n = init.strftime('%y')
            hhs = mms = hhe = mme = 0
            for diary_line in rec.diary_ids.search(
                [('curso_id', '=', self.id)]):
                ss = diary_line.schedule.start_time
                ee = diary_line.schedule.end_time
                mms = ss - int(ss)
                hhs = int(ss - mms)
                mms = int(mms * 60)
                mme = ee - int(ee)
                hhe = int(ee - mme)
                mme = int(mme * 60)
                break

            # https://docs.python.org/2/library/datetime.html#datetime-objects
            fmt = u'[{}] {} {}/{}/{} ({:0>2d}:{:0>2d} {:0>2d}:{:0>2d}) - {}'
            rec.name = fmt.format(
                rec.curso_instance,
                # Codigo de producto, Nro de instancia
                unicode(weekday.capitalize(), 'utf-8'),
                # dia de la semana en letras
                day_n, month_n, year_n,  # dia , mes, anio en numeros
                hhs, mms, hhe, mme,  # hora de inicio hora de fin
                rec.product.name)  # nombre del producto

    @api.depends('tot_hs_lecture', 'hs_lecture')
    def _compute_no_lectures(self):
        for rec in self:
            try:
                rec.no_lectures = int(rec.tot_hs_lecture / rec.hs_lecture)
                if rec.tot_hs_lecture % rec.hs_lecture != 0:
                    raise
            except:
                self.no_lectures = 'Error!'

    @api.depends('address_id')
    def _compute_country(self):
        for rec in self:
            rec.country_id = rec.address_id.country_id

    def button_generate_lectures(self):
        """ Generar las clases que correspondan a este curso
        """
        for rec in self:
            date_begin = datetime.strptime(rec.date_begin, '%Y-%m-%d')
            tot_hs_lecture = rec.tot_hs_lecture
            hs_lecture = rec.hs_lecture
            #        default_code = self.default_code
            if operator.mod(tot_hs_lecture, hs_lecture) != 0:
                raise Warning(
                    'Error!', u"la cantidad de horas catedra no es divisible "
                              u"por las horas de clase!.")

            no_lectures = int(tot_hs_lecture // hs_lecture)
            weekload = rec.get_weekload()

            if weekload == []:
                raise Warning('Error!', u"No se definió la agenda!.")

            # get lecture templates
            lecture_templates = rec.get_lecture_templates(rec.product.id)

            # get a lectures list or an exception if overlaps.
            seq = 1
            lectures = []
            for date, schedule, room in rec.lectures_list(
                rec.weekdays(weekload, date_begin), no_lectures):
                if not rec.lecture_overlaps(date, schedule, room):
                    lectures.append(
                        {'date': date,
                         'schedule': schedule,
                         'curso': rec,
                         'seq': seq}
                    )
                    seq += 1
                else:
                    raise Warning('Error!',
                                  u'La clase del %s en el horario %s y en el '
                                  u'aula %s se superpone con una ya existente',
                                  date, schedule.name, room)

            if len(lectures) != len(lecture_templates):
                raise Warning('Error!',
                              u'La cantidad de clases no coincide con la '
                              u'cantidad de contenidos.')

            lecs = []
            for ix, lec in enumerate(lectures):
                lec['name'] = lecture_templates[ix]['name']
                lec['curso_id'] = lectures[ix]['curso'].id
                lec['schedule_id'] = lectures[ix]['schedule'].id
                lec['date_start'] = lectures[ix]['schedule'].start_datetime(
                    lec['date'])
                lec['date_stop'] = lectures[ix]['schedule'].stop_datetime(
                    lec['date'])
                lec['seq'] = lectures[ix]['seq']
                lecs.append(lec)

            # Add lectures
            lectures = rec.env['curso.lecture'].search(
                [('curso_id', '=', rec.id)])
            for lecture in lectures:
                lecture.unlink()

            for lec in lecs:
                lectures.create(lec)

    @api.constrains('register_max', 'register_virtual')
    def _check_seats_limit(self):
        """ Verifica que no se pase el máximo de vacantes, tiene en cuenta el
            register_virtual que es la cantidad de alumnas en la clase que
            tiene mas alumnas.
            Además si register_max = 0 no se valida.
        """
        for rec in self:
            if rec.register_max and rec.register_virtual > rec.register_max:
                raise Warning('No hay mas vacantes en el curso {}'.format(
                    self.curso_instance))

    def button_curso_confirm(self):
        """ Confirmar curso chequeando antes que tenga fecha de inicio y que
            coincida con la agenda
        """
        for rec in self:
            # Verificar si tiene fecha de inicio.
            if not rec.date_begin:
                raise ValidationError(
                    u"No se puede confirmar el curso porque no tiene "
                    u"fecha de inicio.")

            if not rec.diary_ids:
                raise ValidationError(
                    u"No se puede confirmar el curso porque no tiene "
                    u"agenda creada.")

            if rec.email_confirmation_id:
                # send reminder that will confirm the event for all the
                # people that were already confirmed
                regs = self.registration_ids.filtered(
                    lambda reg: reg.state not in ('draft', 'cancel'))
            # regs.mail_user_confirm()
            rec.state = 'confirm'

    def button_curso_in_progress(self):
        """ Poner el curso en proceso, chequeando antes que las fechas de
            inicio y fin esten correctas
        """
        for rec in self:
            # levanta excepción si no se puede poner in_process
            rec.may_go_in_process(self)
            rec.state = 'in_progress'

    def button_curso_draft(self):
        for rec in self:
            rec.state = 'draft'

    def do_curso_done(self):
        """ Poner las alumnas del curso en estado cumplido si estan en cursando y tienen todas las clases """
        for rec in self:
            # recorrer las alumnas del curso
            for registration in rec.registration_ids:
                # las que estan cursando (confirm)
                if registration.state in 'confirm':
                    # recorro las asistencias
                    for assist in registration.partner_id.assistance_id:
                        # verificar que hizo todas las clases
                        if assist.state not in 'programmed,absent,abandoned':
                            registration.state = 'done'

    def may_go_in_process(self, silent=False):
        for rec in self:
            # verificar si está confirmado
            if rec.state != 'confirm':
                if silent:
                    return False
                else:
                    raise ValidationError(
                        u'Debe estar confirmado para pasarlo a En proceso')

        today = datetime.today().strftime('%Y-%m-%d')
        # Verificar si la fecha actual es menor que la de inicio.
        if rec.date_begin < today:
            if silent:
                return False
            else:
                raise Warning(u"No se puede arrancar el curso antes de su "
                              u"fecha de inicio")

        # Verificar si la fecha actual es igual o menor que la fecha de fin.
        if rec.date_end > today:
            if silent:
                return False
            else:
                raise ValidationError(u"No se puede arrancar el curso, porque "
                                      u"ya pasó su fecha de finalización")
        return True

    def may_go_done(self, silent=False):
        for rec in self:
            if rec.state != 'in_process':
                if silent:
                    return False
                else:
                    raise Warning

            today = datetime.today().strftime('%Y-%m-%d')
            if rec.date_end < today:
                if silent:
                    return False
                else:
                    raise Warning('Error!', u"El curso todavia no termina.")
            return True

    def button_curso_done(self):
        """ Terminar el curso, y también a las alumnas que cursaron y
            completaron todas las clases
        """
        for rec in self:
            # chequear que el curso se puede terminar levanta excepcion si no
            rec.may_go_done()

            # terminar el curso en cada alumna
            rec.do_curso_done()
            rec.state = 'done'

    def do_invoice(self, actual_price, instance_code, seq, partner_id):
        """ Genera una factura relacionada con este curso """
        for rec in self:
            date_invoice = datetime.today()
            date_due = (date_invoice + timedelta(days=10))

            invoice_lines = []
            invoice_line = {
                'name': u'Recuperación clase {} del curso {}'.format(seq,
                                                                     instance_code),
                'sequence': 5,
                'invoice_id': False,
                # TODO aca hay una cuenta contable harcodeada !!!
                'account_id': 88,  # venta de cursos
                'price_unit': actual_price,
                'quantity': 1.0,
            }
            invoice_line = rec.env['account.invoice.line'].create(invoice_line)

            invoice_lines.append(invoice_line.id)

            new_invoice = {
                'date_due': date_due.strftime('%Y-%m-%d'),
                'date_invoice': date_invoice.strftime('%Y-%m-%d'),
                'name': '{} C{:.0f}'.format(instance_code, seq),
                'type': 'out_invoice',
                'reference': '{} recuperatorio C{:.0f}'.format(instance_code,
                                                               seq),
                'account_id': 11,
                'partner_id': partner_id.id,
                'journal_id': 29,
                'invoice_line': [(6, 0, invoice_lines)],
                'currency_id': 20,  # commission.invoice.currency_id.id,
                'comment': 'generado automáticamente',
                'fiscal_position': partner_id.property_account_position.id,
                'company_id': rec.company_id.id,
                'user_id': self._uid
            }
            self.env['account.invoice'].create(new_invoice)
