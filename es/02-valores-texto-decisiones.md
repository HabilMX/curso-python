# Lección 2 — Valores, texto y decisiones

**Tiempo:** 90 min

**Qué construyes:** el encabezado del `revisor` y la clasificación de **un** servicio: su estado, su tiempo y su detalle, impresos en un renglón de tabla

**Qué aprendes:** tres conceptos. Primero, los valores y los nombres (números, texto, verdadero o falso, y `None`); segundo, el texto con formato (las f-strings); tercero, las decisiones con `if`, `elif` y `else`, y la indentación como parte de la sintaxis

**De dónde vienes.** Traes la [Lección 1](01-instalacion.md): tienes la carpeta `~/curso-python/` con su entorno virtual `.venv`, el entorno activo (el *prompt* muestra `(.venv)`) y, dentro de `~/curso-python/revisor/`, un archivo `revisor.py` de una sola línea que imprime «revisor: todavía no revisa nada». Eso es todo lo que hace tu programa hasta hoy: no revisa nada. En esta lección empieza a hacerlo, para un servicio. Todos los comandos se escriben como si estuvieras parado en `~/curso-python/revisor/`, y el programa se corre con `python archivo.py`. Guarda cada figura de la lección con el nombre que trae en su primera línea (`fig02_01.py`, `fig02_02.py`, y así), en esa misma carpeta.

**Qué no hace esta lección.** No hay todavía listas, ni funciones, ni repeticiones. El `revisor` de hoy sabe de **un** solo servicio, guardado en unas cuantas variables, y lo clasifica una vez. Revisar los cuatro a la vez, y repetir el mismo código sin copiarlo, es el tema de la [Lección 3](03-bucles-funciones-modulos.md). Hoy se resuelve primero lo más pequeño: **qué es un dato, cómo se escribe un renglón de la tabla y cómo decide el programa si un servicio está arriba, lento o caído**.

## Al terminar vas a poder

- Guardar un dato con un nombre y decir de qué tipo es (`int`, `float`, `str`, `bool` o `None`), con la función `type()`.
- Calcular con los operadores de aritmética y de comparación, combinar condiciones con `and`, `or` y `not`, y preguntar si un valor es `None` con `is`.
- Armar un texto con una f-string y alinear columnas con `:<12`, `:>6` y `:.1f`.
- Escribir un `if`/`elif`/`else`, explicar por qué la indentación es parte de la sintaxis y por qué el orden de las ramas cambia el resultado.
- Clasificar un servicio como ARRIBA, LENTO o CAIDO con las cuatro reglas del `revisor` e imprimir su renglón con el encabezado de la tabla.
- Leer tres errores del principiante, `SyntaxError: expected ':'`, `IndentationError` y `TypeError` al sumar texto con un número, y decir qué los causó.

## El porqué antes del cómo

Imagina que trabajas en un equipo que mantiene cuatro servicios dentro de una empresa: el catálogo de productos, el inventario, los pagos y los reportes. Un lunes por la mañana alguien pregunta lo mismo que se pregunta todos los lunes: «¿cuáles están funcionando?». Hoy lo averiguas abriendo cuatro direcciones en el navegador y mirando. El `revisor`, el proyecto que vas a construir en este curso, hace esa pregunta por ti y te responde con una tabla como ésta:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Mira la tabla con ojos de programador y verás que cada celda es **un dato de una clase distinta**. `catalogo` es un texto. `142` es una cantidad. `ARRIBA` es una de tres palabras posibles. Y el tiempo de `reportes` es... nada: ese servicio no contestó, así que no hay un tiempo que mostrar, y eso hay que poder expresarlo de alguna manera que no sea escribir un cero (un servicio que no contestó no respondió en cero milisegundos). Si un programa va a producir esta tabla, necesita tres cosas, y son las tres de esta lección:

- **Representar los datos** con la clase correcta: texto para el nombre, números para el código y el tiempo, un valor especial para «no hay dato». Es el concepto 2.1.
- **Armar el renglón**: pegar el nombre, el estado y el tiempo en columnas alineadas, y convertir 2300 milisegundos en `2.3s`. Es el concepto 2.2.
- **Decidir**: si el servicio contestó con un código de error, está CAIDO; si contestó bien pero tardó mil milisegundos o más, está LENTO; si no, está ARRIBA. Es el concepto 2.3.

Al final de la lección vas a tener un `revisor.py` de unas treinta líneas que, para el servicio `inventario`, imprime exactamente estos dos renglones:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

Son dos renglones de los cinco de la tabla, pero son los que importan: el encabezado, que ya no cambia en todo el curso, y un servicio completo, con sus tres decisiones. Cuando en la Lección 3 aprendas a repetir, los otros tres servicios saldrán con el mismo código.

Una última idea antes de empezar, porque va a servirte todo el curso. Un programa es una lista de instrucciones que Python ejecuta **una tras otra, de arriba abajo**. Cuando una instrucción falla, Python se detiene en ella y te dice cuál fue; cuando una instrucción no pide nada especial, Python pasa a la siguiente. No hay magia por debajo: si quieres saber qué hace un programa, léelo como lo lee Python, de arriba abajo y una línea a la vez. Eso es lo que vas a hacer con cada figura.

## Los conceptos

### 2.1 Valores y nombres

#### 2.1.1 Los valores y sus tipos

Un **valor** es un dato concreto: el número 2300, el texto `"inventario"`, el «sí» de «¿contestó?». Todo valor tiene un **tipo**, que es la clase de dato que es y que determina qué se puede hacer con él: con los números se suma, con los textos se pega. Python tiene muchos tipos; hoy necesitas cinco, y los cinco aparecen en el `revisor`.

- **`int`** (entero): un número sin decimales. El código de respuesta de un servicio (`200`, `503`) y el tiempo en milisegundos (`2300`) son enteros. [La documentación de Python](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) los llama «tipos numéricos»; los enteros no tienen un tamaño máximo que debas vigilar.
- **`float`** (decimal): un número con punto decimal, como `2.3`. Se llama así por «punto flotante», la manera en que las computadoras guardan los decimales. Más abajo verás una sorpresa que viene con ellos.
- **`str`** (cadena de texto, *string*): una secuencia de caracteres entre comillas, simples o dobles, como `"inventario"`. En este curso se escriben con comillas dobles. Un texto puede traer acentos y símbolos (`"sin conexión"`, `"—"`): Python 3 guarda el texto en Unicode.
- **`bool`** (booleano): solo dos valores posibles, `True` y `False`, con la primera letra en mayúscula. Es la respuesta a una pregunta de sí o no, como «¿el servicio contestó?». Lleva el nombre de George Boole, el matemático que formalizó la lógica de verdadero y falso.
- **`None`**: el valor que significa «no hay nada aquí». Es el único valor de su propio tipo, que se llama `NoneType`. Lo vas a usar para el tiempo y el código de un servicio que no contestó, y es la respuesta correcta a «¿cuánto tardó?» cuando la respuesta es «no hay respuesta».

La función `type()` te dice el tipo de cualquier valor. Y `print()` puede recibir varios valores separados por comas: los imprime en la misma línea, con un espacio entre ellos. Con las dos cosas puedes ver los cinco tipos juntos. Guarda esta figura como `fig02_01.py` y córrela:

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

Línea por línea. La primera línea, la que empieza con `#`, es un **comentario**: Python ignora todo lo que va desde un `#` hasta el final de la línea. Sirve para que las personas lean notas, y en este curso la primera línea de cada figura es un comentario con su nombre (`# fig02_01.py`), para que sepas cómo guardarla. Las siguientes seis líneas **crean variables**, que es el tema del apartado siguiente; fíjate solo en que cada una guarda un valor de un tipo distinto. `tiempo_ms / 1000` divide 2300 entre 1000 y da `2.3`, un `float`, aunque los dos números de la cuenta eran enteros: la división `/` siempre da un decimal. Después, seis `print` muestran cada valor y su tipo. La salida dice `<class 'str'>`, `<class 'int'>` y así: en Python, «tipo» y «clase» son la misma idea, y la palabra *class* en la respuesta no te obliga a saber nada más de clases por ahora (llegan en la Lección 5).

Dos cosas para fijarte. Primera: `200` y `"200"` **no son lo mismo**. El primero es un número, y con él se puede comparar y sumar; el segundo es un texto de tres caracteres que casualmente son dígitos, y con él no se puede calcular. Cuando en la tabla veas `200` en la columna DETALLE, ahí es un texto (es un trozo de un renglón que se imprime), pero en la variable `codigo` es un número. Segunda: `None` **no es** `0`, ni `""` (el texto vacío), ni `False`. Es un valor distinto, que dice «aquí no hay dato». Un servicio caído que no devolvió código no tiene «código cero»: no tiene código.

#### 2.1.2 Los nombres y la asignación

Una **variable** es un nombre que apunta a un valor. Se crea con el signo igual:

```python
tiempo_ms = 2300
```

Esa línea se llama **asignación** y se lee de derecha a izquierda: primero se calcula el valor de la derecha (2300) y después se le pone el nombre de la izquierda (`tiempo_ms`). El signo `=` **no significa «es igual a»** como en matemáticas; significa «guarda esto bajo ese nombre». La pregunta de si dos cosas son iguales se escribe con dos signos, `==`, y la verás en un momento. Confundir los dos es uno de los tropiezos más comunes del principiante, y Python te protege de la mayoría: `if codigo = 200:` es un error de sintaxis, porque dentro de un `if` solo cabe una pregunta.

Un nombre puede cambiar de valor cuando quieras: `tiempo_ms = 2300` y más abajo `tiempo_ms = 87` hacen que el nombre apunte ahora al 87. El valor anterior simplemente deja de tener nombre. Y un valor puede tener varios nombres a la vez, aunque eso solo importa de verdad cuando los valores se pueden modificar por dentro, y esa historia empieza en la Lección 4.

Las reglas para escribir un nombre son pocas:

- Lleva letras, dígitos y guion bajo (`_`), y **no puede empezar con un dígito**: `1servicio` no sirve, `servicio1` sí.
- No puede ser una **palabra reservada**, de las que Python usa para su propia sintaxis (`if`, `else`, `None`, `True`...). Verás el resto conforme las necesites.
- **Las mayúsculas cuentan**: `Nombre` y `nombre` son dos nombres distintos. Si escribes uno donde querías el otro, Python no te dirá «te equivocaste de mayúscula», te dirá que el nombre no existe.

Y además hay **convenciones**, que no son obligatorias pero que todo el mundo de Python sigue, porque están en [la guía de estilo oficial, la PEP 8](https://peps.python.org/pep-0008/#naming-conventions): los nombres de variables van en minúsculas con guion bajo entre palabras (`tiempo_ms`, que se llama *snake_case*), y los nombres de valores que **no van a cambiar** (las constantes) van en mayúsculas (`UMBRAL_LENTO_MS`). Python no impide que cambies una «constante»; la mayúscula es un aviso para quien lea el código.

Este curso agrega dos reglas propias, que verás en cada figura. **Los identificadores van en español, sin acentos ni `ñ`**: `nombre`, `tiempo_ms`, `estado`. Python acepta acentos en los nombres, pero se escriben mal en teclados ajenos y complican compartir el código. Y **las unidades van en el nombre**: `tiempo_ms`, nunca `tiempo` a secas. Cuando alguien lee `tiempo = 2300`, no sabe si son milisegundos, segundos o minutos; cuando lee `tiempo_ms = 2300`, lo sabe. Es una costumbre que evita errores caros: [la NASA atribuyó la falla de la sonda Mars Climate Orbiter a un error de navegación](https://science.nasa.gov/mission/mars-climate-orbiter/), causado por no traducir unidades inglesas a métricas entre el programa de tierra y el de la nave.

#### 2.1.3 Operadores: calcular, comparar y combinar

Un **operador** es un símbolo que hace algo con valores. Hay tres familias y las tres sirven al `revisor`.

Los de **aritmética** calculan: `+` suma, `-` resta, `*` multiplica, `/` divide y siempre devuelve un `float`, `//` divide y se queda con la parte entera, `%` da el residuo de la división y `**` eleva a una potencia. Los de **comparación** preguntan y siempre responden con un `bool`: `==` (igual), `!=` (distinto), `<`, `<=`, `>` y `>=`. Y los **lógicos** combinan preguntas: `and` es verdadero solo si las dos son verdaderas, `or` es verdadero si al menos una lo es, y `not` invierte la respuesta. Guarda `fig02_02.py`:

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

Las cinco primeras líneas de salida son aritmética: 2300 entre 1000 da `2.3`; la división entera da `2` (cuántos segundos completos caben en 2300 ms) y el residuo da `300` (los milisegundos que sobran); sumar 100 da `2400`, y `2**3` es dos al cubo, `8`. Las tres siguientes son comparaciones: 2300 sí es mayor o igual que el umbral de 1000 (`True`), el código sí es 200 (`True`) y por lo tanto no es distinto de 200 (`False`). Las últimas tres combinan: la primera dice «¿el código es de error **o** el tiempo pasó del umbral?», y como lo segundo es cierto, el `or` entero lo es; la segunda dice «¿contestó bien **y** rápido?», y como no fue rápido, es falsa; la tercera guarda en una variable la respuesta a «¿el código es menor que 400?» (`True`) y la invierte con `not`, y por eso da `False`. Observa que una comparación se puede guardar en una variable igual que un número: su valor es un `bool`.

Observa un detalle de la figura que se repetirá todo el curso: el umbral está en una variable con nombre en mayúsculas, `UMBRAL_LENTO_MS = 1000`, y las comparaciones lo usan por su nombre. Si mañana el equipo decide que un servicio es lento a partir de 800 ms, cambias **una** línea. Si hubieras escrito `1000` en cada comparación, tendrías que encontrarlas todas.

Dos precisiones sobre los operadores. La primera es la **precedencia**: igual que en matemáticas, `*` y `/` se hacen antes que `+` y `-`, y Python hace las comparaciones antes que `not`, `and` y `or`. Cuando tengas dudas, usa paréntesis. La segunda es que **`and` y `or` no evalúan lo que no necesitan**. En `A or B`, si `A` ya es verdadera, Python ni mira `B`, porque el resultado ya no puede cambiar; en `A and B`, si `A` es falsa, tampoco mira `B`. Esto se llama *evaluación de cortocircuito* y no es un detalle de erudito: dentro de unos minutos va a evitar que el `revisor` truene con el servicio `reportes`.

Un aviso sobre los decimales, que prometí. Mira esta sesión del REPL (el intérprete interactivo de la Lección 1):

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> 10 / 2
5.0
```

La primera respuesta parece un error de Python y no lo es. Las computadoras guardan los decimales en binario, y algunos decimales sencillos, como 0.1, no tienen una representación exacta en binario; se guardan aproximados, y la suma de dos aproximaciones da una aproximación ligeramente distinta del 0.3 que esperabas. [El tutorial oficial dedica un capítulo a esto](https://docs.python.org/3/tutorial/floatingpoint.html) y recuerda que no es un defecto de Python ni de tu código: es cómo funcionan los números de punto flotante en binario, la representación que usan casi todas las computadoras (y, con ellas, casi todos los lenguajes). La consecuencia práctica: **no compares con `==` el resultado de una cuenta con decimales esperando un valor exacto**. En el `revisor` esto casi no te toca, porque los tiempos son enteros (milisegundos), y por eso están en milisegundos y no en segundos con decimales. La segunda respuesta enseña otra costumbre: `10 / 2` da `5.0`, no `5`. La `/` siempre devuelve un `float`.

#### 2.1.4 `None`, `is` y las conversiones con `str()` e `int()`

Para preguntar si un valor es `None`, Python tiene un operador específico: **`is`**. Se escribe `valor is None`, y su contrario es `valor is not None`. Es la forma correcta de hacerlo, y la que usa [la guía de estilo](https://peps.python.org/pep-0008/#programming-recommendations), que pide comparar con `None` siempre con `is` o `is not`, nunca con `==`. El motivo, dicho en una frase: en todo el programa **existe un solo `None`**, así que lo que se pregunta no es «¿se parece a `None`?» sino «¿es *el* `None`?». (La diferencia completa entre `==` y `is` es el tema de la Lección 3; por ahora quédate con la regla.)

También hay dos funciones que convierten entre tipos. `str(valor)` devuelve el texto que representa a un valor: `str(503)` es `"503"`. Y `int(texto)` hace lo contrario: `int("503")` es `503`. Las vas a necesitar en dos lugares: `str(codigo)` para poner un código dentro del renglón de la tabla, y más adelante `int(...)` para convertir lo que llega de fuera, que casi siempre llega como texto. Guarda `fig02_03.py`:

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

Mientras `codigo` valía `None`, la primera pregunta da `True` y la segunda `False`. Cuando se le asigna 503, el servicio ya tiene código y la pregunta da `False`. Después, `"código: " + str(codigo)` pega dos textos con `+` (a los textos, `+` los une) y funciona **porque `str(codigo)` convirtió el número en texto antes**. Las dos últimas líneas confirman que `str(503)` es un `str` y que `int("503")` es un `int`. Guarda esta idea: Python no convierte entre tipos por ti. Si intentas pegar un texto con un número, te lo reclama, y esa queja es uno de los errores de la sección «El error que vas a ver».

### 2.2 Texto con formato: las f-strings

#### 2.2.1 Por qué no pegar con `+`

Hay que armar un renglón de la tabla: el nombre, el estado, el tiempo y el detalle, en columnas alineadas. Con lo que ya sabes, la manera sería pegar textos con `+`, convirtiendo cada número con `str()`, y calcular a mano cuántos espacios faltan para completar cada columna. Se puede, y sale ilegible y frágil: cada pieza nueva es otro `+` y otro `str()`, y cambiar el ancho de una columna obliga a recontar espacios.

Python tiene una herramienta pensada para esto: las **f-strings** (*formatted string literals*). Una f-string es un texto que empieza con la letra `f` antes de las comillas, y que acepta **expresiones entre llaves**: Python calcula lo que hay dentro de cada par de llaves y mete el resultado en el texto. Se explican en [la referencia del lenguaje](https://docs.python.org/3/reference/lexical_analysis.html#f-strings). Existen otras dos formas más antiguas de formatear texto, el operador `%` y el método `.format()`. Las vas a encontrar en código viejo, así que conviene reconocerlas, pero este curso no las usa y no necesitas aprenderlas: las f-strings hacen todo lo que ellas hacen y se leen mejor.

#### 2.2.2 Meter valores y cuentas en el texto

Lo más simple es poner un nombre entre llaves: `f"{nombre} respondió"`. Pero lo que va entre llaves puede ser cualquier expresión, incluso una cuenta: `f"{tiempo_ms * 2}"` calcula el doble y lo inserta. Esto elimina por completo el `str()` de la sección anterior: la f-string convierte a texto lo que insertas, sin que se lo pidas.

#### 2.2.3 La especificación de formato: ancho, alineación y decimales

Después de la expresión, y separada por dos puntos, se puede escribir una **especificación de formato** que le dice a Python cómo mostrar el valor. Hoy necesitas tres, y [el lenguaje de formato completo está en la documentación](https://docs.python.org/3/library/string.html#format-specification-mini-language):

- **`:<12`**: ocupa **12 caracteres** y alinea el valor a la **izquierda** (`<`), rellenando con espacios a la derecha.
- **`:>6`**: ocupa **6 caracteres** y alinea el valor a la **derecha** (`>`), rellenando a la izquierda.
- **`:.1f`**: muestra un número **decimal con un dígito** después del punto (`f` de *fixed*, punto fijo).

Guarda `fig02_04.py`. Las llaves se rodean con corchetes en la salida para que veas dónde empieza y termina cada campo:

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

Las tres primeras líneas ya no necesitan explicación: el nombre y el tiempo se insertan tal cual, la cuenta se calcula y se inserta, y `2300 / 1000` sale como `2.3`. Las siguientes enseñan el ancho: `inventario` tiene diez caracteres, y con `:<12` queda con dos espacios después (mira dónde cae el corchete de cierre); con `:>12`, los dos espacios van antes. Con `{87:>6}` el 87 ocupa seis posiciones, alineado a la derecha, y por eso hay cuatro espacios antes. Las dos últimas muestran `.1f`: `2.3` ya tenía un decimal, y `1000 / 1000`, que es `1.0`, mantiene su `.0` (Python lo redondea al número de decimales pedido, no los quita).

Esto es lo que necesitas para armar un renglón de la tabla. La plantilla del `revisor`, que no cambiará en todo el curso, es:

```text
f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

Léela de izquierda a derecha: el nombre del servicio en 12 columnas, alineado a la izquierda; el estado en 10, a la izquierda; el tiempo en 6, a la derecha (los números se alinean mejor por la derecha, para que las unidades queden una debajo de otra); dos espacios fijos, y el detalle, que va al final y no necesita ancho. Y el encabezado de la tabla usa **la misma plantilla**, con los títulos en lugar de los datos. Un detalle de escritura: el encabezado va entre comillas dobles y, dentro de las llaves, los títulos llevan comillas simples (`{'SERVICIO':<12}`). Desde Python 3.12 podrías repetir las dobles dentro de las llaves y funcionaría (lo permitió la [PEP 701](https://peps.python.org/pep-0701/)), pero alternarlas se lee mejor, porque a simple vista se distingue dónde termina la f-string y dónde empieza el texto de dentro, y además funciona en versiones anteriores de Python.

### 2.3 Decisiones: `if`, `elif`, `else` y la indentación

#### 2.3.1 Una pregunta y un bloque

Un programa que siempre hace lo mismo no sirve para revisar servicios. Necesita **decidir**: si pasa tal cosa, hacer esto; si no, aquello. En Python la decisión se escribe con `if`:

```text
if <pregunta>:
    <lo que se hace si la respuesta es verdadera>
```

La pregunta es cualquier expresión que dé un `bool`, como las de la sección anterior. Después de la pregunta va un signo de **dos puntos** (`:`), que le dice a Python «aquí empieza lo que depende de la pregunta». Y lo que depende de ella va en las líneas siguientes, **corrido hacia la derecha**. A ese conjunto de líneas se le llama un **bloque**.

Aquí viene una característica de Python que lo distingue de la mayoría de los lenguajes y que a veces sorprende al principiante: **la indentación es parte de la sintaxis**. En otros lenguajes los bloques se delimitan con llaves o con palabras como `begin` y `end`, y la sangría es una cuestión de estilo. En Python **la sangría es la que dice dónde empieza y dónde termina el bloque**. Las líneas que están corridas la misma cantidad pertenecen al mismo bloque; cuando una línea vuelve al margen izquierdo, el bloque terminó. [La referencia del lenguaje lo define con precisión](https://docs.python.org/3/reference/lexical_analysis.html#indentation), y la regla práctica de la PEP 8 es: **cuatro espacios por nivel**, y nunca mezclar tabuladores con espacios. Configura tu editor para que la tecla Tab inserte cuatro espacios, y no vuelvas a pensar en ello.

Guarda `fig02_05.py`:

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

Con `codigo = 503`, la pregunta `codigo >= 400` es verdadera y se ejecuta el primer bloque. El `else` (en español, «si no») es la rama que se ejecuta cuando la respuesta es falsa; no lleva pregunta, pero sí sus dos puntos. Fíjate en la última línea: está **al margen izquierdo**, fuera de los dos bloques, y por eso se ejecuta siempre, sea cual sea el código. Prueba a cambiar `codigo` a `200` y comprueba que cambia la primera línea de la salida, pero la última no. Si alguna vez una línea se ejecuta «cuando no debía» (o no se ejecuta cuando sí), mira primero su sangría: en Python, ahí empieza el 80 % de esas sorpresas.

#### 2.3.2 `elif`: varias preguntas en cadena

Un servicio no tiene dos estados sino tres, y las decisiones del `revisor` son encadenadas: primero se pregunta si está caído; si no, se pregunta si está lento; y si tampoco, está arriba. Para eso existe `elif`, contracción de *else if*, «si no, y si...». Una cadena `if`/`elif`/`else` funciona así: **Python evalúa las preguntas de arriba abajo, ejecuta el bloque de la primera que sea verdadera y se salta todas las demás**. Si ninguna lo es, ejecuta el `else`, si lo hay. De una cadena siempre se ejecuta, como máximo, un bloque.

Las reglas del `revisor` para clasificar un servicio, que son las mismas desde esta lección hasta la última, son cuatro:

1. Si **no hubo código** (no hubo respuesta), está **CAIDO**.
2. Si el código es **400 o más** (el servidor contestó, pero con error), está **CAIDO**; el detalle será el propio código, por ejemplo `503`.
3. Si contestó bien y tardó **1000 ms o más**, está **LENTO**.
4. Si no, está **ARRIBA**.

Las dos primeras tienen el mismo resultado, y se pueden juntar en una sola pregunta con `or`. Guarda `fig02_06.py`:

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

Para `inventario`, con código 200 y 2300 ms, la primera pregunta es falsa (el código existe y no llega a 400), la segunda es verdadera (2300 es mayor o igual que 1000), y el estado queda en `"LENTO"`. Prueba con otros valores: `codigo = 503` da `CAIDO`; `tiempo_ms = 142` da `ARRIBA`.

#### 2.3.3 El orden de las preguntas importa

Hay una razón por la que la pregunta del código va **primero**, y es la misma que se prometió con el cortocircuito. Piensa en `reportes`: no contestó, así que su `codigo` es `None` y su `tiempo_ms` también. Con la cadena de arriba, la primera pregunta (`codigo is None or ...`) es verdadera en cuanto Python mira el `is None`, y **ya no evalúa** la segunda mitad del `or`, que habría fallado: `None >= 400` no tiene sentido. Y como la primera rama se cumplió, tampoco se evalúa el `elif`, que preguntaría `None >= 1000`. El servicio queda CAIDO sin que Python compare un `None` con un número.

Si pones las preguntas en otro orden, la cadena deja de ser segura. Ese error es uno de los de «Lo que se hace mal», y vale la pena provocarlo en el Ejercicio 4. La regla de fondo: **en una cadena de `elif`, ordena las preguntas de la más específica o más peligrosa a la más general**, de modo que cada rama pueda dar por cierto lo que las anteriores descartaron. En el `elif`, ya sabes que el servicio contestó y con un código menor a 400, así que `tiempo_ms` tiene un valor.

#### 2.3.4 Todo junto: el renglón de un servicio

Ya tienes todo lo necesario. Falta calcular las otras dos columnas con el mismo mecanismo. El **tiempo** es un texto que depende del valor: si no hubo tiempo, una raya (`"—"`); si fue menos de un segundo, milisegundos pegados a la unidad (`"142ms"`); si fue un segundo o más, segundos con un decimal (`"2.3s"`). Observa que el 1000 de aquí **no es el umbral de lento**: es la cantidad de milisegundos que hay en un segundo. Se parecen en el valor y significan cosas distintas, y por eso el primero tiene nombre (el umbral puede cambiar) y el segundo no (un segundo siempre tiene mil milisegundos). Y el **detalle** es el código convertido en texto, o `"sin conexión"` si no hubo código.

Esta es la figura de la lección, tu nuevo `revisor.py`. Guárdala con el nombre `fig02_07.py` para compararla y también como `revisor.py`, que reemplaza a la línea de la Lección 1:

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

Léela como la lee Python. Las primeras cinco líneas guardan los datos de un servicio; `url` es la dirección del servicio y todavía no se imprime, pero el proyecto ya la lleva, igual que el dominio `.example`, que es un nombre reservado que nunca llega a ninguna página real (ningún programa de este curso toca internet hasta la Lección 9). El primer bloque `if` calcula `estado` con las reglas de arriba. El segundo calcula `tiempo`, el texto de la columna: si `tiempo_ms is None` pone la raya, si es menor que 1000 pega `ms` al número y si no lo convierte a segundos con un decimal. El tercero calcula `detalle`. Las dos últimas líneas imprimen el encabezado y el renglón con la plantilla de la sección 2.2: el mismo patrón, con títulos en el primero y con las variables en el segundo.

Cambia las cinco variables por las de otro servicio y corre el programa otra vez: no hace falta tocar nada más. De eso se trata el Ejercicio 1, y de ahí viene la siguiente lección: copiar y pegar ese bloque para cada servicio sería absurdo, y Python tiene herramientas para no hacerlo.

## El error que vas a ver

En esta sección vas a provocar a propósito los tres errores que el principiante ve primero. Los tres están copiados de una corrida real. Cuando el programa falla, Python imprime un informe del error que se llama ***traceback***, y la regla, desde la Lección 1, es la misma: **se lee de la última línea hacia arriba**. La última línea dice qué pasó; las de arriba dicen dónde. Las rutas completas de los archivos que verás en tu pantalla serán distintas de las que muestra este texto (aquí se abrevian al nombre del archivo).

### `TypeError: can only concatenate str (not "int") to str`

Guarda `fig02_08.py`, que intenta pegar un texto con un número:

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

La última línea dice: un `TypeError` (un error de tipo) con el mensaje «solo se puede concatenar `str` (no `int`) a `str`». Concatenar es pegar. El `+` entre dos textos los pega, pero aquí el segundo era un número, y Python no sabe cómo pegar un texto con un número: no va a adivinar si querías «2300» o un cálculo. Las líneas de arriba te dicen **dónde**: `line 4`, y debajo la línea del programa con unas marcas que señalan la operación que falló. La corrección es hacer la conversión tú, con `str(tiempo_ms)`, o mejor, no pegar nada: `print(f"respondió en {tiempo_ms}")`. [La documentación de `TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) lo describe como «una operación o función aplicada a un objeto de un tipo inapropiado», que es exactamente esto.

### `SyntaxError: expected ':'`

Guarda `fig02_09.py`, un `if` al que se le olvidaron los dos puntos:

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

Un `SyntaxError` es un error de **sintaxis**: Python ni siquiera empezó a ejecutar el programa, porque lo leyó completo antes y encontró algo que no es Python válido. Por eso la salida **no** dice `Traceback`: no hay un recorrido de ejecución que mostrar, solo el lugar del problema. El mensaje, `expected ':'`, dice qué esperaba: dos puntos. La flecha de abajo (`^`) señala el lugar donde se dio cuenta, el final de la línea del `if`. Cuando veas un `SyntaxError`, mira la línea indicada y también la **anterior**, porque a veces el olvido está antes (un paréntesis sin cerrar, por ejemplo, hace fallar a la línea siguiente).

### `IndentationError: expected an indented block after 'if' statement on line 3`

Guarda `fig02_10.py`: ahora los dos puntos están, pero la línea de abajo se quedó en el margen:

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

`IndentationError` es una variante de `SyntaxError` para los problemas de sangría. El mensaje es literal: después de un `if` (el de la línea 3) se esperaba un bloque con sangría, y la línea 4 no la tiene. Los dos puntos al final del `if` prometían un bloque, y Python lo exige. Es el recordatorio de la sección 2.3: **los dos puntos y la sangría van juntos**. La corrección es meter `print("CAIDO")` cuatro espacios hacia la derecha.

## Lo que se hace mal

**Poner las preguntas en el orden equivocado.** Es el error más traicionero de esta lección, porque se ve razonable y falla justo con el servicio que más importa. Guarda `fig02_11.py`, donde la pregunta del tiempo va antes que la del código:

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

El mensaje, `'>=' not supported between instances of 'NoneType' and 'int'`, dice: el operador `>=` no está definido entre un `NoneType` (el `None`) y un `int` (el 1000). Con servicios que contestaron, el programa funciona y no te enteras; con `reportes`, que no contestó, truena. Costo: un `revisor` que se cae justo cuando un servicio está caído, que es cuando más lo necesitas. La cura es la regla de la sección 2.3: primero la rama que descarta los datos que faltan.

**Escribir `=` donde va `==`.** `if codigo = 200:` es un `SyntaxError`, y el mensaje de Python lo adivina: *invalid syntax. Maybe you meant '==' or ':=' instead of '='?* La asignación guarda; la comparación pregunta. No se pueden intercambiar.

**Comparar con `None` usando `==`.** Funciona en los casos simples y es lo que advierte [la PEP 8](https://peps.python.org/pep-0008/#programming-recommendations): con `None` se usa siempre `is` o `is not`. Las herramientas de revisión que conocerás en la Lección 8 también lo señalan.

**Guardar un número como texto.** `codigo = "200"` parece lo mismo que `codigo = 200`, y ya no lo es: `"200" >= 400` truena con otro `TypeError`, y `"200" + "1"` da `"2001"`. Lo que es una cantidad se guarda como número, sin comillas.

**Representar «no respondió» con `0` o con un texto.** `tiempo_ms = 0` dice «contestó en cero milisegundos», que es la respuesta más rápida posible, justo la contraria de la verdad; y un texto como `"sin respuesta"` no se puede comparar con 1000. Un dato que falta se guarda como `None`, y el programa decide qué hacer con él.

**Escribir `tiempo` a secas.** Una variable llamada `tiempo` no dice si son segundos o milisegundos. Pon la unidad en el nombre, y cuando un número sea una cantidad con unidad, que el nombre la cargue.

**Escribir el mismo número en tres lugares.** Si el umbral de lento está escrito como `1000` en cada comparación y mañana cambia a 800, olvidarás una. Se nombra una vez (`UMBRAL_LENTO_MS`) y se usa por su nombre.

**Mezclar tabuladores y espacios.** Python 3 se niega a ejecutar un bloque cuya sangría mezcla los dos de manera inconsistente, con un `TabError: inconsistent use of tabs and spaces in indentation`. Tu editor puede hacerlo sin avisarte; configúralo para que Tab inserte cuatro espacios.

## Ejercicios

### Ejercicio 1 — Los otros tres servicios y uno extra

Cambia las cinco variables de tu `revisor.py` por las de cada uno de los otros tres servicios, y **antes de correr cada vez, escribe en un papel el renglón que esperas**:

| nombre | url | código | tiempo_ms |
|---|---|---|---|
| `catalogo` | `https://catalogo.example` | 200 | 142 |
| `pagos` | `https://pagos.example` | 200 | 87 |
| `reportes` | `https://reportes.example` | `None` | `None` |

Después prueba con `facturacion` (`https://facturacion.example`), que contesta con el código 503 en 95 ms. ¿Coincidió tu predicción en los cuatro? Si no, ¿qué parte de las reglas aplicaste distinto?

### Ejercicio 2 — Mover el umbral

Con el servicio `catalogo` (200, 142 ms), cambia `UMBRAL_LENTO_MS` a 100 y predice el estado. Luego déjalo en 2500 y predice el estado de `inventario` (200, 2300 ms). Explica en una frase por qué cambiar **una sola línea** cambió el resultado en los dos casos.

### Ejercicio 3 — Provocar los tres errores

En una copia de tu programa, provoca uno por uno estos tres errores y copia el mensaje exacto de la última línea: (a) quita los dos puntos de un `elif`; (b) quita la sangría de la línea que sigue al `else`; (c) cambia el `str(codigo)` de `detalle` por `"código " + codigo`. Para cada uno, escribe qué significa el mensaje y cuál es la corrección.

### Ejercicio 4 — Lo mismo al revés, y cómo salvarlo

Parte de `fig02_11.py` (el de las preguntas en mal orden, que truena con `None`). Sin cambiar el orden de las dos primeras ramas, arregla la **primera pregunta** para que ya no truene con `reportes`. Pista: hay que preguntar primero que `tiempo_ms` exista y luego compararlo, y el operador que une dos preguntas obligando a que se cumplan las dos es `and`. Después explica por qué esta solución funciona gracias al cortocircuito.

## Soluciones

### Solución 1

Las predicciones correctas, y lo que imprime el programa con cada servicio (el encabezado es el mismo de siempre):

```text
catalogo    ARRIBA     142ms  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
```

El de `facturacion` es el que más se falla. Con el código 503, la primera pregunta (`codigo >= 400`) es verdadera, así que el estado es CAIDO **aunque haya contestado en 95 ms**, que sería rapidísimo. El tiempo se sigue mostrando (`95ms`) porque existe, y el detalle es el código, `503`. Además, `facturacion` tiene once letras y cabe en las doce columnas del nombre, pero casi sin margen: por eso su renglón queda pegado al estado.

### Solución 2

Con `UMBRAL_LENTO_MS = 100`, el estado de `catalogo` (142 ms) pasa de ARRIBA a **LENTO**: 142 ya es mayor o igual que 100. Con el umbral en 2500, `inventario` (2300 ms) pasa de LENTO a **ARRIBA**: 2300 ya no llega a 2500. En los dos casos cambió el resultado porque el umbral se escribió una sola vez y todas las comparaciones lo usan por su nombre; si el 1000 estuviera repetido en cada pregunta, habría que cambiarlo en todas.

### Solución 3

(a) Sin los dos puntos del `elif`: `SyntaxError: expected ':'`. Python esperaba los dos puntos que anuncian el bloque. Corrección: ponerlos al final de la línea del `elif`.

(b) Sin sangría después del `else`: `IndentationError: expected an indented block after 'else' statement on line N`, donde `N` es el número de la línea del `else`. Corrección: cuatro espacios antes de la línea que depende del `else`.

(c) `"código " + codigo`, con `codigo` valiendo 200: `TypeError: can only concatenate str (not "int") to str`. Corrección: `"código " + str(codigo)` o, mejor, una f-string: `f"código {codigo}"`.

### Solución 4

La primera pregunta pasa a ser `tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS`:

```python
if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"
```

Funciona por el cortocircuito: con `tiempo_ms = None`, la primera mitad (`tiempo_ms is not None`) es falsa, y como un `and` con una mitad falsa ya no puede ser verdadero, Python **no evalúa** la segunda mitad, que era la que tronaba. Pero ojo: esta versión es peor que la original en un caso. Con `codigo = 503` y `tiempo_ms = 2300`, un servicio que respondió **lento y con error** quedaría LENTO en lugar de CAIDO, porque la rama del tiempo gana a la del código. Arreglar el síntoma sin ordenar las ramas cambió las reglas sin querer. Es la mejor razón para dejar la pregunta del código primero.

## Cómo sé que lo logré

- [ ] `python revisor.py` imprime exactamente dos líneas: `SERVICIO    ESTADO    TIEMPO  DETALLE` y `inventario  LENTO       2.3s  200`, con las columnas alineadas como en la figura `fig02_07.py`.
- [ ] Al cambiar las variables por las de `reportes` (`codigo = None`, `tiempo_ms = None`), el programa imprime `reportes    CAIDO          —  sin conexión` y **no** termina con un *traceback*.
- [ ] Con `facturacion` (503, 95 ms) el estado es CAIDO y el detalle es `503`.
- [ ] Puedes provocar a propósito `SyntaxError: expected ':'`, `IndentationError` y `TypeError: can only concatenate str (not "int") to str`, y decir en una frase qué dice la última línea de cada uno.
- [ ] Puedes explicar con tus palabras la diferencia entre `=` y `==`, entre `200` y `"200"`, y entre `None` y `0`.
- [ ] Puedes explicar por qué la pregunta del código va antes que la del tiempo en la cadena `if`/`elif`/`else`.

## Resumen

Responde sin mirar la lección:

1. ¿Qué tipo devuelve `type()` para `142`, para `2.3`, para `"142"`, para `True` y para `None`?
2. ¿Qué hace `=` y qué hace `==`? ¿Y por qué `UMBRAL_LENTO_MS` va en mayúsculas?
3. ¿Qué da `10 / 2`, `7 // 2` y `7 % 2`? ¿Por qué `0.1 + 0.2` no da `0.3`?
4. ¿Cómo se pregunta si un valor es `None`, y por qué no se usa `==`?
5. ¿Qué significan `:<12`, `:>6` y `:.1f` dentro de una f-string?
6. En una cadena `if`/`elif`/`else`, ¿cuántos bloques se ejecutan como máximo, y cuál? ¿Qué hace la indentación?
7. ¿Qué es el cortocircuito de `or` y de `and`, y qué problema evita en el `revisor`?
8. ¿Cuál es la última línea de un `SyntaxError` por olvidar los dos puntos, y por qué ese error no muestra un *traceback*?

## Para leer más

- [El tutorial de Python, «Una introducción informal»](https://docs.python.org/3/tutorial/introduction.html) — números, texto y variables, con la sesión interactiva que reconocerás de la Lección 1. Documentación oficial. Consultado el 7 de octubre de 2026.
- [El tutorial de Python, «Más herramientas de control de flujo»](https://docs.python.org/3/tutorial/controlflow.html#if-statements) — la sección sobre `if`, `elif` y `else`. Consultado el 7 de octubre de 2026.
- [PEP 8, la guía de estilo de Python](https://peps.python.org/pep-0008/) — las convenciones de nombres, de sangría y de comparación con `None` que usa este curso. Consultado el 7 de octubre de 2026.
- [Mini-lenguaje de especificación de formato](https://docs.python.org/3/library/string.html#format-specification-mini-language) — todo lo que puede ir después de los dos puntos en una f-string; no es un texto para aprender de corrido sino para consultar. Consultado el 7 de octubre de 2026.
