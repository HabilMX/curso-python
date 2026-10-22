# Lección 9 — HTTP y asyncio

**Tiempo:** 2 × 90 min (la primera sesión llega hasta el final de 9.2; la segunda cubre 9.3, 9.4 y 9.5)

**Qué construyes:** el `revisor` que consulta servicios de verdad, uno tras otro, con tiempo límite en cada petición

**Qué aprendes:** pedir una página con `urllib` y con `httpx`; qué dice un código de estado; por qué toda petición lleva tiempo límite; corrutinas (`async def`, `await`, `asyncio.run`, `async with`); y por qué un `await` solo, sin nadie más, no hace nada más rápido

**De dónde vienes.** Traes el paquete de la [Lección 8](08-pruebas-tipos-calidad.md): el `revisor` con 21 pruebas, sus tipos revisados y su estilo vigilado. Pero hay una verdad incómoda en ese paquete: **nunca ha consultado a nadie**. Las cifras de la tabla (142 ms, 2.3 s, 87 ms) salen de un diccionario, `SIMULADO`, que tú mismo escribiste; el programa te devuelve lo que le dijiste que dijera. Hoy lo cambias por una consulta real: el `revisor` le hace una petición a cada servicio, cronometra cuánto tarda en contestar y clasifica lo que recibe. Para practicar sin molestar a ningún servicio de verdad, la lección te da un servidor de práctica que corre en tu propia computadora.

**Qué no hace esta lección.** Todavía no consulta a los servicios **a la vez**: lo hace uno tras otro, y la lección te enseña a medir cuánto cuesta eso. Juntarlos es la [Lección 10](10-concurrencia-pruebas-sin-red.md). Y el código nuevo, el que usa la red, **no tiene prueba**: el proyecto sigue teniendo las 21 pruebas de la Lección 8, y la lección te lo dice de frente en vez de esconderlo. Probar código de red sin red es el tema de la Lección 10.

## Al terminar vas a poder

- Explicar qué es una petición HTTP, qué contiene una respuesta y qué significan los códigos de estado `2xx`, `4xx` y `5xx`.
- Pedir una dirección con `urllib.request` y con `httpx`, y decir en qué se diferencian cuando el servidor contesta `503` y cuando no contesta.
- Explicar por qué `urllib` acepta una dirección `file://`, y por qué la validación de la Lección 6 evita que el `revisor` lea archivos de tu computadora.
- Ponerle tiempo límite a una petición, saber qué excepción se lanza cuando se acaba y cuál cuando no hay a quién llamar.
- Escribir una corrutina con `async def`, ejecutarla con `asyncio.run` y esperar a otra con `await`, y explicar por qué llamar a una corrutina **no** la ejecuta.
- Medir con el reloj que consultar los servicios uno tras otro tarda la suma de sus tiempos, y explicar por qué un `await` solo no lo acelera.
- Leer el aviso `coroutine ... was never awaited` y el mensaje de `mypy` «Maybe you forgot to use "await"?».

## El porqué antes del cómo

Imagina que le preguntas a un compañero de oficina si el sistema de pagos está funcionando. Tiene que hacer algo parecido a lo que hace tu navegador cuando abres una página: preguntar a esa máquina por una dirección y esperar la contestación. La pregunta se llama **petición** y la contestación, **respuesta**. Ambas siguen un lenguaje común, **HTTP**, que es el que usa toda la web. Una petición dice, en esencia, «dame lo que hay en esta dirección» (el método `GET`, más la dirección). Una respuesta trae tres cosas: un **código de estado**, un número de tres cifras que resume cómo salió todo; unas **cabeceras**, datos sobre la respuesta (qué tipo de contenido es, cuánto mide); y un **cuerpo**, el contenido mismo.

Lo que más te importa de la respuesta es el código, y su primera cifra lo clasifica. [El estándar de HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) los agrupa en cinco familias: los `1xx` son informativos, los `2xx` quieren decir que salió bien (`200` es «aquí está»), los `3xx` son redirecciones, los `4xx` son errores de quien pregunta (`404`: esa dirección no existe) y los `5xx` son errores del servidor (`503`: ahora mismo no puedo atenderte). Para el `revisor`, un servicio puede terminar de **tres formas** distintas, y cada una acaba en una fila de la tabla:

| Qué pasó | Qué ve el `revisor` | Cómo queda en la tabla |
|---|---|---|
| El servicio contestó con un código menor que 400 (`2xx`, o un `3xx`) | un código y un tiempo | `ARRIBA`, o `LENTO` si tardó 1000 ms o más |
| Contestó con un código `4xx` o `5xx` | un código y un tiempo | `CAIDO`, con el código en el detalle (`503`) |
| No contestó | una excepción: no se pudo conectar, o se acabó el tiempo | `CAIDO`, con `sin conexión` o `tiempo agotado` |

Los `3xx` caen en la primera fila a propósito. Una redirección dice «lo que buscas está en otra dirección», y `httpx` [no la sigue por omisión](https://www.python-httpx.org/quickstart/#redirection-and-history): devuelve la respuesta tal cual, con su código. Para el `revisor`, que un servicio conteste con una redirección quiere decir que está vivo y contestando, y la regla de siempre (caído solo con `400` o más) lo cuenta como arriba, con el código en el detalle para que lo veas.

Esa tabla es todo el diseño de la lección. (HTTP es el estilo más común para que dos programas se hablen, pero no el único; si te interesa qué viene después de «pedir una dirección y leer lo que contesta», el blog de Hábil compara dos estilos en [REST o gRPC: cuándo conviene cada uno](https://www.habil.mx/es/blog/rest-o-grpc-cuando-conviene-cada-uno/).) El resto es cómo se hace cada fila sin que el programa se caiga: la tercera, sobre todo, porque un servicio que no contesta es justo el caso que el `revisor` existe para detectar, y no puede ser el caso que lo tumbe.

La lección tiene dos mitades. En la primera sesión haces una consulta bien hecha: primero con la biblioteca que viene con Python, `urllib`, para ver cómo es una petición por dentro, y luego con `httpx`, la que usa el curso. Aprendes que **toda petición lleva un tiempo límite**. En la segunda sesión llegas a las **corrutinas**, la herramienta de Python para esperar sin quedarte parado, y pones el `revisor` a consultar de verdad. Es el salto conceptual más grande del curso; por eso el ritmo de esta lección es lento a propósito.

### El servidor de práctica

El `revisor` necesita a quién preguntarle. Los nombres `catalogo.example` o `pagos.example` que usaste hasta ahora son direcciones inventadas: el sufijo `.example` está [reservado para ejemplos](https://www.rfc-editor.org/rfc/rfc2606) y nunca existe en internet. Para que cada servicio conteste de verdad, y siempre igual, la lección incluye `laboratorio.py`, un pequeño servidor que corre **en tu computadora** y finge ser los servicios del curso.

Aquí está el archivo completo. **Tómalo como una caja negra: se usa, no se escribe.** Está construido con una clase y métodos, cosas que este curso no enseña, y entenderlo no es necesario para nada de lo que sigue. Cópialo tal cual a `~/curso-python/revisor/laboratorio.py`. Cuando termines el curso puedes volver a leerlo; la biblioteca que usa, [`http.server`](https://docs.python.org/3/library/http.server.html), es parte de Python.

```python
# fig09_11/laboratorio.py
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

Lo que importa de él es qué contesta cada ruta, que es lo que dicen la tabla `RUTAS` y la función `buscar_ruta`. (La clase `Servidor` solo cambia un número, `request_queue_size`: cuántas conexiones pueden esperar turno a la vez para ser atendidas. El valor de fábrica, 5, se queda corto cuando en la Lección 10 el `revisor` abra veinte conexiones de golpe, y las que no caben en la fila serían rechazadas como si el servicio estuviera caído.)

| Ruta | Qué contesta | Cuánto tarda |
|---|---|---|
| `/catalogo` | `200` | 142 ms |
| `/inventario` | `200` | 2300 ms |
| `/pagos` | `200` | 87 ms |
| `/facturacion` | `503` | 95 ms |
| `/notificaciones` | `200` | 10 segundos |
| `/espera/<ms>` | `200` | los milisegundos que pongas en lugar de `<ms>` |

Son los mismos números de la tabla del temario, ahora producidos por un servidor de verdad. La dirección es `127.0.0.1`, que significa «esta misma computadora», así que lo que ocurre en la lección no sale de tu máquina. Hay una sola excepción, y casi seguro no te toca: si en tu terminal hay configurado un **proxy** (un intermediario por el que pasan las peticiones, común en algunas redes de oficina, y que se nota porque existen variables como `HTTP_PROXY` o `ALL_PROXY`, en mayúsculas o en minúsculas; `env | grep -i proxy` te las muestra), las peticiones a `127.0.0.1` también se van al proxy, y la práctica falla. `httpx` hace caso de `HTTP_PROXY`, `HTTPS_PROXY` y `ALL_PROXY`; `urllib`, solo de las dos primeras. Se arregla diciéndoles que esa dirección no pasa por el proxy, con `export NO_PROXY=127.0.0.1` en cada terminal donde corras los programas; la [documentación de `httpx`](https://www.python-httpx.org/environment_variables/) explica esas variables. El puerto `8099` es el «número de ventanilla» en que escucha. Y hay una trampa deliberada: el puerto **`8098` no lo atiende nadie**. Ahí vive el servicio `reportes`: preguntarle a una ventanilla donde no hay nadie es la forma más fiel de simular un servicio caído, y siempre sale igual.

Antes de cada ejercicio de esta lección, enciende el servidor **en una segunda terminal** (con el entorno virtual activado, desde `~/curso-python/revisor/`) y déjalo abierto:

```text
laboratorio en http://127.0.0.1:8099 (Ctrl+C para detenerlo)
```

Esa línea es lo único que imprime; cuando termines de practicar, `Ctrl`+`C` en esa terminal lo detiene. Si por error lo dejas apagado, ya verás qué pasa: está en «El error que vas a ver». En la terminal de siempre sigues corriendo los programas de la lección.

## Los conceptos

### 9.1 HTTP: pedir una dirección y leer lo que contesta

#### 9.1.1 Con la biblioteca que ya trae Python

`urllib.request` viene con Python; no hay que instalar nada. Su función principal, [`urlopen`](https://docs.python.org/3/library/urllib.request.html), recibe una dirección, hace la petición y devuelve la respuesta como un objeto que se puede usar con `with` (el mismo `with` de la Lección 6, que cierra la conexión al terminar). Pídele el catálogo al servidor de práctica:

```python
# fig09_01.py
import time
from urllib.request import urlopen

inicio = time.perf_counter()
with urlopen("http://127.0.0.1:8099/catalogo") as respuesta:
    print(respuesta.status, respuesta.reason)
    cuerpo = respuesta.read()
print(cuerpo)
print(cuerpo.decode("utf-8"))
tardo_ms = (time.perf_counter() - inicio) * 1000
print(f"tardó 142 ms o más: {tardo_ms >= 142}")
```

```text
$ python fig09_01.py
200 OK
b'ok'
ok
tardó 142 ms o más: True
```

Línea por línea. `respuesta.status` es el código de estado, `200`, y `respuesta.reason` es la frase que lo acompaña, `OK`. `respuesta.read()` devuelve el cuerpo, y lo que sale en la segunda línea, `b'ok'`, tiene una `b` delante que conviene explicar: la red no transporta texto sino **bytes**, números de 0 a 255, y `read()` te los entrega tal cual. Para convertirlos en texto hay que decir con qué codificación se escribieron, que es el mismo UTF-8 de la Lección 6: `cuerpo.decode("utf-8")` da el `str` normal, `ok`. La última línea comprueba el tiempo. [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) es el reloj de alta precisión de Python: devuelve los segundos como un decimal, y restar dos lecturas da lo que tardó lo que hay entre ellas. El servidor se toma 142 ms para contestar el catálogo, así que la petición no pudo tardar menos. Imprimir el tiempo exacto haría que cada ejecución diera un número distinto; el `True` es lo que no cambia.

Fíjate en lo que **no** hay en este programa: ningún tiempo límite. Lo corregirás en 9.2, pero apúntalo desde ahora como una promesa pendiente.

#### 9.1.2 Los códigos de estado, y las dos excepciones de `urllib`

Pedir el catálogo es el caso feliz. El `revisor` tiene que sobrevivir a los otros dos: el servicio que contesta con un error y el que no contesta. Este programa consulta uno de cada tipo:

```python
# fig09_02.py
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DIRECCIONES = {
    "catalogo": "http://127.0.0.1:8099/catalogo",
    "facturacion": "http://127.0.0.1:8099/facturacion",
    "reportes": "http://127.0.0.1:8098/",
}

for nombre, direccion in DIRECCIONES.items():
    try:
        with urlopen(direccion) as respuesta:
            print(nombre, "respondió", respuesta.status)
    except HTTPError as error:
        print(nombre, "respondió con un error", error.code)
    except URLError as error:
        print(nombre, "no se pudo conectar:", type(error.reason).__name__)
```

```text
$ python fig09_02.py
catalogo respondió 200
facturacion respondió con un error 503
reportes no se pudo conectar: ConnectionRefusedError
```

`catalogo` salió como se esperaba. Pero `facturacion`, que contesta `503`, **no devolvió una respuesta: lanzó una excepción**, `HTTPError`, y por eso entró al primer `except`. Es una decisión de diseño de `urllib` que sorprende al principio: para esta biblioteca, un código `4xx` o `5xx` es una excepción, y el código que lleva se lee en `error.code`. Y `reportes`, donde nadie escucha, lanzó `URLError`, que trae en `error.reason` la causa real. Aquí es `ConnectionRefusedError` (la conexión fue rechazada). Fíjate en que el programa imprime solo el **nombre** de la causa, `type(error.reason).__name__` (`type` da la clase del valor, la de la Lección 2, y `__name__` su nombre como texto), y no el mensaje. El mensaje del sistema operativo cambia entre computadoras (en Linux dice `[Errno 111]`, en macOS `[Errno 61]`), y el curso decidió que el detalle que muestra el `revisor` nunca sea ese texto: dice `sin conexión`, igual en todas partes.

El **orden** de los `except` importa y es el mismo problema de la Lección 6. [`HTTPError` es una subclase de `URLError`](https://docs.python.org/3/library/urllib.error.html): todo `HTTPError` es también un `URLError`. Si pusieras el `except URLError` primero, atraparía todo y el `except HTTPError` de abajo nunca se ejecutaría. La regla es la de siempre: **lo más específico primero**.

#### 9.1.3 Una dirección que no es de internet: `file://`

Hay una sorpresa en `urlopen`, y tiene que ver con seguridad. Una dirección empieza con un **esquema**, la parte antes de `://`: `http`, `https`, y también `file`, que significa «un archivo de esta misma computadora». `urlopen` entiende el esquema `file`:

```python
# fig09_03.py
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

archivo = Path("secreto.txt")
if archivo.exists():
    raise SystemExit("ya existe secreto.txt en esta carpeta; este ejemplo no lo pisa")
archivo.write_text("contraseña: 12345\n", encoding="utf-8")
direccion = archivo.resolve().as_uri()

with urlopen(direccion) as respuesta:
    print("urlopen leyó:", respuesta.read().decode("utf-8").strip())

esquema = urlsplit(direccion).scheme
print("esquema:", esquema, "| lo acepta el revisor:", esquema in {"http", "https"})
archivo.unlink()
```

```text
$ python fig09_03.py
urlopen leyó: contraseña: 12345
esquema: file | lo acepta el revisor: False
```

El programa crea un archivo `secreto.txt` (y lo borra al final con `unlink()`, para no dejar nada). Como lo va a sobrescribir y después a borrar, antes pregunta si ya existe uno con ese nombre: si existe, se detiene sin tocarlo, con `raise SystemExit(...)`, la misma excepción de la Lección 7, que esta vez lleva un texto en lugar de un número; Python imprime ese texto en la salida de error y termina con código 1. Después toma la ruta absoluta del archivo con `resolve()`, arma su dirección con [`.as_uri()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.as_uri) (que produce algo como `file:///home/tu/secreto.txt`) y se la da a `urlopen`, que **lo lee sin protestar**. Es una función legítima, pero imagina el `revisor` leyendo direcciones de un `servicios.toml` que alguien más escribió, y alguien pone `file:///etc/passwd` en lugar de la dirección de un servicio: el programa leería el archivo y lo trataría como una «respuesta». Por eso en la Lección 6 la validación exigía que el esquema fuera `http` o `https`, con [`urlsplit(url).scheme`](https://docs.python.org/3/library/urllib.parse.html) dentro de `{"http", "https"}`; la última línea de este programa hace esa misma comprobación y contesta `False` para `file`. No es un detalle de estilo: **la dirección que otro escribe no se le entrega a una biblioteca sin comprobar a dónde apunta**. Es la segunda vez que ves la idea, y en la Lección 11 la repasarás.

#### 9.1.4 Por qué el curso pasa a `httpx`

`urllib` sirve, pero la propia documentación de Python [recomienda otra herramienta para algo más cómodo](https://docs.python.org/3/library/urllib.request.html) («The Requests package is recommended for a higher-level HTTP client interface»). Este curso usa [`httpx`](https://www.python-httpx.org/), por cuatro razones concretas que verás en esta lección:

| | `urllib.request` | `httpx` |
|---|---|---|
| Un `503` | lanza una excepción | es una respuesta normal, con su código |
| Tiempo límite por omisión | ninguno | 5 segundos |
| Formas de usarla | solo síncrona (una cosa a la vez) | síncrona **y** asíncrona, con la misma interfaz |
| Una dirección `file://` | la lee | la rechaza |

`httpx` no viene con Python, pero ya lo tienes: lo instalaste dentro del entorno virtual en la Lección 1, y a partir de hoy es la única dependencia del `revisor`. Compara con el programa de `urllib`:

```python
# fig09_04.py
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/facturacion")
print(respuesta.status_code, respuesta.reason_phrase)
print("es un error:", respuesta.is_error)

try:
    respuesta.raise_for_status()
except httpx.HTTPStatusError as error:
    print("raise_for_status avisó:", error.response.status_code)

try:
    httpx.get("file:///etc/hosts")
except httpx.UnsupportedProtocol as error:
    print("httpx no lo permite:", error)
```

```text
$ python fig09_04.py
503 Service Unavailable
es un error: True
raise_for_status avisó: 503
httpx no lo permite: Request URL is missing an 'http://' or 'https://' protocol.
```

El `503` **no lanzó nada**: `httpx.get` devolvió una respuesta como cualquier otra, con `status_code`, `reason_phrase` y un `is_error` que vale `True` para los códigos `4xx` y `5xx`. Si prefieres que un error se vuelva excepción, existe `raise_for_status()`, que lanza `httpx.HTTPStatusError`; el programa lo demuestra, pero el `revisor` no lo usará. Un `503` no es un fallo del `revisor`: es el **dato** que el `revisor` vino a recolectar. Tratarlo como excepción lo sacaría del camino normal y obligaría a atraparlo para volver a ponerlo donde estaba. Y la última parte confirma la cuarta fila de la tabla: `httpx` rechaza `file://` con `UnsupportedProtocol`. Una defensa más, no sustituta de la validación de la Lección 6.

### 9.2 Tiempo límite: ninguna petición espera para siempre

Hay una pregunta que no hemos hecho: ¿qué pasa si el servicio **acepta** la conexión y no contesta? No lo rechaza, no lo cierra: simplemente se queda pensando. Tu programa queda ahí, parado, hasta que algo cambie. Si ese «algo» es una caída de red o un servicio colgado, puede ser **para siempre**. El `revisor` existe para detectar servicios colgados; un `revisor` que se cuelga con ellos es peor que no tener `revisor`. Por eso la regla de este curso es una sola:

> **Toda petición lleva un tiempo límite. Sin excepciones.**

Mira cómo está `urllib` por omisión. La primera línea del programa imprime el tiempo límite global de Python; después pide `/notificaciones`, que tarda 10 segundos, pero ahora con `timeout=1`, un segundo:

```python
# fig09_05.py
import socket
from urllib.request import urlopen

print("tiempo límite global:", socket.getdefaulttimeout())

try:
    urlopen("http://127.0.0.1:8099/notificaciones", timeout=1)
except TimeoutError as error:
    print("se acabó el tiempo:", error)
```

```text
$ python fig09_05.py
tiempo límite global: None
se acabó el tiempo: timed out
```

[`socket.getdefaulttimeout()`](https://docs.python.org/3/library/socket.html#socket.getdefaulttimeout) devuelve `None`: la biblioteca estándar, por omisión, **no tiene ningún tiempo límite** (la documentación de [`urlopen`](https://docs.python.org/3/library/urllib.request.html) dice que usa el valor global). Sin `timeout=`, esa petición se habría quedado diez segundos esperando; contra un servidor que nunca contesta, no habría terminado. Con `timeout=1` la espera se cortó al segundo y Python lanzó `TimeoutError`.

`httpx`, en cambio, trae un tiempo límite de 5 segundos: [la documentación](https://www.python-httpx.org/advanced/timeouts/) dice que «lanza una `TimeoutException` después de 5 segundos de inactividad en la red». Observa dos palabras: *inactividad*, no tiempo total. Hay cuatro tiempos límite distintos: para **conectarse** (`connect`), para **recibir** un trozo de la respuesta (`read`), para **enviar** (`write`) y para **conseguir** una conexión libre del grupo (`pool`). Cada uno cuenta cuánto espera *una operación*, no cuánto dura todo el intercambio: un servidor que gotea un byte cada 4 segundos nunca dispara el `read` de 5 segundos aunque la respuesta tarde horas. El tope total por servicio lo pondrás en la Lección 10 con `asyncio.timeout()`; hoy, el de cada operación es suficiente. Un solo número en `httpx.Timeout(1.0)` los fija los cuatro en un segundo.

```python
# fig09_06.py
import httpx

print("httpx, por omisión:", httpx.Client().timeout)
limite = httpx.Timeout(1.0)

try:
    httpx.get("http://127.0.0.1:8099/notificaciones", timeout=limite)
except httpx.ReadTimeout:
    print("notificaciones: tiempo agotado")

try:
    httpx.get("http://127.0.0.1:8098/", timeout=limite)
except httpx.ConnectError:
    print("reportes: sin conexión")

print(issubclass(httpx.ReadTimeout, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.HTTPError))
```

```text
$ python fig09_06.py
httpx, por omisión: Timeout(timeout=5.0)
notificaciones: tiempo agotado
reportes: sin conexión
True
False
True
```

La primera línea muestra el valor por omisión de `httpx` (`Timeout(timeout=5.0)`). Luego, dos peticiones con tiempo límite de un segundo, y cada una termina con una excepción **distinta**, que es justo lo que el `revisor` necesita distinguir:

- `/notificaciones`, que tarda diez segundos, lanzó `httpx.ReadTimeout`: la conexión se estableció, pero el servicio no contestó a tiempo. Es la causa de «tiempo agotado».
- El puerto 8098, donde no escucha nadie, lanzó `httpx.ConnectError`: no hubo a quién conectarse. Es la causa de «sin conexión».

Las últimas tres líneas, con `issubclass` (que pregunta si una clase es hija de otra), confirman la jerarquía [que documenta `httpx`](https://www.python-httpx.org/exceptions/): `ReadTimeout` es una `TimeoutException`; `ConnectError` **no** lo es; y `ConnectError` sí es una `HTTPError`, la clase madre de casi todo lo que `httpx` puede lanzar. Eso decide el orden de los `except` del `revisor`: primero `TimeoutException`, luego `ConnectError`, y al final `HTTPError` para recoger lo que quede (un servidor que cierra a media respuesta, por ejemplo). Las tres ramas devuelven un `Resultado` con estado `CAIDO` y su detalle (`tiempo agotado`, `sin conexión` o `error de red`). **Nunca dejan escapar la excepción.**

De dónde sale el número: cada `Servicio` trae su `timeout_ms`, por omisión 5000, en milisegundos. `httpx` quiere segundos, así que el `revisor` divide: `httpx.Timeout(servicio.timeout_ms / 1000)`. La unidad vive en el nombre (`timeout_ms`) precisamente para que esta conversión no se olvide. **Aquí termina la primera sesión.**

### 9.3 Corrutinas: funciones que pueden esperar

#### 9.3.1 Una corrutina no se ejecuta al llamarla

En la segunda sesión llega la idea que más cuesta. Durante los 2.3 segundos que `inventario` tarda en contestar, tu programa no hace nada: espera. Todo ese tiempo, el procesador está libre. Una **corrutina** es una función que puede **pausarse en el punto donde espera** y dejar que otra cosa use ese tiempo. Se escribe con `async def`, en lugar de `def`:

```python
# fig09_07.py
async def saludar() -> str:
    return "hola"


print(saludar())
print("listo")
```

```text
$ python fig09_07.py
<coroutine object saludar at 0x...>
fig09_07.py:6: RuntimeWarning: coroutine 'saludar' was never awaited
  print(saludar())
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
listo
```

`saludar` es una función normal en todo menos en su primera palabra. Pero fíjate en lo que imprimió `print(saludar())`: **no** dice `hola`. Dice `<coroutine object saludar at 0x...>`. Llamar a una función `async def` no ejecuta su cuerpo; crea un **objeto corrutina**, una receta en pausa. [La documentación de `asyncio`](https://docs.python.org/3/library/asyncio-task.html) lo dice así: llamar a una corrutina no la programa para ejecutarse, y en su ejemplo `nested()` se llama sin esperarla: se crea el objeto, pero el cuerpo «no se ejecutará en absoluto». Y como el objeto se tiró a la basura sin que nadie lo ejecutara, Python avisa: `RuntimeWarning: coroutine 'saludar' was never awaited`, «la corrutina `saludar` nunca fue esperada». El aviso incluye la línea del programa donde se llamó y es **la señal más común** de que se te olvidó un `await`.

#### 9.3.2 `asyncio.run`: el arranque

¿Cómo se ejecuta entonces una corrutina? Necesita un coordinador que la corra, el **bucle de eventos** (*event loop*): un programa pequeño, dentro de Python, que reparte el tiempo entre las corrutinas pausadas. No lo manejas directamente. [`asyncio.run`](https://docs.python.org/3/library/asyncio-runner.html) lo crea, ejecuta la corrutina que le des hasta que termina, devuelve su resultado y cierra el bucle:

```python
# fig09_08.py
import asyncio


async def saludar() -> str:
    return "hola"


print(asyncio.run(saludar()))
```

```text
$ python fig09_08.py
hola
```

Ahora sí: `hola`. `asyncio.run` se escribe una sola vez, en la entrada del programa, y desde ahí todo lo demás se encadena con `await`. En el `revisor` quedará en `cli.py`.

#### 9.3.3 `await` y `async with`: esperar a otra corrutina

Dentro de una corrutina, `await` significa **«espera aquí a que esta otra cosa termine, y mientras esperas, deja que el bucle haga otras cosas»**. Es la forma explícita de pausar una corrutina, y solo funciona dentro de una función `async def`. (Hay otras dos, que esperan sin que escribas la palabra: `async with`, que verás en un momento, y `async for`, que el curso no usa; [la referencia del lenguaje](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement) explica que por dentro hacen `await`.) La corrutina que más vas a esperar en el curso es una petición de `httpx`, y para eso `httpx` trae [una versión asíncrona del cliente](https://www.python-httpx.org/async/), `httpx.AsyncClient`, que se usa con un `async with`:

```python
# fig09_09.py
import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get("http://127.0.0.1:8099/pagos")
        print(respuesta.status_code)


asyncio.run(main())
```

```text
$ python fig09_09.py
200
```

`async with` es el `with` de la Lección 6 para recursos cuya apertura y cierre **también** pueden esperar: crear y cerrar el cliente de red es una operación de este tipo. Dentro, `cliente.get(...)` es una corrutina; `await` la espera, y lo que se obtiene es la respuesta. Observa que la respuesta es exactamente la misma que en el `httpx.get` síncrono: `status_code`, `is_error` y el resto. La diferencia está en cómo se espera. Y el cliente **se crea una vez y se reutiliza** para varias peticiones: abrir y cerrar uno por consulta sería como colgar y volver a marcar cada vez que haces una pregunta.

### 9.4 Un `await` tras otro no ahorra tiempo: la serie

Aquí está el malentendido más extendido sobre `asyncio`, y conviene desmontarlo con una medición. Un principiante lee «asíncrono» y supone «más rápido». No lo es. Mira este programa, que espera tres veces medio segundo, una tras otra, cada una con `await` ([`asyncio.sleep`](https://docs.python.org/3/library/asyncio-task.html#sleeping) es la espera asíncrona de siempre):

```python
# fig09_10.py
import asyncio
import time


async def esperar(nombre: str, segundos: float) -> str:
    await asyncio.sleep(segundos)
    return f"{nombre} esperó {segundos} s"


async def main() -> None:
    inicio = time.perf_counter()
    for nombre in ("catalogo", "inventario", "pagos"):
        print(await esperar(nombre, 0.5))
    total = time.perf_counter() - inicio
    print(f"en serie tarda la suma, 1.5 s o más: {1.5 <= total < 2.0}")


asyncio.run(main())
```

```text
$ python fig09_10.py
catalogo esperó 0.5 s
inventario esperó 0.5 s
pagos esperó 0.5 s
en serie tarda la suma, 1.5 s o más: True
```

La última línea pregunta `1.5 <= total < 2.0`, las dos cosas a la vez: que `total` sea al menos 1.5 y menos de 2. Las tres esperas tardaron la **suma**: 1.5 segundos o más. No ganaste nada. La razón está en lo que `await` hace de verdad: pausa **esta** corrutina y le ofrece al bucle atender a otras, pero en este programa **no hay otras**. El bucle ofrece el turno y nadie lo toma. Es la misma [secuencia que muestra la documentación de Python](https://docs.python.org/3/library/asyncio-task.html): un `await` seguido de otro `await` se ejecuta en serie. Para ganar tiempo hacen falta **varias corrutinas vivas a la vez**, y eso se logra con tareas (`asyncio.TaskGroup`), que es el contenido de la Lección 10.

El `revisor` de hoy, entonces, será una versión asíncrona que se comporta **como el síncrono**: consulta los servicios de uno en uno. ¿Para qué entonces? Primero, porque es el paso intermedio que hace visible la ganancia: la Lección 10 mide la misma tabla de servicios en serie y en paralelo, y necesita el punto de partida. Segundo, porque cambiar de `def` a `async def` toca toda la cadena de llamadas, y es más fácil de entender haciéndolo antes de meter concurrencia. Y tercero, porque lo que importa de este paso es todo lo que no tiene que ver con el tiempo: tiempos límite, excepciones, clasificación.

### 9.5 El `revisor` consulta de verdad

Con todo lo anterior, `revision.py` se reescribe entero. Se borra `SIMULADO`, y las dos funciones se vuelven corrutinas:

```python
# fig09_11/src/revisor/revision.py
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        respuesta = await cliente.get(servicio.url, timeout=limite)
    except httpx.TimeoutException:
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


async def revisar_todos(servicios: list[Servicio]) -> list[Resultado]:
    resultados: list[Resultado] = []
    async with httpx.AsyncClient() as cliente:
        for servicio in servicios:
            resultados.append(await revisar(cliente, servicio))
    return resultados
```

Lee `revisar` de arriba hacia abajo. Recibe un **cliente** y un **servicio**; el cliente viene de afuera para que se reutilice. Arma el `httpx.Timeout` con el `timeout_ms` del servicio, apunta la hora con `time.perf_counter()` (el reloj de alta precisión de Python) y hace la petición con `await`. Los tres primeros `except` son los de 9.2, **del más específico al más general**, y cada uno devuelve un `Resultado` caído con su texto. El cuarto atrapa algo que no es un error de red: una dirección que pasó la validación de la Lección 6 pero que `httpx` no puede usar. Pasa, por ejemplo, con `http://999.1.1.1:8099/pagos`: para `urlsplit` es una dirección con servidor y puerto, pero cada una de las cuatro partes de una dirección IP va de 0 a 255, y 999 no cabe, y `httpx` lo rechaza con `httpx.InvalidURL`, que **no** es hija de `httpx.HTTPError` (lo dice [su jerarquía de excepciones](https://www.python-httpx.org/exceptions/)). Otros nombres de servidor imposibles terminan en un `ValueError` de las bibliotecas que `httpx` usa por dentro. Sin este `except`, uno solo de esos servicios tumbaría el reporte entero con un *traceback*; con él, sale en su fila como `CAIDO`, con el detalle `dirección inválida`, y los demás se revisan igual. El `ValueError` se atrapa aquí, alrededor de una sola llamada, y no en todo el programa: un `ValueError` de tu propio código, fuera del `try`, seguiría deteniéndolo con su informe, como debe ser. Si no hubo excepción, mide cuánto pasó (`round(... * 1000)` convierte segundos a milisegundos enteros), clasifica con la misma función `clasificar` de siempre, que recibe el código real, y arma el `Resultado` con el código como detalle. Un `503` pasa por aquí: no es excepción, sale con `clasificar(503, 95)` y se convierte en `CAIDO` con detalle `503`.

`revisar_todos` abre **un** cliente con `async with` y recorre los servicios con un `for` y un `await` por vuelta. Es la serie de 9.4, escrita a propósito. El orden de los resultados es el de la configuración.

`main` en `cli.py` solo cambia en una línea: la llamada se envuelve en `asyncio.run`.

```python
# fig09_11/src/revisor/cli.py
import argparse
import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import encabezado, linea, reporte_a_json, resumen
from revisor.modelo import Estado
from revisor.revision import revisar_todos


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
        "--version",
        action="version",
        version=f"revisor {version('revisor')}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios))
    if argumentos.formato == "json":
        print(reporte_a_json(resultados))
    else:
        print(encabezado())
        for resultado in resultados:
            print(linea(resultado))
        print()
        print(resumen(resultados))

    problemas = [r for r in resultados if r.estado is not Estado.ARRIBA]
    if len(problemas) == 0:
        return 0
    return 1
```

Para que `asyncio.run` tenga algo que ejecutar, `revisar_todos(servicios)` sin `await` produce una corrutina, y `asyncio.run` la corre. Es el único `asyncio.run` del programa. Las pruebas siguen llamando a `main` como una función normal, así que **no necesitan ser corrutinas**; esto es lo que permite no instalar ningún complemento de `pytest` para código asíncrono. Los otros cambios son datos. El `pyproject.toml` sube a `0.8.0` y declara la primera dependencia del paquete, `httpx`:

```toml
dependencies = ["httpx>=0.28"]
```

Reinstala el paquete (`pip install -e .`) para que el entorno vea la dependencia y la versión nueva. Y el `servicios.toml` apunta ahora al servidor de práctica: los mismos cuatro nombres, otras direcciones. (El proyecto completo está en 9.6.)

```toml fig09_11/servicios.toml
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

Con el servidor de práctica abierto en la otra terminal, corre el `revisor` y mira el código de salida:

```text
$ cd fig09_11
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
$ echo $?
1
```

Es la tabla del temario, ahora **medida**: `catalogo` y `pagos` arriba con tiempos reales (el servidor espera 142 y 87 ms, y cada petición añade unos milisegundos de red, así que verás números como 156 y 98, distintos en cada corrida), `inventario` lento con 2.3 s, `reportes` caído con `sin conexión` (nadie escucha en el 8098). El resumen cuenta dos arriba, uno lento, uno caído, y el código de salida es `1`, el mismo de siempre, por la misma razón: hay un lento y un caído. Lo que cambió es que ahora es verdad.

¿Cuánto tarda? En serie, la suma: 142 + 2300 + 87 son unos 2.5 segundos de espera más lo que tarda en arrancar Python y cargar `httpx`. Medida con el comando `time` de la terminal, una corrida completa dura unos 2.7 segundos. El tuyo dará un número cercano, no igual. Esa cifra es el punto de partida de la Lección 10. Lo mide el Ejercicio 1.

Y las pruebas: córrelas.

```text
$ cd fig09_11
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

Siguen siendo **21**. El único archivo de pruebas que cambió es `tests/test_cli.py`, y no por capricho. Su primera prueba usaba los datos simulados para comprobar que `main` devuelve `1`, y ya no existen; y las funciones falsas del `monkeypatch` ahora devuelven una corrutina, porque la verdadera es una corrutina y `main` hace `asyncio.run` de lo que le devuelvan. Por eso son `async def`:

```python
# fig09_11/tests/test_cli.py
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


def test_con_servicios_caidos_sale_con_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_caidos(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Una advertencia que hay que decir en voz alta: **pasa `21 passed` y, sin embargo, lo nuevo no tiene una sola prueba**. Nada de lo que acabas de escribir (el tiempo límite, la clasificación de un `503`, el `sin conexión`) se ejercita en esas 21. Las dos pruebas de `test_cli.py` sustituyen `revisar_todos` completa, así que el código de red ni se toca. Ese es el tamaño del hueco, y es el motivo de la Lección 10: cómo probar código de red sin red.

### 9.6 El proyecto completo

La foto del proyecto al terminar la lección. Los archivos que ya viste son `laboratorio.py`, `servicios.toml`, `revision.py`, `cli.py` y `tests/test_cli.py`. El `pyproject.toml` es el de la Lección 8 con la versión y la dependencia nuevas:

```toml fig09_11/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.8.0"
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

Los demás archivos **no cambian** respecto a la Lección 8, y se repiten aquí solo para que el proyecto esté completo:

```python
# fig09_11/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig09_11/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig09_11/src/revisor/modelo.py
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
# fig09_11/src/revisor/formato.py
import json
from urllib.parse import urlsplit, urlunsplit

from revisor.modelo import Estado, Resultado


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(resultado: Resultado) -> str:
    nombre = resultado.servicio.nombre
    estado = resultado.estado.value
    tiempo = formatear_tiempo(resultado.tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {resultado.detalle}"


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


def url_sin_secretos(url: str) -> str:
    partes = urlsplit(url)
    servidor = partes.netloc.rpartition("@")[2]
    return urlunsplit((partes.scheme, servidor, partes.path, "", ""))


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": url_sin_secretos(r.servicio.url),
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

```python
# fig09_11/src/revisor/configuracion.py
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


def tiene_credenciales(url: str) -> bool:
    partes = urlsplit(url)
    return partes.username is not None or partes.password is not None


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
    if tiene_credenciales(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' no debe llevar usuario ni clave"
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
# fig09_11/tests/test_modelo.py
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
# fig09_11/tests/test_formato.py
import pytest

from revisor.formato import formatear_tiempo


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [
        (None, "—"),
        (87, "87ms"),
        (999, "999ms"),
        (2300, "2.3s"),
    ],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado
```

```python
# fig09_11/tests/test_configuracion.py
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

Las cuatro comprobaciones de la Lección 8, que ahora también cubren el código asíncrono:

```text
$ cd fig09_11
$ ruff format --check
12 files already formatted
$ ruff check
All checks passed!
$ mypy
Success: no issues found in 11 source files
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

## El error que vas a ver

### `RuntimeWarning: coroutine 'saludar' was never awaited`

Lo viste en 9.3.1, con el programa `fig09_07.py`, y vale la pena repetir cómo se lee. El aviso no es un error: el programa **sigue** y termina con código `0`, que es lo peligroso, porque hay un aviso entre decenas de líneas y es fácil pasarlo por alto. Dice tres cosas: el archivo y la línea donde llamaste a la corrutina sin esperarla (`fig09_07.py:6`, y debajo imprime la propia línea, `print(saludar())`), qué corrutina fue (`'saludar'`), y la consecuencia: su cuerpo nunca se ejecutó. La cura casi siempre es una palabra: poner `await` delante de la llamada, o pasarla a `asyncio.run`.

En el proyecto, `mypy` te avisa **antes** de correr. Quita el `await` de la línea `resultados.append(await revisar(cliente, servicio))` en `revisar_todos`, y esto es lo que dice `mypy`:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
Found 1 error in 1 file (checked 11 source files)
```

Tú le habías dicho a la lista que guardaba `Resultado`, y le estás dando una `Coroutine`. Y `mypy` lo adivina con una nota: «¿Olvidaste el `await`?». Es el tipo de ayuda por la que se escribieron los tipos en la Lección 8. Si ignoras el aviso y corres el programa, la tabla imprime su encabezado y se detiene con `AttributeError: 'coroutine' object has no attribute 'servicio'` (la última línea del *traceback*), seguido del mismo `RuntimeWarning` al final.

### Todos los servicios dicen `sin conexión`

Si olvidas encender el servidor de práctica, el `revisor` no se cae; hace exactamente lo que debe. Esto es lo que imprime con el servidor apagado:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO          —  sin conexión
inventario  CAIDO          —  sin conexión
pagos       CAIDO          —  sin conexión
reportes    CAIDO          —  sin conexión

4 servicios · 0 arriba · 0 lentos · 4 caídos · promedio —
```

No hay `Traceback`. Los cuatro servicios están `CAIDO`, con `sin conexión` y sin tiempo (`—`), porque nadie contesta en el puerto 8099, igual que en el 8098. Esto es el diseño funcionando: un servicio que no contesta es un **dato**, no una excepción que tumba el reporte. La señal para ti es que `reportes` no debería ser el único caído: si lo son los cuatro, antes de buscar un error en tu código, mira si la segunda terminal sigue abierta. (Fíjate también en el promedio: sale como `—`, igual que el tiempo de cada fila, porque no hay tiempos que promediar. Es la misma decisión de la Lección 2: lo que no se midió no vale `0`.)

### La prueba que se rompe porque su falso dejó de ser una corrutina

Si dejas `tests/test_cli.py` como estaba en la Lección 8, y solo cambias `revision.py` y `cli.py`, `pytest -q` dice `1 failed, 20 passed`. La roja es la prueba que usa el falso con `def` en lugar de `async def`. La última línea del error cambia de redacción según tu versión de Python, pero dice lo mismo:

```text
ValueError: a coroutine was expected, got [Resultado(servicio=Servicio(nombre='catalogo', ...
```

(en Python 3.12) o

```text
TypeError: An asyncio.Future, a coroutine or an awaitable is required
```

(en 3.14). `asyncio.run(...)` recibió una **lista** y esperaba una corrutina, porque `main` hace `asyncio.run(revisar_todos(servicios))` y el falso, al ser `def`, devolvió el resultado directo. La corrección es la que viste: hacer el falso `async def`.

Pero hay algo más sutil. Una **segunda** prueba vieja, la que corría con los datos simulados, **sigue en verde**, y no debería. Esa prueba usaba direcciones `https://catalogo.example` y esperaba que `main` devolviera `1`. Ahora `main` hace peticiones de verdad a esas direcciones inventadas, no logra conectarse a ninguna, las marca todas como caídas y devuelve `1`. La prueba pasa, pero **por una razón completamente distinta** de la que la escribió, y depende de que `.example` nunca resuelva y de que tu red conteste rápido que no existe. Es lo que pasa cuando una prueba verde sostiene algo que ya no es lo que dice: se sustituyó el falso por una prueba que no hace lo que su nombre promete. Por eso se reescribió con un falso explícito.

## Lo que se hace mal

**Hacer una petición sin tiempo límite.** Es el error que esta lección existe para evitar. Con `urllib`, sin `timeout=`, el programa espera lo que haga falta, incluyendo para siempre. Con `httpx`, el límite por omisión es 5 s, pero depender de un valor por omisión sin saberlo es dejar una decisión importante en manos de otro. El `revisor` lo fija siempre, por servicio.

**Atrapar `Exception` y seguir.** `except Exception: pass` alrededor de una petición hace que un `ReadTimeout`, un `ConnectError` y un error de programación se vean idénticos: nada. El `revisor` atrapa tres excepciones concretas, cada una con su texto, y deja que cualquier otra se vea.

**Imprimir el mensaje del sistema operativo.** `[Errno 111] Connection refused` cambia con el sistema y con el idioma; el reporte de un servicio no debe cambiar de texto según dónde se ejecute. El detalle es una de tres frases fijas.

**Suponer que `async` es más rápido.** Lo desmontaste en 9.4: un `await` tras otro suma sus tiempos. Una función `async` sin concurrencia es una función síncrona con más ceremonia.

**Llamar a una corrutina sin `await`.** El aviso de 9.3.1. Con `mypy` en modo estricto se vuelve un error de tipos, por eso conviene correrlo.

**Bloquear dentro de una corrutina.** Un `time.sleep(1)` dentro de una `async def` detiene **todo** el programa un segundo: nadie más puede avanzar, porque el bucle está atorado dentro de esa llamada. Dentro de una corrutina, la espera es `await asyncio.sleep(1)`. Lo mismo para las bibliotecas de red que no son asíncronas, como `urllib` o `httpx.get`.

**Crear un cliente por petición.** `httpx.AsyncClient()` abre un grupo de conexiones que se reutilizan. Abrir y cerrar uno en cada consulta tira ese ahorro; el `revisor` abre uno al inicio de `revisar_todos` y lo comparte.

**Tratar un `503` como si fuera una falla del programa.** Un servicio que contesta con error es el resultado del trabajo, no un incidente del `revisor`. Por eso se lee el código y se clasifica; `raise_for_status()` convertiría el dato en excepción.

**Poner `0` donde no hubo respuesta.** Un servicio caído tiene `tiempo_ms=None`, no `0`: con cero, el promedio premia al caído. Es la misma lección de la Lección 2, en un proyecto más grande.

## Ejercicios

### Ejercicio 1 — Mide la serie con el reloj

Con el servidor de práctica encendido, mide cuánto tarda el `revisor` completo: `time python -m revisor`. Antes de correrlo, **predice** el número a partir de lo que sabes: la suma de lo que tarda cada servicio. Córrelo tres veces y anota las tres en tu bitácora. ¿Por qué no son idénticas? Este número es tu punto de partida para la Lección 10.

### Ejercicio 2 — Quítale el tiempo límite a una petición y mira por qué es peligroso

Escribe un programa de seis líneas que use `httpx.get` con `timeout=None` (que [desactiva el tiempo límite](https://www.python-httpx.org/advanced/timeouts/)) contra `http://127.0.0.1:8099/espera/60000`, que tarda un minuto. Córrelo, deja pasar cinco segundos y presiona `Ctrl`+`C`. ¿Qué se imprime? ¿Cuánto habría tardado en terminar solo? Después ponle `timeout=2.0` y compara.

### Ejercicio 3 — Los dos servicios de más

Agrega a tu `servicios.toml` `facturacion` (`http://127.0.0.1:8099/facturacion`) y `notificaciones` (`http://127.0.0.1:8099/notificaciones`, con `timeout_ms = 1000`). Antes de correr, predice el estado y el detalle de cada uno, y cuál será la línea del resumen. ¿Algo en la tabla te parece raro? Devuelve el archivo a sus cuatro servicios al terminar.

### Ejercicio 4 — Olvida un `await` a propósito

En `revisar_todos`, quita el `await` de `resultados.append(await revisar(cliente, servicio))`. Corre `mypy`, luego `python -m revisor`, y lee las dos señales: qué dice cada una, y cuál llegó primero. Restituye el `await`.

## Soluciones

### Solución 1

La predicción: 142 + 2300 + 87 = 2529 ms para los tres que contestan, más lo que tarda en intentar conectar con `reportes` (unos milisegundos, porque rechazan de inmediato), más el arranque de Python y de `httpx`. Eso da unos **2.6 o 2.7 segundos**, y es lo que mide el reloj: una corrida de referencia dio 2.674 s. Las tres corridas son parecidas pero no idénticas porque el servidor, el sistema operativo y la red añaden pequeñas variaciones de unos milisegundos cada vez. Lo importante es el orden de magnitud: unos 2.5 segundos, porque **es la suma**. Si la Lección 10 logra que sea cercano a 2.3 s (el servicio más lento), habrá ganado menos de lo que parece con cuatro servicios; por eso la medición fuerte de esa lección usa veinte.

### Solución 2

```python
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/espera/60000", timeout=None)
print(respuesta.status_code)
```

Con `Ctrl`+`C` a los cinco segundos, Python imprime un *traceback* que termina en `KeyboardInterrupt`: interrumpiste tú, no el programa. Habría tardado **un minuto entero** en terminar solo, sin imprimir nada mientras tanto. Contra un servidor que nunca contesta, no habría terminado nunca: eso es lo que significa «sin tiempo límite». Con `timeout=2.0` el programa lanza `httpx.ReadTimeout` a los dos segundos. Ese `ReadTimeout` es una excepción **que sí se puede atrapar**, que es lo que hace `revisar`.

### Solución 3

La predicción: `facturacion` contesta `503` en 95 ms, así que `CAIDO` con detalle `503` y tiempo de unos 100 ms. `notificaciones` tarda 10 s pero su límite es de 1 s: `CAIDO` con `tiempo agotado` y sin tiempo. El resumen: `6 servicios · 2 arriba · 1 lento · 3 caídos`. Esto es lo que imprime:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     160ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO      102ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 666ms
```

Lo raro es la última fila: `notificacionesCAIDO`, sin separación. El nombre tiene 14 letras y la columna `SERVICIO` mide 12 (`{nombre:<12}`), así que desborda y se pega con la siguiente. Es un límite real de la tabla tal como está hoy, y es una de las cosas que la Lección 11 corrige calculando el ancho a partir del nombre más largo. Cuenta también el tiempo: la corrida entera tardó unos 3.8 s en lugar de 2.7, porque `notificaciones` espera su segundo completo antes de rendirse. Cada servicio lento o colgado añade su espera a la serie, que es lo que la Lección 10 viene a resolver.

### Solución 4

`mypy` se queja **primero**, sin correr nada:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
```

Al correr el programa, se imprime el encabezado y se detiene con `AttributeError: 'coroutine' object has no attribute 'servicio'`, porque la lista tiene corrutinas en lugar de resultados, y al final aparece `RuntimeWarning: coroutine 'revisar' was never awaited`. Llegó primero `mypy`, y lo hizo con la causa y con la sugerencia; el error en tiempo de ejecución solo muestra la consecuencia. Es el argumento a favor de correr `mypy` antes que el programa.

## Cómo sé que lo logré

- [ ] Con el servidor de práctica encendido, `python -m revisor` imprime la tabla de cuatro servicios con `catalogo` y `pagos` arriba, `inventario` lento (`2.3s`) y `reportes` caído con `sin conexión`, y `echo $?` imprime `1`.
- [ ] Con el servidor apagado, los cuatro dicen `CAIDO` y `sin conexión`, y el programa no imprime ningún *traceback*.
- [ ] `pytest -q` dice `21 passed` (el mismo número de la Lección 8), y puedes explicar qué parte del programa **no** cubre ninguna de las 21.
- [ ] `mypy` dice `Success: no issues found in 11 source files`, `ruff check` dice `All checks passed!` y `ruff format --check` dice que los archivos ya están formateados.
- [ ] Mediste la corrida con `time` y tu número está cerca de 2.7 segundos, y sabes explicar por qué es la suma y no el máximo.
- [ ] Puedes explicar qué hace `await`, qué hace `asyncio.run` y por qué `saludar()` a secas no imprime `hola`.
- [ ] Puedes decir con qué excepción de `httpx` termina un servicio que no contesta y con cuál uno donde nadie escucha, y por qué un `503` no es una excepción.

## Resumen

Responde sin mirar la lección:

1. ¿Qué trae una respuesta HTTP, y qué familias de código de estado hay? ¿Cuáles vuelven `CAIDO` a un servicio?
2. ¿Qué hace `urllib` cuando el servidor contesta `503`, y qué hace `httpx`?
3. ¿Por qué `urlopen` acepta una dirección `file://`, y qué la detiene en el `revisor`?
4. ¿Qué tiempo límite tiene `urllib` por omisión, y cuál `httpx`?
5. ¿Qué excepción de `httpx` produce un servicio que no contesta, y cuál uno donde nadie escucha?
6. ¿Qué hace `asyncio.run`? ¿Qué pasa si llamas a una función `async def` sin `await` ni `asyncio.run`?
7. ¿Por qué tres `await` seguidos de medio segundo tardan 1.5 s y no 0.5 s?
8. ¿Por qué el informe de la Lección 9 sigue diciendo `21 passed` y qué dejó sin probar?

## Para leer más

- [HTTPX, «Timeouts»](https://www.python-httpx.org/advanced/timeouts/) — los cuatro tiempos límite (`connect`, `read`, `write`, `pool`), el valor por omisión y cómo desactivarlos. En inglés, como casi toda la documentación del ecosistema. Consultado el 7 de octubre de 2026.
- [Python, «Coroutines and tasks»](https://docs.python.org/3/library/asyncio-task.html) — la documentación oficial de `asyncio`: corrutinas, `await`, tareas y el aviso de la corrutina nunca esperada. Consultado el 7 de octubre de 2026.
- [RFC 9110, «HTTP Semantics»](https://www.rfc-editor.org/rfc/rfc9110.html) — el estándar de HTTP; la sección de códigos de estado define qué quiere decir cada número. Es un texto para consultar, no para leer de corrido. Consultado el 7 de octubre de 2026.
- [PEP 492, «Coroutines with async and await syntax»](https://peps.python.org/pep-0492/) — el documento que introdujo `async` y `await`; explica por qué son palabras reservadas del lenguaje. Consultado el 7 de octubre de 2026.
