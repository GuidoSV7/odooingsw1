# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Apoderado(models.Model):
    _name = 'gestion_educativa.apoderado'
    _description = 'Apoderado del alumno'
    _rec_name = 'nombre_completo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    nombre_completo = fields.Char(
        string='Nombre Completo',
        required=True,
        tracking=True
    )
    ci = fields.Char(
        string='CI',
        required=True,
        tracking=True
    )
    direccion = fields.Text(
        string='Dirección',
        tracking=True
    )
    numero_matricula = fields.Char(
        string='Número de Matrícula',
        required=True,
        tracking=True
    )
    telefono = fields.Char(
        string='Teléfono',
        tracking=True
    )
    email = fields.Char(
        string='Correo Electrónico',
        tracking=True
    )
    ocupacion = fields.Char(
        string='Ocupación',
        tracking=True
    )
    token_notifi = fields.Char(
        string='Token de Notificación'
    )

    # Campo para facturación (eliminada la definición duplicada)
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto de Facturación',
        tracking=True,
        required=True
    )

    # Relaciones
    alumno_ids = fields.One2many(
        'gestion_educativa.alumno',
        'apoderado_id',
        string='Alumnos'
    )
    comunicado_ids = fields.Many2many(
        'gestion_educativa.comunicado',
        'apoderado_comunicado_rel',
        'apoderado_id',
        'comunicado_id',
        string='Comunicados Recibidos'
    )
    pago_matricula_ids = fields.One2many(
        'gestion_educativa.matricula_pago',
        'apoderado_id',
        string='Pagos de Matrícula'
    )

    # Campos computados
    matriculas_pendientes = fields.Integer(
        string='Matrículas Pendientes',
        compute='_compute_matriculas_pendientes',
        store=True
    )
    total_pagado = fields.Float(
        string='Total Pagado',
        compute='_compute_total_pagado',
        store=True
    )

    @api.model
    def create(self, vals):
        # Crear automáticamente un contacto en res.partner si no existe
        if not vals.get('partner_id'):
            partner_vals = {
                'name': vals.get('nombre_completo'),
                'email': vals.get('email'),
                'phone': vals.get('telefono'),
                'street': vals.get('direccion'),
                'vat': vals.get('ci'),  # NIT/CI para facturación
                'company_type': 'person',
            }
            partner = self.env['res.partner'].create(partner_vals)
            vals['partner_id'] = partner.id
            
        return super(Apoderado, self).create(vals)

    def write(self, vals):
        # Actualizar el contacto en res.partner
        for record in self:
            if record.partner_id:
                partner_vals = {}
                if vals.get('nombre_completo'):
                    partner_vals['name'] = vals['nombre_completo']
                if vals.get('email'):
                    partner_vals['email'] = vals['email']
                if vals.get('telefono'):
                    partner_vals['phone'] = vals['telefono']
                if vals.get('direccion'):
                    partner_vals['street'] = vals['direccion']
                if vals.get('ci'):
                    partner_vals['vat'] = vals['ci']
                
                if partner_vals:
                    record.partner_id.write(partner_vals)
                    
        return super(Apoderado, self).write(vals)

    @api.depends('pago_matricula_ids.estado')
    def _compute_matriculas_pendientes(self):
        for apoderado in self:
            apoderado.matriculas_pendientes = len(
                apoderado.pago_matricula_ids.filtered(
                    lambda p: p.estado in ['borrador', 'pendiente']
                )
            )

    @api.depends('pago_matricula_ids.monto', 'pago_matricula_ids.estado')
    def _compute_total_pagado(self):
        for apoderado in self:
            apoderado.total_pagado = sum(
                pago.monto for pago in apoderado.pago_matricula_ids.filtered(
                    lambda p: p.estado == 'pagado'
                )
            )

    def action_view_pagos(self):
        """Acción para ver los pagos de matrícula del apoderado"""
        self.ensure_one()
        return {
            'name': 'Pagos de Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion_educativa.matricula_pago',
            'view_mode': 'tree,form',
            'domain': [('apoderado_id', '=', self.id)],
            'context': {'default_apoderado_id': self.id},
        }

    def action_crear_pago(self):
        """Acción para crear un nuevo pago de matrícula"""
        self.ensure_one()
        return {
            'name': 'Nuevo Pago de Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion_educativa.matricula_pago',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_apoderado_id': self.id,
                'default_anio_academico': str(fields.Date.today().year),
            },
        }

    @api.constrains('ci')
    def _check_ci(self):
        """Validar que el CI sea único"""
        for record in self:
            if record.ci:
                duplicate = self.search([
                    ('ci', '=', record.ci),
                    ('id', '!=', record.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError('Ya existe un apoderado con este CI.')