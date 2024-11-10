from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Profesor(models.Model):
    _name = 'gestion_educativa.profesor'
    _description = 'Profesor del centro educativo'
    _rec_name = 'nombre_completo'

    nombre_completo = fields.Char(string='Nombre Completo', required=True)
    ci = fields.Char(string='CI', required=True)
    direccion = fields.Text(string='Dirección')
    numero_matricula = fields.Char(string='Número de Matrícula', required=True)
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    token_notifi = fields.Char(string='Token de Notificación')  
    
    # Relaciones
    horario_ids = fields.One2many('gestion_educativa.horario', 'profesor_id', string='Horarios')
    comunicado_recibido_ids = fields.Many2many(
        'gestion_educativa.comunicado',
        'profesor_comunicado_rel',
        'profesor_id',
        'comunicado_id',
        string='Comunicados Recibidos'
    )
    comunicado_creado_ids = fields.One2many(
        'gestion_educativa.comunicado',
        'profesor_creador_id',
        string='Comunicados Creados'
    )