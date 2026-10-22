# Lección 6 — Errores, archivos y datos de fuera

**Tiempo:** 2 × 90 min (dos sesiones; el corte está entre las secciones 6.2 y 6.3)

**Qué construyes:** la lectura de la configuración del `revisor`: la lista de servicios deja de estar escrita en el código y se lee de un archivo `servicios.toml`

**Qué aprendes:** excepciones (`try`, `except`, `else`, `finally`, una excepción propia y `raise ... from`); leer un *traceback* de abajo hacia arriba; archivos con `with` y `pathlib`; UTF-8 explícito; los formatos TOML y JSON; validar lo que llega de fuera; y por qué no se usan `eval` ni `pickle`

**De dónde vienes.** Traes el proyecto de la [Lección 5](05-modelo-de-datos.md): un `revisor` con su modelo de datos (`Servicio`, `Estado`, `Resultado`), la clasificación con `match`, el reporte en tabla con su resumen, y la lista `SERVICIOS` escrita a mano dentro de `revisor.py`. Funciona, pero el ejercicio de proyecto de la lección 5 te dejó una molestia: para agregar un servicio al reporte hay que **abrir el código Python y editarlo**. Quien administra los servicios no tendría por qué saber programar, y quien programa no tendría por qué volver a tocar el código cada vez que cambia una dirección. Esta lección separa las dos cosas: los datos se van a un archivo, y el programa aprende a leerlo y a desconfiar de él. Trabajas en tu carpeta `~/curso-python/revisor/`, con el entorno virtual activado, y ejecutas todo con `python`.

**Qué no hace esta lección.** No consulta ninguna red: `revisar` sigue usando los datos simulados de la lección 5, y eso no cambia hasta la [Lección 9](09-http-y-asyncio.md). Tampoco convierte el `revisor` en un comando con opciones (`--config`, `--formato`): eso es el trabajo de la [Lección 7](07-paquete-linea-de-comandos.md). Hoy el nombre del archivo está escrito en una constante del programa. Lo que se resuelve aquí es **cómo se lee un archivo de configuración sin que el programa se rompa de formas incomprensibles** cuando el archivo no existe, está mal escrito o dice cosas que no tienen sentido.

**Sobre las corridas.** Para ejecutar una figura, entra a la carpeta de la lección en el repositorio y corre `python fig06_01.py`; las figuras que viven en una carpeta propia (`fig06_06/`, `fig06_07/`, `fig06_18/`) se ejecutan desde dentro de ella. Todas las salidas de esta lección se obtuvieron con Python 3.14.8 y se repitieron con Python 3.12.12, de la misma línea 3.12 que trae Linux Mint 22. (El de Mint 22 es el 3.12.3, que es el que publica Ubuntu 24.04, su base: lo muestra la [página del paquete `python3.12` para Ubuntu 24.04 en Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12).) Son idénticas, salvo por unas marcas de subrayado (`~~~~^^`) que el informe de un error trae en una versión y no en la otra; si en tu pantalla ves más o menos marcas, es normal. Los programas están en [`programas/06-errores-archivos-datos/`](https://github.com/HabilMX/curso-python/tree/main/programas/06-errores-archivos-datos), en el repositorio del curso.

## Al terminar vas a poder

- Leer el informe de un error (el *traceback*) de abajo hacia arriba y decir qué falló, dónde y quién llamó a quién.
- Escribir un `try` con `except`, `else` y `finally`, atrapando la excepción concreta que sabes manejar y dejando pasar las demás.
- Definir una excepción propia con una línea de herencia y lanzarla con `raise ... from`, de modo que el error original no se pierda.
- Abrir y leer un archivo con `with` y con `pathlib.Path`, siempre con la codificación UTF-8 escrita, y explicar qué pasa si no lo está.
- Leer un archivo TOML con `tomllib` y convertir datos a JSON y de vuelta con `json`, leyendo la línea y la columna cuando el JSON está mal.
- Validar datos de fuera con `isinstance` y `urlsplit`, y explicar por qué `True` pasa una validación de enteros hecha a la ligera.
- Explicar por qué un texto que viene de fuera nunca se pasa a `eval` ni a `pickle`.

## El porqué antes del cómo

Abre tu `revisor.py` de la lección 5 y mira la lista `SERVICIOS`. Cada vez que el equipo de operación quiera revisar un servicio nuevo, alguien tiene que editar ese archivo, guardar, y volver a ejecutar. Para el programador es una molestia; para cualquier otra persona es un muro. Y hay un problema más profundo: ese código y esos datos cambian **por razones distintas y a ritmos distintos**. El programa cambia cuando descubres un error o quieres una función nueva; la lista de servicios cambia cuando la empresa agrega un servicio. Mezclar las dos cosas en un archivo obliga a una a esperar a la otra.

La solución es la de siempre: los datos viven en un **archivo de configuración**, un texto con reglas que cualquiera puede editar, y el programa lo lee al arrancar. Pero en cuanto el programa lee algo que escribió otra persona, entra a un terreno nuevo. Hasta la lección 5, cada dato del `revisor` lo escribiste tú, en el mismo archivo que el código, y si estaba mal lo sabías al instante. Un archivo de fuera puede fallar de cuatro formas, y las cuatro son normales, no excepcionales:

1. **No existe**, o existe en otra carpeta de la que tú crees.
2. **Existe pero está mal escrito**: falta una comilla, sobra una coma.
3. **Está bien escrito pero le falta algo**: un servicio sin nombre, sin dirección.
4. **Está completo pero dice algo absurdo**: una dirección que no es de una página web, un tiempo límite negativo, dos servicios con el mismo nombre.

Un programa serio distingue las cuatro y le dice a la persona **cuál le pasó y cómo arreglarlo**, en lugar de mostrar un informe de error de treinta líneas escrito para programadores. Eso se logra con dos herramientas que esta lección enseña juntas porque no se entienden por separado: las **excepciones** (cómo un programa avisa que algo salió mal, y cómo otro lo atrapa) y la **validación** (cómo se revisa que lo que llegó tiene sentido).

El camino tiene dos sesiones. La **primera** cubre los conceptos 6.1 y 6.2: las excepciones y los archivos. Al terminarla sabrás leer un informe de error y abrir un archivo de texto sin sorpresas. La **segunda** cubre 6.3 y 6.4: los formatos (TOML y JSON) y la validación. Al terminarla tendrás el `revisor` leyendo su lista de servicios de un archivo y quejándose en español claro cuando el archivo no sirve. Con ese destino en mente, esto es lo que verás al final de la lección al ejecutar el `revisor` desde otra carpeta, sin haber pasado por donde está el archivo:

```text
error de configuración: no existe el archivo servicios.toml
```

Un mensaje de una línea, en lugar de un informe de error. Para llegar ahí hace falta entender, primero, qué es una excepción.

## Los conceptos

### 6.1 Excepciones

#### 6.1.1 Qué es una excepción y cómo se lee su informe

Hasta ahora, cuando algo falló en tus programas, Python se detuvo e imprimió un bloque de texto en rojo, el *traceback* (en este curso, «el informe del error»). Lo leíste por primera vez en la [Lección 1](01-instalacion.md) y lo has visto en cada lección. Ahora vamos a ver qué hay detrás: ese informe es el aviso de una **excepción**, que es la forma que tiene Python de decir «aquí ocurrió algo que no sé resolver». Cuando una línea del programa no puede hacer lo que se le pidió, **levanta** una excepción. La excepción sube por las funciones que estaban en marcha, de la más reciente a la más antigua, buscando a alguien que sepa qué hacer con ella. Si llega hasta arriba sin que nadie la atrape, el programa se detiene y Python imprime el informe.

Vamos a provocar una a propósito, con un caso que va a ocurrir de verdad cuando el `revisor` lea archivos: un dato que debería ser un número y llega con otra cosa. Para eso necesitas una función nueva: `int(texto)` convierte un texto en un número entero, igual que `str()` (lección 2) convierte un valor en texto. `int("142")` da el número 142. Pero ¿qué da `int("142 ms")`? Ejecútalo con `fig06_01.py`:

```python
# fig06_01.py
def leer_tiempo(texto: str) -> int:
    return int(texto)


def main() -> None:
    tiempo_ms = leer_tiempo("142 ms")
    print(f"tiempo: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

El programa define dos funciones, `leer_tiempo` y `main`, y `main` llama a `leer_tiempo` con un texto que trae las letras «ms» pegadas. Ejecútalo:

```text
$ python fig06_01.py
Traceback (most recent call last):
  File "fig06_01.py", line 12, in <module>
    main()
    ~~~~^^
  File "fig06_01.py", line 7, in main
    tiempo_ms = leer_tiempo("142 ms")
  File "fig06_01.py", line 3, in leer_tiempo
    return int(texto)
ValueError: invalid literal for int() with base 10: '142 ms'
```

Este es el informe, y vale la pena aprender a leerlo bien, porque lo vas a leer cientos de veces. **Se lee de abajo hacia arriba.** La **última línea** es la más importante: `ValueError: invalid literal for int() with base 10: '142 ms'`. Dice dos cosas: el **tipo** de la excepción, `ValueError` («valor inválido»: el tipo del dato era correcto, un texto, pero su contenido no sirve para lo que se quería hacer), y un **mensaje** que explica qué pasó. En español: «texto inválido para convertir a entero en base 10: '142 ms'». La «base 10» es el sistema de numeración que usamos todos los días; el mensaje solo dice que `int` esperaba un número escrito con dígitos del 0 al 9 y encontró, después del 142, un espacio y las letras `ms`. (Los espacios al principio o al final no le molestan: `int(" 142 ")` da `142`; lo que no acepta es nada que no sea parte del número.)

Las líneas de arriba dicen **dónde** pasó, y están en orden inverso a como fueron ocurriendo. Cada par de renglones que empieza con `File` es un **marco**: una función que estaba en marcha. El último marco (`in leer_tiempo`, línea 3) es donde nació la excepción: la línea `return int(texto)`. El marco de arriba (`in main`, línea 7) es quien llamó a `leer_tiempo`. Y el primero (`in <module>`, línea 12) es el programa mismo, que llamó a `main()`. Lee el informe como una pila de platos: el plato de abajo es el más reciente, y es donde empezó el problema. Las líneas con `~~~~^^` son una ayuda de las versiones recientes de Python ([PEP 657](https://peps.python.org/pep-0657/)): subrayan la parte exacta de la línea que falló, para que no tengas que adivinar cuál de las tres llamadas de un renglón largo fue.

Mientras no haya nadie que atrape la excepción, esa es la historia completa: se levanta, sube por la pila, el programa muere. La [documentación oficial sobre errores y excepciones](https://docs.python.org/3/tutorial/errors.html) cuenta lo mismo con más ejemplos. Veamos ahora cómo atraparla.

#### 6.1.2 `try`, `except`, `else` y `finally`

Atrapar una excepción es decirle a Python: «intenta esto; si falla de *esta* manera, haz *esto otro* en lugar de morir». Se escribe con la instrucción `try` (en inglés, «intenta»). Mira el programa `fig06_02.py`, que convierte dos textos, uno bueno y uno malo:

```python
# fig06_02.py
def leer_tiempo(texto: str) -> int | None:
    try:
        tiempo_ms = int(texto)
    except ValueError:
        print(f"  '{texto}' no es un número entero")
        return None
    else:
        print(f"  '{texto}' se convirtió en {tiempo_ms}")
        return tiempo_ms
    finally:
        print("  (fin de la conversión)")


def main() -> None:
    for texto in ["142", "142 ms"]:
        print(f"leyendo '{texto}'")
        tiempo_ms = leer_tiempo(texto)
        print(f"  resultado: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_02.py
leyendo '142'
  '142' se convirtió en 142
  (fin de la conversión)
  resultado: 142
leyendo '142 ms'
  '142 ms' no es un número entero
  (fin de la conversión)
  resultado: None
```

Hay cuatro bloques, y cada uno tiene una regla clara:

- **`try:`** contiene **solo** la línea que puede fallar, aquí `tiempo_ms = int(texto)`. Si no hay error, el programa sigue al bloque `else`. Si lo hay, Python abandona el `try` en esa misma línea y salta al `except` que corresponda.
- **`except ValueError:`** contiene lo que se hace si el error fue de ese tipo. En este caso, avisar que el texto no es un número y devolver `None` (el valor que en este curso significa «no hay dato»). Entre el `except` y los dos puntos va el **tipo de excepción** que se atrapa; cualquier otro tipo pasaría de largo.
- **`else:`** (en este contexto, «si no hubo error») se ejecuta **solo si el `try` terminó sin excepción**. Aquí guarda lo que se hace cuando la conversión funcionó.
- **`finally:`** («finalmente») se ejecuta **siempre**: haya habido error o no, hayas devuelto un valor o no. Se usa para limpiar, por ejemplo cerrar algo que se abrió.

Fíjate en la salida, porque contiene una sorpresa que conviene ver una vez. Con el texto «142» se imprime primero «se convirtió en 142» (del `else`) y **después** «(fin de la conversión)» (del `finally`), aunque el `return tiempo_ms` del `else` aparece antes en el código. Con «142 ms», el `except` imprime su aviso, devuelve `None`, y el `finally` **de todos modos** se ejecuta antes de que la función termine. Es decir: `finally` corre incluso cuando el bloque ya decidió salir con `return`. Esa garantía es la razón de su existencia.

Quedan dos preguntas razonables: ¿por qué un `else`, si el `print` y el `return` podrían ir dentro del `try`? Porque **un `try` debe ser lo más pequeño posible**. Todo lo que pones dentro está protegido por el `except`, y si en esa línea de más ocurre un error del mismo tipo que no esperabas, el `except` lo tragaría y tú creerías que fue el error que sí esperabas. La regla es: en el `try` va **lo que puede fallar de la manera que sabes manejar**, y nada más. Lo que debe ocurrir si todo salió bien va en el `else`.

La segunda pregunta: ¿se pueden atrapar varios tipos? Sí, de dos maneras. Una es poner varios bloques `except` uno tras otro, cada uno con su tipo y su respuesta. La otra es poner los tipos juntos **entre paréntesis**, separados por comas: `except (ValueError, TypeError):`, cuando la respuesta es la misma. Escribe siempre los paréntesis: en Python 3.12 son obligatorios, y aunque Python 3.14 permite omitirlos cuando el `except` no lleva `as` ([PEP 758](https://peps.python.org/pep-0758/)), el código del curso corre en las dos versiones.

#### 6.1.3 Atrapa la excepción concreta, nunca «cualquiera»

Esta es la regla más importante de la sección, y se entiende mejor viendo qué pasa cuando se rompe. Mira `fig06_03.py`. Es la misma función, pero con dos cambios: el `except` dice `Exception` en lugar de `ValueError`, y alguien escribió mal un nombre dentro del `try` (`stirp` en lugar de `strip`, el método que quita espacios en los extremos de un texto):

```python
# fig06_03.py
def leer_tiempo(texto: str) -> int | None:
    try:
        return int(texto.stirp())
    except Exception:  # noqa: BLE001
        print(f"'{texto}' no es un número entero")
        return None


def main() -> None:
    print(leer_tiempo("142"))


if __name__ == "__main__":
    main()
```

```text
$ python fig06_03.py
'142' no es un número entero
None
```

Mira lo que ocurrió: el texto «142» es un número perfectamente válido, y el programa dijo que **no lo es**. La función no tiene nada que ver con números: tiene un error de ortografía. Sin el `try`, Python habría detenido el programa con `AttributeError: 'str' object has no attribute 'stirp'. Did you mean: 'strip'?` («un texto no tiene el atributo `stirp`; ¿quisiste decir `strip`?»), y habrías arreglado la errata en un minuto. Con un `except` demasiado ancho, ese aviso se convirtió en una mentira que sale en pantalla, y el error real queda enterrado hasta que alguien pregunta por qué ningún tiempo se lee bien.

Para entenderlo hay que saber que las excepciones forman una familia. En la cima está `BaseException`; debajo, `Exception`, de la que cuelgan casi todos los errores que vas a encontrar; y de ahí salen los tipos concretos, algunos con parientes. `ValueError` es uno. `KeyError` e `IndexError` (que viste en la lección 4) son hijos de `LookupError`. `FileNotFoundError` es un caso particular de `OSError`, la excepción de los problemas con el sistema operativo. `UnicodeDecodeError`, que vas a ver más abajo, es un tipo de `ValueError`. El árbol completo está en la [lista de excepciones de la documentación](https://docs.python.org/3/library/exceptions.html). Atrapar una excepción atrapa **también a todos sus hijos**: por eso `except Exception` atrapa casi todo, incluido el `AttributeError` de la errata, y por eso `except ValueError` atrapa también los errores de lectura de TOML y de JSON, como verás en 6.3.

Y está la peor versión: el `except:` **sin tipo**, llamado «desnudo». Ese atrapa hasta lo que está por encima de `Exception`, incluido el `KeyboardInterrupt` que Python levanta cuando presionas `Ctrl`+`C` para detener un programa. Un programa con un `except:` desnudo puede no morir cuando se lo pides. La [guía de estilo PEP 8](https://peps.python.org/pep-0008/#programming-recommendations) pide nombrar las excepciones concretas siempre que se pueda en lugar de usarlo, y reservarlo para casos contados; en este curso la regla es más estricta y no tiene excepciones: nunca.

Las reglas, entonces, son tres. **Primera:** atrapa el tipo concreto que sabes manejar, con la respuesta concreta que tiene sentido. **Segunda:** si no sabes qué hacer con un error, **no lo atrapes**: déjalo subir, que se detenga el programa con su informe, y alguien lo verá. Un programa que se detiene con un informe claro es mejor que uno que sigue funcionando con datos equivocados. **Tercera:** si de verdad necesitas atrapar `Exception` (por ejemplo, en la última línea de defensa de un programa que no debe caerse), hazlo en un solo lugar, registra lo que ocurrió y no lo dejes pasar en silencio. El comentario `# noqa: BLE001` que ves en `fig06_03.py` es una marca para `ruff`, la herramienta que revisa el estilo del código y que conocerás en la [Lección 8](08-pruebas-tipos-calidad.md): le dice «sé que esta línea atrapa una excepción demasiado ancha, es a propósito». La regla de `ruff` que protesta se llama justamente «atrapar una excepción ciega».

#### 6.1.4 Una excepción propia y `raise ... from`

Hasta ahora atrapaste excepciones que Python ya trae. Para el `revisor` hace falta una más, porque necesitas distinguir **«el archivo de configuración tiene un problema»** de **«mi programa tiene un error»**. Las dos situaciones merecen respuestas distintas: la primera se le explica a la persona que escribió el archivo; la segunda es un defecto que debe detener el programa con su informe, para que lo arregle un programador. Si todo se levantara como `ValueError`, el programa no podría distinguir una de otra.

La solución es una excepción con nombre propio, que se define con una línea de **herencia**. Mira `fig06_04.py`:

```python
# fig06_04.py
class ErrorDeConfiguracion(Exception):
    """La configuración no se puede usar."""


def leer_timeout_ms(texto: str) -> int:
    try:
        return int(texto)
    except ValueError as error:
        mensaje = f"'timeout_ms' debe ser un entero, llegó '{texto}'"
        raise ErrorDeConfiguracion(mensaje) from error


def main() -> None:
    try:
        timeout_ms = leer_timeout_ms("cinco mil")
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        print(f"causa original: {error.__cause__}")
    else:
        print(f"timeout_ms = {timeout_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_04.py
error de configuración: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
causa original: invalid literal for int() with base 10: 'cinco mil'
```

La primera instrucción es nueva en forma, aunque ya viste `class` en la lección 5 como un «molde de datos»: `class ErrorDeConfiguracion(Exception):` define un molde nuevo que se llama `ErrorDeConfiguracion`, y el paréntesis dice que **hereda** de `Exception`. Heredar significa «es una `Exception` y además tiene su propio nombre»: todo lo que Python sabe hacer con cualquier excepción (levantarla, atraparla, imprimir su mensaje, mostrar su informe) lo sabe hacer con la tuya, sin escribir nada más. Es un solo nivel de herencia, y es todo lo que necesitas; el curso no entra en más. El texto entre triples comillas dentro de la clase es una **cadena de documentación** (*docstring*): una frase que explica para qué sirve, y que Python guarda para quien quiera consultarla. No hace falta ninguna otra instrucción dentro de la clase.

La función `leer_timeout_ms` hace algo que vas a repetir en todo el curso: atrapa un error de bajo nivel (`ValueError`, de `int`) y lo **traduce** a uno del dominio del programa (`ErrorDeConfiguracion`), con un mensaje que habla en los términos de quien escribió la configuración: «'timeout_ms' debe ser un entero, llegó 'cinco mil'». El mensaje de `int` («invalid literal for int()…») es útil para un programador, pero no para quien edita un archivo de configuración. La instrucción `raise` (levantar) lanza la excepción, y la cola `from error` hace algo importante: **conserva el error original como causa**. Esa causa queda guardada dentro de la nueva excepción, en `error.__cause__` (los dos guiones bajos antes y después son la forma en que Python marca nombres que reserva para sí). La segunda línea de la salida lo muestra: el programa imprimió su aviso en español y, aparte, la causa original en inglés, por si hace falta.

¿Qué pasa si nadie atrapa la excepción? Mira `fig06_05.py`, que es el mismo programa sin el `try` en `main`:

```text
$ python fig06_05.py
Traceback (most recent call last):
  File "fig06_05.py", line 8, in leer_timeout_ms
    return int(texto)
ValueError: invalid literal for int() with base 10: 'cinco mil'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "fig06_05.py", line 20, in <module>
    main()
    ~~~~^^
  File "fig06_05.py", line 15, in main
    timeout_ms = leer_timeout_ms("cinco mil")
  File "fig06_05.py", line 11, in leer_timeout_ms
    raise ErrorDeConfiguracion(mensaje) from error
ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
```

Este informe tiene **dos** partes separadas por una frase: «The above exception was the direct cause of the following exception» («la excepción de arriba fue la causa directa de la siguiente»). Es la huella de `from error`. Se lee igual que antes, de abajo hacia arriba: la última línea, `ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'`, es lo que llegó hasta arriba. Pero ahora, además, Python **conserva la historia**: arriba está el `ValueError` original, con su línea exacta (`return int(texto)`). Si no hubieras escrito `from error`, el informe diría en cambio «During handling of the above exception, another exception occurred» («durante el manejo de la excepción de arriba, ocurrió otra»), que sugiere un error nuevo ocurrido dentro del manejo de otro. Python mostraría igual las dos excepciones (la original queda guardada como *contexto*, en el atributo `__context__`), pero el informe ya no diría que una fue **consecuencia** de la otra: diría que la segunda pasó «mientras tanto», como si fuera un accidente aparte. Con `from`, la original queda registrada como **causa** (`__cause__`), que es lo que de verdad ocurrió. La regla: **cuando traduces una excepción, escribe siempre `from`**. Quien depure tu programa te lo agradecerá. La explicación de la técnica está en el [PEP 3134](https://peps.python.org/pep-3134/) y en la [sección sobre encadenar excepciones](https://docs.python.org/3/tutorial/errors.html#exception-chaining) del tutorial.

Con esto tienes el vocabulario de las excepciones. Falta un lugar donde usarlo, y es el que sigue: leer archivos, donde las cosas fallan por razones que no controlas.

### 6.2 Archivos

#### 6.2.1 Abrir, leer, cerrar: `with`

Un archivo en el disco no se «lee» sin más: primero se **abre**, lo que le pide al sistema operativo un acceso a él; se lee su contenido; y al final se **cierra**, lo que devuelve el acceso. Un archivo que se abre y no se cierra consume recursos del sistema (cada programa puede tener abiertos solo un número limitado) y, si estabas escribiendo, puede dejar la última parte sin guardar. La forma más cuidadosa de escribirlo, con lo que ya sabes de `try`, sería esta:

```python
archivo = open("nota.txt", encoding="utf-8")
try:
    texto = archivo.read()
finally:
    archivo.close()
```

Funciona, y el `finally` garantiza el cierre aunque `read()` falle. Pero es mucho ritual para algo tan frecuente, y es fácil olvidar el `finally`. Python ofrece la instrucción `with` («con»), que hace exactamente eso por ti. Mira `fig06_06/leer.py` y el archivo `nota.txt` que lee:

```text fig06_06/nota.txt
Revisión de las 9:00
reportes: sin conexión
```

```python
# fig06_06/leer.py
with open("nota.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
    print(f"dentro del with: cerrado = {archivo.closed}")

print(f"fuera del with: cerrado = {archivo.closed}")
print(texto.splitlines())
```

```text
$ cd fig06_06
$ python leer.py
dentro del with: cerrado = False
fuera del with: cerrado = True
['Revisión de las 9:00', 'reportes: sin conexión']
```

`open("nota.txt", encoding="utf-8")` abre el archivo y devuelve un objeto que representa esa apertura. `with ... as archivo:` dice «mientras dure este bloque, el archivo se llama `archivo`; cuando salgas del bloque, ciérralo, pase lo que pase». La salida lo demuestra: dentro del `with`, `archivo.closed` (la pregunta «¿está cerrado?») dice `False`; en cuanto el bloque termina, dice `True`, y nadie escribió un `close()`. Si el bloque termina por una excepción, el archivo también se cierra: el `with` es, en efecto, un `try`/`finally` escrito de forma abreviada. La [referencia de la instrucción `with`](https://docs.python.org/3/reference/compound_stmts.html#with) explica el mecanismo completo; para este curso basta con la regla: **todo archivo que abras, ábrelo con `with`**.

`archivo.read()` devuelve el contenido completo como un solo texto. En el programa se imprime `texto.splitlines()`, un método de los textos que los parte en una lista con una cadena por línea, y que quita los saltos de línea; así ves de un vistazo que el archivo tiene dos líneas. Fíjate también en `encoding="utf-8"`: es una parte del `open` que no es un adorno, y su razón se explica en 6.2.3.

#### 6.2.2 `pathlib.Path`: una ruta como valor, no como texto

El nombre del archivo, `"nota.txt"`, es una **ruta**: la dirección de un archivo dentro del disco. Hasta ahora la escribimos como un texto, y para un solo archivo en la carpeta actual no hay problema. Pero las rutas tienen reglas propias: en Linux y en macOS las carpetas se separan con `/`, en Windows con `\`; una ruta puede ser **absoluta** (empieza en la raíz del disco, como `/home/ana/curso-python/revisor/servicios.toml`) o **relativa** (se cuenta desde la carpeta donde estás, como `servicios.toml`). Manipular rutas como textos, con sumas y recortes, se rompe en cuanto cambia cualquiera de esas reglas.

Para eso el módulo `pathlib` de la biblioteca estándar ofrece la clase `Path`: un valor que **sabe lo que es una ruta**. Construyes uno con `Path("nota.txt")` y desde entonces tiene operaciones propias, que se invocan con un punto, igual que los métodos de listas y diccionarios que ya conoces. Mira `fig06_07/ruta.py`, que usa el mismo `nota.txt`:

```python
# fig06_07/ruta.py
from pathlib import Path

ruta = Path("nota.txt")
print(ruta.name, ruta.suffix, ruta.exists())
print(Path("no-esta.txt").exists())

otra = Path("datos") / "servicios.toml"
print(otra)

texto = ruta.read_text(encoding="utf-8")
print(texto.splitlines())
```

```text
$ cd fig06_07
$ python ruta.py
nota.txt .txt True
False
datos/servicios.toml
['Revisión de las 9:00', 'reportes: sin conexión']
```

Línea por línea:

- `Path("nota.txt")` crea la ruta. Todavía no toca el disco: solo describe una dirección, exista o no el archivo.
- `ruta.name` es el nombre del archivo (`nota.txt`), `ruta.suffix` es su terminación con el punto (`.txt`), y `ruta.exists()` pregunta al disco si existe (`True`). La segunda línea hace la misma pregunta sobre un archivo que no está, y contesta `False`: **preguntar si existe un archivo que no está no levanta ninguna excepción**. (Un matiz de versión: en 3.12, si la pregunta choca con otro problema del sistema, como no tener permiso para mirar la carpeta, `exists()` todavía puede lanzar un `OSError`; desde 3.14 [contesta `False` en todos esos casos](https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists).)
- `Path("datos") / "servicios.toml"` usa el operador `/` con un significado nuevo: **unir** dos partes de una ruta con el separador que le toque al sistema. El resultado se imprime como `datos/servicios.toml` y no toca el disco. Es mucho más seguro que sumar textos.
- `ruta.read_text(encoding="utf-8")` abre el archivo, lee todo, lo cierra y devuelve el texto, en una sola llamada. Es la forma que usaremos en el `revisor` porque no deja nada abierto. La [documentación de `pathlib`](https://docs.python.org/3/library/pathlib.html) enumera lo demás que puede hacer una ruta (listar carpetas, crear archivos); en este curso solo hace falta lo que ves aquí.

Hay una consecuencia práctica de que las rutas relativas «se cuenten desde donde estás»: el mismo programa, con el mismo `Path("nota.txt")`, funciona o no según la carpeta desde la que lo ejecutes. ¿Qué pasa cuando el archivo no existe? Mira `fig06_08.py`, que intenta abrir un archivo que no está:

```python
# fig06_08.py
with open("no-esta.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
print(texto)
```

```text
$ python fig06_08.py
Traceback (most recent call last):
  File "fig06_08.py", line 2, in <module>
    with open("no-esta.txt", encoding="utf-8") as archivo:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'
```

Se levanta `FileNotFoundError` («archivo no encontrado»), una excepción concreta que puedes atrapar. El texto del mensaje, `[Errno 2] No such file or directory`, viene del sistema operativo y está en inglés: no lo controlas tú, y por eso no lo mostrarás a quien use el `revisor`. En 6.4 el programa atrapará esta excepción y la traducirá a un mensaje propio.

#### 6.2.3 Texto y bytes: por qué siempre `encoding="utf-8"`

Un archivo en el disco no guarda letras: guarda **bytes**, números del 0 al 255. Para que esos números sean texto, alguien tiene que decidir qué número corresponde a qué letra. Esa decisión es la **codificación**, y existen muchas. La que domina hoy es **UTF-8**: puede representar cualquier carácter de cualquier idioma, y las letras sin acento ocupan un solo byte. Los caracteres con acento, como la «ó» de «conexión», ocupan dos. Una codificación antigua, `latin-1`, representa la «ó» con un solo byte, pero solo sirve para unos pocos idiomas europeos. Verlo es más claro que explicarlo. Ejecuta `fig06_09.py`, que fabrica los bytes de un mismo texto en las dos codificaciones:

```python
# fig06_09.py
texto = "sin conexión"

en_utf8 = texto.encode("utf-8")
en_latin1 = texto.encode("latin-1")

print(en_utf8)
print(en_latin1)
print(len(texto), len(en_utf8), len(en_latin1))
print(en_utf8.decode("utf-8"))
```

```text
$ python fig06_09.py
b'sin conexi\xc3\xb3n'
b'sin conexi\xf3n'
12 13 12
sin conexión
```

`texto.encode("utf-8")` convierte un texto en bytes con esa codificación; los bytes se imprimen con una `b` delante (`b'sin conexi\xc3\xb3n'`), y `\xc3\xb3` son los dos bytes (en hexadecimal) que UTF-8 usa para la «ó». Con `latin-1` la «ó» es un solo byte, `\xf3`. La tercera línea lo confirma con una cuenta: el texto tiene 12 caracteres; en UTF-8 son 13 bytes y en `latin-1`, 12. Y `bytes.decode("utf-8")` hace el camino inverso: de bytes a texto. Con los bytes de UTF-8 vuelve «sin conexión».

Ahora el problema. ¿Qué pasa si los bytes se escribieron en una codificación y se leen con otra? Ejecuta `fig06_10.py`, que intenta leer como UTF-8 los bytes de `latin-1`. La `b` antes de las comillas marca un literal de **bytes**, y `\xf3` escribe el byte cuyo valor, en hexadecimal (el sistema de numeración en base 16 con que se acostumbra escribir bytes), es `f3`, es decir, 243:

```python
# fig06_10.py
en_latin1 = b"sin conexi\xf3n"

print(en_latin1.decode("utf-8"))
```

```text
$ python fig06_10.py
Traceback (most recent call last):
  File "fig06_10.py", line 4, in <module>
    print(en_latin1.decode("utf-8"))
          ~~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10: invalid continuation byte
```

El último renglón dice: «el códec `utf-8` no puede decodificar el byte `0xf3` en la posición 10: continuación inválida». El byte `0xf3` es el de la «ó» en `latin-1`, pero en UTF-8 ese valor significa «aquí empieza un carácter de cuatro bytes» y el byte siguiente no tiene la forma que corresponde a la continuación. Python, correctamente, se niega a adivinar. Es un `UnicodeDecodeError`, que es un tipo de `ValueError`.

Esto explica por qué se escribe `encoding="utf-8"` **siempre**: cuando no lo escribes, Python elige la codificación según la configuración del sistema donde corre, según [la documentación de `open`](https://docs.python.org/3/library/functions.html#open). El mismo programa puede leer bien un archivo en tu computadora y fallar en la de un compañero, porque la configuración es distinta. Si lo escribes, el programa se comporta igual en todas partes. Y no es un capricho: los dos formatos que usarás a continuación exigen UTF-8. La [especificación de TOML](https://toml.io/en/v1.0.0) dice que un documento TOML es un texto Unicode válido en UTF-8, y el [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) establece que el JSON que se intercambia entre sistemas, fuera de los ecosistemas cerrados, debe usar UTF-8. Si quieres entender más el tema de fondo, el [HOWTO de Unicode](https://docs.python.org/3/howto/unicode.html) de la documentación lo cuenta paso a paso.

> **Aquí termina la primera sesión.** Hasta este punto tienes los conceptos 6.1 y 6.2: excepciones y archivos. Antes de la segunda sesión, ejecuta las figuras `fig06_01.py` a `fig06_10.py` y cambia algo en cada una: otro texto en lugar de «142 ms», un `except` distinto, otro nombre de archivo. Provocar el error tú mismo fija más que leerlo. La siguiente sesión empieza con los formatos.

### 6.3 Formatos: TOML y JSON

#### 6.3.1 Qué es un formato y por qué hay dos

Un archivo de texto con líneas sueltas no basta para describir una lista de servicios, cada uno con nombre, dirección y quizá un tiempo límite. Hace falta un **formato**: un conjunto de reglas que dice cómo se escribe cada cosa, para que cualquier programa pueda leerlo sin ambigüedades. Los dos formatos más usados en Python y en el resto del mundo para datos estructurados son **TOML** y **JSON**, y cumplen funciones distintas:

- **TOML** está pensado para que **una persona lo escriba y lo lea**: permite comentarios con `#`, no exige llaves ni comas por todos lados, y es difícil escribirlo de forma ambigua. Es el formato de los archivos de configuración, y es el que ya usa Python para la configuración de proyectos (lo verás en la lección 7, en `pyproject.toml`). El `revisor` leerá su lista de servicios de un archivo TOML.
- **JSON** está pensado para que **dos programas se pasen datos**. No admite comentarios y exige llaves, comillas y comas, pero casi todos los lenguajes saben leerlo y escribirlo. Es el formato de las respuestas de casi cualquier servicio web, y el que usará el `revisor` para entregar su reporte a otros programas.

La biblioteca estándar de Python trae un módulo para cada uno: `tomllib` (para leer TOML) y `json` (para leer y escribir JSON). Hay una asimetría que conviene saber: `tomllib` solo **lee**. Para escribir TOML hay que instalar una biblioteca externa, y este curso no la necesita porque nunca escribe configuración, solo la lee.

#### 6.3.2 Leer TOML con `tomllib`

Un TOML es una serie de líneas `llave = valor`, con valores de pocos tipos: texto entre comillas dobles, números enteros y decimales, `true` y `false`, y listas. Además tiene **tablas**, que agrupan llaves bajo un nombre entre corchetes. Lo que nos interesa es un caso particular: una lista de tablas, o *array of tables*, que se escribe con **dobles corchetes**, `[[servicios]]`, y cada vez que aparece el encabezado empieza un elemento nuevo de la lista. Es la forma natural de escribir «una lista de servicios, cada uno con sus campos». La [especificación de TOML](https://toml.io/en/v1.0.0#array-of-tables) tiene la definición exacta; con un ejemplo se entiende más rápido. Mira `fig06_11.py`, que lee un TOML escrito dentro del propio programa:

```python
# fig06_11.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
"""

datos = tomllib.loads(TEXTO)
print(datos)

segundo = datos["servicios"][1]
print(segundo["nombre"], segundo["timeout_ms"], type(segundo["timeout_ms"]))
print(segundo.get("proxy"))
```

```text
$ python fig06_11.py
{'servicios': [{'nombre': 'catalogo', 'url': 'https://catalogo.example'}, {'nombre': 'notificaciones', 'url': 'https://notificaciones.example', 'timeout_ms': 1000}]}
notificaciones 1000 <class 'int'>
None
```

Dos detalles de lectura antes del resultado. El texto va entre **triples comillas** (`"""`...`"""`), que en Python sirven para escribir un texto de varias líneas con los saltos de línea incluidos. Y `tomllib.loads(TEXTO)` es la función que lee: el nombre viene de *load string* («cargar desde un texto»), y devuelve un **diccionario**, una estructura que ya conoces. (Existe también `tomllib.load`, que lee de un archivo abierto en modo binario; en el `revisor` leeremos el texto nosotros con `read_text` para controlar la codificación y los errores.)

Mira cómo quedó el diccionario. Hay una sola llave, `'servicios'`, cuyo valor es una **lista con dos diccionarios**: uno por cada `[[servicios]]`. El segundo diccionario tiene una llave más, `timeout_ms`, y su valor es el número `1000`: la tercera línea de la salida confirma que es un `int`. Así se lee cualquier dato de un TOML: `datos["servicios"]` es la lista, `datos["servicios"][1]` es el segundo servicio, `datos["servicios"][1]["nombre"]` es su nombre. Y la última línea de la salida muestra algo que usaremos mucho: `segundo.get("proxy")` pregunta por una llave que **no existe** y devuelve `None`, mientras que `segundo["proxy"]` habría levantado un `KeyError`. Para los datos que son opcionales (como `timeout_ms`), `.get` es la herramienta.

¿Y si el TOML está mal escrito? Mira `fig06_12.py`, donde a la línea del nombre le falta la comilla de cierre:

```python
# fig06_12.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo
url = "https://catalogo.example"
"""

try:
    tomllib.loads(TEXTO)
except tomllib.TOMLDecodeError as error:
    print(f"TOML inválido: {error}")
```

```text
$ python fig06_12.py
TOML inválido: Illegal character '\n' (at line 3, column 19)
```

`tomllib.TOMLDecodeError` es la excepción de un TOML inválido. Su mensaje, `Illegal character '\n' (at line 3, column 19)`, dice «carácter ilegal, un salto de línea, en la línea 3, columna 19»: el texto empezó con una comilla y encontró el fin de la línea sin que se cerrara. Fíjate que el mensaje te lleva al punto exacto, y que lo dice el propio módulo. En el `revisor` incluiremos ese mensaje tal cual en el error de configuración. Las funciones y las excepciones de este módulo están en la [documentación de `tomllib`](https://docs.python.org/3/library/tomllib.html); el módulo entró a la biblioteca estándar en Python 3.11 con el [PEP 680](https://peps.python.org/pep-0680/).

#### 6.3.3 Leer y escribir JSON con `json`

JSON tiene reglas más estrictas y un vocabulario más pequeño. Un objeto JSON se escribe entre llaves, con pares `"llave": valor`; una lista, entre corchetes; los textos, entre comillas dobles (**siempre dobles**); los números, sin comillas; y existen tres palabras: `true`, `false` y `null`. Python tiene un equivalente para cada pieza, y el módulo `json` convierte de uno a otro:

| JSON | Python |
|---|---|
| objeto `{...}` | `dict` |
| arreglo `[...]` | `list` |
| texto `"..."` | `str` |
| número entero | `int` |
| número con decimales | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Las reglas estrictas son las del estándar; el módulo `json` de Python, por omisión, es un poco más permisivo, y [su documentación](https://docs.python.org/3/library/json.html) lo dice de frente: acepta y escribe `NaN`, `Infinity` y `-Infinity` (los «no es un número» e «infinito» de los `float`), que el estándar no admite, y si un objeto repite una llave se queda con el último valor. Para el `revisor` no importa, porque sus números son enteros; si alguna vez necesitas un JSON que cualquier otro programa acepte, `json.dumps(..., allow_nan=False)` se niega a escribir esos valores.

La conversión de Python a JSON (**serializar**) se hace con `json.dumps` («*dump string*»: volcar a texto), y la inversa (**deserializar**) con `json.loads`. Mira `fig06_13.py`, que usa un resultado del `revisor` como ejemplo:

```python
# fig06_13.py
import json

resultado = {
    "nombre": "reportes",
    "estado": "CAIDO",
    "tiempo_ms": None,
    "detalle": "sin conexión",
    "activo": True,
}

texto = json.dumps(resultado, ensure_ascii=False, indent=2)
print(texto)

de_vuelta = json.loads(texto)
print(de_vuelta["tiempo_ms"] is None, de_vuelta == resultado)

print(json.dumps(resultado["detalle"]))
print(json.dumps(resultado["detalle"], ensure_ascii=False))
```

```text
$ python fig06_13.py
{
  "nombre": "reportes",
  "estado": "CAIDO",
  "tiempo_ms": null,
  "detalle": "sin conexión",
  "activo": true
}
True True
"sin conexi\u00f3n"
"sin conexión"
```

Cuatro cosas que aprender de esta salida. Una: `None` se volvió `null` y `True` se volvió `true`; el JSON no es Python, y cada lenguaje tiene su ortografía de «nada» y de «verdadero». Dos: `indent=2` hace que `dumps` escriba el resultado en varias líneas con dos espacios de sangría, legible para una persona; sin él, saldría todo en una sola línea compacta. Tres: la comprobación `de_vuelta == resultado` da `True`, porque `loads` reconstruye el diccionario original, y `de_vuelta["tiempo_ms"] is None` también, porque `null` regresa como `None`. Y cuatro, la más fina: las últimas dos líneas imprimen el mismo texto, «sin conexión», de dos maneras. Por omisión, `dumps` **escapa** todo carácter que no sea ASCII y escribe `"sin conexi\u00f3n"`, que es JSON válido pero ilegible para una persona. Con `ensure_ascii=False` escribe la «ó» tal cual. Como el `revisor` escribe en español, el reporte JSON llevará siempre `ensure_ascii=False`. Esa es la forma que fija el curso para todo el reporte: `json.dumps(datos, ensure_ascii=False, indent=2)`.

Una advertencia que se aprende mejor a la mala. `json.dumps` solo entiende los tipos de la tabla de arriba (y la tupla, que escribe como arreglo, igual que una lista). Los datos del `revisor` están en objetos propios, `Resultado`, `Servicio` y `Estado`, y si intentas `json.dumps(Estado.CAIDO)` obtienes `TypeError: Object of type Estado is not JSON serializable` («un objeto de tipo `Estado` no se puede serializar a JSON»). La solución es armar primero un diccionario con tipos simples, usando `estado.value` para sacar el texto del `Enum`, y serializar ese diccionario. Es lo que hará la función `reporte_a_json` más adelante.

Y como TOML, JSON también falla. Mira `fig06_14.py`, donde falta una coma entre dos pares:

```python
# fig06_14.py
import json

TEXTO = """{
  "nombre": "pagos",
  "tiempo_ms": 87
  "estado": "ARRIBA"
}"""

try:
    json.loads(TEXTO)
except json.JSONDecodeError as error:
    print(f"mensaje: {error.msg}")
    print(f"línea {error.lineno}, columna {error.colno}")
    print(f"completo: {error}")
```

```text
$ python fig06_14.py
mensaje: Expecting ',' delimiter
línea 4, columna 3
completo: Expecting ',' delimiter: line 4 column 3 (char 43)
```

`json.JSONDecodeError` guarda el problema en tres atributos útiles: `msg` («se esperaba una coma como delimitador»), `lineno` (la línea) y `colno` (la columna). Aquí la línea 4, columna 3: después del `87` de la línea anterior debió ir una coma, y el decodificador la echó de menos justo al empezar el siguiente par. El mensaje completo, que se obtiene al imprimir el error, trae además `char 43`, la posición contando desde el principio. La [documentación de `json`](https://docs.python.org/3/library/json.html) describe todos los parámetros de `dumps` y `loads`, y el [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) es la especificación del formato. Que `JSONDecodeError` sea también un `ValueError` te dice algo que ya sabes de 6.1.3: un `except ValueError` lo atraparía, junto con muchos otros errores que no tienen que ver. Siempre es mejor nombrar el tipo concreto.

### 6.4 Validar lo que llega de fuera

#### 6.4.1 Por qué hay que validar, y dónde

Un archivo puede estar bien escrito y ser, aun así, inútil. Este TOML es perfectamente válido:

```toml
[[servicios]]
nombre = 42
url = "ftp://archivos.example"
timeout_ms = -3
```

Cada línea sigue las reglas de TOML. Pero el nombre es un número, la dirección no es de una página web, y el tiempo límite es negativo. Si el programa lo acepta sin mirarlo, el error aparecerá más adelante, lejos de su causa, en una línea que no tiene nada que ver con el archivo: un `TypeError` al intentar alinear un nombre, o una petición que nunca sale. **Validar** es revisar, en el momento en que los datos entran, que tienen la forma y el sentido que el programa espera.

Hay una razón específica de Python para hacerlo a mano. En la [Lección 0](00-que-es-python.md) viste que las anotaciones de tipo (`nombre: str`) **no se imponen al ejecutar**: son una nota para ti y para las herramientas, no un candado. Un `Servicio(nombre=42, ...)` se crea sin protestar. Por eso la frontera del programa, el punto donde entra lo que viene de fuera, es el lugar donde se comprueban los tipos de verdad. Una vez validados, el resto del programa puede confiar en ellos sin volver a mirar. Esa idea, **validar en la frontera y confiar adentro**, ordena todo el `revisor`: un solo módulo, `configuracion.py`, se encarga de desconfiar del exterior.

La regla de fondo es la que formula la [guía de validación de entradas de OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): lo que llega de fuera no es de confianza hasta que se ha verificado, y la verificación que mejor funciona es una **lista de lo permitido**: se enumera qué sí vale y se rechaza todo lo demás, en lugar de intentar enumerar todo lo que está mal.

#### 6.4.2 `isinstance` y la trampa de `bool`

Para preguntar «¿este valor es de este tipo?» existe `isinstance(valor, tipo)`, una función que devuelve `True` o `False`. `isinstance(5000, int)` es `True`; `isinstance("5000", int)` es `False`, porque el texto «5000» no es un entero aunque se parezca a uno. Con ella se puede escribir la validación del tiempo límite: «tiene que ser un entero mayor que cero». Y aquí hay una trampa que merece su propia figura. Mira `fig06_15.py`:

```python
# fig06_15.py
print(isinstance(True, int))
print(isinstance(True, bool))
print(True + True)


def timeout_valido(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


for valor in [5000, 0, -1, True, "5000", 2.5]:
    print(valor, type(valor), timeout_valido(valor))
```

```text
$ python fig06_15.py
True
True
2
5000 <class 'int'> True
0 <class 'int'> False
-1 <class 'int'> False
True <class 'bool'> False
5000 <class 'str'> False
2.5 <class 'float'> False
```

Las primeras tres líneas son la trampa. `isinstance(True, int)` es **`True`**: en Python, un `bool` es un tipo de entero. `True` es literalmente el número 1, y `False` el 0, y por eso `True + True` da `2`. No es un accidente: es una decisión de diseño antigua del lenguaje, descrita en la [documentación de los tipos incorporados](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool). La consecuencia, para ti, es concreta. Una validación ingenua como `isinstance(timeout_ms, int) and timeout_ms > 0` **acepta `true`** como tiempo límite, porque `true` es un entero positivo: vale 1. Alguien que escribe `timeout_ms = true` en el archivo (una confusión comprensible) obtendría un tiempo límite de un milisegundo sin que nadie se queje.

La función `timeout_valido` del programa lo evita: pregunta `isinstance(valor, int)` **y además** `not isinstance(valor, bool)`. Las últimas seis líneas de la salida muestran el resultado con seis valores: el entero 5000 pasa; el 0 y el -1 no pasan por la condición `valor > 0`; `True` no pasa; el texto `"5000"` no pasa (es un `str`); y el decimal `2.5` tampoco (es un `float`). Observa que la prueba se hizo con una **lista de valores representativos**, incluyendo los casos raros: así se prueba una validación, mirando justo los valores que podrían colarse.

#### 6.4.3 Direcciones: el esquema permitido

Otro dato de fuera del `revisor` es la dirección (`url`) de cada servicio. Una dirección tiene partes, y la primera es el **esquema**: lo que va antes de los dos puntos, y que dice qué protocolo usar (`https`, `http`, `ftp`, `file`...). Para un revisor de servicios web solo tienen sentido dos: `http` y `https`. ¿Por qué importa tanto? Porque más adelante el programa hará una petición a esa dirección, y con la biblioteca `urllib` una dirección `file:///...` hace que el programa **lea un archivo del disco** en lugar de consultar un servicio, mientras que otros esquemas lo harían hablar con otro tipo de servidor. Un archivo de configuración que otra persona editó no debe poder lograr eso.

La biblioteca estándar trae `urllib.parse.urlsplit`, que parte una dirección en sus componentes. Mira `fig06_16.py`, que prueba seis direcciones:

```python
# fig06_16.py
from urllib.parse import urlsplit

DIRECCIONES = [
    "https://catalogo.example",
    "http://127.0.0.1:8099/catalogo",
    "ftp://archivos.example",
    "file:///etc/hosts",
    "catalogo.example",
    "javascript:alert(1)",
]

for direccion in DIRECCIONES:
    esquema = urlsplit(direccion).scheme
    permitida = esquema in {"http", "https"}
    print(f"{direccion:<32} esquema='{esquema}' permitida={permitida}")
```

```text
$ python fig06_16.py
https://catalogo.example         esquema='https' permitida=True
http://127.0.0.1:8099/catalogo   esquema='http' permitida=True
ftp://archivos.example           esquema='ftp' permitida=False
file:///etc/hosts                esquema='file' permitida=False
catalogo.example                 esquema='' permitida=False
javascript:alert(1)              esquema='javascript' permitida=False
```

`urlsplit(direccion).scheme` es el esquema. La validación es una pregunta de pertenencia: `esquema in {"http", "https"}`, con el conjunto de lo permitido, como en la lista de permitidos de la que hablamos. Observa los casos: las dos primeras direcciones pasan; `ftp` y `file` no; `catalogo.example` (sin esquema) tiene un esquema vacío y no pasa; y `javascript:alert(1)` tiene el esquema `javascript`, que tampoco. Nota la elección de diseño: **no** se escribió una lista de esquemas prohibidos (`ftp`, `file`, `javascript`...), porque mañana alguien inventa otro y se cuela. Se escribió la lista de los dos permitidos. El estándar que define cómo se parte una dirección es el [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), y las funciones están en la [documentación de `urllib.parse`](https://docs.python.org/3/library/urllib.parse.html).

Mirar solo el esquema, sin embargo, deja pasar dos clases de direcciones rotas, y conviene verlas. La primera es una dirección sin servidor: `https://` a secas, o `http:catalogo` (sin las dos barras), tienen el esquema correcto pero ningún servidor al que llamar. La segunda es peor: hay direcciones que `urlsplit` ni siquiera puede partir. Con `http://[::1` (un corchete que abre y no cierra) `urlsplit` no devuelve nada: **lanza** `ValueError: Invalid IPv6 URL`. Y con `http://127.0.0.1:abc/`, la dirección se parte, pero al pedir el puerto (`.port`, el número que va después de los dos puntos) sale `ValueError: Port could not be cast to integer value as 'abc'`. Si la validación no atrapa ese `ValueError`, un archivo de configuración mal escrito tumba el programa con un *traceback* en lugar del mensaje claro que prometimos. La [documentación de `urllib.parse`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit) lo advierte: `urlsplit` no valida, y los corchetes sin pareja lanzan `ValueError`.

Hay una tercera clase, más escondida. En TOML, dentro de un texto entre comillas, `\n` es un salto de línea, así que `url = "http://127.0.0.1:8099/cata\nlogo"` llega a Python con un salto de línea en medio. `urlsplit` **lo quita en silencio** (su documentación lo dice: elimina los saltos de línea y los tabuladores, como hacen los navegadores) y la dirección parece buena; pero la biblioteca que hará la petición en la lección 9, `httpx`, sí lo ve y la rechaza con un error propio, que no es un error de red. Algo parecido puede pasar con letras que no son del inglés en el nombre del servidor, que `httpx` tiene que convertir a una forma especial y a veces no puede. La defensa sencilla es no aceptar, en el archivo de configuración, nada que no sea texto común.

Por eso el `revisor` no pregunta por el esquema directamente, sino con una función pequeña que reúne todas las preguntas:

```python
def es_url_http(url: str) -> bool:
    if not url.isascii() or not url.isprintable() or " " in url:
        return False
    try:
        partes = urlsplit(url)
        return (
            partes.scheme in {"http", "https"}
            and partes.hostname is not None
            and (partes.port is None or partes.port > 0)
        )
    except ValueError:
        return False
```

Se lee de arriba abajo. El primer `if` descarta lo que no es texto común, con tres métodos de los textos: `isascii()` es `True` si todos los caracteres son ASCII (las letras del inglés, los dígitos y los signos de un teclado básico; una `é` ya no lo es); `isprintable()` es `True` si ninguno es un carácter de control, como el salto de línea; y `" " in url` pregunta si hay algún espacio. Si falla cualquiera de las tres, el `revisor` no acepta la dirección. Ojo: eso no quiere decir que sea inválida en internet; `https://catálogo.example` es una dirección legítima. Es una regla del `revisor`, más estricta que la de los navegadores: en su configuración, un nombre así se escribe en su forma ASCII, la que empieza con `xn--`. Después, todo va dentro de un `try` porque tanto partir la dirección como leer el puerto pueden lanzar `ValueError`, y para esta función ese error tiene una sola respuesta: la dirección no sirve, `False`. Dentro, tres condiciones unidas con `and`: el esquema es uno de los dos permitidos; `partes.hostname`, el nombre del servidor, existe (en `https://` a secas vale `None`); y el puerto, si lo hay, es un número mayor que 0. Las tres van entre paréntesis para poder repartirlas en varios renglones. Un detalle de `and` que aquí importa: evalúa de izquierda a derecha y **se detiene en la primera condición falsa**, así que el puerto solo se lee si las dos primeras ya se cumplieron. Con esto, las seis direcciones de `fig06_16.py` dan el mismo resultado de antes, y todas las rotas de estos párrafos salen `False`. Lo que esta validación no comprueba es que el servidor exista o conteste: eso solo se sabe al consultarlo, y es el trabajo del `revisor` desde la lección 9. Tampoco garantiza que `httpx` acepte todo lo que pasa: `http://999.1.1.1:8099/pagos` tiene esquema, servidor y puerto, pero 999 no cabe en una dirección IP (cada parte va de 0 a 255), y `httpx` la rechaza. Por eso la lección 9, además de explicar por qué `file://` es un riesgo concreto cuando se usa `urllib`, pone una segunda red al consultar: una dirección que `httpx` no puede usar sale en el reporte como «dirección inválida», sin tumbar a los demás.

#### 6.4.4 Por qué no `eval` ni `pickle`

Con el vocabulario de esta lección ya se puede explicar algo que se ve en muchos programas de principiantes y es un riesgo serio. Alguien piensa: «para leer una lista de servicios no necesito un formato; escribo la lista como código de Python en un archivo, y el programa la ejecuta». Existe una función que lo permite: `eval(texto)`, que toma un texto, lo interpreta **como código** y devuelve su resultado. Mira `fig06_17.py`, una demostración de lo que **no** se hace:

```python
# fig06_17.py
# DEMOSTRACIÓN de lo que NO se hace: eval con un texto que viene de fuera.
print(eval("2300 + 1"))

texto_de_fuera = "print('esto lo escribió otro y se ejecutó')"
eval(texto_de_fuera)
```

```text
$ python fig06_17.py
2301
esto lo escribió otro y se ejecutó
```

La primera llamada parece inocente: `eval("2300 + 1")` calcula y devuelve `2301`. La segunda muestra el problema: el texto que llegó de fuera era una **instrucción**, y `eval` la ejecutó. Aquí fue un `print` inofensivo; podría haber sido cualquier cosa que Python sepa hacer: borrar archivos, leer contraseñas, abrir una conexión a otra computadora. Quien controle el texto controla el programa. La [documentación de `eval`](https://docs.python.org/3/library/functions.html#eval) lo dice sin rodeos: ejecuta código arbitrario y no es un mecanismo de seguridad restringirle las funciones que puede usar. Hay una variante más cuidadosa, `ast.literal_eval`, que acepta solo valores literales (números, textos, listas), pero la [documentación del módulo `ast`](https://docs.python.org/3/library/ast.html#ast.literal_eval) advierte que tampoco es adecuada para entradas no confiables: un texto muy grande o muy anidado puede agotar la memoria o la pila de Python.

El otro caso es `pickle`, el módulo que guarda objetos de Python en un archivo y los reconstruye después. Es cómodo, porque no hay que armar un formato: se guarda el objeto y se recupera. Pero reconstruir un objeto puede ejecutar código, y por eso la [documentación de `pickle`](https://docs.python.org/3/library/pickle.html) abre con una advertencia en grande: **nunca cargues datos de una fuente que no sea de confianza**, porque un archivo hecho a propósito puede ejecutar lo que su autor quiera en tu computadora. Ni siquiera se muestra aquí cómo se hace, porque este curso no lo usa. Esa clase de falla tiene nombre en el catálogo de debilidades de software: [CWE-502, deserialización de datos no confiables](https://cwe.mitre.org/data/definitions/502.html). La solución es la que ya tienes: **los datos de fuera se leen con formatos que solo describen datos**. TOML y JSON describen valores, no instrucciones; por más que alguien se esfuerce en escribirlos, `tomllib.loads` y `json.loads` solo pueden devolver diccionarios, listas, textos, números y booleanos (más `None` en JSON, y fechas y horas en TOML, que `tomllib` devuelve como valores del módulo `datetime`). Ninguno de esos tipos ejecuta nada. Por eso el `revisor` los usa.

Que no ejecuten nada no quiere decir que no puedan hacer daño de otra manera. Las documentaciones de [`tomllib`](https://docs.python.org/3/library/tomllib.html) y de [`json`](https://docs.python.org/3/library/json.html) traen la misma advertencia: un texto hecho con mala intención (enorme, o anidado miles de niveles) puede hacer que la lectura consuma mucho procesador y mucha memoria, y recomiendan **limitar el tamaño** de lo que se lee. El `revisor` no lo hace, y es una decisión consciente: lee un archivo de configuración que escribe quien lo usa, de unos cuantos cientos de bytes. Pero si un programa tuyo recibe TOML o JSON de otros (por la red, de un formulario), lo primero es comprobar el tamaño antes de leerlo, por ejemplo con `ruta.stat().st_size`, que dice cuántos bytes mide un archivo, y rechazar lo que pase de un límite razonable.

Si quieres seguir con la parte de seguridad de los sistemas que exponen servicios, el blog de Hábil tiene un artículo sobre [seguridad de APIs: identidad, puerta de enlace y tokens](https://www.habil.mx/es/blog/seguridad-apis-cto-identidad-gateway-tokens/). Y si te interesa ver cómo otro lenguaje resuelve este mismo problema de los datos de fuera con el mismo `revisor`, el [curso de TypeScript](https://www.habil.mx/es/cursos/typescript/) tiene una lección entera para eso.

#### 6.4.5 El paso del proyecto: el `revisor` lee su configuración

Tienes todas las piezas. Falta ensamblarlas. El `revisor` de esta lección queda así, en tu carpeta `~/curso-python/revisor/`:

```text
revisor/
  servicios.toml      ← NUEVO: los datos, ahora fuera del código
  configuracion.py    ← NUEVO: lee, valida y traduce los errores
  formato.py          ← tiene una función más: reporte_a_json
  revisor.py          ← ya no tiene SERVICIOS escrito a mano
  modelo.py  revision.py   (sin cambios)
```

Empieza por los datos. Este es el archivo `servicios.toml`, con los mismos cuatro servicios de siempre; es el que sustituye a la lista que tenías en el código:

```toml fig06_18/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "inventario"
url = "https://inventario.example"

[[servicios]]
nombre = "pagos"
url = "https://pagos.example"

[[servicios]]
nombre = "reportes"
url = "https://reportes.example"
```

Ahora el módulo nuevo, `configuracion.py`. Es el más largo de la lección, pero cada parte ya la conoces. Léelo completo una vez, y luego se desmonta:

```python
# fig06_18/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from modelo import Servicio, nombres_repetidos


class ErrorDeConfiguracion(Exception):
    """El archivo de configuración no se puede usar."""


def leer_servicios(ruta: Path) -> list[Servicio]:
    try:
        texto = ruta.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error

    try:
        datos = tomllib.loads(texto)
    except tomllib.TOMLDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no es TOML válido: {error}") from error

    lista = datos.get("servicios")
    if not isinstance(lista, list) or len(lista) == 0:
        raise ErrorDeConfiguracion("falta la lista [[servicios]]")

    servicios = [
        validar_servicio(datos_servicio, posicion)
        for posicion, datos_servicio in enumerate(lista, start=1)
    ]

    repetidos = nombres_repetidos(servicios)
    if len(repetidos) > 0:
        raise ErrorDeConfiguracion(f"nombres repetidos: {', '.join(sorted(repetidos))}")
    return servicios


def es_url_http(url: str) -> bool:
    if not url.isascii() or not url.isprintable() or " " in url:
        return False
    try:
        partes = urlsplit(url)
        return (
            partes.scheme in {"http", "https"}
            and partes.hostname is not None
            and (partes.port is None or partes.port > 0)
        )
    except ValueError:
        return False


def tiene_credenciales(url: str) -> bool:
    partes = urlsplit(url)
    return partes.username is not None or partes.password is not None


def validar_servicio(datos: object, posicion: int) -> Servicio:
    if not isinstance(datos, dict):
        raise ErrorDeConfiguracion(f"servicio {posicion}: debe ser una tabla")

    nombre = datos.get("nombre")
    if nombre is None:
        raise ErrorDeConfiguracion(f"servicio {posicion}: falta 'nombre'")
    if not isinstance(nombre, str) or nombre.strip() == "":
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'nombre' debe ser un texto que no esté vacío"
        )

    url = datos.get("url")
    if url is None:
        raise ErrorDeConfiguracion(f"servicio {posicion}: falta 'url'")
    if not isinstance(url, str) or not es_url_http(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' debe ser una dirección "
            "http:// o https:// válida"
        )
    if tiene_credenciales(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' no debe llevar usuario ni clave"
        )

    if "timeout_ms" not in datos:
        return Servicio(nombre, url)

    timeout_ms = datos["timeout_ms"]
    if (
        not isinstance(timeout_ms, int)
        or isinstance(timeout_ms, bool)
        or timeout_ms <= 0
    ):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'timeout_ms' debe ser un entero mayor que 0"
        )
    return Servicio(nombre, url, timeout_ms)
```

La función `leer_servicios` recibe una ruta y devuelve la lista de `Servicio`. Va en cuatro pasos, y en cada uno la regla es la misma: **traducir al dominio de la configuración todo error que pueda tener causa en el archivo**.

1. **Leer el texto.** `ruta.read_text(encoding="utf-8")` está dentro de un `try` con un solo `except`, y es para `FileNotFoundError`. Ese es el único error de lectura que sabe explicarse bien («no existe el archivo»), así que es el único que se atrapa. Si el archivo existe pero no tienes permiso para leerlo, el error es un `PermissionError`, y **no lo atrapa**: la función no tiene nada útil que decir de eso, y es mejor que el programa se detenga con el informe del sistema. (El ejercicio 4 te pide ampliar esto con otro error, el de la codificación.)
2. **Interpretar el TOML.** `tomllib.loads` va en su propio `try` con su propio `except`: si hay `TOMLDecodeError`, el mensaje de `tomllib` se incluye en el nuestro. Se hace `raise ... from error` en ambos casos, por la razón de 6.1.4.
3. **Revisar la forma general.** `datos.get("servicios")` busca la lista; si no es una lista, o está vacía, se avisa de que falta. Este paso protege contra un TOML que es válido pero que no es el nuestro.
4. **Revisar cada servicio.** Una lista por comprensión (lección 4) llama a `validar_servicio` por cada elemento, con su posición. La función `enumerate(lista, start=1)`, que viste en la lección 3, entrega la posición de cada elemento junto con el elemento; el parámetro `start=1` hace que la cuenta empiece en **1** en lugar de 0, porque «el servicio 2» es la forma en que habla una persona. Al final, `nombres_repetidos` (lección 5) devuelve el conjunto de nombres que aparecen más de una vez. Si no está vacío (`len(repetidos) > 0`, la misma pregunta por el tamaño que ya usaste con las listas), se avisa; `sorted(repetidos)` los pone en orden alfabético y `", ".join(...)` los une en un solo texto separado por comas (`join`, «unir», es un método de los textos que junta los elementos de una lista usando ese texto como separador).

La función `validar_servicio` recibe `datos: object`, el tipo más general que existe, a propósito: **no sabe qué es**, porque viene de fuera. Lo primero es comprobar con `isinstance(datos, dict)` que sea un diccionario. Después revisa campo por campo, en este orden, y se detiene en el primer problema:

- el `nombre` debe existir y ser un texto que no esté vacío (`nombre.strip() == ""` atrapa el texto que solo tiene espacios);
- la `url` debe existir y pasar `es_url_http`: esquema permitido, un servidor y, si lo trae, un puerto válido (6.4.3), y además no debe llevar usuario ni clave (`tiene_credenciales`): una dirección como `http://usuario:clave@...` trae un secreto, y el `revisor` no debe guardarlo ni repetirlo;
- `timeout_ms`, que es opcional, solo se revisa si está presente (`"timeout_ms" not in datos`; el operador `in` pregunta si una llave está en el diccionario), y debe ser un entero mayor que 0 que **no** sea `bool` (6.4.2).

Si todo está bien, devuelve un `Servicio`. Si no hay `timeout_ms`, no lo pasa: el valor por omisión de 5000 lo pone la definición de `Servicio`, que viene de la lección 5. Cada mensaje de error empieza con `servicio N:` para que quien edita el archivo sepa **qué** elemento revisar. Los mensajes que produce el módulo son estos, con la posición contando desde 1:

| Caso | Mensaje |
|---|---|
| no existe el archivo | `no existe el archivo servicios.toml` |
| TOML mal escrito | `servicios.toml no es TOML válido: <mensaje de tomllib>` |
| falta la lista | `falta la lista [[servicios]]` |
| falta un campo | `servicio 2: falta 'nombre'` |
| el servicio no es una tabla | `servicio 2: debe ser una tabla` |
| nombre vacío o que no es texto | `servicio 2: 'nombre' debe ser un texto que no esté vacío` |
| url que no es una dirección http/https válida | `servicio 2: 'url' debe ser una dirección http:// o https:// válida` |
| url con usuario o clave | `servicio 2: 'url' no debe llevar usuario ni clave` |
| tiempo límite inválido | `servicio 3: 'timeout_ms' debe ser un entero mayor que 0` |
| nombres repetidos | `nombres repetidos: catalogo` |

El archivo `formato.py` ganó dos funciones. No cambió ninguna de las anteriores (`formatear_tiempo`, `encabezado`, `linea`, `contar`, `resumen`); solo se agregaron `import json` y `from urllib.parse import urlsplit, urlunsplit` al principio y estas dos funciones al final:

```python
def url_sin_secretos(url: str) -> str:
    partes = urlsplit(url)
    servidor = partes.netloc.rpartition("@")[2]
    return urlunsplit((partes.scheme, servidor, partes.path, "", ""))


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": url_sin_secretos(r.servicio.url),
                "estado": r.estado.value,
                "tiempo_ms": r.tiempo_ms,
                "detalle": r.detalle,
            }
            for r in resultados
        ],
        "resumen": {
            "total": len(resultados),
            "arriba": len([r for r in resultados if r.estado == Estado.ARRIBA]),
            "lento": len([r for r in resultados if r.estado == Estado.LENTO]),
            "caido": len([r for r in resultados if r.estado == Estado.CAIDO]),
            "promedio_ms": promedio_ms,
        },
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)
```

Es la aplicación directa de 6.3.3: se arma un diccionario con tipos que JSON entiende (por eso `r.estado.value` y no `r.estado`), y se serializa con `ensure_ascii=False, indent=2`. El promedio sale como `None` (que JSON escribe `null`) cuando ningún servicio respondió, porque no se puede promediar nada. Fíjate también en una repetición que se deja a propósito: las cuentas de `resumen` y las de este diccionario son las mismas, calculadas dos veces. Se hizo así para no tocar lo que ya funciona en la lección 5, pero es el mismo problema con que empezó esta lección, el de un dato calculado en dos sitios: si algún día cambia la regla del promedio, habrá que cambiarla en los dos. Anótalo en tu bitácora: es el tipo de deuda que se paga la próxima vez que se toque el reporte.

`url_sin_secretos` existe porque el reporte sale de tu programa: se guarda en un archivo, se pega en un chat, lo lee otro programa. Si la dirección trae un secreto en la consulta (`?token=...`) o algo en el fragmento (`#...`), el reporte no debe repetirlo. `urlsplit` parte la dirección (6.4.3); `partes.netloc.rpartition("@")[2]` se queda con lo que va después de la última `@`, es decir, el servidor y el puerto sin usuario ni clave (`rpartition` parte el texto en tres en la última aparición del separador, y `[2]` es la parte de la derecha; si no hay `@`, es el texto entero); y `urlunsplit` vuelve a armar la dirección con el esquema, el servidor y la ruta, y con la consulta y el fragmento vacíos. Así, `http://127.0.0.1:1/estado?token=SECRETO#x` sale en el reporte como `http://127.0.0.1:1/estado`. Una dirección con usuario o clave ni siquiera llega aquí, porque `validar_servicio` la rechaza al cargar; quitarlos también aquí es una segunda red. Se redacta la dirección en vez de quitar el campo porque el JSON es un contrato (lo verás después de la corrida): quien lo lee cuenta con que cada servicio traiga su `url`, y sin los secretos sigue sabiendo a qué servidor y a qué ruta se refiere cada entrada.

Falta el programa principal. Así queda `revisor.py`, que perdió la lista de servicios y ganó una constante con la ruta del archivo:

```python
# fig06_18/revisor.py
from pathlib import Path

from configuracion import ErrorDeConfiguracion, leer_servicios
from formato import encabezado, linea, resumen
from revision import revisar_todos

RUTA_CONFIG = Path("servicios.toml")


def main() -> None:
    try:
        servicios = leer_servicios(RUTA_CONFIG)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        return

    resultados = revisar_todos(servicios)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

`RUTA_CONFIG = Path("servicios.toml")` es una constante (mayúsculas, como `UMBRAL_LENTO_MS`) con la ruta relativa. En `main`, la llamada a `leer_servicios` está dentro de un `try` que atrapa **solo** `ErrorDeConfiguracion`: es la excepción propia de 6.1.4, el único error que este programa sabe explicar. Si ocurre, imprime `error de configuración: ` seguido del mensaje, y `return` termina `main` sin seguir adelante. Cualquier otro error (un `ZeroDivisionError` por un defecto, por ejemplo) no se atrapa, y se detiene con su informe para que alguien lo arregle.

Ojo con una consecuencia: cuando avisa de un error de configuración, el programa termina **con código de salida 0**, el que en la terminal significa «todo bien». Para una persona que lee la pantalla no importa; para otro programa que lo llame y solo mire el código, parece un éxito. Es una deuda que esta lección deja a sabiendas, para no mezclar temas: en la [Lección 7](07-paquete-linea-de-comandos.md) esta rama terminará con el código 2; aquí solo se imprime. Ejecútalo:

```text
$ cd fig06_18
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

Es el mismo reporte de la lección 5, con la misma tabla y el mismo resumen (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`), pero ahora los cuatro servicios vienen de `servicios.toml`. Si agregas un servicio al archivo, aparece en la tabla sin tocar Python (verás un caso en el ejercicio 1).

Para ver el JSON del reporte, el proyecto trae un guion de apoyo, `ver_json.py`. No es parte del programa: solo une la lectura de la configuración, la revisión y `reporte_a_json`, para que veas el resultado antes de que en la lección 7 exista una opción de línea de comandos para pedirlo:

```python
# fig06_18/ver_json.py
from configuracion import leer_servicios
from formato import reporte_a_json
from revision import revisar_todos
from revisor import RUTA_CONFIG

servicios = leer_servicios(RUTA_CONFIG)
print(reporte_a_json(revisar_todos(servicios)))
```

```text
$ python ver_json.py
{
  "servicios": [
    {
      "nombre": "catalogo",
      "url": "https://catalogo.example",
      "estado": "ARRIBA",
      "tiempo_ms": 142,
      "detalle": "200"
    },
    {
      "nombre": "inventario",
      "url": "https://inventario.example",
      "estado": "LENTO",
      "tiempo_ms": 2300,
      "detalle": "200"
    },
    {
      "nombre": "pagos",
      "url": "https://pagos.example",
      "estado": "ARRIBA",
      "tiempo_ms": 87,
      "detalle": "200"
    },
    {
      "nombre": "reportes",
      "url": "https://reportes.example",
      "estado": "CAIDO",
      "tiempo_ms": null,
      "detalle": "sin conexión"
    }
  ],
  "resumen": {
    "total": 4,
    "arriba": 2,
    "lento": 1,
    "caido": 1,
    "promedio_ms": 843
  }
}
```

Es el JSON que el curso fija para el reporte del `revisor`, y no cambia en las lecciones que siguen: `servicios` es una lista con una entrada por servicio, `tiempo_ms` es `null` para el que no respondió, y `resumen` repite las cuentas. Quien consuma ese reporte desde otro programa puede apoyarse en esa forma. Lo único que el reporte le cambia a la dirección es quitarle los secretos: los cuatro servicios de `servicios.toml` no traen ninguno, y por eso su `url` sale igual que en el archivo.

## El error que vas a ver

La lección tiene un error principal, el del archivo que no está donde crees, y cuatro mensajes de apoyo que ya viste y que conviene saber leer de una mirada.

**El error principal.** Ejecuta el `revisor` desde la carpeta **de arriba**, la que contiene a `fig06_18`, en lugar de entrar a ella:

```text
$ python fig06_18/revisor.py
error de configuración: no existe el archivo servicios.toml
```

El programa encuentra el código (le diste la ruta), pero `RUTA_CONFIG` es **relativa**: `Path("servicios.toml")` significa «el `servicios.toml` de la carpeta donde estoy parado», no «el que está junto al programa». Desde la carpeta de arriba, ese archivo no existe. Fíjate en lo que hizo bien el programa: no mostró un informe de error ni la excepción `FileNotFoundError` en inglés con el texto del sistema; mostró el mensaje en español que escribiste, que dice qué falta. Y es el mismo error que verás cualquier día cuando un guion funcione en tu computadora y falle en otra: nueve de cada diez veces el archivo existe, pero **la carpeta desde la que se ejecuta es otra**. Para saber en qué carpeta estás, el comando `pwd` te lo dice. En la lección 7, `--config` te dejará indicar la ruta sin depender de dónde estés.

**Los cuatro mensajes de apoyo**, para leer de abajo hacia arriba:

- `ValueError: invalid literal for int() with base 10: '142 ms'`: un texto que se quiso convertir a entero y no son solo dígitos (`fig06_01.py`). Revisa qué texto llegó.
- `FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'`: la ruta no apunta a nada. Revisa la carpeta de trabajo y la ortografía (`fig06_08.py`).
- `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10`: el archivo no está en UTF-8, y el byte que Python menciona dice en qué posición dejó de cuadrar (`fig06_10.py`).
- `TypeError: Object of type Estado is not JSON serializable`: intentaste serializar un objeto propio sin convertirlo a tipos simples. Arma un diccionario con `.value`.

## Lo que se hace mal

**Escribir `except:` sin tipo, o `except Exception:` por si acaso.** Ya viste el costo en 6.1.3: un error de ortografía se disfraza de otro error; y con el `except:` desnudo, además, el programa puede no detenerse ni con `Ctrl`+`C`. La excepción concreta, siempre.

**Tragarse el error en silencio.** Un `except ValueError: pass` («no hagas nada») hace que el programa siga con datos que no existen. El tiempo de `inventario` queda sin leer, el reporte sale con una fila equivocada, y nadie sabe por qué. Si atrapas una excepción, **haz algo con ella**: avisa, traduce, devuelve un valor definido. Si no sabes qué hacer, no la atrapes.

**Un `try` enorme.** Meter veinte líneas en un `try` para «proteger todo» hace que el `except` atrape errores que no esperabas, de líneas que no tienen que ver, igual que en `fig06_03.py`. El `try` contiene la línea que puede fallar de la manera que conoces, y nada más.

**Traducir una excepción sin `from`.** El informe sigue mostrando la original, pero ya no como causa: queda «durante el manejo de la excepción anterior, ocurrió otra», que es peor para quien depura. Si cambias un error por otro, `raise ... from error`.

**Abrir archivos sin `with`.** Un `archivo = open(...)` sin su `close()` deja el archivo abierto si algo falla antes de cerrarlo, y no se nota hasta que el programa abre cientos.

**Omitir `encoding="utf-8"`.** Funciona en tu computadora y falla (o, peor, lee mal los acentos) en otra. Escríbelo siempre.

**Unir rutas con `+` o con `"/"` dentro de un texto.** Se rompe en cuanto cambia el sistema operativo o sobra una barra. Con `Path` y el operador `/` no hay que pensar en eso.

**Validar con verdad o falsedad.** `if timeout_ms:` deja pasar `True` y, peor, **rechaza el `0`** con el mismo gesto con que rechaza el vacío, sin distinguir los casos. Pregunta exactamente lo que quieres saber: `isinstance(timeout_ms, int)` y `timeout_ms > 0`.

**Validar con `assert`.** La instrucción `assert condicion` falla si la condición es falsa, y parece una forma cómoda de validar. Pero Python puede ejecutarse en un modo de optimización (`python -O`) en el que **todos los `assert` se ignoran**, según la [referencia de la instrucción](https://docs.python.org/3/reference/simple_stmts.html#assert). Una validación que desaparece cuando alguien optimiza el programa no valida nada. Los `assert` son para las pruebas, que verás en la lección 8; para los datos de fuera se usa `if` y `raise`.

**Pasar un dato de fuera a `eval` o a `pickle`.** Es dejar que el autor del archivo decida qué hace tu programa. Se usa TOML o JSON.

## Ejercicios

### Ejercicio 1 — Agrega servicios sin tocar el código

Agrega a tu `servicios.toml` los dos servicios extra del curso: `facturacion` (`https://facturacion.example`) y `notificaciones` (`https://notificaciones.example`, con `timeout_ms = 1000`). Como `revisar` sigue usando datos simulados, agrégales también su entrada en `SIMULADO` de `revision.py`, como en el ejercicio 1 de la lección 5: `facturacion` responde 503 en 95 ms, y `notificaciones` no responde (`tiempo agotado`). Antes de ejecutar, **predice** el resumen: cuántos servicios hay, cuántos arriba, lentos y caídos, y cuál es el promedio. Después ejecuta y compara. ¿Notas algo raro en la tabla?

### Ejercicio 2 — Un archivo roto por cada error

Crea una copia de tu `servicios.toml` llamada `roto.toml` y, cambiando `RUTA_CONFIG` a `Path("roto.toml")`, escribe en ella, uno por uno, archivos que provoquen cada uno de estos mensajes: (a) falta la lista `[[servicios]]`; (b) TOML mal escrito (olvida una comilla); (c) un servicio sin `nombre` en la segunda posición; (d) un servicio con la url `ftp://archivos.example`; (e) `timeout_ms = 0` en el tercer servicio; (f) dos servicios con el nombre `catalogo`. **Para cada uno, escribe primero el mensaje que esperas** y compara después con lo que imprime el `revisor`. Anota en la bitácora los que no acertaste.

### Ejercicio 3 — La trampa de `bool`, en vivo

Escribe un `roto.toml` con un solo servicio que tenga `timeout_ms = true`. Ejecuta el `revisor` y anota el mensaje. Ahora cambia, **temporalmente**, la validación de `timeout_ms` en `configuracion.py` por la versión ingenua (`not isinstance(timeout_ms, int) or timeout_ms <= 0`, sin la parte de `bool`) y vuelve a ejecutar. ¿Qué ocurre? ¿Quién avisa? Restaura la versión correcta y explica con tus palabras por qué la ingenua deja pasar `true`.

### Ejercicio 4 — Un error que la lista no tiene

El `revisor` convierte `FileNotFoundError` y `TOMLDecodeError` en `ErrorDeConfiguracion`, pero no `UnicodeDecodeError`. Provócalo con un `servicios.toml` guardado en `latin-1`, otra codificación, sin perder el tuyo. Desde la carpeta del proyecto: (1) guarda una copia de seguridad con `cp servicios.toml servicios-bien.toml` (`cp` copia un archivo; si el destino ya existe, lo reemplaza sin preguntar, así que elige un nombre que no uses); (2) haz otra copia, `cp servicios.toml acento.toml`, y en `acento.toml`, justo debajo de la `url` del primer servicio, agrega la línea `descripcion = "catálogo de productos"`; (3) convierte esa copia a `latin-1` y escríbela como `servicios.toml`: `iconv -f utf-8 -t latin1 acento.toml > servicios.toml` (`iconv` cambia la codificación de un texto, y `>` escribe su salida en el archivo, **borrando antes lo que tuviera**: por eso el paso 1). Ejecuta el `revisor` y lee el informe de abajo hacia arriba. Luego amplía `leer_servicios` para que ese error también se convierta en `ErrorDeConfiguracion`, con un mensaje que diga qué pasó, y vuelve a ejecutar el `revisor` con el mismo `servicios.toml` en `latin-1` para ver tu mensaje en lugar del *traceback*. Este mensaje no está en la tabla del proyecto: es una ampliación de práctica, y el proyecto de las lecciones siguientes no la incluye. Solo al final, cuando ya viste tu mensaje, devuelve tu configuración con `cp servicios-bien.toml servicios.toml`.

## Soluciones

### Solución 1

Los dos servicios nuevos en `servicios.toml`, al final del archivo:

```toml
[[servicios]]
nombre = "facturacion"
url = "https://facturacion.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
```

Y las dos entradas nuevas de `SIMULADO` en `revision.py`, después de la de `reportes`:

```python
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
```

**Predicción.** Seis servicios. `catalogo` y `pagos` siguen arriba (2). `inventario` sigue lento (1). `reportes` y `notificaciones` no respondieron, y `facturacion` respondió con 503, que la regla de clasificación (un código mayor o igual a 400) marca como caído: son 3 caídos. El promedio se calcula **solo con los que respondieron**: `catalogo` (142), `inventario` (2300), `pagos` (87) y `facturacion` (95), que respondió aunque con error; la suma es 2624 y entre 4 da 656. Resultado esperado: `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`.

**Resultado.** Al ejecutar `python revisor.py`, sale:

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

La predicción coincide con el resumen. **Lo raro** está en la tabla: `notificaciones` mide 14 letras, y la columna del nombre tiene un ancho fijo de 12 (`{nombre:<12}`), así que el nombre invade la columna siguiente y se pega a «CAIDO». `facturacion` cabe por muy poco: tiene 11 letras, y queda un solo espacio. No es un error de esta lección: el formato fue escrito para los cuatro nombres canónicos. La [Lección 11](11-el-programa-terminado.md) lo resuelve calculando el ancho a partir del nombre más largo. Lo importante de este ejercicio es otra cosa: agregaste dos servicios **sin cambiar una línea de lógica**, que era el objetivo de la lección.

### Solución 2

Cada archivo roto y el mensaje que produce. Para (b) el nombre del archivo aparece en el mensaje porque `leer_servicios` usa la ruta que recibe; si lo pruebas con `servicios.toml`, dirá `servicios.toml`.

(a) Un archivo sin la lista:

```toml
titulo = "nada"
```

Mensaje: `error de configuración: falta la lista [[servicios]]`

(b) Una comilla de cierre olvidada:

```toml
[[servicios]]
nombre = "catalogo
```

Mensaje: `error de configuración: roto.toml no es TOML válido: Illegal character '\n' (at line 2, column 19)`

(c) El segundo servicio no tiene nombre:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
url = "https://pagos.example"
```

Mensaje: `error de configuración: servicio 2: falta 'nombre'`

(d) Una dirección que no es web, en el segundo servicio:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "archivos"
url = "ftp://archivos.example"
```

Mensaje: `error de configuración: servicio 2: 'url' debe ser una dirección http:// o https:// válida`

(e) Un tiempo límite en cero, en el tercer servicio:

```toml
[[servicios]]
nombre = "a"
url = "https://a.example"

[[servicios]]
nombre = "b"
url = "https://b.example"

[[servicios]]
nombre = "c"
url = "https://c.example"
timeout_ms = 0
```

Mensaje: `error de configuración: servicio 3: 'timeout_ms' debe ser un entero mayor que 0`

(f) Dos servicios con el mismo nombre:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "catalogo"
url = "https://otro.example"
```

Mensaje: `error de configuración: nombres repetidos: catalogo`

Tres detalles para cuando comparaste. El error del TOML (b) es el único cuyo texto no escribiste tú: viene de `tomllib` y trae la línea y la columna. En (a) la lista no falta a medias: no hay nada, y el mensaje dice exactamente eso. Y en (f) el error se detecta **después** de validar cada servicio por separado, porque sus nombres son válidos uno por uno; el defecto es de la lista entera. Los mensajes se obtuvieron ejecutando cada archivo con el módulo de esta lección.

### Solución 3

Con la validación correcta, el mensaje es el de siempre: `error de configuración: servicio 1: 'timeout_ms' debe ser un entero mayor que 0`.

Con la versión ingenua el `revisor` **no se queja**: imprime su tabla normal, y el resumen sale sin problema. El `Servicio` quedó con `timeout_ms=True`, y como `True` es el número 1, el tiempo límite que el programa cree tener es de un milisegundo. Nadie avisa: es un error que no hace ruido, y aparecerá en la lección 9, cuando el `revisor` use ese tiempo límite: con un milisegundo de espera, casi cualquier petición real se agotaría, y el servicio saldría caído por «tiempo agotado» sin motivo aparente. Se produce porque, en Python, `bool` es un tipo de entero (`isinstance(True, int)` es `True`), y la validación ingenua solo pregunta eso. La versión correcta añade `isinstance(timeout_ms, bool)` para rechazar los booleanos explícitamente.

### Solución 4

Al ejecutar con el archivo en `latin-1`, la última línea del informe es:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 85: invalid continuation byte
```

El byte `0xe1` es la «á» de «catálogo» en `latin-1`; la posición 85 es donde cae en el archivo, contando los bytes desde 0: es la que sale si pusiste la línea donde dice el ejercicio, y será otra si la pusiste en otro lugar. Las líneas de arriba pasan por `read_text` y la biblioteca estándar: el error nace dentro de la lectura, no en tu código, y tú lo ves subir por tus funciones. Para convertirlo, se agrega un segundo `except` en el primer paso de `leer_servicios`:

```python
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error
    except UnicodeDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no está guardado en UTF-8") from error
```

Con eso, el `revisor` imprime `error de configuración: servicios.toml no está guardado en UTF-8`. Observa que `UnicodeDecodeError` es un tipo de `ValueError`, pero no hace falta atrapar `ValueError`: con el tipo concreto, un `ValueError` de otra causa no se disfraza.

## Cómo sé que lo logré

- [ ] `python fig06_01.py` termina con el informe de `ValueError`, y puedes decir qué función llamó a cuál, de abajo hacia arriba, sin mirar la lección.
- [ ] `python fig06_03.py` dice que «142» no es un número, y puedes explicar por qué eso es una mentira y qué línea del programa tiene el error de verdad.
- [ ] En `fig06_05.py` ves la frase «The above exception was the direct cause of the following exception», y sabes qué instrucción del código la produjo.
- [ ] Desde `fig06_18/`, `python revisor.py` imprime la tabla de cuatro servicios con el resumen `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Desde la carpeta de arriba, `python fig06_18/revisor.py` imprime `error de configuración: no existe el archivo servicios.toml`, y sabes explicar por qué.
- [ ] Los seis archivos rotos del ejercicio 2 producen los seis mensajes de la tabla, y los predijiste antes de ejecutar.
- [ ] `python ver_json.py` imprime un JSON con `null` en el `tiempo_ms` de `reportes` y con `"promedio_ms": 843`.
- [ ] Puedes explicar por qué `isinstance(True, int)` es `True` y qué validación del `revisor` lo tiene en cuenta.
- [ ] Anotaste en tu bitácora qué error de esta lección te costó leer.

## Resumen

Responde sin mirar la lección:

1. ¿De qué lado se lee un informe de error, y qué dice su última línea?
2. ¿Qué diferencia hay entre el `else` y el `finally` de un `try`? ¿Cuál se ejecuta aunque haya un `return`?
3. ¿Por qué no se escribe `except:` sin tipo, ni `except Exception:` por si acaso? ¿Qué pasa con el error que no sabes manejar?
4. ¿Qué hace `raise ... from error`, y qué pasa en el informe si lo omites?
5. ¿Qué garantiza un `with`? ¿Por qué se escribe `encoding="utf-8"` siempre?
6. ¿Qué devuelve `tomllib.loads`? ¿Qué diferencia hay entre `datos["servicios"]` y `datos.get("servicios")` si la llave no existe?
7. ¿Qué tres cosas hacen distinto `json.dumps(x)` y `json.dumps(x, ensure_ascii=False, indent=2)`? ¿Por qué falla `json.dumps(Estado.CAIDO)`?
8. ¿Por qué `isinstance(True, int)` es `True`? ¿Cómo se escribe la validación de un entero positivo que rechaza `true`?
9. ¿Por qué se valida el esquema de una dirección con una lista de lo permitido y no con una de lo prohibido?
10. ¿Qué riesgo tiene `eval` con un texto que viene de fuera, y qué formato se usa en su lugar?

## Para leer más

- [Python, «Errores y excepciones» (tutorial oficial)](https://docs.python.org/3/tutorial/errors.html): `try`, `except`, `else`, `finally`, excepciones propias y encadenadas, con más ejemplos que esta lección. En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [Python, `tomllib`](https://docs.python.org/3/library/tomllib.html) y [la especificación de TOML](https://toml.io/en/v1.0.0): lo que el módulo lee y las reglas del formato, incluidas las tablas y las listas de tablas. Consultado el 7 de octubre de 2026.
- [Python, `json`](https://docs.python.org/3/library/json.html) y [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259): la biblioteca y la norma del formato. Consultado el 7 de octubre de 2026.
- [OWASP, «Input Validation Cheat Sheet»](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): por qué se valida en la frontera y por qué una lista de lo permitido funciona mejor que una de lo prohibido. Consultado el 7 de octubre de 2026.
