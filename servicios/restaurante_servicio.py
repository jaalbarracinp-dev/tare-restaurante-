from pathlib import Path
from .archivo_servicio import ArchivoServicio
from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta

BASE = Path(__file__).resolve().parent.parent
PRODUCTOS = BASE / "datos" / "productos.json"
USUARIOS = BASE / "datos" / "usuarios.json"
VENTAS = BASE / "datos" / "ventas.json"


class RestauranteServicio:
    ROLES = ("Administrador", "Empleado", "Cliente")

    def validar_login(self, usuario, contrasena):
        for d in ArchivoServicio.cargar(USUARIOS):
            u = Usuario.from_dict(d)
            if u.usuario == usuario and u.contrasena == contrasena:
                return u
        return None

    # -------------------- USUARIOS --------------------

    def listar_usuarios(self):
        return [Usuario.from_dict(x) for x in ArchivoServicio.cargar(USUARIOS)]

    def buscar_usuario(self, usuario):
        usuario = str(usuario).strip()
        return next((u for u in self.listar_usuarios() if u.usuario == usuario), None)

    def registrar_usuario(self, u):
        usuarios = self.listar_usuarios()
        if not u.usuario.strip():
            raise ValueError("El usuario es obligatorio.")
        if not u.nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not u.contrasena.strip():
            raise ValueError("La contraseña es obligatoria.")
        if u.rol not in self.ROLES:
            raise ValueError("Seleccione un rol válido.")
        if self.buscar_usuario(u.usuario):
            raise ValueError("Ya existe un usuario con ese identificador.")

        usuarios.append(u)
        self._guardar_usuarios(usuarios)

    def actualizar_usuario(self, usuario_original, u):
        usuarios = self.listar_usuarios()
        usuario_original = str(usuario_original).strip()

        if not usuario_original:
            raise ValueError("Seleccione un usuario.")
        if not u.usuario.strip():
            raise ValueError("El usuario es obligatorio.")
        if not u.nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not u.contrasena.strip():
            raise ValueError("La contraseña es obligatoria.")
        if u.rol not in self.ROLES:
            raise ValueError("Seleccione un rol válido.")

        indice = next((i for i, x in enumerate(usuarios) if x.usuario == usuario_original), None)
        if indice is None:
            raise ValueError("Usuario no encontrado.")

        if u.usuario != usuario_original and self.buscar_usuario(u.usuario):
            raise ValueError("Ya existe otro usuario con ese identificador.")

        usuarios[indice] = u
        self._guardar_usuarios(usuarios)

    def eliminar_usuario(self, usuario, usuario_actual):
        usuario = str(usuario).strip()
        usuario_actual = str(usuario_actual).strip()

        if not usuario:
            raise ValueError("Seleccione un usuario.")
        if usuario == usuario_actual:
            raise ValueError("No puede eliminar la cuenta administrativa actualmente autenticada.")

        usuarios = self.listar_usuarios()
        nuevos = [u for u in usuarios if u.usuario != usuario]

        if len(usuarios) == len(nuevos):
            raise ValueError("Usuario no encontrado.")

        self._guardar_usuarios(nuevos)

    def _guardar_usuarios(self, usuarios):
        ArchivoServicio.guardar(USUARIOS, [u.to_dict() for u in usuarios])

    # -------------------- PRODUCTOS --------------------

    def listar_productos(self):
        return [Producto.from_dict(x) for x in ArchivoServicio.cargar(PRODUCTOS)]

    def buscar_producto(self, id):
        return next((p for p in self.listar_productos() if p.id == str(id)), None)

    def registrar_producto(self, p):
        ps = self.listar_productos()
        if any(x.id == p.id for x in ps):
            raise ValueError("Ya existe un producto con ese ID.")
        if not p.nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if p.precio < 0 or p.stock < 0:
            raise ValueError("Precio y stock no pueden ser negativos.")
        ps.append(p)
        ArchivoServicio.guardar(PRODUCTOS, [x.to_dict() for x in ps])

    def actualizar_producto(self, p):
        ps = self.listar_productos()
        for i, x in enumerate(ps):
            if x.id == p.id:
                ps[i] = p
                ArchivoServicio.guardar(PRODUCTOS, [a.to_dict() for a in ps])
                return
        raise ValueError("Producto no encontrado.")

    def eliminar_producto(self, id):
        ps = self.listar_productos()
        nuevos = [p for p in ps if p.id != str(id)]
        if len(ps) == len(nuevos):
            raise ValueError("Producto no encontrado.")
        ArchivoServicio.guardar(PRODUCTOS, [p.to_dict() for p in nuevos])

    # -------------------- VENTAS --------------------

    def listar_ventas(self):
        return [Venta.from_dict(x) for x in ArchivoServicio.cargar(VENTAS)]

    def registrar_venta(self, usuario_id, producto_id):
        usuario_id = str(usuario_id).strip()
        producto_id = str(producto_id).strip()
        if not usuario_id or not producto_id:
            raise ValueError("Debe seleccionar un usuario y un producto.")

        usuario = self.buscar_usuario(usuario_id)
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe.")

        producto = self.buscar_producto(producto_id)
        if producto is None:
            raise ValueError("El producto seleccionado no existe.")

        ventas = self.listar_ventas()
        venta = Venta(usuario.usuario, producto.id)
        ventas.append(venta)
        ArchivoServicio.guardar(VENTAS, [v.to_dict() for v in ventas])
        return venta
