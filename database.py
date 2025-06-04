import sqlite3

def crear_tablas():
    conn = sqlite3.connect('redconocer.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('evaluacion', 'certificacion', 'administrativa')),
            estado TEXT CHECK(estado IN ('pendiente', 'en_proceso', 'completada')),
            fecha_limite DATE,
            responsable TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def guardar_actividad(datos):
    conn = sqlite3.connect('redconocer.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO actividades (titulo, tipo, estado, fecha_limite, responsable)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datos["titulo"],
        datos["tipo"],
        datos["estado"],
        datos["fecha"],
        datos["responsable"]
    ))
    conn.commit()
    conn.close()

def obtener_actividades(filtro_tipo="Todos", filtro_estado="Todos"):
    conn = sqlite3.connect('redconocer.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM actividades"
    condiciones = []
    params = []
    
    if filtro_tipo != "Todos":
        condiciones.append("tipo = ?")
        params.append(filtro_tipo)
    if filtro_estado != "Todos":
        condiciones.append("estado = ?")
        params.append(filtro_estado)
    
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    
    cursor.execute(query, params)
    actividades = cursor.fetchall()
    conn.close()
    return actividades

def actualizar_actividad(datos):
    conn = sqlite3.connect('redconocer.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE actividades 
        SET titulo=?, tipo=?, estado=?, fecha_limite=?, responsable=?
        WHERE id=?
    ''', (
        datos["titulo"],
        datos["tipo"],
        datos["estado"],
        datos["fecha"],
        datos["responsable"],
        datos["id"]
    ))
    conn.commit()
    conn.close()

def eliminar_actividad(id_actividad):
    conn = sqlite3.connect('redconocer.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM actividades WHERE id = ?", (id_actividad,))
    conn.commit()
    conn.close()