# Lesson 8 — Tests, types, and quality

**Time:** 2 × 90 min (the first session runs to the end of 8.3; the second starts at 8.4)

**What you build:** the `revisor` with 21 tests that run with one command, with its types checked and its style watched over

**What you learn:** `pytest` (`assert`, the test seen red before green, `parametrize`, `tmp_path` and `monkeypatch`), gradual typing with `mypy`, `ruff` to check and format, and reading the count in the report rather than the exit code

**Where you come from.** You bring the package from [Lesson 7](07-paquete-linea-de-comandos.md): the `revisor` lives in `~/curso-python/revisor/` with the `src/` layout, is installed with `pip install -e .` and is run with `python -m revisor`. With the four practice services it prints the table from the syllabus and exits with code 1, because one is slow and one is down. It works. What you do not have is a way to **know that it still works** after touching it: until today the only check was running it and looking at the table, and eyes get tired and do not see what they do not expect to see. This lesson gives you three checkers that do not get tired: one that runs your code with known data and compares the answer, another that reads your code without running it and checks that the data fit together, and another that watches that it is written the way Python is written.

**What this lesson does not do.** It does not touch the network: the `revisor` still reads the simulated data in `SIMULADO`, and querying real services is [Lesson 9](09-http-y-asyncio.md). Nor does it test asynchronous code or simulate the network, which is [Lesson 10](10-concurrencia-pruebas-sin-red.md), nor does it measure how much code each test touches (the *coverage*): it is a useful number and easy to fake, and it is of no use until you know what each test tests.

## By the end you will be able to

- Write a test with `pytest` (a `test_*.py` file, a `test_*` function and an `assert`), run it and read its report from the top down.
- See a test **red before green**, and explain why a test you have never seen fail proves nothing.
- Say how many tests ran by reading the **report**, and explain why the exit code is not enough: a `0` coexists with a test that never ran.
- Turn a table of cases into a single test with `@pytest.mark.parametrize` and tell in the report which row failed.
- Test code that reads files with `tmp_path` and code that depends on another function with `monkeypatch`, knowing **where** to patch.
- Check the package's types with `mypy` in strict mode and read its message, and explain what it means that Python's typing is gradual.
- Check and format the code with `ruff check` and `ruff format`, with all three tools configured in `pyproject.toml`.

## The why before the how

Open `src/revisor/modelo.py` and find, inside `clasificar`, the line that decides when a service is slow: `if tiempo_ms is not None and tiempo_ms >= umbral_ms:`. Imagine that tomorrow, in a hurry, someone “fixes” that `>=` and leaves it as `>`: a single character. Run the `revisor` with the four practice services. **The table comes out identical.** `catalogo` takes 142 ms, `inventario` 2300, `pagos` 87 and `reportes` does not answer; none takes exactly 1000 ms, the only value at which `>=` and `>` behave differently. The defect exists, the program runs without an error and the table looks perfect. The day a real service takes exactly 1000 ms (response times pile up on round numbers more than it seems) it will be “up” when the course's rule says it is already “slow.”

The check you had, looking at the table, **could not** find that defect, because it asks nothing about the cases that matter. What is needed is to write those questions once (“a service that answers 200 in 999 ms, is it up? and one that answers 200 in 1000 ms, is it slow?”) and have a machine repeat them every time you touch the code, in less than a second. That is a **test**: a small program that calls your code with a known input and checks that the answer is the one it should be. A set of tests is a safety net: it lets you change the code calmly, because if you break something you know it at once and you know where.

The lesson brings three tools, each with its question:

| Tool | The question it answers | How it works |
|---|---|---|
| `pytest` | Does the program do what I said, with this data? | **Runs** your code and compares |
| `mypy` | Does the data fit together? Did I pass a text where a number went, or forget that something can be `None`? | **Reads** your code without running it |
| `ruff` | Is it written the way Python is written, without leftover imports or known traps? | **Reads** your code and reformats it |

None replaces the others, and together they are what a team calls a quality gate: the change that does not pass them does not get in. The Hábil blog tells how that discipline looks in a team project, in [tests that catch errors, coverage and quality gates](https://www.habil.mx/en/blog/tests-that-catch-errors-coverage-quality-gate/). The first session uses `pytest` until you have the `revisor`'s 21 tests; the second checks types and style and leaves all three tools set up in the project.

### Prepare the tools

They are installed with `pip` (as in Lesson 1, with `python -m pip`, so that it is the environment's `pip`) inside the course's virtual environment, the same one you activated in [Lesson 1](01-instalacion.md) (the prompt shows `(.venv)`):

```bash
python -m pip install pytest==9.1.1 ruff==0.16.10 mypy==2.4.0
```

The versions are pinned on purpose: the messages of `ruff` and `mypy` change wording between versions, and with the same versions what you see on your screen is what you see here. They are the current ones as of October 7, 2026 on [PyPI](https://pypi.org/project/pytest/), and the same ones are in `herramientas/requisitos.txt` in the course repository. They are **development** tools: the `revisor` does not need them to run, so they do not go into the `dependencies` list of `pyproject.toml`, which stays empty until Lesson 9. Check with `pytest --version`, `ruff --version` and `mypy --version`; if any says “command not found,” the virtual environment is not active, the same stumble as in Lesson 1.

## The concepts

### 8.1 `pytest`: running your code with known data

#### 8.1.1 The first test

[`pytest`](https://docs.pytest.org/en/stable/getting-started.html) is the program that looks for tests, runs them and hands you a report. It does not come with Python: it is a third-party tool, the most used in the language. [Its rules for finding tests](https://docs.pytest.org/en/stable/explanation/goodpractices.html) are few: it looks for files called `test_*.py` or `*_test.py` and, inside them, runs the functions whose name starts with `test`. Everything else it ignores. Keep that rule: further down, ignoring in silence is expensive.

A test prepares an input, calls the code you want to check and ends with an `assert`. Start with the smallest one, on the `formatear_tiempo` function from Lesson 3. So that the example runs on its own, in one file, the function is copied above its tests:

```python
# fig08_01.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def test_menos_de_un_segundo_va_en_milisegundos() -> None:
    assert formatear_tiempo(87) == "87ms"


def test_sin_tiempo_va_una_raya() -> None:
    assert formatear_tiempo(None) == "—"
```

The two functions below are the tests, and they are recognized by the name. Each contains an `assert`, the reserved word that means “I assert that this is true”: [`assert condición`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) does nothing if the condition is true and, if it is false, stops the function with an `AssertionError`. Call and assert: that is all that is needed. Two details of form. The names are sentences that say **what is expected**: `test_sin_tiempo_va_una_raya` (“with no time, a dash goes”) tells you, the day it turns red, what broke without your opening the file. And the `-> None` says the function returns nothing, like every test: it either ends in silence or stops with an error (in 8.4 you will see that `mypy` in strict mode demands it).

This file is not called `test_*.py`, but when you give `pytest` the name of a file, it runs it even if it does not match the pattern. With the environment active:

```text
$ pytest -q fig08_01.py
..                                                                       [100%]
2 passed in 0.00s
```

The `-q` option (*quiet*) asks for a short report. The first line has a dot for each test that passed and, on the right, the progress. The last is the summary: `2 passed`. **That is the line you will learn to read with healthy distrust**: it says how many tests ran and what happened to each.

#### 8.1.2 Seeing it red before green

A test that passes does not say much: it passes if the code is right, but also if the test checks nothing. There is only one way to know whether a test checks anything: **see it fail**. From today on, you see every test red before accepting it green. Here is the defect from the beginning, written inside a file:

```python
# fig08_02.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms > UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"
```

`clasificar` decides the status from the code and the time; this short version returns text. It has the defect: it uses `>` where the rule says “a thousand milliseconds or more.” The two tests are the questions from before. Run it and look at the exit code too:

```text
$ pytest -q fig08_02.py
.F                                                                       [100%]
=================================== FAILURES ===================================
____________________________ test_1000_ms_es_lento _____________________________

    def test_1000_ms_es_lento() -> None:
>       assert clasificar(200, 1000) == "LENTO"
E       AssertionError: assert 'ARRIBA' == 'LENTO'
E         
E         - LENTO
E         + ARRIBA

fig08_02.py:18: AssertionError
=========================== short test summary info ============================
FAILED fig08_02.py::test_1000_ms_es_lento - AssertionError: assert 'ARRIBA' =...
1 failed, 1 passed in 0.01s
$ echo $?
1
```

Read the report from the top down. `.F`: the first test passed and the second failed. The `FAILURES` section brings a block for each failure, with the name of the test, its code and an arrow `>` on the line that failed. The lines with `E` are the error: `assert 'ARRIBA' == 'LENTO'`. This is what is special about `pytest`: it rewrites your `assert`s so that, when they fail, they show **the two values** compared ([the documentation explains it](https://docs.pytest.org/en/stable/how-to/assert.html)); with a bare `assert` you would have seen only `AssertionError`. The lines with `-` and `+` break down the comparison; in this version of `pytest`, the one with `-` is the value on the right of the `==` (`LENTO`, what the test expected) and the one with `+` the one on the left (`ARRIBA`, what the code returned). Then comes the file and the line (`fig08_02.py:18`), a one-line summary per failure, cut to the width of the terminal (hence it ends in `=...`), and the count: `1 failed, 1 passed`.

The `echo $?` prints the **exit code** of the previous command: the number every program leaves when it ends to tell the system how it went. By convention, `0` is “fine” and any other is “something failed.” You used it in Lesson 7 with the `revisor`. Here `pytest` exited with `1` because there were failed tests. Scripts and continuous integration tools read that number to decide whether to go on or stop.

The fix is to change `>` to `>=`:

```python
# fig08_03.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"
```

```text
$ pytest -q fig08_03.py
..                                                                       [100%]
2 passed in 0.00s
$ echo $?
0
```

Two passed, code `0`. Notice the order: first the question (the test for 1000), then the red against the code with the defect, and only then the fix. That order is the guarantee. If you had written it **after** fixing, you would never know whether it was capable of detecting the defect. When you add a test to code that already works, the equivalent is to break the code on purpose for a moment, see the red and undo the change. Exercise 1 does it with the real `revisor`.

#### 8.1.3 The count is read from the report, not from the exit code

Here is the trap that gives its name to one of the course's rules. [The `pytest` documentation](https://docs.pytest.org/en/stable/reference/exit-codes.html) defines its exit codes: `0`, all tests **that were collected** passed; `1`, some failed; `2`, the user interrupted; `3`, internal error; `4`, usage error; `5`, no tests were collected; `6`, the maximum number of warnings was exceeded. Notice the phrase for `0`: “that were collected.” A test that `pytest` never collected does not exist for it. Look at a file where that happens:

```python
# fig08_04.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"


def test_un_503_es_caido() -> None:
    assert clasificar(503, 95) == "CAIDO"


def prueba_sin_respuesta_es_caido() -> None:
    assert clasificar(None, None) == "ARRIBA"
```

There are four test functions and a trap. The last one is called `prueba_sin_respuesta_es_caido`, not `test_...`, and `pytest` **does not see it**. Its `assert` is false on purpose (it asserts that the absence of a response is `"ARRIBA"`), so if it ran it would fail. Run it; then ask `pytest` to only list what it found (`--collect-only`) and to run only the tests whose name contains a text that does not exist (`-k`):

```text
$ pytest -q fig08_04.py
...                                                                      [100%]
3 passed in 0.00s
$ echo $?
0
$ pytest -q --collect-only fig08_04.py
fig08_04.py::test_999_ms_es_arriba
fig08_04.py::test_1000_ms_es_lento
fig08_04.py::test_un_503_es_caido

3 tests collected in 0.00s
$ pytest -q -k nombre_que_no_existe fig08_04.py

3 deselected in 0.00s
$ echo $?
5
```

The first report says `3 passed` and the exit code is `0`: green across the board, with a broken test that nobody ran. A dashboard that only looked at the exit code would say “all fine.” Whoever reads the report sees `3` and, if they wrote four, wonders where the fourth went; `--collect-only` confirms it, because it lists three. It happens in any project: with a badly named function, a file that is not called `test_*.py` or a rename that left a test out. The last command shows the other extreme: `3 deselected` and code `5`, “none collected.” There `pytest` did warn you, but the warning is lost if your script ends with `|| true` or if there is a filter (`| tail`, `| grep`) in the middle that swallows the exit code. Hence the rule:

> **The number of tests is read from the report (“N passed”). A `0` is not evidence that what you thought ran. Always compare N with the N you expect.**

The `revisor` ends this lesson with 21 tests, and that number is the one you will check at the end of each session. Lesson 9 starts from it. If one day the report says 20, it does not matter that it is green: something disappeared. (A test can also be marked as skipped, `skipped`, and then it neither passes nor fails: it only appears in the summary. It is not used in this course; if a test is no good, it is fixed or deleted.)

### 8.2 `parametrize`: a table of cases, a single test

`clasificar` applies four rules and has a boundary (1000 ms) where errors concentrate. To test it well you need **seven cases**: two fast (142 and 999 ms, the slowest that is still up), two slow (1000 ms, the first that already is, and 2300), two down by code (503 and 404) and one with no response (`None`, `None`). Written as separate functions they would be seven functions identical except for two numbers and a text, with seven places to touch the day the rule changes.

What you want is to write the test once and the cases as a table. [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html) does it. The at-sign is a **decorator**: a line above a function that modifies it (you already saw `@dataclass(frozen=True)` in Lesson 5, on a class). Here it tells `pytest` to run the function once for each row:

```python
# fig08_05.py
import pytest

UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, "ARRIBA"),
        (200, 999, "ARRIBA"),
        (200, 1000, "LENTO"),
        (200, 2300, "LENTO"),
        (503, 95, "CAIDO"),
        (404, 50, "CAIDO"),
        (None, None, "CAIDO"),
    ],
)
def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
    assert clasificar(codigo, tiempo_ms) == esperado
```

The first argument is the list of **parameter names**, which must match those of the function below. The second is the list of **cases**: one tuple per case, with one value for each name. The `esperado` (“expected”) goes in the table and is not calculated inside the function: if the test used the same formula as the code it tests, two equal errors would cancel out and it would pass green over a defect. Run it and list what it collected:

```text
$ pytest -q fig08_05.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q --collect-only fig08_05.py
fig08_05.py::test_clasificar[200-142-ARRIBA]
fig08_05.py::test_clasificar[200-999-ARRIBA]
fig08_05.py::test_clasificar[200-1000-LENTO]
fig08_05.py::test_clasificar[200-2300-LENTO]
fig08_05.py::test_clasificar[503-95-CAIDO]
fig08_05.py::test_clasificar[404-50-CAIDO]
fig08_05.py::test_clasificar[None-None-CAIDO]

7 tests collected in 0.00s
```

`7 passed`: `pytest` turned the function into **seven tests**, each with a name that carries the case's values in square brackets (`test_clasificar[200-1000-LENTO]`). That name matters when something fails. See what happens if you put the `>` defect in this table:

```python
# fig08_06.py
import pytest

UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms > UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, "ARRIBA"),
        (200, 999, "ARRIBA"),
        (200, 1000, "LENTO"),
        (200, 2300, "LENTO"),
        (503, 95, "CAIDO"),
        (404, 50, "CAIDO"),
        (None, None, "CAIDO"),
    ],
)
def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
    assert clasificar(codigo, tiempo_ms) == esperado
```

```text
$ pytest -q fig08_06.py
..F....                                                                  [100%]
=================================== FAILURES ===================================
_______________________ test_clasificar[200-1000-LENTO] ________________________

codigo = 200, tiempo_ms = 1000, esperado = 'LENTO'

    @pytest.mark.parametrize(
        ("codigo", "tiempo_ms", "esperado"),
        [
            (200, 142, "ARRIBA"),
            (200, 999, "ARRIBA"),
            (200, 1000, "LENTO"),
            (200, 2300, "LENTO"),
            (503, 95, "CAIDO"),
            (404, 50, "CAIDO"),
            (None, None, "CAIDO"),
        ],
    )
    def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
>       assert clasificar(codigo, tiempo_ms) == esperado
E       AssertionError: assert 'ARRIBA' == 'LENTO'
E         
E         - LENTO
E         + ARRIBA

fig08_06.py:28: AssertionError
=========================== short test summary info ============================
FAILED fig08_06.py::test_clasificar[200-1000-LENTO] - AssertionError: assert ...
1 failed, 6 passed in 0.01s
```

`1 failed, 6 passed`, and the line `..F....` says it was the third row. The name, `test_clasificar[200-1000-LENTO]`, is the exact case; under it, `pytest` prints the values of the parameters of **that** case, and the other six passed: a row that fails does not stop the others. Adding a case is adding a line.

Now the project. The real tests live in a `tests/` folder next to `src/`. The first covers `clasificar` with the seven cases, with the true `Estado`:

```python
# fig08_15/tests/test_modelo.py
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

It compares with `is` and not with `==`: the members of an `Enum` are unique and `is` asks about identity, like the `is None` of Lesson 2. And the parameters carry **type annotations**, like the package's code; in 8.4 you will see why. The second covers `formatear_tiempo` with four cases: no time, one in milliseconds, the last one that still is (999) and one in seconds:

```python
# fig08_15/tests/test_formato.py
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

So that `pytest` knows where to look without your telling it, the `pyproject.toml` gains a section (the complete file is in 8.6):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` is the list of folders where it looks when you run it without arguments. In what follows, the line `cd fig08_15` stands for “being inside the project”; you are already in `~/curso-python/revisor/`, so do not type it.

```text
$ cd fig08_15
$ pytest -q tests/test_modelo.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q tests/test_formato.py
....                                                                     [100%]
4 passed in 0.00s
```

Seven and four: eleven so far. Each report counts what it should; if you add wrong, it will tell you.

### 8.3 `tmp_path` and `monkeypatch`: tests that neither make a mess nor depend on anything

`clasificar` and `formatear_tiempo` are pure functions: they receive values, return a value and touch nothing outside themselves. But `leer_servicios` reads a file, and `main` reads arguments, prints and calls the function that queries the services. Testing that raises two problems, and `pytest` brings a tool for each. Both are *fixtures*.

A **fixture** is a function that `pytest` runs for you before a test to hand it something it needs. You ask for it by declaring it as a **parameter**: if your test is `test_algo(tmp_path)`, `pytest` sees the name, looks for a fixture with that name, runs it and passes the result as an argument. You neither import it nor call it ([the documentation details it](https://docs.pytest.org/en/stable/how-to/fixtures.html)).

#### 8.3.1 `tmp_path`: a new folder for each test

To test that `leer_servicios` reads a file correctly, you need a file. If the tests used your project's `servicios.toml`, any change to that file would break tests that have nothing to do with it, and a test that **writes** would make a mess of your folder. The [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html) fixture hands you a `Path` (the one from `pathlib`, from Lesson 6) that points to a **temporary folder, new and empty, unique to that test**:

```python
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
```

The first test builds a small `servicios.toml` and checks that two services are counted. The second demonstrates the isolation: it receives an **empty** folder, even though the previous one has just written a file in its own. To check it, it uses two things from `pathlib`: `is_dir()` asks whether the path is a folder that exists, and `iterdir()` walks over what is inside it, one element for each file or subfolder. Since `iterdir()` hands over the elements one by one and not a list, `list(...)` gathers them into a list (as you did with `list(tiempos_ms)` in Lesson 4), and the list of an empty folder is `[]`.

```text
$ pytest -q fig08_07.py
..                                                                       [100%]
2 passed in 0.01s
```

The folders live in the system's temporary directory, and `pytest` keeps those of the last three runs in case you want to inspect what a failed test left behind.

With that you write the tests for `leer_servicios`: one that reads a valid file and seven that reject it. Three of the seven protect what you saw in 6.4.3: `url mal formada` (“malformed url”; with `http://[::1`, `urlsplit` raises `ValueError`, and the test demands that it arrive as the configuration message and not as a *traceback*; if you remove the `try` from `es_url_http`, it turns red), `url con salto` (“url with a line break”; a line break inside the address; it turns red if you remove `isprintable()`. In the table you will see `\\n`, with the double backslash: inside a Python string, `\\` writes a backslash, so the TOML file receives `\n`, and TOML turns it into the real line break) and `url con acento` (“url with an accent”; `https://catálogo.example`; it turns red if you remove `isascii()`). The seven share a shape, so they go in a table, with `ids=` so that the report uses readable names:

```python
# fig08_15/tests/test_configuracion.py
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

The valid file is compared with a list that contains one `Servicio`; it works because `dataclass`es compare by content. The rejection ones use `with pytest.raises(ErrorDeConfiguracion) as informe:`, a `with` (the one from Lesson 6) that asserts the opposite of a normal `assert`: that the code inside **raises** that exception. If the block ends without raising anything, `pytest` marks the test as failed with `DID NOT RAISE`. The `as informe` keeps the exception; `str(informe.value)` is the message you wrote in Lesson 6, and the test compares it in full. Checking the message and not just the type distinguishes “it failed for the right reason” from “it failed for any reason.”

#### 8.3.2 `monkeypatch`: changing something only for the length of the test

`main` calls `revisar_todos`, which today reads `SIMULADO` and from Lesson 9 will query the network. To test only what `main` does with the results (which exit code it returns), it is convenient to **replace** that function with a fake one. The [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) fixture exists for that: `monkeypatch.setattr(destino, valor)` replaces an attribute, and **when the test ends it leaves it as it was**. See the mechanism in a small file:

```python
# fig08_08.py
import pytest

UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    return tiempo_ms >= UMBRAL_LENTO_MS


def test_con_el_umbral_normal() -> None:
    assert es_lento(1500)


def test_con_un_umbral_mas_alto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fig08_08.UMBRAL_LENTO_MS", 3000)
    assert not es_lento(1500)


def test_el_umbral_vuelve_a_su_valor() -> None:
    assert UMBRAL_LENTO_MS == 1000
```

There is a module variable, `UMBRAL_LENTO_MS`, and a function that reads it. The first test uses the usual threshold. The second **changes it to 3000 for the length of that test**: `"fig08_08.UMBRAL_LENTO_MS"` is the address of the attribute, in the form `module.name` (this module is named like the file, without the `.py`); inside that test, 1500 is no longer slow. The third checks that afterwards the threshold was 1000 again.

```text
$ pytest -q fig08_08.py
...                                                                      [100%]
3 passed in 0.00s
```

All three passed, and the one that matters is the third: the change **does not stay**. Assigning the variable by hand would leave it changed for the following tests and would produce order-dependent failures, among the hardest to understand.

Now the real test. `main` returns `0` if everything is up and `1` if not. To test both cases without depending on the simulated data, you replace `revisar_todos` with a fake function that returns whatever you decide:

```python
# fig08_15/tests/test_cli.py
from pathlib import Path

import pytest

from revisor.cli import main
from revisor.modelo import Estado, Resultado, Servicio

CONFIGURACION = """\
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "reportes"
url = "https://reportes.example"
"""


def test_con_un_servicio_caido_sale_con_1(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def todos_arriba(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Before the tests, the `CONFIGURACION` constant is the text of a small `servicios.toml`, between triple quotation marks, like the multi-line texts of Lesson 6. The backslash right after the opening quotation marks (`"""\`) keeps the text from starting with a line break: at the end of a line, inside a text, `\` means “this line continues on the next,” so the first line of the text is `[[servicios]]` and not an empty one. TOML would not care, but this way what the test writes is exactly what you see.

The first test uses the real simulated data with a configuration that includes `reportes`, which is down. The second replaces the function with `todos_arriba` (“all up”), defined inside the test because only it uses it, with the same signature as the real one: when `main` calls it, it will not know it is fake.

Look closely at the target: `"revisor.cli.revisar_todos"`, the name **inside `cli`**, and not the one in `revision`, where the function is defined. [The `monkeypatch` documentation](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) says so: you have to patch the reference that your code uses. A `from modulo import nombre` statement creates, inside the module that imports, a name of its own that points to the same function: two names for one thing, and replacing one does not change the other. `cli.py` begins with `from revisor.revision import revisar_todos`, so `main` looks for `revisar_todos` among the names of `cli`. If you patched the one in `revision`, `cli` would keep calling the real one. In “The error you will see” you break it on purpose.

With the four files written you run **everything together** for the first time. You already know what it must say:

```text
$ cd fig08_15
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

Twenty-one dots and `21 passed`: 7 + 4 + 8 + 2. That number is the contract with Lesson 9. **The first session ends here.** When you come back, `pytest -q` is the first thing you run, to know that you left the project as you thought.

### 8.4 `mypy`: types that are checked without running anything

#### 8.4.1 Annotations are not enforced at run time

Since Lesson 3 you have been writing annotations like `tiempo_ms: int | None`. Lesson 0 said that **Python does not use them when running**: they are information for the reader and for external tools, not an order. [PEP 484](https://peps.python.org/pep-0484/), which introduced them, says so bluntly: types are not checked at run time. You can see it in four lines:

```python
# fig08_09.py
def doble(tiempo_ms: int) -> int:
    return tiempo_ms * 2


print(doble("142"))
```

The signature says `doble` (“double”) receives an integer, and the call passes it the text `"142"`. Run it and ask `mypy` to check it:

```text
$ python fig08_09.py
142142
$ mypy fig08_09.py
fig08_09.py:6: error: Argument 1 to "doble" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Python does not complain: `"142" * 2` is valid (it repeats the text) and the program prints `142142`, an absurd result for a time in milliseconds that nobody flagged. [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) reads the file **without running it**, compares every call with the annotations and complains. Its message always has the same structure: `file:line: error: description  [code]`. It says where (line 6), what (argument 1 of `doble` is `str` and `int` was expected) and, in brackets, the code of the kind of error (`arg-type`), useful for looking it up. The last line counts errors and files.

That is *gradual typing*: you decide how much you annotate, and `mypy` checks what you annotated. It is the counterpart of what TypeScript does in Hábil's [TypeScript course](https://www.habil.mx/en/courses/typescript/): types are written and checked before running, but they are not a mechanism of the language at run time.

#### 8.4.2 What `mypy` catches: the `None` you forgot

The most frequent error `mypy` finds is forgetting that something can be `None`. The `reportes` service does not answer and its `tiempo_ms` is `None`: that is why the field is annotated `int | None`. Here is a function that forgets it (the program catches the error itself just so you see the message without noise):

```python
# fig08_10.py
def segundos(tiempo_ms: int | None) -> float:
    return tiempo_ms / 1000


print(segundos(87))
try:
    print(segundos(None))
except TypeError as error:
    print(f"se rompió: {error}")
```

```text
$ python fig08_10.py
0.087
se rompió: unsupported operand type(s) for /: 'NoneType' and 'int'
$ mypy fig08_10.py
fig08_10.py:3: error: Unsupported operand types for / ("None" and "int")  [operator]
fig08_10.py:3: note: Left operand is of type "int | None"
Found 1 error in 1 file (checked 1 source file)
```

Python finds out when it reaches the second call: `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`. If that call were on a path walked once a month, the error would have reached production. `mypy` finds it **without running anything**, on line 3, and explains it: `Unsupported operand types for / ("None" and "int")` and a note, `Left operand is of type "int | None"`. The solution is not to silence `mypy` but to decide what must happen when there is no time. Here, return `None` too, and say so in the return type:

```python
# fig08_11.py
def segundos(tiempo_ms: int | None) -> float | None:
    if tiempo_ms is None:
        return None
    return tiempo_ms / 1000


print(segundos(87))
try:
    print(segundos(None))
except TypeError as error:
    print(f"se rompió: {error}")
```

```text
$ python fig08_11.py
0.087
None
$ mypy fig08_11.py
Success: no issues found in 1 source file
```

The function now tells the truth in its signature, `float | None`, and that truth has a consequence: **everyone who uses the result is obliged to check whether it is `None`**, because `mypy` will complain if they treat it as a number. Instead of a hidden error that shows up at dawn, you have an uncomfortable question in your editor, which is exactly where you want it.

#### 8.4.3 `match` and the missing case

In Lesson 5 you saw that `match` together with an `Enum` has an advantage that `mypy` takes advantage of here. Imagine the `revisor` gains a fourth status, `DEGRADADO` (“degraded”), and a function that translates statuses into colors is left without its `case`:

```python
# fig08_12.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"
    DEGRADADO = "DEGRADADO"


def semaforo(estado: Estado) -> str:
    match estado:
        case Estado.ARRIBA:
            return "verde"
        case Estado.LENTO:
            return "amarillo"
        case Estado.CAIDO:
            return "rojo"


for estado in Estado:
    print(estado.value, "->", semaforo(estado))
```

```text
$ python fig08_12.py
ARRIBA -> verde
LENTO -> amarillo
CAIDO -> rojo
DEGRADADO -> None
$ mypy fig08_12.py
fig08_12.py:12: error: Missing return statement  [return]
Found 1 error in 1 file (checked 1 source file)
```

Python **does not warn**: when no `case` matches, the `match` ends without doing anything, the function reaches its end without a `return` and returns `None`. The fourth line prints `DEGRADADO -> None`, a color that does not exist, and in a real program that `None` would travel to whoever uses it. `mypy` sees it without running anything: the signature promises a `str`, but there is a path (that of `DEGRADADO`) that ends without returning anything, and that is why it says `Missing return statement`. The message does not mention the missing member, but it points at the function (`def semaforo`), and comparing its `case`s with the `Enum`'s members is enough to find it. It is the safety net that Lesson 5 promised: you add a member, and `mypy` points out every `match` that was left behind.

#### 8.4.4 Gradual: what you do not annotate, `mypy` does not check, unless you ask it to

[The `mypy` documentation](https://mypy.readthedocs.io/en/stable/getting_started.html) establishes it: a function without annotations is considered dynamically typed, and by default `mypy` **does not check its body**. It is a design decision so that types can be added little by little to old code. See it with a function that has not a single annotation:

```python
# fig08_13.py
def duplicar(x):
    return x * 2


print(duplicar("ms"))
```

```text
$ python fig08_13.py
msms
$ mypy fig08_13.py
Success: no issues found in 1 source file
$ mypy --strict fig08_13.py
fig08_13.py:2: error: Function is missing a type annotation  [no-untyped-def]
fig08_13.py:6: error: Call to untyped function "duplicar" in typed context  [no-untyped-call]
Found 2 errors in 1 file (checked 1 source file)
```

Without options, `mypy` says “Success”: `duplicar` (“duplicate”) has no annotations and is not checked. With `--strict`, the same file gives two errors: the function has no annotations (`no-untyped-def`) and you call it from code with types (`no-untyped-call`). Strict mode is a shortcut that turns on several checks at once; [the documentation lists them](https://mypy.readthedocs.io/en/stable/command_line.html): among them `--disallow-untyped-defs` (every function carries annotations), `--check-untyped-defs` (check the body of those that do not too), `--warn-return-any` and `--warn-unused-ignores`. The exact list can change between versions, which is why the lesson pins the `mypy` one.

The course rule: **the project goes in strict mode from the start**; it is much cheaper to maintain types than to add them afterwards. It is configured in `pyproject.toml`, [where `mypy` reads it](https://mypy.readthedocs.io/en/stable/config_file.html):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`python_version` is which version of Python to check against (the course's Mint one), `strict = true` turns on strict mode and `files` says what to check when you run it without arguments: the package and also the tests, because a badly typed test hides errors just like any other code.

#### 8.4.5 `mypy` on the `revisor`

With the configuration in place, the whole project is checked with one command. All the code of the package and of the tests carries annotations (that is why the tests end in `-> None` and ask for `tmp_path: Path`):

```text
$ cd fig08_15
$ mypy
Success: no issues found in 11 source files
```

`Success: no issues found in 11 source files`: seven files of the package (`__init__`, `__main__`, `cli`, `configuracion`, `formato`, `modelo` and `revision`) and four of tests. Read the count as you learned with `pytest`: if one day it says `0 source files`, `mypy` checked nothing and the green is worthless. To see it work on the project, do Exercise 3: change an annotation and watch how `mypy` leads you to those who use it. It is its most valuable use: when you change a function's signature, it tells you all the places you must adjust.

A warning about emergency exits. `# type: ignore` tells `mypy` not to complain about that line, and the `Any` type turns off the checks on a value. They exist for legitimate reasons (third-party code without types) and are the fastest way to make the tool useless. The rule: **the complaint is almost always right**; before silencing it, understand what it says.

### 8.5 `ruff`: checking and formatting

The last tool knows nothing about your problem or your types: it reads the code as text and does two different things with two commands. [`ruff`](https://docs.astral.sh/ruff/) is a single program that covers both roles:

- **`ruff check`** is the *linter* (a static analyzer): it looks for known errors and bad practices, such as an import that is not used or a default value shared between calls. [Each finding has a code](https://docs.astral.sh/ruff/linter/) of one or two letters and three digits (`F401`, `E711`).
- **`ruff format`** is the *formatter*: it rewrites the code in a single format (spaces, line breaks, quotation marks, where a long line is split). [It imitates `Black`'s](https://docs.astral.sh/ruff/formatter/), the community standard, so your code looks like that of any other project. The best part is what it **takes away from you**: the discussion about style is settled once and the machine carries it out.

See both on a file with real defects. It is messy on purpose: it is the only one in the course that is.

```python
# fig08_14.py
import os, sys
from pathlib import Path

def agregar(servicio, lista=[]):
    lista.append(servicio)
    return lista

def es_nulo(valor):
    return valor == None

print(agregar("catalogo"))
print(agregar("pagos"))
```

The program runs (it prints the two lists), and it has at least five things wrong. Since you are outside the project and there is no `pyproject.toml` to say which rules to apply, you pass them with `--select`; `--output-format concise` asks for one line per finding:

```text
$ python fig08_14.py
['catalogo']
['catalogo', 'pagos']
$ ruff check --select E,F,I,B,UP --output-format concise fig08_14.py
fig08_14.py:2:1: E401 [*] Multiple imports on one line
fig08_14.py:2:1: I001 [*] Import block is un-sorted or un-formatted
fig08_14.py:2:8: F401 [*] `os` imported but unused
fig08_14.py:2:12: F401 [*] `sys` imported but unused
fig08_14.py:3:21: F401 [*] `pathlib.Path` imported but unused
fig08_14.py:5:29: B006 Do not use mutable data structures for argument defaults
fig08_14.py:10:21: E711 Comparison to `None` should be `cond is None`
Found 7 errors.
[*] 5 fixable with the `--fix` option (2 hidden fixes can be enabled with the `--unsafe-fixes` option).
$ ruff format --check fig08_14.py
unformatted: File would be reformatted
  --> fig08_14.py:5:1
   |
4  |
5  +
6  | def agregar(servicio, lista=[]):
7  |     lista.append(servicio)
8  |     return lista
9  |
10 +
11 | def es_nulo(valor):
12 |     return valor == None
13 |
14 +
15 | print(agregar("catalogo"))
   |

1 file would be reformatted
```

The second call printed `['catalogo', 'pagos']`: the defect from Lesson 3 in action. The default value `lista=[]` is **shared** between calls, and `ruff` sees it beforehand as `B006`. There are seven findings, each with `file:line:column: CODE description`. The letter of the code is the name of the collection of rules, which you choose with `select`:

| Letter | What it watches | An example from above |
|---|---|---|
| `E` | Style ([pycodestyle](https://peps.python.org/pep-0008/), the official guide) | `E401` several imports on one line; `E711` comparing with `None` using `==` |
| `F` | Simple logic errors ([Pyflakes](https://docs.astral.sh/ruff/rules/unused-import/)) | `F401` three unused imports |
| `I` | The order of imports | `I001` unsorted block |
| `B` | Known traps ([bugbear](https://docs.astral.sh/ruff/rules/mutable-argument-default/)) | `B006` mutable default value |
| `UP` | Modernizing the syntax to your Python version | (none in this file) |

The documentation [recommends starting with few rules](https://docs.astral.sh/ruff/linter/) (`E` and `F`), adding groups one at a time and choosing with `select` so that the set is explicit and does not change on its own when updating. Those five are the `revisor`'s set.

The `[*]` mark says that `ruff` knows how to fix the finding by itself; the summary counts five findings with a fix, and two others have *unsafe* fixes that could change what the program does (like the one for `B006`). `ruff` only applies the safe ones, unless you ask otherwise. `ruff format --check` is the question “is it formatted?”: it answered no, and shows what would change. To see what each would do without touching the file there is `--diff`:

```text
$ ruff check --select E,F,I,B,UP --fix --diff fig08_14.py
--- fig08_14.py
+++ fig08_14.py
@@ -1,6 +1,4 @@
 # fig08_14.py
-import os, sys
-from pathlib import Path
 
 def agregar(servicio, lista=[]):
     lista.append(servicio)

Would fix 4 errors (2 additional fixes available with `--unsafe-fixes`).
$ ruff format --diff fig08_14.py
--- fig08_14.py
+++ fig08_14.py
@@ -2,12 +2,15 @@
 import os, sys
 from pathlib import Path
 
+
 def agregar(servicio, lista=[]):
     lista.append(servicio)
     return lista
 
+
 def es_nulo(valor):
     return valor == None
 
+
 print(agregar("catalogo"))
 print(agregar("pagos"))

1 file would be reformatted
```

The first shows the safe fix: deleting the two import lines, which are entirely redundant. Notice that it says `Would fix 4 errors`, not five: the five findings with `[*]` are on the same two lines, and their fixes overlap. When applying those for `F401`, which delete the unused imports, the line disappears and another of the fixes (separating `os` and `sys`, or sorting them) has nothing left to do. That is why it pays to look at the `--diff` and not just count marks. The `== None` and the default value remain, because their fixes are unsafe: it is up to you to decide. The second shows what the formatter would do: two blank lines between functions, the convention. What `ruff format` does is mechanical and does not change what the program does.

#### 8.5.1 In the project: the configuration

The rules are written once in `pyproject.toml`, like those of `pytest` and `mypy`, and then `ruff check` and `ruff format` need no arguments:

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`target-version` says which version of Python you write for: Mint's 3.12, the oldest the course admits. It matters: `ruff` decides with it what is “standard library” when sorting imports (`tomllib` is since 3.11) and what modern syntax to suggest. In this project, if you did not write it, [`ruff` would take it](https://docs.astral.sh/ruff/settings/#target-version) from `requires-python = ">=3.12"`, in `[project]`, which says the same; it is written so that it stays in view next to the rules. With neither of the two, `ruff` assumes 3.10, and with that `tomllib` would no longer be standard library and would end up in the third-party packages block. `select` goes in the `[tool.ruff.lint]` subsection, [as `ruff` documents it](https://docs.astral.sh/ruff/configuration/).

```text
$ cd fig08_15
$ ruff check
All checks passed!
$ ruff format --check
11 files already formatted
```

`All checks passed!` and all files already formatted. If you run `ruff check` on code that has not yet been through the formatter, it is common for it to complain about `E501` (line longer than 88 characters), and for a `ruff format` to resolve almost all of them, because it spreads long calls and lists over several lines. That is why the order is always the same: **first `ruff format`, then `ruff check`**. And if a linter rule seems excessive to you, the honest answer is to discuss it and remove it from the `select` with a reason, not to hide it with a comment on every line.

### 8.6 The complete project

The snapshot of the project at the end of the lesson is the package of Lesson 7 with `version = "0.7.0"`, the `tests/` folder (four files you have already seen) and three new configuration sections. The complete `pyproject.toml`:

```toml fig08_15/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.7.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = []

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

What is new compared with Lesson 7 is the version and the last three sections. The other files **do not change**; they are repeated here only so that the project is complete and you can compare with yours if something does not match:

```toml fig08_15/servicios.toml
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

```python
# fig08_15/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig08_15/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig08_15/src/revisor/modelo.py
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
# fig08_15/src/revisor/revision.py
from revisor.modelo import Resultado, Servicio, clasificar

SIMULADO: dict[str, tuple[int | None, int | None, str | None]] = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}


def revisar(servicio: Servicio) -> Resultado:
    sin_respuesta = (None, None, "sin conexión")
    codigo, tiempo_ms, error = SIMULADO.get(servicio.nombre, sin_respuesta)
    if codigo is not None:
        detalle = str(codigo)
    elif error is not None:
        detalle = error
    else:
        detalle = "sin conexión"
    estado = clasificar(codigo, tiempo_ms)
    return Resultado(servicio, estado, tiempo_ms, detalle)


def revisar_todos(servicios: list[Servicio]) -> list[Resultado]:
    return [revisar(servicio) for servicio in servicios]
```

```python
# fig08_15/src/revisor/formato.py
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
# fig08_15/src/revisor/configuracion.py
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
# fig08_15/src/revisor/cli.py
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

Reinstall it with `pip install -e .` so that the environment sees the new version. From today on, every time you finish a change you repeat this ritual, in this order:

```text
$ cd fig08_15
$ ruff format --check
11 files already formatted
$ ruff check
All checks passed!
$ mypy
Success: no issues found in 11 source files
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

## The error you will see

### `ModuleNotFoundError: No module named 'revisor'`

It is the first error anyone hits when opening the project in a new environment. The tests import the package (`from revisor.modelo import clasificar`) and the package **is not installed** in the environment that runs `pytest`. The report does not begin with dots but with an `ERRORS` block: the error happened when *collecting* the file, before running anything. Shortened version (the long `importlib` paths go as `...`):

```text
==================================== ERRORS ====================================
______________________ ERROR collecting tests/test_cli.py ______________________
ImportError while importing test module '.../tests/test_cli.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
...
tests/test_cli.py:6: in <module>
    from revisor.cli import main
E   ModuleNotFoundError: No module named 'revisor'
=========================== short test summary info ============================
ERROR tests/test_cli.py
ERROR tests/test_configuracion.py
ERROR tests/test_formato.py
ERROR tests/test_modelo.py
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
4 errors in 0.05s
```

It is read from the bottom up: the last `E` line is the cause, the one before says which line provoked it (`from revisor.cli import main`, line 6 of `test_cli.py`) and the intermediate steps, from `importlib`, are of no use to you. The summary counts four errors, one per file, and does not say `0 passed`. The fix is `pip install -e .` from the folder that has the `pyproject.toml`: the project is fine, it just needs installing.

### `fixture 'tmp_pth' not found`

It is what happens if you misspell the name of a fixture, `tmp_pth` instead of `tmp_path`. Since `pytest` looks for it by the parameter's name, a name that does not exist is a `pytest` error and not a Python one:

```text
___________________________ ERROR at setup of test_x ___________________________
file tests/test_x.py, line 4
  def test_x(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: anyio_backend, anyio_backend_name, ... tmp_path, ...
>       use 'pytest --fixtures [testpath]' for help on them.
```

Look at the heading: `ERROR at setup`, not `FAILED`. The test did not even get to run; it failed while being *set up*. The message offers you the available fixtures (shortened here), and there is `tmp_path`. (The `anyio_*` ones appear because `httpx`, which you installed in Lesson 1, brings a `pytest` plugin; they do not affect you.)

### The red test that patches the wrong place

The most educational one, because it is not about syntax but about reasoning. In `tests/test_cli.py`, change the target of the `monkeypatch` from `revisor.cli.revisar_todos` to `revisor.revision.revisar_todos`, where the function is defined, and run the tests. Real report, shortened:

```text
.F                                                                       [100%]
=================================== FAILURES ===================================
_______________________ test_con_todos_arriba_sale_con_0 _______________________
...
        monkeypatch.setattr("revisor.revision.revisar_todos", todos_arriba)
        archivo = tmp_path / "servicios.toml"
        archivo.write_text(CONFIGURACION, encoding="utf-8")
>       assert main(["--config", str(archivo)]) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = main(['--config', '/tmp/pytest-of-tu/pytest-0/test_con_todos_arriba_sale_con0/servicios.toml'])

tests/test_cli.py:35: AssertionError
----------------------------- Captured stdout call -----------------------------
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
reportes    CAIDO          —  sin conexión

2 servicios · 1 arriba · 0 lentos · 1 caído · promedio 142ms
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_con_todos_arriba_sale_con_0 - AssertionError: ...
1 failed, 1 passed in 0.02s
```

The `E` line says `assert 1 == 0` and, below, that `main` returned `1`. The `Captured stdout call` section (what the code printed during the test, which `pytest` keeps and shows only if it fails) carries the decisive clue: **`reportes` appears as down, with the usual data**. The patch had no effect, because `cli` kept using its own copy of `revisar_todos`. The moral is the documentation's: patch the name **where it is used**. Undo the change before going on.

## What gets done wrong

**Writing a test that cannot fail.** `assert clasificar(200, 142) is not None` always passes, because `clasificar` never returns `None`. It is the reason for the habit of 8.1.2. Cost: a net with a hole the size of the test and the false calm of green.

**Letting the test compute the answer with the code's formula.** `assert formatear_tiempo(2300) == f"{2300 / 1000:.1f}s"` repeats the implementation: if the formula is wrong, the test copies it. The expected value is written by hand, as data: `"2.3s"`.

**Copying the current output as the expected value without looking at it.** You run the code, see that it returns `'ARRIBA'` and write it in the test because “that is what comes out.” If it was wrong, you turned the defect into the specification, and the test defends it. The expected value comes from the rule, never from what the code does today.

**Looking only at the exit code.** That is 8.1.3: a `0` does not count how many tests ran.

**Patching where the function is defined and not where it is used**, or patching so much that the test no longer exercises real code. If everything inside `main` is fake, the only thing you test is the fake.

**Silencing `mypy` with `# type: ignore` or with `Any` so that it “passes.”** You leave the defect and remove the warning. If there is a real exception, it carries a comment with the why.

**Annotating halfway.** A function with annotations on two parameters and none on the third is not left out of the check: `mypy` does check its body, but the unannotated parameter is treated as `Any`, “anything,” and everything you do with it goes through without questions. With `strict = true`, besides, `mypy` flags it as `[no-untyped-def]`. All or nothing; in this course, all.

**Fighting the formatter.** Reformatting by hand what `ruff format` already decided, or disabling a rule because you cannot be bothered to understand it.

**Tests that depend on the order, on the disk or on the network.** A test that reads the real `servicios.toml`, or that only passes if another ran before, fails on another machine with no explanation. With `tmp_path` and `monkeypatch`, each test is self-sufficient.

## Exercises

### Exercise 1 — Break, see the red, fix

In `src/revisor/modelo.py`, change the `>=` of `if tiempo_ms is not None and tiempo_ms >= umbral_ms:` to `>`. Before running, **predict**: how many tests will turn red and which? Run `pytest -q`. Then run `python -m revisor` and compare the table with the usual one. Undo the change and run again. Note in your logbook the number from the report before and after, and what the table taught you.

### Exercise 2 — A new test for exit code 2

`main` returns `2` when the configuration file does not exist. Write in `tests/test_cli.py` a test that checks it: call `main(["--config", ...])` with a path inside `tmp_path` to a file you did not create, and assert that the result is `2`. Before keeping it, **check that it can fail**: how would you turn it red on purpose? The report must say `22 passed`. Delete it when you finish (Lesson 9 starts from 21) and check that it says 21 again.

### Exercise 3 — Let `mypy` lead you to the caller

In `src/revisor/formato.py`, change `def formatear_tiempo(tiempo_ms: int | None) -> str:` to `def formatear_tiempo(tiempo_ms: int) -> str:`, touching nothing else. Run `mypy`. How many errors come out and in which files? Why is there one in `tests/test_formato.py`, which you did not touch? Undo the change.

### Exercise 4 — The missing test

There is a one-character change in `formatear_tiempo` that the 21 tests do **not** detect. The 1000-millisecond boundary has its case in `clasificar`, but this is the same boundary. Change `if tiempo_ms < 1000:` to `if tiempo_ms <= 1000:` and run `pytest -q`: green or red? If it is green, write the missing case in the table of `tests/test_formato.py`, check that it now turns red, undo the change to the code and **delete** the new case so that the project goes back to 21, the number Lesson 9 starts from.

## Solutions

### Solution 1

The correct prediction is **one** red test: `test_clasificar[200-1000-Estado.LENTO]`. No other touches exactly 1000. Real report, shortened:

```text
................F....                                                    [100%]
=================================== FAILURES ===================================
____________________ test_clasificar[200-1000-Estado.LENTO] ____________________

codigo = 200, tiempo_ms = 1000, esperado = <Estado.LENTO: 'LENTO'>
...
>       assert clasificar(codigo, tiempo_ms) is esperado
E       AssertionError: assert <Estado.ARRIBA: 'ARRIBA'> is <Estado.LENTO: 'LENTO'>
E        +  where <Estado.ARRIBA: 'ARRIBA'> = clasificar(200, 1000)

tests/test_modelo.py:22: AssertionError
=========================== short test summary info ============================
FAILED tests/test_modelo.py::test_clasificar[200-1000-Estado.LENTO] - Asserti...
1 failed, 20 passed in 0.02s
```

`1 failed, 20 passed` adds up to 21: the total is still there. And the table of `python -m revisor`, with the defect in place, **comes out identical** to the usual one: looking at the table does not find the defect, the test does. When you undo the change, the report goes back to `21 passed`.

### Solution 2

```python
def test_sin_archivo_de_configuracion_sale_con_2(tmp_path: Path) -> None:
    inexistente = tmp_path / "no-existe.toml"
    assert main(["--config", str(inexistente)]) == 2
```

To see it red, change the `2` to a `0` and run: it must fail with `assert 2 == 0`, which shows it looks at the real exit code. With the good version, `22 passed`. When you delete it, `21 passed` must come back; if not, something was left in the file.

### Solution 3

**Three** errors come out, in two files (`Found 3 errors in 2 files (checked 11 source files)`):

```text
src/revisor/formato.py:22: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
src/revisor/formato.py:46: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
tests/test_formato.py:17: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
```

The first is in `linea`, which passes it `resultado.tiempo_ms`, an `int | None`. The second is in `resumen`, which passes it the average, which can also be `None` when no service answered. The third is the test: its `tiempo_ms` parameter is `int | None` (the table includes the `None`) and it calls the function with it. All three are the same problem seen from three places, and the average one you may not even have remembered: `mypy` showed it to you without your looking for it. When you undo the change, `Success: no issues found in 11 source files` comes back.

### Solution 4

The change **passes green** (`21 passed`): none of the four rows uses 1000 (there is a `None`, an 87, a 999 and a 2300). With `<=`, the 1000 would come out as `1000ms` instead of `1.0s` and nobody would notice. The missing case:

```python
        (1000, "1.0s"),
```

With it, the mutation turns red (`test_formatear_tiempo[1000-1.0s]` tells you which). In a project of your own you would keep it without a second thought; here you delete it only for a calendar reason: Lesson 9 compares its count with 21. What this solution wants to leave you with is the question: **a green suite does not say the code is right, it says the questions you asked it have answers**. Revert the fix and check that it turns red: that is the method.

## How I know I got it

- [ ] `pytest -q`, from the project root, ends with `21 passed` (the number, not just the green).
- [ ] `mypy` ends with `Success: no issues found in 11 source files`.
- [ ] `ruff check` says `All checks passed!` and `ruff format --check` says all 11 files are already formatted.
- [ ] You changed `>=` to `>` in `clasificar`, `pytest -q` said `1 failed, 20 passed`, and when you undid it, it went back to `21 passed`.
- [ ] You can explain why an `echo $?` equal to `0` does not tell you how many tests ran, and what `--collect-only` does.
- [ ] You can explain why `monkeypatch.setattr` points to `revisor.cli.revisar_todos` and not to `revisor.revision.revisar_todos`.
- [ ] `pyproject.toml` has the three sections (`[tool.pytest.ini_options]`, `[tool.ruff]` with its `[tool.ruff.lint]` and `[tool.mypy]`) and `version = "0.7.0"`.

## Summary

Answer without looking at the lesson:

1. How does `pytest` recognize what a test is, and what happens with a function called `prueba_algo`?
2. Why do you see a test red before accepting it green?
3. What exit codes does `pytest` have for “everything passed,” “some failed” and “none collected”? Why is the count read from the report?
4. What does `@pytest.mark.parametrize` save you and how do you know which row failed?
5. What is a fixture and what do `tmp_path` and `monkeypatch` hand over?
6. Why does `monkeypatch.setattr` point to `revisor.cli.revisar_todos`?
7. What does it mean that Python's typing is gradual and what changes with `strict = true`?
8. What is the difference between `ruff check` and `ruff format`, and why is the second run first?

## Further reading

- [pytest, “Get Started”](https://docs.pytest.org/en/stable/getting-started.html) — the official guide, with the discovery rules and how to read the report. Accessed on October 7, 2026.
- [mypy, “Getting started”](https://mypy.readthedocs.io/en/stable/getting_started.html) — what dynamic and static typing are, and how to introduce types into existing code. Accessed on October 7, 2026.
- [Ruff, “The Ruff Linter”](https://docs.astral.sh/ruff/linter/) — how rules are chosen, what the codes mean and what a safe fix is. Accessed on October 7, 2026.
- [PEP 484, “Type Hints”](https://peps.python.org/pep-0484/) — the document that introduced type annotations and makes clear they are not checked at run time. Accessed on October 7, 2026.
