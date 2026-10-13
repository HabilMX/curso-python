# Lesson 4 — Collections

**Time:** 2 × 90 min (the first session runs to the end of 4.2; the second starts at 4.3)

**What you build:** the `revisor` without parallel lists: each service's data travels together, in a dictionary that is looked up by the service's name

**What you learn:** `list`, `tuple`, `dict`, and `set`; comprehensions; copy versus reference; not changing what you are traversing; `KeyError` and `IndexError`

**Where you come from.** You bring the project from [Lesson 3](03-bucles-funciones-modulos.md): two files, `formato.py` and `revisor.py`. The first knows how to format the time and build the header and each row; the second keeps the data, classifies each service, and traverses the four to print them. It works, and the table comes out right. But the services' data lives in **three parallel lists**, `NOMBRES`, `CODIGOS`, and `TIEMPOS_MS`, which correspond only by position: name number 2 goes with code number 2 and with time number 2. In the Lesson 3 exercise you added `facturacion` to two lists, forgot the third, and saw the `IndexError` or the wrong row that this produces. That fragility is what gets removed today.

**What this lesson does not do.** It does not yet give each service a shape of its own with a name (a `Servicio`, an `Estado`): that is [Lesson 5](05-modelo-de-datos.md), which builds on everything from today. Nor does it read the configuration from a file (the services are still written by hand in the code; [Lesson 6](06-errores-archivos-datos.md) takes them out of there), it does not catch errors with `try`, and it does not query any internet address: the codes and the times come from a simulated table inside the program.

You work in your `~/curso-python/revisor/` folder. The lesson's small programs (the ones that are not part of the project) you can save in a `practica/` subfolder inside it, so they do not get mixed with the `revisor`'s files. All the commands assume that the virtual environment from Lesson 1 is active, so you type `python`, not `python3`.

## By the end you will be able to

- Choose between list, tuple, dictionary, and set according to what you are going to store and how you are going to look it up, and write each one with its type annotation (`list[str]`, `dict[str, int | None]`, `set[str]`).
- Read an `IndexError` and a `KeyError`, say which position or which key was missing, and use `.get` when absence is a normal case and not an error.
- Rewrite a loop that builds a list as a comprehension, and know when it is better to leave it as a loop.
- Predict what happens with `b = a` when `a` is a list, make shallow and deep copies, and explain why changing a list while you traverse it gives wrong results without warning.
- Rewrite the `revisor` without parallel lists: a dictionary that stores, for each name, a tuple with its code, its time, and its error, and a traversal that no longer depends on three lists being aligned.

## The why before the how

Open the `revisor.py` from Lesson 3 and look at how `inventario` is represented: the text `"inventario"` in `NOMBRES[1]`, the number `200` in `CODIGOS[1]`, and the number `2300` in `TIEMPOS_MS[1]`. Three values that belong to one single thing, stored in three different places. To add a service you have to remember to touch three lists and to touch them in the same order, and Python does not warn you if you get it wrong: if you forget the third, the program fails on reaching the fifth service, or worse, it pairs one service's code with another's time and the table comes out well formatted and **wrong**. It is the usual rule in programming: a piece of data written in two places ends up differing.

The solution is **a single place for each piece of data**, and for that you need ways of grouping values. Python ships four (list, tuple, dictionary, and set), each designed for a different question: “in what order are they?”, “which one is the one for this name?”, “have I seen this value?”. This lesson presents them one by one (4.1), together with the two tools with which they are built and handled without surprises: comprehensions (4.2) and care with copies (4.3). At the end (4.4) you use them to rewrite the `revisor`: each service's data comes to live together, under its name, and the three parallel lists disappear. The next lesson takes the missing step, giving the things of the problem a name of their own (a `Servicio`, an `Estado`), and to take it, it needs everything from today.

At the end of the lesson, the `revisor` will do this:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

It is exactly the table from Lesson 3, letter for letter, and that is on purpose: what changes today is not what the program prints, but how it stores its data inside. A change like this, which leaves the result identical and improves the structure, has an enormous advantage: it is checked by comparing the two outputs. What the program gains is not seen in the table but when modifying it, and you will check it in Exercise 3: adding a service stops being an operation on three lists that have to be touched in the same order.

## The concepts

### 4.1 The four collections

A **collection** is a value that holds other values. Python ships four for daily use, and they are told apart by two questions. The first: can it be changed after it is created? What can be changed is called **mutable**, and what cannot, **immutable**; the list, the dictionary, and the set are mutable, the tuple is not. The second: how is an element found? By its **position** (list and tuple), by its **name** (dictionary), or simply by asking whether it **is or is not** there (set). See each one with an example from the `revisor` and at the end, in 4.1.5, there is a table for deciding.

#### 4.1.1 The list: values in order

You already used the minimal list in Lesson 3: the literal with brackets, `len`, `.append`, and `lista[i]`. Here it is seen in full. A **list** keeps values in an order, can be changed, and is written between square brackets. Save the following program as `fig04_01.py` in your `practica/` folder and run it:

```python
# fig04_01.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]
print(nombres[0], nombres[3])
print(nombres[-1], nombres[-2])
print(nombres[1:3])
print(len(nombres))
print("pagos" in nombres, "gateway" in nombres)

nombres.append("facturacion")
print(nombres)
ultimo = nombres.pop()
print(ultimo, len(nombres))

tiempos_ms = [142, 2300, 87]
print(sorted(tiempos_ms), tiempos_ms)
tiempos_ms.sort()
print(tiempos_ms)
print(sum(tiempos_ms), min(tiempos_ms), max(tiempos_ms))
```

```text
$ python fig04_01.py
catalogo reportes
reportes pagos
['inventario', 'pagos']
4
True False
['catalogo', 'inventario', 'pagos', 'reportes', 'facturacion']
facturacion 4
[87, 142, 2300] [142, 2300, 87]
[87, 142, 2300]
2529 87 2300
```

Line by line:

- `nombres[0]` and `nombres[3]` ask for the first and the fourth element. The positions, which are called **indexes**, start at **0**: with four elements the valid positions are 0, 1, 2, and 3. That is why the last position of a list of `len(nombres)` elements is `len(nombres) - 1`, and not `len(nombres)`.
- `nombres[-1]` and `nombres[-2]` count from the end: `-1` is the last, `-2` the second to last. It is the convenient way of asking for “the last one” without calculating anything.
- `nombres[1:3]` is a **slice**: the elements from position 1 **up to 3 without including it**, that is, positions 1 and 2. It returns a new list with `['inventario', 'pagos']`. The “without including” is a rule that is bewildering once and afterwards is used without thinking: `nombres[1:3]` has `3 - 1 = 2` elements, and `nombres[0:len(nombres)]` is the whole list. [The Python tutorial](https://docs.python.org/3/tutorial/introduction.html#lists) explains slices with more examples.
- `len(nombres)` you already know. Together with `sorted`, `sum`, `min`, and `max` it is one of the **built-in functions**: they come with Python and are used without importing anything.
- `"pagos" in nombres` is another way of using the word `in`, the same one you saw in `for ... in`: here it answers `True` or `False` depending on whether the value **is** in the list. Careful, because with a list Python checks it element by element; with short lists it does not matter, and in 4.1.4 you will see a much faster collection for that question.
- `nombres.append("facturacion")` adds at the end, and **changes the list that already exists** (it does not create another). `nombres.pop()` removes the last element and returns it, so `ultimo` is `"facturacion"` and the list has four again. That `append` and `pop` modify the list that already exists is what “mutable” means, and it has consequences you will see in 4.3.
- `sorted(tiempos_ms)` returns a **new** sorted list and leaves the original as it was: that is why the second part of the line still shows `[142, 2300, 87]`. In contrast, `tiempos_ms.sort()` sorts **the list itself** and returns nothing (strictly, it returns `None`). [The documentation puts it this way](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types): to remind you that it acts “by side effect,” `sort` does not return the sorted list, and to ask for a new one there is `sorted`. That distinction between “changes the one I have” and “gives me a new one” reappears throughout Python, and becomes a common trap (you will see it in “What gets done wrong”).
- `sum`, `min`, and `max` add, find the smallest, and find the largest of the list's numbers: 87 + 142 + 2300 = 2529, which is the sum of times you will use in the summary.

A list can mix anything: texts, numbers, other lists. In the `revisor` it is better for each list to hold **a single kind of thing** (only names, or only times), because that way you know what to expect from each element and because the type annotations of 4.1.5 express it easily.

Now, the error. Asking for a position that does not exist:

```python
# fig04_02.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]
print(nombres[4])
```

```text
$ python fig04_02.py
Traceback (most recent call last):
  File "fig04_02.py", line 3, in <module>
    print(nombres[4])
          ~~~~~~~^^^
IndexError: list index out of range
```

Read the *traceback* as you learned in Lesson 1: from the last line upward. `IndexError: list index out of range` says the index is outside the list's range. Above, Python points you to the line and marks with a stripe of `~` and `^` the expression that failed: `nombres[4]`. The list has four elements, with positions 0 to 3, and 4 does not exist. It is the same error Lesson 3 gave you when one of the three parallel lists was shorter than the others. (Python writes the full path of your file in the *traceback*; in this lesson they are shortened to `File "fig04_02.py"` so that the text is the same for everyone, and on your screen you will see the path as it is on your computer.)

#### 4.1.2 The tuple: a fixed group of values

A **tuple** looks like a list with parentheses instead of brackets, but it has a difference that changes what it is for: it **cannot be changed**. Once created, its positions stay fixed. And the difference in use is deeper than the syntactic one: the list is “a variable number of things of the same type” (four names, or twenty), while the tuple is “a **fixed** number of things each of which means something different by its position.” The result of checking a service, for example, is always three things: the code, the time, and the error if there was one.

```python
# fig04_03.py
resultado = (200, 142, None)
print(resultado[0], resultado[1])
codigo, tiempo_ms, error = resultado
print(f"código {codigo}, tiempo {tiempo_ms}, error {error}")
print(len(resultado))

pares = [("catalogo", 142), ("pagos", 87)]
for nombre, ms in pares:
    print(f"{nombre} respondió en {ms}ms")

uno = (200,)
no_es_tupla = 200
print(type(uno), type(no_es_tupla))
```

```text
$ python fig04_03.py
200 142
código 200, tiempo 142, error None
3
catalogo respondió en 142ms
pagos respondió en 87ms
<class 'tuple'> <class 'int'>
```

- `resultado = (200, 142, None)` creates a tuple of three elements. It is read with indexes just like a list: `resultado[0]` is the code.
- `codigo, tiempo_ms, error = resultado` **unpacks**, the same thing `for i, nombre in enumerate(...)` did in Lesson 3, where each turn handed over a pair, which is in reality a tuple of two: it distributes the tuple's three elements among three names, in order. It is much more readable than `resultado[0]`, `resultado[1]`, `resultado[2]`, because each value gets a name that says what it is.
- The `for nombre, ms in pares:` is the same unpacking as in `enumerate`, now with your own pairs: each element of `pares` is a tuple of two, and `nombre` and `ms` receive its halves. You will see it again as soon as you reach dictionaries.
- A tuple of **a single element** demands the comma: `(200,)` is a tuple; `(200)` is parentheses around a number, and is simply `200`, as the `type` on the last line shows. [The tutorial warns about this case](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) as a quirk of the syntax. In practice you will almost never write it, but you will read it, and confusing it gives no warning.

If the number of names does not match the number of elements, Python rejects it instead of silently distributing too many or too few:

<!-- frag: desempaque.py -->
```python
codigo, tiempo_ms = (200, 142, None)
```

When run, the last line of the *traceback*, the one that matters, says “too many values to unpack.” In Python 3.12:

```text
ValueError: too many values to unpack (expected 2)
```

and in 3.14 it adds how many it received:

```text
ValueError: too many values to unpack (expected 2, got 3)
```

When a function returns “several things,” what it returns is a tuple: `return codigo, tiempo_ms` creates a tuple of two, and whoever calls it unpacks it with `codigo, tiempo_ms = f(...)`.

And what happens if you try to change one?

```python
# fig04_04.py
resultado = (200, 142, None)
resultado[0] = 500
```

```text
$ python fig04_04.py
Traceback (most recent call last):
  File "fig04_04.py", line 3, in <module>
    resultado[0] = 500
    ~~~~~~~~~^^^
TypeError: 'tuple' object does not support item assignment
```

`TypeError: 'tuple' object does not support item assignment`: “the tuple object does not allow assigning to a position.” It is not a failure, it is the tuple's guarantee: what it stored, stays. If you need another one with a different value, you create another tuple. That guarantee is useful for data describing a fact that already happened, like the result of a check. But notice the cost: `resultado[1]` does not say it is the time; only your memory says so. When a tuple grows to five or six elements, nobody remembers which is which. That is the limitation that the `dataclass` of Lesson 5 resolves.

#### 4.1.3 The dictionary: values with a name

Think about what `revisar` needs for the `pagos` service: not “the third element,” but “the data of `pagos`.” A **dictionary** (`dict`) stores **key: value** pairs and is looked up by the key. It is written between curly braces, and the key and the value are separated by a colon.

```python
# fig04_05.py
tiempos_ms = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
print(tiempos_ms["pagos"])
print(len(tiempos_ms))
print("pagos" in tiempos_ms, "gateway" in tiempos_ms)

print(tiempos_ms.get("gateway"))
print(tiempos_ms.get("gateway", "sin dato"))
print(tiempos_ms.get("reportes"))
print("reportes" in tiempos_ms, tiempos_ms.get("reportes"), tiempos_ms.get("gateway"))

tiempos_ms["facturacion"] = 95
for nombre, ms in tiempos_ms.items():
    print(nombre, ms)

print(list(tiempos_ms))
print(list(tiempos_ms.values()))
```

```text
$ python fig04_05.py
87
4
True False
None
sin dato
None
True None None
catalogo 142
inventario 2300
pagos 87
reportes None
facturacion 95
['catalogo', 'inventario', 'pagos', 'reportes', 'facturacion']
[142, 2300, 87, None, 95]
```

- `tiempos_ms["pagos"]` looks for the key `"pagos"` and returns its value, 87. Unlike a list, here it does not matter at what place it is: what matters is what it is called. Keys are unique (a dictionary cannot have `"pagos"` twice); values can repeat and be of any kind, even `None`, like the one for `reportes`.
- `len(tiempos_ms)` counts the pairs. `"pagos" in tiempos_ms` asks whether **the key** exists (not the value), and it is fast even if the dictionary is huge.
- `tiempos_ms.get("gateway")` is the way to ask calmly. With brackets, a key that does not exist is an error (you provoke it further down, in “The error you will see”); with `.get`, it returns `None` if it does not find it, or the value you put as the second argument: `.get("gateway", "sin dato")` returns `"sin dato"` (“no data”).
- Watch the `reportes` line, which is the trap of this method. `.get("reportes")` returns `None`... and `.get("gateway")` too. **The same answer for two different situations:** a key that does not exist, and a key that exists and is `None`. The second-to-last line makes it visible: `"reportes" in tiempos_ms` is `True` but its `.get` is `None`; `"gateway"` is not there and its `.get` is also `None`. When the difference matters, you ask first with `in`.
- `tiempos_ms["facturacion"] = 95` **adds** a pair if the key did not exist (and if it existed, replaces its value). Dictionaries, like lists, can be changed.
- `tiempos_ms.items()` hands over the pairs one by one, each as a tuple `(key, value)` (just as `enumerate` handed over pairs), and the `for nombre, ms in ...` unpacks them, as you saw in the previous section. Dictionaries **remember the order in which you added the keys**: [the documentation guarantees it](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) (“dictionaries preserve insertion order”), which is why `facturacion` comes out last.
- `list(tiempos_ms)` turns into a list what you get by traversing the dictionary directly, and that is **the keys**. It is important to remember: `for nombre in tiempos_ms:` traverses names, not pairs. `tiempos_ms.values()` hands over the values, and `tiempos_ms.keys()` exists for the keys, but it is almost never necessary to write it.

A restriction worth knowing from now on: a dictionary's key must be something that does not change. Texts, numbers, and tuples of them work; a list does not work as a key. What can be used this way is what [the glossary calls **hashable**](https://docs.python.org/3/glossary.html#term-hashable). Trying it gives a `TypeError: unhashable type: 'list'`, which you will see in 4.1.4 next to the set.

#### 4.1.4 The set: “have I seen it?”

A **set** (`set`) stores values **without repeating and without order**. It is good for two things: removing duplicates, and asking “is this value there?” very fast. When you write `{"catalogo", "pagos"}`, with braces and without a colon, it is a set.

```python
# fig04_06.py
registrados = ["catalogo", "pagos", "catalogo", "reportes", "pagos"]
unicos = set(registrados)
print(len(registrados), len(unicos))
print(sorted(unicos))

arriba = {"catalogo", "pagos"}
todos = {"catalogo", "inventario", "pagos", "reportes"}
print("pagos" in arriba)
print(sorted(todos - arriba))
print(sorted(todos & arriba))
print(sorted(arriba | {"gateway"}))
arriba.add("pagos")
arriba.add("inventario")
print(sorted(arriba))
print(type({}), type(set()))
```

```text
$ python fig04_06.py
5 3
['catalogo', 'pagos', 'reportes']
True
['inventario', 'reportes']
['catalogo', 'pagos']
['catalogo', 'gateway', 'pagos']
['catalogo', 'inventario', 'pagos']
<class 'dict'> <class 'set'>
```

- `set(registrados)` turns the list into a set and, along the way, discards the repetitions: five registered names, three distinct. This is the shortest way to count “how many different values there are.”
- The set is printed inside `sorted(...)` on purpose, and it is not an ornament: **a set has no order**, and for texts the order in which Python shows them changes from one run to another, because [the language documentation explains](https://docs.python.org/3/reference/datamodel.html#object.__hash__) that the `hash` values of texts carry an unpredictable “salt” that changes every time Python starts. When measured for this lesson, the same set `{"catalogo", "inventario", "pagos", "reportes"}` came out in different orders from one run to another, and that is why you will see `sorted` on every printing of a set: so that the output is always the same. Practical rule: **never trust the order of a set; if you need order, convert it with `sorted`**.
- The operators between sets are those of mathematics: `-` is the **difference** (what is in one and not in the other: those that are not up), `&` the **intersection** (what is in both), and `|` the **union** (everything from both). `.add` adds a value and nothing happens if it was already there, which is precisely the point: `arriba.add("pagos")` duplicates nothing.
- The last line is a classic trap. **An empty `{}` is not an empty set, it is an empty dictionary**: the brace syntax was used first for dictionaries. For an empty set, `set()`. [The tutorial stresses it](https://docs.python.org/3/tutorial/datastructures.html#sets) and the `type` above confirms it.

The elements of a set must also be *hashable*, for the same reason as dictionary keys: Python places them according to a number calculated from their value, and if the value could change, that number would too. If you try to put in a list, the message changes between versions, and it is worth seeing both:

<!-- frag: hashable.py -->
```python
datos = {["catalogo"]: 1}
```

In Python 3.12 the last line is this:

```text
TypeError: unhashable type: 'list'
```

And in 3.14, which words the warning better, it says:

```text
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

Both mean the same: a list cannot be a key. What you should remember is the word `unhashable`.

A real use in the `revisor`: detecting repeated names. A set of “the ones I have seen” and another of “the ones that repeat” solve it in a single pass. But that function uses type annotations for collections, which is next.

#### 4.1.5 Annotating collections and choosing the right one

In Lesson 3 you annotated simple types: `int`, `str`, `int | None`. With collections, **of what** the collection is gets added, between brackets: `list[str]` is “list of texts,” `set[str]` is “set of texts,” `dict[str, int | None]` is “dictionary whose keys are texts and whose values are integers or `None`,” and `tuple[int | None, int | None, str | None]` is “tuple of three elements: an integer or `None`, another integer or `None`, and a text or `None`” (the tuple annotates **each position**, because each one means something). Remember what you learned in Lesson 0: Python **does not require** annotations to hold at run time. They are documentation that someone else can check (in Lesson 8, `mypy`); today they serve to make the code say what it expects.

Here is the function that detects repeated names, with annotations, and it is the same one the `revisor`'s model will use in Lesson 5:

```python
# fig04_07.py
def nombres_repetidos(nombres: list[str]) -> set[str]:
    vistos: set[str] = set()
    repetidos: set[str] = set()
    for nombre in nombres:
        if nombre in vistos:
            repetidos.add(nombre)
        vistos.add(nombre)
    return repetidos


print(sorted(nombres_repetidos(["catalogo", "pagos", "catalogo", "reportes", "pagos"])))
print(sorted(nombres_repetidos(["catalogo", "inventario", "pagos", "reportes"])))
```

```text
$ python fig04_07.py
['catalogo', 'pagos']
[]
```

`vistos: set[str] = set()` annotates a variable when creating it: the syntax is `nombre: tipo = valor`. The annotation is needed because `set()` by itself does not say what the set is of. For each name: if it was already in `vistos`, it is added to `repetidos`; in any case it is added to `vistos`. The second call returns an empty set, which `sorted` shows as `[]`. Notice that the question `nombre in vistos` is asked of a set: it would be just as correct with a list, but with thousands of names the set answers immediately and the list would have to check them one by one.

Which one to use? You can consult this table whenever you are unsure; the answer almost always comes from the first column.

| If what you store is... | Use | Looked up by | Can it be changed? | Example in the `revisor` |
|---|---|---|---|---|
| a variable number of things of the same type, in an order | `list` | position | yes | the services to check |
| a fixed number of things, each position with its meaning | `tuple` | position | no | the trio (code, time, error) |
| data that is asked for by name | `dict` | key | yes | each service's time by its name |
| unique values, without order, about which you ask “is it there?” | `set` | membership | yes | the names already seen |

If you are torn between `list` and `set`, ask whether order matters or whether there can be repeats. If you are torn between `dict` and `list`, ask whether you are going to look up by position or by name. And if you catch yourself writing `resultado[2]` and have to remember what the 2 was, it is the sign that you need a name for that, which is the topic of Lesson 5.

### 4.2 Comprehensions

Building a new list from another is one of the most common tasks of a program, and it is always written the same way: an empty list is created, the original is traversed, it is decided whether each element goes in, and it is added with `.append`. Python has a compact form for that, the **comprehension**. Look at the two versions of the same job:

```python
# fig04_08.py
tiempos_ms = [142, 2300, 87]

lentos: list[int] = []
for tiempo_ms in tiempos_ms:
    if tiempo_ms >= 1000:
        lentos.append(tiempo_ms)
print(lentos)

lentos = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms >= 1000]
print(lentos)

textos = [f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]
print(textos)
print(", ".join(textos))

por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
respondieron = {nombre: ms for nombre, ms in por_servicio.items() if ms is not None}
print(respondieron)
sin_respuesta = {nombre for nombre, ms in por_servicio.items() if ms is None}
print(sin_respuesta)
promedio_ms = round(sum(respondieron.values()) / len(respondieron))
print(promedio_ms)
```

```text
$ python fig04_08.py
[2300]
[2300]
['142ms', '2300ms', '87ms']
142ms, 2300ms, 87ms
{'catalogo': 142, 'inventario': 2300, 'pagos': 87}
{'reportes'}
843
```

The first half is the usual loop: it creates `lentos` empty (annotated as a list of integers), traverses, filters with `if`, and appends. The second half does the same in **one line**:

```text
[ tiempo_ms   for tiempo_ms in tiempos_ms   if tiempo_ms >= 1000 ]
  ^qué pones   ^de dónde sale               ^condición (opcional)
```

It reads almost like a sentence: “build a list with `tiempo_ms`, for each `tiempo_ms` in `tiempos_ms`, if `tiempo_ms >= 1000`.” It has three parts: **what is put** in the new list (it can be the same element or a transformation of it, like `f"{tiempo_ms}ms"`), **where it comes from** (the `for`), and, optionally, **the condition** that decides whether it goes in. [The Python tutorial](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) presents it with the same structure. The `for` variable lives only inside the comprehension and does not get in the way outside.

Line by line for the rest:

- `[f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]` has no condition: it transforms each number into a text. It is a simple version of what `formatear_tiempo` did in Lesson 3.
- `", ".join(textos)` is a new text method: it **joins** the texts of a list putting between them the text on which it is called. Here, a comma and a space. You will need it in the `revisor`'s summary.
- With braces and a `key: value` you get a **dictionary comprehension**: `{nombre: ms for nombre, ms in por_servicio.items() if ms is not None}` builds a new dictionary with the services that do have a time. Notice that the right question about `None` is still `is not None`, as you learned in lessons 2 and 3.
- With braces and a single value you get a **set comprehension**: the names whose time is `None`. Only `reportes`.
- The last line is the real average of the summary. `respondieron.values()` are the times of those that answered (142, 2300, and 87); `sum(...)` adds them (2529); `len(respondieron)` is 3; the `/` bar divides and **always gives a number with decimals**, 843.0; and `round(...)` rounds it to the nearest integer, 843. All the course's averages are calculated this way, over those that answered: the fourth service has no time to average. A note on `round`: when the decimal is exactly `.5`, [Python rounds to the **even** integer](https://docs.python.org/3/library/functions.html#round), so `round(0.5)` is 0, `round(1.5)` is 2, and `round(2.5)` is also 2.

<!-- frag: redondeo.py -->
```python
print(round(0.5), round(1.5), round(2.5))
```

```text
0 2 2
```

(For the `revisor` it does not matter, because 2529 / 3 is exact, but it is worth having seen it once: it is one of those things that, if you do not know them, make you look for an error that does not exist.)

When not to use a comprehension? When it becomes hard to read. A simple condition or a simple transformation fits well; two nested `for` or three conditions, no: in that case write the loop, which can be read line by line. And never use a comprehension just for what it does on the outside (for example, to call `print` on each element): a comprehension is for **building a value**, not for executing actions.

> **The first session ends here.** You have the four collections and the comprehensions: everything needed to **store** the data in a different way. Before the second session, run the figures of 4.1 and 4.2 again and change something in each one (another service, another condition in the comprehension) to predict the result before seeing it. The second session deals with what surprises you when **sharing** that data, and ends with the `revisor` without parallel lists.

### 4.3 Copy versus reference, and not changing what you traverse

This section explains the most frequent stumble for those who come from other languages, and the one that wastes the most time when it is not known. It arrives now because it only makes sense once you have lists and dictionaries that can be changed.

#### 4.3.1 A name is a label, not a box

When you write `a = [1, 2]`, Python does two things: it **creates** the list somewhere in memory and **puts the label `a`** on it. The label does not contain the list; it **points to** it. If you then write `b = a`, a second list is not created: a second label, `b`, is put on the **same** one. There is one list and two names for it. (In Lesson 3, when comparing `==` with `is`, you saw in passing that `c = a` does not copy the list; here you see what consequences it has when that list changes.) [The official documentation explains it](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) with this same case: variables are names that refer to objects, and assigning one variable to another does not copy the object.

```python
# fig04_09.py
principales = ["catalogo", "pagos"]
respaldo = principales
respaldo.append("reportes")
print(principales)
print(principales is respaldo)

copia = principales.copy()
copia.append("inventario")
print(principales)
print(copia)
print(principales is copia)

a = 5
b = a
b = b + 1
print(a, b)
```

```text
$ python fig04_09.py
['catalogo', 'pagos', 'reportes']
True
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes', 'inventario']
False
5 6
```

- `respaldo = principales` puts a second label. When you do `respaldo.append("reportes")`, the **single** list grows, and that is why `principales` also already carries `reportes`. Nobody “touched” `principales`: it is the same list seen under another name. The `is` you saw in Lesson 3 confirms it: `principales is respaldo` is `True` (they are the same object, not two equal ones).
- `principales.copy()` creates a **new** list with the same elements. Now there are two: adding `inventario` to `copia` does not touch `principales`, and `principales is copia` is `False`. There are two other ways of getting the same thing, `list(principales)` and `principales[:]` (a full slice); all three give a copy. Use the one that reads clearest, and in this course it is `.copy()`.
- Why then does `a = 5; b = a; b = b + 1` not leave `a` at 6? Because `b + 1` **does not change the 5**: it creates a new number, the 6, and moves the label `b` to it. Numbers and texts are immutable: there is no way to change them from the inside, so sharing them between two names is harmless. The tuple is too, with a nuance: it does not let you change what is at each position, but if a position holds a list, **that list** can change, and the shared tuple “changes” with it (`t = ([142], 87)` followed by `t[0].append(5)` is valid). The `revisor`'s tuples only hold numbers, texts, and `None`, so for them sharing is harmless. The danger is in what is **mutable**: the list, the dictionary, and the set, and everything that carries them inside.

A case where this surprises, and one you already ran into in Lesson 3: **a function that receives a list receives the list itself, not a copy**.

```python
# fig04_10.py
def agregar_reportes(nombres: list[str]) -> None:
    nombres.append("reportes")


base = ["catalogo", "pagos"]
agregar_reportes(base)
print(base)
```

```text
$ python fig04_10.py
['catalogo', 'pagos', 'reportes']
```

The function returned nothing and yet `base` changed. It is exactly the mechanism of the list that “remembered” previous calls (`registrar_caido`, in Lesson 3): the default value `[]` was a single list, created once, that all calls shared. With today's material you can say it in one go: a function that receives a list can change it, and that is a design decision to be made with open eyes. Python's convention follows the example of `sort` and `sorted`: methods that **change** a collection (`append`, `sort`, `remove`) return `None`, so you do not confuse them with those that return something new, and those that return something new (`sorted`, `copy`) do not touch what they received. The useful exception is `pop`, which removes an element and also returns it.

#### 4.3.2 Shallow copy and deep copy

`.copy()` copies the outer list, but **does not copy what the list holds**: if inside there are other lists, the copy and the original share those inner lists. This is called a **shallow** copy; the alternative is the **deep** one, which also copies what is inside, and is offered by the `copy` module (brought in with `import copy`, as you learned in Lesson 3). [Its documentation defines the difference](https://docs.python.org/3/library/copy.html): the shallow one inserts references to the same objects; the deep one inserts copies, recursively.

```python
# fig04_11.py
import copy

grupos = [["catalogo", "pagos"], ["reportes"]]
superficial = grupos.copy()
superficial[1].append("inventario")
print(grupos)
print(grupos[1] is superficial[1])

grupos = [["catalogo", "pagos"], ["reportes"]]
profunda = copy.deepcopy(grupos)
profunda[1].append("inventario")
print(grupos)
print(profunda)
```

```text
$ python fig04_11.py
[['catalogo', 'pagos'], ['reportes', 'inventario']]
True
[['catalogo', 'pagos'], ['reportes']]
[['catalogo', 'pagos'], ['reportes', 'inventario']]
```

With the shallow copy, adding to `superficial[1]` also changed `grupos[1]`: the two outer lists are different, but the inner list is **the same**, and `is` confirms it. With `copy.deepcopy`, the inner one was also copied, and `grupos` stayed intact. Do not use `deepcopy` by reflex: it copies everything it reaches, is slower, and sometimes copies too much of what should have been shared. Use it when you truly need two independent nested structures. In the `revisor` it will rarely be needed, because (you will see this in Lesson 5) the important data will not be changed: it will be **replaced** by other data.

#### 4.3.3 Do not change what you are traversing

The last consequence of mutability is the most treacherous, because it **gives no error**. If you remove elements from a list while traversing it with `for`, the traversal breaks down. Remove the services whose time is less than 100 ms. (To remove a value from a list you use `.remove(valor)`, which deletes the first occurrence of that value.)

```python
# fig04_12.py
tiempos_ms = [142, 2300, 87, 95]
for tiempo_ms in tiempos_ms:
    if tiempo_ms < 100:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

```text
$ python fig04_12.py
[142, 2300, 95]
```

There were two values below 100, the 87 and the 95, and only the 87 was removed: the 95 stayed. No line failed, and the result is incorrect. The reason: the `for` traverses the list **by position**, with an internal counter. When it reaches position 2 and sees the 87, it removes it; the elements that came after shift one place to the left, the 95 comes to occupy position 2, and the `for` continues with position 3, which no longer exists. The 95 is never examined, and nobody tells you. [The Python tutorial itself warns about this](https://docs.python.org/3/tutorial/controlflow.html#for-statements): code that modifies a collection while traversing it is hard to get right, and the simplest thing is to traverse a copy or build a new collection. Building a new collection is exactly what a comprehension does:

```python
# fig04_13.py
tiempos_ms = [142, 2300, 87, 95]
rapidos = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms >= 100]
print(rapidos)
print(tiempos_ms)
```

```text
$ python fig04_13.py
[142, 2300]
[142, 2300, 87, 95]
```

Now the result is the correct one and, as a bonus, the original list stays as it was. With a dictionary, the carelessness of **adding or removing keys** while you traverse it does give an error, because Python detects it:

```python
# fig04_14.py
tiempos_ms = {"catalogo": 142, "pagos": 87}
for nombre in tiempos_ms:
    tiempos_ms[nombre + "-copia"] = 0
```

```text
$ python fig04_14.py
Traceback (most recent call last):
  File "fig04_14.py", line 3, in <module>
    for nombre in tiempos_ms:
                  ^^^^^^^^^^
RuntimeError: dictionary changed size during iteration
```

`RuntimeError: dictionary changed size during iteration`: “the dictionary changed size during the traversal.” The `for nombre in tiempos_ms` traverses the keys, and inside you added one; Python noticed and stopped. Notice the word *size*: changing the **value** of a key that already exists (`tiempos_ms[nombre] = 0`) does not change how many keys there are and gives no error; what fails is adding or deleting keys. The solutions are the same: traverse a copy (`for nombre in list(tiempos_ms):`) or build a new dictionary with a comprehension.

#### Before the project

Before going to the project, check that you can do this without looking at the lesson; it is also what will give fluency to what follows:

- Write a dictionary with the four services and their times, read one with brackets and another with `.get`, and explain why `.get` of a key whose value is `None` misleads.
- Write a comprehension that filters a list, and the same thing as a loop.
- Say out loud what `b = a; b.append(1); print(a)` prints if `a` is a list, and what changes if `a` is a number.
- Explain why `sorted(x)` and `x.sort()` are not the same.

With that in hand, today's project reads without surprises.

### 4.4 The project step: the `revisor` without parallel lists

Put today's material together in the project. The change lives entirely in `revisor.py`. `formato.py` stays exactly as Lesson 3 left it, because its job (giving text form to a name, a status, a time, and a detail) did not change; it is repeated here only so that the figure's folder is complete:

```python
# fig04_15/formato.py
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
# fig04_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
SERVICIOS = ["catalogo", "inventario", "pagos", "reportes"]
SIMULADO: dict[str, tuple[int | None, int | None, str | None]] = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str) -> str:
    sin_respuesta = (None, None, "sin conexión")
    codigo, tiempo_ms, error = SIMULADO.get(nombre, sin_respuesta)
    if codigo is not None:
        detalle = str(codigo)
    elif error is not None:
        detalle = error
    else:
        detalle = "sin conexión"
    estado = clasificar(codigo, tiempo_ms)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    renglones = [revisar(nombre) for nombre in SERVICIOS]
    print(encabezado())
    for renglon in renglones:
        print(renglon)


if __name__ == "__main__":
    main()
```

Read `revisor.py` in parts.

**The data.** Instead of the three lists there are two constants. `SERVICIOS` is a **list** of names: the services you want to check, in the order you want to see them in the table. It is a list because order matters and because the quantity may grow. `SIMULADO` is a **dictionary** that, for each name, stores a **tuple of three** with what that service “answered”: `(code, tiempo_ms, error)`. It is a tuple because they are three fixed things that always travel together and each position means something different, and the annotation `dict[str, tuple[int | None, int | None, str | None]]` says so with one position per element, as you saw in 4.1.5. The one for `reportes` is `(None, None, "sin conexión")`: there was no code or time, and the third element tells why. Notice what you gained: the three pieces of data of `inventario` are on **one single line**, under its name. There is no longer any way for its code to end up paired with another service's time.

Why two constants and not one? Because they answer different questions and are going to follow different paths. `SERVICIOS` is **what you want to check**: in Lesson 6 it will stop being written in the code and will be read from a file. `SIMULADO` plays the role of **the network**: it is what each service answers while the program still does not know how to really ask, and in Lesson 9, when the `revisor` queries each service, it disappears. Separating them already teaches something from today: a service that is in `SERVICIOS` and not in `SIMULADO` is a service that did not answer.

**`revisar`** changed its signature. Before, it received the name, the code, and the time, which `main` had to pull from three lists at the same position; now it receives **only the name** and looks up the rest on its own. The lookup is `SIMULADO.get(nombre, sin_respuesta)`, with `.get` **on purpose**: a name that is not in `SIMULADO` is not a mistake of the program but a service for which there is no data, and it is treated as down “sin conexión.” That is why the default value, `sin_respuesta`, is the same tuple as that of `reportes`. It is the criterion from 4.1.3: `.get` when absence is an anticipated case, brackets when it should not happen. Then, `codigo, tiempo_ms, error = ...` unpacks the tuple into three names (4.1.2), and the detail is decided with the Lesson 2 rule, extended with the third piece of data: the code as text if there was a response; if not, the error's text; and if there is no error either, “sin conexión.” `clasificar` did not change a single letter.

**`main`** first builds the list of rows with a comprehension, `[revisar(nombre) for nombre in SERVICIOS]` (4.2), and then prints it under the header. The traversal no longer uses `range(len(...))` or positions: it traverses the names, one by one, like the first `for` of Lesson 3. And the table's order is that of `SERVICIOS`, not that of `SIMULADO`: what decides what is shown and in what order is the list of what you want to check.

Run the project from its folder:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

The same table as Lesson 3, as promised. Compare it with Exercise 1 of that lesson, the one with `facturacion`: there you had to touch three lists in the same order, and an omission produced an `IndexError` or, worse, a row with another service's data. Now a service is a name in `SERVICIOS` and a line in `SIMULADO`, and if you forget the line, the service appears as down “sin conexión,” which is the truth: there is no data about it. You check it in Exercise 3.

Something remains awkward, and it is the starting point of Lesson 5. Look at the line `codigo, tiempo_ms, error = SIMULADO.get(...)`: the tuple does not say what each position is; only your memory says so. And `clasificar` still returns a text, `"ARRIBA"`, `"LENTO"`, or `"CAIDO"`, that nothing prevents you from misspelling. Giving each thing of the problem a name of its own that Python recognizes is the topic of the next lesson. There the summary line also arrives (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`): you would already know how to count it with today's comprehensions, but it becomes clearer once each result is a single named thing.

## The error you will see

In the previous sections you already provoked several errors where they are born (`IndexError`, `TypeError`, `ValueError`, `RuntimeError`). Here is the one you will meet most when working with dictionaries, and at the end a table to recognize them all at a glance.

### `KeyError: 'catalgo'`

Asking a dictionary for a key it does not have. Type `catalgo` instead of `catalogo`:

```python
# fig04_16.py
SIMULADO = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}
codigo, tiempo_ms, error = SIMULADO["catalgo"]
print(codigo, tiempo_ms, error)
```

```text
$ python fig04_16.py
Traceback (most recent call last):
  File "fig04_16.py", line 8, in <module>
    codigo, tiempo_ms, error = SIMULADO["catalgo"]
                               ~~~~~~~~^^^^^^^^^^^
KeyError: 'catalgo'
```

Read it from the bottom up, as always. **The last line:** `KeyError: 'catalgo'`. The type is `KeyError` (a key error) and the text between quotes is **the key that was asked for and does not exist**, exactly as you typed it; if you compare it with the dictionary's keys, the typo jumps out. **One line above:** the program, with a stripe of `~` and `^` under the expression that failed, `SIMULADO["catalgo"]`. **Further up:** the line and the file. Here there is no function in between, so the *traceback* is short; with functions calling each other, there would be more lines, and it reads the same: the immediate cause is at the end.

Two questions before fixing it. The first: should the key exist? If so, it is a typo or a data error, and the `KeyError` is **exactly what you want**: the program stopped at the exact place of the mistake, without letting a false value move on. The second: is it normal for it sometimes not to exist? Then the dictionary is not queried with brackets, but with `.get(key, default_value)` or with a prior `in`. That is the reason `revisar`, in 4.4, uses `.get`: a service with no simulated data is an anticipated case. What you should **not** do is use `.get` everywhere “just in case”: it swaps a clear error for a `None` that will fail later and farther away (Lesson 5 starts with just such a case). Catching the error with `try`/`except` is the topic of Lesson 6.

### The errors of this lesson at a glance

When one shows up, look up its last line here. All of them came from this lesson's runs.

| The last line says... | What happened | Where you saw it |
|---|---|---|
| `IndexError: list index out of range` | you asked for a position that does not exist in the list | 4.1.1 |
| `KeyError: 'catalgo'` | you asked for a key the dictionary does not have | above |
| `TypeError: 'tuple' object does not support item assignment` | you tried to change an element of a tuple | 4.1.2 |
| `ValueError: too many values to unpack (expected 2...` | you unpacked into more or fewer names than elements | 4.1.2 |
| `TypeError: unhashable type: 'list'` | you used a list as a key or set element | 4.1.4 |
| `RuntimeError: dictionary changed size during iteration` | you changed a dictionary's size while traversing it | 4.3.3 |

The texts in the table are those of Python 3.12, the one on your Mint. Two change in 3.14, although the error is the same: the unpacking one adds how many there were, `ValueError: too many values to unpack (expected 2, got 3)`, and the one for the list as a key says where you used it: `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')` (or `as a set element`, if it was in a set).

## What gets done wrong

Each of these slips has a concrete cost, and most do not give an error at first.

**Maintaining parallel lists.** Three lists that correspond by position get out of alignment with one omission, and the symptom appears far from the cause: an `IndexError` halfway down the table, or a row with another service's time. The cost is the day lost looking for why service number 4 says 87 ms. One entry per service in a dictionary, with its data together, avoids it by design.

**Storing the result of `.sort()`.** `.sort()` sorts the list that already exists and returns `None`. Whoever writes `ordenados = tiempos_ms.sort()` gets a variable that is `None`, and the error appears where it is used:

```python
# fig04_17.py
tiempos_ms = [142, 2300, 87]
ordenados = tiempos_ms.sort()
print(ordenados)
print(tiempos_ms)
```

```text
$ python fig04_17.py
None
[87, 142, 2300]
```

The list did end up sorted (the second line), but `ordenados` does not contain it. If you need a sorted copy, `sorted(tiempos_ms)`; if you need to sort the list itself, `tiempos_ms.sort()` **without** assigning.

**Using `.get` for everything.** It swaps a clear error (`KeyError`, with the key that failed) for a `None` that propagates and blows up later, elsewhere and with another message. Use it when absence is an anticipated case, not to silence errors.

**Writing `{}` expecting an empty set.** It is an empty dictionary, and the failure comes later, on the first set operation:

<!-- frag: llaves_vacias.py -->
```python
vistos = {}
vistos.add("catalogo")
```

The last line of the *traceback* says:

```text
AttributeError: 'dict' object has no attribute 'add'
```

The correct form is `vistos: set[str] = set()`. An empty set is written with `set()`.

**Trusting the order of a set.** It works “most of the time” in tests on one machine and fails on another, because the order of texts changes between runs. If order matters, `sorted(...)`. If the order of arrival matters to you, a list or a dictionary (which does remember insertion order).

**Copying with `=`.** `respaldo = principales` does not make a copy: it puts a second name. The cost is modifying data “from someone else” without realizing it, and the defect appearing in a place you did not touch. To copy, `.copy()`; to copy what is nested, `copy.deepcopy`.

**Changing a collection while traversing it.** With a list it does not fail and skips elements (4.3.3); with a dictionary, adding or removing keys fails with `RuntimeError`. Traverse a copy or build a new collection with a comprehension.

**Unreadable comprehensions.** A comprehension with two `for` and three conditions fits on one line but does not fit in the head of whoever reads it. If you need to read it twice, it is a loop. The cost is maintenance: whoever touches it afterwards (you, in three months) will rewrite it.

**A long tuple instead of a name.** A tuple of three elements is remembered; one of six is not, and `resultado[4]` ends up meaning whatever each person believes. If you catch yourself writing a comment to remember what each position is, it is the sign that the data deserves a name of its own, which is what Lesson 5 brings.

## Exercises

Try each one before looking at the solutions.

### Exercise 1 — Predict, run, and fix

Before running anything, **write on paper** what each `print` of this program prints. Then run it in your `practica/` folder and compare with your prediction.

<!-- frag: ej1a.py -->
```python
a = ["catalogo", "pagos"]
b = a
b.append("reportes")
c = list(a)
c.remove("pagos")
print(a)
print(b)
print(c)
print(a is b, a is c)
```

Next, this traversal has the defect of 4.3.3, but with `None` values. Predict what it prints, explain why it comes out that way, and fix it with a comprehension.

<!-- frag: ej1b.py -->
```python
tiempos_ms = [142, None, None, 87]
for tiempo_ms in tiempos_ms:
    if tiempo_ms is None:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

### Exercise 2 — Three questions to the dictionary

With this dictionary, write three comprehensions: (a) the **list** of names of the services whose time is 1000 ms or more; (b) a **dictionary** with the time in seconds (milliseconds divided by 1000) of the services that did respond; (c) the **set** of names with no response. Make sure none of them compares `None` with a number.

<!-- frag: ej2_datos.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
```

### Exercise 3 — One more service, and a deliberate omission

Work on the `revisor` of 4.4. (a) Add `"facturacion"` at the end of `SERVICIOS`, **without** touching `SIMULADO`, and before running, predict its row. (b) Now add to `SIMULADO` the entry for `facturacion`, which answers with code 503 in 95 ms, and predict again. (c) Finally add `notificaciones` in both places; in `SIMULADO`, with `(None, None, "tiempo agotado")` (“timed out”), because it fails to answer in time. Predict its row and notice how it ends up aligned. Compare each step with what happened in Exercise 1 of Lesson 3, when you forgot one of the three lists.

### Exercise 4 — Provoke three errors and read them

Open the REPL with `python` from your `revisor` folder (the one you met in Lesson 1), import `SIMULADO` with `from revisor import SIMULADO`, and provoke these three errors, one by one: (a) `SIMULADO["catalgo"]`; (b) position 3 of a three-element list; (c) changing the first element of the `pagos` tuple with `SIMULADO["pagos"][0] = 500`. For each one, write in your logbook the **last line** and, in your own words, what it means and how it is fixed. One extra question: why did the `import` not print the table?

## Solutions

### Solution 1

The first part:

```text
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes']
['catalogo', 'reportes']
True False
```

`a` and `b` are **the same object**: `b.append("reportes")` changed both, and `a is b` is `True`. `c = list(a)` is a copy made **after** `a` already had `reportes`; when removing `"pagos"` from `c`, `a` and `b` did not find out, and `a is c` is `False`. The second part prints:

```text
[142, None, 87]
```

The `None` at position 1 is removed; the list shifts left, the second `None` comes to position 1, and the `for` continues with position 2, so it **never examines it**: a `None` remains in a list from which you wanted to remove them all. The fix builds a new list:

<!-- frag: ej1c.py -->
```python
tiempos_ms = [142, None, None, 87]
tiempos_ms = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms is not None]
print(tiempos_ms)
```

```text
[142, 87]
```

### Solution 2

<!-- frag: ej2_solucion.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}

lentos = [n for n, ms in por_servicio.items() if ms is not None and ms >= 1000]
en_segundos = {n: ms / 1000 for n, ms in por_servicio.items() if ms is not None}
sin_respuesta = {n for n, ms in por_servicio.items() if ms is None}

print(lentos)
print(en_segundos)
print(sin_respuesta)
```

```text
['inventario']
{'catalogo': 0.142, 'inventario': 2.3, 'pagos': 0.087}
{'reportes'}
```

Three things to check. In (a) the condition `ms is not None and ms >= 1000` asks about `None` first: `and` stops as soon as one part is false, so `None >= 1000` (which would fail with a `TypeError`) never gets evaluated. In (b) the division `ms / 1000` always gives a number with decimals, and that is why `2.3` and not `2`. In (c) braces with a single value and no colon give a set; with a single element it looks like `{'reportes'}`.

### Solution 3

(a) With `facturacion` in `SERVICIOS` and with no entry in `SIMULADO`, the program **does not crash**: `.get` does not find the name, returns `sin_respuesta`, and the new row is that of a down service with no data:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO          —  sin conexión
```

Compare it with Lesson 3: there, forgetting a list produced an `IndexError` or, worse, shifted the data from one service to another. Here the omission affects **only** `facturacion`, and what its row says is true: there is no response from it.

(b) With `"facturacion": (503, 95, None),` in `SIMULADO`, its row becomes `facturacion CAIDO       95ms  503`: it answered, but with an error code, and the first rule of `clasificar` marks it down even though it was fast. The name has 11 letters and fits in the 12 columns, with only one space of margin.

(c) The two constants end up like this (with six names, the list no longer fits on a line of 88 characters and is spread over several, like the long signatures of Lesson 3):

```python
SERVICIOS = [
    "catalogo",
    "inventario",
    "pagos",
    "reportes",
    "facturacion",
    "notificaciones",
]
```

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

And the last row comes out like this:

```text
notificacionesCAIDO          —  tiempo agotado
```

The name has 14 letters and the column is 12 wide, so it spills out of its cell and ends up **stuck to the status**. It is a real limitation of today's format, and Lesson 11 resolves it by calculating the width from the longest name. Notice also the detail: `tiempo agotado`, the third element of the tuple, because there was no code.

### Solution 4

The last three lines, each one measured:

```text
KeyError: 'catalgo'
```

`KeyError` with the requested key between quotes: the dictionary does not have `catalgo`. Fix: write `catalogo`, or `.get` if absence is normal.

```text
IndexError: list index out of range
```

`IndexError`: a three-element list has positions 0, 1, and 2. Fix: `lista[2]`, or `lista[-1]` for the last.

```text
TypeError: 'tuple' object does not support item assignment
```

`TypeError`: a tuple is not changed from the inside. Fix: if what `pagos` answered truly changed, a new tuple is stored in the dictionary, `SIMULADO["pagos"] = (500, 87, None)`; the dictionary can be changed, the tuple cannot.

The extra question: the `import` executed `revisor.py` from top to bottom, but the call to `main()` is inside `if __name__ == "__main__":`, and on import, `__name__` is `revisor`. It is the idiom from Lesson 3 doing its job.

## How I know I got it

- [ ] In `~/curso-python/revisor/`, `python revisor.py` prints the header and the four rows, identical to those of Lesson 3 and to those of `fig04_15`.
- [ ] In your `revisor.py`, `NOMBRES`, `CODIGOS`, and `TIEMPOS_MS` no longer exist, nor does any `range(len(...))`.
- [ ] With `facturacion` in `SERVICIOS` and no entry in `SIMULADO`, its row says `CAIDO` and `sin conexión`, and the program does not crash; when you add it to `SIMULADO`, it says `503`.
- [ ] For the `reportes` service, `.get` gives `None` for two possible reasons, and you can say which they are and how to tell them apart with `in`.
- [ ] You can explain in your own words the difference between `b = a` and `b = a.copy()`, between `sorted(x)` and `x.sort()`, and why removing elements from a list while traversing it skips one without warning.
- [ ] You noted in the [logbook](bitacora.md) what was hardest for you: what you note there is what you should review.

## Summary

Answer without looking at the lesson:

1. What question does each collection answer: the list, the tuple, the dictionary, and the set? Which ones can be changed?
2. What is the difference between `IndexError` and `KeyError`, and what does the last line of each say?
3. What does `.get("reportes")` return if `reportes` exists with the value `None`? And if it does not exist? How do you tell the two cases apart?
4. What three parts does a comprehension have? When is it better to leave a loop?
5. If `a = [1, 2]` and you do `b = a`, how many lists are there? What changes with `b = a.copy()`? And with `copy.deepcopy`?
6. Why does removing elements from a list while traversing it skip elements without giving an error?
7. In the `revisor`, why are `SERVICIOS` and `SIMULADO` two separate things, and what happens to a name that is in the first and not in the second?

## Further reading

- [Python, “Data Structures” (tutorial)](https://docs.python.org/3/tutorial/datastructures.html) — lists, tuples, sets, dictionaries, and comprehensions, with more examples and in the same order as this lesson. Accessed on October 7, 2026.
- [Python, “Built-in Types”](https://docs.python.org/3/library/stdtypes.html) — the reference for each collection: which operations it admits and which change the value in place. It is for consulting, not for reading straight through. Accessed on October 7, 2026.
- [Python, `copy` module](https://docs.python.org/3/library/copy.html) — the difference between shallow and deep copy, told by the official documentation. Accessed on October 7, 2026.
- [Programming FAQ: “Why did changing list ‘y’ also change list ‘x’?”](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) — the official explanation of copy versus reference, with the same case as 4.3.1. Accessed on October 7, 2026.
