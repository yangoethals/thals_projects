import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import scapy.all as scapy

import threading

class SnifferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YPCAP Sniffer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.captured_packets = []

        created_label = ttk.Label(self.root, text="Created by Yan Goethals", font=("Arial", 10, "italic"))
        created_label.pack(anchor="nw", padx=10, pady=5)

        top_right_frame = ttk.Frame(self.root)
        top_right_frame.pack(anchor="ne", padx=10, pady=10)

        # Bouton Analyser
        analyze_button = ttk.Button(top_right_frame, text="Analyser", command=self.load_capture)
        analyze_button.pack(side="left", padx=5)

        # Bouton Documentation
        doc_button = ttk.Button(top_right_frame, text="Documentation", command=self.show_documentation)
        doc_button.pack(side="left", padx=5)

        # Interfaces Listbox
        ttk.Label(self.root, text="Interfaces:").pack(pady=5)
        self.interface_listbox = tk.Listbox(self.root)
        self.interface_listbox.pack(fill="both", expand=True, padx=20, pady=5)

        # Afficher interfaces lisibles
        self.iface_mapping = []
        for iface in scapy.get_if_list():
            try:
                ip = scapy.get_if_addr(iface)
                display_name = f"{iface} ({ip})"
            except Exception:
                display_name = iface
            self.interface_listbox.insert(tk.END, display_name)
            self.iface_mapping.append(iface)

        # Bouton Valider
        self.validate_button = ttk.Button(self.root, text="Valider", command=self.show_protocols)
        self.validate_button.pack(pady=10)

        self.protocol_listbox = None
        self.count_entry = None
        self.execute_button = None
        self.progress = None
        self.show_button = None

    def show_protocols(self):
        selected = self.interface_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une interface.")
            return
        index = selected[0]
        self.interface = self.iface_mapping[index]

        if not self.protocol_listbox:
            ttk.Label(self.root, text="Protocoles:").pack(pady=5)
            self.protocol_listbox = tk.Listbox(self.root)
            self.protocol_listbox.pack(fill="both", expand=True, padx=20, pady=5)
            for proto in ["ip", "tcp", "udp", "icmp", "arp"]:
                self.protocol_listbox.insert(tk.END, proto)

            ttk.Label(self.root, text="Nombre de paquets:").pack(pady=5)
            self.count_entry = ttk.Entry(self.root)
            self.count_entry.pack(pady=5)

            self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", maximum=100)
            self.progress.pack(fill="x", padx=20, pady=10)

            self.execute_button = ttk.Button(self.root, text="Exécuter", command=self.start_sniffing)
            self.execute_button.pack(pady=5)

            self.show_button = ttk.Button(self.root, text="Afficher", command=self.show_packets)
            self.show_button.pack(pady=5)

    def start_sniffing(self):
        selected = self.protocol_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un protocole.")
            return
        self.protocol = self.protocol_listbox.get(selected)
        try:
            self.count = int(self.count_entry.get())
        except ValueError:
            messagebox.showwarning("Attention", "Veuillez entrer un nombre valide.")
            return

        self.progress["value"] = 0
        threading.Thread(target=self.sniff_packets).start()

    def sniff_packets(self):
        self.captured_packets = []

        def update_progress(pkt):
            self.captured_packets.append(pkt)
            percent = int(len(self.captured_packets) / self.count * 100)
            self.progress["value"] = percent

        scapy.sniff(count=self.count, iface=self.interface, filter=self.protocol, prn=update_progress)

    def show_packets(self):
        if not self.captured_packets:
            messagebox.showwarning("Attention", "Aucun paquet capturé ou chargé.")
            return

        window = tk.Toplevel(self.root)
        window.geometry("700x700")
        window.title("Paquets capturés")
        window.resizable(True, True)

        text = tk.Text(window)
        text.pack(fill="both", expand=True, padx=10, pady=10)

        for pkt in self.captured_packets:
            text.insert(tk.END, pkt.show(dump=True) + "\n\n")

        frame = ttk.Frame(window)
        frame.pack(pady=10)

        save_button = ttk.Button(frame, text="Enregistrer", command=lambda: self.save_capture())
        save_button.pack(side="left", padx=10)

        quit_button = ttk.Button(frame, text="Quitter", command=lambda: self.confirm_quit(window))
        quit_button.pack(side="left", padx=10)

    def save_capture(self):
        if not self.captured_packets:
            messagebox.showwarning("Attention", "Aucune capture à enregistrer.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pcap",
                                                 filetypes=[("PCAP Files", "*.pcap")])
        if file_path:
            scapy.wrpcap(file_path, self.captured_packets)
            messagebox.showinfo("Succès", f"Capture enregistrée sous {file_path}")

    def confirm_quit(self, window):
        if messagebox.askyesno("Confirmation", "Voulez-vous quitter ?"):
            window.destroy()

    def load_capture(self):
        file_path = filedialog.askopenfilename(filetypes=[("PCAP Files", "*.pcap")])
        if file_path:
            self.captured_packets = scapy.rdpcap(file_path)
            self.show_packets()

    def show_documentation(self):
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("800x500")

        text = tk.Text(doc_window, wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)

        documentation = (
            "DOCUMENTATION YPCAP\n\n"
            "Cette application est conçue pour permettre aux étudiants de l'Université Protestante de Lubumbashi "
            "à la Faculté de Sciences Informatiques de capturer, analyser et comprendre en profondeur le trafic réseau.\n\n"
            "Objectifs :\n"
            "- Capturer les paquets circulant sur le réseau en temps réel.\n"
            "- Analyser chaque paquet afin d'identifier les protocoles utilisés, les adresses IP, les ports et les données échangées.\n"
            "- Comprendre la structure des datagrammes à différents niveaux (Ethernet, IP, TCP/UDP, Application).\n"
            "- Explorer la sécurité réseau, le débogage de trafic et la surveillance des communications.\n\n"
            "Destinée aux cours et projets en :\n"
            "- Réseaux Informatiques\n"
            "- Sécurité des Systèmes\n"
            "- Administration Réseau\n"
            "- Développement d'outils de monitoring.\n\n"
            "Cette application est un outil pédagogique pour expérimenter concrètement "
            "les concepts vus en théorie et mieux appréhender le fonctionnement des réseaux modernes.\n\n"
            "Utilisez-la de manière responsable et respectez les règles de votre institution.\n"
        )

        text.insert(tk.END, documentation)

        quit_doc_button = ttk.Button(doc_window, text="Quitter", command=doc_window.destroy)
        quit_doc_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = SnifferApp(root)
    root.mainloop()
