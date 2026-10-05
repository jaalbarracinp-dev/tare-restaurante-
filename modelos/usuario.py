class Usuario:
    def __init__(self, usuario, contrasena, nombre, rol="Cliente"):
        self.usuario = usuario
        self.contrasena = contrasena
        self.nombre = nombre
        self.rol = rol

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "nombre": self.nombre,
            "rol": self.rol,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["usuario"],
            d.get("contrasena", ""),
            d.get("nombre", ""),
            d.get("rol", "Cliente"),
        )
