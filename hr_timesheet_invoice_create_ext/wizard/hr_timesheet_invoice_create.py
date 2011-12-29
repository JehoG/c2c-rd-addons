# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
from osv import osv, fields
from tools.translate import _
#
# TODO: check unit of measure !!!
#
class hr_timesheet_invoice_create(osv.osv_memory):

    _inherit = 'hr.timesheet.invoice.create'
    _columns = \
        { 'date_invoice' : fields.date
            ( 'Date Invoice'
            , help='The date of the invoice or empty will take the current day on validate'
            )
        , 'description'  : fields.char
            ( 'Prefix Invoice Text'
            , size=16
            , help='This text will be placed before the name of the analytic account instead of the current date'
            )
        , 'journal_id'   : fields.many2one
            ( 'account.journal'
            , 'Journal'
            , help='The journal to be used'
            )
        , 'reference'    : fields.char
            ( 'Reference'
            , size=64
            , help='The reference on the invoice, usually the period of service'
            )
        }
    _defaults = {'reference' : lambda *a: 'automatic'}
    
    def _ref(self, dates) :
        _min = datetime.datetime.strptime(dates[0][0:10], '%Y-%m-%d') 
        _max = datetime.datetime.strptime(dates[-1][0:10], '%Y-%m-%d')
        if _min.year != _max.year :
            return _('Clearing period: ') + dates[0] + ".." + dates[-1]
        else :
            if _min.month == _max.month :
                return _('Clearing period: ') + datetime.datetime.strftime(_min,"%b") + " " + str(_min.year)
            else :
                for i, r in enumerate([range(1,4), range(4,7), range(7,10), range(10,13)]) :
                    if (_min.month in r) and (_max.month in r) :
                        return _('Clearing period: ') + str(i+1) + _(".Quarter ") + str(_min.year)
                for i, r in enumerate([range(1,7), range(6,13)]) :
                    if (_min.month in r) and (_max.month in r) :
                        return _('Clearing period: ') + str(i+1) + _(".Half-year ") + str(_min.year)
                return _('Clearing period: ') + _("Calendaryear ") + str(_min.year)
    # end def _ref

    def do_create(self, cr, uid, ids, context=None) :
        act_win = super(hr_timesheet_invoice_create, self).do_create(cr, uid, ids, context)
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_obj = self.pool.get('account.analytic.line')
        inv_obj  = self.pool.get('account.invoice')

        inv_ids = []
        for d in act_win.get('domain') :
            if d[0] == 'id' : 
                inv_ids = d[2]

        for inv in inv_obj.browse(cr, uid, inv_ids) :
            if data['reference'] == 'automatic' :
                analytic_ids = line_obj.search(cr, uid, [('invoice_id','=',inv.id)])
                lines = line_obj.browse(cr, uid, analytic_ids)
                ref = self._ref(sorted([l.date for l in lines]))
            else :
                ref = data['reference'] or False
            values = \
                { 'date_invoice' : data['date_invoice'] or False
                , 'reference'    : ref
                }
            if data['description'] :
                values['name'] = data['description'] + ' - ' + inv.invoice_line[0].account_analytic_id.name
            else:
                values['name'] = inv.invoice_line[0].account_analytic_id.name
            if data['journal_id'] :
                values['journal_id'] =  data['journal_id'][0]
            inv_obj.write(cr, uid, [inv.id], values)
        return act_win
    # end def do_create
hr_timesheet_invoice_create()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: