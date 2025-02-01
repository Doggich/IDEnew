from os import path
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
from tkinter import ttk
import json
from module_importer import ModuleInstaller
import pkgutil


def open_file(path_: str) -> dict:
    with open(path_, "r") as f:
        return json.load(f)


def iter_dict(dct: dict) -> list:
    temp_lst: list = []
    for key in dct.keys():
        temp_lst.append(key)
    return temp_lst


THEMES: str = iter_dict(open_file(path.abspath("theme_config/theme.json")))
ICON: str = path.abspath("theme_config/icon.ico")


def view_modules() -> None:
    module_names = [(i, module.name) for i, module in enumerate(pkgutil.iter_modules())]
    module_names.sort()

    formatted_module_names = ""
    for i, (index, module_name) in enumerate(module_names):
        formatted_module_names += f"{index + 1}: {module_name} "
        if (i + 1) % 5 == 0:
            formatted_module_names += "\n"

    messagebox.showinfo("Modules", formatted_module_names)


class IDE:
    def __init__(self, root_):
        self.root = root_
        self.root.title("Alphabet IDE ")
        self.root.geometry("800x600")
        self.root.iconbitmap(ICON)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # File menu
        self.root.option_add("*tearOff", False)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New (Ctrl + n)", command=self.new_file)
        self.file_menu.add_command(label="Open (Ctrl + o)", command=self.open_file)
        self.file_menu.add_command(label="Save (Ctrl + s)", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut (Ctrl + x)", command=self.cut)
        self.edit_menu.add_command(label="Copy (Ctrl + c)", command=self.copy)
        self.edit_menu.add_command(label="Paste (Ctrl + v)", command=self.paste)
        self.edit_menu.add_command(label="Undo (Ctrl + y)", command=self.undo)
        self.edit_menu.add_command(label="Redo (Ctrl + u)", command=self.redo)

        # Execute menu and snippet
        self.exec_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Execute", menu=self.exec_menu)
        self.exec_menu.add_command(label="Run code (Ctrl + r)", command=self.run_code)
        self.exec_menu.add_command(label="Run snipet (Ctrl + q)", command=self.run_snipet)

        # Add menu
        self.add_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Add", menu=self.add_menu)
        self.add_menu.add_command(label="Add page (Ctrl + j)", command=self.create_new_window)

        # Module menu
        self.module_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Modules", menu=self.module_menu)
        self.module_menu.add_command(label="Module master (Ctrl + n)", command=self.open_module_settings)
        self.module_menu.add_command(label="View modules (Ctrl + m)", command=view_modules)

        # Information menu
        self.info_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Info.", menu=self.info_menu)
        self.info_menu.add_command(label="About app (Ctrl + i)")

        self.text_area = tk.Text(self.root, undo=True)
        self.text_area.pack(fill="both", expand=True, padx=5)

        # Change themes
        self.theme_combobox = ttk.Combobox(self.root, values=THEMES)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)
        self.theme_combobox.pack()

        # Hotkeys
        self.root.bind_all("<Control-j>", lambda event: self.create_new_window())
        self.root.bind_all("<Control-n>", lambda event: self.new_file())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
        self.root.bind_all("<Control-o>", lambda event: self.open_file())
        self.root.bind_all("<Control-r>", lambda event: self.run_code())
        self.root.bind_all("<Control-q>", lambda event: self.run_snipet())
        self.root.bind_all("<Control-v>", lambda event: self.paste())
        self.root.bind_all("<Control-x>", lambda event: self.cut())
        self.root.bind_all("<Control-c>", lambda event: self.copy())
        self.root.bind_all("<Control-m>", lambda event: view_modules())
        self.root.bind_all("<Control-y>", lambda event: self.undo())
        self.root.bind_all("<Control-u>", lambda event: self.redo())
        self.root.bind_all("<Control-n>", lambda event: self.open_module_settings())

    def new_file(self) -> None:
        self.text_area.delete(1.0, "end")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("SQL files", "*.sql"), ("All files", "*.*")])
        if file_path:
            try:
                self.text_area.delete(1.0, "end")
                with open(file_path, "r") as file:
                    self.text_area.insert("end", file.read())
            except UnicodeDecodeError:
                messagebox.showerror("Error", "Incorrect format!")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("SQL files", "*.sql"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, "end"))

    def cut(self):
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.selection_get())
        self.text_area.delete("sel.first", "sel.last")

    def copy(self):
        self.text_area.clipboard_clear()
        self.text_area.clipboard_append(self.text_area.selection_get())

    def paste(self):
        self.text_area.insert("insert", self.text_area.clipboard_get())

    def undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def run_code(self):
        code = self.text_area.get(1.0, "end")
        try:
            with open("temp.py", "w") as file:
                file.write(code)

            def run_in_thread():
                subprocess.call("start cmd /k python temp.py", shell=True)

            threading.Thread(target=run_in_thread).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def run_snipet():
        try:
            subprocess.call("start cmd /k title NewSnipet & python /k ", shell=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        theme_config = open_file("theme_config/theme.json")[selected_theme]
        self.text_area.config(
            bg=theme_config["bg"].upper(),
            fg=theme_config["fg"].upper(),
            font=(theme_config["font"], theme_config["font"][1]),
            insertbackground=theme_config["insertbg"].upper(),
            selectbackground=theme_config["selectbg"].upper())
        self.root.configure(bg=theme_config["windowbg"].upper())
        if theme_config["cursor_activ"].lower() == "default":
            self.text_area.config(cursor="dot")
        else:
            self.text_area.config(cursor=theme_config["cursor_activ"])

    def create_new_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Window")
        new_window.geometry("800x600")
        IDE(new_window)

    def open_module_settings(self):
        module_installer = tk.Toplevel(self.root)
        module_installer.title("Alphabet Module master")
        module_installer.geometry("300x100")
        ModuleInstaller(module_installer)


if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()
