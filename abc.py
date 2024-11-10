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
        self.id = id(self)

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico Visual - SS|aSb|aSc|E")
        self.root.geometry("1200x800")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(top_frame, text="Ingrese cadena:").grid(row=0, column=0, padx=5)
        self.entrada = ttk.Entry(top_frame, width=40)
        self.entrada.grid(row=0, column=1, padx=5)
        self.entrada.insert(0, "ab")
        
        self.btn_analizar = ttk.Button(top_frame, text="Analizar", command=self.analizar)
        self.btn_analizar.grid(row=0, column=2, padx=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log de análisis", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=100, width=50)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        graph_frame = ttk.LabelFrame(main_frame, text="Árbol de análisis", padding="5")
        graph_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)

    def log(self, mensaje: str, nivel: int = 0):
        self.log_text.insert(tk.END, "  " * nivel + mensaje + "\n")
        self.log_text.see(tk.END)

    def es_valida(self, palabra: str) -> Tuple[bool, Optional[Nodo]]:
        self.log_text.delete(1.0, tk.END)
        
        if not palabra:
            self.log("✓ Palabra vacía (E)")
            return True, Nodo("EMPTY", "E")

        def es_valida_recursiva(palabra: str, nivel: int) -> Tuple[bool, Optional[Nodo]]:
            self.log(f"Analizando: '{palabra}'", nivel)
            
            # Caso E (cadena vacía)
            if not palabra:
                self.log("✓ Caso E válido", nivel)
                return True, Nodo("EMPTY", "E")
            
            # Caso SS
            self.log("Probando caso SS", nivel)
            for i in range(1, len(palabra)):
                izq, arbol_izq = es_valida_recursiva(palabra[:i], nivel + 1)
                if izq:
                    der, arbol_der = es_valida_recursiva(palabra[i:], nivel + 1)
                    if der:
                        self.log("✓ Caso SS válido", nivel)
                        return True, Nodo("CONCAT", "SS", [arbol_izq, arbol_der])
            
            # Casos aSb y aSc
            if len(palabra) >= 2 and palabra[0] == 'a':
                if palabra[-1] == 'b' or palabra[-1] == 'c':
                    interno = palabra[1:-1]
                    self.log(f"Probando caso aS{palabra[-1]}", nivel)
                    valido, arbol = es_valida_recursiva(interno, nivel + 1)
                    if valido:
                        self.log(f"✓ Caso aS{palabra[-1]} válido", nivel)
                        return True, Nodo("PROD", f"aS{palabra[-1]}", [arbol])

            self.log("❌ No se encontró una producción válida", nivel)
            return False, None

        return es_valida_recursiva(palabra, 0)

    def crear_grafo(self, nodo: Optional[Nodo]) -> nx.Graph:
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
        self.ax.clear()
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        nx.draw(G, pos, ax=self.ax, 
                node_color='lightblue',
                node_size=2000,
                width=2,
                edge_color='gray',
                arrows=False)
        
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=12)
        
        self.ax.set_axis_off()
        self.canvas.draw()

    def analizar(self):
        palabra = self.entrada.get().strip()
        
        if not re.match(r'^[abc]*$', palabra):
            self.log("Error: La palabra solo debe contener los caracteres a, b y c")
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