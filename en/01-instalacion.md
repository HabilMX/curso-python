# Lesson 1 — Installing Python on your Linux Mint

**Time:** 90 min

**What you build:** the course's virtual environment, your first script (`hola.py`), and the file where the `revisor` (the checker) will live

**What you learn:** the system's `python3` and why it does not install packages (`No module named pip` and the `externally-managed-environment` warning); creating, activating, and deactivating a virtual environment (`venv`); `pip` inside the environment; the REPL and running a file; reading your first *traceback*

**Where you come from.** From [Lesson 0](00-que-es-python.md), which was for reading: you already know that Python reads your file, translates it to *bytecode*, and runs it; that types are checked at run time and not before; that the GIL is not going to get in your way; and that there is something called a virtual environment that protects your system's Python. Today you stop reading and move to the terminal. You work on a computer with **Linux Mint 22.x** (any of its versions, from 22 to 22.3, which share the same base) and with a terminal open. Almost nothing you will do requires administrator permissions: at most one line (with two administrator commands inside), and only if your Mint does not ship the piece that creates virtual environments (you will see it in 1.2.2). What is more, one of the things you will learn today is **not** to install Python packages with those permissions.

**What this lesson does not do.** It does not teach the language yet: the `print` you are going to use is explained in one line and [Lesson 2](02-valores-texto-decisiones.md) studies it in depth. Nor does it install `uv` or `pipx`, other tools you will see later: today you use what the system already ships, because understanding the environment with the basic pieces is what later lets you understand why the other tools exist.

## By the end you will be able to

- Check which Python your Mint ships (`python3 --version`) and where it runs from (`which python3`).
- Deliberately try to install a package in the system's Python, read the response, and explain why Mint protects its Python, what the `externally-managed-environment` warning looks like on systems that do ship `pip`, and what the correct way out is.
- Create the course's virtual environment with `python3 -m venv`, activate it, check with `which python` that you are inside, install a package with `pip`, and deactivate it.
- Type an expression in the REPL, exit it, and tell when the REPL is the right tool and when a file is.
- Create and run `hola.py` and `revisor/revisor.py`, inside and outside the environment, and note which `python` was used in each case.
- Read a `NameError` *traceback* from the last line upward and say which misspelled word caused it.

## The why before the how

To take the first step with the `revisor` you need a firm base: a Python that works, a place to keep the packages the course will need, and a folder where the project will live. If that base is improvised, the problems appear later and in the most confusing form possible: a package that “got installed” but cannot be found, a Python version that is not the one you thought, a command that worked yesterday and not today. This lesson exists so that does not happen to you.

Think of setting up a workshop before building a piece of furniture. It is not the exciting part, but it decides whether the rest comes out clean. In the Python workshop there are three things to prepare. The **first** is knowing which Python you have and whose it is: your Mint already ships one, and it belongs to Mint, not to you. The **second** is creating your own workspace, the virtual environment, where you can install and break things without consequences. The **third** is checking that everything works by running the smallest possible program.

There is one more reason to do it right now, and it is that **the stumble you will see today is the same one you will have in a real job**. Almost everyone who installs Python on modern Linux runs into, sooner or later, a system Python that refuses to install packages: on your Mint, because it does not even ship `pip`; on other systems, with a message that says `externally-managed-environment`. Many people read it as an obstacle, search the internet for how to get around it, and end up using an option that breaks the system's protection. This course does the opposite: it **provokes the refusal on purpose**, reads it line by line, and shows that it is a help, not a wall. Whoever understands it once solves it in ten seconds for the rest of their life.

### The minimum of the terminal you need today

The terminal is a window where you type commands instead of clicking. In Mint it opens with the shortcut `Ctrl + Alt + T`, or by searching for “Terminal” in the menu. In this course, the lines that start with `$` are what **you type**, and the others are what the computer answers. The `$` itself is not typed: it is the symbol the terminal shows you to indicate it is waiting for a command. Today's commands are few:

- `pwd` (*print working directory*): shows which folder you are in.
- `ls`: lists what is in the current folder.
- `cd carpeta`: moves you to that folder. `cd ..` goes up one level and `cd` with nothing after it takes you to your home folder.
- `mkdir carpeta`: creates a folder.
- `which nombre`: shows **which file** would be run if you typed that name. It is the tool that answers “which Python am I using?”.
- `~`: a shortcut for your home folder, the one that holds your documents. `~/curso-python` means “the `curso-python` folder inside your home folder.”

If any of these is new to you, try it now in your terminal before going on: type `pwd`, press Enter, and compare with what it says. It breaks nothing.

## The concepts

There are four: the system's Python and the error that protects it; the virtual environment with `pip`; the REPL and files; and the first *traceback*. Each one ends with something you can check on your screen.

### 1.1 The system's `python3` and the `externally-managed-environment` error

#### 1.1.1 Which Python you have

Open a terminal and type:

```text
$ python3 --version
Python 3.12.3
```

On any Mint 22.x the output is `Python 3.12.3`, however many updates it has received: Ubuntu 24.04, Mint 22's base, published the Python package with the number 3.12.3 and since then delivers its fixes as revisions of that same package (`3.12.3-1ubuntu0.1`, `3.12.3-1ubuntu0.2` and so on up to `3.12.3-1ubuntu0.17`, the current one on October 22, 2026), without changing the number Python prints. The [page of the `python3.12` package for Ubuntu 24.04 on Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12) shows it. What matters is the `3.12`. That is the version the course works with, and as you saw in the previous lesson, all the code also runs on 3.14. If your terminal says something else (a 3.10 or a 3.11), the course will almost surely work the same, but 3.10 reached end of life on October 1, 2026; note it in the [logbook](bitacora.md) and go on.

Now ask **where** that Python comes from:

```text
$ which python3
/usr/bin/python3
```

`/usr/bin/` is the folder where the system keeps its own programs. That your `python3` is there means **it is Mint's**: the distribution installed it, the package manager (`apt`) updates it, and several system tools depend on it. It is the “household pantry” from the previous lesson.

If you are on another system (a macOS, or a Linux with Python installed some other way), `which` will show a different path. Nothing wrong with that, but the error in the next section may be different or may not appear, and this course is written for Mint.

#### 1.1.2 Trying to install something, and the system saying no

`pip` is Python's tool for installing **packages**: libraries of code that other people wrote and published in a public catalog called **PyPI**, so you do not have to write them yourself. The course will later need a package called `httpx`, which is used to query services over the network. Let us try to install it, **on purpose, the wrong way**: with the system's Python, outside any environment. On a freshly installed Linux Mint 22, this is what happens:

```text
$ python3 -m pip install httpx
/usr/bin/python3: No module named pip
```

The command reads: “run the `pip` module with Python (`-m` means *module*) and ask it to install `httpx`.” It is written `python3 -m pip` and not just `pip` for a reason explained by the [pip documentation](https://pip.pypa.io/en/stable/getting-started/): this way you make sure the `pip` that runs is the one **belonging to that Python**, and not another one that may be on your system.

The response reads like any error report, from the end: `No module named pip`, “there is no module called `pip`.” Before the colon comes who is speaking: `/usr/bin/python3`, the system's Python. It is not a failure of yours or of the course. In the Debian and Ubuntu family, which Mint comes from, `pip` is a separate system package (`python3-pip`), and a freshly installed Mint does not ship it. That Python is administered by the system's package manager, not by you. The practical result is what matters: **outside an environment, nothing gets installed**. Inside the virtual environment, which you will create in a moment, `pip` comes included.

#### 1.1.3 The warning you will see if one day you install the system's `pip`

There is a second protection, more explicit, and it is worth recognizing because it is the one you will find on almost any modern Linux where `pip` is present on the system (for example, if one day you install Mint's `python3-pip` package, or on another distribution). **Do not provoke it**: you do not need to install anything to understand it. There, the same command does not say `No module named pip`, but a message that begins like this:

```text
error: externally-managed-environment
```

This is what the specification that causes it, [PEP 668](https://peps.python.org/pep-0668/), says: Python tools “should neither install nor remove packages into the interpreter’s global context, by default” when that interpreter is administered by another package manager. The mechanism is simple: the distribution leaves a file called `EXTERNALLY-MANAGED` in the standard library folder of its Python, and `pip` looks for it before installing. If it finds it, it stops. That folder can be asked of Python:

```text
$ python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))"
```

It prints the path of your Python's standard library, a folder whose name ends in `python3.12`; the specification says that is where the marker file goes.

That command is a recipe to copy as it is; you do not need to understand all of it today, but you should know what each piece does. `-c` means “run this text as a program”: it is a quick way to ask Python a one-off question without creating a file. The text between quotes is **two statements**, separated by the semicolon `;`, which in Python lets you write two statements on the same line (in the course's files it is not used: each statement goes on its own line). The first, `import sysconfig`, brings in a **module**, a set of tools that comes with Python and is not available until you ask for it; [Lesson 3](03-bucles-funciones-modulos.md) explains `import` in depth. The second, `print(sysconfig.get_path('stdlib'))`, asks that module for the path of the standard library (*stdlib*) and shows it with `print`.

The complete message, besides, **tells you what to do**, and that is why it is a lesson and not a wall. The specification allows the distribution to put its own help text inside the marker file, so the body changes from one system to another; the usual thing is that it suggests three ways out: install the package with the system's manager if a packaged version exists, create a virtual environment if not, or use `pipx` if what you want to install is an application and not a library. For what the course does, the way out is the second: **a virtual environment**. In the section “The error you will see” you have a complete example, read in parts.

There is also a fourth way out, and `pip` tells you about it itself in the note that closes the message: an option called `--break-system-packages`, which turns off the protection and lets you install anyway. The specification admits it must exist, and it exists. **This course neither teaches nor uses it.** It is the equivalent of removing the lock because you could not find the key: it works until a package you installed overwrites a library the system needed, and then tools that have nothing to do with your project fail. The key exists and it is called a virtual environment.

### 1.2 The virtual environment: create, activate, use `pip`, deactivate

#### 1.2.1 Creating the environment

First the course folder. Everything you do will live inside `~/curso-python/`:

```text
$ mkdir ~/curso-python
$ cd ~/curso-python
$ python3 -m venv .venv
```

The third line is the one that creates the environment. It reads: “run the `venv` module with `python3` and create an environment in a folder called `.venv`.” The dot at the start of the name makes the folder “hidden” by convention: it does not appear in a normal `ls`. It is the usual name for environments and some tools recognize it by themselves. When everything goes well, it **prints nothing**; in the terminal, silence is success.

The environment lives in `~/curso-python/.venv`, **not** inside the project folder `revisor/` that you will create below. There is a reason: the documentation of the [`venv`](https://docs.python.org/3/library/venv.html) module says an environment is considered “disposable” (it should be easy to delete and recreate it from scratch) and that “you don’t place any project code in the environment.” Keeping it apart from the code is the cleanest way to comply.

#### 1.2.2 If your Mint does not ship the environments piece

On a freshly installed Mint 22, the most likely thing is that the third line will **not** come out silent, but with this message:

```text
$ python3 -m venv .venv
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /home/tu_usuario/curso-python/.venv/bin/python3
```

Read it in parts. The first sentence says what happened: the environment “was not created successfully” because `ensurepip` is missing, the piece that puts `pip` inside each new environment. The second says why: on systems of the Debian and Ubuntu family, which Mint comes from, that piece arrives in a separate package. The third gives you the exact command, `apt install python3.12-venv`, and the next one warns you of two things: that you may need `sudo` and that, after installing, you have to **recreate** the environment. The last line, `Failing command`, says which internal command failed; you do not have to do anything with it.

Notice the word “recreate,” because it hides a trap. Although the message says the environment was not created, **the `.venv` folder did stay on disk**, half-built: it has `pyvenv.cfg`, the `lib` and `include` folders, and, inside `bin`, only the shortcuts to Python (`python`, `python3`, and `python3.12`). Two things are missing: `pip` and the `activate` script. That is why it cannot be used yet: `source .venv/bin/activate` would answer `No such file or directory` (“that file does not exist”), a message that does not mention the environment and that is bewildering if you do not know what happened.

The way out is two commands:

```text
$ sudo apt update && sudo apt install python3.12-venv
$ python3 -m venv .venv
```

- **`sudo apt update && sudo apt install python3.12-venv`.** `apt` is the system's package manager, the one that installs and updates Mint's programs. `sudo` means “run this command with administrator permissions”: installing something for the whole system needs them, so the terminal will ask for **your password** (while you type it nothing appears on screen, not even asterisks; that is normal). The line is really two commands joined by `&&`, which means “and, if the first one went well, the second.” The first, `apt update`, installs nothing: it downloads the up-to-date list of available packages, so the second finds the current version (with an old list, `apt` may not find the package or may choose a version that no longer exists). The second installs `python3.12-venv`; `apt` will tell you it installs **three** packages (`python3.12-venv` and two it depends on: `python3-pip-whl`, which brings the `pip` that will go into each environment, and `python3-setuptools-whl`, another packaging tool the course does not use) and will ask whether you want to continue: answer `s` (the Spanish “sí”; or `y`, if your Mint is in English) and Enter. Here you are not installing a Python package with `pip`, but a system program that completes the system's Python, and that is why it is a matter for `apt`. Outside this line, the course only uses `sudo` again in [Lesson 11](11-el-programa-terminado.md), to install `pipx`, and it is of the same kind.
- **`python3 -m venv .venv`**, again, on the same folder. Now it should come out silent. There is no need to delete the half-built folder: `venv` reuses it and completes what was missing, the `activate` script and `pip`.

Check that this time the environment ships its `pip`, calling it by its path (still without activating anything):

```text
$ .venv/bin/python -m pip --version
pip 24.0 from /home/tu_usuario/curso-python/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

`pip 24.0` is the version Mint 22 puts in new environments; what matters is that it answers with a version and a path **inside `.venv`**, and not with `No module named pip`. If your first run of `python3 -m venv .venv` printed nothing, nothing in this section applies to you: your environment was already complete.

Let us see what it created. Look inside the folder with `ls .venv`:

```text
$ ls .venv
bin  include  lib  lib64  pyvenv.cfg
```

There are five entries, but four different things: `lib64` is not one more folder but a shortcut to `lib`, which `venv` creates on 64-bit Linux for programs that look for their libraries under that name. `bin` holds the environment's programs: its own `python`, its own `pip`, and the activation scripts. `lib` is where the packages you install will be stored. `include` holds support files this course does not use. And `pyvenv.cfg` is a small text file that points to the Python the environment was created with; the [module's documentation](https://docs.python.org/3/library/venv.html) explains that it carries a `home` key with that location. You can read it with `cat .venv/pyvenv.cfg`.

An important consequence: the environment's `python` is **a shortcut to the Python it was created with**, not an independent copy. That is why, if someday you change or upgrade the system's Python, the environment may end up broken and will have to be recreated. And for that very reason an environment **is neither moved nor copied** to another folder or another computer: the documentation says it in so many words (“not considered as movable or copyable”; it is recreated at the destination). Programs installed in an environment keep the absolute path of their interpreter on their first line; if the environment is moved, that path points to nothing. Recreating an environment takes ten seconds. Learning to do it without fear is the goal.

#### 1.2.3 Activating the environment

Creating the environment does not use it yet. For your terminal to use **its** Python instead of the system's, you have to **activate** it:

```text
$ source .venv/bin/activate
(.venv) $
```

`source` is a terminal command that runs a script “inside” the current terminal (instead of opening a new one). The `activate` script changes three things, **only in that terminal**: it adds a prefix to the prompt, `(.venv)`, which is your visual sign that you are inside; it adjusts the list of folders where the terminal looks for programs (the `PATH` variable), putting `.venv/bin` first; and it creates a variable, `VIRTUAL_ENV`, with the environment's path, so other programs know which one you are in (`echo $VIRTUAL_ENV` shows it). It also makes the `deactivate` command available, which undoes everything. It is the change in `PATH` that makes `python` come to mean “the environment's Python.” The [documentation](https://docs.python.org/3/tutorial/venv.html) sums it up: activating will “modify the environment so that running `python` will get you that particular version.”

Check it, which is what matters. With the environment active, ask which `python` it is:

```text
(.venv) $ which python
/home/tu_usuario/curso-python/.venv/bin/python
(.venv) $ python --version
Python 3.12.3
```

Notice two things. The first: now `python` (without the 3) **exists**, and it points **inside your environment**. Outside an environment, on your Mint the `python` command **does not exist**: only `python3` exists (`which python` prints nothing). If you type it and the terminal tells you it cannot find it or suggests `python3`, that is expected. The rule, for the whole course: **outside the environment, `python3`; inside the activated environment, `python`**. The second: the version is the same as before, because the environment was created with that Python. If you had created the environment with `python3.14`, `python --version` would say 3.14. **The environment decides the version; you chose it when you created it.**

That pair of commands, `which python` and `python --version`, is the safety routine of the whole course. Before suspecting your code, check which Python is running.

#### 1.2.4 Installing a package: now for real

With the environment active, the same command that was rejected before works:

```text
(.venv) $ python -m pip install httpx
Collecting httpx
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
...
Successfully installed anyio-4.15.1 certifi-2026.7.22 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 typing_extensions-4.16.0
```

(The intermediate lines are trimmed. The version numbers you will see are the current ones on the day you install, so they almost surely will not match these; what matters is the final `Successfully installed` line.)

What happened: `pip` downloaded `httpx` and also six other packages `httpx` needs in order to work. They are called **dependencies**: packages another one depends on. Everything landed **inside `.venv/lib`**, without touching the system's Python. Check it with:

```text
(.venv) $ python -m pip list
Package           Version
----------------- ---------
anyio             4.15.1
certifi           2026.7.22
h11               0.16.0
httpcore          1.0.9
httpx             0.28.1
idna              3.20
pip               24.0
typing_extensions 4.16.0
```

The list shows what is **in this environment**. If you now open another terminal (without activating anything) and ask for the list with `python3 -m pip list`, you will not see `httpx` (on your Mint, in fact, the answer will be `No module named pip`): what you install in an environment does not exist outside it. That is what the isolation looks like. A notice may also appear at the end of the installation saying something like `[notice] A new release of pip is available`: it is informational. Updating `pip` is not necessary for the course.

A note on `httpx`: no program of the course uses it before [Lesson 9](09-http-y-asyncio.md). We install it today **only to demonstrate `pip`**, with a real package that has dependencies, and so that you see what the difference looks like between installing inside the environment and outside.

#### 1.2.5 Deactivating, and the habit to acquire

```text
(.venv) $ deactivate
$ which python
```

`deactivate` restores the terminal's previous state: the `(.venv)` prefix disappears and `python` goes back to meaning what it meant (on Mint, as we saw, normally nothing). Closing the terminal has the same effect, and that is where the **habit to acquire** comes from: every time you open a new terminal to work on the course, you have to activate the environment again:

```text
$ cd ~/curso-python
$ source .venv/bin/activate
(.venv) $
```

Two lines, always the same, and the `(.venv)` prefix as confirmation. Almost all the “it doesn't work for me” cases at this stage are solved by checking whether the prefix is on screen.

There is another way to use an environment without activating it, and it is worth knowing it exists: calling the environment's Python by its full path, `~/curso-python/.venv/bin/python hola.py`. The [documentation](https://docs.python.org/3/library/venv.html) confirms it: it is not necessary to activate the environment, it is enough to give the path of its interpreter. Activating is a convenience (you type `python` instead of the long path), not a requirement.

### 1.3 The REPL and running a file

There are two ways to talk to Python, and they are used for different things.

#### 1.3.1 The REPL: a conversation

With the environment active, type just `python` and Enter. Python does not run a file; it opens a **conversation**: it shows you a `>>>` symbol and waits for an instruction. This is called a REPL (from *read-eval-print loop*: it reads what you type, evaluates it, prints the result, and goes back to waiting). Try it like this (you type what comes after `>>>`; the welcome line in the first rows changes with your version):

```text
(.venv) $ python
Python 3.12.3 (main, ...) [GCC ...] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 142 + 1
143
>>> "reportes"
'reportes'
>>> tiempo_ms = 142
>>> tiempo_ms
142
>>> print("142" + 1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can only concatenate str (not "int") to str
>>> exit()
(.venv) $
```

Go through the conversation. `142 + 1` returns `143`, with no need for `print`: the REPL prints for you the value of whatever you type. `"reportes"` comes back with single quotes, because that is how Python shows a text when it represents it. `tiempo_ms = 142` is an assignment and returns nothing; afterward, typing `tiempo_ms` returns `142`: **the REPL remembers** what you told it as long as you do not close it. The fourth is the error you already know from Lesson 0, `TypeError`, and notice it: the REPL **does not close** because of the error. It shows the report and goes back to waiting. That makes it ideal for making mistakes and learning. To exit you type `exit()` (or its twin `quit()`) or press `Ctrl + D`; the [documentation](https://docs.python.org/3/tutorial/interpreter.html) gives `Ctrl + D` as the main way and `quit()` as an alternative.

Two version details, so you are not thrown off if your screen looks different. The REPL of **3.13 onward** is renewed: it has color and multi-line editing, and the name it shows in an error report is `<python-input-0>` instead of `<stdin>`, along with the line that failed itself. And the 3.12 REPL, the one on your Mint, is the plain one above. Nothing the course does depends on that difference.

What is the REPL for? For **trying quick ideas**: “what does this operation do?”, “what was this function called?”. What is it **not** for? Writing programs. What you say in the REPL is lost when you exit; no file is left. A program is a text that is saved, corrected, and run again. That is what files are for.

#### 1.3.2 A file: your first script

A **script** is a text file with Python instructions that is run from start to finish. To create it you need a text editor. Mint ships one called **Xed** (it appears in the menu as “Editor de texto,” that is, “Text Editor”). It is worth configuring once: in its preferences turn on **insert spaces instead of tabs** and set the tab width to 4. Python gives great importance to the spaces at the start of lines ([Lesson 2](02-valores-texto-decisiones.md) explains why), and mixing tabs with spaces is a classic source of errors that we prefer to avoid from the first day. If you prefer the terminal, `nano hola.py` opens a simple editor: type, save with `Ctrl + O` and Enter, exit with `Ctrl + X`.

Create the file `~/curso-python/hola.py` with this content:

```python
# fig01_01.py
print("Hola, Python")
```

```text
$ cd ~/curso-python
$ python3 hola.py
Hola, Python
```

The name `fig01_01.py` on the first line is the figure's label within the course (in the course's repository the file is called that); **you save it as `hola.py`**, and that is why the command is `python3 hola.py`. The first line is a comment (it starts with `#`, Python ignores it) and you can omit it. The second is the program. `print` is a **function** that Python already ships: it shows on screen what goes between the parentheses. What goes between quotes is a **text**, as you saw in the previous lesson. That is all the explanation you need today; Lesson 2 goes deeper.

Run it twice: once **without** the environment active and once **with** it. Outside the environment the command is `python3 hola.py`. Inside it is `python hola.py`, because inside the environment `python` exists and points to its Python. In both cases, the output is `Hola, Python`; what changes, without your noticing, is **which Python ran it**. That difference is invisible while everything works and decisive when something fails, and that is why there is an exercise at the end to note it down.

With that comes the second file of today, the first one of the project. Create the `revisor` folder and the file where it will grow:

```text
$ mkdir ~/curso-python/revisor
```

```python
# fig01_02.py
print("revisor: todavía no revisa nada")
```

It is saved as `~/curso-python/revisor/revisor.py` (the label `fig01_02.py` is, again, just the figure's name). To run it, first go into its folder, because `python3 revisor.py` looks for the file in the folder you are in:

```text
$ cd ~/curso-python/revisor
$ python3 revisor.py
revisor: todavía no revisa nada
```

It is a one-line program, on purpose: what matters is that **the file exists, runs, and is the starting point**. From Lesson 2 on it grows until it is the complete program. The word “todavía” (“not yet”) is a promise.

### 1.4 The first *traceback*

In Lesson 0 you saw an error report and read its last line. Today you read it whole, with an error you are going to make early on and many times: misspelling the name of something. This program has a deliberate typo. This time save it under the figure's name, `~/curso-python/fig01_03.py`, so that the report on your screen matches the one below:

```python
# fig01_03.py
pirnt("hola")
```

```text
$ cd ~/curso-python
$ python3 fig01_03.py
Traceback (most recent call last):
  File "fig01_03.py", line 2, in <module>
    pirnt("hola")
    ^^^^^
NameError: name 'pirnt' is not defined. Did you mean: 'print'?
```

(On your screen, the file's path will be the full path; here it is shortened to the name.)

**The rule for reading a Python error report: from the last line upward.** Three questions are answered, in this order.

**What kind of error is it?** Look at the beginning of the last line: `NameError`. A `NameError` happens when you use a name that Python does not know. Lesson 0 explained that a name is a label that points to a value; Python has some names built in (like `print`) and others that you create with an assignment. `pirnt` is neither.

**What exactly does it say?** The rest of the last line: `name 'pirnt' is not defined`, “the name `pirnt` is not defined.” And the help: `Did you mean: 'print'?`. Python compared the unknown name with the ones it does know, found one very similar, and suggests it to you. That suggestion, which for this kind of error is identical in versions 3.12 and 3.14, solves most of a beginner's stumbles.

**Where did it happen?** The lines above. `File "fig01_03.py", line 2, in <module>` gives the file and the line (the 2nd, because the 1st is the comment). Below, Python repeats the text of that line of your code, and the carets `^^^^^` point at the exact word: five characters, precisely `pirnt`.

Do what the suggestion says: change `pirnt` to `print`, save, and run again. With that small ceremony (read, understand, fix, repeat) you will work for the rest of the course. An error does not mean you did it wrong; it means Python is answering you with precision.

## The error you will see

Today there are three messages worth knowing how to read: you have seen two already and the third is a warning for later.

**`NameError`** is the one from the previous section. Variants you will see: a capital letter where it does not belong (`Print("hola")` gives `NameError: name 'Print' is not defined. Did you mean: 'print'?`, because Python distinguishes between uppercase and lowercase), one letter too many, a name you forgot to define. In all cases it reads the same.

**`No module named pip`** is your Mint's answer in 1.1.2, and its relative, the `ensurepip` message in 1.2.2, is that of an environment missing the same piece. Both say in so many words what is missing, and both are resolved without touching the system's Python: the first, by working inside the environment; the second, by installing `python3.12-venv` and creating the environment again over the half-built folder.

**`externally-managed-environment`** is the warning from 1.1.3: you will not see it on a freshly installed Mint, but you will the day you install the system's `pip`, or on another distribution. The first line, `error: externally-managed-environment`, is put there by `pip`: PEP 668 does not fix that text, it only requires the installer to refuse with an error and show the message the distribution wrote in its marker file (or, if there is none, one of its own suggesting a virtual environment). The body, therefore, is written by each system. As a real example, this is the complete message given by Homebrew's Python on a macOS (the package manager there is called `brew`; on Mint it would be `apt`):

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.

    If you wish to install a Python library that isn't in Homebrew,
    use a virtual environment:

    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz

    If you wish to install a Python application that isn't in Homebrew,
    it may be easiest to use 'pipx install xyz', which will manage a
    virtual environment for you. You can install pipx with

    brew install pipx

    You may restore the old behavior of pip by passing
    the '--break-system-packages' flag to pip, or by adding
    'break-system-packages = true' to your pip.conf file. The latter
    will permanently disable this error.

    If you disable this error, we STRONGLY recommend that you additionally
    pass the '--user' flag to pip, or set 'user = true' in your pip.conf
    file. Failure to do this can result in a broken Homebrew installation.

    Read more about this behavior here: <https://peps.python.org/pep-0668/>

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

Read it the way you read a *traceback*, without fear, in parts. The first line is the **class**: `externally-managed-environment`, “externally managed environment.” The second, `This environment is externally managed`, gives the reason: this Python belongs to another manager. The third opens the list of ways out. **First**, install the package with the system's manager (here `brew`; on Mint it would be `apt`), as long as the package exists there. **Second**, if the package is not in the manager, create a virtual environment and use `python3 -m pip` inside it: the three lines it shows are exactly `venv`, `source ... activate`, and `pip install`, which you have just used. **Third**, if what you want is an *application* (not a library to use in your code), `pipx`, which creates an isolated environment for each application. The `revisor` will end up being installed that way, in [Lesson 11](11-el-programa-terminado.md).

Below the three ways out come two more paragraphs written by Homebrew: how to “restore the old behavior of pip” with `--break-system-packages` and the warning, in capital letters, that doing so can break the installation. And the last two lines are no longer from the distribution but from `pip`: a `note:` that mentions `--break-system-packages` again “at the risk of breaking your Python installation or OS,” and a `hint:` that points to PEP 668. That the option appears twice does not make it advisable: it appears so that you know it exists and what it costs, which is what the next section says.

The body is a resolution guide written by whoever administers that Python, and it changes from one system to another; what does not change, because `pip` puts it and not the distribution, is the first line and the final note. **Read it every time it appears**: it saves you searching the internet, and most of the answers on the internet for this error recommend the shortcut that breaks the protection.

## What gets done wrong

- **Using `sudo pip install`.** It installs into the system's Python with administrator permissions. It is the fastest way to overwrite a library Mint needs and find out weeks later. Every package goes inside a virtual environment.
- **Using `--break-system-packages` to make it “just work.”** It turns off exactly the protection that helps you. The course neither teaches nor uses it. If you see it in an answer on the internet, ignore it.
- **Installing without seeing the `(.venv)` prefix.** If you opened a new terminal and forgot to activate, the installation is rejected (because you are outside the environment) or, on a system without protection, happens in the wrong place. The routine is to look at the prefix before installing and check with `which python` when in doubt.
- **Moving or copying the `.venv` folder.** An environment keeps absolute paths and does not survive a change of folder. It is deleted and recreated with `python3 -m venv .venv`; the packages are installed again. It is disposable by design.
- **Putting the project's code inside the environment.** The environment holds Python and the packages; your code lives next to it, in `revisor/`. That way deleting the environment does not cost you a single line of your own.
- **Mixing tabs and spaces in the editor.** Python uses the spaces at the start of the line to structure the program, and mixing the two kinds gives errors that are hard to see. Set your editor to 4 spaces, today, before writing real code.
- **Typing the `python` command outside the environment and concluding that “Python is not installed.”** What is missing is the `python` alias: outside the environment you type `python3`. That `python` does not exist on a freshly installed Mint is normal.
- **Staying hours with an error without reading it.** A Python report almost always says what and where. The habit of starting at the last line solves most of them.

## Exercises

### Exercise 1 — Your environment, measured

In a terminal with no environment active, run: `python3 --version` and `which python3`. Then activate the environment and run `python --version`, `which python`, and `python -m pip --version`. Write in your [logbook](bitacora.md) the five outputs and a sentence that answers: what changed between `which python3` outside and `which python` inside, and why?

### Exercise 2 — Provoke the refusal and read it

Deactivate the environment (`deactivate`) and run `python3 -m pip install httpx`. Note in the logbook the exact response and explain in your own words who is speaking (what comes before the colon) and what it says. Then read the `externally-managed-environment` example in the section “The error you will see” and write what each of its first three parts says (the class, the reason, the list of ways out). Finally, activate the environment and repeat the installation. Describe what changed and what you checked with `python -m pip list`.

### Exercise 3 — The `revisor` inside and outside the environment

Create `~/curso-python/revisor/revisor.py` with the line from figure 2 and go into its folder (`cd ~/curso-python/revisor`). Run it **without** the environment (with `python3 revisor.py`) and **with** it (with `python revisor.py`). Before each run, execute `which python3` or `which python` as appropriate, and note in the logbook which Python was used each time. Did the result come out different?

### Exercise 4 — Provoke a new error and read it

Without touching the environment, create a file with the line `Print("hola")` (with a capital P). Before running it, predict the last line of the report. Run it and compare. Then provoke a second, different error: create a two-line file, `print("primera")` and `print("hola)` (the second without the closing quote), and look at what kind of error appears. Does `primera` manage to be shown?

## Solutions

### Solution 1

A typical output is `Python 3.12.x`, `/usr/bin/python3`, `Python 3.12.x`, `/home/tu_usuario/curso-python/.venv/bin/python`, and a `pip` with the path `.venv/lib/python3.12/site-packages/pip`. What changed between outside and inside is **the path**: outside it is `/usr/bin/python3`, the system's Python; inside it is the one in `.venv/bin/`, the environment's. It changed because `activate` put `.venv/bin` at the start of the list of places where the terminal looks for programs; that is why `python` (which did not even exist outside) comes to mean “the environment's.” The version is the same because the environment was created with the system's `python3`.

### Solution 2

Outside the environment, your Mint answers `/usr/bin/python3: No module named pip`: the system's Python is speaking and it says it has no `pip`, so nothing gets installed there. In the `externally-managed-environment` example, the class is `externally-managed-environment`: the type of problem. The reason is that that Python is administered by another package manager, and `pip` respects the `EXTERNALLY-MANAGED` mark left by whoever installed it. The list of ways out is: install with the system's manager if the package exists there, create a virtual environment for libraries, or `pipx` for applications. When you activate the environment and repeat, the installation completes: inside the environment there is a `pip`, and its protection does not apply because there it is not touching the system's Python. `python -m pip list` shows `httpx` and its dependencies in the environment's list, and not in the system's.

### Solution 3

It must print `revisor: todavía no revisa nada` (“revisor: not checking anything yet”) in both cases. What changes is the Python: without the environment, `which python3` gives `/usr/bin/python3`; with the environment, `which python` gives the path inside `.venv/bin/`. The result does not change because the program only uses `print`, which does not depend on any package; the difference will become visible when a program imports something installed in the environment (from Lesson 9): that program would work only with the environment active. Knowing which Python you used is what lets you understand why.

### Solution 4

With `Print("hola")` the last line is `NameError: name 'Print' is not defined. Did you mean: 'print'?`: Python distinguishes uppercase from lowercase. With `print("hola)` the error changes class: a `SyntaxError: unterminated string literal (detected at line 2)` appears, which means “unfinished text,” because the quote that closes it is missing. `primera` is **not** shown: the error happens before anything is run. It is an error of form, and Python detects it in the step where it reads and translates the file (the first of the four steps in Lesson 0). It is not a `NameError`, which is only discovered upon reaching that line with the program already running. Lesson 2 studies this error in depth.

## How I know I got it

- [ ] `python3 --version` shows a version that starts with `Python 3.` and you noted it in the logbook.
- [ ] `python3 -m pip install httpx`, with the environment **deactivated**, ends with `No module named pip`, you can explain without looking at the lesson what it means and what the correct way out is, and you would recognize the `externally-managed-environment` warning if you ever see it.
- [ ] The folder `~/curso-python/.venv` exists; with the environment active, the terminal prompt starts with `(.venv)`, and `which python` shows a path that ends in `.venv/bin/python`.
- [ ] With the environment active, `python -m pip list` shows `httpx`; with the environment deactivated, `python3 -m pip list` answers `No module named pip`: outside the environment there is no `pip`, and therefore no `httpx` either.
- [ ] `python3 hola.py` outside the environment and `python hola.py` inside show `Hola, Python`.
- [ ] `~/curso-python/revisor/revisor.py` exists and, when run, shows `revisor: todavía no revisa nada`.
- [ ] You can read, without asking for help, the `NameError` report of figure 3: you say which word failed, on which line, and what suggestion Python gave.
- [ ] You can say, without looking, why the environment is neither moved nor copied, and why it is never installed with `sudo pip`.

## Summary

Answer without looking at the lesson:

1. Which Python comes with your Mint, whose is it, and how do you check where it runs from?
2. What does `externally-managed-environment` say, who puts it there, and what are the three ways out it suggests? Which one does the course use?
3. What three things does `source .venv/bin/activate` change in your terminal, and how do you know you are inside?
4. Why does the environment live outside the `revisor/` folder and why is it neither moved nor copied?
5. What is the difference between the REPL and a file? When do you use each?
6. In what order is a Python error report read, and what three questions does it answer?
7. Which Python does `python` use inside the environment and which Python does `python3` use outside?

## Further reading

- [Python tutorial: Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html) — the official guide to `venv` and `pip`, with the commands from this lesson. Accessed on October 7, 2026.
- [PEP 668, “Marking Python base environments as externally managed”](https://peps.python.org/pep-0668/) — the specification that explains the `EXTERNALLY-MANAGED` file and `pip`'s refusal. Accessed on October 7, 2026.
- [Documentation of the `venv` module](https://docs.python.org/3/library/venv.html) — what `pyvenv.cfg` is, why an environment is disposable, and why it is not moved. Accessed on October 7, 2026.
- [pip: getting started](https://pip.pypa.io/en/stable/getting-started/) — checking that `pip` is installed, installing a package, and why it is invoked as `python -m pip`. Accessed on October 7, 2026.
