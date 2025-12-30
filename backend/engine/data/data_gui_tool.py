import csv
import tkinter as tk
from tkinter import ttk, messagebox

CSV_FILE = "backend/engine/data/raw_data.csv"  # your CSV path

class MahjongEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Mahjong Best Discard Editor")
        self.data = []
        self.index = 0

        # Load CSV
        self.load_csv()

        # Start at first row where best_discard is empty
        for i, row in enumerate(self.data):
            if not row["best_discard"].strip():
                self.index = i
                break

        # Labels for current row
        self.row_label = tk.Label(master, text="")
        self.row_label.pack(pady=5)

        # Display the hand info
        self.concealed_label = tk.Label(master, text="")
        self.concealed_label.pack()
        self.display_label = tk.Label(master, text="")
        self.display_label.pack()
        self.flowers_label = tk.Label(master, text="")
        self.flowers_label.pack()

        # Entry for best_discard
        tk.Label(master, text="Best Discard:").pack()
        self.discard_entry = tk.Entry(master, width=30)
        self.discard_entry.pack()

        # Navigation buttons
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Previous", command=self.prev_row).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Next", command=self.next_row).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Save CSV", command=self.save_csv).grid(row=0, column=2, padx=5)

        self.show_row()

    def load_csv(self):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.data = list(reader)

    def show_row(self):
        row = self.data[self.index]
        self.row_label.config(text=f"Row {self.index+1}/{len(self.data)}")
        self.concealed_label.config(text="Concealed: " + row["concealed"])
        self.display_label.config(text="Display: " + row["display"])
        self.flowers_label.config(text="Flowers: " + row["flowers"])
        self.discard_entry.delete(0, tk.END)
        self.discard_entry.insert(0, row["best_discard"])

    def save_current_row(self):
        self.data[self.index]["best_discard"] = self.discard_entry.get().strip()

    def prev_row(self):
        self.save_current_row()
        if self.index > 0:
            self.index -= 1
            self.show_row()

    def next_row(self):
        self.save_current_row()
        if self.index < len(self.data) - 1:
            self.index += 1
            self.show_row()

    def save_csv(self):
        self.save_current_row()
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["concealed","display","flowers","best_discard"])
            writer.writeheader()
            writer.writerows(self.data)
        messagebox.showinfo("Saved", "CSV saved successfully!")
