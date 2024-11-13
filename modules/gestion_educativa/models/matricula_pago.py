from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MatriculaPago(models.Model):
    _name = 'gestion_educativa.matricula_pago'
    _description = 'Pago de Matrícula'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'numero_referencia'
    monto = fields.Float(string='Monto', required=True)
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    ], string='Estado', default='borrador', required=True, tracking=True)
    
    apoderado_id = fields.Many2one('gestion_educativa.apoderado', string='Apoderado', required=True)
    alumno_id = fields.Many2one('gestion_educativa.alumno', string='Alumno', required=True, domain="[('apoderado_id', '=', apoderado_id)]")
    fecha_pago = fields.Date(string='Fecha de Pago', required=True)
    factura_id = fields.Many2one('account.move', string='Factura', readonly=True)
    anio_academico = fields.Char(string='Año Académico', required=True)
    numero_referencia = fields.Char(
        string='Número de Recibo',
        readonly=True,
        copy=False,
        tracking=True,
        default='Nuevo'
    )

    # ... (otros campos se mantienen igual)
    
    @api.model
    def default_get(self, fields):
        res = super(MatriculaPago, self).default_get(fields)
        if 'apoderado_id' in self.env.context:
            apoderado_id = self.env.context['apoderado_id']
            res['alumno_id'] = self.env['gestion_educativa.alumno'].search([
                ('apoderado_id', '=', apoderado_id)
            ], limit=1).id
        return res

    def action_generar_factura(self):
        self.ensure_one()

        if not self.monto or self.monto <= 0:
            raise ValidationError('Por favor, ingrese un monto válido para la matrícula.')

        if not self.alumno_id:
            raise ValidationError('Debe seleccionar un alumno para generar la factura.')

        if not self.apoderado_id or not self.apoderado_id.partner_id:
            raise ValidationError(
                'El apoderado debe tener un contacto de facturación asociado. '
                'Por favor, configure el contacto en el registro del apoderado.'
            )

        # Buscar la cuenta de ingresos por defecto
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if not journal:
            raise ValidationError(
                'No se encontró un diario de ventas configurado. '
                'Por favor, configure un diario de ventas en el módulo de contabilidad.'
            )

        try:
            # Crear la factura
            invoice_vals = {
                'partner_id': self.apoderado_id.partner_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f'Matrícula {self.anio_academico} - {self.alumno_id.nombre_completo}',
                    'quantity': 1,
                    'price_unit': self.monto,
                    'account_id': journal.default_account_id.id,
                })],
            }

            factura = self.env['account.move'].create(invoice_vals)

            # Actualizar el registro de pago
            self.write({
                'factura_id': factura.id,
                'estado': 'pendiente'
            })

            # Mostrar mensaje de éxito y acción para ver la factura
            return {
                'name': 'Factura',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': factura.id,
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'form_view_initial_mode': 'edit'},
            }

        except Exception as e:
            raise ValidationError(f'Error al generar la factura: {str(e)}')

    @api.model
    def create(self, vals):
        if not vals.get('numero_referencia'):
            vals['numero_referencia'] = self.env['ir.sequence'].next_by_code('matricula.pago.sequence')
        return super().create(vals)

    @api.constrains('monto')
    def _check_monto(self):
        for record in self:
            if record.monto <= 0:
                raise ValidationError('El monto debe ser mayor que cero.')