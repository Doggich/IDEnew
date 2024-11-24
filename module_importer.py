import tkinter as tk
from tkinter import messagebox
import subprocess


class ModuleInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Alphabet LibMaster")
        self.root.geometry("300x100")

        self.entry = tk.Entry(self.root, width=30)
        self.entry.pack(pady=10)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.install_button = tk.Button(self.button_frame, text="Install", command=self.import_module)
        self.install_button.pack(side=tk.LEFT, padx=5)

        self.uninstall_button = tk.Button(self.button_frame, text="Uninstall", command=self.remove_module)
        self.uninstall_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.close_window)
        self.exit_button.pack(side=tk.LEFT, padx=5)

    def import_module(self):
        module = self.entry.get()
        if module:
            try:
                subprocess.call(f"pip install {module}", shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error installing module: {e}")
        else:
            messagebox.showinfo("Info", "Please enter a module name")

    def remove_module(self):
        module = self.entry.get()
        if module:
            try:
                subprocess.call(f"pip uninstall -y {module}", shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error uninstalling module: {e}")
        else:
            messagebox.showinfo("Info", "Please enter a module name")

    def close_window(self):
        self.root.destroy()
