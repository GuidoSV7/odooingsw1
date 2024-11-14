from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Horario(models.Model):
    _name = 'gestion_educativa.horario'
    _description = 'Horario de clases'
    _rec_name = 'display_name'

    dia = fields.Selection([
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
    ], string='Día', required=True)
    hora_inicio = fields.Char(string='Hora de Inicio', required=True)
    hora_fin = fields.Char(string='Hora de Fin', required=True)
    
    profesor_id = fields.Many2one('gestion_educativa.profesor', string='Profesor', required=True)
    materia_id = fields.Many2one('gestion_educativa.materia', string='Materia', required=True)
    grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('dia', 'hora_inicio', 'hora_fin', 'materia_id', 'profesor_id')
    def _compute_display_name(self):
        for record in self:
            try:
                if not isinstance(record.dia, bool) and record.dia and record.materia_id:
                   record.display_name = f"{record.dia.capitalize()} - {record.materia_id.nombre} ({record.hora_inicio} - {record.hora_fin})"
                else:
                    record.display_name = "Nuevo Horario"
            except:
                record.display_name = "Nuevo Horario"