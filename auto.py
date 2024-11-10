import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class MenuAutomatas:
    def __init__(self):
        # Configuración de la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Opciones de Derivadas de Gramáticas")
        self.ventana.geometry("400x300")
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear widgets
        self.crear_widgets()

    def configurar_estilo(self):
        # Configurar colores y estilos
        self.style = {
            'bg_color': '#f0f0f0',
            'button_bg': '#4a90e2',
            'button_fg': 'white',
            'button_active_bg': '#357abd',
            'title_fg': '#2c3e50'
        }
        
        self.ventana.configure(bg=self.style['bg_color'])

    def crear_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=self.style['bg_color'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Etiqueta de título
        titulo = tk.Label(
            main_frame,
            text="Selecciona una opción de derivada:",
            font=("Arial", 16, "bold"),
            fg=self.style['title_fg'],
            bg=self.style['bg_color']
        )
        titulo.pack(pady=20)

        # Botones de opciones
        botones = [
            ("Derivación ()", "arbol.py"),
            ("Derivación ABC", "abc.py"),
            ("Derivación STF", "stf.py")
        ]

        for texto, archivo in botones:
            self.crear_boton(main_frame, texto, archivo)

    def crear_boton(self, parent, texto, archivo):
        boton = tk.Button(
            parent,
            text=texto,
            command=lambda: self.ejecutar_automata(archivo),
            bg=self.style['button_bg'],
            fg=self.style['button_fg'],
            activebackground=self.style['button_active_bg'],
            font=("Arial", 12),
            width=25,
            height=2,
            relief=tk.RAISED,
            borderwidth=2
        )
        boton.pack(pady=10)
        
        # Efectos hover
        boton.bind('<Enter>', lambda e: boton.configure(bg=self.style['button_active_bg']))
        boton.bind('<Leave>', lambda e: boton.configure(bg=self.style['button_bg']))

    def ejecutar_automata(self, archivo):
        try:
            # Verificar si el archivo existe
            if not os.path.exists(archivo):
                messagebox.showerror("Error", f"No se encontró el archivo {archivo}")
                return

            # Ejecutar el archivo Python en un nuevo proceso
            if sys.platform.startswith('win'):
                subprocess.Popen(['python', archivo], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(['python3', archivo])

        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el autómata: {str(e)}")

    def ejecutar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    app = MenuAutomatas()
    app.ejecutar()