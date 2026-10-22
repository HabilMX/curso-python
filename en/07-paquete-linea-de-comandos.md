# Lesson 7 — A package with a command line

**Time:** 90 min

**What you build:** the `revisor` as a real package: a folder with structure, a `pyproject.toml` file that describes it, a command with options (`--config`, `--formato`, `--version`) and an exit code that other programs can read

**What you learn:** the structure of a package with the `src/` layout (`__init__.py`, `__main__.py`, absolute imports); `python -m revisor`; `pyproject.toml` (`[build-system]`, `[project]`, `[project.scripts]`); `argparse`; exit codes; standard output versus standard error; and the editable install with `pip install -e .`

**Where you come from.** You bring the project from [Lesson 6](06-errores-archivos-datos.md): a `revisor` that no longer has the services written in the code but reads them from `servicios.toml`, validates them, and complains in Spanish when the file is no good. It is six files in a single folder (`revisor.py`, `modelo.py`, `revision.py`, `formato.py`, `configuracion.py` and the support script `ver_json.py`) plus the `servicios.toml`. It works, with three limitations that show today. First: **it only works if you are standing in that folder** and type `python revisor.py`; the modules find one another because they are stuck together, and the name of the configuration file is written in a constant of the program. Second: **to see the report in JSON you have to run another script**, because the program has no way for you to tell it what you want. Third: **the program does not tell anyone if it found problems**: it ends just as well when everything is up as when half is down, and a script, a task scheduler or a continuous integration system cannot tell the difference. You work in your `~/curso-python/revisor/` folder, with the virtual environment from [Lesson 1](01-instalacion.md) activated.

**What this lesson does not do.** It queries no network (the data is still the simulated data of Lesson 5; the network arrives in [Lesson 9](09-http-y-asyncio.md)) and it writes no tests (that is [Lesson 8](08-pruebas-tipos-calidad.md)). What gets solved today is **how a set of files becomes a program that is installed, run with one command and communicates with the rest of the system**.

**About the runs.** All the outputs were obtained with Python 3.14.8 and repeated with Python 3.12.12, from the same 3.12 line that Linux Mint 22 ships. (Mint 22's is 3.12.3, the one published by Ubuntu 24.04, its base: the [page of the `python3.12` package for Ubuntu 24.04 on Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12) shows it.) They are identical with a single exception, pointed out where it occurs: the text of an `argparse` error. The paths you will see in the messages start with `/home/tu_usuario/curso-python/`; yours will start with your own folder. The complete project is in [`programas/07-paquete-linea-de-comandos/fig07_01/`](https://github.com/HabilMX/curso-python/tree/main/programas/07-paquete-linea-de-comandos/fig07_01), in the course repository; the two loose figures (`fig07_02.py` and `fig07_03.py`) are run from the lesson's folder.

## By the end you will be able to

- Explain the difference between a module and a package, and why the code lives in `src/revisor/` and not next to the `pyproject.toml`.
- Run a package with `python -m revisor` and explain what `__main__.py` does.
- Read and write a `pyproject.toml` with its three tables: `[build-system]`, `[project]` and `[project.scripts]`.
- Define command-line options with `argparse`: one with a default value, one with closed choices and a `--version`.
- Make a program end with an exit code that says what happened (0, 1 or 2), and read it in the terminal with `echo $?`.
- Send error messages to standard error and the report to standard output, and check the difference by redirecting one of the two.
- Install the package in editable mode with `pip install -e .` and explain why a change in the code is noticed without reinstalling, but a change in `pyproject.toml` is not.

## The why before the how

Think about how you would use the `revisor` in real life. Someone in operations runs it every morning from a task scheduler, to find out whether any service woke up down. That task scheduler does not look at the table that is printed: it is a program, and it does not know how to read a table. The only thing it can ask another program when it finishes is one thing: **“did you end well or badly?”**. On Linux, that answer is a number, the *exit code*, and the convention is that 0 means “all well” and any other number means “something happened.” If the `revisor` does not know how to answer that question, the automation is blind. And if in addition the person wants the report in JSON to hand to another system, they need to be able to ask for it with an option, not by editing a file.

A program that runs this way, with options, with an exit code and from any folder, is a **command-line program**. To be one, structure is needed: you cannot do it with six loose files. Python has a standard way to put it together, which consists of three pieces: a **package** (a folder that Python recognizes as an importable unit), a **`pyproject.toml`** file that describes the project for the tools, and an **install command** that leaves everything available in your environment. Those are the three sections of the lesson, plus the one that closes it: how a program communicates with whoever called it, with exit codes and with two distinct text channels.

The lesson is mechanical, and that is a fair warning: there are many file names and many rules that are learned by doing them, not by reading them. The best way to follow it is to have the terminal open in `~/curso-python/revisor/` and run each step as you go. At the end, when you run `python -m revisor --formato json` you will see the report in JSON on the screen, and when you ask the terminal how the program ended with `echo $?`, you will see a `1`, because among the services there is one slow and one down. There are many things hidden in that sentence (an option, a format, a number that comes out at the end), and the lesson untangles them one by one.

## The concepts

### 7.1 A package with the `src/` layout

#### 7.1.1 Module, package and how they are found

You already know what a **module** is: a `.py` file whose content another file can import (Lesson 3). So far your `revisor` has five, and they are imported with statements like `from modelo import Servicio`. That works for a very concrete reason that had never been named: when you run `python revisor.py`, Python looks for the modules you import **in the folder where that file is**, and also in the folders of the standard library and in those of the virtual environment where `pip` installs things (a folder called `site-packages`). That list of places is consulted in order, and it is what decides whether an `import` finds what it is looking for or fails with `ModuleNotFoundError`. As long as all your files are together, everything is found. As soon as something is moved or run from somewhere else, it starts to fail.

A **package** is a folder of modules that Python treats as a unit with a name. If there is a `revisor/` folder with an `__init__.py` file inside and other modules, from anywhere you can write `from revisor.modelo import Servicio`, which reads “from the package `revisor`, the module `modelo`, import `Servicio`.” The dot separates the levels. This kind of import, which always starts with the name of the package, is called an **absolute import**, and it is the only one this course uses: it is the clearest to read, because anyone who sees the line knows where the name comes from without having to guess which folder the file is in. The [tutorial section on packages](https://docs.python.org/3/tutorial/modules.html#packages) explains the mechanism in more detail.

#### 7.1.2 Why `src/`

What remains to be decided is **where** the package's folder goes. The most obvious way is next to the `pyproject.toml`, in the root of the project. But there is a better way, which is the one used by Python's official packaging guide: putting it in a subfolder called `src/`. This is the layout you will have when you finish the lesson:

```text
revisor/                      ← la carpeta del proyecto (~/curso-python/revisor/)
  pyproject.toml              ← describe el proyecto
  servicios.toml              ← los datos, como en la lección 5
  src/
    revisor/                  ← el paquete
      __init__.py
      __main__.py
      cli.py
      modelo.py
      revision.py
      formato.py
      configuracion.py
```

The name `revisor` appears twice, and it is not carelessness: the outer one is the folder of the **project** (what you download, what holds the configuration files, the tests that will come in Lesson 8), and the inner one is the **package** (what Python imports). The advantage of `src/` is that it **forces you to install the package before using it**. If the package were in the root, `python -m revisor` from that folder would find it without installing it, because the current folder is always in the list of places where Python looks. And that hides errors: you could have a package that works in your folder but, once installed, is missing files, and you would not find out until another person used it. With `src/`, the package's folder is not where Python looks by default, so no copy sneaks in just because it sits in the folder where you work: to import the package, you first have to install it.

What `src/` does not guarantee is that what you run is the package exactly as it would be installed on another computer: that depends on **how** you install it. The installation you will use for developing, the **editable** one from 7.4.3, does not copy the package anywhere: it adds the **entire** `src/` folder to the list of places where Python looks. What runs then is your folder, and any file that sits in `src/` can be imported, even if it is not part of the package. This was measured with this same project, with Python 3.14.8 and 3.12.12 and `hatchling` 1.32.4, by adding a file `src/suelto.py`, outside `src/revisor/`. With the editable installation, `import suelto` works from any folder; with the normal installation (`pip install .`, without `-e`), the same line ends in `ModuleNotFoundError: No module named 'suelto'`, because the built package only carries what is in `src/revisor/`. The [`pip` documentation](https://pip.pypa.io/en/stable/topics/local-project-installs/) says it in so many words: an editable install does not copy any files; instead, “the files in the development directory are added to Python’s import path”; and it warns that it can behave differently from the normal one, which is the one whoever receives your program will see. The [`hatchling` documentation](https://hatch.pypa.io/latest/config/build/#dev-mode) explains that, in an editable install, it decides which **entire** directories to add to the search path. That is why the [packaging guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) splits the roles this way: the editable installation is used for development, and the normal one for testing. This course develops with the editable one, because it is the convenient one; the normal one arrives in Lesson 11, when the `revisor` is packaged into a file and installed with `pipx`. And the tests of Lesson 8 do not change this account: they run against whatever is installed, and with the editable installation that is your `src/` folder, whatever the mode in which `pytest` imports the test files. This was measured too: with the editable installation, a test that imports `suelto` passes with `pytest`'s default mode and with the `importlib` mode, the one its [good practices guide](https://docs.pytest.org/en/stable/explanation/goodpractices.html#which-import-mode) recommends for new projects; with the normal installation, it fails in both.

That same packaging guide discusses the two ways and their trade-offs; this course adopts the `src/` one without reservations.

#### 7.1.3 `__init__.py`, `__main__.py` and `python -m`

The package carries two files that are not part of your program but part of the mechanism. The first is `__init__.py`. Its mere presence tells Python “this folder is a package.” It can be empty; here it carries a sentence in triple quotation marks that describes the package, what is called a documentation string:

```python
# fig07_01/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

The second is `__main__.py`, which is what runs when someone types `python -m revisor`. The `-m` option (for *module*) tells Python “do not run a file; run this package as a program.” For a package, that means running its `__main__.py`. The whole file is this:

```python
# fig07_01/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

The first line imports the `main` function from the `cli` module (which you will see in 7.3). The second does something that looks like a formality but is the center of the lesson: `raise SystemExit(main())`. You already know what `raise` is (Lesson 6): it raises an exception. `SystemExit` is a special exception that Python already ships, and that **nobody catches on purpose**: when it goes all the way up, instead of printing an error report, Python ends the program, and the value you build it with becomes the **exit code**. So `main()` runs, **returns a number**, and that number becomes the code with which the program ends. We will see it in detail in 7.4; for now it is enough to know that the `-m` looks for this piece. The [documentation of `__main__`](https://docs.python.org/3/library/__main__.html#main-py-in-python-packages) and that of the [`-m` option](https://docs.python.org/3/using/cmdline.html#cmdoption-m) tell it in detail.

#### 7.1.4 Moving the files

The four modules you already had (`modelo.py`, `revision.py`, `formato.py`, `configuracion.py`) move into the package **without changing a single function**: the signatures are the same as in Lesson 6. The only thing that changes is their imports, which stop being `from modelo import ...` and become `from revisor.modelo import ...`. The flat `revisor.py` becomes `cli.py` and is rewritten in 7.3. And the `ver_json.py` script disappears, because `--formato json` replaces it. From the project folder, with the environment activated, these are the steps. They use three terminal commands you had not seen, and it is worth knowing what each does before typing it:

- **`mkdir -p src/revisor`** creates the `src` folder and, inside it, `revisor`, in one go. Without `-p`, `mkdir` would refuse to create `revisor` because `src` does not exist yet; with `-p` (*parents*) it also creates the intermediate folders that are missing, and does not complain if they already existed.
- **`mv origen destino`** (*move*) **moves** files, or renames them. `mv modelo.py revision.py formato.py configuracion.py src/revisor/` moves the four files to that folder (the final slash says that the destination is a folder). `mv revisor.py src/revisor/cli.py` moves and renames at once. If a file with that name already exists at the destination, `mv` replaces it without asking.
- **`rm archivo`** (*remove*) **deletes** a file, and does not send it to the trash: it cannot be recovered. Here it deletes `ver_json.py`, which is no longer needed, and at the end the `.bak` copies that `sed` leaves. The `*` in `src/revisor/*.bak` means “all the files of that folder that end in `.bak`”; before an `rm` with `*`, an `ls` with the same pattern shows you exactly what is going to be deleted.

These are the steps:

```bash
mkdir -p src/revisor
mv modelo.py revision.py formato.py configuracion.py src/revisor/
mv revisor.py src/revisor/cli.py
rm ver_json.py
sed -i.bak -E 's/^from (modelo|formato|configuracion|revision) import/from revisor.\1 import/' src/revisor/*.py
rm src/revisor/*.bak
```

The `sed` command is a text editor without a window: it looks in each file for the lines that start with `from modelo import` (or `formato`, `configuracion`, `revision`) and puts `revisor.` in front of them. The `-i.bak` parameters ask it to save a backup copy of each file with the ending `.bak`, which is deleted right afterwards. If you prefer not to use it, edit by hand the lines that say `from modelo import`, and verify with this what must remain in each file:

| File | Imports when finished |
|---|---|
| `revision.py` | `from revisor.modelo import Resultado, Servicio, clasificar` |
| `formato.py` | `import json` and `from revisor.modelo import Estado, Resultado` |
| `configuracion.py` | `from revisor.modelo import Servicio, nombres_repetidos` (plus those of the standard library, unchanged) |
| `modelo.py` | imports nothing from your project |

The `cli.py` is rewritten entirely in 7.3. You cannot run anything yet: the three new files are still to be created (`__init__.py`, `__main__.py` and `pyproject.toml`) and `cli.py` still has to be written. Keep reading.

### 7.2 `pyproject.toml`: the project described for the tools

A package, by itself, is only a folder. For `pip` to know how to install it, it has to be described: what it is called, what version it is, what version of Python it needs, what command it creates. That is written in a file called `pyproject.toml` in the root of the project. It is a TOML file, the format you learned to read in Lesson 6, and it is the official mechanism: the [packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) describes it as the place where a Python project's metadata goes. This is the `revisor`'s:

```toml fig07_01/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.6.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
revisor = "revisor.cli:main"
```

It has three tables, and each one answers a different question.

**`[build-system]`: what is it built with?** Installing a package, even if it is yours and local, implies a build step: reading the `pyproject.toml`, gathering the files, producing something installable. That work is done by a tool called a *build backend*, and the project must say which one it wants. `requires` lists what has to be downloaded to build, and `build-backend` names the backend. Here `hatchling` is used, the one the official packaging guide uses, and version 1.27 or later is requested (`>=1.27`). There is a detail worth knowing from the start: the first time you install the package, `pip` **downloads `hatchling` from the internet** into a temporary environment to build it. It is a *build* dependency, not one of your program: the `revisor` still depends on nothing to work. But without a connection, the installation would fail at that step. The rules of this table are in [PEP 518](https://peps.python.org/pep-0518/) and the interface of the backends in [PEP 517](https://peps.python.org/pep-0517/); `hatchling` has its [own documentation](https://hatch.pypa.io/latest/).

**`[project]`: what is this project?** Here go the data anyone would expect on a package's data sheet. `name` is the name it is installed under. `version` is the version: the course raises it one step in each lesson from today on (`0.6.0` is today's, and Lesson 11 leaves it at `1.0.0`). `description` is a sentence. `requires-python = ">=3.12"` says which versions of Python can run it: `pip` will refuse to install it on an older Python, instead of letting it fail with an incomprehensible `SyntaxError` later. And `dependencies = []` is the list of third-party packages your program needs in order to run: today, none, and that is why it is empty. In Lesson 9 one will appear. The standard that defines these fields is [PEP 621](https://peps.python.org/pep-0621/).

**`[project.scripts]`: what command does it create?** This is the table that turns a package into a tool. The line `revisor = "revisor.cli:main"` says: “when installing, create in the environment a command called `revisor`, and when someone runs it, have it call the `main` function of the `revisor.cli` module.” The `package.module:function` form is a convention fixed by the [entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/). When you install it, the `revisor` command will sit next to your environment's `python`, and it will work the same as `python -m revisor`. And again: the value that `main` returns becomes the command's exit code.

Copy the content into `pyproject.toml`, next to `servicios.toml`, in the project folder. You cannot install yet: the center of the program is still missing.

### 7.3 `argparse`: command-line options

#### 7.3.1 What a program receives from the terminal

When you type `python -m revisor --formato json`, the terminal splits what you typed into words and hands them to the program as a list of texts, which Python keeps in `sys.argv`. In that list, the first position is the name of the program and the others are the arguments: `["fig07_02.py", "--formato", "json"]`. You could walk through it yourself, with a `for`, and look by hand for `--formato` and the text that follows it. But that soon becomes tedious: what happens if the user writes the option twice? If they forget the value? If they write `--formato=json` with an equals sign? So as not to rewrite those rules in every program, the standard library ships the `argparse` module, which solves them, generates the help by itself, and validates what the user types.

Look at a small program that demonstrates it, `fig07_02.py`. It declares two options and prints them:

```python
# fig07_02.py
import argparse

parser = argparse.ArgumentParser(description="Demostración de argparse.")
parser.add_argument("--config", default="servicios.toml")
parser.add_argument("--formato", choices=["tabla", "json"], default="tabla")

argumentos = parser.parse_args()
print(f"config = {argumentos.config}")
print(f"formato = {argumentos.formato}")
```

`argparse.ArgumentParser(description=...)` creates the **parser**: the object that will know how to interpret the command line. Each `add_argument` declares an option: its name (with two hyphens in front, the convention for long options), a default value (`default`) and, in the second one, `choices`, the closed list of permitted values. Finally, `parse_args()` reads `sys.argv`, checks everything and returns an object with one attribute per option, so that `argumentos.formato` has the value the user typed, or the default if they typed nothing. Run it without options, and then with them:

```text
$ python fig07_02.py
config = servicios.toml
formato = tabla
```

```text
$ python fig07_02.py --formato json --config otro.toml
config = otro.toml
formato = json
```

Without options the default values apply. With them, the ones you typed apply, in whatever order you like. But what is valuable is what `argparse` does without being asked. First, the help: `-h` and `--help` exist automatically.

```text
$ python fig07_02.py --help
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]

Demostración de argparse.

options:
  -h, --help            show this help message and exit
  --config CONFIG
  --formato {tabla,json}
```

It is put together from what you declared: the usage, the description, and each option with its list of values. (The fixed words of `argparse`, like “options” or “show this help message and exit,” are in English because they come from the library; the texts you write with `help=` and `description=` come out as you write them, and that is what we will do in the `revisor`.) Second, the errors: if the user types something you did not declare, `argparse` rejects it with a message and ends the program:

```text
$ python fig07_02.py --verbose
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]
fig07_02.py: error: unrecognized arguments: --verbose
```

The message says what failed (`unrecognized arguments: --verbose`) and repeats the usage line so that the user sees what the correct form is. It also ends the program with an exit code other than zero, specifically 2: the [`argparse` documentation](https://docs.python.org/3/library/argparse.html#exiting-methods) establishes it for every usage error. That 2 will be the `revisor`'s when the usage is invalid.

#### 7.3.2 The `revisor`'s `cli.py`

With that in hand, the central module of the package reads without surprises. `cli.py` (“*command-line interface*”) replaces the flat `revisor.py` of Lesson 6. It has two functions: one that builds the parser and another that is the program. Read it whole once:

```python
# fig07_01/src/revisor/cli.py
import argparse
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

    resultados = revisar_todos(servicios)
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

**`construir_parser`** returns the parser, with three options. `--config` receives the path of the configuration file; `type=Path` tells `argparse` to convert the text the user types into a `Path` (Lesson 6), and its default value is `Path("servicios.toml")`, the same as always. `--formato` has two closed choices, `tabla` and `json`, and defaults to `tabla`: if the user types anything else, `argparse` rejects it before the rest of `main` gets to see the value, and no `if` has to be written for that. And `--version` uses `action="version"`, a predefined action that prints a text and ends: the text is `revisor` followed by the version number, which is **read from the metadata of the installed package** with `importlib.metadata.version("revisor")`. This solves a very common problem: the version number would be written in `pyproject.toml` and again in the code, and the two copies would end up differing. This way it exists in a single place, the `pyproject.toml`. The `prog="revisor"` argument fixes the name that appears in the usage and in the errors; without it, in Python 3.12 `__main__.py` would appear, the file run with `-m`, and in 3.14 `python -m revisor` would appear; with `prog`, both versions say the same thing.

**`main`** is the program. It receives an optional list of arguments, `argv: list[str] | None = None`, and returns an integer. If `argv` is `None`, `parse_args(None)` reads the real command line; if you pass it a list, it uses that instead. That parameter looks like a luxury today and is a key piece in Lesson 8, where the tests will call `main(["--formato", "json"])` without touching the terminal. The body is what you already know: it reads the services with `leer_servicios(argumentos.config)`, and if that fails with `ErrorDeConfiguracion`, it prints the message and returns 2. There are two differences from Lesson 6, and they are the two ideas of 7.4: the message now goes out with `file=sys.stderr` (to the error output, not the standard one) and returns 2 instead of cleaning up and going on. Then it checks the services, and depending on `--formato` it prints the usual table or the JSON from `reporte_a_json`. Finally, it decides the exit code: it builds the list of results whose status is **not** `ARRIBA` (the `is not` operator is the negation of `is`, Lesson 3), and if it is empty it returns 0, and if not, 1.

To make it explicit, the `revisor`'s exit codes are these three, **those of the whole course**:

| Code | What it means |
|---|---|
| `0` | Everything is `ARRIBA` (up). |
| `1` | The `revisor` worked, but some service is `LENTO` (slow) or `CAIDO` (down). |
| `2` | The `revisor` could not check: the usage is invalid (`argparse` decides this) or the configuration is no good. |

The distinction between 1 and 2 matters a lot. A `1` is an answer: “I checked and found problems.” A `2` is a failure of the program itself: “I could not even check.” Whoever automates the `revisor` will treat them differently: with a `1` they will notify whoever attends to the services; with a `2` they will notify whoever maintains the `revisor`.

### 7.4 Exit codes, two text channels, and the editable install

#### 7.4.1 Exit codes

Every program that ends leaves whoever called it an integer between 0 and 255. It is the **exit code** (*exit status*). By Unix convention, **0 means success and any other number means some kind of failure**. There is nothing magic: it is an agreement, and the whole terminal ecosystem respects it. In the terminal (technically, the command shell, which on Linux Mint is `bash`) you can ask for the code of the last command with the special variable `$?`, read with `echo $?`. The POSIX standard defines how the shell interprets it in the [exit status section](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_08_02), and it is what makes it possible to write things like `revisor && echo "todo bien"` (the `echo` only runs if `revisor` ended with 0) or `revisor || avisar.sh` (the second only runs if the first ended with something other than 0).

In Python, there are two ways to exit with a code. One is to call `sys.exit(codigo)`, which raises `SystemExit`. The other is what you already saw in `__main__.py`: raising `SystemExit` yourself. They do the same, and the [documentation of `sys.exit`](https://docs.python.org/3/library/sys.html#sys.exit) and that of [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) explain it. What matters is the design: `main` **returns** the code instead of calling `sys.exit` on its own, and it is `__main__.py` that turns it into an exit. That way `main` can be called from other code (a test, for example) and return its number without killing the process that called it. When someone installs the package, the `revisor` command created by `[project.scripts]` does the same: it calls `main()` and exits with whatever it returns.

#### 7.4.2 Two channels: standard output and standard error

A program has, from the moment it starts, two places to write text. The **standard output** (`stdout`) is the normal channel: what `print` writes by default, and where the results go. The **standard error** (`stderr`) is a separate channel for warnings and errors. In the terminal, both appear on the screen, side by side, and that is why they look like the same thing. But they are different channels, and that difference shows as soon as we redirect one. Look at `fig07_03.py`, which writes to both:

```python
# fig07_03.py
import sys

print("reporte: 4 servicios revisados")
print("aviso: reportes no respondió", file=sys.stderr)
```

`print(..., file=sys.stderr)` sends the text to the standard error instead of the standard output; `sys` is a standard library module that gives access to things of the interpreter itself, among them `sys.stderr` ([documentation](https://docs.python.org/3/library/sys.html#sys.stderr)). Run it three times:

```text
$ python fig07_03.py
reporte: 4 servicios revisados
aviso: reportes no respondió
```

```text
$ python fig07_03.py > /dev/null
aviso: reportes no respondió
```

```text
$ python fig07_03.py 2> /dev/null
reporte: 4 servicios revisados
```

The first shows both lines. The second uses `>`, which **redirects the standard output** to another place (here, `/dev/null`, a special Linux file that discards everything written to it): only the warning remains, which travels through the other channel. The third uses `2>`, which redirects channel number 2, the error one, and lets the report through. (The channels have numbers: 0 the input, 1 the standard output, 2 the error output.) The [shell redirections](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_07) are the mechanism that makes it possible.

That is what makes the separation useful. When someone runs `revisor --formato json > reporte.json`, they want the `reporte.json` file to contain **only the JSON**. If the program wrote an error message to the standard output, the file would end up with mixed text and stop being valid JSON. With the error in `stderr`, the message appears on the screen, the file stays clean (or empty, if the program did not get to produce anything) and the exit code tells what happened. That is why `cli.py` sends configuration errors to `stderr` and the report to `stdout`.

This is how the already installed `revisor` behaves when it is given a configuration file that does not exist: the message goes out through the error output and the program ends with code 2.

```text
$ python -m revisor --config no-existe.toml
error de configuración: no existe el archivo no-existe.toml
$ echo $?
2
```

#### 7.4.3 Installing in editable mode

The step that ties everything together is still missing: installing the package. First, see what happens if you try to run it **without** installing it. With the environment active and standing in the project folder, with the files already in place:

```text
$ python -m revisor
/home/tu_usuario/curso-python/.venv/bin/python: No module named revisor
```

The message, `No module named revisor`, is what was to be expected from 7.1.2: Python looked for a module called `revisor` in the current folder and in the environment, and did not find it, because the package is inside `src/`, a folder where it does not look. (The path at the beginning is that of your virtual environment's `python`; yours will be that of your folder.) It is not an error in your code: it is what `src/` causes on purpose, and it is solved by installing.

The installation is done with `pip`, already inside the environment, from the project folder (where the `pyproject.toml` is):

```bash
python -m pip install -e .
```

The final dot means “the project in this folder,” and `-e` (“*editable*”) asks for an **editable** installation. You will see several progress lines, which change from one version of `pip` to another, and the last one says something like this:

```text
Successfully installed revisor-0.6.0
```

If the message is a different one, read the cause: the most common is that you are not in the folder that has the `pyproject.toml`, or that you have no connection for `pip` to download `hatchling`.

What does “editable” mean? A normal installation **copies** the package's files to the environment's `site-packages` folder, and from then on the installed package and your working folder are two different things: if you edit your code, the installed one does not find out. An editable installation, on the other hand, leaves in the environment **a pointer to your `src/` folder**, so Python imports the code from where it is, just as you wrote it ([PEP 660](https://peps.python.org/pep-0660/); the [`pip` documentation](https://pip.pypa.io/en/stable/topics/local-project-installs/) explains the two types of local installation). It is what you want while developing: you change a line, run, and see the change, without reinstalling. With the package installed, run it; this time the exit code is printed by `echo $?`:

```text
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
$ echo $?
1
```

There is the usual table, with the summary, and the exit code is **1**, because among the four services there is one `LENTO` (`inventario`) and one `CAIDO` (`reportes`). It is the behavior that was wanted: the program worked, and warns that it found problems. The `--formato json` option produces the report for machines, which is the contract Lesson 6 fixed:

```text
$ python -m revisor --formato json
{
  "servicios": [
    {
      "nombre": "catalogo",
      "url": "https://catalogo.example",
      "estado": "ARRIBA",
      "tiempo_ms": 142,
      "detalle": "200"
    },
    {
      "nombre": "inventario",
      "url": "https://inventario.example",
      "estado": "LENTO",
      "tiempo_ms": 2300,
      "detalle": "200"
    },
    {
      "nombre": "pagos",
      "url": "https://pagos.example",
      "estado": "ARRIBA",
      "tiempo_ms": 87,
      "detalle": "200"
    },
    {
      "nombre": "reportes",
      "url": "https://reportes.example",
      "estado": "CAIDO",
      "tiempo_ms": null,
      "detalle": "sin conexión"
    }
  ],
  "resumen": {
    "total": 4,
    "arriba": 2,
    "lento": 1,
    "caido": 1,
    "promedio_ms": 843
  }
}
$ echo $?
1
```

The `--version` option reads the number from the installation, and it works because you installed the package:

```text
$ python -m revisor --version
revisor 0.6.0
```

And `--help` gives you the help, put together with the texts you wrote in `help=`:

```text
$ python -m revisor --help
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]

Revisa el estado de una lista de servicios.

options:
  -h, --help            show this help message and exit
  --config CONFIG       archivo TOML con la lista de servicios (por omisión:
                        servicios.toml)
  --formato {tabla,json}
                        forma del reporte (por omisión: tabla)
  --version             show program's version number and exit
```

Half of what `[project.scripts]` promised is still missing: the `revisor` **command**. It was created on installing, next to the environment's `python`, and with the environment active it is run without `python -m`:

```text
$ revisor --version
revisor 0.6.0
```

What `-m` does is useful because it always works, even if the command were not in view. But the command is how people will use the `revisor` in Lesson 11, installed with `pipx`.

Two clarifications about what “editable” does not cover. The first: **it only follows the code, not the metadata**. If you change the content of a module, the change is seen immediately. But if you change the `pyproject.toml` (for example, the version, or a command in `[project.scripts]`), the environment keeps the metadata of the last installation, until you run `python -m pip install -e .` again. Exercise 4 checks it. The second: the editable installation lives in your **virtual environment**, so a new environment (or a freshly created one) does not have the `revisor` until you install it again. It is exactly the behavior that is wanted: no installation gets mixed with the system's Python.

> **Optional box: `uv`.** There is a newer tool, `uv`, that does by itself the work of `venv` and `pip`, and is faster. With it, the same steps are written `uv venv` (creates the `.venv` environment) and `uv pip install -e .` (installs the project in it). It can also install other versions of Python: `uv python install 3.14` downloads 3.14 without touching the system's Python, which is the most convenient way to try this course on the latest version in addition to Mint's 3.12. The [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/) explains how to get it, and its documentation on [Python versions](https://docs.astral.sh/uv/concepts/python-versions/) and on [the `uv pip` interface](https://docs.astral.sh/uv/pip/) covers the rest. This course does not require it: everything you see here works with the `python` and `pip` you already have.

#### 7.4.4 The project step: putting it all together

If you have been following the lesson, your `~/curso-python/revisor/` folder already looks like 7.1.2. These are the complete steps, in order, for whoever wants them in one go:

1. Create `src/revisor/` and move the four modules into it; rename `revisor.py` to `cli.py` and delete `ver_json.py` (7.1.4).
2. Put `revisor.` in front of the imports of your modules (7.1.4).
3. Write `src/revisor/__init__.py` and `src/revisor/__main__.py` (7.1.3).
4. Write `pyproject.toml` (7.2).
5. Rewrite `src/revisor/cli.py` with `construir_parser` and `main` (7.3.2).
6. With the environment activated and from the project folder, run `python -m pip install -e .` (7.4.3).
7. Test: `python -m revisor`, `python -m revisor --formato json`, `python -m revisor --version`, and after each one, `echo $?`.

There is a consequence of what you have just done, which shows when you run it from **another folder**. Go up to the folder above and run the same command:

```text
$ python -m revisor
error de configuración: no existe el archivo servicios.toml
```

The package was found (it is installed in the environment, it no longer matters where you are), but the configuration file was not: `--config` is `servicios.toml` by default, a relative path, and the folder above does not have one. The message is the one you know from Lesson 6, now on the error output and with exit code 2. The `--config` option exists precisely for this: `python -m revisor --config revisor/servicios.toml` would work from there. Where the code lives and where the configuration lives are two different questions, and the program separates them.

## The error you will see

This lesson has two main errors, both from the list above, and two supporting ones that appear when something in the setup is forgotten.

**`No module named revisor`.** You already saw it in 7.4.3: running `python -m revisor` before `pip install -e .`. The cause is the `src/` layout, and the fix is to install. If you already installed and it still appears, check that you have the environment activated: the message begins with the path of the `python` that was used, and if that path is `/usr/bin/python3` instead of that of your `.venv`, you are using the system's Python, which does not have your package.

**The `argparse` usage error.** Ask for a format that does not exist:

```text
$ python -m revisor --formato xml
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]
revisor: error: argument --formato: invalid choice: 'xml' (choose from 'tabla', 'json')
$ echo $?
2
```

Read the two lines: the first repeats the usage, with the options that exist and their permitted values between braces (`{tabla,json}`); the second says which argument failed and why: `invalid choice: 'xml'`. In parentheses, the list of the valid ones. The exit code is 2, the one `argparse` always uses for invalid usage. A version detail: this is the text of Python 3.14, which shows the options in quotation marks, `('tabla', 'json')`. In Python 3.12 the list comes out without quotation marks, `(choose from tabla, json)`. It is the only output of the lesson that differs between the two versions, and it is a change in the format of the text; the meaning is the same.

**`ModuleNotFoundError: No module named 'modelo'`.** It appears if you moved the files but forgot to change some import: the package is found, but one of its modules still imports `modelo` plain, and there is no loose `modelo` anymore. The report, abbreviated:

```text
Traceback (most recent call last):
  ...
  File "src/revisor/__main__.py", line 2, in <module>
    from revisor.cli import main
  File "src/revisor/cli.py", line 9, in <module>
    from modelo import Estado
ModuleNotFoundError: No module named 'modelo'
```

It is read from the bottom up, as always: the last line says which module was not found (`modelo`); the line above, in which file and on which line the failing `import` is (`cli.py`, line 9); and further up, the chain of who imported whom. The fix is `from revisor.modelo import Estado`. (The line number will depend on how you wrote your `cli.py`; what matters is the module name on the last line.)

**`importlib.metadata.PackageNotFoundError: No package metadata was found for revisor`.** It appears if you run the code without having installed the package (for example, adding `src` to the list of search places by hand). The modules are found, but `version("revisor")`, which `construir_parser` always runs, looks for the **metadata** of an installation, and there is none. It is the proof that the version number comes from the installation and not from the code: the solution is `python -m pip install -e .`, not hiding the line. The report ends like this:

```text
importlib.metadata.PackageNotFoundError: No package metadata was found for revisor
```

## What gets done wrong

**Importing without the package name inside a package.** `from modelo import Servicio` works while the files are stuck together and fails as soon as the code is installed or run with `-m`. Inside the package, always write `from revisor.modelo import Servicio`.

**Fixing the imports by modifying `sys.path`.** It is a recipe that circulates: adding the code's folder by hand to the list of search places so that the `import`s work. It solves the symptom and hides the cause, which is that the package is not installed. With `pip install -e .` it is not needed.

**Installing with `pip` outside the virtual environment.** You already know why it does not work on Linux Mint (Lesson 1): the system's Python does not ship `pip` (`No module named pip`), and where it does, the PEP 668 protection stops it with `externally-managed-environment`. And the way out that is sometimes suggested, forcing it, breaks the system's own tools. Install inside the `.venv`, always.

**Writing the version number in two places.** One in `pyproject.toml` and another in a constant in the code: sooner or later they differ, and the version the program reports is no longer the one that was installed. The number lives in the `pyproject.toml`, and the program reads it with `importlib.metadata`.

**Sending errors to the standard output.** It mixes the warning with the report, and `revisor --formato json > reporte.json` produces a file that is not valid JSON. Errors go to `sys.stderr`.

**Always ending with code 0.** A program that exits just as well with everything down as with everything up is of no use to any automation. The exit code is part of the program's contract, as much as the format of the report.

**Inventing exit codes without documenting them.** A 3 for this, a 4 for that, without anyone knowing them, forces whoever automates to read the source code. There are three codes and they are in a table.

**Reading `sys.argv` by hand.** It works until someone writes `--formato=json` instead of `--formato json`, or forgets the value, or asks for the help. `argparse` already solved those cases.

**Changing `pyproject.toml` and not reinstalling.** The editable installation follows the code, not the metadata. If you change the version or a command and the environment keeps the previous one, a `python -m pip install -e .` is missing.

## Exercises

### Exercise 1 — The report in JSON and its code

With the package installed, run `python -m revisor --formato json` and, right after, `echo $?`. Before running, write what you expect to see: how many services there are in the `servicios` array, what value `tiempo_ms` has for `reportes`, and what exit code. Then redirect the output to a file with `python -m revisor --formato json > reporte.json` and look at the content of `reporte.json` with `cat reporte.json` (`cat` prints the content of a file on the screen). Did the exit code change when redirecting?

### Exercise 2 — The three codes

Provoke the `revisor`'s three exit codes, one by one, and check them with `echo $?`: (a) a `0`, for which you need a configuration in which all the services are `ARRIBA` (write a `solo-arriba.toml` file with a single service, `pagos`, and use it with `--config`); (b) a `1`, with the usual `servicios.toml`; (c) a `2` for invalid configuration, with a `roto.toml` that has a service without `nombre`; (d) another `2`, now for invalid usage, with a `--formato` value that does not exist. For each case, first write what you expect to see and on which channel the message appears.

### Exercise 3 — Where the code lives and where the configuration lives

Leave the project folder with `cd ..` and run `python -m revisor`. What message do you get and what exit code? Then run the same command passing the path of the configuration with `--config`. Explain in your own words why the package is found from any folder but the configuration file is not.

### Exercise 4 — What the editable installation follows and what it does not

With the package installed in editable mode: (a) in `src/revisor/formato.py`, change the word `promedio` in the summary to `media`, and run the `revisor` without reinstalling: is the change noticed? Put it back as it was. (b) In `pyproject.toml`, change the version to `0.6.1`, and run `python -m revisor --version` without reinstalling: what version does it say? (c) Run `python -m pip install -e .` and ask for the version again. (d) Put the version back to `0.6.0` and reinstall. Explain the difference between (a) and (b).

## Solutions

### Solution 1

The prediction: the `servicios` array has **four** elements, one per service; the one for `reportes` has `"tiempo_ms": null` (it did not answer, and `None` is written `null` in JSON); and the exit code is **1**, because of the slow service and the down one. The output of `python -m revisor --formato json` is the one you saw in 7.4.3, and `echo $?` prints `1`.

When redirecting, the content of `reporte.json` is **exactly the same JSON**: nothing from the terminal got mixed into it, because the warnings (if there were any) go through another channel. And the exit code **does not change**: redirecting moves the text, not the result. That is the property that makes it possible to write `revisor --formato json > reporte.json || avisar.sh` and have the `||` keep working.

### Solution 2

(a) With a single service that answers well:

```toml
[[servicios]]
nombre = "pagos"
url = "https://pagos.example"
```

Run with `python -m revisor --config solo-arriba.toml`:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA      87ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 87ms
```

and `echo $?` prints **0**. (Notice that the summary says “1 servicio” and “0 lentos”: the plural is decided by the count, as in Lesson 5.)

(b) With the usual `servicios.toml`: the table of four services and the code **1**.

(c) With a `roto.toml` whose only service has no `nombre`:

```toml
[[servicios]]
url = "https://pagos.example"
```

Run with `python -m revisor --config roto.toml`, the message `error de configuración: servicio 1: falta 'nombre'` comes out through the **error output**, and the code is **2**. To check the channel, repeat the command with `2> /dev/null`: nothing appears on the screen, because the only thing printed went through `stderr`; the exit code is still 2.

(d) With `python -m revisor --formato xml`, the `argparse` error you already saw: it goes through the error output, and the code is **2**.

### Solution 3

From the folder above, `python -m revisor` prints, through the error output, `error de configuración: no existe el archivo servicios.toml`, and the exit code is **2**. With `python -m revisor --config revisor/servicios.toml` the program finds the file, prints the table of four services and exits with **1**.

The reason: the **package** is found because it is installed in the environment, and the environment does not depend on the folder where you are. In contrast, `servicios.toml` is a **data** file with a relative path, and a relative path is always counted from where you are standing. They are two different search mechanisms: Python looks for code in the environment's folders; the program looks for the configuration where it is told. That is why `--config` exists.

### Solution 4

(a) Yes, it is noticed: the summary says `media 843ms` instead of `promedio 843ms`, without reinstalling, because the editable installation imports the code from your `src/` folder. (b) It is not noticed: `--version` still says `revisor 0.6.0`, because the version is read from the metadata that was saved in the last installation, and editing the `pyproject.toml` does not update it. (c) After `python -m pip install -e .`, `--version` says `revisor 0.6.1`. (d) When putting the version back to `0.6.0` and reinstalling, it says `revisor 0.6.0` again.

The difference: the **code** is imported from where it is, every time Python starts; the **metadata** (version, commands) is copied into the environment on installing. What `-e` avoids is the copying of the code, not that of the metadata.

## How I know I got it

- [ ] `python -m revisor` prints the table of four services with the summary `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`, and `echo $?` prints `1`.
- [ ] `python -m revisor --formato json` prints the JSON with `"promedio_ms": 843`, and `python -m revisor --formato json > reporte.json` leaves in the file a valid JSON and nothing else.
- [ ] `python -m revisor --version` prints `revisor 0.6.0`, and the `revisor --version` command prints the same.
- [ ] `python -m revisor --formato xml` ends with the `argparse` error and code 2.
- [ ] `python -m revisor --config no-existe.toml` prints `error de configuración: no existe el archivo no-existe.toml` and ends with 2; with `2> /dev/null`, nothing is seen on the screen.
- [ ] You can explain in your own words why `python -m revisor` fails with `No module named revisor` before installing, and why that is what `src/` intends.
- [ ] You can say which channel each of the `revisor`'s messages uses (report, configuration error, usage error) and which code goes with each case.
- [ ] You noted in your logbook which part of the setup (paths, imports, installation) was hardest for you.

## Summary

Answer without looking at the lesson:

1. What is the difference between a module and a package, and what makes something a package?
2. What advantage does putting the package inside `src/` have? What would happen with `python -m revisor` from the root if it were not there?
3. What does `python -m revisor` run, and what does `raise SystemExit(main())` do?
4. What question does each table of the `pyproject.toml` answer: `[build-system]`, `[project]` and `[project.scripts]`?
5. Why does `pip install -e .` need the internet the first time, if the `revisor` has no dependencies?
6. What does `parse_args()` return? What does `argparse` do when the user types an option that does not exist, and with what code does it end?
7. What do the `revisor`'s codes 0, 1 and 2 mean? How is the code of the last command read in the terminal?
8. What is the difference between the standard output and the standard error? What do `>` and `2>` do?
9. What does an editable installation follow and what does it not? How is what it does not follow updated?
10. Where does the number that `--version` prints come from, and why is it not written in the code?

## Further reading

- [Python, `argparse`](https://docs.python.org/3/library/argparse.html): the complete reference for the module (actions, subcommands, option groups). Accessed on October 7, 2026.
- [Python Packaging User Guide, “Writing your `pyproject.toml`”](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/): all the fields of `[project]` and of `[project.scripts]`, and the reasons for the design. Accessed on October 7, 2026.
- [Python Packaging User Guide, “src layout vs flat layout”](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/): the two ways of placing the package, compared with their costs. Accessed on October 7, 2026.
- [Python, tutorial on modules and packages](https://docs.python.org/3/tutorial/modules.html#packages): how a package is imported and organized, with absolute and relative imports. Accessed on October 7, 2026.
