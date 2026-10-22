# Lesson 11 — The finished program

**Time:** 2 × 90 min (the first session runs to the end of 11.2; the second starts at 11.3)

**What you build:** the complete `revisor`, version 1.0.0, installed on your computer as one more command

**What you learn:** the report as a contract (a table with calculated width and a tested JSON); `logging` and `--verbose`; exit codes reviewed; a security review (the address someone else writes, `subprocess` without `shell=True`, `secrets`, neither `eval` nor `pickle`); building the package and installing it with `pipx`

**Where you come from.** You bring the `revisor` from [Lesson 10](10-concurrencia-pruebas-sin-red.md): a package that reads its configuration, queries the services at once, with a timeout and a cap on simultaneous ones, and that has 27 tests that do not touch the network. It works, and it works well. But it still lives in your folder: it is run with `python -m revisor` from where the code is, and its table has a defect you have not seen because all your services have short names: the `SERVICIO` column is always 12 characters wide, and a service called `notificaciones-de-clientes` overflows it. Today all that is closed. You work in your `~/curso-python/revisor/` folder, with the virtual environment activated and, for the last part, with `pipx` installed.

**What this lesson does not do.** It brings almost no new Python concepts: it is the lesson in which you **put together** what you already know and check that it is finished. What is new is a matter of craft: `logging`, which is the language a program uses to say what it is doing without making a mess of its report; the final packaging; and the review of the four security habits the course has been sowing. The final step is not one more lesson: it is the list of seven checks with which `en/README.md` defines when the course is finished, and this lesson goes through them **one by one**, with the real output of each.

## By the end you will be able to

- Explain why a report that another program reads is a contract, and test that contract with a test that turns red if someone renames a field.
- Calculate a column's width from the data and align a table even if a name is long.
- Use `logging` instead of `print` for what the program says about itself, and explain why the report goes to standard output and the log to standard error.
- Say, for each exit code (0, 1 and 2), what the `revisor` promises to whoever calls it from a script.
- Name and avoid four frequent security risks: an address that someone else writes, `subprocess` with `shell=True`, `eval` and `pickle` with outside data, and “random” numbers for secrets.
- Build the package as an installable file (`.whl`), install it with `pipx` and run it from any folder.
- Check, with one command and one output for each, that the `revisor` meets the seven points of “How you know you are done.”

## The why before the how

When someone says “I finished the program,” there are at least three things they may mean. That it **works on their computer**, today, with their data. That **another person can install it and use it** without asking them for help. Or that **it can be trusted**: that if something goes wrong it says so clearly, that if something changes a test finds out before a user does, that it does not hang, that it does not open doors it should not. The three are different, and it is very common to deliver the first believing it is the third.

The course began with you, sitting in front of a `print("revisor: todavía no revisa nada")`, and ends in this lesson because the `revisor` now has to be able to fend for itself. To decide whether it achieved that, the impression that “it's done now” is not enough: the impression is the first thing to fail. That is why the syllabus defines the end with **seven checks** that can be run, not with an opinion. Here they are, and you will go through them one by one at the end of the lesson:

1. `pytest` ends green and the report says how many tests ran.
2. `ruff check`, `ruff format --check` and `mypy` report nothing.
3. It checks 20 services at once in a time close to that of the slowest, not to that of the sum.
4. A service that is down, slow or answers garbage does not take down the report.
5. No request can wait forever.
6. It runs the same on Python 3.14 and on the 3.12 of your Mint.
7. It installs with `pipx install` and `revisor --help` works from another folder; it exits with 0 if everything is up and with 1 if not.

Of those seven, your `revisor` already meets almost all and you may not know it. What is missing is three things: **measuring it** (nobody trusts “I think so”), **leaving it in a state that another person can use** (the report, the log, the packaging) and **reviewing the security habits** so that point 4, “it does not take down the report,” is not only a matter of accidental failures but also of hostile inputs. The four parts of the lesson follow that order.

## The concepts

### 11.1 The report as a contract

#### 11.1.1 Who reads your report

Until now you were the one reading the report, in a terminal. But a command-line program that exits with code 0 or 1 is made for **another program** to call it: an on-call script that runs every five minutes, a continuous integration task that decides whether to let a deployment through. That other program does not *read* the report as you do: it **interprets** it. It looks for a field with a name and expects a type. If tomorrow someone renames `caido` to `caidos` in the JSON, for a person it is a spelling change; for the script it is a field that disappeared, and without a test to catch it nobody finds out until the three-in-the-morning alarm does not go off.

That is called a **contract**: the way the program promises to deliver its result, and which others can take as true. The `revisor` has two contracts. The **JSON** (defined in Lesson 6) is for machines: its fields and types are fixed, and the `tiempo_ms` of a service that did not answer is `null`, not `0` nor a text. And the **exit code** (defined in Lesson 7) is for the shell and for any script: `0` if all services are `ARRIBA`; `1` if any is `LENTO` or `CAIDO`; `2` if the usage is invalid or the configuration is no good. The table, on the other hand, is for people, and can change its look without warning anyone.

Today what was implicit is made explicit: a **test that describes the whole JSON** is written. And a defect of the table is fixed.

#### 11.1.2 A column's width is calculated, not guessed

See the defect before fixing it. Lesson 2 fixed the width of the first column at 12 characters with `f"{nombre:<12}"`, and with the sample names (the longest, `inventario`, has 10) it looked perfect. With a long name, the text spills out of its column and pushes all the others. The solution is to make the width **depend on the data**: the longest of the names plus two spaces of breathing room, with a minimum of 12 so that short tables look as they always did.

There is a novelty of syntax. An f-string lets you put the width **inside** the specification, with another pair of braces: `f"{nombre:<{ancho}}"` means “align `nombre` to the left in a field of `ancho` characters,” where `ancho` is a variable. It is the same as `:<12`, with the 12 replaced by a variable. See how `formato.py` turns out in full:

```python
# fig11_05/src/revisor/formato.py
import json

from revisor.modelo import Estado, Resultado

ANCHO_MINIMO = 12


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado(ancho: int = ANCHO_MINIMO) -> str:
    return f"{'SERVICIO':<{ancho}}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(resultado: Resultado, ancho: int = ANCHO_MINIMO) -> str:
    nombre = resultado.servicio.nombre
    estado = resultado.estado.value
    tiempo = formatear_tiempo(resultado.tiempo_ms)
    return f"{nombre:<{ancho}}{estado:<10}{tiempo:>6}  {resultado.detalle}"


def ancho_servicio(resultados: list[Resultado]) -> int:
    mas_largo = max([len(r.servicio.nombre) for r in resultados], default=0)
    return max(ANCHO_MINIMO, mas_largo + 2)


def contar(cantidad: int, palabra: str) -> str:
    if cantidad == 1:
        return f"{cantidad} {palabra}"
    return f"{cantidad} {palabra}s"


def resumen(resultados: list[Resultado]) -> str:
    total = len(resultados)
    arriba = len([r for r in resultados if r.estado == Estado.ARRIBA])
    lentos = len([r for r in resultados if r.estado == Estado.LENTO])
    caidos = len([r for r in resultados if r.estado == Estado.CAIDO])
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    partes = [
        contar(total, "servicio"),
        f"{arriba} arriba",
        contar(lentos, "lento"),
        contar(caidos, "caído"),
        f"promedio {formatear_tiempo(promedio_ms)}",
    ]
    return " · ".join(partes)


def tabla(resultados: list[Resultado]) -> str:
    ancho = ancho_servicio(resultados)
    renglones = [encabezado(ancho)]
    renglones += [linea(resultado, ancho) for resultado in resultados]
    renglones += ["", resumen(resultados)]
    return "\n".join(renglones)


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": r.servicio.url,
                "estado": r.estado.value,
                "tiempo_ms": r.tiempo_ms,
                "detalle": r.detalle,
            }
            for r in resultados
        ],
        "resumen": {
            "total": len(resultados),
            "arriba": len([r for r in resultados if r.estado == Estado.ARRIBA]),
            "lento": len([r for r in resultados if r.estado == Estado.LENTO]),
            "caido": len([r for r in resultados if r.estado == Estado.CAIDO]),
            "promedio_ms": promedio_ms,
        },
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)
```

Three new or changed functions. `ancho_servicio` calculates the width: a comprehension takes the length of each name, `max(..., default=0)` returns the greatest (the `default=0` is what `max` returns if the list is empty; without it, `max([])` raises `ValueError`), and two are added. `max(ANCHO_MINIMO, ...)` imposes the minimum. `encabezado` and `linea` receive an `ancho` with default value `ANCHO_MINIMO`; this way, all code that called them without a width (your tests from Lesson 8, for example) keeps working unchanged. And `tabla` puts it all together: it calculates the width **once**, builds the header, one line per result, a blank line and the summary, and joins them with line breaks. (`renglones += [...]` adds to the end of the list all the elements of the other one, like several `append`s in a row; and `"\n".join(...)` is the `join` from Lesson 4 with the line break as the separator.) With the four canonical services, the longest name is 10, `10 + 2 = 12` and the calculated width is 12: the table comes out **identical** to the one you had, byte for byte. It only changes when it needs to change.

#### 11.1.3 The JSON as a contract, tested

The second change is a test. Read it whole: it is not short, and its length is the point.

```python
# fig11_05/tests/test_formato.py
import json

import pytest

from revisor.formato import formatear_tiempo, reporte_a_json, tabla
from revisor.modelo import Estado, Resultado, Servicio


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [(None, "—"), (87, "87ms"), (999, "999ms"), (2300, "2.3s")],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado


def servicio(nombre: str) -> Servicio:
    return Servicio(nombre, f"https://{nombre}.example")


CANONICOS = [
    Resultado(servicio("catalogo"), Estado.ARRIBA, 142, "200"),
    Resultado(servicio("inventario"), Estado.LENTO, 2300, "200"),
    Resultado(servicio("pagos"), Estado.ARRIBA, 87, "200"),
    Resultado(servicio("reportes"), Estado.CAIDO, None, "sin conexión"),
]


def test_el_json_es_un_contrato() -> None:
    esperado = {
        "servicios": [
            {
                "nombre": "catalogo",
                "url": "https://catalogo.example",
                "estado": "ARRIBA",
                "tiempo_ms": 142,
                "detalle": "200",
            },
            {
                "nombre": "inventario",
                "url": "https://inventario.example",
                "estado": "LENTO",
                "tiempo_ms": 2300,
                "detalle": "200",
            },
            {
                "nombre": "pagos",
                "url": "https://pagos.example",
                "estado": "ARRIBA",
                "tiempo_ms": 87,
                "detalle": "200",
            },
            {
                "nombre": "reportes",
                "url": "https://reportes.example",
                "estado": "CAIDO",
                "tiempo_ms": None,
                "detalle": "sin conexión",
            },
        ],
        "resumen": {
            "total": 4,
            "arriba": 2,
            "lento": 1,
            "caido": 1,
            "promedio_ms": 843,
        },
    }
    assert json.loads(reporte_a_json(CANONICOS)) == esperado


def test_la_tabla_se_alinea_con_un_nombre_largo() -> None:
    largo = Resultado(servicio("notificaciones-de-clientes"), Estado.ARRIBA, 50, "200")
    lineas = tabla([*CANONICOS, largo]).splitlines()
    ancho = len("notificaciones-de-clientes") + 2
    assert lineas[0].index("ESTADO") == ancho
    for renglon in lineas[1:6]:
        assert renglon[ancho : ancho + 6] in {"ARRIBA", "LENTO ", "CAIDO "}
```

`CANONICOS` are the four canonical results, built by hand in the test; **they come neither from the network nor from the lab server**. `test_el_json_es_un_contrato` (“the JSON is a contract”) writes the expected JSON in full, field by field, as a dictionary, and compares it with `json.loads(reporte_a_json(CANONICOS))`. There are two decisions that matter. The first: the test compares **what the JSON means** (the dictionary that comes out of `json.loads`) and not the **text** (the spaces and the order of the lines), because a script that interprets JSON does not care how many spaces there are and cares a lot which the fields are. The second: the test includes the awkward case, `reportes` with `"tiempo_ms": None` (which in JSON is `null`), and the `promedio_ms` of 843. If someone changes the `null` for `0`, or removes a field, or changes the rounding of the average, the test turns red.

The second new test, `test_la_tabla_se_alinea_con_un_nombre_largo` (“the table aligns with a long name”), adds to the four canonical ones a service with a 26-character name (`[*CANONICOS, largo]` builds a new list with the elements of `CANONICOS`, which the asterisk “unpacks” one by one, and `largo` at the end, without touching `CANONICOS`) and checks two things: that the word `ESTADO` in the header starts at column 28 (26 plus the 2 of breathing room) and that in each data line, at that same column, there is a valid status. For the first it uses `.index(...)`, a text method that looks for where a piece begins inside the text and returns its position, counting from 0 like list indexes: `lineas[0].index("ESTADO")` is the column where `ESTADO` starts in the header (if it did not find it, it would fail with `ValueError`). That `renglon[ancho : ancho + 6]` is a slice: the `[inicio:fin]` syntax takes the characters from position `inicio` up to the one before `fin`, so here they are the six that start at the status column, which is what `"ARRIBA"` measures. The `in {"ARRIBA", "LENTO ", "CAIDO "}` has a trailing space in `"LENTO "` and `"CAIDO "` because those statuses are five characters long and the slice takes six.

In a test like this it is worth asking whether it meets the bar from Lesson 8: does it turn red if what it claims to test is broken? Exercise 2 asks you to break the JSON on purpose and check it.

### 11.2 `logging`: what the program says about itself

#### 11.2.1 Why not `print`

The report is **what the program produces**. But a program also has things to say about **its own work**: “I read 4 services,” “the `pagos` service answered in 87 ms.” That is information for whoever is investigating something odd, not for whoever reads the report. If those messages are printed with `print` next to the report, they get mixed with it: the script that reads the JSON finds diagnostic lines in the middle and can no longer interpret it.

The Unix world solved this decades ago with two channels: the **standard output** (*stdout*) is for the program's result, and the **standard error** (*stderr*) is for everything else the program has to say about itself. You already use them: the report goes through the first, the `error de configuración: ...` goes through the second (Lesson 7). The standard library's [`logging`](https://docs.python.org/3/library/logging.html) module is the orderly way to write on the second channel, with an advantage over `print`: each message has a **level** of importance, and you decide from which level you want to hear them, without touching the code that writes them.

#### 11.2.2 The levels and a first program

The levels, from least to most serious: `DEBUG` (fine detail, for whoever debugs), `INFO` (the program is advancing), `WARNING` (something odd, but it goes on), `ERROR` (something failed) and `CRITICAL`. By default, `logging` only shows from `WARNING` up. A **logger** is the object you talk to, and it is requested by name: `logging.getLogger("demo")`. This figure shows it all together:

```python
# fig11_01.py
import logging
import sys

logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
registro = logging.getLogger("demo")

print("este renglón es el reporte: va a la salida estándar", flush=True)
registro.debug("detalle fino: nadie lo ve con el nivel por omisión")
registro.warning("aviso: %s tardó %s ms", "inventario", 2300)
registro.setLevel(logging.DEBUG)
registro.debug("ahora sí aparece, porque subí el detalle")
```

```text
$ python fig11_01.py
este renglón es el reporte: va a la salida estándar
WARNING demo: aviso: inventario tardó 2300 ms
DEBUG demo: ahora sí aparece, porque subí el detalle
```

Line by line. `logging.basicConfig(stream=sys.stderr, format=...)` does the minimal configuration: that messages go to `sys.stderr` (the error output) and with the format `LEVEL name: message`. `registro.debug(...)` writes a message of level `DEBUG`, and it does not appear, because the default level is `WARNING`: that message is **kept in the code but turned off**, which is the beauty of it. `registro.warning("aviso: %s tardó %s ms", "inventario", 2300)` does appear. Notice how it is written: the message carries `%s` placeholders and the values go **separately**, as arguments. It is the old `%` string format (`"%s" % x`), which the course uses nowhere else; here you do not apply it: `logging` applies it inside, putting the message and the values together, and [its documentation](https://docs.python.org/3/howto/logging.html#logging-variable-data) asks for it this way. The values are passed separately so that `logging` only builds the text **if the message is going to be emitted**; with an `f"..."` the text would always be built, even if the level is off, and in a program that logs thousands of lines that difference counts. And `registro.setLevel(logging.DEBUG)` lowers the level, so that the last `debug` does appear. The program printed the report with `print(..., flush=True)`; the `flush=True` only forces the text out at that moment, so that the order of the documented output is the same one you see in the terminal.

A design warning, which comes from [the official guide](https://docs.python.org/3/howto/logging.html): the code of a **library** (or of a module of the package) never configures `logging`; it only asks for its logger and writes. The one that configures is the **main program**, which is the one that knows where the messages should go. That is why, in the `revisor`, `basicConfig` lives in `cli.py` and not in `revision.py`.

#### 11.2.3 `--verbose` in the `revisor`

The `revisor` records, at `DEBUG` level, the result of each service, and a `--verbose` option turns it on. `revision.py` asks for the `"revisor"` logger at the start, and its `revisar` function is now a wrapper: it calls `_consultar` (the usual body, which did not change) and records the result before returning it.

```python
# fig11_05/src/revisor/revision.py
import asyncio
import logging
import time

import httpx

from revisor.formato import formatear_tiempo
from revisor.modelo import Estado, Resultado, Servicio, clasificar

registro = logging.getLogger("revisor")


async def _consultar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(servicio.timeout_ms / 1000):
            respuesta = await cliente.get(servicio.url, timeout=limite)
    except (httpx.TimeoutException, TimeoutError):
        return Resultado(servicio, Estado.CAIDO, None, "tiempo agotado")
    except httpx.ConnectError:
        return Resultado(servicio, Estado.CAIDO, None, "sin conexión")
    except httpx.HTTPError:
        return Resultado(servicio, Estado.CAIDO, None, "error de red")
    except (httpx.InvalidURL, ValueError):
        return Resultado(servicio, Estado.CAIDO, None, "dirección inválida")
    tiempo_ms = round((time.perf_counter() - inicio) * 1000)
    estado = clasificar(respuesta.status_code, tiempo_ms)
    return Resultado(servicio, estado, tiempo_ms, str(respuesta.status_code))


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    resultado = await _consultar(cliente, servicio)
    registro.debug(
        "%s: %s, %s, %s",
        servicio.nombre,
        resultado.estado.value,
        formatear_tiempo(resultado.tiempo_ms),
        resultado.detalle,
    )
    return resultado


async def _revisar_con_limite(
    semaforo: asyncio.Semaphore, cliente: httpx.AsyncClient, servicio: Servicio
) -> Resultado:
    async with semaforo:
        return await revisar(cliente, servicio)


async def revisar_todos(
    servicios: list[Servicio],
    limite: int = 10,
    transporte: httpx.AsyncBaseTransport | None = None,
) -> list[Resultado]:
    if limite < 1:
        raise ValueError("el límite debe ser al menos 1")
    semaforo = asyncio.Semaphore(limite)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        async with asyncio.TaskGroup() as grupo:
            tareas = [
                grupo.create_task(_revisar_con_limite(semaforo, cliente, servicio))
                for servicio in servicios
            ]
    return [tarea.result() for tarea in tareas]
```

Notice the separation: `_consultar` makes the query; `revisar` makes it and **counts** it. That way the logging is in a single place and not repeated in each `return`. In `cli.py`, three changes: the `--verbose` option (with `action="store_true"`, which means “if it appears, it is `True`; if not, `False`,” without waiting for a value), a `configurar_logging` function and the call to `tabla`:

```python
# fig11_05/src/revisor/cli.py
import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import reporte_a_json, tabla
from revisor.modelo import Estado
from revisor.revision import revisar_todos


def entero_positivo(texto: str) -> int:
    try:
        numero = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{texto!r} no es un entero") from None
    if numero < 1:
        raise argparse.ArgumentTypeError("debe ser al menos 1")
    return numero


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="revisor",
        description="Revisa el estado de una lista de servicios.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("servicios.toml"),
        help="archivo TOML con la lista de servicios (por omisión: servicios.toml)",
    )
    parser.add_argument(
        "--formato",
        choices=["tabla", "json"],
        default="tabla",
        help="forma del reporte (por omisión: tabla)",
    )
    parser.add_argument(
        "--concurrencia",
        type=entero_positivo,
        default=10,
        help="cuántos servicios se consultan a la vez (por omisión: 10)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"revisor {version('revisor')}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="escribe en la salida de error el detalle de cada revisión",
    )
    return parser


def configurar_logging(verbose: bool) -> None:
    logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    nivel = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger("revisor").setLevel(nivel)


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)
    configurar_logging(argumentos.verbose)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
    if argumentos.formato == "json":
        print(reporte_a_json(resultados))
    else:
        print(tabla(resultados))

    problemas = [r for r in resultados if r.estado is not Estado.ARRIBA]
    if len(problemas) == 0:
        return 0
    return 1
```

`configurar_logging` does three things. `basicConfig` connects the log to `sys.stderr`. The line `nivel = logging.DEBUG if verbose else logging.WARNING` is a **conditional expression**, an `if`/`else` that fits on one line and that **gives a value**: it reads “`logging.DEBUG` if `verbose` is true; if not, `logging.WARNING`,” and is equivalent to a four-line `if`/`else` that assigns `nivel` in each branch. And `logging.getLogger("revisor").setLevel(nivel)` sets the level **only on the `revisor`'s logger**: `DEBUG` if they asked for `--verbose`, `WARNING` if not. That distinction matters: if you had set level `DEBUG` on **everyone's** logger (the root), `httpx` and the library it uses underneath would write hundreds of lines of their own, and yours would get lost among them. In addition, each option now carries its help text in Spanish (`help=...`), because the seventh check asks that `revisor --help` be useful. (The texts that `argparse` puts on its own, like `options:` and `show this help message and exit`, come out in English; they belong to the library.)

See the difference with the lab server running (again, the times vary on your machine):

```text
$ cd fig11_05
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 854ms
```

Without `--verbose`, the report comes out as always and the error output says nothing. With `--verbose` the log appears **on the other channel**. To see them separately, redirect them to different files (it is Exercise 3): the clean report in one and the log in the other.

One last comment, a matter of craft. The order of the log lines is the order in which the services *finish*, not that of the configuration: `reportes` (which fails immediately) comes out first. It is another reason for the **report** not to depend on the log: the report is built in order, from the list; the log is a journal of what was happening. The [blog entry on telemetry](https://www.habil.mx/en/blog/telemetry-prometheus-loki-tempo-grafana-opentelemetry/) tells how, in a real system, the logs of many programs like this one are brought together.

> **The first session ends here.** You have the final report (the table that calculates its width and the JSON tested as a contract) and the log with `--verbose`, each on its own channel. Before the second session, run the tests and the `revisor` with and without `--verbose`, redirecting each channel to its file. The second session adds no code to the `revisor`: it reviews security, builds and installs it with `pipx`, and checks one by one the seven points of “How you know you are done.”

### 11.3 Security review: four habits

The course has been sowing security where the risk was, not in a separate chapter: validating what arrives from outside (Lesson 6), treating the `urllib` address with care (Lesson 9). This part gathers the four habits so that you have them together. **It adds no code to the `revisor`**: the `revisor` already applies the first and has none of the other three. They are explained because you will need them as soon as you write the next program, and because the first takes on a new meaning now that the program is a tool anyone can install.

#### 11.3.1 The address someone else writes

Your `revisor` makes a request to the address that is in `servicios.toml`. Whoever writes that file decides **where your program goes**. If it is only you, there is no risk. But a program gets reused, and tomorrow that file may come from another team, from a web page or from a form. Lesson 6 put in a defense: `validar_servicio` only accepts `http://` or `https://` addresses that pass the checks of `es_url_http` (scheme, server, port and ordinary text). It is not a complete validation, and that is why Lesson 9 put in a second net: if `httpx` rejects an address that passed, that service comes out as “dirección inválida” and the others are checked just the same. See what the first defense does with an address that does not pass:

```text
$ python -m revisor --config raro.toml
error de configuración: servicio 1: 'url' debe ser una dirección http:// o https:// válida
$ echo $?
2
```

A file with `url = "file:///etc/passwd"` is rejected before doing anything: the configuration message comes out and the code `2`. Without that validation, depending on the tool that made the request, `file://` could read files on your own machine. And there is a subtler variant that the scheme validation does not cover: an `http://` address that points **inward** into your network (to an internal service or to the metadata service of a server in the cloud) makes *your* program, which is inside, query something that the address's author could not reach from outside. That attack is called *server-side request forgery* (SSRF) and [OWASP describes it in detail](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). For the `revisor`, which reads a configuration file that you write, it is a low risk; for a web service that receives addresses from users, it is a central risk. The rule: **an address that comes from outside is untrusted data, and is validated (and limited to a permitted set) before being used**. The Hábil blog entry on [API security](https://www.habil.mx/en/blog/api-security-cto-identity-gateway-tokens/) takes that rule to the level of architecture.

#### 11.3.2 `subprocess`: a list, never an assembled text

Some day your program will want to run another system program (`ping`, `git`, `ls`). The [`subprocess`](https://docs.python.org/3/library/subprocess.html) module does it, and it has two ways of receiving the command, with very different consequences. This figure uses `echo` (which only prints) so that you can see the difference without risk:

```python
# fig11_02.py
import subprocess

nombre = "catalogo; echo INYECTADO"

print("--- con shell=True y un texto armado ---", flush=True)
subprocess.run(f"echo revisando {nombre}", shell=True, check=True)

print("--- con una lista y sin shell ---", flush=True)
subprocess.run(["echo", "revisando", nombre], check=True)
```

```text
$ python fig11_02.py
--- con shell=True y un texto armado ---
revisando catalogo
INYECTADO
--- con una lista y sin shell ---
revisando catalogo; echo INYECTADO
```

In both cases, the “name” is `catalogo; echo INYECTADO`: a text where someone wrote, after the name, a semicolon and **another command**. With `shell=True`, Python does not run the program directly, but gives it to the *shell* (the terminal's interpreter) as a text for it to interpret, and the shell understands `;` as “end this command and run another.” The result: **two** things were run, and the second was chosen by whoever wrote the name. That is a *command injection*. With a **list** (`["echo", "revisando", nombre]`) each element is an argument, the shell does not intervene, and the `;` is just one more character of the text. If the command had been `rm` instead of `echo`, the difference would have been deleting your files. The documentation of [`subprocess` in its security section](https://docs.python.org/3/library/subprocess.html#security-considerations) asks for exactly this; [OWASP explains it with more examples](https://owasp.org/www-community/attacks/Command_Injection). The rule: **a list of arguments and no `shell=True`; if the shell is needed, the text that reaches it cannot contain anything that came from outside**. The `check=True` makes a command that fails raise an exception instead of passing in silence.

#### 11.3.3 `eval` and `pickle`: running what arrives from outside

`eval(texto)` takes a text and **runs it as Python code**. It looks convenient for turning “2 + 2” into 4, but look at what it accepts:

```python
# fig11_03.py
texto_de_afuera = "__import__('sys').version_info.major"

print(eval(texto_de_afuera))
```

```text
$ python fig11_03.py
3
```

The “outside text” is a statement that imports a module and reads its Python version: nothing harmful, but identical in form to what a statement that deletes files or sends your data elsewhere would do. `eval` does not distinguish. Any data that arrives from outside and goes through `eval` gives whoever wrote it control of your program. To turn text into data there are tools that **only** understand data: `json.loads` (which you have used since Lesson 6) for JSON, `tomllib.loads` for TOML. Not even `ast.literal_eval`, the “safe version” of `eval`, is a complete defense against a hostile text, as [its documentation](https://docs.python.org/3/library/ast.html#ast.literal_eval) warns.

`pickle` is the sibling case. It is the module that saves Python objects to a file, and its [documentation](https://docs.python.org/3/library/pickle.html) opens with a warning in red: *it is not secure*, because unpickling can run arbitrary code. A `pickle` file that another person sends you is, in practice, a program. For data that crosses borders, JSON. There is no `pickle` figure in the course because showing it requires writing a class with methods, and you have not seen that piece; the warning is enough.

#### 11.3.4 `secrets`, not `random`

The `random` module produces numbers that *look* random but are calculated with a formula from a **seed**: if you know the seed, you know all the numbers. That is a virtue for a simulation you want to repeat, and a disaster for a password or a token. See the two things together:

```python
# fig11_04.py
import random
import secrets

random.seed(1)
primero = random.random()
random.seed(1)
segundo = random.random()
print("random con la misma semilla:", primero == segundo)

token = secrets.token_hex(16)
print("secrets, largo del token:", len(token))
```

```text
$ python fig11_04.py
random con la misma semilla: True
secrets, largo del token: 32
```

With the same seed (`random.seed(1)`), `random.random()` gives **exactly the same number** twice: it is `True`. An attacker who guesses the seed (for example, the time at which the program started) reproduces all your “secrets.” [`secrets`](https://docs.python.org/3/library/secrets.html) is made for the opposite: it takes its randomness from the operating system, the same one it uses for encryption keys. `secrets.token_hex(16)` gives 16 random bytes written in hexadecimal, that is, a text of 32 characters (hence the `32`). The [`random` documentation](https://docs.python.org/3/library/random.html) says it in its first warning: do not use for security purposes. The rule: **if the number is a secret (token, password, an identifier that must not be guessable), `secrets`; if not, `random` is fine**.

### 11.4 Building and installing

#### 11.4.1 What an installable package is

So far the `revisor` is run with `python -m revisor` from the project folder, and it was installed in your environment with `pip install -e .` (the **editable** installation of Lesson 7, which does not copy the code but points to it). That works for developing. To hand it to another person you need a **file** that contains the program already packed. In Python that file is called a [*wheel*](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), has the extension `.whl` and is, inside, a compressed file with your code and its installation data (name, version, dependencies, and which command must be created). The name tells a story: `revisor-1.0.0-py3-none-any.whl` means “the `revisor` package, version 1.0.0, for any version of Python 3, without compiled code, on any system.”

The version rises to `1.0.0` in the `pyproject.toml`; it is the only thing that changes there:

```toml fig11_05/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "1.0.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = ["httpx>=0.28"]

[project.scripts]
revisor = "revisor.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

It is built with the package installer. One detail: you need neither the `build` package nor anything new; `pip` already knows how to build a *wheel* (the command is [`pip wheel`](https://pip.pypa.io/en/stable/cli/pip_wheel/)). The `--no-deps` option tells it to build **only your package** and not download the dependencies, and `-w dist` to leave the result in the `dist/` folder. The final dot is “build the project in this folder.” To put it together, `pip` downloads for a moment the build tool you declared in `[build-system]` (`hatchling`): it is a *build* dependency, not a run-time one, and it does not travel inside the *wheel*.

```text
$ python -m pip wheel --no-deps -w dist .
Processing /home/tu_usuario/curso-python/revisor
  Installing build dependencies: started
...
Building wheels for collected packages: revisor
  Building wheel for revisor (pyproject.toml): started
  Building wheel for revisor (pyproject.toml): finished with status 'done'
  Created wheel for revisor: filename=revisor-1.0.0-py3-none-any.whl size=6397 sha256=...
  Stored in directory: ...
Successfully built revisor
$ ls dist
revisor-1.0.0-py3-none-any.whl
$ unzip -Z1 dist/revisor-1.0.0-py3-none-any.whl
revisor/__init__.py
revisor/__main__.py
revisor/cli.py
revisor/configuracion.py
revisor/formato.py
revisor/modelo.py
revisor/revision.py
revisor-1.0.0.dist-info/METADATA
revisor-1.0.0.dist-info/WHEEL
revisor-1.0.0.dist-info/entry_points.txt
revisor-1.0.0.dist-info/RECORD
```

(The output of `pip wheel` is shortened: the `...` mark lines that were removed, among them the download of `hatchling` and a long `sha256` fingerprint. The size, `size`, depends on your code, so yours may be different; what matters is `Successfully built revisor`.)

Two things to read here. The *wheel* contains the `revisor` package (seven files) and its `dist-info` folder with the metadata; it **does not contain** `servicios.toml`, nor the tests, nor the lab server files. That is correct: the program does not bring its configuration, whoever uses it does. And the version in the file's name, `1.0.0`, came from the `pyproject.toml`.

#### 11.4.2 `pipx`: installing a tool, not a library

You could install the *wheel* with `pip install` inside a virtual environment, but then the `revisor` would only exist while that environment was activated. For a **tool** you want to use from any folder, like `git` or `ruff`, the solution is [`pipx`](https://pipx.pypa.io/stable/). `pipx` creates a virtual environment **of its own for each tool**, installs the package there with its dependencies, and leaves the command available in your `PATH`. Each tool stays isolated from the others and from your system Python (which, remember from Lesson 1, must not be touched with `pip`).

On Linux Mint it is installed with the system's package manager: `sudo apt install pipx` (the package is in the Ubuntu 24.04 repositories, the base of Mint 22: [version 1.4.3](https://packages.ubuntu.com/noble/pipx)), and then `pipx ensurepath`, which adds the folder of `pipx`'s commands (`~/.local/bin`) to your `PATH`; open a new terminal so that it notices. With that, installing the `revisor` is one line. The output below was obtained with a newer version of `pipx` and of Python than your Mint's, so the text may differ in details: what matters are the last three lines. The environment-preparation lines were removed.

```text
$ pipx install dist/revisor-1.0.0-py3-none-any.whl
done!
  installed package revisor 1.0.0, installed using Python 3.14.8
  These apps are now available
    - revisor
```

`pipx` created the environment, installed the *wheel* with its dependencies (`httpx` and its own) and left the `revisor` command. Trying it from **another folder** is the point. This run is from an empty folder:

```text
$ revisor --version
revisor 1.0.0
$ echo $?
0
$ revisor
error de configuración: no existe el archivo servicios.toml
$ echo $?
2
$ revisor --config servicios.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      91ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
$ echo $?
1
```

Three things. `revisor --version` works from any folder and says `revisor 1.0.0`; remember that this number is not written in the code, but `cli.py` reads it from the installed package's metadata, which comes from the `pyproject.toml`. Second: a bare `revisor`, from a folder that has no `servicios.toml`, ends with the configuration message and the code `2`. It is the same lesson as in Lesson 6 (the relative path depends on where you are), and it is not a defect: it is right for a tool, which must not guess where your configuration is. That is what `--config` is for. And third: with a valid `--config`, the report comes out and the code is `1`, because there is one `LENTO` service and one `CAIDO`.

#### 11.4.3 What is coming, and is not yet for you

Two novelties of Python 3.14 are left out of the course on purpose, and it is worth knowing that they exist. The first is the **free-threaded interpreter** (without the GIL): a variant of Python that can run Python code in several threads at the same time; with 3.14 it became [officially supported](https://peps.python.org/pep-0779/), but it is still a separate and optional build, and many libraries are not ready yet. For the `revisor` nothing changes, because it already does concurrent waits in a single thread and is not limited by the GIL. The second is ***t-strings*** (template strings, [PEP 750](https://peps.python.org/pep-0750/)): they are written like an f-string but with a `t` in front, and instead of a text they return an object that separates the fixed from the interpolated, useful for escaping HTML or building SQL queries safely. Neither is necessary for what you did, neither is used in the course (and the course's code has to run on your Mint's 3.12, which does not have them), and both are explained in [the list of what is new in 3.14](https://docs.python.org/3/whatsnew/3.14.html). When you need them, you will already know how to read that documentation on your own, which is what the course set out to do.

## The seven points, one by one

Here the course closes. Each point is one command and one output; the output below is the real one, from the `fig11_05/` folder with the lab server running in another terminal.

### Point 1 — `pytest` ends green and says how many tests ran

`pytest -q` is run and **the report's count** is read, the last line. In this folder it must say `30 passed`: the 27 from Lesson 10 plus today's three (the JSON contract, the table with a long name and `--version`).

Why the count and not the exit code: `pytest`'s code 0 only says there were *no failures*, and you can have 0 failures with almost no tests running. See two cases, measured. One: a file with a single test marked to be skipped.

```text
$ pytest -q tests/test_saltada.py
s                                                                        [100%]
1 skipped in 0.00s
$ echo $?
0
```

Code 0, and `1 skipped`: nothing was tested, and everything looks fine. Two: filtering by name.

```text
$ pytest -q -k sale_con
..                                                                       [100%]
2 passed, 28 deselected in 0.02s
$ echo $?
0
```

Also with code 0, but `2 passed, 28 deselected`: of 30 tests, two ran. Whoever only looks at the green color or the code does not notice; whoever reads the count does. The [`pytest` exit codes reference](https://docs.pytest.org/en/stable/reference/exit-codes.html) lists them (there is a specific one, 5, for “no tests were collected,” but not even that protects against a filter that lets two through). **Rule: point 1 is met when you read `30 passed` and that 30 is the number you expected.**

### Points 2 and 6 — quality, and running the same on 3.14 and on 3.12

The four quality tools are run, with each version of Python. First with 3.14:

```text
$ python --version
Python 3.14.8
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

And exactly the same with 3.12, your Mint's line. The run below was made with Python 3.12.12; Mint 22's is 3.12.3 (you saw it in Lesson 1), so on your screen the first line will say `Python 3.12.3`:

```text
$ python --version
Python 3.12.12
$ pytest -q
..............................                                           [100%]
30 passed in 0.05s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

The only difference is the `python --version` line. `ruff check` and `ruff format --check` report nothing (they check 13 files, the lab server included) and `mypy` says `Success`. The 30 tests pass on both. To repeat this on your Mint: the system's Python (3.12) you already have in your usual environment. If you installed 3.14 with `uv` (the box in Lesson 7), create a second environment with it (`python3.14 -m venv .venv314`), activate it and install the project and the tools with the versions in `herramientas/requisitos.txt`, and run the same four commands. If you did not install 3.14, point 6 is met *for the version you have*, and the other half you check yourself whenever you like: you install 3.14 with `uv` and repeat these four commands. Nobody checks it for you; the output above is from a run on both versions, and what counts is yours.

### Point 3 — 20 services at once, in the slowest one's time

With the twenty half-second services (`servicios-20.toml`), in a line and with all at once:

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 504ms

real	0m10.169s
user	0m0.093s
sys	0m0.020s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 509ms

real	0m0.606s
user	0m0.083s
sys	0m0.018s
```

In a line (`--concurrencia 1`): 10.2 seconds, the sum. With `--concurrencia 20`: 0.61, close to the slowest (0.5) plus Python's start-up. **Point 3 is met** because the time is not the sum of the waits: it is of the order of the longest wait. If your machine shows a few hundredths more, it does not matter; what matters is that it is about sixteen times less.

### Point 4 — a service that is down, slow or answers garbage does not take down the report

With the lab server you already saw it in every run: `reportes` is down, `inventario` is slow, and the other two come out complete. The third kind is missing, the one that **answers garbage**: something that responds, but not with valid HTTP. That cannot be asked of the lab server, but it can of a fake transport (Lesson 10), which can raise the exception `httpx` raises when facing a response that is not HTTP (`httpx.RemoteProtocolError`). This figure brings together five kinds of service in a single run: a healthy one, a slow one, one that answers garbage, one that returns 503 and one really hung (it waits 30 seconds with a half-second timeout).

```python
# fig11_06.py
import asyncio

import httpx
from revisor.formato import tabla
from revisor.modelo import Servicio
from revisor.revision import revisar_todos

SERVICIOS = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("lento", "https://lento.example"),
    Servicio("basura", "https://basura.example"),
    Servicio("caido", "https://caido.example"),
    Servicio("colgado", "https://colgado.example", timeout_ms=500),
    Servicio("pagos", "https://pagos.example"),
]


async def atender(peticion: httpx.Request) -> httpx.Response:
    anfitrion = peticion.url.host
    if anfitrion == "lento.example":
        await asyncio.sleep(1.1)
    if anfitrion == "colgado.example":
        await asyncio.sleep(30)
    if anfitrion == "basura.example":
        raise httpx.RemoteProtocolError("lo que llegó no es HTTP", request=peticion)
    if anfitrion == "caido.example":
        return httpx.Response(503)
    return httpx.Response(200)


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    resultados = await revisar_todos(SERVICIOS, transporte=transporte)
    print(tabla(resultados))


asyncio.run(main())
```

```text
$ python fig11_06.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA       0ms  200
lento       LENTO       1.1s  200
basura      CAIDO          —  error de red
caido       CAIDO        0ms  503
colgado     CAIDO          —  tiempo agotado
pagos       ARRIBA       0ms  200

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 275ms
```

This program **imports the package** `revisor`: it runs with the environment where you installed the project (`pip install -e .` in the `fig11_05/` folder). The six services come out in the report, in their order, each with its own: `lento` is `LENTO` (1.1 s), `basura` appears as `CAIDO` with detail `error de red`, `caido` carries its `503`, and `colgado` gave up with `tiempo agotado` without waiting the 30 seconds. None took down the others. And it is not just a matter of the simulation: if a real server answers something that is not HTTP (for example, a program that listens on a port and replies any text), `httpx` raises a protocol error, which is an `httpx.HTTPError`, and the `revisor` reports it just the same, as `error de red`. The `0ms` of `catalogo` and `pagos` are because the fake transport answers instantly; with a real network they would be tens or hundreds. **Point 4 is met.**

### Point 5 — no request waits forever

Two checks. The first, in the code: how many places make a request, and are they all protected?

```text
$ grep -rn "cliente.get" src/revisor
src/revisor/revision.py:19:            respuesta = await cliente.get(servicio.url, timeout=limite)
```

A single request in the whole package, and it is inside `async with asyncio.timeout(...)` and with `httpx.Timeout(...)` (you saw it in `revision.py`). The second, with the run: a lab server service that takes 10 seconds with `timeout_ms = 1000`, and another that takes 8 seconds **without** `timeout_ms` in the configuration (it uses the default value, 5000):

```text
$ time python -m revisor --config servicios-limite.toml
SERVICIO        ESTADO    TIEMPO  DETALLE
notificaciones  CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m1.127s
user	0m0.106s
sys	0m0.022s

$ time python -m revisor --config servicios-sin-limite.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
colgado     CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m5.141s
user	0m0.115s
sys	0m0.027s
```

The first gives up at 1.1 seconds; the second, at 5.1. Neither waited as long as the server wanted. **Point 5 is met**, also for whoever forgets to put the timeout in their configuration, because `Servicio`'s default value is 5000 ms.

### Point 7 — it installs with `pipx` and is used from another folder

You already did it in 11.4: `pipx install`, `revisor --version` and `revisor --help` from any folder. What is left is checking the exit-code contract: **0 if everything is up, 1 if not**. With the lab server's four services you already saw the 1. With a file that only has `pagos`:

```text
$ revisor --config bien.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA     102ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 102ms
$ echo $?
0
```

Code 0. And `revisor --help` works from any folder and shows the options' help with the Spanish text you gave them in 11.2.3. **Point 7 is met.**

With the seven met, the `revisor` is finished in the sense the course defined at the start. Not because it is perfect, but because what it says it does, **it does and you can check it**.

## The complete project

The files of the `fig11_05/` folder that did not change in this lesson are here so that the folder is complete and can be run:

<details>
<summary>The files that do not change in this lesson</summary>


```toml fig11_05/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "inventario"
url = "http://127.0.0.1:8099/inventario"

[[servicios]]
nombre = "pagos"
url = "http://127.0.0.1:8099/pagos"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
```

```python
# fig11_05/laboratorio.py
"""Servidor de práctica del curso: contesta como si fuera cada servicio del revisor.

Se corre aparte (python laboratorio.py) y se deja abierto mientras practicas.
No necesitas entender cómo está escrito; lo que importa son sus rutas.
"""

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PUERTO = 8099

# ruta -> (código de la respuesta, milisegundos que tarda en contestar)
RUTAS: dict[str, tuple[int, int]] = {
    "/catalogo": (200, 142),
    "/inventario": (200, 2300),
    "/pagos": (200, 87),
    "/facturacion": (503, 95),
    "/notificaciones": (200, 10000),
}


class Laboratorio(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        codigo, espera_ms = self.buscar_ruta()
        time.sleep(espera_ms / 1000)
        cuerpo = b"ok" if codigo == 200 else b"error"
        try:
            self.send_response(codigo)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        except OSError:
            pass  # quien preguntó se cansó de esperar y colgó

    def buscar_ruta(self) -> tuple[int, int]:
        if self.path.startswith("/espera/"):
            texto = self.path.removeprefix("/espera/")
            if texto.isdigit():
                return 200, int(texto)
        return RUTAS.get(self.path, (404, 0))

    def log_message(self, format: str, *args: object) -> None:
        """No imprime una línea por cada petición."""


class Servidor(ThreadingHTTPServer):
    request_queue_size = 128  # conexiones que pueden esperar turno (de fábrica: 5)


def main() -> None:
    servidor = Servidor(("127.0.0.1", PUERTO), Laboratorio)
    print(f"laboratorio en http://127.0.0.1:{PUERTO} (Ctrl+C para detenerlo)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("laboratorio detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
```

```toml fig11_05/servicios-20.toml
[[servicios]]
nombre = "servicio01"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio02"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio03"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio04"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio05"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio06"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio07"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio08"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio09"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio10"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio11"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio12"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio13"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio14"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio15"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio16"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio17"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio18"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio19"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio20"
url = "http://127.0.0.1:8099/espera/500"
```

```python
# fig11_05/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig11_05/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig11_05/src/revisor/modelo.py
from dataclasses import dataclass
from enum import Enum

UMBRAL_LENTO_MS = 1000


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


@dataclass(frozen=True)
class Resultado:
    servicio: Servicio
    estado: Estado
    tiempo_ms: int | None
    detalle: str


def clasificar(
    codigo: int | None,
    tiempo_ms: int | None,
    umbral_ms: int = UMBRAL_LENTO_MS,
) -> Estado:
    match codigo:
        case None:
            return Estado.CAIDO
        case c if c >= 400:
            return Estado.CAIDO
        case _:
            if tiempo_ms is not None and tiempo_ms >= umbral_ms:
                return Estado.LENTO
            return Estado.ARRIBA


def nombres_repetidos(servicios: list[Servicio]) -> set[str]:
    vistos: set[str] = set()
    repetidos: set[str] = set()
    for servicio in servicios:
        if servicio.nombre in vistos:
            repetidos.add(servicio.nombre)
        vistos.add(servicio.nombre)
    return repetidos
```

```python
# fig11_05/src/revisor/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from revisor.modelo import Servicio, nombres_repetidos


class ErrorDeConfiguracion(Exception):
    """El archivo de configuración no se puede usar."""


def leer_servicios(ruta: Path) -> list[Servicio]:
    try:
        texto = ruta.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error

    try:
        datos = tomllib.loads(texto)
    except tomllib.TOMLDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no es TOML válido: {error}") from error

    lista = datos.get("servicios")
    if not isinstance(lista, list) or len(lista) == 0:
        raise ErrorDeConfiguracion("falta la lista [[servicios]]")

    servicios = [
        validar_servicio(datos_servicio, posicion)
        for posicion, datos_servicio in enumerate(lista, start=1)
    ]

    repetidos = nombres_repetidos(servicios)
    if len(repetidos) > 0:
        raise ErrorDeConfiguracion(f"nombres repetidos: {', '.join(sorted(repetidos))}")
    return servicios


def es_url_http(url: str) -> bool:
    if not url.isascii() or not url.isprintable() or " " in url:
        return False
    try:
        partes = urlsplit(url)
        return (
            partes.scheme in {"http", "https"}
            and partes.hostname is not None
            and (partes.port is None or partes.port > 0)
        )
    except ValueError:
        return False


def validar_servicio(datos: object, posicion: int) -> Servicio:
    if not isinstance(datos, dict):
        raise ErrorDeConfiguracion(f"servicio {posicion}: debe ser una tabla")

    nombre = datos.get("nombre")
    if nombre is None:
        raise ErrorDeConfiguracion(f"servicio {posicion}: falta 'nombre'")
    if not isinstance(nombre, str) or nombre.strip() == "":
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'nombre' debe ser un texto que no esté vacío"
        )

    url = datos.get("url")
    if url is None:
        raise ErrorDeConfiguracion(f"servicio {posicion}: falta 'url'")
    if not isinstance(url, str) or not es_url_http(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' debe ser una dirección "
            "http:// o https:// válida"
        )

    if "timeout_ms" not in datos:
        return Servicio(nombre, url)

    timeout_ms = datos["timeout_ms"]
    if (
        not isinstance(timeout_ms, int)
        or isinstance(timeout_ms, bool)
        or timeout_ms <= 0
    ):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'timeout_ms' debe ser un entero mayor que 0"
        )
    return Servicio(nombre, url, timeout_ms)
```

```python
# fig11_05/tests/test_modelo.py
import pytest

from revisor.modelo import Estado, clasificar


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, Estado.ARRIBA),
        (200, 999, Estado.ARRIBA),
        (200, 1000, Estado.LENTO),
        (200, 2300, Estado.LENTO),
        (503, 95, Estado.CAIDO),
        (404, 50, Estado.CAIDO),
        (None, None, Estado.CAIDO),
    ],
)
def test_clasificar(
    codigo: int | None, tiempo_ms: int | None, esperado: Estado
) -> None:
    assert clasificar(codigo, tiempo_ms) is esperado
```

```python
# fig11_05/tests/test_configuracion.py
from pathlib import Path

import pytest

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.modelo import Servicio


def test_lee_un_archivo_valido(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(
        '[[servicios]]\nnombre = "catalogo"\nurl = "https://catalogo.example"\n',
        encoding="utf-8",
    )
    assert leer_servicios(archivo) == [Servicio("catalogo", "https://catalogo.example")]


@pytest.mark.parametrize(
    ("contenido", "mensaje"),
    [
        (
            '[[servicios]]\nurl = "https://catalogo.example"\n',
            "servicio 1: falta 'nombre'",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "ftp://catalogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "http://[::1"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://cata\\nlogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://catálogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://catalogo.example"\n'
            "timeout_ms = 0\n",
            "servicio 1: 'timeout_ms' debe ser un entero mayor que 0",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://a.example"\n\n'
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://b.example"\n',
            "nombres repetidos: catalogo",
        ),
    ],
    ids=[
        "sin nombre",
        "url ftp",
        "url mal formada",
        "url con salto",
        "url con acento",
        "timeout cero",
        "nombres repetidos",
    ],
)
def test_rechaza_configuraciones_invalidas(
    tmp_path: Path, contenido: str, mensaje: str
) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorDeConfiguracion) as informe:
        leer_servicios(archivo)
    assert str(informe.value) == mensaje
```

```python
# fig11_05/tests/test_revision.py
import asyncio

import httpx

from revisor.modelo import Estado, Resultado, Servicio
from revisor.revision import revisar, revisar_todos

CATALOGO = Servicio("catalogo", "https://catalogo.example")
PAGOS = Servicio("pagos", "https://pagos.example")
FACTURACION = Servicio("facturacion", "https://facturacion.example")
REPORTES = Servicio("reportes", "https://reportes.example")
NOTIFICACIONES = Servicio("notificaciones", "https://notificaciones.example", 1000)


def atender(peticion: httpx.Request) -> httpx.Response:
    """Un servidor de mentira: contesta según el nombre del anfitrión."""
    anfitrion = peticion.url.host
    if anfitrion == "facturacion.example":
        return httpx.Response(503)
    if anfitrion == "reportes.example":
        raise httpx.ConnectError("sin ruta", request=peticion)
    if anfitrion == "notificaciones.example":
        raise httpx.ReadTimeout("muy lento", request=peticion)
    return httpx.Response(200)


async def revisar_uno(servicio: Servicio) -> Resultado:
    async with httpx.AsyncClient(transport=httpx.MockTransport(atender)) as cliente:
        return await revisar(cliente, servicio)


def test_200_rapido_es_arriba() -> None:
    resultado = asyncio.run(revisar_uno(CATALOGO))
    assert resultado.estado is Estado.ARRIBA
    assert resultado.detalle == "200"


def test_503_es_caido_con_el_codigo() -> None:
    resultado = asyncio.run(revisar_uno(FACTURACION))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "503"


def test_sin_conexion_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(REPORTES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "sin conexión"


def test_tiempo_agotado_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(NOTIFICACIONES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "tiempo agotado"


def test_la_mezcla_sale_completa_y_en_orden() -> None:
    servicios = [CATALOGO, FACTURACION, REPORTES, NOTIFICACIONES]
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos(servicios, transporte=transporte))
    assert [r.servicio.nombre for r in resultados] == [
        "catalogo",
        "facturacion",
        "reportes",
        "notificaciones",
    ]
    assert [r.detalle for r in resultados] == [
        "200",
        "503",
        "sin conexión",
        "tiempo agotado",
    ]


def test_una_direccion_invalida_no_tumba_a_los_demas() -> None:
    mala = Servicio("mala", "http://999.1.1.1:8099/pagos")
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos([mala, CATALOGO], transporte=transporte))
    assert [r.detalle for r in resultados] == ["dirección inválida", "200"]
```

</details>

And `tests/test_cli.py`, which changed: it gained the `--version` test.

```python
# fig11_05/tests/test_cli.py
from pathlib import Path

import pytest

from revisor.cli import main
from revisor.modelo import Estado, Resultado, Servicio

CONFIGURACION = """\
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
"""


def test_version_dice_1_0_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as salida:
        main(["--version"])
    assert salida.value.code == 0
    assert capsys.readouterr().out == "revisor 1.0.0\n"


def test_con_servicios_caidos_sale_con_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_caidos(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

The new test uses `capsys`, a `pytest` tool that is a sibling of `tmp_path` and `monkeypatch`: it collects what the program **prints** during the test, so that it can be checked. Its annotation, `pytest.CaptureFixture[str]`, is read like the collection ones from Lesson 4: `CaptureFixture` is the type of that tool, and `[str]` says that what it collects is text, just as `list[str]` says the list holds texts. `main(["--version"])` prints `revisor 1.0.0` and ends the program with `SystemExit` (that is how `argparse` works with `--version`), so the test receives it with `pytest.raises(SystemExit)` (which checks that the block raises that exception, and with `as salida` lets you look at it) and then reads what was printed with `capsys.readouterr().out`. There is a trap in this test that is worth knowing: the number `1.0.0` does not come from the code but from the **installed package's metadata**, so it depends on when you installed.

## The error you will see

### `AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'`

You raised the version in `pyproject.toml` to `1.0.0`, ran the tests and the `--version` one turned red saying the version is the old one:

```text
$ pytest -q --tb=short tests/test_cli.py
F..                                                                      [100%]
=================================== FAILURES ===================================
___________________________ test_version_dice_1_0_0 ____________________________
tests/test_cli.py:24: in test_version_dice_1_0_0
    assert capsys.readouterr().out == "revisor 1.0.0\n"
E   AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'
E     
E     - revisor 1.0.0
E     ?         ^ ^
E     + revisor 0.9.0
E     ?         ^ ^
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_version_dice_1_0_0 - AssertionError: assert 'r...
1 failed, 2 passed in 0.04s
```

Read it from the bottom up: the test expected `revisor 1.0.0` and the program said `revisor 0.9.0`. But you **already changed** the `pyproject.toml`. Where does the `0.9.0` come from, then? From the metadata of the editable installation you did earlier: it is generated on installing, not on changing the file. The `pyproject.toml` is the recipe; the installation is the dish already served. The fix is to install again:

```text
$ pip install -e .
$ pytest -q tests/test_cli.py
...                                                                      [100%]
3 passed in 0.02s
```

The rule: **when you change something the installer reads (the name, the version, the commands), install again**. This is not a defect of `pip`, it is a consequence of the version living in a single place (`pyproject.toml`), as was decided in Lesson 7 so as not to repeat the number in two files.

### `bash: revisor: command not found`

You installed with `pipx`, open a terminal and type `revisor`:

```text
bash: revisor: command not found
```

The command is not found because the folder where `pipx` leaves commands (`~/.local/bin`) is not in your `PATH`, which is the list of folders where the terminal looks for programs. It is fixed with `pipx ensurepath` and **opening a new terminal**: the change applies only to terminals opened afterwards. (The exact text of the error changes from one terminal to another; Linux Mint may suggest installing a package with that name, and it is not what you want.)

### `error de configuración: no existe el archivo servicios.toml`

It is the one from Lesson 6, and reappears when running `revisor` from a folder without configuration (you saw it in 11.4.2). There is nothing to fix in the code: pass `--config` with the path, or run the command from the folder where your `servicios.toml` is.

## What gets done wrong

**Letting the version live in two places.** The number in `pyproject.toml` and another written by hand in `cli.py` end up differing. The `revisor` reads it from the installed package. Cost: a `--version` that lies.

**Mixing the log with the report.** Printing diagnostics with `print` between the lines of the report. Cost: the script that reads the JSON receives garbage and stops working. The report goes to standard output; everything else, through `logging` to standard error.

**Configuring `logging` inside a module of the package.** If `revision.py` called `basicConfig`, importing the module would change the behavior of the program that imports it. Cost: two configurations fighting. It is configured in a single place, at the entry point.

**Putting `DEBUG` on everyone's logger.** It fills up with `httpx` lines and yours get lost. The level is raised only on your own logger.

**Using an `f"..."` in a `logging` message.** It builds the text even if the level is off. Cost: wasted work on every message, noticeable when there are thousands.

**Changing the JSON format without warning.** Renaming a field, changing the `null` for a `0`, reordering for no reason. Cost: everything that reads that JSON breaks. If the contract changes, the major version is raised and notice is given.

**`subprocess` with `shell=True` and a text assembled with outside data.** Cost: someone else running commands on your machine.

**`eval` or `pickle` with data that is not yours.** Cost: the same.

**`random` for a secret.** Cost: a token that someone else can reconstruct.

**Considering a program finished when nobody has installed it the way a user would.** It works in the development environment and fails on installation because a file or a dependency is missing. The *wheel* is built and tried **from another folder**, not from the code.

**Reading only the color of `pytest`.** Green with 2 tests out of 30 is a green. Read the count.

## Exercises

### Exercise 1 — A really long name

Write a `servicios-largo.toml` with two services that point to the lab server: `catalogo` and another called `notificaciones-de-clientes` (26 characters). **Before running**, predict at which column `ESTADO` will start, and run it. Check that the table stays aligned.

### Exercise 2 — Break the contract

In a copy of `fig11_05/`, rename in `formato.py` the `"caido"` field of the JSON summary to `"caidos"`. Run `pytest -q --tb=short`. Note how many tests turn red and which. Repair and run again. Answer: what would have happened with a script that reads `resumen.caido` if nobody had that test?

### Exercise 3 — Two channels, two files

Run `python -m revisor --verbose` redirecting the standard output to `reporte.txt` and the error output to `registro.txt` (in the shell, `> archivo` redirects the standard and `2> archivo` the error). **Before running**, predict what will be in each file. Then look at their content.

### Exercise 4 — One more log line

Add to the `revisor` a `DEBUG`-level message in `main` that says how many services were read from the configuration. It must appear with `--verbose` and not without it. Check that the 30 tests still pass, and that `ruff` and `mypy` still report nothing.

## Solutions

### Solution 1

The longest name is 26 long; with the two spaces of breathing room the width is 28, so `ESTADO` starts at column 28 (counting from 0). The run:

```text
$ python -m revisor --config servicios-largo.toml
SERVICIO                    ESTADO    TIEMPO  DETALLE
catalogo                    ARRIBA     172ms  200
notificaciones-de-clientes  ARRIBA      94ms  200

2 servicios · 2 arriba · 0 lentos · 0 caídos · promedio 133ms
```

The word `ESTADO` stays aligned with `ARRIBA` in both rows, and `catalogo` has its column widened just like the other. With the usual services, the width goes back to 12.

### Solution 2

**One** test turns red, `test_el_json_es_un_contrato`; the other 29 pass:

```text
$ pytest -q --tb=short
...............F..............                                           [100%]
=================================== FAILURES ===================================
_________________________ test_el_json_es_un_contrato __________________________
tests/test_formato.py:70: in test_el_json_es_un_contrato
    assert json.loads(reporte_a_json(CANONICOS)) == esperado
E   AssertionError: assert {'servicios':...dos': 1, ...}} == {'servicios':...ido': 1, ...}}
E     
E     Omitting 1 identical items, use -vv to show
E     Differing items:
E     {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caidos': 1, ...}} != {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caido': 1, ...}}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_formato.py::test_el_json_es_un_contrato - AssertionError: a...
1 failed, 29 passed in 0.04s
```

The test tells you which field changed (`'caidos': 1` against `'caido': 1`). Without it, a script that read `resumen.caido` would have received a nonexistent field (`null` or an error, depending on the script's language) and would have continued, in the best case, treating “0 down” as a good result, just when there is a service down. It is the kind of error that does not show its face until the worst day.

### Solution 3

In `registro.txt` go the four `DEBUG revisor: ...` lines (the error channel); in `reporte.txt`, the table with its summary (the standard channel). Neither mixes with the other:

```text
$ python -m revisor --verbose > reporte.txt 2> registro.txt
$ cat registro.txt
DEBUG revisor: reportes: CAIDO, —, sin conexión
DEBUG revisor: pagos: ARRIBA, 92ms, 200
DEBUG revisor: catalogo: ARRIBA, 158ms, 200
DEBUG revisor: inventario: LENTO, 2.3s, 200
$ cat reporte.txt
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
```

### Solution 4

In `cli.py`, right before `asyncio.run(...)`:

```python
logging.getLogger("revisor").debug("leídos %s servicios", len(servicios))
```

The `logging` module is already imported. Result, measured (the new line comes out first, because it is written before anything is queried):

```text
$ python -m revisor --verbose 2>&1 >/dev/null | head -n 2
DEBUG revisor: leídos 4 servicios
DEBUG revisor: reportes: CAIDO, —, sin conexión
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
```

The first command needs a calm reading, because the order of the redirections matters and they are applied from left to right. `2>&1` says “send the error output (channel 2) to where the standard one goes today (channel 1),” which at that moment is the `|` pipe toward `head`. Then, `>/dev/null` sends the **standard** output to the trash. Result: what reaches `head` is only the log, which came out through the error channel, and the report is discarded. And `head -n 2` shows only the first two lines of what it receives. If you wrote the two redirections the other way round, `>/dev/null 2>&1`, both outputs would go to the trash and you would see nothing.

The 30 tests still pass, and `ruff check`, `ruff format` and `mypy` say nothing.

## How I know I got it

- [ ] `pytest -q` in `fig11_05/` ends with `30 passed`, and that is the number you expected.
- [ ] `ruff check`, `ruff format --check` and `mypy` report nothing; the four commands give the same result with Python 3.12 (and with 3.14 if you have it).
- [ ] With `servicios-20.toml`, `--concurrencia 1` takes about 10 seconds and `--concurrencia 20`, less than one.
- [ ] `fig11_06.py` shows six services in their order, with `LENTO`, `error de red`, `503` and `tiempo agotado` in their rows, and none takes down the others.
- [ ] A service that takes 10 seconds with `timeout_ms = 1000` is reported as `tiempo agotado` in a little over a second, and another without `timeout_ms` in a little over five.
- [ ] `python -m pip wheel --no-deps -w dist .` produces `dist/revisor-1.0.0-py3-none-any.whl`, and `pipx install` of that file leaves the `revisor` command.
- [ ] From a folder that is not the project's, `revisor --version` says `revisor 1.0.0`, `revisor --help` shows the options' help and `revisor --config servicios.toml` ends with `echo $?` equal to `1` (there are `LENTO` and `CAIDO` services) or to `0` (all up).
- [ ] You can explain why the report goes to standard output and the log to the error one; why the JSON is tested as a contract; and why `subprocess` receives a list, `eval` is not used with outside data and secrets come from `secrets`.

## Summary

Answer without looking at the lesson:

1. What two things make the `revisor`'s JSON a contract, and what test protects it?
2. How is the width of the first column calculated? Why, with the four canonical services, does the table come out identical to the one before?
3. What is the difference between standard output and standard error? Why does the report go to one and the log to the other?
4. Why does a `logging` message carry `%s` and the values separately, and not an f-string?
5. Why is `basicConfig` in `cli.py` and not in `revision.py`? Why is the level set on the `"revisor"` logger and not on everyone's?
6. What happens with `subprocess.run(f"echo {x}", shell=True)` if `x` carries a `;`? And with a list?
7. Why does `random` not work for a token and what do you use instead?
8. What does a *wheel* contain and what not? Why is a tool installed with `pipx` and not with `pip` in the system Python?
9. Why can the `--version` test turn red even though you changed the `pyproject.toml`? How is it fixed?
10. List, from memory, the seven checks with which the course ends and the command for each.

## Further reading

- [`logging` documentation and its basic guide](https://docs.python.org/3/howto/logging.html) — levels, loggers and configuration, with the right pattern for libraries and programs. Accessed on October 7, 2026.
- [Python packaging guide: writing the `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) and [`pipx`](https://pipx.pypa.io/stable/) — the source of the whole last stretch: what goes in the `pyproject.toml`, what a *wheel* is and how tools are installed. Accessed on October 7, 2026.
- [`subprocess` documentation: security considerations](https://docs.python.org/3/library/subprocess.html#security-considerations) and [`secrets`](https://docs.python.org/3/library/secrets.html) — the two official warnings of 11.3 with their examples. Accessed on October 7, 2026.
- [What's new in Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — the interpreter without the GIL, *t-strings* and the rest of what is new, to read when the course is behind you. Accessed on October 7, 2026.
