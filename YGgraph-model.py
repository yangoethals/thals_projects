import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Button
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import math
import copy

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YGgraphe-modele")
        self.root.geometry("900x500")

        self.G = nx.MultiDiGraph()
        self.pos = {}
        self.dragging_node = None

        self.history = []
        self.future = []

        # Panels
        self.panel1 = tk.Frame(root, width=300, bg='lightgray')
        self.panel1.pack(side='left', fill='y')
        self.panel2 = tk.Frame(root, width=600, bg='white')
        self.panel2.pack(side='right', fill='both', expand=True)

        # Sommet
        self.frame_sommets = tk.LabelFrame(self.panel1, text="Sommet", padx=10, pady=10)
        self.frame_sommets.pack(padx=10, pady=10, fill='x')
        tk.Label(self.frame_sommets, text="Initiale :").pack(anchor='w')
        self.entry_sommet = tk.Entry(self.frame_sommets)
        self.entry_sommet.pack(fill='x')
        tk.Button(self.frame_sommets, text="Ajouter", command=self.ajouter_sommet).pack(pady=5)

        # Arête
        self.frame_aretes = tk.LabelFrame(self.panel1, text="Arête", padx=10, pady=10)
        self.frame_aretes.pack(padx=10, pady=10, fill='x')
        tk.Label(self.frame_aretes, text="Sommet 1 :").pack(anchor='w')
        self.entry_s1 = tk.Entry(self.frame_aretes)
        self.entry_s1.pack(fill='x')
        tk.Label(self.frame_aretes, text="Sommet 2 :").pack(anchor='w')
        self.entry_s2 = tk.Entry(self.frame_aretes)
        self.entry_s2.pack(fill='x')
        tk.Label(self.frame_aretes, text="Poids (optionnel) :").pack(anchor='w')
        self.entry_poids = tk.Entry(self.frame_aretes)
        self.entry_poids.pack(fill='x')
        tk.Button(self.frame_aretes, text="Valider", command=self.ajouter_arete).pack(pady=5)

        # Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel2)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("button_press_event", self.on_right_click)

        # Boutons
        bouton_frame = tk.Frame(self.panel2)
        bouton_frame.pack(fill='x')
        tk.Button(bouton_frame, text="Enregistrer Graphe", command=self.enregistrer_graphe).pack(side='left', padx=5, pady=5)
        tk.Button(bouton_frame, text="Parcours", command=self.ouvrir_parcours).pack(side='left', padx=5, pady=5)
        tk.Button(bouton_frame, text="Nouveau Graphe", command=self.nouveau_graphe).pack(side='left', padx=5, pady=5)
        tk.Button(bouton_frame, text="Annuler", command=self.undo).pack(side='left', padx=5, pady=5)
        tk.Button(bouton_frame, text="Rétablir", command=self.redo).pack(side='left', padx=5, pady=5)
        tk.Button(bouton_frame, text="Documentation", command=self.documentation_plateforme).pack(side='left', padx=5, pady=5)

    def save_state(self):
        self.history.append((copy.deepcopy(self.G), copy.deepcopy(self.pos)))
        self.future.clear()

    def ajouter_sommet(self):
        sommet = self.entry_sommet.get().strip()
        if not sommet.isalnum():
            messagebox.showerror("Erreur", "Lettre ou chiffre seulement")
            return
        if sommet in self.G.nodes:
            messagebox.showwarning("Attention", "Sommet existe déjà")
            return
        self.save_state()
        self.G.add_node(sommet)
        self.pos[sommet] = self._generer_position_unique()
        self.redessiner()

    def ajouter_arete(self):
        s1, s2 = self.entry_s1.get().strip(), self.entry_s2.get().strip()
        poids = self.entry_poids.get().strip()
        if s1 not in self.G.nodes or s2 not in self.G.nodes:
            messagebox.showerror("Erreur", "Sommets inexistants")
            return
        self.save_state()
        if poids:
            try:
                poids = float(poids)
                self.G.add_edge(s1, s2, weight=poids)
            except:
                messagebox.showerror("Erreur", "Poids doit être un nombre")
        else:
            self.G.add_edge(s1, s2)
        self.redessiner()

    def undo(self):
        if not self.history:
            return
        self.future.append((copy.deepcopy(self.G), copy.deepcopy(self.pos)))
        self.G, self.pos = self.history.pop()
        self.redessiner()

    def redo(self):
        if not self.future:
            return
        self.history.append((copy.deepcopy(self.G), copy.deepcopy(self.pos)))
        self.G, self.pos = self.future.pop()
        self.redessiner()

    def nouveau_graphe(self):
        self.save_state()
        self.G.clear()
        self.pos.clear()
        self.redessiner()

    def _generer_position_unique(self):
        tries = 0
        while True:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.1, 0.4)
            x = 0.5 + radius * math.cos(angle)
            y = 0.5 + radius * math.sin(angle)
            overlap = False
            for other in self.pos.values():
                if (x - other[0]) ** 2 + (y - other[1]) ** 2 < 0.02:
                    overlap = True
                    break
            if not overlap:
                return [x, y]
            tries += 1
            if tries > 100:
                return [0.5, 0.5]

    def redessiner(self):
        self.ax.clear()
        nx.draw_networkx_nodes(self.G, pos=self.pos, ax=self.ax, node_size=800, node_color='lightblue')
        nx.draw_networkx_labels(self.G, pos=self.pos, ax=self.ax, font_size=12)
        for u, v, key in self.G.edges(keys=True):
            if u == v:
                nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=[(u, v)], ax=self.ax,
                                       connectionstyle="arc3,rad=0.3", arrowstyle='-|>', arrowsize=20)
            elif self.G.number_of_edges(u, v) > 1 or self.G.number_of_edges(v, u) > 0:
                rad = 0.2 if (u, v) > (v, u) else -0.2
                nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=[(u, v)], ax=self.ax,
                                       connectionstyle=f"arc3,rad={rad}", arrowstyle='-|>', arrowsize=20)
            else:
                nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=[(u, v)], ax=self.ax,
                                       arrowstyle='-|>', arrowsize=20)
        labels = {(u, v): d['weight'] for u, v, d in self.G.edges(data=True) if 'weight' in d}
        nx.draw_networkx_edge_labels(self.G, pos=self.pos, edge_labels=labels, ax=self.ax, label_pos=0.7)
        self.ax.set_axis_off()
        self.canvas.draw()

    def on_press(self, event):
        if event.xdata and event.ydata:
            for node, (x, y) in self.pos.items():
                if (x - event.xdata) ** 2 + (y - event.ydata) ** 2 < 0.02:
                    self.dragging_node = node
                    break

    def on_motion(self, event):
        if self.dragging_node and event.xdata and event.ydata:
            self.pos[self.dragging_node] = [event.xdata, event.ydata]
            self.redessiner()

    def on_release(self, event):
        self.dragging_node = None

    def on_right_click(self, event):
        if event.button == 3 and event.xdata and event.ydata:
            for node, (x, y) in self.pos.items():
                if (x - event.xdata) ** 2 + (y - event.ydata) ** 2 < 0.02:
                    self.save_state()
                    self.G.remove_node(node)
                    self.pos.pop(node)
                    self.redessiner()
                    return

    def enregistrer_graphe(self):
        nx.write_gml(self.G, "graphe_enregistre.gml")
        messagebox.showinfo("Info", "Graphe enregistré dans graphe_enregistre.gml")

    def ouvrir_parcours(self):
        ParcoursWindow(self.root, self.G, self.pos)

    def documentation_plateforme(self):
        doc = Toplevel(self.root)
        doc.title("Documentation de la plateforme")
        doc.geometry("400x300")
        text = (
            "Plateforme conçue pour la modélisation et la manipulation de graphes.\n\n"
            "Créateur : Yan Goethals\n"
            "Université Protestante de Lubumbashi\n"
            "Faculté des Sciences Informatiques\n"
            "BAC 3 Système Informatique\n"
            "Inspiré par le cours de Modélisation Objet en Réseau donné par M. Wesley Kumwimba\n"
            "Année académique 2025."
        )
        Label(doc, text=text, justify="left", wraplength=380).pack(padx=10, pady=10)
        Button(doc, text="Fermer", command=doc.destroy).pack(pady=5)



class ParcoursWindow:
    def __init__(self, parent, G, pos):
        self.G = G
        self.pos = pos
        self.win = tk.Toplevel(parent)
        self.win.title("Parcours et Vérification")
        self.win.geometry("900x500")

        self.panel1 = tk.Frame(self.win, width=300, bg='lightgray')
        self.panel1.pack(side='left', fill='y')
        self.panel2 = tk.Frame(self.win, width=600, bg='white')
        self.panel2.pack(side='right', fill='both', expand=True)

        self.frame_verif = tk.LabelFrame(self.panel1, text="Vérification", padx=10, pady=10)
        self.frame_verif.pack(padx=10, pady=10, fill='x')
        self.btn_verif = tk.Button(self.frame_verif, text="Vérifier", command=self.verifier_graphe)
        self.btn_verif.pack(pady=5)

        self.frame_parcours = tk.LabelFrame(self.panel1, text="Parcours", padx=10, pady=10)
        self.frame_parcours.pack(padx=10, pady=10, fill='x')
        tk.Button(self.frame_parcours, text="DFS", command=self.parcours_dfs).pack(pady=5)
        tk.Button(self.frame_parcours, text="BFS", command=self.parcours_bfs).pack(pady=5)

        self.frame_chemin = tk.LabelFrame(self.panel1, text="Chemin Dijkstra", padx=10, pady=10)
        self.frame_chemin.pack(padx=10, pady=10, fill='x')
        tk.Label(self.frame_chemin, text="Sommet 1 :").pack(anchor='w')
        self.entry_c1 = tk.Entry(self.frame_chemin)
        self.entry_c1.pack(fill='x')
        tk.Label(self.frame_chemin, text="Sommet 2 :").pack(anchor='w')
        self.entry_c2 = tk.Entry(self.frame_chemin)
        self.entry_c2.pack(fill='x')
        tk.Button(self.frame_chemin, text="Valider", command=self.chemin_dijkstra).pack(pady=5)

    def verifier_graphe(self):
        result = ""
        if nx.is_eulerian(self.G):
            result = "Eulérien"
        elif self._is_hamiltonian():
            result = "Hamiltonien"
        elif nx.is_tree(self.G.to_undirected()):
            result = "Arbre"
        elif nx.is_multigraph(self.G):
            result = "Multigraphe"
        elif self.G.number_of_nodes() == 0:
            result = "Graphe Nul"
        else:
            result = "Aucun"
        messagebox.showinfo("Vérification", f"Type : {result}")
        self._affiche_doc("Documentation Vérification", self._get_doc(result))

    def _is_hamiltonian(self):
        n = len(self.G.nodes)
        for node in self.G.nodes:
            if self.G.degree(node) < n / 2:
                return False
        return True

    def parcours_dfs(self):
        start = simpledialog.askstring("DFS", "Sommet de départ :")
        if start not in self.G.nodes:
            messagebox.showerror("Erreur", "Sommet inexistant")
            return
        path = list(nx.dfs_edges(self.G, source=start))
        self._afficher_parcours(path, "DFS", "red")

    def parcours_bfs(self):
        start = simpledialog.askstring("BFS", "Sommet de départ :")
        if start not in self.G.nodes:
            messagebox.showerror("Erreur", "Sommet inexistant")
            return
        path = list(nx.bfs_edges(self.G, source=start))
        self._afficher_parcours(path, "BFS", "blue")

    def chemin_dijkstra(self):
        s1 = self.entry_c1.get().strip()
        s2 = self.entry_c2.get().strip()
        if s1 not in self.G.nodes or s2 not in self.G.nodes:
            messagebox.showerror("Erreur", "Sommet inexistant")
            return
        if not nx.is_weighted(self.G):
            messagebox.showerror("Erreur", "Graphe non pondéré")
            return
        shortest = nx.dijkstra_path(self.G, s1, s2)
        edges = list(zip(shortest, shortest[1:]))
        fig, ax = plt.subplots()
        nx.draw_networkx(self.G, pos=self.pos, ax=ax, with_labels=True, node_color='lightblue')
        nx.draw_networkx_edges(self.G, pos=self.pos, ax=ax, edgelist=edges, edge_color='green', width=2)
        ax.set_title("Chemin Dijkstra")
        plt.show()
        self._affiche_doc("Documentation Dijkstra", self._get_doc("Dijkstra"))

    def _afficher_parcours(self, path, algo, color):
        fig, ax = plt.subplots()
        nx.draw_networkx(self.G, pos=self.pos, ax=ax, with_labels=True, node_color='lightblue')
        nx.draw_networkx_edges(self.G, pos=self.pos, ax=ax, edgelist=path, edge_color=color, width=2)
        ax.set_title(f"{algo} Parcours")
        plt.show()
        self._affiche_doc(f"Documentation {algo}", self._get_doc(algo))

    def _get_doc(self, key):
        docs = {
            "Eulérien": "Un graphe Eulérien a un chemin fermé visitant chaque arête une fois. Tous les sommets ont un degré pair et le graphe est connexe.",
            "Hamiltonien": "Un graphe Hamiltonien a un cycle passant une fois par chaque sommet. Sa vérification est complexe (NP-complet).",
            "Arbre": "Un arbre est un graphe connexe sans cycle. Il a n sommets et n-1 arêtes.",
            "Multigraphe": "Un multigraphe peut contenir plusieurs arêtes entre deux sommets.",
            "Graphe Nul": "Un graphe nul ne contient aucun sommet ni arête.",
            "Aucun": "Le graphe ne vérifie pas les propriétés standards.",
            "DFS": "DFS explore en profondeur chaque branche avant de revenir. Utilise une pile ou la récursion.",
            "BFS": "BFS explore niveau par niveau, visitant tous les voisins avant d'approfondir. Utilise une file FIFO.",
            "Dijkstra": "Dijkstra trouve le chemin le plus court dans un graphe pondéré à poids positifs. Il utilise une file de priorité pour choisir l'arête de plus faible coût."
        }
        return docs.get(key, "")

    def _affiche_doc(self, title, text):
        doc_win = Toplevel(self.win)
        doc_win.title(title)
        doc_win.geometry("300x200")
        Label(doc_win, text=text, wraplength=280, justify="left").pack(padx=10, pady=10)
        Button(doc_win, text="Fermer", command=doc_win.destroy).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
