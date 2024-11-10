from odoo import http
from odoo.http import request
from datetime import datetime
import json

class ProfesorController(http.Controller):

    # READ : POST PARA QUE EL PROFESOR PUEDA ENTRAR A SU CUENTA
    # {
    #   "ci": "1234567",
    #   "numero_matricula": "ABC123",
    #   "token_notifi": "token123abc..."
    # }
    @http.route('/api/profesor', auth='public', method=['POST'], csrf=False)
    def get_profesor_by_ci_matricula(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            ci = data.get('ci')
            numero_matricula = data.get('numero_matricula')
            # Obtener el token del body
            token_notifi = data.get('token_notifi')  

            profesor = request.env['gestion_educativa.profesor'].sudo().search([
                ('ci', '=', ci),
                ('numero_matricula', '=', numero_matricula)
            ], limit=1)

            if profesor:
                # Actualizar el token del profesor con el recibido
                profesor.sudo().write({
                    'token_notifi': token_notifi
                })

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
                            'sigla': horario.grado_id.sigla
                        }
                    })

                resultado = {
                    'id': profesor.id,
                    'nombre_completo': profesor.nombre_completo,
                    'ci': profesor.ci,
                    'direccion': profesor.direccion,
                    'numero_matricula': profesor.numero_matricula,
                    'telefono': profesor.telefono,
                    'email': profesor.email,
                    'token_notifi': token_notifi,  
                    'horarios': horarios
                }
                return request.make_response(json.dumps(resultado).encode('utf-8'), 
                                        headers=[('Content-Type', 'application/json')])
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


    # READ : GET PARA QUE EL PROFESOR PUEDA VER LOS COMUNICADOS QUE HA EMITIDO
    @http.route('/api/profesor/<int:profesor_id>/comunicados', auth='public', method=['GET'], csrf=False)
    def obtener_comunicados_por_profesor(self, profesor_id, **kwargs):
        try:
            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)
            if profesor:
                # Usamos comunicado_creado_ids en lugar de comunicado_ids
                comunicados = profesor.comunicado_creado_ids
                resultado = []
                for comunicado in comunicados:
                    # Obtenemos la información de los destinatarios
                    profesores_destinatarios = [{'id': p.id, 'nombre': p.nombre_completo} for p in comunicado.profesor_ids]
                    apoderados_destinatarios = [{'id': a.id, 'nombre': a.nombre_completo} for a in comunicado.apoderado_ids]
                    alumnos_destinatarios = [{'id': a.id, 'nombre': a.nombre_completo} for a in comunicado.alumno_ids]
                    resultado.append({
                        'id': comunicado.id,
                        'titulo': comunicado.titulo,
                        'donde': comunicado.donde,
                        'cuando': str(comunicado.cuando),
                        'motivo': comunicado.motivo,
                        'visto': comunicado.visto,
                        'destinatarios': {
                            'todos_profesores': comunicado.todos_profesores,
                            'todos_apoderados': comunicado.todos_apoderados,
                            'todos_alumnos': comunicado.todos_alumnos,
                            'profesores': profesores_destinatarios,
                            'apoderados': apoderados_destinatarios,
                            'alumnos': alumnos_destinatarios
                        }
                    })
                return request.make_response(
                    json.dumps(resultado).encode('utf-8'),
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

    # READ : POST PARA QUE EL PROFESOR PUEDA EMITIR UN COMUNICADO A UN CURSO ESPECÍFICO MEDIANTE SU HORARIO
    # {
    # "profesor_id": 1,
    # "horario_id": 1,
    # "titulo": "Comunicado importante",
    # "donde": "Aula 101",
    # "cuando": "2023-06-15T10:00:00",
    # "motivo": "Reunión de padres de familia"
    # }
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

            profesor = request.env['gestion_educativa.profesor'].sudo().browse(profesor_id)
            horario = request.env['gestion_educativa.horario'].sudo().browse(horario_id)

            if profesor and horario:
                grado = horario.grado_id
                alumnos = grado.alumno_ids
                apoderados = request.env['gestion_educativa.apoderado'].sudo().search([
                    ('alumno_ids', 'in', alumnos.ids)
                ])

                # Convertir la fecha y hora al formato esperado por Odoo
                cuando_dt = datetime.strptime(cuando, '%Y-%m-%dT%H:%M:%S')
                cuando_formatted = cuando_dt.strftime('%Y-%m-%d %H:%M:%S')

                comunicado = request.env['gestion_educativa.comunicado'].sudo().create({
                    'titulo': titulo,
                    'donde': donde,
                    'cuando': cuando_formatted,
                    'motivo': motivo,
                    'profesor_creador_id': profesor.id,  # Agregamos el profesor creador
                    'alumno_ids': [(6, 0, alumnos.ids)],
                    'apoderado_ids': [(6, 0, apoderados.ids)]  # También notificamos a los apoderados
                })

                return request.make_response(
                    json.dumps({
                        'message': 'Comunicado creado exitosamente',
                        'comunicado_id': comunicado.id
                    }).encode('utf-8'), 
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return request.make_response(
                    json.dumps({'error': 'Profesor u horario no encontrado'}).encode('utf-8'), 
                    headers=[('Content-Type', 'application/json')], 
                    status=404
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}).encode('utf-8'), 
                headers=[('Content-Type', 'application/json')], 
                status=500
            )  
    

    # READ : POST PARA QUE EL ALUMNO AL VER EL COMUNICADO POR PRIMARA VES, SER MARQUE COMO VISTO AUTOMÁTICAMENTE
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

            comunicado = request.env['gestion_educativa.comunicado'].sudo().browse(comunicado_id)
            alumno = request.env['gestion_educativa.alumno'].sudo().browse(alumno_id)

            if comunicado and alumno:
                comunicado_alumno = alumno.comunicado_ids.filtered(lambda c: c.id == comunicado.id)
                if comunicado_alumno:
                    comunicado_alumno.write({'visto': True})
                    return request.make_response(json.dumps({'message': 'Comunicado marcado como visto'}).encode('utf-8'), headers=[('Content-Type', 'application/json')])
                else:
                    return request.make_response(json.dumps({'error': 'El alumno no está relacionado con el comunicado'}).encode('utf-8'), headers=[('Content-Type', 'application/json')], status=400)
            else:
                return request.make_response(json.dumps({'error': 'Comunicado o alumno no encontrado'}).encode('utf-8'), headers=[('Content-Type', 'application/json')], status=404)
        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}).encode('utf-8'), headers=[('Content-Type', 'application/json')], status=500)

    # READ : GET PARA QUE EL PROFESOR PUEDA VER LOS ALUMNOS QUE HAN VISTO UN COMUNICADO Y LA INFORMACION DEL COMUNICADO
    @http.route('/api/comunicado/<int:comunicado_id>', auth='public', method=['GET'], csrf=False)
    def obtener_comunicado_con_alumnos_visto(self, comunicado_id, **kwargs):
        try:
            comunicado = request.env['gestion_educativa.comunicado'].sudo().browse(comunicado_id)

            if comunicado:
                alumnos_visto = []
                for alumno in comunicado.alumno_ids:
                    if alumno.comunicado_ids.filtered(lambda c: c.id == comunicado.id and c.visto):
                        alumnos_visto.append({
                            'id': alumno.id,
                            'nombre_completo': alumno.nombre_completo,
                            'ci': alumno.ci,
                            'numero_matricula': alumno.numero_matricula
                        })

                resultado = {
                    'id': comunicado.id,
                    'titulo': comunicado.titulo,
                    'donde': comunicado.donde,
                    'cuando': str(comunicado.cuando),
                    'motivo': comunicado.motivo,
                    'alumnos_visto': alumnos_visto
                }

                return request.make_response(json.dumps(resultado).encode('utf-8'), headers=[('Content-Type', 'application/json')])
            else:
                return request.make_response(json.dumps({'error': 'Comunicado no encontrado'}).encode('utf-8'), headers=[('Content-Type', 'application/json')], status=404)
        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}).encode('utf-8'), headers=[('Content-Type', 'application/json')], status=500)