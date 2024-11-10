from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Alumno(models.Model):
    _name = 'gestion_educativa.alumno'
    _description = 'Alumno del centro educativo'
    _rec_name = 'nombre_completo'

    nombre_completo = fields.Char(string='Nombre Completo', required=True)
    ci = fields.Char(string='CI', required=True)
    direccion = fields.Text(string='Dirección')
    numero_matricula = fields.Char(string='Número de Matrícula', required=True)
    telefono = fields.Char(string='Teléfono')
    numero_kardex = fields.Char(string='Número de Kardex', required=True)
    token_notifi = fields.Char(string='Token de Notificación')  
    
    # Relaciones
    grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
    apoderado_id = fields.Many2one('gestion_educativa.apoderado', string='Apoderado', required=True)
    comunicado_ids = fields.Many2many(
        'gestion_educativa.comunicado',
        'alumno_comunicado_rel',
        'alumno_id',
        'comunicado_id',
        string='Comunicados Recibidos'
    )