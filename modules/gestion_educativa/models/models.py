# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

# class Profesor(models.Model):
#     _name = 'gestion_educativa.profesor'
#     _description = 'Profesor del centro educativo'
#     _rec_name = 'nombre_completo'

#     nombre_completo = fields.Char(string='Nombre Completo', required=True)
#     ci = fields.Char(string='CI', required=True)
#     direccion = fields.Text(string='Dirección')
#     numero_matricula = fields.Char(string='Número de Matrícula', required=True)
#     telefono = fields.Char(string='Teléfono')
#     email = fields.Char(string='Correo Electrónico')
    
#     # Relaciones
#     horario_ids = fields.One2many('gestion_educativa.horario', 'profesor_id', string='Horarios')
#     # Comunicados que el profesor recibe
#     comunicado_recibido_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         'profesor_comunicado_rel',
#         'profesor_id',
#         'comunicado_id',
#         string='Comunicados Recibidos'
#     )
#     # Comunicados que el profesor crea
#     comunicado_creado_ids = fields.One2many(
#         'gestion_educativa.comunicado',
#         'profesor_creador_id',
#         string='Comunicados Creados'
#     )

# class Horario(models.Model):
#     _name = 'gestion_educativa.horario'
#     _description = 'Horario de clases'
#     _rec_name = 'display_name'

#     dia = fields.Selection([
#         ('lunes', 'Lunes'),
#         ('martes', 'Martes'),
#         ('miercoles', 'Miércoles'),
#         ('jueves', 'Jueves'),
#         ('viernes', 'Viernes'),
#     ], string='Día', required=True)
#     hora_inicio = fields.Float(string='Hora de Inicio', required=True)
#     hora_fin = fields.Float(string='Hora de Fin', required=True)
    
#     profesor_id = fields.Many2one('gestion_educativa.profesor', string='Profesor', required=True)
#     materia_id = fields.Many2one('gestion_educativa.materia', string='Materia', required=True)
#     grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
    
#     display_name = fields.Char(compute='_compute_display_name', store=True)
    
#     @api.depends('dia', 'hora_inicio', 'hora_fin', 'materia_id', 'profesor_id')
#     def _compute_display_name(self):
#         for record in self:
#             try:
#                 if not isinstance(record.dia, bool) and record.dia and record.materia_id:
#                     record.display_name = f"{record.dia.capitalize()} - {record.materia_id.nombre} ({int(record.hora_inicio)}:00 - {int(record.hora_fin)}:00)"
#                 else:
#                     record.display_name = "Nuevo Horario"
#             except:
#                 record.display_name = "Nuevo Horario"

# class Materia(models.Model):
#     _name = 'gestion_educativa.materia'
#     _description = 'Materia académica'
#     _rec_name = 'nombre'

#     nombre = fields.Char(string='Nombre', required=True)
#     sigla = fields.Char(string='Sigla', required=True)
    
#     # Relaciones
#     horario_ids = fields.One2many('gestion_educativa.horario', 'materia_id', string='Horarios')

# class Grado(models.Model):
#     _name = 'gestion_educativa.grado'
#     _description = 'Grado académico'
#     _rec_name = 'nombre'

#     nombre = fields.Char(string='Nombre', required=True)
#     sigla = fields.Char(string='Sigla', required=True)
    
#     # Relaciones
#     horario_ids = fields.One2many('gestion_educativa.horario', 'grado_id', string='Horarios')
#     alumno_ids = fields.One2many('gestion_educativa.alumno', 'grado_id', string='Alumnos')

# class Alumno(models.Model):
#     _name = 'gestion_educativa.alumno'
#     _description = 'Alumno del centro educativo'
#     _rec_name = 'nombre_completo'

#     nombre_completo = fields.Char(string='Nombre Completo', required=True)
#     ci = fields.Char(string='CI', required=True)
#     direccion = fields.Text(string='Dirección')
#     numero_matricula = fields.Char(string='Número de Matrícula', required=True)
#     telefono = fields.Char(string='Teléfono')
#     numero_kardex = fields.Char(string='Número de Kardex', required=True)
    
#     # Relaciones
#     grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
#     apoderado_id = fields.Many2one('gestion_educativa.apoderado', string='Apoderado', required=True)
#     # Solo comunicados recibidos
#     comunicado_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         'alumno_comunicado_rel',
#         'alumno_id',
#         'comunicado_id',
#         string='Comunicados Recibidos'
#     )

# class Apoderado(models.Model):
#     _name = 'gestion_educativa.apoderado'
#     _description = 'Apoderado del alumno'
#     _rec_name = 'nombre_completo'

#     nombre_completo = fields.Char(string='Nombre Completo', required=True)
#     ci = fields.Char(string='CI', required=True)
#     direccion = fields.Text(string='Dirección')
#     numero_matricula = fields.Char(string='Número de Matrícula', required=True)
#     telefono = fields.Char(string='Teléfono')
#     email = fields.Char(string='Correo Electrónico')
#     ocupacion = fields.Char(string='Ocupación')

#     # Relaciones
#     alumno_ids = fields.One2many('gestion_educativa.alumno', 'apoderado_id', string='Alumnos')
#     # Solo comunicados recibidos
#     comunicado_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         'apoderado_comunicado_rel',
#         'apoderado_id',
#         'comunicado_id',
#         string='Comunicados Recibidos'
#     )

# class Comunicado(models.Model):
#     _name = 'gestion_educativa.comunicado'
#     _description = 'Comunicado escolar'
#     _rec_name = 'titulo'

#     titulo = fields.Char(string='Título', required=True)
#     donde = fields.Char(string='Donde', required=True)
#     cuando = fields.Datetime(string='Cuando', required=True)
#     motivo = fields.Text(string='Motivo', required=True)
#     visto = fields.Boolean(string='Visto', default=False)

#     # Campo para identificar al profesor que crea el comunicado
#     profesor_creador_id = fields.Many2one(
#         'gestion_educativa.profesor',
#         string='Creado por Profesor',
#         required=True
#     )

#     imagen = fields.Binary(
#         string='Imagen',
#         attachment=True,
#         help="Imagen del comunicado",
#         store=True
#     )
#     imagen_filename = fields.Char("Nombre del archivo")

#     # Campos para seleccionar todos
#     todos_profesores = fields.Boolean(string='Enviar a todos los profesores')
#     todos_apoderados = fields.Boolean(string='Enviar a todos los apoderados')
#     todos_alumnos = fields.Boolean(string='Enviar a todos los alumnos')

#     # Relaciones para destinatarios específicos
#     profesor_ids = fields.Many2many(
#         'gestion_educativa.profesor',
#         'profesor_comunicado_rel',
#         'comunicado_id',
#         'profesor_id',
#         string='Profesores destinatarios'
#     )
#     apoderado_ids = fields.Many2many(
#         'gestion_educativa.apoderado',
#         'apoderado_comunicado_rel',
#         'comunicado_id',
#         'apoderado_id',
#         string='Apoderados destinatarios'
#     )
#     alumno_ids = fields.Many2many(
#         'gestion_educativa.alumno',
#         'alumno_comunicado_rel',
#         'comunicado_id',
#         'alumno_id',
#         string='Alumnos destinatarios'
#     )

#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             if vals.get('imagen'):
#                 vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()
#         return super().create(vals_list)

#     def write(self, vals):
#         if vals.get('imagen'):
#             vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()
#         return super().write(vals)

#     @api.onchange('todos_profesores')
#     def _onchange_todos_profesores(self):
#         if self.todos_profesores:
#             self.profesor_ids = [(6, 0, self.env['gestion_educativa.profesor'].search([]).ids)]
#         else:
#             self.profesor_ids = [(5, 0, 0)]

#     @api.onchange('todos_apoderados')
#     def _onchange_todos_apoderados(self):
#         if self.todos_apoderados:
#             self.apoderado_ids = [(6, 0, self.env['gestion_educativa.apoderado'].search([]).ids)]
#         else:
#             self.apoderado_ids = [(5, 0, 0)]

#     @api.onchange('todos_alumnos')
#     def _onchange_todos_alumnos(self):
#         if self.todos_alumnos:
#             self.alumno_ids = [(6, 0, self.env['gestion_educativa.alumno'].search([]).ids)]
#         else:
#             self.alumno_ids = [(5, 0, 0)]