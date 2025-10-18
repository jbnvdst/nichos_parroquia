# backup/scheduler.py
"""
Programador automático de respaldos
"""

import threading
import time
import schedule
from datetime import datetime
from backup.backup_manager import BackupManager


class BackupScheduler:
    def __init__(self):
        self.backup_manager = BackupManager()
        self.scheduler_thread = None
        self.running = False
        self.stop_event = threading.Event()

        # Cargar configuración de horario desde BackupManager
        self.load_schedule_config()

    def load_schedule_config(self):
        """Cargar configuración de horario desde el archivo de configuración"""
        config = self.backup_manager.config
        self.backup_day = config.get('backup_day', 'saturday')
        self.backup_time = config.get('backup_time', '12:00')

    def start_scheduler(self, day=None, time_str=None):
        """
        Iniciar el programador de respaldos automáticos

        Args:
            day: Día de la semana (monday, tuesday, etc.) - opcional
            time_str: Hora en formato HH:MM - opcional
        """
        if self.running:
            self.stop_scheduler()

        # Usar parámetros proporcionados o valores de configuración
        if day:
            self.backup_day = day.lower()
        if time_str:
            self.backup_time = time_str

        # Configurar el horario de respaldo según el día especificado
        day_methods = {
            'Lunes': schedule.every().monday,
            'Martes': schedule.every().tuesday,
            'Miercoles': schedule.every().wednesday,
            'Jueves': schedule.every().thursday,
            'Viernes': schedule.every().friday,
            'Sabado': schedule.every().saturday,
            'Domingo': schedule.every().sunday
        }

        if self.backup_day in day_methods:
            day_methods[self.backup_day].at(self.backup_time).do(self.run_automatic_backup)
        else:
            # Por defecto usar sábado si el día no es válido
            schedule.every().friday.at(self.backup_time).do(self.run_automatic_backup)

        self.running = True
        self.stop_event.clear()

        # Ejecutar el scheduler en un hilo separado
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """Detener el programador de respaldos"""
        if not self.running:
            return

        self.running = False
        self.stop_event.set()

        # Limpiar trabajos programados
        schedule.clear()

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=0.5)


    def _run_scheduler(self):
        """Ejecutar el loop del scheduler en hilo separado"""
        while self.running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                print(f"Error en el scheduler: {e}")
                time.sleep(60)

    def run_automatic_backup(self):
        """Ejecutar respaldo automático"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_backup_sabado_{timestamp}"

            print(f"Iniciando respaldo automático: {backup_name}")

            # Ejecutar respaldo en un hilo separado para no bloquear el scheduler
            backup_thread = threading.Thread(
                target=self._create_backup_threaded,
                args=(backup_name,),
                daemon=True
            )
            backup_thread.start()

        except Exception as e:
            print(f"Error al ejecutar respaldo automático: {e}")

    def _create_backup_threaded(self, backup_name):
        """Crear respaldo en hilo separado"""
        try:
            backup_path = self.backup_manager.create_backup(backup_name)
            print(f"Respaldo automático completado exitosamente: {backup_path}")
        except Exception as e:
            print(f"Error al crear respaldo automático: {e}")

    def get_next_backup_time(self):
        """Obtener la hora del próximo respaldo programado"""
        jobs = schedule.get_jobs()
        if jobs:
            next_job = min(jobs, key=lambda job: job.next_run)
            return next_job.next_run
        return None

    def is_running(self):
        """Verificar si el scheduler está ejecutándose"""
        return self.running

    def force_backup_now(self):
        """Forzar un respaldo inmediato (manual)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"manual_backup_{timestamp}"

            backup_thread = threading.Thread(
                target=self._create_backup_threaded,
                args=(backup_name,),
                daemon=True
            )
            backup_thread.start()

            return True
        except Exception as e:
            print(f"Error al forzar respaldo: {e}")
            return False

    def update_schedule(self, day, time_str):
        """
        Actualizar el horario de respaldos automáticos

        Args:
            day: Día de la semana (monday, tuesday, etc.)
            time_str: Hora en formato HH:MM
        """
        # Actualizar configuración en BackupManager
        self.backup_manager.config['backup_day'] = day.lower()
        self.backup_manager.config['backup_time'] = time_str
        self.backup_manager.save_config()

        # Reiniciar el scheduler con el nuevo horario
        self.start_scheduler(day, time_str)

        return True

    def get_schedule_info(self):
        """
        Obtener información del horario actual de respaldos

        Returns:
            dict: Información del horario (día, hora, próxima ejecución)
        """
        return {
            'day': self.backup_day,
            'time': self.backup_time,
            'next_run': self.get_next_backup_time(),
            'is_running': self.is_running()
        }