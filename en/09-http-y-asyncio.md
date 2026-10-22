# Lesson 9 — HTTP and asyncio

**Time:** 2 × 90 min (the first session runs to the end of 9.2; the second covers 9.3, 9.4 and 9.5)

**What you build:** the `revisor` that queries real services, one after another, with a timeout on each request

**What you learn:** requesting a page with `urllib` and with `httpx`; what a status code says; why every request carries a timeout; coroutines (`async def`, `await`, `asyncio.run`, `async with`); and why a lone `await`, with nobody else, does not make anything faster

**Where you come from.** You bring the package from [Lesson 8](08-pruebas-tipos-calidad.md): the `revisor` with 21 tests, its types checked and its style watched over. But there is an uncomfortable truth in that package: **it has never queried anyone**. The figures in the table (142 ms, 2.3 s, 87 ms) come from a dictionary, `SIMULADO`, that you wrote yourself; the program gives back what you told it to say. Today you replace it with a real query: the `revisor` makes a request to each service, times how long it takes to answer and classifies what it receives. To practice without bothering any real service, the lesson gives you a practice server that runs on your own computer.

**What this lesson does not do.** It does not yet query the services **at the same time**: it does it one after another, and the lesson teaches you to measure what that costs. Putting them together is [Lesson 10](10-concurrencia-pruebas-sin-red.md). And the new code, the one that uses the network, **has no tests**: the project still has the 21 tests of Lesson 8, and the lesson tells you so plainly instead of hiding it. Testing network code without a network is the topic of Lesson 10.

## By the end you will be able to

- Explain what an HTTP request is, what a response contains and what the `2xx`, `4xx` and `5xx` status codes mean.
- Request an address with `urllib.request` and with `httpx`, and say how they differ when the server answers `503` and when it does not answer.
- Explain why `urllib` accepts a `file://` address, and why the validation from Lesson 6 keeps the `revisor` from reading files on your computer.
- Put a timeout on a request, and know which exception is raised when it runs out and which when there is nobody to call.
- Write a coroutine with `async def`, run it with `asyncio.run` and wait for another with `await`, and explain why calling a coroutine does **not** run it.
- Measure with the clock that querying the services one after another takes the sum of their times, and explain why a lone `await` does not speed it up.
- Read the warning `coroutine ... was never awaited` and the `mypy` message “Maybe you forgot to use "await"?”.

## The why before the how

Imagine you ask an office colleague whether the payments system is working. They have to do something like what your browser does when you open a page: ask that machine about an address and wait for the reply. The question is called a **request** and the reply, a **response**. Both follow a common language, **HTTP**, which is the one the whole web uses. A request says, in essence, “give me what is at this address” (the `GET` method, plus the address). A response brings three things: a **status code**, a three-digit number that summarizes how everything went; some **headers**, data about the response (what kind of content it is, how big); and a **body**, the content itself.

What matters most to you in the response is the code, and its first digit classifies it. [The HTTP standard](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) groups them into five families: `1xx` are informational, `2xx` mean it went well (`200` is “here it is”), `3xx` are redirections, `4xx` are errors by whoever asks (`404`: that address does not exist) and `5xx` are errors by the server (`503`: right now I cannot serve you). For the `revisor`, a service can end in **three** different ways, and each one ends up in a row of the table:

| What happened | What the `revisor` sees | How it ends up in the table |
|---|---|---|
| The service answered with a code lower than 400 (`2xx`, or a `3xx`) | a code and a time | `ARRIBA` (up), or `LENTO` (slow) if it took 1000 ms or more |
| It answered with a `4xx` or `5xx` code | a code and a time | `CAIDO` (down), with the code in the detail (`503`) |
| It did not answer | an exception: it could not connect, or the time ran out | `CAIDO`, with `sin conexión` (“no connection”) or `tiempo agotado` (“timed out”) |

The `3xx` fall in the first row on purpose. A redirection says “what you are looking for is at another address,” and `httpx` [does not follow it by default](https://www.python-httpx.org/quickstart/#redirection-and-history): it returns the response as it is, with its code. For the `revisor`, a service answering with a redirection means it is alive and answering, and the usual rule (down only with `400` or more) counts it as up, with the code in the detail so you see it.

That table is the whole design of the lesson. (HTTP is the most common style for two programs to talk to each other, but not the only one; if you are interested in what comes after “request an address and read what it answers,” the Hábil blog compares two styles in [REST or gRPC: when each fits](https://www.habil.mx/en/blog/rest-or-grpc-when-to-use-each/).) The rest is how each row is done without the program falling over: the third, above all, because a service that does not answer is exactly the case the `revisor` exists to detect, and it cannot be the case that takes it down.

The lesson has two halves. In the first session you make a well-built query: first with the library that comes with Python, `urllib`, to see what a request looks like on the inside, and then with `httpx`, the one the course uses. You learn that **every request carries a timeout**. In the second session you reach **coroutines**, Python's tool for waiting without standing still, and you make the `revisor` query for real. It is the biggest conceptual leap of the course; that is why the pace of this lesson is slow on purpose.

### The practice server

The `revisor` needs someone to ask. The names `catalogo.example` or `pagos.example` that you have used so far are made-up addresses: the `.example` suffix is [reserved for examples](https://www.rfc-editor.org/rfc/rfc2606) and never exists on the internet. So that each service really answers, and always the same, the lesson includes `laboratorio.py`, a small server that runs **on your computer** and pretends to be the course's services.

Here is the complete file. **Take it as a black box: it is used, not written.** It is built with a class and methods, things this course does not teach, and understanding it is not necessary for anything that follows. Copy it as it is to `~/curso-python/revisor/laboratorio.py`. When you finish the course you can read it again; the library it uses, [`http.server`](https://docs.python.org/3/library/http.server.html), is part of Python.

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

What matters about it is what each route answers, which is what the `RUTAS` table and the `buscar_ruta` function say. (The `Servidor` class only changes one number, `request_queue_size`: how many connections can wait their turn at once to be served. The factory value, 5, falls short when in Lesson 10 the `revisor` opens twenty connections at once, and the ones that do not fit in the queue would be rejected as if the service were down.)

| Route | What it answers | How long it takes |
|---|---|---|
| `/catalogo` | `200` | 142 ms |
| `/inventario` | `200` | 2300 ms |
| `/pagos` | `200` | 87 ms |
| `/facturacion` | `503` | 95 ms |
| `/notificaciones` | `200` | 10 seconds |
| `/espera/<ms>` | `200` | the milliseconds you put in place of `<ms>` |

They are the same numbers as in the syllabus table, now produced by a real server. The address is `127.0.0.1`, which means “this same computer,” so what happens in the lesson does not leave your machine. There is a single exception, and it almost certainly does not apply to you: if your terminal has a **proxy** configured (an intermediary that requests pass through, common on some office networks, and noticeable because variables like `HTTP_PROXY` or `ALL_PROXY` exist, in upper or lower case; `env | grep -i proxy` shows them), requests to `127.0.0.1` also go to the proxy, and the practice fails. `httpx` honors `HTTP_PROXY`, `HTTPS_PROXY` and `ALL_PROXY`; `urllib`, only the first two. It is fixed by telling them that this address does not go through the proxy, with `export NO_PROXY=127.0.0.1` in each terminal where you run the programs; the [`httpx` documentation](https://www.python-httpx.org/environment_variables/) explains those variables. Port `8099` is the “window number” it listens on. And there is a deliberate trap: **nobody serves port `8098`**. The `reportes` service lives there: asking a window where nobody is is the most faithful way to simulate a service that is down, and it always comes out the same.

Before each exercise in this lesson, start the server **in a second terminal** (with the virtual environment activated, from `~/curso-python/revisor/`) and leave it open:

```text
laboratorio en http://127.0.0.1:8099 (Ctrl+C para detenerlo)
```

That line is the only thing it prints; when you finish practicing, `Ctrl`+`C` in that terminal stops it. If you leave it off by mistake, you will see what happens: it is in “The error you will see.” In the usual terminal you keep running the lesson's programs.

## The concepts

### 9.1 HTTP: requesting an address and reading what it answers

#### 9.1.1 With the library Python already ships

`urllib.request` comes with Python; nothing has to be installed. Its main function, [`urlopen`](https://docs.python.org/3/library/urllib.request.html), receives an address, makes the request and returns the response as an object that can be used with `with` (the same `with` from Lesson 6, which closes the connection when done). Ask the practice server for the catalog:

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

Line by line. `respuesta.status` is the status code, `200`, and `respuesta.reason` is the phrase that goes with it, `OK`. `respuesta.read()` returns the body, and what comes out on the second line, `b'ok'`, has a `b` in front that is worth explaining: the network carries not text but **bytes**, numbers from 0 to 255, and `read()` hands them to you as they are. To turn them into text you have to say which encoding they were written in, which is the same UTF-8 from Lesson 6: `cuerpo.decode("utf-8")` gives the normal `str`, `ok`. The last line checks the time. [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) is Python's high-precision clock: it returns the seconds as a decimal, and subtracting two readings gives what took place between them. The server takes 142 ms to answer the catalog, so the request could not take less. Printing the exact time would make each run give a different number; the `True` is what does not change.

Notice what there is **not** in this program: any timeout. You will fix that in 9.2, but note it down from now on as a pending promise.

#### 9.1.2 Status codes, and `urllib`'s two exceptions

Requesting the catalog is the happy case. The `revisor` has to survive the other two: the service that answers with an error and the one that does not answer. This program queries one of each kind:

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

`catalogo` came out as expected. But `facturacion`, which answers `503`, **did not return a response: it raised an exception**, `HTTPError`, and that is why it entered the first `except`. It is a design decision of `urllib` that surprises at first: for this library, a `4xx` or `5xx` code is an exception, and the code it carries is read in `error.code`. And `reportes`, where nobody listens, raised `URLError`, which carries the real cause in `error.reason`. Here it is `ConnectionRefusedError` (the connection was refused). Notice that the program prints only the **name** of the cause, `type(error.reason).__name__` (`type` gives the class of the value, the one from Lesson 2, and `__name__` its name as text), and not the message. The operating system's message changes between computers (on Linux it says `[Errno 111]`, on macOS `[Errno 61]`), and the course decided that the detail the `revisor` shows is never that text: it says `sin conexión`, the same everywhere.

The **order** of the `except`s matters and is the same problem as in Lesson 6. [`HTTPError` is a subclass of `URLError`](https://docs.python.org/3/library/urllib.error.html): every `HTTPError` is also a `URLError`. If you put the `except URLError` first, it would catch everything and the `except HTTPError` below it would never run. The rule is the usual one: **the most specific first**.

#### 9.1.3 An address that is not from the internet: `file://`

There is a surprise in `urlopen`, and it has to do with security. An address begins with a **scheme**, the part before `://`: `http`, `https`, and also `file`, which means “a file on this same computer.” `urlopen` understands the `file` scheme:

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

The program creates a file `secreto.txt` (and deletes it at the end with `unlink()`, to leave nothing behind). Since it is going to overwrite it and then delete it, it first asks whether one with that name already exists: if it does, it stops without touching it, with `raise SystemExit(...)`, the same exception from Lesson 7, which this time carries a text instead of a number; Python prints that text on the error output and ends with code 1. Then it takes the absolute path of the file with `resolve()`, builds its address with [`.as_uri()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.as_uri) (which produces something like `file:///home/tu/secreto.txt`) and gives it to `urlopen`, which **reads it without complaint**. It is a legitimate function, but imagine the `revisor` reading addresses from a `servicios.toml` that someone else wrote, and someone puts `file:///etc/passwd` in place of a service's address: the program would read the file and treat it as a “response.” That is why in Lesson 6 the validation demanded that the scheme be `http` or `https`, with [`urlsplit(url).scheme`](https://docs.python.org/3/library/urllib.parse.html) inside `{"http", "https"}`; the last line of this program does that same check and answers `False` for `file`. It is not a matter of style: **an address that someone else writes is not handed to a library without checking where it points**. It is the second time you see the idea, and in Lesson 11 you will review it.

#### 9.1.4 Why the course moves to `httpx`

`urllib` works, but Python's own documentation [recommends another tool for something more convenient](https://docs.python.org/3/library/urllib.request.html) (“The Requests package is recommended for a higher-level HTTP client interface”). This course uses [`httpx`](https://www.python-httpx.org/), for four concrete reasons that you will see in this lesson:

| | `urllib.request` | `httpx` |
|---|---|---|
| A `503` | raises an exception | is a normal response, with its code |
| Default timeout | none | 5 seconds |
| Ways of using it | synchronous only (one thing at a time) | synchronous **and** asynchronous, with the same interface |
| A `file://` address | reads it | rejects it |

`httpx` does not come with Python, but you already have it: you installed it inside the virtual environment in Lesson 1, and from today it is the `revisor`'s only dependency. Compare with the `urllib` program:

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

The `503` **raised nothing**: `httpx.get` returned a response like any other, with `status_code`, `reason_phrase` and an `is_error` that is `True` for `4xx` and `5xx` codes. If you prefer an error to become an exception, there is `raise_for_status()`, which raises `httpx.HTTPStatusError`; the program demonstrates it, but the `revisor` will not use it. A `503` is not a failure of the `revisor`: it is the **data** the `revisor` came to collect. Treating it as an exception would take it off the normal path and force you to catch it just to put it back where it was. And the last part confirms the fourth row of the table: `httpx` rejects `file://` with `UnsupportedProtocol`. One more defense, not a substitute for the validation of Lesson 6.

### 9.2 Timeout: no request waits forever

There is a question we have not asked: what happens if the service **accepts** the connection and does not answer? It does not refuse it, does not close it: it simply stays thinking. Your program stays there, stopped, until something changes. If that “something” is a network outage or a hung service, it can be **forever**. The `revisor` exists to detect hung services; a `revisor` that hangs with them is worse than having no `revisor`. That is why this course has a single rule:

> **Every request carries a timeout. No exceptions.**

See how `urllib` is by default. The first line of the program prints Python's global timeout; then it requests `/notificaciones`, which takes 10 seconds, but now with `timeout=1`, one second:

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

[`socket.getdefaulttimeout()`](https://docs.python.org/3/library/socket.html#socket.getdefaulttimeout) returns `None`: the standard library, by default, **has no timeout at all** (the documentation of [`urlopen`](https://docs.python.org/3/library/urllib.request.html) says it uses the global value). Without `timeout=`, that request would have stayed ten seconds waiting; against a server that never answers, it would not have ended. With `timeout=1` the wait was cut at one second and Python raised `TimeoutError`.

`httpx`, on the other hand, comes with a timeout of 5 seconds: [the documentation](https://www.python-httpx.org/advanced/timeouts/) says it “raises a `TimeoutException` after 5 seconds of network inactivity.” Notice two words: *inactivity*, not total time. There are four distinct timeouts: for **connecting** (`connect`), for **receiving** a piece of the response (`read`), for **sending** (`write`) and for **getting** a free connection from the pool (`pool`). Each counts how long *one operation* waits, not how long the whole exchange lasts: a server that drips one byte every 4 seconds never triggers the 5-second `read` even if the response takes hours. The total cap per service you will set in Lesson 10 with `asyncio.timeout()`; today, the per-operation one is enough. A single number in `httpx.Timeout(1.0)` fixes all four at one second.

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

The first line shows `httpx`'s default value (`Timeout(timeout=5.0)`). Then, two requests with a timeout of one second, and each ends with a **different** exception, which is exactly what the `revisor` needs to tell apart:

- `/notificaciones`, which takes ten seconds, raised `httpx.ReadTimeout`: the connection was established, but the service did not answer in time. It is the cause of “tiempo agotado” (“timed out”).
- Port 8098, where nobody listens, raised `httpx.ConnectError`: there was no one to connect to. It is the cause of “sin conexión” (“no connection”).

The last three lines, with `issubclass` (which asks whether a class is the child of another), confirm the hierarchy [that `httpx` documents](https://www.python-httpx.org/exceptions/): `ReadTimeout` is a `TimeoutException`; `ConnectError` is **not**; and `ConnectError` is indeed an `HTTPError`, the parent class of almost everything `httpx` can raise. That decides the order of the `revisor`'s `except`s: first `TimeoutException`, then `ConnectError`, and at the end `HTTPError` to pick up whatever is left (a server that closes mid-response, for example). The three branches return a `Resultado` with status `CAIDO` and its detail (`tiempo agotado`, `sin conexión` or `error de red`, “network error”). **They never let the exception escape.**

Where the number comes from: each `Servicio` carries its `timeout_ms`, by default 5000, in milliseconds. `httpx` wants seconds, so the `revisor` divides: `httpx.Timeout(servicio.timeout_ms / 1000)`. The unit lives in the name (`timeout_ms`) precisely so that this conversion is not forgotten. **The first session ends here.**

### 9.3 Coroutines: functions that can wait

#### 9.3.1 A coroutine does not run when you call it

In the second session comes the idea that costs the most. During the 2.3 seconds that `inventario` takes to answer, your program does nothing: it waits. All that time, the processor is free. A **coroutine** is a function that can **pause at the point where it waits** and let something else use that time. It is written with `async def`, instead of `def`:

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

`saludar` (“greet”) is a normal function in everything but its first word. But notice what `print(saludar())` printed: it does **not** say `hola`. It says `<coroutine object saludar at 0x...>`. Calling an `async def` function does not run its body; it creates a **coroutine object**, a recipe on pause. [The `asyncio` documentation](https://docs.python.org/3/library/asyncio-task.html) puts it this way: calling a coroutine does not schedule it to run, and in its example `nested()` is called without being awaited: the object is created, but the body “won't run at all.” And since the object was thrown away without anyone running it, Python warns: `RuntimeWarning: coroutine 'saludar' was never awaited`. The warning includes the line of the program where it was called and is **the most common signal** that you forgot an `await`.

#### 9.3.2 `asyncio.run`: the start

How, then, is a coroutine run? It needs a coordinator to run it, the **event loop**: a small program, inside Python, that divides time among the paused coroutines. You do not handle it directly. [`asyncio.run`](https://docs.python.org/3/library/asyncio-runner.html) creates it, runs the coroutine you give it until it finishes, returns its result and closes the loop:

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

Now it works: `hola`. `asyncio.run` is written once, at the entrance of the program, and from there everything else is chained with `await`. In the `revisor` it will live in `cli.py`.

#### 9.3.3 `await` and `async with`: waiting for another coroutine

Inside a coroutine, `await` means **“wait here for this other thing to finish, and while you wait, let the loop do other things”**. It is the explicit way to pause a coroutine, and it only works inside an `async def` function. (There are two others, which wait without your writing the word: `async with`, which you will see in a moment, and `async for`, which the course does not use; [the language reference](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement) explains that inside they do `await`.) The coroutine you will wait for most in the course is an `httpx` request, and for that `httpx` brings [an asynchronous version of the client](https://www.python-httpx.org/async/), `httpx.AsyncClient`, which is used with an `async with`:

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

`async with` is the `with` from Lesson 6 for resources whose opening and closing **can also** wait: creating and closing the network client is an operation of this kind. Inside, `cliente.get(...)` is a coroutine; `await` waits for it, and what you get is the response. Notice that the response is exactly the same as in the synchronous `httpx.get`: `status_code`, `is_error` and the rest. The difference lies in how it is waited for. And the client is **created once and reused** for several requests: opening and closing one per query would be like hanging up and redialing each time you ask a question.

### 9.4 One `await` after another saves no time: the series

Here is the most widespread misunderstanding about `asyncio`, and it is worth dismantling with a measurement. A beginner reads “asynchronous” and assumes “faster.” It is not. Look at this program, which waits three times half a second, one after another, each with `await` ([`asyncio.sleep`](https://docs.python.org/3/library/asyncio-task.html#sleeping) is the usual asynchronous wait):

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

The last line asks `1.5 <= total < 2.0`, both things at once: that `total` be at least 1.5 and less than 2. The three waits took the **sum**: 1.5 seconds or more. You gained nothing. The reason lies in what `await` really does: it pauses **this** coroutine and offers the loop the chance to attend to others, but in this program **there are no others**. The loop offers the turn and nobody takes it. It is the same [sequence that Python's documentation shows](https://docs.python.org/3/library/asyncio-task.html): an `await` followed by another `await` runs in series. To save time you need **several coroutines alive at once**, and that is achieved with tasks (`asyncio.TaskGroup`), which is the content of Lesson 10.

Today's `revisor`, then, will be an asynchronous version that behaves **like the synchronous one**: it queries the services one by one. Why, then? First, because it is the intermediate step that makes the gain visible: Lesson 10 measures the same table of services in series and in parallel, and needs the starting point. Second, because changing from `def` to `async def` touches the whole chain of calls, and it is easier to understand doing it before bringing in concurrency. And third, because what matters in this step is everything that has nothing to do with time: timeouts, exceptions, classification.

### 9.5 The `revisor` queries for real

With all of the above, `revision.py` is rewritten whole. `SIMULADO` is deleted, and the two functions become coroutines:

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

Read `revisar` from top to bottom. It receives a **client** and a **service**; the client comes from outside so that it is reused. It builds the `httpx.Timeout` with the service's `timeout_ms`, notes the time with `time.perf_counter()` (Python's high-precision clock) and makes the request with `await`. The first three `except`s are those of 9.2, **from the most specific to the most general**, and each returns a down `Resultado` with its text. The fourth catches something that is not a network error: an address that passed the validation of Lesson 6 but that `httpx` cannot use. It happens, for example, with `http://999.1.1.1:8099/pagos`: for `urlsplit` it is an address with a server and a port, but each of the four parts of an IP address goes from 0 to 255, and 999 does not fit, and `httpx` rejects it with `httpx.InvalidURL`, which is **not** a child of `httpx.HTTPError` (as [its exception hierarchy](https://www.python-httpx.org/exceptions/) shows). Other impossible server names end in a `ValueError` from the libraries `httpx` uses inside. Without this `except`, a single one of those services would take down the whole report with a *traceback*; with it, it appears in its row as `CAIDO`, with the detail `dirección inválida` (“invalid address”), and the others are checked just the same. The `ValueError` is caught here, around a single call, and not in the whole program: a `ValueError` from your own code, outside the `try`, would still stop it with its report, as it should. If there was no exception, it measures how much time passed (`round(... * 1000)` converts seconds to whole milliseconds), classifies with the same `clasificar` function as always, which receives the real code, and builds the `Resultado` with the code as the detail. A `503` goes through here: it is not an exception, it comes out with `clasificar(503, 95)` and becomes `CAIDO` with detail `503`.

`revisar_todos` opens **one** client with `async with` and walks over the services with a `for` and one `await` per turn. It is the series of 9.4, written on purpose. The order of the results is that of the configuration.

`main` in `cli.py` changes in only one line: the call is wrapped in `asyncio.run`.

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

So that `asyncio.run` has something to run, `revisar_todos(servicios)` without `await` produces a coroutine, and `asyncio.run` runs it. It is the only `asyncio.run` in the program. The tests still call `main` as a normal function, so they **do not need to be coroutines**; this is what makes it possible not to install any `pytest` plugin for asynchronous code. The other changes are data. The `pyproject.toml` rises to `0.8.0` and declares the package's first dependency, `httpx`:

```toml
dependencies = ["httpx>=0.28"]
```

Reinstall the package (`pip install -e .`) so that the environment sees the dependency and the new version. And the `servicios.toml` now points to the practice server: the same four names, other addresses. (The complete project is in 9.6.)

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

With the practice server open in the other terminal, run the `revisor` and look at the exit code:

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

It is the syllabus table, now **measured**: `catalogo` and `pagos` up with real times (the server waits 142 and 87 ms, and each request adds a few milliseconds of network, so you will see numbers like 156 and 98, different on every run), `inventario` slow with 2.3 s, `reportes` down with `sin conexión` (nobody listens on 8098). The summary counts two up, one slow, one down, and the exit code is `1`, the same as always, for the same reason: there is one slow and one down. What changed is that now it is true.

How long does it take? In series, the sum: 142 + 2300 + 87 is about 2.5 seconds of waiting plus the time Python takes to start and load `httpx`. Measured with the terminal's `time` command, a full run lasts about 2.7 seconds. Yours will give a close number, not an equal one. That figure is the starting point of Lesson 10. Exercise 1 measures it.

And the tests: run them.

```text
$ cd fig09_11
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

They are still **21**. The only test file that changed is `tests/test_cli.py`, and not on a whim. Its first test used the simulated data to check that `main` returns `1`, and those no longer exist; and the `monkeypatch` fakes now return a coroutine, because the real one is a coroutine and `main` does `asyncio.run` of whatever they return. That is why they are `async def`:

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

A warning that has to be said out loud: **the report says `21 passed` and yet the new code does not have a single test**. Nothing of what you have just written (the timeout, the classification of a `503`, the `sin conexión`) is exercised in those 21. The two tests in `test_cli.py` replace `revisar_todos` entirely, so the network code is not even touched. That is the size of the hole, and it is the reason for Lesson 10: how to test network code without a network.

### 9.6 The complete project

The snapshot of the project at the end of the lesson. The files you have already seen are `laboratorio.py`, `servicios.toml`, `revision.py`, `cli.py` and `tests/test_cli.py`. The `pyproject.toml` is that of Lesson 8 with the new version and dependency:

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

The other files **do not change** from Lesson 8, and are repeated here only so that the project is complete:

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

The four checks from Lesson 8, which now also cover the asynchronous code:

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

## The error you will see

### `RuntimeWarning: coroutine 'saludar' was never awaited`

You saw it in 9.3.1, with the program `fig09_07.py`, and it is worth repeating how it is read. The warning is not an error: the program **goes on** and ends with code `0`, which is the dangerous part, because there is one warning among dozens of lines and it is easy to overlook. It says three things: the file and the line where you called the coroutine without awaiting it (`fig09_07.py:6`, and below it prints the line itself, `print(saludar())`), which coroutine it was (`'saludar'`), and the consequence: its body never ran. The cure is almost always one word: put `await` in front of the call, or pass it to `asyncio.run`.

In the project, `mypy` warns you **before** running. Remove the `await` from the line `resultados.append(await revisar(cliente, servicio))` in `revisar_todos`, and this is what `mypy` says:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
Found 1 error in 1 file (checked 11 source files)
```

You had told the list that it held `Resultado`, and you are giving it a `Coroutine`. And `mypy` guesses it with a note: “Maybe you forgot to use "await"?” It is the kind of help for which types were written in Lesson 8. If you ignore the warning and run the program, the table prints its header and stops with `AttributeError: 'coroutine' object has no attribute 'servicio'` (the last line of the *traceback*), followed by the same `RuntimeWarning` at the end.

### All the services say `sin conexión`

If you forget to start the practice server, the `revisor` does not fall over; it does exactly what it should. This is what it prints with the server off:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO          —  sin conexión
inventario  CAIDO          —  sin conexión
pagos       CAIDO          —  sin conexión
reportes    CAIDO          —  sin conexión

4 servicios · 0 arriba · 0 lentos · 4 caídos · promedio —
```

There is no `Traceback`. All four services are `CAIDO`, with `sin conexión` and without a time (`—`), because nobody answers on port 8099, just as on 8098. This is the design working: a service that does not answer is a **piece of data**, not an exception that takes down the report. The signal for you is that `reportes` should not be the only one down: if all four are, before looking for an error in your code, check whether the second terminal is still open. (Notice also the average: it comes out as `—`, like the time of each row, because there are no times to average. It is the same decision as in Lesson 2: what was not measured is not worth `0`.)

### The test that breaks because its fake stopped being a coroutine

If you leave `tests/test_cli.py` as it was in Lesson 8, and only change `revision.py` and `cli.py`, `pytest -q` says `1 failed, 20 passed`. The red one is the test that uses the fake with `def` instead of `async def`. The last line of the error changes wording depending on your version of Python, but says the same:

```text
ValueError: a coroutine was expected, got [Resultado(servicio=Servicio(nombre='catalogo', ...
```

(in Python 3.12) or

```text
TypeError: An asyncio.Future, a coroutine or an awaitable is required
```

(in 3.14). `asyncio.run(...)` received a **list** and expected a coroutine, because `main` does `asyncio.run(revisar_todos(servicios))` and the fake, being `def`, returned the result directly. The fix is the one you saw: make the fake `async def`.

But there is something more subtle. A **second** old test, the one that ran with the simulated data, **stays green**, and it should not. That test used `https://catalogo.example` addresses and expected `main` to return `1`. Now `main` makes real requests to those made-up addresses, fails to connect to any, marks them all as down and returns `1`. The test passes, but **for a completely different reason** from the one it was written for, and it depends on `.example` never resolving and on your network answering quickly that it does not exist. It is what happens when a green test holds up something that is no longer what it says: the fake was replaced by a test that does not do what its name promises. That is why it was rewritten with an explicit fake.

## What gets done wrong

**Making a request without a timeout.** It is the error this lesson exists to avoid. With `urllib`, without `timeout=`, the program waits as long as it takes, including forever. With `httpx`, the default limit is 5 s, but depending on a default value without knowing it is leaving an important decision in someone else's hands. The `revisor` always sets it, per service.

**Catching `Exception` and going on.** `except Exception: pass` around a request makes a `ReadTimeout`, a `ConnectError` and a programming error look identical: nothing. The `revisor` catches three specific exceptions, each with its text, and lets any other be seen.

**Printing the operating system's message.** `[Errno 111] Connection refused` changes with the system and with the language; a service's report must not change text depending on where it is run. The detail is one of three fixed phrases.

**Assuming `async` is faster.** You dismantled that in 9.4: one `await` after another adds up their times. An `async` function without concurrency is a synchronous function with more ceremony.

**Calling a coroutine without `await`.** The warning of 9.3.1. With `mypy` in strict mode it becomes a type error, which is why it is worth running.

**Blocking inside a coroutine.** A `time.sleep(1)` inside an `async def` stops **the whole** program for a second: nobody else can advance, because the loop is stuck inside that call. Inside a coroutine, the wait is `await asyncio.sleep(1)`. The same goes for network libraries that are not asynchronous, such as `urllib` or `httpx.get`.

**Creating a client per request.** `httpx.AsyncClient()` opens a pool of connections that are reused. Opening and closing one on each query throws that saving away; the `revisor` opens one at the start of `revisar_todos` and shares it.

**Treating a `503` as if it were a failure of the program.** A service that answers with an error is the result of the work, not an incident of the `revisor`. That is why the code is read and classified; `raise_for_status()` would turn the data into an exception.

**Putting `0` where there was no response.** A down service has `tiempo_ms=None`, not `0`: with zero, the average rewards the down one. It is the same lesson as Lesson 2, in a bigger project.

## Exercises

### Exercise 1 — Measure the series with the clock

With the practice server on, measure how long the whole `revisor` takes: `time python -m revisor`. Before running it, **predict** the number from what you know: the sum of what each service takes. Run it three times and note the three in your logbook. Why are they not identical? This number is your starting point for Lesson 10.

### Exercise 2 — Remove a request's timeout and see why it is dangerous

Write a six-line program that uses `httpx.get` with `timeout=None` (which [disables the timeout](https://www.python-httpx.org/advanced/timeouts/)) against `http://127.0.0.1:8099/espera/60000`, which takes a minute. Run it, let five seconds go by and press `Ctrl`+`C`. What is printed? How long would it have taken to finish on its own? Then give it `timeout=2.0` and compare.

### Exercise 3 — The two extra services

Add to your `servicios.toml` `facturacion` (`http://127.0.0.1:8099/facturacion`) and `notificaciones` (`http://127.0.0.1:8099/notificaciones`, with `timeout_ms = 1000`). Before running, predict the status and detail of each, and what the summary line will be. Does anything in the table look odd to you? Put the file back to its four services when you finish.

### Exercise 4 — Forget an `await` on purpose

In `revisar_todos`, remove the `await` from `resultados.append(await revisar(cliente, servicio))`. Run `mypy`, then `python -m revisor`, and read the two signals: what each says, and which arrived first. Put the `await` back.

## Solutions

### Solution 1

The prediction: 142 + 2300 + 87 = 2529 ms for the three that answer, plus the time it takes to try to connect to `reportes` (a few milliseconds, because they refuse immediately), plus the start-up of Python and `httpx`. That gives about **2.6 or 2.7 seconds**, and it is what the clock measures: a reference run gave 2.674 s. The three runs are similar but not identical because the server, the operating system and the network add small variations of a few milliseconds each time. What matters is the order of magnitude: about 2.5 seconds, because **it is the sum**. If Lesson 10 manages to bring it close to 2.3 s (the slowest service), it will have gained less than it seems with four services; that is why that lesson's strong measurement uses twenty.

### Solution 2

```python
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/espera/60000", timeout=None)
print(respuesta.status_code)
```

With `Ctrl`+`C` at five seconds, Python prints a *traceback* that ends in `KeyboardInterrupt`: you interrupted, not the program. It would have taken **a whole minute** to finish on its own, printing nothing in the meantime. Against a server that never answers, it would never have finished: that is what “without a timeout” means. With `timeout=2.0` the program raises `httpx.ReadTimeout` at two seconds. That `ReadTimeout` is an exception **that can indeed be caught**, which is what `revisar` does.

### Solution 3

The prediction: `facturacion` answers `503` in 95 ms, so `CAIDO` with detail `503` and a time of about 100 ms. `notificaciones` takes 10 s but its limit is 1 s: `CAIDO` with `tiempo agotado` and no time. The summary: `6 servicios · 2 arriba · 1 lento · 3 caídos`. This is what it prints:

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

The odd thing is the last row: `notificacionesCAIDO`, with no separation. The name has 14 letters and the `SERVICIO` column is 12 wide (`{nombre:<12}`), so it overflows and sticks to the next one. It is a real limit of the table as it is today, and it is one of the things Lesson 11 fixes by calculating the width from the longest name. Count the time too: the whole run took about 3.8 s instead of 2.7, because `notificaciones` waits its full second before giving up. Each slow or hung service adds its wait to the series, which is what Lesson 10 comes to solve.

### Solution 4

`mypy` complains **first**, without running anything:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
```

When you run the program, the header is printed and it stops with `AttributeError: 'coroutine' object has no attribute 'servicio'`, because the list has coroutines instead of results, and at the end `RuntimeWarning: coroutine 'revisar' was never awaited` appears. `mypy` arrived first, and it did so with the cause and with the suggestion; the run-time error only shows the consequence. It is the argument in favor of running `mypy` before the program.

## How I know I got it

- [ ] With the practice server on, `python -m revisor` prints the table of four services with `catalogo` and `pagos` up, `inventario` slow (`2.3s`) and `reportes` down with `sin conexión`, and `echo $?` prints `1`.
- [ ] With the server off, all four say `CAIDO` and `sin conexión`, and the program prints no *traceback*.
- [ ] `pytest -q` says `21 passed` (the same number as in Lesson 8), and you can explain which part of the program none of the 21 covers.
- [ ] `mypy` says `Success: no issues found in 11 source files`, `ruff check` says `All checks passed!` and `ruff format --check` says the files are already formatted.
- [ ] You measured the run with `time` and your number is near 2.7 seconds, and you can explain why it is the sum and not the maximum.
- [ ] You can explain what `await` does, what `asyncio.run` does and why a bare `saludar()` does not print `hola`.
- [ ] You can say with which `httpx` exception a service that does not answer ends and with which one where nobody listens, and why a `503` is not an exception.

## Summary

Answer without looking at the lesson:

1. What does an HTTP response carry, and which families of status code are there? Which ones make a service `CAIDO`?
2. What does `urllib` do when the server answers `503`, and what does `httpx` do?
3. Why does `urlopen` accept a `file://` address, and what stops it in the `revisor`?
4. What timeout does `urllib` have by default, and which does `httpx`?
5. Which `httpx` exception does a service that does not answer produce, and which one where nobody listens?
6. What does `asyncio.run` do? What happens if you call an `async def` function without `await` or `asyncio.run`?
7. Why do three consecutive `await`s of half a second take 1.5 s and not 0.5 s?
8. Why does the report of Lesson 9 still say `21 passed` and what did it leave untested?

## Further reading

- [HTTPX, “Timeouts”](https://www.python-httpx.org/advanced/timeouts/) — the four timeouts (`connect`, `read`, `write`, `pool`), the default value and how to disable them. Accessed on October 7, 2026.
- [Python, “Coroutines and tasks”](https://docs.python.org/3/library/asyncio-task.html) — the official `asyncio` documentation: coroutines, `await`, tasks and the warning of the coroutine never awaited. Accessed on October 7, 2026.
- [RFC 9110, “HTTP Semantics”](https://www.rfc-editor.org/rfc/rfc9110.html) — the HTTP standard; the status codes section defines what each number means. It is a text to consult, not to read straight through. Accessed on October 7, 2026.
- [PEP 492, “Coroutines with async and await syntax”](https://peps.python.org/pep-0492/) — the document that introduced `async` and `await`; it explains why they are reserved words of the language. Accessed on October 7, 2026.
