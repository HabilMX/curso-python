# Curso de Python — de cero a un programa que revisa muchos servicios a la vez

[![Verificar el curso](https://github.com/HabilMX/curso-python/actions/workflows/verificar.yml/badge.svg)](https://github.com/HabilMX/curso-python/actions/workflows/verificar.yml)


**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Cada lección de este curso se mide en cada cambio —su profundidad, que cumpla la plantilla, que las traducciones correspondan al español y que no se publique material interno—, y la comprobación se corre con un comando que cualquiera puede repetir.**
Haz clic en el sello para abrir la última corrida y ver, paso por paso, qué se ejecutó y qué salió. Los guiones que la hacen viven en [`herramientas/`](herramientas/) y se corren desde la raíz del repositorio.
🔴 **Lo que esa corrida NO hace es ejecutar los programas**: ningún guion los compila ni los corre todavía. Mientras no exista, que cada programa dé la salida que la lección documenta es responsabilidad de quien escribe la lección.

> El curso está en cinco idiomas: español (el original), inglés, francés, portugués de Brasil y búlgaro, cada uno en su carpeta.

## Dónde está el contenido

- **[Español — el curso completo](es/README.md)** ← empieza aquí
- **[English — the full course](en/README.md)**
- **[Français — le cours complet](fr/README.md)**
- **[Português (Brasil) — o curso completo](pt/README.md)**
- **[Български — пълният курс](bg/README.md)**
- **[`programas/`](programas/)** — todos los programas del curso, listos para ejecutar

## Para quién es

Quien **nunca ha programado**, o ha copiado scripts que funcionan sin saber por qué. **No damos por hecho nada**: ni que tengas Python instalado, ni que sepas qué es un entorno virtual, ni qué significa que Python sea «interpretado». Cada concepto se explica cuando aparece, y se explica por qué existe, no solo cómo se escribe.

## El proyecto que crece

El **`revisor`**, el mismo de los cursos de Go, Rust, TypeScript y Java, ahora en Python: un programa de línea de comandos que lee una lista de servicios, los **consulta todos a la vez**, mide cuánto tarda cada uno, aísla los fallos de cada servicio y entrega un reporte en tabla o en JSON. Al final se instala en tu computadora como un comando más.

Se repite el proyecto y no se inventa otro porque quien después lleve otro curso de esta casa ve el mismo problema resuelto en otro lenguaje, y de esa comparación se aprende más que de empezar de cero. **Lo que cambia es el lenguaje, no el problema.**

Y hay razones propias de Python. De los cursos y libros de Python que se revisaron para armar éste (una muestra, no un censo), los gratuitos enseñan temas sueltos o juegos y dejan para el final —o para nunca— las pruebas, la concurrencia y el empaquetado. Aquí el programa crece desde la primera lección y termina siendo algo que se instala y se usa.

## Las lecciones

Numeración única y continua: «Lección N», de la 0 a la 11 — **doce lecciones**.

| # | Lección | Qué construyes | Qué aprendes |
|---|---|---|---|
| 0 | Qué es Python y qué NO es | nada todavía (lectura) | intérprete y *bytecode*; tipado dinámico pero fuerte; las anotaciones no se imponen; el GIL; entornos virtuales; versiones |
| 1 | Instalar Python en tu Linux Mint | el entorno y tu primer script | `python3` del sistema; `externally-managed-environment`; `venv`; `pip`; el REPL; el primer *traceback* |
| 2 | Valores, texto y decisiones | el encabezado del `revisor` y la clasificación de un servicio | tres conceptos: números, cadenas, booleanos y `None`; f-strings; `if`/`elif`/`else` y la indentación |
| 3 | Bucles, funciones y módulos | la función `revisar()` y el recorrido de la lista | `for`, `while`; `==` contra `is`; `def`; ámbito; el argumento mutable por defecto; `import`; `__main__` |
| 4 | Colecciones | el `revisor` sin listas paralelas: los datos de cada servicio, juntos | `list`, `dict`, `tuple`, `set`; comprensiones; copia contra referencia; `KeyError` e `IndexError` |
| 5 | El modelo de datos | el modelo `Servicio` / `Estado` y el reporte con su resumen | `dataclass`; `Enum`; `match` y `case` |
| 6 | Errores, archivos y datos de fuera | la lectura de la configuración | `try`/`except`; leer un *traceback*; `with`; `pathlib`; UTF-8; `json` y `tomllib`; validar; no `eval` ni `pickle` |
| 7 | Un paquete con línea de comandos | el `revisor` como paquete | `pyproject.toml`; `python -m revisor`; `argparse`; códigos de salida; instalación editable con `pip`; `uv` como recuadro opcional |
| 8 | Pruebas, tipos y calidad | el `revisor` con pruebas | `pytest` y tabla de casos; `tmp_path`; `monkeypatch`; tipado gradual con `mypy`; `ruff` |
| 9 | HTTP y asyncio | el `revisor` que consulta de verdad | `urllib` y `httpx`; tiempos límite; `async` y `await`; `asyncio.run` |
| 10 | Concurrencia con límites y pruebas sin red | el `revisor` concurrente y probado | `TaskGroup`; `timeout`; `Semaphore`; grupos de excepciones; red simulada en las pruebas |
| 11 | El programa terminado | el `revisor` completo, instalable | reporte en tabla y JSON; `logging`; seguridad; construir e instalar con `pipx` |

Lo que la tabla promete por lección es lo que la lección trae.

**Tres criterios que no son lecciones, son costumbres de todas.**

- **El error es contenido planificado.** Cada lección provoca a propósito el error que verás —el *traceback* real, leído línea por línea— y explica qué dice, no solo cómo callarlo. La mayoría de los cursos gratuitos deja al principiante solo frente a la pantalla roja.
- **El entorno es real.** Se trabaja en Linux Mint, con el Python que el sistema trae y sus reglas (PEP 668), no en un cuaderno en el navegador. La fricción que vas a encontrar en un trabajo se enseña desde la lección 1.
- **Las pruebas y la seguridad aparecen donde aparece el riesgo**, no en un capítulo final: los datos de fuera se validan en la 6, las pruebas llegan en la 8 y se comprueban en rojo (una prueba que nunca se ha visto fallar no demuestra nada), y la dirección que alguien escribe en un archivo se trata como lo que es en la 9 y la 11.

**Solo se enseña lo que ya es definitivo.** Todo el código corre en Python 3.14 y también en 3.12, que es el que trae Linux Mint. Lo que es nuevo o experimental (el intérprete sin GIL, las *t-strings*) se menciona en un recuadro «lo que viene» y se dice que no se use en producción.

**Lo que este curso NO enseña, a propósito:** Django, Flask y FastAPI (son cursos aparte), cuadernos de Jupyter, `requests` (el curso usa `httpx`, que sirve igual en código síncrono y asíncrono), `setup.py`, el formato `%` y `.format()` (hay f-strings), herencia profunda y metaclases, los hilos a mano y los procesos. Quien termine estas once lecciones los aprende cuando los necesite.

**Para seguir leyendo en el blog de Hábil:** [pruebas que atrapan errores](https://www.habil.mx/es/blog/pruebas-que-atrapan-errores-cobertura-quality-gate/) y [seguridad de APIs](https://www.habil.mx/es/blog/seguridad-apis-cto-identidad-gateway-tokens/). **Y en los otros cursos:** el mismo `revisor` está en [Go](https://www.habil.mx/es/cursos/go/), [Rust](https://www.habil.mx/es/cursos/rust/) y [TypeScript](https://www.habil.mx/es/cursos/typescript/); si ya sabes programar y buscas Java moderno, ve directo al [curso de Java](https://github.com/HabilMX/curso-java).

## La plantilla de cada lección

Igual en todas:

1. **Encabezado:** «Lección N — título», tiempo (90 min o 2 × 45) y «Al terminar vas a poder…» (3 a 7 objetivos medibles).
2. **El porqué antes del cómo:** qué problema resuelve el concepto, con una situación concreta del `revisor`.
3. **Los conceptos**, uno por sección, **máximo cuatro nuevos por lección** (la lección 2, tres): explicación, ejemplo mínimo ejecutable y ejemplo en el `revisor`.
4. **El error que vas a ver:** el *traceback* real, reducido, y cómo leer su última línea. Se provoca a propósito.
5. **Lo que se hace mal** (antipatrones), con su costo.
6. **Ejercicios** (2 a 4), de menor a mayor, con sus **soluciones** aparte.
7. **Cómo sé que lo logré:** medible. Tal comando da tal salida; las pruebas pasan y el informe dice cuántas fueron.
8. **Para leer más:** 2 a 4 fuentes, documentación oficial primero. **No hay una sección «Fuentes» aparte**: lo que se afirma se cita en línea, donde se afirma, y aquí van las 2 a 4 lecturas para seguir.

## Cómo ver que los programas funcionan

Sin instalar nada: abre el sello de arriba. Cada corrida muestra los pasos que se ejecutaron y su resultado.

En tu computadora, con Python 3 instalado (la lección 1 lo comprueba y explica cómo preparar el entorno):

```bash
python3 --version
python3 -m venv .venv && source .venv/bin/activate
pip install -r herramientas/requisitos.txt
cd programas/04-colecciones
python fig04_01.py                  # compara lo que imprime con fig04_01.salida.txt
```

Cada programa es un archivo `figNN_NN.py` dentro de la carpeta de su lección, con su salida esperada al lado (`figNN_NN.salida.txt`). Los programas que a propósito fallan traen `figNN_NN.error-esperado.txt`, con el *traceback* que la lección enseña a leer. Los de varios archivos traen los demás en la carpeta `figNN_NN/`. Los proyectos completos (desde la lección 6) son carpetas con su propio `pyproject.toml`: entra en la carpeta, instala el proyecto en el entorno y corre `pytest`.

**Las lecciones son la fuente; `programas/` guarda los programas de cada una.** Hoy las dos se escriben a la par y **nada comprueba que coincidan**: no hay guion que extraiga los bloques de código de `es/*.md` y los compare contra los archivos. Mientras no exista, que lo que lees y lo que ejecutas sean lo mismo depende de quien edita.

## Qué hay en el repositorio

| | |
|---|---|
| `es/` | el curso en español, una lección por archivo |
| `en/`, `fr/`, `pt/`, `bg/` | las traducciones, una lección por archivo |
| `programas/` | los programas de las lecciones (uno por archivo, con su salida esperada) |
| `herramientas/` | los guiones que verifican el curso (ver abajo) y las versiones fijadas de las herramientas |
| `verificar-publicable.sh` | revisa que el material no contenga rutas internas ni claves antes de publicarlo. Se corre en el repositorio de trabajo: lee una lista de patrones que no se publica, porque enumerarlos en claro delataría justo lo que protegen |
| `LICENSE.md` | CC BY-SA 4.0 |

Dentro de `herramientas/`:

| | |
|---|---|
| `medir-profundidad.sh` | cuenta las palabras de explicación por lección y exige las dos varas |
| `verificar-plantilla.sh` | comprueba que cada lección cumpla la plantilla, **en cualquiera de los cinco idiomas** |
| `verificar-traducciones.sh` | dice qué traducciones están al día, cuáles vencieron y cuáles faltan |
| `registrar-traduccion.sh` | registra una traducción con la huella del español del que se tradujo |
| `registro-traducciones.tsv` | ese registro: un renglón por capítulo e idioma |
| `requisitos.txt` | las versiones exactas de `httpx`, `pytest`, `ruff` y `mypy` |

🔴 **Lo que sigue faltando, dicho con nombre: no hay guion que EJECUTE los programas ni que compruebe que `programas/` coincide con los bloques de código de las lecciones.** Se agregan aquí el día que existan y corran: un README que promete verificación que no ocurre es peor que uno que no promete nada, porque nadie vuelve a comprobarlo.

## La profundidad se mide

La vara que este curso comparte con los de Go, Rust y TypeScript son dos umbrales absolutos sobre las **palabras de explicación** (lo que está fuera de los bloques de código): **piso de 3,000 por lección y mediana de 4,000 para el curso**. `herramientas/medir-profundidad.sh` las cuenta y sale con código 1 si alguna lección no llega, así que el incumplimiento no pasa inadvertido.

Medido con él el **7-oct-2026 a las 21:15**: de **6,052 a 11,997 palabras, con mediana de 7,578** — muy por encima de las dos varas.

⚠️ **Esa cifra se mide, no se hereda.** La anterior que estuvo escrita aquí —mediana de 7,224— quedó vieja en **dos horas**, porque el curso siguió creciendo mientras se escribía el README. **Corre el guion antes de citar un número**, no copies el de arriba.

Se cuentan palabras y no líneas porque las líneas se inflan: una frase por línea suma muchas líneas sin explicar más. Y las varas son absolutas y no «la mitad de la mediana del curso» porque ese criterio se muerde la cola: unas lecciones flacas bajan la mediana y entonces pasan. Un criterio relativo garantiza uniformidad, no profundidad.

## Qué es un programa y qué es un fragmento

**No todo bloque de código de este curso es un programa completo.** Un **programa** corre solo, de principio a fin: su bloque empieza con un comentario `# figNN_NN.py` y trae, justo después, la corrida real (`$ python ...` y la salida). Cada uno se ejecuta en cada cambio, y su salida documentada se compara contra la real. Un **fragmento** es una ilustración que no pretende correr por sí sola, y por eso no se verifica; se reconoce porque su bloque no empieza con ese comentario.

## Reglas del repositorio

- **Licencia CC BY-SA 4.0** (ver `LICENSE.md`): el material es público y se puede reusar citando la fuente.
- **Multiidioma:** `es/` es el original; las traducciones se agregan después y un guion avisa cuando alguna quedó vieja respecto al español.
- **El código no se traduce.** Los nombres de archivo, funciones y datos quedan como están; se traducen las explicaciones, los ejercicios, los errores y el glosario.
- `./verificar-publicable.sh` antes de publicar, desde el repositorio de trabajo, que es donde vive su lista de patrones internos. Falla cerrado: si no pudo buscar, o si no llegó a revisar ni un patrón, sale en error y no en verde. Y trae autoprueba: siembra un patrón y exige detectarlo.
- Sin emojis en los títulos de las lecciones.
