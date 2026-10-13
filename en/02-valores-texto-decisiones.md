# Lesson 2 — Values, text, and decisions

**Time:** 90 min

**What you build:** the `revisor`'s header and the classification of **one** service: its status, its time, and its detail, printed on one table row

**What you learn:** three concepts. First, values and names (numbers, text, true or false, and `None`); second, formatted text (f-strings); third, decisions with `if`, `elif`, and `else`, and indentation as part of the syntax

**Where you come from.** You bring [Lesson 1](01-instalacion.md) with you: you have the folder `~/curso-python/` with its virtual environment `.venv`, the environment active (the *prompt* shows `(.venv)`), and, inside `~/curso-python/revisor/`, a one-line `revisor.py` file that prints “revisor: todavía no revisa nada” (“revisor: not checking anything yet”). That is all your program does so far: it checks nothing. In this lesson it starts to, for one service. All the commands are written as if you were standing in `~/curso-python/revisor/`, and the program is run with `python archivo.py`. Save each figure of the lesson under the name it carries on its first line (`fig02_01.py`, `fig02_02.py`, and so on), in that same folder.

**What this lesson does not do.** There are no lists yet, no functions, no repetition. Today's `revisor` knows about just **one** service, kept in a handful of variables, and classifies it once. Checking all four at once, and repeating the same code without copying it, is the topic of [Lesson 3](03-bucles-funciones-modulos.md). Today the smallest thing is solved first: **what a piece of data is, how a table row is written, and how the program decides whether a service is up, slow, or down**.

## By the end you will be able to

- Store a piece of data under a name and say what type it is (`int`, `float`, `str`, `bool`, or `None`), with the `type()` function.
- Calculate with arithmetic and comparison operators, combine conditions with `and`, `or`, and `not`, and ask whether a value is `None` with `is`.
- Build a text with an f-string and align columns with `:<12`, `:>6`, and `:.1f`.
- Write an `if`/`elif`/`else`, explain why indentation is part of the syntax and why the order of the branches changes the result.
- Classify a service as ARRIBA (up), LENTO (slow), or CAIDO (down) with the `revisor`'s four rules and print its row together with the table header.
- Read three beginner errors, `SyntaxError: expected ':'`, `IndentationError`, and `TypeError` when adding text and a number, and say what caused them.

## The why before the how

Imagine you work on a team that maintains four services inside a company: the product catalog, the inventory, the payments, and the reports. On a Monday morning someone asks the same thing that is asked every Monday: “which ones are working?”. Today you find out by opening four addresses in the browser and looking. The `revisor`, the project you are going to build in this course, asks that question for you and answers with a table like this one:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Look at the table with a programmer's eyes and you will see that each cell is **a piece of data of a different kind**. `catalogo` is a text. `142` is a quantity. `ARRIBA` is one of three possible words. And the time of `reportes` is... nothing: that service did not answer, so there is no time to show, and that has to be expressible in some way other than writing a zero (a service that did not answer did not respond in zero milliseconds). If a program is going to produce this table, it needs three things, and they are the three of this lesson:

- **Represent the data** with the right kind: text for the name, numbers for the code and the time, a special value for “there is no data.” That is concept 2.1.
- **Build the row**: glue the name, the status, and the time into aligned columns, and turn 2300 milliseconds into `2.3s`. That is concept 2.2.
- **Decide**: if the service answered with an error code, it is CAIDO; if it answered fine but took a thousand milliseconds or more, it is LENTO; if not, it is ARRIBA. That is concept 2.3.

By the end of the lesson you will have a `revisor.py` of about thirty lines that, for the `inventario` service, prints exactly these two rows:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

They are two rows out of the table's five, but they are the ones that matter: the header, which no longer changes for the whole course, and one complete service, with its three decisions. When you learn to repeat in Lesson 3, the other three services will come out with the same code.

One last idea before starting, because it will serve you throughout the course. A program is a list of instructions that Python executes **one after another, from top to bottom**. When an instruction fails, Python stops at it and tells you which one it was; when an instruction asks for nothing special, Python moves on to the next. There is no magic underneath: if you want to know what a program does, read it the way Python reads it, from top to bottom and one line at a time. That is what you are going to do with each figure.

## The concepts

### 2.1 Values and names

#### 2.1.1 Values and their types

A **value** is a concrete piece of data: the number 2300, the text `"inventario"`, the “yes” of “did it answer?”. Every value has a **type**, which is the kind of data it is and determines what can be done with it: with numbers you add, with texts you glue. Python has many types; today you need five, and all five appear in the `revisor`.

- **`int`** (integer): a number without decimals. A service's response code (`200`, `503`) and the time in milliseconds (`2300`) are integers. [Python's documentation](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) calls them “numeric types”; integers have no maximum size you need to watch.
- **`float`** (decimal): a number with a decimal point, like `2.3`. It is called that after “floating point,” the way computers store decimals. Further down you will see a surprise that comes with them.
- **`str`** (text string): a sequence of characters between quotes, single or double, like `"inventario"`. In this course they are written with double quotes. A text may carry accents and symbols (`"sin conexión"`, `"—"`): Python 3 stores text as Unicode.
- **`bool`** (boolean): only two possible values, `True` and `False`, with the first letter capitalized. It is the answer to a yes-or-no question, like “did the service answer?”. It is named after George Boole, the mathematician who formalized the logic of true and false.
- **`None`**: the value that means “there is nothing here.” It is the only value of its own type, which is called `NoneType`. You will use it for the time and the code of a service that did not answer, and it is the right answer to “how long did it take?” when the answer is “there is no answer.”

The `type()` function tells you the type of any value. And `print()` can receive several values separated by commas: it prints them on the same line, with a space between them. With the two you can see the five types together. Save this figure as `fig02_01.py` and run it:

```python
# fig02_01.py
nombre = "inventario"
codigo = 200
tiempo_ms = 2300
tiempo_s = tiempo_ms / 1000
respondio = True
error = None

print(nombre, type(nombre))
print(codigo, type(codigo))
print(tiempo_ms, type(tiempo_ms))
print(tiempo_s, type(tiempo_s))
print(respondio, type(respondio))
print(error, type(error))
```

```text
$ python fig02_01.py
inventario <class 'str'>
200 <class 'int'>
2300 <class 'int'>
2.3 <class 'float'>
True <class 'bool'>
None <class 'NoneType'>
```

Line by line. The first line, the one that starts with `#`, is a **comment**: Python ignores everything from a `#` to the end of the line. It is there for people to read notes, and in this course the first line of each figure is a comment with its name (`# fig02_01.py`), so you know how to save it. The next six lines **create variables**, which is the topic of the next section; just notice that each one stores a value of a different type. `tiempo_ms / 1000` divides 2300 by 1000 and gives `2.3`, a `float`, even though the two numbers in the calculation were integers: the `/` division always gives a decimal. Then, six `print` calls show each value and its type. The output says `<class 'str'>`, `<class 'int'>`, and so on: in Python, “type” and “class” are the same idea, and the word *class* in the answer does not oblige you to know anything more about classes for now (they arrive in Lesson 5).

Two things to notice. First: `200` and `"200"` **are not the same**. The first is a number, and with it you can compare and add; the second is a three-character text that happens to be digits, and with it you cannot calculate. When in the table you see `200` in the DETALLE (detail) column, there it is a text (it is a piece of a row being printed), but in the `codigo` variable it is a number. Second: `None` **is not** `0`, nor `""` (the empty text), nor `False`. It is a different value, which says “there is no data here.” A down service that returned no code does not have a “code of zero”: it has no code.

#### 2.1.2 Names and assignment

A **variable** is a name that points to a value. It is created with the equals sign:

```python
tiempo_ms = 2300
```

That line is called an **assignment** and it is read from right to left: first the value on the right (2300) is calculated and then the name on the left (`tiempo_ms`) is put on it. The `=` sign **does not mean “is equal to”** as in mathematics; it means “store this under that name.” The question of whether two things are equal is written with two signs, `==`, and you will see it in a moment. Confusing the two is one of the most common stumbles for a beginner, and Python protects you from most of them: `if codigo = 200:` is a syntax error, because inside an `if` only a question fits.

A name can change value whenever you like: `tiempo_ms = 2300` and further down `tiempo_ms = 87` make the name now point to 87. The previous value simply stops having a name. And a value can have several names at once, although that only really matters when values can be modified from the inside, and that story starts in Lesson 4.

The rules for writing a name are few:

- It carries letters, digits, and the underscore (`_`), and **cannot start with a digit**: `1servicio` does not work, `servicio1` does.
- It cannot be a **reserved word**, one of those Python uses for its own syntax (`if`, `else`, `None`, `True`...). You will see the rest as you need them.
- **Capitals count**: `Nombre` and `nombre` are two different names. If you write one where you meant the other, Python will not tell you “you got the capital wrong,” it will tell you the name does not exist.

And there are also **conventions**, which are not mandatory but which everyone in Python follows, because they are in [the official style guide, PEP 8](https://peps.python.org/pep-0008/#naming-conventions): variable names go in lowercase with underscores between words (`tiempo_ms`, which is called *snake_case*), and the names of values that **are not going to change** (constants) go in capitals (`UMBRAL_LENTO_MS`). Python does not stop you from changing a “constant”; the capital is a warning to whoever reads the code.

This course adds two rules of its own, which you will see in every figure. **Identifiers are in Spanish, without accents or `ñ`**: `nombre`, `tiempo_ms`, `estado`. Python accepts accents in names, but they are typed badly on other people's keyboards and complicate sharing code. And **units go in the name**: `tiempo_ms`, never plain `tiempo`. When someone reads `tiempo = 2300`, they do not know whether it is milliseconds, seconds, or minutes; when they read `tiempo_ms = 2300`, they do. It is a habit that avoids expensive errors: [NASA attributed the failure of the Mars Climate Orbiter probe to a navigation error](https://science.nasa.gov/mission/mars-climate-orbiter/), caused by not converting English units to metric between the ground program and the spacecraft's.

#### 2.1.3 Operators: calculating, comparing, and combining

An **operator** is a symbol that does something with values. There are three families and all three serve the `revisor`.

The **arithmetic** ones calculate: `+` adds, `-` subtracts, `*` multiplies, `/` divides and always returns a `float`, `//` divides and keeps the whole part, `%` gives the remainder of the division, and `**` raises to a power. The **comparison** ones ask and always answer with a `bool`: `==` (equal), `!=` (different), `<`, `<=`, `>`, and `>=`. And the **logical** ones combine questions: `and` is true only if both are true, `or` is true if at least one is, and `not` inverts the answer. Save `fig02_02.py`:

```python
# fig02_02.py
UMBRAL_LENTO_MS = 1000
tiempo_ms = 2300
codigo = 200

# Aritmética
print(tiempo_ms / 1000)
print(tiempo_ms // 1000)
print(tiempo_ms % 1000)
print(tiempo_ms + 100)
print(2**3)

# Comparaciones
print(tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200)
print(codigo != 200)

# Lógicos
print(codigo >= 400 or tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200 and tiempo_ms < UMBRAL_LENTO_MS)
contesto_bien = codigo < 400
print(not contesto_bien)
```

```text
$ python fig02_02.py
2.3
2
300
2400
8
True
True
False
True
False
False
```

The first five lines of output are arithmetic: 2300 divided by 1000 gives `2.3`; whole division gives `2` (how many complete seconds fit in 2300 ms) and the remainder gives `300` (the milliseconds left over); adding 100 gives `2400`, and `2**3` is two cubed, `8`. The next three are comparisons: 2300 is indeed greater than or equal to the threshold of 1000 (`True`), the code is indeed 200 (`True`), and therefore it is not different from 200 (`False`). The last three combine: the first says “is the code an error **or** did the time exceed the threshold?”, and since the second is true, the whole `or` is; the second says “did it answer well **and** fast?”, and since it was not fast, it is false; the third stores in a variable the answer to “is the code less than 400?” (`True`) and inverts it with `not`, and that is why it gives `False`. Notice that a comparison can be stored in a variable just like a number: its value is a `bool`.

Notice a detail of the figure that will repeat all course long: the threshold is in a variable with a name in capitals, `UMBRAL_LENTO_MS = 1000`, and the comparisons use it by its name. If tomorrow the team decides that a service is slow from 800 ms on, you change **one** line. If you had written `1000` in each comparison, you would have to find them all.

Two clarifications about operators. The first is **precedence**: just as in mathematics, `*` and `/` are done before `+` and `-`, and Python does comparisons before `not`, `and`, and `or`. When in doubt, use parentheses. The second is that **`and` and `or` do not evaluate what they do not need**. In `A or B`, if `A` is already true, Python does not even look at `B`, because the result can no longer change; in `A and B`, if `A` is false, it does not look at `B` either. This is called *short-circuit evaluation* and it is not a scholar's detail: in a few minutes it is going to keep the `revisor` from blowing up on the `reportes` service.

A warning about decimals, which I promised. Look at this REPL session (the interactive interpreter from Lesson 1):

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> 10 / 2
5.0
```

The first answer looks like a Python error and is not. Computers store decimals in binary, and some simple decimals, like 0.1, have no exact representation in binary; they are stored approximately, and the sum of two approximations gives an approximation slightly different from the 0.3 you expected. [The official tutorial devotes a chapter to this](https://docs.python.org/3/tutorial/floatingpoint.html) and reminds you that it is not a defect of Python or of your code: it is how binary floating-point numbers work, the representation used by almost all computers (and, with them, almost all languages). The practical consequence: **do not compare with `==` the result of a calculation with decimals expecting an exact value**. In the `revisor` this hardly affects you, because the times are integers (milliseconds), and that is why they are in milliseconds and not in seconds with decimals. The second answer shows another habit: `10 / 2` gives `5.0`, not `5`. The `/` always returns a `float`.

#### 2.1.4 `None`, `is`, and conversions with `str()` and `int()`

To ask whether a value is `None`, Python has a specific operator: **`is`**. It is written `valor is None`, and its opposite is `valor is not None`. It is the correct way to do it, and the one used by [the style guide](https://peps.python.org/pep-0008/#programming-recommendations), which asks that comparisons with `None` always be made with `is` or `is not`, never with `==`. The reason, in one sentence: in the whole program **there exists a single `None`**, so what is asked is not “does it look like `None`?” but “is it *the* `None`?”. (The full difference between `==` and `is` is the topic of Lesson 3; for now keep the rule.)

There are also two functions that convert between types. `str(valor)` returns the text that represents a value: `str(503)` is `"503"`. And `int(texto)` does the opposite: `int("503")` is `503`. You will need them in two places: `str(codigo)` to put a code inside the table row, and later `int(...)` to convert what arrives from outside, which almost always arrives as text. Save `fig02_03.py`:

```python
# fig02_03.py
codigo = None
tiempo_ms = None

print(codigo is None)
print(codigo is not None)

codigo = 503
print(codigo is None)
print("código: " + str(codigo))
print(type(str(codigo)))
print(type(int("503")))
```

```text
$ python fig02_03.py
True
False
False
código: 503
<class 'str'>
<class 'int'>
```

While `codigo` was `None`, the first question gives `True` and the second `False`. When 503 is assigned to it, the service already has a code and the question gives `False`. Then, `"código: " + str(codigo)` glues two texts with `+` (for texts, `+` joins them) and works **because `str(codigo)` converted the number into text beforehand**. The last two lines confirm that `str(503)` is a `str` and that `int("503")` is an `int`. Keep this idea: Python does not convert between types for you. If you try to glue a text to a number, it complains, and that complaint is one of the errors in the section “The error you will see.”

### 2.2 Formatted text: f-strings

#### 2.2.1 Why not glue with `+`

A table row has to be built: the name, the status, the time, and the detail, in aligned columns. With what you already know, the way would be to glue texts with `+`, converting each number with `str()`, and calculating by hand how many spaces are missing to complete each column. It can be done, and it comes out unreadable and fragile: each new piece is another `+` and another `str()`, and changing a column's width forces you to recount spaces.

Python has a tool designed for this: **f-strings** (*formatted string literals*). An f-string is a text that starts with the letter `f` before the quotes, and that accepts **expressions between curly braces**: Python calculates what is inside each pair of braces and puts the result into the text. They are explained in [the language reference](https://docs.python.org/3/reference/lexical_analysis.html#f-strings). Two other, older ways of formatting text exist, the `%` operator and the `.format()` method. You will find them in old code, so it is worth recognizing them, but this course does not use them and you do not need to learn them: f-strings do everything they do and read better.

#### 2.2.2 Putting values and calculations into the text

The simplest thing is to put a name between braces: `f"{nombre} respondió"`. But what goes between braces can be any expression, even a calculation: `f"{tiempo_ms * 2}"` calculates the double and inserts it. This eliminates the `str()` of the previous section entirely: the f-string converts to text what you insert, without your asking.

#### 2.2.3 The format specification: width, alignment, and decimals

After the expression, and separated by a colon, you can write a **format specification** that tells Python how to show the value. Today you need three, and [the full formatting language is in the documentation](https://docs.python.org/3/library/string.html#format-specification-mini-language):

- **`:<12`**: occupies **12 characters** and aligns the value to the **left** (`<`), padding with spaces on the right.
- **`:>6`**: occupies **6 characters** and aligns the value to the **right** (`>`), padding on the left.
- **`:.1f`**: shows a **decimal number with one digit** after the point (`f` for *fixed*, fixed point).

Save `fig02_04.py`. The braces are surrounded by square brackets in the output so that you can see where each field starts and ends:

```python
# fig02_04.py
nombre = "inventario"
tiempo_ms = 2300

print(f"{nombre} respondió en {tiempo_ms} ms")
print(f"el doble: {tiempo_ms * 2}")
print(f"en segundos: {tiempo_ms / 1000}")
print(f"[{nombre:<12}]")
print(f"[{nombre:>12}]")
print(f"[{87:>6}]")
print(f"[{tiempo_ms / 1000:.1f}s]")
print(f"[{1000 / 1000:.1f}s]")
```

```text
$ python fig02_04.py
inventario respondió en 2300 ms
el doble: 4600
en segundos: 2.3
[inventario  ]
[  inventario]
[    87]
[2.3s]
[1.0s]
```

The first three lines no longer need an explanation: the name and the time are inserted as they are, the calculation is done and inserted, and `2300 / 1000` comes out as `2.3`. The next ones show the width: `inventario` has ten characters, and with `:<12` it ends up with two spaces after it (look at where the closing bracket falls); with `:>12`, the two spaces go before. With `{87:>6}` the 87 occupies six positions, aligned to the right, and that is why there are four spaces before it. The last two show `.1f`: `2.3` already had one decimal, and `1000 / 1000`, which is `1.0`, keeps its `.0` (Python rounds to the requested number of decimals, it does not remove them).

This is what you need to build a table row. The `revisor`'s template, which will not change for the whole course, is:

```text
f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

Read it from left to right: the service name in 12 columns, aligned to the left; the status in 10, to the left; the time in 6, to the right (numbers align better on the right, so the units line up one under another); two fixed spaces, and the detail, which goes last and needs no width. And the table header uses **the same template**, with the titles in place of the data. A detail of writing: the header goes between double quotes and, inside the braces, the titles carry single quotes (`{'SERVICIO':<12}`). Since Python 3.12 you could repeat the double ones inside the braces and it would work (it was allowed by [PEP 701](https://peps.python.org/pep-0701/)), but alternating them reads better, because at a glance you can tell where the f-string ends and where the text inside begins, and it also works in earlier versions of Python.

### 2.3 Decisions: `if`, `elif`, `else`, and indentation

#### 2.3.1 A question and a block

A program that always does the same thing is no use for checking services. It needs to **decide**: if such a thing happens, do this; if not, that. In Python the decision is written with `if`:

```text
if <pregunta>:
    <lo que se hace si la respuesta es verdadera>
```

The question is any expression that gives a `bool`, like those in the previous section. After the question goes a **colon** (`:`), which tells Python “here begins what depends on the question.” And what depends on it goes in the following lines, **shifted to the right**. That set of lines is called a **block**.

Here comes a feature of Python that sets it apart from most languages and that sometimes surprises the beginner: **indentation is part of the syntax**. In other languages blocks are delimited with curly braces or with words like `begin` and `end`, and indenting is a matter of style. In Python **the indentation is what says where the block starts and where it ends**. The lines that are shifted by the same amount belong to the same block; when a line goes back to the left margin, the block has ended. [The language reference defines it precisely](https://docs.python.org/3/reference/lexical_analysis.html#indentation), and PEP 8's practical rule is: **four spaces per level**, and never mix tabs with spaces. Configure your editor so the Tab key inserts four spaces, and never think about it again.

Save `fig02_05.py`:

```python
# fig02_05.py
codigo = 503

if codigo >= 400:
    print("el servicio contestó con un error")
else:
    print("el servicio contestó bien")

print("fin de la revisión")
```

```text
$ python fig02_05.py
el servicio contestó con un error
fin de la revisión
```

With `codigo = 503`, the question `codigo >= 400` is true and the first block is executed. The `else` (in English, “otherwise”) is the branch executed when the answer is false; it takes no question, but it does take its colon. Notice the last line: it is **at the left margin**, outside both blocks, and that is why it is always executed, whatever the code is. Try changing `codigo` to `200` and check that the first line of the output changes, but the last one does not. If a line is ever executed “when it shouldn't” (or is not executed when it should), look first at its indentation: in Python, that is where 80% of those surprises begin.

#### 2.3.2 `elif`: several questions in a chain

A service does not have two states but three, and the `revisor`'s decisions are chained: first it asks whether it is down; if not, it asks whether it is slow; and if not that either, it is up. That is what `elif` is for, a contraction of *else if*, “otherwise, and if...”. An `if`/`elif`/`else` chain works like this: **Python evaluates the questions from top to bottom, executes the block of the first one that is true, and skips all the others**. If none is, it executes the `else`, if there is one. In a chain, at most one block is ever executed.

The `revisor`'s rules for classifying a service, which are the same from this lesson to the last, are four:

1. If there was **no code** (no response), it is **CAIDO**.
2. If the code is **400 or more** (the server answered, but with an error), it is **CAIDO**; the detail will be the code itself, for example `503`.
3. If it answered fine and took **1000 ms or more**, it is **LENTO**.
4. If not, it is **ARRIBA**.

The first two have the same result, and can be joined in a single question with `or`. Save `fig02_06.py`:

```python
# fig02_06.py
UMBRAL_LENTO_MS = 1000
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

print(estado)
```

```text
$ python fig02_06.py
LENTO
```

For `inventario`, with code 200 and 2300 ms, the first question is false (the code exists and does not reach 400), the second is true (2300 is greater than or equal to 1000), and the status ends up as `"LENTO"`. Try other values: `codigo = 503` gives `CAIDO`; `tiempo_ms = 142` gives `ARRIBA`.

#### 2.3.3 The order of the questions matters

There is a reason the code question goes **first**, and it is the same one promised with short-circuiting. Think about `reportes`: it did not answer, so its `codigo` is `None` and its `tiempo_ms` too. With the chain above, the first question (`codigo is None or ...`) is true as soon as Python looks at the `is None`, and it **no longer evaluates** the second half of the `or`, which would have failed: `None >= 400` makes no sense. And since the first branch was satisfied, the `elif` is not evaluated either, which would ask `None >= 1000`. The service ends up CAIDO without Python comparing a `None` with a number.

If you put the questions in another order, the chain stops being safe. That error is one of those in “What gets done wrong,” and it is worth provoking in Exercise 4. The underlying rule: **in a chain of `elif`, order the questions from the most specific or most dangerous to the most general**, so that each branch can take for granted what the previous ones ruled out. In the `elif`, you already know the service answered and with a code below 400, so `tiempo_ms` has a value.

#### 2.3.4 All together: a service's row

You now have everything you need. What remains is calculating the other two columns with the same mechanism. The **time** is a text that depends on the value: if there was no time, a dash (`"—"`); if it was less than a second, milliseconds glued to the unit (`"142ms"`); if it was a second or more, seconds with one decimal (`"2.3s"`). Notice that the 1000 here **is not the slow threshold**: it is the number of milliseconds in a second. They look alike in value and mean different things, and that is why the first has a name (the threshold may change) and the second does not (a second always has a thousand milliseconds). And the **detail** is the code converted into text, or `"sin conexión"` (“no connection”) if there was no code.

This is the lesson's figure, your new `revisor.py`. Save it under the name `fig02_07.py` to compare it and also as `revisor.py`, which replaces the line from Lesson 1:

```python
# fig02_07.py
UMBRAL_LENTO_MS = 1000

nombre = "inventario"
url = "https://inventario.example"  # todavía no se usa: la ocupará la lección 9
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

if tiempo_ms is None:
    tiempo = "—"
elif tiempo_ms < 1000:  # 1000 ms es un segundo, no el umbral de lento
    tiempo = f"{tiempo_ms}ms"
else:
    tiempo = f"{tiempo_ms / 1000:.1f}s"

if codigo is None:
    detalle = "sin conexión"
else:
    detalle = str(codigo)

print(f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}")
print(f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}")
```

```text
$ python fig02_07.py
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

Read it the way Python reads it. The first five lines store the data of one service; `url` is the service's address and is not printed yet, but the project already carries it, like the `.example` domain, which is a reserved name that never reaches any real page (no program in this course touches the internet until Lesson 9). The first `if` block calculates `estado` with the rules above. The second calculates `tiempo`, the column's text: if `tiempo_ms is None` it puts the dash, if it is less than 1000 it glues `ms` to the number, and if not it converts it to seconds with one decimal. The third calculates `detalle`. The last two lines print the header and the row with the template from section 2.2: the same pattern, with titles in the first and with the variables in the second.

Change the five variables to those of another service and run the program again: nothing else needs to be touched. That is what Exercise 1 is about, and from there comes the next lesson: copying and pasting that block for each service would be absurd, and Python has tools so you do not have to.

## The error you will see

In this section you will deliberately provoke the three errors a beginner sees first. All three are copied from a real run. When the program fails, Python prints an error report called a ***traceback***, and the rule, since Lesson 1, is the same: **it is read from the last line upward**. The last line says what happened; those above say where. The full file paths you will see on your screen will differ from those this text shows (here they are shortened to the file's name).

### `TypeError: can only concatenate str (not "int") to str`

Save `fig02_08.py`, which tries to glue a text to a number:

```python
# fig02_08.py
nombre = "inventario"
tiempo_ms = 2300
print("respondió en " + tiempo_ms)
```

```text
$ python fig02_08.py
Traceback (most recent call last):
  File "fig02_08.py", line 4, in <module>
    print("respondió en " + tiempo_ms)
          ~~~~~~~~~~~~~~~~^~~~~~~~~~~
TypeError: can only concatenate str (not "int") to str
```

The last line says: a `TypeError` (a type error) with the message “can only concatenate `str` (not `int`) to `str`.” To concatenate is to glue. The `+` between two texts glues them, but here the second one was a number, and Python does not know how to glue a text to a number: it is not going to guess whether you wanted “2300” or a calculation. The lines above tell you **where**: `line 4`, and below it the program's line with some marks pointing to the operation that failed. The fix is to do the conversion yourself, with `str(tiempo_ms)`, or better, not to glue anything: `print(f"respondió en {tiempo_ms}")`. [The documentation of `TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) describes it as raised “when an operation or function is applied to an object of inappropriate type,” which is exactly this.

### `SyntaxError: expected ':'`

Save `fig02_09.py`, an `if` whose colon was forgotten:

```python
# fig02_09.py
codigo = 503
if codigo >= 400
    print("CAIDO")
```

```text
$ python fig02_09.py
  File "fig02_09.py", line 3
    if codigo >= 400
                    ^
SyntaxError: expected ':'
```

A `SyntaxError` is a **syntax** error: Python did not even start executing the program, because it read it entirely beforehand and found something that is not valid Python. That is why the output does **not** say `Traceback`: there is no execution path to show, only the place of the problem. The message, `expected ':'`, says what it expected: a colon. The arrow below (`^`) points to the place where it noticed, the end of the `if` line. When you see a `SyntaxError`, look at the indicated line and also the **previous** one, because sometimes the omission is earlier (an unclosed parenthesis, for example, makes the next line fail).

### `IndentationError: expected an indented block after 'if' statement on line 3`

Save `fig02_10.py`: now the colon is there, but the line below stayed at the margin:

```python
# fig02_10.py
codigo = 503
if codigo >= 400:
print("CAIDO")
```

```text
$ python fig02_10.py
  File "fig02_10.py", line 4
    print("CAIDO")
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 3
```

`IndentationError` is a variant of `SyntaxError` for indentation problems. The message is literal: after an `if` (the one on line 3) an indented block was expected, and line 4 does not have it. The colon at the end of the `if` promised a block, and Python demands it. It is the reminder from section 2.3: **the colon and the indentation go together**. The fix is to push `print("CAIDO")` four spaces to the right.

## What gets done wrong

**Putting the questions in the wrong order.** It is the most treacherous error of this lesson, because it looks reasonable and fails precisely with the service that matters most. Save `fig02_11.py`, where the time question goes before the code question:

```python
# fig02_11.py
UMBRAL_LENTO_MS = 1000
codigo = None
tiempo_ms = None

if tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"

print(estado)
```

```text
$ python fig02_11.py
Traceback (most recent call last):
  File "fig02_11.py", line 6, in <module>
    if tiempo_ms >= UMBRAL_LENTO_MS:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

The message, `'>=' not supported between instances of 'NoneType' and 'int'`, says: the `>=` operator is not defined between a `NoneType` (the `None`) and an `int` (the 1000). With services that answered, the program works and you do not find out; with `reportes`, which did not answer, it blows up. Cost: a `revisor` that crashes precisely when a service is down, which is when you need it most. The cure is the rule from section 2.3: first the branch that rules out the missing data.

**Writing `=` where `==` goes.** `if codigo = 200:` is a `SyntaxError`, and Python's message guesses it: *invalid syntax. Maybe you meant '==' or ':=' instead of '='?* Assignment stores; comparison asks. They cannot be swapped.

**Comparing with `None` using `==`.** It works in simple cases and is what [PEP 8](https://peps.python.org/pep-0008/#programming-recommendations) warns about: with `None` you always use `is` or `is not`. The checking tools you will meet in Lesson 8 also flag it.

**Storing a number as text.** `codigo = "200"` looks the same as `codigo = 200`, and it no longer is: `"200" >= 400` blows up with another `TypeError`, and `"200" + "1"` gives `"2001"`. What is a quantity is stored as a number, without quotes.

**Representing “did not answer” with `0` or with a text.** `tiempo_ms = 0` says “it answered in zero milliseconds,” which is the fastest possible answer, exactly the opposite of the truth; and a text like `"sin respuesta"` cannot be compared with 1000. A missing piece of data is stored as `None`, and the program decides what to do with it.

**Writing plain `tiempo`.** A variable called `tiempo` does not say whether it is seconds or milliseconds. Put the unit in the name, and when a number is a quantity with a unit, let the name carry it.

**Writing the same number in three places.** If the slow threshold is written as `1000` in each comparison and tomorrow it changes to 800, you will forget one. It is named once (`UMBRAL_LENTO_MS`) and used by its name.

**Mixing tabs and spaces.** Python 3 refuses to run a block whose indentation mixes the two inconsistently, with a `TabError: inconsistent use of tabs and spaces in indentation`. Your editor may do it without telling you; configure it so Tab inserts four spaces.

## Exercises

### Exercise 1 — The other three services and an extra one

Change the five variables of your `revisor.py` to those of each of the other three services, and **before running each time, write on paper the row you expect**:

| name | url | code | time in ms |
|---|---|---|---|
| `catalogo` | `https://catalogo.example` | 200 | 142 |
| `pagos` | `https://pagos.example` | 200 | 87 |
| `reportes` | `https://reportes.example` | `None` | `None` |

Then try `facturacion` (`https://facturacion.example`), which answers with code 503 in 95 ms. Did your prediction match in all four? If not, which part of the rules did you apply differently?

### Exercise 2 — Moving the threshold

With the `catalogo` service (200, 142 ms), change `UMBRAL_LENTO_MS` to 100 and predict the status. Then leave it at 2500 and predict the status of `inventario` (200, 2300 ms). Explain in one sentence why changing **a single line** changed the result in both cases.

### Exercise 3 — Provoking the three errors

In a copy of your program, provoke these three errors one by one and copy the exact message from the last line: (a) remove the colon from an `elif`; (b) remove the indentation from the line that follows the `else`; (c) change the `str(codigo)` in `detalle` to `"código " + codigo`. For each one, write what the message means and what the fix is.

### Exercise 4 — The same in reverse, and how to save it

Start from `fig02_11.py` (the one with the questions in the wrong order, which blows up with `None`). Without changing the order of the first two branches, fix the **first question** so that it no longer blows up with `reportes`. Hint: you have to first ask that `tiempo_ms` exist and then compare it, and the operator that joins two questions requiring both to hold is `and`. Then explain why this solution works thanks to short-circuiting.

## Solutions

### Solution 1

The correct predictions, and what the program prints with each service (the header is the same as always):

```text
catalogo    ARRIBA     142ms  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
```

The one for `facturacion` is the one most often missed. With code 503, the first question (`codigo >= 400`) is true, so the status is CAIDO **even though it answered in 95 ms**, which would be very fast. The time is still shown (`95ms`) because it exists, and the detail is the code, `503`. Besides, `facturacion` has eleven letters and fits in the twelve columns of the name, but with almost no margin: that is why its row ends up stuck to the status.

### Solution 2

With `UMBRAL_LENTO_MS = 100`, the status of `catalogo` (142 ms) goes from ARRIBA to **LENTO**: 142 is already greater than or equal to 100. With the threshold at 2500, `inventario` (2300 ms) goes from LENTO to **ARRIBA**: 2300 no longer reaches 2500. In both cases the result changed because the threshold was written only once and all the comparisons use it by its name; if the 1000 were repeated in each question, it would have to be changed in all of them.

### Solution 3

(a) Without the colon on the `elif`: `SyntaxError: expected ':'`. Python expected the colon that announces the block. Fix: put it at the end of the `elif` line.

(b) Without indentation after the `else`: `IndentationError: expected an indented block after 'else' statement on line N`, where `N` is the number of the `else` line. Fix: four spaces before the line that depends on the `else`.

(c) `"código " + codigo`, with `codigo` being 200: `TypeError: can only concatenate str (not "int") to str`. Fix: `"código " + str(codigo)` or, better, an f-string: `f"código {codigo}"`.

### Solution 4

The first question becomes `tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS`:

```python
if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"
```

It works thanks to short-circuiting: with `tiempo_ms = None`, the first half (`tiempo_ms is not None`) is false, and since an `and` with a false half can no longer be true, Python **does not evaluate** the second half, which was the one that blew up. But careful: this version is worse than the original in one case. With `codigo = 503` and `tiempo_ms = 2300`, a service that answered **slow and with an error** would end up LENTO instead of CAIDO, because the time branch wins over the code branch. Fixing the symptom without ordering the branches changed the rules by accident. It is the best reason to leave the code question first.

## How I know I got it

- [ ] `python revisor.py` prints exactly two lines: `SERVICIO    ESTADO    TIEMPO  DETALLE` and `inventario  LENTO       2.3s  200`, with the columns aligned as in figure `fig02_07.py`.
- [ ] When you change the variables to those of `reportes` (`codigo = None`, `tiempo_ms = None`), the program prints `reportes    CAIDO          —  sin conexión` and does **not** end with a *traceback*.
- [ ] With `facturacion` (503, 95 ms) the status is CAIDO and the detail is `503`.
- [ ] You can deliberately provoke `SyntaxError: expected ':'`, `IndentationError`, and `TypeError: can only concatenate str (not "int") to str`, and say in one sentence what the last line of each one says.
- [ ] You can explain in your own words the difference between `=` and `==`, between `200` and `"200"`, and between `None` and `0`.
- [ ] You can explain why the code question goes before the time question in the `if`/`elif`/`else` chain.

## Summary

Answer without looking at the lesson:

1. What type does `type()` return for `142`, for `2.3`, for `"142"`, for `True`, and for `None`?
2. What does `=` do and what does `==` do? And why does `UMBRAL_LENTO_MS` go in capitals?
3. What do `10 / 2`, `7 // 2`, and `7 % 2` give? Why does `0.1 + 0.2` not give `0.3`?
4. How do you ask whether a value is `None`, and why is `==` not used?
5. What do `:<12`, `:>6`, and `:.1f` mean inside an f-string?
6. In an `if`/`elif`/`else` chain, how many blocks are executed at most, and which one? What does indentation do?
7. What is the short-circuiting of `or` and `and`, and what problem does it avoid in the `revisor`?
8. What is the last line of a `SyntaxError` caused by forgetting the colon, and why does that error not show a *traceback*?

## Further reading

- [The Python tutorial, “An Informal Introduction to Python”](https://docs.python.org/3/tutorial/introduction.html) — numbers, text, and variables, with the interactive session you will recognize from Lesson 1. Official documentation. Accessed on October 7, 2026.
- [The Python tutorial, “More Control Flow Tools”](https://docs.python.org/3/tutorial/controlflow.html#if-statements) — the section on `if`, `elif`, and `else`. Accessed on October 7, 2026.
- [PEP 8, the Python style guide](https://peps.python.org/pep-0008/) — the conventions on names, indentation, and comparison with `None` that this course uses. Accessed on October 7, 2026.
- [Format specification mini-language](https://docs.python.org/3/library/string.html#format-specification-mini-language) — everything that can go after the colon in an f-string; not a text to learn straight through but to consult. Accessed on October 7, 2026.
