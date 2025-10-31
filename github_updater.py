# github_updater.py
# Sistema de actualizaciones basado en GitHub Releases
# Permite descargar e instalar automáticamente nuevas versiones desde GitHub

import requests
import json
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
import threading

class GitHubUpdater:
    """
    Clase para gestionar actualizaciones desde GitHub Releases
    Verifica versiones, descarga e instala actualizaciones
    """

    def __init__(self, repo_owner="jbnvdst", repo_name="nichos_parroquia", current_version="1.0.0", github_token=None):
        """
        Inicializar el actualizador

        Args:
            repo_owner: Usuario u organización dueña del repositorio
            repo_name: Nombre del repositorio
            current_version: Versión actual de la aplicación
            github_token: Token de GitHub para repositorios privados (opcional)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.github_token = github_token
        self.latest_release = None
        self.headers = self._get_headers()

    def _get_headers(self):
        """
        Obtener headers para las requests a GitHub API
        Si hay token de autenticación, se incluye en el header Authorization

        Returns:
            dict: Headers con autenticación (si está disponible)
        """
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        return headers

    def get_latest_release(self):
        """
        Obtener información del último release desde GitHub
        Si no hay releases, intenta obtener el último tag

        Returns:
            dict: Información del release o None si hay error
        """
        try:
            url = f"{self.github_api_url}/releases/latest"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                self.latest_release = response.json()
                return self.latest_release
            elif response.status_code == 404:
                # No hay releases publicados, intentar obtener el último tag
                return self.get_latest_tag()
            else:
                print(f"Error al obtener releases: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"Error de conexión al verificar actualizaciones: {e}")
            return None

    def get_latest_tag(self):
        """
        Obtener información del último tag desde GitHub
        Se usa como alternativa cuando no hay releases publicados

        Returns:
            dict: Información del tag formateado como release, o None si hay error
        """
        try:
            url = f"{self.github_api_url}/tags"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                tags = response.json()
                if tags:
                    # Tomar el primer tag (más reciente)
                    latest_tag = tags[0]
                    # Formatear como release para compatibilidad
                    formatted_release = {
                        'tag_name': latest_tag.get('name', ''),
                        'name': f"Tag: {latest_tag.get('name', '')}",
                        'body': 'No hay información disponible (obtida desde tags)',
                        'html_url': f"https://github.com/{self.repo_owner}/{self.repo_name}/releases/tag/{latest_tag.get('name', '')}",
                        'published_at': None,
                        'assets': []
                    }
                    self.latest_release = formatted_release
                    return formatted_release
            return None

        except requests.RequestException as e:
            return None

    def compare_versions(self, version1, version2):
        """
        Comparar dos versiones en formato semántico (ej: 1.2.3)

        Args:
            version1: Primera versión (string)
            version2: Segunda versión (string)

        Returns:
            int: 1 si version1 > version2, -1 si version1 < version2, 0 si son iguales
        """
        # Remover 'v' si existe al inicio
        v1 = version1.lstrip('v').split('.')
        v2 = version2.lstrip('v').split('.')

        # Convertir a enteros y comparar
        for i in range(max(len(v1), len(v2))):
            num1 = int(v1[i]) if i < len(v1) else 0
            num2 = int(v2[i]) if i < len(v2) else 0

            if num1 > num2:
                return 1
            elif num1 < num2:
                return -1

        return 0

    def check_for_updates(self, silent=False):
        """
        Verificar si hay actualizaciones disponibles

        Args:
            silent: Si es True, no muestra mensajes de error o confirmación

        Returns:
            tuple: (bool, dict) - (hay_actualizacion, info_release)
        """
        release = self.get_latest_release()

        if not release:
            if not silent:
                messagebox.showwarning(
                    "Actualizaciones",
                    "No se pudo verificar actualizaciones.\nVerifica tu conexión a internet."
                )
            return False, None

        latest_version = release.get('tag_name', '').lstrip('v')

        # Comparar versiones
        comparison = self.compare_versions(latest_version, self.current_version)

        if comparison > 0:
            # Hay una nueva versión disponible
            if not silent:
                self.show_update_dialog(release)
            return True, release
        else:
            if not silent:
                messagebox.showinfo(
                    "Actualizaciones",
                    f"Ya tienes la versión más reciente.\nVersión actual: {self.current_version}"
                )
            return False, None

    def show_update_dialog(self, release):
        """
        Mostrar diálogo con información de la actualización

        Args:
            release: Información del release desde GitHub
        """
        dialog = tk.Toplevel()
        dialog.title("Actualización Disponible")
        dialog.geometry("600x500")
        dialog.resizable(False, False)

        # Hacer modal
        dialog.transient()
        dialog.grab_set()

        # Frame principal con padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Información de la versión
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            version_frame,
            text="Nueva versión disponible",
            font=("Arial", 14, "bold")
        ).pack()

        version_info = ttk.Frame(version_frame)
        version_info.pack(pady=10)

        ttk.Label(
            version_info,
            text=f"Versión actual: {self.current_version}",
            font=("Arial", 10)
        ).pack()

        ttk.Label(
            version_info,
            text=f"Nueva versión: {release.get('tag_name', 'Desconocida')}",
            font=("Arial", 10, "bold"),
            foreground="green"
        ).pack()

        # Fecha de publicación
        published_date = release.get('published_at', '')
        if published_date:
            from datetime import datetime
            date_obj = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = date_obj.strftime("%d/%m/%Y")
            ttk.Label(
                version_info,
                text=f"Publicada el: {formatted_date}",
                font=("Arial", 9),
                foreground="gray"
            ).pack()

        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Notas de la versión
        ttk.Label(
            main_frame,
            text="Novedades:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))

        # Text widget para el changelog
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        changelog_text = tk.Text(
            text_frame,
            height=15,
            width=70,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9)
        )
        changelog_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=changelog_text.yview)

        # Insertar changelog
        changelog = release.get('body', 'No hay información disponible.')
        changelog_text.insert("1.0", changelog)
        changelog_text.config(state="disabled")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))

        # Estilo para botones
        style = ttk.Style()
        style.configure("Update.TButton", font=("Arial", 10, "bold"))

        download_btn = ttk.Button(
            button_frame,
            text="Descargar e Instalar",
            command=lambda: self.start_download(dialog, release),
            style="Update.TButton"
        )
        download_btn.pack(side="left", padx=5)

        view_release_btn = ttk.Button(
            button_frame,
            text="Ver en GitHub",
            command=lambda: self.open_release_page(release)
        )
        view_release_btn.pack(side="left", padx=5)

        later_btn = ttk.Button(
            button_frame,
            text="Más Tarde",
            command=dialog.destroy
        )
        later_btn.pack(side="left", padx=5)

        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def open_release_page(self, release):
        """Abrir página del release en el navegador"""
        import webbrowser
        url = release.get('html_url', f"https://github.com/{self.repo_owner}/{self.repo_name}/releases")
        webbrowser.open(url)

    def start_download(self, parent_dialog, release):
        """
        Iniciar descarga de la actualización en un hilo separado

        Args:
            parent_dialog: Ventana padre a cerrar
            release: Información del release
        """
        # Buscar el asset del instalador (archivo .exe)
        assets = release.get('assets', [])
        installer_asset = None

        for asset in assets:
            if asset.get('name', '').endswith('.exe'):
                installer_asset = asset
                break

        if not installer_asset:
            messagebox.showerror(
                "Error",
                "No se encontró el instalador en este release.\n"
                "Por favor, descárgalo manualmente desde GitHub."
            )
            self.open_release_page(release)
            return

        parent_dialog.destroy()

        # Crear ventana de progreso
        progress_window = tk.Toplevel()
        progress_window.title("Descargando Actualización")
        progress_window.geometry("500x150")
        progress_window.resizable(False, False)

        progress_frame = ttk.Frame(progress_window, padding="20")
        progress_frame.pack(fill="both", expand=True)

        ttk.Label(
            progress_frame,
            text="Descargando actualización...",
            font=("Arial", 12)
        ).pack(pady=(0, 10))

        progress_bar = ttk.Progressbar(
            progress_frame,
            length=450,
            mode='determinate'
        )
        progress_bar.pack(pady=10)

        status_label = ttk.Label(
            progress_frame,
            text="Preparando descarga...",
            font=("Arial", 9)
        )
        status_label.pack()

        # Centrar ventana
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (progress_window.winfo_width() // 2)
        y = (progress_window.winfo_screenheight() // 2) - (progress_window.winfo_height() // 2)
        progress_window.geometry(f"+{x}+{y}")

        # Descargar en hilo separado
        def download_thread():
            try:
                self.download_and_install(
                    installer_asset,
                    progress_bar,
                    status_label,
                    progress_window
                )
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"Error al descargar: {str(e)}")

        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def download_and_install(self, asset, progress_bar, status_label, progress_window):
        """
        Descargar e instalar la actualización

        Args:
            asset: Asset del release a descargar
            progress_bar: Barra de progreso para actualizar
            status_label: Label de estado para actualizar
            progress_window: Ventana de progreso
        """
        download_url = asset.get('browser_download_url')
        file_name = asset.get('name')
        file_size = asset.get('size', 0)

        # Crear directorio permanente en AppData para descargas de actualización
        # Esto evita conflictos con carpetas temporales inestables de PyInstaller
        updates_dir = os.path.join(
            os.path.expanduser("~"),
            "AppData",
            "Local",
            "SistemaCriptas",
            "Updates"
        )
        os.makedirs(updates_dir, exist_ok=True)
        download_path = os.path.join(updates_dir, file_name)

        try:
            # Descargar archivo
            status_label.config(text=f"Descargando {file_name}...")

            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            downloaded = 0
            chunk_size = 8192

            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Actualizar progreso
                        if file_size > 0:
                            progress = (downloaded / file_size) * 100
                            progress_bar['value'] = progress

                            # Mostrar MB descargados
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = file_size / (1024 * 1024)
                            status_label.config(
                                text=f"Descargado: {mb_downloaded:.1f} MB / {mb_total:.1f} MB"
                            )

                        progress_window.update()

            # Descarga completada - Validar integridad
            progress_bar['value'] = 100

            # Verificar que el archivo se descargó completamente
            actual_size = os.path.getsize(download_path)
            if file_size > 0 and actual_size != file_size:
                os.remove(download_path)
                raise Exception(
                    f"Descarga incompleta.\n"
                    f"Esperado: {file_size / (1024*1024):.1f} MB\n"
                    f"Obtenido: {actual_size / (1024*1024):.1f} MB\n\n"
                    f"Por favor, intenta de nuevo."
                )

            status_label.config(text="Descarga completada. Iniciando instalador...")
            progress_window.update()

            # Esperar un momento antes de cerrar
            progress_window.after(1000, progress_window.destroy)

            # Ejecutar instalador
            messagebox.showinfo(
                "Actualización",
                "La descarga se completó exitosamente.\n\n"
                "Se iniciará el instalador.\n"
                "Por favor, cierra esta aplicación antes de continuar con la instalación."
            )

            # Abrir instalador
            os.startfile(download_path)

        except Exception as e:
            progress_window.destroy()
            raise e

    def check_updates_on_startup(self, parent_window):
        """
        Verificar actualizaciones al iniciar la aplicación (silenciosamente)
        No muestra mensajes de error si no hay releases o hay problemas de conexión

        Args:
            parent_window: Ventana padre de la aplicación
        """
        def check_thread():
            try:
                has_update, release = self.check_for_updates(silent=True)
                if has_update and release:
                    # Mostrar notificación en la barra de estado o menú
                    parent_window.after(0, lambda: self.show_update_notification(parent_window, release))
            except Exception:
                # Silenciar todos los errores en verificación automática
                # Esto previene errores de consola si no hay releases o no hay conexión
                pass

        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()

    def show_update_notification(self, parent_window, release):
        """
        Mostrar notificación pequeña de actualización disponible

        Args:
            parent_window: Ventana padre
            release: Información del release
        """
        result = messagebox.askyesno(
            "Actualización Disponible",
            f"Hay una nueva versión disponible: {release.get('tag_name')}\n\n"
            "¿Deseas ver los detalles?",
            icon='info'
        )

        if result:
            self.show_update_dialog(release)


# Función para usar en el main.py
def check_for_updates_github(current_version="1.0.0", silent=False):
    """
    Función helper para verificar actualizaciones

    Args:
        current_version: Versión actual de la aplicación
        silent: Si es True, solo verifica sin mostrar diálogos

    Returns:
        tuple: (tiene_actualizacion, info_release)
    """
    updater = GitHubUpdater(current_version=current_version)
    return updater.check_for_updates(silent=silent)


if __name__ == "__main__":
    # Prueba del módulo
    print("Verificando actualizaciones desde GitHub...")
    updater = GitHubUpdater(current_version="1.0.0")
    has_update, release = updater.check_for_updates(silent=False)

    if has_update:
        print(f"Nueva versión disponible: {release.get('tag_name')}")
    else:
        print("No hay actualizaciones disponibles")
