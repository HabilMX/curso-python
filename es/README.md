# Curso de Python — de cero a un programa que revisa muchos servicios a la vez

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Para quién es:** quien nunca ha programado, o ha copiado scripts que funcionan sin saber por qué. No se supone nada: ni que tengas Python instalado, ni que sepas qué es un entorno virtual. Cada concepto se explica cuando aparece, y se explica por qué existe, no solo cómo se escribe.

**Qué vas a terminar sabiendo:** escribir un programa completo, con pruebas y varias tareas a la vez, entender lo que escribiste y poder explicárselo a alguien más. Y quedarte con el criterio para leer la documentación de Python por tu cuenta, que es la verdadera prueba.

**Dónde sigue:** el mismo problema, el `revisor`, está resuelto en los cursos de [Go](https://www.habil.mx/es/cursos/go/), [Rust](https://www.habil.mx/es/cursos/rust/) y [TypeScript](https://www.habil.mx/es/cursos/typescript/) de esta casa. Cuando termines éste, comparar tu solución con las suyas enseña más que empezar de cero.

**Lo que necesitas antes de empezar:** una computadora con Linux Mint y saber abrir una terminal. Nada más. La [Lección 1](01-instalacion.md) prepara todo desde cero.

## El proyecto que vas a construir

El **`revisor`**: un programa de línea de comandos que recibe una lista de servicios, los consulta **todos a la vez** y entrega un reporte en tabla o en JSON.

    $ revisor --config servicios.toml --formato tabla
    SERVICIO    ESTADO    TIEMPO  DETALLE
    catalogo    ARRIBA     160ms  200
    inventario  LENTO       2.3s  200
    pagos       ARRIBA      90ms  200
    reportes    CAIDO          —  sin conexión

    4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms

Empieza en la lección 2 con un encabezado y un solo servicio, y crece en cada lección hasta ser un paquete que se instala como cualquier comando. Parece pequeño y no lo es: para escribirlo bien necesitas funciones, colecciones, errores, archivos, pruebas, tipos, HTTP y tareas concurrentes.

## Las doce lecciones

| Lección | | Qué construyes | Qué aprendes |
|---|---|---|---|
| 0 | [Qué es Python y qué NO es](00-que-es-python.md) | nada todavía (lectura) | intérprete y *bytecode*; tipado dinámico pero fuerte; las anotaciones no se imponen; el GIL; entornos virtuales; versiones |
| 1 | [Instalar Python en tu Linux Mint](01-instalacion.md) | el entorno y tu primer script | `python3` del sistema; `externally-managed-environment`; `venv`; `pip`; el REPL; el primer *traceback* |
| 2 | [Valores, texto y decisiones](02-valores-texto-decisiones.md) | el encabezado del `revisor` y la clasificación de un servicio | tres conceptos: números, cadenas, booleanos y `None`; f-strings; `if`/`elif`/`else` y la indentación |
| 3 | [Bucles, funciones y módulos](03-bucles-funciones-modulos.md) | la función `revisar()` y el recorrido de la lista | `for`, `while`; `==` contra `is`; `def`; ámbito; el argumento mutable por defecto; `import`; `__main__` |
| 4 | [Colecciones](04-colecciones.md) | el `revisor` sin listas paralelas: los datos de cada servicio, juntos | `list`, `dict`, `tuple`, `set`; comprensiones; copia contra referencia; `KeyError` e `IndexError` |
| 5 | [El modelo de datos](05-modelo-de-datos.md) | el modelo `Servicio` / `Estado` y el reporte con su resumen | `dataclass`; `Enum`; `match` y `case` |
| 6 | [Errores, archivos y datos de fuera](06-errores-archivos-datos.md) | la lectura de la configuración | `try`/`except`; leer un *traceback*; `with`; `pathlib`; UTF-8; `json` y `tomllib`; validar; no `eval` ni `pickle` |
| 7 | [Un paquete con línea de comandos](07-paquete-linea-de-comandos.md) | el `revisor` como paquete | `pyproject.toml`; `python -m revisor`; `argparse`; códigos de salida; instalación editable con `pip`; `uv` como recuadro opcional |
| 8 | [Pruebas, tipos y calidad](08-pruebas-tipos-calidad.md) | el `revisor` con pruebas | `pytest` y tabla de casos; `tmp_path`; `monkeypatch`; tipado gradual con `mypy`; `ruff` |
| 9 | [HTTP y asyncio](09-http-y-asyncio.md) | el `revisor` que consulta de verdad | `urllib` y `httpx`; tiempos límite; `async` y `await`; `asyncio.run` |
| 10 | [Concurrencia con límites y pruebas sin red](10-concurrencia-pruebas-sin-red.md) | el `revisor` concurrente y probado | `TaskGroup`; `timeout`; `Semaphore`; grupos de excepciones; red simulada en las pruebas |
| 11 | [El programa terminado](11-el-programa-terminado.md) | el `revisor` completo, instalable | reporte en tabla y JSON; `logging`; seguridad; construir e instalar con `pipx` |

Al final de cada lección hay ejercicios con sus soluciones y una sección «Para leer más»; las fuentes de lo que se afirma van enlazadas en el texto, donde se usan. Y la [bitácora](https://github.com/HabilMX/curso-python/blob/main/es/bitacora.md) es tuya: anota ahí lo que te costó.

**Para seguir leyendo:** en el blog de Hábil, [pruebas que atrapan errores](https://www.habil.mx/es/blog/pruebas-que-atrapan-errores-cobertura-quality-gate/) y [seguridad de APIs](https://www.habil.mx/es/blog/seguridad-apis-cto-identidad-gateway-tokens/). Y en los cursos: si ya sabes programar y quieres Java moderno, el [curso de Java](https://github.com/HabilMX/curso-java).

## Tres criterios que atraviesan todo el curso

**El error es contenido, no un accidente.** Cada lección provoca a propósito el error que vas a ver, muestra el *traceback* real y enseña a leerlo, de la última línea hacia arriba. Saber leer un error es la mitad de saber programar.

**El entorno es real.** Se trabaja en Linux Mint con el Python que el sistema trae y sus reglas, no en un cuaderno en el navegador. Todo el código corre en Python 3.14 y también en 3.12, que es el de Mint.

**Las pruebas y la seguridad no son lecciones, son costumbres.** Los datos de fuera se validan en la 6, las pruebas llegan en la 8 y una prueba no cuenta hasta que la viste fallar, y la dirección que alguien escribe en un archivo se trata como lo que es en la 9 y la 11.

## Cómo sabes que terminaste

El curso no se acaba cuando leíste la lección 11, sino cuando tu `revisor` cumple estas siete cosas:

1. **`pytest` termina en verde y el informe dice cuántas pruebas corrieron.** Cuéntalas del informe, no del código de salida: un verde con cero pruebas se ve igual que un verde de verdad.
2. **`ruff check` y `ruff format --check` no reportan nada, y `mypy` tampoco.**
3. **Revisa 20 servicios a la vez en un tiempo cercano al del más lento**, no a la suma de todos. Lo mides tú, con el reloj, en serie y en paralelo.
4. **Un servicio caído, lento o que contesta basura no tumba el reporte:** aparece en su fila con su error, y el resto sale completo.
5. **Ninguna petición puede esperar para siempre:** todas tienen tiempo límite.
6. **Corre igual en Python 3.14 y en el 3.12 de tu Mint.**
7. **Se instala con `pipx install` y `revisor --help` funciona desde otra carpeta.** Sale con código 0 si todo está arriba y 1 si no.
