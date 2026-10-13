# Lección 11 — El programa terminado

**Tiempo:** 2 × 90 min (la primera sesión llega hasta el final de 11.2; la segunda empieza en 11.3)

**Qué construyes:** el `revisor` completo, versión 1.0.0, instalado en tu computadora como un comando más

**Qué aprendes:** el reporte como contrato (tabla con ancho calculado y JSON probado); `logging` y `--verbose`; los códigos de salida repasados; un repaso de seguridad (la dirección que otro escribe, `subprocess` sin `shell=True`, `secrets`, ni `eval` ni `pickle`); construir el paquete e instalarlo con `pipx`

**De dónde vienes.** Traes el `revisor` de la [Lección 10](10-concurrencia-pruebas-sin-red.md): un paquete que lee su configuración, consulta los servicios a la vez, con tiempo límite y con un tope de simultáneas, y que tiene 27 pruebas que no tocan la red. Funciona, y funciona bien. Pero todavía vive en tu carpeta: se corre con `python -m revisor` desde donde está el código, y su tabla tiene un defecto que no has visto porque todos tus servicios tienen nombres cortos: la columna `SERVICIO` mide siempre 12 caracteres, y un servicio llamado `notificaciones-de-clientes` la desborda. Hoy se cierra todo eso. Trabajas en tu carpeta `~/curso-python/revisor/`, con el entorno virtual activado y, para la última parte, con `pipx` instalado.

**Qué no hace esta lección.** Casi no trae conceptos nuevos de Python: es la lección en que **juntas** lo que ya sabes y compruebas que está terminado. Lo nuevo es de oficio: `logging`, que es el idioma con que un programa cuenta lo que hace sin ensuciar su reporte; el empaquetado final; y el repaso de las cuatro costumbres de seguridad que el curso fue sembrando. El paso final no es una lección más: es la lista de siete comprobaciones con que `es/README.md` define cuándo terminó el curso, y esta lección las recorre **una por una**, con la salida real de cada una.

## Al terminar vas a poder

- Explicar por qué un reporte que otro programa lee es un contrato, y probar ese contrato con una prueba que se pone roja si alguien renombra un campo.
- Calcular el ancho de una columna a partir de los datos y alinear una tabla aunque un nombre sea largo.
- Usar `logging` en lugar de `print` para lo que el programa cuenta de sí mismo, y explicar por qué el reporte va a la salida estándar y el registro a la salida de error.
- Decir, para cada código de salida (0, 1 y 2), qué le promete el `revisor` a quien lo llama desde un guion.
- Nombrar y evitar cuatro riesgos de seguridad frecuentes: una dirección que otro escribe, `subprocess` con `shell=True`, `eval` y `pickle` con datos de fuera, y números «aleatorios» para secretos.
- Construir el paquete como un archivo instalable (`.whl`), instalarlo con `pipx` y ejecutarlo desde cualquier carpeta.
- Comprobar, con un comando y una salida para cada uno, que el `revisor` cumple los siete puntos de «Cómo sabes que terminaste».

## El porqué antes del cómo

Cuando alguien dice «ya terminé el programa», hay al menos tres cosas que puede estar queriendo decir. Que **funciona en su computadora**, hoy, con sus datos. Que **otra persona puede instalarlo y usarlo** sin pedirle ayuda. O que **se puede confiar en él**: que si algo sale mal lo dice claro, que si cambia algo se entera una prueba antes que un usuario, que no se queda colgado, que no abre puertas que no debía. Las tres son distintas, y es muy común entregar la primera creyendo que es la tercera.

El curso empezó por ti, sentado frente a un `print("revisor: todavía no revisa nada")`, y termina en esta lección porque el `revisor` ya tiene que poder valerse solo. Para decidir si lo logró, no basta con la impresión de que «ya quedó»: la impresión es lo primero que falla. Por eso el temario define el final con **siete comprobaciones** que se pueden ejecutar, no con una opinión. Son estas, y las vas a recorrer una por una al final de la lección:

1. `pytest` termina en verde y el informe dice cuántas pruebas corrieron.
2. `ruff check`, `ruff format --check` y `mypy` no reportan nada.
3. Revisa 20 servicios a la vez en un tiempo cercano al del más lento, no al de la suma.
4. Un servicio caído, lento o que contesta basura no tumba el reporte.
5. Ninguna petición puede esperar para siempre.
6. Corre igual en Python 3.14 y en el 3.12 de tu Mint.
7. Se instala con `pipx install` y `revisor --help` funciona desde otra carpeta; sale con 0 si todo está arriba y con 1 si no.

De esas siete, tu `revisor` ya cumple casi todas y puede que no lo sepas. Lo que faltan son tres cosas: **medirlo** (nadie confía en «creo que sí»), **dejarlo en un estado que otro pueda usar** (el reporte, el registro, el empaquetado) y **revisar las costumbres de seguridad** para que el punto 4, «no tumba el reporte», no sea solo cosa de fallos accidentales sino también de entradas hostiles. Las cuatro partes de la lección siguen ese orden.

## Los conceptos

### 11.1 El reporte como contrato

#### 11.1.1 Quién lee tu reporte

Hasta ahora el reporte lo leías tú, en una terminal. Pero un programa de línea de comandos que sale con código 0 o 1 está hecho para que **otro programa** lo llame: un guion de la guardia que corre cada cinco minutos, una tarea de integración continua que decide si deja pasar un despliegue. Ese otro programa no *lee* el reporte como tú: lo **interpreta**. Busca un campo con un nombre y espera un tipo. Si el día de mañana alguien renombra `caido` a `caidos` en el JSON, para una persona es un cambio de ortografía; para el guion es un campo que desapareció, y sin una prueba que lo atrape nadie se entera hasta que la alarma de las tres de la mañana no suena.

A eso se le llama **contrato**: la forma en que el programa promete entregar su resultado, y que otros pueden dar por cierta. El `revisor` tiene dos contratos. El **JSON** (definido en la Lección 6) es para las máquinas: sus campos y sus tipos son fijos, y el `tiempo_ms` de un servicio que no respondió es `null`, no `0` ni un texto. Y el **código de salida** (definido en la Lección 7) es para el shell y para cualquier guion: `0` si todos los servicios están `ARRIBA`; `1` si alguno está `LENTO` o `CAIDO`; `2` si el uso es inválido o la configuración no sirve. La tabla, en cambio, es para personas, y puede cambiar de aspecto sin avisar a nadie.

Hoy se hace explícito lo que antes era implícito: se escribe una **prueba que describe el JSON entero**. Y se arregla un defecto de la tabla.

#### 11.1.2 El ancho de una columna se calcula, no se adivina

Mira el defecto antes de arreglarlo. La Lección 2 fijó el ancho de la primera columna en 12 caracteres con `f"{nombre:<12}"`, y con los nombres de la muestra (el más largo, `inventario`, tiene 10) quedaba perfecto. Con un nombre largo, el texto se sale de su columna y empuja a todas las demás. La solución es hacer que el ancho **dependa de los datos**: el más largo de los nombres más dos espacios de aire, con un mínimo de 12 para que las tablas cortas se vean como siempre.

Hay una novedad de sintaxis. Una f-string te deja poner el ancho **dentro** de la especificación, con otro par de llaves: `f"{nombre:<{ancho}}"` significa «alinea `nombre` a la izquierda en un campo de `ancho` caracteres», donde `ancho` es una variable. Es lo mismo que `:<12`, con el 12 reemplazado por una variable. Mira cómo queda `formato.py` completo:

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

Tres funciones nuevas o cambiadas. `ancho_servicio` calcula el ancho: una comprensión saca la longitud de cada nombre, `max(..., default=0)` devuelve el mayor (el `default=0` es lo que `max` devuelve si la lista está vacía; sin él, `max([])` lanza `ValueError`), y se le suman dos. `max(ANCHO_MINIMO, ...)` impone el mínimo. `encabezado` y `linea` reciben un `ancho` con valor por omisión `ANCHO_MINIMO`; así, todo código que las llamaba sin ancho (tus pruebas de la Lección 8, por ejemplo) sigue funcionando sin cambios. Y `tabla` junta todo: calcula el ancho **una vez**, arma el encabezado, una línea por resultado, un renglón en blanco y el resumen, y los une con saltos de línea. (`renglones += [...]` agrega al final de la lista todos los elementos de la otra, como varios `append` seguidos; y `"\n".join(...)` es el `join` de la Lección 4 con el salto de línea como separador.) Con los cuatro servicios canónicos, el nombre más largo mide 10, `10 + 2 = 12` y el ancho calculado es 12: la tabla sale **idéntica** a la que tenías, byte por byte. Solo cambia cuando hace falta que cambie.

#### 11.1.3 El JSON como contrato, probado

El segundo cambio es una prueba. Léela completa: no es corta, y su largo es el punto.

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

`CANONICOS` son los cuatro resultados canónicos, armados a mano en la prueba; **no vienen de la red ni del laboratorio**. `test_el_json_es_un_contrato` escribe el JSON esperado entero, campo por campo, como un diccionario, y lo compara con `json.loads(reporte_a_json(CANONICOS))`. Hay dos decisiones que importan. La primera: la prueba compara **lo que significa** el JSON (el diccionario que sale de `json.loads`) y no el **texto** (los espacios y el orden de los renglones), porque a un guion que interpreta JSON le da igual cuántos espacios haya y le importa mucho cuáles son los campos. La segunda: la prueba incluye el caso incómodo, `reportes` con `"tiempo_ms": None` (que en JSON es `null`), y el `promedio_ms` de 843. Si alguien cambia el `0` por el `null`, o quita un campo, o cambia el redondeo del promedio, la prueba se pone roja.

La segunda prueba nueva, `test_la_tabla_se_alinea_con_un_nombre_largo`, añade a los cuatro canónicos un servicio con un nombre de 26 caracteres (`[*CANONICOS, largo]` arma una lista nueva con los elementos de `CANONICOS`, que el asterisco «desempaca» uno por uno, y `largo` al final, sin tocar `CANONICOS`) y comprueba dos cosas: que la palabra `ESTADO` del encabezado empiece en la columna 28 (26 más los 2 de aire) y que en cada renglón de datos, en esa misma columna, haya un estado válido. Para la primera usa `.index(...)`, un método de los textos que busca dónde empieza un pedazo dentro del texto y devuelve su posición, contando desde 0 como los índices de las listas: `lineas[0].index("ESTADO")` es la columna donde arranca `ESTADO` en el encabezado (si no lo encontrara, fallaría con `ValueError`). Ese `renglon[ancho : ancho + 6]` es una rebanada: la sintaxis `[inicio:fin]` toma los caracteres desde la posición `inicio` hasta la anterior a `fin`, así que aquí son los seis que empiezan en la columna del estado, que es lo que mide `"ARRIBA"`. El `in {"ARRIBA", "LENTO ", "CAIDO "}` tiene un espacio al final de `"LENTO "` y de `"CAIDO "` porque esos estados miden cinco caracteres y la rebanada toma seis.

En una prueba como esta vale la pena preguntarse si cumple la vara de la Lección 8: ¿se pone roja si se rompe lo que dice probar? El Ejercicio 2 te pide romper el JSON a propósito y comprobarlo.

### 11.2 `logging`: lo que el programa cuenta de sí mismo

#### 11.2.1 Por qué no `print`

El reporte es **lo que el programa produce**. Pero un programa también tiene cosas que contar sobre **su propio trabajo**: «leí 4 servicios», «el servicio `pagos` respondió en 87 ms». Eso es información para quien está investigando algo raro, no para quien lee el reporte. Si esos mensajes se imprimen con `print` al lado del reporte, quedan mezclados con él: el guion que lee el JSON se encuentra renglones de diagnóstico en medio y deja de poder interpretarlo.

El mundo de Unix resolvió esto hace décadas con dos canales: la **salida estándar** (*stdout*) es para el resultado del programa, y la **salida de error** (*stderr*) es para todo lo demás que el programa tenga que decir sobre sí mismo. Ya los usas: el reporte va por la primera, el `error de configuración: ...` va por la segunda (Lección 7). El módulo [`logging`](https://docs.python.org/3/library/logging.html) de la biblioteca estándar es la forma ordenada de escribir en el segundo canal, con una ventaja sobre `print`: cada mensaje tiene un **nivel** de importancia, y tú decides desde qué nivel quieres oírlos, sin tocar el código que los escribe.

#### 11.2.2 Los niveles y un primer programa

Los niveles, de menos a más grave: `DEBUG` (detalle fino, para quien depura), `INFO` (el programa avanza), `WARNING` (algo raro, pero sigue), `ERROR` (algo falló) y `CRITICAL`. Por omisión, `logging` solo muestra desde `WARNING`. Un **registrador** (*logger*) es el objeto al que le hablas, y se pide por nombre: `logging.getLogger("demo")`. Esta figura muestra todo junto:

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

Línea por línea. `logging.basicConfig(stream=sys.stderr, format=...)` hace la configuración mínima: que los mensajes vayan a `sys.stderr` (la salida de error) y con el formato `NIVEL nombre: mensaje`. `registro.debug(...)` escribe un mensaje de nivel `DEBUG`, y no aparece, porque el nivel por omisión es `WARNING`: ese mensaje está **guardado en el código pero apagado**, que es la gracia. `registro.warning("aviso: %s tardó %s ms", "inventario", 2300)` sí aparece. Fíjate cómo se escribe: el mensaje lleva marcadores `%s` y los valores van **aparte**, como argumentos. Es el formato `%` de las cadenas, el antiguo (`"%s" % x`), que el curso no usa en ningún otro lugar; aquí no lo aplicas tú: `logging` lo aplica por dentro, juntando el mensaje y los valores, y [su documentación](https://docs.python.org/3/howto/logging.html#logging-variable-data) lo pide así. Los valores se pasan por separado para que `logging` solo arme el texto **si el mensaje se va a emitir**; con un `f"..."` el texto se armaría siempre, aunque el nivel esté apagado, y en un programa que registra miles de líneas esa diferencia cuenta. Y `registro.setLevel(logging.DEBUG)` baja el nivel, con lo que el último `debug` ya aparece. El programa imprimió el reporte con `print(..., flush=True)`; el `flush=True` solo obliga a que el texto salga en el momento, para que el orden de la salida documentada sea el mismo que ves en la terminal.

Una advertencia de diseño, que viene de [la guía oficial](https://docs.python.org/3/howto/logging.html): el código de una **biblioteca** (o de un módulo del paquete) nunca configura `logging`; solo pide su registrador y escribe. Quien configura es el **programa principal**, que es quien sabe a dónde deben ir los mensajes. Por eso, en el `revisor`, `basicConfig` vive en `cli.py` y no en `revision.py`.

#### 11.2.3 `--verbose` en el `revisor`

El `revisor` registra, en nivel `DEBUG`, el resultado de cada servicio, y una opción `--verbose` lo enciende. `revision.py` pide el registrador `"revisor"` al principio, y su función `revisar` ahora es un envoltorio: llama a `_consultar` (el cuerpo de siempre, que no cambió) y registra el resultado antes de devolverlo.

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

Fíjate en la separación: `_consultar` hace la consulta; `revisar` la hace y la **cuenta**. Así el registro está en un solo lugar y no repetido en cada `return`. En `cli.py`, tres cambios: la opción `--verbose` (con `action="store_true"`, que significa «si aparece, vale `True`; si no, `False`», sin esperar un valor), una función `configurar_logging` y la llamada a `tabla`:

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

`configurar_logging` hace tres cosas. `basicConfig` conecta el registro a `sys.stderr`. La línea `nivel = logging.DEBUG if verbose else logging.WARNING` es una **expresión condicional**, un `if`/`else` que cabe en una línea y que **da un valor**: se lee «`logging.DEBUG` si `verbose` es verdadero; si no, `logging.WARNING`», y equivale a un `if`/`else` de cuatro líneas que asigne `nivel` en cada rama. Y `logging.getLogger("revisor").setLevel(nivel)` pone el nivel **solo al registrador del `revisor`**: `DEBUG` si pidieron `--verbose`, `WARNING` si no. Esa distinción importa: si hubieras puesto el nivel `DEBUG` en el registrador de **todos** (la raíz), `httpx` y la biblioteca que usa por debajo escribirían cientos de líneas propias, y entre ellas se perdería lo tuyo. Además, cada opción trae ahora su texto de ayuda en español (`help=...`), porque la séptima comprobación pide que `revisor --help` sirva. (Los textos que `argparse` pone por su cuenta, como `options:` y `show this help message and exit`, salen en inglés; son de la biblioteca.)

Mira la diferencia con el laboratorio corriendo (de nuevo, los tiempos varían en tu máquina):

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

Sin `--verbose`, el reporte sale igual que siempre y la salida de error no dice nada. Con `--verbose` el registro aparece **en el otro canal**. Para verlos por separado, redirígelos a archivos distintos (es el Ejercicio 3): el reporte limpio en uno y el registro en otro.

Un último comentario, de oficio. El orden de las líneas de registro es el orden en que los servicios *terminan*, no el de la configuración: `reportes` (que falla de inmediato) sale primero. Es otra razón para que el **reporte** no dependa del registro: el reporte se arma ordenado, desde la lista; el registro es una bitácora de lo que fue pasando. La [entrada del blog sobre telemetría](https://www.habil.mx/es/blog/telemetria-prometheus-loki-tempo-grafana-opentelemetry/) cuenta cómo se juntan, en un sistema de verdad, los registros de muchos programas como este.

> **Aquí termina la primera sesión.** Tienes el reporte final (la tabla que calcula su ancho y el JSON probado como contrato) y el registro con `--verbose`, cada uno en su canal. Antes de la segunda sesión, corre las pruebas y el `revisor` con y sin `--verbose`, redirigiendo cada canal a su archivo. La segunda sesión no agrega código al `revisor`: repasa la seguridad, lo construye e instala con `pipx`, y comprueba uno por uno los siete puntos de «Cómo sabes que terminaste».

### 11.3 Repaso de seguridad: cuatro costumbres

El curso fue sembrando la seguridad donde estaba el riesgo, no en un capítulo aparte: validar lo que llega de fuera (Lección 6), tratar la dirección de `urllib` con cuidado (Lección 9). Esta parte reúne las cuatro costumbres para que las tengas juntas. **No agrega código al `revisor`**: el `revisor` ya aplica la primera y no tiene ninguna de las otras tres. Se explican porque las vas a necesitar en cuanto escribas el siguiente programa, y porque la primera cobra un sentido nuevo ahora que el programa es una herramienta que cualquiera puede instalar.

#### 11.3.1 La dirección que otro escribe

Tu `revisor` hace una petición a la dirección que está en `servicios.toml`. Quien escribe ese archivo decide **a dónde va tu programa**. Si es solo tú, no hay riesgo. Pero un programa se reutiliza, y mañana ese archivo puede venir de otro equipo, de una página web o de un formulario. La Lección 6 puso una defensa: `validar_servicio` solo acepta direcciones `http://` o `https://` que pasan las comprobaciones de `es_url_http` (esquema, servidor, puerto y texto común). No es una validación completa, y por eso la Lección 9 puso una segunda red: si `httpx` rechaza una dirección que pasó, ese servicio sale como «dirección inválida» y los demás se revisan igual. Mira lo que hace la primera defensa con una dirección que no pasa:

```text
$ python -m revisor --config raro.toml
error de configuración: servicio 1: 'url' debe ser una dirección http:// o https:// válida
$ echo $?
2
```

Un archivo con `url = "file:///etc/passwd"` es rechazado antes de hacer nada: sale el mensaje de configuración y el código `2`. Sin esa validación, según la herramienta que hiciera la petición, `file://` podría leer archivos de tu propia máquina. Y hay una variante más sutil que la validación del esquema no cubre: una dirección `http://` que apunta **hacia adentro** de tu red (a un servicio interno o al servicio de metadatos de un servidor en la nube) hace que *tu* programa, que está dentro, consulte algo que el autor de la dirección no podría alcanzar desde fuera. Ese ataque se llama *server-side request forgery* (SSRF) y [OWASP lo describe con detalle](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). Para el `revisor`, que lee un archivo de configuración que tú escribes, es un riesgo bajo; para un servicio web que recibe direcciones de usuarios, es un riesgo central. La regla: **una dirección que viene de fuera es un dato no confiable, y se valida (y se limita a un conjunto permitido) antes de usarse**. La entrada del blog de Hábil sobre [seguridad de APIs](https://www.habil.mx/es/blog/seguridad-apis-cto-identidad-gateway-tokens/) lleva esa regla al nivel de la arquitectura.

#### 11.3.2 `subprocess`: una lista, nunca un texto armado

Algún día tu programa querrá ejecutar otro programa del sistema (`ping`, `git`, `ls`). El módulo [`subprocess`](https://docs.python.org/3/library/subprocess.html) lo hace, y tiene dos formas de recibir el comando, con consecuencias muy distintas. Esta figura usa `echo` (que solo imprime) para que puedas ver la diferencia sin riesgo:

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

En ambos casos, el «nombre» es `catalogo; echo INYECTADO`: un texto donde alguien escribió, después del nombre, un punto y coma y **otro comando**. Con `shell=True`, Python no ejecuta el programa directamente, sino que se lo da al *shell* (el intérprete de la terminal) como un texto para que lo interprete, y el shell entiende `;` como «termina este comando y ejecuta otro». El resultado: se ejecutaron **dos** cosas, y la segunda la eligió quien escribió el nombre. Eso es una *inyección de comandos*. Con una **lista** (`["echo", "revisando", nombre]`) cada elemento es un argumento, el shell no interviene, y el `;` es solo un carácter más del texto. Si el comando hubiera sido `rm` en lugar de `echo`, la diferencia habría sido borrar tus archivos. La documentación de [`subprocess` en su apartado de seguridad](https://docs.python.org/3/library/subprocess.html#security-considerations) pide justo esto; [OWASP lo explica con más ejemplos](https://owasp.org/www-community/attacks/Command_Injection). La regla: **lista de argumentos y sin `shell=True`; si hace falta el shell, el texto que le llega no puede contener nada que viniera de fuera**. El `check=True` hace que un comando que falla lance una excepción en lugar de pasar en silencio.

#### 11.3.3 `eval` y `pickle`: ejecutar lo que llega de fuera

`eval(texto)` toma un texto y lo **ejecuta como código de Python**. Parece cómodo para convertir «2 + 2» en 4, pero hay que ver lo que acepta:

```python
# fig11_03.py
texto_de_afuera = "__import__('sys').version_info.major"

print(eval(texto_de_afuera))
```

```text
$ python fig11_03.py
3
```

El «texto de afuera» es una instrucción que importa un módulo y lee su versión de Python: nada dañino, pero idéntico en forma a lo que haría una instrucción que borre archivos o mande tus datos a otro lado. `eval` no distingue. Cualquier dato que llegue de fuera y pase por `eval` le da a quien lo escribió el control de tu programa. Para convertir texto en datos existen herramientas que **solo** entienden datos: `json.loads` (que usas desde la 6) para JSON, `tomllib.loads` para TOML. Ni siquiera `ast.literal_eval`, la «versión segura» de `eval`, es una defensa completa contra un texto hostil, como advierte [su documentación](https://docs.python.org/3/library/ast.html#ast.literal_eval).

`pickle` es el caso hermano. Es el módulo que guarda objetos de Python en archivo, y su [documentación](https://docs.python.org/3/library/pickle.html) abre con una advertencia en rojo: *no es seguro*, porque deshacer un `pickle` puede ejecutar código arbitrario. Un archivo `pickle` que te manda otra persona es, en la práctica, un programa. Para datos que cruzan fronteras, JSON. No hay figura de `pickle` en el curso porque mostrarlo exige escribir una clase con métodos, y esa pieza no la has visto; con la advertencia basta.

#### 11.3.4 `secrets`, no `random`

El módulo `random` produce números que *parecen* al azar pero que se calculan con una fórmula a partir de una **semilla**: si conoces la semilla, conoces todos los números. Eso es una virtud para una simulación que quieres repetir, y un desastre para una contraseña o un token. Mira las dos cosas juntas:

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

Con la misma semilla (`random.seed(1)`), `random.random()` da **exactamente el mismo número** dos veces: es `True`. Un atacante que adivine la semilla (por ejemplo, la hora en que arrancó el programa) reproduce todos tus «secretos». [`secrets`](https://docs.python.org/3/library/secrets.html) está hecho para lo contrario: toma su azar del sistema operativo, el mismo que usa para las llaves de cifrado. `secrets.token_hex(16)` da 16 bytes aleatorios escritos en hexadecimal, es decir, un texto de 32 caracteres (de ahí el `32`). La [documentación de `random`](https://docs.python.org/3/library/random.html) lo dice en su primera advertencia: no usar para fines de seguridad. La regla: **si el número es un secreto (token, contraseña, identificador que no deben poder adivinar), `secrets`; si no, `random` está bien**.

### 11.4 Construir e instalar

#### 11.4.1 Qué es un paquete instalable

Hasta ahora el `revisor` se ejecuta con `python -m revisor` desde la carpeta del proyecto, y quedó instalado en tu entorno con `pip install -e .` (la instalación **editable** de la Lección 7, que no copia el código sino que apunta a él). Eso sirve para desarrollar. Para entregárselo a otra persona hace falta un **archivo** que contenga el programa ya empacado. En Python ese archivo se llama [*wheel*](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), tiene extensión `.whl` y es, por dentro, un archivo comprimido con tu código y sus datos de instalación (nombre, versión, dependencias, y cuál es el comando que debe crearse). El nombre cuenta una historia: `revisor-1.0.0-py3-none-any.whl` quiere decir «el paquete `revisor`, versión 1.0.0, para cualquier versión de Python 3, sin código compilado, en cualquier sistema».

La versión sube a `1.0.0` en el `pyproject.toml`; es lo único que cambia ahí:

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

Se construye con el instalador de paquetes. Un detalle: no necesitas el paquete `build` ni nada nuevo; `pip` ya sabe construir una *wheel* (el comando es [`pip wheel`](https://pip.pypa.io/en/stable/cli/pip_wheel/)). La opción `--no-deps` le dice que construya **solo tu paquete** y no descargue las dependencias, y `-w dist` que deje el resultado en la carpeta `dist/`. El punto final es «construye el proyecto de esta carpeta». Para armarlo, `pip` descarga por un momento la herramienta de construcción que declaraste en `[build-system]` (`hatchling`): es una dependencia de *construcción*, no de ejecución, y no viaja dentro de la *wheel*.

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

(La salida de `pip wheel` está recortada: los `...` marcan renglones que se quitaron, entre ellos la descarga de `hatchling` y una huella `sha256` larga. El tamaño, `size`, depende de tu código, así que el tuyo puede ser otro; lo que importa es `Successfully built revisor`.)

Dos cosas que leer de aquí. La *wheel* contiene el paquete `revisor` (siete archivos) y su carpeta `dist-info` con los metadatos; **no contiene** `servicios.toml`, ni las pruebas, ni los archivos de laboratorio. Es lo correcto: el programa no trae su configuración, la trae quien lo usa. Y la versión del nombre del archivo, `1.0.0`, salió del `pyproject.toml`.

#### 11.4.2 `pipx`: instalar una herramienta, no una biblioteca

Podrías instalar la *wheel* con `pip install` dentro de un entorno virtual, pero entonces el `revisor` solo existiría mientras ese entorno estuviera activado. Para una **herramienta** que quieres usar desde cualquier carpeta, como `git` o `ruff`, la solución es [`pipx`](https://pipx.pypa.io/stable/). `pipx` crea un entorno virtual **propio para cada herramienta**, instala ahí el paquete con sus dependencias, y deja el comando disponible en tu `PATH`. Cada herramienta queda aislada de las demás y de tu Python del sistema (que, recuerda de la Lección 1, no se debe tocar con `pip`).

En Linux Mint se instala con el gestor de paquetes del sistema: `sudo apt install pipx` (el paquete está en los repositorios de Ubuntu 24.04, la base de Mint 22: [versión 1.4.3](https://packages.ubuntu.com/noble/pipx)), y después `pipx ensurepath`, que agrega la carpeta de los comandos de `pipx` (`~/.local/bin`) a tu `PATH`; abre una terminal nueva para que lo note. Con eso, instalar el `revisor` es una línea. La salida de abajo se obtuvo con una versión de `pipx` y de Python más nuevas que las de tu Mint, así que el texto puede diferir en detalles: lo que importa son las tres últimas líneas. Se quitaron las líneas de preparación del entorno.

```text
$ pipx install dist/revisor-1.0.0-py3-none-any.whl
done!
  installed package revisor 1.0.0, installed using Python 3.14.8
  These apps are now available
    - revisor
```

`pipx` creó el entorno, instaló la *wheel* con sus dependencias (`httpx` y las suyas) y dejó el comando `revisor`. Probarlo desde **otra carpeta** es el punto. Esta corrida es desde una carpeta vacía:

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

Tres cosas. `revisor --version` funciona desde cualquier carpeta y dice `revisor 1.0.0`; recuerda que ese número no está escrito en el código, sino que `cli.py` lo lee de los metadatos del paquete instalado, que salen del `pyproject.toml`. Segunda: `revisor` a secas, desde una carpeta que no tiene `servicios.toml`, termina con el mensaje de configuración y el código `2`. Es la misma lección de la 6 (la ruta relativa depende de dónde estás), y no es un defecto: es lo correcto para una herramienta, que no debe adivinar dónde está tu configuración. Para eso existe `--config`. Y tercera: con un `--config` válido, el reporte sale y el código es `1`, porque hay un servicio `LENTO` y otro `CAIDO`.

#### 11.4.3 Lo que viene, y todavía no es para ti

Dos novedades de Python 3.14 quedan fuera del curso a propósito, y conviene que sepas que existen. La primera es el **intérprete sin GIL** (*free-threaded*): una variante de Python que puede ejecutar código de Python en varios hilos al mismo tiempo; con la 3.14 pasó a ser [oficialmente soportada](https://peps.python.org/pep-0779/), pero sigue siendo una compilación aparte y opcional, y muchas bibliotecas aún no están listas. Para el `revisor` no cambia nada, porque ya hace esperas concurrentes en un solo hilo y no está limitado por el GIL. La segunda son las ***t-strings*** (cadenas de plantilla, [PEP 750](https://peps.python.org/pep-0750/)): se escriben como una f-string pero con una `t` delante, y en lugar de un texto devuelven un objeto que separa lo fijo de lo interpolado, útil para escapar HTML o armar consultas SQL con seguridad. Ninguna de las dos es necesaria para lo que hiciste, ninguna se usa en el curso (y el código del curso tiene que correr en la 3.12 de tu Mint, que no las tiene), y las dos se explican en [la lista de novedades de 3.14](https://docs.python.org/3/whatsnew/3.14.html). Cuando las necesites, ya sabrás leer esa documentación por tu cuenta, que es lo que el curso se propuso.

## Los siete puntos, uno por uno

Aquí se cierra el curso. Cada punto es un comando y una salida; la salida de abajo es la real, de la carpeta `fig11_05/` con el laboratorio corriendo en otra terminal.

### Punto 1 — `pytest` termina en verde y dice cuántas pruebas corrieron

Se corre `pytest -q` y se lee **el conteo del informe**, la última línea. En esta carpeta debe decir `30 passed`: las 27 de la Lección 10 más las tres de hoy (el contrato del JSON, la tabla con un nombre largo y `--version`).

Por qué el conteo y no el código de salida: el código 0 de `pytest` solo dice que *no hubo fallos*, y se puede tener 0 fallos con casi ninguna prueba corriendo. Mira dos casos, medidos. Uno: un archivo con una sola prueba marcada para saltarse.

```text
$ pytest -q tests/test_saltada.py
s                                                                        [100%]
1 skipped in 0.00s
$ echo $?
0
```

Código 0, y `1 skipped`: nada se probó, y todo parece bien. Dos: filtrar por nombre.

```text
$ pytest -q -k sale_con
..                                                                       [100%]
2 passed, 28 deselected in 0.02s
$ echo $?
0
```

También con código 0, pero `2 passed, 28 deselected`: de 30 pruebas corrieron dos. Quien solo mira el color verde o el código no lo nota; quien lee el conteo, sí. La [referencia de códigos de salida de `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) los enumera (hay uno específico, el 5, para «no se recogió ninguna prueba», pero ni siquiera ese protege de un filtro que deja pasar dos). **Regla: el punto 1 se cumple cuando lees `30 passed` y ese 30 es el número que esperabas.**

### Puntos 2 y 6 — la calidad, y que corra igual en 3.14 y en 3.12

Se corren las cuatro herramientas de calidad, con cada versión de Python. Primero con 3.14:

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

Y exactamente lo mismo con 3.12, que es el de tu Mint:

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

La única diferencia es la línea de `python --version`. `ruff check` y `ruff format --check` no reportan nada (revisan 13 archivos, el laboratorio incluido) y `mypy` dice `Success`. Las 30 pruebas pasan en las dos. Para repetir esto en tu Mint: el Python del sistema (3.12) ya lo tienes en tu entorno de siempre. Si instalaste 3.14 con `uv` (el recuadro de la Lección 7), crea un segundo entorno con él (`python3.14 -m venv .venv314`), actívalo e instala el proyecto y las herramientas con las versiones de `herramientas/requisitos.txt`, y corre los mismos cuatro comandos. Si no instalaste 3.14, el punto 6 se cumple *para la versión que tienes*, y la otra mitad la compruebas tú cuando quieras: instalas 3.14 con `uv` y repites estos cuatro comandos. Nadie la comprueba por ti; la salida de arriba es la de una corrida en las dos versiones, y lo que vale es la tuya.

### Punto 3 — 20 servicios a la vez, en el tiempo del más lento

Con los veinte servicios de medio segundo (`servicios-20.toml`), en fila y con todos a la vez:

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

En fila (`--concurrencia 1`): 10.2 segundos, la suma. Con `--concurrencia 20`: 0.61, cerca del más lento (0.5) más el arranque de Python. **El punto 3 se cumple** porque el tiempo no es la suma de las esperas: es del orden de la espera más larga. Si tu máquina marca unos centésimos de más, no importa; lo que importa es que sean unas dieciséis veces menos.

### Punto 4 — un servicio caído, lento o que contesta basura no tumba el reporte

Con el laboratorio ya lo viste en cada corrida: `reportes` está caído, `inventario` es lento, y los otros dos salen completos. Falta el tercer tipo, el que **contesta basura**: algo que responde, pero no con HTTP válido. Eso no se puede pedir al laboratorio, pero sí a un transporte de mentira (Lección 10), que puede lanzar la excepción que `httpx` lanza ante una respuesta que no es HTTP (`httpx.RemoteProtocolError`). Esta figura junta cinco tipos de servicio en una sola corrida: uno sano, uno lento, uno que contesta basura, uno que devuelve 503 y uno colgado de verdad (espera 30 segundos con un tiempo límite de medio segundo).

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

Este programa **importa el paquete** `revisor`: corre con el entorno donde instalaste el proyecto (`pip install -e .` en la carpeta `fig11_05/`). Los seis servicios salen en el reporte, en su orden, cada uno con lo suyo: `lento` es `LENTO` (1.1 s), `basura` aparece como `CAIDO` con detalle `error de red`, `caido` trae su `503`, y `colgado` se rindió con `tiempo agotado` sin esperar los 30 segundos. Ninguno tumbó a los demás. Y no es solo cosa de la simulación: si un servidor de verdad contesta algo que no es HTTP (por ejemplo, un programa que escucha en un puerto y responde un texto cualquiera), `httpx` lanza un error de protocolo, que es un `httpx.HTTPError`, y el `revisor` lo reporta igual, como `error de red`. Los `0ms` de `catalogo` y `pagos` son porque el transporte de mentira contesta al instante; con red real serían decenas o cientos. **El punto 4 se cumple.**

### Punto 5 — ninguna petición espera para siempre

Dos comprobaciones. La primera, en el código: ¿cuántos lugares hacen una petición, y están todos protegidos?

```text
$ grep -rn "cliente.get" src/revisor
src/revisor/revision.py:19:            respuesta = await cliente.get(servicio.url, timeout=limite)
```

Una sola petición en todo el paquete, y está dentro de `async with asyncio.timeout(...)` y con `httpx.Timeout(...)` (lo viste en `revision.py`). La segunda, con la corrida: un servicio del laboratorio que tarda 10 segundos con `timeout_ms = 1000`, y otro que tarda 8 segundos **sin** `timeout_ms` en la configuración (usa el valor por omisión, 5000):

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

El primero se rinde a los 1.1 segundos; el segundo, a los 5.1. Ninguno esperó lo que el servidor quería. **El punto 5 se cumple**, también para quien olvida poner el tiempo límite en su configuración, porque el valor por omisión de `Servicio` es 5000 ms.

### Punto 7 — se instala con `pipx` y se usa desde otra carpeta

Ya lo hiciste en 11.4: `pipx install`, `revisor --version` y `revisor --help` desde una carpeta cualquiera. Falta comprobar el contrato de los códigos de salida: **0 si todo está arriba, 1 si no**. Con los cuatro servicios del laboratorio ya viste el 1. Con un archivo que solo tiene `pagos`:

```text
$ revisor --config bien.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA     102ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 102ms
$ echo $?
0
```

Código 0. Y `revisor --help` funciona desde cualquier carpeta y muestra la ayuda de las opciones con el texto en español que les pusiste en 11.2.3. **El punto 7 se cumple.**

Con los siete cumplidos, el `revisor` está terminado en el sentido que el curso definió al principio. No porque sea perfecto, sino porque lo que dice que hace, **lo hace y puedes comprobarlo**.

## El proyecto completo

Los archivos de la carpeta `fig11_05/` que no cambiaron en esta lección están aquí para que la carpeta esté completa y se pueda correr:

<details>
<summary>Los archivos que no cambian en esta lección</summary>


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

Y `tests/test_cli.py`, que cambió: ganó la prueba de `--version`.

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

La prueba nueva usa `capsys`, una herramienta de `pytest` hermana de `tmp_path` y `monkeypatch`: recoge lo que el programa **imprime** durante la prueba, para poder comprobarlo. Su anotación, `pytest.CaptureFixture[str]`, se lee como las de colecciones de la Lección 4: `CaptureFixture` es el tipo de esa herramienta, y `[str]` dice que lo que recoge es texto, igual que `list[str]` dice que la lista guarda textos. `main(["--version"])` imprime `revisor 1.0.0` y termina el programa con `SystemExit` (así funciona `argparse` con `--version`), de modo que la prueba lo recibe con `pytest.raises(SystemExit)` (que comprueba que el bloque lance esa excepción, y con `as salida` te deja mirarla) y luego lee lo impreso con `capsys.readouterr().out`. Hay una trampa en esta prueba que conviene conocer: el número `1.0.0` no sale del código sino de los **metadatos del paquete instalado**, así que depende de cuándo instalaste.

## El error que vas a ver

### `AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'`

Subiste la versión en `pyproject.toml` a `1.0.0`, corriste las pruebas y la de `--version` se puso roja diciendo que la versión es la vieja:

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

Léelo de abajo hacia arriba: la prueba esperaba `revisor 1.0.0` y el programa dijo `revisor 0.9.0`. Pero tú **ya cambiaste** el `pyproject.toml`. ¿De dónde sale entonces el `0.9.0`? De los metadatos de la instalación editable que hiciste antes: se generan al instalar, no al cambiar el archivo. El `pyproject.toml` es la receta; la instalación es el plato ya servido. La solución es volver a instalar:

```text
$ pip install -e .
$ pytest -q tests/test_cli.py
...                                                                      [100%]
3 passed in 0.02s
```

La regla: **cuando cambias algo que el instalador lee (el nombre, la versión, los comandos), vuelve a instalar**. Esto no es un defecto de `pip`, es una consecuencia de que la versión viva en un solo lugar (`pyproject.toml`), como se decidió en la Lección 7 para no repetir el número en dos archivos.

### `bash: revisor: command not found`

Instalaste con `pipx`, abres una terminal y escribes `revisor`:

```text
bash: revisor: command not found
```

El comando no se encuentra porque la carpeta donde `pipx` deja los comandos (`~/.local/bin`) no está en tu `PATH`, que es la lista de carpetas donde la terminal busca los programas. Se arregla con `pipx ensurepath` y **abriendo una terminal nueva**: el cambio se aplica solo a las terminales que se abren después. (El texto exacto del error cambia de una terminal a otra; Linux Mint puede sugerirte instalar un paquete con ese nombre, y no es lo que quieres.)

### `error de configuración: no existe el archivo servicios.toml`

Es el de la Lección 6, y reaparece al correr `revisor` desde una carpeta sin configuración (lo viste en 11.4.2). No hay nada que arreglar en el código: pasa `--config` con la ruta, o corre el comando desde la carpeta donde está tu `servicios.toml`.

## Lo que se hace mal

**Dejar que la versión viva en dos sitios.** El número en `pyproject.toml` y otro escrito a mano en `cli.py` terminan por diferir. El `revisor` lo lee del paquete instalado. Costo: un `--version` que miente.

**Mezclar el registro con el reporte.** Imprimir diagnósticos con `print` entre las líneas del reporte. Costo: el guion que lee el JSON recibe basura y deja de funcionar. El reporte va por la salida estándar; lo demás, por `logging` a la salida de error.

**Configurar `logging` dentro de un módulo del paquete.** Si `revision.py` llamara a `basicConfig`, importar el módulo cambiaría el comportamiento del programa que lo importa. Costo: dos configuraciones peleando. Se configura en un solo lugar, en el punto de entrada.

**Poner `DEBUG` en el registrador de todos.** Se llena de líneas de `httpx` y lo tuyo se pierde. Se sube el nivel solo al registrador propio.

**Usar un `f"..."` en un mensaje de `logging`.** Arma el texto aunque el nivel esté apagado. Costo: trabajo desperdiciado en cada mensaje, que se nota cuando son miles.

**Cambiar el formato del JSON sin avisar.** Renombrar un campo, cambiar el `null` por un `0`, reordenar sin motivo. Costo: todo lo que lee ese JSON se rompe. Si el contrato cambia, se sube la versión mayor y se avisa.

**`subprocess` con `shell=True` y un texto armado con datos de fuera.** Costo: que otro ejecute comandos en tu máquina.

**`eval` o `pickle` con datos que no son tuyos.** Costo: lo mismo.

**`random` para un secreto.** Costo: un token que otro puede reconstruir.

**Dar por terminado un programa que nadie ha instalado como lo instalaría un usuario.** Funciona en el entorno de desarrollo y falla en la instalación porque falta un archivo o una dependencia. Se construye la *wheel* y se prueba **desde otra carpeta**, no desde el código.

**Leer solo el color de `pytest`.** El verde con 2 pruebas de 30 es un verde. Se lee el conteo.

## Ejercicios

### Ejercicio 1 — Un nombre largo de verdad

Escribe un `servicios-largo.toml` con dos servicios que apunten al laboratorio: `catalogo` y otro llamado `notificaciones-de-clientes` (26 caracteres). **Antes de correr**, predice en qué columna empezará `ESTADO` y córrelo. Comprueba que la tabla queda alineada.

### Ejercicio 2 — Rompe el contrato

En una copia de `fig11_05/`, renombra en `formato.py` el campo `"caido"` del resumen del JSON a `"caidos"`. Corre `pytest -q --tb=short`. Anota cuántas pruebas se ponen rojas y cuál. Repara y vuelve a correr. Responde: ¿qué habría pasado con un guion que lee `resumen.caido` si nadie hubiera tenido esa prueba?

### Ejercicio 3 — Dos canales, dos archivos

Corre `python -m revisor --verbose` redirigiendo la salida estándar a `reporte.txt` y la de error a `registro.txt` (en el shell, `> archivo` redirige la estándar y `2> archivo` la de error). **Antes de correr**, predice qué habrá en cada archivo. Después mira su contenido.

### Ejercicio 4 — Un renglón de registro más

Agrega al `revisor` un mensaje de nivel `DEBUG` en `main` que diga cuántos servicios se leyeron de la configuración. Debe aparecer con `--verbose` y no sin él. Comprueba que las 30 pruebas siguen pasando, y que `ruff` y `mypy` siguen sin reportar nada.

## Soluciones

### Solución 1

El nombre más largo mide 26; con los dos espacios de aire el ancho es 28, así que `ESTADO` empieza en la columna 28 (contando desde 0). La corrida:

```text
$ python -m revisor --config servicios-largo.toml
SERVICIO                    ESTADO    TIEMPO  DETALLE
catalogo                    ARRIBA     172ms  200
notificaciones-de-clientes  ARRIBA      94ms  200

2 servicios · 2 arriba · 0 lentos · 0 caídos · promedio 133ms
```

La palabra `ESTADO` queda alineada con `ARRIBA` en las dos filas, y `catalogo` tiene su columna ensanchada igual que el otro. Con los servicios de siempre, el ancho vuelve a ser 12.

### Solución 2

Se pone roja **una** prueba, `test_el_json_es_un_contrato`; las otras 29 pasan:

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

La prueba te dice cuál campo cambió (`'caidos': 1` contra `'caido': 1`). Sin ella, un guion que leyera `resumen.caido` habría recibido un campo inexistente (`null` o un error, según el lenguaje del guion) y habría seguido, en el mejor caso, tratando «0 caídos» como un buen resultado, justo cuando hay un servicio caído. Es la clase de error que no da la cara hasta el peor día.

### Solución 3

En `registro.txt` van las cuatro líneas `DEBUG revisor: ...` (el canal de error); en `reporte.txt`, la tabla con su resumen (el canal estándar). Ninguna cosa se mezcla con la otra:

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

### Solución 4

En `cli.py`, justo antes de `asyncio.run(...)`:

```python
logging.getLogger("revisor").debug("leídos %s servicios", len(servicios))
```

El módulo `logging` ya está importado. Resultado, medido (la línea nueva sale primero, porque se escribe antes de consultar nada):

```text
$ python -m revisor --verbose 2>&1 >/dev/null | head -n 2
DEBUG revisor: leídos 4 servicios
DEBUG revisor: reportes: CAIDO, —, sin conexión
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
```

La primera orden necesita una lectura con calma, porque el orden de las redirecciones importa y se aplican de izquierda a derecha. `2>&1` dice «manda la salida de error (el canal 2) a donde hoy va la estándar (el canal 1)», que en ese momento es la tubería `|` hacia `head`. Después, `>/dev/null` manda la salida **estándar** a la basura. Resultado: lo que llega a `head` es solo el registro, que salía por el canal de error, y el reporte se descarta. Y `head -n 2` muestra solo las dos primeras líneas de lo que recibe. Si escribieras las dos redirecciones al revés, `>/dev/null 2>&1`, las dos salidas irían a la basura y no verías nada.

Las 30 pruebas siguen pasando, y `ruff check`, `ruff format` y `mypy` no dicen nada.

## Cómo sé que lo logré

- [ ] `pytest -q` en `fig11_05/` termina con `30 passed`, y ese es el número que esperabas.
- [ ] `ruff check`, `ruff format --check` y `mypy` no reportan nada; los cuatro comandos dan el mismo resultado con Python 3.12 (y con 3.14 si lo tienes).
- [ ] Con `servicios-20.toml`, `--concurrencia 1` tarda cerca de 10 segundos y `--concurrencia 20`, menos de uno.
- [ ] `fig11_06.py` muestra seis servicios en su orden, con `LENTO`, `error de red`, `503` y `tiempo agotado` en sus filas, y ninguno tumba a los demás.
- [ ] Un servicio que tarda 10 segundos con `timeout_ms = 1000` se reporta como `tiempo agotado` en poco más de un segundo, y otro sin `timeout_ms` en poco más de cinco.
- [ ] `python -m pip wheel --no-deps -w dist .` produce `dist/revisor-1.0.0-py3-none-any.whl`, y `pipx install` de ese archivo deja el comando `revisor`.
- [ ] Desde una carpeta que no es la del proyecto, `revisor --version` dice `revisor 1.0.0`, `revisor --help` muestra la ayuda de las opciones y `revisor --config servicios.toml` termina con `echo $?` igual a `1` (hay servicios `LENTO` y `CAIDO`) o a `0` (todos arriba).
- [ ] Sabes explicar por qué el reporte va a la salida estándar y el registro a la de error; por qué el JSON se prueba como contrato; y por qué `subprocess` recibe una lista, `eval` no se usa con datos de fuera y los secretos salen de `secrets`.

## Resumen

Responde sin mirar la lección:

1. ¿Qué dos cosas hacen que el JSON del `revisor` sea un contrato, y qué prueba lo protege?
2. ¿Cómo se calcula el ancho de la primera columna? ¿Por qué con los cuatro servicios canónicos la tabla sale idéntica a la de antes?
3. ¿Qué diferencia hay entre la salida estándar y la salida de error? ¿Por qué el reporte va a una y el registro a la otra?
4. ¿Por qué un mensaje de `logging` lleva `%s` y los valores aparte, y no una f-string?
5. ¿Por qué `basicConfig` está en `cli.py` y no en `revision.py`? ¿Por qué el nivel se pone al registrador `"revisor"` y no al de todos?
6. ¿Qué pasa con `subprocess.run(f"echo {x}", shell=True)` si `x` trae un `;`? ¿Y con una lista?
7. ¿Por qué `random` no sirve para un token y qué usas en su lugar?
8. ¿Qué contiene una *wheel* y qué no? ¿Por qué se instala una herramienta con `pipx` y no con `pip` en el Python del sistema?
9. ¿Por qué la prueba de `--version` se puede poner roja aunque hayas cambiado el `pyproject.toml`? ¿Cómo se arregla?
10. Enumera, de memoria, las siete comprobaciones con que se termina el curso y el comando de cada una.

## Para leer más

- [Documentación de `logging` y su guía básica](https://docs.python.org/3/howto/logging.html) — niveles, registradores y configuración, con el patrón correcto para bibliotecas y programas. Consultado el 7 de octubre de 2026.
- [Guía de empaquetado de Python: escribir el `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) y [`pipx`](https://pipx.pypa.io/stable/) — la fuente de todo el último tramo: qué va en el `pyproject.toml`, qué es una *wheel* y cómo se instalan las herramientas. Consultado el 7 de octubre de 2026.
- [Documentación de `subprocess`: consideraciones de seguridad](https://docs.python.org/3/library/subprocess.html#security-considerations) y [`secrets`](https://docs.python.org/3/library/secrets.html) — las dos advertencias oficiales de 11.3 con sus ejemplos. Consultado el 7 de octubre de 2026.
- [Novedades de Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — el intérprete sin GIL, las *t-strings* y el resto de lo nuevo, para leer cuando el curso quede atrás. Consultado el 7 de octubre de 2026.
