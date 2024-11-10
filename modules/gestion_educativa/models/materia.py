from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Materia(models.Model):
    _name = 'gestion_educativa.materia'
    _description = 'Materia académica'
    _rec_name = 'nombre'

    nombre = fields.Char(string='Nombre', required=True)
    sigla = fields.Char(string='Sigla', required=True)
    
    # Relaciones
    horario_ids = fields.One2many('gestion_educativa.horario', 'materia_id', string='Horarios')