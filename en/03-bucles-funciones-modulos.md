# Lesson 3 — Loops, functions, and modules

**Time:** 2 × 90 min (two sessions)

**What you build:** the `revisar()` function and the traversal of the list: a two-file `revisor` that prints the header and the rows of the four services

**What you learn:** four concepts. First, loops (`for`, `while`, `range`, `enumerate`) and the minimal list needed to traverse; second, functions (`def`, parameters, default values, `return`, simple annotations, and the trap of a default value that is a list); third, names (where each variable lives, `UnboundLocalError`, and `==` versus `is`); fourth, modules (`import`, `from ... import`, and `if __name__ == "__main__":`)

**Where you come from.** You bring the `revisor.py` from [Lesson 2](02-valores-texto-decisiones.md): about thirty lines that store **one** service (`inventario`) in variables, classify it with an `if`/`elif`/`else`, and print it on an aligned row, under the table header. It works, but it has a problem that was already visible at the end of that lesson: to check the other three services you would have to copy the block three times and change the values in each copy. Today that problem gets taken out of the way. You keep working in `~/curso-python/revisor/`, with the virtual environment active, and programs are run with `python archivo.py`.

**How the lesson is divided.** It is long, and that is why there are two sessions of 90 minutes with a natural break in the middle. **The first session** is sections 3.1 and 3.2 (loops and functions) and ends with figure `fig03_11`, the complete `revisor` in **one** file. **The second session** is sections 3.3 and 3.4 (names and modules), the errors, the exercises, and the `revisor` split into two files. If you run out of time in the first one, stop when you reach `fig03_11`: what follows is better understood with that program working and after a rest.

**What this lesson does not do.** It does not cover lists in depth: today you use a **minimal** list (create it, ask how many elements it has, read one by its position, and add one), just enough to traverse it. Dictionaries, tuples, sets, and comprehensions belong to [Lesson 4](04-colecciones.md), and the data model with `Servicio` and `Estado` to [Lesson 5](05-modelo-de-datos.md). And there are still no caught errors (`try`), no files, no network.

## By the end you will be able to

- Traverse a list with `for` in three ways (by value, by position with `range(len(...))`, and with `enumerate`) and repeat with `while` without falling into an infinite loop.
- Create a list, ask its size with `len`, read an element by its position (which starts at 0), and add one with `.append`.
- Write a function with parameters, a default value, and `return`, with simple type annotations (`int`, `str`, `int | None`, `-> None`), and explain the difference between printing and returning.
- Explain why a default value that is a list “remembers” previous calls, and fix it with the `None` pattern.
- Say where each variable lives (local or global) and read `UnboundLocalError`.
- Explain the difference between `==` (are they equal?) and `is` (are they the same object?) and know when `is` is used.
- Split a program into two files with `import` and `from ... import`, and explain what `if __name__ == "__main__":` is for.

## The why before the how

Look at what you would have to do today, with what you know from Lesson 2, to make the `revisor` check the four services. Copy the `inventario` block three times, and in each copy change the name, the code, and the time. That is a hundred nearly identical lines. And then someone decides that a service is slow from 800 milliseconds, not 1000: you have to find the comparison in each copy and change it. If you forget one, three services are classified with one rule and the fourth with another, and the report lies without giving any error.

That is the underlying problem, and it is the same in every program: **the same logic written several times tends to diverge**. Python (and every language) ships three tools to solve it, which are the three of this lesson:

- **Repeat without copying.** A *loop* executes the same block once for each element of a list, or while a condition holds. That is section 3.1.
- **Give a piece of logic a name.** A *function* wraps a recipe (for example, “classify a service”) under a name, to use it from anywhere with different values. That is section 3.2. The price of functions is that now you have to know **where each name lives**: a variable you create inside a function is not the same as another one with the same name outside. That is section 3.3.
- **Split the program into files.** A *module* is a Python file that another file can use. When the program grows, each file keeps a single kind of thing (here, one for the table format and another for the checking logic). That is section 3.4.

At the end of the lesson, `python revisor.py` will print the four-service table you saw in Lesson 2, without the summary (which needs counting, and that arrives in Lesson 5):

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

A design warning, so you do not read it as carelessness. The data of the four services goes in **three parallel lists**: one of names, one of codes, and one of times, where position 2 of each list speaks about the same service. It is a fragile way of storing data: if one list gets out of order or comes up short, nothing warns you. **It is done this way on purpose**, because it is what can be done with what you know today, and because the fragility is the reason Lesson 4 exists. In the first exercise you will break it on purpose to see it.

## The concepts

### 3.1 Loops: repeating without copying

#### 3.1.1 The minimal list

To repeat something with each service you need a list of services, and the values from Lesson 2 each hold a single piece of data. The list has to be introduced. Here you see the minimum; Lesson 4 studies it in depth.

A **list** is an ordered sequence of values, written between square brackets with the elements separated by commas: `["catalogo", "inventario", "pagos", "reportes"]`. A list can mix types (the codes one has numbers and a `None`), and it is stored under a name like any other value. Four operations are enough for now, and all four are in the next figure. Save it as `fig03_01.py`:

```python
# fig03_01.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]

print(nombres)
print(len(nombres))
print(nombres[0])
print(nombres[3])

nombres.append("facturacion")
print(len(nombres))
print(nombres[4])
```

```text
$ python fig03_01.py
['catalogo', 'inventario', 'pagos', 'reportes']
4
catalogo
reportes
5
facturacion
```

Line by line. `print(nombres)` shows the whole list, with its brackets. `len(nombres)` returns how many elements it has: four. What comes next is what most bewilders the beginner: **positions start at 0**. `nombres[0]` is the first element (`catalogo`) and `nombres[3]` is the fourth (`reportes`). The underlying reason is that the position says how far you are from the start: the first element is zero steps away. The practical consequence, which you will need all course long, is that a list of four elements has positions 0, 1, 2, and 3, and **has no position 4**; the last position is always `len(lista) - 1`.

The last part of the figure adds an element: `nombres.append("facturacion")` glues it at the end. The dot and the parentheses mean that `append` is a *method* of the list, that is, an operation the list knows how to perform on itself (methods are the functions that “belong” to a value, and you will see more of them with texts and dictionaries). After adding it, `len` gives 5 and position 4 now exists. Notice that `append` **changed the list in place**: it did not return a new list, it modified the one it already had. Values that can change like that are called *mutable*, and that property comes up twice more in this lesson, so keep it in your head.

A style detail: in this figure the list's name is in lowercase (`nombres`) because it changes, and in the following figures, when lists are fixed data of the program, they will be in capitals (`NOMBRES`), like the rest of the constants.

#### 3.1.2 `for`: doing something with each element

The `for` loop executes a block once for each element of a list. Save `fig03_02.py`:

```python
# fig03_02.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]

for nombre in nombres:
    print("revisando", nombre)

print("listo")
```

```text
$ python fig03_02.py
revisando catalogo
revisando inventario
revisando pagos
revisando reportes
listo
```

The first line of the loop reads almost like English: “for each `nombre` in `nombres`.” It ends with a **colon**, and the block it repeats goes **indented** (four spaces), just like an `if`. Python does this: it takes the first element of the list, stores it under the name `nombre`, and executes the block; takes the second, stores it under the same name, and executes the block; and so on until they run out. The last line, `print("listo")` (“done”), is at the left margin: it is no longer part of the block, and that is why it is executed just once at the end. It is the same rule as in Lesson 2: indentation says where a block ends.

The name `nombre` was chosen by you. It could be called `x` or `servicio`; but a good name tells what is inside (each turn, `nombre` is *one* name, and the list is `nombres`, in the plural). This is a very useful convention: list in the plural, element in the singular.

#### 3.1.3 `range`: traversing by position

Sometimes the value is not enough; you need its **position**. That happens with the `revisor`'s parallel lists: to know the time of the service you are looking at, you need the same position in the list of times. That is what `range` is for: `range(4)` produces the numbers 0, 1, 2, and 3 (the first four, starting at zero, not including 4). And since `len(NOMBRES)` is 4, `range(len(NOMBRES))` produces exactly the valid positions of the list. Save `fig03_03.py`:

```python
# fig03_03.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(3):
    print(i)

for i in range(len(NOMBRES)):
    print(i, NOMBRES[i], TIEMPOS_MS[i])
```

```text
$ python fig03_03.py
0
1
2
0 catalogo 142
1 inventario 2300
2 pagos 87
3 reportes None
```

The first loop just prints the numbers that `range(3)` produces: `0`, `1`, and `2`. The second is the one that matters: on each turn, `i` is a position, and the two lists are read at that same position, `NOMBRES[i]` and `TIEMPOS_MS[i]`. Notice that this **only works if the two lists are the same length**; if `TIEMPOS_MS` had one element fewer, the last turn would fail. That is the defect of parallel lists, and there is an exercise for it.

A note on names: `i` is the universal habit for “a position” (it comes from *index*), and it is one of the few one-letter names that are accepted. For everything else, names that say what they are.

#### 3.1.4 `enumerate`: the value and its position together

When you need the value **and** the position, `enumerate` gives you both at once. On each turn it hands over a pair, and the syntax `for i, nombre in enumerate(...)` puts the first element of the pair in `i` and the second in `nombre`. That is called *unpacking*. Save `fig03_04.py`:

```python
# fig03_04.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]

for i, nombre in enumerate(NOMBRES):
    print(i, nombre)

for numero, nombre in enumerate(NOMBRES, start=1):
    print(f"{numero}. {nombre}")
```

```text
$ python fig03_04.py
0 catalogo
1 inventario
2 pagos
3 reportes
1. catalogo
2. inventario
3. pagos
4. reportes
```

The first loop prints the positions from 0 with their name. The second uses a second argument, `start=1`, so that the count begins at 1: that is how things are numbered for people. That `start=1` is a **keyword argument**, and you will understand it better in section 3.2.

`enumerate` is the most readable way to traverse **one** list with its position. In today's `revisor` there are **three** parallel lists, so the position is what ties them together and the traversal is that of `range(len(NOMBRES))`; with three lists, `enumerate` only helps with one. But it is worth knowing, because as soon as the `revisor` leaves parallel lists behind (Lesson 4), it will traverse a **single** list, and when the position is needed too, `enumerate` will be the natural tool (you will use it in Lesson 6).

#### 3.1.5 `while`: repeating while something is true

`for` repeats once for each element of something that already exists. `while` repeats **while a condition is true**, without knowing in advance how many turns there will be. It asks the condition again before each turn, and stops when the answer is `False`. Save `fig03_05.py`, which looks for the position of the first service that did not answer:

```python
# fig03_05.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]

i = 0
while i < len(CODIGOS) and CODIGOS[i] is not None:
    i += 1

print("primer servicio sin respuesta, en la posición", i)
print(NOMBRES[i])
```

```text
$ python fig03_05.py
primer servicio sin respuesta, en la posición 3
reportes
```

Before starting, `i` is 0. Each turn asks two things joined with `and`: is `i` still inside the list? and does the code at that position exist (`is not None`, which is the negation of `is None`)? As long as both are true, it executes the block, which says `i += 1`. That line is the shorthand for `i = i + 1`: it adds 1 and stores the result under the same name. At position 3 the code is `None`, the second question fails, and the loop ends with `i` being 3.

Notice the **order of the two questions**, because it is Lesson 2 again. `i < len(CODIGOS)` goes first so that, if `i` ever became 4, the `and` would already be false and Python would **not try** to read `CODIGOS[4]`, which does not exist. Short-circuiting protected you.

With `while` there is a risk that `for` does not have: **the infinite loop**. If the block changes nothing the condition asks about, the condition never becomes false and the program keeps going around forever. If you forgot the `i += 1` of the figure, that is what would happen. When a program hangs like this, the emergency exit is `Ctrl`+`C` in the terminal, which interrupts it. The rule for writing a `while` is: **before running it, locate the line of the block that brings the condition closer to being false**. And whenever a `for` can be used, use it: the `for` ends by construction when the elements run out.

#### 3.1.6 Accumulating, skipping, and leaving

Two very frequent uses of loops complete the section. The first is **accumulating**: going through the data to get a count. Save `fig03_06.py`, which adds up the times of the services that answered:

```python
# fig03_06.py
TIEMPOS_MS = [142, 2300, 87, None]

total = 0
respondieron = 0
for tiempo_ms in TIEMPOS_MS:
    if tiempo_ms is not None:
        total += tiempo_ms
        respondieron += 1

print("suma:", total, "ms")
print("respondieron:", respondieron)
print("promedio:", total / respondieron, "ms")
```

```text
$ python fig03_06.py
suma: 2529 ms
respondieron: 3
promedio: 843.0 ms
```

The pattern repeats in almost every program: before the loop, the accumulating variables are created (`total` and `respondieron`, at zero); inside the loop, they are updated; afterwards, they are used. The block's `if` leaves out the service that did not answer, whose time is `None`; without it, `total += None` would fail with a `TypeError`, like the one in Lesson 2. The sum is 2529 (142 + 2300 + 87), three answered, and the average of those that answered is 843. It comes out with a `.0` because the `/` division always gives a decimal; Lesson 4 teaches you to round it, and Lesson 5 uses it in the table's summary.

The second use is **controlling the loop from inside** with two words: `continue` skips to the next turn without finishing the block, and `break` leaves the loop entirely. Save `fig03_07.py`, which looks for the first slow service:

```python
# fig03_07.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(len(NOMBRES)):
    if TIEMPOS_MS[i] is None:
        continue
    if TIEMPOS_MS[i] >= 1000:
        print("primer servicio lento:", NOMBRES[i])
        break
```

```text
$ python fig03_07.py
primer servicio lento: inventario
```

With `catalogo` (142 ms), the loop asks whether it has a time (yes), asks whether it is slow (no), and moves to the next turn. With `inventario` (2300), the second question is true: it prints the name and `break` ends the loop, so `pagos` and `reportes` are not even looked at. If the first one had been `reportes` (with `None`), the `continue` would have skipped that turn before comparing `None >= 1000`, which blows up. Use `break` and `continue` in moderation: they are convenient and hide the program's flow when abused.

### 3.2 Functions: giving a recipe a name

#### 3.2.1 Defining and calling

A **function** is a named block of code that you can execute whenever you like, as many times as you like, with different data each time. You have already used functions that come with Python: `print`, `len`, `range`, `type`, `str`. Now you are going to write your own, with the word `def` (“define”). The first is the time format, which in Lesson 2 was written as an `if` block inside the program. Save `fig03_08.py`:

```python
# fig03_08.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


print(formatear_tiempo(87))
print(formatear_tiempo(999))
print(formatear_tiempo(1000))
print(formatear_tiempo(2300))
print(formatear_tiempo(None))
```

```text
$ python fig03_08.py
87ms
999ms
1.0s
2.3s
—
```

This figure has two clearly separate parts, and understanding the separation is the most important thing in the section. **The definition** is the first six lines, from `def` to the last `return`: they explain to Python what `formatear_tiempo` does, but **do not execute it**. It is like writing a recipe on a card: the recipe exists, but nobody has cooked anything. **The calls** are the last five lines: each `formatear_tiempo(...)` asks Python to execute the recipe with a concrete piece of data, and that is when the work is done. If you removed the calls, the program would run without printing anything.

The `def` line has four parts. `def` announces the definition. `formatear_tiempo` is the name (in lowercase with underscores, like a variable). Between parentheses go the **parameters**: the names the function uses to refer to the data it receives; here one, `tiempo_ms`. And at the end, the colon and the indented block, the function's **body**. A distinction of vocabulary that is much confused: the **parameter** is the name that appears in the definition (`tiempo_ms`), and the **argument** is the value passed in the call (the `87`, the `999`). Every time the function is called, the arguments are assigned to the parameters and the body is executed.

The word **`return`** does two things at once: it **ends the function at that point** and **hands a value** to whoever called it. That is why the function above needs no `elif` or `else`: if `tiempo_ms` is `None`, the first `return` ends the function and the following lines are never executed; if it is not, it continues with the next question. Compare it with the Lesson 2 version: it does the same, with fewer branches, because each `return` already closes the path. The value it returns can be printed, stored in a variable, or used inside another expression, like any other value.

The cases in the output are the five you will test all course long: 87 is `87ms`; 999 is `999ms` (still less than a second); **1000 is `1.0s`**, right at the edge; 2300 is `2.3s`; and `None`, which has no time, is the long dash.

#### 3.2.2 Printing is not returning

A classic beginner error is confusing two things that look alike on screen: **printing** a value and **returning** it. `print` shows something in the terminal and that is the end of it; `return` hands the value to the code that called the function, which can do with it what it wants. Save `fig03_09.py` to see it:

```python
# fig03_09.py
def decir_tiempo(tiempo_ms: int) -> None:
    print(f"{tiempo_ms}ms")


def dar_tiempo(tiempo_ms: int) -> str:
    return f"{tiempo_ms}ms"


a = decir_tiempo(87)
b = dar_tiempo(87)
print(a)
print(b)
print(type(a))
print(type(b))
```

```text
$ python fig03_09.py
87ms
None
87ms
<class 'NoneType'>
<class 'str'>
```

The first line of the output (`87ms`) was printed by `decir_tiempo` when it was called, inside its body; nothing more. But `a`, what that function **returned**, is `None`: a function that has no `return` returns `None` automatically. In contrast, `dar_tiempo` printed nothing; it returned the text, and `b` stores it. That is why the next two lines print `None` and `87ms`, and the types are `NoneType` and `str`. The practical rule: **a function that calculates something should return it, not print it**, and the caller decides whether to print it. A function that prints instead of returning is hard to reuse and harder to test: Lesson 8 tests functions by comparing what they return with what they should have returned, and what is only printed can also be checked, but you have to capture what comes out on screen (Lesson 11 does it) instead of comparing a value.

#### 3.2.3 Default values and keyword arguments

Sometimes a parameter almost always has the same value. Instead of requiring it in every call, it can be given a **default value** in the definition, with an equals sign: `umbral_ms: int = UMBRAL_LENTO_MS`. If the call does not pass it, that value is used; if it does, the new one is used. And when a call has many arguments, they can be written as **keyword arguments**, by name (`umbral_ms=100`) so as not to depend on the order and so that it reads what each one is. [The official tutorial explains them with more examples](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions). Save `fig03_10.py`, which is the Lesson 2 classification turned into a function:

```python
# fig03_10.py
UMBRAL_LENTO_MS = 1000


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


print(clasificar(200, 142))
print(clasificar(200, 999))
print(clasificar(200, 1000))
print(clasificar(200, 2300))
print(clasificar(503, 95))
print(clasificar(None, None))
print(clasificar(200, 142, umbral_ms=100))
print(clasificar(codigo=200, tiempo_ms=2300))
```

```text
$ python fig03_10.py
ARRIBA
ARRIBA
LENTO
LENTO
CAIDO
CAIDO
LENTO
LENTO
```

The definition follows the `revisor`'s four rules, in the same order as Lesson 2: first, with no code or with an error code, CAIDO; then, LENTO if there was a response and the time reached the threshold; if not, ARRIBA. The question `tiempo_ms is not None and ...` has the `and` in that order for the same reason as always, and since `tiempo_ms` admits `None` in its annotation, the program protects itself although, in practice, a service that answered always carries its time. The signature was split across three lines because it did not fit in one: that is how Python's automatic formatter writes it (Lesson 8 introduces it), and it is normal when the parameter list is long.

The first six calls are the cases of the rules table, in the order of the output: ARRIBA, ARRIBA, **LENTO at the 1000 edge**, LENTO, CAIDO because of code 503 (even though it answered in 95 ms), and CAIDO because there was no response. In the seventh, `umbral_ms=100` **overrides the default value** for that call only: 142 ms is already slow if the limit is 100. In the eighth, both arguments go by name, and they can be written in any order. If you forget an argument that has no default value, Python complains with `TypeError: clasificar() missing 1 required positional argument: 'tiempo_ms'`: “`clasificar()` is missing one required positional argument.”

#### 3.2.4 Simple type annotations

You will have noticed that the parameters and the functions carry things like `: int | None` and `-> str`. They are called **type annotations** and they say what type of value is expected and what type the function returns. They are written like this:

- `tiempo_ms: int` — this parameter is an integer.
- `tiempo_ms: int | None` — this parameter is an integer **or** `None` (the bar is read “or”). It is the way of saying “there may be no data.”
- `-> str` — the function returns a text.
- `-> None` — the function returns nothing useful (it returns `None`).
- `caidos: list[str]` — a list of texts. The brackets say what is inside the list.

A fact you already saw in Lesson 0 and that is worth repeating: **Python does not enforce annotations at run time**. If you call `clasificar("hola", "mundo")`, the program does not complain about the types (it complains, perhaps, further on, for another reason). Annotations serve two readers: people, who understand what each function expects without reading its body, and checking tools, which verify them without running the code. The syntax arrived with [PEP 3107](https://peps.python.org/pep-3107/), in Python 3.0, which left deliberately undefined what they were for; [PEP 484](https://peps.python.org/pep-0484/) gave them their current use, types, and says in so many words that “no type checking happens at runtime”: when running, no type is checked. The tool that checks them (`mypy`) arrives in Lesson 8; until then you write them because they help reading and because it is much easier to write them when a function is born than to add them afterwards.

#### 3.2.5 A complete `revisor` in a single file

With functions you can now assemble the traversal. Two more functions are missing: one that builds the row (`linea`) and another that puts everything together for one service (`revisar`). And the header, which is also a function, so it is written only once. Save `fig03_11.py`, which gathers everything in one file:

```python
# fig03_11.py
UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(nombre: str, estado: str, tiempo_ms: int | None, detalle: str) -> str:
    tiempo = formatear_tiempo(tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str, codigo: int | None, tiempo_ms: int | None) -> str:
    estado = clasificar(codigo, tiempo_ms)
    if codigo is None:
        detalle = "sin conexión"
    else:
        detalle = str(codigo)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    print(encabezado())
    for i in range(len(NOMBRES)):
        print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))


main()
```

```text
$ python fig03_11.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Read the figure from the bottom up, because that is how you understand how the functions lean on each other. At the end, `main()` is the call that sets everything in motion; `main` is the name that by custom is given to the function that starts the program. Inside `main`, the loop `for i in range(len(NOMBRES))` traverses the positions of the parallel lists and, on each turn, calls `revisar` with the name, the code, and the time of that position. `revisar` does three things: it asks `clasificar` for the status, calculates the detail with the same `if`/`else` as Lesson 2 (the code as text, or “sin conexión”), and passes it all to `linea`, which builds the row with the help of `formatear_tiempo`. Each function does **one thing**, has a name that says which, and can be tested on its own.

There are two details worth noting. One: the constants (`UMBRAL_LENTO_MS` and the three lists) are at the start of the file and the functions do not receive them as arguments. A function can **read** variables that are defined outside it; section 3.3 explains when and when not. Two: the 1000 in `formatear_tiempo` (the milliseconds in a second) and `UMBRAL_LENTO_MS` (the limit of what is slow) are still different things, just as in Lesson 2. And remember where the `if`/`else` of `revisar` comes from: when the code is `None`, the detail is “sin conexión,” and the error code is shown as it is, like `503`.

The first session ends here. What you take away: a program that traverses the four services and, to change the threshold or the time format, has a single place to touch.

### 3.3 Names: where each variable lives, and `==` versus `is`

#### 3.3.1 Local and global

When Python sees a name, it needs to know **which variable it refers to**. The rule is called *scope*, and [it is in the official tutorial](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces). For this lesson, two kinds of names are enough:

- **Global**: the one created at the file level, outside any function. `UMBRAL_LENTO_MS` and `NOMBRES` are global.
- **Local**: the one created **inside** a function, including its parameters. It exists only while the function executes, and disappears when it ends. Each call to the function creates its own local names, separate from those of the other calls.

A function can **read** global names without a problem, but a function's local ones are not visible from outside. Save `fig03_12.py`:

```python
# fig03_12.py
UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    limite = UMBRAL_LENTO_MS
    return tiempo_ms >= limite


print(es_lento(2300))
print(es_lento(142))
```

```text
$ python fig03_12.py
True
False
```

Inside `es_lento`, `UMBRAL_LENTO_MS` is global and is read naturally; `tiempo_ms` and `limite` are local. Outside the function, `limite` does not exist. If you add a `print(limite)` line at the end of the program, Python stops with this error (try it and check that your screen says the same):

<!-- frag: prueba_ambito.py -->
```python
UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    limite = UMBRAL_LENTO_MS
    return tiempo_ms >= limite


print(es_lento(2300))
print(limite)
```

```text
True
Traceback (most recent call last):
  File "prueba_ambito.py", line 10, in <module>
    print(limite)
          ^^^^^^
NameError: name 'limite' is not defined
```

The last line is the one that rules: `NameError`, the name `limite` is not defined. The first line of the output, `True`, is the one that `es_lento(2300)` managed to print before the crash. This is the way Python tells you “at this place in the program, that name does not exist,” and it is the second most common beginner error after the missing colon. It is almost always one of three things: you misspelled the name (remember that capitals count), you used the name before creating it, or you created it inside a function and are looking for it outside.

#### 3.3.2 Assigning inside a function creates a local name

There is a scope rule that surprises almost everyone, and that produces the error in the next section. What decides whether a name is local or global **is not whether it exists outside, but whether the function assigns it a value somewhere in its body**. If inside the function there is an assignment to `total` (with `=` or with `+=`, which is an assignment in disguise), Python decides, before executing anything, that `total` is **local throughout that function**. Even if a global `total` exists, the function does not touch it: it uses a local one, and if you read it before assigning it, it has no value yet.

This, which looks like a whim, protects your programs: a function that changes global variables without it being noticed makes the program impossible to understand (who changed `total`?). The correct way for a function to affect the rest of the program is the one you already know: **receive what it needs as parameters and return what it calculated**. Python has a word, `global`, that allows the opposite, and I mention it only so you recognize it when you see it in someone else's code. It is not used in this course.

#### 3.3.3 `==` versus `is`

Python has two ways of asking whether two things are “the same,” and they mean different things:

- **`a == b`** asks whether **they have the same value**: are they equal?
- **`a is b`** asks whether **they are the same object**: are they literally the same thing in memory, the very same one?

There is a useful analogy: two 100-peso bills are equal in value (`==`), but they are not the same bill (`is`). Save `fig03_13.py`:

```python
# fig03_13.py
a = [200, 142]
b = [200, 142]
c = a

print(a == b)
print(a is b)
print(a is c)
```

```text
$ python fig03_13.py
True
False
True
```

`a` and `b` are two **different** lists with the same contents: they are equal (`True`) but they are not the same one (`False`). In contrast, `c = a` does not copy the list: it makes `c` **another name for the same list**, and that is why `a is c` is `True`. (What happens when that list changes, and how a real copy is made, is the topic of “copy versus reference” in Lesson 4.)

So, when is each one used? **Almost always `==`**, to compare values: codes, texts, times. **`is` is reserved for `None`**: since there is only one `None` in the program, the right question is whether the value *is* that object, and that is why Lesson 2 had you write `codigo is None`. It is what the [style guide](https://peps.python.org/pep-0008/#programming-recommendations) asks for. With `True` and `False` there is not even a need to compare: if `activo` is already a boolean, you write `if activo:`, and the same guide calls `if activo == True:` incorrect and `if activo is True:` worse.

The danger is in using `is` with numbers or texts, because sometimes it **seems to work**. Python, for efficiency, reuses the same object for small integers: [the documentation says it keeps one for each integer between -5 and 256](https://docs.python.org/3/c-api/long.html#c.PyLong_FromLong). This is a detail of the CPython implementation, the Python you use, and not a promise of the language. The REPL shows it:

```pycon
>>> a = 100
>>> b = 100
>>> a is b
True
>>> a = 1000
>>> b = 1000
>>> a is b
False
```

With 100 the comparison comes out right by accident; with 1000, wrong. A comparison with `is` that works with some numbers and not with others is an error waiting for its day. Python warns you when it sees something like this. If you save the following program and run it, it works, but first it prints a warning:

<!-- frag: prueba_is.py -->
```python
codigo = 200
if codigo is 200:
    print("contestó bien")
```

```text
prueba_is.py:2: SyntaxWarning: "is" with 'int' literal. Did you mean "=="?
  if codigo is 200:
contestó bien
```

It is a `SyntaxWarning`, a warning, not an error: the program went on and finished fine. Read it anyway. It says exactly what you did wrong and what you meant to do: `"is"` with a literal number, “did you mean `==`?”. Warnings are Python's way of telling you something that does not blow up today but may lie to you tomorrow.

### 3.4 Modules: splitting the program into files

#### 3.4.1 A file is a module

A hundred-line program fits in one file; a thousand-line one no longer reads well. The age-old solution is to split it: each file keeps a single kind of thing, and the others use it. In Python, **every `.py` file is a *module***, and one file uses another with the word **`import`**. Python also ships hundreds of already-written modules, the *standard library*, which are imported the same way (for example, `statistics`, for basic statistics).

There are two ways to import, and both appear in the `revisor`:

- **`import modulo`**: brings in the whole module, and its names are used with the module's prefix: `modulo.nombre`. It is the form that makes clearest where each thing comes from.
- **`from modulo import nombre1, nombre2`**: brings in just those names, and they are used directly, without a prefix. It is convenient when you only need one or two things.

When Python imports a module, according to [the modules documentation](https://docs.python.org/3/tutorial/modules.html#the-module-search-path), it first checks whether it is one of the few modules **built in** to the interpreter itself (like `sys`); if it is not, it looks for it **in the folder of the file it is running** and then in the standard library and in the places where `pip` installs things. That is why, for `import formato` to work, `formato.py` has to be in the same folder as `revisor.py`. The first time you import a module, Python also translates it to *bytecode* (remember Lesson 0) and stores the result in a folder called `__pycache__` next to it, so that next time it loads faster. That folder appears on its own; do not edit it or store it in any repository.

#### 3.4.2 `if __name__ == "__main__":`

A file can be two things: a **program** that is run (`python revisor.py`) or a **module** that another file imports. Sometimes it is both. A way of telling the two cases apart is needed, because when someone imports your module they do not want the program to start by itself. Python solves it with a special variable, `__name__` (with two underscores on each side, which are read “dunder”): **it is `"__main__"` when the file is being run directly, and it is the module's name when it was imported**. [The documentation of the `__main__` module](https://docs.python.org/3/library/__main__.html) explains that behavior and the idiom that takes advantage of it. Save the two files of figure `fig03_14`, in a folder with that name:

```python
# fig03_14/medidas.py
print("medidas.py: __name__ vale", __name__)


def segundos(tiempo_ms: int) -> float:
    return tiempo_ms / 1000


if __name__ == "__main__":
    print("medidas.py se está ejecutando directamente")
    print(segundos(2300))
```

```python
# fig03_14/uso.py
import statistics

import medidas

print("uso.py: __name__ vale", __name__)
print(medidas.segundos(87))
print(statistics.mean([142, 2300, 87]))
```

Run each file separately, from the `fig03_14` folder:

```text
$ cd fig03_14
$ python medidas.py
medidas.py: __name__ vale __main__
medidas.py se está ejecutando directamente
2.3
$ python uso.py
medidas.py: __name__ vale medidas
uso.py: __name__ vale __main__
0.087
843
```

When `medidas.py` is run directly, `__name__` is `__main__`, and that is why the `if` at the end holds and the two lines below are printed. When `uso.py` is run, the `import medidas` makes Python **execute `medidas.py` from top to bottom once**, and this time `__name__` is `medidas`, the module's name, so the `if` does not hold and the two final lines do not come out. Then `uso.py` goes on, with its own `__name__` being `__main__`, and uses `medidas.segundos` with the module's prefix. The last line uses a standard library module: `statistics.mean` calculates the list's average, and gives 843, the figure that in `fig03_06` came out with `.0` because of dividing by hand.

That is what the idiom means:

```text
if __name__ == "__main__":
    main()
```

“If this file is being run as a program, call `main()`.” If instead someone imports it, it does nothing, and the functions remain available. It is a habit of almost every serious Python program, and it is the one that closes the `revisor` below.

#### 3.4.3 Splitting the `revisor` into two files

With all that, the `revisor` ends up split into two modules with a clear division of responsibilities. `formato.py` keeps **everything to do with how the table looks** (the time format, the header, and the row). `revisor.py` keeps **everything to do with checking** (the data, the classification, and the traversal), and imports from `formato` what it needs. This is the lesson's project figure: a `fig03_15` folder with two files. It is the state your `~/curso-python/revisor/` ends up in at the end of the lesson, and the starting point of Lesson 4.

```python
# fig03_15/formato.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(nombre: str, estado: str, tiempo_ms: int | None, detalle: str) -> str:
    tiempo = formatear_tiempo(tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

```python
# fig03_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str, codigo: int | None, tiempo_ms: int | None) -> str:
    estado = clasificar(codigo, tiempo_ms)
    if codigo is None:
        detalle = "sin conexión"
    else:
        detalle = str(codigo)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    print(encabezado())
    for i in range(len(NOMBRES)):
        print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))


if __name__ == "__main__":
    main()
```

```text
$ cd fig03_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Notice three things. **First**, `from formato import encabezado, linea` brings in only two of the three functions of `formato.py`: `formatear_tiempo` is not used in `revisor.py` (`linea` uses it, inside), and there is no need to bring it in. **Second**, the program prints exactly the same table as `fig03_11`, the one-file version: splitting a program does not change what it does, only where each piece lives. **Third**, the last line is no longer a bare `main()` but the idiom from the previous section; now, if in the future another file imports `revisor`, the table will not be printed by accident. It is exactly what you will need when, later on, you write tests that import your functions.

After running it, look at what appeared in the folder:

```console
$ ls
formato.py  __pycache__  revisor.py
```

That `__pycache__` is the one Python created when importing `formato`; there it stored the *bytecode* version. (The order in which `ls` arranges the names depends on your terminal's language setting, so it may come out different for you.) If inside it you see a file `formato.cpython-312.pyc`, the `312` is the Python version that generated it; with another version, the number changes.

One last design detail: `formato.py` knows **nothing** about services. It only receives a name, a status, a time, and a detail, and returns text. That ignorance is a virtue: the format module can stay almost the same when, in lessons 4 and 5, the data changes shape.

## The error you will see

This lesson has two errors of its own, and both are better learned by provoking them. Both are copied from a real run. And a reminder for reading any *traceback*: the last line says **what** happened; those above, **where**, from the most recent (bottom) to the oldest (top) in the chain of calls.

### `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`

It is the error of section 3.3.2. Save this program, which tries to accumulate a total from inside a function, and run it:

<!-- frag: prueba_total.py 312-distinto -->
```python
total = 0


def sumar_tiempo(tiempo_ms: int) -> None:
    total += tiempo_ms


sumar_tiempo(142)
print(total)
```

```text
Traceback (most recent call last):
  File "prueba_total.py", line 8, in <module>
    sumar_tiempo(142)
    ~~~~~~~~~~~~^^^^^
  File "prueba_total.py", line 5, in sumar_tiempo
    total += tiempo_ms
    ^^^^^
UnboundLocalError: cannot access local variable 'total' where it is not associated with a value
```

A note on this output: it is the one from Python 3.14. In Python 3.12 the line of the call (`sumar_tiempo(142)`) does not carry the `~~~~^^^^^` marks below it; everything else, and in particular the last line, is identical. It is a good example of why reading starts from the bottom.

The last line says: the local variable `total` cannot be accessed because it has no value associated yet. The two above say **where**: inside `sumar_tiempo`, on line 5, which is `total += tiempo_ms`; and that function was called from line 8 of the program. Why does it fail? Because `total += tiempo_ms` is an assignment (it is equivalent to `total = total + tiempo_ms`), and by the rule in section 3.3.2 that makes `total` a **local** variable of the entire function; but to add, the function needs to read the current value of `total`, and the local `total` has none yet. The `total = 0` outside is another variable, and the function does not even look at it.

The fix is the one prescribed by the golden rule of functions: let it receive what it needs and return what it calculates. For example, `def sumar_tiempo(total: int, tiempo_ms: int) -> int: return total + tiempo_ms`, and in the program, `total = sumar_tiempo(total, 142)`. [The official documentation has a frequently-asked-questions entry for this exact case](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value), and [the one for `UnboundLocalError`](https://docs.python.org/3/library/exceptions.html#UnboundLocalError) defines it as the error that occurs when a reference is made to a local variable in a function that has no value yet.

### The list that remembers previous calls

This is not an error with a message, and that is why it is worse: the program does not crash, it **gives a wrong answer without warning**. It is one of Python's most famous traps. Save this program, which keeps count of the down services, and run it:

<!-- frag: prueba_recuerda.py -->
```python
def registrar_caido(nombre: str, caidos: list[str] = []) -> list[str]:
    caidos.append(nombre)
    return caidos


print(registrar_caido("reportes"))
print(registrar_caido("facturacion"))
print(registrar_caido("notificaciones"))
```

```text
['reportes']
['reportes', 'facturacion']
['reportes', 'facturacion', 'notificaciones']
```

Each call was independent: none passed a list to the function. You expected to see `['reportes']`, `['facturacion']`, and `['notificaciones']`. Instead, the list **accumulates** what earlier calls put in. It is as if the function had a memory.

The explanation comes from when a default value is evaluated: **just once, when Python executes the `def`, not each time the function is called**. The `[]` in `caidos: list[str] = []` is created once, when the function is defined, and stays stored next to it; each call that does not pass its own list uses **that same list**, and `.append` changes it in place (remember: lists are mutable). So, what the first call put in, the second one finds. [The official tutorial warns about it with this very example](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values), and [the FAQ](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects) explains why it is that way.

The rule is: **never use a list (or a dictionary, or any other mutable value) as a default value**. The correct pattern uses `None` as a signal for “nothing was passed to me” and creates the list inside the function, where a new one is created on every call. Save `fig03_16.py`:

```python
# fig03_16.py
def registrar_caido(nombre: str, caidos: list[str] | None = None) -> list[str]:
    if caidos is None:
        caidos = []
    caidos.append(nombre)
    return caidos


print(registrar_caido("reportes"))
print(registrar_caido("facturacion"))
historial = []
registrar_caido("reportes", historial)
registrar_caido("facturacion", historial)
print(historial)
```

```text
$ python fig03_16.py
['reportes']
['facturacion']
['reportes', 'facturacion']
```

Now the first two calls are independent, as expected. And when you **do** want to accumulate, the caller says so explicitly: it creates its own list (`historial`) and passes it to the function, which uses it instead of creating one. The parameter admits `list[str] | None`, which is read “a list of texts, or nothing.” You will see this pattern (`None` by default and create inside) in other people's code very many times. And this defect is so well known that checking tools detect it on their own: `ruff`, which you will meet in Lesson 8, has a specific rule for it (B006) and can flag it before you run the program.

### `ModuleNotFoundError` and `ImportError`

The two errors of the modules section. If a module's name is misspelled, or the file is not in the folder you run from, Python does not find it:

<!-- frag: prueba_import1.py -->
```python
from formatos import encabezado

print(encabezado())
```

```text
Traceback (most recent call last):
  File "prueba_import1.py", line 1, in <module>
    from formatos import encabezado
ModuleNotFoundError: No module named 'formatos'
```

And if the module exists but the name you ask for is not in it, the error is another:

<!-- frag: prueba_import2.py -->
```python
from formato import lineas

print(lineas)
```

```text
Traceback (most recent call last):
  File "prueba_import2.py", line 1, in <module>
    from formato import lineas
ImportError: cannot import name 'lineas' from 'formato' (/home/tu_usuario/curso-python/revisor/formato.py). Did you mean: 'linea'?
```

Both messages are literal. The first says there is no module called `formatos` (in the example an extra `s` was written). The second says `formato` does exist, but has nothing called `lineas`; Python shows you the file where it looked (the path will be your machine's) and even suggests the name you seem to have wanted: `linea`. Faced with a `ModuleNotFoundError`, check three things in order: how you wrote the name, whether the file is in the folder, and whether you are standing in the right folder when you run the program.

## What gets done wrong

**Printing instead of returning.** `def total(...): print(...)` seems to work as long as you only want to see the result. Cost: when you need to use the result in another calculation, or test it, you discover the function returned `None`. Functions that calculate, return.

**Using a list as a default value.** It is the error above. Cost: data that gets mixed between calls without any error message, and that shows up in production as a report with services that should not be there.

**Changing a global variable from a function.** With `global` it can be done, and the program becomes a maze: to understand what value a variable has you have to read all the functions. If a function needs a piece of data, let it receive it; if it produces one, let it return it.

**Comparing with `is` things that are not `None`.** It may work with small numbers and fail with large ones, or give a `SyntaxWarning` like the one above. Comparing values is `==`.

**A `while` without progress.** If the block does not bring the condition closer to being false, the program never ends. Before running a `while`, locate the line that advances it.

**Writing `range(len(NOMBRES))` and then touching only one list.** It is the fragility of parallel lists: if you add a service to `NOMBRES` and forget to add its code or its time, the program fails (with an `IndexError`) or, worse, prints data that is not that service's. Exercise 1 shows it in action. There is no fix with what you know today: the fix is to store each service as a single thing, and that is the topic of Lesson 4.

**Naming your file like a standard library module.** If you create `statistics.py` in the project folder and another file does `import statistics`, Python finds yours **first** (remember the search order: the program's folder comes before the standard library; only modules built in to the interpreter, like `sys`, are spared, because they are searched before any folder) and the real module's names stop existing. The symptom is an error of the kind `AttributeError: module 'statistics' has no attribute 'mean'` (recent versions of Python add a suggestion at the end to rename the file), and it is very bewildering because your own code has no error. Avoid the names `statistics`, `random`, `json`, `string`, `types`, and the other standard library ones.

**Putting a bare `main()` at the end of a module.** When another file imports it, the program will start by itself. The `if __name__ == "__main__":` idiom exists for that.

**Copying and pasting a function instead of importing it.** If the same code is in two files, sooner or later one of the two gets fixed and the other does not. What is shared is imported.

## Exercises

### Exercise 1 — Adding a service and forgetting a list

In `fig03_15/revisor.py`, add `facturacion` (code 503, time 95 ms) to the lists. Do it twice. **First time:** add `"facturacion"` to `NOMBRES` and `503` to `CODIGOS`, but **forget** `TIEMPOS_MS`. Predict what is going to happen before running it. **Second time:** add the three pieces of data but in a different order: `503` at the **start** of `CODIGOS` and `95` at the end of `TIEMPOS_MS`. Predict, and then compare with what you see. Which of the two failures is more dangerous and why?

### Exercise 2 — Counting the down services

Write a function `contar_caidos(codigos: list[int | None]) -> int` that receives the list of codes and returns how many services are down according to the usual rule (no code, or a code of 400 or more). Test it with `CODIGOS` (it must give 1), with `[200, 503, None]` (it must give 2), and with an empty list `[]` (it must give 0). It must **return** the number, not print it.

### Exercise 3 — Provoking the lesson's errors

In copies of your project, provoke one by one: (a) using a local name from outside its function; (b) a `total += x` inside a function; (c) the list that remembers; (d) `from formato import lineas`; (e) removing `formato.py` from the folder. For each one, copy the last line of the message, write what it means and what the fix is.

### Exercise 4 — The slowest service

Write a function `mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None` that returns the **name** of the service with the greatest time, ignoring those that did not answer (the ones with `None`). If none answered, it must return `None`. With `NOMBRES` and `TIEMPOS_MS` it must return `"inventario"`. Hint: traverse by position, keep in two variables the best time seen so far and its name, and update them when you find a greater time. Think about what value those variables should start with.

## Solutions

### Solution 1

First failure, with `TIEMPOS_MS` shorter than the other two lists: the loop goes through the first four services without a problem and on reaching the fifth, `TIEMPOS_MS[4]` does not exist.

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
Traceback (most recent call last):
  File "revisor.py", line 36, in <module>
    main()
    ~~~~^^
  File "revisor.py", line 32, in main
    print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))
                                          ~~~~~~~~~~^^^
IndexError: list index out of range
```

(It is the output of Python 3.14; in 3.12 the line of `~~~~^^` marks below `main()` does not appear, and everything else, including the marks of `TIEMPOS_MS[i]` and the last line, is identical.)

The last line says the index is out of the list's range: you asked for a position that does not exist. It is the error that parallel lists produce when one comes up short.

Second failure, with the data in a different order: the program **does not fail**, and prints this:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO      142ms  503
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    ARRIBA         —  200
facturacion CAIDO       95ms  sin conexión
```

Look at how each row turned out. `catalogo` appears CAIDO with code 503, even though it works. `reportes`, which did not answer, appears ARRIBA with code 200 (and without a time, because its time really was `None`). `facturacion` appears with “sin conexión,” when in reality it answered with a 503 in 95 ms. The codes are shifted one position relative to the times, and nothing warns you. This is the more dangerous one: the first failure is visible; the second produces a report that looks valid and lies. That is the reason why in Lesson 4 each service will stop being three loose numbers in three lists and become **a single thing** that cannot get out of step.

### Solution 2

```python
def contar_caidos(codigos: list[int | None]) -> int:
    caidos = 0
    for codigo in codigos:
        if codigo is None or codigo >= 400:
            caidos += 1
    return caidos
```

With `CODIGOS` it gives `1`, with `[200, 503, None]` it gives `2`, and with `[]` it gives `0`: the loop does not turn at all and returns the value the counter started with. The `return` goes **outside** the loop (at the `for`'s margin); if you put it inside, the function would end on the first turn. And the condition is the same as in `clasificar`: first `is None`, so that `None >= 400` is never evaluated.

### Solution 3

(a) `NameError: name 'limite' is not defined` (or the name you use): the name is local and outside it does not exist. Fix: return the value with `return` and store it in an outside variable.

(b) `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`: the assignment makes `total` local. Fix: receive it as a parameter and return the new one.

(c) The list that accumulates between calls, with no message at all. Fix: `None` by default and create the list inside.

(d) `ImportError: cannot import name 'lineas' from 'formato' (...)`: the module exists but does not have that name. Fix: write `linea`.

(e) Without `formato.py` in the folder: `ModuleNotFoundError: No module named 'formato'`. Fix: put the file where `revisor.py` is, or run the program from the folder that contains it.

### Solution 4

```python
def mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None:
    mejor_nombre = None
    mejor_tiempo_ms = None
    for i in range(len(nombres)):
        tiempo_ms = tiempos_ms[i]
        if tiempo_ms is None:
            continue
        if mejor_tiempo_ms is None or tiempo_ms > mejor_tiempo_ms:
            mejor_nombre = nombres[i]
            mejor_tiempo_ms = tiempo_ms
    return mejor_nombre
```

With the `revisor`'s data it returns `"inventario"`; with `[None, None]` it returns `None`. The key is in the starting value: both variables start at `None`, which means “I have not seen anyone yet,” and that is why the question `mejor_tiempo_ms is None or ...` goes first: the first service that answered always wins, and from there on comparison starts. If you had started `mejor_tiempo_ms` at 0 it would work with this data, but it would give an absurd answer with a list of negative times, and you would have to decide what name to return when nobody answered. `None` expresses that without inventing anything.

## How I know I got it

- [ ] From `fig03_15` (or from your `revisor/` folder), `python revisor.py` prints the header and the four rows of the table, identical to those in the figure, including the long dash and “sin conexión” in the one for `reportes`.
- [ ] `python fig03_11.py` (everything in one file) and `python revisor.py` (in two files) print exactly the same.
- [ ] When you change `UMBRAL_LENTO_MS` to 100 in `revisor.py`, `catalogo` becomes LENTO without your touching any other line.
- [ ] After running the program there is a `__pycache__` folder next to `formato.py`, and you can say why.
- [ ] You can provoke `UnboundLocalError` and `ImportError` on purpose and say, looking only at the last line, what happened.
- [ ] You can explain in your own words the difference between `print` and `return`, between `==` and `is`, and between a parameter and an argument.
- [ ] You can explain why the `registrar_caido` function from the errors section “remembered” and why the `None` version does not.

## Summary

Answer without looking at the lesson:

1. From what number do a list's positions start, and what is the last position of a list of `n` elements?
2. What does `range(len(NOMBRES))` produce if `NOMBRES` has four elements? And what does `enumerate` hand over on each turn?
3. What risk does a `while` have that a `for` does not, and how do you avoid it?
4. What is the difference between defining a function and calling it? What is a parameter and what is an argument?
5. What does a function with no `return` return? Why should a function that calculates return and not print?
6. When is a default value evaluated, and why does that make a list as a default value “remember”? What is the correct pattern?
7. What decides whether a name is local or global inside a function? Why does `total += x` fail in a function?
8. What question does `==` ask and what question does `is` ask? With what value is `is` used?
9. What value does `__name__` have when you run a file directly, and which when it is imported? What is that for?
10. Why are the `revisor`'s three parallel lists a bad idea, and why are they used today?

## Further reading

- [The Python tutorial, “More Control Flow Tools”](https://docs.python.org/3/tutorial/controlflow.html) — `for`, `range`, `break` and `continue`, `def`, default values, and keyword arguments, in a single chapter. Official documentation. Accessed on October 7, 2026.
- [The Python tutorial, “Modules”](https://docs.python.org/3/tutorial/modules.html) — `import`, `from ... import`, the search order, and `__pycache__`. Accessed on October 7, 2026.
- [Programming FAQ](https://docs.python.org/3/faq/programming.html) — the traps of this lesson (the mutable default value, `UnboundLocalError`, `is` versus `==`), with the Python team's own explanation. Accessed on October 7, 2026.
- [PEP 8, the Python style guide](https://peps.python.org/pep-0008/) — names, indentation, and the use of `is` with `None`; it is the guide this course follows. Accessed on October 7, 2026.
