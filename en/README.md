# Python course — from zero to a program that checks many services at once

**By Dorian Chávez, founder of Hábil and integration architect.**

**Who it is for:** anyone who has never programmed, or who has copied scripts that work without knowing why. Nothing is assumed: not that you have Python installed, nor that you know what a virtual environment is. Each concept is explained when it appears, and it is explained why it exists, not only how it is written.

**What you will know by the end:** how to write a complete program, with tests and several tasks at once, understand what you wrote, and be able to explain it to someone else. And you will keep the judgment to read Python's documentation on your own, which is the real test.

**Where it goes next:** the same problem, the `revisor` (the checker), is solved in Hábil's [Go](https://www.habil.mx/en/courses/go/), [Rust](https://www.habil.mx/en/courses/rust/), and [TypeScript](https://www.habil.mx/en/courses/typescript/) courses. When you finish this one, comparing your solution with theirs teaches more than starting from scratch.

**What you need before starting:** a computer with Linux Mint and knowing how to open a terminal. Nothing more. [Lesson 1](01-instalacion.md) gets everything ready from scratch.

## The project you are going to build

The **`revisor`**: a command-line program that receives a list of services, queries **all of them at once**, and delivers a report as a table or as JSON.

    $ revisor --config servicios.toml --formato tabla
    SERVICIO    ESTADO    TIEMPO  DETALLE
    catalogo    ARRIBA     160ms  200
    inventario  LENTO       2.3s  200
    pagos       ARRIBA      90ms  200
    reportes    CAIDO          —  sin conexión

    4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms

It starts in Lesson 2 with a header and a single service, and grows in each lesson until it is a package that installs like any other command. It looks small and it is not: to write it well you need functions, collections, errors, files, tests, types, HTTP, and concurrent tasks.

## The twelve lessons

| Lesson | | What you build | What you learn |
|---|---|---|---|
| 0 | [What Python is and what it is NOT](00-que-es-python.md) | nothing yet (reading) | interpreter and *bytecode*; dynamic but strong typing; annotations are not enforced; the GIL; virtual environments; versions |
| 1 | [Installing Python on your Linux Mint](01-instalacion.md) | the environment and your first script | the system's `python3`; `externally-managed-environment`; `venv`; `pip`; the REPL; the first *traceback* |
| 2 | [Values, text, and decisions](02-valores-texto-decisiones.md) | the `revisor`'s header and the classification of one service | three concepts: numbers, strings, booleans, and `None`; f-strings; `if`/`elif`/`else` and indentation |
| 3 | [Loops, functions, and modules](03-bucles-funciones-modulos.md) | the `revisar()` function and the traversal of the list | `for`, `while`; `==` versus `is`; `def`; scope; the mutable default argument; `import`; `__main__` |
| 4 | [Collections](04-colecciones.md) | the `revisor` without parallel lists: each service's data, together | `list`, `dict`, `tuple`, `set`; comprehensions; copy versus reference; `KeyError` and `IndexError` |
| 5 | [The data model](05-modelo-de-datos.md) | the `Servicio` / `Estado` model and the report with its summary | `dataclass`; `Enum`; `match` and `case` |
| 6 | [Errors, files, and outside data](06-errores-archivos-datos.md) | reading the configuration | `try`/`except`; reading a *traceback*; `with`; `pathlib`; UTF-8; `json` and `tomllib`; validating; no `eval` or `pickle` |
| 7 | [A package with a command line](07-paquete-linea-de-comandos.md) | the `revisor` as a package | `pyproject.toml`; `python -m revisor`; `argparse`; exit codes; editable install with `pip`; `uv` as an optional box |
| 8 | [Tests, types, and quality](08-pruebas-tipos-calidad.md) | the `revisor` with tests | `pytest` and table of cases; `tmp_path`; `monkeypatch`; gradual typing with `mypy`; `ruff` |
| 9 | [HTTP and asyncio](09-http-y-asyncio.md) | the `revisor` that really queries | `urllib` and `httpx`; timeouts; `async` and `await`; `asyncio.run` |
| 10 | [Concurrency with limits and tests without a network](10-concurrencia-pruebas-sin-red.md) | the concurrent, tested `revisor` | `TaskGroup`; `timeout`; `Semaphore`; exception groups; simulated network in tests |
| 11 | [The finished program](11-el-programa-terminado.md) | the complete, installable `revisor` | table and JSON report; `logging`; security; building and installing with `pipx` |

At the end of each lesson there are exercises with their solutions and a “Further reading” section; the sources of what is claimed are linked in the text, where they are used. And the [logbook](https://github.com/HabilMX/curso-python/blob/main/en/bitacora.md) is yours: write down there what was hard for you.

**To keep reading:** on Hábil's blog, [tests that catch errors](https://www.habil.mx/en/blog/tests-that-catch-errors-coverage-quality-gate/) and [API security](https://www.habil.mx/en/blog/api-security-cto-identity-gateway-tokens/). And in the courses: if you already know how to program and want modern Java, the [Java course](https://github.com/HabilMX/curso-java).

## Three criteria that run through the whole course

**The error is content, not an accident.** Each lesson deliberately provokes the error you are going to see, shows the real *traceback*, and teaches you to read it, from the last line upward. Knowing how to read an error is half of knowing how to program.

**The environment is real.** You work on Linux Mint with the Python the system ships and its rules, not in a notebook in the browser. All the code runs on Python 3.14 and also on 3.12, which is Mint's.

**Tests and security are not lessons, they are habits.** Data from outside is validated in Lesson 6, tests arrive in Lesson 8 and a test does not count until you have seen it fail, and the address someone writes in a file is treated for what it is in lessons 9 and 11.

## How you know you are done

The course does not end when you have read Lesson 11, but when your `revisor` meets these seven things:

1. **`pytest` ends green and the report says how many tests ran.** Count them from the report, not from the exit code: a green with zero tests looks the same as a real green.
2. **`ruff check` and `ruff format --check` report nothing, and neither does `mypy`.**
3. **It checks 20 services at once in a time close to that of the slowest one**, not to the sum of all of them. You measure it yourself, with the clock, in series and in parallel.
4. **A service that is down, slow, or answers garbage does not bring down the report:** it appears in its row with its error, and the rest comes out complete.
5. **No request can wait forever:** all of them have a timeout.
6. **It runs the same on Python 3.14 and on your Mint's 3.12.**
7. **It installs with `pipx install` and `revisor --help` works from another folder.** It exits with code 0 if everything is up and 1 if not.
