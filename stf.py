import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import Optional, Tuple, List
import re

class Nodo:
    def __init__(self, tipo: str, valor: str, hijos: List['Nodo'] = None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.id = id(self)

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico - Expresiones Aritméticas")
        self.root.geometry("1200x800")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Entrada y botón
        ttk.Label(top_frame, text="Ingrese expresión:").pack(side=tk.LEFT, padx=5)
        self.entrada = ttk.Entry(top_frame, width=40)
        self.entrada.pack(side=tk.LEFT, padx=5)
        self.entrada.insert(0, "a+a*a")
        
        ttk.Button(top_frame, text="Analizar", command=self.analizar).pack(side=tk.LEFT, padx=5)
        
        # Frame de gramática
        grammar_frame = ttk.LabelFrame(main_frame, text="Gramática", padding="5")
        grammar_frame.pack(fill=tk.X, pady=5)
        
        grammar_text = "S → S + T | T\nT → T * F | F\nF → (S) | a"
        ttk.Label(grammar_frame, text=grammar_text, font=('Courier', 12)).pack(pady=5)
        
        # Frame inferior dividido
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame del log
        log_frame = ttk.LabelFrame(bottom_frame, text="Log de análisis", padding="5")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame del árbol
        tree_frame = ttk.LabelFrame(bottom_frame, text="Árbol sintáctico", padding="5")
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(self.fig, master=tree_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.pos = 0
        self.tokens = []

    def log(self, mensaje: str, nivel: int = 0):
        self.log_text.insert(tk.END, "  " * nivel + mensaje + "\n")
        self.log_text.see(tk.END)

    def parse_S(self) -> Optional[Nodo]:
        self.log("Intentando S")
        pos_inicial = self.pos
        
        # Primero intentamos T
        nodo_t = self.parse_T()
        if nodo_t is None:
            return None
            
        # Si encontramos un T, verificamos si hay un '+'
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '+':
            self.pos += 1
            siguiente_t = self.parse_T()
            if siguiente_t is None:
                self.pos = pos_inicial
                return None
            nodo_t = Nodo('S', 'S+T', [nodo_t, siguiente_t])
            
        return Nodo('S', 'T', [nodo_t]) if len(nodo_t.hijos) == 1 else nodo_t

    def parse_T(self) -> Optional[Nodo]:
        self.log("Intentando T")
        pos_inicial = self.pos
        
        # Primero intentamos F
        nodo_f = self.parse_F()
        if nodo_f is None:
            return None
            
        # Si encontramos un F, verificamos si hay un '*'
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '*':
            self.pos += 1
            siguiente_f = self.parse_F()
            if siguiente_f is None:
                self.pos = pos_inicial
                return None
            nodo_f = Nodo('T', 'T*F', [nodo_f, siguiente_f])
            
        return Nodo('T', 'F', [nodo_f]) if len(nodo_f.hijos) == 1 else nodo_f

    def parse_F(self) -> Optional[Nodo]:
        self.log("Intentando F", nivel=1)  # Añadido nivel para mejor visualización
        if self.pos >= len(self.tokens):
            self.log("Fin de entrada alcanzado", nivel=2)
            return None
        
        # F -> (S)
        if self.tokens[self.pos] == '(':
            self.log("Encontrado '('", nivel=2)
            self.pos += 1
            nodo_s = self.parse_S()
            if nodo_s is not None and self.pos < len(self.tokens) and self.tokens[self.pos] == ')':
                self.pos += 1
                self.log("Encontrado ')', cerrando paréntesis", nivel=2)
                return Nodo('F', '(S)', [nodo_s])
            self.log("Error: falta paréntesis de cierre", nivel=2)
            return None
        
        # F -> a
        if self.tokens[self.pos] == 'a':
            self.log("Encontrado 'a'", nivel=2)
            self.pos += 1
            return Nodo('F', 'a', [])
        
        self.log(f"Token no esperado: {self.tokens[self.pos]}", nivel=2)    
        return None

    def tokenizar(self, entrada: str) -> List[str]:
        self.log("Tokenizando entrada: " + entrada)
        tokens = []
        for char in entrada:
            if char in {'a', '+', '*', '(', ')'}:
                tokens.append(char)
                self.log(f"Token encontrado: {char}", nivel=1)
        self.log("Tokens resultantes: " + " ".join(tokens), nivel=1)
        return tokens

    def dibujar_arbol(self, nodo: Nodo):
        G = nx.Graph()
        
        def agregar_nodos(nodo: Nodo, padre_id: Optional[int] = None):
            if not nodo:
                return
            
            nodo_id = id(nodo)
            G.add_node(nodo_id, label=f"{nodo.tipo}\n{nodo.valor}")
            
            if padre_id is not None:
                G.add_edge(padre_id, nodo_id)
            
            for hijo in nodo.hijos:
                agregar_nodos(hijo, nodo_id)
        
        agregar_nodos(nodo)
        
        self.ax.clear()
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        nx.draw(G, pos, ax=self.ax,
                node_color='lightblue',
                node_size=3000,
                width=2,
                edge_color='gray',
                arrows=False)
        
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        
        self.ax.set_axis_off()
        self.fig.canvas.draw()

    def analizar(self):
        # Limpiar el log
        self.log_text.delete(1.0, tk.END)
        
        # Obtener la entrada
        entrada = self.entrada.get().strip()
        self.log("Iniciando análisis de: " + entrada)
        
        # Validar caracteres
        if not re.match(r'^[a+*()\s]*$', entrada):
            self.log("Error: La expresión solo puede contener a, +, *, ( y )")
            return
        
        # Eliminar espacios y tokenizar
        entrada = entrada.replace(" ", "")
        self.tokens = self.tokenizar(entrada)
        self.pos = 0
        
        # Realizar el análisis
        self.log("\nIniciando análisis sintáctico...")
        resultado = self.parse_S()
        
        # Verificar si se consumió toda la entrada
        if resultado is not None and self.pos == len(self.tokens):
            self.log("\n✓ La expresión PERTENECE a la gramática")
            self.dibujar_arbol(resultado)
        else:
            self.log("\n❌ La expresión NO pertenece a la gramática")
            self.ax.clear()
            self.ax.set_axis_off()
            self.fig.canvas.draw()

def main():
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()