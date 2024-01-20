import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3

class EntryForm(tk.Toplevel):
    def __init__(self, parent, db_connection, is_edit=False, initial_data=None):
        super().__init__(parent)
        self.title("Edit Entry" if is_edit else "Add Entry")
        self.geometry("400x220")
        self.db_connection = db_connection
        self.is_edit = is_edit
        self.initial_data = initial_data

        self.title_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.year_var = tk.IntVar()
        self.executable_path_var = tk.StringVar()

        ttk.Label(self, text="Title:").grid(row=1, column=0, padx=10, pady=10)
        self.title_entry = ttk.Entry(self, textvariable=self.title_var, width=25)
        self.title_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text="Genre:").grid(row=2, column=0, padx=10, pady=10)
        self.genre_entry = ttk.Entry(self, textvariable=self.genre_var, width=25)
        self.genre_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="Year:").grid(row=3, column=0, padx=10, pady=10)
        self.year_entry = ttk.Spinbox(self, from_=0, to=9999, textvariable=self.year_var, width=5)
        self.year_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self, text="Executable path:").grid(row=4, column=0, padx=10, pady=10)
        self.executable_path_entry = ttk.Entry(self, textvariable=self.executable_path_var, width=25)
        self.executable_path_entry.grid(row=4, column=1, padx=10, pady=10)

        browse_button = ttk.Button(self, text="Browse", command=self.browse_executable_path)
        browse_button.grid(row=4, column=2, padx=5, pady=10)

        save_button = ttk.Button(self, text="Save", command=self.save_entry)
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Toplevel in editing mode
        if is_edit and initial_data:
            self.title_var.set(initial_data[1])
            self.genre_var.set(initial_data[2])
            self.year_var.set(initial_data[3])
            self.executable_path_var.set(initial_data[4])

    def browse_executable_path(self):
        executable_path = filedialog.askopenfilename(parent=self, title="Select Executable Path", filetypes=[("Executable Files", "*.exe")])

        if executable_path:
            self.executable_path_var.set(executable_path)

    def save_entry(self):
        title = self.title_var.get()
        genre = self.genre_var.get()

        try:
            year = self.year_var.get()
        except tk.TclError:
            messagebox.showerror("Error", "Year must be a valid integer.")
            return

        executable_path = self.executable_path_var.get()

        if not executable_path:
            messagebox.showerror("Error", "Executable path is required.")
            return

        if self.is_edit:
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE entries SET title=?, genre=?, year=?, executable_path=? WHERE id=?",
                           (title, genre, year, executable_path, self.initial_data[0]))
        else:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO entries (title, genre, year, executable_path) VALUES (?, ?, ?, ?)",
                           (title, genre, year, executable_path))

        self.db_connection.commit()

        print("Entry saved!")
        self.destroy()