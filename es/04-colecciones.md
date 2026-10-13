# Lección 4 — Colecciones

**Tiempo:** 2 × 90 min (la primera sesión llega hasta el final de 4.2; la segunda empieza en 4.3)

**Qué construyes:** el `revisor` sin listas paralelas: los datos de cada servicio viajan juntos, en un diccionario que se consulta por el nombre del servicio

**Qué aprendes:** `list`, `tuple`, `dict` y `set`; comprensiones; copia contra referencia; no cambiar lo que se recorre; `KeyError` e `IndexError`

**De dónde vienes.** Traes el proyecto de la [Lección 3](03-bucles-funciones-modulos.md): dos archivos, `formato.py` y `revisor.py`. El primero sabe dar formato al tiempo y armar el encabezado y cada renglón; el segundo guarda los datos, clasifica cada servicio y recorre los cuatro para imprimirlos. Funciona, y la tabla sale bien. Pero los datos de los servicios viven en **tres listas paralelas**, `NOMBRES`, `CODIGOS` y `TIEMPOS_MS`, que solo se corresponden por la posición: el nombre número 2 va con el código número 2 y con el tiempo número 2. En el ejercicio de la Lección 3 agregaste `facturacion` a dos listas, olvidaste la tercera, y viste el `IndexError` o el renglón equivocado que eso produce. Esa fragilidad es la que se quita hoy.

**Qué no hace esta lección.** No le da todavía a cada servicio una forma propia con nombre (un `Servicio`, un `Estado`): eso es la [Lección 5](05-modelo-de-datos.md), que se apoya en todo lo de hoy. Tampoco lee la configuración de un archivo (los servicios siguen escritos a mano en el código; la [Lección 6](06-errores-archivos-datos.md) los saca de ahí), no atrapa errores con `try` y no consulta ninguna dirección de internet: los códigos y los tiempos salen de una tabla simulada dentro del programa.

Trabajas en tu carpeta `~/curso-python/revisor/`. Los programas pequeños de la lección (los que no son parte del proyecto) puedes guardarlos en una subcarpeta `practica/` dentro de ella, para que no se mezclen con los archivos del `revisor`. Todos los comandos asumen que el entorno virtual de la Lección 1 está activo, así que se escribe `python`, no `python3`.

## Al terminar vas a poder

- Elegir entre lista, tupla, diccionario y conjunto según lo que vas a guardar y cómo lo vas a buscar, y escribir cada una con su anotación de tipo (`list[str]`, `dict[str, int | None]`, `set[str]`).
- Leer un `IndexError` y un `KeyError`, decir qué posición o qué clave faltó, y usar `.get` cuando la ausencia es un caso normal y no un error.
- Reescribir un bucle que arma una lista como una comprensión, y saber cuándo conviene dejarlo como bucle.
- Predecir qué pasa con `b = a` cuando `a` es una lista, copiar de forma superficial y profunda, y explicar por qué cambiar una lista mientras la recorres da resultados equivocados sin avisar.
- Reescribir el `revisor` sin listas paralelas: un diccionario que guarda, para cada nombre, una tupla con su código, su tiempo y su error, y un recorrido que ya no depende de que tres listas estén alineadas.

## El porqué antes del cómo

Abre el `revisor.py` de la Lección 3 y mira cómo se representa `inventario`: el texto `"inventario"` en `NOMBRES[1]`, el número `200` en `CODIGOS[1]` y el número `2300` en `TIEMPOS_MS[1]`. Tres valores que pertenecen a una misma cosa, guardados en tres lugares distintos. Para agregar un servicio tienes que acordarte de tocar tres listas y de tocarlas en el mismo orden, y Python no te avisa si te equivocas: si olvidas la tercera, el programa falla al llegar al quinto servicio, o peor, empareja el código de un servicio con el tiempo de otro y la tabla sale bien formateada y **mal**. Es la regla de siempre en programación: un dato escrito en dos sitios termina por diferir.

La solución es **un solo lugar para cada dato**, y para eso hacen falta formas de agrupar valores. Python trae cuatro (lista, tupla, diccionario y conjunto), cada una pensada para una pregunta distinta: «¿en qué orden están?», «¿cuál es el de este nombre?», «¿ya vi este valor?». Esta lección las presenta una por una (4.1), junto con las dos herramientas con que se construyen y se manejan sin sorpresas: las comprensiones (4.2) y el cuidado con las copias (4.3). Al final (4.4) las usas para reescribir el `revisor`: los datos de cada servicio pasan a vivir juntos, bajo su nombre, y las tres listas paralelas desaparecen. La lección siguiente da el paso que falta, ponerles nombre propio a las cosas del problema (un `Servicio`, un `Estado`), y para darlo necesita todo lo de hoy.

Al final de la lección, el `revisor` hará esto:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Es exactamente la tabla de la Lección 3, letra por letra, y es a propósito: lo que cambia hoy no es lo que el programa imprime, sino cómo guarda sus datos por dentro. Un cambio así, que deja el resultado idéntico y mejora la estructura, tiene una ventaja enorme: se comprueba comparando las dos salidas. Lo que gana el programa no se ve en la tabla sino al modificarlo, y lo vas a comprobar en el ejercicio 3: agregar un servicio deja de ser una operación sobre tres listas que hay que tocar en el mismo orden.

## Los conceptos

### 4.1 Las cuatro colecciones

Una **colección** es un valor que guarda otros valores. Python trae cuatro de uso diario, y se distinguen por dos preguntas. La primera: ¿se puede cambiar después de crearla? A lo que se puede cambiar se le llama **mutable**, y a lo que no, **inmutable**; la lista, el diccionario y el conjunto son mutables, la tupla no. La segunda: ¿cómo se encuentra un elemento? Por su **posición** (lista y tupla), por su **nombre** (diccionario) o simplemente preguntando si **está o no está** (conjunto). Ve cada una con un ejemplo del `revisor` y al final, en 4.1.5, hay una tabla para decidir.

#### 4.1.1 La lista: valores en orden

Ya usaste la lista mínima en la Lección 3: el literal con corchetes, `len`, `.append` y `lista[i]`. Aquí se ve completa. Una **lista** guarda valores en un orden, se puede cambiar y se escribe entre corchetes. Guarda el siguiente programa como `fig04_01.py` en tu carpeta `practica/` y córrelo:

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

Línea por línea:

- `nombres[0]` y `nombres[3]` piden el primer y el cuarto elemento. Las posiciones, que se llaman **índices**, empiezan en **0**: con cuatro elementos las posiciones válidas son 0, 1, 2 y 3. Por eso la última posición de una lista de `len(nombres)` elementos es `len(nombres) - 1`, y no `len(nombres)`.
- `nombres[-1]` y `nombres[-2]` cuentan desde el final: `-1` es el último, `-2` el penúltimo. Es la forma cómoda de pedir «el último» sin calcular nada.
- `nombres[1:3]` es una **rebanada** (en inglés, *slice*): los elementos desde la posición 1 **hasta la 3 sin incluirla**, es decir, las posiciones 1 y 2. Devuelve una lista nueva con `['inventario', 'pagos']`. El «sin incluir» es una regla que desconcierta una vez y después se usa sin pensar: `nombres[1:3]` tiene `3 - 1 = 2` elementos, y `nombres[0:len(nombres)]` es la lista entera. [El tutorial de Python](https://docs.python.org/3/tutorial/introduction.html#lists) explica las rebanadas con más ejemplos.
- `len(nombres)` ya la conoces. Junto con `sorted`, `sum`, `min` y `max` es una de las **funciones incluidas** (*built-in*): vienen con Python y se usan sin importar nada.
- `"pagos" in nombres` es otra forma de usar la palabra `in`, la misma que ya viste en `for ... in`: aquí responde `True` o `False` según si el valor **está** en la lista. Cuidado, que con una lista Python la revisa elemento por elemento; con listas cortas da igual, y en 4.1.4 verás una colección mucho más rápida para esa pregunta.
- `nombres.append("facturacion")` agrega al final, y **cambia la lista que ya existe** (no crea otra). `nombres.pop()` quita el último elemento y lo devuelve, de modo que `ultimo` vale `"facturacion"` y la lista vuelve a tener cuatro. Que `append` y `pop` modifiquen la lista que ya existe es lo que significa «mutable», y tiene consecuencias que verás en 4.3.
- `sorted(tiempos_ms)` devuelve una lista **nueva** ordenada y deja la original como estaba: por eso la segunda parte de la línea sigue mostrando `[142, 2300, 87]`. En cambio `tiempos_ms.sort()` ordena **la propia lista** y no devuelve nada (en rigor, devuelve `None`). [La documentación lo dice así](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types): para recordarte que actúa «por efecto secundario», `sort` no devuelve la lista ordenada, y para pedir una nueva existe `sorted`. Esa distinción entre «cambia la que tengo» y «me da una nueva» reaparece en todo Python, y se vuelve una trampa común (la verás en «Lo que se hace mal»).
- `sum`, `min` y `max` suman, buscan el menor y buscan el mayor de los números de la lista: 87 + 142 + 2300 = 2529, que es la suma de tiempos que usarás en el resumen.

Una lista puede mezclar cualquier cosa: textos, números, otras listas. En el `revisor` conviene que cada lista guarde **una sola clase de cosa** (puros nombres, o puros tiempos), porque así sabes qué esperar de cada elemento y porque las anotaciones de tipo de 4.1.5 lo expresan fácil.

Ahora, el error. Pedir una posición que no existe:

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

Lee el *traceback* como aprendiste en la Lección 1: de la última línea hacia arriba. `IndexError: list index out of range` dice que el índice está fuera del rango de la lista. Arriba, Python te señala la línea y marca con una raya de `~` y `^` la expresión que falló: `nombres[4]`. La lista tiene cuatro elementos, con posiciones de 0 a 3, y la 4 no existe. Es el mismo error que te daba la Lección 3 cuando una de las tres listas paralelas era más corta que las otras. (Python escribe en el *traceback* la ruta completa de tu archivo; en esta lección se acortan a `File "fig04_02.py"` para que el texto quede igual para todos, y en tu pantalla verás la ruta tal como está en tu computadora.)

#### 4.1.2 La tupla: un grupo fijo de valores

Una **tupla** parece una lista con paréntesis en lugar de corchetes, pero tiene una diferencia que cambia para qué sirve: **no se puede cambiar**. Una vez creada, sus posiciones quedan fijas. Y la diferencia de uso es más honda que la sintáctica: la lista es «una cantidad variable de cosas del mismo tipo» (cuatro nombres, o veinte), mientras que la tupla es «una cantidad **fija** de cosas que cada una significa algo distinto por su posición». El resultado de revisar un servicio, por ejemplo, es siempre tres cosas: el código, el tiempo y el error si lo hubo.

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

- `resultado = (200, 142, None)` crea una tupla de tres elementos. Se lee con índices igual que una lista: `resultado[0]` es el código.
- `codigo, tiempo_ms, error = resultado` **desempaqueta** (en inglés, *unpacking*), lo mismo que hacía `for i, nombre in enumerate(...)` en la Lección 3, donde cada vuelta entregaba una pareja, que en realidad es una tupla de dos: reparte los tres elementos de la tupla entre tres nombres, en orden. Es mucho más legible que `resultado[0]`, `resultado[1]`, `resultado[2]`, porque cada valor recibe un nombre que dice qué es.
- El `for nombre, ms in pares:` es el mismo desempaquetado de `enumerate`, ahora con tus propias parejas: cada elemento de `pares` es una tupla de dos, y `nombre` y `ms` reciben sus mitades. Lo vas a ver otra vez en cuanto llegues a los diccionarios.
- Una tupla de **un solo elemento** exige la coma: `(200,)` es una tupla; `(200)` son unos paréntesis alrededor de un número, y es simplemente `200`, como muestra el `type` de la última línea. [El tutorial advierte de este caso](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) como una rareza de la sintaxis. En la práctica casi no la vas a escribir, pero sí la vas a leer, y confundirla no avisa.

Si la cantidad de nombres no coincide con la de elementos, Python lo rechaza en lugar de repartir de más o de menos en silencio:

<!-- frag: desempaque.py -->
```python
codigo, tiempo_ms = (200, 142, None)
```

Al correrlo, la última línea del *traceback*, que es la que importa, dice «demasiados valores para desempaquetar». En Python 3.12:

```text
ValueError: too many values to unpack (expected 2)
```

y en 3.14 añade cuántos recibió:

```text
ValueError: too many values to unpack (expected 2, got 3)
```

Cuando una función devuelve «varias cosas», lo que devuelve es una tupla: `return codigo, tiempo_ms` crea una tupla de dos, y quien llama la desempaqueta con `codigo, tiempo_ms = f(...)`.

¿Y qué pasa si intentas cambiar una?

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

`TypeError: 'tuple' object does not support item assignment`: «el objeto tupla no admite asignar a una posición». No es un fallo, es la garantía de la tupla: lo que guardó, queda. Si necesitas otra con un valor distinto, creas otra tupla. Esa garantía es útil para datos que describen un hecho que ya ocurrió, como el resultado de una revisión. Pero fíjate en el costo: `resultado[1]` no dice que es el tiempo; solo tu memoria lo dice. Cuando una tupla crece a cinco o seis elementos, nadie recuerda cuál es cuál. Esa es la limitación que resuelve el `dataclass` de la Lección 5.

#### 4.1.3 El diccionario: valores con nombre

Piensa en lo que necesita `revisar` para el servicio `pagos`: no «el tercer elemento», sino «los datos de `pagos`». Un **diccionario** (`dict`) guarda pares **clave: valor** y se consulta por la clave. Se escribe entre llaves, y la clave y el valor van separados por dos puntos.

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

- `tiempos_ms["pagos"]` busca la clave `"pagos"` y devuelve su valor, 87. A diferencia de una lista, aquí no importa en qué lugar está: importa cómo se llama. Las claves son únicas (un diccionario no puede tener dos veces `"pagos"`); los valores pueden repetirse y ser de cualquier clase, incluso `None`, como el de `reportes`.
- `len(tiempos_ms)` cuenta los pares. `"pagos" in tiempos_ms` pregunta si **la clave** existe (no el valor), y es rápida aunque el diccionario sea enorme.
- `tiempos_ms.get("gateway")` es la forma de preguntar con calma. Con corchetes, una clave que no existe es un error (lo provocas más abajo, en «El error que vas a ver»); con `.get`, devuelve `None` si no la encuentra, o el valor que tú le pongas como segundo argumento: `.get("gateway", "sin dato")` devuelve `"sin dato"`.
- Ojo con la línea de `reportes`, que es la trampa de este método. `.get("reportes")` devuelve `None`... y `.get("gateway")` también. **La misma respuesta para dos situaciones distintas:** una clave que no existe, y una clave que existe y vale `None`. La penúltima línea lo deja a la vista: `"reportes" in tiempos_ms` es `True` pero su `.get` es `None`; `"gateway"` no está y su `.get` también es `None`. Cuando la diferencia importa, se pregunta primero con `in`.
- `tiempos_ms["facturacion"] = 95` **agrega** un par si la clave no existía (y si existía, reemplaza su valor). Los diccionarios, como las listas, se pueden cambiar.
- `tiempos_ms.items()` entrega los pares uno por uno, cada uno como una tupla `(clave, valor)` (igual que `enumerate` entregaba parejas), y el `for nombre, ms in ...` los desempaqueta, como viste en la sección anterior. Los diccionarios **recuerdan el orden en que agregaste las claves**: [la documentación lo garantiza](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) («los diccionarios preservan el orden de inserción»), por eso `facturacion` sale al final.
- `list(tiempos_ms)` convierte en lista lo que se obtiene al recorrer el diccionario directamente, y eso son **las claves**. Es importante recordarlo: `for nombre in tiempos_ms:` recorre nombres, no pares. `tiempos_ms.values()` entrega los valores, y existe `tiempos_ms.keys()` para las claves, pero casi nunca hace falta escribirlo.

Una restricción que conviene saber desde ahora: la clave de un diccionario debe ser algo que no cambie. Textos, números y tuplas de ellos sirven; una lista no sirve como clave. [El glosario le llama **hashable**](https://docs.python.org/3/glossary.html#term-hashable) a lo que puede usarse así. Intentarlo da un `TypeError: unhashable type: 'list'`, que verás en 4.1.4 junto al conjunto.

#### 4.1.4 El conjunto: «¿ya lo vi?»

Un **conjunto** (`set`) guarda valores **sin repetir y sin orden**. Sirve para dos cosas: quitar repetidos, y preguntar «¿está este valor?» muy rápido. Cuando escribes `{"catalogo", "pagos"}`, con llaves y sin dos puntos, es un conjunto.

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

- `set(registrados)` convierte la lista en un conjunto y, de paso, descarta las repeticiones: cinco nombres registrados, tres distintos. Esta es la forma más corta de contar «cuántos valores diferentes hay».
- El conjunto se imprime dentro de `sorted(...)` a propósito, y no es un adorno: **un conjunto no tiene orden**, y para los textos el orden en que Python los muestra cambia de una corrida a otra, porque [la documentación del lenguaje explica](https://docs.python.org/3/reference/datamodel.html#object.__hash__) que los valores `hash` de los textos llevan una «sal» impredecible que cambia cada vez que arranca Python. Al medirlo para esta lección, el mismo conjunto `{"catalogo", "inventario", "pagos", "reportes"}` salió en órdenes distintos de una corrida a otra, y por eso verás `sorted` en cada impresión de un conjunto: para que la salida sea siempre la misma. Regla práctica: **nunca confíes en el orden de un conjunto; si necesitas orden, conviértelo con `sorted`**.
- Los operadores entre conjuntos son los de las matemáticas: `-` es la **diferencia** (lo que está en uno y no en el otro: los que no están arriba), `&` la **intersección** (lo que está en los dos) y `|` la **unión** (todo lo de ambos). `.add` agrega un valor y no pasa nada si ya estaba, que es justo la gracia: `arriba.add("pagos")` no duplica nada.
- La última línea es una trampa clásica. **`{}` vacío no es un conjunto vacío, es un diccionario vacío**: la sintaxis de llaves se usó primero para diccionarios. Para un conjunto vacío, `set()`. [El tutorial lo remarca](https://docs.python.org/3/tutorial/datastructures.html#sets) y el `type` de arriba lo comprueba.

Los elementos de un conjunto también deben ser *hashable*, por la misma razón que las claves del diccionario: Python los coloca según un número calculado de su valor, y si el valor pudiera cambiar, ese número también. Si intentas meter una lista, el mensaje cambia entre versiones, y vale la pena ver los dos:

<!-- frag: hashable.py -->
```python
datos = {["catalogo"]: 1}
```

En Python 3.12 la última línea es esta:

```text
TypeError: unhashable type: 'list'
```

Y en 3.14, que redacta mejor el aviso, dice:

```text
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

Las dos significan lo mismo: una lista no puede ser clave. Lo que debes recordar es la palabra `unhashable`.

Un uso real en el `revisor`: detectar nombres repetidos. Un conjunto de «los que ya vi» y otro de «los que se repiten» lo resuelven en un solo recorrido. Pero esa función usa anotaciones de tipo para colecciones, que es lo siguiente.

#### 4.1.5 Anotar las colecciones y elegir la correcta

En la Lección 3 anotaste tipos simples: `int`, `str`, `int | None`. Con colecciones se agrega **de qué** es la colección, entre corchetes: `list[str]` es «lista de textos», `set[str]` es «conjunto de textos», `dict[str, int | None]` es «diccionario cuyas claves son textos y cuyos valores son enteros o `None`», y `tuple[int | None, int | None, str | None]` es «tupla de tres elementos: un entero o `None`, otro entero o `None`, y un texto o `None`» (la tupla anota **cada posición**, porque cada una significa algo). Recuerda lo que aprendiste en la Lección 0: Python **no obliga** a que las anotaciones se cumplan al ejecutar. Son documentación que alguien más puede comprobar (en la Lección 8, `mypy`); hoy sirven para que el código diga lo que espera.

Aquí está la función que detecta nombres repetidos, con anotaciones, y es la misma que usará el modelo del `revisor` en la Lección 5:

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

`vistos: set[str] = set()` anota una variable al crearla: la sintaxis es `nombre: tipo = valor`. Se necesita la anotación porque `set()` por sí solo no dice de qué es el conjunto. Para cada nombre: si ya estaba en `vistos`, se agrega a `repetidos`; en cualquier caso se agrega a `vistos`. La segunda llamada devuelve un conjunto vacío, que `sorted` muestra como `[]`. Observa que la pregunta `nombre in vistos` se hace con un conjunto: sería igual de correcta con una lista, pero con miles de nombres el conjunto responde de inmediato y la lista tendría que revisarlos uno por uno.

¿Cuál usar? Esta tabla la puedes consultar cada vez que dudes; casi siempre la respuesta sale de la primera columna.

| Si lo que guardas es... | Usa | Se busca por | ¿Se puede cambiar? | Ejemplo en el `revisor` |
|---|---|---|---|---|
| una cantidad variable de cosas del mismo tipo, en un orden | `list` | posición | sí | los servicios a revisar |
| una cantidad fija de cosas, cada posición con su significado | `tuple` | posición | no | el trío (código, tiempo, error) |
| datos que se piden por nombre | `dict` | clave | sí | el tiempo de cada servicio por su nombre |
| valores únicos, sin orden, de los que preguntas «¿está?» | `set` | pertenencia | sí | los nombres ya vistos |

Si dudas entre `list` y `set`, pregunta si importa el orden o si puede haber repetidos. Si dudas entre `dict` y `list`, pregunta si vas a buscar por posición o por nombre. Y si te descubres escribiendo `resultado[2]` y tienes que recordar qué era el 2, es la señal de que necesitas un nombre para eso, que es el tema de la Lección 5.

### 4.2 Comprensiones

Armar una lista nueva a partir de otra es de las tareas más comunes de un programa, y se escribe siempre igual: se crea una lista vacía, se recorre la original, se decide si cada elemento entra y se agrega con `.append`. Python tiene una forma compacta para eso, la **comprensión** (en inglés, *comprehension*). Mira las dos versiones del mismo trabajo:

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

La primera mitad es el bucle de siempre: crea `lentos` vacía (anotada como lista de enteros), recorre, filtra con `if` y agrega. La segunda mitad hace lo mismo en **una línea**:

```text
[ tiempo_ms   for tiempo_ms in tiempos_ms   if tiempo_ms >= 1000 ]
  ^qué pones   ^de dónde sale               ^condición (opcional)
```

Se lee casi como una frase: «arma una lista con `tiempo_ms`, para cada `tiempo_ms` en `tiempos_ms`, si `tiempo_ms >= 1000`». Tiene tres partes: **qué se pone** en la lista nueva (puede ser el mismo elemento o una transformación de él, como `f"{tiempo_ms}ms"`), **de dónde sale** (el `for`) y, opcional, **la condición** que decide si entra. [El tutorial de Python](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) la presenta con la misma estructura. La variable del `for` vive solo dentro de la comprensión y no estorba afuera.

Línea por línea del resto:

- `[f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]` no tiene condición: transforma cada número en un texto. Es una versión sencilla de lo que hacía `formatear_tiempo` en la Lección 3.
- `", ".join(textos)` es un método de texto nuevo: **une** los textos de una lista poniendo entre ellos el texto sobre el que se llama. Aquí, una coma y un espacio. Lo vas a necesitar en el resumen del `revisor`.
- Con llaves y un `clave: valor` se obtiene una **comprensión de diccionario**: `{nombre: ms for nombre, ms in por_servicio.items() if ms is not None}` construye un diccionario nuevo con los servicios que sí tienen tiempo. Fíjate en que la pregunta correcta sobre `None` sigue siendo `is not None`, como aprendiste en las lecciones 2 y 3.
- Con llaves y un solo valor se obtiene una **comprensión de conjunto**: los nombres cuyo tiempo es `None`. Solo `reportes`.
- La última línea es el promedio real del resumen. `respondieron.values()` son los tiempos de los que contestaron (142, 2300 y 87); `sum(...)` los suma (2529); `len(respondieron)` es 3; la barra `/` divide y **siempre da un número con decimales**, 843.0; y `round(...)` lo redondea al entero más cercano, 843. Todos los promedios del curso se calculan así, sobre los que respondieron: el cuarto servicio no tiene tiempo que promediar. Una nota sobre `round`: cuando el decimal es exactamente `.5`, [Python redondea al entero **par**](https://docs.python.org/3/library/functions.html#round), así que `round(0.5)` es 0, `round(1.5)` es 2 y `round(2.5)` también es 2.

<!-- frag: redondeo.py -->
```python
print(round(0.5), round(1.5), round(2.5))
```

```text
0 2 2
```

(Para el `revisor` no importa, porque 2529 / 3 es exacto, pero conviene haberlo visto una vez: es de esas cosas que, si no las sabes, te hacen buscar un error que no existe.)

¿Cuándo no usar una comprensión? Cuando se vuelve difícil de leer. Una condición sencilla o una transformación sencilla caben bien; dos `for` anidados o tres condiciones, no: en ese caso escribe el bucle, que se puede leer línea por línea. Y nunca uses una comprensión solo por lo que hace por fuera (por ejemplo, para llamar a `print` en cada elemento): una comprensión sirve para **construir un valor**, no para ejecutar acciones.

> **Aquí termina la primera sesión.** Tienes las cuatro colecciones y las comprensiones: todo lo que hace falta para **guardar** los datos de otra manera. Antes de la segunda sesión, corre de nuevo las figuras de 4.1 y 4.2 y cambia algo en cada una (otro servicio, otra condición en la comprensión) para predecir el resultado antes de verlo. La segunda sesión trata de lo que sorprende al **compartir** esos datos, y termina con el `revisor` sin listas paralelas.

### 4.3 Copia contra referencia, y no cambiar lo que se recorre

Esta sección explica el tropiezo más frecuente de quien viene de otros lenguajes, y el que más tiempo hace perder cuando no se conoce. Llega ahora porque solo tiene sentido cuando ya tienes listas y diccionarios que se pueden cambiar.

#### 4.3.1 Un nombre es una etiqueta, no una caja

Cuando escribes `a = [1, 2]`, Python hace dos cosas: **crea** la lista en algún lugar de la memoria y **pone la etiqueta `a`** en ella. La etiqueta no contiene la lista; la **señala**. Si después escribes `b = a`, no se crea una segunda lista: se pone una segunda etiqueta, `b`, en la **misma**. Hay una lista y dos nombres para ella. (En la Lección 3, al comparar `==` con `is`, viste de pasada que `c = a` no copia la lista; aquí se ve qué consecuencias tiene cuando esa lista cambia.) [La documentación oficial lo explica](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) con este mismo caso: las variables son nombres que se refieren a objetos, y asignar una variable a otra no copia el objeto.

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

- `respaldo = principales` pone una segunda etiqueta. Al hacer `respaldo.append("reportes")`, la lista **única** crece, y por eso `principales` también ya trae `reportes`. Nadie «tocó» `principales`: es la misma lista vista con otro nombre. El `is` que viste en la Lección 3 lo confirma: `principales is respaldo` es `True` (son el mismo objeto, no dos iguales).
- `principales.copy()` crea una lista **nueva** con los mismos elementos. Ahora sí hay dos: agregar `inventario` a `copia` no toca a `principales`, y `principales is copia` es `False`. Hay otras dos formas de obtener lo mismo, `list(principales)` y `principales[:]` (una rebanada completa); las tres dan una copia. Usa la que se lea más claro, y en este curso es `.copy()`.
- ¿Por qué entonces `a = 5; b = a; b = b + 1` no deja a `a` en 6? Porque `b + 1` **no cambia el 5**: crea un número nuevo, el 6, y mueve la etiqueta `b` a él. Los números y los textos son inmutables: no hay forma de cambiarlos por dentro, así que compartirlos entre dos nombres es inofensivo. La tupla también lo es, con un matiz: no deja cambiar qué hay en cada posición, pero si una posición guarda una lista, **esa lista** sí puede cambiar, y la tupla compartida «cambia» con ella (`t = ([142], 87)` seguido de `t[0].append(5)` es válido). Las tuplas del `revisor` solo guardan números, textos y `None`, así que para ellas compartir es inofensivo. El peligro está en lo **mutable**: la lista, el diccionario y el conjunto, y todo lo que los lleve dentro.

Un caso donde esto sorprende, y que ya te topaste en la Lección 3: **una función que recibe una lista recibe la lista misma, no una copia**.

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

La función no devolvió nada y sin embargo `base` cambió. Es exactamente el mecanismo de la lista que «recordaba» las llamadas anteriores (`registrar_caido`, en la Lección 3): el valor por omisión `[]` era una sola lista, creada una vez, que todas las llamadas compartían. Con lo de hoy puedes decirlo de una vez: una función que recibe una lista puede cambiarla, y eso es una decisión de diseño que hay que tomar con los ojos abiertos. La convención de Python sigue el ejemplo de `sort` y `sorted`: los métodos que **cambian** una colección (`append`, `sort`, `remove`) devuelven `None`, para que no los confundas con los que devuelven algo nuevo, y los que devuelven algo nuevo (`sorted`, `copy`) no tocan lo que recibieron. La excepción útil es `pop`, que quita un elemento y además lo devuelve.

#### 4.3.2 Copia superficial y copia profunda

`.copy()` copia la lista de afuera, pero **no copia lo que la lista guarda**: si dentro hay otras listas, la copia y la original comparten esas listas de adentro. A esto se le llama copia **superficial** (*shallow*); la alternativa es la **profunda** (*deep*), que copia también lo de adentro, y la ofrece el módulo `copy` (se trae con `import copy`, como aprendiste en la Lección 3). [Su documentación define la diferencia](https://docs.python.org/3/library/copy.html): la superficial inserta referencias a los mismos objetos; la profunda inserta copias, de forma recursiva.

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

Con la copia superficial, agregar a `superficial[1]` cambió también `grupos[1]`: las dos listas de afuera son distintas, pero la lista de adentro es **la misma**, y el `is` lo confirma. Con `copy.deepcopy`, la de adentro también se copió, y `grupos` quedó intacta. No uses `deepcopy` por reflejo: copia todo lo que alcanza, es más lento, y a veces copia de más lo que debía compartirse. Úsala cuando de verdad necesites dos estructuras anidadas independientes. En el `revisor` rara vez hará falta, porque (lo verás en la Lección 5) los datos importantes no se cambiarán: se **reemplazarán** por otros.

#### 4.3.3 No cambies lo que estás recorriendo

La última consecuencia de lo mutable es la más traicionera, porque **no da error**. Si quitas elementos de una lista mientras la recorres con `for`, el recorrido se descompone. Quita los servicios cuyo tiempo es menor que 100 ms. (Para quitar un valor de una lista se usa `.remove(valor)`, que borra la primera aparición de ese valor.)

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

Había dos valores menores que 100, el 87 y el 95, y solo se quitó el 87: el 95 se quedó. Ninguna línea falló, y el resultado es incorrecto. La razón: el `for` recorre la lista **por posición**, con un contador interno. Cuando llega a la posición 2 y ve el 87, lo quita; los elementos que venían después se corren un lugar hacia la izquierda, el 95 pasa a ocupar la posición 2, y el `for` sigue con la posición 3, que ya no existe. El 95 nunca se examina, y nadie lo avisa. [El propio tutorial de Python previene de esto](https://docs.python.org/3/tutorial/controlflow.html#for-statements): el código que modifica una colección mientras la recorre es difícil de acertar, y lo más sencillo es recorrer una copia o armar una colección nueva. Armar una colección nueva es justo lo que hace una comprensión:

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

Ahora el resultado es el correcto y, de regalo, la lista original queda como estaba. Con un diccionario, el descuido de **agregar o quitar claves** mientras lo recorres sí da error, porque Python lo detecta:

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

`RuntimeError: dictionary changed size during iteration`: «el diccionario cambió de tamaño durante el recorrido». El `for nombre in tiempos_ms` recorre las claves, y dentro agregaste una; Python lo notó y se detuvo. Fíjate en la palabra *tamaño*: cambiar el **valor** de una clave que ya existe (`tiempos_ms[nombre] = 0`) no cambia cuántas claves hay y no da error; lo que falla es agregar o borrar claves. Las soluciones son las mismas: recorrer una copia (`for nombre in list(tiempos_ms):`) o construir un diccionario nuevo con una comprensión.

#### Antes del proyecto

Antes de ir al proyecto, comprueba que puedes hacer esto sin mirar la lección; es también lo que dará fluidez a lo que sigue:

- Escribir un diccionario con los cuatro servicios y sus tiempos, leer uno con corchetes y otro con `.get`, y explicar por qué `.get` de una clave que vale `None` engaña.
- Escribir una comprensión que filtre una lista, y la misma cosa como bucle.
- Decir en voz alta qué imprime `b = a; b.append(1); print(a)` si `a` es una lista, y qué cambia si `a` es un número.
- Explicar por qué `sorted(x)` y `x.sort()` no son lo mismo.

Con eso en la mano, el proyecto de hoy se lee sin sorpresas.

### 4.4 El paso del proyecto: el `revisor` sin listas paralelas

Junta lo de hoy en el proyecto. El cambio vive entero en `revisor.py`. `formato.py` se queda exactamente como lo dejó la Lección 3, porque su trabajo (dar forma de texto a un nombre, un estado, un tiempo y un detalle) no cambió; se repite aquí solo para que la carpeta de la figura esté completa:

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

Lee `revisor.py` por partes.

**Los datos.** En lugar de las tres listas hay dos constantes. `SERVICIOS` es una **lista** de nombres: los servicios que quieres revisar, en el orden en que quieres verlos en la tabla. Es una lista porque importa el orden y porque la cantidad puede crecer. `SIMULADO` es un **diccionario** que, para cada nombre, guarda una **tupla de tres** con lo que «contestó» ese servicio: `(código, tiempo_ms, error)`. Es una tupla porque son tres cosas fijas que viajan siempre juntas y cada posición significa algo distinto, y la anotación `dict[str, tuple[int | None, int | None, str | None]]` lo dice con una posición por elemento, como viste en 4.1.5. La de `reportes` es `(None, None, "sin conexión")`: no hubo código ni tiempo, y el tercer elemento cuenta por qué. Fíjate en lo que ganaste: los tres datos de `inventario` están en **una sola línea**, bajo su nombre. Ya no hay manera de que su código quede emparejado con el tiempo de otro servicio.

¿Por qué dos constantes y no una? Porque responden preguntas distintas y van a seguir caminos distintos. `SERVICIOS` es **lo que quieres revisar**: en la Lección 6 dejará de estar escrito en el código y se leerá de un archivo. `SIMULADO` hace el papel de **la red**: es lo que cada servicio contesta mientras el programa todavía no sabe preguntar de verdad, y en la Lección 9, cuando el `revisor` consulte a cada servicio, desaparece. Separarlos ya enseña algo desde hoy: un servicio que está en `SERVICIOS` y no en `SIMULADO` es un servicio que no contestó.

**`revisar`** cambió de firma. Antes recibía el nombre, el código y el tiempo, que `main` tenía que sacar de tres listas en la misma posición; ahora recibe **solo el nombre** y busca lo demás por su cuenta. La búsqueda es `SIMULADO.get(nombre, sin_respuesta)`, con `.get` **a propósito**: un nombre que no esté en `SIMULADO` no es una equivocación del programa sino un servicio del que no hay datos, y se trata como caído «sin conexión». Por eso el valor por omisión, `sin_respuesta`, es la misma tupla que la de `reportes`. Es el criterio de 4.1.3: `.get` cuando la ausencia es un caso previsto, corchetes cuando no debería ocurrir. Después, `codigo, tiempo_ms, error = ...` desempaqueta la tupla en tres nombres (4.1.2), y el detalle se decide con la regla de la Lección 2, ampliada con el tercer dato: el código como texto si hubo respuesta; si no, el texto del error; y si tampoco hay error, «sin conexión». `clasificar` no cambió ni una letra.

**`main`** arma primero la lista de renglones con una comprensión, `[revisar(nombre) for nombre in SERVICIOS]` (4.2), y después la imprime bajo el encabezado. El recorrido ya no usa `range(len(...))` ni posiciones: recorre los nombres, uno por uno, como el primer `for` de la Lección 3. Y el orden de la tabla es el de `SERVICIOS`, no el de `SIMULADO`: quien decide qué se muestra y en qué orden es la lista de lo que quieres revisar.

Corre el proyecto desde su carpeta:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

La misma tabla de la Lección 3, como se prometió. Compárala con el ejercicio 1 de aquella lección, el de `facturacion`: allá había que tocar tres listas en el mismo orden, y un olvido producía un `IndexError` o, peor, un renglón con datos de otro servicio. Ahora un servicio es un nombre en `SERVICIOS` y una línea en `SIMULADO`, y si olvidas la línea, el servicio aparece como caído «sin conexión», que es la verdad: no hay datos de él. Lo compruebas en el ejercicio 3.

Queda algo incómodo, y es el punto de partida de la Lección 5. Mira la línea `codigo, tiempo_ms, error = SIMULADO.get(...)`: la tupla no dice qué es cada posición; solo tu memoria lo dice. Y `clasificar` sigue devolviendo un texto, `"ARRIBA"`, `"LENTO"` o `"CAIDO"`, que nada impide escribir mal. Darle a cada cosa del problema un nombre propio que Python reconozca es el tema de la siguiente lección. Allí llega también la línea del resumen (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`): ya sabrías contarla con las comprensiones de hoy, pero queda más clara cuando cada resultado sea una sola cosa con nombre.

## El error que vas a ver

En las secciones anteriores ya provocaste varios errores en el lugar donde nacen (`IndexError`, `TypeError`, `ValueError`, `RuntimeError`). Aquí va el que más vas a encontrar al trabajar con diccionarios, y al final una tabla para reconocerlos todos de un vistazo.

### `KeyError: 'catalgo'`

Pedir a un diccionario una clave que no tiene. Escribe `catalgo` en lugar de `catalogo`:

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

Léelo de abajo hacia arriba, como siempre. **La última línea:** `KeyError: 'catalgo'`. El tipo es `KeyError` (un error de clave) y el texto entre comillas es **la clave que se pidió y no existe**, tal cual la escribiste; si la comparas con las claves del diccionario, el error de dedo salta a la vista. **Una línea arriba:** el programa, con una raya de `~` y `^` bajo la expresión que falló, `SIMULADO["catalgo"]`. **Más arriba:** la línea y el archivo. Aquí no hay ninguna función en medio, así que el *traceback* es corto; con funciones llamándose entre sí, serían más renglones, y se lee igual: la causa inmediata está al final.

Dos preguntas antes de arreglarlo. La primera: ¿la clave debería existir? Si sí, es un error de dedo o de datos, y el `KeyError` es **justo lo que quieres**: el programa se detuvo en el lugar exacto de la equivocación, sin dejar que un valor falso siguiera avanzando. La segunda: ¿es normal que a veces no exista? Entonces el diccionario no se consulta con corchetes, sino con `.get(clave, valor_por_omisión)` o con un `in` previo. Esa es la razón por la que `revisar`, en 4.4, usa `.get`: un servicio que no tiene datos simulados es un caso previsto. Lo que **no** debes hacer es usar `.get` en todas partes «por si acaso»: cambia un error claro por un `None` que fallará más tarde y más lejos (la Lección 5 empieza justo con un caso así). Atrapar el error con `try`/`except` es el tema de la Lección 6.

### Los errores de esta lección de un vistazo

Cuando te aparezca uno, busca aquí la última línea. Todos salieron de las corridas de esta lección.

| La última línea dice... | Qué pasó | Dónde lo viste |
|---|---|---|
| `IndexError: list index out of range` | pediste una posición que no existe en la lista | 4.1.1 |
| `KeyError: 'catalgo'` | pediste una clave que el diccionario no tiene | arriba |
| `TypeError: 'tuple' object does not support item assignment` | quisiste cambiar un elemento de una tupla | 4.1.2 |
| `ValueError: too many values to unpack (expected 2...` | desempaquetaste en más o menos nombres que elementos | 4.1.2 |
| `TypeError: unhashable type: 'list'` | usaste una lista como clave o elemento de conjunto | 4.1.4 |
| `RuntimeError: dictionary changed size during iteration` | cambiaste el tamaño de un diccionario mientras lo recorrías | 4.3.3 |

Los textos de la tabla son los de Python 3.12, el de tu Mint. Dos cambian en 3.14, aunque el error es el mismo: el de desempaquetar agrega cuántos había, `ValueError: too many values to unpack (expected 2, got 3)`, y el de la lista como clave dice dónde la usaste: `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')` (o `as a set element`, si fue en un conjunto).

## Lo que se hace mal

Cada uno de estos descuidos tiene un costo concreto, y la mayoría no da error a la primera.

**Mantener listas paralelas.** Tres listas que se corresponden por posición se descuadran con un olvido, y el síntoma aparece lejos de la causa: un `IndexError` a la mitad de la tabla, o un renglón con el tiempo de otro servicio. El costo es el día que se pierde buscando por qué el servicio número 4 dice 87 ms. Una entrada por servicio en un diccionario, con sus datos juntos, lo evita desde el diseño.

**Guardar el resultado de `.sort()`.** `.sort()` ordena la lista que ya existe y devuelve `None`. Quien escribe `ordenados = tiempos_ms.sort()` obtiene una variable que vale `None`, y el error aparece donde se use:

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

La lista sí quedó ordenada (la segunda línea), pero `ordenados` no la contiene. Si hace falta una copia ordenada, `sorted(tiempos_ms)`; si hace falta ordenar la propia, `tiempos_ms.sort()` **sin** asignar.

**Usar `.get` para todo.** Cambia un error claro (`KeyError`, con la clave que falló) por un `None` que se propaga y revienta más tarde, en otro lado y con otro mensaje. Úsalo cuando la ausencia es un caso previsto, no para callar errores.

**Escribir `{}` esperando un conjunto vacío.** Es un diccionario vacío, y el fallo llega después, en la primera operación de conjunto:

<!-- frag: llaves_vacias.py -->
```python
vistos = {}
vistos.add("catalogo")
```

La última línea del *traceback* dice:

```text
AttributeError: 'dict' object has no attribute 'add'
```

La forma correcta es `vistos: set[str] = set()`. Un conjunto vacío se escribe con `set()`.

**Confiar en el orden de un conjunto.** Funciona «la mayoría de las veces» en las pruebas de una máquina y falla en otra, porque el orden de los textos cambia entre corridas. Si el orden importa, `sorted(...)`. Si te importa el orden de llegada, una lista o un diccionario (que sí recuerda el orden de inserción).

**Copiar con `=`.** `respaldo = principales` no hace una copia: pone un segundo nombre. El costo es modificar datos «de otro» sin darte cuenta, y que el defecto aparezca en un lugar que no tocaste. Para copiar, `.copy()`; para copiar lo que está anidado, `copy.deepcopy`.

**Cambiar una colección mientras la recorres.** Con una lista no falla y se salta elementos (4.3.3); con un diccionario, agregar o quitar claves falla con `RuntimeError`. Recorre una copia o arma una colección nueva con una comprensión.

**Comprensiones ilegibles.** Una comprensión con dos `for` y tres condiciones cabe en una línea pero no cabe en la cabeza de quien la lee. Si necesitas leerla dos veces, es un bucle. El costo es de mantenimiento: quien la toque después (tú, en tres meses) la va a reescribir.

**Una tupla larga en lugar de un nombre.** Una tupla de tres elementos se recuerda; una de seis, no, y `resultado[4]` acaba significando lo que cada quien cree. Si te descubres escribiendo un comentario para recordar qué es cada posición, es la señal de que esos datos merecen un nombre propio, que es lo que trae la Lección 5.

## Ejercicios

Intenta cada uno antes de mirar las soluciones.

### Ejercicio 1 — Predice, corre y arregla

Antes de correr nada, **escribe en papel** lo que imprime cada `print` de este programa. Después córrelo en tu carpeta `practica/` y compara con tu predicción.

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

Después, este recorrido tiene el defecto de 4.3.3, pero con valores `None`. Predice qué imprime, explica por qué sale así y corrígelo con una comprensión.

<!-- frag: ej1b.py -->
```python
tiempos_ms = [142, None, None, 87]
for tiempo_ms in tiempos_ms:
    if tiempo_ms is None:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

### Ejercicio 2 — Tres preguntas al diccionario

Con este diccionario, escribe tres comprensiones: (a) la **lista** de nombres de los servicios cuyo tiempo es 1000 ms o más; (b) un **diccionario** con el tiempo en segundos (milisegundos divididos entre 1000) de los servicios que sí respondieron; (c) el **conjunto** de nombres sin respuesta. Cuida que ninguna compare `None` con un número.

<!-- frag: ej2_datos.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
```

### Ejercicio 3 — Un servicio más, y un olvido a propósito

Trabaja sobre el `revisor` de 4.4. (a) Agrega `"facturacion"` al final de `SERVICIOS`, **sin** tocar `SIMULADO`, y antes de correr predice su renglón. (b) Ahora agrega a `SIMULADO` la entrada de `facturacion`, que contesta con el código 503 en 95 ms, y predice de nuevo. (c) Por último agrega `notificaciones` en los dos lugares; en `SIMULADO`, con `(None, None, "tiempo agotado")`, porque no logra contestar a tiempo. Predice su renglón y fíjate en cómo queda alineado. Compara cada paso con lo que pasaba en el ejercicio 1 de la Lección 3, cuando olvidabas una de las tres listas.

### Ejercicio 4 — Provoca tres errores y léelos

Abre el REPL con `python` desde tu carpeta del `revisor` (el que conociste en la Lección 1), importa `SIMULADO` con `from revisor import SIMULADO` y provoca estos tres errores, uno por uno: (a) `SIMULADO["catalgo"]`; (b) la posición 3 de una lista de tres elementos; (c) cambiar el primer elemento de la tupla de `pagos` con `SIMULADO["pagos"][0] = 500`. Para cada uno, escribe en tu bitácora la **última línea** y, con tus palabras, qué quiere decir y cómo se arregla. Una pregunta extra: ¿por qué el `import` no imprimió la tabla?

## Soluciones

### Solución 1

La primera parte:

```text
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes']
['catalogo', 'reportes']
True False
```

`a` y `b` son **el mismo objeto**: `b.append("reportes")` cambió ambos, y `a is b` es `True`. `c = list(a)` es una copia hecha **después** de que `a` ya tenía `reportes`; al quitar `"pagos"` de `c`, `a` y `b` no se enteraron, y `a is c` es `False`. La segunda parte imprime:

```text
[142, None, 87]
```

El `None` de la posición 1 se quita; la lista se corre a la izquierda, el segundo `None` pasa a la posición 1, y el `for` sigue con la posición 2, de modo que **nunca lo examina**: queda un `None` en una lista de la que querías quitarlos todos. La corrección arma una lista nueva:

<!-- frag: ej1c.py -->
```python
tiempos_ms = [142, None, None, 87]
tiempos_ms = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms is not None]
print(tiempos_ms)
```

```text
[142, 87]
```

### Solución 2

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

Tres cosas a comprobar. En (a) la condición `ms is not None and ms >= 1000` pregunta primero por `None`: `and` se detiene en cuanto una parte es falsa, así que `None >= 1000` (que fallaría con un `TypeError`) nunca llega a evaluarse. En (b) la división `ms / 1000` siempre da un número con decimales, y por eso `2.3` y no `2`. En (c) las llaves con un solo valor y sin dos puntos dan un conjunto; con un solo elemento se ve como `{'reportes'}`.

### Solución 3

(a) Con `facturacion` en `SERVICIOS` y sin entrada en `SIMULADO`, el programa **no se cae**: `.get` no encuentra el nombre, devuelve `sin_respuesta`, y el renglón nuevo es el de un servicio caído sin datos:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO          —  sin conexión
```

Compáralo con la Lección 3: allá, olvidar una lista producía un `IndexError` o, peor, corría los datos de un servicio a otro. Aquí el olvido afecta **solo** a `facturacion`, y lo que dice su renglón es cierto: no hay respuesta de él.

(b) Con `"facturacion": (503, 95, None),` en `SIMULADO`, su renglón pasa a ser `facturacion CAIDO       95ms  503`: contestó, pero con un código de error, y la primera regla de `clasificar` lo marca caído aunque haya sido rápido. El nombre tiene 11 letras y cabe en las 12 columnas, con un solo espacio de margen.

(c) Las dos constantes quedan así (con seis nombres, la lista ya no cabe en una línea de 88 caracteres y se reparte en varias, como las firmas largas de la Lección 3):

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

Y el último renglón sale así:

```text
notificacionesCAIDO          —  tiempo agotado
```

El nombre tiene 14 letras y la columna mide 12, así que se sale de su casilla y queda **pegado al estado**. Es una limitación real del formato de hoy, y la Lección 11 la resuelve calculando el ancho a partir del nombre más largo. Observa también el detalle: `tiempo agotado`, el tercer elemento de la tupla, porque no hubo código.

### Solución 4

Las tres últimas líneas, cada una medida:

```text
KeyError: 'catalgo'
```

`KeyError` con la clave pedida entre comillas: el diccionario no tiene `catalgo`. Arreglo: escribir `catalogo`, o `.get` si la ausencia es normal.

```text
IndexError: list index out of range
```

`IndexError`: una lista de tres elementos tiene las posiciones 0, 1 y 2. Arreglo: `lista[2]`, o `lista[-1]` para el último.

```text
TypeError: 'tuple' object does not support item assignment
```

`TypeError`: una tupla no se cambia por dentro. Arreglo: si de verdad cambió lo que contestó `pagos`, se guarda una tupla nueva en el diccionario, `SIMULADO["pagos"] = (500, 87, None)`; el diccionario sí se puede cambiar, la tupla no.

La pregunta extra: el `import` ejecutó `revisor.py` de arriba abajo, pero la llamada a `main()` está dentro de `if __name__ == "__main__":`, y al importar, `__name__` vale `revisor`. Es el idioma de la Lección 3 haciendo su trabajo.

## Cómo sé que lo logré

- [ ] En `~/curso-python/revisor/`, `python revisor.py` imprime el encabezado y los cuatro renglones, idénticos a los de la Lección 3 y a los de `fig04_15`.
- [ ] En tu `revisor.py` ya no existen `NOMBRES`, `CODIGOS` ni `TIEMPOS_MS`, ni ningún `range(len(...))`.
- [ ] Con `facturacion` en `SERVICIOS` y sin entrada en `SIMULADO`, su renglón dice `CAIDO` y `sin conexión`, y el programa no se cae; al agregarlo a `SIMULADO`, dice `503`.
- [ ] Para el servicio `reportes`, `.get` da `None` por dos razones posibles, y puedes decir cuáles son y cómo distinguirlas con `in`.
- [ ] Puedes explicar con tus palabras la diferencia entre `b = a` y `b = a.copy()`, entre `sorted(x)` y `x.sort()`, y por qué quitar elementos de una lista mientras la recorres se salta alguno sin avisar.
- [ ] Anotaste en la [bitácora](bitacora.md) qué te costó más: lo que anotes ahí es lo que debes repasar.

## Resumen

Responde sin mirar la lección:

1. ¿Qué pregunta responde cada colección: la lista, la tupla, el diccionario y el conjunto? ¿Cuáles se pueden cambiar?
2. ¿Qué diferencia hay entre `IndexError` y `KeyError`, y qué dice la última línea de cada uno?
3. ¿Qué devuelve `.get("reportes")` si `reportes` existe con el valor `None`? ¿Y si no existe? ¿Cómo distingues los dos casos?
4. ¿Qué tres partes tiene una comprensión? ¿Cuándo conviene dejar un bucle?
5. Si `a = [1, 2]` y haces `b = a`, ¿cuántas listas hay? ¿Qué cambia con `b = a.copy()`? ¿Y con `copy.deepcopy`?
6. ¿Por qué quitar elementos de una lista mientras la recorres se salta elementos sin dar error?
7. En el `revisor`, ¿por qué `SERVICIOS` y `SIMULADO` son dos cosas separadas, y qué le pasa a un nombre que está en la primera y no en la segunda?

## Para leer más

- [Python, «Estructuras de datos» (tutorial)](https://docs.python.org/3/tutorial/datastructures.html) — listas, tuplas, conjuntos, diccionarios y comprensiones, con más ejemplos y en el mismo orden que esta lección. En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [Python, «Tipos incorporados»](https://docs.python.org/3/library/stdtypes.html) — la referencia de cada colección: qué operaciones admite y cuáles cambian el valor en su lugar. Es para consultar, no para leer de corrido. Consultado el 7 de octubre de 2026.
- [Python, módulo `copy`](https://docs.python.org/3/library/copy.html) — la diferencia entre la copia superficial y la profunda, contada por la documentación oficial. Consultado el 7 de octubre de 2026.
- [Preguntas frecuentes de programación: «¿Por qué cambiar la lista `y` también cambió la lista `x`?»](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) — la explicación oficial de copia contra referencia, con el mismo caso de 4.3.1. Consultado el 7 de octubre de 2026.
