from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Grado(models.Model):
    _name = 'gestion_educativa.grado'
    _description = 'Grado académico'
    _rec_name = 'nombre'

    nombre = fields.Char(string='Nombre', required=True)
    sigla = fields.Char(string='Sigla', required=True)
    
    # Relaciones
    horario_ids = fields.One2many('gestion_educativa.horario', 'grado_id', string='Horarios')
    alumno_ids = fields.One2many('gestion_educativa.alumno', 'grado_id', string='Alumnos')