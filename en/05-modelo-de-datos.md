# Lesson 5 — The data model

**Time:** 90 min

**What you build:** the `revisor`'s model (`Servicio`, `Estado`, `Resultado`) and its complete report, with table and summary

**What you learn:** data molds with `class` and `@dataclass(frozen=True)`; `Enum`; `match` and `case`, with wildcard and with guards; the report with its summary line

**Where you come from.** You bring the project from [Lesson 4](04-colecciones.md): two files, `formato.py` and `revisor.py`, already without parallel lists. In `revisor.py`, `SERVICIOS` is the list of names you want to check and `SIMULADO` is a dictionary that stores, for each name, a tuple `(code, tiempo_ms, error)`. It works and no longer gets out of step. But Lesson 4 ended with three annoyances noted down. The tuple does not say what each position is: the second element is the time because you remember it, not because the code says so. `clasificar` returns a text (`"ARRIBA"`, `"LENTO"`, `"CAIDO"`) and nothing prevents you from writing `"ARIBA"` without Python protesting. And the table does not yet have its summary line.

**What this lesson does not do.** It does not read the configuration from a file (the four services are still written by hand; [Lesson 6](06-errores-archivos-datos.md) takes them out of there), it does not catch errors with `try`, and it does not define methods of its own in the classes. Nor does it query any internet address: the codes and the times still come from `SIMULADO`.

You work in your `~/curso-python/revisor/` folder, with the virtual environment active. The small programs go, as in Lesson 4, in the `practica/` subfolder.

## By the end you will be able to

- Declare `Servicio` and `Resultado` as `@dataclass(frozen=True)` and `Estado` as an `Enum`, and explain what is gained compared with a tuple, a dictionary, or a loose text.
- Build an instance with the fields by position or by name, read them with a dot, and make another with `replace` instead of changing the one you have.
- Classify a service with `match` and `case`, with a wildcard and with guards (`case c if c >= 400`), without falling into the trap of the name that captures.
- Read `FrozenInstanceError`, the `ValueError` of a `dataclass` with a list as a default value, and the one of an `Enum` that is asked for a value it does not have.
- Assemble the four-file `revisor` and reproduce its table with the summary `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.

## The why before the how

Look at how the `revisor` speaks today about the things of its problem. A service is a **loose name** inside a list. What it answered is an **anonymous tuple**, `(200, 2300, None)`. And its status is a **text**, `"LENTO"`. All three forms work, and all three have the same defect: Python does not know what they mean. It does not know that the tuple's second element is a time, or that `"LENTO"` is one of only three possible values. For Python they are a tuple and a text like any other, and that is why a typo (writing `"ARIBA"`, or asking for `respuesta[2]` wanting the time) does not fail where it happens: it slips through the program and produces a wrong table without a single message.

The solution is to give each thing of the problem **a name of its own that Python recognizes**. A service will no longer be “a text in a list” but a `Servicio`, with fields called `nombre`, `url`, and `timeout_ms`; a status will no longer be a text that can be misspelled, but an `Estado.LENTO` that Python recognizes or rejects; and what came out of checking a service will be a `Resultado`. The shape we give, in the program, to what the problem is about is what we call here **the data model**. (Careful, it is not the same as the “Data model” section of Python's documentation, which talks about how the language works inside; here “model” is ours.)

The path has three tools and an assembly. `dataclass` (5.1) makes data molds; `Enum` (5.2) closes the list of allowed values; `match` (5.3) decides among many cases with clarity; and in 5.4 they come together in the project, which also gains its summary line. At the end of the lesson, the `revisor` will do this:

```text
$ cd fig05_07
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

It is the usual table, now with a blank line and a summary, and produced from named objects instead of loose tuples and texts. Notice that the header and the four rows come out identical to those of lessons 3 and 4, and that the summary is new: to count how many are up, how many slow, and how many down, and to compute the average, you need the comprehensions from Lesson 4, now applied to results that already know what they are.

## The concepts

### 5.1 A mold for each service: `class` and `@dataclass`

#### 5.1.1 Why the tuple and the dictionary are not enough

With what you already know, a service could be a tuple, `("catalogo", "https://catalogo.example", 5000)`, or a dictionary, `{"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}`. The tuple, as you saw in Lesson 4, does not say what each position is. The dictionary does say it, but it has another problem: the keys are texts you write from memory, and a typo is not noticed where it happens.

<!-- frag: dict_typo.py -->
```python
servicio = {"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}
print(servicio.get("nmbre"))
```

```text
None
```

Writing `"nmbre"` instead of `"nombre"` broke nothing: `.get` returned `None`, and that `None` will keep slipping through the program until something fails three functions later, far from the cause. What we want is for that typo to **fail right there**, with a message that says so. A type of our own gives that.

#### 5.1.2 A class as a mold

A **class** is a mold for making values that all have the same shape. Each value made with the mold is called an **instance**. Think of a cookie mold: there is one shape and many cookies. In the `revisor` the mold is `Servicio`, and `catalogo`, `inventario`, and `pagos` are three instances. Here you will use classes only as data molds: without methods, without inheritance (with one syntax exception you will see in 5.2). The word `class` followed by a name and a colon opens the mold, and below, indented, **one field per line** is declared, with the format `nombre: tipo`.

Python has a tool, the `dataclasses` module, that makes almost everything a data mold needs: the way of building each instance, the way of showing it when printed, and the way of comparing it with `==`. It is activated with a line right above the class, which starts with `@` and is called a **decorator**: it is a mark that asks Python to process the class with that tool before handing it over. [The module's documentation](https://docs.python.org/3/library/dataclasses.html) describes it this way: the decorator adds the generated methods to the class it decorates. Here it is used as `@dataclass(frozen=True)`, where `frozen=True` additionally asks that instances **cannot be changed**, like a tuple. Save this as `fig05_01.py`:

```python
# fig05_01.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
notificaciones = Servicio(
    nombre="notificaciones",
    url="https://notificaciones.example",
    timeout_ms=1000,
)
print(catalogo)
print(notificaciones.timeout_ms)
print(catalogo.nombre, catalogo.timeout_ms)

igual = Servicio("catalogo", "https://catalogo.example")
print(catalogo == igual, catalogo is igual)

raro = Servicio(nombre=5, url=None)
print(raro)
```

```text
$ python fig05_01.py
Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)
1000
catalogo 5000
True False
Servicio(nombre=5, url=None, timeout_ms=5000)
```

- `from dataclasses import dataclass` brings in from the `dataclasses` module only the tool you need, with the `from ... import` form from Lesson 3.
- The two blank lines before and after the class are a style convention ([PEP 8](https://peps.python.org/pep-0008/#blank-lines)), not syntax; the formatter you will see in Lesson 8 demands them.
- `nombre: str` and `url: str` declare two text fields. `timeout_ms: int = 5000` declares an integer field with a **default value**: if you do not give it when building, it is 5000, the `httpx` timeout the `revisor` will use later. Fields with a default value go **at the end**, just like a function's parameters with a default value.
- `Servicio("catalogo", "https://catalogo.example")` **builds** an instance: the mold is called as if it were a function, with the fields in the order they were declared. Each field can also be given by its name, as in `notificaciones`, which also changes the timeout to 1000. By name it reads better when there are more than two or three fields.
- `print(catalogo)` shows `Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)`: the way of printing was also generated by `dataclass`, and that is why an instance you print during debugging explains itself. With a tuple without names you would have seen `('catalogo', 'https://catalogo.example', 5000)`.
- `catalogo.timeout_ms` reads a field with a dot. If you misspell the name (`catalogo.timeout`), Python fails right there with `AttributeError`, which is what we wanted.
- `catalogo == igual` is `True` because `==` compares **field by field**: they are two separate instances with the same data. `catalogo is igual` is `False` because they are two different objects. It is the `==` versus `is` of Lesson 3, with a real case: `==` asks “do they have the same value?”, `is` asks “are they the same thing?”.
- The last two lines are so you do not get overconfident. `Servicio(nombre=5, url=None)` **is built without protest**, even though `nombre` should be text and so should `url`. It is what you learned in Lesson 0: annotations are not enforced at run time. `dataclass` uses the annotations only to know which fields there are and in what order: [the documentation makes clear](https://docs.python.org/3/library/dataclasses.html) that, apart from two exceptions you will not use, nothing in the decorator examines the annotated type. The one that does check them is a separate tool, `mypy`, in Lesson 8.

#### 5.1.3 Frozen: to change, another one is created

What does `frozen=True` do? It forbids assigning to a field. See what happens if you try:

<!-- frag: congelado.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
catalogo.timeout_ms = 1000
```

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

Of this *traceback* only the last line is shown, which is the one that matters: in between it passes through a line that `dataclasses` generates internally and that is not the same in 3.12 and in 3.14. It says “cannot assign to field `timeout_ms`.” As with the tuple, it is a guarantee and not a failure. [The documentation](https://docs.python.org/3/library/dataclasses.html#frozen-instances) calls it emulation of read-only instances.

Why would you want that? Because the result of checking a service is a **fact**: “at 10:42, `inventario` took 2300 ms.” Nobody should be able to correct it afterwards without leaving a trace. And because, when in lessons 9 and 10 several tasks read the same services at once, that none can change them avoids a whole class of errors. And if you truly need another version of a service, you do not edit it: you **make another** with `dataclasses.replace`, which copies an instance changing only the fields you indicate:

```python
# fig05_02.py
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
catalogo_corto = replace(catalogo, timeout_ms=1000)
print(catalogo.timeout_ms, catalogo_corto.timeout_ms)

repetido = Servicio("catalogo", "https://catalogo.example")
print(len({catalogo, repetido}))
```

```text
$ python fig05_02.py
5000 1000
1
```

`replace` did not touch `catalogo`: it returned `catalogo_corto`, a new instance. And the last line shows another advantage of the immutable: a frozen instance can be put in a **set** (or be a dictionary key), because it no longer changes: it is *hashable* in the sense of Lesson 4 (4.1.4), **as long as all its fields are**. Python computes its fingerprint from the fields, and those of `Servicio` are texts and integers. Two equal instances count as one: `{catalogo, repetido}` has one element.

A warning that connects with the copy versus reference of Lesson 4: `frozen` forbids reassigning the **field**, but does not make immutable what the field contains. A field that holds a list can still change on the inside (`servicio.etiquetas.append(...)`), because the list is still mutable. And it has a second effect: such an instance can no longer be put in a set, because the fingerprint is computed from all the fields and a list has no fingerprint; the attempt fails with `TypeError: unhashable type: 'list'` (in 3.14 the text adds `cannot use ... as a set element`). That is why in the `revisor` the fields are of immutable types: texts, integers, `None`.

### 5.2 `Enum`: a closed list of values

Look at another, similar problem. `clasificar` from Lesson 3 returns the text `"ARRIBA"`, `"LENTO"`, or `"CAIDO"`, and whoever uses it compares against texts. If one is misspelled:

<!-- frag: estado_typo.py -->
```python
estado = "ARIBA"
if estado == "ARRIBA":
    print("el servicio está arriba")
else:
    print("el servicio NO está arriba")
```

```text
el servicio NO está arriba
```

The program did not fail: it said the service was **not** up, when what happened is that someone wrote one R too few. It is the same typo as in 5.1.1, now in a value. What is needed is a **closed** list of allowed values, with names that Python recognizes, and that is an `Enum` (from “enumeration”). [The `enum` module](https://docs.python.org/3/library/enum.html) defines it as a set of symbolic names bound to unique values.

```python
# fig05_03.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


estado = Estado.LENTO
print(estado)
print(estado.name, estado.value)
print(Estado("CAIDO"))
print(estado is Estado.LENTO, estado == "LENTO")
for posible in Estado:
    print(posible.value)
```

```text
$ python fig05_03.py
Estado.LENTO
LENTO LENTO
Estado.CAIDO
True False
ARRIBA
LENTO
CAIDO
```

- `class Estado(Enum):` opens a mold, just like `Servicio`, but with `(Enum)` between parentheses: that is how Python is told “this mold is based on `Enum`,” that is, that it is an enumeration. The parentheses after the name mean “this class starts from that other one.” In the code you write in this course you will only see them with `Enum` and, in Lesson 6, with `Exception` (the Lesson 9 lab also uses them, but you run that program without writing it); for what you need it is enough to read it as “a class of the `Enum` family.”
- Inside there is one line per **member**: `ARRIBA = "ARRIBA"` gives the member's name (on the left, always in capitals by convention) and its **value** (on the right). Here the value is the same text that is printed in the table, without an accent and in capitals, which is also how Lesson 6's JSON will store it.
- `Estado.LENTO` is a member. `print` shows it with its class name in front: `Estado.LENTO`. `.name` is its name (`LENTO`) and `.value` its value (`LENTO`). When the report wants the word for the table, it uses `.value`.
- `Estado("CAIDO")` goes in the opposite direction: it looks for the member whose **value** is that text. If there is none, it fails on the spot (you see it in a moment).
- `estado is Estado.LENTO` is `True`: [members are compared by identity](https://docs.python.org/3/howto/enum.html#comparisons), and each member exists only once. And `estado == "LENTO"` is **`False`**: the member `Estado.LENTO` and the text `"LENTO"` are different things, even though they print almost the same. This surprises almost everyone the first time. You always compare against members (`estado == Estado.LENTO`), never against the text.
- `for posible in Estado:` traverses the members in the order they were declared.

Now the typo, in its two variants. Writing `Estado.ARIBA` fails instantly, at the exact point of the error:

<!-- frag: enum_typo.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


print(Estado.ARIBA)
```

The last line of the *traceback* is:

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

Python even guesses what you meant to write. What matters is that the error occurs on the line of the typo and not three functions later. And looking up by value a text that does not exist:

<!-- frag: enum_valor.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


Estado("ROTO")
```

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError: 'ROTO' is not a valid Estado`. The two errors say the same thing in different words: “that member does not exist.” Notice that they are exactly the kind of failure we wanted: early, clear, and with the culprit's name.

### 5.3 `match` and `case`: deciding among many cases

Lesson 2 taught you `if`/`elif`/`else`. When the branches are many and all ask about the **same value**, a long chain of `elif` becomes hard to read, and for that Python ships, since version 3.10, the `match` statement. It is very powerful (the [official documentation](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement) devotes a whole section to it, and [PEP 636](https://peps.python.org/pep-0636/) is a tutorial), but here you will use only its simplest part. Look first at a function that describes a status code, and that is not yet the `revisor`'s:

```python
# fig05_04.py
def describir(codigo: int | None) -> str:
    match codigo:
        case None:
            return "sin respuesta"
        case 200:
            return "todo bien"
        case 301 | 302:
            return "redirección"
        case 404:
            return "no existe"
        case c if c >= 500:
            return f"falla del servidor ({c})"
        case c if c >= 400:
            return f"error del cliente ({c})"
        case _:
            return "otro"


for codigo in [None, 200, 302, 404, 418, 503, 100]:
    print(codigo, "->", describir(codigo))
```

```text
$ python fig05_04.py
None -> sin respuesta
200 -> todo bien
302 -> redirección
404 -> no existe
418 -> error del cliente (418)
503 -> falla del servidor (503)
100 -> otro
```

How it reads:

- `match codigo:` says “I am going to compare this value” (the **subject**). Each `case` below is a **pattern** with which Python tries it, **from top to bottom**, and it takes **the first one that fits**: it executes its block and does not look at the others. That is why order matters.
- `case None`, `case 200`, `case 404` are **literal** patterns: they fit if the subject equals that value. The first asks about `None` by identity, as you were taught in Lesson 2, and the others by equality.
- `case 301 | 302` is **one or the other**: the vertical bar means “or.” It fits either of the two codes.
- `case c if c >= 500` is the one that deserves attention. First `c` is a **capture** pattern: a loose name fits *anything* and, along the way, stores the subject in that variable, so inside the block `c` is the code. Then, `if c >= 500` is a **guard**: an extra condition that must hold for the case to count. If it does not hold, Python continues with the next `case`. [The documentation](https://docs.python.org/3/reference/compound_stmts.html#guards) describes it this way: if the pattern fails, the guard is not even evaluated; if it fits, the guard is evaluated, and the case is chosen only if it is true. That is why 418 passes by the 500 case (it is smaller) and falls into the next one, `c >= 400`.
- `case _:` is the **wildcard**: the underscore fits everything and stores nothing. It goes last and collects what no earlier case caught (here, the 100).

The complete classification of the `revisor`'s services is four rules, which you know from Lesson 2: with no code it is down; a code of 400 or more is down; if it answered and took 1000 ms or more it is slow; if not, it is up. It is written with the same mold, and returns members of `Estado` instead of texts. This is what will end up in `modelo.py`:

```python
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
```

Read it from top to bottom, which is how Python does it. The first `case` catches “no code” and the second, with its guard, catches “code of 400 or more”: the first two rules, and both give `CAIDO`. What reaches `case _` we already know answered well (there is a code and it is less than 400), and there only the choice between the other two rules remains, with an `if` from Lesson 2: if the time exists and is at least the threshold, `LENTO`; if not, `ARRIBA`. Checking `tiempo_ms is not None` before comparing is necessary because a code can exist without a time, and comparing `None >= 1000` fails with a `TypeError`. Notice also that the order of the cases **is** the logic: if you put the 400 case before the `None` one, `None >= 400` would fail. In the project of 5.4 the function lives in `modelo.py`, next to the classes you defined in 5.1 and 5.2.

Now the most famous trap of `match`. In a pattern, **a loose name does not compare, it captures**. If you want to compare against a constant, writing its name is not enough:

```python
# fig05_05.py
LIMITE = 400


def es_error(codigo: int) -> bool:
    match codigo:
        case LIMITE:
            return True
        case _:
            return False
```

```text
$ python fig05_05.py
  File "fig05_05.py", line 7
    case LIMITE:
         ^^^^^^
SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable
```

This program **does not even start**: Python rejects it when reading it, with a `SyntaxError`. `case LIMITE:` does not ask “is the code 400?”; it says “anything fits, and store it in a variable called `LIMITE`.” Since it fits everything, the `case _` below could never be reached, and that is why the message says `name capture 'LIMITE' makes remaining patterns unreachable`. Python only warns because after `case LIMITE:` there is another case. If `case LIMITE:` were the last one, it would warn about nothing: [the documentation](https://docs.python.org/3/reference/compound_stmts.html#irrefutable-case-blocks) allows a case that always fits (it calls it irrefutable) as long as it goes last, and the program would run with a wildcard disguised as a constant, returning `True` for any code. You can check it: with a `case LIMITE:` at the end, `es_error(5)` returns `True`. The practical rule: to compare against a constant, you use a name **with a dot**, like `Estado.CAIDO`; the dot tells Python it is a value and not a new name, and [it calls them value patterns](https://docs.python.org/3/reference/compound_stmts.html#value-patterns).

```python
# fig05_06.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


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
$ python fig05_06.py
ARRIBA -> verde
LENTO -> amarillo
CAIDO -> rojo
```

Here `Estado.ARRIBA` has a dot, so it compares. It is the most natural use of `match` together with an `Enum`: one case per member, without a wildcard. And it brings an advantage that `mypy` takes advantage of in Lesson 8: if someday you add a new member to `Estado` and forget its `case`, the type checker flags it.

### 5.4 Assembling the `revisor`

Put everything together in the project. When finished you will have four files in `~/curso-python/revisor/`: `modelo.py` (new), `revision.py` (new), `formato.py` (changes), and `revisor.py` (changes). Each file has a reason to exist: `modelo.py` says **what things there are** (the service, the status, the result) and how they are classified; `revision.py` **checks** a service; `formato.py` **gives text form** to a result, and `revisor.py` is the entry point that brings them together.

The first is the model:

```python
# fig05_07/modelo.py
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
# fig05_07/revision.py
from modelo import Resultado, Servicio, clasificar

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
# fig05_07/formato.py
from modelo import Estado, Resultado


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
```

```python
# fig05_07/revisor.py
from formato import encabezado, linea, resumen
from modelo import Servicio
from revision import revisar_todos

SERVICIOS: list[Servicio] = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("inventario", "https://inventario.example"),
    Servicio("pagos", "https://pagos.example"),
    Servicio("reportes", "https://reportes.example"),
]


def main() -> None:
    resultados = revisar_todos(SERVICIOS)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

The four pieces, one by one.

**`modelo.py`.** It gathers everything from sections 5.1 to 5.3. The constants and the classes go at the top, because `clasificar` uses them. `Resultado` is a second mold that no longer stores loose texts: it stores **a `Servicio`** (the one that was checked), **an `Estado`**, the time (`int | None`, because a down service does not have one), and the detail. Notice the composition: a mold can have fields whose type is another mold. `clasificar` is the one you wrote in 5.3, except that the parameter list is spread over lines because the `def` line does not fit in the 88 characters the style asks for (the comma at the end of the parameter list is part of that way of arranging). And `nombres_repetidos` is the one from Lesson 4 (4.1.5), except that it now receives a list of `Servicio` and looks at the field `servicio.nombre`.

**`revision.py`.** It is a new module, but its content is not: `SIMULADO` is the dictionary from Lesson 4, which leaves `revisor.py` and moves here, with the same tuple of three `(code, tiempo_ms, error)` for each name. `revisar` changes its signature again: now it receives a `Servicio` and returns a `Resultado`, instead of receiving a name and returning an already-built row. The inside is what you already know: it looks up with `.get` (a name that is not in `SIMULADO` is a service without data, and comes out down “sin conexión”), unpacks the tuple into three names, decides the `detalle` with the same rule (the code as text if there was a response, and if not, the error's text), classifies, and returns a `Resultado`. That `revisar` no longer builds the row is the separation we were after: checking is one thing and showing is another, and each lives in its module. `revisar_todos` is a comprehension: a list of `Resultado`, one per service, in the same order. When in Lesson 9 the program really queries, `SIMULADO` disappears and `revisar` keeps returning the same.

**`formato.py`.** `formatear_tiempo` and `encabezado` stay as in lessons 3 and 4. (If you wrote them differently but the output was the same, leave them as they are.) What changes is `linea`, which **changes its signature**: before, it received four loose values and now it receives a single `Resultado`, and takes from it what it needs. That is what we were after: there is no longer a need to pass four things in the right order. The two new functions are `contar` and `resumen`. `contar` adds an “s” when the quantity is not one: `contar(1, "caído")` gives `1 caído` and `contar(3, "caído")` gives `3 caídos`. `resumen` counts the total with `len`, uses three comprehensions to count how many there are of each status, takes with a fourth the times of those that responded, computes the average **only if there is any** (with `len(tiempos_ms) > 0`, because dividing by zero would fail), and joins the parts with `" · ".join(partes)`. The annotation `promedio_ms: int | None = None` says it starts without a value and may end up being an integer; if no service responded, the summary says `promedio —`.

**`revisor.py`.** `SERVICIOS` stops being a list of names and becomes a **list of `Servicio`**: the four canonical ones, written by hand, each with its name and its address (the timeout stays at the default value). To add a service you write a `Servicio(...)` and, while the data is simulated, its line in `SIMULADO`, just as in Lesson 4. `main` checks all of them, prints the header, one row per result, a blank line (the one a `print()` with no arguments writes), and the summary. The `from ... import` work because the four files are in the same folder, as in Lesson 3.

Run the project from its folder:

```text
$ cd fig05_07
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

It is the table from lessons 3 and 4, with a blank line and the summary. If the columns do not come out aligned for you, the culprit is almost always an extra or missing space inside one of the f-strings; check that they are identical to those in the text. And if the summary counts wrong, compare each comprehension with the lesson's: the three that count statuses only change the member of `Estado`.

With this the `revisor` already has its **model**: the `Servicio` that is checked, the `Estado` it ends up in, and the `Resultado` that joins the two with what was measured. But something remains awkward, and you will feel it in Exercise 1: the list of services is **inside the code**. To check another service you have to open `revisor.py` and edit. [Lesson 6](06-errores-archivos-datos.md) takes it out to a configuration file, and with it come the errors that deserve their own lesson.

## The error you will see

In the previous sections you already provoked several errors where they are born (`FrozenInstanceError`, `AttributeError`, `ValueError`, `SyntaxError`). Here is the one you will meet most when writing molds with `dataclass`, and at the end a table to recognize them all at a glance.

### `ValueError: mutable default <class 'list'> for field ... is not allowed`

It is the same problem as the mutable default argument of Lesson 3, now in a `dataclass` field. If you give it a list as a default value:

<!-- frag: lista_defecto.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    etiquetas: list[str] = []
```

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

The last line says: “a mutable default (`list`) for the field `etiquetas` is not allowed: use `default_factory`.” (Here too only the last line is shown: between it and your file the *traceback* passes through internal lines of `dataclasses.py` that change between one Python version and another, and do not help you read the error. What counts is the type, `ValueError`, and the message, which also tells you how to fix it.) Python protects you from something that in a normal function happened silently: a single list shared by all the instances. The solution is a **factory**: instead of “this list,” you say “call `list` every time a new one is needed.”

```python
# fig05_08.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Servicio:
    nombre: str
    etiquetas: list[str] = field(default_factory=list)


catalogo = Servicio("catalogo")
pagos = Servicio("pagos")
catalogo.etiquetas.append("critico")
print(catalogo.etiquetas, pagos.etiquetas)
```

```text
$ python fig05_08.py
['critico'] []
```

Each instance has its own list, and that is why `pagos` did not find out about `catalogo`'s tag. Along the way you see what was warned about in 5.1.3: the instance is frozen, and even so `catalogo.etiquetas.append(...)` worked, because `frozen` prevents reassigning the field, not changing the list it contains. That is why lists are not used as fields in the `revisor`.

### The errors of this lesson at a glance

When one shows up, look up its last line here. All of them came from this lesson's runs.

| The last line says... | What happened | Where you saw it |
|---|---|---|
| `dataclasses.FrozenInstanceError: cannot assign to field '...'` | you tried to assign to a field of a frozen instance | 5.1.3 |
| `ValueError: mutable default ... use default_factory` | you put a list as a field's default value | above |
| `AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?` | you asked for an `Enum` member that does not exist | 5.2 |
| `ValueError: 'ROTO' is not a valid Estado` | you looked up by value a member that does not exist | 5.2 |
| `SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable` | you wrote a loose name where you wanted to compare | 5.3 |

## What gets done wrong

Each of these slips has a concrete cost, and most do not give an error at first.

**Storing a record in a dictionary or in a tuple when you already have a mold.** A tuple of six elements forces you to remember which is which; a dictionary with text keys turns typos into distant `None`s. If the data has a fixed shape, that shape deserves a name: `@dataclass`.

**Believing that a `dataclass` validates its fields.** `Servicio(nombre=5, url=None)` is built without protest (5.1.2): annotations say what you expect, but do not check it at run time. The cost is a bad piece of data traveling through the whole program until it fails far away. What arrives from outside is validated on the way in, and that is Lesson 6.

**Leaving loose texts where there is already an `Enum`.** This is the most treacherous. If you change `clasificar` so that it returns `Estado.LENTO` but somewhere else in the program an `if estado == "LENTO"` is left, that comparison will **never be true** (5.2: a member is not equal to its text), and the program will keep running without warning. When you migrate from texts to an `Enum`, find all the places that compare.

**Writing `case NOMBRE:` wanting to compare.** It captures, it does not compare. If you want to compare against a constant, use a name with a dot (`Estado.CAIDO`) or a guard (`case c if c == LIMITE`).

**Putting a mutable collection as a field of a frozen mold.** `frozen` protects the field, not what the field contains: a list stored in a frozen instance can still be changed on the inside (`fig05_08.py`). The cost is a guarantee that seems to exist and does not. In the `revisor` the fields are texts, integers, `None`, and other frozen molds.

**Building instances by position when there are many fields.** `Servicio("notificaciones", "https://notificaciones.example", 1000)` reads fine; with six fields, nobody knows which is the fourth. With more than two or three, by name: `Servicio(nombre=..., url=..., timeout_ms=...)`.

## Exercises

Try each one before looking at the solutions.

### Exercise 1 — Two more services, and an average of only those that are up

(a) Add the `revisor`'s two extra services to the 5.4 version: `facturacion` (answers with code 503 in 95 ms) and `notificaciones` (with a timeout of 1000 ms, gets no response: “tiempo agotado,” that is, “timed out”). You have to touch **two** places. Before running, predict the last two lines of the output: the `notificaciones` row and the summary. (b) Add at the end of `main` a line that prints the average of the times of the `ARRIBA` services only, without rounding. The convenient way is with a comprehension.

### Exercise 2 — Provoke four errors and read them

Open the REPL with `python` from your `revisor` folder, import what you need from `modelo`, and provoke these four errors, one by one: (a) assign `timeout_ms` on an instance of `Servicio`; (b) `Estado("ROTO")`; (c) `Estado.ARIBA`; (d) in a file in your `practica/` folder, a `dataclass` with a field `etiquetas: list[str] = []`. For each one, write in your logbook the **last line** and, in your own words, what it means and how it is fixed.

### Exercise 3 — A code without a time

What does `clasificar(200, None)` return, that is, a service that answered with 200 but for which there is no measured time? Predict it twice: with Lesson 3's `clasificar` (the one that returns texts) and with today's (the `match` one). Then check it from your `revisor` folder, with `from modelo import clasificar`. Why does the rule give that result and not `LENTO`? And finally: what would happen if you removed the `tiempo_ms is not None` part from the condition?

## Solutions

### Solution 1

(a) In `revision.py`, `SIMULADO` gains two lines:

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

And in `revisor.py`, `SERVICIOS` gains two services:

```python
    Servicio("reportes", "https://reportes.example"),
    Servicio("facturacion", "https://facturacion.example"),
    Servicio("notificaciones", "https://notificaciones.example", timeout_ms=1000),
]
```

The full output:

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

The summary is `6 servicios · 2 arriba · 1 lento · 3 caídos`, and the average comes out 656 ms because it is calculated over the **four that had a time** (142, 2300, 87, and 95, which add up to 2624, divided by 4). Notice that `facturacion` counts in the average even though it is down: it responded, with a 503 and 95 ms. `notificaciones` has no time and does not count. Notice also the `notificaciones` row: it is the same overflow you saw in Lesson 4, with the name stuck to the status because it is 14 letters and the column 12; Lesson 11 resolves it by computing the width from the longest name. And the third observation is the one that leads into the next lesson: to check two more services you had to **edit the code**, in two files.

(b) `Estado` is imported and the comprehension is added at the end of `main`:

```python
from modelo import Estado, Servicio
```

```python
    print(resumen(resultados))
    tiempos_arriba = [
        r.tiempo_ms
        for r in resultados
        if r.estado == Estado.ARRIBA and r.tiempo_ms is not None
    ]
    print(sum(tiempos_arriba) / len(tiempos_arriba))
```

The last line of the output is:

```text
114.5
```

(142 and 87 add up to 229, divided by 2 is 114.5.) The condition `r.tiempo_ms is not None` is not an ornament. An `ARRIBA` service may have no time: `clasificar(200, None)` returns `Estado.ARRIBA`, because with no measured time there is no evidence of slowness. If that `None` reached `sum`, the program would fail with a `TypeError`. And besides, `tiempo_ms` is annotated as `int | None`, and whoever reads the code (or `mypy`, in Lesson 8) needs to see that the `None` was already discarded before adding.

### Solution 2

The last four lines, each one measured:

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

`FrozenInstanceError`: the instance is frozen. Fix: do not assign; make another with `replace(servicio, timeout_ms=...)`.

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError`: there is no member of `Estado` with the value `ROTO`. Fix: use one of the three allowed values, or `Estado.CAIDO` directly, which does not even go through the text.

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

`AttributeError`: `Estado` has no member called `ARIBA`, and Python suggests the one that looks like it. Fix: the one it suggests. It is the typo that the `Enum` came to catch, and it catches it on the line where it happens.

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

`ValueError` when **defining** the class, before creating any instance. Fix: `etiquetas: list[str] = field(default_factory=list)`, as in `fig05_08.py`.

### Solution 3

Both versions return **ARRIBA**: the Lesson 3 one, the text `"ARRIBA"`; today's, `Estado.ARRIBA`. From the `revisor` folder:

<!-- frag: codigo_sin_tiempo.py -->
```python
from modelo import clasificar

print(clasificar(200, None))
```

```text
Estado.ARRIBA
```

The reason is in the third rule, which has been the same since Lesson 2: a service is `LENTO` if it **responded and took** 1000 ms or more. With `None` there is no measured time, so there is no evidence of slowness, and all that is known is that it answered with a good code: `ARRIBA`. Both versions treat the case the same because both ask `tiempo_ms is not None` before comparing. In the `revisor` this case does not occur (a service that answered always carries its time), but `tiempo_ms` is annotated as `int | None`, and the function has to give an answer for everything its signature admits.

If you removed `tiempo_ms is not None`, the comparison `None >= 1000` would get evaluated and the program would stop with:

```text
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

It is the same error as in Lesson 2, when the questions were in the wrong order.

## How I know I got it

- [ ] In `~/curso-python/revisor/`, `python revisor.py` prints seven lines (the header, four rows, a blank line, and the summary), and the last one is `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] With the two extra services of Exercise 1, the last line is `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`, and the `notificaciones` row comes out with the name stuck to the status (and you know why).
- [ ] In the REPL, assigning `timeout_ms` on a `Servicio` fails with `dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'`, and `Estado("ROTO")` fails with `ValueError: 'ROTO' is not a valid Estado`.
- [ ] You can write `clasificar` from memory with `match`: with no code it is `CAIDO`, a code of 400 or more is `CAIDO`, a time of 1000 or more is `LENTO`, and anything else is `ARRIBA`.
- [ ] You can explain in your own words the difference between `==` and `is` for two equal `Servicio` instances, why `Estado.LENTO == "LENTO"` is `False`, and what `replace` does.
- [ ] You noted in the [logbook](bitacora.md) what was hardest for you: what you note there is what you should review.

## Summary

Answer without looking at the lesson:

1. What is a class and what is an instance? What does `@dataclass` add to a class, and what does `frozen=True` add?
2. What is gained with `@dataclass(frozen=True)` compared with a dictionary or a tuple? What does `replace` do?
3. What does `==` compare between two `Servicio` instances, and what does `is` compare?
4. Why does `Estado.LENTO == "LENTO"` give `False`, and how do you get a member's text?
5. In what order does `match` try its cases, and what does the wildcard `case _` do?
6. In a `match`, what does a loose name like `case LIMITE:` do? How do you compare against a constant?
7. Why did `linea` change its signature in this lesson, and what did it gain with the change?

## Further reading

- [Python, “dataclasses”](https://docs.python.org/3/library/dataclasses.html) — the module's complete reference: `frozen`, `field`, `replace`, and everything this lesson did not use. Accessed on October 7, 2026.
- [PEP 557, “Data Classes”](https://peps.python.org/pep-0557/) — the document that proposed `dataclass` and explains for which cases it was designed and for which not. Accessed on October 7, 2026.
- [Python, “Enum HOWTO”](https://docs.python.org/3/howto/enum.html) — the official guide to enumerations, from the basics to derived types. Accessed on October 7, 2026.
- [PEP 636, “Structural Pattern Matching: Tutorial”](https://peps.python.org/pep-0636/) — the official `match` tutorial, which goes quite a bit further than this lesson. Accessed on October 7, 2026.
