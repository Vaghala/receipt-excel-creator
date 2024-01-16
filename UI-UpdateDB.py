

import tkinter as tk
from tkinter import ttk,Label,messagebox
from tkinter.filedialog import askopenfilename

import sqlite3 

if __name__ == "__main__":
    with sqlite3.connect("./Database.db") as db:
        cursor = db.cursor()

        afm = input(f"Εισαγωγή ΑΦΜ ή 'ε' για εξοδο : ")
        while True:

            if afm == 'ε' or afm =='e':
                break

            cursor.execute(f"select AFM,Company_Name,Product_Type from Companies where AFM = '{afm}';")

            if res := cursor.fetchone():

                AFM,Company_Name,Product_Type = res

                print(f"\nΑΦΜ : {AFM}\nΕταιρία : {Company_Name}\nΕίδος : {Product_Type}\n")
                
                p_type = input(f"\nΕισαγωγή νεου ειδους ή 'ε' για εξοδο : ")

                if not(p_type == 'ε' or p_type =='e'):
                    cursor.execute(f"Update Companies set Product_Type = '{p_type}' where AFM = '{afm}';")
                    db.commit()
                    print(f"Καταχωρήθηκε:\n{AFM}\t{Company_Name}\t{p_type}\n")
            else:
                print("\nΗ εγγραφη ΔΕΝ υπαρχει στην βαση !\n")

            afm = input(f"Εισαγωγή ΑΦΜ ή 'ε' για εξοδο : ")

    print("Exiting...")