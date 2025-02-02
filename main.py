from os import path
import re
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


THEMES: list[str] = iter_dict(open_file(path.abspath("theme_config/theme.json")))
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
        self.syntax_colors = {}

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

        self.text_area.tag_config("red", foreground="red")
        self.text_area.tag_config("blue", foreground="blue")
        self.text_area.tag_config("green", foreground="green")

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
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.on_key_release()

    def highlight_words(self, words, tag):
        content = self.text_area.get("1.0", tk.END)
        self.text_area.tag_remove(tag, "1.0", tk.END)

        # Escape special characters in the words list
        escaped_words = [re.escape(word) for word in words]

        # Define operators to highlight
        operators = ['+=', '-=', '*=', '/=', '**=', '%=', '>', '<', '>=', '<=', '==', '!=', '<<=', '>>=', '&=', '|=',
                     '^=', "->"]

        # Join the escaped words with '|' and add word boundaries where appropriate
        pattern = r'\b(?:' + '|'.join(escaped_words) + r')\b|(?:' + '|'.join(
            re.escape(op) for op in operators) + r')'

        for match in re.finditer(pattern, content):
            start = self.text_area.index(f"1.0+{match.start()}c")
            end = self.text_area.index(f"1.0+{match.end()}c")
            self.text_area.tag_add(tag, start, end)

    def delayed_highlight(self, words, color):
        if hasattr(self, f'_highlight_after_{color}'):
            self.text_area.after_cancel(getattr(self, f'_highlight_after_{color}'))
        setattr(self, f'_highlight_after_{color}',
                self.text_area.after(200, lambda: self.highlight_words(words, color)))

    def on_key_release(self, event=None):
        self.delayed_highlight(["print", "input", "int", "str", "float", "bool",
                                "list", "set", "tuple", "dict", "complex", "__getattr__", "__setattr__",
                                "__delattr__", "__getattribute__", "__len__", "__getitem__",
                                "__setitem__", "__delitem__", "__iter__", "__reversed__", "__contains__",
                                "__missing__", "__instancecheck__", "__subclasscheck__", "__call__", "__enter__",
                                "__exit__", "__get__", "__set__", "__delete__", "__copy__", "__deepcopy__",
                                "__getinitargs__", "__getnewargs__", "__getstate__", "__setstate__", "__reduce__",
                                "__reduce_ex__"
                                ], "SyntSet1")

        self.delayed_highlight(
            ["if", "else", "elif", "for", "while", "in", "and", "or",
             "not", "try", "except", "finally", "frozenset", "abs", "max", "round",
             "sum", "map", "filter", "len", "<<=", ">>=", "&=", "|=", "^=",
             "__int__", "__long__", "__float__", "__complex__", "__oct__", "__hex__",
             "__index__", "__trunc__", "__coerce__", "__str__", "__repr__", "__unicode__",
             "__format__", "__nonzero__", "__dir__", "__sizeof__"
             ], "SyntSet2")

        self.delayed_highlight(["def", "class", "return", "import", "from", "as", "range",
                                "__lshift__", "__rshift__", "__and__", "__or__", "__xor__",
                                "__radd__", "__rsub__", "__rmul__", "__rfloordiv__", "__rdiv__",
                                "__rtruediv__", "__rmod__", "__rdivmod__", "__rpow__", "__rlshift__", "__rrshift__",
                                "__rand__", "__ror__", "__rxor__", "__iadd__", "__isub__", "__imul__", "__ifloordiv__",
                                "__idiv__", "__itruediv__", "__imod__", "__ipow__", "__ilshift__", "__irshift__",
                                "__iand__", "__ior__", "__ixor__", "->"
                                ], "SyntSet3")

        self.delayed_highlight(
            ["True", "False", "None", "type", "+=", "-=", "*=", "lambda", "break", "open",
             "/=", "**=", "%=", ">", "<", ">=", "<=", "==", "!=", "__init__", "__del__", "__new__",
             "__cmp__", "__eq__", "__ne__", "__lt__", "__gt__", "__le__", "__ge__", "__pos__",
             "__neg__", "__abs__", "__invert__", "__round__", "__floor__", "__ceil__", "__trunc__",
             "__add__", "__sub__", "__mul__", "__floordiv__", "__div__", "__truediv__", "__mod__",
             "__divmod__", "__pow__"
             ], "SyntSet4")

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
                self.on_key_release(None)
            except UnicodeDecodeError:
                messagebox.showerror("Error", "Incorrect format!")
        self.on_key_release(None)

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
        from datetime import datetime
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subprocess.call(f'start cmd /k "title Snippet {current_time} && python"', shell=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        theme_config = open_file("theme_config/theme.json")[selected_theme]
        self.text_area.config(
            bg=theme_config["bg"].upper(),
            fg=theme_config["fg"].upper(),
            font=(theme_config["font"][0], theme_config["font"][1]),
            insertbackground=theme_config["insertbg"].upper(),
            selectbackground=theme_config["selectbg"].upper())
        self.root.configure(bg=theme_config["windowbg"].upper())
        if theme_config["cursor_activ"].lower() == "default":
            self.text_area.config(cursor="dot")
        else:
            self.text_area.config(cursor=theme_config["cursor_activ"])

        # Update syntax highlighting colors
        self.syntax_colors = theme_config["syntax"]
        self.update_syntax_highlighting()

    def update_syntax_highlighting(self):
        for tag, color in self.syntax_colors.items():
            self.text_area.tag_config(tag, foreground=color)
        self.on_key_release()

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
