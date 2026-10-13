# Lección 1 — Instalar Python en tu Linux Mint

**Tiempo:** 90 min

**Qué construyes:** el entorno virtual del curso, tu primer guion (`hola.py`) y el archivo donde vivirá el `revisor`

**Qué aprendes:** el `python3` del sistema y por qué no instala paquetes (`No module named pip` y el aviso `externally-managed-environment`); crear, activar y desactivar un entorno virtual (`venv`); `pip` dentro del entorno; el REPL y ejecutar un archivo; leer el primer *traceback*

**De dónde vienes.** De la [Lección 0](00-que-es-python.md), que fue de lectura: ya sabes que Python lee tu archivo, lo traduce a *bytecode* y lo ejecuta; que los tipos se revisan al correr y no antes; que el GIL no te va a estorbar; y que existe algo llamado entorno virtual que protege al Python de tu sistema. Hoy dejas de leer y pasas a la terminal. Trabajas en una computadora con **Linux Mint 22.x** (cualquiera de sus versiones, de la 22 a la 22.3, que comparten la misma base) y con una terminal abierta. Casi nada de lo que harás requiere permisos de administrador: a lo sumo una línea (con dos órdenes de administrador dentro), y solo si tu Mint no trae la pieza que crea entornos virtuales (lo verás en 1.2.2). Es más, una de las cosas que aprenderás hoy es a **no** instalar paquetes de Python con esos permisos.

**Qué no hace esta lección.** No enseña todavía el lenguaje: el `print` que vas a usar se explica en una línea y la [Lección 2](02-valores-texto-decisiones.md) lo estudia a fondo. Tampoco instala `uv` ni `pipx`, otras herramientas que verás más adelante: hoy se usa lo que ya trae el sistema, porque entender el entorno con las piezas básicas es lo que luego te permite entender por qué las demás herramientas existen.

## Al terminar vas a poder

- Comprobar qué Python trae tu Mint (`python3 --version`) y desde dónde corre (`which python3`).
- Intentar a propósito instalar un paquete en el Python del sistema, leer la respuesta y explicar por qué Mint protege su Python, cómo se ve el aviso `externally-managed-environment` en los sistemas que sí traen `pip`, y cuál es la salida correcta.
- Crear el entorno virtual del curso con `python3 -m venv`, activarlo, comprobar con `which python` que estás dentro, instalar un paquete con `pip` y desactivarlo.
- Escribir una expresión en el REPL, salir de él y distinguir cuándo conviene el REPL y cuándo un archivo.
- Crear y ejecutar `hola.py` y `revisor/revisor.py`, dentro y fuera del entorno, y anotar qué `python` se usó en cada caso.
- Leer un *traceback* de `NameError` de la última línea hacia arriba y decir qué palabra mal escrita lo causó.

## El porqué antes del cómo

Para dar el primer paso con el `revisor` hace falta una base firme: un Python que funcione, un lugar donde guardar los paquetes que el curso va a necesitar y una carpeta donde vivirá el proyecto. Si esa base se improvisa, los problemas aparecen más tarde y con la forma más confusa posible: un paquete que «se instaló» pero no se encuentra, una versión de Python que no es la que creías, un comando que funcionaba ayer y hoy no. Esta lección existe para que eso no te pase.

Piensa en armar un taller antes de construir un mueble. No es la parte emocionante, pero decide si el resto sale limpio. En el taller de Python hay tres cosas que preparar. La **primera** es saber qué Python tienes y de quién es: tu Mint ya trae uno, y es de él, no tuyo. La **segunda** es crear tu propio espacio de trabajo, el entorno virtual, donde puedas instalar y romper cosas sin consecuencias. La **tercera** es comprobar que todo funciona ejecutando el programa más pequeño posible.

Hay una razón más para hacerlo bien ahora, y es que **el tropiezo que vas a ver hoy es el mismo que tendrás en un trabajo real**. Casi todo el que instala Python en Linux moderno se topa, tarde o temprano, con un Python del sistema que se niega a instalar paquetes: en tu Mint, porque ni siquiera trae `pip`; en otros sistemas, con un mensaje que dice `externally-managed-environment`. Mucha gente lo lee como un obstáculo, busca en internet cómo saltárselo y termina usando una opción que rompe la protección del sistema. Este curso hace lo contrario: **provoca el rechazo a propósito**, lo lee línea por línea y muestra que es una ayuda, no un muro. Quien lo entiende una vez lo resuelve en diez segundos el resto de su vida.

### Lo mínimo de la terminal que necesitas hoy

La terminal es una ventana donde escribes órdenes en vez de hacer clic. Se abre en Mint con el atajo `Ctrl + Alt + T`, o buscando «Terminal» en el menú. En este curso, las líneas que empiezan con `$` son lo que **tú escribes**, y las demás son lo que la computadora contesta. El `$` mismo no se escribe: es el símbolo que la terminal te muestra para indicar que está esperando una orden. Los comandos de hoy son pocos:

- `pwd` (*print working directory*): muestra en qué carpeta estás.
- `ls`: lista lo que hay en la carpeta actual.
- `cd carpeta`: te mueve a esa carpeta. `cd ..` sube un nivel y `cd` sin nada te lleva a tu carpeta personal.
- `mkdir carpeta`: crea una carpeta.
- `which nombre`: muestra **cuál archivo** se ejecutaría si escribieras ese nombre. Es la herramienta que contesta «¿qué Python estoy usando?».
- `~`: es un atajo para tu carpeta personal, la que contiene tus documentos. `~/curso-python` quiere decir «la carpeta `curso-python` dentro de tu carpeta personal».

Si alguno de estos te es nuevo, pruébalo ahora en tu terminal antes de seguir: escribe `pwd`, presiona Enter, y compara con lo que dice. No rompe nada.

## Los conceptos

Son cuatro: el Python del sistema y el error que protege; el entorno virtual con `pip`; el REPL y los archivos; y el primer *traceback*. Cada uno termina con algo que puedes comprobar en tu pantalla.

### 1.1 El `python3` del sistema y el error `externally-managed-environment`

#### 1.1.1 Qué Python tienes

Abre una terminal y escribe:

```text
$ python3 --version
Python 3.12.3
```

La salida que verás es de la forma `Python 3.12.x`: el último número (el parche) depende de las actualizaciones que tu Mint haya recibido. Lo que importa es el `3.12`. Esa es la versión con la que trabaja el curso, y como viste en la lección anterior, todo el código corre también en la 3.14. Si tu terminal dice otra cosa (una 3.10 o una 3.11), el curso casi seguro funcionará igual, pero la 3.10 llegó a su fin de vida el 1 de octubre de 2026; anótalo en la [bitácora](bitacora.md) y sigue.

Ahora pregunta **de dónde sale** ese Python:

```text
$ which python3
/usr/bin/python3
```

`/usr/bin/` es la carpeta donde el sistema guarda sus propios programas. Que tu `python3` esté ahí significa que **es el de Mint**: lo instaló la distribución, lo actualiza el gestor de paquetes (`apt`) y varias herramientas del sistema dependen de él. Es la «despensa de la casa» de la lección anterior.

Si estás en otro sistema (un macOS, o un Linux con Python instalado de otra manera), `which` mostrará otra ruta. No pasa nada, pero el error de la próxima sección puede ser distinto o no aparecer, y este curso está escrito para Mint.

#### 1.1.2 Intentar instalar algo, y que el sistema diga que no

`pip` es la herramienta de Python para instalar **paquetes**: bibliotecas de código que otras personas escribieron y publicaron en un catálogo público llamado **PyPI**, para que no tengas que escribirlas tú. El curso necesitará más adelante un paquete llamado `httpx`, que sirve para consultar servicios por red. Vamos a intentar instalarlo, **a propósito, de la forma equivocada**: con el Python del sistema, fuera de cualquier entorno. En una Linux Mint 22 recién instalada, esto es lo que pasa:

```text
$ python3 -m pip install httpx
/usr/bin/python3: No module named pip
```

La orden se lee: «ejecuta el módulo `pip` con Python (`-m` quiere decir *módulo*) y pídele que instale `httpx`». Se escribe `python3 -m pip` y no solo `pip` por una razón que explica la [documentación de pip](https://pip.pypa.io/en/stable/getting-started/): así te aseguras de que el `pip` que se ejecuta es el **de ese Python**, y no otro que haya en tu sistema.

La respuesta se lee como cualquier informe de error, por el final: `No module named pip`, «no hay ningún módulo llamado `pip`». Antes de los dos puntos viene quién habla: `/usr/bin/python3`, el Python del sistema. No es un fallo tuyo ni del curso. En la familia Debian y Ubuntu, de la que viene Mint, `pip` es un paquete aparte del sistema (`python3-pip`), y una Mint recién instalada no lo trae. Ese Python lo administra el gestor de paquetes del sistema, no tú. El resultado práctico es el que importa: **fuera de un entorno no se instala nada**. Dentro del entorno virtual, que crearás en un momento, `pip` viene incluido.

#### 1.1.3 El aviso que verás si un día instalas el `pip` del sistema

Hay una segunda protección, más explícita, y conviene que la reconozcas porque es la que encontrarás en casi cualquier Linux moderno donde sí haya `pip` en el sistema (por ejemplo, si un día instalas el paquete `python3-pip` de Mint, o en otra distribución). **No la provoques**: no hace falta instalar nada para entenderla. Ahí, la misma orden no dice `No module named pip`, sino un mensaje que empieza así:

```text
error: externally-managed-environment
```

Esto es lo que dice la especificación que lo causa, [PEP 668](https://peps.python.org/pep-0668/): las herramientas de Python «no deberían instalar ni quitar paquetes en el contexto global del intérprete, por omisión», cuando ese intérprete lo administra otro gestor de paquetes. El mecanismo es simple: la distribución deja un archivo llamado `EXTERNALLY-MANAGED` en la carpeta de la biblioteca estándar de su Python, y `pip` lo busca antes de instalar. Si lo encuentra, se detiene. Esa carpeta se puede preguntar a Python:

```text
$ python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))"
```

Imprime la ruta de la biblioteca estándar de tu Python, una carpeta cuyo nombre termina en `python3.12`; la especificación dice que ahí es donde va el archivo marcador.

Esa orden es una receta para copiar tal cual; no necesitas entenderla entera hoy, pero sí saber qué hace cada pedazo. `-c` significa «ejecuta este texto como programa»: es una forma rápida de hacer una pregunta suelta a Python sin crear un archivo. El texto entre comillas son **dos instrucciones**, separadas por el punto y coma `;`, que en Python permite escribir dos instrucciones en el mismo renglón (en los archivos del curso no se usa: cada instrucción va en su línea). La primera, `import sysconfig`, trae un **módulo**, un conjunto de herramientas que viene con Python y que no está disponible hasta que lo pides; la [Lección 3](03-bucles-funciones-modulos.md) explica `import` a fondo. La segunda, `print(sysconfig.get_path('stdlib'))`, le pide a ese módulo la ruta (*path*) de la biblioteca estándar (*stdlib*) y la muestra con `print`.

El mensaje completo, además, **te dice qué hacer**, y por eso es una lección y no un muro. La especificación permite que la distribución ponga su propio texto de ayuda dentro del archivo marcador, así que el cuerpo cambia de un sistema a otro; lo habitual es que sugiera tres salidas: instalar el paquete con el gestor del sistema si existe versión empaquetada, crear un entorno virtual si no, o usar `pipx` si lo que quieres instalar es una aplicación y no una biblioteca. Para lo que hace el curso, la salida es la segunda: **un entorno virtual**. En la sección «El error que vas a ver» tienes un ejemplo completo, leído por partes.

Hay además una cuarta salida, y `pip` te la dice él mismo en la nota con la que cierra el mensaje: una opción llamada `--break-system-packages`, que desactiva la protección y deja instalar de todos modos. La especificación admite que debe existir, y existe. **Este curso no la enseña ni la usa.** Es el equivalente a quitar la cerradura porque no encontraste la llave: funciona hasta que un paquete que instalaste pisa una biblioteca que el sistema necesitaba, y entonces fallan herramientas que no tienen nada que ver con tu proyecto. La llave existe y se llama entorno virtual.

### 1.2 El entorno virtual: crear, activar, usar `pip`, desactivar

#### 1.2.1 Crear el entorno

Primero la carpeta del curso. Todo lo que hagas vivirá dentro de `~/curso-python/`:

```text
$ mkdir ~/curso-python
$ cd ~/curso-python
$ python3 -m venv .venv
```

La tercera línea es la que crea el entorno. Se lee: «ejecuta el módulo `venv` con `python3` y crea un entorno en una carpeta llamada `.venv`». El punto al principio del nombre hace que la carpeta sea «oculta» por convención: no aparece en un `ls` normal. Es el nombre habitual de los entornos y algunas herramientas lo reconocen solas. Cuando todo sale bien, **no imprime nada**; en la terminal, el silencio es éxito.

El entorno vive en `~/curso-python/.venv`, **no** dentro de la carpeta del proyecto `revisor/` que crearás más abajo. Hay una razón: la documentación del módulo [`venv`](https://docs.python.org/3/library/venv.html) dice que un entorno se considera «desechable» (debe ser sencillo borrarlo y recrearlo desde cero) y que «no se coloca código de proyecto dentro del entorno». Mantenerlo aparte del código es la forma más limpia de cumplirlo.

#### 1.2.2 Si tu Mint no trae la pieza de los entornos

En una Mint 22 recién instalada, lo más probable es que la tercera línea **no** salga en silencio, sino con este mensaje:

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

Léelo por partes. La primera frase dice qué pasó: el entorno «no se creó con éxito» porque falta `ensurepip`, la pieza que pone `pip` dentro de cada entorno nuevo. La segunda dice por qué: en los sistemas de la familia Debian y Ubuntu, de la que viene Mint, esa pieza llega en un paquete aparte. La tercera te da la orden exacta, `apt install python3.12-venv`, y la siguiente te avisa de dos cosas: que quizá necesites `sudo` y que, después de instalar, hay que **recrear** el entorno. La última línea, `Failing command`, dice qué orden interna falló; no tienes que hacer nada con ella.

Fíjate en la palabra «recrear», porque esconde una trampa. Aunque el mensaje dice que el entorno no se creó, **la carpeta `.venv` sí quedó en el disco**, a medias: tiene `pyvenv.cfg`, las carpetas `lib` e `include` y, dentro de `bin`, solo los accesos directos a Python (`python`, `python3` y `python3.12`). Le faltan dos cosas: `pip` y el guion `activate`. Por eso todavía no se puede usar: `source .venv/bin/activate` contestaría `No such file or directory` («no existe ese archivo»), un mensaje que no menciona el entorno y que desconcierta si no sabes lo que pasó.

La salida son dos órdenes:

```text
$ sudo apt update && sudo apt install python3.12-venv
$ python3 -m venv .venv
```

- **`sudo apt update && sudo apt install python3.12-venv`.** `apt` es el gestor de paquetes del sistema, el que instala y actualiza los programas de Mint. `sudo` significa «ejecuta esta orden con permisos de administrador»: instalar algo para todo el sistema los necesita, así que la terminal te pedirá **tu contraseña** (mientras la escribes no aparece nada en pantalla, ni asteriscos; es normal). La línea son en realidad dos órdenes unidas por `&&`, que quiere decir «y, si la primera salió bien, la segunda». La primera, `apt update`, no instala nada: descarga la lista al día de los paquetes disponibles, para que la segunda encuentre la versión vigente (con una lista vieja, `apt` puede no encontrar el paquete o elegir una versión que ya no existe). La segunda instala `python3.12-venv`; `apt` te avisará que instala **tres** paquetes (`python3.12-venv` y dos de los que depende: `python3-pip-whl`, que trae el `pip` que irá en cada entorno, y `python3-setuptools-whl`, otra herramienta de empaquetado que el curso no usa) y te preguntará si continúas: contesta `s` (o `y`, si tu Mint está en inglés) y Enter. Aquí no instalas un paquete de Python con `pip`, sino un programa del sistema que completa el Python del sistema, y por eso sí es asunto de `apt`. Fuera de esta línea, el curso solo vuelve a usar `sudo` en la [Lección 11](11-el-programa-terminado.md), para instalar `pipx`, y es del mismo tipo.
- **`python3 -m venv .venv`**, otra vez, sobre la misma carpeta. Ahora sí debe salir en silencio. No hace falta borrar la carpeta a medias: `venv` la reutiliza y completa lo que faltaba, el guion `activate` y `pip`.

Comprueba que esta vez el entorno trae su `pip`, llamándolo por su ruta (todavía sin activar nada):

```text
$ .venv/bin/python -m pip --version
pip 24.0 from /home/tu_usuario/curso-python/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

`pip 24.0` es la versión que Mint 22 pone en los entornos nuevos; lo que importa es que conteste con una versión y una ruta **dentro de `.venv`**, y no con `No module named pip`. Si tu primera ejecución de `python3 -m venv .venv` no imprimió nada, nada de esta sección te toca: tu entorno ya estaba completo.

Veamos qué creó. Mira dentro de la carpeta con `ls .venv`:

```text
$ ls .venv
bin  include  lib  lib64  pyvenv.cfg
```

Hay cinco entradas, pero cuatro cosas distintas: `lib64` no es una carpeta más sino un acceso directo a `lib`, que `venv` crea en los Linux de 64 bits para los programas que buscan sus bibliotecas con ese nombre. `bin` contiene los programas del entorno: su propio `python`, su propio `pip`, y los guiones de activación. `lib` es donde se guardarán los paquetes que instales. `include` guarda archivos de apoyo que este curso no usa. Y `pyvenv.cfg` es un archivo de texto pequeño que apunta al Python con el que se creó el entorno; la [documentación del módulo](https://docs.python.org/3/library/venv.html) explica que lleva una clave `home` con esa ubicación. Puedes leerlo con `cat .venv/pyvenv.cfg`.

Una consecuencia importante: el `python` del entorno es **un acceso directo al Python con el que se creó**, no una copia independiente. Por eso, si algún día cambias o actualizas el Python del sistema, el entorno puede quedar roto y habrá que recrearlo. Y por eso mismo **no se mueve ni se copia** un entorno a otra carpeta o a otra computadora: la documentación lo dice con todas sus letras («no se considera movible ni copiable»; se recrea en el destino). Los programas instalados en un entorno guardan en su primera línea la ruta absoluta de su intérprete; si el entorno se mueve, esa ruta ya no apunta a nada. Recrear un entorno cuesta diez segundos. Aprender a hacerlo sin miedo es el objetivo.

#### 1.2.3 Activar el entorno

Crear el entorno no lo usa todavía. Para que tu terminal use **su** Python en vez del del sistema, hay que **activarlo**:

```text
$ source .venv/bin/activate
(.venv) $
```

`source` es una orden de la terminal que ejecuta un guion «dentro» de la terminal actual (en lugar de abrir una nueva). El guion `activate` cambia tres cosas, **solo en esa terminal**: añade un prefijo al símbolo del sistema, `(.venv)`, que es tu señal visual de que estás dentro; ajusta la lista de carpetas donde la terminal busca los programas (la variable `PATH`), poniendo primero `.venv/bin`; y crea una variable, `VIRTUAL_ENV`, con la ruta del entorno, para que otros programas sepan en cuál estás (`echo $VIRTUAL_ENV` la muestra). Además deja disponible la orden `deactivate`, que deshace todo. Es el cambio de `PATH` el que hace que `python` pase a significar «el Python del entorno». La [documentación](https://docs.python.org/3/tutorial/venv.html) lo resume: activar «modifica el entorno para que ejecutar `python` use esa versión particular».

Compruébalo, que es lo que importa. Con el entorno activo, pregunta cuál es el `python`:

```text
(.venv) $ which python
/home/tu_usuario/curso-python/.venv/bin/python
(.venv) $ python --version
Python 3.12.3
```

Fíjate en dos cosas. La primera: ahora `python` (sin el 3) **existe**, y apunta **dentro de tu entorno**. Fuera de un entorno, en tu Mint el comando `python` **no existe**: solo existe `python3` (`which python` no imprime nada). Si lo escribes y la terminal te dice que no lo encuentra o te sugiere `python3`, es lo esperado. La regla, para todo el curso: **fuera del entorno, `python3`; dentro del entorno activado, `python`**. La segunda: la versión es la misma de antes, porque el entorno se creó con ese Python. Si creaste el entorno con `python3.14`, `python --version` diría 3.14. **El entorno decide la versión; tú la elegiste al crearlo.**

Esa pareja de comandos, `which python` y `python --version`, es la rutina de seguridad de todo el curso. Antes de sospechar de tu código, comprueba cuál Python está corriendo.

#### 1.2.4 Instalar un paquete: ahora sí

Con el entorno activo, la misma orden que antes fue rechazada funciona:

```text
(.venv) $ python -m pip install httpx
Collecting httpx
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
...
Successfully installed anyio-4.15.1 certifi-2026.7.22 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 typing_extensions-4.16.0
```

(Se recortan las líneas intermedias. Los números de versión que verás son los vigentes el día que lo instales, así que casi seguro no coinciden con estos; lo que importa es la línea final `Successfully installed`.)

Qué pasó: `pip` descargó `httpx` y también otros seis paquetes que `httpx` necesita para funcionar. Se llaman **dependencias**: paquetes de los que depende otro. Todo cayó **dentro de `.venv/lib`**, sin tocar el Python del sistema. Compruébalo con:

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

La lista muestra lo que hay **en este entorno**. Si ahora abres otra terminal (sin activar nada) y pides la lista con `python3 -m pip list`, no verás `httpx` (en tu Mint, de hecho, la respuesta será `No module named pip`): lo que instalas en un entorno no existe fuera de él. Así se ve el aislamiento. También puede aparecer un aviso al final de la instalación que dice algo como `[notice] A new release of pip is available`: es informativo. Actualizar `pip` no es necesario para el curso.

Una nota sobre `httpx`: ningún programa del curso lo usa antes de la [Lección 9](09-http-y-asyncio.md). Lo instalamos hoy **solo para demostrar `pip`**, con un paquete real que tiene dependencias, y para que veas cómo se ve la diferencia entre instalar dentro del entorno y fuera.

#### 1.2.5 Desactivar, y la costumbre que hay que adquirir

```text
(.venv) $ deactivate
$ which python
```

`deactivate` restaura el estado anterior de la terminal: el prefijo `(.venv)` desaparece y `python` vuelve a significar lo que significaba (en Mint, como vimos, normalmente nada). Cerrar la terminal tiene el mismo efecto, y por eso aparece la **costumbre que hay que adquirir**: cada vez que abras una terminal nueva para trabajar en el curso, hay que volver a activar el entorno:

```text
$ cd ~/curso-python
$ source .venv/bin/activate
(.venv) $
```

Dos líneas, siempre las mismas, y el prefijo `(.venv)` como confirmación. Casi todos los «no me funciona» de esta etapa se resuelven al mirar si el prefijo está en pantalla.

Hay otra forma de usar un entorno sin activarlo, y conviene saber que existe: llamar al Python del entorno por su ruta completa, `~/curso-python/.venv/bin/python hola.py`. La [documentación](https://docs.python.org/3/library/venv.html) lo confirma: no es necesario activar el entorno, basta con indicar la ruta de su intérprete. Activar es una comodidad (se escribe `python` en lugar de la ruta larga), no un requisito.

### 1.3 El REPL y ejecutar un archivo

Hay dos maneras de hablar con Python, y se usan para cosas distintas.

#### 1.3.1 El REPL: una conversación

Con el entorno activo, escribe solo `python` y Enter. Python no ejecuta un archivo; abre una **conversación**: te muestra un símbolo `>>>` y espera una instrucción. A esto se le llama REPL (de *read-eval-print loop*: lee lo que escribes, lo evalúa, imprime el resultado y vuelve a esperar). Pruébalo así (tú escribes lo que va después de `>>>`; la línea de bienvenida de las primeras filas cambia con tu versión):

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

Recorre la conversación. `142 + 1` devuelve `143`, sin necesidad de `print`: el REPL imprime por ti el valor de lo que escribas. `"reportes"` vuelve con comillas simples, porque así muestra Python un texto cuando lo representa. `tiempo_ms = 142` es una asignación y no devuelve nada; después, escribir `tiempo_ms` devuelve `142`: **el REPL recuerda** lo que le dijiste mientras no lo cierres. La cuarta es el error que ya conoces de la Lección 0, `TypeError`, y obsérvalo: el REPL **no se cierra** por el error. Muestra el informe y vuelve a esperar. Eso lo hace ideal para equivocarse y aprender. Para salir se escribe `exit()` (o su gemelo `quit()`) o se presiona `Ctrl + D`; la [documentación](https://docs.python.org/3/tutorial/interpreter.html) da `Ctrl + D` como la forma principal y `quit()` como alternativa.

Dos detalles de versión, para que no te desconcierte si tu pantalla se ve distinta. El REPL de **3.13 en adelante** es renovado: tiene color y edición de varias líneas, y el nombre que muestra en un informe de error es `<python-input-0>` en lugar de `<stdin>`, y la propia línea que falló. Y el REPL de 3.12, el de tu Mint, es el sencillo de arriba. Nada de lo que se hace en el curso depende de esa diferencia.

¿Para qué sirve el REPL? Para **probar ideas rápidas**: «¿qué hace esta operación?», «¿cómo se llamaba esta función?». ¿Para qué **no** sirve? Para escribir programas. Lo que dices en el REPL se pierde cuando sales; no queda ningún archivo. Un programa es un texto que se guarda, se corrige y se vuelve a ejecutar. Para eso están los archivos.

#### 1.3.2 Un archivo: tu primer guion

Un **guion** (*script*) es un archivo de texto con instrucciones de Python que se ejecuta de principio a fin. Para crearlo necesitas un editor de texto. Mint trae uno llamado **Xed** (aparece en el menú como «Editor de texto»). Conviene configurarlo una vez: en sus preferencias activa **insertar espacios en lugar de tabuladores** y pon el ancho del tabulador en 4. Python da mucha importancia a los espacios al comienzo de las líneas (la [Lección 2](02-valores-texto-decisiones.md) te explica por qué), y mezclar tabuladores con espacios es una fuente clásica de errores que preferimos evitar desde el primer día. Si prefieres la terminal, `nano hola.py` abre un editor sencillo: escribe, guarda con `Ctrl + O` y Enter, sal con `Ctrl + X`.

Crea el archivo `~/curso-python/hola.py` con este contenido:

```python
# fig01_01.py
print("Hola, Python")
```

```text
$ cd ~/curso-python
$ python3 hola.py
Hola, Python
```

El nombre `fig01_01.py` de la primera línea es la etiqueta de la figura dentro del curso (en el repositorio del curso el archivo se llama así); **tú lo guardas como `hola.py`**, y por eso la orden es `python3 hola.py`. La primera línea es un comentario (empieza con `#`, Python la ignora) y puedes omitirla. La segunda es el programa. `print` es una **función** que ya trae Python: muestra en pantalla lo que va entre paréntesis. Lo que va entre comillas es un **texto**, como viste en la lección anterior. Esa es toda la explicación que necesitas hoy; la Lección 2 va a fondo.

Ejecútalo dos veces: una **sin** el entorno activo y otra **con** él. Fuera del entorno la orden es `python3 hola.py`. Dentro es `python hola.py`, porque dentro del entorno `python` existe y apunta a su Python. En ambos casos, la salida es `Hola, Python`; lo que cambia, sin que lo notes, es **qué Python lo ejecutó**. Esa diferencia es invisible mientras todo funciona y decisiva cuando algo falla, y por eso hay un ejercicio al final para anotarla.

Con eso aparece el segundo archivo de hoy, el primero del proyecto. Crea la carpeta del `revisor` y el archivo donde crecerá:

```text
$ mkdir ~/curso-python/revisor
```

```python
# fig01_02.py
print("revisor: todavía no revisa nada")
```

Se guarda como `~/curso-python/revisor/revisor.py` (la etiqueta `fig01_02.py` es, otra vez, solo el nombre de la figura). Para correrlo, entra primero a su carpeta, porque `python3 revisor.py` busca el archivo en la carpeta donde estás:

```text
$ cd ~/curso-python/revisor
$ python3 revisor.py
revisor: todavía no revisa nada
```

Es un programa de una línea, a propósito: lo importante es que **el archivo exista, corra y sea el punto de partida**. Desde la Lección 2 crece hasta ser el programa completo. La palabra «todavía» es una promesa.

### 1.4 El primer *traceback*

En la Lección 0 viste un informe de error y leíste su última línea. Hoy lo lees completo, con un error que vas a cometer pronto y muchas veces: escribir mal el nombre de algo. Este programa tiene una errata deliberada. Esta vez guárdalo con el nombre de la figura, `~/curso-python/fig01_03.py`, para que el informe de tu pantalla coincida con el de abajo:

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

(En tu pantalla, la ruta del archivo será la ruta completa; aquí se acorta al nombre.)

**La regla para leer un informe de error de Python: de la última línea hacia arriba.** Se contestan tres preguntas, en este orden.

**¿Qué clase de error es?** Mira el principio de la última línea: `NameError`. Un `NameError` ocurre cuando usas un nombre que Python no conoce. La Lección 0 explicó que un nombre es una etiqueta que apunta a un valor; Python tiene algunos nombres de fábrica (como `print`) y otros que tú creas con una asignación. `pirnt` no es ninguno de los dos.

**¿Qué dice exactamente?** El resto de la última línea: `name 'pirnt' is not defined`, «el nombre `pirnt` no está definido». Y la ayuda: `Did you mean: 'print'?`, «¿quisiste decir `print`?». Python comparó el nombre desconocido con los que sí conoce, encontró uno muy parecido y te lo sugiere. Esa sugerencia, que para este tipo de error es idéntica en las versiones 3.12 y 3.14, resuelve la mayor parte de los tropiezos de un principiante.

**¿Dónde pasó?** Las líneas de arriba. `File "fig01_03.py", line 2, in <module>` dice el archivo y la línea (la 2, porque la 1 es el comentario). Debajo, Python repite el texto de esa línea de tu código, y los acentos circunflejos `^^^^^` señalan la palabra exacta: cinco caracteres, justo `pirnt`.

Haz lo que dice la sugerencia: cambia `pirnt` por `print`, guarda y vuelve a ejecutar. Con esa pequeña ceremonia (leer, entender, corregir, repetir) vas a trabajar el resto del curso. Un error no significa que lo hiciste mal; significa que Python te está contestando con precisión.

## El error que vas a ver

Hoy hay tres mensajes que conviene saber leer: dos ya los viste y el tercero es un aviso para después.

**`NameError`** es el de la sección anterior. Variantes que verás: una mayúscula donde no va (`Print("hola")` da `NameError: name 'Print' is not defined. Did you mean: 'print'?`, porque Python distingue entre mayúsculas y minúsculas), una letra de más, un nombre que olvidaste definir. En todos los casos se lee igual.

**`No module named pip`** es la respuesta de tu Mint en 1.1.2, y su pariente, el mensaje de `ensurepip` de 1.2.2, es la de un entorno al que le falta la misma pieza. Los dos dicen con todas sus letras qué falta, y los dos se resuelven sin tocar el Python del sistema: el primero, trabajando dentro del entorno; el segundo, instalando `python3.12-venv` y volviendo a crear el entorno sobre la carpeta a medias.

**`externally-managed-environment`** es el aviso de 1.1.3: no lo verás en una Mint recién instalada, pero sí el día que instales el `pip` del sistema, o en otra distribución. La primera línea, `error: externally-managed-environment`, la pone `pip`: la PEP 668 no fija ese texto, solo exige que el instalador se niegue con un error y muestre el mensaje que la distribución escribió en su archivo marcador (o, si no hay, uno propio que sugiera un entorno virtual). El cuerpo, por eso, lo escribe cada sistema. Como ejemplo real, este es el mensaje completo que da el Python de Homebrew en un macOS (el gestor de paquetes de ahí se llama `brew`; en Mint sería `apt`):

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

Léelo como lees un *traceback*, sin miedo, por partes. La primera línea es la **clase**: `externally-managed-environment`, «entorno administrado externamente». La segunda, `This environment is externally managed`, dice la razón: este Python pertenece a otro gestor. La tercera abre la lista de salidas. **Primero**, instalar el paquete con el gestor del sistema (aquí `brew`; en Mint sería `apt`), siempre que el paquete exista allí. **Segundo**, si el paquete no está en el gestor, crear un entorno virtual y usar `python3 -m pip` dentro de él: las tres líneas que muestra son exactamente `venv`, `source ... activate` y `pip install`, que acabas de usar. **Tercero**, si lo que quieres es una *aplicación* (no una biblioteca para usar en tu código), `pipx`, que crea un entorno aislado por cada aplicación. El `revisor` terminará instalándose así, en la [Lección 11](11-el-programa-terminado.md).

Debajo de las tres salidas vienen dos párrafos más que escribió Homebrew: cómo «restaurar el comportamiento anterior» con `--break-system-packages` y la advertencia, en mayúsculas, de que hacerlo puede romper la instalación. Y las dos últimas líneas ya no son de la distribución sino de `pip`: una `note:` que vuelve a mencionar `--break-system-packages` «a riesgo de romper tu instalación de Python o tu sistema operativo», y una `hint:` que remite a la PEP 668. Que la opción aparezca dos veces no la vuelve recomendable: aparece para que sepas que existe y lo que cuesta, que es lo que dice la sección siguiente.

El cuerpo es una guía de resolución escrita por quien administra ese Python, y cambia de un sistema a otro; lo que no cambia, porque lo pone `pip` y no la distribución, es la primera línea y la nota final. **Léelo cada vez que aparezca**: te ahorra buscar en internet, y la mayoría de las respuestas de internet para este error recomiendan el atajo que rompe la protección.

## Lo que se hace mal

- **Usar `sudo pip install`.** Instala en el Python del sistema con permisos de administrador. Es la forma más rápida de pisar una biblioteca que Mint necesita y descubrirlo semanas después. Cada paquete va dentro de un entorno virtual.
- **Usar `--break-system-packages` para que «ya funcione».** Desactiva exactamente la protección que te ayuda. El curso no lo enseña ni lo usa. Si lo ves en una respuesta de internet, ignórala.
- **Instalar sin ver el prefijo `(.venv)`.** Si abriste una terminal nueva y olvidaste activar, la instalación se rechaza (porque estás fuera del entorno) o, en un sistema sin protección, ocurre en el lugar equivocado. La rutina es mirar el prefijo antes de instalar y comprobar con `which python` ante la duda.
- **Mover o copiar la carpeta `.venv`.** Un entorno guarda rutas absolutas y no sobrevive a un cambio de carpeta. Se borra y se recrea con `python3 -m venv .venv`; los paquetes se vuelven a instalar. Es desechable por diseño.
- **Poner el código del proyecto dentro del entorno.** El entorno contiene a Python y a los paquetes; tu código vive al lado, en `revisor/`. Así borrar el entorno no te cuesta ni una línea de lo tuyo.
- **Mezclar tabuladores y espacios en el editor.** Python usa los espacios del comienzo de línea para estructurar el programa, y mezclar los dos tipos da errores difíciles de ver. Configura tu editor a 4 espacios, hoy, antes de escribir código de verdad.
- **Escribir el comando `python` fuera del entorno y concluir que «Python no está instalado».** Lo que falta es el alias `python`: fuera del entorno se escribe `python3`. Que `python` no exista en una Mint recién instalada es normal.
- **Quedarse horas con un error sin leerlo.** Un informe de Python casi siempre dice qué y dónde. La costumbre de empezar por la última línea resuelve la mayoría.

## Ejercicios

### Ejercicio 1 — Tu entorno, medido

Ejecuta en una terminal sin entorno activo: `python3 --version` y `which python3`. Después activa el entorno y ejecuta `python --version`, `which python` y `python -m pip --version`. Escribe en tu [bitácora](bitacora.md) las cinco salidas y una frase que conteste: ¿qué cambió entre `which python3` fuera y `which python` dentro, y por qué?

### Ejercicio 2 — Provoca el rechazo y léelo

Desactiva el entorno (`deactivate`) y ejecuta `python3 -m pip install httpx`. Anota en la bitácora la respuesta exacta y explica con tus palabras quién habla (lo que va antes de los dos puntos) y qué dice. Después lee el ejemplo de `externally-managed-environment` de la sección «El error que vas a ver» y escribe lo que dice cada una de sus tres primeras partes (la clase, la razón, la lista de salidas). Por último, activa el entorno y repite la instalación. Describe qué cambió y qué comprobaste con `python -m pip list`.

### Ejercicio 3 — El `revisor` dentro y fuera del entorno

Crea `~/curso-python/revisor/revisor.py` con la línea de la figura 2 y entra a su carpeta (`cd ~/curso-python/revisor`). Ejecútalo **sin** el entorno (con `python3 revisor.py`) y **con** él (con `python revisor.py`). Antes de cada ejecución, corre `which python3` o `which python` según el caso, y anota en la bitácora cuál Python se usó cada vez. ¿Salió distinto el resultado?

### Ejercicio 4 — Provoca un error nuevo y léelo

Sin tocar el entorno, crea un archivo con la línea `Print("hola")` (con P mayúscula). Antes de ejecutarlo, predice la última línea del informe. Ejecútalo y compara. Después provoca un segundo error distinto: crea un archivo de dos líneas, `print("primera")` y `print("hola)` (la segunda sin la comilla de cierre), y mira qué clase de error aparece. ¿Se alcanza a mostrar `primera`?

## Soluciones

### Solución 1

Una salida típica es `Python 3.12.x`, `/usr/bin/python3`, `Python 3.12.x`, `/home/tu_usuario/curso-python/.venv/bin/python` y un `pip` con la ruta de `.venv/lib/python3.12/site-packages/pip`. Lo que cambió entre fuera y dentro es **la ruta**: fuera es `/usr/bin/python3`, el Python del sistema; dentro es el que está en `.venv/bin/`, el del entorno. Cambió porque `activate` puso `.venv/bin` al principio de la lista de lugares donde la terminal busca programas; por eso `python` (que ni siquiera existía fuera) pasa a significar «el del entorno». La versión es la misma porque el entorno se creó con el `python3` del sistema.

### Solución 2

Fuera del entorno, tu Mint contesta `/usr/bin/python3: No module named pip`: habla el Python del sistema y dice que no tiene `pip`, así que ahí no se instala nada. En el ejemplo de `externally-managed-environment`, la clase es `externally-managed-environment`: el tipo de problema. La razón es que ese Python lo administra otro gestor de paquetes, y `pip` respeta la marca `EXTERNALLY-MANAGED` que dejó quien lo instaló. La lista de salidas es: instalar con el gestor del sistema si el paquete existe allí, crear un entorno virtual para bibliotecas, o `pipx` para aplicaciones. Al activar el entorno y repetir, la instalación se completa: dentro del entorno hay `pip`, y su protección no se aplica porque ahí no está tocando el Python del sistema. `python -m pip list` muestra `httpx` y sus dependencias en la lista del entorno, y no en la del sistema.

### Solución 3

Debe salir `revisor: todavía no revisa nada` en ambos casos. Lo que cambia es el Python: sin entorno, `which python3` da `/usr/bin/python3`; con entorno, `which python` da la ruta dentro de `.venv/bin/`. El resultado no cambia porque el programa solo usa `print`, que no depende de ningún paquete; la diferencia se volverá visible cuando un programa importe algo instalado en el entorno (desde la Lección 9): ese programa funcionaría solo con el entorno activo. Saber qué Python usaste es lo que te permite entender por qué.

### Solución 4

Con `Print("hola")` la última línea es `NameError: name 'Print' is not defined. Did you mean: 'print'?`: Python distingue mayúsculas de minúsculas. Con `print("hola)` el error cambia de clase: aparece un `SyntaxError: unterminated string literal (detected at line 2)`, que significa «texto sin terminar», porque falta la comilla que lo cierra. `primera` **no** se muestra: el error ocurre antes de ejecutar nada. Es un error de forma, y Python lo detecta en el paso en que lee y traduce el archivo (el primero de los cuatro pasos de la Lección 0). No es un `NameError`, que solo se descubre al llegar a esa línea con el programa ya en marcha. La Lección 2 estudia este error a fondo.

## Cómo sé que lo logré

- [ ] `python3 --version` muestra una versión que empieza con `Python 3.` y la anotaste en la bitácora.
- [ ] `python3 -m pip install httpx`, con el entorno **desactivado**, termina con `No module named pip`, sabes explicar sin mirar la lección qué significa y cuál es la salida correcta, y reconocerías el aviso `externally-managed-environment` si un día lo ves.
- [ ] Existe la carpeta `~/curso-python/.venv`; con el entorno activo, el símbolo de la terminal empieza con `(.venv)`, y `which python` muestra una ruta que termina en `.venv/bin/python`.
- [ ] Con el entorno activo, `python -m pip list` muestra `httpx`; con el entorno desactivado, `python3 -m pip list` contesta `No module named pip`: fuera del entorno no hay `pip`, y por lo tanto tampoco `httpx`.
- [ ] `python3 hola.py` fuera del entorno y `python hola.py` dentro muestran `Hola, Python`.
- [ ] `~/curso-python/revisor/revisor.py` existe y, al ejecutarlo, muestra `revisor: todavía no revisa nada`.
- [ ] Sabes leer, sin pedir ayuda, el informe de `NameError` de la figura 3: dices qué palabra falló, en qué línea y qué sugerencia dio Python.
- [ ] Puedes decir, sin mirar, por qué el entorno no se mueve ni se copia, y por qué nunca se instala con `sudo pip`.

## Resumen

Responde sin mirar la lección:

1. ¿Cuál es el Python que viene con tu Mint, de quién es, y cómo compruebas desde dónde corre?
2. ¿Qué dice `externally-managed-environment`, quién lo pone, y cuáles son las tres salidas que sugiere? ¿Cuál es la que usa el curso?
3. ¿Qué tres cosas cambia `source .venv/bin/activate` en tu terminal, y cómo sabes que estás dentro?
4. ¿Por qué el entorno vive fuera de la carpeta `revisor/` y por qué no se mueve ni se copia?
5. ¿Qué diferencia hay entre el REPL y un archivo? ¿Cuándo usas cada uno?
6. ¿En qué orden se lee un informe de error de Python, y qué tres preguntas contesta?
7. ¿Qué Python usa `python` dentro del entorno y qué Python usa `python3` fuera?

## Para leer más

- [Tutorial de Python: Entornos virtuales y paquetes](https://docs.python.org/3/tutorial/venv.html) — la guía oficial de `venv` y `pip`, con las órdenes de esta lección. En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [PEP 668, «Marking Python base environments as externally managed»](https://peps.python.org/pep-0668/) — la especificación que explica el archivo `EXTERNALLY-MANAGED` y el rechazo de `pip`. Consultado el 7 de octubre de 2026.
- [Documentación del módulo `venv`](https://docs.python.org/3/library/venv.html) — qué es `pyvenv.cfg`, por qué un entorno es desechable y por qué no se mueve. Consultado el 7 de octubre de 2026.
- [pip: primeros pasos](https://pip.pypa.io/en/stable/getting-started/) — comprobar que `pip` está instalado, instalar un paquete y por qué se invoca como `python -m pip`. Consultado el 7 de octubre de 2026.
