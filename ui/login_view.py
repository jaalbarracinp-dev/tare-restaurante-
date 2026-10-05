import tkinter as tk
from tkinter import ttk, messagebox


class LoginView:
    def __init__(self, root, servicio, on_login):
        self.root = root
        self.servicio = servicio
        self.on_login = on_login

        root.title("Restaurante App - Login")
        root.geometry("420x300")
        root.resizable(False, False)

        f = ttk.Frame(root, padding=30)
        f.pack(fill="both", expand=True)

        ttk.Label(
            f, text="RESTAURANTE APP", font=("Arial", 18, "bold")
        ).pack(pady=(10, 20))

        ttk.Label(f, text="Usuario").pack(anchor="w")
        self.usuario = ttk.Entry(f)
        self.usuario.pack(fill="x", pady=(0, 12))

        ttk.Label(f, text="Contraseña").pack(anchor="w")
        self.contrasena = ttk.Entry(f, show="*")
        self.contrasena.pack(fill="x", pady=(0, 18))

        ttk.Button(f, text="Ingresar", command=self.ingresar).pack(fill="x")
        ttk.Label(
            f, text="Prueba: admin / 1234", foreground="gray"
        ).pack(pady=12)

        self.contrasena.bind("<Return>", self.ingresar)

    def ingresar(self, event=None):
        u = self.servicio.validar_login(
            self.usuario.get().strip(),
            self.contrasena.get(),
        )

        if u:
            self.root.destroy()
            self.on_login(u)
        else:
            messagebox.showerror(
                "Acceso", "Usuario o contraseña incorrectos."
            )
