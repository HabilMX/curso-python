# Lección 0 — Qué es Python y qué NO es

**Tiempo:** 90 min

**Qué construyes:** nada todavía (lectura)

**Qué aprendes:** qué hace Python con tu archivo (intérprete y *bytecode*); tipado dinámico pero fuerte; las anotaciones de tipo no se imponen al ejecutar; qué es el GIL, dicho sin miedo; qué es un entorno virtual y por qué el curso usa Python 3.14 y también 3.12

**De dónde vienes.** De ningún lado, y está bien. No hace falta que tengas Python instalado, que hayas escrito una línea de código ni que sepas qué es un entorno virtual. Esta lección es **de lectura**: no instalas nada y no construyes nada todavía. Los programas que aparecen son de una o dos líneas, y cada uno trae la salida que produce, de modo que puedes seguirlos sin una computadora delante. Si ya tienes `python3` en tu Linux Mint y quieres probarlos, adelante; si no, la [Lección 1](01-instalacion.md) lo deja todo listo.

**Qué no hace esta lección.** No enseña a programar ni a instalar. Enseña **qué es la cosa que vas a aprender**, y sobre todo qué *no* es, porque la mayoría de los problemas de un principiante en Python no vienen de la sintaxis sino de una expectativa equivocada: creer que Python avisa de un error de tipos antes de correr (no avisa), que «interpretado» quiere decir «sin compilar nada» (no es tan simple) o que el GIL impide hacer cualquier cosa en paralelo (impide menos de lo que se cree). Poner las expectativas bien desde el principio ahorra semanas de confusión.

## Al terminar vas a poder

- Explicar, en cuatro pasos, qué hace Python con un archivo `.py` desde que lo ejecutas hasta que aparece el resultado, y decir qué es el *bytecode* y para qué sirve la carpeta `__pycache__`.
- Decir por qué Python es **dinámico pero fuerte** y predecir qué pasa con `"142" + 1` y con `"142" + "1"` sin ejecutarlos.
- Explicar por qué `tiempo_ms: int = "rápido"` corre sin quejarse, y quién sí puede avisar de esa contradicción.
- Describir el GIL con tus palabras, decir cuándo afecta y cuándo no, y por qué el `revisor` no tiene que preocuparse por él.
- Explicar qué es un entorno virtual y por qué existe, y justificar por qué el curso se enseña con Python 3.14 pero todo el código corre también en 3.12.
- Leer la última línea de un *traceback* de `TypeError` y decir qué te cuenta.

## El porqué antes del cómo

Dentro de once lecciones habrás escrito un programa llamado el **`revisor`**. Recibe una lista de servicios (el catálogo de productos de una tienda, su sistema de pagos, su inventario), pregunta a todos a la vez si están funcionando y entrega una tabla como esta:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Léela como la leería alguien de guardia a las once de la noche. `catalogo` y `pagos` contestaron rápido. `inventario` contestó, pero tardó 2.3 segundos, que es demasiado: está **lento**. `reportes` no contestó: está **caído**, y el detalle dice por qué (`sin conexión`). Esa tabla es el destino del curso. En esta lección no la construyes, pero te sirve de material: cada dato de ella es de una clase distinta (el nombre es texto, 142 es un número, la raya `—` representa que **no hay dato**), y entender esas clases es justo lo que viene.

Antes de escribir una sola línea hace falta contestar tres preguntas que todo principiante se hace, aunque no siempre en voz alta. La primera: **¿qué es exactamente Python y qué hace con lo que escribo?** La segunda: **¿qué me va a avisar de mis errores y qué no?** La tercera: **¿por qué veo gente discutir sobre «el GIL», «el entorno virtual» y «qué versión usas»?** Las tres tienen respuesta corta. La primera: Python es un programa que lee tu texto y lo ejecuta. La segunda: casi nada te avisa antes de que el programa corra, así que aprenderás a leer los errores en lugar de temerlos. La tercera: son tres decisiones prácticas que conviene entender una vez.

Un **programa** es una lista de instrucciones escritas en un archivo de texto. Un **lenguaje de programación** es el conjunto de reglas con que se escriben esas instrucciones para que sean claras tanto para ti como para la computadora. El problema es que la computadora, por dentro, solo entiende instrucciones diminutas y numéricas (sumar dos cantidades, copiar un valor de un lugar a otro) que se llaman **código máquina**, y que dependen del procesador. Nadie escribe a mano en código máquina. Siempre hay algo en medio que **traduce**, y la gran diferencia entre un lenguaje y otro está en *cuándo* y *cómo* traduce. Python hace su traducción de una manera particular, y esa manera explica casi todo lo demás de esta lección.

Una advertencia de vocabulario antes de seguir. La palabra «Python» nombra dos cosas distintas. Una es el **lenguaje**: las reglas de cómo se escribe, que se describen en una especificación pública. La otra es el **programa que ejecuta ese lenguaje** en tu computadora, y el que casi todo el mundo usa se llama **CPython** (la «C» es porque está escrito en el lenguaje C). Cuando en una terminal escribes `python3`, estás llamando a CPython. Existen otros ejecutores (PyPy, por ejemplo), pero este curso, como casi todo el trabajo profesional, usa CPython. Cuando una frase como «el GIL» aparezca más abajo, será una característica de CPython, no del lenguaje en abstracto.

## Los conceptos

Son cuatro: qué hace el intérprete con tu archivo, qué significa que el tipado sea dinámico pero fuerte (con las anotaciones de tipo como tercer apartado), qué es el GIL y qué es un entorno virtual con las versiones. Se explican en ese orden, cada uno con un ejemplo mínimo.

### 0.1 El intérprete y el *bytecode*

#### 0.1.1 Qué pasa cuando ejecutas un archivo

Imagina que guardas esto en un archivo llamado `lectura.py`:

```text
tiempo_ms = 142
print(tiempo_ms)
```

(Dos palabras de lectura por adelantado. `tiempo_ms = 142` quiere decir «guarda el número 142 bajo el nombre `tiempo_ms`»; el nombre lleva `_ms` porque es el tiempo en milisegundos, y en este curso las unidades siempre van en el nombre. `print(...)` quiere decir «muestra en pantalla lo que va entre paréntesis». La [Lección 2](02-valores-texto-decisiones.md) explica ambas a fondo.)

Para ejecutarlo escribes en una terminal `python3 lectura.py`. Lo que ocurre entonces tiene cuatro pasos, y vale la pena conocerlos porque cada uno explica una conducta que de otro modo parece magia.

1. **Python lee el texto.** Abre el archivo y lo recorre de arriba abajo, fijándose en que esté bien escrito según las reglas del lenguaje. Si falta un paréntesis por cerrar, aquí es donde se descubre, y el programa **no empieza a correr**: ni una sola línea anterior se ejecuta. Lo puedes comprobar con un archivo cuya primera línea es `print("primera")` y cuya segunda tiene un paréntesis sin cerrar: no aparece «primera», solo el error `SyntaxError: '(' was never closed`. Es decir, la revisión de la forma ocurre antes de la ejecución.
2. **Python traduce el texto a una lista de instrucciones propias.** No a código máquina, sino a un formato intermedio, más sencillo que tu texto y más abstracto que el procesador. Esa lista se llama ***bytecode***. La [documentación oficial](https://docs.python.org/3/glossary.html#term-bytecode) lo define como «la representación interna de un programa Python en el intérprete CPython».
3. **Una máquina virtual ejecuta el *bytecode*.** «Virtual» significa que no es un aparato físico sino un programa que se comporta como si lo fuera: toma cada instrucción del *bytecode*, de una en una, y hace lo que dice. Esa máquina virtual es el corazón de CPython, y es lo que llamamos el **intérprete**.
4. **El resultado aparece**, en este caso el número `142` en tu pantalla.

Todo eso ocurre en una fracción de segundo cada vez que ejecutas el archivo, sin que tengas que pedirlo. Por eso se dice que Python es un lenguaje **interpretado**: ejecutas el archivo de texto directamente, sin un paso previo en el que tú mismo generes un programa ejecutable. La [documentación lo explica](https://docs.python.org/3/glossary.html#term-interpreted) casi con esas palabras («los archivos fuente se pueden ejecutar directamente sin crear explícitamente un ejecutable que luego se ejecuta»), y añade enseguida una salvedad honesta: la distinción entre interpretado y compilado «puede ser borrosa por la presencia del compilador de *bytecode*». Es la salvedad que importa. Python **sí** compila (el paso 2 es una compilación), solo que compila a un formato intermedio y lo hace por ti, en silencio, cada vez.

El contraste con otros lenguajes ayuda. En Go o en Rust escribes tu código, ejecutas un compilador que produce un archivo ejecutable (código máquina directo para tu procesador) y después ejecutas ese archivo. El ejecutable ya no necesita al compilador ni al lenguaje: lo copias a otra computadora y corre. En Python no hay ese archivo final: la computadora donde quieras correr tu programa necesita **tener Python instalado**, porque es Python quien lee y ejecuta tu texto cada vez. Esta es una consecuencia práctica que verás a partir de la Lección 1, y es la razón de que la mitad de lo que se aprende «alrededor» de Python (versiones, entornos, instalación) tenga que ver con ese hecho.

#### 0.1.2 Lo que Python guarda: `__pycache__` y los archivos `.pyc`

Compilar a *bytecode* cuesta un poco de tiempo, y si el archivo no ha cambiado desde la última vez, repetir esa traducción es trabajo perdido. Por eso Python guarda el resultado. La [documentación del glosario](https://docs.python.org/3/glossary.html#term-bytecode) dice que el *bytecode* «también se guarda en caché en archivos `.pyc`, de modo que ejecutar el mismo archivo es más rápido la segunda vez». Esos archivos viven en una carpeta llamada `__pycache__`, junto a tu código.

Hay un detalle que sorprende y que conviene medir en vez de suponer. Si ejecutas directamente `python3 lectura.py`, **no** aparece ninguna carpeta `__pycache__`: Python compila el archivo que le diste a la memoria, lo ejecuta y no guarda nada. La carpeta aparece cuando un archivo se **importa** desde otro, es decir, cuando un programa usa el contenido de otro archivo (`import` se explica en la [Lección 3](03-bucles-funciones-modulos.md)). Se midió así: se ejecutó un archivo directamente y se contaron cero archivos `.pyc`; se ejecutó otro que importaba al primero y apareció uno. Si quieres forzar la creación sin importar nada, existe `python3 -m py_compile lectura.py`. Un fragmento, con las versiones 3.12 y 3.14 de la misma máquina, deja ver el nombre que se genera:

```text
$ python3.12 -m py_compile lectura.py
$ python3.14 -m py_compile lectura.py
$ ls __pycache__
lectura.cpython-312.pyc
lectura.cpython-314.pyc
```

Fíjate en el nombre: `lectura.cpython-312.pyc`. Dice cuál archivo fue (`lectura`), qué ejecutor lo generó (`cpython`) y con qué versión (`312` es la 3.12). El *bytecode* de una versión **no sirve** en otra, y la [documentación lo avisa](https://docs.python.org/3/glossary.html#term-bytecode): «no se espera que los *bytecodes* funcionen entre diferentes máquinas virtuales de Python, ni que sean estables entre versiones». Por eso Python guarda un archivo distinto por versión y no mezcla los de una con los de otra.

Tres consecuencias prácticas:

- **`__pycache__` es seguro de borrar.** Python lo vuelve a crear cuando lo necesita. No es parte de tu programa, es un caché.
- **No se guarda en el repositorio del proyecto.** Un repositorio es el lugar donde un equipo guarda y comparte el código de un programa, con su historia de cambios. Ahí solo va lo que escribes tú; `__pycache__` es un derivado de tu código y cambia con cada versión de Python, así que se deja fuera.
- **No es una protección.** Algunas personas creen que enviar solo los `.pyc` oculta su código. No es así: los `.pyc` se pueden volver a leer con herramientas, y no es una medida de seguridad.

#### 0.1.3 Ver el *bytecode* (solo por curiosidad)

Python trae una herramienta, el módulo `dis`, que muestra el *bytecode* de un archivo en forma legible. No necesitas aprenderlo, pero verlo una vez quita el misterio. Este es el resultado en Python 3.12 para las dos líneas de `lectura.py`:

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

La columna del centro son las instrucciones. `LOAD_CONST 142` significa «pon el valor constante 142 a la mano», `STORE_NAME tiempo_ms` significa «guárdalo bajo el nombre `tiempo_ms`», y las de la línea 2 piden el nombre `print`, piden el nombre `tiempo_ms` y llaman a la primera con la segunda. Cada línea de tu texto se vuelve dos, tres o cuatro de estas. Y aquí está la razón por la que este bloque es un **fragmento** y no un programa del curso: *el bytecode cambia entre versiones*. Al medirlo en Python 3.14, la primera instrucción de la línea 1 ya no se llama `LOAD_CONST 142` sino `LOAD_SMALL_INT 142`, y el orden de dos instrucciones de la línea 2 es otro. La conducta del programa es la misma; el idioma interno que usa la máquina virtual para describirla, no. Lo que tienes que quedarte de esto no es ninguna de esas palabras sino la idea: entre tu texto y el resultado hay una lista de instrucciones intermedia que tú no escribes y que Python te esconde.

#### 0.1.4 Por qué importa esto para el `revisor`

Dos cosas. La primera: Python tarda más que un programa compilado a código máquina en ejecutar cálculos puros, porque cada instrucción del *bytecode* pasa por la máquina virtual. En un programa que multiplica millones de números eso se nota. Pero el `revisor` casi no calcula: **pasa su tiempo esperando** a que una red conteste. Mientras espera 2.3 segundos la respuesta de `inventario`, la velocidad de Python es irrelevante. Lo que importará será esperar a todos los servicios a la vez en lugar de uno tras otro, y eso es un tema de las lecciones 9 y 10. La segunda: como Python necesita estar instalado donde se ejecuta tu programa, y como cada versión tiene su propio *bytecode* y su propio comportamiento, saber **cuál Python estás usando** es una pregunta que te harás con frecuencia. La respuesta está en el último apartado de esta lección.

### 0.2 Tipado dinámico, pero fuerte

#### 0.2.1 Qué es un tipo

Un **valor** es un dato concreto: el número `142`, el texto `"catalogo"`. El **tipo** de un valor es la clase de cosa que es: un número entero, un texto, una raya que significa «no hay dato». Un **nombre** (o variable) es una etiqueta que apuntas a un valor, como `tiempo_ms` en el ejemplo anterior. Mira la tabla del `revisor`: `catalogo` es un texto, `142` es un número, `—` es la ausencia de dato. El tipo importa porque determina **qué se puede hacer** con el valor: los números se suman, los textos se pegan uno con otro. Y la pregunta que distingue a los lenguajes es *cuándo y quién revisa* que lo que intentas hacer tenga sentido para ese tipo.

#### 0.2.2 Dinámico: el tipo vive en el valor, no en el nombre

En Python, **el tipo pertenece al valor, no al nombre**. Un nombre puede apuntar hoy a un número y mañana a un texto, y a Python no le importa. La revisión de si una operación tiene sentido ocurre **mientras el programa corre**, justo en el momento de ejecutar esa línea: eso es lo que significa **dinámico**. Esto contrasta con los lenguajes de tipado estático (Go, Rust, Java), donde cada nombre se declara con su tipo y el compilador revisa todo antes de ejecutar.

Mira la primera figura. Es una sola línea y hay que leerla pieza por pieza.

```python
# fig00_01.py
print(142 + 1, "142" + "1")
```

```text
$ python3 fig00_01.py
143 1421
```

La primera línea es un **comentario**: todo lo que va después de un `#` es una nota para humanos que Python ignora. Aquí lleva el nombre de la figura, para que sepas qué archivo es. La segunda es la que ejecuta. `print(a, b)` muestra los dos valores separados por un espacio, y por eso la salida trae dos cosas: `143` y `1421`. Lo interesante es que **ambas usan el mismo signo `+`** y dan resultados de naturaleza distinta.

- `142 + 1`: los dos son números (no llevan comillas), y `+` los **suma**: 143.
- `"142" + "1"`: lo que va entre comillas es **texto**, aunque parezca un número. Un texto se escribe entre comillas, dobles o simples. Aquí `+` no suma: **pega** un texto con otro, y el resultado es el texto `1421`, que se muestra sin las comillas.

El signo es el mismo, pero qué hace depende del tipo de los valores. Es la primera lección de tipos: `"142"` y `142` **se ven casi iguales y son cosas distintas**. En el `revisor`, el `142` de la tabla es un número que se puede comparar con 1000 para decidir si un servicio está lento; si por error llegara como el texto `"142"`, esa comparación no tendría sentido.

Otra forma de ver lo dinámico es que el mismo nombre cambie de tipo. Este fragmento es válido en Python:

```text
lectura = 142
lectura = "rápido"
```

El nombre `lectura` apuntó primero a un número y luego a un texto. Python no protesta, porque no hay ningún lugar donde hayas dicho «`lectura` es un número» y la regla se mantenga. Esa libertad es cómoda para escribir rápido y peligrosa para escribir con descuido, y por eso este curso, aunque Python no lo exija, te enseñará a ser ordenado: un nombre, una clase de dato.

#### 0.2.3 Fuerte: Python no adivina lo que quisiste decir

Que Python sea dinámico **no** quiere decir que sea permisivo. Es dinámico **y fuerte**: cuando intentas una operación que no tiene sentido para esos tipos, Python **no inventa una conversión**; se detiene y te dice que hay un error. Veamos la segunda figura, una sola línea que mezcla un texto con un número.

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

El programa **no imprimió nada**: se detuvo y mostró un informe de error, que en Python se llama ***traceback*** (algo así como «el rastro hacia atrás»). Por ahora fíjate solo en la última línea: `TypeError: can only concatenate str (not "int") to str`. «`TypeError`» es la clase del error (un problema de tipos); lo que sigue es la explicación en inglés. Traducida: «solo se puede concatenar (pegar) un `str` (texto) con otro `str`, no con un `int` (número entero)». Python te está diciendo que intentaste pegar un texto con un número y que no sabe qué hacer. La sección «El error que vas a ver» lee el resto del informe línea por línea. (En tu pantalla la ruta del archivo será larga y completa; aquí se acorta al nombre para que se lea.)

Aquí está lo de **fuerte**. Otros lenguajes, ante `"142" + 1`, resuelven por su cuenta: JavaScript, por ejemplo, convierte el número a texto y devuelve `"1421"` sin avisar. Eso puede parecer amable y es una fuente clásica de errores, porque el programa sigue corriendo con un dato que nadie esperaba. Python prefiere la queja inmediata a la conversión silenciosa. Esa decisión juega a tu favor: el error aparece **donde ocurre**, con el nombre del problema y la línea exacta, y no tres funciones más adelante como un resultado raro.

Junta las dos mitades y obtienes la conducta completa. **Dinámico**: la revisión de tipos ocurre al ejecutar cada línea, no antes. **Fuerte**: cuando esa revisión falla, Python se detiene en lugar de adivinar. De ahí sale una consecuencia que debes tener presente: **un error de tipos solo aparece si esa línea llega a ejecutarse**. Si tu programa tiene una rama que se usa una vez al mes, un error de tipos escondido ahí no se descubrirá hasta ese día. Es un argumento a favor de las pruebas (lección 8) y de las herramientas que revisan el código sin ejecutarlo.

#### 0.2.4 Las anotaciones de tipo: una promesa que Python no vigila

Python permite *escribir* el tipo que esperas junto a un nombre, y lo hace con una sintaxis llamada **anotación**: `nombre: tipo = valor`. La [documentación las llama «sugerencias de tipo»](https://docs.python.org/3/glossary.html#term-type-hint) (*type hints*) y dice dos cosas importantes: que son **opcionales** y que «Python no las impone» (en inglés, *are not enforced*). Veamos lo que eso significa con la tercera figura:

```python
# fig00_03.py
tiempo_ms: int = "rápido"
print(tiempo_ms)
```

```text
$ python3 fig00_03.py
rápido
```

Léela con calma, porque contiene una contradicción deliberada. La línea 2 dice: «el nombre `tiempo_ms` es de tipo `int`» (`int` es la abreviatura de *integer*, entero, el tipo de los números sin decimales), y a continuación le asigna `"rápido"`, que es un texto. Un lenguaje de tipado estático rechazaría el programa. Python **lo ejecuta sin quejarse** y muestra `rápido`. La anotación quedó escrita, pero nadie la comparó con el valor.

Esta es la parte de la lección que más conviene recordar: **las anotaciones de tipo no se imponen al ejecutar**. La especificación que las creó, [PEP 484](https://peps.python.org/pep-0484/), lo dice sin rodeos: *Python sigue siendo un lenguaje de tipado dinámico, y los autores no tienen ninguna intención de hacer obligatorios los tipos, ni siquiera por convención*. Entonces, ¿para qué se escriben?

- **Para que las **lean** las personas.** Una anotación documenta qué clase de dato se espera en cada sitio, y a diferencia de un comentario, tiene un formato que no se pudre fácil.
- **Para que las **use** el editor.** Muchos editores muestran sugerencias y avisan de contradicciones al escribir.
- **Para que las **revise** una herramienta aparte.** Existen programas llamados verificadores de tipos, el más conocido `mypy`, que leen tu código **sin ejecutarlo** y reportan que `tiempo_ms: int = "rápido"` es una contradicción. Se enseñan en la [Lección 8](08-pruebas-tipos-calidad.md). La [documentación de `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) explica que su revisión es **gradual**: revisa las partes anotadas y deja pasar las que no lo están.
- **Para que otras piezas del lenguaje las aprovechen.** En la [Lección 5](05-modelo-de-datos.md) usarás `dataclass`, una herramienta que lee las anotaciones para construir cosas; ahí cumplen una función real, aunque sigan sin validar valores.

Dicho de otro modo, en Python **hay dos revisores distintos**: el intérprete (revisa al ejecutar, de manera fuerte pero tarde) y el verificador de tipos (revisa antes de ejecutar, pero solo si lo corres y solo lo que anotaste). El intérprete nunca consulta las anotaciones para decidir si algo es válido. Si vienes del curso de [TypeScript](https://www.habil.mx/es/cursos/typescript/) de esta casa, el principio es el mismo que allá: los tipos escritos son una promesa que una herramienta puede comprobar, no una barrera que el programa levante al correr.

Y hay un límite que ninguna anotación cruza: **los datos que vienen de fuera**. Si tu programa lee un archivo de configuración y en él alguien escribe `"timeout_ms": "rápido"`, no importa lo que hayas anotado en tu código: el texto llegará tal cual. Esos datos hay que **validarlos** al entrar, con código que los compare de verdad, y eso se hace en la [Lección 6](06-errores-archivos-datos.md). La anotación es una promesa entre las partes de tu programa; la validación es lo que protege de lo que el programa no controla.

Un último dato de actualidad, sin consecuencias para ti: en Python 3.14 cambió *cuándo* se evalúan las anotaciones (dejan de evaluarse en el momento de definirlas), según la [lista de novedades de la versión](https://docs.python.org/3/whatsnew/3.14.html). Para escribir código que corra igual en 3.12 y en 3.14, este curso evita depender de ese cambio, y lo avisa cuando haga falta.

### 0.3 El GIL, dicho sin miedo

Tarde o temprano alguien te dirá «Python no puede hacer cosas en paralelo por culpa del GIL». La frase asusta y simplifica demasiado. Vamos por partes.

Primero, dos palabras. Un **hilo** (*thread*) es una línea de ejecución dentro de un programa: un programa puede tener varios, y en principio cada uno puede avanzar mientras otros esperan. Y un **procesador** moderno tiene varios núcleos, que pueden ejecutar instrucciones en el mismo instante. Aprovechar varios núcleos con varios hilos es lo que se llama **paralelismo**.

El **GIL** (*Global Interpreter Lock*, «cerrojo global del intérprete») es una regla de CPython. La [documentación lo define](https://docs.python.org/3/glossary.html#term-global-interpreter-lock) así: es el mecanismo que asegura que **solo un hilo ejecute *bytecode* de Python a la vez**. Existe porque simplifica el diseño del intérprete: las estructuras internas, como los diccionarios, quedan protegidas de que dos hilos las modifiquen al mismo tiempo. El precio, dice la misma definición, es que se pierde buena parte del paralelismo de las máquinas con varios procesadores.

Traducido a la práctica, el GIL afecta de forma distinta a dos clases de trabajo:

- **Trabajo de cálculo** (convertir mil imágenes, comprimir un archivo grande): con hilos de Python, no se reparte entre núcleos; un solo hilo calcula a la vez. Aquí el GIL estorba.
- **Trabajo de espera** (preguntar a una red, leer un archivo, esperar la respuesta de una base de datos): el hilo que espera suelta el cerrojo mientras no está ejecutando Python, y otro puede avanzar. Aquí el GIL casi no estorba. La [documentación del módulo `threading`](https://docs.python.org/3/library/threading.html) lo dice así: los hilos siguen siendo un buen modelo cuando se quiere ejecutar varias tareas de **entrada/salida** al mismo tiempo.

El `revisor` es del segundo tipo, **casi por completo**. Su trabajo es esperar respuestas de la red, no calcular. Y además, no usará hilos: resolverá «preguntar a todos a la vez» con **`asyncio`**, que corre en un solo hilo y alterna entre tareas cada vez que una se pone a esperar. En ese esquema el GIL ni siquiera entra en la conversación. Puedes olvidarte de él mientras usas este curso, pero no del dato: saber que existe te permite no creer, ni repetir, la frase exagerada.

¿Y si algún día quisieras cálculo en paralelo? Hoy existen dos caminos que este curso no recorre: usar varios **procesos** (cada uno con su propio intérprete y su propio GIL) y, desde hace poco, una variante de CPython **sin GIL**. La historia de esa variante, resumida: [PEP 703](https://peps.python.org/pep-0703/) propuso hacer el GIL opcional y apareció como experimento en 3.13; [PEP 779](https://peps.python.org/pep-0779/) la declaró oficialmente **soportada** a partir de 3.14, pero **no es la opción por defecto**: es un ejecutable aparte, con un costo en velocidad cuando se usa un solo hilo, y muchas bibliotecas aún se están adaptando. Es lo que en este curso se llama «lo que viene»: se menciona, no se usa y no se recomienda para producción de entrada.

### 0.4 El entorno virtual y las versiones

#### 0.4.1 El problema que resuelve un entorno virtual

Piensa en tu cocina. Tienes una despensa de la casa, donde viven las cosas que toda la familia usa: sal, aceite, arroz. Si tú, para un experimento, empiezas a guardar ahí frascos raros, a cambiar el arroz por otro tipo o a quitar el aceite, estorbas a los demás y alguien un día no podrá cocinar. Lo sensato es tener tu **estante propio** para tus experimentos.

El Python que trae tu Linux Mint es la despensa de la casa. El sistema operativo lo usa para sus propias herramientas, y depende de que sus bibliotecas estén en una versión determinada. Si instalas ahí paquetes tuyos, o cambias alguno, corres el riesgo de romper algo del sistema. Y hay un segundo problema, independiente del primero: **dos proyectos tuyos pueden necesitar versiones diferentes de la misma biblioteca**. Si todos los paquetes viven en un solo lugar, uno de los dos proyectos pierde.

La solución se llama **entorno virtual** (*virtual environment*, *venv*): una carpeta con su propio Python (en Linux, un acceso directo al Python con el que se creó, no una copia; la Lección 1 lo muestra) y su propio espacio para paquetes, aislada del resto. La [documentación oficial](https://docs.python.org/3/glossary.html#term-virtual-environment) lo define como un entorno de ejecución «cooperativamente aislado» que permite instalar y actualizar paquetes «sin interferir con otras aplicaciones de Python» del mismo sistema. Lo que instalas dentro de un entorno vive solo ahí; si algo sale mal, borras la carpeta del entorno y lo recreas, y el sistema ni se entera.

Las distribuciones de Linux han tomado esto en serio. Desde que existe la especificación [PEP 668](https://peps.python.org/pep-0668/), una distribución puede marcar su Python como **«administrado externamente»**: significa que ese Python pertenece al gestor de paquetes del sistema y que `pip` (la herramienta de Python para instalar paquetes) debe negarse a instalar nada en él fuera de un entorno virtual. En tu Linux Mint la protección es todavía más directa: su Python ni siquiera trae `pip`. Verás el rechazo con tus propios ojos, y aprenderás a leer las dos formas que toma, en la Lección 1. Por ahora basta saber que **no es un fallo de tu instalación**: es una protección, y la salida correcta es el entorno virtual.

#### 0.4.2 Las versiones, y por qué dos

Las versiones de Python tienen tres números: `3.14.8` se lee mayor, menor y parche. El primero (3) lleva años sin cambiar. El segundo (14) cambia **una vez al año, en octubre**, e introduce novedades. El tercero (8) son correcciones de errores que no cambian lo que el lenguaje permite. Cuando se dice «Python 3.12» se habla de una línea de versiones, y el parche puede ser cualquiera.

Hay tres hechos que sostienen las decisiones del curso, todos medidos en la fecha en que se escribió esta lección (7 de octubre de 2026):

- **La versión estable vigente es la 3.14.** Salió el 7 de octubre de 2025, y la [página oficial de descargas](https://www.python.org/downloads/) mostraba como última la 3.14.8, del 30 de septiembre de 2026. La 3.15 estaba programada para octubre de este año según la [guía de desarrolladores](https://devguide.python.org/versions/) y aparecía todavía en estado de prelanzamiento.
- **Linux Mint 22.x trae Python 3.12.** Mint 22 y sus actualizaciones (22.1, 22.2, 22.3) están construidas sobre la base de Ubuntu 24.04, con [soporte hasta abril de 2029](https://linuxmint.com/download_all.php), y esa base es la que decide el Python que viene instalado: la línea 3.12.
- **La 3.12 sigue recibiendo correcciones de seguridad hasta octubre de 2028**, según la misma guía de desarrolladores. En cambio, la 3.10 llegó a su fin de vida el 1 de octubre de 2026: quien siga en ella ya no recibe ni arreglos de seguridad.

De ahí la decisión: **el curso se enseña con Python 3.14 y todo su código corre también en 3.12**, el que trae tu Mint. Cada programa de las lecciones se ejecuta con las dos versiones y su resultado se compara con el que ves en el texto. Eso tiene un costo, que es no usar un puñado de novedades que solo existen en 3.14, y una ventaja decisiva: **no tienes que instalar nada especial** para seguir el curso, ni dejar de usar el Python de tu sistema. Si algún día quieres probar la 3.14, la Lección 7 te cuenta una forma cómoda de instalarla.

Por eso, cuando aparezca el comando `python3`, lo que corre en tu Mint es la 3.12, y es correcto. Una última advertencia que te evitará una tarde: en muchos sistemas el comando `python` (sin el 3) no existe, o apunta a otra cosa. Al terminar de leer esta lección sabes la regla del curso: **fuera de un entorno virtual se escribe `python3`; dentro del entorno, `python` apunta al Python del entorno** (la Lección 1 lo comprueba con `which`).

## El error que vas a ver

El único error de esta lección es el de la figura 2, y conviene leerlo entero porque todos los informes de error de Python tienen la misma forma. Aquí está de nuevo, con el nombre de cada línea; no hace falta volver a ejecutarlo.

La primera línea del informe es `Traceback (most recent call last):`, que se traduce «rastro, la llamada más reciente al final». Es una señal de que lo que sigue es una lista de lugares, ordenada de **el más antiguo al más reciente**, y de que lo que ocurrió está **al final**. Por eso la regla de oro para leer un informe de error en Python es **empezar por la última línea y subir**.

La última línea es `TypeError: can only concatenate str (not "int") to str`. Contiene la **clase** del error (`TypeError`) y su **mensaje**. `TypeError` quiere decir que una operación recibió un valor de un tipo que no admite. El mensaje dice exactamente cuál: se quiso pegar (`concatenate`) un `str` con algo que no era `str`, sino un `int`. Con eso solo ya sabes qué pasó y por qué.

Subiendo una línea encuentras el dibujo del error: `print("142" + 1)` en la línea de código, y debajo una marca de virgulillas y un acento circunflejo (`~~~~~~^~~`). Esa marca señala **qué parte exacta** de la línea falló: el `+` que une `"142"` con `1`. Es una ayuda que las versiones recientes añaden, y te ahorra adivinar en una línea larga.

Sube otra línea: `File "fig00_02.py", line 2, in <module>`. Te dice **en qué archivo**, **en qué número de línea** y **dentro de qué**. La palabra `<module>` significa «a nivel del archivo, no dentro de una función»; cuando conozcas las funciones (Lección 3), aquí verás el nombre de la función en lugar de `<module>`. La línea es la 2 porque la 1 es el comentario con el nombre de la figura.

El arreglo no es convertir cualquier cosa a texto para que el error se calle. Primero decide qué querías. Si querías sumar, los dos deben ser números (`142 + 1` da 143). Si querías armar un mensaje de texto, los dos deben ser texto (`"142" + "1"`), y entonces el resultado se pega, no se suma. El error te obligó a decidir qué representaba cada dato. Eso es lo que hace un buen mensaje de error.

## Lo que se hace mal

- **Creer que una anotación valida el dato.** Escribir `tiempo_ms: int` no impide que `tiempo_ms` valga `"rápido"`. Si necesitas la garantía, hace falta un verificador de tipos (mientras escribes) o una validación explícita (cuando el dato viene de fuera). La anotación sola no hace ninguna de las dos.
- **Arreglar un `TypeError` convirtiéndolo todo a texto.** Poner comillas o llamar a una función de conversión hasta que el error desaparece oculta que mezclaste dos ideas. Pregunta primero qué debería ser cada valor.
- **Decir «Python es interpretado, así que no compila».** Sí compila (a *bytecode*); lo hace por ti y en cada ejecución. Decir «sin compilar» te lleva a sorpresas, como no entender qué es un `__pycache__` ni por qué los errores de sintaxis aparecen antes de la primera línea.
- **Culpar al GIL de cualquier lentitud.** Un programa que espera a una red no es lento por el GIL: es lento porque espera, y se arregla esperando a todos a la vez. Antes de culpar al GIL, mide qué está haciendo tu programa mientras tarda.
- **Guardar `__pycache__` en el repositorio, o creer que hay que protegerlo.** Es un caché de Python, derivado de tu código, distinto en cada versión. Se deja fuera.
- **Instalar paquetes con `sudo pip` en el Python del sistema.** Es el atajo que hay que rechazar y el que lleva a romper herramientas del sistema. Cada paquete de tus proyectos vive en un entorno virtual (Lección 1). Aunque `pip` ofrece una opción para saltarse la protección de PEP 668, el curso **no** la enseña ni la usa.
- **Mezclar `python` y `python3` sin saber cuál es cuál.** Ante cualquier duda de «¿qué Python estoy usando?», la pregunta correcta es `which`, y se contesta en la próxima lección.

## Ejercicios

### Ejercicio 1 — Los datos de la tabla

Mira la tabla del `revisor` del principio. Para cada una de estas cuatro celdas di si su dato es un **número**, un **texto** o **nada** (ausencia de dato): el `142` de `catalogo`, el `catalogo` de la primera columna, el `—` del tiempo de `reportes`, y el `200` del detalle de `pagos`. Después contesta: ¿por qué sería un problema que el tiempo de `inventario` llegara al programa como el texto `"2300"` en lugar del número 2300?

### Ejercicio 2 — Predice antes de ejecutar

Sin ejecutar nada, escribe qué hace cada una de estas tres líneas: la que muestra un resultado, la que muestra otro resultado distinto y la que falla. Para la que falla, escribe la **última línea** del informe de error.

```text
print(142 + 1)
print("142" + "1")
print(142 + "1")
```

### Ejercicio 3 — La promesa que nadie vigila

Con la figura 3 delante (`tiempo_ms: int = "rápido"`), contesta con tus palabras: (a) ¿por qué el programa muestra `rápido` y no un error? (b) Si instalaras un verificador de tipos y lo corrieras sobre ese archivo, ¿qué esperarías que dijera? (c) Si el valor `"rápido"` llegara desde un archivo de configuración y no desde una línea escrita por ti, ¿le serviría de algo la anotación?

### Ejercicio 4 — Explícaselo a un compañero

Un compañero de trabajo te dice: «Python es lento porque es interpretado y no puede hacer nada en paralelo por el GIL, así que para consultar muchos servicios hay que usar otro lenguaje». Escribe tu respuesta en cuatro o cinco frases, corrigiendo con precisión lo que está incompleto o exagerado y diciendo qué hace realmente el `revisor` durante casi todo su tiempo.

## Soluciones

### Solución 1

El `142` es un **número**; `catalogo` es un **texto**; el `—` representa que **no hay dato** (el servicio no contestó, así que no hay un tiempo que medir); el `200` del detalle es el código con que contestó el servicio y, en la tabla, se muestra como texto, porque en esa columna también pueden aparecer cosas como `sin conexión` (esa columna mezcla las dos clases, y por eso el programa la tratará siempre como texto). Que el tiempo de `inventario` llegara como el texto `"2300"` sería un problema porque el `revisor` lo compara con el umbral de 1000 para decidir si el servicio está lento. Un texto no se compara de forma significativa con un número: Python, por ser fuerte, se detendría con un `TypeError` en vez de dar un veredicto equivocado.

### Solución 2

La primera línea suma dos números y muestra `143`. La segunda pega dos textos y muestra `1421`. La tercera falla, porque mezcla un número con un texto; la última línea del informe es `TypeError: unsupported operand type(s) for +: 'int' and 'str'`. El mensaje es distinto del de la figura 2 porque aquí el número está a la izquierda: Python intenta primero sumar y, como no puede, dice que el operador `+` no admite un `int` con un `str`. Lo importante es la clase (`TypeError`) y entender que la causa es la misma: se mezclaron dos tipos.

### Solución 3

(a) Porque las anotaciones no se imponen al ejecutar: Python registró la anotación `int` pero nunca la comparó con el valor asignado. (b) Que hay una contradicción: se declaró un `int` y se le asignó un texto. El verificador lee el código sin ejecutarlo y compara las anotaciones con los valores. (c) No: una anotación es una promesa entre partes de *tu* código. Un valor que llega de fuera entra tal como viene, sea cual sea su contenido, y solo una validación explícita al entrar (Lección 6) puede comprobar que realmente es un número.

### Solución 4

Una respuesta posible: «Es verdad que Python ejecuta más despacio los cálculos puros, pero un programa que consulta servicios casi no calcula: pasa su tiempo esperando respuestas de la red. El GIL impide que dos hilos ejecuten *bytecode* de Python al mismo tiempo, pero un hilo que espera suelta el cerrojo, y de todos modos el `revisor` no usa hilos sino `asyncio`, que alterna tareas en uno solo. Lo que decide cuánto tarda es esperar a todos a la vez en lugar de uno tras otro: con cuatro servicios que tardan 142, 2300 y 87 milisegundos (el cuarto no contesta), en serie suma cerca de 2.5 segundos y a la vez tarda cerca de lo que tarda el más lento, unos 2.3. Y si algún día hiciera falta cálculo pesado en paralelo, hay otros caminos, como varios procesos.»

## Cómo sé que lo logré

- [ ] Puedes enumerar de memoria los cuatro pasos entre ejecutar un archivo y ver el resultado (leer y revisar la forma, traducir a *bytecode*, ejecutar en la máquina virtual, mostrar el resultado) y decir en cuál se detecta un paréntesis sin cerrar.
- [ ] Puedes explicar para qué sirve `__pycache__`, decir por qué es seguro borrarlo y por qué no se guarda en el repositorio.
- [ ] Sabes predecir que `print(142 + 1, "142" + "1")` muestra `143 1421`, y que `print("142" + 1)` termina en `TypeError`; y puedes explicar la diferencia entre «dinámico» y «fuerte» con esos dos ejemplos.
- [ ] Puedes decir, sin mirar la lección, por qué `tiempo_ms: int = "rápido"` no da error al ejecutar y qué clase de herramienta sí avisaría.
- [ ] Puedes explicar en dos frases qué es el GIL, cuándo afecta (cálculo con hilos) y por qué no afecta al `revisor`.
- [ ] Puedes explicar con una analogía propia qué es un entorno virtual y por qué Linux Mint rechaza `pip install` en su Python del sistema.
- [ ] Puedes decir qué versión de Python trae Mint 22.x, cuál es la vigente a la fecha de la lección, y por qué el curso se enseña con una y corre en las dos.

## Resumen

Responde sin mirar la lección:

1. ¿Qué dos cosas significa la palabra «Python»? ¿Qué es CPython?
2. ¿Qué es el *bytecode* y dónde se guarda? ¿Por qué un `.pyc` de 3.12 no sirve en 3.14?
3. ¿Qué diferencia hay entre tipado dinámico y tipado fuerte? ¿Qué sale de combinarlos?
4. ¿Quién revisa las anotaciones de tipo, y quién no las revisa?
5. ¿Qué es el GIL? ¿En qué tipo de trabajo estorba y en cuál casi no?
6. ¿Qué problema resuelve un entorno virtual? ¿Por qué Mint no deja que `pip` instale en su Python del sistema?
7. ¿Por qué el curso se enseña con 3.14 y corre también en 3.12?

## Para leer más

- [Glosario de Python](https://docs.python.org/3/glossary.html) — las definiciones oficiales de *bytecode*, interpretado, GIL, entorno virtual y sugerencia de tipo que se citan en la lección. En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [PEP 484, «Type Hints»](https://peps.python.org/pep-0484/) — el documento que introdujo las anotaciones de tipo y dice que no se imponen al ejecutar. Consultado el 7 de octubre de 2026.
- [PEP 668, «Marking Python base environments as externally managed»](https://peps.python.org/pep-0668/) — el origen del aviso `externally-managed-environment` que la próxima lección te enseña a reconocer. Consultado el 7 de octubre de 2026.
- [Guía de desarrolladores: estado de las versiones de Python](https://devguide.python.org/versions/) — qué versión está vigente, cuál recibe seguridad y cuándo termina cada una. Consultado el 7 de octubre de 2026.
