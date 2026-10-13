# fig08_07.py
import tomllib
from pathlib import Path


def contar_servicios(ruta: Path) -> int:
    datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    return len(datos["servicios"])


def test_cuenta_los_servicios_del_archivo(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(
        '[[servicios]]\nnombre = "catalogo"\n\n[[servicios]]\nnombre = "pagos"\n',
        encoding="utf-8",
    )
    assert contar_servicios(archivo) == 2


def test_cada_prueba_recibe_una_carpeta_vacia(tmp_path: Path) -> None:
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []
