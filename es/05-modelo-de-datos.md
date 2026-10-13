# Lección 5 — El modelo de datos

**Tiempo:** 90 min

**Qué construyes:** el modelo del `revisor` (`Servicio`, `Estado`, `Resultado`) y su reporte completo, con tabla y resumen

**Qué aprendes:** moldes de datos con `class` y `@dataclass(frozen=True)`; `Enum`; `match` y `case`, con comodín y con guardas; el reporte con su línea de resumen

**De dónde vienes.** Traes el proyecto de la [Lección 4](04-colecciones.md): dos archivos, `formato.py` y `revisor.py`, ya sin listas paralelas. En `revisor.py`, `SERVICIOS` es la lista de nombres que quieres revisar y `SIMULADO` es un diccionario que guarda, para cada nombre, una tupla `(código, tiempo_ms, error)`. Funciona y ya no se descuadra. Pero la Lección 4 terminó con tres incomodidades anotadas. La tupla no dice qué es cada posición: el segundo elemento es el tiempo porque lo recuerdas, no porque lo diga el código. `clasificar` devuelve un texto (`"ARRIBA"`, `"LENTO"`, `"CAIDO"`) y nada impide escribir `"ARIBA"` sin que Python proteste. Y la tabla todavía no tiene su línea de resumen.

**Qué no hace esta lección.** No lee la configuración de un archivo (los cuatro servicios siguen escritos a mano; la [Lección 6](06-errores-archivos-datos.md) los saca de ahí), no atrapa errores con `try` y no define métodos propios en las clases. Tampoco consulta ninguna dirección de internet: los códigos y los tiempos siguen saliendo de `SIMULADO`.

Trabajas en tu carpeta `~/curso-python/revisor/`, con el entorno virtual activo. Los programas pequeños van, como en la Lección 4, en la subcarpeta `practica/`.

## Al terminar vas a poder

- Declarar `Servicio` y `Resultado` como `@dataclass(frozen=True)` y `Estado` como `Enum`, y explicar qué se gana contra una tupla, un diccionario o un texto suelto.
- Construir una instancia con los campos por posición o por nombre, leerlos con un punto, y fabricar otra con `replace` en lugar de cambiar la que tienes.
- Clasificar un servicio con `match` y `case`, con comodín y con guardas (`case c if c >= 400`), sin caer en la trampa del nombre que captura.
- Leer `FrozenInstanceError`, el `ValueError` de un `dataclass` con una lista como valor por omisión y el de un `Enum` al que se le pide un valor que no tiene.
- Armar el `revisor` de cuatro archivos y reproducir su tabla con el resumen `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.

## El porqué antes del cómo

Mira cómo habla hoy el `revisor` de las cosas de su problema. Un servicio es un **nombre suelto** dentro de una lista. Lo que contestó es una **tupla anónima**, `(200, 2300, None)`. Y su estado es un **texto**, `"LENTO"`. Las tres formas funcionan, y las tres tienen el mismo defecto: Python no sabe qué significan. No sabe que el segundo elemento de la tupla es un tiempo, ni que `"LENTO"` es uno de solo tres valores posibles. Para Python son una tupla y un texto como cualquier otro, y por eso un error de dedo (escribir `"ARIBA"`, o pedir `respuesta[2]` queriendo el tiempo) no falla donde ocurre: se cuela por el programa y produce una tabla equivocada sin un solo mensaje.

La solución es darle a cada cosa del problema **un nombre propio que Python reconozca**. Un servicio ya no será «un texto en una lista» sino un `Servicio`, con campos que se llaman `nombre`, `url` y `timeout_ms`; un estado ya no será un texto que se puede escribir mal, sino un `Estado.LENTO` que Python reconoce o rechaza; y lo que salió de revisar un servicio será un `Resultado`. A esa forma que le damos, en el programa, a lo que el problema trata, le llamamos aquí **el modelo de datos**. (Ojo, que no es lo mismo que la sección «Data model» de la documentación de Python, que habla de cómo funciona el lenguaje por dentro; aquí «modelo» es el nuestro.)

El camino tiene tres herramientas y un ensamble. `dataclass` (5.1) fabrica moldes de datos; `Enum` (5.2) cierra la lista de valores permitidos; `match` (5.3) decide entre muchos casos con claridad; y en 5.4 se juntan en el proyecto, que gana además su línea de resumen. Al final de la lección, el `revisor` hará esto:

```text
$ cd fig05_07
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

Es la tabla de siempre, ahora con una línea en blanco y un resumen, y producida a partir de objetos con nombre en lugar de tuplas y textos sueltos. Fíjate en que el encabezado y los cuatro renglones salen idénticos a los de las lecciones 3 y 4, y que el resumen es nuevo: para contar cuántos están arriba, cuántos lentos y cuántos caídos, y sacar el promedio, hacen falta las comprensiones de la Lección 4, ahora aplicadas a resultados que ya saben qué son.

## Los conceptos

### 5.1 Un molde para cada servicio: `class` y `@dataclass`

#### 5.1.1 Por qué la tupla y el diccionario no bastan

Con lo que ya sabes, un servicio podría ser una tupla, `("catalogo", "https://catalogo.example", 5000)`, o un diccionario, `{"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}`. La tupla, como viste en la Lección 4, no dice qué es cada posición. El diccionario sí lo dice, pero tiene otro problema: las claves son textos que escribes de memoria, y un error de dedo no se nota donde ocurre.

<!-- frag: dict_typo.py -->
```python
servicio = {"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}
print(servicio.get("nmbre"))
```

```text
None
```

Escribir `"nmbre"` en vez de `"nombre"` no rompió nada: `.get` devolvió `None`, y ese `None` se va a ir colando por el programa hasta que algo falle tres funciones después, lejos de la causa. Lo que queremos es que ese error de dedo **falle ahí mismo**, con un mensaje que lo diga. Eso lo da un tipo propio.

#### 5.1.2 Una clase como molde

Una **clase** es un molde para fabricar valores que tienen todos la misma forma. Cada valor fabricado con el molde se llama una **instancia**. Piensa en el molde de una galleta: la forma es una sola y las galletas son muchas. En el `revisor` el molde es `Servicio`, y `catalogo`, `inventario` y `pagos` son tres instancias. Aquí solo vas a usar las clases como moldes de datos: sin métodos, sin herencia (con una excepción de sintaxis que verás en 5.2). La palabra `class` seguida de un nombre y dos puntos abre el molde, y debajo, con sangría, se declara **un campo por línea**, con el formato `nombre: tipo`.

Python tiene una herramienta, el módulo `dataclasses`, que fabrica casi todo lo que un molde de datos necesita: la forma de construir cada instancia, la de mostrarla al imprimir y la de compararla con `==`. Se activa con una línea justo encima de la clase, que empieza con `@` y se llama **decorador**: es una marca que le pide a Python que procese la clase con esa herramienta antes de entregarla. [La documentación del módulo](https://docs.python.org/3/library/dataclasses.html) lo describe así: el decorador agrega los métodos generados a la clase que decora. Aquí se usa como `@dataclass(frozen=True)`, donde `frozen=True` (congelado) pide además que las instancias **no se puedan cambiar**, como una tupla. Guarda esto como `fig05_01.py`:

```python
# fig05_01.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
notificaciones = Servicio(
    nombre="notificaciones",
    url="https://notificaciones.example",
    timeout_ms=1000,
)
print(catalogo)
print(notificaciones.timeout_ms)
print(catalogo.nombre, catalogo.timeout_ms)

igual = Servicio("catalogo", "https://catalogo.example")
print(catalogo == igual, catalogo is igual)

raro = Servicio(nombre=5, url=None)
print(raro)
```

```text
$ python fig05_01.py
Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)
1000
catalogo 5000
True False
Servicio(nombre=5, url=None, timeout_ms=5000)
```

- `from dataclasses import dataclass` trae del módulo `dataclasses` solo la herramienta que necesitas, con la forma `from ... import` de la Lección 3.
- Las dos líneas en blanco antes y después de la clase son convención de estilo ([PEP 8](https://peps.python.org/pep-0008/#blank-lines)), no sintaxis; el formateador que verás en la Lección 8 las exige.
- `nombre: str` y `url: str` declaran dos campos de texto. `timeout_ms: int = 5000` declara un campo entero con **valor por omisión**: si al construir no lo das, vale 5000, el tiempo límite de `httpx` que usará el `revisor` más adelante. Los campos con valor por omisión van **al final**, igual que los parámetros con valor por omisión de una función.
- `Servicio("catalogo", "https://catalogo.example")` **construye** una instancia: se llama al molde como si fuera una función, con los campos en el orden en que se declararon. También se puede dar cada campo por su nombre, como en `notificaciones`, que además cambia el tiempo límite a 1000. Por nombre se lee mejor cuando son más de dos o tres campos.
- `print(catalogo)` muestra `Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)`: la forma de imprimir también la generó `dataclass`, y por eso una instancia que imprimes durante una depuración se entiende sola. Con una tupla sin nombres habrías visto `('catalogo', 'https://catalogo.example', 5000)`.
- `catalogo.timeout_ms` lee un campo con un punto. Si escribes mal el nombre (`catalogo.timeout`), Python falla ahí mismo con `AttributeError`, que es lo que queríamos.
- `catalogo == igual` es `True` porque `==` compara **campo por campo**: son dos instancias separadas con los mismos datos. `catalogo is igual` es `False` porque son dos objetos distintos. Es el `==` contra `is` de la Lección 3, con un caso real: `==` pregunta «¿valen lo mismo?», `is` pregunta «¿son la misma cosa?».
- Las dos últimas líneas son para que no te confíes. `Servicio(nombre=5, url=None)` **se construye sin protestar**, aunque `nombre` debería ser texto y `url` también. Es lo que aprendiste en la Lección 0: las anotaciones no se imponen al ejecutar. `dataclass` usa las anotaciones solo para saber qué campos hay y en qué orden: [la documentación aclara](https://docs.python.org/3/library/dataclasses.html) que, salvo dos excepciones que no usarás, nada en el decorador examina el tipo anotado. Quien sí las comprueba es una herramienta aparte, `mypy`, en la Lección 8.

#### 5.1.3 Congelado: para cambiar, se crea otro

¿Qué hace `frozen=True`? Prohíbe asignar a un campo. Mira lo que pasa si lo intentas:

<!-- frag: congelado.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
catalogo.timeout_ms = 1000
```

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

De este *traceback* se muestra solo la última línea, que es la que importa: entre medias pasa por un renglón que `dataclasses` genera por dentro y que no es igual en 3.12 y en 3.14. Dice «no se puede asignar al campo `timeout_ms`». Como con la tupla, es una garantía y no un fallo. [La documentación](https://docs.python.org/3/library/dataclasses.html#frozen-instances) la llama emulación de instancias de solo lectura.

¿Por qué querrías eso? Porque el resultado de revisar un servicio es un **hecho**: «a las 10:42, `inventario` tardó 2300 ms». Nadie debería poder corregirlo después sin dejar rastro. Y porque, cuando en las lecciones 9 y 10 varias tareas lean los mismos servicios a la vez, que ninguna pueda cambiarlos evita toda una clase de errores. Y si de verdad necesitas otra versión de un servicio, no la editas: **fabricas otra** con `dataclasses.replace`, que copia una instancia cambiando solo los campos que le indiques:

```python
# fig05_02.py
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
catalogo_corto = replace(catalogo, timeout_ms=1000)
print(catalogo.timeout_ms, catalogo_corto.timeout_ms)

repetido = Servicio("catalogo", "https://catalogo.example")
print(len({catalogo, repetido}))
```

```text
$ python fig05_02.py
5000 1000
1
```

`replace` no tocó a `catalogo`: devolvió `catalogo_corto`, una instancia nueva. Y la última línea muestra otra ventaja de lo inmutable: una instancia congelada se puede poner en un **conjunto** (o ser clave de un diccionario), porque ya no cambia: es *hashable* en el sentido de la Lección 4 (4.1.4), **siempre que todos sus campos lo sean**. Python calcula su huella a partir de los campos, y los de `Servicio` son textos y enteros. Dos instancias iguales cuentan como una sola: `{catalogo, repetido}` tiene un elemento.

Una advertencia que conecta con la copia contra referencia de la Lección 4: `frozen` prohíbe reasignar el **campo**, pero no vuelve inmutable lo que el campo contiene. Un campo que guarde una lista sigue pudiendo cambiar por dentro (`servicio.etiquetas.append(...)`), porque la lista sigue siendo mutable. Y tiene un segundo efecto: una instancia así ya no se puede meter en un conjunto, porque la huella se calcula con todos los campos y una lista no tiene huella; el intento falla con `TypeError: unhashable type: 'list'` (en 3.14 el texto agrega `cannot use ... as a set element`). Por eso en el `revisor` los campos son de tipos inmutables: textos, enteros, `None`.

### 5.2 `Enum`: una lista cerrada de valores

Mira otro problema parecido. `clasificar` de la Lección 3 devuelve el texto `"ARRIBA"`, `"LENTO"` o `"CAIDO"`, y quien lo usa compara contra textos. Si se escribe uno mal:

<!-- frag: estado_typo.py -->
```python
estado = "ARIBA"
if estado == "ARRIBA":
    print("el servicio está arriba")
else:
    print("el servicio NO está arriba")
```

```text
el servicio NO está arriba
```

El programa no falló: dijo que el servicio **no** estaba arriba, cuando lo que pasó es que alguien escribió una R de menos. Es el mismo error de dedo de 5.1.1, ahora en un valor. Lo que hace falta es una lista **cerrada** de valores permitidos, con nombres que Python reconozca, y eso es un `Enum` (de «enumeración»). [El módulo `enum`](https://docs.python.org/3/library/enum.html) lo define como un conjunto de nombres simbólicos ligados a valores únicos.

```python
# fig05_03.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


estado = Estado.LENTO
print(estado)
print(estado.name, estado.value)
print(Estado("CAIDO"))
print(estado is Estado.LENTO, estado == "LENTO")
for posible in Estado:
    print(posible.value)
```

```text
$ python fig05_03.py
Estado.LENTO
LENTO LENTO
Estado.CAIDO
True False
ARRIBA
LENTO
CAIDO
```

- `class Estado(Enum):` abre un molde, igual que `Servicio`, pero con `(Enum)` entre paréntesis: así se le dice a Python «este molde se basa en `Enum`», o sea, que es una enumeración. Los paréntesis después del nombre significan «esta clase parte de aquella otra». En el código que escribes en este curso solo los verás con `Enum` y, en la Lección 6, con `Exception` (el laboratorio de la Lección 9 también los usa, pero ese programa lo corres sin escribirlo); para lo que necesitas basta con leerlo como «una clase de la familia `Enum`».
- Dentro hay una línea por **miembro**: `ARRIBA = "ARRIBA"` da el nombre del miembro (a la izquierda, siempre en mayúsculas por convención) y su **valor** (a la derecha). Aquí el valor es el mismo texto que se imprime en la tabla, sin acento y en mayúsculas, que es también como lo guardará el JSON de la Lección 6.
- `Estado.LENTO` es un miembro. `print` lo muestra con el nombre de su clase delante: `Estado.LENTO`. `.name` es su nombre (`LENTO`) y `.value` su valor (`LENTO`). Cuando el reporte quiere la palabra para la tabla, usa `.value`.
- `Estado("CAIDO")` va en sentido contrario: busca el miembro cuyo **valor** es ese texto. Si no hay ninguno, falla en el acto (lo ves en un momento).
- `estado is Estado.LENTO` es `True`: [los miembros se comparan por identidad](https://docs.python.org/3/howto/enum.html#comparisons), y cada miembro existe una sola vez. Y `estado == "LENTO"` es **`False`**: el miembro `Estado.LENTO` y el texto `"LENTO"` son cosas distintas, aunque se impriman casi igual. Esto sorprende a casi todos la primera vez. Se compara siempre contra miembros (`estado == Estado.LENTO`), nunca contra el texto.
- `for posible in Estado:` recorre los miembros en el orden en que se declararon.

Ahora el error de dedo, en sus dos variantes. Escribir `Estado.ARIBA` falla al instante, en el punto exacto del error:

<!-- frag: enum_typo.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


print(Estado.ARIBA)
```

La última línea del *traceback* es:

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

Python incluso adivina lo que querías escribir. Lo que importa es que el error ocurre en la línea del dedo y no tres funciones después. Y buscar por valor un texto que no existe:

<!-- frag: enum_valor.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


Estado("ROTO")
```

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError: 'ROTO' is not a valid Estado`. Los dos errores dicen lo mismo con palabras distintas: «ese miembro no existe». Fíjate que son exactamente el tipo de fallo que queríamos: temprano, claro y con el nombre del culpable.

### 5.3 `match` y `case`: decidir entre muchos casos

La Lección 2 te enseñó `if`/`elif`/`else`. Cuando las ramas son muchas y todas preguntan por el **mismo valor**, una cadena larga de `elif` se vuelve difícil de leer, y para eso Python trae, desde la versión 3.10, la instrucción `match`. Es muy poderosa (la [documentación oficial](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement) le dedica una sección entera, y el [PEP 636](https://peps.python.org/pep-0636/) es un tutorial), pero aquí vas a usar solo su parte más sencilla. Mira primero una función que describe un código de estado, y que no es todavía la del `revisor`:

```python
# fig05_04.py
def describir(codigo: int | None) -> str:
    match codigo:
        case None:
            return "sin respuesta"
        case 200:
            return "todo bien"
        case 301 | 302:
            return "redirección"
        case 404:
            return "no existe"
        case c if c >= 500:
            return f"falla del servidor ({c})"
        case c if c >= 400:
            return f"error del cliente ({c})"
        case _:
            return "otro"


for codigo in [None, 200, 302, 404, 418, 503, 100]:
    print(codigo, "->", describir(codigo))
```

```text
$ python fig05_04.py
None -> sin respuesta
200 -> todo bien
302 -> redirección
404 -> no existe
418 -> error del cliente (418)
503 -> falla del servidor (503)
100 -> otro
```

Cómo se lee:

- `match codigo:` dice «voy a comparar este valor» (el **sujeto**). Cada `case` debajo es un **patrón** con el que Python lo prueba, **de arriba abajo**, y se queda con **el primero que encaje**: ejecuta su bloque y no mira los demás. Por eso el orden importa.
- `case None`, `case 200`, `case 404` son patrones **literales**: encajan si el sujeto vale eso. El primero pregunta por `None` con identidad, como te enseñaron en la Lección 2, y los demás con igualdad.
- `case 301 | 302` es **uno u otro**: la barra vertical significa «o». Encaja con cualquiera de los dos códigos.
- `case c if c >= 500` es el que merece atención. Primero `c` es un patrón de **captura**: un nombre suelto encaja con *cualquier* cosa y, de paso, guarda el sujeto en esa variable, así que dentro del bloque `c` vale el código. Después, `if c >= 500` es una **guarda**: una condición extra que debe cumplirse para que el caso valga. Si no se cumple, Python sigue con el siguiente `case`. [La documentación](https://docs.python.org/3/reference/compound_stmts.html#guards) lo describe así: si el patrón falla, la guarda ni se evalúa; si encaja, se evalúa la guarda, y el caso se elige solo si esta es verdadera. Por eso el 418 pasa de largo el caso de 500 (es menor) y cae en el siguiente, `c >= 400`.
- `case _:` es el **comodín**: el guion bajo encaja con todo y no guarda nada. Va al final y recoge lo que ningún caso anterior atrapó (aquí, el 100).

La clasificación completa de los servicios del `revisor` son cuatro reglas, que ya conoces de la Lección 2: sin código es caído; código de 400 o más es caído; si respondió y tardó 1000 ms o más es lento; si no, está arriba. Se escribe con el mismo molde, y devuelve miembros de `Estado` en lugar de textos. Esto es lo que quedará en `modelo.py`:

```python
def clasificar(
    codigo: int | None,
    tiempo_ms: int | None,
    umbral_ms: int = UMBRAL_LENTO_MS,
) -> Estado:
    match codigo:
        case None:
            return Estado.CAIDO
        case c if c >= 400:
            return Estado.CAIDO
        case _:
            if tiempo_ms is not None and tiempo_ms >= umbral_ms:
                return Estado.LENTO
            return Estado.ARRIBA
```

Léela de arriba abajo, que es como lo hace Python. El primer `case` atrapa «sin código» y el segundo, con su guarda, atrapa «código de 400 o más»: las dos primeras reglas, y las dos dan `CAIDO`. Lo que llega al `case _` ya sabemos que respondió bien (hay código y es menor que 400), y ahí solo queda decidir entre las otras dos reglas con un `if` de la Lección 2: si el tiempo existe y es al menos el umbral, `LENTO`; si no, `ARRIBA`. Comprobar `tiempo_ms is not None` antes de comparar es necesario porque un código puede existir sin tiempo, y comparar `None >= 1000` falla con un `TypeError`. Observa también que el orden de los casos **es** la lógica: si pusieras el caso del 400 antes que el de `None`, `None >= 400` fallaría. En el proyecto de 5.4 la función vive en `modelo.py`, junto a las clases que definiste en 5.1 y 5.2.

Ahora la trampa más famosa de `match`. En un patrón, **un nombre suelto no compara, captura**. Si quieres comparar contra una constante, no basta con escribir su nombre:

```python
# fig05_05.py
LIMITE = 400


def es_error(codigo: int) -> bool:
    match codigo:
        case LIMITE:
            return True
        case _:
            return False
```

```text
$ python fig05_05.py
  File "fig05_05.py", line 7
    case LIMITE:
         ^^^^^^
SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable
```

Este programa **ni siquiera arranca**: Python lo rechaza al leerlo, con un `SyntaxError`. `case LIMITE:` no pregunta «¿el código vale 400?»; dice «cualquier cosa encaja, y guárdala en una variable llamada `LIMITE`». Como encaja con todo, el `case _` de abajo nunca se alcanzaría, y por eso el mensaje dice `name capture 'LIMITE' makes remaining patterns unreachable` («la captura del nombre deja inalcanzables los patrones restantes»). Python solo avisa porque después de `case LIMITE:` hay otro caso. Si `case LIMITE:` fuera el último, no avisaría de nada: [la documentación](https://docs.python.org/3/reference/compound_stmts.html#irrefutable-case-blocks) permite un caso que encaja siempre (lo llama irrefutable) siempre que vaya al final, y el programa correría con un comodín disfrazado de constante, devolviendo `True` para cualquier código. Puedes comprobarlo: con un `case LIMITE:` al final, `es_error(5)` devuelve `True`. La regla práctica: para comparar contra una constante, se usa un nombre **con punto**, como `Estado.CAIDO`; el punto le dice a Python que es un valor y no un nombre nuevo, y [los llama patrones de valor](https://docs.python.org/3/reference/compound_stmts.html#value-patterns).

```python
# fig05_06.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


def semaforo(estado: Estado) -> str:
    match estado:
        case Estado.ARRIBA:
            return "verde"
        case Estado.LENTO:
            return "amarillo"
        case Estado.CAIDO:
            return "rojo"


for estado in Estado:
    print(estado.value, "->", semaforo(estado))
```

```text
$ python fig05_06.py
ARRIBA -> verde
LENTO -> amarillo
CAIDO -> rojo
```

Aquí `Estado.ARRIBA` lleva punto, así que compara. Es el uso más natural de `match` junto a un `Enum`: un caso por miembro, sin comodín. Y trae una ventaja que `mypy` aprovecha en la Lección 8: si algún día agregas un miembro nuevo a `Estado` y olvidas su `case`, el verificador de tipos lo señala.

### 5.4 Armar el `revisor`

Junta todo en el proyecto. Al terminar tendrás cuatro archivos en `~/curso-python/revisor/`: `modelo.py` (nuevo), `revision.py` (nuevo), `formato.py` (cambia) y `revisor.py` (cambia). Cada archivo tiene una razón de existir: `modelo.py` dice **qué cosas hay** (el servicio, el estado, el resultado) y cómo se clasifica; `revision.py` **revisa** un servicio; `formato.py` **le da forma de texto** a un resultado, y `revisor.py` es el punto de entrada que los junta.

El primero es el modelo:

```python
# fig05_07/modelo.py
from dataclasses import dataclass
from enum import Enum

UMBRAL_LENTO_MS = 1000


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


@dataclass(frozen=True)
class Resultado:
    servicio: Servicio
    estado: Estado
    tiempo_ms: int | None
    detalle: str


def clasificar(
    codigo: int | None,
    tiempo_ms: int | None,
    umbral_ms: int = UMBRAL_LENTO_MS,
) -> Estado:
    match codigo:
        case None:
            return Estado.CAIDO
        case c if c >= 400:
            return Estado.CAIDO
        case _:
            if tiempo_ms is not None and tiempo_ms >= umbral_ms:
                return Estado.LENTO
            return Estado.ARRIBA


def nombres_repetidos(servicios: list[Servicio]) -> set[str]:
    vistos: set[str] = set()
    repetidos: set[str] = set()
    for servicio in servicios:
        if servicio.nombre in vistos:
            repetidos.add(servicio.nombre)
        vistos.add(servicio.nombre)
    return repetidos
```

```python
# fig05_07/revision.py
from modelo import Resultado, Servicio, clasificar

SIMULADO: dict[str, tuple[int | None, int | None, str | None]] = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}


def revisar(servicio: Servicio) -> Resultado:
    sin_respuesta = (None, None, "sin conexión")
    codigo, tiempo_ms, error = SIMULADO.get(servicio.nombre, sin_respuesta)
    if codigo is not None:
        detalle = str(codigo)
    elif error is not None:
        detalle = error
    else:
        detalle = "sin conexión"
    estado = clasificar(codigo, tiempo_ms)
    return Resultado(servicio, estado, tiempo_ms, detalle)


def revisar_todos(servicios: list[Servicio]) -> list[Resultado]:
    return [revisar(servicio) for servicio in servicios]
```

```python
# fig05_07/formato.py
from modelo import Estado, Resultado


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(resultado: Resultado) -> str:
    nombre = resultado.servicio.nombre
    estado = resultado.estado.value
    tiempo = formatear_tiempo(resultado.tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {resultado.detalle}"


def contar(cantidad: int, palabra: str) -> str:
    if cantidad == 1:
        return f"{cantidad} {palabra}"
    return f"{cantidad} {palabra}s"


def resumen(resultados: list[Resultado]) -> str:
    total = len(resultados)
    arriba = len([r for r in resultados if r.estado == Estado.ARRIBA])
    lentos = len([r for r in resultados if r.estado == Estado.LENTO])
    caidos = len([r for r in resultados if r.estado == Estado.CAIDO])
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    partes = [
        contar(total, "servicio"),
        f"{arriba} arriba",
        contar(lentos, "lento"),
        contar(caidos, "caído"),
        f"promedio {formatear_tiempo(promedio_ms)}",
    ]
    return " · ".join(partes)
```

```python
# fig05_07/revisor.py
from formato import encabezado, linea, resumen
from modelo import Servicio
from revision import revisar_todos

SERVICIOS: list[Servicio] = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("inventario", "https://inventario.example"),
    Servicio("pagos", "https://pagos.example"),
    Servicio("reportes", "https://reportes.example"),
]


def main() -> None:
    resultados = revisar_todos(SERVICIOS)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

Las cuatro piezas, una por una.

**`modelo.py`.** Reúne todo lo de las secciones 5.1 a 5.3. Las constantes y las clases van arriba, porque `clasificar` las usa. `Resultado` es un segundo molde que ya no guarda textos sueltos: guarda **un `Servicio`** (el que se revisó), **un `Estado`**, el tiempo (`int | None`, porque un servicio caído no tiene) y el detalle. Observa la composición: un molde puede tener campos cuyo tipo es otro molde. `clasificar` es la que escribiste en 5.3, solo que la lista de parámetros se reparte en renglones porque la línea del `def` no cabe en los 88 caracteres que pide el estilo (la coma al final de la lista de parámetros es parte de esa forma de acomodar). Y `nombres_repetidos` es la de la Lección 4 (4.1.5), solo que ahora recibe una lista de `Servicio` y mira el campo `servicio.nombre`.

**`revision.py`.** Es un módulo nuevo, pero su contenido no lo es: `SIMULADO` es el diccionario de la Lección 4, que deja `revisor.py` y se muda aquí, con la misma tupla de tres `(código, tiempo_ms, error)` para cada nombre. `revisar` cambia de firma otra vez: ahora recibe un `Servicio` y devuelve un `Resultado`, en lugar de recibir un nombre y devolver un renglón ya armado. Lo de adentro es lo que ya conoces: busca con `.get` (un nombre que no esté en `SIMULADO` es un servicio sin datos, y sale caído «sin conexión»), desempaqueta la tupla en tres nombres, decide el `detalle` con la misma regla (el código como texto si hubo respuesta, y si no, el texto del error), clasifica y devuelve un `Resultado`. Que `revisar` ya no arme el renglón es la separación que buscábamos: revisar es una cosa y mostrar es otra, y cada una vive en su módulo. `revisar_todos` es una comprensión: una lista de `Resultado`, uno por servicio, en el mismo orden. Cuando en la Lección 9 el programa consulte de verdad, `SIMULADO` desaparece y `revisar` sigue devolviendo lo mismo.

**`formato.py`.** `formatear_tiempo` y `encabezado` quedan como en las lecciones 3 y 4. (Si los escribiste de otra forma pero la salida era la misma, déjalos como están.) Lo que cambia es `linea`, que **cambia de firma**: antes recibía cuatro valores sueltos y ahora recibe un solo `Resultado`, y saca de él lo que necesita. Eso es lo que buscábamos: ya no hay que pasar cuatro cosas en el orden correcto. Las dos funciones nuevas son `contar` y `resumen`. `contar` agrega una «s» cuando la cantidad no es uno: `contar(1, "caído")` da `1 caído` y `contar(3, "caído")` da `3 caídos`. `resumen` cuenta el total con `len`, usa tres comprensiones para contar cuántos hay de cada estado, saca con una cuarta los tiempos de los que respondieron, calcula el promedio **solo si hay alguno** (con `len(tiempos_ms) > 0`, porque dividir entre cero fallaría) y junta las partes con `" · ".join(partes)`. La anotación `promedio_ms: int | None = None` dice que empieza sin valor y que puede acabar siendo un entero; si ningún servicio respondió, el resumen dice `promedio —`.

**`revisor.py`.** `SERVICIOS` deja de ser una lista de nombres y pasa a ser una **lista de `Servicio`**: los cuatro canónicos, escritos a mano, cada uno con su nombre y su dirección (el tiempo límite se queda en el valor por omisión). Para agregar un servicio escribes un `Servicio(...)` y, mientras los datos sean simulados, su línea en `SIMULADO`, igual que en la Lección 4. `main` revisa todos, imprime el encabezado, un renglón por resultado, una línea en blanco (la que `print()` sin argumentos escribe) y el resumen. Los `from ... import` funcionan porque los cuatro archivos están en la misma carpeta, como en la Lección 3.

Corre el proyecto desde su carpeta:

```text
$ cd fig05_07
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

Es la tabla de las lecciones 3 y 4, con una línea en blanco y el resumen. Si las columnas no te salen alineadas, el culpable casi siempre es un espacio de más o de menos dentro de una de las f-strings; revisa que sean idénticas a las del texto. Y si el resumen cuenta mal, compara cada comprensión con la de la lección: las tres que cuentan estados solo cambian el miembro de `Estado`.

Con esto el `revisor` tiene ya su **modelo**: el `Servicio` que se revisa, el `Estado` en que queda y el `Resultado` que une las dos cosas con lo medido. Pero hay algo que sigue incómodo, y lo vas a sentir en el ejercicio 1: la lista de servicios está **dentro del código**. Para revisar otro servicio hay que abrir `revisor.py` y editar. La [Lección 6](06-errores-archivos-datos.md) lo saca a un archivo de configuración, y con él llegan los errores que merecen su propia lección.

## El error que vas a ver

En las secciones anteriores ya provocaste varios errores en el lugar donde nacen (`FrozenInstanceError`, `AttributeError`, `ValueError`, `SyntaxError`). Aquí va el que más vas a encontrar al escribir moldes con `dataclass`, y al final una tabla para reconocerlos todos de un vistazo.

### `ValueError: mutable default <class 'list'> for field ... is not allowed`

Es el mismo problema del argumento mutable por omisión de la Lección 3, ahora en un campo de `dataclass`. Si le pones una lista como valor por omisión:

<!-- frag: lista_defecto.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    etiquetas: list[str] = []
```

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

La última línea dice: «un valor por omisión mutable (`list`) para el campo `etiquetas` no está permitido: usa `default_factory`». (Aquí también se muestra solo la última línea: entre ella y tu archivo el *traceback* pasa por renglones internos de `dataclasses.py` que cambian entre una versión de Python y otra, y no te ayudan a leer el error. Lo que cuenta es el tipo, `ValueError`, y el mensaje, que además te dice cómo arreglarlo.) Python te protege de algo que en una función normal pasaba en silencio: una sola lista compartida por todas las instancias. La solución es una **fábrica**: en lugar de «esta lista», dices «llama a `list` cada vez que haga falta una nueva».

```python
# fig05_08.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Servicio:
    nombre: str
    etiquetas: list[str] = field(default_factory=list)


catalogo = Servicio("catalogo")
pagos = Servicio("pagos")
catalogo.etiquetas.append("critico")
print(catalogo.etiquetas, pagos.etiquetas)
```

```text
$ python fig05_08.py
['critico'] []
```

Cada instancia tiene su propia lista, y por eso `pagos` no se enteró de la etiqueta de `catalogo`. De paso se ve lo que se avisó en 5.1.3: la instancia está congelada, y aun así `catalogo.etiquetas.append(...)` funcionó, porque `frozen` impide reasignar el campo, no cambiar la lista que contiene. Por eso en el `revisor` no se usan listas como campos.

### Los errores de esta lección de un vistazo

Cuando te aparezca uno, busca aquí la última línea. Todos salieron de las corridas de esta lección.

| La última línea dice... | Qué pasó | Dónde lo viste |
|---|---|---|
| `dataclasses.FrozenInstanceError: cannot assign to field '...'` | intentaste asignar a un campo de una instancia congelada | 5.1.3 |
| `ValueError: mutable default ... use default_factory` | pusiste una lista como valor por omisión de un campo | arriba |
| `AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?` | pediste un miembro de `Enum` que no existe | 5.2 |
| `ValueError: 'ROTO' is not a valid Estado` | buscaste por valor un miembro que no existe | 5.2 |
| `SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable` | escribiste un nombre suelto donde querías comparar | 5.3 |

## Lo que se hace mal

Cada uno de estos descuidos tiene un costo concreto, y la mayoría no da error a la primera.

**Guardar un registro en un diccionario o en una tupla cuando ya tienes un molde.** Una tupla de seis elementos obliga a recordar cuál es cuál; un diccionario con claves de texto convierte los errores de dedo en `None`s lejanos. Si los datos tienen una forma fija, esa forma merece un nombre: `@dataclass`.

**Creer que un `dataclass` valida sus campos.** `Servicio(nombre=5, url=None)` se construye sin protestar (5.1.2): las anotaciones dicen qué esperas, pero no lo comprueban al ejecutar. El costo es un dato malo que viaja por todo el programa hasta que falla lejos. Lo que llega de fuera se valida al entrar, y eso es la Lección 6.

**Dejar textos sueltos donde ya hay un `Enum`.** Este es el más traicionero. Si cambias `clasificar` para que devuelva `Estado.LENTO` pero en otra parte del programa queda un `if estado == "LENTO"`, esa comparación **nunca será verdadera** (5.2: un miembro no es igual a su texto), y el programa seguirá corriendo sin avisar. Cuando migres de textos a un `Enum`, busca todos los lugares que comparan.

**Escribir `case NOMBRE:` queriendo comparar.** Captura, no compara. Si quieres comparar contra una constante, usa un nombre con punto (`Estado.CAIDO`) o una guarda (`case c if c == LIMITE`).

**Poner una colección mutable como campo de un molde congelado.** `frozen` protege el campo, no lo que el campo contiene: una lista guardada en una instancia congelada se puede seguir cambiando por dentro (`fig05_08.py`). El costo es una garantía que parece existir y no existe. En el `revisor` los campos son textos, enteros, `None` y otros moldes congelados.

**Construir instancias por posición cuando son muchos campos.** `Servicio("notificaciones", "https://notificaciones.example", 1000)` se lee; con seis campos, nadie sabe cuál es el cuarto. Con más de dos o tres, por nombre: `Servicio(nombre=..., url=..., timeout_ms=...)`.

## Ejercicios

Intenta cada uno antes de mirar las soluciones.

### Ejercicio 1 — Dos servicios más, y un promedio solo de los que están arriba

(a) Agrega los dos servicios extra del `revisor` a la versión de 5.4: `facturacion` (responde con código 503 en 95 ms) y `notificaciones` (con tiempo límite de 1000 ms, no logra respuesta: «tiempo agotado»). Tienes que tocar **dos** lugares. Antes de correr, predice las dos últimas líneas de la salida: la del renglón de `notificaciones` y el resumen. (b) Agrega al final de `main` una línea que imprima el promedio de los tiempos de los servicios `ARRIBA` solamente, sin redondear. Lo conveniente es hacerlo con una comprensión.

### Ejercicio 2 — Provoca cuatro errores y léelos

Abre el REPL con `python` desde tu carpeta del `revisor`, importa lo que haga falta de `modelo` y provoca estos cuatro errores, uno por uno: (a) asignar `timeout_ms` a una instancia de `Servicio`; (b) `Estado("ROTO")`; (c) `Estado.ARIBA`; (d) en un archivo de tu carpeta `practica/`, un `dataclass` con un campo `etiquetas: list[str] = []`. Para cada uno, escribe en tu bitácora la **última línea** y, con tus palabras, qué quiere decir y cómo se arregla.

### Ejercicio 3 — Un código sin tiempo

¿Qué devuelve `clasificar(200, None)`, es decir, un servicio que contestó con 200 pero del que no hay tiempo medido? Predícelo dos veces: con la `clasificar` de la Lección 3 (la que devuelve textos) y con la de hoy (la de `match`). Después compruébalo desde tu carpeta del `revisor`, con `from modelo import clasificar`. ¿Por qué la regla da ese resultado y no `LENTO`? Y por último: ¿qué pasaría si quitaras de la condición la parte `tiempo_ms is not None`?

## Soluciones

### Solución 1

(a) En `revision.py`, `SIMULADO` gana dos líneas:

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

Y en `revisor.py`, `SERVICIOS` gana dos servicios:

```python
    Servicio("reportes", "https://reportes.example"),
    Servicio("facturacion", "https://facturacion.example"),
    Servicio("notificaciones", "https://notificaciones.example", timeout_ms=1000),
]
```

La salida completa:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms
```

El resumen es `6 servicios · 2 arriba · 1 lento · 3 caídos`, y el promedio sale 656 ms porque lo calculan los **cuatro que tuvieron tiempo** (142, 2300, 87 y 95, que suman 2624, entre 4). Observa que `facturacion` cuenta en el promedio aunque esté caído: respondió, con un 503 y 95 ms. `notificaciones` no tiene tiempo y no cuenta. Observa también el renglón de `notificaciones`: es el mismo desborde que viste en la Lección 4, con el nombre pegado al estado porque mide 14 letras y la columna 12; la Lección 11 lo resuelve calculando el ancho a partir del nombre más largo. Y la tercera observación es la que da pie a la siguiente lección: para revisar dos servicios más tuviste que **editar el código**, en dos archivos.

(b) Se importa `Estado` y se agrega la comprensión al final de `main`:

```python
from modelo import Estado, Servicio
```

```python
    print(resumen(resultados))
    tiempos_arriba = [
        r.tiempo_ms
        for r in resultados
        if r.estado == Estado.ARRIBA and r.tiempo_ms is not None
    ]
    print(sum(tiempos_arriba) / len(tiempos_arriba))
```

La última línea de la salida es:

```text
114.5
```

(142 y 87 suman 229, entre 2 son 114.5.) La condición `r.tiempo_ms is not None` no es un adorno. Un servicio `ARRIBA` puede no tener tiempo: `clasificar(200, None)` devuelve `Estado.ARRIBA`, porque sin tiempo medido no hay evidencia de lentitud. Si ese `None` llegara a `sum`, el programa fallaría con un `TypeError`. Y además `tiempo_ms` está anotado como `int | None`, y quien lea el código (o `mypy`, en la Lección 8) necesita ver que ya se descartó el `None` antes de sumar.

### Solución 2

Las cuatro últimas líneas, cada una medida:

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

`FrozenInstanceError`: la instancia está congelada. Arreglo: no asignar; fabricar otra con `replace(servicio, timeout_ms=...)`.

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError`: no existe un miembro de `Estado` con valor `ROTO`. Arreglo: usar uno de los tres valores permitidos, o `Estado.CAIDO` directamente, que ni siquiera pasa por el texto.

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

`AttributeError`: `Estado` no tiene un miembro llamado `ARIBA`, y Python sugiere el que se parece. Arreglo: el que sugiere. Es el error de dedo que el `Enum` vino a atrapar, y lo atrapa en la línea donde ocurre.

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

`ValueError` al **definir** la clase, antes de crear ninguna instancia. Arreglo: `etiquetas: list[str] = field(default_factory=list)`, como en `fig05_08.py`.

### Solución 3

Las dos versiones devuelven **ARRIBA**: la de la Lección 3, el texto `"ARRIBA"`; la de hoy, `Estado.ARRIBA`. Desde la carpeta del `revisor`:

<!-- frag: codigo_sin_tiempo.py -->
```python
from modelo import clasificar

print(clasificar(200, None))
```

```text
Estado.ARRIBA
```

La razón está en la tercera regla, que es la misma desde la Lección 2: un servicio es `LENTO` si **respondió y tardó** 1000 ms o más. Con `None` no hay tiempo medido, así que no hay evidencia de lentitud, y lo único que se sabe es que contestó con un código bueno: `ARRIBA`. Las dos versiones tratan el caso igual porque las dos preguntan `tiempo_ms is not None` antes de comparar. En el `revisor` este caso no ocurre (un servicio que contestó siempre trae su tiempo), pero `tiempo_ms` está anotado como `int | None`, y la función tiene que dar una respuesta para todo lo que su firma admite.

Si quitaras `tiempo_ms is not None`, la comparación `None >= 1000` llegaría a evaluarse y el programa se detendría con:

```text
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

Es el mismo error de la Lección 2, cuando las preguntas iban en mal orden.

## Cómo sé que lo logré

- [ ] En `~/curso-python/revisor/`, `python revisor.py` imprime siete líneas (el encabezado, cuatro renglones, una línea en blanco y el resumen), y la última es `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Con los dos servicios extra del ejercicio 1, la última línea es `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`, y el renglón de `notificaciones` sale con el nombre pegado al estado (y sabes por qué).
- [ ] En el REPL, asignar `timeout_ms` a un `Servicio` falla con `dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'`, y `Estado("ROTO")` falla con `ValueError: 'ROTO' is not a valid Estado`.
- [ ] Puedes escribir de memoria `clasificar` con `match`: sin código es `CAIDO`, un código de 400 o más es `CAIDO`, un tiempo de 1000 o más es `LENTO`, y lo demás es `ARRIBA`.
- [ ] Puedes explicar con tus palabras la diferencia entre `==` y `is` para dos `Servicio` iguales, por qué `Estado.LENTO == "LENTO"` es `False` y qué hace `replace`.
- [ ] Anotaste en la [bitácora](bitacora.md) qué te costó más: lo que anotes ahí es lo que debes repasar.

## Resumen

Responde sin mirar la lección:

1. ¿Qué es una clase y qué es una instancia? ¿Qué agrega `@dataclass` a una clase, y qué agrega `frozen=True`?
2. ¿Qué se gana con `@dataclass(frozen=True)` frente a un diccionario o una tupla? ¿Qué hace `replace`?
3. ¿Qué compara `==` entre dos `Servicio`, y qué compara `is`?
4. ¿Por qué `Estado.LENTO == "LENTO"` da `False`, y cómo se obtiene el texto de un miembro?
5. ¿En qué orden prueba `match` sus casos, y qué hace el comodín `case _`?
6. En un `match`, ¿qué hace un nombre suelto como `case LIMITE:`? ¿Cómo se compara contra una constante?
7. ¿Por qué `linea` cambió de firma en esta lección, y qué ganó con el cambio?

## Para leer más

- [Python, «dataclasses»](https://docs.python.org/3/library/dataclasses.html) — la referencia completa del módulo: `frozen`, `field`, `replace` y todo lo que esta lección no usó. En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [PEP 557, «Data Classes»](https://peps.python.org/pep-0557/) — el documento que propuso `dataclass` y explica para qué casos se pensó y para cuáles no. Consultado el 7 de octubre de 2026.
- [Python, «Enum HOWTO»](https://docs.python.org/3/howto/enum.html) — la guía oficial de las enumeraciones, de lo básico a los tipos derivados. Consultado el 7 de octubre de 2026.
- [PEP 636, «Structural Pattern Matching: Tutorial»](https://peps.python.org/pep-0636/) — el tutorial oficial de `match`, que llega bastante más lejos que esta lección. Consultado el 7 de octubre de 2026.
