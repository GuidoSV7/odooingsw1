

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
#     token_notifi = fields.Char(string='Token de Notificación')  
    
#     # Relaciones
#     grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
#     apoderado_id = fields.Many2one('gestion_educativa.apoderado', string='Apoderado', required=True)
    
#     # Nueva relación usando tabla intermedia
#     comunicado_rel_ids = fields.One2many(
#         'gestion_educativa.comunicado.alumno',
#         'alumno_id',
#         string='Relaciones con comunicados'
#     )
#     comunicado_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         string='Comunicados Recibidos',
#         compute='_compute_comunicados'
#     )

#     @api.depends('comunicado_rel_ids')
#     def _compute_comunicados(self):
#         for alumno in self:
#             alumno.comunicado_ids = alumno.comunicado_rel_ids.mapped('comunicado_id')


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
#     token_notifi = fields.Char(string='Token de Notificación')
    
#     # Relaciones
#     horario_ids = fields.One2many(
#         'gestion_educativa.horario', 
#         'profesor_id', 
#         string='Horarios'
#     )
    
#     # Nueva relación para comunicados recibidos usando la tabla intermedia
#     comunicado_rel_ids = fields.One2many(
#         'gestion_educativa.comunicado.profesor',
#         'profesor_id',
#         string='Relaciones con comunicados'
#     )
    
#     comunicado_recibido_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         string='Comunicados Recibidos',
#         compute='_compute_comunicados'
#     )
    
#     # Mantener la relación de comunicados creados
#     comunicado_creado_ids = fields.One2many(
#         'gestion_educativa.comunicado',
#         'profesor_creador_id',
#         string='Comunicados Creados'
#     )

#     @api.depends('comunicado_rel_ids')
#     def _compute_comunicados(self):
#         for profesor in self:
#             profesor.comunicado_recibido_ids = profesor.comunicado_rel_ids.mapped('comunicado_id')

# class Materia(models.Model):
#     _name = 'gestion_educativa.materia'
#     _description = 'Materia académica'
#     _rec_name = 'nombre'

#     nombre = fields.Char(string='Nombre', required=True)
#     sigla = fields.Char(string='Sigla', required=True)
    
#     # Relaciones
#     horario_ids = fields.One2many('gestion_educativa.horario', 'materia_id', string='Horarios')


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
#     token_notifi = fields.Char(string='Token de Notificación')  
    
#     # Relaciones
#     grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
#     apoderado_id = fields.Many2one('gestion_educativa.apoderado', string='Apoderado', required=True)
    
#     # Nueva relación usando tabla intermedia
#     comunicado_rel_ids = fields.One2many(
#         'gestion_educativa.comunicado.alumno',
#         'alumno_id',
#         string='Relaciones con comunicados'
#     )
#     comunicado_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         string='Comunicados Recibidos',
#         compute='_compute_comunicados'
#     )

#     @api.depends('comunicado_rel_ids')
#     def _compute_comunicados(self):
#         for alumno in self:
#             alumno.comunicado_ids = alumno.comunicado_rel_ids.mapped('comunicado_id')

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
#     hora_inicio = fields.Char(string='Hora de Inicio', required=True)
#     hora_fin = fields.Char(string='Hora de Fin', required=True)
    
#     profesor_id = fields.Many2one('gestion_educativa.profesor', string='Profesor', required=True)
#     materia_id = fields.Many2one('gestion_educativa.materia', string='Materia', required=True)
#     grado_id = fields.Many2one('gestion_educativa.grado', string='Grado', required=True)
    
#     display_name = fields.Char(compute='_compute_display_name', store=True)
    
#     @api.depends('dia', 'hora_inicio', 'hora_fin', 'materia_id', 'profesor_id')
#     def _compute_display_name(self):
#         for record in self:
#             try:
#                 if not isinstance(record.dia, bool) and record.dia and record.materia_id:
#                     record.display_name = f"{record.dia.capitalize()} - {record.materia_id.nombre} ({record.hora_inicio} - {record.hora_fin})"
#                 else:
#                     record.display_name = "Nuevo Horario"
#             except:
#                 record.display_name = "Nuevo Horario"

# class Grado(models.Model):
#     _name = 'gestion_educativa.grado'
#     _description = 'Grado académico'
#     _rec_name = 'nombre'

#     nombre = fields.Char(string='Nombre', required=True)
#     sigla = fields.Char(string='Sigla', required=True)
    
#     # Relaciones
#     horario_ids = fields.One2many('gestion_educativa.horario', 'grado_id', string='Horarios')
#     alumno_ids = fields.One2many('gestion_educativa.alumno', 'grado_id', string='Alumnos')

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
#     token_notifi = fields.Char(string='Token de Notificación')  

#     # Relaciones
#     alumno_ids = fields.One2many('gestion_educativa.alumno', 'apoderado_id', string='Alumnos')
#     comunicado_rel_ids = fields.One2many(
#         'gestion_educativa.comunicado.apoderado',
#         'apoderado_id',
#         string='Relaciones con comunicados'
#     )
    
#     comunicado_ids = fields.Many2many(
#         'gestion_educativa.comunicado',
#         string='Comunicados Recibidos',
#         compute='_compute_comunicados'
#     )

#     @api.depends('comunicado_rel_ids')
#     def _compute_comunicados(self):
#         for apoderado in self:
#             apoderado.comunicado_ids = apoderado.comunicado_rel_ids.mapped('comunicado_id')

# class Comunicado(models.Model):
#    _name = 'gestion_educativa.comunicado'
#    _description = 'Comunicado escolar'
#    _rec_name = 'titulo'

#    titulo = fields.Selection([
#        # TITULO COMUNICADO PARA ADMINISTRATIVO
#        ('informativos', 'Informativos oficiales'),
#        ('emergencias', 'Emergencias'),
#        ('eventos', 'Eventos escolares'),
#        ('reuniones', 'Reuniones generales'),
#        ('circulares', 'Circulares generales'),
#        # TITULO COMUNICADO PARA PROFESOR
#        ('rendimiento', 'Rendimiento académico'),
#        ('comportamiento', 'Comportamiento del alumno'),
#        ('citaciones', 'Citación a apoderados'),
#        ('tareas', 'Tareas y evaluaciones'),
#        ('felicitaciones', 'Felicitaciones'),
#    ], string='Título', required=True)
   
#    donde = fields.Char(string='Donde', required=True)
#    cuando = fields.Datetime(string='Cuando', required=True)
#    motivo = fields.Text(string='Motivo', required=True)

#    profesor_creador_id = fields.Many2one(
#        'gestion_educativa.profesor',
#        string='Creado por Profesor',
#        required=False
#    )

#    imagen = fields.Binary(
#        string='Imagen',
#        attachment=True,
#        help="Imagen del comunicado",
#        store=True
#    )
#    imagen_filename = fields.Char("Nombre del archivo")
#    imagen_url = fields.Char(
#             string='URL de imagen',
#             help="URL de la imagen almacenada en Cloudinary",
#             store=True
#         )
#    todos_profesores = fields.Boolean(string='Enviar a todos los profesores')
#    todos_apoderados = fields.Boolean(string='Enviar a todos los apoderados')
#    todos_alumnos = fields.Boolean(string='Enviar a todos los alumnos')

#    # Relaciones con tablas intermedias
#    profesor_rel_ids = fields.One2many(
#        'gestion_educativa.comunicado.profesor',
#        'comunicado_id',
#        string='Relaciones con profesores'
#    )
#    apoderado_rel_ids = fields.One2many(
#        'gestion_educativa.comunicado.apoderado',
#        'comunicado_id',
#        string='Relaciones con apoderados'
#    )
#    alumno_rel_ids = fields.One2many(
#        'gestion_educativa.comunicado.alumno',
#        'comunicado_id',
#        string='Relaciones con alumnos'
#    )

#    # Campos computados para mantener compatibilidad
#    profesor_ids = fields.Many2many(
#        'gestion_educativa.profesor',
#        string='Profesores destinatarios',
#        compute='_compute_profesores'
#    )
#    apoderado_ids = fields.Many2many(
#        'gestion_educativa.apoderado',
#        string='Apoderados destinatarios',
#        compute='_compute_apoderados'
#    )
#    alumno_ids = fields.Many2many(
#        'gestion_educativa.alumno',
#        string='Alumnos destinatarios',
#        compute='_compute_alumnos'
#    )

#    def upload_image_to_cloudinary(self, image_data):
#         """
#         Upload an image to Cloudinary and return the secure URL
#         Args:
#             image_data: Base64 encoded image data
#         Returns:
#             str: Secure URL of the uploaded image, or None if upload fails
#         """
#         if not image_data:
#             return None
            
#         try:
#             # If image_data is already base64 encoded, use it directly
#             if isinstance(image_data, str):
#                 encoded_image = image_data
#             else:
#                 # If it's binary data, encode it
#                 encoded_image = base64.b64encode(image_data).decode('utf-8')

#             url = 'https://api.cloudinary.com/v1_1/da9xsfose/image/upload'
#             payload = {
#                 'file': f'data:image/png;base64,{encoded_image}',
#                 'upload_preset': 'fqw7ooma',
#             }
            
#             response = requests.post(url, json=payload)
            
#             if response.status_code == 200:
#                 return response.json().get('secure_url')
#             else:
#                 print(f"Cloudinary upload failed: {response.text}")
#                 return None
                
#         except Exception as e:
#             print(f"Error uploading to Cloudinary: {str(e)}")
#             return None

#    def _send_notifications(self, is_update=False):
#        """
#        Envía notificaciones a todos los destinatarios del comunicado
#        """
#        notification_tokens = []
       
#        # Recolectar tokens de profesores
#        if self.profesor_ids:
#            profesor_tokens = self.profesor_ids.mapped('token_notifi')
#            notification_tokens.extend(token for token in profesor_tokens if token)
           
#        # Recolectar tokens de apoderados
#        if self.apoderado_ids:
#            apoderado_tokens = self.apoderado_ids.mapped('token_notifi')
#            notification_tokens.extend(token for token in apoderado_tokens if token)
           
#        # Recolectar tokens de alumnos
#        if self.alumno_ids:
#            alumno_tokens = self.alumno_ids.mapped('token_notifi')
#            notification_tokens.extend(token for token in alumno_tokens if token)

#        if not notification_tokens:
#            return False

#        # Obtener el título formateado
#        titulo_display = dict(self._fields['titulo'].selection).get(self.titulo, self.titulo)
       
#        # Preparar el mensaje según si es creación o actualización
#     #    action_text = "actualizado" if is_update else "creado"
#     #    notification_body = f"Se ha {action_text} un comunicado: {self.motivo}"

#        notification_data = {
#            "tokens": list(set(notification_tokens)),  
#            "title": titulo_display,
#            "body": self.motivo
#        }

#        try:
#            response = requests.post(
#                "https://notificationodoo-651539c5d67d.herokuapp.com/api/send-multiple-notifications",
#                json=notification_data
#            )
#            return response.status_code == 200
#        except Exception as e:
#            return False

#    @api.depends('profesor_rel_ids')
#    def _compute_profesores(self):
#        for record in self:
#            record.profesor_ids = record.profesor_rel_ids.mapped('profesor_id')

#    @api.depends('apoderado_rel_ids')
#    def _compute_apoderados(self):
#        for record in self:
#            record.apoderado_ids = record.apoderado_rel_ids.mapped('apoderado_id')

#    @api.depends('alumno_rel_ids')
#    def _compute_alumnos(self):
#        for record in self:
#            record.alumno_ids = record.alumno_rel_ids.mapped('alumno_id')

#    def asignar_destinatarios(self, tipo, ids):
#        """
#        Asigna destinatarios al comunicado
#        tipo: 'alumno', 'profesor' o 'apoderado'
#        ids: lista de IDs de destinatarios
#        """
#        model_map = {
#            'alumno': 'gestion_educativa.comunicado.alumno',
#            'profesor': 'gestion_educativa.comunicado.profesor',
#            'apoderado': 'gestion_educativa.comunicado.apoderado'
#        }
       
#        if tipo not in model_map:
#            return

#        for dest_id in ids:
#            self.env[model_map[tipo]].create({
#                'comunicado_id': self.id,
#                f'{tipo}_id': dest_id,
#            })

#    # Override create para manejar los destinatarios al guardar
#    @api.model_create_multi
#    def create(self, vals_list):
#         for vals in vals_list:
#             if vals.get('imagen'):
#                 # Subir la imagen a Cloudinary
#                 image_url = self.upload_image_to_cloudinary(vals['imagen'])
#                 vals['imagen_url'] = image_url

#                 vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()


#             if vals.get('todos_profesores'):
#                 profesores = self.env['gestion_educativa.profesor'].search([])
#                 profesor_lines = [(0, 0, {
#                     'profesor_id': profesor.id,
#                     'visto': False
#                 }) for profesor in profesores]
#                 vals['profesor_rel_ids'] = profesor_lines

#             if vals.get('todos_apoderados'):
#                 apoderados = self.env['gestion_educativa.apoderado'].search([])
#                 apoderado_lines = [(0, 0, {
#                     'apoderado_id': apoderado.id,
#                     'visto': False
#                 }) for apoderado in apoderados]
#                 vals['apoderado_rel_ids'] = apoderado_lines

#             if vals.get('todos_alumnos'):
#                 alumnos = self.env['gestion_educativa.alumno'].search([])
#                 alumno_lines = [(0, 0, {
#                     'alumno_id': alumno.id,
#                     'visto': False
#                 }) for alumno in alumnos]
#                 vals['alumno_rel_ids'] = alumno_lines

#             if vals.get('imagen'):
#                     # Subir la imagen a Cloudinary
#                     image_url = self.upload_image_to_cloudinary(vals['imagen'])
#                     vals['imagen_url'] = image_url
#                     vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()

#         records = super().create(vals_list)
#         for record in records:
#             record._send_notifications(is_update=False)
#         return records

#     # Override write para manejar los cambios en los destinatarios
#    def write(self, vals):
#         if 'todos_profesores' in vals and vals['todos_profesores']:
#             profesores = self.env['gestion_educativa.profesor'].search([])
#             profesor_lines = [(0, 0, {
#                 'profesor_id': profesor.id,
#                 'visto': False
#             }) for profesor in profesores]
#             vals['profesor_rel_ids'] = profesor_lines

#         if 'todos_apoderados' in vals and vals['todos_apoderados']:
#             apoderados = self.env['gestion_educativa.apoderado'].search([])
#             apoderado_lines = [(0, 0, {
#                 'apoderado_id': apoderado.id,
#                 'visto': False
#             }) for apoderado in apoderados]
#             vals['apoderado_rel_ids'] = apoderado_lines

#         if 'todos_alumnos' in vals and vals['todos_alumnos']:
#             alumnos = self.env['gestion_educativa.alumno'].search([])
#             alumno_lines = [(0, 0, {
#                 'alumno_id': alumno.id,
#                 'visto': False
#             }) for alumno in alumnos]
#             vals['alumno_rel_ids'] = alumno_lines

#         if vals.get('imagen'):
#             # Subir la imagen a Cloudinary
#             image_url = self.upload_image_to_cloudinary(vals['imagen'])
#             vals['imagen_url'] = image_url
#             vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()

#         result = super().write(vals)
#         self._send_notifications(is_update=True)
#         return result

#    @api.onchange('todos_profesores')
#    def _onchange_todos_profesores(self):
#         if not self.profesor_rel_ids:
#             self.profesor_rel_ids = []
            
#         if self.todos_profesores:
#             # Buscar todos los profesores
#             profesores = self.env['gestion_educativa.profesor'].search([])
#             # Crear las líneas en memoria
#             profesor_lines = []
#             for profesor in profesores:
#                 profesor_lines.append((0, 0, {
#                     'profesor_id': profesor.id,
#                     'visto': False
#                 }))
#             self.profesor_rel_ids = profesor_lines
#         else:
#             # Limpiar las líneas
#             self.profesor_rel_ids = [(5, 0, 0)]

#    @api.onchange('todos_apoderados')
#    def _onchange_todos_apoderados(self):
#         if not self.apoderado_rel_ids:
#             self.apoderado_rel_ids = []
            
#         if self.todos_apoderados:
#             # Buscar todos los apoderados
#             apoderados = self.env['gestion_educativa.apoderado'].search([])
#             # Crear las líneas en memoria
#             apoderado_lines = []
#             for apoderado in apoderados:
#                 apoderado_lines.append((0, 0, {
#                     'apoderado_id': apoderado.id,
#                     'visto': False
#                 }))
#             self.apoderado_rel_ids = apoderado_lines
#         else:
#             # Limpiar las líneas
#             self.apoderado_rel_ids = [(5, 0, 0)]

#    @api.onchange('todos_alumnos')
#    def _onchange_todos_alumnos(self):
#         if not self.alumno_rel_ids:
#             self.alumno_rel_ids = []
            
#         if self.todos_alumnos:
#             # Buscar todos los alumnos
#             alumnos = self.env['gestion_educativa.alumno'].search([])
#             # Crear las líneas en memoria
#             alumno_lines = []
#             for alumno in alumnos:
#                 alumno_lines.append((0, 0, {
#                     'alumno_id': alumno.id,
#                     'visto': False
#                 }))
#             self.alumno_rel_ids = alumno_lines
#         else:
#             # Limpiar las líneas
#             self.alumno_rel_ids = [(5, 0, 0)]

# class ComunicadoAlumno(models.Model):
#     _name = 'gestion_educativa.comunicado.alumno'
#     _description = 'Relación entre comunicados y alumnos'
#     _rec_name = 'comunicado_id'

#     comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
#     alumno_id = fields.Many2one('gestion_educativa.alumno', required=True)
#     visto = fields.Boolean(default=False)
#     fecha_visto = fields.Datetime()

#     _sql_constraints = [
#         ('comunicado_alumno_unique', 
#          'unique(comunicado_id, alumno_id)', 
#          'Ya existe una relación para este alumno y comunicado')
#     ]

#     def marcar_como_visto(self):
#         self.write({
#             'visto': True,
#             'fecha_visto': fields.Datetime.now()
#         })

# class ComunicadoProfesor(models.Model):
#     _name = 'gestion_educativa.comunicado.profesor'
#     _description = 'Relación entre comunicados y profesores'
#     _rec_name = 'comunicado_id'

#     comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
#     profesor_id = fields.Many2one('gestion_educativa.profesor', required=True)
#     visto = fields.Boolean(default=False)
#     fecha_visto = fields.Datetime()

#     _sql_constraints = [
#         ('comunicado_profesor_unique', 
#          'unique(comunicado_id, profesor_id)', 
#          'Ya existe una relación para este profesor y comunicado')
#     ]

#     def marcar_como_visto(self):
#         self.write({
#             'visto': True,
#             'fecha_visto': fields.Datetime.now()
#         })

# class ComunicadoApoderado(models.Model):
#     _name = 'gestion_educativa.comunicado.apoderado'
#     _description = 'Relación entre comunicados y apoderados'
#     _rec_name = 'comunicado_id'

#     comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
#     apoderado_id = fields.Many2one('gestion_educativa.apoderado', required=True)
#     visto = fields.Boolean(default=False)
#     fecha_visto = fields.Datetime()

#     _sql_constraints = [
#         ('comunicado_apoderado_unique', 
#          'unique(comunicado_id, apoderado_id)', 
#          'Ya existe una relación para este apoderado y comunicado')
#     ]

#     def marcar_como_visto(self):
#         self.write({
#             'visto': True,
#             'fecha_visto': fields.Datetime.now()
#         })