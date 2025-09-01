# update_checker.py
# Módulo para verificar actualizaciones remotas

import requests
import json
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class UpdateChecker:
    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.update_server_url = "https://your-server.com/api/updates"  # Cambiar por tu servidor
        self.download_url = None
        
    def check_for_updates(self, silent=True):
        """Verificar si hay actualizaciones disponibles"""
        try:
            response = requests.get(
                f"{self.update_server_url}/check",
                params={'current_version': self.current_version},
                timeout=10
            )
            
            if response.status_code == 200:
                update_info = response.json()
                
                if update_info.get('update_available', False):
                    new_version = update_info.get('latest_version')
                    self.download_url = update_info.get('download_url')
                    
                    if not silent:
                        self.show_update_dialog(new_version, update_info.get('changelog', ''))
                    
                    return True, new_version
                else:
                    if not silent:
                        messagebox.showinfo("Actualización", "Ya tienes la versión más reciente.")
                    return False, None
                    
        except requests.RequestException as e:
            if not silent:
                messagebox.showerror("Error", f"No se pudo verificar actualizaciones: {e}")
            return False, None
        
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Error inesperado: {e}")
            return False, None
    
    def show_update_dialog(self, new_version, changelog):
        """Mostrar diálogo de actualización"""
        dialog = tk.Toplevel()
        dialog.title("Actualización Disponible")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Hacer modal
        dialog.transient()
        dialog.grab_set()
        
        # Título
        title_label = tk.Label(dialog, text=f"Nueva versión disponible: {new_version}", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Changelog
        if changelog:
            changelog_label = tk.Label(dialog, text="Novedades:", font=("Arial", 12, "bold"))
            changelog_label.pack(anchor="w", padx=20)
            
            changelog_text = tk.Text(dialog, height=10, width=60, wrap=tk.WORD)
            changelog_text.pack(padx=20, pady=10, fill="both", expand=True)
            changelog_text.insert("1.0", changelog)
            changelog_text.config(state="disabled")
        
        # Botones
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        download_btn = tk.Button(button_frame, text="Descargar Actualización", 
                                command=lambda: self.download_update(dialog))
        download_btn.pack(side="left", padx=10)
        
        later_btn = tk.Button(button_frame, text="Más Tarde", 
                             command=dialog.destroy)
        later_btn.pack(side="left", padx=10)
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def download_update(self, dialog):
        """Descargar e instalar actualización"""
        if not self.download_url:
            messagebox.showerror("Error", "URL de descarga no disponible")
            return
        
        dialog.destroy()
        
        # Aquí implementarías la lógica de descarga
        # Por ejemplo, abrir el navegador web con la URL de descarga
        import webbrowser
        webbrowser.open(self.download_url)
        
        messagebox.showinfo("Actualización", 
                           "Se abrirá el navegador para descargar la actualización.\n"
                           "Cierra el programa antes de instalar la nueva versión.")