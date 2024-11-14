from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import base64
import logging
_logger = logging.getLogger(__name__)

class Comunicado(models.Model):
   _name = 'gestion_educativa.comunicado'
   _description = 'Comunicado escolar'
   _rec_name = 'titulo'

   titulo = fields.Selection([
       # TITULO COMUNICADO PARA ADMINISTRATIVO
       ('informativos', 'Informativos oficiales'),
       ('emergencias', 'Emergencias'),
       ('eventos', 'Eventos escolares'),
       ('reuniones', 'Reuniones generales'),
       ('circulares', 'Circulares generales'),
       # TITULO COMUNICADO PARA PROFESOR
       ('rendimiento', 'Rendimiento académico'),
       ('comportamiento', 'Comportamiento del alumno'),
       ('citaciones', 'Citación a apoderados'),
       ('tareas', 'Tareas y evaluaciones'),
       ('felicitaciones', 'Felicitaciones'),
   ], string='Título', required=True)
   
   donde = fields.Char(string='Donde', required=True)
   cuando = fields.Datetime(string='Cuando', required=True)
   motivo = fields.Text(string='Motivo', required=True)

   profesor_creador_id = fields.Many2one(
       'gestion_educativa.profesor',
       string='Creado por Profesor',
       required=False
   )

   imagen = fields.Binary(
       string='Imagen',
       attachment=True,
       help="Imagen del comunicado",
       store=True
   )
   imagen_filename = fields.Char("Nombre del archivo")
   imagen_url = fields.Char("URL de imagen")
   todos_profesores = fields.Boolean(string='Enviar a todos los profesores')
   todos_apoderados = fields.Boolean(string='Enviar a todos los apoderados')
   todos_alumnos = fields.Boolean(string='Enviar a todos los alumnos')

   # Relaciones con tablas intermedias
   profesor_rel_ids = fields.One2many(
       'gestion_educativa.comunicado.profesor',
       'comunicado_id',
       string='Relaciones con profesores'
   )
   apoderado_rel_ids = fields.One2many(
       'gestion_educativa.comunicado.apoderado',
       'comunicado_id',
       string='Relaciones con apoderados'
   )
   alumno_rel_ids = fields.One2many(
       'gestion_educativa.comunicado.alumno',
       'comunicado_id',
       string='Relaciones con alumnos'
   )

   # Campos computados para mantener compatibilidad
   profesor_ids = fields.Many2many(
       'gestion_educativa.profesor',
       string='Profesores destinatarios',
       compute='_compute_profesores'
   )
   apoderado_ids = fields.Many2many(
       'gestion_educativa.apoderado',
       string='Apoderados destinatarios',
       compute='_compute_apoderados'
   )
   alumno_ids = fields.Many2many(
       'gestion_educativa.alumno',
       string='Alumnos destinatarios',
       compute='_compute_alumnos'
   )

   def upload_image_to_cloudinary(self, image_data):
        """
        Upload an image to Cloudinary and return the secure URL
        Args:
            image_data: Base64 encoded image data
        Returns:
            str: Secure URL of the uploaded image, or None if upload fails
        """
        if not image_data:
            _logger.warning("No image data provided for upload")
            return None
            
        try:
            # Si la imagen ya está en base64, procesar el string
            if isinstance(image_data, str):
                # Remover prefijo base64 si existe
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                encoded_image = image_data
            else:
                # Si son datos binarios, encodear a base64
                encoded_image = base64.b64encode(image_data).decode('utf-8')

            if not encoded_image:
                _logger.error("Failed to encode image data")
                return None

            url = 'https://api.cloudinary.com/v1_1/da9xsfose/image/upload'
            payload = {
                'file': f'data:image/jpeg;base64,{encoded_image}',
                'upload_preset': 'fqw7ooma',
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            _logger.info("Attempting to upload image to Cloudinary")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if 'secure_url' in result:
                    _logger.info(f"Successfully uploaded image to Cloudinary: {result['secure_url']}")
                    return result['secure_url']
                else:
                    _logger.error(f"No secure_url in Cloudinary response: {result}")
                    return None
            else:
                _logger.error(f"Cloudinary upload failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            _logger.error(f"Error uploading to Cloudinary: {str(e)}")
            return None

   def _send_notifications(self, is_update=False):
       """
       Envía notificaciones a todos los destinatarios del comunicado
       """
       notification_tokens = []
       
       # Recolectar tokens de profesores
       if self.profesor_ids:
           profesor_tokens = self.profesor_ids.mapped('token_notifi')
           notification_tokens.extend(token for token in profesor_tokens if token)
           
       # Recolectar tokens de apoderados
       if self.apoderado_ids:
           apoderado_tokens = self.apoderado_ids.mapped('token_notifi')
           notification_tokens.extend(token for token in apoderado_tokens if token)
           
       # Recolectar tokens de alumnos
       if self.alumno_ids:
           alumno_tokens = self.alumno_ids.mapped('token_notifi')
           notification_tokens.extend(token for token in alumno_tokens if token)

       if not notification_tokens:
           return False

       # Obtener el título formateado
       titulo_display = dict(self._fields['titulo'].selection).get(self.titulo, self.titulo)
       
       # Preparar el mensaje según si es creación o actualización
    #    action_text = "actualizado" if is_update else "creado"
    #    notification_body = f"Se ha {action_text} un comunicado: {self.motivo}"

       notification_data = {
           "tokens": list(set(notification_tokens)),  
           "title": titulo_display,
           "body": self.motivo
       }

       try:
           response = requests.post(
               "https://notificationodoo-651539c5d67d.herokuapp.com/api/send-multiple-notifications",
               json=notification_data
           )
           return response.status_code == 200
       except Exception as e:
           return False

   @api.depends('profesor_rel_ids')
   def _compute_profesores(self):
       for record in self:
           record.profesor_ids = record.profesor_rel_ids.mapped('profesor_id')

   @api.depends('apoderado_rel_ids')
   def _compute_apoderados(self):
       for record in self:
           record.apoderado_ids = record.apoderado_rel_ids.mapped('apoderado_id')

   @api.depends('alumno_rel_ids')
   def _compute_alumnos(self):
       for record in self:
           record.alumno_ids = record.alumno_rel_ids.mapped('alumno_id')

   def asignar_destinatarios(self, tipo, ids):
       """
       Asigna destinatarios al comunicado
       tipo: 'alumno', 'profesor' o 'apoderado'
       ids: lista de IDs de destinatarios
       """
       model_map = {
           'alumno': 'gestion_educativa.comunicado.alumno',
           'profesor': 'gestion_educativa.comunicado.profesor',
           'apoderado': 'gestion_educativa.comunicado.apoderado'
       }
       
       if tipo not in model_map:
           return

       for dest_id in ids:
           self.env[model_map[tipo]].create({
               'comunicado_id': self.id,
               f'{tipo}_id': dest_id,
           })

   # Override create para manejar los destinatarios al guardar
   @api.model_create_multi
   def create(self, vals_list):
        for vals in vals_list:
            if vals.get('imagen'):
                try:
                    _logger.info("Processing image upload for new comunicado")
                    image_url = self.upload_image_to_cloudinary(vals['imagen'])
                    if image_url:
                        vals['imagen_url'] = image_url
                        vals['imagen_filename'] = f"comunicado_imagen_{fields.Datetime.now()}.png"
                        _logger.info(f"Image URL set to: {image_url}")
                    else:
                        _logger.warning("Failed to get image URL from Cloudinary")
                except Exception as e:
                    _logger.error(f"Error processing image upload: {str(e)}")


            if vals.get('todos_profesores'):
                profesores = self.env['gestion_educativa.profesor'].search([])
                profesor_lines = [(0, 0, {
                    'profesor_id': profesor.id,
                    'visto': False
                }) for profesor in profesores]
                vals['profesor_rel_ids'] = profesor_lines

            if vals.get('todos_apoderados'):
                apoderados = self.env['gestion_educativa.apoderado'].search([])
                apoderado_lines = [(0, 0, {
                    'apoderado_id': apoderado.id,
                    'visto': False
                }) for apoderado in apoderados]
                vals['apoderado_rel_ids'] = apoderado_lines

            if vals.get('todos_alumnos'):
                alumnos = self.env['gestion_educativa.alumno'].search([])
                alumno_lines = [(0, 0, {
                    'alumno_id': alumno.id,
                    'visto': False
                }) for alumno in alumnos]
                vals['alumno_rel_ids'] = alumno_lines

            if vals.get('imagen'):
                    # Subir la imagen a Cloudinary
                    image_url = self.upload_image_to_cloudinary(vals['imagen'])
                    vals['imagen_url'] = image_url
                    vals['imagen_filename'] = 'comunicado_imagen_%s.png' % fields.Datetime.now()

        records = super().create(vals_list)
        for record in records:
            record._send_notifications(is_update=False)
        return records

    # Override write para manejar los cambios en los destinatarios
   def write(self, vals):
        if 'todos_profesores' in vals and vals['todos_profesores']:
            profesores = self.env['gestion_educativa.profesor'].search([])
            profesor_lines = [(0, 0, {
                'profesor_id': profesor.id,
                'visto': False
            }) for profesor in profesores]
            vals['profesor_rel_ids'] = profesor_lines

        if 'todos_apoderados' in vals and vals['todos_apoderados']:
            apoderados = self.env['gestion_educativa.apoderado'].search([])
            apoderado_lines = [(0, 0, {
                'apoderado_id': apoderado.id,
                'visto': False
            }) for apoderado in apoderados]
            vals['apoderado_rel_ids'] = apoderado_lines

        if 'todos_alumnos' in vals and vals['todos_alumnos']:
            alumnos = self.env['gestion_educativa.alumno'].search([])
            alumno_lines = [(0, 0, {
                'alumno_id': alumno.id,
                'visto': False
            }) for alumno in alumnos]
            vals['alumno_rel_ids'] = alumno_lines

        if vals.get('imagen'):
            try:
                _logger.info("Processing image upload for existing comunicado")
                image_url = self.upload_image_to_cloudinary(vals['imagen'])
                if image_url:
                    vals['imagen_url'] = image_url
                    vals['imagen_filename'] = f"comunicado_imagen_{fields.Datetime.now()}.png"
                    _logger.info(f"Image URL set to: {image_url}")
                else:
                    _logger.warning("Failed to get image URL from Cloudinary")
            except Exception as e:
                _logger.error(f"Error processing image upload: {str(e)}")

        result = super().write(vals)
        self._send_notifications(is_update=True)
        return result

   @api.onchange('todos_profesores')
   def _onchange_todos_profesores(self):
        if not self.profesor_rel_ids:
            self.profesor_rel_ids = []
            
        if self.todos_profesores:
            # Buscar todos los profesores
            profesores = self.env['gestion_educativa.profesor'].search([])
            # Crear las líneas en memoria
            profesor_lines = []
            for profesor in profesores:
                profesor_lines.append((0, 0, {
                    'profesor_id': profesor.id,
                    'visto': False
                }))
            self.profesor_rel_ids = profesor_lines
        else:
            # Limpiar las líneas
            self.profesor_rel_ids = [(5, 0, 0)]

   @api.onchange('todos_apoderados')
   def _onchange_todos_apoderados(self):
        if not self.apoderado_rel_ids:
            self.apoderado_rel_ids = []
            
        if self.todos_apoderados:
            # Buscar todos los apoderados
            apoderados = self.env['gestion_educativa.apoderado'].search([])
            # Crear las líneas en memoria
            apoderado_lines = []
            for apoderado in apoderados:
                apoderado_lines.append((0, 0, {
                    'apoderado_id': apoderado.id,
                    'visto': False
                }))
            self.apoderado_rel_ids = apoderado_lines
        else:
            # Limpiar las líneas
            self.apoderado_rel_ids = [(5, 0, 0)]

   @api.onchange('todos_alumnos')
   def _onchange_todos_alumnos(self):
        if not self.alumno_rel_ids:
            self.alumno_rel_ids = []
            
        if self.todos_alumnos:
            # Buscar todos los alumnos
            alumnos = self.env['gestion_educativa.alumno'].search([])
            # Crear las líneas en memoria
            alumno_lines = []
            for alumno in alumnos:
                alumno_lines.append((0, 0, {
                    'alumno_id': alumno.id,
                    'visto': False
                }))
            self.alumno_rel_ids = alumno_lines
        else:
            # Limpiar las líneas
            self.alumno_rel_ids = [(5, 0, 0)]

class ComunicadoAlumno(models.Model):
    _name = 'gestion_educativa.comunicado.alumno'
    _description = 'Relación entre comunicados y alumnos'
    _rec_name = 'comunicado_id'

    comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
    alumno_id = fields.Many2one('gestion_educativa.alumno', required=True)
    visto = fields.Boolean(default=False)
    fecha_visto = fields.Datetime()

    _sql_constraints = [
        ('comunicado_alumno_unique', 
         'unique(comunicado_id, alumno_id)', 
         'Ya existe una relación para este alumno y comunicado')
    ]

    def marcar_como_visto(self):
        self.write({
            'visto': True,
            'fecha_visto': fields.Datetime.now()
        })

class ComunicadoProfesor(models.Model):
    _name = 'gestion_educativa.comunicado.profesor'
    _description = 'Relación entre comunicados y profesores'
    _rec_name = 'comunicado_id'

    comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
    profesor_id = fields.Many2one('gestion_educativa.profesor', required=True)
    visto = fields.Boolean(default=False)
    fecha_visto = fields.Datetime()

    _sql_constraints = [
        ('comunicado_profesor_unique', 
         'unique(comunicado_id, profesor_id)', 
         'Ya existe una relación para este profesor y comunicado')
    ]

    def marcar_como_visto(self):
        self.write({
            'visto': True,
            'fecha_visto': fields.Datetime.now()
        })

class ComunicadoApoderado(models.Model):
    _name = 'gestion_educativa.comunicado.apoderado'
    _description = 'Relación entre comunicados y apoderados'
    _rec_name = 'comunicado_id'

    comunicado_id = fields.Many2one('gestion_educativa.comunicado', required=True)
    apoderado_id = fields.Many2one('gestion_educativa.apoderado', required=True)
    visto = fields.Boolean(default=False)
    fecha_visto = fields.Datetime()

    _sql_constraints = [
        ('comunicado_apoderado_unique', 
         'unique(comunicado_id, apoderado_id)', 
         'Ya existe una relación para este apoderado y comunicado')
    ]

    def marcar_como_visto(self):
        self.write({
            'visto': True,
            'fecha_visto': fields.Datetime.now()
        })