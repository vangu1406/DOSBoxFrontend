import tkinter as tk
from tkinter import ttk, messagebox
from entry_form import EntryForm
import sqlite3
import os

class DOSBoxFrontend:

    def __init__(self, root):
        self.root = root
        self.root.title("DOSBox Frontend")
        self.db_connection = sqlite3.connect("dosbox_entries.db")
        self.conf_file_path = ""
        self.dosbox_path = "PATH\\FOR\\DOSBOX\\EXECUTABLE"
        self.create_table()
        self.create_widgets()
        self.populate_treeview()
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_exit())

    def open_entry_form(self):
        if hasattr(self, 'entry_form') and self.entry_form.winfo_exists():
            self.entry_form.focus_set()
        else:
            self.entry_form = EntryForm(self.root, self.db_connection)
            self.root.wait_window(self.entry_form)
            self.root.after(100, self.update_treeview)

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, title TEXT, genre TEXT, year INTEGER, executable_path TEXT)")
        self.db_connection.commit()

    def populate_treeview(self):
        # Remove duplicates
        for item in self.table.get_children():
            self.table.delete(item)

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM entries")
        rows = cursor.fetchall()

        # Insert data into the table
        for row in rows:
            self.table.insert("", "end", values=row)

    def update_treeview(self):
        self.populate_treeview()

    def remove_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a row to remove.")
            return

        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to remove the selected entry?")
        if confirmation:
            selected_id = self.table.item(selected_item, "values")[0]

            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM entries WHERE id=?", (selected_id,))
            self.db_connection.commit()

            cursor.execute("UPDATE entries SET id = id - 1 WHERE id > ?", (selected_id,))
            self.db_connection.commit()

            self.update_treeview()

    def edit_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a row to edit.")
            return

        selected_id = self.table.item(selected_item, "values")[0]

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM entries WHERE id=?", (selected_id,))
        entry_data = cursor.fetchone()

        if hasattr(self, 'entry_form') and self.entry_form.winfo_exists():
            self.entry_form.focus_set()
        else:
            self.entry_form = EntryForm(self.root, self.db_connection, is_edit=True, initial_data=entry_data)
            self.root.wait_window(self.entry_form)
            self.root.after(100, self.update_treeview)

    def run_dosbox(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a row to run.")
            return

        selected_values = self.table.item(selected_item, "values")
        game_path = selected_values[4]

        # Place the conf file in the same dir as the game
        self.conf_file_path = os.path.join(os.path.dirname(game_path), "dosbox_auto.conf")

        conf_file_content = f"""
[autoexec]
mount c "{os.path.dirname(game_path)}"
c:
{os.path.basename(game_path)}

"""

        if not os.path.exists(self.conf_file_path):
            with open(self.conf_file_path, "w") as conf_file:
                conf_file.write(conf_file_content)

        os.system(f'{self.dosbox_path} -conf {self.conf_file_path}')

    def on_exit(self):
        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
            self.db_connection.close()
            self.root.destroy()

    def create_widgets(self):
        self.frame_buttons = ttk.Frame(self.root)
        self.frame_buttons.grid(row=0, column=0, columnspan=4)

        btn_add = ttk.Button(self.frame_buttons, text="Add", command=self.open_entry_form)
        btn_remove = ttk.Button(self.frame_buttons, text="Remove", command=self.remove_entry)
        btn_edit = ttk.Button(self.frame_buttons, text="Edit", command=self.edit_entry)
        btn_run = ttk.Button(self.frame_buttons, text="Run", command=self.run_dosbox)

        btn_add.grid(row=0, column=0, padx=10, pady=10)
        btn_remove.grid(row=0, column=1, padx=10, pady=10)
        btn_edit.grid(row=0, column=2, padx=10, pady=10)
        btn_run.grid(row=0, column=3, padx=10, pady=10)

        self.table = ttk.Treeview(self.root, columns=("id", "title", "genre", "year", "executable path"), show="headings")
        self.table.heading("id", text="ID")
        self.table.heading("title", text="Title")
        self.table.heading("genre", text="Genre")
        self.table.heading("year", text="Year")
        self.table.heading("executable path", text="Executable path")

        self.table.column("id", width=50, anchor="center")
        self.table.column("title", width=100, anchor="center")
        self.table.column("genre", width=100, anchor="center")
        self.table.column("year", width=50, anchor="center")
        self.table.column("executable path", width=450, anchor="center")
        self.table.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.table.yview)
        self.scrollbar.grid(row=1, column=4, sticky="ns")
        self.table.configure(yscrollcommand=self.scrollbar.set)


if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    dosbox_frontend = DOSBoxFrontend(root)
    root.mainloop()