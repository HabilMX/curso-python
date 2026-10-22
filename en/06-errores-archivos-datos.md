# Lesson 6 — Errors, files, and outside data

**Time:** 2 × 90 min (two sessions; the break falls between sections 6.2 and 6.3)

**What you build:** reading the `revisor`'s configuration: the list of services is no longer written in the code and is read from a `servicios.toml` file

**What you learn:** exceptions (`try`, `except`, `else`, `finally`, a custom exception and `raise ... from`); reading a *traceback* from the bottom up; files with `with` and `pathlib`; explicit UTF-8; the TOML and JSON formats; validating what arrives from outside; and why `eval` and `pickle` are not used

**Where you come from.** You bring the project from [Lesson 5](05-modelo-de-datos.md): a `revisor` with its data model (`Servicio`, `Estado`, `Resultado`), the classification with `match`, the table report with its summary, and the `SERVICIOS` list written by hand inside `revisor.py`. It works, but the project exercise of Lesson 5 left you with an annoyance: to add a service to the report you have to **open the Python code and edit it**. Whoever manages the services should not need to know how to program, and whoever programs should not have to touch the code every time an address changes. This lesson separates the two things: the data goes into a file, and the program learns to read it and to distrust it. You work in your `~/curso-python/revisor/` folder, with the virtual environment activated, and you run everything with `python`.

**What this lesson does not do.** It queries no network: `revisar` still uses the simulated data of Lesson 5, and that does not change until [Lesson 9](09-http-y-asyncio.md). Nor does it turn the `revisor` into a command with options (`--config`, `--formato`): that is the work of [Lesson 7](07-paquete-linea-de-comandos.md). Today the file name is written in a constant of the program. What gets solved here is **how to read a configuration file without the program breaking in incomprehensible ways** when the file does not exist, is badly written or says things that make no sense.

**About the runs.** To run a figure, go into the lesson's folder in the repository and run `python fig06_01.py`; the figures that live in a folder of their own (`fig06_06/`, `fig06_07/`, `fig06_18/`) are run from inside it. All the outputs of this lesson were obtained with Python 3.14.8 and repeated with Python 3.12.12, from the same 3.12 line that Linux Mint 22 ships. (Mint 22's is 3.12.3, the one published by Ubuntu 24.04, its base: the [page of the `python3.12` package for Ubuntu 24.04 on Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12) shows it.) They are identical, except for some underline marks (`~~~~^^`) that an error's report carries in one version and not in the other; if you see more or fewer marks on your screen, that is normal. The programs are in [`programas/06-errores-archivos-datos/`](https://github.com/HabilMX/curso-python/tree/main/programas/06-errores-archivos-datos), in the course repository.

## By the end you will be able to

- Read an error's report (the *traceback*) from the bottom up and say what failed, where, and who called whom.
- Write a `try` with `except`, `else` and `finally`, catching the specific exception you know how to handle and letting the others through.
- Define a custom exception with one line of inheritance and raise it with `raise ... from`, so that the original error is not lost.
- Open and read a file with `with` and with `pathlib.Path`, always with the UTF-8 encoding spelled out, and explain what happens if it is not.
- Read a TOML file with `tomllib` and convert data to JSON and back with `json`, reading the line and the column when the JSON is malformed.
- Validate outside data with `isinstance` and `urlsplit`, and explain why `True` passes a sloppy integer validation.
- Explain why a text that comes from outside is never passed to `eval` or to `pickle`.

## The why before the how

Open your `revisor.py` from Lesson 5 and look at the `SERVICIOS` list. Every time the operations team wants to check a new service, someone has to edit that file, save it, and run it again. For the programmer it is an annoyance; for anyone else it is a wall. And there is a deeper problem: that code and that data change **for different reasons and at different paces**. The program changes when you discover a bug or want a new function; the list of services changes when the company adds a service. Mixing the two in one file forces one to wait for the other.

The solution is the usual one: the data lives in a **configuration file**, a text with rules that anyone can edit, and the program reads it at startup. But as soon as the program reads something another person wrote, it enters new territory. Up to Lesson 5, every piece of data in the `revisor` was written by you, in the same file as the code, and if it was wrong you knew instantly. A file from outside can fail in four ways, and all four are normal, not exceptional:

1. **It does not exist**, or it exists in a different folder than the one you think.
2. **It exists but is badly written**: a quotation mark is missing, a comma is left over.
3. **It is well written but something is missing**: a service without a name, without an address.
4. **It is complete but says something absurd**: an address that is not a web page, a negative timeout, two services with the same name.

A serious program tells the four apart and tells the person **which one happened and how to fix it**, instead of showing a thirty-line error report written for programmers. That is achieved with two tools that this lesson teaches together because they cannot be understood separately: **exceptions** (how a program signals that something went wrong, and how another one catches it) and **validation** (how you check that what arrived makes sense).

The path has two sessions. The **first** covers concepts 6.1 and 6.2: exceptions and files. When you finish it you will know how to read an error report and open a text file without surprises. The **second** covers 6.3 and 6.4: the formats (TOML and JSON) and validation. When you finish it you will have the `revisor` reading its list of services from a file and complaining in clear Spanish when the file is no good. With that destination in mind, this is what you will see at the end of the lesson when you run the `revisor` from another folder, without having gone through where the file is:

```text
error de configuración: no existe el archivo servicios.toml
```

A one-line message, instead of an error report. To get there you first need to understand what an exception is.

## The concepts

### 6.1 Exceptions

#### 6.1.1 What an exception is and how to read its report

Until now, when something failed in your programs, Python stopped and printed a block of text in red, the *traceback* (in this course, “the error report”). You read it for the first time in [Lesson 1](01-instalacion.md) and you have seen it in every lesson. Now we are going to see what is behind it: that report is the notice of an **exception**, which is Python's way of saying “something happened here that I do not know how to resolve.” When a line of the program cannot do what it was asked, it **raises** an exception. The exception goes up through the functions that were running, from the most recent to the oldest, looking for someone who knows what to do with it. If it reaches the top without anyone catching it, the program stops and Python prints the report.

Let us provoke one on purpose, with a case that will really happen when the `revisor` reads files: a piece of data that should be a number and arrives as something else. For that you need a new function: `int(texto)` converts a text into an integer, just as `str()` (Lesson 2) converts a value into text. `int("142")` gives the number 142. But what does `int("142 ms")` give? Run it with `fig06_01.py`:

```python
# fig06_01.py
def leer_tiempo(texto: str) -> int:
    return int(texto)


def main() -> None:
    tiempo_ms = leer_tiempo("142 ms")
    print(f"tiempo: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

The program defines two functions, `leer_tiempo` and `main`, and `main` calls `leer_tiempo` with a text that has the letters “ms” stuck on. Run it:

```text
$ python fig06_01.py
Traceback (most recent call last):
  File "fig06_01.py", line 12, in <module>
    main()
    ~~~~^^
  File "fig06_01.py", line 7, in main
    tiempo_ms = leer_tiempo("142 ms")
  File "fig06_01.py", line 3, in leer_tiempo
    return int(texto)
ValueError: invalid literal for int() with base 10: '142 ms'
```

This is the report, and it is worth learning to read it well, because you will read it hundreds of times. **It is read from the bottom up.** The **last line** is the most important one: `ValueError: invalid literal for int() with base 10: '142 ms'`. It says two things: the **type** of the exception, `ValueError` (“invalid value”: the type of the data was right, a text, but its content is no good for what was wanted), and a **message** that explains what happened. In plain words: “invalid text to convert to an integer in base 10: '142 ms'.” The “base 10” is the numbering system we all use every day; the message only says that `int` expected a number written with digits from 0 to 9 and found, after the 142, a space and the letters `ms`. (Spaces at the beginning or at the end do not bother it: `int(" 142 ")` gives `142`; what it does not accept is anything that is not part of the number.)

The lines above say **where** it happened, and they are in reverse order from how things occurred. Each pair of lines that starts with `File` is a **frame**: a function that was running. The last frame (`in leer_tiempo`, line 3) is where the exception was born: the line `return int(texto)`. The frame above it (`in main`, line 7) is the one that called `leer_tiempo`. And the first (`in <module>`, line 12) is the program itself, which called `main()`. Read the report as a stack of plates: the plate at the bottom is the most recent, and it is where the problem started. The lines with `~~~~^^` are a help from recent versions of Python ([PEP 657](https://peps.python.org/pep-0657/)): they underline the exact part of the line that failed, so that you do not have to guess which of the three calls on a long line it was.

As long as nobody catches the exception, that is the complete story: it is raised, it goes up the stack, the program dies. The [official documentation on errors and exceptions](https://docs.python.org/3/tutorial/errors.html) tells the same with more examples. Let us now see how to catch it.

#### 6.1.2 `try`, `except`, `else` and `finally`

Catching an exception is telling Python: “try this; if it fails in *this* way, do *this other thing* instead of dying.” It is written with the `try` statement. Look at the program `fig06_02.py`, which converts two texts, a good one and a bad one:

```python
# fig06_02.py
def leer_tiempo(texto: str) -> int | None:
    try:
        tiempo_ms = int(texto)
    except ValueError:
        print(f"  '{texto}' no es un número entero")
        return None
    else:
        print(f"  '{texto}' se convirtió en {tiempo_ms}")
        return tiempo_ms
    finally:
        print("  (fin de la conversión)")


def main() -> None:
    for texto in ["142", "142 ms"]:
        print(f"leyendo '{texto}'")
        tiempo_ms = leer_tiempo(texto)
        print(f"  resultado: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_02.py
leyendo '142'
  '142' se convirtió en 142
  (fin de la conversión)
  resultado: 142
leyendo '142 ms'
  '142 ms' no es un número entero
  (fin de la conversión)
  resultado: None
```

There are four blocks, and each one has a clear rule:

- **`try:`** contains **only** the line that can fail, here `tiempo_ms = int(texto)`. If there is no error, the program continues to the `else` block. If there is one, Python abandons the `try` on that very line and jumps to the matching `except`.
- **`except ValueError:`** contains what is done if the error was of that type. In this case, warn that the text is not a number and return `None` (the value that in this course means “there is no data”). Between the `except` and the colon goes the **exception type** that is caught; any other type would pass by.
- **`else:`** (in this context, “if there was no error”) runs **only if the `try` finished without an exception**. Here it holds what is done when the conversion worked.
- **`finally:`** runs **always**: whether there was an error or not, whether you returned a value or not. It is used for cleaning up, for example closing something that was opened.

Look at the output, because it contains a surprise worth seeing once. With the text “142,” it first prints “se convirtió en 142” (“it was converted to 142,” from the `else`) and **afterwards** “(fin de la conversión)” (“end of the conversion,” from the `finally`), even though the `return tiempo_ms` of the `else` appears earlier in the code. With “142 ms,” the `except` prints its warning, returns `None`, and the `finally` runs **all the same** before the function ends. That is: `finally` runs even when the block has already decided to leave with `return`. That guarantee is the reason it exists.

Two reasonable questions remain: why an `else`, if the `print` and the `return` could go inside the `try`? Because **a `try` must be as small as possible**. Everything you put inside is protected by the `except`, and if on that extra line an error of the same type that you did not expect occurs, the `except` would swallow it and you would believe it was the error you did expect. The rule is: in the `try` goes **what can fail in the way you know how to handle**, and nothing else. What must happen if everything went well goes in the `else`.

The second question: can several types be caught? Yes, in two ways. One is to put several `except` blocks one after another, each with its type and its response. The other is to put the types together **in parentheses**, separated by commas: `except (ValueError, TypeError):`, when the response is the same. Always write the parentheses: in Python 3.12 they are mandatory, and although Python 3.14 allows omitting them when the `except` has no `as` ([PEP 758](https://peps.python.org/pep-0758/)), the course code runs on both versions.

#### 6.1.3 Catch the specific exception, never “any”

This is the most important rule of the section, and it is better understood by seeing what happens when it is broken. Look at `fig06_03.py`. It is the same function, but with two changes: the `except` says `Exception` instead of `ValueError`, and someone misspelled a name inside the `try` (`stirp` instead of `strip`, the method that removes spaces at the ends of a text):

```python
# fig06_03.py
def leer_tiempo(texto: str) -> int | None:
    try:
        return int(texto.stirp())
    except Exception:  # noqa: BLE001
        print(f"'{texto}' no es un número entero")
        return None


def main() -> None:
    print(leer_tiempo("142"))


if __name__ == "__main__":
    main()
```

```text
$ python fig06_03.py
'142' no es un número entero
None
```

Look at what happened: the text “142” is a perfectly valid number, and the program said it **is not**. The function has nothing to do with numbers: it has a spelling mistake. Without the `try`, Python would have stopped the program with `AttributeError: 'str' object has no attribute 'stirp'. Did you mean: 'strip'?` (“a text has no attribute `stirp`; did you mean `strip`?”), and you would have fixed the typo in a minute. With an `except` that is too wide, that warning turned into a lie that is printed on the screen, and the real error stays buried until someone asks why no time is read correctly.

To understand it you have to know that exceptions form a family. At the top is `BaseException`; below it, `Exception`, from which almost all the errors you will meet hang; and from there come the specific types, some with relatives. `ValueError` is one. `KeyError` and `IndexError` (which you saw in Lesson 4) are children of `LookupError`. `FileNotFoundError` is a particular case of `OSError`, the exception for problems with the operating system. `UnicodeDecodeError`, which you will see further down, is a kind of `ValueError`. The full tree is in the [list of exceptions in the documentation](https://docs.python.org/3/library/exceptions.html). Catching an exception catches **also all its children**: that is why `except Exception` catches almost everything, including the `AttributeError` from the typo, and why `except ValueError` also catches TOML and JSON reading errors, as you will see in 6.3.

And there is the worst version: the `except:` **without a type**, called “bare.” That one catches even what is above `Exception`, including the `KeyboardInterrupt` that Python raises when you press `Ctrl`+`C` to stop a program. A program with a bare `except:` may not die when you ask it to. The [PEP 8 style guide](https://peps.python.org/pep-0008/#programming-recommendations) asks to name the specific exceptions whenever possible instead of using it, and to reserve it for rare cases; in this course the rule is stricter and has no exceptions: never.

The rules, then, are three. **First:** catch the specific type you know how to handle, with the specific response that makes sense. **Second:** if you do not know what to do with an error, **do not catch it**: let it go up, let the program stop with its report, and someone will see it. A program that stops with a clear report is better than one that keeps working with wrong data. **Third:** if you truly need to catch `Exception` (for example, in the last line of defense of a program that must not fall over), do it in a single place, record what happened and do not let it pass in silence. The comment `# noqa: BLE001` that you see in `fig06_03.py` is a mark for `ruff`, the tool that checks the style of the code and that you will meet in [Lesson 8](08-pruebas-tipos-calidad.md): it tells it “I know this line catches an exception that is too wide, it is on purpose.” The `ruff` rule that complains is called precisely “catching a blind exception.”

#### 6.1.4 A custom exception and `raise ... from`

Until now you caught exceptions that Python already ships. For the `revisor` one more is needed, because you need to tell apart **“the configuration file has a problem”** from **“my program has a bug”**. The two situations deserve different responses: the first is explained to the person who wrote the file; the second is a defect that must stop the program with its report, so that a programmer fixes it. If everything were raised as `ValueError`, the program could not tell one from the other.

The solution is an exception with a name of its own, defined with one line of **inheritance**. Look at `fig06_04.py`:

```python
# fig06_04.py
class ErrorDeConfiguracion(Exception):
    """La configuración no se puede usar."""


def leer_timeout_ms(texto: str) -> int:
    try:
        return int(texto)
    except ValueError as error:
        mensaje = f"'timeout_ms' debe ser un entero, llegó '{texto}'"
        raise ErrorDeConfiguracion(mensaje) from error


def main() -> None:
    try:
        timeout_ms = leer_timeout_ms("cinco mil")
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        print(f"causa original: {error.__cause__}")
    else:
        print(f"timeout_ms = {timeout_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_04.py
error de configuración: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
causa original: invalid literal for int() with base 10: 'cinco mil'
```

The first statement is new in form, although you already saw `class` in Lesson 5 as a “data mold”: `class ErrorDeConfiguracion(Exception):` defines a new mold called `ErrorDeConfiguracion`, and the parenthesis says it **inherits** from `Exception`. Inheriting means “it is an `Exception` and also has its own name”: everything Python knows how to do with any exception (raise it, catch it, print its message, show its report) it knows how to do with yours, without writing anything else. It is a single level of inheritance, and it is all you need; the course does not go further. The text between triple quotation marks inside the class is a **documentation string** (*docstring*): a sentence that explains what it is for, and that Python keeps for whoever wants to look it up. No other statement is needed inside the class.

The function `leer_timeout_ms` does something you will repeat throughout the course: it catches a low-level error (`ValueError`, from `int`) and **translates** it into one from the program's domain (`ErrorDeConfiguracion`), with a message that speaks in the terms of whoever wrote the configuration: “'timeout_ms' debe ser un entero, llegó 'cinco mil'” (“'timeout_ms' must be an integer, 'cinco mil' arrived”). The message from `int` (“invalid literal for int()…”) is useful for a programmer, but not for someone editing a configuration file. The `raise` statement raises the exception, and the tail `from error` does something important: it **keeps the original error as the cause**. That cause stays stored inside the new exception, in `error.__cause__` (the two underscores before and after are the way Python marks names it reserves for itself). The second line of the output shows it: the program printed its warning in Spanish and, separately, the original cause in English, in case it is needed.

What happens if nobody catches the exception? Look at `fig06_05.py`, which is the same program without the `try` in `main`:

```text
$ python fig06_05.py
Traceback (most recent call last):
  File "fig06_05.py", line 8, in leer_timeout_ms
    return int(texto)
ValueError: invalid literal for int() with base 10: 'cinco mil'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "fig06_05.py", line 20, in <module>
    main()
    ~~~~^^
  File "fig06_05.py", line 15, in main
    timeout_ms = leer_timeout_ms("cinco mil")
  File "fig06_05.py", line 11, in leer_timeout_ms
    raise ErrorDeConfiguracion(mensaje) from error
ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
```

This report has **two** parts separated by a sentence: “The above exception was the direct cause of the following exception.” It is the trace of `from error`. It is read the same way as before, from the bottom up: the last line, `ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'`, is what reached the top. But now, in addition, Python **keeps the history**: above it is the original `ValueError`, with its exact line (`return int(texto)`). If you had not written `from error`, the report would say instead “During handling of the above exception, another exception occurred,” which suggests a new error that happened inside the handling of another. Python would still show both exceptions (the original is stored as the *context*, in the `__context__` attribute), but the report would no longer say that one was a **consequence** of the other: it would say the second happened “meanwhile,” as if it were a separate accident. With `from`, the original is recorded as the **cause** (`__cause__`), which is what really happened. The rule: **when you translate an exception, always write `from`**. Whoever debugs your program will thank you. The explanation of the technique is in [PEP 3134](https://peps.python.org/pep-3134/) and in the [section on chaining exceptions](https://docs.python.org/3/tutorial/errors.html#exception-chaining) of the tutorial.

With this you have the vocabulary of exceptions. What is missing is a place to use it, and that is next: reading files, where things fail for reasons you do not control.

### 6.2 Files

#### 6.2.1 Open, read, close: `with`

A file on the disk is not simply “read”: first it is **opened**, which asks the operating system for access to it; its content is read; and at the end it is **closed**, which gives the access back. A file that is opened and not closed consumes system resources (each program can have only a limited number open) and, if you were writing, it can leave the last part unsaved. The most careful way to write it, with what you already know about `try`, would be this:

```python
archivo = open("nota.txt", encoding="utf-8")
try:
    texto = archivo.read()
finally:
    archivo.close()
```

It works, and the `finally` guarantees the closing even if `read()` fails. But it is a lot of ritual for something so frequent, and it is easy to forget the `finally`. Python offers the `with` statement, which does exactly that for you. Look at `fig06_06/leer.py` and the `nota.txt` file it reads:

```text fig06_06/nota.txt
Revisión de las 9:00
reportes: sin conexión
```

```python
# fig06_06/leer.py
with open("nota.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
    print(f"dentro del with: cerrado = {archivo.closed}")

print(f"fuera del with: cerrado = {archivo.closed}")
print(texto.splitlines())
```

```text
$ cd fig06_06
$ python leer.py
dentro del with: cerrado = False
fuera del with: cerrado = True
['Revisión de las 9:00', 'reportes: sin conexión']
```

`open("nota.txt", encoding="utf-8")` opens the file and returns an object that represents that opening. `with ... as archivo:` says “while this block lasts, the file is called `archivo`; when you leave the block, close it, no matter what.” The output proves it: inside the `with`, `archivo.closed` (the question “is it closed?”) says `False`; as soon as the block ends, it says `True`, and nobody wrote a `close()`. If the block ends because of an exception, the file is also closed: the `with` is, in effect, a `try`/`finally` written in abbreviated form. The [reference for the `with` statement](https://docs.python.org/3/reference/compound_stmts.html#with) explains the full mechanism; for this course the rule is enough: **every file you open, open it with `with`**.

`archivo.read()` returns the complete content as a single text. In the program, `texto.splitlines()` is printed, a text method that splits it into a list with one string per line, and that removes the line breaks; that way you see at a glance that the file has two lines. Notice also `encoding="utf-8"`: it is a part of `open` that is not decoration, and its reason is explained in 6.2.3.

#### 6.2.2 `pathlib.Path`: a path as a value, not as text

The file name, `"nota.txt"`, is a **path**: the address of a file inside the disk. Until now we wrote it as a text, and for a single file in the current folder there is no problem. But paths have rules of their own: on Linux and macOS folders are separated with `/`, on Windows with `\`; a path can be **absolute** (it starts at the root of the disk, like `/home/ana/curso-python/revisor/servicios.toml`) or **relative** (it is counted from the folder where you are, like `servicios.toml`). Manipulating paths as texts, with additions and trimmings, breaks as soon as any of those rules changes.

For that, the `pathlib` module of the standard library offers the `Path` class: a value that **knows what a path is**. You build one with `Path("nota.txt")` and from then on it has operations of its own, invoked with a dot, just like the methods of lists and dictionaries you already know. Look at `fig06_07/ruta.py`, which uses the same `nota.txt`:

```python
# fig06_07/ruta.py
from pathlib import Path

ruta = Path("nota.txt")
print(ruta.name, ruta.suffix, ruta.exists())
print(Path("no-esta.txt").exists())

otra = Path("datos") / "servicios.toml"
print(otra)

texto = ruta.read_text(encoding="utf-8")
print(texto.splitlines())
```

```text
$ cd fig06_07
$ python ruta.py
nota.txt .txt True
False
datos/servicios.toml
['Revisión de las 9:00', 'reportes: sin conexión']
```

Line by line:

- `Path("nota.txt")` creates the path. It does not touch the disk yet: it only describes an address, whether or not the file exists.
- `ruta.name` is the name of the file (`nota.txt`), `ruta.suffix` is its ending with the dot (`.txt`), and `ruta.exists()` asks the disk whether it exists (`True`). The second line asks the same question about a file that is not there, and answers `False`: **asking whether a file that is not there exists raises no exception at all**. (A version nuance: in 3.12, if the question runs into another system problem, such as not having permission to look at the folder, `exists()` can still raise an `OSError`; since 3.14 it [answers `False` in all those cases](https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists).)
- `Path("datos") / "servicios.toml"` uses the `/` operator with a new meaning: **joining** two parts of a path with the separator that the system calls for. The result is printed as `datos/servicios.toml` and does not touch the disk. It is much safer than adding texts.
- `ruta.read_text(encoding="utf-8")` opens the file, reads everything, closes it and returns the text, in a single call. It is the form we will use in the `revisor` because it leaves nothing open. The [`pathlib` documentation](https://docs.python.org/3/library/pathlib.html) lists everything else a path can do (list folders, create files); in this course only what you see here is needed.

There is a practical consequence of relative paths being “counted from where you are”: the same program, with the same `Path("nota.txt")`, works or not depending on the folder you run it from. What happens when the file does not exist? Look at `fig06_08.py`, which tries to open a file that is not there:

```python
# fig06_08.py
with open("no-esta.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
print(texto)
```

```text
$ python fig06_08.py
Traceback (most recent call last):
  File "fig06_08.py", line 2, in <module>
    with open("no-esta.txt", encoding="utf-8") as archivo:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'
```

`FileNotFoundError` (“file not found”) is raised, a specific exception that you can catch. The text of the message, `[Errno 2] No such file or directory`, comes from the operating system and is in English: you do not control it, and that is why you will not show it to whoever uses the `revisor`. In 6.4 the program will catch this exception and translate it into a message of its own.

#### 6.2.3 Text and bytes: why always `encoding="utf-8"`

A file on the disk does not store letters: it stores **bytes**, numbers from 0 to 255. For those numbers to be text, someone has to decide which number corresponds to which letter. That decision is the **encoding**, and there are many. The one that dominates today is **UTF-8**: it can represent any character of any language, and letters without an accent take a single byte. Characters with an accent, like the “ó” of “conexión,” take two. An old encoding, `latin-1`, represents the “ó” with a single byte, but it only works for a few European languages. Seeing it is clearer than explaining it. Run `fig06_09.py`, which builds the bytes of the same text in the two encodings:

```python
# fig06_09.py
texto = "sin conexión"

en_utf8 = texto.encode("utf-8")
en_latin1 = texto.encode("latin-1")

print(en_utf8)
print(en_latin1)
print(len(texto), len(en_utf8), len(en_latin1))
print(en_utf8.decode("utf-8"))
```

```text
$ python fig06_09.py
b'sin conexi\xc3\xb3n'
b'sin conexi\xf3n'
12 13 12
sin conexión
```

`texto.encode("utf-8")` converts a text into bytes with that encoding; the bytes are printed with a `b` in front (`b'sin conexi\xc3\xb3n'`), and `\xc3\xb3` are the two bytes (in hexadecimal) that UTF-8 uses for the “ó.” With `latin-1` the “ó” is a single byte, `\xf3`. The third line confirms it with a count: the text has 12 characters; in UTF-8 that is 13 bytes and in `latin-1`, 12. And `bytes.decode("utf-8")` does the reverse path: from bytes to text. With the UTF-8 bytes it comes back as “sin conexión.”

Now the problem. What happens if the bytes were written in one encoding and are read with another? Run `fig06_10.py`, which tries to read the `latin-1` bytes as UTF-8. The `b` before the quotation marks marks a **bytes** literal, and `\xf3` writes the byte whose value, in hexadecimal (the base-16 numbering system in which bytes are usually written), is `f3`, that is, 243:

```python
# fig06_10.py
en_latin1 = b"sin conexi\xf3n"

print(en_latin1.decode("utf-8"))
```

```text
$ python fig06_10.py
Traceback (most recent call last):
  File "fig06_10.py", line 4, in <module>
    print(en_latin1.decode("utf-8"))
          ~~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10: invalid continuation byte
```

The last line says: “the `utf-8` codec cannot decode byte `0xf3` in position 10: invalid continuation.” The byte `0xf3` is the one for the “ó” in `latin-1`, but in UTF-8 that value means “here begins a four-byte character” and the next byte does not have the form that a continuation requires. Python, correctly, refuses to guess. It is a `UnicodeDecodeError`, which is a kind of `ValueError`.

This explains why `encoding="utf-8"` is written **always**: when you do not write it, Python chooses the encoding according to the configuration of the system where it runs, according to [the documentation of `open`](https://docs.python.org/3/library/functions.html#open). The same program can read a file correctly on your computer and fail on a colleague's, because the configuration is different. If you write it, the program behaves the same everywhere. And it is not a whim: the two formats you will use next require UTF-8. The [TOML specification](https://toml.io/en/v1.0.0) says that a TOML document is a valid Unicode text in UTF-8, and [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) establishes that JSON exchanged between systems, outside closed ecosystems, must use UTF-8. If you want to understand the underlying topic better, the [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) in the documentation tells it step by step.

> **The first session ends here.** Up to this point you have concepts 6.1 and 6.2: exceptions and files. Before the second session, run the figures `fig06_01.py` to `fig06_10.py` and change something in each one: another text instead of “142 ms,” a different `except`, another file name. Provoking the error yourself fixes it in memory better than reading it. The next session starts with the formats.

### 6.3 Formats: TOML and JSON

#### 6.3.1 What a format is and why there are two

A text file with loose lines is not enough to describe a list of services, each with a name, an address and perhaps a timeout. A **format** is needed: a set of rules that says how each thing is written, so that any program can read it without ambiguity. The two most used formats in Python and in the rest of the world for structured data are **TOML** and **JSON**, and they serve different functions:

- **TOML** is designed so that **a person writes and reads it**: it allows comments with `#`, does not demand braces or commas everywhere, and is hard to write ambiguously. It is the format of configuration files, and it is the one Python already uses for project configuration (you will see it in Lesson 7, in `pyproject.toml`). The `revisor` will read its list of services from a TOML file.
- **JSON** is designed so that **two programs pass data to each other**. It admits no comments and demands braces, quotation marks and commas, but almost all languages know how to read and write it. It is the format of the responses of almost any web service, and the one the `revisor` will use to hand its report to other programs.

Python's standard library ships a module for each: `tomllib` (to read TOML) and `json` (to read and write JSON). There is an asymmetry worth knowing: `tomllib` only **reads**. To write TOML you have to install an external library, and this course does not need it because it never writes configuration, it only reads it.

#### 6.3.2 Reading TOML with `tomllib`

A TOML is a series of `key = value` lines, with values of a few types: text in double quotation marks, integers and decimals, `true` and `false`, and lists. It also has **tables**, which group keys under a name in square brackets. What interests us is a particular case: a list of tables, or *array of tables*, written with **double square brackets**, `[[servicios]]`, where each time the heading appears a new element of the list starts. It is the natural way to write “a list of services, each with its fields.” The [TOML specification](https://toml.io/en/v1.0.0#array-of-tables) has the exact definition; with an example it is understood faster. Look at `fig06_11.py`, which reads a TOML written inside the program itself:

```python
# fig06_11.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
"""

datos = tomllib.loads(TEXTO)
print(datos)

segundo = datos["servicios"][1]
print(segundo["nombre"], segundo["timeout_ms"], type(segundo["timeout_ms"]))
print(segundo.get("proxy"))
```

```text
$ python fig06_11.py
{'servicios': [{'nombre': 'catalogo', 'url': 'https://catalogo.example'}, {'nombre': 'notificaciones', 'url': 'https://notificaciones.example', 'timeout_ms': 1000}]}
notificaciones 1000 <class 'int'>
None
```

Two reading details before the result. The text goes between **triple quotation marks** (`"""`...`"""`), which in Python are used to write a multi-line text with the line breaks included. And `tomllib.loads(TEXTO)` is the function that reads: the name comes from *load string* (“load from a text”), and it returns a **dictionary**, a structure you already know. (There is also `tomllib.load`, which reads from a file opened in binary mode; in the `revisor` we will read the text ourselves with `read_text` to control the encoding and the errors.)

Look at how the dictionary turned out. There is a single key, `'servicios'`, whose value is a **list with two dictionaries**: one for each `[[servicios]]`. The second dictionary has one more key, `timeout_ms`, and its value is the number `1000`: the third line of the output confirms that it is an `int`. That is how any piece of data from a TOML is read: `datos["servicios"]` is the list, `datos["servicios"][1]` is the second service, `datos["servicios"][1]["nombre"]` is its name. And the last line of the output shows something we will use a lot: `segundo.get("proxy")` asks for a key that **does not exist** and returns `None`, whereas `segundo["proxy"]` would have raised a `KeyError`. For data that is optional (like `timeout_ms`), `.get` is the tool.

And what if the TOML is badly written? Look at `fig06_12.py`, where the name line is missing its closing quotation mark:

```python
# fig06_12.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo
url = "https://catalogo.example"
"""

try:
    tomllib.loads(TEXTO)
except tomllib.TOMLDecodeError as error:
    print(f"TOML inválido: {error}")
```

```text
$ python fig06_12.py
TOML inválido: Illegal character '\n' (at line 3, column 19)
```

`tomllib.TOMLDecodeError` is the exception for an invalid TOML. Its message, `Illegal character '\n' (at line 3, column 19)`, says “illegal character, a line break, at line 3, column 19”: the text started with a quotation mark and found the end of the line without it being closed. Notice that the message takes you to the exact spot, and that the module itself says it. In the `revisor` we will include that message as it is in the configuration error. The functions and exceptions of this module are in the [`tomllib` documentation](https://docs.python.org/3/library/tomllib.html); the module entered the standard library in Python 3.11 with [PEP 680](https://peps.python.org/pep-0680/).

#### 6.3.3 Reading and writing JSON with `json`

JSON has stricter rules and a smaller vocabulary. A JSON object is written between braces, with `"key": value` pairs; a list, between square brackets; texts, between double quotation marks (**always double**); numbers, without quotation marks; and there are three words: `true`, `false` and `null`. Python has an equivalent for each piece, and the `json` module converts from one to the other:

| JSON | Python |
|---|---|
| object `{...}` | `dict` |
| array `[...]` | `list` |
| text `"..."` | `str` |
| integer number | `int` |
| number with decimals | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

The strict rules are those of the standard; Python's `json` module, by default, is a little more permissive, and [its documentation](https://docs.python.org/3/library/json.html) says so openly: it accepts and writes `NaN`, `Infinity` and `-Infinity` (the “not a number” and “infinity” of `float`s), which the standard does not admit, and if an object repeats a key it keeps the last value. For the `revisor` it does not matter, because its numbers are integers; if you ever need a JSON that any other program accepts, `json.dumps(..., allow_nan=False)` refuses to write those values.

The conversion from Python to JSON (**serializing**) is done with `json.dumps` (“*dump string*”: dump to text), and the reverse (**deserializing**) with `json.loads`. Look at `fig06_13.py`, which uses a `revisor` result as an example:

```python
# fig06_13.py
import json

resultado = {
    "nombre": "reportes",
    "estado": "CAIDO",
    "tiempo_ms": None,
    "detalle": "sin conexión",
    "activo": True,
}

texto = json.dumps(resultado, ensure_ascii=False, indent=2)
print(texto)

de_vuelta = json.loads(texto)
print(de_vuelta["tiempo_ms"] is None, de_vuelta == resultado)

print(json.dumps(resultado["detalle"]))
print(json.dumps(resultado["detalle"], ensure_ascii=False))
```

```text
$ python fig06_13.py
{
  "nombre": "reportes",
  "estado": "CAIDO",
  "tiempo_ms": null,
  "detalle": "sin conexión",
  "activo": true
}
True True
"sin conexi\u00f3n"
"sin conexión"
```

Four things to learn from this output. One: `None` became `null` and `True` became `true`; JSON is not Python, and each language has its own spelling of “nothing” and “true.” Two: `indent=2` makes `dumps` write the result on several lines with two spaces of indentation, readable for a person; without it, everything would come out on a single compact line. Three: the check `de_vuelta == resultado` gives `True`, because `loads` rebuilds the original dictionary, and `de_vuelta["tiempo_ms"] is None` too, because `null` comes back as `None`. And four, the finest: the last two lines print the same text, “sin conexión,” in two ways. By default, `dumps` **escapes** every character that is not ASCII and writes `"sin conexi\u00f3n"`, which is valid JSON but unreadable for a person. With `ensure_ascii=False` it writes the “ó” as it is. Since the `revisor` writes in Spanish, the JSON report will always carry `ensure_ascii=False`. That is the form the course fixes for the whole report: `json.dumps(datos, ensure_ascii=False, indent=2)`.

A warning that is better learned the hard way. `json.dumps` only understands the types in the table above (and the tuple, which it writes as an array, just like a list). The `revisor`'s data is in objects of its own, `Resultado`, `Servicio` and `Estado`, and if you try `json.dumps(Estado.CAIDO)` you get `TypeError: Object of type Estado is not JSON serializable` (“an object of type `Estado` cannot be serialized to JSON”). The solution is to first build a dictionary with simple types, using `estado.value` to take the text out of the `Enum`, and serialize that dictionary. It is what the `reporte_a_json` function will do later.

And like TOML, JSON also fails. Look at `fig06_14.py`, where a comma is missing between two pairs:

```python
# fig06_14.py
import json

TEXTO = """{
  "nombre": "pagos",
  "tiempo_ms": 87
  "estado": "ARRIBA"
}"""

try:
    json.loads(TEXTO)
except json.JSONDecodeError as error:
    print(f"mensaje: {error.msg}")
    print(f"línea {error.lineno}, columna {error.colno}")
    print(f"completo: {error}")
```

```text
$ python fig06_14.py
mensaje: Expecting ',' delimiter
línea 4, columna 3
completo: Expecting ',' delimiter: line 4 column 3 (char 43)
```

`json.JSONDecodeError` keeps the problem in three useful attributes: `msg` (“expecting ',' delimiter”), `lineno` (the line) and `colno` (the column). Here line 4, column 3: after the `87` of the previous line a comma should have gone, and the decoder missed it right at the start of the next pair. The full message, which you get by printing the error, also carries `char 43`, the position counting from the beginning. The [`json` documentation](https://docs.python.org/3/library/json.html) describes all the parameters of `dumps` and `loads`, and [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) is the specification of the format. That `JSONDecodeError` is also a `ValueError` tells you something you already know from 6.1.3: an `except ValueError` would catch it, along with many other errors that have nothing to do with it. It is always better to name the specific type.

### 6.4 Validating what arrives from outside

#### 6.4.1 Why you have to validate, and where

A file can be well written and still be useless. This TOML is perfectly valid:

```toml
[[servicios]]
nombre = 42
url = "ftp://archivos.example"
timeout_ms = -3
```

Each line follows the rules of TOML. But the name is a number, the address is not a web page's, and the timeout is negative. If the program accepts it without looking, the error will appear later, far from its cause, on a line that has nothing to do with the file: a `TypeError` when trying to align a name, or a request that never goes out. **Validating** is checking, at the moment the data enters, that it has the shape and the meaning the program expects.

There is a reason specific to Python for doing it by hand. In [Lesson 0](00-que-es-python.md) you saw that type annotations (`nombre: str`) **are not enforced at run time**: they are a note for you and for the tools, not a lock. A `Servicio(nombre=42, ...)` is created without complaint. That is why the boundary of the program, the point where what comes from outside enters, is the place where types are really checked. Once validated, the rest of the program can trust them without looking again. That idea, **validate at the boundary and trust inside**, organizes the whole `revisor`: a single module, `configuracion.py`, is in charge of distrusting the outside.

The underlying rule is the one formulated by the [OWASP input validation guide](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): what arrives from outside is not trusted until it has been verified, and the verification that works best is an **allow list**: you enumerate what is valid and reject everything else, instead of trying to enumerate everything that is wrong.

#### 6.4.2 `isinstance` and the `bool` trap

To ask “is this value of this type?” there is `isinstance(valor, tipo)`, a function that returns `True` or `False`. `isinstance(5000, int)` is `True`; `isinstance("5000", int)` is `False`, because the text “5000” is not an integer even if it looks like one. With it you can write the validation of the timeout: “it has to be an integer greater than zero.” And here there is a trap that deserves its own figure. Look at `fig06_15.py`:

```python
# fig06_15.py
print(isinstance(True, int))
print(isinstance(True, bool))
print(True + True)


def timeout_valido(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


for valor in [5000, 0, -1, True, "5000", 2.5]:
    print(valor, type(valor), timeout_valido(valor))
```

```text
$ python fig06_15.py
True
True
2
5000 <class 'int'> True
0 <class 'int'> False
-1 <class 'int'> False
True <class 'bool'> False
5000 <class 'str'> False
2.5 <class 'float'> False
```

The first three lines are the trap. `isinstance(True, int)` is **`True`**: in Python, a `bool` is a kind of integer. `True` is literally the number 1, and `False` is 0, and that is why `True + True` gives `2`. It is not an accident: it is an old design decision of the language, described in the [documentation of the built-in types](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool). The consequence, for you, is concrete. A naive validation like `isinstance(timeout_ms, int) and timeout_ms > 0` **accepts `true`** as a timeout, because `true` is a positive integer: it is worth 1. Someone who writes `timeout_ms = true` in the file (an understandable confusion) would get a timeout of one millisecond without anybody complaining.

The program's `timeout_valido` function avoids it: it asks `isinstance(valor, int)` **and also** `not isinstance(valor, bool)`. The last six lines of the output show the result with six values: the integer 5000 passes; 0 and -1 do not pass the `valor > 0` condition; `True` does not pass; the text `"5000"` does not pass (it is a `str`); and the decimal `2.5` does not either (it is a `float`). Notice that the test was done with a **list of representative values**, including the odd cases: that is how a validation is tested, looking at exactly the values that might sneak in.

#### 6.4.3 Addresses: the permitted scheme

Another piece of outside data in the `revisor` is the address (`url`) of each service. An address has parts, and the first is the **scheme**: what goes before the colon, and says which protocol to use (`https`, `http`, `ftp`, `file`...). For a web service checker only two make sense: `http` and `https`. Why does it matter so much? Because later the program will make a request to that address, and with the `urllib` library a `file:///...` address makes the program **read a file from the disk** instead of querying a service, while other schemes would make it talk to another kind of server. A configuration file that another person edited must not be able to achieve that.

The standard library ships `urllib.parse.urlsplit`, which splits an address into its components. Look at `fig06_16.py`, which tests six addresses:

```python
# fig06_16.py
from urllib.parse import urlsplit

DIRECCIONES = [
    "https://catalogo.example",
    "http://127.0.0.1:8099/catalogo",
    "ftp://archivos.example",
    "file:///etc/hosts",
    "catalogo.example",
    "javascript:alert(1)",
]

for direccion in DIRECCIONES:
    esquema = urlsplit(direccion).scheme
    permitida = esquema in {"http", "https"}
    print(f"{direccion:<32} esquema='{esquema}' permitida={permitida}")
```

```text
$ python fig06_16.py
https://catalogo.example         esquema='https' permitida=True
http://127.0.0.1:8099/catalogo   esquema='http' permitida=True
ftp://archivos.example           esquema='ftp' permitida=False
file:///etc/hosts                esquema='file' permitida=False
catalogo.example                 esquema='' permitida=False
javascript:alert(1)              esquema='javascript' permitida=False
```

`urlsplit(direccion).scheme` is the scheme. The validation is a membership question: `esquema in {"http", "https"}`, with the set of what is permitted, as in the allow list we talked about. Look at the cases: the first two addresses pass; `ftp` and `file` do not; `catalogo.example` (without a scheme) has an empty scheme and does not pass; and `javascript:alert(1)` has the scheme `javascript`, which does not either. Note the design choice: a list of forbidden schemes (`ftp`, `file`, `javascript`...) was **not** written, because tomorrow someone invents another and it slips through. The list of the two permitted ones was written. The standard that defines how an address is split is [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), and the functions are in the [`urllib.parse` documentation](https://docs.python.org/3/library/urllib.parse.html).

Looking only at the scheme, however, lets two classes of broken addresses through, and they are worth seeing. The first is an address without a server: a bare `https://`, or `http:catalogo` (without the two slashes), have the right scheme but no server to call. The second is worse: there are addresses that `urlsplit` cannot even split. With `http://[::1` (a bracket that opens and does not close) `urlsplit` returns nothing: it **raises** `ValueError: Invalid IPv6 URL`. And with `http://127.0.0.1:abc/`, the address is split, but when asking for the port (`.port`, the number that goes after the colon) it gives `ValueError: Port could not be cast to integer value as 'abc'`. If the validation does not catch that `ValueError`, a badly written configuration file knocks the program down with a *traceback* instead of the clear message we promised. The [`urllib.parse` documentation](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit) warns about it: `urlsplit` does not validate, and unpaired brackets raise `ValueError`.

There is a third class, more hidden. In TOML, inside a quoted text, `\n` is a line break, so `url = "http://127.0.0.1:8099/cata\nlogo"` reaches Python with a line break in the middle. `urlsplit` **removes it silently** (its documentation says so: it strips line breaks and tabs, as browsers do) and the address looks fine; but the library that will make the request in Lesson 9, `httpx`, does see it and rejects it with an error of its own, which is not a network error. Something similar can happen with non-English letters in the server name, which `httpx` has to convert to a special form and sometimes cannot. The simple defense is to accept nothing in the configuration file that is not ordinary text.

That is why the `revisor` does not ask about the scheme directly, but with a small function that gathers all the questions:

```python
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
```

It is read from top to bottom. The first `if` discards what is not ordinary text, with three text methods: `isascii()` is `True` if all the characters are ASCII (English letters, digits and the signs of a basic keyboard; an `é` is no longer one); `isprintable()` is `True` if none is a control character, such as the line break; and `" " in url` asks whether there is any space. If any of the three fails, the `revisor` does not accept the address. Careful: that does not mean it is invalid on the internet; `https://catálogo.example` is a legitimate address. It is a rule of the `revisor`, stricter than the browsers': in its configuration, a name like that is written in its ASCII form, the one that starts with `xn--`. After that, everything goes inside a `try` because both splitting the address and reading the port can raise `ValueError`, and for this function that error has a single response: the address is no good, `False`. Inside, three conditions joined with `and`: the scheme is one of the two permitted; `partes.hostname`, the server name, exists (in a bare `https://` it is `None`); and the port, if there is one, is a number greater than 0. The three go in parentheses so they can be spread over several lines. A detail of `and` that matters here: it evaluates from left to right and **stops at the first false condition**, so the port is only read if the first two were already met. With this, the six addresses of `fig06_16.py` give the same result as before, and all the broken ones in these paragraphs come out `False`. What this validation does not check is that the server exists or answers: that is only known by querying it, and it is the `revisor`'s job from Lesson 9. Nor does it guarantee that `httpx` accepts everything that passes: `http://999.1.1.1:8099/pagos` has a scheme, a server and a port, but 999 does not fit in an IP address (each part goes from 0 to 255), and `httpx` rejects it. That is why Lesson 9, besides explaining why `file://` is a concrete risk when `urllib` is used, adds a second safety net when querying: an address that `httpx` cannot use comes out in the report as “dirección inválida” (“invalid address”), without knocking down the others.

#### 6.4.4 Why not `eval` or `pickle`

With the vocabulary of this lesson it is now possible to explain something seen in many beginner programs that is a serious risk. Someone thinks: “to read a list of services I do not need a format; I write the list as Python code in a file, and the program runs it.” There is a function that allows it: `eval(texto)`, which takes a text, interprets it **as code** and returns its result. Look at `fig06_17.py`, a demonstration of what is **not** done:

```python
# fig06_17.py
# DEMOSTRACIÓN de lo que NO se hace: eval con un texto que viene de fuera.
print(eval("2300 + 1"))

texto_de_fuera = "print('esto lo escribió otro y se ejecutó')"
eval(texto_de_fuera)
```

```text
$ python fig06_17.py
2301
esto lo escribió otro y se ejecutó
```

The first call looks innocent: `eval("2300 + 1")` calculates and returns `2301`. The second shows the problem: the text that arrived from outside was an **instruction**, and `eval` executed it. Here it was a harmless `print`; it could have been anything Python knows how to do: delete files, read passwords, open a connection to another computer. Whoever controls the text controls the program. The [documentation of `eval`](https://docs.python.org/3/library/functions.html#eval) says it bluntly: it executes arbitrary code, and restricting the functions it can use is not a security mechanism. There is a more careful variant, `ast.literal_eval`, which accepts only literal values (numbers, texts, lists), but the [documentation of the `ast` module](https://docs.python.org/3/library/ast.html#ast.literal_eval) warns that it is not suitable for untrusted input either: a very large or very nested text can exhaust Python's memory or stack.

The other case is `pickle`, the module that saves Python objects to a file and rebuilds them later. It is convenient, because no format has to be put together: the object is saved and recovered. But rebuilding an object can execute code, and that is why the [documentation of `pickle`](https://docs.python.org/3/library/pickle.html) opens with a big warning: **never load data from a source that is not trusted**, because a file made on purpose can execute whatever its author wants on your computer. It is not even shown here how it is done, because this course does not use it. That class of flaw has a name in the catalog of software weaknesses: [CWE-502, deserialization of untrusted data](https://cwe.mitre.org/data/definitions/502.html). The solution is the one you already have: **outside data is read with formats that only describe data**. TOML and JSON describe values, not instructions; however hard someone tries when writing them, `tomllib.loads` and `json.loads` can only return dictionaries, lists, texts, numbers and booleans (plus `None` in JSON, and dates and times in TOML, which `tomllib` returns as values of the `datetime` module). None of those types executes anything. That is why the `revisor` uses them.

That they execute nothing does not mean they cannot do harm in another way. The documentation of [`tomllib`](https://docs.python.org/3/library/tomllib.html) and of [`json`](https://docs.python.org/3/library/json.html) carries the same warning: a text made with bad intent (huge, or nested thousands of levels deep) can make the reading consume a lot of processor and a lot of memory, and they recommend **limiting the size** of what is read. The `revisor` does not do it, and it is a conscious decision: it reads a configuration file written by whoever uses it, of a few hundred bytes. But if a program of yours receives TOML or JSON from others (over the network, from a form), the first thing is to check the size before reading it, for example with `ruta.stat().st_size`, which says how many bytes a file measures, and reject what goes past a reasonable limit.

If you want to continue with the security side of systems that expose services, the Hábil blog has an article on [API security: identity, gateway and tokens](https://www.habil.mx/en/blog/api-security-cto-identity-gateway-tokens/). And if you are interested in seeing how another language solves this same problem of outside data with the same `revisor`, the [TypeScript course](https://www.habil.mx/en/courses/typescript/) has a whole lesson for that.

#### 6.4.5 The project step: the `revisor` reads its configuration

You have all the pieces. What is left is assembling them. The `revisor` of this lesson ends up like this, in your `~/curso-python/revisor/` folder:

```text
revisor/
  servicios.toml      ← NUEVO: los datos, ahora fuera del código
  configuracion.py    ← NUEVO: lee, valida y traduce los errores
  formato.py          ← tiene una función más: reporte_a_json
  revisor.py          ← ya no tiene SERVICIOS escrito a mano
  modelo.py  revision.py   (sin cambios)
```

Start with the data. This is the `servicios.toml` file, with the same four services as always; it is the one that replaces the list you had in the code:

```toml fig06_18/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "inventario"
url = "https://inventario.example"

[[servicios]]
nombre = "pagos"
url = "https://pagos.example"

[[servicios]]
nombre = "reportes"
url = "https://reportes.example"
```

Now the new module, `configuracion.py`. It is the longest of the lesson, but you already know each part. Read it whole once, and then it is taken apart:

```python
# fig06_18/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from modelo import Servicio, nombres_repetidos


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

The `leer_servicios` function receives a path and returns the list of `Servicio`. It goes in four steps, and in each one the rule is the same: **translate into the domain of the configuration every error that can have its cause in the file**.

1. **Read the text.** `ruta.read_text(encoding="utf-8")` is inside a `try` with a single `except`, and it is for `FileNotFoundError`. That is the only reading error that knows how to explain itself well (“the file does not exist”), so it is the only one that is caught. If the file exists but you do not have permission to read it, the error is a `PermissionError`, and **it does not catch it**: the function has nothing useful to say about that, and it is better for the program to stop with the system's report. (Exercise 4 asks you to extend this with another error, the encoding one.)
2. **Interpret the TOML.** `tomllib.loads` goes in its own `try` with its own `except`: if there is a `TOMLDecodeError`, the message from `tomllib` is included in ours. `raise ... from error` is done in both cases, for the reason in 6.1.4.
3. **Check the general shape.** `datos.get("servicios")` looks for the list; if it is not a list, or it is empty, a notice says it is missing. This step protects against a TOML that is valid but is not ours.
4. **Check each service.** A list comprehension (Lesson 4) calls `validar_servicio` for each element, with its position. The `enumerate(lista, start=1)` function, which you saw in Lesson 3, delivers the position of each element along with the element; the `start=1` parameter makes the count start at **1** instead of 0, because “service 2” is how a person speaks. At the end, `nombres_repetidos` (Lesson 5) returns the set of names that appear more than once. If it is not empty (`len(repetidos) > 0`, the same size question you already used with lists), a notice is given; `sorted(repetidos)` puts them in alphabetical order and `", ".join(...)` joins them into a single text separated by commas (`join` is a text method that joins the elements of a list using that text as the separator).

The `validar_servicio` function receives `datos: object`, the most general type there is, on purpose: it **does not know what it is**, because it comes from outside. The first thing is to check with `isinstance(datos, dict)` that it is a dictionary. After that it checks field by field, in this order, and stops at the first problem:

- the `nombre` must exist and be a text that is not empty (`nombre.strip() == ""` catches the text that only has spaces);
- the `url` must exist and pass `es_url_http`: permitted scheme, a server and, if it carries one, a valid port (6.4.3), and it must not carry a user or password (`tiene_credenciales`): an address like `http://usuario:clave@...` carries a secret, and the `revisor` must neither keep it nor repeat it;
- `timeout_ms`, which is optional, is only checked if present (`"timeout_ms" not in datos`; the `in` operator asks whether a key is in the dictionary), and must be an integer greater than 0 that is **not** `bool` (6.4.2).

If everything is fine, it returns a `Servicio`. If there is no `timeout_ms`, it does not pass it: the default value of 5000 is set by the definition of `Servicio`, which comes from Lesson 5. Each error message starts with `servicio N:` so that whoever edits the file knows **which** element to check. The messages the module produces are these, with the position counting from 1 (the messages are in Spanish, as the program prints them, each one followed by a gloss):

| Case | Message |
|---|---|
| the file does not exist | `no existe el archivo servicios.toml` (“the file servicios.toml does not exist”) |
| badly written TOML | `servicios.toml no es TOML válido: <mensaje de tomllib>` (“servicios.toml is not valid TOML: <message from tomllib>”) |
| the list is missing | `falta la lista [[servicios]]` (“the [[servicios]] list is missing”) |
| a field is missing | `servicio 2: falta 'nombre'` (“service 2: 'nombre' is missing”) |
| the service is not a table | `servicio 2: debe ser una tabla` (“service 2: must be a table”) |
| name empty or not a text | `servicio 2: 'nombre' debe ser un texto que no esté vacío` (“service 2: 'nombre' must be a text that is not empty”) |
| url that is not a valid http/https address | `servicio 2: 'url' debe ser una dirección http:// o https:// válida` (“service 2: 'url' must be a valid http:// or https:// address”) |
| url with a user or password | `servicio 2: 'url' no debe llevar usuario ni clave` (“service 2: 'url' must not carry a user or password”) |
| invalid timeout | `servicio 3: 'timeout_ms' debe ser un entero mayor que 0` (“service 3: 'timeout_ms' must be an integer greater than 0”) |
| repeated names | `nombres repetidos: catalogo` (“repeated names: catalogo”) |

The `formato.py` file gained two functions. None of the previous ones changed (`formatear_tiempo`, `encabezado`, `linea`, `contar`, `resumen`); only `import json` and `from urllib.parse import urlsplit, urlunsplit` were added at the top and these two functions at the end:

```python
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

It is the direct application of 6.3.3: a dictionary is built with types JSON understands (hence `r.estado.value` and not `r.estado`), and it is serialized with `ensure_ascii=False, indent=2`. The average comes out as `None` (which JSON writes `null`) when no service answered, because nothing can be averaged. Notice also a repetition that is left on purpose: the counts in `resumen` and those in this dictionary are the same, calculated twice. It was done this way so as not to touch what already works from Lesson 5, but it is the same problem this lesson began with, that of a piece of data calculated in two places: if one day the rule for the average changes, it will have to be changed in both. Note it in your logbook: it is the kind of debt that gets paid the next time the report is touched.

`url_sin_secretos` exists because the report leaves your program: it is saved to a file, pasted into a chat, read by another program. If the address carries a secret in the query (`?token=...`) or something in the fragment (`#...`), the report must not repeat it. `urlsplit` splits the address (6.4.3); `partes.netloc.rpartition("@")[2]` keeps what comes after the last `@`, that is, the server and the port without user or password (`rpartition` splits the text in three at the last occurrence of the separator, and `[2]` is the right-hand part; if there is no `@`, it is the whole text); and `urlunsplit` puts the address back together with the scheme, the server and the path, and with an empty query and fragment. So `http://127.0.0.1:1/estado?token=SECRETO#x` comes out in the report as `http://127.0.0.1:1/estado`. An address with a user or password does not even get here, because `validar_servicio` rejects it on load; removing them here as well is a second net. The address is redacted instead of dropping the field because the JSON is a contract (you will see it after the run): whoever reads it counts on each service carrying its `url`, and without the secrets they still know which server and which path each entry refers to.

The main program is missing. This is how `revisor.py` turns out, which lost the list of services and gained a constant with the file's path:

```python
# fig06_18/revisor.py
from pathlib import Path

from configuracion import ErrorDeConfiguracion, leer_servicios
from formato import encabezado, linea, resumen
from revision import revisar_todos

RUTA_CONFIG = Path("servicios.toml")


def main() -> None:
    try:
        servicios = leer_servicios(RUTA_CONFIG)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        return

    resultados = revisar_todos(servicios)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

`RUTA_CONFIG = Path("servicios.toml")` is a constant (capital letters, like `UMBRAL_LENTO_MS`) with the relative path. In `main`, the call to `leer_servicios` is inside a `try` that catches **only** `ErrorDeConfiguracion`: it is the custom exception from 6.1.4, the only error this program knows how to explain. If it occurs, it prints `error de configuración: ` followed by the message, and `return` ends `main` without going on. Any other error (a `ZeroDivisionError` from a defect, for example) is not caught, and stops with its report so that someone fixes it.

Watch out for one consequence: when it reports a configuration error, the program ends **with exit code 0**, which in the terminal means “all is well.” For a person reading the screen it does not matter; for another program that calls it and only looks at the code, it looks like a success. It is a debt that this lesson leaves knowingly, so as not to mix topics: in [Lesson 7](07-paquete-linea-de-comandos.md) this branch will end with code 2; here it is only printed. Run it:

```text
$ cd fig06_18
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

It is the same report as in Lesson 5, with the same table and the same summary (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`, that is, “4 services · 2 up · 1 slow · 1 down · average 843ms”), but now the four services come from `servicios.toml`. If you add a service to the file, it appears in the table without touching Python (you will see a case in Exercise 1).

To see the report's JSON, the project brings a support script, `ver_json.py`. It is not part of the program: it only joins the reading of the configuration, the check and `reporte_a_json`, so that you see the result before a command-line option exists in Lesson 7 to ask for it:

```python
# fig06_18/ver_json.py
from configuracion import leer_servicios
from formato import reporte_a_json
from revision import revisar_todos
from revisor import RUTA_CONFIG

servicios = leer_servicios(RUTA_CONFIG)
print(reporte_a_json(revisar_todos(servicios)))
```

```text
$ python ver_json.py
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
```

It is the JSON the course fixes for the `revisor`'s report, and it does not change in the lessons that follow: `servicios` is a list with one entry per service, `tiempo_ms` is `null` for the one that did not answer, and `resumen` repeats the counts. Whoever consumes that report from another program can rely on that shape. The only thing the report changes in the address is removing its secrets: the four services in `servicios.toml` carry none, and that is why their `url` comes out the same as in the file.

## The error you will see

The lesson has one main error, the one about the file that is not where you think, and four supporting messages that you have already seen and that are worth knowing how to read at a glance.

**The main error.** Run the `revisor` from the folder **above**, the one that contains `fig06_18`, instead of going into it:

```text
$ python fig06_18/revisor.py
error de configuración: no existe el archivo servicios.toml
```

The program finds the code (you gave it the path), but `RUTA_CONFIG` is **relative**: `Path("servicios.toml")` means “the `servicios.toml` in the folder where I am standing,” not “the one next to the program.” From the folder above, that file does not exist. Notice what the program did right: it did not show an error report or the English `FileNotFoundError` exception with the system's text; it showed the message in Spanish that you wrote, which says what is missing. And it is the same error you will see any day when a script works on your computer and fails on another: nine times out of ten the file exists, but **the folder it is run from is a different one**. To know which folder you are in, the `pwd` command tells you. In Lesson 7, `--config` will let you indicate the path without depending on where you are.

**The four supporting messages**, to be read from the bottom up:

- `ValueError: invalid literal for int() with base 10: '142 ms'`: a text that was to be converted to an integer and is not only digits (`fig06_01.py`). Check what text arrived.
- `FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'`: the path points to nothing. Check the working folder and the spelling (`fig06_08.py`).
- `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10`: the file is not in UTF-8, and the byte that Python mentions says at which position things stopped adding up (`fig06_10.py`).
- `TypeError: Object of type Estado is not JSON serializable`: you tried to serialize an object of your own without converting it to simple types. Build a dictionary with `.value`.

## What gets done wrong

**Writing `except:` without a type, or `except Exception:` just in case.** You already saw the cost in 6.1.3: a spelling mistake disguises itself as another error; and with the bare `except:`, in addition, the program may not stop even with `Ctrl`+`C`. The specific exception, always.

**Swallowing the error in silence.** An `except ValueError: pass` (“do nothing”) makes the program continue with data that does not exist. The `inventario` time is left unread, the report comes out with a wrong row, and nobody knows why. If you catch an exception, **do something with it**: warn, translate, return a defined value. If you do not know what to do, do not catch it.

**A huge `try`.** Putting twenty lines in a `try` to “protect everything” makes the `except` catch errors you did not expect, from lines that have nothing to do with it, just as in `fig06_03.py`. The `try` contains the line that can fail in the way you know, and nothing else.

**Translating an exception without `from`.** The report still shows the original, but no longer as the cause: it reads “during handling of the previous exception, another occurred,” which is worse for whoever debugs. If you swap one error for another, `raise ... from error`.

**Opening files without `with`.** An `archivo = open(...)` without its `close()` leaves the file open if something fails before it is closed, and it is not noticed until the program opens hundreds.

**Omitting `encoding="utf-8"`.** It works on your computer and fails (or, worse, misreads the accents) on another. Always write it.

**Joining paths with `+` or with `"/"` inside a text.** It breaks as soon as the operating system changes or a slash is left over. With `Path` and the `/` operator there is nothing to think about.

**Validating with truthiness.** `if timeout_ms:` lets `True` through and, worse, **rejects `0`** with the same gesture with which it rejects the empty value, without telling the cases apart. Ask exactly what you want to know: `isinstance(timeout_ms, int)` and `timeout_ms > 0`.

**Validating with `assert`.** The `assert condicion` statement fails if the condition is false, and it looks like a convenient way to validate. But Python can run in an optimization mode (`python -O`) in which **all `assert`s are ignored**, according to the [statement's reference](https://docs.python.org/3/reference/simple_stmts.html#assert). A validation that disappears when someone optimizes the program validates nothing. `assert`s are for tests, which you will see in Lesson 8; for outside data, `if` and `raise` are used.

**Passing outside data to `eval` or to `pickle`.** It lets the author of the file decide what your program does. Use TOML or JSON.

## Exercises

### Exercise 1 — Add services without touching the code

Add to your `servicios.toml` the two extra services of the course: `facturacion` (`https://facturacion.example`) and `notificaciones` (`https://notificaciones.example`, with `timeout_ms = 1000`). Since `revisar` still uses simulated data, also add their entry in `SIMULADO` of `revision.py`, as in Exercise 1 of Lesson 5: `facturacion` answers 503 in 95 ms, and `notificaciones` does not answer (`tiempo agotado`, “timed out”). Before running, **predict** the summary: how many services there are, how many up, slow and down, and what the average is. Then run and compare. Do you notice anything odd in the table?

### Exercise 2 — A broken file for each error

Make a copy of your `servicios.toml` called `roto.toml` and, changing `RUTA_CONFIG` to `Path("roto.toml")`, write in it, one by one, files that provoke each of these messages: (a) the `[[servicios]]` list is missing; (b) badly written TOML (forget a quotation mark); (c) a service without `nombre` in the second position; (d) a service with the url `ftp://archivos.example`; (e) `timeout_ms = 0` in the third service; (f) two services with the name `catalogo`. **For each one, first write the message you expect** and afterwards compare it with what the `revisor` prints. Note in the logbook the ones you got wrong.

### Exercise 3 — The `bool` trap, live

Write a `roto.toml` with a single service that has `timeout_ms = true`. Run the `revisor` and note the message. Now **temporarily** change the validation of `timeout_ms` in `configuracion.py` to the naive version (`not isinstance(timeout_ms, int) or timeout_ms <= 0`, without the `bool` part) and run again. What happens? Who warns you? Restore the correct version and explain in your own words why the naive one lets `true` through.

### Exercise 4 — An error that the list does not have

The `revisor` converts `FileNotFoundError` and `TOMLDecodeError` into `ErrorDeConfiguracion`, but not `UnicodeDecodeError`. Provoke it with a `servicios.toml` saved in `latin-1`, another encoding, without losing yours. From the project folder: (1) save a backup copy with `cp servicios.toml servicios-bien.toml` (`cp` copies a file; if the destination already exists, it replaces it without asking, so choose a name you do not use); (2) make another copy, `cp servicios.toml acento.toml`, and in `acento.toml`, right below the `url` of the first service, add the line `descripcion = "catálogo de productos"`; (3) convert that copy to `latin-1` and write it as `servicios.toml`: `iconv -f utf-8 -t latin1 acento.toml > servicios.toml` (`iconv` changes the encoding of a text, and `>` writes its output into the file, **erasing first whatever it had**: hence step 1). Run the `revisor` and read the report from the bottom up. Then extend `leer_servicios` so that this error is also converted into `ErrorDeConfiguracion`, with a message that says what happened, and run the `revisor` again with the same `latin-1` `servicios.toml` to see your message instead of the *traceback*. This message is not in the project's table: it is a practice extension, and the project of the following lessons does not include it. Only at the end, when you have seen your message, restore your configuration with `cp servicios-bien.toml servicios.toml`.

## Solutions

### Solution 1

The two new services in `servicios.toml`, at the end of the file:

```toml
[[servicios]]
nombre = "facturacion"
url = "https://facturacion.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
```

And the two new entries of `SIMULADO` in `revision.py`, after the one for `reportes`:

```python
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
```

**Prediction.** Six services. `catalogo` and `pagos` are still up (2). `inventario` is still slow (1). `reportes` and `notificaciones` did not answer, and `facturacion` answered with 503, which the classification rule (a code greater than or equal to 400) marks as down: that makes 3 down. The average is calculated **only with those that answered**: `catalogo` (142), `inventario` (2300), `pagos` (87) and `facturacion` (95), which answered though with an error; the sum is 2624 and divided by 4 gives 656. Expected result: `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`.

**Result.** When you run `python revisor.py`, it prints:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms
```

The prediction matches the summary. **The odd thing** is in the table: `notificaciones` is 14 letters long, and the name column has a fixed width of 12 (`{nombre:<12}`), so the name invades the next column and sticks to “CAIDO.” `facturacion` fits by a hair: it has 11 letters, and a single space is left. It is not an error of this lesson: the format was written for the four canonical names. [Lesson 11](11-el-programa-terminado.md) solves it by calculating the width from the longest name. What matters in this exercise is something else: you added two services **without changing a line of logic**, which was the goal of the lesson.

### Solution 2

Each broken file and the message it produces. For (b) the file name appears in the message because `leer_servicios` uses the path it receives; if you try it with `servicios.toml`, it will say `servicios.toml`.

(a) A file without the list:

```toml
titulo = "nada"
```

Message: `error de configuración: falta la lista [[servicios]]`

(b) A forgotten closing quotation mark:

```toml
[[servicios]]
nombre = "catalogo
```

Message: `error de configuración: roto.toml no es TOML válido: Illegal character '\n' (at line 2, column 19)`

(c) The second service has no name:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
url = "https://pagos.example"
```

Message: `error de configuración: servicio 2: falta 'nombre'`

(d) An address that is not a web one, in the second service:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "archivos"
url = "ftp://archivos.example"
```

Message: `error de configuración: servicio 2: 'url' debe ser una dirección http:// o https:// válida`

(e) A timeout of zero, in the third service:

```toml
[[servicios]]
nombre = "a"
url = "https://a.example"

[[servicios]]
nombre = "b"
url = "https://b.example"

[[servicios]]
nombre = "c"
url = "https://c.example"
timeout_ms = 0
```

Message: `error de configuración: servicio 3: 'timeout_ms' debe ser un entero mayor que 0`

(f) Two services with the same name:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "catalogo"
url = "https://otro.example"
```

Message: `error de configuración: nombres repetidos: catalogo`

Three details for when you compared. The TOML error (b) is the only one whose text you did not write yourself: it comes from `tomllib` and carries the line and the column. In (a) the list is not half missing: there is nothing, and the message says exactly that. And in (f) the error is detected **after** validating each service separately, because their names are valid one by one; the defect belongs to the whole list. The messages were obtained by running each file with this lesson's module.

### Solution 3

With the correct validation, the message is the usual one: `error de configuración: servicio 1: 'timeout_ms' debe ser un entero mayor que 0`.

With the naive version the `revisor` **does not complain**: it prints its normal table, and the summary comes out without a problem. The `Servicio` ended up with `timeout_ms=True`, and since `True` is the number 1, the timeout the program believes it has is one millisecond. Nobody warns you: it is an error that makes no noise, and it will show up in Lesson 9, when the `revisor` uses that timeout: with a one-millisecond wait, almost any real request would time out, and the service would come out down because of “tiempo agotado” (“timed out”) for no apparent reason. It happens because, in Python, `bool` is a kind of integer (`isinstance(True, int)` is `True`), and the naive validation only asks that. The correct version adds `isinstance(timeout_ms, bool)` to reject booleans explicitly.

### Solution 4

When you run with the file in `latin-1`, the last line of the report is:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 85: invalid continuation byte
```

The byte `0xe1` is the “á” of “catálogo” in `latin-1`; position 85 is where it falls in the file, counting the bytes from 0: it is the one you get if you put the line where the exercise says, and it will be another if you put it somewhere else. The lines above pass through `read_text` and the standard library: the error is born inside the reading, not in your code, and you see it go up through your functions. To convert it, a second `except` is added in the first step of `leer_servicios`:

```python
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error
    except UnicodeDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no está guardado en UTF-8") from error
```

With that, the `revisor` prints `error de configuración: servicios.toml no está guardado en UTF-8` (“configuration error: servicios.toml is not saved in UTF-8”). Notice that `UnicodeDecodeError` is a kind of `ValueError`, but there is no need to catch `ValueError`: with the specific type, a `ValueError` from another cause is not disguised.

## How I know I got it

- [ ] `python fig06_01.py` ends with the `ValueError` report, and you can say which function called which, from the bottom up, without looking at the lesson.
- [ ] `python fig06_03.py` says that “142” is not a number, and you can explain why that is a lie and which line of the program has the real error.
- [ ] In `fig06_05.py` you see the sentence “The above exception was the direct cause of the following exception,” and you know which statement in the code produced it.
- [ ] From `fig06_18/`, `python revisor.py` prints the table of four services with the summary `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] From the folder above, `python fig06_18/revisor.py` prints `error de configuración: no existe el archivo servicios.toml`, and you know how to explain why.
- [ ] The six broken files of Exercise 2 produce the six messages of the table, and you predicted them before running.
- [ ] `python ver_json.py` prints a JSON with `null` in the `tiempo_ms` of `reportes` and with `"promedio_ms": 843`.
- [ ] You can explain why `isinstance(True, int)` is `True` and which validation of the `revisor` takes it into account.
- [ ] You noted in your logbook which error of this lesson was hard for you to read.

## Summary

Answer without looking at the lesson:

1. Which way is an error report read, and what does its last line say?
2. What is the difference between the `else` and the `finally` of a `try`? Which one runs even if there is a `return`?
3. Why is `except:` without a type not written, nor `except Exception:` just in case? What happens to the error you do not know how to handle?
4. What does `raise ... from error` do, and what happens in the report if you omit it?
5. What does a `with` guarantee? Why is `encoding="utf-8"` always written?
6. What does `tomllib.loads` return? What is the difference between `datos["servicios"]` and `datos.get("servicios")` if the key does not exist?
7. Which three things make `json.dumps(x)` and `json.dumps(x, ensure_ascii=False, indent=2)` different? Why does `json.dumps(Estado.CAIDO)` fail?
8. Why is `isinstance(True, int)` `True`? How is the validation of a positive integer that rejects `true` written?
9. Why is the scheme of an address validated with a list of what is permitted and not with one of what is forbidden?
10. What risk does `eval` have with a text that comes from outside, and what format is used instead?

## Further reading

- [Python, “Errors and Exceptions” (official tutorial)](https://docs.python.org/3/tutorial/errors.html): `try`, `except`, `else`, `finally`, custom and chained exceptions, with more examples than this lesson. Accessed on October 7, 2026.
- [Python, `tomllib`](https://docs.python.org/3/library/tomllib.html) and [the TOML specification](https://toml.io/en/v1.0.0): what the module reads and the rules of the format, including tables and lists of tables. Accessed on October 7, 2026.
- [Python, `json`](https://docs.python.org/3/library/json.html) and [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259): the library and the standard of the format. Accessed on October 7, 2026.
- [OWASP, “Input Validation Cheat Sheet”](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): why validation happens at the boundary and why an allow list works better than a deny list. Accessed on October 7, 2026.
