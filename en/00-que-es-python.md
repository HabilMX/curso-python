# Lesson 0 — What Python is and what it is NOT

**Time:** 90 min

**What you build:** nothing yet (reading)

**What you learn:** what Python does with your file (interpreter and *bytecode*); dynamic but strong typing; type annotations are not enforced at run time; what the GIL is, explained without fear; what a virtual environment is and why the course uses Python 3.14 and also 3.12

**Where you come from.** From nowhere, and that is fine. You do not need Python installed, you do not need to have written a single line of code, and you do not need to know what a virtual environment is. This lesson is **for reading**: you install nothing and you build nothing yet. The programs that appear are one or two lines long, and each one shows the output it produces, so you can follow them without a computer in front of you. If you already have `python3` on your Linux Mint and want to try them, go ahead; if not, [Lesson 1](01-instalacion.md) gets everything ready.

**What this lesson does not do.** It does not teach you to program or to install anything. It teaches **what the thing you are about to learn is**, and above all what it is *not*, because most of a beginner's problems with Python come not from the syntax but from a wrong expectation: believing that Python warns you about a type error before running (it does not), that “interpreted” means “nothing gets compiled” (it is not that simple), or that the GIL prevents doing anything in parallel (it prevents less than people think). Setting your expectations right from the start saves weeks of confusion.

## By the end you will be able to

- Explain, in four steps, what Python does with a `.py` file from the moment you run it until the result appears, and say what *bytecode* is and what the `__pycache__` folder is for.
- Say why Python is **dynamic but strong**, and predict what happens with `"142" + 1` and with `"142" + "1"` without running them.
- Explain why `tiempo_ms: int = "rápido"` runs without complaint, and who can warn you about that contradiction.
- Describe the GIL in your own words, say when it matters and when it does not, and why the `revisor` does not have to worry about it.
- Explain what a virtual environment is and why it exists, and justify why the course is taught with Python 3.14 but all the code also runs on 3.12.
- Read the last line of a `TypeError` *traceback* and say what it tells you.

## The why before the how

Eleven lessons from now you will have written a program called the **`revisor`** (the checker). It takes a list of services (a store's product catalog, its payment system, its inventory), asks all of them at once whether they are working, and hands back a table like this:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Read it the way someone on call would read it at eleven at night. `catalogo` and `pagos` answered quickly. `inventario` answered, but it took 2.3 seconds, which is too long: it is **slow**. `reportes` did not answer: it is **down**, and the detail says why (`sin conexión`, “no connection”). That table is the destination of the course. You do not build it in this lesson, but it works as raw material: every piece of data in it is of a different kind (the name is text, 142 is a number, the dash `—` stands for **no data**), and understanding those kinds is exactly what comes next.

Before writing a single line, three questions need answering, ones every beginner asks even if not always out loud. The first: **what exactly is Python, and what does it do with what I write?** The second: **what will warn me about my mistakes, and what will not?** The third: **why do I see people arguing about “the GIL,” “the virtual environment,” and “which version you use”?** All three have a short answer. The first: Python is a program that reads your text and runs it. The second: almost nothing warns you before the program runs, so you will learn to read errors instead of fearing them. The third: they are three practical decisions worth understanding once.

A **program** is a list of instructions written in a text file. A **programming language** is the set of rules for writing those instructions so that they are clear both to you and to the computer. The problem is that the computer, inside, only understands tiny numeric instructions (add two quantities, copy a value from one place to another) called **machine code**, which depend on the processor. Nobody writes machine code by hand. There is always something in between that **translates**, and the big difference between one language and another lies in *when* and *how* it translates. Python does its translation in a particular way, and that way explains almost everything else in this lesson.

A note on vocabulary before going on. The word “Python” names two different things. One is the **language**: the rules for how it is written, described in a public specification. The other is the **program that runs that language** on your computer, and the one almost everyone uses is called **CPython** (the “C” is because it is written in the C language). When you type `python3` in a terminal, you are calling CPython. Other runners exist (PyPy, for example), but this course, like most professional work, uses CPython. When a phrase like “the GIL” appears below, it will be a feature of CPython, not of the language in the abstract.

## The concepts

There are four: what the interpreter does with your file, what it means for typing to be dynamic but strong (with type annotations as a third part), what the GIL is, and what a virtual environment is along with the versions. They are explained in that order, each with a minimal example.

### 0.1 The interpreter and the *bytecode*

#### 0.1.1 What happens when you run a file

Imagine you save this in a file called `lectura.py`:

```text
tiempo_ms = 142
print(tiempo_ms)
```

(Two words of reading in advance. `tiempo_ms = 142` means “store the number 142 under the name `tiempo_ms`”; the name carries `_ms` because it is the time in milliseconds, and in this course units always go in the name. `print(...)` means “show on screen what goes between the parentheses.” [Lesson 2](02-valores-texto-decisiones.md) explains both in depth.)

To run it you type `python3 lectura.py` in a terminal. What happens then has four steps, and they are worth knowing because each one explains a behavior that would otherwise look like magic.

1. **Python reads the text.** It opens the file and goes through it from top to bottom, checking that it is written correctly according to the rules of the language. If a parenthesis is left unclosed, this is where it is discovered, and the program **does not start running**: not a single earlier line is executed. You can check it with a file whose first line is `print("primera")` and whose second line has an unclosed parenthesis: “primera” does not appear, only the error `SyntaxError: '(' was never closed`. In other words, the check of the form happens before execution.
2. **Python translates the text into a list of instructions of its own.** Not into machine code, but into an intermediate format, simpler than your text and more abstract than the processor. That list is called ***bytecode***. The [official documentation](https://docs.python.org/3/glossary.html#term-bytecode) defines it as “the internal representation of a Python program in the CPython interpreter.”
3. **A virtual machine runs the *bytecode*.** “Virtual” means it is not a physical device but a program that behaves as if it were one: it takes each instruction of the *bytecode*, one at a time, and does what it says. That virtual machine is the heart of CPython, and it is what we call the **interpreter**.
4. **The result appears**, in this case the number `142` on your screen.

All of that happens in a fraction of a second every time you run the file, without your having to ask for it. That is why Python is said to be an **interpreted** language: you run the text file directly, without a prior step in which you yourself generate an executable program. The [documentation explains it](https://docs.python.org/3/glossary.html#term-interpreted) in almost those words (“source files can be run directly without explicitly creating an executable which is then run”), and immediately adds an honest caveat: the distinction between interpreted and compiled “can be blurry because of the presence of the bytecode compiler.” That caveat is the one that matters. Python **does** compile (step 2 is a compilation); it just compiles to an intermediate format, and it does so for you, silently, every time.

The contrast with other languages helps. In Go or in Rust you write your code, run a compiler that produces an executable file (machine code directly for your processor), and then run that file. The executable no longer needs the compiler or the language: you copy it to another computer and it runs. In Python there is no such final file: the computer where you want to run your program needs to **have Python installed**, because it is Python that reads and runs your text each time. This is a practical consequence you will see from Lesson 1 on, and it is the reason half of what is learned “around” Python (versions, environments, installation) has to do with that fact.

#### 0.1.2 What Python keeps: `__pycache__` and the `.pyc` files

Compiling to *bytecode* costs a little time, and if the file has not changed since the last time, repeating that translation is wasted work. That is why Python keeps the result. The [glossary documentation](https://docs.python.org/3/glossary.html#term-bytecode) says that *bytecode* is “also cached in `.pyc` files so that executing the same file is faster the second time.” Those files live in a folder called `__pycache__`, next to your code.

There is a detail that surprises people and that is better measured than assumed. If you run `python3 lectura.py` directly, **no** `__pycache__` folder appears: Python compiles the file you gave it into memory, runs it, and saves nothing. The folder appears when a file is **imported** from another one, that is, when a program uses the contents of another file (`import` is explained in [Lesson 3](03-bucles-funciones-modulos.md)). It was measured like this: one file was run directly and zero `.pyc` files were counted; another one that imported the first was run and one appeared. If you want to force the creation without importing anything, `python3 -m py_compile lectura.py` exists. A fragment, with versions 3.12 and 3.14 on the same machine, shows the name that gets generated:

```text
$ python3.12 -m py_compile lectura.py
$ python3.14 -m py_compile lectura.py
$ ls __pycache__
lectura.cpython-312.pyc
lectura.cpython-314.pyc
```

Look at the name: `lectura.cpython-312.pyc`. It says which file it was (`lectura`), which runner generated it (`cpython`), and with which version (`312` is 3.12). The *bytecode* of one version **does not work** in another, and the [documentation warns about it](https://docs.python.org/3/glossary.html#term-bytecode): “bytecodes are not expected to work between different Python virtual machines, nor to be stable between Python releases.” That is why Python keeps a different file per version and does not mix those of one with those of another.

Three practical consequences:

- **`__pycache__` is safe to delete.** Python creates it again when it needs it. It is not part of your program, it is a cache.
- **It is not saved in the project's repository.** A repository is the place where a team stores and shares a program's code, with its history of changes. Only what you write goes there; `__pycache__` is derived from your code and changes with every Python version, so it is left out.
- **It is not a protection.** Some people believe that shipping only the `.pyc` files hides their code. It does not: `.pyc` files can be read back with tools, and this is not a security measure.

#### 0.1.3 Seeing the *bytecode* (just out of curiosity)

Python ships with a tool, the `dis` module, that shows the *bytecode* of a file in readable form. You do not need to learn it, but seeing it once removes the mystery. This is the result in Python 3.12 for the two lines of `lectura.py`:

```text
$ python3.12 -m dis lectura.py
  0           0 RESUME                   0

  1           2 LOAD_CONST               0 (142)
              4 STORE_NAME               0 (tiempo_ms)

  2           6 PUSH_NULL
              8 LOAD_NAME                1 (print)
             10 LOAD_NAME                0 (tiempo_ms)
             12 CALL                     1
             20 POP_TOP
             22 RETURN_CONST             1 (None)
```

The middle column holds the instructions. `LOAD_CONST 142` means “put the constant value 142 within reach,” `STORE_NAME tiempo_ms` means “store it under the name `tiempo_ms`,” and those on line 2 ask for the name `print`, ask for the name `tiempo_ms`, and call the first with the second. Each line of your text turns into two, three, or four of these. And here is the reason this block is a **fragment** and not a program of the course: *the bytecode changes between versions*. When measured in Python 3.14, the first instruction of line 1 is no longer called `LOAD_CONST 142` but `LOAD_SMALL_INT 142`, and the order of two instructions on line 2 is different. The program's behavior is the same; the internal language the virtual machine uses to describe it is not. What you should take from this is not any of those words but the idea: between your text and the result there is an intermediate list of instructions that you do not write and that Python hides from you.

#### 0.1.4 Why this matters for the `revisor`

Two things. The first: Python takes longer than a program compiled to machine code to run pure calculations, because every *bytecode* instruction goes through the virtual machine. In a program that multiplies millions of numbers you notice it. But the `revisor` hardly calculates at all: it **spends its time waiting** for a network to answer. While it waits 2.3 seconds for the reply from `inventario`, Python's speed is irrelevant. What will matter is waiting for all the services at once instead of one after another, and that is a topic for lessons 9 and 10. The second: since Python needs to be installed where your program runs, and since each version has its own *bytecode* and its own behavior, knowing **which Python you are using** is a question you will ask yourself often. The answer is in the last section of this lesson.

### 0.2 Dynamic typing, but strong

#### 0.2.1 What a type is

A **value** is a concrete piece of data: the number `142`, the text `"catalogo"`. The **type** of a value is the kind of thing it is: a whole number, a text, a dash that means “no data.” A **name** (or variable) is a label you point at a value, like `tiempo_ms` in the previous example. Look at the `revisor`'s table: `catalogo` is a text, `142` is a number, `—` is the absence of data. The type matters because it determines **what can be done** with the value: numbers are added, texts are glued to one another. And the question that sets languages apart is *when and by whom* it is checked that what you are trying to do makes sense for that type.

#### 0.2.2 Dynamic: the type lives in the value, not in the name

In Python, **the type belongs to the value, not to the name**. A name can point to a number today and to a text tomorrow, and Python does not care. The check of whether an operation makes sense happens **while the program runs**, at the very moment that line is executed: that is what **dynamic** means. This contrasts with statically typed languages (Go, Rust, Java), where each name is declared with its type and the compiler checks everything before running.

Look at the first figure. It is a single line and has to be read piece by piece.

```python
# fig00_01.py
print(142 + 1, "142" + "1")
```

```text
$ python3 fig00_01.py
143 1421
```

The first line is a **comment**: everything after a `#` is a note for humans that Python ignores. Here it carries the name of the figure, so you know which file it is. The second line is the one that runs. `print(a, b)` shows the two values separated by a space, and that is why the output has two things: `143` and `1421`. The interesting part is that **both use the same `+` sign** and give results of a different nature.

- `142 + 1`: both are numbers (they have no quotes), and `+` **adds** them: 143.
- `"142" + "1"`: what is between quotes is **text**, even if it looks like a number. A text is written between quotes, double or single. Here `+` does not add: it **glues** one text to the other, and the result is the text `1421`, shown without the quotes.

The sign is the same, but what it does depends on the type of the values. This is the first lesson about types: `"142"` and `142` **look almost the same and are different things**. In the `revisor`, the `142` in the table is a number that can be compared with 1000 to decide whether a service is slow; if by mistake it arrived as the text `"142"`, that comparison would make no sense.

Another way to see the dynamic nature is for the same name to change type. This fragment is valid in Python:

```text
lectura = 142
lectura = "rápido"
```

The name `lectura` first pointed to a number and then to a text. Python does not complain, because there is no place where you said “`lectura` is a number” and the rule is kept. That freedom is convenient for writing fast and dangerous for writing carelessly, and that is why this course, although Python does not require it, will teach you to be tidy: one name, one kind of data.

#### 0.2.3 Strong: Python does not guess what you meant

Python being dynamic does **not** mean it is permissive. It is dynamic **and strong**: when you attempt an operation that makes no sense for those types, Python **does not invent a conversion**; it stops and tells you there is an error. Let us look at the second figure, a single line that mixes a text with a number.

```python
# fig00_02.py
print("142" + 1)
```

```text
$ python3 fig00_02.py
Traceback (most recent call last):
  File "fig00_02.py", line 2, in <module>
    print("142" + 1)
          ~~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

The program **printed nothing**: it stopped and showed an error report, which in Python is called a ***traceback*** (something like “the trail backwards”). For now look only at the last line: `TypeError: can only concatenate str (not "int") to str`. “`TypeError`” is the class of the error (a problem with types); what follows is the explanation in English. Translated: “you can only concatenate (glue) a `str` (text) with another `str`, not with an `int` (whole number).” Python is telling you that you tried to glue a text to a number and it does not know what to do. The section “The error you will see” reads the rest of the report line by line. (On your screen the path of the file will be long and complete; here it is shortened to the name so that it reads well.)

Here is the **strong** part. Other languages, faced with `"142" + 1`, resolve it on their own: JavaScript, for example, converts the number to text and returns `"1421"` without warning. That may seem friendly and it is a classic source of errors, because the program keeps running with a piece of data nobody expected. Python prefers the immediate complaint to the silent conversion. That decision plays in your favor: the error appears **where it happens**, with the name of the problem and the exact line, and not three functions later as a strange result.

Put the two halves together and you get the complete behavior. **Dynamic**: the type check happens when each line is executed, not before. **Strong**: when that check fails, Python stops instead of guessing. One consequence follows that you must keep in mind: **a type error only appears if that line actually gets executed**. If your program has a branch that is used once a month, a type error hidden there will not be discovered until that day. It is an argument in favor of tests (Lesson 8) and of tools that check the code without running it.

#### 0.2.4 Type annotations: a promise Python does not police

Python lets you *write* the type you expect next to a name, and it does so with a syntax called an **annotation**: `nombre: tipo = valor`. The [documentation calls them “type hints”](https://docs.python.org/3/glossary.html#term-type-hint) and says two important things: that they are **optional** and that they “are not enforced by Python.” Let us see what that means with the third figure:

```python
# fig00_03.py
tiempo_ms: int = "rápido"
print(tiempo_ms)
```

```text
$ python3 fig00_03.py
rápido
```

Read it calmly, because it contains a deliberate contradiction. Line 2 says: “the name `tiempo_ms` is of type `int`” (`int` is short for *integer*, the type of numbers without decimals), and then assigns it `"rápido"`, which is a text. A statically typed language would reject the program. Python **runs it without complaint** and shows `rápido`. The annotation was written down, but nobody compared it with the value.

This is the part of the lesson most worth remembering: **type annotations are not enforced at run time**. The specification that created them, [PEP 484](https://peps.python.org/pep-0484/), says so bluntly: *Python will remain a dynamically typed language, and the authors have no desire to ever make type hints mandatory, even by convention*. So why are they written?

- **So that people **read** them.** An annotation documents what kind of data is expected in each place, and unlike a comment, it has a format that does not rot easily.
- **So that the editor **uses** them.** Many editors show suggestions and warn about contradictions as you type.
- **So that a separate tool **checks** them.** There are programs called type checkers, the best known being `mypy`, that read your code **without running it** and report that `tiempo_ms: int = "rápido"` is a contradiction. They are taught in [Lesson 8](08-pruebas-tipos-calidad.md). The [`mypy` documentation](https://mypy.readthedocs.io/en/stable/getting_started.html) explains that its checking is **gradual**: it checks the annotated parts and lets the unannotated ones through.
- **So that other parts of the language can take advantage of them.** In [Lesson 5](05-modelo-de-datos.md) you will use `dataclass`, a tool that reads the annotations to build things; there they serve a real function, even though they still do not validate values.

Put another way, in Python **there are two different checkers**: the interpreter (it checks at run time, strongly but late) and the type checker (it checks before running, but only if you run it and only what you annotated). The interpreter never consults the annotations to decide whether something is valid. If you come from Hábil's [TypeScript](https://www.habil.mx/en/courses/typescript/) course, the principle is the same as there: written types are a promise that a tool can check, not a barrier the program raises when it runs.

And there is a limit no annotation crosses: **data that comes from outside**. If your program reads a configuration file and someone writes `"timeout_ms": "rápido"` in it, it does not matter what you annotated in your code: the text will arrive as it is. That data has to be **validated** on the way in, with code that really compares it, and that is done in [Lesson 6](06-errores-archivos-datos.md). The annotation is a promise between the parts of your program; validation is what protects you from what the program does not control.

One last up-to-date fact, with no consequences for you: in Python 3.14 *when* annotations are evaluated changed (they are no longer evaluated at the moment they are defined), according to the [release's list of new features](https://docs.python.org/3/whatsnew/3.14.html). To write code that runs the same on 3.12 and on 3.14, this course avoids depending on that change, and says so when needed.

### 0.3 The GIL, explained without fear

Sooner or later someone will tell you “Python cannot do things in parallel because of the GIL.” The phrase is scary and oversimplifies. Let us take it in parts.

First, two words. A **thread** is a line of execution inside a program: a program can have several, and in principle each can move forward while others wait. And a modern **processor** has several cores, which can execute instructions at the same instant. Taking advantage of several cores with several threads is what is called **parallelism**.

The **GIL** (*Global Interpreter Lock*) is a rule of CPython. The [documentation defines it](https://docs.python.org/3/glossary.html#term-global-interpreter-lock) like this: it is the mechanism that ensures that **only one thread executes Python *bytecode* at a time**. It exists because it simplifies the interpreter's design: internal structures, such as dictionaries, are protected from two threads modifying them at the same time. The price, the same definition says, is that a good part of the parallelism of multi-processor machines is lost.

Translated into practice, the GIL affects two kinds of work differently:

- **Computation work** (converting a thousand images, compressing a large file): with Python threads, it is not spread across cores; a single thread computes at a time. Here the GIL gets in the way.
- **Waiting work** (asking a network, reading a file, waiting for a database's answer): the thread that waits releases the lock while it is not running Python, and another one can move forward. Here the GIL hardly gets in the way. The [documentation of the `threading` module](https://docs.python.org/3/library/threading.html) puts it like this: threads are still an appropriate model when you want to run multiple **I/O-bound** tasks at the same time.

The `revisor` is of the second kind, **almost entirely**. Its job is to wait for answers from the network, not to calculate. And besides, it will not use threads: it will solve “ask everyone at once” with **`asyncio`**, which runs in a single thread and switches between tasks every time one starts waiting. In that scheme the GIL does not even enter the conversation. You can forget about it while you use this course, but not the fact: knowing it exists lets you neither believe nor repeat the exaggerated phrase.

And if someday you wanted parallel computation? Today there are two paths this course does not walk: using several **processes** (each with its own interpreter and its own GIL) and, recently, a variant of CPython **without a GIL**. The story of that variant, in short: [PEP 703](https://peps.python.org/pep-0703/) proposed making the GIL optional and it appeared as an experiment in 3.13; [PEP 779](https://peps.python.org/pep-0779/) declared it officially **supported** as of 3.14, but it is **not the default option**: it is a separate executable, with a speed cost when a single thread is used, and many libraries are still adapting. It is what this course calls “what is coming”: it is mentioned, not used, and not recommended for production from the start.

### 0.4 The virtual environment and the versions

#### 0.4.1 The problem a virtual environment solves

Think of your kitchen. You have the household pantry, where the things the whole family uses live: salt, oil, rice. If you, for an experiment, start putting strange jars in there, swapping the rice for another kind, or taking out the oil, you get in everyone else's way and one day someone will not be able to cook. The sensible thing is to have **your own shelf** for your experiments.

The Python that comes with your Linux Mint is the household pantry. The operating system uses it for its own tools, and it depends on its libraries being at a certain version. If you install your own packages there, or change one, you risk breaking something in the system. And there is a second problem, independent of the first: **two projects of yours may need different versions of the same library**. If all the packages live in a single place, one of the two projects loses.

The solution is called a **virtual environment** (*venv*): a folder with its own Python (on Linux, a shortcut to the Python it was created with, not a copy; Lesson 1 shows it) and its own space for packages, isolated from the rest. The [official documentation](https://docs.python.org/3/glossary.html#term-virtual-environment) defines it as a “cooperatively isolated” runtime environment that allows installing and upgrading packages “without interfering with the behaviour of other Python applications” on the same system. What you install inside an environment lives only there; if something goes wrong, you delete the environment folder and recreate it, and the system never notices.

Linux distributions have taken this seriously. Since the [PEP 668](https://peps.python.org/pep-0668/) specification exists, a distribution can mark its Python as **“externally managed”**: it means that Python belongs to the system's package manager and that `pip` (Python's tool for installing packages) must refuse to install anything in it outside a virtual environment. In your Linux Mint the protection is even more direct: its Python does not even come with `pip`. You will see the refusal with your own eyes, and you will learn to read the two forms it takes, in Lesson 1. For now it is enough to know that **it is not a failure of your installation**: it is a protection, and the correct way out is the virtual environment.

#### 0.4.2 The versions, and why two

Python versions have three numbers: `3.14.8` reads as major, minor, and patch. The first (3) has not changed in years. The second (14) changes **once a year, in October**, and introduces new features. The third (8) is bug fixes that do not change what the language allows. When people say “Python 3.12” they mean a line of versions, and the patch can be anything.

Three facts support the decisions of the course, all measured on the date this lesson was written (October 7, 2026):

- **The current stable version is 3.14.** It came out on October 7, 2025, and the [official downloads page](https://www.python.org/downloads/) showed 3.14.8, from September 30, 2026, as the latest. 3.15 was scheduled for October of this year according to the [Python Developer's Guide](https://devguide.python.org/versions/) and still appeared in pre-release status.
- **Linux Mint 22.x ships Python 3.12.** Mint 22 and its updates (22.1, 22.2, 22.3) are built on the Ubuntu 24.04 base, with [support until April 2029](https://linuxmint.com/download_all.php), and that base is what decides the Python that comes installed: the 3.12 line.
- **3.12 keeps receiving security fixes until October 2028**, according to the same Developer's Guide. By contrast, 3.10 reached end of life on October 1, 2026: whoever is still on it no longer receives even security fixes.

Hence the decision: **the course is taught with Python 3.14 and all its code also runs on 3.12**, the one your Mint ships. Every program in the lessons is run with both versions and its result is compared with the one you see in the text. That has a cost, which is not using a handful of new features that exist only in 3.14, and a decisive advantage: **you do not have to install anything special** to follow the course, nor stop using your system's Python. If someday you want to try 3.14, Lesson 7 tells you a convenient way to install it.

So when the command `python3` appears, what runs on your Mint is 3.12, and that is correct. One last warning that will save you an afternoon: on many systems the `python` command (without the 3) does not exist, or points to something else. By the end of this lesson you know the course's rule: **outside a virtual environment you write `python3`; inside the environment, `python` points to the environment's Python** (Lesson 1 checks it with `which`).

## The error you will see

The only error in this lesson is the one in figure 2, and it is worth reading in full because all Python error reports have the same shape. Here it is again, with the name of each line; there is no need to run it again.

The first line of the report is `Traceback (most recent call last):`, which translates as “trail, most recent call last.” It is a sign that what follows is a list of places, ordered from **the oldest to the most recent**, and that what happened is **at the end**. That is why the golden rule for reading an error report in Python is to **start at the last line and go up**.

The last line is `TypeError: can only concatenate str (not "int") to str`. It contains the error's **class** (`TypeError`) and its **message**. `TypeError` means an operation received a value of a type it does not accept. The message says exactly which: someone tried to glue (`concatenate`) a `str` with something that was not a `str` but an `int`. With that alone you already know what happened and why.

Going up one line you find the picture of the error: `print("142" + 1)` on the code line, and below it a mark made of tildes and a caret (`~~~~~~^~~`). That mark points to **which exact part** of the line failed: the `+` that joins `"142"` with `1`. It is a help that recent versions add, and it saves you from guessing on a long line.

Go up another line: `File "fig00_02.py", line 2, in <module>`. It tells you **in which file**, **at which line number**, and **inside what**. The word `<module>` means “at the level of the file, not inside a function”; once you know functions (Lesson 3), here you will see the name of the function instead of `<module>`. The line is 2 because line 1 is the comment with the figure's name.

The fix is not to convert anything to text to make the error go quiet. First decide what you meant. If you meant to add, both must be numbers (`142 + 1` gives 143). If you meant to build a text message, both must be text (`"142" + "1"`), and then the result is glued, not added. The error forced you to decide what each piece of data represented. That is what a good error message does.

## What gets done wrong

- **Believing that an annotation validates the data.** Writing `tiempo_ms: int` does not prevent `tiempo_ms` from being `"rápido"`. If you need the guarantee, you need a type checker (while you write) or an explicit validation (when the data comes from outside). The annotation alone does neither.
- **Fixing a `TypeError` by converting everything to text.** Adding quotes or calling a conversion function until the error disappears hides the fact that you mixed two ideas. First ask what each value should be.
- **Saying “Python is interpreted, so it does not compile.”** It does compile (to *bytecode*); it does so for you and on every run. Saying “without compiling” leads to surprises, such as not understanding what a `__pycache__` is or why syntax errors appear before the first line.
- **Blaming the GIL for any slowness.** A program that waits on a network is not slow because of the GIL: it is slow because it waits, and that is fixed by waiting for everyone at once. Before blaming the GIL, measure what your program is doing while it takes its time.
- **Saving `__pycache__` in the repository, or believing it has to be protected.** It is a Python cache, derived from your code, different in each version. It is left out.
- **Installing packages with `sudo pip` in the system's Python.** It is the shortcut to refuse and the one that leads to breaking system tools. Every package of your projects lives in a virtual environment (Lesson 1). Although `pip` offers an option to bypass the PEP 668 protection, the course does **not** teach it or use it.
- **Mixing `python` and `python3` without knowing which is which.** Whenever you wonder “which Python am I using?”, the right question is `which`, and it is answered in the next lesson.

## Exercises

### Exercise 1 — The data in the table

Look at the `revisor`'s table from the beginning. For each of these four cells, say whether its data is a **number**, a **text**, or **nothing** (absence of data): the `142` of `catalogo`, the `catalogo` in the first column, the `—` in the time of `reportes`, and the `200` in the detail of `pagos`. Then answer: why would it be a problem if the time of `inventario` reached the program as the text `"2300"` instead of the number 2300?

### Exercise 2 — Predict before running

Without running anything, write what each of these three lines does: the one that shows a result, the one that shows a different result, and the one that fails. For the one that fails, write the **last line** of the error report.

```text
print(142 + 1)
print("142" + "1")
print(142 + "1")
```

### Exercise 3 — The promise nobody polices

With figure 3 in front of you (`tiempo_ms: int = "rápido"`), answer in your own words: (a) why does the program show `rápido` and not an error? (b) If you installed a type checker and ran it on that file, what would you expect it to say? (c) If the value `"rápido"` arrived from a configuration file and not from a line you wrote, would the annotation be of any use?

### Exercise 4 — Explain it to a colleague

A coworker tells you: “Python is slow because it is interpreted, and it cannot do anything in parallel because of the GIL, so to query many services you have to use another language.” Write your answer in four or five sentences, precisely correcting what is incomplete or exaggerated and saying what the `revisor` really does during almost all of its time.

## Solutions

### Solution 1

The `142` is a **number**; `catalogo` is a **text**; the `—` stands for **no data** (the service did not answer, so there is no time to measure); the `200` in the detail is the code the service answered with and, in the table, it is shown as text, because in that column things like `sin conexión` can also appear (that column mixes the two kinds, and that is why the program will always treat it as text). The time of `inventario` arriving as the text `"2300"` would be a problem because the `revisor` compares it with the threshold of 1000 to decide whether the service is slow. A text is not meaningfully compared with a number: Python, being strong, would stop with a `TypeError` instead of giving a wrong verdict.

### Solution 2

The first line adds two numbers and shows `143`. The second glues two texts and shows `1421`. The third fails, because it mixes a number with a text; the last line of the report is `TypeError: unsupported operand type(s) for +: 'int' and 'str'`. The message differs from the one in figure 2 because here the number is on the left: Python first tries to add and, since it cannot, says that the `+` operator does not accept an `int` with a `str`. What matters is the class (`TypeError`) and understanding that the cause is the same: two types were mixed.

### Solution 3

(a) Because annotations are not enforced at run time: Python recorded the `int` annotation but never compared it with the assigned value. (b) That there is a contradiction: an `int` was declared and a text was assigned to it. The checker reads the code without running it and compares the annotations with the values. (c) No: an annotation is a promise between parts of *your* code. A value that arrives from outside comes in as it is, whatever its contents, and only an explicit validation on the way in (Lesson 6) can check that it really is a number.

### Solution 4

One possible answer: “It is true that Python runs pure calculations more slowly, but a program that queries services hardly calculates at all: it spends its time waiting for answers from the network. The GIL prevents two threads from executing Python *bytecode* at the same time, but a thread that waits releases the lock, and anyway the `revisor` does not use threads but `asyncio`, which switches between tasks in just one. What decides how long it takes is waiting for everyone at once instead of one after another: with four services that take 142, 2300, and 87 milliseconds (the fourth does not answer), in series it adds up to about 2.5 seconds and at once it takes about as long as the slowest, around 2.3. And if heavy parallel computation were ever needed, there are other paths, such as several processes.”

## How I know I got it

- [ ] You can list from memory the four steps between running a file and seeing the result (read and check the form, translate to *bytecode*, run on the virtual machine, show the result) and say at which one an unclosed parenthesis is detected.
- [ ] You can explain what `__pycache__` is for, say why it is safe to delete, and why it is not saved in the repository.
- [ ] You know how to predict that `print(142 + 1, "142" + "1")` shows `143 1421`, and that `print("142" + 1)` ends in `TypeError`; and you can explain the difference between “dynamic” and “strong” with those two examples.
- [ ] You can say, without looking at the lesson, why `tiempo_ms: int = "rápido"` gives no error when run and what kind of tool would warn about it.
- [ ] You can explain in two sentences what the GIL is, when it matters (computation with threads), and why it does not affect the `revisor`.
- [ ] You can explain with an analogy of your own what a virtual environment is and why Linux Mint rejects `pip install` in its system Python.
- [ ] You can say which Python version Mint 22.x ships, which one is current at the lesson's date, and why the course is taught with one and runs on both.

## Summary

Answer without looking at the lesson:

1. What two things does the word “Python” mean? What is CPython?
2. What is *bytecode* and where is it saved? Why does a 3.12 `.pyc` not work in 3.14?
3. What is the difference between dynamic typing and strong typing? What comes out of combining them?
4. Who checks type annotations, and who does not?
5. What is the GIL? In what kind of work does it get in the way, and in which does it hardly matter?
6. What problem does a virtual environment solve? Why does Mint not let `pip` install into its system Python?
7. Why is the course taught with 3.14 and also runs on 3.12?

## Further reading

- [Python glossary](https://docs.python.org/3/glossary.html) — the official definitions of *bytecode*, interpreted, GIL, virtual environment, and type hint that are quoted in the lesson. Accessed on October 7, 2026.
- [PEP 484, “Type Hints”](https://peps.python.org/pep-0484/) — the document that introduced type annotations and says they are not enforced at run time. Accessed on October 7, 2026.
- [PEP 668, “Marking Python base environments as externally managed”](https://peps.python.org/pep-0668/) — the origin of the `externally-managed-environment` warning that the next lesson teaches you to recognize. Accessed on October 7, 2026.
- [Python Developer's Guide: status of Python versions](https://devguide.python.org/versions/) — which version is current, which one receives security fixes, and when each one ends. Accessed on October 7, 2026.
