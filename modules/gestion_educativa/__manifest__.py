# -*- coding: utf-8 -*-
{
    'name': "Gestión Educativa",
    'summary': "Módulo software 1",
    'description': """
Este módulo permite la gestión educativa de una institución escolar. Incluye funcionalidades para la creación y administración de usuarios, aulas, cursos, docentes, alumnos y padres de familia. Es una herramienta completa para gestionar todos los aspectos de una escuela o colegio.
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Education',  # Importante
    'version': '0.1',
    
    'depends': ['base', 'web','mail','portal'],  # Añadimos 'web' como dependencia
    
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/profesor_views.xml',
        'views/apoderado_views.xml',
        'views/alumno_views.xml',
        'views/materia_views.xml',
        'views/grado_views.xml',
        'views/horario_views.xml',
        'views/comunicado_views.xml',
        'views/menu_views.xml',
        # 'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,    # ¡Esto es crucial! Hace que aparezca en Apps
    'installable': True,    # También importante
    'auto_install': False,  # Opcional
    'sequence': 1,         # Opcional, determina el orden en la lista
}

