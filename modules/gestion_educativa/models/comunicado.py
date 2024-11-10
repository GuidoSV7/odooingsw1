from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Comunicado(models.Model):
    _name = 'gestion_educativa.comunicado'
    _description = 'Comunicado escolar'
    _rec_name = 'titulo'

    titulo = fields.Char(string='Título', required=True)
    donde = fields.Char(string='Donde', required=True)
    cuando = fields.Datetime(string='Cuando', required=True)
    motivo = fields.Text(string='Motivo', required=True)
    visto = fields.Boolean(string='Visto', default=False)

    # Hacemos que el profesor_creador_id sea opcional
    profesor_creador_id = fields.Many2one(
        'gestion_educativa.profesor',
        string='Creado por Profesor',
        required=False  # Cambiamos a False para que sea opcional
    )

    imagen = fields.Binary(
        string='Imagen',
        attachment=True,
        help="Imagen del comunicado",
        store=True
    )
    imagen_filename = fields.Char("Nombre del archivo")

    # Campos para seleccionar todos
    todos_profesores = fields.Boolean(string='Enviar a todos los profesores')
    todos_apoderados = fields.Boolean(string='Enviar a todos los apoderados')
    todos_alumnos = fields.Boolean(string='Enviar a todos los alumnos')

    # Relaciones para destinatarios específicos
    profesor_ids = fields.Many2many(
        'gestion_educativa.profesor',
        'profesor_comunicado_rel',
        'comunicado_id',
        'profesor_id',
        string='Profesores destinatarios'
    )
    apoderado_ids = fields.Many2many(
        'gestion_educativa.apoderado',
        'apoderado_comunicado_rel',
        'comunicado_id',
        'apoderado_id',
        string='Apoderados destinatarios'
    )
    alumno_ids = fields.Many2many(
        'gestion_educativa.alumno',
        'alumno_comunicado_rel',
        'comunicado_id',
        'alumno_id',
        string='Alumnos destinatarios'
    )

    # Resto de tus métodos...

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('imagen'):
                vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('imagen'):
            vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()
        return super().write(vals)

    @api.onchange('todos_profesores')
    def _onchange_todos_profesores(self):
        if self.todos_profesores:
            self.profesor_ids = [(6, 0, self.env['gestion_educativa.profesor'].search([]).ids)]
        else:
            self.profesor_ids = [(5, 0, 0)]

    @api.onchange('todos_apoderados')
    def _onchange_todos_apoderados(self):
        if self.todos_apoderados:
            self.apoderado_ids = [(6, 0, self.env['gestion_educativa.apoderado'].search([]).ids)]
        else:
            self.apoderado_ids = [(5, 0, 0)]

    @api.onchange('todos_alumnos')
    def _onchange_todos_alumnos(self):
        if self.todos_alumnos:
            self.alumno_ids = [(6, 0, self.env['gestion_educativa.alumno'].search([]).ids)]
        else:
            self.alumno_ids = [(5, 0, 0)]