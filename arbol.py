import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import re
from typing import Optional, Tuple, Dict, List
import math

class Nodo:
    def __init__(self, tipo: str, valor: str, hijos: List['Nodo'] = None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.id = id(self)  # ID único para el nodo

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico Visual")
        self.root.geometry("1200x800")
        
        # Configurar el estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame superior para entrada y controles
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Entrada
        ttk.Label(top_frame, text="Ingrese expresión:").grid(row=0, column=0, padx=5)
        self.entrada = ttk.Entry(top_frame, width=40)
        self.entrada.grid(row=0, column=1, padx=5)
        self.entrada.insert(0, "(())")
        
        # Botón de análisis
        self.btn_analizar = ttk.Button(top_frame, text="Analizar", command=self.analizar)
        self.btn_analizar.grid(row=0, column=2, padx=5)
        
        # Frame para el log
        log_frame = ttk.LabelFrame(main_frame, text="Log de análisis", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Área de texto para el log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=100, width=50)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para el gráfico
        graph_frame = ttk.LabelFrame(main_frame, text="Árbol de análisis", padding="5")
        graph_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)

    def log(self, mensaje: str, nivel: int = 0):
        """Agrega un mensaje al log"""
        self.log_text.insert(tk.END, "  " * nivel + mensaje + "\n")
        self.log_text.see(tk.END)

    def es_valida(self, palabra: str) -> Tuple[bool, Optional[Nodo]]:
        """Analiza si la palabra es válida según la gramática"""
        self.log_text.delete(1.0, tk.END)
        
        if not palabra:
            self.log("❌ Palabra vacía")
            return False, None
        
        if len(palabra) % 2 != 0:
            self.log(f"❌ Longitud impar ({len(palabra)})")
            return False, None

        def es_par_parentesis(inicio: int, fin: int, nivel: int) -> Tuple[bool, Optional[Nodo]]:
            segmento = palabra[inicio:fin+1]
            self.log(f"Analizando segmento: {segmento}", nivel)
            
            # Caso base: paréntesis vacíos
            if inicio + 1 == fin and palabra[inicio] == '(' and palabra[fin] == ')':
                self.log("✓ Encontrado () válido", nivel)
                return True, Nodo("EMPTY", "()")
            
            if fin - inicio < 1 or palabra[inicio] != '(' or palabra[fin] != ')':
                self.log("❌ Paréntesis no válidos o segmento muy corto", nivel)
                return False, None

            # Caso (S)
            self.log("Probando caso (S)", nivel)
            valido_interno, arbol_interno = es_valida_recursiva(inicio + 1, fin - 1, nivel + 1)
            if valido_interno:
                self.log("✓ Caso (S) válido", nivel)
                return True, Nodo("PAREN", "(S)", [arbol_interno])

            # Caso SS
            self.log("Probando caso SS", nivel)
            for medio in range(inicio + 1, fin, 2):
                self.log(f"Intentando división en posición {medio}", nivel)
                valido_izq, arbol_izq = es_valida_recursiva(inicio, medio, nivel + 1)
                if valido_izq:
                    valido_der, arbol_der = es_valida_recursiva(medio + 1, fin, nivel + 1)
                    if valido_der:
                        self.log("✓ Caso SS válido", nivel)
                        return True, Nodo("CONCAT", "SS", [arbol_izq, arbol_der])
            
            self.log("❌ No se encontró una división válida", nivel)
            return False, None

        def es_valida_recursiva(inicio: int, fin: int, nivel: int) -> Tuple[bool, Optional[Nodo]]:
            if inicio > fin:
                self.log("❌ Índices inválidos", nivel)
                return False, None
            if inicio == fin:
                self.log("❌ Segmento de longitud 1", nivel)
                return False, None
            return es_par_parentesis(inicio, fin, nivel)

        return es_valida_recursiva(0, len(palabra) - 1, 0)

    def crear_grafo(self, nodo: Optional[Nodo]) -> nx.Graph:
        """Crea un grafo NetworkX a partir del árbol"""
        G = nx.Graph()
        
        def agregar_nodos(nodo: Nodo, padre_id: Optional[int] = None):
            if not nodo:
                return
                
            nodo_id = nodo.id
            G.add_node(nodo_id, label=nodo.valor)
            
            if padre_id is not None:
                G.add_edge(padre_id, nodo_id)
                
            for hijo in nodo.hijos:
                agregar_nodos(hijo, nodo_id)
        
        agregar_nodos(nodo)
        return G

    def visualizar_arbol(self, G: nx.Graph):
        """Visualiza el grafo usando NetworkX y Matplotlib"""
        self.ax.clear()
        
        # Calcular el layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Dibujar el grafo
        nx.draw(G, pos, ax=self.ax, 
                node_color='lightblue',
                node_size=2000,
                width=2,
                edge_color='gray',
                arrows=False)
        
        # Agregar etiquetas
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=12)
        
        # Ajustar la visualización
        self.ax.set_axis_off()
        self.canvas.draw()

    def analizar(self):
        """Maneja el evento de análisis"""
        palabra = self.entrada.get().strip()
        
        if not re.match(r'^[()]*$', palabra):
            self.log("Error: La palabra solo debe contener paréntesis")
            return
        
        valida, arbol = self.es_valida(palabra)
        
        if valida:
            self.log("\n✓ RESULTADO FINAL: La palabra pertenece a la gramática")
            G = self.crear_grafo(arbol)
            self.visualizar_arbol(G)
        else:
            self.log("\n❌ RESULTADO FINAL: La palabra NO pertenece a la gramática")
            self.ax.clear()
            self.ax.set_axis_off()
            self.canvas.draw()

def main():
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()