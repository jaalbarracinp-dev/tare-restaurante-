class Producto:
    def __init__(self,id,nombre,categoria,precio,stock):
        self.id=str(id); self.nombre=str(nombre); self.categoria=str(categoria)
        self.precio=float(precio); self.stock=int(stock)
    def to_dict(self):
        return {"id":self.id,"nombre":self.nombre,"categoria":self.categoria,"precio":self.precio,"stock":self.stock}
    @classmethod
    def from_dict(cls,d):
        return cls(d["id"],d["nombre"],d["categoria"],d["precio"],d["stock"])
