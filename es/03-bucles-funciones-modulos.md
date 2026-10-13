# Lección 3 — Bucles, funciones y módulos

**Tiempo:** 2 × 90 min (dos sesiones)

**Qué construyes:** la función `revisar()` y el recorrido de la lista: un `revisor` de dos archivos que imprime el encabezado y los renglones de los cuatro servicios

**Qué aprendes:** cuatro conceptos. Primero, los bucles (`for`, `while`, `range`, `enumerate`) y la lista mínima para recorrer; segundo, las funciones (`def`, parámetros, valores por omisión, `return`, anotaciones simples y la trampa del valor por omisión que es una lista); tercero, los nombres (dónde vive cada variable, `UnboundLocalError`, y `==` contra `is`); cuarto, los módulos (`import`, `from ... import` y `if __name__ == "__main__":`)

**De dónde vienes.** Traes el `revisor.py` de la [Lección 2](02-valores-texto-decisiones.md): unas treinta líneas que guardan **un** servicio (`inventario`) en variables, lo clasifican con un `if`/`elif`/`else` y lo imprimen en un renglón alineado, bajo el encabezado de la tabla. Funciona, pero tiene un problema que ya se vio al final de aquella lección: para revisar los otros tres servicios habría que copiar el bloque tres veces y cambiar los valores de cada copia. Hoy se quita ese problema de en medio. Sigues trabajando en `~/curso-python/revisor/`, con el entorno virtual activo, y los programas se corren con `python archivo.py`.

**Cómo se reparte la lección.** Es larga, y por eso son dos sesiones de 90 minutos con un corte natural en medio. **La primera sesión** son los apartados 3.1 y 3.2 (bucles y funciones) y termina con la figura `fig03_11`, el `revisor` completo en **un** archivo. **La segunda sesión** son los apartados 3.3 y 3.4 (nombres y módulos), los errores, los ejercicios y el `revisor` repartido en dos archivos. Si te quedas sin tiempo en la primera, para al llegar a `fig03_11`: lo que sigue se entiende mejor con ese programa funcionando y descansado.

**Qué no hace esta lección.** No ve las listas a fondo: hoy usas una lista **mínima** (crearla, preguntar cuántos elementos tiene, leer uno por su posición y agregar uno), lo justo para recorrerla. Los diccionarios, las tuplas, los conjuntos y las comprensiones son de la [Lección 4](04-colecciones.md), y el modelo de datos con `Servicio` y `Estado`, de la [Lección 5](05-modelo-de-datos.md). Y todavía no hay errores atrapados (`try`), ni archivos, ni red.

## Al terminar vas a poder

- Recorrer una lista con `for` de tres maneras (por valor, por posición con `range(len(...))` y con `enumerate`) y repetir con `while` sin caer en un bucle infinito.
- Crear una lista, preguntar su tamaño con `len`, leer un elemento por su posición (que empieza en 0) y agregar uno con `.append`.
- Escribir una función con parámetros, valor por omisión y `return`, con anotaciones de tipo simples (`int`, `str`, `int | None`, `-> None`), y explicar qué diferencia hay entre imprimir y devolver.
- Explicar por qué un valor por omisión que es una lista «recuerda» las llamadas anteriores, y arreglarlo con el patrón de `None`.
- Decir dónde vive cada variable (local o global) y leer `UnboundLocalError`.
- Explicar la diferencia entre `==` (¿son iguales?) y `is` (¿son el mismo objeto?) y saber en qué caso se usa `is`.
- Repartir un programa en dos archivos con `import` y `from ... import`, y explicar para qué sirve `if __name__ == "__main__":`.

## El porqué antes del cómo

Mira lo que habría que hacer hoy, con lo que sabes de la Lección 2, para que el `revisor` revise los cuatro servicios. Copiar el bloque de `inventario` tres veces, y en cada copia cambiar el nombre, el código y el tiempo. Eso son cien líneas casi idénticas. Y después alguien decide que un servicio es lento a partir de los 800 milisegundos, no de los 1000: hay que encontrar la comparación en cada copia y cambiarla. Si te olvidas de una, tres servicios se clasifican con una regla y el cuarto con otra, y el reporte miente sin dar ningún error.

Ese es el problema de fondo, y es el mismo en todos los programas: **la misma lógica escrita varias veces tiende a divergir**. Python (y todos los lenguajes) trae tres herramientas para resolverlo, que son las tres de esta lección:

- **Repetir sin copiar.** Un *bucle* ejecuta el mismo bloque una vez por cada elemento de una lista, o mientras una condición se cumpla. Es el apartado 3.1.
- **Ponerle nombre a un trozo de lógica.** Una *función* encierra una receta (por ejemplo, «clasificar un servicio») bajo un nombre, para usarla desde cualquier parte con valores distintos. Es el apartado 3.2. El precio de las funciones es que ahora hay que saber **dónde vive cada nombre**: una variable que creas dentro de una función no es la misma que otra que tenga el mismo nombre afuera. Eso es el apartado 3.3.
- **Repartir el programa en archivos.** Un *módulo* es un archivo de Python que otro archivo puede usar. Cuando el programa crece, cada archivo guarda una sola clase de cosas (aquí, uno para el formato de la tabla y otro para la lógica de la revisión). Es el apartado 3.4.

Al final de la lección, `python revisor.py` imprimirá la tabla de cuatro servicios que viste en la Lección 2, sin el resumen (que necesita contar, y eso llega en la Lección 5):

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Una advertencia de diseño, para que no la leas como descuido. Los datos de los cuatro servicios van en **tres listas paralelas**: una de nombres, una de códigos y una de tiempos, donde la posición 2 de cada lista habla del mismo servicio. Es una manera frágil de guardar datos: si una lista se desordena o se queda corta, nada te avisa. **Se hace así a propósito**, porque es lo que se puede hacer con lo que sabes hoy, y porque la fragilidad es la razón por la que la Lección 4 existe. En el primer ejercicio vas a romperlo a propósito para verla.

## Los conceptos

### 3.1 Bucles: repetir sin copiar

#### 3.1.1 La lista mínima

Para repetir algo con cada servicio hace falta una lista de servicios, y los valores de la Lección 2 guardan un solo dato cada uno. Hay que presentar la lista. Aquí se ve lo mínimo; la Lección 4 la estudia a fondo.

Una **lista** es una secuencia ordenada de valores, escrita entre corchetes y con los elementos separados por comas: `["catalogo", "inventario", "pagos", "reportes"]`. Una lista puede mezclar tipos (la de los códigos tiene números y un `None`), y se guarda bajo un nombre como cualquier otro valor. Cuatro operaciones bastan por ahora, y las cuatro están en la siguiente figura. Guárdala como `fig03_01.py`:

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

Línea por línea. `print(nombres)` muestra la lista completa, con sus corchetes. `len(nombres)` devuelve cuántos elementos tiene: cuatro. Lo que viene es lo que más desconcierta al principiante: **las posiciones empiezan en 0**. `nombres[0]` es el primer elemento (`catalogo`) y `nombres[3]` es el cuarto (`reportes`). La razón de fondo es que la posición dice cuánto te alejas del principio: el primer elemento está a cero pasos. La consecuencia práctica, que vas a necesitar todo el curso, es que una lista de cuatro elementos tiene las posiciones 0, 1, 2 y 3, y **no tiene posición 4**; la última posición siempre es `len(lista) - 1`.

La última parte de la figura agrega un elemento: `nombres.append("facturacion")` lo pega al final. El punto y el paréntesis significan que `append` es un *método* de la lista, es decir, una operación que la lista sabe hacer sobre sí misma (los métodos son las funciones que «pertenecen» a un valor, y los verás más con los textos y los diccionarios). Después de agregarlo, `len` da 5 y la posición 4 ya existe. Fíjate en que `append` **cambió la lista en su lugar**: no devolvió una lista nueva, modificó la que ya tenía. Los valores que pueden cambiar así se llaman *mutables*, y esa propiedad vuelve a salir dos veces más en esta lección, así que guárdala en la cabeza.

Un detalle de estilo: en esta figura el nombre de la lista va en minúsculas (`nombres`) porque cambia, y en las figuras siguientes, cuando las listas son datos fijos del programa, irán en mayúsculas (`NOMBRES`), como el resto de las constantes.

#### 3.1.2 `for`: hacer algo con cada elemento

El bucle `for` ejecuta un bloque una vez por cada elemento de una lista. Guarda `fig03_02.py`:

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

La primera línea del bucle se lee casi en español: «para cada `nombre` en `nombres`». Termina con **dos puntos**, y el bloque que repite va **con sangría** (cuatro espacios), igual que un `if`. Python hace esto: toma el primer elemento de la lista, lo guarda bajo el nombre `nombre`, ejecuta el bloque; toma el segundo, lo guarda bajo el mismo nombre, ejecuta el bloque; y así hasta que se acaban. La última línea, `print("listo")`, está al margen izquierdo: ya no es parte del bloque, y por eso se ejecuta una sola vez al final. Es la misma regla de la Lección 2: la sangría dice dónde acaba un bloque.

El nombre `nombre` lo eligiste tú. Podría llamarse `x` o `servicio`; pero un buen nombre cuenta qué hay dentro (cada vuelta, `nombre` es *un* nombre, y la lista es `nombres`, en plural). Esta es una convención muy útil: lista en plural, elemento en singular.

#### 3.1.3 `range`: recorrer por posición

A veces no te basta el valor; necesitas su **posición**. Eso pasa con las listas paralelas del `revisor`: para saber el tiempo del servicio que estás mirando, necesitas la misma posición en la lista de tiempos. Para eso existe `range`: `range(4)` produce los números 0, 1, 2 y 3 (los cuatro primeros, empezando en cero, sin incluir el 4). Y como `len(NOMBRES)` vale 4, `range(len(NOMBRES))` produce exactamente las posiciones válidas de la lista. Guarda `fig03_03.py`:

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

El primer bucle solo imprime los números que `range(3)` produce: `0`, `1` y `2`. El segundo es el que importa: en cada vuelta, `i` vale una posición, y las dos listas se leen en esa misma posición, `NOMBRES[i]` y `TIEMPOS_MS[i]`. Observa que esto **solo funciona si las dos listas tienen el mismo largo**; si `TIEMPOS_MS` tuviera un elemento menos, la última vuelta fallaría. Ese es el defecto de las listas paralelas, y tiene un ejercicio para él.

Una nota sobre los nombres: `i` es la costumbre universal para «una posición» (viene de *index*, «índice»), y es de los pocos nombres de una letra que se aceptan. Para todo lo demás, nombres que digan qué son.

#### 3.1.4 `enumerate`: el valor y su posición juntos

Cuando necesitas el valor **y** la posición, `enumerate` te da los dos a la vez. En cada vuelta entrega una pareja, y la sintaxis `for i, nombre in enumerate(...)` pone el primer elemento de la pareja en `i` y el segundo en `nombre`. A eso se le llama *desempaquetar*. Guarda `fig03_04.py`:

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

El primer bucle imprime las posiciones desde 0 con su nombre. El segundo usa un segundo argumento, `start=1`, para que la cuenta empiece en 1: así se numeran las cosas para las personas. Ese `start=1` es un **argumento con nombre**, y lo vas a entender mejor en el apartado 3.2.

`enumerate` es la manera más legible de recorrer **una** lista con su posición. En el `revisor` de hoy hay **tres** listas paralelas, así que la posición es lo que las une y el recorrido es el de `range(len(NOMBRES))`; con tres listas, `enumerate` solo ayuda con una. Pero conviene que lo conozcas, porque en cuanto el `revisor` deje atrás las listas paralelas (Lección 4), recorrerá **una** sola lista, y cuando además haga falta la posición, `enumerate` será la herramienta natural (la usarás en la Lección 6).

#### 3.1.5 `while`: repetir mientras algo sea cierto

`for` repite una vez por cada elemento de algo que ya existe. `while` repite **mientras una condición sea verdadera**, sin saber de antemano cuántas vueltas serán. Vuelve a preguntar la condición antes de cada vuelta, y se detiene cuando la respuesta es `False`. Guarda `fig03_05.py`, que busca la posición del primer servicio que no contestó:

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

Antes de empezar, `i` vale 0. Cada vuelta pregunta dos cosas unidas con `and`: ¿`i` todavía está dentro de la lista? y ¿el código en esa posición existe (`is not None`, que es la negación de `is None`)? Mientras las dos sean verdaderas, ejecuta el bloque, que dice `i += 1`. Esa línea es la abreviatura de `i = i + 1`: suma 1 y guarda el resultado en el mismo nombre. En la posición 3 el código es `None`, la segunda pregunta falla y el bucle termina con `i` valiendo 3.

Fíjate en el **orden de las dos preguntas**, porque es la lección 2 de nuevo. `i < len(CODIGOS)` va primero para que, si `i` llegara a valer 4, el `and` ya fuera falso y Python **no intentara** leer `CODIGOS[4]`, que no existe. El cortocircuito te protegió.

Con `while` hay un riesgo que `for` no tiene: **el bucle infinito**. Si el bloque no cambia nada de lo que la condición pregunta, la condición nunca se vuelve falsa y el programa se queda dando vueltas para siempre. Si olvidaras el `i += 1` de la figura, ocurriría eso. Cuando un programa se cuelga así, la salida de emergencia es `Ctrl`+`C` en la terminal, que lo interrumpe. La regla para escribir un `while` es: **antes de correrlo, localiza la línea del bloque que acerca la condición a ser falsa**. Y cuando se pueda usar un `for`, úsalo: el `for` termina por construcción cuando se acaban los elementos.

#### 3.1.6 Acumular, saltar y salir

Dos usos muy frecuentes de los bucles completan el apartado. El primero es **acumular**: recorrer los datos para sacar una cuenta. Guarda `fig03_06.py`, que suma los tiempos de los servicios que contestaron:

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

El patrón se repite en casi todos los programas: antes del bucle, se crean las variables que acumulan (`total` y `respondieron`, en cero); dentro del bucle, se actualizan; después, se usan. El `if` del bloque deja fuera al servicio que no contestó, cuyo tiempo es `None`; sin él, `total += None` fallaría con un `TypeError`, como el de la Lección 2. La suma es 2529 (142 + 2300 + 87), contestaron tres, y el promedio de los que contestaron es 843. Sale con un `.0` porque la división `/` siempre da un decimal; la Lección 4 te enseña a redondearlo, y la 5 lo usa en el resumen de la tabla.

El segundo uso es **controlar el bucle desde dentro** con dos palabras: `continue` salta a la siguiente vuelta sin terminar el bloque, y `break` sale del bucle por completo. Guarda `fig03_07.py`, que busca el primer servicio lento:

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

Con `catalogo` (142 ms), el bucle pregunta si tiene tiempo (sí), pregunta si es lento (no) y pasa a la siguiente vuelta. Con `inventario` (2300), la segunda pregunta es verdadera: imprime el nombre y `break` termina el bucle, así que `pagos` y `reportes` ni se miran. Si el primero hubiera sido `reportes` (con `None`), el `continue` habría saltado esa vuelta antes de comparar `None >= 1000`, que truena. Usa `break` y `continue` con moderación: son cómodos y esconden el flujo del programa cuando se abusa de ellos.

### 3.2 Funciones: ponerle nombre a una receta

#### 3.2.1 Definir y llamar

Una **función** es un bloque de código con nombre que puedes ejecutar cuando quieras, las veces que quieras, con datos distintos cada vez. Ya has usado funciones que vienen con Python: `print`, `len`, `range`, `type`, `str`. Ahora vas a escribir las tuyas, con la palabra `def` («definir»). La primera es la del formato del tiempo, que en la Lección 2 estaba escrita como un bloque `if` dentro del programa. Guarda `fig03_08.py`:

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

Esta figura tiene dos partes bien separadas, y entender la separación es lo más importante del apartado. **La definición** son las primeras seis líneas, de `def` hasta el último `return`: le explican a Python qué hace `formatear_tiempo`, pero **no la ejecutan**. Es como escribir una receta en una tarjeta: la receta existe, pero nadie ha cocinado nada. **Las llamadas** son las últimas cinco líneas: cada `formatear_tiempo(...)` pide a Python que ejecute la receta con un dato concreto, y es ahí cuando se hace el trabajo. Si quitaras las llamadas, el programa correría sin imprimir nada.

La línea del `def` tiene cuatro partes. `def` anuncia la definición. `formatear_tiempo` es el nombre (en minúsculas con guion bajo, como una variable). Entre paréntesis van los **parámetros**: los nombres que la función usa para referirse a los datos que recibe; aquí uno, `tiempo_ms`. Y al final, los dos puntos y el bloque con sangría, el **cuerpo** de la función. Una distinción de vocabulario que se confunde mucho: el **parámetro** es el nombre que aparece en la definición (`tiempo_ms`), y el **argumento** es el valor que se pasa en la llamada (el `87`, el `999`). Cada vez que se llama la función, los argumentos se asignan a los parámetros y el cuerpo se ejecuta.

La palabra **`return`** hace dos cosas a la vez: **termina la función en ese punto** y **entrega un valor** a quien la llamó. Por eso la función de arriba no necesita `elif` ni `else`: si `tiempo_ms` es `None`, el primer `return` termina la función y las líneas siguientes nunca se ejecutan; si no lo es, se sigue con la pregunta siguiente. Compáralo con la versión de la Lección 2: hace lo mismo, con menos ramas, porque cada `return` ya cierra el camino. El valor que devuelve se puede imprimir, guardar en una variable o usar dentro de otra expresión, igual que cualquier otro valor.

Los casos de la salida son los cinco que vas a probar todo el curso: 87 es `87ms`; 999 es `999ms` (todavía menos de un segundo); **1000 es `1.0s`**, justo en el borde; 2300 es `2.3s`; y `None`, que no tiene tiempo, es la raya larga.

#### 3.2.2 Imprimir no es devolver

Un error clásico del principiante es confundir dos cosas que en la pantalla se parecen: **imprimir** un valor y **devolverlo**. `print` muestra algo en la terminal y se acabó; `return` entrega el valor al código que llamó a la función, que puede hacer con él lo que quiera. Guarda `fig03_09.py` para verlo:

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

La primera línea de la salida (`87ms`) la imprimió `decir_tiempo` al ser llamada, dentro de su cuerpo; nada más. Pero `a`, lo que esa función **devolvió**, es `None`: una función que no tiene `return` devuelve `None` automáticamente. En cambio `dar_tiempo` no imprimió nada; devolvió el texto, y `b` lo guarda. Por eso las dos líneas siguientes imprimen `None` y `87ms`, y los tipos son `NoneType` y `str`. La regla práctica: **una función que calcula algo debe devolverlo, no imprimirlo**, y el que la llama decide si lo imprime. Una función que imprime en vez de devolver es difícil de reusar y más difícil de probar: la Lección 8 prueba funciones comparando lo que devuelven con lo que debían devolver, y lo que solo se imprime también se puede comprobar, pero hay que capturar lo que sale en pantalla (la Lección 11 lo hace) en lugar de comparar un valor.

#### 3.2.3 Valores por omisión y argumentos con nombre

A veces un parámetro casi siempre tiene el mismo valor. En vez de exigirlo en cada llamada, se le puede dar un **valor por omisión** en la definición, con un signo igual: `umbral_ms: int = UMBRAL_LENTO_MS`. Si la llamada no lo pasa, se usa ese valor; si lo pasa, se usa el nuevo. Y cuando una llamada tiene muchos argumentos, se pueden escribir **con nombre** (`umbral_ms=100`) para no depender del orden y para que se lea qué es cada uno. [El tutorial oficial los explica con más ejemplos](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions). Guarda `fig03_10.py`, que es la clasificación de la Lección 2 convertida en función:

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

La definición sigue las cuatro reglas del `revisor`, en el mismo orden de la Lección 2: primero, sin código o con código de error, CAIDO; después, LENTO si hubo respuesta y el tiempo llegó al umbral; si no, ARRIBA. La pregunta `tiempo_ms is not None and ...` tiene el `and` en ese orden por la misma razón de siempre, y como `tiempo_ms` admite `None` en su anotación, el programa se protege aunque, en la práctica, un servicio que contestó siempre trae su tiempo. La firma se partió en tres líneas porque no cabía en una: así lo escribe el formateador automático de Python (la Lección 8 lo presenta), y es lo normal cuando la lista de parámetros es larga.

Las primeras seis llamadas son los casos de la tabla de reglas, en el orden de la salida: ARRIBA, ARRIBA, **LENTO en el borde de 1000**, LENTO, CAIDO por el código 503 (aunque haya contestado en 95 ms) y CAIDO por no haber respuesta. En la séptima, `umbral_ms=100` **sobrescribe el valor por omisión** solo para esa llamada: 142 ms ya es lento si el límite es 100. En la octava, los dos argumentos van con nombre, y se pueden escribir en cualquier orden. Si olvidas un argumento que no tiene valor por omisión, Python lo reclama con `TypeError: clasificar() missing 1 required positional argument: 'tiempo_ms'`: «a `clasificar()` le falta un argumento posicional obligatorio».

#### 3.2.4 Anotaciones de tipo simples

Habrás notado que los parámetros y las funciones llevan cosas como `: int | None` y `-> str`. Se llaman **anotaciones de tipo** y dicen qué tipo de valor se espera y qué tipo devuelve la función. Se escriben así:

- `tiempo_ms: int` — este parámetro es un entero.
- `tiempo_ms: int | None` — este parámetro es un entero **o** `None` (la barra se lee «o»). Es la forma de decir «puede no haber dato».
- `-> str` — la función devuelve un texto.
- `-> None` — la función no devuelve nada útil (devuelve `None`).
- `caidos: list[str]` — una lista de textos. Los corchetes dicen qué hay dentro de la lista.

Un hecho que ya viste en la Lección 0 y que importa repetir: **Python no impone las anotaciones al ejecutar**. Si llamas a `clasificar("hola", "mundo")`, el programa no se queja de los tipos (se queja, quizás, más adelante, por otro motivo). Las anotaciones sirven a dos lectores: a las personas, que entienden qué espera cada función sin leer su cuerpo, y a las herramientas de revisión, que las comprueban sin ejecutar el código. La sintaxis llegó con [la PEP 3107](https://peps.python.org/pep-3107/), en Python 3.0, que dejó a propósito sin definir para qué servían; [la PEP 484](https://peps.python.org/pep-0484/) les dio su uso actual, los tipos, y dice con todas sus letras que «no type checking happens at runtime»: al ejecutar, no se comprueba ningún tipo. La herramienta que las comprueba (`mypy`) llega en la Lección 8; hasta entonces las escribes porque ayudan a leer y porque es mucho más fácil escribirlas al nacer una función que añadirlas después.

#### 3.2.5 Un `revisor` completo en un solo archivo

Con las funciones ya puedes armar el recorrido. Faltan dos funciones más: una que arme el renglón (`linea`) y otra que ponga todo junto para un servicio (`revisar`). Y el encabezado, que también es una función, porque así se escribe una sola vez. Guarda `fig03_11.py`, que reúne todo en un archivo:

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

Lee la figura de abajo hacia arriba, porque así se entiende cómo se apoyan las funciones. Al final, `main()` es la llamada que pone todo en marcha; `main` («principal») es el nombre que por costumbre se le da a la función que arranca el programa. Dentro de `main`, el bucle `for i in range(len(NOMBRES))` recorre las posiciones de las listas paralelas y, en cada vuelta, llama a `revisar` con el nombre, el código y el tiempo de esa posición. `revisar` hace tres cosas: pide el estado a `clasificar`, calcula el detalle con el mismo `if`/`else` de la Lección 2 (el código como texto, o «sin conexión»), y se lo pasa todo a `linea`, que arma el renglón con ayuda de `formatear_tiempo`. Cada función hace **una cosa**, tiene un nombre que dice cuál, y se puede probar sola.

Hay dos detalles que conviene notar. Uno: las constantes (`UMBRAL_LENTO_MS` y las tres listas) están al principio del archivo y las funciones no las reciben como argumento. Una función puede **leer** variables que están definidas fuera de ella; el apartado 3.3 explica cuándo y cuándo no. Dos: el 1000 de `formatear_tiempo` (los milisegundos de un segundo) y el `UMBRAL_LENTO_MS` (el límite de lo lento) siguen siendo cosas distintas, igual que en la Lección 2. Y recuerda de dónde viene la `if`/`else` de `revisar`: cuando el código es `None`, el detalle es «sin conexión», y el código de error se muestra tal cual, como `503`.

Aquí termina la primera sesión. Lo que te llevas: un programa que recorre los cuatro servicios y que, para cambiar el umbral o el formato del tiempo, tiene un solo lugar donde tocar.

### 3.3 Nombres: dónde vive cada variable, y `==` contra `is`

#### 3.3.1 Local y global

Cuando Python ve un nombre, necesita saber **a qué variable se refiere**. La regla se llama *ámbito* (en inglés, *scope*), y [está en el tutorial oficial](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces). Para esta lección alcanzan dos clases de nombres:

- **Global**: el que se crea al nivel del archivo, fuera de cualquier función. `UMBRAL_LENTO_MS` y `NOMBRES` son globales.
- **Local**: el que se crea **dentro** de una función, incluyendo sus parámetros. Existe solo mientras la función se ejecuta, y desaparece cuando termina. Cada llamada a la función crea sus propios nombres locales, aparte de los de las otras llamadas.

Una función puede **leer** nombres globales sin problema, pero los locales de una función no se ven desde afuera. Guarda `fig03_12.py`:

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

Dentro de `es_lento`, `UMBRAL_LENTO_MS` es global y se lee con naturalidad; `tiempo_ms` y `limite` son locales. Fuera de la función, `limite` no existe. Si añades al final del programa una línea `print(limite)`, Python se detiene con este error (pruébalo y comprueba que tu pantalla dice lo mismo):

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

La última línea es la que manda: `NameError`, el nombre `limite` no está definido. La primera línea de la salida, `True`, es la que alcanzó a imprimir `es_lento(2300)` antes de la caída. Este es el modo en que Python te dice «en este lugar del programa, ese nombre no existe», y es el segundo error más común del principiante después del de los dos puntos. Casi siempre es una de tres cosas: te equivocaste al escribir el nombre (recuerda que las mayúsculas cuentan), usaste el nombre antes de crearlo, o lo creaste dentro de una función y lo buscas afuera.

#### 3.3.2 Asignar dentro de una función crea un nombre local

Hay una regla del ámbito que sorprende a casi todos, y que produce el error de la sección siguiente. Lo que decide si un nombre es local o global **no es si existe afuera, sino si la función le asigna un valor en alguna parte de su cuerpo**. Si dentro de la función hay una asignación a `total` (con `=` o con `+=`, que es una asignación disfrazada), Python decide, antes de ejecutar nada, que `total` es **local en toda esa función**. Aunque exista un `total` global, la función no lo toca: usa uno local, y si lo lees antes de asignarlo, no tiene valor todavía.

Esto, que parece un capricho, protege tus programas: una función que cambia variables globales sin que se note vuelve el programa imposible de entender (¿quién cambió `total`?). La manera correcta de que una función afecte al resto del programa es la que ya conoces: **recibe lo que necesita como parámetros y devuelve lo que calculó**. Python tiene una palabra, `global`, que permite lo contrario, y la menciono solo para que la reconozcas cuando la veas en código ajeno. En este curso no se usa.

#### 3.3.3 `==` contra `is`

Python tiene dos maneras de preguntar si dos cosas son «lo mismo», y significan cosas distintas:

- **`a == b`** pregunta si **tienen el mismo valor**: ¿son iguales?
- **`a is b`** pregunta si **son el mismo objeto**: ¿son literalmente la misma cosa en la memoria, la misma?

Hay una analogía útil: dos billetes de cien pesos son iguales en valor (`==`), pero no son el mismo billete (`is`). Guarda `fig03_13.py`:

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

`a` y `b` son dos listas **distintas** con el mismo contenido: son iguales (`True`) pero no son la misma (`False`). En cambio `c = a` no copia la lista: hace que `c` sea **otro nombre para la misma lista**, y por eso `a is c` es `True`. (Qué pasa cuando esa lista cambia, y cómo se hace una copia de verdad, es el tema de «copia contra referencia» en la Lección 4.)

Entonces, ¿cuándo se usa cada una? **Casi siempre `==`**, para comparar valores: códigos, textos, tiempos. **`is` se reserva para `None`**: como en el programa existe un solo `None`, la pregunta correcta es si el valor *es* ese objeto, y por eso la Lección 2 te hizo escribir `codigo is None`. Es lo que pide la [guía de estilo](https://peps.python.org/pep-0008/#programming-recommendations). Con `True` y `False` ni siquiera hace falta comparar: si `activo` ya es un booleano, se escribe `if activo:`, y la misma guía califica `if activo == True:` de incorrecto y `if activo is True:` de peor.

El peligro está en usar `is` con números o textos, porque a veces **parece funcionar**. Python, por eficiencia, reutiliza el mismo objeto para los números enteros pequeños: [la documentación dice que guarda uno para cada entero entre -5 y 256](https://docs.python.org/3/c-api/long.html#c.PyLong_FromLong). Esto es un detalle de la implementación de CPython, el Python que usas, y no una promesa del lenguaje. El REPL lo muestra:

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

Con 100 la comparación sale bien por accidente; con 1000, mal. Una comparación con `is` que funciona con unos números y no con otros es un error esperando el día de salir. Python te avisa cuando ve algo así. Si guardas el siguiente programa y lo corres, funciona, pero primero imprime un aviso:

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

Es un `SyntaxWarning`, un aviso, no un error: el programa siguió y terminó bien. Léelo igual. Dice exactamente qué hiciste mal y qué querías hacer: `"is"` con un número literal, «¿querías `==`?». Los avisos son la manera que tiene Python de decirte algo que hoy no truena pero que mañana puede mentirte.

### 3.4 Módulos: repartir el programa en archivos

#### 3.4.1 Un archivo es un módulo

Un programa de cien líneas cabe en un archivo; uno de mil, ya no se lee bien. La solución de siempre es repartirlo: cada archivo guarda una sola clase de cosas, y los demás lo usan. En Python, **cada archivo `.py` es un *módulo***, y un archivo usa a otro con la palabra **`import`**. Python trae además cientos de módulos ya escritos, la *biblioteca estándar*, que se importan igual (por ejemplo, `statistics`, para estadística básica).

Hay dos formas de importar, y las dos aparecen en el `revisor`:

- **`import modulo`**: trae el módulo completo, y sus nombres se usan con el prefijo del módulo: `modulo.nombre`. Es la forma que deja más claro de dónde viene cada cosa.
- **`from modulo import nombre1, nombre2`**: trae solo esos nombres, y se usan directamente, sin prefijo. Es cómoda cuando solo necesitas una o dos cosas.

Cuando Python importa un módulo, según [la documentación de módulos](https://docs.python.org/3/tutorial/modules.html#the-module-search-path), primero mira si es uno de los pocos módulos **incorporados** al propio intérprete (como `sys`); si no lo es, lo busca **en la carpeta del archivo que está ejecutando** y después en la biblioteca estándar y en los lugares donde `pip` instala cosas. Por eso, para que `import formato` funcione, `formato.py` tiene que estar en la misma carpeta que `revisor.py`. La primera vez que importas un módulo, Python además lo traduce a *bytecode* (recuerda la Lección 0) y guarda el resultado en una carpeta llamada `__pycache__` junto a él, para que la próxima vez cargue más rápido. Esa carpeta aparece sola; no la edites ni la guardes en ningún repositorio.

#### 3.4.2 `if __name__ == "__main__":`

Un archivo puede ser dos cosas: un **programa** que se ejecuta (`python revisor.py`) o un **módulo** que otro archivo importa. A veces es las dos. Hace falta una manera de distinguir los dos casos, porque cuando alguien importa tu módulo no quiere que el programa arranque solo. Python lo resuelve con una variable especial, `__name__` (con dos guiones bajos a cada lado, que se leen «dunder»): **vale `"__main__"` cuando el archivo se está ejecutando directamente, y vale el nombre del módulo cuando fue importado**. [La documentación del módulo `__main__`](https://docs.python.org/3/library/__main__.html) explica ese comportamiento y el idioma que lo aprovecha. Guarda los dos archivos de la figura `fig03_14`, en una carpeta con ese nombre:

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

Corre cada archivo por separado, desde la carpeta `fig03_14`:

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

Cuando se ejecuta `medidas.py` directamente, `__name__` vale `__main__`, y por eso se cumple el `if` del final y se imprimen las dos líneas de abajo. Cuando se ejecuta `uso.py`, el `import medidas` hace que Python **ejecute `medidas.py` de arriba abajo una vez**, y esta vez `__name__` vale `medidas`, el nombre del módulo, así que el `if` no se cumple y las dos líneas finales no salen. Después `uso.py` sigue, con su propio `__name__` valiendo `__main__`, y usa `medidas.segundos` con el prefijo del módulo. La última línea usa un módulo de la biblioteca estándar: `statistics.mean` calcula el promedio de la lista, y da 843, la cifra que en la figura `fig03_06` salió con `.0` por dividir a mano.

Eso es lo que significa el idioma:

```text
if __name__ == "__main__":
    main()
```

«Si este archivo se está ejecutando como programa, llama a `main()`». Si en cambio alguien lo importa, no hace nada, y las funciones quedan disponibles. Es una costumbre de casi todo programa serio en Python, y es la que cierra el `revisor` de abajo.

#### 3.4.3 Partir el `revisor` en dos archivos

Con todo eso, el `revisor` queda repartido en dos módulos con una división de responsabilidades clara. `formato.py` guarda **todo lo que tiene que ver con cómo se ve la tabla** (el formato del tiempo, el encabezado y el renglón). `revisor.py` guarda **todo lo que tiene que ver con revisar** (los datos, la clasificación y el recorrido), e importa de `formato` lo que necesita. Esta es la figura de proyecto de la lección: una carpeta `fig03_15` con dos archivos. Es el estado en que queda tu `~/curso-python/revisor/` al terminar la lección, y el punto de partida de la Lección 4.

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

Observa tres cosas. **Primero**, `from formato import encabezado, linea` trae solo dos de las tres funciones de `formato.py`: `formatear_tiempo` no se usa en `revisor.py` (la usa `linea`, por dentro), y no hace falta traerla. **Segundo**, el programa imprime exactamente la misma tabla que `fig03_11`, el de un solo archivo: partir un programa no cambia lo que hace, solo dónde vive cada pieza. **Tercero**, la última línea ya no es `main()` a secas sino el idioma del apartado anterior; ahora, si en el futuro otro archivo importa `revisor`, no se imprimirá la tabla sin querer. Es justo lo que necesitarás cuando, más adelante, escribas pruebas que importen tus funciones.

Tras correrlo, mira lo que apareció en la carpeta:

```console
$ ls
formato.py  __pycache__  revisor.py
```

Ese `__pycache__` es el que Python creó al importar `formato`; ahí guardó la versión en *bytecode*. (El orden en que `ls` acomoda los nombres depende de la configuración de idioma de tu terminal, así que puede salirte distinto.) Si ahí dentro ves un archivo `formato.cpython-312.pyc`, el `312` es la versión de Python que lo generó; con otra versión, el número cambia.

Un último detalle de diseño: `formato.py` no sabe **nada** de servicios. Solo recibe un nombre, un estado, un tiempo y un detalle, y devuelve texto. Esa ignorancia es una virtud: el módulo de formato puede seguir casi igual cuando, en las lecciones 4 y 5, los datos cambien de forma.

## El error que vas a ver

Esta lección tiene dos errores que son suyos, y los dos se aprenden mejor provocándolos. Ambos están copiados de una corrida real. Y un recordatorio para leer cualquier *traceback*: la última línea dice **qué** pasó; las de arriba, **dónde**, de la más reciente (abajo) a la más antigua (arriba) en la cadena de llamadas.

### `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`

Es el error del apartado 3.3.2. Guarda este programa, que intenta acumular un total desde dentro de una función, y córrelo:

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

Una nota sobre esta salida: es la de Python 3.14. En Python 3.12 la línea de la llamada (`sumar_tiempo(142)`) no trae las marcas `~~~~^^^^^` debajo; todo lo demás, y en particular la última línea, es idéntico. Es un buen ejemplo de por qué la lectura empieza por abajo.

La última línea dice: no se puede acceder a la variable local `total` porque no tiene valor asociado todavía. Las dos de arriba dicen **dónde**: dentro de `sumar_tiempo`, en la línea 5, que es `total += tiempo_ms`; y esa función fue llamada desde la línea 8 del programa. ¿Por qué falla? Porque `total += tiempo_ms` es una asignación (equivale a `total = total + tiempo_ms`), y por la regla del apartado 3.3.2 eso vuelve a `total` una variable **local** de toda la función; pero para sumar, la función necesita leer el valor actual de `total`, y el `total` local todavía no tiene ninguno. El `total = 0` de afuera es otra variable, y la función ni la mira.

La corrección es la que prescribe la regla de oro de las funciones: que reciba lo que necesita y devuelva lo que calcula. Por ejemplo, `def sumar_tiempo(total: int, tiempo_ms: int) -> int: return total + tiempo_ms`, y en el programa, `total = sumar_tiempo(total, 142)`. [La documentación oficial tiene una entrada de preguntas frecuentes para este caso exacto](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value), y [la de `UnboundLocalError`](https://docs.python.org/3/library/exceptions.html#UnboundLocalError) la define como el error que ocurre cuando se hace referencia a una variable local de una función que aún no tiene valor.

### La lista que recuerda las llamadas anteriores

Este no es un error con mensaje, y por eso es peor: el programa no se cae, **da una respuesta equivocada sin avisar**. Es una de las trampas más famosas de Python. Guarda este programa, que lleva la cuenta de los servicios caídos, y córrelo:

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

Cada llamada era independiente: ninguna le pasó una lista a la función. Se esperaba ver `['reportes']`, `['facturacion']` y `['notificaciones']`. En cambio, la lista **acumula** lo de las llamadas anteriores. Es como si la función tuviera memoria.

La explicación viene de cuándo se evalúa un valor por omisión: **una sola vez, cuando Python ejecuta el `def`, no cada vez que se llama la función**. El `[]` de `caidos: list[str] = []` se crea una vez, al definir la función, y queda guardado junto a ella; cada llamada que no pasa su propia lista usa **esa misma lista**, y `.append` la cambia en su lugar (recuerda: las listas son mutables). Así, lo que la primera llamada metió, la segunda lo encuentra. [El tutorial oficial lo advierte con este mismo ejemplo](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values), y [las preguntas frecuentes](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects) explican por qué es así.

La regla es: **nunca uses una lista (ni un diccionario, ni ningún otro valor mutable) como valor por omisión**. El patrón correcto usa `None` como señal de «no me pasaron nada» y crea la lista dentro de la función, donde se crea nueva en cada llamada. Guarda `fig03_16.py`:

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

Ahora las dos primeras llamadas son independientes, como se esperaba. Y cuando **sí** se quiere acumular, la persona que llama lo dice explícitamente: crea su propia lista (`historial`) y se la pasa a la función, que la usa en lugar de crear una. El parámetro admite `list[str] | None`, que se lee «una lista de textos, o nada». Este patrón (`None` por omisión y crear dentro) lo verás en código ajeno muchísimas veces. Y este defecto es tan conocido que las herramientas de revisión lo detectan solas: `ruff`, que verás en la Lección 8, tiene una regla específica para él (la B006) y puede señalarlo antes de que corras el programa.

### `ModuleNotFoundError` e `ImportError`

Los dos errores del apartado de módulos. Si el nombre de un módulo está mal escrito, o el archivo no está en la carpeta de donde se ejecuta, Python no lo encuentra:

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

Y si el módulo existe pero el nombre que pides no está en él, el error es otro:

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

Los dos mensajes son literales. El primero dice que no hay ningún módulo llamado `formatos` (en el ejemplo se escribió una `s` de más). El segundo dice que `formato` sí existe, pero no tiene nada llamado `lineas`; Python te muestra el archivo donde buscó (la ruta será la de tu máquina) y hasta te sugiere el nombre que parece que querías: `linea`. Ante un `ModuleNotFoundError`, revisa tres cosas por orden: cómo escribiste el nombre, si el archivo está en la carpeta, y si estás parado en la carpeta correcta cuando corres el programa.

## Lo que se hace mal

**Imprimir en vez de devolver.** `def total(...): print(...)` parece funcionar mientras solo quieres ver el resultado. Costo: cuando necesitas usar el resultado en otra cuenta, o probarlo, descubres que la función devolvió `None`. Las funciones que calculan, devuelven.

**Usar una lista como valor por omisión.** Es el error de arriba. Costo: datos que se mezclan entre llamadas sin ningún mensaje de error, y que aparecen en producción como un reporte con servicios que no deberían estar.

**Cambiar una variable global desde una función.** Con `global` se puede, y el programa se vuelve un laberinto: para entender qué valor tiene una variable hay que leer todas las funciones. Si una función necesita un dato, que lo reciba; si produce uno, que lo devuelva.

**Comparar con `is` cosas que no son `None`.** Puede funcionar con números pequeños y fallar con los grandes, o dar un `SyntaxWarning` como el de arriba. Comparar valores es `==`.

**Un `while` sin avance.** Si el bloque no acerca la condición a ser falsa, el programa nunca termina. Antes de correr un `while`, localiza la línea que lo avanza.

**Escribir `range(len(NOMBRES))` y luego tocar solo una lista.** Es la fragilidad de las listas paralelas: si agregas un servicio a `NOMBRES` y olvidas agregar su código o su tiempo, el programa falla (con un `IndexError`) o, peor, imprime datos que no son de ese servicio. El Ejercicio 1 lo muestra en acción. No hay arreglo con lo que sabes hoy: el arreglo es guardar cada servicio como una sola cosa, y es el tema de la Lección 4.

**Nombrar tu archivo como un módulo de la biblioteca estándar.** Si creas `statistics.py` en la carpeta del proyecto y otro archivo hace `import statistics`, Python encuentra **primero** el tuyo (recuerda el orden de búsqueda: la carpeta del programa va antes que la biblioteca estándar; solo los módulos incorporados al intérprete, como `sys`, se salvan, porque se buscan antes que cualquier carpeta) y los nombres del módulo real dejan de existir. El síntoma es un error del tipo `AttributeError: module 'statistics' has no attribute 'mean'` (las versiones recientes de Python añaden al final una sugerencia de renombrar el archivo), y desconcierta mucho porque tu propio código no tiene ningún error. Evita los nombres `statistics`, `random`, `json`, `string`, `types` y los demás de la biblioteca estándar.

**Poner `main()` a secas al final de un módulo.** Cuando otro archivo lo importe, el programa arrancará solo. El idioma `if __name__ == "__main__":` existe para eso.

**Copiar y pegar una función en lugar de importarla.** Si el mismo código está en dos archivos, tarde o temprano uno de los dos se corrige y el otro no. Lo que se comparte se importa.

## Ejercicios

### Ejercicio 1 — Agregar un servicio y olvidar una lista

En `fig03_15/revisor.py`, agrega `facturacion` (código 503, tiempo 95 ms) a las listas. Hazlo dos veces. **Primera vez:** agrega `"facturacion"` a `NOMBRES` y `503` a `CODIGOS`, pero **olvida** `TIEMPOS_MS`. Predice qué va a pasar antes de correrlo. **Segunda vez:** agrega los tres datos pero en un orden distinto: `503` al **principio** de `CODIGOS` y `95` al final de `TIEMPOS_MS`. Predice, y después compara con lo que ves. ¿Cuál de las dos fallas es más peligrosa y por qué?

### Ejercicio 2 — Contar los servicios caídos

Escribe una función `contar_caidos(codigos: list[int | None]) -> int` que reciba la lista de códigos y devuelva cuántos servicios están caídos según la regla de siempre (sin código, o con código de 400 o más). Pruébala con `CODIGOS` (debe dar 1), con `[200, 503, None]` (debe dar 2) y con una lista vacía `[]` (debe dar 0). Debe **devolver** el número, no imprimirlo.

### Ejercicio 3 — Provocar los errores de la lección

En copias de tu proyecto, provoca uno por uno: (a) usar un nombre local desde afuera de su función; (b) un `total += x` dentro de una función; (c) la lista que recuerda; (d) `from formato import lineas`; (e) quitar `formato.py` de la carpeta. Para cada uno, copia la última línea del mensaje, escribe qué significa y cuál es la corrección.

### Ejercicio 4 — El servicio más lento

Escribe una función `mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None` que devuelva el **nombre** del servicio con el mayor tiempo, ignorando los que no contestaron (los que tienen `None`). Si ninguno contestó, debe devolver `None`. Con `NOMBRES` y `TIEMPOS_MS` debe devolver `"inventario"`. Pista: recorre por posición, guarda en dos variables el mejor tiempo visto hasta ahora y su nombre, y actualízalas cuando encuentres un tiempo mayor. Piensa con qué valor deben empezar esas variables.

## Soluciones

### Solución 1

Primera falla, con `TIEMPOS_MS` más corta que las otras dos listas: el bucle pasa por los cuatro primeros servicios sin problema y al llegar al quinto, `TIEMPOS_MS[4]` no existe.

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

(Es la salida de Python 3.14; en 3.12 no aparece la línea de marcas `~~~~^^` debajo de `main()`, y todo lo demás, incluidas las marcas de `TIEMPOS_MS[i]` y la última línea, es idéntico.)

La última línea dice que el índice está fuera del rango de la lista: pediste una posición que no existe. Es el error que producen las listas paralelas cuando una se queda corta.

Segunda falla, con los datos en un orden distinto: el programa **no falla**, e imprime esto:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO      142ms  503
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    ARRIBA         —  200
facturacion CAIDO       95ms  sin conexión
```

Mira cómo quedó cada renglón. `catalogo` aparece CAIDO con código 503, aunque funciona. `reportes`, que no contestó, aparece ARRIBA con código 200 (y sin tiempo, porque su tiempo sí era `None`). `facturacion` aparece con «sin conexión», cuando en realidad contestó con un 503 en 95 ms. Los códigos están corridos una posición respecto de los tiempos, y nada avisa. Esta es la más peligrosa: la primera falla se ve; la segunda produce un reporte que parece válido y miente. Esa es la razón por la que en la Lección 4 cada servicio dejará de ser tres números sueltos en tres listas para ser **una sola cosa** que no se puede desfasar.

### Solución 2

```python
def contar_caidos(codigos: list[int | None]) -> int:
    caidos = 0
    for codigo in codigos:
        if codigo is None or codigo >= 400:
            caidos += 1
    return caidos
```

Con `CODIGOS` da `1`, con `[200, 503, None]` da `2` y con `[]` da `0`: el bucle no da ninguna vuelta y devuelve el valor con que empezó el contador. El `return` va **fuera** del bucle (al margen del `for`); si lo pusieras dentro, la función terminaría en la primera vuelta. Y la condición es la misma que en `clasificar`: primero `is None`, para que `None >= 400` no se evalúe nunca.

### Solución 3

(a) `NameError: name 'limite' is not defined` (o el nombre que uses): el nombre es local y afuera no existe. Corrección: devolver el valor con `return` y guardarlo en una variable de afuera.

(b) `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`: la asignación vuelve local a `total`. Corrección: recibirlo como parámetro y devolver el nuevo.

(c) La lista que acumula entre llamadas, sin ningún mensaje. Corrección: `None` por omisión y crear la lista dentro.

(d) `ImportError: cannot import name 'lineas' from 'formato' (...)`: el módulo existe pero no tiene ese nombre. Corrección: escribir `linea`.

(e) Sin `formato.py` en la carpeta: `ModuleNotFoundError: No module named 'formato'`. Corrección: poner el archivo donde está `revisor.py`, o correr el programa desde la carpeta que lo contiene.

### Solución 4

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

Con los datos del `revisor` devuelve `"inventario"`; con `[None, None]` devuelve `None`. La clave está en el valor de partida: las dos variables empiezan en `None`, que significa «todavía no vi a nadie», y por eso la pregunta `mejor_tiempo_ms is None or ...` va primero: el primer servicio que contestó siempre gana, y a partir de ahí se compara. Si hubieras empezado `mejor_tiempo_ms` en 0 funcionaría con estos datos, pero daría una respuesta absurda con una lista de tiempos negativos, y habría que decidir qué nombre devolver cuando nadie contestó. `None` expresa eso sin inventar nada.

## Cómo sé que lo logré

- [ ] Desde `fig03_15` (o desde tu carpeta `revisor/`), `python revisor.py` imprime el encabezado y los cuatro renglones de la tabla, idénticos a los de la figura, incluida la raya larga y «sin conexión» en el de `reportes`.
- [ ] `python fig03_11.py` (todo en un archivo) y `python revisor.py` (en dos archivos) imprimen exactamente lo mismo.
- [ ] Al cambiar `UMBRAL_LENTO_MS` a 100 en `revisor.py`, `catalogo` pasa a LENTO sin que toques ninguna otra línea.
- [ ] Después de correr el programa existe una carpeta `__pycache__` junto a `formato.py`, y sabes decir por qué.
- [ ] Puedes provocar `UnboundLocalError` y `ImportError` a propósito y decir, mirando solo la última línea, qué pasó.
- [ ] Puedes explicar con tus palabras la diferencia entre `print` y `return`, entre `==` y `is`, y entre un parámetro y un argumento.
- [ ] Puedes explicar por qué la función `registrar_caido` de la sección de errores «recordaba» y por qué la versión con `None` no.

## Resumen

Responde sin mirar la lección:

1. ¿Desde qué número empiezan las posiciones de una lista, y cuál es la última posición de una lista de `n` elementos?
2. ¿Qué produce `range(len(NOMBRES))` si `NOMBRES` tiene cuatro elementos? ¿Y qué entrega `enumerate` en cada vuelta?
3. ¿Qué riesgo tiene un `while` que no tiene un `for`, y cómo lo evitas?
4. ¿Qué diferencia hay entre definir una función y llamarla? ¿Qué es un parámetro y qué es un argumento?
5. ¿Qué devuelve una función que no tiene `return`? ¿Por qué una función que calcula debe devolver y no imprimir?
6. ¿Cuándo se evalúa un valor por omisión, y por qué eso hace que una lista como valor por omisión «recuerde»? ¿Cuál es el patrón correcto?
7. ¿Qué decide si un nombre es local o global dentro de una función? ¿Por qué `total += x` falla en una función?
8. ¿Qué pregunta hace `==` y qué pregunta hace `is`? ¿Con qué valor se usa `is`?
9. ¿Qué valor tiene `__name__` cuando ejecutas un archivo directamente, y cuál cuando lo importan? ¿Para qué sirve eso?
10. ¿Por qué las tres listas paralelas del `revisor` son una mala idea, y por qué se usan hoy?

## Para leer más

- [El tutorial de Python, «Más herramientas de control de flujo»](https://docs.python.org/3/tutorial/controlflow.html) — `for`, `range`, `break` y `continue`, `def`, valores por omisión y argumentos con nombre, en un solo capítulo. Documentación oficial. Consultado el 7 de octubre de 2026.
- [El tutorial de Python, «Módulos»](https://docs.python.org/3/tutorial/modules.html) — `import`, `from ... import`, el orden de búsqueda y `__pycache__`. Consultado el 7 de octubre de 2026.
- [Preguntas frecuentes de programación en Python](https://docs.python.org/3/faq/programming.html) — las trampas de esta lección (el valor por omisión mutable, `UnboundLocalError`, `is` contra `==`), con la explicación del propio equipo de Python. Consultado el 7 de octubre de 2026.
- [PEP 8, la guía de estilo de Python](https://peps.python.org/pep-0008/) — nombres, sangría y el uso de `is` con `None`; es la guía que sigue este curso. Consultado el 7 de octubre de 2026.
