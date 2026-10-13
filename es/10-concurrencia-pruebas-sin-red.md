# Lección 10 — Concurrencia con límites y pruebas sin red

**Tiempo:** 2 × 90 min (la primera sesión llega hasta el final de 10.2; la segunda empieza en 10.3)

**Qué construyes:** el `revisor` concurrente y probado, versión 0.9.0

**Qué aprendes:** `asyncio.TaskGroup`; `asyncio.timeout()` y `asyncio.Semaphore`; grupos de excepciones (`ExceptionGroup`, `except*`) y por qué un fallo no tumba el reporte; pruebas sin red con `httpx.MockTransport` y `monkeypatch`

**De dónde vienes.** Traes el paquete de la [Lección 9](09-http-y-asyncio.md): el `revisor` ya consulta de verdad, con `httpx`, un tiempo límite por servicio y una función `revisar` que nunca deja escapar un error de red. Pero lo hace **en fila**: `for` y `await`, un servicio a la vez. Con los cuatro servicios del laboratorio la corrida tarda la suma de las esperas, unos 2.5 segundos, y con veinte servicios de medio segundo tardaría diez. Además tiene una deuda que la lección anterior dijo de frente: sus 21 pruebas no tocan nada de lo nuevo, porque probar código que usa la red todavía no sabes hacerlo. Hoy se pagan las dos cosas. Trabajas en tu carpeta `~/curso-python/revisor/`, con el entorno virtual activado, y necesitas tener a la mano el `laboratorio.py` de la lección 9 para la parte de medir.

**Qué no hace esta lección.** No cambia lo que el `revisor` imprime: la tabla y el JSON salen igual que en la Lección 9. Lo que cambia es **cuánto tarda** y **qué tan seguro es**. Tampoco usa hilos ni procesos: toda la concurrencia de hoy ocurre en un solo hilo, que es lo que conviene cuando lo que se hace es esperar a la red. El reporte final con ancho de columna calculado, el registro de eventos (`logging`) y la instalación como comando son de la [Lección 11](11-el-programa-terminado.md).

## Al terminar vas a poder

- Lanzar varias consultas a la vez con `asyncio.TaskGroup`, recoger sus resultados en el orden de la configuración y medir con el reloj que el total se parece al servicio más lento y no a la suma.
- Explicar por qué una tarea solo cede el turno en un `await`, y por qué un `time.sleep` dentro de una corrutina deshace toda la ganancia.
- Poner un techo de tiempo a una operación entera con `asyncio.timeout()` y decir en qué se distingue de los tiempos límite de `httpx`.
- Limitar cuántas consultas corren a la vez con `asyncio.Semaphore`, y explicar por qué con 20 servicios y un límite de 10 el tiempo es el doble que con límite 20.
- Leer un `ExceptionGroup` y atrapar lo que contiene con `except*`; decir por qué `revisar` convierte los errores de red en resultados y por qué **no** convierte los errores de programación.
- Probar `revisar` y `revisar_todos` sin tocar la red, con `httpx.MockTransport`, y probar `main` cambiando una función por otra con `monkeypatch`.
- Comprobar en rojo una prueba (romper el código, verla fallar, arreglarlo) y leer el conteo del informe de `pytest`.

## El porqué antes del cómo

Imagina que el `revisor` lo usa la guardia de una empresa para revisar sesenta servicios cada cinco minutos. Cada servicio sano contesta en medio segundo; los caídos tardan en rendirse hasta su tiempo límite, digamos cinco segundos. En fila, el mejor día la corrida tarda treinta segundos, y el peor día, con diez servicios caídos, tarda setenta y cinco (cincuenta sanos por medio segundo, más diez caídos por cinco segundos). Pero la computadora no estuvo trabajando durante esos setenta y cinco segundos: estuvo **esperando**. Mandó una petición, se quedó mirando la pared hasta que llegó la respuesta, y solo entonces mandó la siguiente. La red no necesita que el programa haga fila: las sesenta peticiones pueden estar viajando a la vez, y el programa solo tiene que recoger las respuestas conforme lleguen.

Eso es lo que hace `asyncio` bien, y por eso existe esta lección. Pero hay tres problemas escondidos detrás de «hazlo todo a la vez», y cada uno es un concepto de hoy.

El primero es **cómo se lanzan y se recogen** muchas consultas sin perder ninguna. Python 3.11 trajo una herramienta pensada para eso, `asyncio.TaskGroup`, que arranca las tareas, las espera a todas antes de seguir y no deja que ninguna se pierda por el camino.

El segundo es **hasta dónde**. «Todo a la vez» con sesenta servicios es razonable. Con seis mil puede ser un ataque a tus propios servidores, o tu sistema operativo diciendo que ya no te da más conexiones. Hace falta un límite de cuántas consultas corren simultáneamente, y hace falta un techo de tiempo para que ninguna se quede colgada para siempre.

El tercero es **qué pasa cuando algo falla**. En fila, un error detiene el programa en el punto exacto en que ocurrió, y es fácil de entender. Con muchas tareas a la vez, una falla puede afectar a las demás, y lo que Python te entrega no es una excepción sino un **grupo** de ellas. Si no lo entiendes, un solo servicio caído puede tumbar el reporte entero, que es exactamente lo contrario de lo que el `revisor` promete.

Y debajo de todo, el cuarto problema, el de la confianza: un programa que hace tantas cosas a la vez, con tiempos y fallos mezclados, **no se puede probar a mano** de manera repetible. Si para comprobar que «un servicio colgado no tumba el reporte» necesitas colgar un servicio de verdad, nunca vas a comprobarlo dos veces igual. La cuarta parte de la lección enseña a probar todo eso sin red: con un servidor de mentira que contesta lo que tú digas, al instante, siempre igual.

## Los conceptos

### 10.1 `TaskGroup`: todas a la vez

#### 10.1.1 Lo que cuesta esperar en fila

Antes de arreglar algo hay que medirlo. Este primer programa no usa la red: cada «servicio» es una espera de verdad, hecha con `asyncio.sleep`, que es la forma de decir «no hagas nada durante este tiempo, pero déjame hacer otra cosa mientras». Las esperas son las de cuatro servicios inventados, de una décima a medio segundo, para que las corridas sean cortas.

```python
# fig10_01.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    for nombre, espera_s in ESPERAS_S.items():
        await consultar(nombre, espera_s)
    print(f"en serie: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_01.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
en serie: 1.1 s
```

Lee `main` de arriba abajo. `time.perf_counter()` es el reloj para medir intervalos que ya usaste en la Lección 9: se llama al principio y al final, y la resta es el tiempo transcurrido. El `for` recorre el diccionario con `.items()` (que te da cada pareja nombre-espera) y, por cada una, hace `await consultar(...)`. El `await` dice «espera aquí a que esta corrutina termine»; hasta que no termina, el `for` no pasa a la siguiente vuelta. Por eso las respuestas salen en el orden en que se pidieron, y por eso el total, 1.1 segundos, es la suma exacta: 0.3 más 0.5 más 0.1 más 0.2.

Es el mismo problema que mediste en la Lección 9 con el `revisor`: `await` sobre **una corrutina sola** espera a que termine antes de seguir. No es un defecto del `await`; es lo que significa. Para que dos esperas ocurran a la vez hace falta que las dos **existan** al mismo tiempo, y para eso sirve una tarea.

#### 10.1.2 Una tarea: una corrutina que ya está en marcha

Una **corrutina** es una receta: `consultar("catalogo", 0.3)` no hace nada, solo produce el objeto-receta, y la receta empieza a ejecutarse cuando alguien le hace `await`. Una **tarea** (*task*) es una corrutina a la que ya se le dio cuerda: el bucle de eventos la tiene anotada en su lista de pendientes y la ejecuta en cuanto pueda, **sin que nadie la esté esperando todavía**. El **bucle de eventos** (*event loop*) es la pieza de `asyncio` que lleva esa lista: toma una tarea, la ejecuta hasta que se topa con un `await` que tiene que esperar, la pone en pausa, toma la siguiente, y así sucesivamente, en un solo hilo.

Con eso en la mano, la versión a la vez:

```python
# fig10_02.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    print(f"{nombre}: empieza")
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        tareas = [
            grupo.create_task(consultar(nombre, espera_s))
            for nombre, espera_s in ESPERAS_S.items()
        ]
    print(f"a la vez: {time.perf_counter() - inicio:.1f} s")
    print([tarea.result() for tarea in tareas])


asyncio.run(main())
```

```text
$ python fig10_02.py
catalogo: empieza
inventario: empieza
pagos: empieza
reportes: empieza
pagos: respondió
reportes: respondió
catalogo: respondió
inventario: respondió
a la vez: 0.5 s
['catalogo', 'inventario', 'pagos', 'reportes']
```

Cambió una sola cosa: en lugar de `await consultar(...)` dentro del `for`, se hace `grupo.create_task(consultar(...))`. Eso **no espera**: registra la tarea y regresa enseguida, con un objeto `Task` en la mano. Por eso el `for` (aquí, dentro de una comprensión de lista, que es el `for` en una línea de la Lección 4) pasa por los cuatro servicios en un instante y deja cuatro tareas pendientes. Mira la salida: los cuatro «empieza» salen primero, seguidos, antes de que ninguno responda. Luego responden en orden de **rapidez**, no de petición: `pagos` (0.1 s), `reportes` (0.2 s), `catalogo` (0.3 s), `inventario` (0.5 s). Y el total ya no es 1.1 sino 0.5: el del más lento.

¿Y el `async with asyncio.TaskGroup() as grupo:`? Es lo que hace que esto sea seguro. Funciona como el `with` de la Lección 6: al **salir** del bloque, el grupo **espera a que todas las tareas que creó terminen**. Por eso la línea `print(f"a la vez: ...")`, que está después del bloque, solo se ejecuta cuando las cuatro respondieron. Puedes crear las tareas donde quieras dentro del bloque; no puedes olvidarte de ninguna, porque el bloque no te deja salir mientras haya una viva. Eso es lo que la [documentación de `asyncio`](https://docs.python.org/3/library/asyncio-task.html#task-groups) llama *concurrencia estructurada*: las tareas nacen y mueren dentro de un bloque con sangría, igual que un `with` cierra su archivo.

#### 10.1.3 Los resultados y su orden

`create_task` devuelve la tarea, y la tarea guarda su resultado. Después del bloque, `tarea.result()` te lo entrega: si la tarea terminó bien, el valor que devolvió su función; si falló, vuelve a lanzar la excepción. Fíjate en el detalle que importa para el `revisor`: guardamos las tareas **en una lista, en el orden de los servicios**, y después sacamos los resultados **recorriendo esa lista**. Las respuestas llegaron en desorden (pagos primero), pero la última línea de la salida, `['catalogo', 'inventario', 'pagos', 'reportes']`, está en el orden de la configuración. Ese orden no es un lujo: un reporte donde las filas cambian de lugar cada corrida es ilegible, y un JSON que se compara contra el de ayer necesita estar en el mismo orden. La regla es sencilla: **el orden en que llegan las respuestas lo decide la red; el orden en que se muestran lo decides tú**, y se decide guardando las tareas en una lista y no apilando los resultados según van terminando.

#### 10.1.4 Una tarea solo cede el turno en un `await`

Falta una pieza para que el modelo mental esté completo, y es la que más errores produce. El bucle de eventos corre **en un solo hilo**. Cuando ejecuta una tarea, esa tarea tiene el hilo entero hasta que ella misma lo suelta, y lo suelta únicamente en un `await` que tiene que esperar. Entre dos `await`, nadie más corre. A eso se le llama concurrencia **cooperativa**: las tareas cooperan cediendo el turno. Si una tarea no coopera, bloquea a todas. Mira qué pasa si en lugar de `await asyncio.sleep(...)` se usa el `time.sleep(...)` de siempre, que es una espera que **no cede nada**:

```python
# fig10_03.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    time.sleep(espera_s)  # noqa: ASYNC251
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for nombre, espera_s in ESPERAS_S.items():
            grupo.create_task(consultar(nombre, espera_s))
    print(f"TaskGroup con time.sleep: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_03.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
TaskGroup con time.sleep: 1.1 s
```

Es el mismo `TaskGroup` de la figura anterior, con las cuatro tareas creadas igual. Pero el resultado es otro: se imprimen en el orden en que se crearon, no en el de rapidez, y el total es 1.1 segundos, la suma. ¿Por qué? Porque la primera tarea llegó a `time.sleep(0.3)`, y `time.sleep` detiene **el hilo**, y con el hilo detenido el bucle de eventos no puede ni pasar a la siguiente tarea. Las otras tres esperaron su turno, en fila, aunque estén en un `TaskGroup`. Este error es especialmente traicionero porque **el programa no falla**: da el resultado correcto, solo que tan lento como si no hubiera concurrencia. El comentario `# noqa: ASYNC251` está ahí porque `ruff` (la herramienta de la Lección 8) conoce este error y lo marca, aunque no con el conjunto de reglas del `revisor`: `ASYNC251` es de la colección `ASYNC`, la de los errores de `asyncio`, que no está en el `select` del proyecto (`E`, `F`, `I`, `B`, `UP`). Si se la pides, `ruff check --select ASYNC` sobre esta figura sin ese comentario dice ``ASYNC251 Async functions should not call `time.sleep` ``. Y si tu código usa `asyncio` en serio, es buena candidata a entrar en tu `select`. En esta figura lo dejamos a propósito para mostrar el daño; en tu código real, el aviso de `ruff` es una pista a seguir.

La regla práctica: dentro de una corrutina, todo lo que espere (red, disco lento, tiempo) debe ser un `await` sobre algo hecho para `asyncio`: `asyncio.sleep`, `httpx.AsyncClient`. Una llamada normal que tarde (un `time.sleep`, un cálculo largo, una función de `requests`) no coopera y se lleva puesto a todo el bucle. Es la razón por la que el curso usa `httpx` y no `requests`: `httpx` sabe esperar sin bloquear. El capítulo de la documentación sobre [cómo desarrollar con `asyncio`](https://docs.python.org/3/library/asyncio-dev.html) trae el modo de depuración, que avisa cuando una tarea retiene el hilo demasiado tiempo.

### 10.2 Límites: un techo de tiempo y un tope de simultáneas

#### 10.2.1 `asyncio.timeout()`: el techo de una operación entera

Desde la Lección 9 sabes que toda petición debe llevar un tiempo límite: sin él, un servicio colgado hace esperar al `revisor` para siempre. `httpx` ya tiene uno, el que le pasas con `httpx.Timeout(...)`. Entonces ¿para qué otro?

Porque los tiempos límite de `httpx` miden **fases**, no el total. Según [su documentación](https://www.python-httpx.org/advanced/timeouts/), `httpx` distingue cuatro: el de **conexión** (cuánto esperar para abrir el canal), el de **lectura** (cuánto esperar el siguiente trozo de datos), el de **escritura** y el de **espera de un canal libre en el conjunto de conexiones**. `httpx.Timeout(5.0)` pone esos cuatro en 5 segundos, cada uno por su lado. Un servidor que manda un byte cada cuatro segundos nunca dispara el de lectura —cada trozo llega a tiempo—, y la respuesta puede tardar minutos. `httpx` no hizo nada mal: cada fase cumplió su límite. Lo que falta es un límite al **conjunto**. Eso es `asyncio.timeout()`, que existe desde Python 3.11 y está en la [documentación de `asyncio`](https://docs.python.org/3/library/asyncio-task.html#timeouts):

```python
# fig10_04.py
import asyncio
import time


async def servicio_colgado() -> None:
    await asyncio.sleep(10)


async def main() -> None:
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(1):
            await servicio_colgado()
    except TimeoutError:
        print(f"tiempo agotado tras {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_04.py
tiempo agotado tras 1.0 s
```

El bloque `async with asyncio.timeout(1):` pone un reloj de 1 segundo a todo lo que ocurra dentro. Adentro hay una espera de 10 segundos. Al cumplirse el segundo, `asyncio` **cancela** lo que esté esperando dentro del bloque y, al salir, lanza `TimeoutError` (una excepción normal de Python, desde la 3.11; antes se llamaba `asyncio.TimeoutError`, que hoy es solo otro nombre para la misma). El `except TimeoutError` la atrapa, y el programa imprime el tiempo que de verdad esperó: 1.0 segundos, no 10. Aprende los dos efectos del bloque: **corta** la espera (no se quedan colgadas las tareas) y **avisa** con una excepción que tú decides cómo tratar.

Los dos mecanismos no se estorban; se complementan. En el `revisor` de hoy conviven: `httpx.Timeout` pone el límite a cada fase, y `asyncio.timeout` el del servicio completo. Los dos usan `timeout_ms` del servicio, y cualquiera de los dos que se cumpla primero produce el mismo resultado: «tiempo agotado». Más adelante, en 10.4, verás una de las ventajas de tener los dos: el techo de `asyncio` funciona aun cuando `httpx` no participa.

#### 10.2.2 `asyncio.Semaphore`: cuántas a la vez, a lo mucho

Un **semáforo** (*semaphore*) es un contador de permisos. Se crea con un número, `asyncio.Semaphore(2)`: hay dos permisos. Quien quiere entrar hace `async with semaforo:`; si queda un permiso, lo toma y entra, y si no, **espera** hasta que otro lo devuelva al salir. Es la entrada de un estacionamiento con dos lugares: cuando está lleno, el siguiente coche espera en la calle hasta que sale uno. La [documentación](https://docs.python.org/3/library/asyncio-sync.html#semaphore) lo describe en esos términos. Veamos seis servicios de medio segundo con espacio para dos a la vez:

```python
# fig10_05.py
import asyncio
import time


async def consultar(semaforo: asyncio.Semaphore, numero: int) -> None:
    async with semaforo:
        print(f"servicio {numero}: entra")
        await asyncio.sleep(0.5)
        print(f"servicio {numero}: sale")


async def main() -> None:
    semaforo = asyncio.Semaphore(2)
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for numero in range(1, 7):
            grupo.create_task(consultar(semaforo, numero))
    print(f"seis servicios, de dos en dos: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_05.py
servicio 1: entra
servicio 2: entra
servicio 1: sale
servicio 2: sale
servicio 3: entra
servicio 4: entra
servicio 3: sale
servicio 4: sale
servicio 5: entra
servicio 6: entra
servicio 5: sale
servicio 6: sale
seis servicios, de dos en dos: 1.5 s
```

Lee la salida en grupos de cuatro líneas. Entran el 1 y el 2; salen los dos medio segundo después; recién entonces entran el 3 y el 4, y así. Seis servicios, dos a la vez: tres tandas de medio segundo, 1.5 segundos en total. Todas las tareas se crearon de golpe en el `TaskGroup`, pero cuatro de ellas se quedaron esperando en `async with semaforo` sin gastar nada. Fíjate también en el orden: el 3 entra antes que el 4, el 5 antes que el 6. En CPython el semáforo suele atender en el orden en que llegaron, pero la [documentación](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) no lo promete (sí lo promete para `Lock`), así que tu programa no debe depender de ese orden. El `revisor` no depende: el orden de su reporte lo da la lista de servicios, no el orden en que terminaron.

¿Cuánto vale el límite correcto? Depende de **quién recibe** las consultas. Si son tus propios servicios, lo que aguantan; si son de un tercero, lo que su documentación permita; si son muchos y no sabes, un número moderado. El `revisor` usa **10** por omisión y deja que el usuario lo cambie con `--concurrencia`. El semáforo también protege a tu propia máquina: cada conexión abierta gasta un descriptor de archivo, y cada sistema operativo tiene un tope. Y `httpx` limita por su cuenta el conjunto de conexiones abiertas (100 por omisión, como dice [su documentación de límites](https://www.python-httpx.org/advanced/resource-limits/)), así que un límite mayor que ese solo haría que las consultas esperaran en otra fila.

#### 10.2.3 Llevarlo al `revisor`

Todo el cambio de esta mitad cabe en tres archivos y un archivo de datos nuevo. Primero la versión del paquete, `0.9.0` (la dependencia de `httpx` ya estaba desde la 9):

```toml fig10_08/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.9.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = ["httpx>=0.28"]

[project.scripts]
revisor = "revisor.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

Luego el corazón, `revision.py`. Léelo en tres movimientos:

```python
# fig10_08/src/revisor/revision.py
import asyncio
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(servicio.timeout_ms / 1000):
            respuesta = await cliente.get(servicio.url, timeout=limite)
    except (httpx.TimeoutException, TimeoutError):
        return Resultado(servicio, Estado.CAIDO, None, "tiempo agotado")
    except httpx.ConnectError:
        return Resultado(servicio, Estado.CAIDO, None, "sin conexión")
    except httpx.HTTPError:
        return Resultado(servicio, Estado.CAIDO, None, "error de red")
    except (httpx.InvalidURL, ValueError):
        return Resultado(servicio, Estado.CAIDO, None, "dirección inválida")
    tiempo_ms = round((time.perf_counter() - inicio) * 1000)
    estado = clasificar(respuesta.status_code, tiempo_ms)
    return Resultado(servicio, estado, tiempo_ms, str(respuesta.status_code))


async def _revisar_con_limite(
    semaforo: asyncio.Semaphore, cliente: httpx.AsyncClient, servicio: Servicio
) -> Resultado:
    async with semaforo:
        return await revisar(cliente, servicio)


async def revisar_todos(
    servicios: list[Servicio],
    limite: int = 10,
    transporte: httpx.AsyncBaseTransport | None = None,
) -> list[Resultado]:
    if limite < 1:
        raise ValueError("el límite debe ser al menos 1")
    semaforo = asyncio.Semaphore(limite)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        async with asyncio.TaskGroup() as grupo:
            tareas = [
                grupo.create_task(_revisar_con_limite(semaforo, cliente, servicio))
                for servicio in servicios
            ]
    return [tarea.result() for tarea in tareas]
```

**Primero, `revisar`** (una sola consulta). Cambió muy poco respecto a la Lección 9: el `await cliente.get(...)` ahora vive dentro de `async with asyncio.timeout(servicio.timeout_ms / 1000):`. La división entre mil es porque `timeout_ms` está en milisegundos y `asyncio.timeout` quiere segundos. En el `except`, `(httpx.TimeoutException, TimeoutError)` atrapa los dos tiempos agotados: el de fase de `httpx` y el techo de `asyncio`. Con paréntesis, porque en Python 3.12 un `except` con dos clases las lleva dentro de una tupla. Lo demás es igual: cada error de red se convierte en un `Resultado` con su detalle, y la función **nunca** deja salir un error de red. Hay una excepción que `revisar` **no** atrapa a propósito y que merece un párrafo: `asyncio.CancelledError`. Es la forma en que `asyncio` le avisa a una tarea «te cancelaron». Si la atraparas, tragarías la orden de cancelar y el `TaskGroup` o el `timeout` quedarían sin poder hacer su trabajo. Por eso el `except` nombra clases concretas y nunca es un `except Exception` ancho: la regla de la Lección 6 (nada de `except:` desnudo) ahora tiene una razón más.

**Segundo, `_revisar_con_limite`**: tres líneas que toman un permiso del semáforo y revisan. Está **fuera** de `revisar` por una razón de medición. Si el semáforo estuviera dentro, el reloj de `revisar` empezaría a correr antes de obtener el permiso, y un servicio que esperó su turno medio segundo aparecería como «lento» sin serlo. Con el permiso afuera, el tiempo que `revisar` mide es el de la consulta, y la espera en la fila del semáforo no se cuenta. Lo mismo vale para el techo de `asyncio.timeout`: empieza a contar cuando la consulta empieza, no cuando la tarea se creó.

**Tercero, `revisar_todos`**. Su firma cambió: ahora recibe `limite` (por omisión 10) y `transporte`, que por ahora puedes ignorar (existe para 10.4: es la puerta por la que las pruebas meten un servidor de mentira). Línea por línea: si `limite` es menor que 1 lanza `ValueError`, porque `Semaphore(0)` no explota: deja a todo el mundo esperando un permiso que nunca llega, y el programa se queda colgado sin decir nada. Se crea el semáforo. Se abre **un solo** `httpx.AsyncClient` para todas las consultas, porque un cliente mantiene un conjunto de conexiones reutilizables y abrir veinte clientes sería desperdicio. Se abre el `TaskGroup`, y la comprensión crea una tarea por servicio, **en el orden de la lista**. Al salir del bloque, todas terminaron. La última línea, fuera de los `async with`, arma la lista de resultados recorriendo las tareas en ese mismo orden: así el reporte respeta la configuración sin importar quién contestó primero.

Falta que el usuario pueda elegir el límite. En `cli.py`:

```python
# fig10_08/src/revisor/cli.py
import argparse
import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import encabezado, linea, reporte_a_json, resumen
from revisor.modelo import Estado
from revisor.revision import revisar_todos


def entero_positivo(texto: str) -> int:
    try:
        numero = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{texto!r} no es un entero") from None
    if numero < 1:
        raise argparse.ArgumentTypeError("debe ser al menos 1")
    return numero


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="revisor",
        description="Revisa el estado de una lista de servicios.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("servicios.toml"),
        help="archivo TOML con la lista de servicios (por omisión: servicios.toml)",
    )
    parser.add_argument(
        "--formato",
        choices=["tabla", "json"],
        default="tabla",
        help="forma del reporte (por omisión: tabla)",
    )
    parser.add_argument(
        "--concurrencia",
        type=entero_positivo,
        default=10,
        help="cuántos servicios se consultan a la vez (por omisión: 10)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"revisor {version('revisor')}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
    if argumentos.formato == "json":
        print(reporte_a_json(resultados))
    else:
        print(encabezado())
        for resultado in resultados:
            print(linea(resultado))
        print()
        print(resumen(resultados))

    problemas = [r for r in resultados if r.estado is not Estado.ARRIBA]
    if len(problemas) == 0:
        return 0
    return 1
```

Hay dos cosas nuevas. `entero_positivo` es una función que `argparse` usa para convertir y validar el texto que el usuario escribió después de `--concurrencia`: si no es un entero, o es menor que 1, lanza `argparse.ArgumentTypeError`, y `argparse` lo convierte en su error de uso con código de salida **2**, el mismo código que ya usabas para «el uso es inválido». Dos detalles de escritura en esa función. `{texto!r}` dentro de la f-string pide la *representación* del valor en lugar del texto tal cual: un texto sale con sus comillas (`'diez'`), y así el mensaje deja ver exactamente qué escribió el usuario, incluso si fueron espacios. Y `raise ... from None` es el `raise ... from` de la Lección 6 con la intención contraria: en lugar de conservar el error original como causa, lo **oculta**, porque el `ValueError` de `int` no le dice nada a quien escribió `--concurrencia diez` y el mensaje nuevo ya lo dice todo. Por último, en `main` la llamada pasó a ser `revisar_todos(servicios, limite=argumentos.concurrencia)`.

Para medir con algo más interesante que cuatro servicios, hay un archivo con veinte, todos apuntando a la ruta `/espera/500` del laboratorio (cada uno contesta tras medio segundo):

```toml fig10_08/servicios-20.toml
[[servicios]]
nombre = "servicio01"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio02"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio03"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio04"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio05"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio06"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio07"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio08"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio09"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio10"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio11"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio12"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio13"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio14"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio15"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio16"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio17"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio18"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio19"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio20"
url = "http://127.0.0.1:8099/espera/500"
```

Con el laboratorio corriendo en otra terminal (`python laboratorio.py`, como en la Lección 9), mide tres veces la misma corrida. `time` es un comando de la terminal que ejecuta lo que le sigue y, al final, dice cuánto tardó; la línea `real` es el tiempo del reloj de pared. Con `| tail -n 1` solo se conserva la última línea del reporte, el resumen, para no ver veinte filas:

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 507ms

real	0m10.263s
user	0m0.154s
sys	0m0.029s

$ time python -m revisor --config servicios-20.toml --concurrencia 10 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m1.146s
user	0m0.115s
sys	0m0.024s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m0.627s
user	0m0.104s
sys	0m0.019s
```

Los números cuentan la historia. Con `--concurrencia 1` (un permiso, es decir, en fila) tarda **10.3 segundos**: veinte esperas de medio segundo. Con 10 tarda **1.15**: veinte servicios, diez a la vez, son dos tandas de medio segundo. Con 20 tarda **0.63**: una sola tanda. ¿Por qué 10 da el doble que 20 y no algo intermedio? Porque con límite 10 los primeros diez ocupan los permisos durante medio segundo, y los otros diez **no pueden empezar** hasta que se libere alguno: dos tandas seguidas. Con límite 20 caben todos de golpe. Y ¿por qué 0.63 y no 0.5? Porque el reloj de `time` incluye lo que no es espera de red: arrancar Python, importar `httpx`, abrir las conexiones. Son entre 0.1 y 0.15 segundos que no dependen de cuántos servicios haya. Si tu máquina es más lenta, los tuyos serán un poco mayores; la **proporción** entre las tres corridas es lo que importa.

Con eso termina la primera sesión. Lo que tienes es un `revisor` que consulta varios servicios a la vez y no abusa. Lo que le falta es resistir los fallos y, sobre todo, **demostrar** que los resiste.

### 10.3 Grupos de excepciones: un fallo no tumba el reporte

#### 10.3.1 Qué pasa cuando una tarea falla

Hasta ahora todo salió bien. El `TaskGroup` tiene una regla para cuando no sale bien, y conviene verla con los ojos antes de leerla: si **una** de las tareas termina con una excepción, el grupo **cancela a las demás**. Mira qué le ocurre a un reporte con tres tareas, una de las cuales se rompe:

```python
# fig10_06.py
import asyncio


async def consulta_buena(nombre: str, espera_s: float) -> None:
    try:
        await asyncio.sleep(espera_s)
        print(f"{nombre}: terminó")
    except asyncio.CancelledError:
        print(f"{nombre}: cancelada")
        raise


async def consulta_rota(nombre: str) -> None:
    await asyncio.sleep(0.1)
    raise ConnectionError(f"{nombre}: sin conexión")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as grupo:
            grupo.create_task(consulta_buena("catalogo", 0.05))
            grupo.create_task(consulta_rota("reportes"))
            grupo.create_task(consulta_buena("inventario", 0.5))
    except* ConnectionError as grupo_de_errores:
        for error in grupo_de_errores.exceptions:
            print(f"falló: {error}")
    print("fin")


asyncio.run(main())
```

```text
$ python fig10_06.py
catalogo: terminó
inventario: cancelada
falló: reportes: sin conexión
fin
```

Hay tres tareas dentro del grupo. `catalogo` espera 0.05 segundos y termina bien. `reportes` espera 0.1 y lanza `ConnectionError` (la excepción de Python para una conexión que no se pudo hacer; es la prima de la `httpx.ConnectError` que usa el `revisor`). `inventario` espera 0.5 segundos. Mira la salida: `catalogo` terminó, `inventario` fue **cancelada** (nunca llegó a decir «terminó»; el medio segundo que le faltaba se perdió), y la excepción de `reportes` salió por el `except*`.

En el código hay dos formas nuevas. La primera está en `consulta_buena`: el `except asyncio.CancelledError:` imprime «cancelada» y luego hace `raise` a secas. Un `raise` sin nada más **vuelve a lanzar la excepción que se está atendiendo**; hace falta porque, como viste en 10.2.3, tragarse una cancelación estropea el mecanismo. La segunda es `except*`, que merece su propia sección.

#### 10.3.2 `ExceptionGroup` y `except*`

Cuando varias tareas de un grupo fallan a la vez, Python no puede lanzar una sola excepción: serían varias al mismo tiempo. Por eso desde la 3.11 existe `ExceptionGroup` ([PEP 654](https://peps.python.org/pep-0654/)): una excepción que **contiene otras excepciones**, en su atributo `.exceptions`, que es una tupla (la colección que no cambia, de la Lección 4). Un `TaskGroup` que sufrió fallas las empaca en uno al salir del bloque, aunque haya fallado una sola.

Un `except` normal atrapa por la clase de la excepción que llega; como lo que llega es un `ExceptionGroup`, un `except ConnectionError` no la reconocería. Para eso se creó `except*` (con asterisco), que **abre el grupo**: `except* ConnectionError as grupo_de_errores` atrapa las excepciones del grupo que son `ConnectionError`, las junta en un grupo nuevo y lo deja en la variable. Por eso el `for error in grupo_de_errores.exceptions:` recorre esa tupla, y no un solo error. Si en el grupo había excepciones de otras clases que ningún `except*` atrapó, siguen su camino hacia arriba. Un mismo `try` puede tener varios `except*`, cada uno para su clase, y cada uno recibe lo suyo. Lo que **no** puedes hacer es mezclar `except` y `except*` en el mismo `try`. La [documentación del lenguaje](https://docs.python.org/3/reference/compound_stmts.html#except-star) tiene todas las reglas; para el `revisor` basta con lo que ves.

Fíjate en lo que ganó y perdió el programa. Ganó la limpieza: ninguna tarea quedó huérfana, el grupo esperó a que las canceladas terminaran de cancelarse, y el error llegó ordenado. Perdió el reporte: `inventario` estaba sana y su resultado se tiró. En un `revisor` eso es inaceptable, porque su razón de ser es decirte el estado de **todos**.

#### 10.3.3 Un fallo de red es un resultado, no una excepción

La solución del `revisor` ya la tienes escrita, y ahora puedes entender por qué está como está. `revisar` **atrapa** los errores de red dentro de la propia tarea y los convierte en un `Resultado` (`CAIDO`, con su detalle). Desde el punto de vista del `TaskGroup`, la tarea terminó bien: devolvió un valor. Nadie lanza nada hacia arriba, nadie cancela a nadie, y el reporte sale completo con la fila de `reportes` diciendo «sin conexión». Es el principio de la lección: **un fallo esperado es un dato, no un incidente**. Un servicio caído no es una sorpresa para un `revisor`; es parte de su trabajo.

¿Y todos los errores se convierten en datos? No, y la diferencia es lo más valioso de esta sección. `revisar` atrapa **clases concretas de `httpx`**: los errores que el mundo exterior puede causar. No atrapa un `ZeroDivisionError`, un `KeyError` o un `TypeError`: esos son errores **del programa**, y esconderlos como si fueran «un servicio caído» sería mentir. Si un servicio aparece como caído porque tu código tiene un error, pasarás una tarde buscando el problema en la red. Con el diseño de hoy, un error de programación hace lo que debe: detiene el reporte, ruidosamente, con un informe que apunta a la línea. Esa salida ruidosa es lo que ves en la sección «El error que vas a ver» de más abajo, y es una buena noticia, no una mala.

### 10.4 Pruebas sin red

#### 10.4.1 Por qué no se prueba contra la red

Para comprobar el párrafo anterior («un servicio caído no tumba el reporte») hacen falta servicios caídos, lentos, que devuelvan 503 y que se desconecten, y los cuatro cosas **a la vez**. Las pruebas contra la red real tienen tres problemas. Son **lentas**: una prueba de tiempo límite de 5 segundos hace esperar 5 segundos a quien corre la suite. Son **frágiles**: fallan porque se cayó el wifi, no porque tu código esté mal, y un rojo que no significa nada hace que la gente deje de mirar los rojos. Y son **imposibles de repetir**: no puedes pedirle a un servicio real que se caiga justo ahora. Por eso la regla es que **una prueba unitaria nunca sale a la red**. La red se sustituye por un doble: algo con la misma forma que lo real, pero que contesta lo que la prueba le diga.

La entrada del [blog de Hábil sobre pruebas que atrapan errores](https://www.habil.mx/es/blog/pruebas-que-atrapan-errores-cobertura-quality-gate/) cuenta por qué una prueba que se puede poner roja a voluntad vale más que diez que siempre están verdes; y la que trata de [estilos de integración en línea, cola y evento](https://www.habil.mx/es/blog/estilos-integracion-en-linea-cola-evento/) muestra el mismo problema desde el lado de la arquitectura: separar al que pregunta de al que contesta. Aquí lo separas con una pieza de `httpx`.

#### 10.4.2 `httpx.MockTransport`: un servidor de mentira

Un cliente HTTP tiene dos mitades: la que arma la petición y entiende la respuesta, y el **transporte**, que es la que realmente toca la red. `httpx` te deja cambiar el transporte, y trae uno hecho para pruebas, [`httpx.MockTransport`](https://www.python-httpx.org/advanced/transports/#mock-transports): recibe una función que, dada la petición, **devuelve la respuesta** que tú quieras. Nada sale de tu computadora.

```python
# fig10_07.py
import asyncio

import httpx


def atender(peticion: httpx.Request) -> httpx.Response:
    print(f"el servidor de mentira recibió: GET {peticion.url}")
    return httpx.Response(200, text="todo bien")


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        respuesta = await cliente.get("https://catalogo.example/estado")
        print(respuesta.status_code, respuesta.text)


asyncio.run(main())
```

```text
$ python fig10_07.py
el servidor de mentira recibió: GET https://catalogo.example/estado
200 todo bien
```

`atender` es la función de mentira: recibe un `httpx.Request` (la petición, con su dirección en `.url`), imprime qué le llegó y devuelve un `httpx.Response` con el código 200 y el texto «todo bien». `httpx.MockTransport(atender)` la envuelve como transporte, y `httpx.AsyncClient(transport=transporte)` arma un cliente que, en lugar de abrir una conexión, la llama. El cliente hace `get("https://catalogo.example/estado")`, una dirección que no existe (`.example` es un dominio reservado que nunca resuelve), y aun así responde, porque nunca fue a buscarla. Esto es lo que `revisar_todos` ofrece con su parámetro `transporte`: recibe el transporte y lo pasa a `httpx.AsyncClient(transport=transporte)`. Cuando vale `None` (lo normal), `httpx` usa el verdadero.

Un transporte de mentira puede hacer más que contestar 200: puede devolver un 503 (`httpx.Response(503)`), o **lanzar** una excepción de red como si el cable se hubiera cortado (`raise httpx.ConnectError(...)`), o incluso esperar, si la función es `async def`. Con esas cuatro cosas se simula todo lo que el `revisor` tiene que tolerar.

#### 10.4.3 Las seis pruebas de `revisar`

Un archivo nuevo, `tests/test_revision.py`. Antes del código, el plan: las pruebas hablan de un servidor de mentira que se comporta según el **nombre del anfitrión** (la parte de la dirección entre `https://` y la primera barra). `facturacion.example` contesta 503; `reportes.example` lanza `ConnectError`; `notificaciones.example` lanza `ReadTimeout` (la excepción de `httpx` para «se cumplió el tiempo de lectura»); cualquier otra contesta 200.

```python
# fig10_08/tests/test_revision.py
import asyncio

import httpx

from revisor.modelo import Estado, Resultado, Servicio
from revisor.revision import revisar, revisar_todos

CATALOGO = Servicio("catalogo", "https://catalogo.example")
PAGOS = Servicio("pagos", "https://pagos.example")
FACTURACION = Servicio("facturacion", "https://facturacion.example")
REPORTES = Servicio("reportes", "https://reportes.example")
NOTIFICACIONES = Servicio("notificaciones", "https://notificaciones.example", 1000)


def atender(peticion: httpx.Request) -> httpx.Response:
    """Un servidor de mentira: contesta según el nombre del anfitrión."""
    anfitrion = peticion.url.host
    if anfitrion == "facturacion.example":
        return httpx.Response(503)
    if anfitrion == "reportes.example":
        raise httpx.ConnectError("sin ruta", request=peticion)
    if anfitrion == "notificaciones.example":
        raise httpx.ReadTimeout("muy lento", request=peticion)
    return httpx.Response(200)


async def revisar_uno(servicio: Servicio) -> Resultado:
    async with httpx.AsyncClient(transport=httpx.MockTransport(atender)) as cliente:
        return await revisar(cliente, servicio)


def test_200_rapido_es_arriba() -> None:
    resultado = asyncio.run(revisar_uno(CATALOGO))
    assert resultado.estado is Estado.ARRIBA
    assert resultado.detalle == "200"


def test_503_es_caido_con_el_codigo() -> None:
    resultado = asyncio.run(revisar_uno(FACTURACION))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "503"


def test_sin_conexion_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(REPORTES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "sin conexión"


def test_tiempo_agotado_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(NOTIFICACIONES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "tiempo agotado"


def test_la_mezcla_sale_completa_y_en_orden() -> None:
    servicios = [CATALOGO, FACTURACION, REPORTES, NOTIFICACIONES]
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos(servicios, transporte=transporte))
    assert [r.servicio.nombre for r in resultados] == [
        "catalogo",
        "facturacion",
        "reportes",
        "notificaciones",
    ]
    assert [r.detalle for r in resultados] == [
        "200",
        "503",
        "sin conexión",
        "tiempo agotado",
    ]


def test_una_direccion_invalida_no_tumba_a_los_demas() -> None:
    mala = Servicio("mala", "http://999.1.1.1:8099/pagos")
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos([mala, CATALOGO], transporte=transporte))
    assert [r.detalle for r in resultados] == ["dirección inválida", "200"]
```

Cada prueba es una función normal (no `async`): arma lo que necesita y llama a `asyncio.run(...)`, igual que hace `main`. Así no hace falta ningún complemento de `pytest` para correr corrutinas, y el curso se queda con lo que ya conoces. `revisar_uno` es un auxiliar que abre un cliente con el transporte de mentira y revisa un solo servicio. Las cuatro primeras pruebas recorren los cuatro desenlaces de `revisar`: 200 rápido es `ARRIBA`; 503 es `CAIDO` y el detalle es el código, `"503"`; un `ConnectError` es `CAIDO` con «sin conexión»; un `ReadTimeout` es `CAIDO` con «tiempo agotado». La quinta, `test_la_mezcla_sale_completa_y_en_orden`, es la que demuestra la promesa de la lección: pasa a `revisar_todos` cuatro servicios, uno de cada tipo, y comprueba que **volvieron los cuatro, en el orden de la configuración, cada uno con su detalle**. Si un fallo tumbara el reporte, esta prueba se pondría roja. Y la sexta, `test_una_direccion_invalida_no_tumba_a_los_demas`, cuida el cuarto `except` de la Lección 9: junta un servicio con la dirección imposible `http://999.1.1.1:8099/pagos` y uno sano, y exige que el primero salga con «dirección inválida» y el segundo con su `200`. Sin ese `except`, la `httpx.InvalidURL` escaparía de su tarea, el `TaskGroup` cancelaría al resto y la prueba fallaría con un grupo de excepciones (10.3).

(Una cosa que `LENTO` no tiene aquí: no hay prueba de ese estado, porque simular que pasó más de un segundo con un transporte de mentira distrae. El umbral de lentitud ya está probado donde vive, en `clasificar`, con sus siete casos de la Lección 8.)

#### 10.4.4 Verla en rojo antes de creerle

Una prueba que nunca has visto fallar no demuestra nada: quizá pasaría igual con el código roto. Así que se comprueba. En una copia del proyecto, se borra la rama `except httpx.ConnectError` de `revisar`, de modo que un `ConnectError` caiga en la rama general y diga «error de red». Se corre:

```text
$ pytest -q --tb=short
.......................F.F.                                              [100%]
=================================== FAILURES ===================================
__________________________ test_sin_conexion_es_caido __________________________
tests/test_revision.py:48: in test_sin_conexion_es_caido
    assert resultado.detalle == "sin conexión"
E   AssertionError: assert 'error de red' == 'sin conexión'
E     
E     - sin conexión
E     + error de red
___________________ test_la_mezcla_sale_completa_y_en_orden ____________________
tests/test_revision.py:67: in test_la_mezcla_sale_completa_y_en_orden
    assert [r.detalle for r in resultados] == [
E   AssertionError: assert ['200', '503'...empo agotado'] == ['200', '503'...empo agotado']
E     
E     At index 2 diff: 'error de red' != 'sin conexión'
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_revision.py::test_sin_conexion_es_caido - AssertionError: a...
FAILED tests/test_revision.py::test_la_mezcla_sale_completa_y_en_orden - Asse...
2 failed, 25 passed in 0.04s
```

Se pusieron en rojo **exactamente dos** pruebas: la que habla de la conexión, y la de la mezcla (que incluye ese caso). La que dice `2 failed, 25 passed` te da el informe que importa: no es un verde de casualidad. Repara el código y vuelve a correr:

```text
$ pytest -q
...........................                                              [100%]
27 passed in 0.03s
```

`27 passed`: las 21 de la lección anterior más las seis de hoy. Ese número se lee del informe, no del código de salida, porque un código 0 no te dice cuántas pruebas corrieron: lo mismo sale con 27 que con 2 si por error filtraste el resto. (La Lección 11 vuelve a esto con un caso concreto.)

Hay un límite que conviene decir de frente. La prueba del tiempo agotado hace que el servidor de mentira **lance** un `ReadTimeout`, es decir, prueba la rama de `httpx.TimeoutException`. No prueba el **techo** de `asyncio.timeout`, que existe precisamente para el caso en que `httpx` no se entere de nada. Esa prueba hace falta, y es el Ejercicio 2: la escribes tú, y comprobarás que si se quita el `asyncio.timeout`, se pone roja.

#### 10.4.5 `monkeypatch` y la firma que no debes cambiar sin avisar

`test_cli.py` ya existía, con dos pruebas, y tenía un detalle que hoy salta a la vista. Esas pruebas llaman a `main`, y `main` llama a `revisar_todos`, que sale a la red. Para que no lo haga, el curso usó `monkeypatch` (Lección 8): cambia, durante una prueba, un nombre por otro, y al terminar la prueba lo restaura. Aquí cambia `revisor.cli.revisar_todos` por una función falsa que devuelve lo que la prueba necesita.

```python
# fig10_08/tests/test_cli.py
from pathlib import Path

import pytest

from revisor.cli import main
from revisor.modelo import Estado, Resultado, Servicio

CONFIGURACION = """\
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
"""


def test_con_servicios_caidos_sale_con_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_caidos(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Nota **dónde** se cambia el nombre: `"revisor.cli.revisar_todos"`, no `"revisor.revision.revisar_todos"`. `cli.py` hizo `from revisor.revision import revisar_todos`, así que `cli` tiene **su propia copia del nombre**; si cambiaras el original en `revision`, `cli` seguiría usando el suyo. La regla de `monkeypatch`: se cambia el nombre en el lugar donde **se usa**, no en el lugar donde se definió.

Y ahora lo importante de esta versión: las dos funciones falsas, `todos_caidos` y `todos_arriba` (cada una definida dentro de su prueba), **aceptan `limite`**. Hoy `main` llama a `revisar_todos(servicios, limite=argumentos.concurrencia)`, y un falso que no acepte ese argumento no es un doble de la función real: es otra función, y la prueba se rompe. Si en la Lección 9 tu falso era `async def todos_caidos(servicios)`, ahora tienes que agregarle el parámetro. Lo ves en «El error que vas a ver». Es una lección más general: **un doble debe tener la misma firma que lo que sustituye**, y cuando cambias la firma de la función real, las pruebas con dobles son lo primero que se rompe. Eso no es un fastidio; es la prueba haciendo su trabajo, avisándote que hay otros que dependían de esa firma.

#### 10.4.6 El proyecto completo

Los archivos que no cambiaron en esta lección están aquí para que la carpeta `fig10_08/` esté completa y puedas correrla. Son los mismos que traías de la Lección 9:

<details>
<summary>Los archivos que no cambian en esta lección</summary>


```toml fig10_08/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "inventario"
url = "http://127.0.0.1:8099/inventario"

[[servicios]]
nombre = "pagos"
url = "http://127.0.0.1:8099/pagos"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
```

```python
# fig10_08/laboratorio.py
"""Servidor de práctica del curso: contesta como si fuera cada servicio del revisor.

Se corre aparte (python laboratorio.py) y se deja abierto mientras practicas.
No necesitas entender cómo está escrito; lo que importa son sus rutas.
"""

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PUERTO = 8099

# ruta -> (código de la respuesta, milisegundos que tarda en contestar)
RUTAS: dict[str, tuple[int, int]] = {
    "/catalogo": (200, 142),
    "/inventario": (200, 2300),
    "/pagos": (200, 87),
    "/facturacion": (503, 95),
    "/notificaciones": (200, 10000),
}


class Laboratorio(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        codigo, espera_ms = self.buscar_ruta()
        time.sleep(espera_ms / 1000)
        cuerpo = b"ok" if codigo == 200 else b"error"
        try:
            self.send_response(codigo)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        except OSError:
            pass  # quien preguntó se cansó de esperar y colgó

    def buscar_ruta(self) -> tuple[int, int]:
        if self.path.startswith("/espera/"):
            texto = self.path.removeprefix("/espera/")
            if texto.isdigit():
                return 200, int(texto)
        return RUTAS.get(self.path, (404, 0))

    def log_message(self, format: str, *args: object) -> None:
        """No imprime una línea por cada petición."""


class Servidor(ThreadingHTTPServer):
    request_queue_size = 128  # conexiones que pueden esperar turno (de fábrica: 5)


def main() -> None:
    servidor = Servidor(("127.0.0.1", PUERTO), Laboratorio)
    print(f"laboratorio en http://127.0.0.1:{PUERTO} (Ctrl+C para detenerlo)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("laboratorio detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
```

```python
# fig10_08/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig10_08/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig10_08/src/revisor/modelo.py
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
# fig10_08/src/revisor/formato.py
import json

from revisor.modelo import Estado, Resultado


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


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": r.servicio.url,
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

```python
# fig10_08/src/revisor/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from revisor.modelo import Servicio, nombres_repetidos


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

```python
# fig10_08/tests/test_modelo.py
import pytest

from revisor.modelo import Estado, clasificar


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, Estado.ARRIBA),
        (200, 999, Estado.ARRIBA),
        (200, 1000, Estado.LENTO),
        (200, 2300, Estado.LENTO),
        (503, 95, Estado.CAIDO),
        (404, 50, Estado.CAIDO),
        (None, None, Estado.CAIDO),
    ],
)
def test_clasificar(
    codigo: int | None, tiempo_ms: int | None, esperado: Estado
) -> None:
    assert clasificar(codigo, tiempo_ms) is esperado
```

```python
# fig10_08/tests/test_formato.py
import pytest

from revisor.formato import formatear_tiempo


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [
        (None, "—"),
        (87, "87ms"),
        (999, "999ms"),
        (2300, "2.3s"),
    ],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado
```

```python
# fig10_08/tests/test_configuracion.py
from pathlib import Path

import pytest

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.modelo import Servicio


def test_lee_un_archivo_valido(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(
        '[[servicios]]\nnombre = "catalogo"\nurl = "https://catalogo.example"\n',
        encoding="utf-8",
    )
    assert leer_servicios(archivo) == [Servicio("catalogo", "https://catalogo.example")]


@pytest.mark.parametrize(
    ("contenido", "mensaje"),
    [
        (
            '[[servicios]]\nurl = "https://catalogo.example"\n',
            "servicio 1: falta 'nombre'",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "ftp://catalogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "http://[::1"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://cata\\nlogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://catálogo.example"\n',
            "servicio 1: 'url' debe ser una dirección http:// o https:// válida",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://catalogo.example"\n'
            "timeout_ms = 0\n",
            "servicio 1: 'timeout_ms' debe ser un entero mayor que 0",
        ),
        (
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://a.example"\n\n'
            '[[servicios]]\nnombre = "catalogo"\nurl = "https://b.example"\n',
            "nombres repetidos: catalogo",
        ),
    ],
    ids=[
        "sin nombre",
        "url ftp",
        "url mal formada",
        "url con salto",
        "url con acento",
        "timeout cero",
        "nombres repetidos",
    ],
)
def test_rechaza_configuraciones_invalidas(
    tmp_path: Path, contenido: str, mensaje: str
) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorDeConfiguracion) as informe:
        leer_servicios(archivo)
    assert str(informe.value) == mensaje
```

</details>

Con el laboratorio corriendo, la foto del proyecto produce el mismo reporte de siempre, pero esta vez los cuatro servicios se consultan a la vez, así que el total es el del más lento (`inventario`, 2.3 segundos) y no la suma:

```text
$ cd fig10_08
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
```

Los tiempos de la columna TIEMPO variarán un poco en tu máquina; el ESTADO y el DETALLE no, porque el laboratorio está hecho para que salgan siempre igual. Y el código de salida, como en la Lección 7, es 1: hay un `LENTO` y un `CAIDO`.

**Para comparar.** El mismo problema —lanzar, esperar a todas, limitar, no perder el reporte por un fallo— está resuelto en el [curso de Go](https://www.habil.mx/es/cursos/go/) con `sync.WaitGroup` y en el [curso de TypeScript](https://www.habil.mx/es/cursos/typescript/) con `Promise.all` y `Promise.allSettled`. La idea es la misma; lo que cambia es dónde vive la espera. En Go cada tarea es una *goroutine*, un hilo liviano que reparte el planificador del propio Go (no el sistema operativo) entre los hilos del procesador; en TypeScript y en Python es una tarea cooperativa en un solo hilo. Comparar las tres soluciones enseña más que leer una sola.

## El error que vas a ver

### `ExceptionGroup: unhandled errors in a TaskGroup`

Es el que te va a salir la primera vez que tengas un error de programación dentro de una tarea. La figura 9 lo provoca: una función que promedia una lista y se la pasan **vacía**, de modo que divide entre cero.

```python
# fig10_09.py
import asyncio


async def promedio(tiempos_ms: list[int]) -> float:
    return sum(tiempos_ms) / len(tiempos_ms)


async def main() -> None:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))


asyncio.run(main())
```

Dos tareas dentro del grupo: una promedia dos números, la otra una lista vacía. Esto es lo que Python dice (rutas acortadas a su nombre, como en todo el curso; en tu máquina vienen completas y los renglones de `asyncio/` pueden diferir según la versión de Python):

```text
$ python fig10_09.py
  + Exception Group Traceback (most recent call last):
  |   File "fig10_09.py", line 15, in <module>
  |     asyncio.run(main())
  |     ~~~~~~~~~~~^^^^^^^^
  |   File "asyncio/runners.py", line 205, in run
  |     return runner.run(main)
  |            ~~~~~~~~~~^^^^^^
  |   File "asyncio/runners.py", line 128, in run
  |     return self._loop.run_until_complete(task)
  |            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  |   File "asyncio/base_events.py", line 720, in run_until_complete
  |     return future.result()
  |            ~~~~~~~~~~~~~^^
  |   File "fig10_09.py", line 10, in main
  |     async with asyncio.TaskGroup() as grupo:
  |                ~~~~~~~~~~~~~~~~~^^
  |   File "asyncio/taskgroups.py", line 72, in __aexit__
  |     return await self._aexit(et, exc)
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "asyncio/taskgroups.py", line 174, in _aexit
  |     raise BaseExceptionGroup(
  |     ...<2 lines>...
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "fig10_09.py", line 6, in promedio
    |     return sum(tiempos_ms) / len(tiempos_ms)
    |            ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~
    | ZeroDivisionError: division by zero
    +------------------------------------
```

Lo primero: este *traceback* **no se lee como los de las lecciones anteriores**, de la última línea hacia arriba. La última línea de arriba, `+------------------------------------`, es decoración; la causa real está **dentro de la caja** marcada con `|`, al fondo. Léelo así:

1. La primera línea, `+ Exception Group Traceback`, te avisa: lo que sigue es un grupo.
2. Los renglones con `|` bajan por el camino que recorrió la ejecución: tu `asyncio.run(main())`, los pasos internos de `asyncio` y, importante, tu `main` en la línea 10, en el `async with asyncio.TaskGroup()`. Ahí es donde el grupo, al salir, empacó el error.
3. `ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` es el rótulo del grupo: «errores sin atender en un TaskGroup, una subexcepción». El número entre paréntesis te dice cuántas contiene.
4. Y **adentro de la caja** (`+-+---------------- 1 ----------------`) está la subexcepción número 1 con su propio *traceback*: `promedio`, línea 6, `ZeroDivisionError: division by zero`. **Esa es la causa**, y la que tienes que arreglar. La línea de tu archivo está en el renglón donde dice `fig10_09.py", line 6, in promedio`.

Nota también lo que pasó con la **otra** tarea (`promedio([142, 87])`): no hubo nada que cancelar. Como no tiene ningún `await`, corrió entera, sin ceder el turno, y terminó con su `114.5` antes de que la segunda empezara. Si hubiera estado esperando algo, como `inventario` en `fig10_06.py`, el `TaskGroup` la habría cancelado aunque estuviera sana: eso es el grupo haciendo su trabajo.

Qué hacer: arreglar la causa (comprobar que la lista no esté vacía), no esconder el error. Resiste la tentación de poner un `except*` ancho para callarlo: un error de programación debe verse.

### `TypeError: ... got an unexpected keyword argument 'limite'`

El segundo error de hoy es el de 10.4.5. Si tu falso de `test_cli.py` es de la Lección 9 y no acepta `limite`:

```text
$ pytest -q --tb=short -x tests/test_cli.py
F
=================================== FAILURES ===================================
_____________________ test_con_servicios_caidos_sale_con_1 _____________________
tests/test_cli.py:29: in test_con_servicios_caidos_sale_con_1
    assert main(["--config", str(archivo)]) == 1
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/revisor/cli.py:64: in main
    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: test_con_servicios_caidos_sale_con_1.<locals>.todos_caidos() got an unexpected keyword argument 'limite'
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_con_servicios_caidos_sale_con_1 - TypeError: t...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 0.03s
```

Léelo de abajo hacia arriba, como siempre: `TypeError`, «`todos_caidos()` recibió un argumento con nombre inesperado, `limite`». (El `test_con_servicios_caidos_sale_con_1.<locals>.` que antecede al nombre quiere decir que esa función está definida **dentro** de la prueba.) El renglón de arriba (`src/revisor/cli.py:64`) te dice quién lo mandó: `main`. Y el de más arriba, que la prueba llamó a `main`. La solución no está en `cli.py`: está en el falso, que debe aceptar lo mismo que la función real.

## Lo que se hace mal

**Esperar con `time.sleep` dentro de una corrutina.** Bloquea el hilo y deshace la concurrencia entera, sin dar error (10.1.4). Costo: un programa que parece concurrente y tarda lo mismo que en fila. Se detecta con el modo de depuración de `asyncio` y con `ruff`, siempre que agregues la colección `ASYNC` a tu `select` (la del `revisor` no la trae; 10.1.4).

**Crear tareas con `asyncio.create_task` y olvidar guardarlas.** Python solo guarda una referencia **débil** a las tareas sueltas, y una tarea que nadie referencia puede ser recogida por el recolector de basura a media ejecución. La [documentación](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) lo advierte. Con `TaskGroup` no pasa, porque el grupo las guarda. Costo: tareas que desaparecen sin error.

**No limitar la concurrencia.** `TaskGroup` sin semáforo con mil servicios abre mil conexiones a la vez. Costo: te topas con el límite del sistema operativo, o saturas al servicio que revisas, y el reporte falla por razones que no son las que mide.

**Atrapar `Exception` (o `BaseException`) dentro de la tarea para «que no falle nunca».** Se come los errores de programación y, con `BaseException`, hasta la cancelación. Costo: un reporte que miente («servicio caído») cuando el que falló es tu código.

**Tragarse `CancelledError`.** Un `except asyncio.CancelledError:` que no vuelve a lanzar la excepción deja al `TaskGroup` y a `asyncio.timeout` sin poder cancelar. Costo: programas que no terminan o que no respetan el tiempo límite. Si la atrapas para limpiar algo, haz `raise` al final.

**Probar contra la red real.** Lentas, frágiles, imposibles de repetir (10.4.1). Costo: rojos que nadie cree.

**Un falso con otra firma.** El doble que no acepta lo que la función real acepta es otra función. Costo: pruebas que se rompen cuando cambia la firma, o, peor, que siguen pasando sin probar nada porque nadie las llamó con los argumentos nuevos.

**Medir con una sola corrida.** Un solo número no dice nada: el arranque de Python, el calentamiento de las conexiones y lo que haga tu computadora en ese segundo se mezclan. Mide varias veces y compara la **proporción**.

## Ejercicios

### Ejercicio 1 — Mide un límite que no probaste

Con `servicios-20.toml` y el laboratorio corriendo, mide con `--concurrencia 5` y con `--concurrencia 4`. **Antes de correr**, predice los tiempos con el razonamiento de las tandas (cuántas tandas de medio segundo hacen falta con ese límite). Anota predicción y medición en tu bitácora y explica la diferencia, si la hay.

### Ejercicio 2 — La prueba del techo

Escribe una prueba para el techo de `asyncio.timeout`: un servicio con `timeout_ms = 100` cuyo servidor de mentira **espera diez segundos** antes de contestar. La prueba debe pasar en una fracción de segundo. Pista: la función que atiende puede ser `async def` y usar `await asyncio.sleep(10)`. Después, **verifícala en rojo**: quita el `asyncio.timeout` de `revisar` (déjalo con un `if True:` en su lugar), corre la prueba y anota cuánto tarda en fallar y por qué.

### Ejercicio 3 — Un tiempo límite más corto que la respuesta

Copia `servicios.toml` y agrega `timeout_ms = 1500` al servicio `inventario` (que en el laboratorio contesta tras 2.3 segundos). Predice la fila de `inventario`, el resumen y cuánto tardará la corrida, y compáralo con lo que sale. ¿Qué cambió en el `ESTADO` de `inventario`, y por qué?

### Ejercicio 4 — Provoca tres errores y léelos

Provoca, uno por uno: (a) en `fig10_09.py`, cambia la lista vacía por `[100]` y corre (¿qué desapareció?); luego vuelve a ponerla y pasa el `ZeroDivisionError` de la tarea por un `except*` que lo atrape e imprima un mensaje; (b) corre `python -m revisor --concurrencia 0` y anota el código con `echo $?`; (c) quítale `limite` a uno de los falsos de `test_cli.py` y corre `pytest`. Para cada uno, escribe en una frase qué significa el mensaje.

## Soluciones

### Solución 1

Con límite 5 y veinte servicios hacen falta cuatro tandas de medio segundo: 2.0 segundos más el arranque. Con límite 4 hacen falta cinco tandas: 2.5 más el arranque. Una corrida de referencia dio 2.15 y 2.67 segundos: el arranque (los 0.15 a 0.2 s que no son espera) explica la diferencia con 2.0 y 2.5. La regla general: el tiempo ≈ (número de servicios dividido entre el límite, redondeado hacia arriba) por la espera de cada uno, más el arranque.

### Solución 2

La prueba se agrega a `tests/test_revision.py` (o a un archivo propio):

```python
import asyncio

import httpx

from revisor.modelo import Estado, Servicio
from revisor.revision import revisar


async def colgado(peticion: httpx.Request) -> httpx.Response:
    await asyncio.sleep(10)
    return httpx.Response(200)


async def revisar_colgado() -> tuple[Estado, str]:
    servicio = Servicio("colgado", "https://colgado.example", 100)
    async with httpx.AsyncClient(transport=httpx.MockTransport(colgado)) as cliente:
        resultado = await revisar(cliente, servicio)
    return resultado.estado, resultado.detalle


def test_el_techo_corta_lo_que_httpx_no_ve() -> None:
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
```

El servidor de mentira es `async def` y espera diez segundos; el transporte de mentira no aplica ningún tiempo límite de `httpx` (no hay red), así que el único que puede cortar es el techo de `asyncio.timeout`. Con el código completo, la prueba pasa en una fracción de segundo:

```text
$ pytest -q tests/test_techo.py
.                                                                        [100%]
1 passed in 0.12s
```

Y con el `asyncio.timeout` quitado (el `if True:`), la prueba **falla**, y tarda diez segundos en fallar, porque nadie corta la espera; el informe muestra que `revisar` entregó `LENTO` con `'200'` después de esperar diez segundos:

```text
$ pytest -q --tb=short tests/test_techo.py
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_el_techo_corta_lo_que_httpx_no_ve ____________________
tests/test_techo.py:22: in test_el_techo_corta_lo_que_httpx_no_ve
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
E   AssertionError: assert (<Estado.LENT...ENTO'>, '200') == (<Estado.CAID...empo agotado')
E     
E     At index 0 diff: <Estado.LENTO: 'LENTO'> != <Estado.CAIDO: 'CAIDO'>
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_techo.py::test_el_techo_corta_lo_que_httpx_no_ve - Assertio...
1 failed in 10.04s
```

Eso demuestra que la prueba depende del arreglo que dice probar. Las seis pruebas de `test_revision.py` no habrían notado esa regresión.

### Solución 3

`inventario` pasa de `LENTO` a `CAIDO` con detalle «tiempo agotado»: su respuesta tardaba 2.3 segundos y el techo es 1.5, así que se corta antes. El resumen cuenta ahora `2 caídos`, y la corrida tarda unos 1.6 segundos (el techo de 1.5 más el arranque) en lugar de 2.4. Una corrida real:

```text
$ time python -m revisor --config servicios-corto.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  CAIDO          —  tiempo agotado
pagos       ARRIBA      95ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 0 lentos · 2 caídos · promedio 126ms

real	0m1.634s
user	0m0.110s
sys	0m0.019s
```

Dos observaciones. El promedio cambia (126 ms en esta corrida; varía un poco en cada una), porque `inventario` ya no aporta tiempo: un servicio que no respondió no entra en el promedio. Y la corrida es más corta porque el más lento ya no es `inventario` sino su techo.

### Solución 4

(a) Con `[100]` en lugar de `[]` ya no hay división entre cero, el programa termina sin salida y sin error: las dos tareas completaron. Con el `except*`:

```python
try:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))
except* ZeroDivisionError:
    print("una lista de tiempos venía vacía")
```

atrapa el error y el programa imprime el mensaje en vez del *traceback*. (b) Sale `revisor: error: argument --concurrencia: debe ser al menos 1` y el código es 2: es un error de uso, y lo detecta `argparse` antes de que corra nada. (c) `TypeError: ... todos_caidos() got an unexpected keyword argument 'limite'`: el falso no acepta lo que `main` le manda.

## Cómo sé que lo logré

- [ ] `fig10_02.py` imprime «a la vez: 0.5 s» y `fig10_01.py` imprime «en serie: 1.1 s», y puedes decir por qué el primero es el del más lento y el segundo la suma.
- [ ] `fig10_03.py` imprime las respuestas en el orden en que se crearon las tareas, no en el orden de rapidez, y sabes explicar qué hace `time.sleep` que `asyncio.sleep` no.
- [ ] `fig10_05.py` muestra las tandas de dos en dos y el total de 1.5 s.
- [ ] En la carpeta `fig10_08/`, `pytest -q` termina con `27 passed` y no con otro número, y lo hace con el laboratorio apagado (esa es la gracia de probar sin red).
- [ ] `ruff check`, `ruff format --check` y `mypy` no reportan nada en esa carpeta.
- [ ] Con `servicios-20.toml`, `--concurrencia 1` tarda cerca de 10 segundos, `--concurrencia 10` cerca de 1.1 y `--concurrencia 20` cerca de 0.6, y puedes explicar por qué 10 da el doble que 20.
- [ ] `python -m revisor --concurrencia 0` termina con código 2 y un mensaje de uso.
- [ ] Rompiste a propósito la rama `ConnectError` de `revisar` y viste ponerse en rojo exactamente dos pruebas; la arreglaste y volvieron las 27.
- [ ] Puedes explicar con tus palabras la diferencia entre el tiempo límite de `httpx` y `asyncio.timeout`, por qué `revisar` atrapa `httpx.HTTPError` y **no** `Exception`, y por qué el falso de `test_cli.py` tiene que aceptar `limite`.

## Resumen

Responde sin mirar la lección:

1. ¿Qué diferencia hay entre una corrutina y una tarea? ¿Qué hace `create_task` y qué hace la salida de un bloque `async with asyncio.TaskGroup()`?
2. ¿En qué momento exacto puede el bucle de eventos pasar de una tarea a otra? ¿Qué pasa con un `time.sleep` dentro de una corrutina?
3. Si cuatro servicios contestan en 0.3, 0.5, 0.1 y 0.2 segundos, ¿cuánto tarda la corrida en fila y cuánto con un `TaskGroup`? ¿Y con un `Semaphore(2)`?
4. ¿Qué mide `httpx.Timeout` y qué mide `asyncio.timeout()`? ¿Cuál de los dos corta a un servidor que manda un byte cada cuatro segundos?
5. ¿Por qué el semáforo se toma **fuera** de `revisar` y no dentro?
6. Cuando una tarea de un `TaskGroup` lanza una excepción, ¿qué le pasa a las demás? ¿Qué recibe el código que está fuera del bloque?
7. ¿Qué hace `except*` que no hace `except`? ¿Cuál es la diferencia entre `revisar` convirtiendo un `ConnectError` en un `Resultado` y atrapando un `ZeroDivisionError`?
8. ¿Dónde se cambia el nombre con `monkeypatch` si `cli.py` hizo `from revisor.revision import revisar_todos`? ¿Por qué el falso tiene que aceptar `limite`?

## Para leer más

- [Documentación de `asyncio`: corrutinas y tareas](https://docs.python.org/3/library/asyncio-task.html) — `TaskGroup`, `create_task`, `timeout()` y `sleep()` con todas sus reglas, incluida la cancelación. Es la fuente de esta lección. Consultado el 7 de octubre de 2026.
- [PEP 654, «Exception Groups and except\*»](https://peps.python.org/pep-0654/) — por qué existen los grupos de excepciones, con los casos que los motivaron. Más técnico, pero la sección de motivación se lee bien. Consultado el 7 de octubre de 2026.
- [Documentación de `httpx`: transportes (`MockTransport`)](https://www.python-httpx.org/advanced/transports/) y [tiempos límite](https://www.python-httpx.org/advanced/timeouts/) — las dos piezas de `httpx` que usaste hoy. Consultado el 7 de octubre de 2026.
- [Documentación de `pytest`: `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — todas las formas de cambiar un nombre durante una prueba y cuándo usar cada una. Consultado el 7 de octubre de 2026.
