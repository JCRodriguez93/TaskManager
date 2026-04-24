# esto lo que hace es cambiar las contraseñas a bcrypt, 
# para que la API funcione correctamente.

import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Usuario, Proyecto, Tarea, Etiqueta
from app.security import hashear_password

def recrear_base_de_datos_bcrypt():
    """
    Script para poblar la base de datos de la API recreando las tablas y 
    asegurando que las contraseñas se almacenen correctamente con el hash bcrypt.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Usuarios ────────────────────────────────────────────────────────
        admin = Usuario(
            nombre='Admin TaskManager',
            email='admin@taskmanager.com',
            rol='admin',
            password=hashear_password('admin1234')
        )

        ana = Usuario(
            nombre='Ana García', 
            email='ana@taskmanager.com',
            password=hashear_password('password123')
        )

        pablo = Usuario(
            nombre='Pablo López', 
            email='pablo@taskmanager.com',
            password=hashear_password('password123')
        )

        db.add_all([admin, ana, pablo])
        db.flush() # Sincronizar para obtener los IDs

        # ── Etiquetas ────────────────────────────────────────────────────────
        e_frontend = Etiqueta(nombre='frontend', color='#3498db')
        e_backend = Etiqueta(nombre='backend', color='#e74c3c')
        e_bug = Etiqueta(nombre='bug', color='#e67e22')
        e_mejora = Etiqueta(nombre='mejora', color='#2ecc71')
        e_docs = Etiqueta(nombre='documentación', color='#9b59b6')

        db.add_all([e_frontend, e_backend, e_bug, e_mejora, e_docs])
        db.flush()

        # ── Proyectos ────────────────────────────────────────────────────────
        p1 = Proyecto(
            titulo='Rediseño web corporativa',
            descripcion='Modernizar la web con nuevo diseño y mejor rendimiento.',
            estado='activo',
            fecha_limite=date.today() + timedelta(days=45),
            propietario_id=ana.id
        )

        p2 = Proyecto(
            titulo='App móvil iOS/Android',
            descripcion='Nueva aplicación móvil nativa para los clientes.',
            estado='activo',
            fecha_limite=date.today() + timedelta(days=90),
            propietario_id=pablo.id
        )

        p3 = Proyecto(
            titulo='Migración de base de datos',
            descripcion='Migrar de MySQL a PostgreSQL sin downtime.',
            estado='pausado',
            propietario_id=admin.id
        )

        db.add_all([p1, p2, p3])
        db.flush()

        # ── Tareas ───────────────────────────────────────────────────────────
        tareas_p1 = [
            Tarea(
                titulo='Diseñar wireframes de la home',
                prioridad='alta',
                estado='completada',
                proyecto_id=p1.id,
                asignado_id=ana.id
            ),
            Tarea(
                titulo='Implementar nuevo header responsive',
                prioridad='alta',
                estado='en_progreso',
                proyecto_id=p1.id,
                asignado_id=pablo.id,
                fecha_limite=date.today() + timedelta(days=7)
            ),
            Tarea(
                titulo='Implementar autenticación con JWT',
                prioridad='alta',
                estado='pendiente',
                proyecto_id=p2.id
            ),
        ]

        db.add_all(tareas_p1)
        db.flush()

        db.commit()
        print('✓ Base de datos poblada correctamente.')
        print('✓ Las contraseñas han sido hasheadas con bcrypt para la API.')
        
    except Exception as e:
        db.rollback()
        print(f'✗ Error durante la ejecución del script: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    recrear_base_de_datos_bcrypt()
