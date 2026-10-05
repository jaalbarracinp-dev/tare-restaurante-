import json
from pathlib import Path
class ArchivoServicio:
    @staticmethod
    def cargar(ruta):
        p=Path(ruta)
        if not p.exists(): return []
        with p.open("r",encoding="utf-8") as f: return json.load(f)
    @staticmethod
    def guardar(ruta,datos):
        p=Path(ruta); p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("w",encoding="utf-8") as f: json.dump(datos,f,indent=4,ensure_ascii=False)
