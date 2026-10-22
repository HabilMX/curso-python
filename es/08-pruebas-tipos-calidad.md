# Lección 8 — Pruebas, tipos y calidad

**Tiempo:** 2 × 90 min (la primera sesión llega hasta el final de 8.3; la segunda empieza en 8.4)

**Qué construyes:** el `revisor` con 21 pruebas que se corren con un comando, con sus tipos revisados y su estilo vigilado

**Qué aprendes:** `pytest` (`assert`, la prueba vista en rojo antes que en verde, `parametrize`, `tmp_path` y `monkeypatch`), tipado gradual con `mypy`, `ruff` para revisar y formatear, y a leer el conteo del informe y no el código de salida

**De dónde vienes.** Traes el paquete de la [Lección 7](07-paquete-linea-de-comandos.md): el `revisor` vive en `~/curso-python/revisor/` con diseño `src/`, se instala con `pip install -e .` y se corre con `python -m revisor`. Con los cuatro servicios de práctica imprime la tabla del temario y sale con código 1, porque hay uno lento y uno caído. Funciona. Lo que no tienes es una forma de **saber que sigue funcionando** después de tocarlo: hasta hoy la única comprobación era correrlo y mirar la tabla, y los ojos se cansan y no ven lo que no esperan ver. Esta lección te da tres revisores que no se cansan: uno que ejecuta tu código con datos conocidos y compara la respuesta, otro que lee tu código sin ejecutarlo y comprueba que los datos encajan, y otro que vigila que esté escrito como se escribe en Python.

**Qué no hace esta lección.** No toca la red: el `revisor` sigue leyendo los datos simulados de `SIMULADO`, y consultar servicios de verdad es la [Lección 9](09-http-y-asyncio.md). Tampoco prueba código asíncrono ni simula la red, que es la [Lección 10](10-concurrencia-pruebas-sin-red.md), ni mide cuánto código toca cada prueba (la *cobertura*): es un número útil y fácil de falsear, y no sirve de nada hasta que sepas qué prueba cada prueba.

## Al terminar vas a poder

- Escribir una prueba con `pytest` (un archivo `test_*.py`, una función `test_*` y un `assert`), correrla y leer su informe de arriba hacia abajo.
- Ver una prueba **en rojo antes que en verde**, y explicar por qué una prueba que nunca has visto fallar no demuestra nada.
- Decir cuántas pruebas corrieron leyendo el **informe**, y explicar por qué el código de salida no alcanza: un `0` convive con una prueba que nunca se ejecutó.
- Convertir una tabla de casos en una sola prueba con `@pytest.mark.parametrize` y distinguir en el informe cuál fila falló.
- Probar código que lee archivos con `tmp_path` y código que depende de otra función con `monkeypatch`, sabiendo **dónde** hay que parchear.
- Revisar los tipos del paquete con `mypy` en modo estricto y leer su mensaje, y explicar qué quiere decir que el tipado de Python sea gradual.
- Revisar y formatear el código con `ruff check` y `ruff format`, con las tres herramientas configuradas en `pyproject.toml`.

## El porqué antes del cómo

Abre `src/revisor/modelo.py` y busca, dentro de `clasificar`, la línea que decide cuándo un servicio es lento: `if tiempo_ms is not None and tiempo_ms >= umbral_ms:`. Imagina que mañana, con prisa, alguien «arregla» ese `>=` y lo deja en `>`: un solo carácter. Corre el `revisor` con los cuatro servicios de práctica. **La tabla sale idéntica.** `catalogo` tarda 142 ms, `inventario` 2300, `pagos` 87 y `reportes` no responde; ninguno tarda exactamente 1000 ms, el único valor en el que `>=` y `>` se comportan distinto. El defecto existe, el programa corre sin un error y la tabla se ve perfecta. El día que un servicio real tarde justo 1000 ms (los tiempos de respuesta se amontonan en números redondos más de lo que parece) quedará «arriba» cuando la regla del curso dice que ya es «lento».

La comprobación que tenías, mirar la tabla, **no podía** encontrar ese defecto, porque no pregunta nada sobre los casos que importan. Lo que hace falta es escribir esas preguntas una vez («un servicio que responde 200 en 999 ms, ¿está arriba?, ¿y uno que responde 200 en 1000 ms, está lento?») y que una máquina las repita cada vez que toques el código, en menos de un segundo. Eso es una **prueba**: un programa pequeño que llama a tu código con una entrada conocida y comprueba que la respuesta es la que debe ser. Un conjunto de pruebas es una red de seguridad: te deja cambiar el código con calma, porque si rompes algo lo sabes en el acto y sabes dónde.

La lección trae tres herramientas, cada una con su pregunta:

| Herramienta | La pregunta que contesta | Cómo trabaja |
|---|---|---|
| `pytest` | ¿Hace el programa lo que dije, con estos datos? | **Ejecuta** tu código y compara |
| `mypy` | ¿Encajan los datos entre sí? ¿Pasé un texto donde iba un número, o me olvidé de que algo puede ser `None`? | **Lee** tu código sin ejecutarlo |
| `ruff` | ¿Está escrito como se escribe en Python, sin importaciones sobrantes ni trampas conocidas? | **Lee** tu código y lo reformatea |

Ninguna sustituye a las otras, y juntas son lo que en un equipo se llama una puerta de calidad: el cambio que no las pasa no entra. El blog de Hábil cuenta cómo se ve esa disciplina en un proyecto de equipo, en [pruebas que atrapan errores, cobertura y puertas de calidad](https://www.habil.mx/es/blog/pruebas-que-atrapan-errores-cobertura-quality-gate/). La primera sesión usa `pytest` hasta tener las 21 pruebas del `revisor`; la segunda revisa tipos y estilo y deja las tres herramientas puestas en el proyecto.

### Prepara las herramientas

Se instalan con `pip` (como en la Lección 1, con `python -m pip`, para que sea el `pip` del entorno) dentro del entorno virtual del curso, el mismo que activaste en la [Lección 1](01-instalacion.md) (el prompt muestra `(.venv)`):

```bash
python -m pip install pytest==9.1.1 ruff==0.16.10 mypy==2.4.0
```

Las versiones van fijas a propósito: los mensajes de `ruff` y de `mypy` cambian de redacción entre versiones, y con las mismas versiones lo que ves en tu pantalla es lo que ves aquí. Son las vigentes al 7 de octubre de 2026 en [PyPI](https://pypi.org/project/pytest/), y las mismas están en `herramientas/requisitos.txt` del repositorio del curso. Son herramientas de **desarrollo**: el `revisor` no las necesita para correr, así que no entran en la lista `dependencies` de `pyproject.toml`, que sigue vacía hasta la Lección 9. Comprueba con `pytest --version`, `ruff --version` y `mypy --version`; si alguna dice «command not found», el entorno virtual no está activo, el mismo tropiezo de la Lección 1.

## Los conceptos

### 8.1 `pytest`: ejecutar tu código con datos conocidos

#### 8.1.1 La primera prueba

[`pytest`](https://docs.pytest.org/en/stable/getting-started.html) es el programa que busca las pruebas, las ejecuta y te entrega un informe. No viene con Python: es una herramienta de terceros, la más usada del lenguaje. [Sus reglas para encontrar pruebas](https://docs.pytest.org/en/stable/explanation/goodpractices.html) son pocas: busca archivos llamados `test_*.py` o `*_test.py` y, dentro de ellos, ejecuta las funciones cuyo nombre empieza con `test`. Todo lo demás lo ignora. Guarda esa regla: más abajo, ignorar en silencio sale caro.

Una prueba prepara una entrada, llama al código que quieres comprobar y termina con un `assert`. Empieza por la más pequeña, sobre la función `formatear_tiempo` de la Lección 3. Para que el ejemplo corra solo, en un archivo, la función va copiada arriba de sus pruebas:

```python
# fig08_01.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def test_menos_de_un_segundo_va_en_milisegundos() -> None:
    assert formatear_tiempo(87) == "87ms"


def test_sin_tiempo_va_una_raya() -> None:
    assert formatear_tiempo(None) == "—"
```

Las dos funciones de abajo son las pruebas, y se reconocen por el nombre. Cada una contiene un `assert`, la palabra reservada que significa «afirmo que esto es verdad»: [`assert condición`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) no hace nada si la condición es verdadera y, si es falsa, detiene la función con un `AssertionError`. Llamar y afirmar: eso es todo lo que hace falta. Dos detalles de forma. Los nombres son frases que dicen **qué se espera**: `test_sin_tiempo_va_una_raya` te dice, el día que se ponga roja, qué se rompió sin que abras el archivo. Y el `-> None` dice que la función no devuelve nada, como toda prueba: o termina en silencio o se detiene con un error (en 8.4 verás que `mypy` en modo estricto lo exige).

Este archivo no se llama `test_*.py`, pero cuando le das a `pytest` el nombre de un archivo, lo corre aunque no cumpla el patrón. Con el entorno activo:

```text
$ pytest -q fig08_01.py
..                                                                       [100%]
2 passed in 0.00s
```

La opción `-q` (*quiet*, «callado») pide un informe corto. La primera línea tiene un punto por cada prueba que pasó y, a la derecha, el avance. La última es el resumen: `2 passed`, «dos pasaron». **Esa es la línea que vas a aprender a leer con desconfianza sana**: dice cuántas pruebas se ejecutaron y qué pasó con cada una.

#### 8.1.2 Verla en rojo antes que en verde

Una prueba que pasa no dice mucho: pasa si el código está bien, pero también si la prueba no comprueba nada. Solo hay una manera de saber si una prueba comprueba algo: **verla fallar**. Desde hoy, cada prueba la ves en rojo antes de aceptarla en verde. Aquí está el defecto del principio, escrito dentro de un archivo:

```python
# fig08_02.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms > UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"
```

`clasificar` decide el estado a partir del código y el tiempo; esta versión corta devuelve texto. Tiene el defecto: usa `>` donde la regla dice «mil milisegundos o más». Las dos pruebas son las preguntas de antes. Córrela y mira también el código de salida:

```text
$ pytest -q fig08_02.py
.F                                                                       [100%]
=================================== FAILURES ===================================
____________________________ test_1000_ms_es_lento _____________________________

    def test_1000_ms_es_lento() -> None:
>       assert clasificar(200, 1000) == "LENTO"
E       AssertionError: assert 'ARRIBA' == 'LENTO'
E         
E         - LENTO
E         + ARRIBA

fig08_02.py:18: AssertionError
=========================== short test summary info ============================
FAILED fig08_02.py::test_1000_ms_es_lento - AssertionError: assert 'ARRIBA' =...
1 failed, 1 passed in 0.01s
$ echo $?
1
```

Lee el informe de arriba hacia abajo. `.F`: la primera prueba pasó y la segunda falló. La sección `FAILURES` trae un bloque por cada falla, con el nombre de la prueba, su código y una flecha `>` en la línea que falló. Las líneas con `E` son el error: `assert 'ARRIBA' == 'LENTO'`. Esto es lo especial de `pytest`: reescribe tus `assert` para que, al fallar, muestren **los dos valores** comparados ([la documentación lo explica](https://docs.pytest.org/en/stable/how-to/assert.html)); con un `assert` pelado habrías visto solo `AssertionError`. Las líneas con `-` y `+` desglosan la comparación; en esta versión de `pytest`, la que lleva `-` es el valor de la derecha del `==` (`LENTO`, lo que la prueba esperaba) y la que lleva `+` el de la izquierda (`ARRIBA`, lo que el código devolvió). Después viene el archivo y la línea (`fig08_02.py:18`), un resumen de una línea por falla, cortado al ancho de la terminal (por eso termina en `=...`), y el conteo: `1 failed, 1 passed`.

El `echo $?` imprime el **código de salida** del comando anterior: el número que todo programa deja al terminar para decirle al sistema cómo le fue. Por convención, `0` es «bien» y cualquier otro es «algo falló». Lo usaste en la Lección 7 con el `revisor`. Aquí `pytest` salió con `1` porque hubo pruebas fallidas. Los guiones y las herramientas de integración continua leen ese número para decidir si siguen o se detienen.

El arreglo es cambiar `>` por `>=`:

```python
# fig08_03.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"
```

```text
$ pytest -q fig08_03.py
..                                                                       [100%]
2 passed in 0.00s
$ echo $?
0
```

Dos pasaron, código `0`. Fíjate en el orden: primero la pregunta (la prueba del 1000), luego el rojo contra el código con defecto, y solo entonces el arreglo. Ese orden es la garantía. Si la hubieras escrito **después** de arreglar, nunca sabrías si era capaz de detectar el defecto. Cuando agregues una prueba a código que ya funciona, el equivalente es romper el código a propósito un momento, ver el rojo y deshacer el cambio. El Ejercicio 1 lo hace con el `revisor` real.

#### 8.1.3 El conteo se lee del informe, no del código de salida

Aquí está la trampa que da nombre a una de las reglas del curso. [La documentación de `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) define sus códigos de salida: `0`, todas las pruebas **que se recolectaron** pasaron; `1`, algunas fallaron; `2`, el usuario interrumpió; `3`, error interno; `4`, error de uso; `5`, no se recolectó ninguna prueba; `6`, se superó el máximo de advertencias. Fíjate en la frase del `0`: «las que se recolectaron». Una prueba que `pytest` nunca recolectó no existe para él. Mira un archivo donde eso ocurre:

```python
# fig08_04.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"


def test_un_503_es_caido() -> None:
    assert clasificar(503, 95) == "CAIDO"


def prueba_sin_respuesta_es_caido() -> None:
    assert clasificar(None, None) == "ARRIBA"
```

Hay cuatro funciones de prueba y una trampa. La última se llama `prueba_sin_respuesta_es_caido`, no `test_...`, y `pytest` **no la ve**. Su `assert` es falso a propósito (afirma que la ausencia de respuesta es `"ARRIBA"`), así que si se ejecutara fallaría. Córrelo; después pídele a `pytest` que solo enumere lo que encontró (`--collect-only`) y que corra solo las pruebas cuyo nombre contenga un texto que no existe (`-k`):

```text
$ pytest -q fig08_04.py
...                                                                      [100%]
3 passed in 0.00s
$ echo $?
0
$ pytest -q --collect-only fig08_04.py
fig08_04.py::test_999_ms_es_arriba
fig08_04.py::test_1000_ms_es_lento
fig08_04.py::test_un_503_es_caido

3 tests collected in 0.00s
$ pytest -q -k nombre_que_no_existe fig08_04.py

3 deselected in 0.00s
$ echo $?
5
```

El primer informe dice `3 passed` y el código de salida es `0`: verde en toda la línea, con una prueba rota que nadie ejecutó. Un tablero que solo mirara el código de salida diría «todo bien». Quien lee el informe ve `3` y, si escribió cuatro, se pregunta dónde quedó la cuarta; `--collect-only` lo confirma, porque enumera tres. Pasa en cualquier proyecto: con una función mal nombrada, un archivo que no se llama `test_*.py` o un cambio de nombre que dejó una prueba fuera. El último comando muestra el otro extremo: `3 deselected` y código `5`, «no se recolectó ninguna». Ahí `pytest` sí avisó, pero el aviso se pierde si tu guion termina con `|| true` o si hay un filtro (`| tail`, `| grep`) en medio que se traga el código de salida. De ahí la regla:

> **El número de pruebas se lee del informe («N passed»). Un `0` no es evidencia de que corrió lo que creías. Compara siempre N con el N que esperas.**

El `revisor` termina esta lección con 21 pruebas, y ese número es el que comprobarás al final de cada sesión. La Lección 9 parte de él. Si un día el informe dice 20, no importa que esté en verde: algo desapareció. (Una prueba también puede marcarse como *saltada*, `skipped`, y entonces ni pasa ni falla: solo sale en el resumen. En este curso no se usa; si una prueba no sirve, se arregla o se borra.)

### 8.2 `parametrize`: una tabla de casos, una sola prueba

`clasificar` aplica cuatro reglas y tiene una frontera (1000 ms) donde se concentran los errores. Para probarla bien necesitas **siete casos**: dos rápidos (142 y 999 ms, el más lento que todavía está arriba), dos lentos (1000 ms, el primero que ya lo es, y 2300), dos caídos por código (503 y 404) y uno sin respuesta (`None`, `None`). Escritos como funciones separadas serían siete funciones idénticas salvo por dos números y un texto, con siete lugares que tocar el día que cambie la regla.

Lo que quieres es escribir la prueba una vez y los casos como una tabla. [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html) lo hace. La arroba es un **decorador**: una línea encima de una función que la modifica (ya viste `@dataclass(frozen=True)` en la Lección 5, sobre una clase). Aquí le dice a `pytest` que ejecute la función una vez por cada fila:

```python
# fig08_05.py
import pytest

UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, "ARRIBA"),
        (200, 999, "ARRIBA"),
        (200, 1000, "LENTO"),
        (200, 2300, "LENTO"),
        (503, 95, "CAIDO"),
        (404, 50, "CAIDO"),
        (None, None, "CAIDO"),
    ],
)
def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
    assert clasificar(codigo, tiempo_ms) == esperado
```

El primer argumento es la lista de **nombres de los parámetros**, que deben coincidir con los de la función de abajo. El segundo es la lista de **casos**: una tupla por caso, con un valor por cada nombre. El `esperado` va en la tabla y no calculado dentro de la función: si la prueba usara la misma fórmula del código que prueba, dos errores iguales se cancelarían y pasaría en verde sobre un defecto. Córrela y enumera lo que recolectó:

```text
$ pytest -q fig08_05.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q --collect-only fig08_05.py
fig08_05.py::test_clasificar[200-142-ARRIBA]
fig08_05.py::test_clasificar[200-999-ARRIBA]
fig08_05.py::test_clasificar[200-1000-LENTO]
fig08_05.py::test_clasificar[200-2300-LENTO]
fig08_05.py::test_clasificar[503-95-CAIDO]
fig08_05.py::test_clasificar[404-50-CAIDO]
fig08_05.py::test_clasificar[None-None-CAIDO]

7 tests collected in 0.00s
```

`7 passed`: `pytest` convirtió la función en **siete pruebas**, cada una con un nombre que lleva entre corchetes los valores del caso (`test_clasificar[200-1000-LENTO]`). Ese nombre importa cuando algo falla. Mira qué pasa si metes el defecto del `>` en esta tabla:

```python
# fig08_06.py
import pytest

UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms > UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


@pytest.mark.parametrize(
    ("codigo", "tiempo_ms", "esperado"),
    [
        (200, 142, "ARRIBA"),
        (200, 999, "ARRIBA"),
        (200, 1000, "LENTO"),
        (200, 2300, "LENTO"),
        (503, 95, "CAIDO"),
        (404, 50, "CAIDO"),
        (None, None, "CAIDO"),
    ],
)
def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
    assert clasificar(codigo, tiempo_ms) == esperado
```

```text
$ pytest -q fig08_06.py
..F....                                                                  [100%]
=================================== FAILURES ===================================
_______________________ test_clasificar[200-1000-LENTO] ________________________

codigo = 200, tiempo_ms = 1000, esperado = 'LENTO'

    @pytest.mark.parametrize(
        ("codigo", "tiempo_ms", "esperado"),
        [
            (200, 142, "ARRIBA"),
            (200, 999, "ARRIBA"),
            (200, 1000, "LENTO"),
            (200, 2300, "LENTO"),
            (503, 95, "CAIDO"),
            (404, 50, "CAIDO"),
            (None, None, "CAIDO"),
        ],
    )
    def test_clasificar(codigo: int | None, tiempo_ms: int | None, esperado: str) -> None:
>       assert clasificar(codigo, tiempo_ms) == esperado
E       AssertionError: assert 'ARRIBA' == 'LENTO'
E         
E         - LENTO
E         + ARRIBA

fig08_06.py:28: AssertionError
=========================== short test summary info ============================
FAILED fig08_06.py::test_clasificar[200-1000-LENTO] - AssertionError: assert ...
1 failed, 6 passed in 0.01s
```

`1 failed, 6 passed`, y la línea `..F....` dice que fue la tercera fila. El nombre, `test_clasificar[200-1000-LENTO]`, es el caso exacto; bajo él, `pytest` imprime los valores de los parámetros de **ese** caso, y las otras seis pasaron: una fila que falla no detiene a las demás. Agregar un caso es agregar una línea.

Ahora el proyecto. Las pruebas reales viven en una carpeta `tests/` junto a `src/`. La primera cubre `clasificar` con los siete casos, con el `Estado` verdadero:

```python
# fig08_15/tests/test_modelo.py
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

Compara con `is` y no con `==`: los miembros de un `Enum` son únicos y `is` pregunta por la identidad, como el `is None` de la Lección 2. Y los parámetros llevan **anotaciones de tipo**, como el código del paquete; en 8.4 verás por qué. La segunda cubre `formatear_tiempo` con cuatro casos: sin tiempo, uno en milisegundos, el último que todavía lo está (999) y uno en segundos:

```python
# fig08_15/tests/test_formato.py
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

Para que `pytest` sepa dónde buscar sin que se lo digas, el `pyproject.toml` gana una sección (el archivo completo está en 8.6):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` es la lista de carpetas donde busca cuando lo corres sin argumentos. En lo que sigue, la línea `cd fig08_15` representa «estar dentro del proyecto»; tú ya estás en `~/curso-python/revisor/`, así que no la escribas.

```text
$ cd fig08_15
$ pytest -q tests/test_modelo.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q tests/test_formato.py
....                                                                     [100%]
4 passed in 0.00s
```

Siete y cuatro: once hasta ahora. Cada informe cuenta lo que debe; si sumas mal, te lo dirá.

### 8.3 `tmp_path` y `monkeypatch`: pruebas que no ensucian ni dependen de nada

`clasificar` y `formatear_tiempo` son funciones puras: reciben valores, devuelven un valor y no tocan nada fuera de sí. Pero `leer_servicios` lee un archivo, y `main` lee argumentos, imprime y llama a la función que consulta los servicios. Probar eso plantea dos problemas, y `pytest` trae una herramienta para cada uno. Ambas son *fixtures*.

Una **fixture** es una función que `pytest` ejecuta por ti antes de una prueba para entregarle algo que necesita. La pides declarándola como **parámetro**: si tu prueba es `test_algo(tmp_path)`, `pytest` ve el nombre, busca una fixture que se llame así, la ejecuta y pasa el resultado como argumento. No la importas ni la llamas ([la documentación lo detalla](https://docs.pytest.org/en/stable/how-to/fixtures.html)).

#### 8.3.1 `tmp_path`: una carpeta nueva para cada prueba

Para probar que `leer_servicios` lee bien un archivo, necesitas un archivo. Si las pruebas usaran el `servicios.toml` de tu proyecto, cualquier cambio a ese archivo rompería pruebas que no tienen nada que ver, y una prueba que **escribe** ensuciaría tu carpeta. La fixture [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html) entrega un `Path` (el de `pathlib`, de la Lección 6) que apunta a una **carpeta temporal, nueva y vacía, única para esa prueba**:

```python
# fig08_07.py
import tomllib
from pathlib import Path


def contar_servicios(ruta: Path) -> int:
    datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    return len(datos["servicios"])


def test_cuenta_los_servicios_del_archivo(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(
        '[[servicios]]\nnombre = "catalogo"\n\n[[servicios]]\nnombre = "pagos"\n',
        encoding="utf-8",
    )
    assert contar_servicios(archivo) == 2


def test_cada_prueba_recibe_una_carpeta_vacia(tmp_path: Path) -> None:
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []
```

La primera prueba arma un `servicios.toml` pequeño y comprueba que se cuentan dos servicios. La segunda demuestra el aislamiento: recibe una carpeta **vacía**, aunque la anterior acabe de escribir un archivo en la suya. Para comprobarlo usa dos cosas de `pathlib`: `is_dir()` pregunta si la ruta es una carpeta que existe, e `iterdir()` recorre lo que hay dentro de ella, un elemento por cada archivo o subcarpeta. Como `iterdir()` entrega los elementos uno por uno y no una lista, `list(...)` los junta en una lista (como hiciste con `list(tiempos_ms)` en la Lección 4), y la lista de una carpeta vacía es `[]`.

```text
$ pytest -q fig08_07.py
..                                                                       [100%]
2 passed in 0.01s
```

Las carpetas viven en el directorio temporal del sistema, y `pytest` conserva las de las últimas tres corridas por si quieres inspeccionar lo que dejó una prueba fallida.

Con eso escribes las pruebas de `leer_servicios`: una que lee un archivo válido y siete que lo rechazan. Tres de las siete protegen lo que viste en 6.4.3: `url mal formada` (con `http://[::1`, `urlsplit` lanza `ValueError`, y la prueba exige que llegue como el mensaje de configuración y no como un *traceback*; si quitas el `try` de `es_url_http`, se pone roja), `url con salto` (un salto de línea dentro de la dirección; se pone roja si quitas `isprintable()`. En la tabla verás `\\n`, con la barra doble: dentro de una cadena de Python, `\\` escribe una barra invertida, así que el archivo TOML recibe `\n`, y TOML la convierte en el salto de línea de verdad) y `url con acento` (`https://catálogo.example`; se pone roja si quitas `isascii()`). Las siete comparten forma, así que van en una tabla, con `ids=` para que el informe use nombres legibles:

```python
# fig08_15/tests/test_configuracion.py
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

El archivo válido se compara con una lista que contiene un `Servicio`; funciona porque los `dataclass` comparan por contenido. Las de rechazo usan `with pytest.raises(ErrorDeConfiguracion) as informe:`, un `with` (el de la Lección 6) que afirma lo contrario de un `assert` normal: que el código de adentro **lanza** esa excepción. Si el bloque termina sin lanzar nada, `pytest` marca la prueba como fallida con `DID NOT RAISE`. El `as informe` guarda la excepción; `str(informe.value)` es el mensaje que escribiste en la Lección 6, y la prueba lo compara completo. Comprobar el mensaje y no solo el tipo distingue «falló por la razón correcta» de «falló por cualquier razón».

#### 8.3.2 `monkeypatch`: cambiar algo solo mientras dura la prueba

El `main` llama a `revisar_todos`, que hoy lee `SIMULADO` y desde la Lección 9 consultará la red. Para probar solo lo que `main` hace con los resultados (qué código de salida devuelve), conviene **sustituir** esa función por una falsa. La fixture [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) existe para eso: `monkeypatch.setattr(destino, valor)` reemplaza un atributo, y **al terminar la prueba lo deja como estaba**. Mira el mecanismo en un archivo pequeño:

```python
# fig08_08.py
import pytest

UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    return tiempo_ms >= UMBRAL_LENTO_MS


def test_con_el_umbral_normal() -> None:
    assert es_lento(1500)


def test_con_un_umbral_mas_alto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fig08_08.UMBRAL_LENTO_MS", 3000)
    assert not es_lento(1500)


def test_el_umbral_vuelve_a_su_valor() -> None:
    assert UMBRAL_LENTO_MS == 1000
```

Hay una variable de módulo, `UMBRAL_LENTO_MS`, y una función que la lee. La primera prueba usa el umbral de siempre. La segunda **lo cambia a 3000 durante esa prueba**: `"fig08_08.UMBRAL_LENTO_MS"` es la dirección del atributo, con la forma `módulo.nombre` (este módulo se llama como el archivo, sin el `.py`); dentro de esa prueba, 1500 ya no es lento. La tercera comprueba que después el umbral volvió a valer 1000.

```text
$ pytest -q fig08_08.py
...                                                                      [100%]
3 passed in 0.00s
```

Pasaron las tres, y la que importa es la tercera: el cambio **no se queda**. Asignar la variable a mano la dejaría cambiada para las pruebas siguientes y produciría fallos que dependen del orden, de los más difíciles de entender.

Ahora la prueba real. `main` devuelve `0` si todo está arriba y `1` si no. Para probar ambos casos sin depender de los datos simulados, sustituyes `revisar_todos` por una función falsa que devuelve lo que tú decidas:

```python
# fig08_15/tests/test_cli.py
from pathlib import Path

import pytest

from revisor.cli import main
from revisor.modelo import Estado, Resultado, Servicio

CONFIGURACION = """\
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "reportes"
url = "https://reportes.example"
"""


def test_con_un_servicio_caido_sale_con_1(tmp_path: Path) -> None:
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def todos_arriba(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Antes de las pruebas, la constante `CONFIGURACION` es el texto de un `servicios.toml` pequeño, entre triples comillas, como los textos de varias líneas de la Lección 6. La barra invertida justo después de las comillas que abren (`"""\`) evita que el texto empiece con un salto de línea: al final de una línea, dentro de un texto, `\` quiere decir «esta línea sigue en la siguiente», así que el primer renglón del texto es `[[servicios]]` y no uno vacío. Al TOML le daría igual, pero así lo que escribe la prueba es exactamente lo que ves.

La primera prueba usa los datos simulados reales con una configuración que incluye a `reportes`, que está caído. La segunda sustituye la función por `todos_arriba`, definida dentro de la prueba porque solo ella la usa, con la misma firma que la verdadera: cuando `main` la llame, no sabrá que es falsa.

Mira bien el destino: `"revisor.cli.revisar_todos"`, el nombre **dentro de `cli`**, y no el de `revision`, donde se define la función. [La documentación de `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) lo dice: hay que parchear la referencia que tu código usa. Una instrucción `from modulo import nombre` crea, dentro del módulo que importa, un nombre propio que apunta a la misma función: dos nombres para una cosa, y reemplazar uno no cambia el otro. `cli.py` empieza con `from revisor.revision import revisar_todos`, así que `main` busca `revisar_todos` entre los nombres de `cli`. Si parchearas el de `revision`, `cli` seguiría llamando a la verdadera. En «El error que vas a ver» lo rompes a propósito.

Con los cuatro archivos escritos corres **todo junto** por primera vez. Ya sabes lo que debe decir:

```text
$ cd fig08_15
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

Veintiún puntos y `21 passed`: 7 + 4 + 8 + 2. Ese número es el contrato con la Lección 9. **Aquí termina la primera sesión.** Cuando vuelvas, `pytest -q` es lo primero que corres, para saber que dejaste el proyecto como creías.

### 8.4 `mypy`: tipos que se revisan sin ejecutar nada

#### 8.4.1 Las anotaciones no se imponen al ejecutar

Desde la Lección 3 escribes anotaciones como `tiempo_ms: int | None`. La Lección 0 dijo que **Python no las usa al ejecutar**: son información para quien lee y para herramientas externas, no una orden. La [PEP 484](https://peps.python.org/pep-0484/), que las introdujo, lo dice sin rodeos: no se comprueban tipos en tiempo de ejecución. Se ve con cuatro líneas:

```python
# fig08_09.py
def doble(tiempo_ms: int) -> int:
    return tiempo_ms * 2


print(doble("142"))
```

La firma dice que `doble` recibe un entero, y la llamada le pasa el texto `"142"`. Córrelo y pídele a `mypy` que lo revise:

```text
$ python fig08_09.py
142142
$ mypy fig08_09.py
fig08_09.py:6: error: Argument 1 to "doble" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Python no se queja: `"142" * 2` es válido (repite el texto) y el programa imprime `142142`, un resultado absurdo para un tiempo en milisegundos que nadie avisó. [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) lee el archivo **sin ejecutarlo**, compara cada llamada con las anotaciones y se queja. Su mensaje tiene siempre la misma estructura: `archivo:línea: error: descripción  [código]`. Dice dónde (línea 6), qué (el argumento 1 de `doble` es `str` y se esperaba `int`) y, entre corchetes, el código del tipo de error (`arg-type`), útil para buscarlo. La última línea cuenta errores y archivos.

Eso es el *tipado gradual*: tú decides cuánto anotas, y `mypy` revisa lo que anotaste. Es la contraparte de lo que hace TypeScript en el [curso de esta casa](https://www.habil.mx/es/cursos/typescript/): los tipos se escriben y se comprueban antes de correr, pero no son un mecanismo del lenguaje en ejecución.

#### 8.4.2 Lo que `mypy` atrapa: el `None` que se te olvidó

El error más frecuente que `mypy` encuentra es olvidar que algo puede ser `None`. El servicio `reportes` no responde y su `tiempo_ms` es `None`: por eso el campo se anota `int | None`. Aquí una función que lo olvida (el programa atrapa el error solo para que veas el mensaje sin ruido):

```python
# fig08_10.py
def segundos(tiempo_ms: int | None) -> float:
    return tiempo_ms / 1000


print(segundos(87))
try:
    print(segundos(None))
except TypeError as error:
    print(f"se rompió: {error}")
```

```text
$ python fig08_10.py
0.087
se rompió: unsupported operand type(s) for /: 'NoneType' and 'int'
$ mypy fig08_10.py
fig08_10.py:3: error: Unsupported operand types for / ("None" and "int")  [operator]
fig08_10.py:3: note: Left operand is of type "int | None"
Found 1 error in 1 file (checked 1 source file)
```

Python se entera cuando llega a la segunda llamada: `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`. Si esa llamada estuviera en un camino que se recorre una vez al mes, el error habría llegado a producción. `mypy` lo encuentra **sin correr nada**, en la línea 3, y lo explica: `Unsupported operand types for / ("None" and "int")` y una nota, `Left operand is of type "int | None"`. La solución no es callar a `mypy` sino decidir qué debe pasar cuando no hay tiempo. Aquí, devolver `None` también, y decirlo en el tipo de retorno:

```python
# fig08_11.py
def segundos(tiempo_ms: int | None) -> float | None:
    if tiempo_ms is None:
        return None
    return tiempo_ms / 1000


print(segundos(87))
try:
    print(segundos(None))
except TypeError as error:
    print(f"se rompió: {error}")
```

```text
$ python fig08_11.py
0.087
None
$ mypy fig08_11.py
Success: no issues found in 1 source file
```

La función ahora dice la verdad en su firma, `float | None`, y esa verdad tiene una consecuencia: **todo el que use el resultado queda obligado a revisar si es `None`**, porque `mypy` se quejará si lo trata como número. En vez de un error escondido que aparece de madrugada, tienes una pregunta incómoda en tu editor, que es justo donde conviene tenerla.

#### 8.4.3 `match` y el caso que falta

En la Lección 5 viste que `match` junto a un `Enum` tiene una ventaja que `mypy` aprovecha aquí. Imagina que el `revisor` gana un cuarto estado, `DEGRADADO`, y una función que traduce estados a colores se queda sin su `case`:

```python
# fig08_12.py
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"
    DEGRADADO = "DEGRADADO"


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
$ python fig08_12.py
ARRIBA -> verde
LENTO -> amarillo
CAIDO -> rojo
DEGRADADO -> None
$ mypy fig08_12.py
fig08_12.py:12: error: Missing return statement  [return]
Found 1 error in 1 file (checked 1 source file)
```

Python **no avisa**: cuando ningún `case` coincide, el `match` termina sin hacer nada, la función llega a su final sin un `return` y devuelve `None`. La cuarta línea imprime `DEGRADADO -> None`, un color que no existe, y en un programa real ese `None` viajaría hasta quien lo use. `mypy` lo ve sin correr nada: la firma promete un `str`, pero hay un camino (el de `DEGRADADO`) que termina sin devolver nada, y por eso dice `Missing return statement`. El mensaje no menciona al miembro que falta, pero señala la función (`def semaforo`), y basta comparar sus `case` con los miembros del `Enum` para encontrarlo. Es la red de seguridad que prometía la Lección 5: agregas un miembro, y `mypy` te señala cada `match` que se quedó atrás.

#### 8.4.4 Gradual: lo que no anotas, `mypy` no lo revisa, salvo que se lo pidas

[La documentación de `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) lo establece: una función sin anotaciones se considera de tipado dinámico, y por omisión `mypy` **no revisa su cuerpo**. Es una decisión de diseño para poder agregar tipos poco a poco a código viejo. Míralo con una función sin una sola anotación:

```python
# fig08_13.py
def duplicar(x):
    return x * 2


print(duplicar("ms"))
```

```text
$ python fig08_13.py
msms
$ mypy fig08_13.py
Success: no issues found in 1 source file
$ mypy --strict fig08_13.py
fig08_13.py:2: error: Function is missing a type annotation  [no-untyped-def]
fig08_13.py:6: error: Call to untyped function "duplicar" in typed context  [no-untyped-call]
Found 2 errors in 1 file (checked 1 source file)
```

Sin opciones, `mypy` dice «Success»: `duplicar` no tiene anotaciones y no se revisa. Con `--strict`, el mismo archivo da dos errores: la función no tiene anotaciones (`no-untyped-def`) y la llamas desde código con tipos (`no-untyped-call`). El modo estricto es un atajo que enciende varias comprobaciones a la vez; [la documentación las lista](https://mypy.readthedocs.io/en/stable/command_line.html): entre ellas `--disallow-untyped-defs` (toda función lleva anotaciones), `--check-untyped-defs` (revisar también el cuerpo de las que no), `--warn-return-any` y `--warn-unused-ignores`. La lista exacta puede cambiar entre versiones, por eso la lección fija la de `mypy`.

La regla del curso: **el proyecto va en modo estricto desde el principio**; es mucho más barato mantener los tipos que agregarlos después. Se configura en `pyproject.toml`, [donde `mypy` lo lee](https://mypy.readthedocs.io/en/stable/config_file.html):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`python_version` es contra qué versión de Python comprobar (la del Mint del curso), `strict = true` enciende el modo estricto y `files` dice qué revisar cuando lo corres sin argumentos: el paquete y también las pruebas, porque una prueba mal tipada oculta errores igual que cualquier otro código.

#### 8.4.5 `mypy` en el `revisor`

Con la configuración puesta, el proyecto entero se revisa con un comando. Todo el código del paquete y de las pruebas lleva anotaciones (por eso las pruebas terminan en `-> None` y piden `tmp_path: Path`):

```text
$ cd fig08_15
$ mypy
Success: no issues found in 11 source files
```

`Success: no issues found in 11 source files`: siete archivos del paquete (`__init__`, `__main__`, `cli`, `configuracion`, `formato`, `modelo` y `revision`) y cuatro de pruebas. Lee el conteo como aprendiste con `pytest`: si un día dice `0 source files`, `mypy` no revisó nada y el verde no vale. Para verlo trabajar sobre el proyecto, haz el Ejercicio 3: cambia una anotación y mira cómo `mypy` te lleva hasta quienes la usan. Es su uso más valioso: cuando cambias la firma de una función, te dice todos los lugares que debes ajustar.

Una advertencia sobre las salidas de emergencia. `# type: ignore` le dice a `mypy` que no se queje de esa línea, y el tipo `Any` apaga las comprobaciones sobre un valor. Existen por razones legítimas (código de terceros sin tipos) y son la forma más rápida de volver inútil la herramienta. La regla: **la queja casi siempre tiene razón**; antes de callarla, entiende qué dice.

### 8.5 `ruff`: revisar y formatear

La última herramienta no sabe nada de tu problema ni de tus tipos: lee el código como texto y hace dos cosas distintas con dos comandos. [`ruff`](https://docs.astral.sh/ruff/) es un solo programa que cubre los dos papeles:

- **`ruff check`** es el *linter* (en español, «analizador estático»): busca errores y malas prácticas conocidas, como una importación que no se usa o un valor por omisión que se comparte entre llamadas. [Cada hallazgo tiene un código](https://docs.astral.sh/ruff/linter/) de una o dos letras y tres dígitos (`F401`, `E711`).
- **`ruff format`** es el *formateador*: reescribe el código con un formato único (espacios, saltos de línea, comillas, dónde se parte una línea larga). [Imita al de `Black`](https://docs.astral.sh/ruff/formatter/), el estándar de la comunidad, así que tu código se ve como el de cualquier otro proyecto. Lo mejor es lo que **te quita**: la discusión sobre estilo se decide una vez y la ejecuta la máquina.

Mira ambos sobre un archivo con defectos reales. Está desordenado a propósito: es lo único del curso que lo está.

```python
# fig08_14.py
import os, sys
from pathlib import Path

def agregar(servicio, lista=[]):
    lista.append(servicio)
    return lista

def es_nulo(valor):
    return valor == None

print(agregar("catalogo"))
print(agregar("pagos"))
```

El programa corre (imprime las dos listas), y tiene al menos cinco cosas mal. Como estás fuera del proyecto y no hay `pyproject.toml` que diga qué reglas aplicar, se las pasas con `--select`; `--output-format concise` pide una línea por hallazgo:

```text
$ python fig08_14.py
['catalogo']
['catalogo', 'pagos']
$ ruff check --select E,F,I,B,UP --output-format concise fig08_14.py
fig08_14.py:2:1: E401 [*] Multiple imports on one line
fig08_14.py:2:1: I001 [*] Import block is un-sorted or un-formatted
fig08_14.py:2:8: F401 [*] `os` imported but unused
fig08_14.py:2:12: F401 [*] `sys` imported but unused
fig08_14.py:3:21: F401 [*] `pathlib.Path` imported but unused
fig08_14.py:5:29: B006 Do not use mutable data structures for argument defaults
fig08_14.py:10:21: E711 Comparison to `None` should be `cond is None`
Found 7 errors.
[*] 5 fixable with the `--fix` option (2 hidden fixes can be enabled with the `--unsafe-fixes` option).
$ ruff format --check fig08_14.py
unformatted: File would be reformatted
  --> fig08_14.py:5:1
   |
4  |
5  +
6  | def agregar(servicio, lista=[]):
7  |     lista.append(servicio)
8  |     return lista
9  |
10 +
11 | def es_nulo(valor):
12 |     return valor == None
13 |
14 +
15 | print(agregar("catalogo"))
   |

1 file would be reformatted
```

La segunda llamada imprimió `['catalogo', 'pagos']`: el defecto de la Lección 3 en acción. El valor por omisión `lista=[]` se **comparte** entre llamadas, y `ruff` lo ve de antemano como `B006`. Son siete hallazgos, cada uno con `archivo:línea:columna: CÓDIGO descripción`. La letra del código es el nombre de la colección de reglas, que eliges con `select`:

| Letra | Qué vigila | Un ejemplo de arriba |
|---|---|---|
| `E` | Estilo ([pycodestyle](https://peps.python.org/pep-0008/), la guía oficial) | `E401` varias importaciones en una línea; `E711` comparar con `None` usando `==` |
| `F` | Errores lógicos sencillos ([Pyflakes](https://docs.astral.sh/ruff/rules/unused-import/)) | `F401` tres importaciones sin usar |
| `I` | El orden de las importaciones | `I001` bloque desordenado |
| `B` | Trampas conocidas ([bugbear](https://docs.astral.sh/ruff/rules/mutable-argument-default/)) | `B006` valor por omisión mutable |
| `UP` | Modernizar la sintaxis a tu versión de Python | (ninguno en este archivo) |

La documentación [recomienda empezar con pocas reglas](https://docs.astral.sh/ruff/linter/) (`E` y `F`), agregar grupos de uno en uno y elegir con `select` para que el conjunto sea explícito y no cambie solo al actualizar. Esas cinco son el conjunto del `revisor`.

La marca `[*]` dice que `ruff` sabe arreglar el hallazgo solo; el resumen cuenta cinco hallazgos con arreglo, y otros dos tienen arreglos *inseguros* que podrían cambiar lo que hace el programa (como el de `B006`). `ruff` solo aplica los seguros, salvo que se lo pidas. `ruff format --check` es la pregunta «¿está formateado?»: contestó que no, y muestra qué cambiaría. Para ver qué haría cada uno sin tocar el archivo existe `--diff`:

```text
$ ruff check --select E,F,I,B,UP --fix --diff fig08_14.py
--- fig08_14.py
+++ fig08_14.py
@@ -1,6 +1,4 @@
 # fig08_14.py
-import os, sys
-from pathlib import Path
 
 def agregar(servicio, lista=[]):
     lista.append(servicio)

Would fix 4 errors (2 additional fixes available with `--unsafe-fixes`).
$ ruff format --diff fig08_14.py
--- fig08_14.py
+++ fig08_14.py
@@ -2,12 +2,15 @@
 import os, sys
 from pathlib import Path
 
+
 def agregar(servicio, lista=[]):
     lista.append(servicio)
     return lista
 
+
 def es_nulo(valor):
     return valor == None
 
+
 print(agregar("catalogo"))
 print(agregar("pagos"))

1 file would be reformatted
```

El primero muestra el arreglo seguro: borrar las dos líneas de importaciones, que sobran enteras. Fíjate en que dice `Would fix 4 errors`, no cinco: los cinco hallazgos con `[*]` están en las mismas dos líneas, y sus arreglos se pisan. Al aplicar los de `F401`, que borran las importaciones sin usar, la línea desaparece y otro de los arreglos (separar `os` y `sys`, u ordenarlos) ya no tiene nada que hacer. Por eso conviene mirar el `--diff` y no solo contar marcas. El `== None` y el valor por omisión quedan, porque sus arreglos son inseguros: te toca decidir. El segundo muestra lo que haría el formateador: dos líneas en blanco entre funciones, la convención. Lo que hace `ruff format` es mecánico y no cambia lo que el programa hace.

#### 8.5.1 En el proyecto: la configuración

Las reglas se escriben una vez en `pyproject.toml`, como las de `pytest` y `mypy`, y entonces `ruff check` y `ruff format` no necesitan argumentos:

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`target-version` dice para qué versión de Python escribes: la 3.12 del Mint, la más vieja que el curso admite. Importa: `ruff` decide con ella qué es «biblioteca estándar» al ordenar importaciones (`tomllib` lo es desde la 3.11) y qué sintaxis moderna sugerir. En este proyecto, si no la escribieras, [`ruff` la tomaría](https://docs.astral.sh/ruff/settings/#target-version) de `requires-python = ">=3.12"`, en `[project]`, que dice lo mismo; se escribe para que quede a la vista junto a las reglas. Sin ninguna de las dos, `ruff` supone la 3.10, y con ella `tomllib` ya no sería biblioteca estándar y acabaría en el bloque de paquetes de terceros. `select` va en la subsección `[tool.ruff.lint]`, [como lo documenta `ruff`](https://docs.astral.sh/ruff/configuration/).

```text
$ cd fig08_15
$ ruff check
All checks passed!
$ ruff format --check
11 files already formatted
```

`All checks passed!` y todos los archivos ya formateados. Si corres `ruff check` sobre código que todavía no pasó por el formateador, es común que se queje de `E501` (línea de más de 88 caracteres), y que un `ruff format` las resuelva casi todas, porque reparte en varios renglones las llamadas y las listas largas. Por eso el orden es siempre el mismo: **primero `ruff format`, luego `ruff check`**. Y si una regla del linter te parece excesiva, la respuesta honesta es discutirla y quitarla del `select` con una razón, no esconderla con un comentario en cada línea.

### 8.6 El proyecto completo

La foto del proyecto al terminar la lección es el paquete de la Lección 7 con `version = "0.7.0"`, la carpeta `tests/` (cuatro archivos que ya viste) y tres secciones nuevas de configuración. El `pyproject.toml` completo:

```toml fig08_15/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.7.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = []

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

Lo nuevo respecto a la Lección 7 es la versión y las tres últimas secciones. Los demás archivos **no cambian**; se repiten aquí solo para que el proyecto esté completo y puedas comparar con los tuyos si algo no coincide:

```toml fig08_15/servicios.toml
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

```python
# fig08_15/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig08_15/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig08_15/src/revisor/modelo.py
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
# fig08_15/src/revisor/revision.py
from revisor.modelo import Resultado, Servicio, clasificar

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
# fig08_15/src/revisor/formato.py
import json
from urllib.parse import urlsplit, urlunsplit

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

```python
# fig08_15/src/revisor/configuracion.py
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

```python
# fig08_15/src/revisor/cli.py
import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import encabezado, linea, reporte_a_json, resumen
from revisor.modelo import Estado
from revisor.revision import revisar_todos


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

    resultados = revisar_todos(servicios)
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

Reinstálalo con `pip install -e .` para que el entorno vea la versión nueva. Desde hoy, cada vez que termines un cambio repites este ritual, en este orden:

```text
$ cd fig08_15
$ ruff format --check
11 files already formatted
$ ruff check
All checks passed!
$ mypy
Success: no issues found in 11 source files
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

## El error que vas a ver

### `ModuleNotFoundError: No module named 'revisor'`

Es el primero con que tropieza quien abre el proyecto en un entorno nuevo. Las pruebas importan el paquete (`from revisor.modelo import clasificar`) y el paquete **no está instalado** en el entorno que corre `pytest`. El informe no empieza con puntos sino con un bloque `ERRORS`: el error ocurrió al *recolectar* el archivo, antes de ejecutar nada. Versión recortada (las rutas largas de `importlib` van como `...`):

```text
==================================== ERRORS ====================================
______________________ ERROR collecting tests/test_cli.py ______________________
ImportError while importing test module '.../tests/test_cli.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
...
tests/test_cli.py:6: in <module>
    from revisor.cli import main
E   ModuleNotFoundError: No module named 'revisor'
=========================== short test summary info ============================
ERROR tests/test_cli.py
ERROR tests/test_configuracion.py
ERROR tests/test_formato.py
ERROR tests/test_modelo.py
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
4 errors in 0.05s
```

Se lee de abajo hacia arriba: la última línea `E` es la causa, la anterior dice qué línea la provocó (`from revisor.cli import main`, línea 6 de `test_cli.py`) y los pasos intermedios, de `importlib`, no te sirven. El resumen cuenta cuatro errores, uno por archivo, y no dice `0 passed`. La corrección es `pip install -e .` desde la carpeta que tiene el `pyproject.toml`: el proyecto está bien, falta instalarlo.

### `fixture 'tmp_pth' not found`

Es lo que ocurre si escribes mal el nombre de una fixture, `tmp_pth` en lugar de `tmp_path`. Como `pytest` la busca por el nombre del parámetro, un nombre que no existe es un error de `pytest` y no de Python:

```text
___________________________ ERROR at setup of test_x ___________________________
file tests/test_x.py, line 4
  def test_x(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: anyio_backend, anyio_backend_name, ... tmp_path, ...
>       use 'pytest --fixtures [testpath]' for help on them.
```

Mira el encabezado: `ERROR at setup`, no `FAILED`. La prueba ni llegó a ejecutarse; falló al *prepararse*. El mensaje te ofrece las fixtures disponibles (aquí recortadas), y ahí está `tmp_path`. (Las `anyio_*` salen porque `httpx`, que instalaste en la Lección 1, trae un complemento de `pytest`; no te afectan.)

### La prueba roja que parchea el lugar equivocado

El más educativo, porque no es de sintaxis sino de razonamiento. En `tests/test_cli.py`, cambia el destino del `monkeypatch` de `revisor.cli.revisar_todos` a `revisor.revision.revisar_todos`, donde se define la función, y corre las pruebas. Informe real, recortado:

```text
.F                                                                       [100%]
=================================== FAILURES ===================================
_______________________ test_con_todos_arriba_sale_con_0 _______________________
...
        monkeypatch.setattr("revisor.revision.revisar_todos", todos_arriba)
        archivo = tmp_path / "servicios.toml"
        archivo.write_text(CONFIGURACION, encoding="utf-8")
>       assert main(["--config", str(archivo)]) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = main(['--config', '/tmp/pytest-of-tu/pytest-0/test_con_todos_arriba_sale_con0/servicios.toml'])

tests/test_cli.py:35: AssertionError
----------------------------- Captured stdout call -----------------------------
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
reportes    CAIDO          —  sin conexión

2 servicios · 1 arriba · 0 lentos · 1 caído · promedio 142ms
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_con_todos_arriba_sale_con_0 - AssertionError: ...
1 failed, 1 passed in 0.02s
```

La línea `E` dice `assert 1 == 0` y, debajo, que `main` devolvió `1`. La sección `Captured stdout call` (lo que el código imprimió durante la prueba, que `pytest` guarda y muestra solo si falla) trae la pista decisiva: **`reportes` aparece caído, con los datos de siempre**. El parche no tuvo efecto, porque `cli` siguió usando su propia copia de `revisar_todos`. La moraleja es la de la documentación: parchea el nombre **donde se usa**. Deshaz el cambio antes de seguir.

## Lo que se hace mal

**Escribir una prueba que no puede fallar.** `assert clasificar(200, 142) is not None` pasa siempre, porque `clasificar` nunca devuelve `None`. Es la razón de la costumbre de 8.1.2. Costo: una red con un agujero del tamaño de la prueba y la tranquilidad falsa del verde.

**Dejar que la prueba calcule la respuesta con la fórmula del código.** `assert formatear_tiempo(2300) == f"{2300 / 1000:.1f}s"` repite la implementación: si la fórmula está mal, la prueba la copia. El esperado se escribe a mano, como dato: `"2.3s"`.

**Copiar la salida actual como valor esperado sin mirarla.** Corres el código, ves que devuelve `'ARRIBA'` y lo escribes en la prueba porque «eso es lo que sale». Si estaba mal, convertiste el defecto en la especificación, y la prueba lo defiende. El esperado sale de la regla, nunca de lo que el código hace hoy.

**Mirar solo el código de salida.** Es 8.1.3: un `0` no cuenta cuántas pruebas corrieron.

**Parchear donde se define la función y no donde se usa**, o parchear tanto que la prueba ya no ejercita código real. Si todo lo de adentro de `main` es falso, lo único que pruebas es el falso.

**Callar a `mypy` con `# type: ignore` o con `Any` para que «pase».** Dejas el defecto y quitas el aviso. Si hay una excepción real, lleva un comentario con el porqué.

**Anotar a medias.** Una función con anotaciones en dos parámetros y sin ellas en el tercero no queda fuera de la revisión: `mypy` sí revisa su cuerpo, pero el parámetro sin anotar vale `Any`, «cualquier cosa», y todo lo que hagas con él pasa sin preguntas. Con `strict = true`, además, `mypy` lo señala como `[no-untyped-def]`. O todo o nada; en este curso, todo.

**Pelear con el formateador.** Reformatear a mano lo que `ruff format` ya decidió, o desactivar una regla por pereza de entenderla.

**Pruebas que dependen del orden, del disco o de la red.** Una prueba que lee el `servicios.toml` real, o que solo pasa si otra corrió antes, falla en otra máquina sin explicación. Con `tmp_path` y `monkeypatch`, cada prueba se basta a sí misma.

## Ejercicios

### Ejercicio 1 — Rompe, mira el rojo, arregla

En `src/revisor/modelo.py`, cambia el `>=` de `if tiempo_ms is not None and tiempo_ms >= umbral_ms:` por `>`. Antes de correr, **predice**: ¿cuántas pruebas se pondrán rojas y cuál? Corre `pytest -q`. Después corre `python -m revisor` y compara la tabla con la de siempre. Deshaz el cambio y vuelve a correr. Anota en tu bitácora el número del informe antes y después, y qué te enseñó la tabla.

### Ejercicio 2 — Una prueba nueva para el código de salida 2

`main` devuelve `2` cuando el archivo de configuración no existe. Escribe en `tests/test_cli.py` una prueba que lo compruebe: llama a `main(["--config", ...])` con una ruta dentro de `tmp_path` a un archivo que no creaste, y afirma que el resultado es `2`. Antes de dejarla, **comprueba que puede fallar**: ¿cómo la pondrías en rojo a propósito? El informe debe decir `22 passed`. Bórrala al terminar (la Lección 9 parte de 21) y comprueba que vuelve a decir 21.

### Ejercicio 3 — Que `mypy` te lleve hasta quien llama

En `src/revisor/formato.py`, cambia `def formatear_tiempo(tiempo_ms: int | None) -> str:` por `def formatear_tiempo(tiempo_ms: int) -> str:`, sin tocar nada más. Corre `mypy`. ¿Cuántos errores salen y en qué archivos? ¿Por qué hay uno en `tests/test_formato.py`, que no tocaste? Deshaz el cambio.

### Ejercicio 4 — La prueba que falta

Hay un cambio de un solo carácter en `formatear_tiempo` que las 21 pruebas **no** detectan. La frontera de los mil milisegundos tiene su caso en `clasificar`, pero esta es la misma frontera. Cambia `if tiempo_ms < 1000:` por `if tiempo_ms <= 1000:` y corre `pytest -q`: ¿verde o rojo? Si es verde, escribe el caso que falta en la tabla de `tests/test_formato.py`, comprueba que ahora se pone rojo, deshaz el cambio al código y **borra** el caso nuevo para que el proyecto vuelva a 21, el número con el que arranca la Lección 9.

## Soluciones

### Solución 1

La predicción correcta es **una** prueba roja: `test_clasificar[200-1000-Estado.LENTO]`. Ninguna otra toca el 1000 exacto. Informe real, recortado:

```text
................F....                                                    [100%]
=================================== FAILURES ===================================
____________________ test_clasificar[200-1000-Estado.LENTO] ____________________

codigo = 200, tiempo_ms = 1000, esperado = <Estado.LENTO: 'LENTO'>
...
>       assert clasificar(codigo, tiempo_ms) is esperado
E       AssertionError: assert <Estado.ARRIBA: 'ARRIBA'> is <Estado.LENTO: 'LENTO'>
E        +  where <Estado.ARRIBA: 'ARRIBA'> = clasificar(200, 1000)

tests/test_modelo.py:22: AssertionError
=========================== short test summary info ============================
FAILED tests/test_modelo.py::test_clasificar[200-1000-Estado.LENTO] - Asserti...
1 failed, 20 passed in 0.02s
```

`1 failed, 20 passed` suma 21: el total sigue ahí. Y la tabla de `python -m revisor`, con el defecto puesto, **sale idéntica** a la de siempre: mirar la tabla no encuentra el defecto, la prueba sí. Al deshacer el cambio, el informe vuelve a `21 passed`.

### Solución 2

```python
def test_sin_archivo_de_configuracion_sale_con_2(tmp_path: Path) -> None:
    inexistente = tmp_path / "no-existe.toml"
    assert main(["--config", str(inexistente)]) == 2
```

Para verla en rojo, cambia el `2` por un `0` y corre: debe fallar con `assert 2 == 0`, lo que demuestra que mira el código de salida real. Con la versión buena, `22 passed`. Al borrarla debe volver `21 passed`; si no, algo quedó en el archivo.

### Solución 3

Salen **tres** errores, en dos archivos (`Found 3 errors in 2 files (checked 11 source files)`):

```text
src/revisor/formato.py:23: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
src/revisor/formato.py:47: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
tests/test_formato.py:17: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
```

El primero está en `linea`, que le pasa `resultado.tiempo_ms`, un `int | None`. El segundo está en `resumen`, que le pasa el promedio, que también puede ser `None` cuando ningún servicio respondió. El tercero es la prueba: su parámetro `tiempo_ms` es `int | None` (la tabla incluye el `None`) y llama a la función con él. Los tres son el mismo problema visto desde tres lugares, y el del promedio quizá ni lo recordabas: `mypy` te lo mostró sin que lo buscaras. Al deshacer el cambio vuelve `Success: no issues found in 11 source files`.

### Solución 4

El cambio **pasa en verde** (`21 passed`): ninguna de las cuatro filas usa 1000 (hay un `None`, un 87, un 999 y un 2300). Con `<=`, el 1000 saldría como `1000ms` en lugar de `1.0s` y nadie lo notaría. El caso que falta:

```python
        (1000, "1.0s"),
```

Con él, la mutación se pone roja (`test_formatear_tiempo[1000-1.0s]` te dice cuál). En un proyecto tuyo lo conservarías sin pensarlo; aquí lo borras solo por una razón de calendario: la Lección 9 compara su conteo con 21. Lo que esta solución quiere dejarte es la pregunta: **una suite verde no dice que el código está bien, dice que las preguntas que le hiciste tienen respuesta**. Revierte el arreglo y comprueba que se pone rojo: ese es el método.

## Cómo sé que lo logré

- [ ] `pytest -q`, desde la raíz del proyecto, termina con `21 passed` (el número, no solo el verde).
- [ ] `mypy` termina con `Success: no issues found in 11 source files`.
- [ ] `ruff check` dice `All checks passed!` y `ruff format --check` dice que los 11 archivos ya están formateados.
- [ ] Cambiaste `>=` por `>` en `clasificar`, `pytest -q` dijo `1 failed, 20 passed`, y al deshacerlo volvió a `21 passed`.
- [ ] Puedes explicar por qué un `echo $?` igual a `0` no te dice cuántas pruebas corrieron, y qué hace `--collect-only`.
- [ ] Puedes explicar por qué `monkeypatch.setattr` apunta a `revisor.cli.revisar_todos` y no a `revisor.revision.revisar_todos`.
- [ ] `pyproject.toml` tiene las tres secciones (`[tool.pytest.ini_options]`, `[tool.ruff]` con su `[tool.ruff.lint]` y `[tool.mypy]`) y `version = "0.7.0"`.

## Resumen

Responde sin mirar la lección:

1. ¿Cómo reconoce `pytest` qué es una prueba, y qué pasa con una función llamada `prueba_algo`?
2. ¿Por qué se ve una prueba en rojo antes de aceptarla en verde?
3. ¿Qué códigos de salida tiene `pytest` para «todo pasó», «alguna falló» y «no se recolectó ninguna»? ¿Por qué el conteo se lee del informe?
4. ¿Qué te ahorra `@pytest.mark.parametrize` y cómo sabes cuál fila falló?
5. ¿Qué es una fixture y qué entregan `tmp_path` y `monkeypatch`?
6. ¿Por qué `monkeypatch.setattr` apunta a `revisor.cli.revisar_todos`?
7. ¿Qué significa que el tipado de Python sea gradual y qué cambia con `strict = true`?
8. ¿Qué diferencia hay entre `ruff check` y `ruff format`, y por qué se corre primero el segundo?

## Para leer más

- [pytest, «Get Started»](https://docs.pytest.org/en/stable/getting-started.html) — la guía oficial, con las reglas de descubrimiento y la lectura del informe; en inglés, como casi toda la documentación del ecosistema. Consultado el 7 de octubre de 2026.
- [mypy, «Getting started»](https://mypy.readthedocs.io/en/stable/getting_started.html) — qué es el tipado dinámico y el estático, y cómo introducir tipos en código existente. Consultado el 7 de octubre de 2026.
- [Ruff, «The Ruff Linter»](https://docs.astral.sh/ruff/linter/) — cómo se eligen reglas, qué significan los códigos y qué es un arreglo seguro. Consultado el 7 de octubre de 2026.
- [PEP 484, «Type Hints»](https://peps.python.org/pep-0484/) — el documento que introdujo las anotaciones de tipo y aclara que no se comprueban al ejecutar. Consultado el 7 de octubre de 2026.
