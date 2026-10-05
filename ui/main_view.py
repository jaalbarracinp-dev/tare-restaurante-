import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from modelos.producto import Producto
from modelos.usuario import Usuario


class MainView:
    def __init__(self, root, servicio, usuario):
        self.root = root
        self.servicio = servicio
        self.usuario = usuario
        self.assets = Path(__file__).resolve().parent.parent / "assets"

        root.title("Restaurante App - Gestión")
        root.geometry("1100x700")
        root.minsize(950, 620)

        self.vars = [tk.StringVar() for _ in range(5)]
        self.usuario_venta = tk.StringVar()
        self.producto_venta = tk.StringVar()

        self.usuario_form_var = tk.StringVar()
        self.nombre_form_var = tk.StringVar()
        self.contrasena_form_var = tk.StringVar()
        self.rol_form_var = tk.StringVar()
        self.usuario_seleccionado = None

        self.logo = None
        self.iconos = {}
        self._cargar_assets()
        self._ui()

        self.cargar_productos()
        self.cargar_usuarios()
        self.cargar_opciones_venta()
        self.cargar_ventas()

    def _cargar_assets(self):
        try:
            self.logo = tk.PhotoImage(file=str(self.assets / "logo.png"))
            for nombre in ("usuarios", "productos", "ventas"):
                self.iconos[nombre] = tk.PhotoImage(
                    file=str(self.assets / f"icono_{nombre}.png")
                )
        except tk.TclError:
            self.logo = None
            self.iconos = {}

    def _ui(self):
        p = ttk.Frame(self.root, padding=12)
        p.pack(fill="both", expand=True)

        encabezado = ttk.Frame(p)
        encabezado.pack(fill="x", pady=(0, 10))

        if self.logo:
            ttk.Label(encabezado, image=self.logo).pack(side="left", padx=(0, 10))

        ttk.Label(
            encabezado,
            text=f"Restaurante App | Usuario: {self.usuario.nombre} | Rol: {self.usuario.rol}",
            font=("Arial", 16, "bold"),
        ).pack(side="left")

        nb = ttk.Notebook(p)
        nb.pack(fill="both", expand=True)

        pr = ttk.Frame(nb, padding=10)
        ve = ttk.Frame(nb, padding=10)

        nb.add(pr, text="Productos")
        ve_tab = nb.add(ve, text="Ventas")

        self._crear_tab_productos(pr)
        self._crear_tab_ventas(ve)

        # Solo el Administrador dispone de la gestión administrativa de usuarios.
        if self.usuario.rol == "Administrador":
            us = ttk.Frame(nb, padding=10)
            nb.insert(1, us, text="Usuarios")
            self._crear_tab_usuarios(us)

    # -------------------- PRODUCTOS --------------------

    def _crear_tab_productos(self, pr):
        form = ttk.LabelFrame(pr, text="Formulario de producto", padding=10)
        form.pack(fill="x", pady=(0, 10))

        labels = ["ID", "Nombre", "Categoría", "Precio", "Stock"]
        for i, (lab, var) in enumerate(zip(labels, self.vars)):
            ttk.Label(form, text=lab).grid(row=0, column=i, padx=5, sticky="w")
            ttk.Entry(form, textvariable=var, width=18).grid(
                row=1, column=i, padx=5, pady=4
            )

        a = ttk.Frame(form)
        a.grid(row=2, column=0, columnspan=5, pady=8)

        for text, cmd in [
            ("Registrar", self.registrar),
            ("Cargar / Consultar", self.cargar_seleccionado),
            ("Actualizar", self.actualizar),
            ("Eliminar", self.eliminar),
            ("Limpiar", self.limpiar),
        ]:
            ttk.Button(a, text=text, command=cmd).pack(side="left", padx=4)

        tf = ttk.Frame(pr)
        tf.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(
            tf,
            columns=("id", "nombre", "categoria", "precio", "stock"),
            show="headings",
        )

        for c, t, w in [
            ("id", "ID", 90),
            ("nombre", "Nombre", 250),
            ("categoria", "Categoría", 170),
            ("precio", "Precio", 100),
            ("stock", "Stock", 90),
        ]:
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=w)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # -------------------- USUARIOS --------------------

    def _crear_tab_usuarios(self, us):
        ttk.Label(
            us,
            text="Gestión de usuarios",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        form = ttk.LabelFrame(us, text="Formulario de usuario", padding=10)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Usuario").grid(row=0, column=0, padx=6, sticky="w")
        entrada_usuario = ttk.Entry(form, textvariable=self.usuario_form_var, width=22)
        entrada_usuario.grid(row=1, column=0, padx=6, pady=4)

        ttk.Label(form, text="Nombre").grid(row=0, column=1, padx=6, sticky="w")
        entrada_nombre = ttk.Entry(form, textvariable=self.nombre_form_var, width=28)
        entrada_nombre.grid(row=1, column=1, padx=6, pady=4)

        ttk.Label(form, text="Contraseña").grid(row=0, column=2, padx=6, sticky="w")
        entrada_contrasena = ttk.Entry(
            form, textvariable=self.contrasena_form_var, show="*", width=22
        )
        entrada_contrasena.grid(row=1, column=2, padx=6, pady=4)

        ttk.Label(form, text="Rol").grid(row=0, column=3, padx=6, sticky="w")
        self.combo_rol = ttk.Combobox(
            form,
            textvariable=self.rol_form_var,
            values=list(self.servicio.ROLES),
            state="readonly",
            width=18,
        )
        self.combo_rol.grid(row=1, column=3, padx=6, pady=4)
        self.combo_rol.bind("<<ComboboxSelected>>", self.on_rol_selected)

        # <Return> queda asociado a los controles del formulario de usuarios.
        for widget in (entrada_usuario, entrada_nombre, entrada_contrasena, self.combo_rol):
            widget.bind("<Return>", self.on_return_usuario)
            widget.bind("<Escape>", self.on_escape_usuario)

        botones = ttk.Frame(form)
        botones.grid(row=2, column=0, columnspan=4, pady=8)

        ttk.Button(botones, text="Registrar", command=self.registrar_usuario).pack(
            side="left", padx=4
        )
        ttk.Button(botones, text="Actualizar", command=self.actualizar_usuario).pack(
            side="left", padx=4
        )
        ttk.Button(botones, text="Eliminar", command=self.eliminar_usuario).pack(
            side="left", padx=4
        )
        ttk.Button(botones, text="Limpiar", command=self.limpiar_usuario).pack(
            side="left", padx=4
        )

        tfu = ttk.Frame(us)
        tfu.pack(fill="both", expand=True)

        self.tabla_u = ttk.Treeview(
            tfu,
            columns=("usuario", "nombre", "rol"),
            show="headings",
            selectmode="browse",
        )
        for c, t, w in [
            ("usuario", "Usuario", 180),
            ("nombre", "Nombre", 300),
            ("rol", "Rol", 180),
        ]:
            self.tabla_u.heading(c, text=t)
            self.tabla_u.column(c, width=w)

        sb = ttk.Scrollbar(tfu, orient="vertical", command=self.tabla_u.yview)
        self.tabla_u.configure(yscrollcommand=sb.set)
        self.tabla_u.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Evento solicitado: selección de fila -> callback -> servicio -> formulario.
        self.tabla_u.bind("<<TreeviewSelect>>", self.on_usuario_select)

        # Atajos solicitados para el formulario de usuarios.
        self.root.bind("<Escape>", self.on_escape_usuario)

    def usuario_form(self):
        usuario = self.usuario_form_var.get().strip()
        nombre = self.nombre_form_var.get().strip()
        contrasena = self.contrasena_form_var.get()
        rol = self.rol_form_var.get().strip()

        if not usuario or not nombre or not contrasena or not rol:
            raise ValueError("Complete todos los campos del usuario.")

        return Usuario(usuario, contrasena, nombre, rol)

    def cargar_usuarios(self):
        if not hasattr(self, "tabla_u"):
            return

        self.tabla_u.delete(*self.tabla_u.get_children())

        for u in self.servicio.listar_usuarios():
            # No se muestra la contraseña en la tabla.
            self.tabla_u.insert(
                "",
                "end",
                iid=u.usuario,
                values=(u.usuario, u.nombre, u.rol),
            )

    def on_usuario_select(self, event):
        seleccion = self.tabla_u.selection()
        if not seleccion:
            return

        usuario_id = seleccion[0]
        usuario = self.servicio.buscar_usuario(usuario_id)

        if usuario is None:
            return

        self.usuario_seleccionado = usuario.usuario
        self.usuario_form_var.set(usuario.usuario)
        self.nombre_form_var.set(usuario.nombre)
        self.contrasena_form_var.set(usuario.contrasena)
        self.rol_form_var.set(usuario.rol)

    def on_return_usuario(self, event):
        # Reutiliza el método de registro; no duplica la lógica.
        if hasattr(self, "tabla_u") and self.usuario.rol == "Administrador":
            self.registrar_usuario()

    def on_escape_usuario(self, event):
        if hasattr(self, "tabla_u") and self.usuario.rol == "Administrador":
            self.limpiar_usuario()

    def on_rol_selected(self, event):
        # Callback sencillo para evidenciar <<ComboboxSelected>>.
        rol = self.rol_form_var.get()
        self.combo_rol.configure(width=max(18, len(rol) + 4))

    def registrar_usuario(self):
        try:
            nuevo = self.usuario_form()
            self.servicio.registrar_usuario(nuevo)
            self.cargar_usuarios()
            self.cargar_opciones_venta()
            self.limpiar_usuario()
            messagebox.showinfo("Usuarios", "Usuario registrado correctamente.")
        except ValueError as e:
            messagebox.showerror("Registrar usuario", str(e))

    def actualizar_usuario(self):
        try:
            if not self.usuario_seleccionado:
                raise ValueError("Seleccione un usuario en la tabla.")

            actualizado = self.usuario_form()
            self.servicio.actualizar_usuario(
                self.usuario_seleccionado,
                actualizado,
            )

            self.cargar_usuarios()
            self.cargar_opciones_venta()
            self.limpiar_usuario()
            messagebox.showinfo("Usuarios", "Usuario actualizado correctamente.")
        except ValueError as e:
            messagebox.showerror("Actualizar usuario", str(e))

    def eliminar_usuario(self):
        usuario_id = self.usuario_seleccionado or self.usuario_form_var.get().strip()

        if not usuario_id:
            return messagebox.showwarning(
                "Eliminar usuario",
                "Seleccione un usuario en la tabla.",
            )

        if usuario_id == self.usuario.usuario:
            return messagebox.showwarning(
                "Eliminar usuario",
                "La cuenta administrativa actualmente autenticada no puede eliminarse.",
            )

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Desea eliminar al usuario '{usuario_id}'?",
        ):
            return

        try:
            self.servicio.eliminar_usuario(usuario_id, self.usuario.usuario)
            self.cargar_usuarios()
            self.cargar_opciones_venta()
            self.limpiar_usuario()
            messagebox.showinfo("Usuarios", "Usuario eliminado correctamente.")
        except ValueError as e:
            messagebox.showerror("Eliminar usuario", str(e))

    def limpiar_usuario(self):
        self.usuario_seleccionado = None
        self.usuario_form_var.set("")
        self.nombre_form_var.set("")
        self.contrasena_form_var.set("")
        self.rol_form_var.set("")

        if hasattr(self, "tabla_u"):
            for item in self.tabla_u.selection():
                self.tabla_u.selection_remove(item)
            self.tabla_u.focus("")

    # -------------------- VENTAS --------------------

    def _crear_tab_ventas(self, ve):
        formulario_venta = ttk.LabelFrame(
            ve, text="Registrar nueva venta", padding=14
        )
        formulario_venta.pack(fill="x", pady=(0, 12))

        ttk.Label(formulario_venta, text="Usuario").grid(
            row=0, column=0, padx=6, pady=6, sticky="w"
        )
        self.combo_usuario = ttk.Combobox(
            formulario_venta,
            textvariable=self.usuario_venta,
            state="readonly",
            width=34,
        )
        self.combo_usuario.grid(row=1, column=0, padx=6, pady=4)

        ttk.Label(formulario_venta, text="Producto").grid(
            row=0, column=1, padx=6, pady=6, sticky="w"
        )
        self.combo_producto = ttk.Combobox(
            formulario_venta,
            textvariable=self.producto_venta,
            state="readonly",
            width=42,
        )
        self.combo_producto.grid(row=1, column=1, padx=6, pady=4)

        boton = ttk.Button(
            formulario_venta,
            text="Registrar venta",
            image=self.iconos.get("ventas"),
            compound="left",
            command=self.registrar_venta,
        )
        boton.grid(row=1, column=2, padx=12, pady=4)

        ttk.Label(
            ve, text="Ventas registradas", font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(4, 8))

        tfv = ttk.Frame(ve)
        tfv.pack(fill="both", expand=True)

        self.tabla_v = ttk.Treeview(
            tfv,
            columns=("usuario", "producto", "fecha"),
            show="headings",
        )
        for c, t, w in [
            ("usuario", "Usuario", 180),
            ("producto", "Producto", 180),
            ("fecha", "Fecha y hora", 220),
        ]:
            self.tabla_v.heading(c, text=t)
            self.tabla_v.column(c, width=w)

        sbv = ttk.Scrollbar(tfv, orient="vertical", command=self.tabla_v.yview)
        self.tabla_v.configure(yscrollcommand=sbv.set)
        self.tabla_v.pack(side="left", fill="both", expand=True)
        sbv.pack(side="right", fill="y")

    def cargar_opciones_venta(self):
        usuarios = self.servicio.listar_usuarios()
        productos = self.servicio.listar_productos()

        self.mapa_usuarios = {
            f"{u.usuario} - {u.nombre}": u.usuario for u in usuarios
        }
        self.mapa_productos = {
            f"{p.id} - {p.nombre}": p.id for p in productos
        }

        self.combo_usuario["values"] = list(self.mapa_usuarios.keys())
        self.combo_producto["values"] = list(self.mapa_productos.keys())

        self.usuario_venta.set("")
        self.producto_venta.set("")

    def cargar_ventas(self):
        self.tabla_v.delete(*self.tabla_v.get_children())
        productos = {
            p.id: p.nombre for p in self.servicio.listar_productos()
        }

        for v in self.servicio.listar_ventas():
            self.tabla_v.insert(
                "",
                "end",
                values=(
                    v.usuario,
                    f"{v.producto} - {productos.get(v.producto, 'Producto no disponible')}",
                    v.fecha,
                ),
            )

    def registrar_venta(self):
        try:
            usuario_id = self.mapa_usuarios.get(self.usuario_venta.get())
            producto_id = self.mapa_productos.get(self.producto_venta.get())

            venta = self.servicio.registrar_venta(usuario_id, producto_id)
            self.cargar_ventas()
            self.usuario_venta.set("")
            self.producto_venta.set("")

            messagebox.showinfo(
                "Venta registrada",
                f"Venta registrada correctamente.\nFecha: {venta.fecha}",
            )
        except ValueError as e:
            messagebox.showerror("Registrar venta", str(e))

    # -------------------- PRODUCTOS: OPERACIONES --------------------

    def producto_form(self):
        try:
            id, n, c, pr, st = [v.get().strip() for v in self.vars]
            if not all([id, n, c, pr, st]):
                raise ValueError("Complete todos los campos.")
            return Producto(id, n, c, float(pr), int(st))
        except ValueError as e:
            raise ValueError(f"Datos inválidos: {e}")

    def cargar_productos(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.servicio.listar_productos():
            self.tabla.insert(
                "",
                "end",
                values=(p.id, p.nombre, p.categoria, f"{p.precio:.2f}", p.stock),
            )

    def cargar_seleccionado(self):
        id = self.vars[0].get().strip()

        if not id and self.tabla.selection():
            id = self.tabla.item(self.tabla.selection()[0], "values")[0]

        p = self.servicio.buscar_producto(id)

        if not p:
            return messagebox.showerror("Consultar", "Producto no encontrado.")

        for v, x in zip(
            self.vars,
            [p.id, p.nombre, p.categoria, p.precio, p.stock],
        ):
            v.set(str(x))

    def registrar(self):
        try:
            self.servicio.registrar_producto(self.producto_form())
            self.cargar_productos()
            self.cargar_opciones_venta()
            self.limpiar()
            messagebox.showinfo("Registrar", "Producto registrado.")
        except ValueError as e:
            messagebox.showerror("Registrar", str(e))

    def actualizar(self):
        try:
            self.servicio.actualizar_producto(self.producto_form())
            self.cargar_productos()
            self.cargar_opciones_venta()
            messagebox.showinfo("Actualizar", "Producto actualizado.")
        except ValueError as e:
            messagebox.showerror("Actualizar", str(e))

    def eliminar(self):
        id = self.vars[0].get().strip()

        if not id and self.tabla.selection():
            id = self.tabla.item(self.tabla.selection()[0], "values")[0]

        if not id:
            return messagebox.showwarning(
                "Eliminar", "Indique un ID o seleccione un producto."
            )

        if messagebox.askyesno("Eliminar", f"¿Eliminar {id}?"):
            try:
                self.servicio.eliminar_producto(id)
                self.cargar_productos()
                self.cargar_opciones_venta()
                self.limpiar()
            except ValueError as e:
                messagebox.showerror("Eliminar", str(e))

    def limpiar(self):
        for v in self.vars:
            v.set("")
