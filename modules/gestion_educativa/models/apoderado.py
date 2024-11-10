from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Apoderado(models.Model):
    _name = 'gestion_educativa.apoderado'
    _description = 'Apoderado del alumno'
    _rec_name = 'nombre_completo'

    nombre_completo = fields.Char(string='Nombre Completo', required=True)
    ci = fields.Char(string='CI', required=True)
    direccion = fields.Text(string='Dirección')
    numero_matricula = fields.Char(string='Número de Matrícula', required=True)
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    ocupacion = fields.Char(string='Ocupación')
    token_notifi = fields.Char(string='Token de Notificación')  

    # Relaciones
    alumno_ids = fields.One2many('gestion_educativa.alumno', 'apoderado_id', string='Alumnos')
    comunicado_ids = fields.Many2many(
        'gestion_educativa.comunicado',
        'apoderado_comunicado_rel',
        'apoderado_id',
        'comunicado_id',
        string='Comunicados Recibidos'
    )