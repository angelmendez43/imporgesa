# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
import io
import logging
from datetime import datetime
import datetime

class RecuperacionPagosWizard(models.TransientModel):
    _name = 'imporgesa.recuperacion_pagos.wizard'
    _description = "Wizard para reporte de recuperacion de pagos"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'imporgesa.recuperacion_pagos.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('imporgesa.action_recuperacion_pagos').report_action([], data=data)


    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w.fecha_inicio
            dict['fecha_fin'] = w.fecha_fin

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Recuperación de pagos')
            formato_titulo = libro.add_format({'size': 11, 'color':'#0d354d', 'align':'center', 'fg_color':'#ffffff', 'bold':False})
            #Tamaño de las columnas
            hoja.set_column('A:N', 20)

            hoja.write(1, 0, 'Fecha recuperación', formato_titulo)
            hoja.write(1, 1, 'Correlativo pago', formato_titulo)
            hoja.write(1, 2, 'Forma de pago', formato_titulo)
            hoja.write(1, 3, 'Descripción', formato_titulo)
            hoja.write(1, 4, 'Monto', formato_titulo)
            # hoja.write(1, 5, 'Forma de pago', formato_titulo)
            #hoja.write(1, 5, 'Usuario que recupero', formato_titulo)
            hoja.write(1, 5, 'Comercial del pago', formato_titulo)
            hoja.write(1, 6, 'Establecimiento', formato_titulo)
            hoja.write(1, 7, 'Correlativo factura', formato_titulo)
            hoja.write(1, 8, 'Fecha factura', formato_titulo)
            hoja.write(1, 9, 'Saldo factura', formato_titulo)
            hoja.write(1, 10, 'Cliente', formato_titulo)
            hoja.write(1, 11, 'NIT', formato_titulo)
            hoja.write(1, 12, 'Sucursal', formato_titulo)
            hoja.write(1, 13, 'Días de recuperación', formato_titulo)
            #hoja.write(1, 13, 'Porcentajes de recuperación', formato_titulo)

            pagos = self.env['account.payment'].search([('date', '>=', w.fecha_inicio), ('date', '<=', w.fecha_fin), ('payment_type', '=', 'inbound')])

            fila=2
            for pago in pagos:
                fecha_pago = pago.date.strftime('%d/%m/%Y')
                hoja.write(fila, 0, fecha_pago)
                hoja.write(fila, 1, pago.name)
                hoja.write(fila, 2, pago.journal_id.name)
                if pago.descripcion:
                    hoja.write(fila, 3, pago.descripcion)
                hoja.write(fila, 4, pago.amount)
                #if pago.vendedor_id:
                    #hoja.write(fila, 5, pago.vendedor_id.name)
                if pago.partner_id.user_id:
                    hoja.write(fila, 5, pago.partner_id.user_id.name)
                if pago.reconciled_invoices_count:
                    fel_serie_fel_numero = ''
                    for factura in pago.reconciled_invoice_ids:
                        if factura.fel_serie and factura.fel_numero:
                            fel_serie_fel_numero = str(factura.fel_serie)+'-'+str(factura.fel_numero)
                        fecha_factura = factura.invoice_date.strftime('%d/%m/%Y')
                        hoja.write(fila, 6, factura.journal_id.name)
                        hoja.write(fila, 7, fel_serie_fel_numero)
                        hoja.write(fila, 8, fecha_factura)
                        hoja.write(fila, 9, factura.amount_residual)
                        hoja.write(fila, 10, factura.partner_id.name)
                        hoja.write(fila, 11, factura.partner_id.vat)
                        hoja.write(fila, 12, factura.journal_id.name)
                        dias_recuperacion = pago.date - factura.invoice_date
                        hoja.write(fila, 13, dias_recuperacion)
                        # if pago.invoice_user_id and pago.journal_id.pago_comisiones:
                        #     for linea in pago.journal_id.pago_comisiones:
                        #         if pago.invoice_user_id.id == linea.vendedor_id.id:
                        #             porcentaje = linea.comision / 100
                        #             porcentaje_comision = round(pago.amount * porcentaje,2)                                    
                        # 
                        # if pago.vendedor_id and pago.journal_id.pago_comisiones:
                        #     for linea in pago.journal_id.pago_comisiones:
                        #         if pago.vendedor_id.id == linea.vendedor_id.id:
                        #             logging.warning(pago.vendedor_id.name)
                        #             logging.warning(linea.vendedor_id.id)
                        #             porcentaje = linea.comision / 100
                        #             porcentaje_comision = round(pago.amount * porcentaje,2)
                                    #hoja.write(fila, 13, porcentaje_comision)

                fila+=1
            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'Recuperacion_pagos.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'imporgesa.recuperacion_pagos.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
