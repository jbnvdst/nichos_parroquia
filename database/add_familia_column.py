"""
Script de migración para agregar la columna 'familia' a la tabla ventas
"""

import sqlite3
import os

def agregar_columna_familia():
    """Agregar columna 'familia' a la tabla ventas"""

    # Ruta a la base de datos
    db_path = "criptas.db"

    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        print("Asegúrese de ejecutar este script desde el directorio raíz del proyecto")
        return False

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(ventas)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'familia' in columns:
            print("La columna 'familia' ya existe en la tabla ventas")
            conn.close()
            return True

        # Agregar la columna
        print("Agregando columna 'familia' a la tabla ventas...")
        cursor.execute("ALTER TABLE ventas ADD COLUMN familia VARCHAR(100)")

        # Confirmar cambios
        conn.commit()
        print("✓ Columna 'familia' agregada exitosamente")

        # Cerrar conexión
        conn.close()
        return True

    except Exception as e:
        print(f"Error al agregar columna: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Migración: Agregar columna 'familia' ===\n")

    if agregar_columna_familia():
        print("\n=== Migración completada exitosamente ===")
    else:
        print("\n=== Migración fallida ===")
