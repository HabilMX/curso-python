"""url-sembrada.py — la prueba de la URL sembrada contra UN revisor del curso.

Por qué existe: el revisor lee direcciones de servicios.toml, y una dirección puede
traer secretos: usuario y clave (http://usuario:clave@...), un token en la consulta
(?token=...) o un fragmento (#...). La regla del curso:
  (a) una URL con usuario o clave se rechaza al cargar, con un mensaje propio que no
      repite la URL;
  (b) ningún reporte (tabla ni JSON), error ni registro repite la URL completa: el JSON
      la lleva redactada, sin usuario, clave, consulta ni fragmento.

Uso:  python herramientas/url-sembrada.py <carpeta> <lección>
  - lección 6: <carpeta> es programas/06-*/fig06_18 y se corren revisor.py y ver_json.py;
  - lecciones 7 a 11: <carpeta> es la del proyecto, y el paquete `revisor` de esa
    carpeta tiene que estar instalado en el Python con que se corre esta prueba.
Sale 0 si todas las comprobaciones pasan y 1 si alguna falla. Imprime cada una.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SEMBRADA = "http://usuario:clave@127.0.0.1:1/estado?token=SECRETO#x"
CON_CONSULTA = "http://127.0.0.1:1/estado?token=SECRETO#x"
REDACTADA = "http://127.0.0.1:1/estado"
# Pedazos que solo aparecen si se repite la URL (el mensaje de rechazo dice
# «usuario ni clave», que no contiene ninguno).
SECRETOS = ["usuario:", ":clave", "clave@", "SECRETO", "token=", "#x"]

carpeta = Path(sys.argv[1]).resolve()
leccion = int(sys.argv[2])
fallas = 0
cuentas = 0


def comprobar(nombre: str, ok: bool, detalle: str = "") -> None:
    global fallas, cuentas
    cuentas += 1
    if ok:
        print(f"  ok    {nombre}")
    else:
        fallas += 1
        print(f"  FALLA {nombre}{': ' + detalle if detalle else ''}")


def toml(url: str) -> str:
    return f'[[servicios]]\nnombre = "sembrado"\nurl = "{url}"\ntimeout_ms = 2000\n'


def correr(comando: list[str], trabajo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        comando, cwd=trabajo, capture_output=True, text=True, timeout=60, check=False
    )


def sin_secretos(texto: str) -> list[str]:
    return [s for s in SECRETOS if s in texto]


def url_del_json(texto: str) -> str | None:
    try:
        return str(json.loads(texto)["servicios"][0]["url"])
    except (ValueError, KeyError, IndexError, TypeError):
        return None


with tempfile.TemporaryDirectory() as temporal:
    trabajo = Path(temporal)
    if leccion == 6:
        for archivo in carpeta.glob("*.py"):
            shutil.copy(archivo, trabajo)
        config = trabajo / "servicios.toml"
        corridas = {
            "tabla": [sys.executable, "revisor.py"],
            "json": [sys.executable, "ver_json.py"],
        }
    else:
        config = trabajo / "servicios.toml"
        base = [sys.executable, "-m", "revisor", "--config", str(config)]
        corridas = {"tabla": base, "json": [*base, "--formato", "json"]}
        if leccion >= 11:
            corridas["tabla --verbose"] = [*base, "--verbose"]
            corridas["json --verbose"] = [*base, "--formato", "json", "--verbose"]

    print(f"lección {leccion}: {carpeta.name}")

    # (a) La URL con usuario y clave se rechaza al cargar y nada repite sus secretos.
    config.write_text(toml(SEMBRADA), encoding="utf-8")
    for nombre, comando in corridas.items():
        r = correr(comando, trabajo)
        salida = r.stdout + r.stderr
        comprobar(
            f"(a) {nombre}: rechaza la URL con usuario y clave",
            "usuario ni clave" in salida and url_del_json(r.stdout) is None,
            salida.strip().splitlines()[-1] if salida.strip() else "sin salida",
        )
        if leccion >= 7:
            comprobar(
                f"(a) {nombre}: sale con el código 2",
                r.returncode == 2,
                f"salió con {r.returncode}",
            )
        filtrados = sin_secretos(salida)
        comprobar(
            f"(a) {nombre}: no repite la URL",
            not filtrados,
            f"repite {', '.join(filtrados)}",
        )

    # (b) Una URL sin usuario pero con consulta y fragmento: el reporte no los repite.
    config.write_text(toml(CON_CONSULTA), encoding="utf-8")
    for nombre, comando in corridas.items():
        r = correr(comando, trabajo)
        salida = r.stdout + r.stderr
        filtrados = sin_secretos(salida)
        comprobar(
            f"(b) {nombre}: no repite consulta ni fragmento",
            not filtrados,
            f"repite {', '.join(filtrados)}",
        )
        if nombre.startswith("json"):
            url = url_del_json(r.stdout)
            comprobar(
                f"(b) {nombre}: el JSON trae la URL redactada",
                url == REDACTADA,
                f"trae {url!r}",
            )

print(f"  {cuentas - fallas} de {cuentas} comprobaciones en verde")
sys.exit(1 if fallas else 0)
