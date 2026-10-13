# Lesson 10 — Concurrency with limits and tests without a network

**Time:** 2 × 90 min (the first session runs to the end of 10.2; the second starts at 10.3)

**What you build:** the concurrent, tested `revisor`, version 0.9.0

**What you learn:** `asyncio.TaskGroup`; `asyncio.timeout()` and `asyncio.Semaphore`; exception groups (`ExceptionGroup`, `except*`) and why one failure does not take down the report; tests without a network with `httpx.MockTransport` and `monkeypatch`

**Where you come from.** You bring the package from [Lesson 9](09-http-y-asyncio.md): the `revisor` already queries for real, with `httpx`, a timeout per service and a `revisar` function that never lets a network error escape. But it does so **in a line**: `for` and `await`, one service at a time. With the four services of the lab server the run takes the sum of the waits, about 2.5 seconds, and with twenty half-second services it would take ten. It also has a debt that the previous lesson stated plainly: its 21 tests touch nothing of what is new, because you did not yet know how to test code that uses the network. Today both things are paid. You work in your `~/curso-python/revisor/` folder, with the virtual environment activated, and you need to have the `laboratorio.py` from Lesson 9 at hand for the measuring part.

**What this lesson does not do.** It does not change what the `revisor` prints: the table and the JSON come out the same as in Lesson 9. What changes is **how long it takes** and **how safe it is**. Nor does it use threads or processes: all of today's concurrency happens in a single thread, which is the right choice when the work is waiting for the network. The final report with a calculated column width, the event log (`logging`) and installation as a command belong to [Lesson 11](11-el-programa-terminado.md).

## By the end you will be able to

- Launch several queries at once with `asyncio.TaskGroup`, collect their results in the order of the configuration and measure with the clock that the total resembles the slowest service and not the sum.
- Explain why a task only yields its turn at an `await`, and why a `time.sleep` inside a coroutine undoes all the gain.
- Put a time ceiling on a whole operation with `asyncio.timeout()` and say how it differs from `httpx`'s timeouts.
- Limit how many queries run at once with `asyncio.Semaphore`, and explain why with 20 services and a limit of 10 the time is double that with a limit of 20.
- Read an `ExceptionGroup` and catch what it contains with `except*`; say why `revisar` converts network errors into results and why it does **not** convert programming errors.
- Test `revisar` and `revisar_todos` without touching the network, with `httpx.MockTransport`, and test `main` by swapping one function for another with `monkeypatch`.
- Check a test in red (break the code, watch it fail, fix it) and read the `pytest` report's count.

## The why before the how

Imagine the `revisor` is used by a company's on-call team to check sixty services every five minutes. Each healthy service answers in half a second; the down ones take until their timeout to give up, say five seconds. In a line, on the best day the run takes thirty seconds, and on the worst day, with ten services down, it takes seventy-five (fifty healthy ones at half a second, plus ten down ones at five seconds). But the computer was not working during those seventy-five seconds: it was **waiting**. It sent a request, stared at the wall until the response arrived, and only then sent the next one. The network does not need the program to stand in line: the sixty requests can be traveling at once, and the program only has to collect the responses as they arrive.

That is what `asyncio` does well, and that is why this lesson exists. But there are three problems hidden behind “do it all at once,” and each one is a concept for today.

The first is **how to launch and collect** many queries without losing any. Python 3.11 brought a tool designed for that, `asyncio.TaskGroup`, which starts the tasks, waits for all of them before going on and does not let any get lost along the way.

The second is **how far**. “All at once” with sixty services is reasonable. With six thousand it can be an attack on your own servers, or your operating system saying it will give you no more connections. A limit is needed on how many queries run simultaneously, and a time ceiling is needed so that none stays hung forever.

The third is **what happens when something fails**. In a line, an error stops the program at the exact point where it occurred, and it is easy to understand. With many tasks at once, a failure can affect the others, and what Python hands you is not an exception but a **group** of them. If you do not understand it, a single service being down can take down the whole report, which is exactly the opposite of what the `revisor` promises.

And underneath everything, the fourth problem, that of trust: a program that does so many things at once, with times and failures mixed together, **cannot be tested by hand** in a repeatable way. If to check that “a hung service does not take down the report” you need to hang a real service, you will never check it the same way twice. The fourth part of the lesson teaches how to test all that without a network: with a fake server that answers whatever you say, instantly, always the same.

## The concepts

### 10.1 `TaskGroup`: all at once

#### 10.1.1 What waiting in a line costs

Before fixing something it has to be measured. This first program does not use the network: each “service” is a real wait, made with `asyncio.sleep`, which is the way to say “do nothing for this time, but let me do something else meanwhile.” The waits are those of four made-up services, from a tenth to half a second, so the runs are short.

```python
# fig10_01.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    for nombre, espera_s in ESPERAS_S.items():
        await consultar(nombre, espera_s)
    print(f"en serie: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_01.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
en serie: 1.1 s
```

Read `main` from top to bottom. `time.perf_counter()` is the clock for measuring intervals that you already used in Lesson 9: it is called at the beginning and at the end, and the subtraction is the elapsed time. The `for` walks over the dictionary with `.items()` (which gives you each name-wait pair) and, for each one, does `await consultar(...)`. The `await` says “wait here for this coroutine to finish”; until it finishes, the `for` does not move to the next turn. That is why the responses come out in the order they were requested, and why the total, 1.1 seconds, is the exact sum: 0.3 plus 0.5 plus 0.1 plus 0.2.

It is the same problem you measured in Lesson 9 with the `revisor`: `await` on **a single coroutine** waits for it to finish before going on. It is not a defect of `await`; it is what it means. For two waits to happen at once, both must **exist** at the same time, and that is what a task is for.

#### 10.1.2 A task: a coroutine that is already running

A **coroutine** is a recipe: `consultar("catalogo", 0.3)` does nothing, it only produces the recipe object, and the recipe starts being executed when someone does `await` on it. A **task** is a coroutine that has already been wound up: the event loop has it noted in its list of pending items and runs it as soon as it can, **without anyone yet awaiting it**. The **event loop** is the piece of `asyncio` that keeps that list: it takes a task, runs it until it comes across an `await` that has to wait, puts it on pause, takes the next one, and so on, in a single thread.

With that in hand, the at-once version:

```python
# fig10_02.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    print(f"{nombre}: empieza")
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        tareas = [
            grupo.create_task(consultar(nombre, espera_s))
            for nombre, espera_s in ESPERAS_S.items()
        ]
    print(f"a la vez: {time.perf_counter() - inicio:.1f} s")
    print([tarea.result() for tarea in tareas])


asyncio.run(main())
```

```text
$ python fig10_02.py
catalogo: empieza
inventario: empieza
pagos: empieza
reportes: empieza
pagos: respondió
reportes: respondió
catalogo: respondió
inventario: respondió
a la vez: 0.5 s
['catalogo', 'inventario', 'pagos', 'reportes']
```

Only one thing changed: instead of `await consultar(...)` inside the `for`, `grupo.create_task(consultar(...))` is done. That **does not wait**: it registers the task and returns at once, with a `Task` object in hand. That is why the `for` (here, inside a list comprehension, which is the `for` on one line from Lesson 4) goes through the four services in an instant and leaves four tasks pending. Look at the output: the four “empieza” (“starts”) come out first, one after another, before any responds. Then they respond in order of **speed**, not of request: `pagos` (0.1 s), `reportes` (0.2 s), `catalogo` (0.3 s), `inventario` (0.5 s). And the total is no longer 1.1 but 0.5: that of the slowest.

And the `async with asyncio.TaskGroup() as grupo:`? It is what makes this safe. It works like the `with` from Lesson 6: on **leaving** the block, the group **waits for all the tasks it created to finish**. That is why the line `print(f"a la vez: ...")`, which is after the block, only runs when all four have responded. You can create the tasks wherever you like inside the block; you cannot forget any, because the block does not let you leave while one is alive. That is what the [`asyncio` documentation](https://docs.python.org/3/library/asyncio-task.html#task-groups) calls *structured concurrency*: tasks are born and die inside an indented block, just as a `with` closes its file.

#### 10.1.3 The results and their order

`create_task` returns the task, and the task keeps its result. After the block, `tarea.result()` hands it to you: if the task ended well, the value its function returned; if it failed, it raises the exception again. Notice the detail that matters for the `revisor`: we keep the tasks **in a list, in the order of the services**, and then take the results out **by walking that list**. The responses arrived out of order (pagos first), but the last line of the output, `['catalogo', 'inventario', 'pagos', 'reportes']`, is in the order of the configuration. That order is not a luxury: a report where the rows change place on every run is unreadable, and a JSON compared against yesterday's needs to be in the same order. The rule is simple: **the order in which responses arrive is decided by the network; the order in which they are shown is decided by you**, and it is decided by keeping the tasks in a list and not by piling up the results as they finish.

#### 10.1.4 A task only yields its turn at an `await`

One piece is missing for the mental model to be complete, and it is the one that produces the most errors. The event loop runs **in a single thread**. When it runs a task, that task has the entire thread until it releases it itself, and it releases it only at an `await` that has to wait. Between two `await`s, nobody else runs. That is called **cooperative** concurrency: tasks cooperate by yielding their turn. If a task does not cooperate, it blocks all of them. See what happens if instead of `await asyncio.sleep(...)` the usual `time.sleep(...)` is used, which is a wait that **yields nothing**:

```python
# fig10_03.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    time.sleep(espera_s)  # noqa: ASYNC251
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for nombre, espera_s in ESPERAS_S.items():
            grupo.create_task(consultar(nombre, espera_s))
    print(f"TaskGroup con time.sleep: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_03.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
TaskGroup con time.sleep: 1.1 s
```

It is the same `TaskGroup` as in the previous figure, with the four tasks created the same way. But the result is different: they are printed in the order they were created, not in the order of speed, and the total is 1.1 seconds, the sum. Why? Because the first task reached `time.sleep(0.3)`, and `time.sleep` stops **the thread**, and with the thread stopped the event loop cannot even move to the next task. The other three waited their turn, in a line, even though they are in a `TaskGroup`. This error is especially treacherous because **the program does not fail**: it gives the correct result, only as slowly as if there were no concurrency. The comment `# noqa: ASYNC251` is there because `ruff` (the tool from Lesson 8) knows this error and flags it, although not with the `revisor`'s set of rules: `ASYNC251` is from the `ASYNC` collection, the one for `asyncio` errors, which is not in the project's `select` (`E`, `F`, `I`, `B`, `UP`). If you ask for it, `ruff check --select ASYNC` on this figure without that comment says ``ASYNC251 Async functions should not call `time.sleep` ``. And if your code uses `asyncio` seriously, it is a good candidate to enter your `select`. In this figure we leave it on purpose to show the damage; in your real code, `ruff`'s warning is a clue to follow.

The practical rule: inside a coroutine, everything that waits (network, slow disk, time) must be an `await` on something made for `asyncio`: `asyncio.sleep`, `httpx.AsyncClient`. A normal call that takes long (a `time.sleep`, a long calculation, a function from `requests`) does not cooperate and takes the whole loop with it. It is the reason the course uses `httpx` and not `requests`: `httpx` knows how to wait without blocking. The documentation chapter on [developing with `asyncio`](https://docs.python.org/3/library/asyncio-dev.html) brings the debug mode, which warns when a task holds the thread for too long.

### 10.2 Limits: a time ceiling and a cap on simultaneous queries

#### 10.2.1 `asyncio.timeout()`: the ceiling of a whole operation

Since Lesson 9 you know that every request must carry a timeout: without it, a hung service makes the `revisor` wait forever. `httpx` already has one, the one you pass with `httpx.Timeout(...)`. So why another?

Because `httpx`'s timeouts measure **phases**, not the total. According to [its documentation](https://www.python-httpx.org/advanced/timeouts/), `httpx` distinguishes four: that of **connection** (how long to wait to open the channel), of **reading** (how long to wait for the next piece of data), of **writing** and of **waiting for a free channel in the connection pool**. `httpx.Timeout(5.0)` sets those four at 5 seconds, each on its own. A server that sends a byte every four seconds never triggers the reading one — each piece arrives in time — and the response can take minutes. `httpx` did nothing wrong: each phase met its limit. What is missing is a limit on the **whole**. That is `asyncio.timeout()`, which exists since Python 3.11 and is in the [`asyncio` documentation](https://docs.python.org/3/library/asyncio-task.html#timeouts):

```python
# fig10_04.py
import asyncio
import time


async def servicio_colgado() -> None:
    await asyncio.sleep(10)


async def main() -> None:
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(1):
            await servicio_colgado()
    except TimeoutError:
        print(f"tiempo agotado tras {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_04.py
tiempo agotado tras 1.0 s
```

The block `async with asyncio.timeout(1):` puts a 1-second clock on everything that happens inside. Inside there is a 10-second wait. When the second is up, `asyncio` **cancels** whatever is waiting inside the block and, on leaving, raises `TimeoutError` (a normal Python exception, since 3.11; before it was called `asyncio.TimeoutError`, which today is just another name for the same one). The `except TimeoutError` catches it, and the program prints the time it really waited: 1.0 seconds, not 10. Learn the two effects of the block: it **cuts** the wait (tasks are not left hung) and it **warns** with an exception that you decide how to handle.

The two mechanisms do not get in each other's way; they complement each other. In today's `revisor` they coexist: `httpx.Timeout` sets the limit for each phase, and `asyncio.timeout` the one for the whole service. Both use the service's `timeout_ms`, and whichever of the two is met first produces the same result: “tiempo agotado.” Later, in 10.4, you will see one of the advantages of having both: `asyncio`'s ceiling works even when `httpx` does not take part.

#### 10.2.2 `asyncio.Semaphore`: how many at a time, at most

A **semaphore** is a counter of permits. It is created with a number, `asyncio.Semaphore(2)`: there are two permits. Whoever wants in does `async with semaforo:`; if a permit is left, it takes it and goes in, and if not, it **waits** until another returns it on leaving. It is the entrance to a parking lot with two spaces: when it is full, the next car waits in the street until one leaves. The [documentation](https://docs.python.org/3/library/asyncio-sync.html#semaphore) describes it in those terms. Let us look at six half-second services with room for two at a time:

```python
# fig10_05.py
import asyncio
import time


async def consultar(semaforo: asyncio.Semaphore, numero: int) -> None:
    async with semaforo:
        print(f"servicio {numero}: entra")
        await asyncio.sleep(0.5)
        print(f"servicio {numero}: sale")


async def main() -> None:
    semaforo = asyncio.Semaphore(2)
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for numero in range(1, 7):
            grupo.create_task(consultar(semaforo, numero))
    print(f"seis servicios, de dos en dos: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_05.py
servicio 1: entra
servicio 2: entra
servicio 1: sale
servicio 2: sale
servicio 3: entra
servicio 4: entra
servicio 3: sale
servicio 4: sale
servicio 5: entra
servicio 6: entra
servicio 5: sale
servicio 6: sale
seis servicios, de dos en dos: 1.5 s
```

Read the output in groups of four lines. 1 and 2 enter; both leave half a second later; only then do 3 and 4 enter, and so on. Six services, two at a time: three batches of half a second, 1.5 seconds in total. All the tasks were created at once in the `TaskGroup`, but four of them stayed waiting at `async with semaforo` without spending anything. Notice also the order: 3 enters before 4, 5 before 6. In CPython the semaphore usually serves in the order in which they arrived, but the [documentation](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) does not promise it (it does promise it for `Lock`), so your program must not depend on that order. The `revisor` does not: the order of its report is given by the list of services, not by the order in which they finished.

What is the right limit? It depends on **who receives** the queries. If they are your own services, what they can bear; if they belong to a third party, what their documentation allows; if there are many and you do not know, a moderate number. The `revisor` uses **10** by default and lets the user change it with `--concurrencia`. The semaphore also protects your own machine: each open connection uses a file descriptor, and every operating system has a cap. And `httpx` limits on its own the set of open connections (100 by default, as [its documentation on limits](https://www.python-httpx.org/advanced/resource-limits/) says), so a limit greater than that would only make the queries wait in another line.

#### 10.2.3 Taking it to the `revisor`

The whole change of this half fits in three files and a new data file. First the package's version, `0.9.0` (the `httpx` dependency was already there since Lesson 9):

```toml fig10_08/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.9.0"
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

Then the heart, `revision.py`. Read it in three movements:

```python
# fig10_08/src/revisor/revision.py
import asyncio
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
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

**First, `revisar`** (a single query). It changed very little from Lesson 9: the `await cliente.get(...)` now lives inside `async with asyncio.timeout(servicio.timeout_ms / 1000):`. The division by a thousand is because `timeout_ms` is in milliseconds and `asyncio.timeout` wants seconds. In the `except`, `(httpx.TimeoutException, TimeoutError)` catches both timeouts: `httpx`'s phase one and `asyncio`'s ceiling. With parentheses, because in Python 3.12 an `except` with two classes carries them inside a tuple. The rest is the same: each network error is converted into a `Resultado` with its detail, and the function **never** lets a network error out. There is one exception that `revisar` deliberately does **not** catch and that deserves a paragraph: `asyncio.CancelledError`. It is the way `asyncio` tells a task “you have been cancelled.” If you caught it, you would swallow the order to cancel and the `TaskGroup` or the `timeout` would be unable to do their job. That is why the `except` names specific classes and is never a wide `except Exception`: the rule of Lesson 6 (no bare `except:`) now has one more reason.

**Second, `_revisar_con_limite`**: three lines that take a permit from the semaphore and check. It is **outside** `revisar` for a measuring reason. If the semaphore were inside, `revisar`'s clock would start running before obtaining the permit, and a service that waited half a second for its turn would show up as “slow” without being so. With the permit outside, the time `revisar` measures is that of the query, and the wait in the semaphore's line is not counted. The same goes for the `asyncio.timeout` ceiling: it starts counting when the query starts, not when the task was created.

**Third, `revisar_todos`**. Its signature changed: it now receives `limite` (by default 10) and `transporte`, which you can ignore for now (it exists for 10.4: it is the door through which the tests slip in a fake server). Line by line: if `limite` is less than 1 it raises `ValueError`, because `Semaphore(0)` does not blow up: it leaves everyone waiting for a permit that never arrives, and the program hangs without saying anything. The semaphore is created. **One** `httpx.AsyncClient` is opened for all the queries, because a client keeps a pool of reusable connections and opening twenty clients would be a waste. The `TaskGroup` is opened, and the comprehension creates one task per service, **in the order of the list**. On leaving the block, all have finished. The last line, outside the `async with`s, builds the list of results by walking the tasks in that same order: that way the report respects the configuration no matter who answered first.

The user still needs to be able to choose the limit. In `cli.py`:

```python
# fig10_08/src/revisor/cli.py
import argparse
import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import encabezado, linea, reporte_a_json, resumen
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
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
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

There are two new things. `entero_positivo` is a function that `argparse` uses to convert and validate the text the user wrote after `--concurrencia`: if it is not an integer, or it is less than 1, it raises `argparse.ArgumentTypeError`, and `argparse` turns it into its usage error with exit code **2**, the same code you already used for “the usage is invalid.” Two writing details in that function. `{texto!r}` inside the f-string asks for the *representation* of the value instead of the text as it is: a text comes out with its quotation marks (`'diez'`), and so the message shows exactly what the user typed, even if it was spaces. And `raise ... from None` is the `raise ... from` of Lesson 6 with the opposite intention: instead of keeping the original error as the cause, it **hides** it, because the `ValueError` from `int` means nothing to whoever typed `--concurrencia diez` and the new message already says it all. Finally, in `main` the call became `revisar_todos(servicios, limite=argumentos.concurrencia)`.

To measure with something more interesting than four services, there is a file with twenty, all pointing at the lab server's `/espera/500` route (each answers after half a second):

```toml fig10_08/servicios-20.toml
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

With the lab server running in another terminal (`python laboratorio.py`, as in Lesson 9), measure the same run three times. `time` is a terminal command that runs what follows it and, at the end, says how long it took; the `real` line is the wall-clock time. With `| tail -n 1` only the last line of the report is kept, the summary, so as not to see twenty rows:

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 507ms

real	0m10.263s
user	0m0.154s
sys	0m0.029s

$ time python -m revisor --config servicios-20.toml --concurrencia 10 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m1.146s
user	0m0.115s
sys	0m0.024s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m0.627s
user	0m0.104s
sys	0m0.019s
```

The numbers tell the story. With `--concurrencia 1` (one permit, that is, in a line) it takes **10.3 seconds**: twenty waits of half a second. With 10 it takes **1.15**: twenty services, ten at a time, are two batches of half a second. With 20 it takes **0.63**: a single batch. Why does 10 give double that of 20 and not something in between? Because with limit 10 the first ten occupy the permits for half a second, and the other ten **cannot start** until one is released: two batches in a row. With limit 20 they all fit at once. And why 0.63 and not 0.5? Because `time`'s clock includes what is not network waiting: starting Python, importing `httpx`, opening the connections. That is between 0.1 and 0.15 seconds that do not depend on how many services there are. If your machine is slower, yours will be a little higher; the **proportion** between the three runs is what matters.

With that the first session ends. What you have is a `revisor` that queries several services at once and does not overdo it. What it lacks is resisting failures and, above all, **demonstrating** that it resists them.

### 10.3 Exception groups: one failure does not take down the report

#### 10.3.1 What happens when a task fails

So far everything went well. The `TaskGroup` has a rule for when it does not go well, and it is worth seeing with your own eyes before reading it: if **one** of the tasks ends with an exception, the group **cancels the others**. See what happens to a report with three tasks, one of which breaks:

```python
# fig10_06.py
import asyncio


async def consulta_buena(nombre: str, espera_s: float) -> None:
    try:
        await asyncio.sleep(espera_s)
        print(f"{nombre}: terminó")
    except asyncio.CancelledError:
        print(f"{nombre}: cancelada")
        raise


async def consulta_rota(nombre: str) -> None:
    await asyncio.sleep(0.1)
    raise ConnectionError(f"{nombre}: sin conexión")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as grupo:
            grupo.create_task(consulta_buena("catalogo", 0.05))
            grupo.create_task(consulta_rota("reportes"))
            grupo.create_task(consulta_buena("inventario", 0.5))
    except* ConnectionError as grupo_de_errores:
        for error in grupo_de_errores.exceptions:
            print(f"falló: {error}")
    print("fin")


asyncio.run(main())
```

```text
$ python fig10_06.py
catalogo: terminó
inventario: cancelada
falló: reportes: sin conexión
fin
```

There are three tasks inside the group. `catalogo` waits 0.05 seconds and ends well. `reportes` waits 0.1 and raises `ConnectionError` (Python's exception for a connection that could not be made; it is the cousin of the `httpx.ConnectError` that the `revisor` uses). `inventario` waits 0.5 seconds. Look at the output: `catalogo` finished, `inventario` was **cancelled** (it never got to say “terminó”; the half second it still needed was lost), and the exception from `reportes` came out through the `except*`.

In the code there are two new forms. The first is in `consulta_buena`: the `except asyncio.CancelledError:` prints “cancelada” (“cancelled”) and then does a bare `raise`. A `raise` with nothing else **re-raises the exception being handled**; it is needed because, as you saw in 10.2.3, swallowing a cancellation spoils the mechanism. The second is `except*`, which deserves its own section.

#### 10.3.2 `ExceptionGroup` and `except*`

When several tasks of a group fail at once, Python cannot raise a single exception: there would be several at the same time. That is why since 3.11 there is `ExceptionGroup` ([PEP 654](https://peps.python.org/pep-0654/)): an exception that **contains other exceptions**, in its `.exceptions` attribute, which is a tuple (the collection that does not change, from Lesson 4). A `TaskGroup` that suffered failures packs them into one on leaving the block, even if only one failed.

A normal `except` catches by the class of the exception that arrives; since what arrives is an `ExceptionGroup`, an `except ConnectionError` would not recognize it. For that `except*` (with an asterisk) was created, which **opens the group**: `except* ConnectionError as grupo_de_errores` catches the exceptions of the group that are `ConnectionError`, gathers them into a new group and leaves it in the variable. That is why the `for error in grupo_de_errores.exceptions:` walks over that tuple, and not over a single error. If the group had exceptions of other classes that no `except*` caught, they continue on their way upward. A single `try` can have several `except*`, each for its class, and each receives its own. What you **cannot** do is mix `except` and `except*` in the same `try`. The [language documentation](https://docs.python.org/3/reference/compound_stmts.html#except-star) has all the rules; for the `revisor`, what you see is enough.

Notice what the program gained and lost. It gained cleanliness: no task was left orphaned, the group waited for the cancelled ones to finish cancelling, and the error arrived in order. It lost the report: `inventario` was healthy and its result was thrown away. In a `revisor` that is unacceptable, because its reason for being is to tell you the status of **all** of them.

#### 10.3.3 A network failure is a result, not an exception

The `revisor`'s solution is already written for you, and now you can understand why it is the way it is. `revisar` **catches** network errors inside the task itself and converts them into a `Resultado` (`CAIDO`, with its detail). From the `TaskGroup`'s point of view, the task ended well: it returned a value. Nobody raises anything upward, nobody cancels anybody, and the report comes out complete with the `reportes` row saying “sin conexión.” It is the principle of the lesson: **an expected failure is data, not an incident**. A service being down is not a surprise to a `revisor`; it is part of its job.

And are all errors converted into data? No, and the difference is the most valuable thing in this section. `revisar` catches **specific `httpx` classes**: the errors the outside world can cause. It does not catch a `ZeroDivisionError`, a `KeyError` or a `TypeError`: those are errors **of the program**, and hiding them as if they were “a service down” would be lying. If a service shows up as down because your code has a bug, you will spend an afternoon looking for the problem in the network. With today's design, a programming error does what it should: it stops the report, noisily, with a report that points to the line. That noisy exit is what you see in the section “The error you will see” further down, and it is good news, not bad.

### 10.4 Tests without a network

#### 10.4.1 Why you do not test against the network

To check the previous paragraph (“a service being down does not take down the report”) you need services that are down, slow, that return 503 and that disconnect, and all four things **at once**. Tests against the real network have three problems. They are **slow**: a 5-second timeout test makes whoever runs the suite wait 5 seconds. They are **fragile**: they fail because the wifi went down, not because your code is wrong, and a red that means nothing makes people stop looking at reds. And they are **impossible to repeat**: you cannot ask a real service to go down right now. That is why the rule is that **a unit test never goes out to the network**. The network is replaced by a double: something with the same shape as the real thing, but that answers what the test tells it to.

The [Hábil blog entry on tests that catch errors](https://www.habil.mx/en/blog/tests-that-catch-errors-coverage-quality-gate/) tells why a test that can be turned red at will is worth more than ten that are always green; and the one on [online, queue and event integration styles](https://www.habil.mx/en/blog/online-or-async-integration-styles/) shows the same problem from the architecture side: separating the one who asks from the one who answers. Here you separate them with a piece of `httpx`.

#### 10.4.2 `httpx.MockTransport`: a fake server

An HTTP client has two halves: the one that builds the request and understands the response, and the **transport**, which is the one that really touches the network. `httpx` lets you change the transport, and it brings one made for tests, [`httpx.MockTransport`](https://www.python-httpx.org/advanced/transports/#mock-transports): it receives a function that, given the request, **returns the response** you want. Nothing leaves your computer.

```python
# fig10_07.py
import asyncio

import httpx


def atender(peticion: httpx.Request) -> httpx.Response:
    print(f"el servidor de mentira recibió: GET {peticion.url}")
    return httpx.Response(200, text="todo bien")


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        respuesta = await cliente.get("https://catalogo.example/estado")
        print(respuesta.status_code, respuesta.text)


asyncio.run(main())
```

```text
$ python fig10_07.py
el servidor de mentira recibió: GET https://catalogo.example/estado
200 todo bien
```

`atender` (“serve”) is the fake function: it receives an `httpx.Request` (the request, with its address in `.url`), prints what reached it and returns an `httpx.Response` with code 200 and the text “todo bien” (“all good”). `httpx.MockTransport(atender)` wraps it as a transport, and `httpx.AsyncClient(transport=transporte)` builds a client that, instead of opening a connection, calls it. The client does `get("https://catalogo.example/estado")`, an address that does not exist (`.example` is a reserved domain that never resolves), and even so it responds, because it never went to look for it. This is what `revisar_todos` offers with its `transporte` parameter: it receives the transport and passes it to `httpx.AsyncClient(transport=transporte)`. When it is `None` (the normal case), `httpx` uses the real one.

A fake transport can do more than answer 200: it can return a 503 (`httpx.Response(503)`), or **raise** a network exception as if the cable had been cut (`raise httpx.ConnectError(...)`), or even wait, if the function is `async def`. With those four things everything the `revisor` has to tolerate is simulated.

#### 10.4.3 The six tests for `revisar`

A new file, `tests/test_revision.py`. Before the code, the plan: the tests talk to a fake server that behaves according to the **host name** (the part of the address between `https://` and the first slash). `facturacion.example` answers 503; `reportes.example` raises `ConnectError`; `notificaciones.example` raises `ReadTimeout` (the `httpx` exception for “the read timeout expired”); any other answers 200.

```python
# fig10_08/tests/test_revision.py
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

Each test is a normal function (not `async`): it sets up what it needs and calls `asyncio.run(...)`, just as `main` does. That way no `pytest` plugin is needed to run coroutines, and the course sticks with what you already know. `revisar_uno` is a helper that opens a client with the fake transport and checks a single service. The first four tests go through the four outcomes of `revisar`: a quick 200 is `ARRIBA`; 503 is `CAIDO` and the detail is the code, `"503"`; a `ConnectError` is `CAIDO` with “sin conexión”; a `ReadTimeout` is `CAIDO` with “tiempo agotado.” The fifth, `test_la_mezcla_sale_completa_y_en_orden` (“the mix comes out complete and in order”), is the one that demonstrates the lesson's promise: it passes `revisar_todos` four services, one of each kind, and checks that **all four came back, in the order of the configuration, each with its detail**. If a failure took down the report, this test would turn red. And the sixth, `test_una_direccion_invalida_no_tumba_a_los_demas` (“an invalid address does not take down the others”), looks after the fourth `except` of Lesson 9: it puts together a service with the impossible address `http://999.1.1.1:8099/pagos` and a healthy one, and demands that the first come out with “dirección inválida” and the second with its `200`. Without that `except`, the `httpx.InvalidURL` would escape from its task, the `TaskGroup` would cancel the rest and the test would fail with an exception group (10.3).

(One thing `LENTO` does not have here: there is no test for that status, because simulating that more than a second passed with a fake transport is a distraction. The slowness threshold is already tested where it lives, in `clasificar`, with its seven cases from Lesson 8.)

#### 10.4.4 Seeing it red before believing it

A test you have never seen fail proves nothing: it might pass just the same with the code broken. So it is checked. In a copy of the project, the `except httpx.ConnectError` branch is deleted from `revisar`, so that a `ConnectError` falls into the general branch and says “error de red.” It is run:

```text
$ pytest -q --tb=short
.......................F.F.                                              [100%]
=================================== FAILURES ===================================
__________________________ test_sin_conexion_es_caido __________________________
tests/test_revision.py:48: in test_sin_conexion_es_caido
    assert resultado.detalle == "sin conexión"
E   AssertionError: assert 'error de red' == 'sin conexión'
E     
E     - sin conexión
E     + error de red
___________________ test_la_mezcla_sale_completa_y_en_orden ____________________
tests/test_revision.py:67: in test_la_mezcla_sale_completa_y_en_orden
    assert [r.detalle for r in resultados] == [
E   AssertionError: assert ['200', '503'...empo agotado'] == ['200', '503'...empo agotado']
E     
E     At index 2 diff: 'error de red' != 'sin conexión'
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_revision.py::test_sin_conexion_es_caido - AssertionError: a...
FAILED tests/test_revision.py::test_la_mezcla_sale_completa_y_en_orden - Asse...
2 failed, 25 passed in 0.04s
```

**Exactly two** tests turned red: the one about the connection, and the one about the mix (which includes that case). The line that says `2 failed, 25 passed` gives you the report that matters: it is not a green by chance. Repair the code and run again:

```text
$ pytest -q
...........................                                              [100%]
27 passed in 0.03s
```

`27 passed`: the 21 from the previous lesson plus today's six. That number is read from the report, not from the exit code, because a code 0 does not tell you how many tests ran: the same comes out with 27 as with 2 if you mistakenly filtered out the rest. (Lesson 11 returns to this with a concrete case.)

There is a limit worth stating plainly. The timeout test makes the fake server **raise** a `ReadTimeout`, that is, it tests the `httpx.TimeoutException` branch. It does not test `asyncio.timeout`'s **ceiling**, which exists precisely for the case where `httpx` finds out nothing. That test is needed, and it is Exercise 2: you write it, and you will check that if the `asyncio.timeout` is removed, it turns red.

#### 10.4.5 `monkeypatch` and the signature you must not change without warning

`test_cli.py` already existed, with two tests, and had a detail that stands out today. Those tests call `main`, and `main` calls `revisar_todos`, which goes out to the network. So that it does not, the course used `monkeypatch` (Lesson 8): it changes, during a test, one name for another, and when the test ends it restores it. Here it changes `revisor.cli.revisar_todos` for a fake function that returns what the test needs.

```python
# fig10_08/tests/test_cli.py
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

Note **where** the name is changed: `"revisor.cli.revisar_todos"`, not `"revisor.revision.revisar_todos"`. `cli.py` did `from revisor.revision import revisar_todos`, so `cli` has **its own copy of the name**; if you changed the original in `revision`, `cli` would keep using its own. The rule of `monkeypatch`: the name is changed in the place where it **is used**, not in the place where it was defined.

And now the important thing about this version: the two fake functions, `todos_caidos` (“all down”) and `todos_arriba` (“all up”) (each defined inside its test), **accept `limite`**. Today `main` calls `revisar_todos(servicios, limite=argumentos.concurrencia)`, and a fake that does not accept that argument is not a double of the real function: it is another function, and the test breaks. If in Lesson 9 your fake was `async def todos_caidos(servicios)`, now you have to add the parameter to it. You see it in “The error you will see.” It is a more general lesson: **a double must have the same signature as what it replaces**, and when you change the real function's signature, tests with doubles are the first thing to break. That is not a nuisance; it is the test doing its job, warning you that there are others who depended on that signature.

#### 10.4.6 The complete project

The files that did not change in this lesson are here so that the `fig10_08/` folder is complete and you can run it. They are the same ones you brought from Lesson 9:

<details>
<summary>The files that do not change in this lesson</summary>


```toml fig10_08/servicios.toml
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
# fig10_08/laboratorio.py
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

```python
# fig10_08/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig10_08/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig10_08/src/revisor/modelo.py
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
# fig10_08/src/revisor/formato.py
import json

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

```python
# fig10_08/src/revisor/configuracion.py
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
# fig10_08/tests/test_modelo.py
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
# fig10_08/tests/test_formato.py
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
# fig10_08/tests/test_configuracion.py
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

</details>

With the lab server running, the project's snapshot produces the same report as always, but this time the four services are queried at once, so the total is that of the slowest (`inventario`, 2.3 seconds) and not the sum:

```text
$ cd fig10_08
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
```

The times in the TIEMPO column will vary a little on your machine; the ESTADO and the DETALLE will not, because the lab server is made to come out the same every time. And the exit code, as in Lesson 7, is 1: there is a `LENTO` and a `CAIDO`.

**For comparison.** The same problem — launch, wait for all, limit, not lose the report because of a failure — is solved in the [Go course](https://www.habil.mx/en/courses/go/) with `sync.WaitGroup` and in the [TypeScript course](https://www.habil.mx/en/courses/typescript/) with `Promise.all` and `Promise.allSettled`. The idea is the same; what changes is where the waiting lives. In Go each task is a *goroutine*, a lightweight thread that Go's own scheduler (not the operating system) distributes among the processor's threads; in TypeScript and in Python it is a cooperative task in a single thread. Comparing the three solutions teaches more than reading just one.

## The error you will see

### `ExceptionGroup: unhandled errors in a TaskGroup`

It is the one you will get the first time you have a programming error inside a task. Figure 9 provokes it: a function that averages a list and is passed an **empty** one, so that it divides by zero.

```python
# fig10_09.py
import asyncio


async def promedio(tiempos_ms: list[int]) -> float:
    return sum(tiempos_ms) / len(tiempos_ms)


async def main() -> None:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))


asyncio.run(main())
```

Two tasks inside the group: one averages two numbers, the other an empty list. This is what Python says (paths shortened to their name, as throughout the course; on your machine they come complete and the `asyncio/` lines may differ depending on the Python version):

```text
$ python fig10_09.py
  + Exception Group Traceback (most recent call last):
  |   File "fig10_09.py", line 15, in <module>
  |     asyncio.run(main())
  |     ~~~~~~~~~~~^^^^^^^^
  |   File "asyncio/runners.py", line 205, in run
  |     return runner.run(main)
  |            ~~~~~~~~~~^^^^^^
  |   File "asyncio/runners.py", line 128, in run
  |     return self._loop.run_until_complete(task)
  |            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  |   File "asyncio/base_events.py", line 720, in run_until_complete
  |     return future.result()
  |            ~~~~~~~~~~~~~^^
  |   File "fig10_09.py", line 10, in main
  |     async with asyncio.TaskGroup() as grupo:
  |                ~~~~~~~~~~~~~~~~~^^
  |   File "asyncio/taskgroups.py", line 72, in __aexit__
  |     return await self._aexit(et, exc)
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "asyncio/taskgroups.py", line 174, in _aexit
  |     raise BaseExceptionGroup(
  |     ...<2 lines>...
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "fig10_09.py", line 6, in promedio
    |     return sum(tiempos_ms) / len(tiempos_ms)
    |            ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~
    | ZeroDivisionError: division by zero
    +------------------------------------
```

First: this *traceback* **is not read like those of the previous lessons**, from the last line up. The last line above, `+------------------------------------`, is decoration; the real cause is **inside the box** marked with `|`, at the bottom. Read it like this:

1. The first line, `+ Exception Group Traceback`, warns you: what follows is a group.
2. The lines with `|` go down the path the execution traveled: your `asyncio.run(main())`, the internal steps of `asyncio` and, importantly, your `main` on line 10, at the `async with asyncio.TaskGroup()`. That is where the group, on leaving, packed the error.
3. `ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` is the group's label. The number in parentheses tells you how many it contains.
4. And **inside the box** (`+-+---------------- 1 ----------------`) is sub-exception number 1 with its own *traceback*: `promedio`, line 6, `ZeroDivisionError: division by zero`. **That is the cause**, and the one you have to fix. The line of your file is on the row that says `fig10_09.py", line 6, in promedio`.

Note also what happened to the **other** task (`promedio([142, 87])`): there was nothing to cancel. Since it has no `await`, it ran whole, without yielding its turn, and ended with its `114.5` before the second one started. If it had been waiting for something, like `inventario` in `fig10_06.py`, the `TaskGroup` would have cancelled it even though it was healthy: that is the group doing its job.

What to do: fix the cause (check that the list is not empty), do not hide the error. Resist the temptation to put a wide `except*` to silence it: a programming error must be seen.

### `TypeError: ... got an unexpected keyword argument 'limite'`

Today's second error is the one from 10.4.5. If your fake in `test_cli.py` is from Lesson 9 and does not accept `limite`:

```text
$ pytest -q --tb=short -x tests/test_cli.py
F
=================================== FAILURES ===================================
_____________________ test_con_servicios_caidos_sale_con_1 _____________________
tests/test_cli.py:29: in test_con_servicios_caidos_sale_con_1
    assert main(["--config", str(archivo)]) == 1
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/revisor/cli.py:64: in main
    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: test_con_servicios_caidos_sale_con_1.<locals>.todos_caidos() got an unexpected keyword argument 'limite'
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_con_servicios_caidos_sale_con_1 - TypeError: t...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 0.03s
```

Read it from the bottom up, as always: `TypeError`, “`todos_caidos()` got an unexpected keyword argument, `limite`.” (The `test_con_servicios_caidos_sale_con_1.<locals>.` that precedes the name means that function is defined **inside** the test.) The line above (`src/revisor/cli.py:64`) tells you who sent it: `main`. And the one above that, that the test called `main`. The fix is not in `cli.py`: it is in the fake, which must accept the same as the real function.

## What gets done wrong

**Waiting with `time.sleep` inside a coroutine.** It blocks the thread and undoes the entire concurrency, without giving an error (10.1.4). Cost: a program that looks concurrent and takes the same as in a line. It is detected with `asyncio`'s debug mode and with `ruff`, as long as you add the `ASYNC` collection to your `select` (the `revisor`'s does not include it; 10.1.4).

**Creating tasks with `asyncio.create_task` and forgetting to keep them.** Python only keeps a **weak** reference to loose tasks, and a task nobody references can be collected by the garbage collector halfway through running. The [documentation](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) warns about it. With `TaskGroup` it does not happen, because the group keeps them. Cost: tasks that vanish without an error.

**Not limiting concurrency.** A `TaskGroup` without a semaphore with a thousand services opens a thousand connections at once. Cost: you run into the operating system's limit, or you saturate the service you are checking, and the report fails for reasons that are not the ones it measures.

**Catching `Exception` (or `BaseException`) inside the task so that it “never fails.”** It eats programming errors and, with `BaseException`, even the cancellation. Cost: a report that lies (“service down”) when the one that failed is your code.

**Swallowing `CancelledError`.** An `except asyncio.CancelledError:` that does not re-raise the exception leaves the `TaskGroup` and `asyncio.timeout` unable to cancel. Cost: programs that do not end or that do not respect the timeout. If you catch it to clean something up, do a `raise` at the end.

**Testing against the real network.** Slow, fragile, impossible to repeat (10.4.1). Cost: reds that nobody believes.

**A fake with another signature.** The double that does not accept what the real function accepts is another function. Cost: tests that break when the signature changes, or, worse, that keep passing without testing anything because nobody called them with the new arguments.

**Measuring with a single run.** A single number says nothing: the start-up of Python, the warming up of the connections and whatever your computer is doing in that second get mixed together. Measure several times and compare the **proportion**.

## Exercises

### Exercise 1 — Measure a limit you did not try

With `servicios-20.toml` and the lab server running, measure with `--concurrencia 5` and with `--concurrencia 4`. **Before running**, predict the times with the reasoning of the batches (how many half-second batches are needed with that limit). Note prediction and measurement in your logbook and explain the difference, if there is one.

### Exercise 2 — The ceiling test

Write a test for the `asyncio.timeout` ceiling: a service with `timeout_ms = 100` whose fake server **waits ten seconds** before answering. The test must pass in a fraction of a second. Hint: the function that serves can be `async def` and use `await asyncio.sleep(10)`. Then **verify it in red**: remove the `asyncio.timeout` from `revisar` (leave an `if True:` in its place), run the test and note how long it takes to fail and why.

### Exercise 3 — A timeout shorter than the response

Copy `servicios.toml` and add `timeout_ms = 1500` to the `inventario` service (which on the lab server answers after 2.3 seconds). Predict `inventario`'s row, the summary and how long the run will take, and compare it with what comes out. What changed in `inventario`'s `ESTADO`, and why?

### Exercise 4 — Provoke three errors and read them

Provoke, one by one: (a) in `fig10_09.py`, change the empty list to `[100]` and run (what disappeared?); then put it back and pass the task's `ZeroDivisionError` through an `except*` that catches it and prints a message; (b) run `python -m revisor --concurrencia 0` and note the code with `echo $?`; (c) remove `limite` from one of the fakes in `test_cli.py` and run `pytest`. For each, write in one sentence what the message means.

## Solutions

### Solution 1

With limit 5 and twenty services, four batches of half a second are needed: 2.0 seconds plus the start-up. With limit 4, five batches are needed: 2.5 plus the start-up. A reference run gave 2.15 and 2.67 seconds: the start-up (the 0.15 to 0.2 s that is not waiting) explains the difference from 2.0 and 2.5. The general rule: the time ≈ (the number of services divided by the limit, rounded up) times each one's wait, plus the start-up.

### Solution 2

The test is added to `tests/test_revision.py` (or to a file of its own):

```python
import asyncio

import httpx

from revisor.modelo import Estado, Servicio
from revisor.revision import revisar


async def colgado(peticion: httpx.Request) -> httpx.Response:
    await asyncio.sleep(10)
    return httpx.Response(200)


async def revisar_colgado() -> tuple[Estado, str]:
    servicio = Servicio("colgado", "https://colgado.example", 100)
    async with httpx.AsyncClient(transport=httpx.MockTransport(colgado)) as cliente:
        resultado = await revisar(cliente, servicio)
    return resultado.estado, resultado.detalle


def test_el_techo_corta_lo_que_httpx_no_ve() -> None:
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
```

The fake server is `async def` and waits ten seconds; the fake transport applies no `httpx` timeout (there is no network), so the only one that can cut is the `asyncio.timeout` ceiling. With the complete code, the test passes in a fraction of a second:

```text
$ pytest -q tests/test_techo.py
.                                                                        [100%]
1 passed in 0.12s
```

And with the `asyncio.timeout` removed (the `if True:`), the test **fails**, and takes ten seconds to fail, because nobody cuts the wait; the report shows that `revisar` delivered `LENTO` with `'200'` after waiting ten seconds:

```text
$ pytest -q --tb=short tests/test_techo.py
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_el_techo_corta_lo_que_httpx_no_ve ____________________
tests/test_techo.py:22: in test_el_techo_corta_lo_que_httpx_no_ve
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
E   AssertionError: assert (<Estado.LENT...ENTO'>, '200') == (<Estado.CAID...empo agotado')
E     
E     At index 0 diff: <Estado.LENTO: 'LENTO'> != <Estado.CAIDO: 'CAIDO'>
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_techo.py::test_el_techo_corta_lo_que_httpx_no_ve - Assertio...
1 failed in 10.04s
```

That shows the test depends on the fix it claims to test. The six tests in `test_revision.py` would not have noticed that regression.

### Solution 3

`inventario` goes from `LENTO` to `CAIDO` with detail “tiempo agotado”: its response took 2.3 seconds and the ceiling is 1.5, so it is cut before. The summary now counts `2 caídos`, and the run takes about 1.6 seconds (the 1.5 ceiling plus the start-up) instead of 2.4. A real run:

```text
$ time python -m revisor --config servicios-corto.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  CAIDO          —  tiempo agotado
pagos       ARRIBA      95ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 0 lentos · 2 caídos · promedio 126ms

real	0m1.634s
user	0m0.110s
sys	0m0.019s
```

Two observations. The average changes (126 ms in this run; it varies a little in each), because `inventario` no longer contributes a time: a service that did not answer does not enter the average. And the run is shorter because the slowest is no longer `inventario` but its ceiling.

### Solution 4

(a) With `[100]` instead of `[]` there is no longer a division by zero, the program ends with no output and no error: both tasks completed. With the `except*`:

```python
try:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))
except* ZeroDivisionError:
    print("una lista de tiempos venía vacía")
```

it catches the error and the program prints the message instead of the *traceback*. (b) `revisor: error: argument --concurrencia: debe ser al menos 1` comes out (“must be at least 1”) and the code is 2: it is a usage error, and `argparse` detects it before anything runs. (c) `TypeError: ... todos_caidos() got an unexpected keyword argument 'limite'`: the fake does not accept what `main` sends it.

## How I know I got it

- [ ] `fig10_02.py` prints “a la vez: 0.5 s” and `fig10_01.py` prints “en serie: 1.1 s,” and you can say why the first is the slowest one's time and the second the sum.
- [ ] `fig10_03.py` prints the responses in the order in which the tasks were created, not in the order of speed, and you can explain what `time.sleep` does that `asyncio.sleep` does not.
- [ ] `fig10_05.py` shows the batches two by two and the total of 1.5 s.
- [ ] In the `fig10_08/` folder, `pytest -q` ends with `27 passed` and not another number, and it does so with the lab server off (that is the beauty of testing without a network).
- [ ] `ruff check`, `ruff format --check` and `mypy` report nothing in that folder.
- [ ] With `servicios-20.toml`, `--concurrencia 1` takes about 10 seconds, `--concurrencia 10` about 1.1 and `--concurrencia 20` about 0.6, and you can explain why 10 gives double that of 20.
- [ ] `python -m revisor --concurrencia 0` ends with code 2 and a usage message.
- [ ] You deliberately broke the `ConnectError` branch of `revisar` and saw exactly two tests turn red; you fixed it and the 27 came back.
- [ ] You can explain in your own words the difference between `httpx`'s timeout and `asyncio.timeout`, why `revisar` catches `httpx.HTTPError` and **not** `Exception`, and why the fake in `test_cli.py` has to accept `limite`.

## Summary

Answer without looking at the lesson:

1. What is the difference between a coroutine and a task? What does `create_task` do and what does the exit from an `async with asyncio.TaskGroup()` block do?
2. At what exact moment can the event loop pass from one task to another? What happens with a `time.sleep` inside a coroutine?
3. If four services answer in 0.3, 0.5, 0.1 and 0.2 seconds, how long does the run take in a line and how long with a `TaskGroup`? And with a `Semaphore(2)`?
4. What does `httpx.Timeout` measure and what does `asyncio.timeout()` measure? Which of the two cuts off a server that sends a byte every four seconds?
5. Why is the semaphore taken **outside** `revisar` and not inside?
6. When a task of a `TaskGroup` raises an exception, what happens to the others? What does the code outside the block receive?
7. What does `except*` do that `except` does not? What is the difference between `revisar` converting a `ConnectError` into a `Resultado` and catching a `ZeroDivisionError`?
8. Where is the name changed with `monkeypatch` if `cli.py` did `from revisor.revision import revisar_todos`? Why does the fake have to accept `limite`?

## Further reading

- [`asyncio` documentation: coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html) — `TaskGroup`, `create_task`, `timeout()` and `sleep()` with all their rules, including cancellation. It is the source of this lesson. Accessed on October 7, 2026.
- [PEP 654, “Exception Groups and except\*”](https://peps.python.org/pep-0654/) — why exception groups exist, with the cases that motivated them. More technical, but the motivation section reads well. Accessed on October 7, 2026.
- [`httpx` documentation: transports (`MockTransport`)](https://www.python-httpx.org/advanced/transports/) and [timeouts](https://www.python-httpx.org/advanced/timeouts/) — the two pieces of `httpx` you used today. Accessed on October 7, 2026.
- [`pytest` documentation: `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — all the ways of changing a name during a test and when to use each. Accessed on October 7, 2026.
