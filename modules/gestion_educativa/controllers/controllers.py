from odoo import http
import requests
from datetime import datetime
import json
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class ProfesorController(http.Controller):

    # READ : PROFESOR

   # LOGIC : POST PARA QUE EL PROFESOR PUEDA ENTRAR A SU CUENTA
    # {
    #   "ci": "1234567",
    #   "numero_matricula": "ABC123",
    #   "token_notifi": "token123abc..."
    # }
    def _procesar_horarios(self, profesor):
        """Procesa y retorna los horarios del profesor"""
        horarios = []
        for horario in profesor.horario_ids:
            horarios.append({
                'id': horario.id,
                'dia': horario.dia,
                'hora_inicio': horario.hora_inicio,
                'hora_fin': horario.hora_fin,
                'materia': {
                    'id': horario.materia_id.id,
                    'nombre': horario.materia_id.nombre,
                    'sigla': horario.materia_id.sigla
                },
                'grado': {
                    'id': horario.grado_id.id,
                    'nombre': horario.grado_id.nombre,
                    'sigla': horario.grado_id.sigla,
                    'alumnos': [{
                        'id': alumno.id,
                        'nombre_completo': alumno.nombre_completo,
                        'numero_matricula': alumno.numero_matricula
                    } for alumno in horario.grado_id.alumno_ids]
                }
            })
        return horarios

    def _procesar_comunicados_creados(self, profesor):
        """Procesa y retorna los comunicados creados por el profesor"""
        comunicados_creados = []
        for comunicado in profesor.comunicado_creado_ids:
            try:
                _logger.info(f"Procesando comunicado ID: {comunicado.id}")
                _logger.info(f"imagen_url value: {comunicado.imagen_url}")
                
                if comunicado.imagen:
                    _logger.info("Comunicado tiene imagen en la base de datos")
                
                comunicado_dict = {
                    'id': comunicado.id,
                    'titulo': comunicado.titulo,
                    'donde': comunicado.donde,
                    'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                    'motivo': comunicado.motivo,
                    'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                    'todos_profesores': comunicado.todos_profesores,
                    'todos_apoderados': comunicado.todos_apoderados,
                    'todos_alumnos': comunicado.todos_alumnos,
                    'cantidad_destinatarios': {
                        'profesores': len(comunicado.profesor_rel_ids),
                        'apoderados': len(comunicado.apoderado_rel_ids),
                        'alumnos': len(comunicado.alumno_rel_ids)
                    }
                }
                comunicados_creados.append(comunicado_dict)
            except Exception as e:
                _logger.error(f"Error procesando comunicado {comunicado.id}: {str(e)}")
        return comunicados_creados

    def _procesar_comunicados_recibidos(self, profesor):
        """Procesa y retorna los comunicados recibidos por el profesor"""
        comunicados_recibidos = []
        for rel in profesor.comunicado_rel_ids:
            try:
                _logger.info(f"Procesando comunicado recibido ID: {rel.comunicado_id.id}")
                _logger.info(f"imagen_url value: {rel.comunicado_id.imagen_url}")

                motivo_completo = rel.comunicado_id.motivo
                if not rel.comunicado_id.profesor_creador_id:
                    motivo_completo = f"Dir. Escolar, {motivo_completo}"

                comunicado_dict = {
                    'id': rel.comunicado_id.id,
                    'titulo': rel.comunicado_id.titulo,
                    'donde': rel.comunicado_id.donde,
                    'cuando': rel.comunicado_id.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                    'motivo': motivo_completo,
                    'visto': rel.visto,
                    'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                    'imagen_url': rel.comunicado_id.imagen_url if rel.comunicado_id.imagen_url else None,
                    'profesor_creador': {
                        'id': rel.comunicado_id.profesor_creador_id.id,
                        'nombre_completo': rel.comunicado_id.profesor_creador_id.nombre_completo
                    } if rel.comunicado_id.profesor_creador_id else None
                }
                comunicados_recibidos.append(comunicado_dict)
            except Exception as e:
                _logger.error(f"Error procesando comunicado recibido {rel.comunicado_id.id}: {str(e)}")
        return comunicados_recibidos

    def _preparar_respuesta_profesor(self, profesor, token_notifi):
        """Prepara el diccionario de respuesta con toda la información del profesor"""
        return {
            'id': profesor.id,
            'nombre_completo': profesor.nombre_completo,
            'ci': profesor.ci,
            'direccion': profesor.direccion,
            'numero_matricula': profesor.numero_matricula,
            'telefono': profesor.telefono,
            'email': profesor.email,
            'token_notifi': token_notifi,
            'horarios': self._procesar_horarios(profesor),
            'comunicados': {
                'creados': self._procesar_comunicados_creados(profesor),
                'recibidos': self._procesar_comunicados_recibidos(profesor)
            }
        }

    @http.route('/api/profesor', auth='public', method=['POST'], csrf=False)
    def get_profesor_by_ci_matricula(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            ci = data.get('ci')
            numero_matricula = data.get('numero_matricula')
            token_notifi = data.get('token_notifi')

            _logger.info(f"Buscando profesor con CI: {ci} y matrícula: {numero_matricula}")

            profesor = request.env['gestion_educativa.profesor'].sudo().search([
                ('ci', '=', ci),
                ('numero_matricula', '=', numero_matricula)
            ], limit=1)

            if not profesor:
                _logger.warning(f"Profesor no encontrado con CI: {ci}")
                return request.make_response(
                    json.dumps({'error': 'Profesor no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Actualizar token
            profesor.sudo().write({'token_notifi': token_notifi})

            # Preparar respuesta
            resultado = self._preparar_respuesta_profesor(profesor, token_notifi)
            _logger.info("Resultado procesado exitosamente")

            return request.make_response(
                json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error en get_profesor_by_ci_matricula: {str(e)}")
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        
    # LOGIC: POST PARA TRAER MENSAJES RECIBIDOS Y ENVIADOS POR EL PROFESOR
    # {
    #   "profesor_id": 1
    # }
    @http.route('/api/profesor/comunicados', auth='public', method=['POST'], csrf=False)
    def obtener_comunicados_profesor(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            profesor_id = data.get('profesor_id')

            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)

            if profesor:
                # Obtener comunicados creados por el profesor
                comunicados_creados = []
                for comunicado in profesor.comunicado_creado_ids:
                    comunicados_creados.append({
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': comunicado.motivo,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,  
                        'todos_profesores': comunicado.todos_profesores,
                        'todos_apoderados': comunicado.todos_apoderados,
                        'todos_alumnos': comunicado.todos_alumnos,
                        'cantidad_destinatarios': {
                            'profesores': len(comunicado.profesor_rel_ids),
                            'apoderados': len(comunicado.apoderado_rel_ids),
                            'alumnos': len(comunicado.alumno_rel_ids)
                        }
                    })

                # Obtener comunicados recibidos por el profesor
                comunicados_recibidos = []
                for rel in profesor.comunicado_rel_ids:
                    comunicado = rel.comunicado_id
                    comunicados_recibidos.append({
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': comunicado.motivo,
                        'visto': rel.visto,
                        'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                        'profesor_creador': {
                            'id': comunicado.profesor_creador_id.id,
                            'nombre_completo': comunicado.profesor_creador_id.nombre_completo
                        } if comunicado.profesor_creador_id else None
                    })

                resultado = {
                    'comunicados_creados': comunicados_creados,
                    'comunicados_recibidos': comunicados_recibidos
                }

                return request.make_response(
                    json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Profesor no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # LOGIC : POST PARA QUE EL PROFESOR PUEDA EMITIR UN COMUNICADO A UN CURSO ESPECÍFICO MEDIANTE SU HORARIO
    # {
    # "profesor_id": 1,
    # "horario_id": 1,
    # "titulo": "Comunicado importante",
    # "donde": "Aula 101",
    # "cuando": "2023-06-15T10:00:00",
    # "motivo": "Reunión de padres de familia"
    # }

    def _get_selection_value(self, field_name, key, model_name='gestion_educativa.comunicado'):
        """Obtiene el valor de visualización de un campo selection"""
        field = request.env[model_name]._fields[field_name]
        selection = dict(field.selection)
        return selection.get(key, key)

    def _send_notifications(self, tokens, title, body):
        """Envía notificaciones a través del servidor de notificaciones"""
        if not tokens:
            return False
            
        notification_data = {
            "tokens": list(set(tokens)),  # Eliminamos duplicados
            "title": title,
            "body": body
        }
        
        try:
            response = requests.post(
                "https://notificationodoo-651539c5d67d.herokuapp.com/api/send-multiple-notifications",
                json=notification_data
            )
            return response.status_code == 200
        except Exception as e:
            return False

    def parse_datetime(fecha_str):
        formatos = [
            '%Y-%m-%dT%H:%M:%S.%f',  # Con milisegundos
            '%Y-%m-%dT%H:%M:%S',     # Sin milisegundos
            '%Y-%m-%d %H:%M:%S'      # Formato Odoo estándar
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
                
        raise ValueError(f'No se pudo parsear la fecha: {fecha_str}')

    @http.route('/api/profesor/comunicado', auth='public', method=['POST'], csrf=False)
    def crear_comunicado(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            profesor_id = data.get('profesor_id')
            horario_id = data.get('horario_id')
            titulo = data.get('titulo')
            donde = data.get('donde')
            cuando = data.get('cuando')
            motivo = data.get('motivo')

            if not all([profesor_id, horario_id, titulo, donde, cuando, motivo]):
                return request.make_response(
                    json.dumps({'error': 'Faltan campos requeridos'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)
            horario = request.env['gestion_educativa.horario'].sudo().browse(horario_id)

            if not profesor or not horario:
                return request.make_response(
                    json.dumps({'error': 'Profesor u horario no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            if horario.profesor_id.id != profesor.id:
                return request.make_response(
                    json.dumps({'error': 'El horario no pertenece al profesor'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=403
                )

            # Convertimos la fecha al formato de Odoo
            cuando_dt = datetime.strptime(cuando.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            cuando_formatted = cuando_dt.strftime('%Y-%m-%d %H:%M:%S')

            # Crear el comunicado
            comunicado = request.env['gestion_educativa.comunicado'].sudo().create({
                'titulo': titulo,
                'donde': donde,
                'cuando': cuando_formatted,
                'motivo': motivo,
                'profesor_creador_id': profesor.id
            })

            # Crear relaciones con alumnos y apoderados
            for alumno in horario.grado_id.alumno_ids:
                request.env['gestion_educativa.comunicado.alumno'].sudo().create({
                    'comunicado_id': comunicado.id,
                    'alumno_id': alumno.id,
                    'visto': False
                })

                # También crear relación con el apoderado del alumno
                request.env['gestion_educativa.comunicado.apoderado'].sudo().create({
                    'comunicado_id': comunicado.id,
                    'apoderado_id': alumno.apoderado_id.id,
                    'visto': False
                })

            # Recolectar tokens para notificaciones
            notification_tokens = []
            for alumno in horario.grado_id.alumno_ids:
                if alumno.token_notifi:
                    notification_tokens.append(alumno.token_notifi)
                if alumno.apoderado_id.token_notifi:
                    notification_tokens.append(alumno.apoderado_id.token_notifi)

            # Enviar notificaciones
            titulo_display = self._get_selection_value('titulo', titulo)
            notification_sent = self._send_notifications(
                tokens=notification_tokens,
                title=titulo_display,
                body=motivo
            )

            return request.make_response(
                json.dumps({
                    'message': 'Comunicado creado exitosamente',
                    'comunicado_id': comunicado.id,
                    'notifications_sent': notification_sent,
                    'recipients_count': len(set(notification_tokens))
                }).encode('utf-8'),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )


    # LOGIC : POST PARA QUE EL PROFESOR PUEDA VER LOS ALUMNOS QUE HAN VISTO UN COMUNICADO Y LA INFORMACION DEL COMUNICADO
    # {
    #   "comunicado_id": 1,
    #   "profesor_id": 1
    # }
    @http.route('/api/comunicado/detalle', auth='public', method=['POST'], csrf=False)
    def obtener_comunicado_con_alumnos_visto(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            comunicado_id = data.get('comunicado_id')
            profesor_id = data.get('profesor_id')

            if not comunicado_id or not profesor_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del comunicado y del profesor'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)
            comunicado = request.env['gestion_educativa.comunicado'].sudo().browse(comunicado_id)

            if not profesor or not comunicado:
                return request.make_response(
                    json.dumps({'error': 'Profesor o comunicado no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Verificar que el profesor sea el creador del comunicado
            if comunicado.profesor_creador_id.id != profesor.id:
                return request.make_response(
                    json.dumps({'error': 'No tiene permiso para ver este comunicado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=403
                )

            # Obtener alumnos que han visto el comunicado usando la tabla intermedia
            alumnos_visto = []
            for rel in comunicado.alumno_rel_ids.filtered(lambda r: r.visto):
                alumno = rel.alumno_id
                alumnos_visto.append({
                    'id': alumno.id,
                    'nombre_completo': alumno.nombre_completo,
                    'ci': alumno.ci,
                    'numero_matricula': alumno.numero_matricula,
                    'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None
                })

            # Obtener información de todos los destinatarios
            alumnos_total = []
            for rel in comunicado.alumno_rel_ids:
                alumno = rel.alumno_id
                alumnos_total.append({
                    'id': alumno.id,
                    'nombre_completo': alumno.nombre_completo,
                    'ci': alumno.ci,
                    'numero_matricula': alumno.numero_matricula,
                    'visto': rel.visto,
                    'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None
                })

            resultado = {
                'id': comunicado.id,
                'titulo': comunicado.titulo,
                'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                'donde': comunicado.donde,
                'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                'motivo': comunicado.motivo,
                'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                'todos_profesores': comunicado.todos_profesores,
                'todos_apoderados': comunicado.todos_apoderados,
                'todos_alumnos': comunicado.todos_alumnos,
                'estadisticas': {
                    'total_alumnos': len(comunicado.alumno_rel_ids),
                    'alumnos_visto': len(alumnos_visto),
                    'porcentaje_visto': (len(alumnos_visto) / len(comunicado.alumno_rel_ids) * 100) if comunicado.alumno_rel_ids else 0
                },
                'alumnos': {
                    'han_visto': alumnos_visto,
                    'todos': alumnos_total
                }
            }

            return request.make_response(
                json.dumps(resultado, ensure_ascii=False).encode('utf-8'), 
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # LOGIC : POST SI EL PROFESOR VE UN COMUNICADO QUE SE ACTUALIZE QUE LO A VISTO 
    # {
    # "comunicado_id": 1,
    # "profesor_id": 2
    # }
    @http.route('/api/profesor/comunicado/confirmar_visto', auth='public', method=['POST'], csrf=False)
    def confirmar_comunicado_visto_profesor(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            comunicado_id = data.get('comunicado_id')
            profesor_id = data.get('profesor_id')

            if not comunicado_id or not profesor_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del comunicado y del profesor'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)
            if not profesor:
                return request.make_response(
                    json.dumps({'error': 'Profesor no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Buscar la relación específica
            comunicado_rel = request.env['gestion_educativa.comunicado.profesor'].sudo().search([
                ('comunicado_id', '=', comunicado_id),
                ('profesor_id', '=', profesor_id)
            ], limit=1)

            if comunicado_rel:
                # Obtener el comunicado
                comunicado = comunicado_rel.comunicado_id

                # Actualizar visto si aún no está marcado
                if not comunicado_rel.visto:
                    comunicado_rel.write({
                        'visto': True,
                        'fecha_visto': datetime.now()
                    })

                # Preparar la respuesta con la información del comunicado
                response_data = {
                    'message': 'Comunicado marcado como visto' if not comunicado_rel.visto else 'El comunicado ya estaba marcado como visto',
                    'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'comunicado': {
                        'id': comunicado.id,
                        'titulo': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': comunicado.motivo,
                        'profesor_creador': {
                            'id': comunicado.profesor_creador_id.id,
                            'nombre': comunicado.profesor_creador_id.nombre_completo
                        } if comunicado.profesor_creador_id else None,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                        'estado_visto': {
                            'visto': comunicado_rel.visto,
                            'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else None
                        }
                    }
                }

                return request.make_response(
                    json.dumps(response_data).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'No se encontró la relación entre el profesor y el comunicado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # READ : ESTUDIANTE

    # LOGIC : POST PARA QUE EL ALUMNO PUEDA ENTRAR A SU CUENTA
    # {
    # "ci": "1234567",
    # "numero_matricula": "ABC123",
    # "token_notifi": "token123abc..."
    # }
    @http.route('/api/alumno', auth='public', method=['POST'], csrf=False)
    def get_alumno_by_ci_matricula(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            ci = data.get('ci')
            numero_matricula = data.get('numero_matricula')
            token_notifi = data.get('token_notifi')

            alumno = request.env['gestion_educativa.alumno'].sudo().search([
                ('ci', '=', ci),
                ('numero_matricula', '=', numero_matricula)
            ], limit=1)

            if alumno:
                # Actualizar el token del alumno
                alumno.sudo().write({
                    'token_notifi': token_notifi
                })

                # Preparar la información del grado
                grado_info = {
                    'id': alumno.grado_id.id,
                    'nombre': alumno.grado_id.nombre,
                    'sigla': alumno.grado_id.sigla
                }

                # Preparar la información del apoderado
                apoderado_info = {
                    'id': alumno.apoderado_id.id,
                    'nombre_completo': alumno.apoderado_id.nombre_completo,
                    'ci': alumno.apoderado_id.ci,
                    'telefono': alumno.apoderado_id.telefono,
                    'email': alumno.apoderado_id.email,
                    'ocupacion': alumno.apoderado_id.ocupacion
                }

                # Procesar comunicados recibidos
                comunicados = []
                for rel in alumno.comunicado_rel_ids:
                    comunicado = rel.comunicado_id
                    profesor_creador = comunicado.profesor_creador_id
                    
                    # Si hay un profesor creador, buscamos su horario para este grado
                    materia_nombre = None
                    prefix = "Dir. Escolar"  # Prefijo por defecto
                    
                    if profesor_creador:
                        horario = request.env['gestion_educativa.horario'].sudo().search([
                            ('profesor_id', '=', profesor_creador.id),
                            ('grado_id', '=', alumno.grado_id.id)
                        ], limit=1)
                        if horario:
                            materia_nombre = horario.materia_id.nombre
                            prefix = f"Prof. {materia_nombre}"

                    profesor_info = {
                        'id': profesor_creador.id,
                        'nombre_completo': profesor_creador.nombre_completo,
                        'materia': materia_nombre
                    } if profesor_creador else None

                    motivo_completo = f"{prefix}, {comunicado.motivo}"

                    prefix = "Dir. Escolar" if not profesor_creador else f"Prof. {materia_nombre}"
                    motivo_completo = f"{prefix}, {comunicado.motivo}"
                    comunicados.append({
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': motivo_completo,
                        'visto': rel.visto,
                        'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,  
                        'profesor_creador': profesor_info,
                        'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    })

                # Ordenar comunicados por fecha de creación (más recientes primero)
                comunicados.sort(key=lambda x: x['created_at'], reverse=True)

                resultado = {
                    'id': alumno.id,
                    'nombre_completo': alumno.nombre_completo,
                    'ci': alumno.ci,
                    'direccion': alumno.direccion,
                    'numero_matricula': alumno.numero_matricula,
                    'telefono': alumno.telefono,
                    'numero_kardex': alumno.numero_kardex,
                    'token_notifi': token_notifi,
                    'grado': grado_info,
                    'apoderado': apoderado_info,
                    'comunicados': comunicados
                }

                return request.make_response(
                    json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Alumno no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        
    # LOGIC : POST PARA QUE EL ALUMNO PUEDA VER LOS COMUNICADOS RECIBIDOS
    # {
    # "alumno_id": 1
    # }
    @http.route('/api/alumno/comunicados', auth='public', method=['POST'], csrf=False)
    def get_comunicados_alumno(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            alumno_id = data.get('alumno_id')

            if not alumno_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del alumno'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            alumno = request.env['gestion_educativa.alumno'].sudo().browse(alumno_id)

            if not alumno:
                return request.make_response(
                    json.dumps({'error': 'Alumno no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Procesar comunicados recibidos
            comunicados = []
            for rel in alumno.comunicado_rel_ids:
                comunicado = rel.comunicado_id
                profesor_creador = comunicado.profesor_creador_id
                
                # Si hay un profesor creador, buscamos su horario para este grado
                materia_nombre = None
                prefix = "Dir. Escolar"  # Prefijo por defecto
                
                if profesor_creador:
                    horario = request.env['gestion_educativa.horario'].sudo().search([
                        ('profesor_id', '=', profesor_creador.id),
                        ('grado_id', '=', alumno.grado_id.id)
                    ], limit=1)
                    if horario:
                        materia_nombre = horario.materia_id.nombre
                        prefix = f"Prof. {materia_nombre}"

                profesor_info = {
                    'id': profesor_creador.id,
                    'nombre_completo': profesor_creador.nombre_completo,
                    'materia': materia_nombre
                } if profesor_creador else None

                motivo_completo = f"{prefix}, {comunicado.motivo}"
                prefix = "Dir. Escolar" if not profesor_creador else f"Prof. {materia_nombre}"
                motivo_completo = f"{prefix}, {comunicado.motivo}"
                comunicados.append({
                    'id': comunicado.id,
                    'titulo': comunicado.titulo,
                    'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                    'donde': comunicado.donde,
                    'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                    'motivo': motivo_completo,
                    'visto': rel.visto,
                    'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                    'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None, 
                    'profesor_creador': profesor_info,
                    'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })

            # Ordenar comunicados por fecha de creación (más recientes primero)
            comunicados.sort(key=lambda x: x['created_at'], reverse=True)

            resultado = {
                'comunicados': comunicados,
                'estadisticas': {
                    'total_comunicados': len(comunicados),
                    'comunicados_no_vistos': len([c for c in comunicados if not c['visto']]),
                    'comunicados_vistos': len([c for c in comunicados if c['visto']])
                }
            }

            return request.make_response(
                json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # LOGIC : POST PARA QUE EL ALUMNO AL VER EL COMUNICADO POR PRIMARA VES, SER MARQUE COMO VISTO AUTOMÁTICAMENTE
    # {
    # "comunicado_id": 1,
    # "alumno_id": 2
    # }
    @http.route('/api/comunicado/confirmar_visto', auth='public', method=['POST'], csrf=False)
    def confirmar_comunicado_visto(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            comunicado_id = data.get('comunicado_id')
            alumno_id = data.get('alumno_id')

            if not comunicado_id or not alumno_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del comunicado y del alumno'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            alumno = request.env['gestion_educativa.alumno'].sudo().browse(alumno_id)
            
            if not alumno:
                return request.make_response(
                    json.dumps({'error': 'Alumno no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Buscar la relación específica
            comunicado_rel = request.env['gestion_educativa.comunicado.alumno'].sudo().search([
                ('comunicado_id', '=', comunicado_id),
                ('alumno_id', '=', alumno_id)
            ], limit=1)

            if comunicado_rel:
                comunicado = comunicado_rel.comunicado_id
                profesor_creador = comunicado.profesor_creador_id
                
                # Preparar información del profesor y materia
                materia_nombre = None
                prefix = "Dir. Escolar"
                
                if profesor_creador:
                    horario = request.env['gestion_educativa.horario'].sudo().search([
                        ('profesor_id', '=', profesor_creador.id),
                        ('grado_id', '=', alumno.grado_id.id)
                    ], limit=1)
                    if horario:
                        materia_nombre = horario.materia_id.nombre
                        prefix = f"Prof. {materia_nombre}"

                profesor_info = {
                    'id': profesor_creador.id,
                    'nombre_completo': profesor_creador.nombre_completo,
                    'materia': materia_nombre
                } if profesor_creador else None

                motivo_completo = f"{prefix}, {comunicado.motivo}"

                if not comunicado_rel.visto:
                    comunicado_rel.write({
                        'visto': True,
                        'fecha_visto': datetime.now()
                    })

                response_data = {
                    'message': 'Comunicado marcado como visto' if not comunicado_rel.visto else 'El comunicado ya estaba marcado como visto',
                    'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'comunicado': {
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': motivo_completo,
                        'visto': comunicado_rel.visto,
                        'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else None,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                        'profesor_creador': profesor_info,
                        'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

                return request.make_response(
                    json.dumps(response_data).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'No se encontró la relación entre el alumno y el comunicado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
                
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
            

    # READ :APODERADO

    # LOGIC : POST PARA QUE EL APODERADO PUEDA ENTRAR 
    # {
    # "ci": "1234567",
    # "numero_matricula": "ABC123",
    # "token_notifi": "token123abc..."
    # }
    @http.route('/api/apoderado', auth='public', method=['POST'], csrf=False)
    def get_apoderado_by_ci_matricula(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            ci = data.get('ci')
            numero_matricula = data.get('numero_matricula')
            token_notifi = data.get('token_notifi')

            apoderado = request.env['gestion_educativa.apoderado'].sudo().search([
                ('ci', '=', ci),
                ('numero_matricula', '=', numero_matricula)
            ], limit=1)

            if apoderado:
                # Actualizar el token del apoderado
                apoderado.sudo().write({
                    'token_notifi': token_notifi
                })

                # Procesar la información de los alumnos
                alumnos_info = []
                for alumno in apoderado.alumno_ids:
                    alumnos_info.append({
                        'id': alumno.id,
                        'nombre_completo': alumno.nombre_completo,
                        'ci': alumno.ci,
                        'numero_matricula': alumno.numero_matricula,
                        'grado': {
                            'id': alumno.grado_id.id,
                            'nombre': alumno.grado_id.nombre,
                            'sigla': alumno.grado_id.sigla
                        }
                    })

                # Obtener todos los comunicados tanto del apoderado como de sus alumnos
                comunicados = []
                comunicados_procesados = set()  # Para evitar duplicados

                # Procesar comunicados del apoderado
                for rel in apoderado.comunicado_rel_ids:
                    if rel.comunicado_id.id not in comunicados_procesados:
                        comunicado = rel.comunicado_id
                        profesor_creador = comunicado.profesor_creador_id
                        
                        # Determinar prefijo y materia
                        materia_nombre = None
                        prefix = "Dir. Escolar"
                        
                        if profesor_creador:
                            # Buscar el horario del profesor relacionado con el grado del alumno
                            for alumno in apoderado.alumno_ids:
                                horario = request.env['gestion_educativa.horario'].sudo().search([
                                    ('profesor_id', '=', profesor_creador.id),
                                    ('grado_id', '=', alumno.grado_id.id)
                                ], limit=1)
                                if horario:
                                    materia_nombre = horario.materia_id.nombre
                                    prefix = f"Prof. {materia_nombre}"
                                    break

                        profesor_info = {
                            'id': profesor_creador.id,
                            'nombre_completo': profesor_creador.nombre_completo,
                            'materia': materia_nombre
                        } if profesor_creador else None

                        motivo_completo = f"{prefix}, {comunicado.motivo}"

                        comunicados.append({
                            'id': comunicado.id,
                            'titulo': comunicado.titulo,
                            'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                            'donde': comunicado.donde,
                            'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                            'motivo': motivo_completo,
                            'visto': rel.visto,
                            'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                            'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                            'profesor_creador': profesor_info,
                            'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'destinatario': 'apoderado'
                        })
                        comunicados_procesados.add(comunicado.id)

                # Procesar comunicados de los alumnos
                for alumno in apoderado.alumno_ids:
                    for rel in alumno.comunicado_rel_ids:
                        if rel.comunicado_id.id not in comunicados_procesados:
                            comunicado = rel.comunicado_id
                            profesor_creador = comunicado.profesor_creador_id
                            
                            # Determinar prefijo y materia
                            materia_nombre = None
                            prefix = "Dir. Escolar"
                            
                            if profesor_creador:
                                horario = request.env['gestion_educativa.horario'].sudo().search([
                                    ('profesor_id', '=', profesor_creador.id),
                                    ('grado_id', '=', alumno.grado_id.id)
                                ], limit=1)
                                if horario:
                                    materia_nombre = horario.materia_id.nombre
                                    prefix = f"Prof. {materia_nombre}"

                            profesor_info = {
                                'id': profesor_creador.id,
                                'nombre_completo': profesor_creador.nombre_completo,
                                'materia': materia_nombre
                            } if profesor_creador else None

                            motivo_completo = f"{prefix}, {comunicado.motivo}"

                            comunicados.append({
                                'id': comunicado.id,
                                'titulo': comunicado.titulo,
                                'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                                'donde': comunicado.donde,
                                'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                                'motivo': motivo_completo,
                                'visto': rel.visto,
                                'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                                'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                                'profesor_creador': profesor_info,
                                'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'destinatario': 'alumno',
                                'alumno_info': {
                                    'id': alumno.id,
                                    'nombre_completo': alumno.nombre_completo
                                }
                            })
                            comunicados_procesados.add(comunicado.id)

                # Ordenar todos los comunicados por fecha de creación (más recientes primero)
                comunicados.sort(key=lambda x: x['created_at'], reverse=True)

                resultado = {
                    'id': apoderado.id,
                    'nombre_completo': apoderado.nombre_completo,
                    'ci': apoderado.ci,
                    'direccion': apoderado.direccion,
                    'numero_matricula': apoderado.numero_matricula,
                    'telefono': apoderado.telefono,
                    'email': apoderado.email,
                    'ocupacion': apoderado.ocupacion,
                    'token_notifi': token_notifi,
                    'alumnos': alumnos_info,
                    'comunicados': comunicados
                }

                return request.make_response(
                    json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Apoderado no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # LOGIC : POST PARA TRAER LOS COMUNICADOS DEL APODERADO Y SUS ALUMNOS
    # {
    # "apoderado_id": 1
    # }
    @http.route('/api/apoderado/comunicados', auth='public', method=['POST'], csrf=False)
    def get_comunicados_apoderado(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            apoderado_id = data.get('apoderado_id')

            if not apoderado_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del apoderado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            apoderado = request.env['gestion_educativa.apoderado'].sudo().browse(apoderado_id)
            if not apoderado:
                return request.make_response(
                    json.dumps({'error': 'Apoderado no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Lista única para todos los comunicados
            comunicados = []
            comunicados_procesados = set()  # Para evitar duplicados

            # Procesar comunicados del apoderado
            for rel in apoderado.comunicado_rel_ids:
                if rel.comunicado_id.id not in comunicados_procesados:
                    comunicado = rel.comunicado_id
                    profesor_creador = comunicado.profesor_creador_id
                    
                    materia_nombre = None
                    prefix = "Dir. Escolar"
                    
                    if profesor_creador:
                        for alumno in apoderado.alumno_ids:
                            horario = request.env['gestion_educativa.horario'].sudo().search([
                                ('profesor_id', '=', profesor_creador.id),
                                ('grado_id', '=', alumno.grado_id.id)
                            ], limit=1)
                            if horario:
                                materia_nombre = horario.materia_id.nombre
                                prefix = f"Prof. {materia_nombre}"
                                break

                    profesor_info = {
                        'id': profesor_creador.id,
                        'nombre_completo': profesor_creador.nombre_completo,
                        'materia': materia_nombre
                    } if profesor_creador else None

                    motivo_completo = f"{prefix}, {comunicado.motivo}"

                    comunicados.append({
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': motivo_completo,
                        'visto': rel.visto,
                        'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                        'profesor_creador': profesor_info,
                        'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'tipo_destinatario': 'apoderado'
                    })
                    comunicados_procesados.add(comunicado.id)

            # Procesar comunicados de los alumnos
            for alumno in apoderado.alumno_ids:
                for rel in alumno.comunicado_rel_ids:
                    if rel.comunicado_id.id not in comunicados_procesados:
                        comunicado = rel.comunicado_id
                        profesor_creador = comunicado.profesor_creador_id
                        
                        materia_nombre = None
                        prefix = "Dir. Escolar"
                        
                        if profesor_creador:
                            horario = request.env['gestion_educativa.horario'].sudo().search([
                                ('profesor_id', '=', profesor_creador.id),
                                ('grado_id', '=', alumno.grado_id.id)
                            ], limit=1)
                            if horario:
                                materia_nombre = horario.materia_id.nombre
                                prefix = f"Prof. {materia_nombre}"

                        profesor_info = {
                            'id': profesor_creador.id,
                            'nombre_completo': profesor_creador.nombre_completo,
                            'materia': materia_nombre
                        } if profesor_creador else None

                        motivo_completo = f"{prefix}, {comunicado.motivo}"

                        comunicados.append({
                            'id': comunicado.id,
                            'titulo': comunicado.titulo,
                            'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                            'donde': comunicado.donde,
                            'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                            'motivo': motivo_completo,
                            'visto': rel.visto,
                            'fecha_visto': rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if rel.fecha_visto else None,
                            'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                            'profesor_creador': profesor_info,
                            'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'tipo_destinatario': 'alumno',
                            'alumno': {
                                'id': alumno.id,
                                'nombre_completo': alumno.nombre_completo,
                                'grado': alumno.grado_id.nombre
                            }
                        })
                        comunicados_procesados.add(comunicado.id)

            # Ordenar todos los comunicados por fecha de creación (más recientes primero)
            comunicados.sort(key=lambda x: x['created_at'], reverse=True)

            # Estadísticas generales
            total_comunicados = len(comunicados)
            comunicados_no_vistos = len([c for c in comunicados if not c['visto']])
            comunicados_vistos = len([c for c in comunicados if c['visto']])

            resultado = {
                'comunicados': comunicados,
                'estadisticas': {
                    'total': total_comunicados,
                    'no_vistos': comunicados_no_vistos,
                    'vistos': comunicados_vistos
                }
            }

            return request.make_response(
                json.dumps(resultado, ensure_ascii=False).encode('utf-8'),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        
    # LOGIC : POST PARA MARCAR COMO VISTO UN COMUNICADO DEL APODERADO
    # {
    # "comunicado_id": 1,
    # "apoderado_id": 2
    # }
    @http.route('/api/apoderado/comunicado/confirmar_visto', auth='public', method=['POST'], csrf=False)
    def confirmar_comunicado_visto_apoderado(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            comunicado_id = data.get('comunicado_id')
            apoderado_id = data.get('apoderado_id')

            if not comunicado_id or not apoderado_id:
                return request.make_response(
                    json.dumps({'error': 'Se requiere el ID del comunicado y del apoderado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            apoderado = request.env['gestion_educativa.apoderado'].sudo().browse(apoderado_id)
            if not apoderado:
                return request.make_response(
                    json.dumps({'error': 'Apoderado no encontrado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # Buscar la relación específica
            comunicado_rel = request.env['gestion_educativa.comunicado.apoderado'].sudo().search([
                ('comunicado_id', '=', comunicado_id),
                ('apoderado_id', '=', apoderado_id)
            ], limit=1)

            if comunicado_rel:
                comunicado = comunicado_rel.comunicado_id
                profesor_creador = comunicado.profesor_creador_id
                
                # Determinar prefijo y materia
                materia_nombre = None
                prefix = "Dir. Escolar"
                
                if profesor_creador:
                    # Buscar el horario del profesor relacionado con el grado del alumno
                    for alumno in apoderado.alumno_ids:
                        horario = request.env['gestion_educativa.horario'].sudo().search([
                            ('profesor_id', '=', profesor_creador.id),
                            ('grado_id', '=', alumno.grado_id.id)
                        ], limit=1)
                        if horario:
                            materia_nombre = horario.materia_id.nombre
                            prefix = f"Prof. {materia_nombre}"
                            break

                profesor_info = {
                    'id': profesor_creador.id,
                    'nombre_completo': profesor_creador.nombre_completo,
                    'materia': materia_nombre
                } if profesor_creador else None

                motivo_completo = f"{prefix}, {comunicado.motivo}"

                if not comunicado_rel.visto:
                    comunicado_rel.write({
                        'visto': True,
                        'fecha_visto': datetime.now()
                    })

                response_data = {
                    'message': 'Comunicado marcado como visto' if not comunicado_rel.visto else 'El comunicado ya estaba marcado como visto',
                    'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'comunicado': {
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'titulo_display': dict(comunicado._fields['titulo'].selection).get(comunicado.titulo),
                        'donde': comunicado.donde,
                        'cuando': comunicado.cuando.strftime('%Y-%m-%d %H:%M:%S'),
                        'motivo': motivo_completo,
                        'imagen_url': comunicado.imagen_url if comunicado.imagen_url else None,
                        'profesor_creador': profesor_info,
                        'estado_visto': {
                            'visto': comunicado_rel.visto,
                            'fecha_visto': comunicado_rel.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if comunicado_rel.fecha_visto else None
                        },
                        'created_at': comunicado.create_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

                return request.make_response(
                    json.dumps(response_data).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'No se encontró la relación entre el apoderado y el comunicado'}).encode('utf-8'),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                headers=[('Content-Type', 'application/json')],
                status=500
            )