from datetime import datetime


class Venta:
    def __init__(self, usuario, producto, fecha=None):
        self.usuario = str(usuario)
        self.producto = str(producto)
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "producto": self.producto,
            "fecha": self.fecha,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["usuario"], d["producto"], d.get("fecha"))
