"""
Script de prueba para verificar la configuración de horarios de respaldos
"""

from backup.backup_manager import BackupManager
from backup.scheduler import BackupScheduler

def test_backup_schedule():
    print("=== Prueba de Configuración de Horarios de Respaldos ===\n")

    # Crear instancias
    backup_manager = BackupManager()
    backup_scheduler = BackupScheduler()

    # 1. Verificar configuración por defecto
    print("1. Configuración por defecto:")
    config = backup_manager.config
    print(f"   Día: {config.get('backup_day', 'No configurado')}")
    print(f"   Hora: {config.get('backup_time', 'No configurado')}")

    # 2. Obtener información del scheduler
    print("\n2. Información del scheduler:")
    schedule_info = backup_scheduler.get_schedule_info()
    print(f"   Día configurado: {schedule_info['day']}")
    print(f"   Hora configurada: {schedule_info['time']}")
    print(f"   Próximo respaldo: {schedule_info['next_run']}")
    print(f"   Scheduler activo: {schedule_info['is_running']}")

    # 3. Probar actualización de horario
    print("\n3. Probando actualización de horario a Lunes 14:30...")
    try:
        result = backup_scheduler.update_schedule('monday', '14:30')
        print(f"   Actualización exitosa: {result}")

        # Verificar que se guardó
        backup_manager_new = BackupManager()
        config_new = backup_manager_new.config
        print(f"   Nuevo día guardado: {config_new.get('backup_day')}")
        print(f"   Nueva hora guardada: {config_new.get('backup_time')}")

    except Exception as e:
        print(f"   Error: {e}")

    # 4. Obtener nueva información del scheduler
    print("\n4. Nueva información del scheduler:")
    schedule_info_new = backup_scheduler.get_schedule_info()
    print(f"   Día configurado: {schedule_info_new['day']}")
    print(f"   Hora configurada: {schedule_info_new['time']}")
    print(f"   Próximo respaldo: {schedule_info_new['next_run']}")

    # 5. Probar diferentes días
    print("\n5. Probando diferentes días de la semana:")
    test_days = ['tuesday', 'wednesday', 'friday', 'sunday']

    for day in test_days:
        try:
            backup_scheduler.update_schedule(day, '10:00')
            info = backup_scheduler.get_schedule_info()
            print(f"   {day.capitalize()}: ✓ (Próximo: {info['next_run']})")
        except Exception as e:
            print(f"   {day.capitalize()}: ✗ ({e})")

    # 6. Restaurar configuración original
    print("\n6. Restaurando configuración original (Sábado 12:00)...")
    backup_scheduler.update_schedule('saturday', '12:00')
    final_info = backup_scheduler.get_schedule_info()
    print(f"   Día: {final_info['day']}")
    print(f"   Hora: {final_info['time']}")

    # 7. Detener el scheduler
    print("\n7. Deteniendo scheduler...")
    backup_scheduler.stop_scheduler()
    print(f"   Scheduler detenido: {not backup_scheduler.is_running()}")

    print("\n=== Prueba completada ===")

if __name__ == "__main__":
    test_backup_schedule()
