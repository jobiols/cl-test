# -*- coding: utf-8 -*-
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
from datetime import datetime

from openerp import models, fields, api


class curso_diary(models.Model):
    """ relaciona un horario con un dia de la semana
    """
    _name = 'curso.diary'
    _order = 'seq'

    curso_id = fields.Many2one(
        'curso.curso',
        'Curso'
    )

    weekday = fields.Selection([
        ('0', u'Domingo'),
        ('1', u'Lunes'),
        ('2', u'Martes'),
        ('3', u'Miércoles'),
        ('4', u'Jueves'),
        ('5', u'Viernes'),
        ('6', u'Sábado')
    ],
        required=True,
        string=u'Día'
    )

    weekday_name = fields.Char(
        compute="_compute_weekday_name",
        string=u'Nombre del dia'
    )

    schedule = fields.Many2one(
        'curso.schedule',
        u'Horario'
    )

    seq = fields.Integer(
        u'Secuencia'
    )

    def check_weekday(self, date):
        """ Chequear que la fecha corresponda al dia del primer elemento de
            la agenda devolver false si no es cierto
        """
        return self.weekday == datetime.strptime(date, '%Y-%m-%d').strftime('%w')

    def _compute_weekday_name(self):
        for rec in self:
            dwd = {
                '0': u'Domingo',
                '1': u'Lunes',
                '2': u'Martes',
                '3': u'Miércoles',
                '4': u'Jueves',
                '5': u'Viernes',
                '6': u'Sábado'
            }
            rec.weekday_name = dwd[rec.weekday]
