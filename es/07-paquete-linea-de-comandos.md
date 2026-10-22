# Lección 7 — Un paquete con línea de comandos

**Tiempo:** 90 min

**Qué construyes:** el `revisor` como un paquete de verdad: una carpeta con estructura, un archivo `pyproject.toml` que lo describe, un comando con opciones (`--config`, `--formato`, `--version`) y un código de salida que otros programas pueden leer

**Qué aprendes:** la estructura de un paquete con diseño `src/` (`__init__.py`, `__main__.py`, importaciones absolutas); `python -m revisor`; `pyproject.toml` (`[build-system]`, `[project]`, `[project.scripts]`); `argparse`; los códigos de salida; la salida estándar contra la salida de error; y la instalación editable con `pip install -e .`

**De dónde vienes.** Traes el proyecto de la [Lección 6](06-errores-archivos-datos.md): un `revisor` que ya no lleva los servicios escritos en el código sino que los lee de `servicios.toml`, los valida, y se queja en español cuando el archivo no sirve. Son seis archivos en una sola carpeta (`revisor.py`, `modelo.py`, `revision.py`, `formato.py`, `configuracion.py` y el guion de apoyo `ver_json.py`) más el `servicios.toml`. Funciona, con tres limitaciones que hoy se notan. Primera: **solo anda si estás parado en esa carpeta** y escribes `python revisor.py`; los módulos se encuentran unos a otros porque están pegados, y el nombre del archivo de configuración está escrito en una constante del programa. Segunda: **para ver el reporte en JSON hay que ejecutar otro guion**, porque el programa no tiene forma de que le digas qué quieres. Tercera: **el programa no le avisa a nadie si encontró problemas**: termina igual de bien cuando todo está arriba que cuando la mitad está caída, y un guion, un programador de tareas o un sistema de integración continua no pueden saber la diferencia. Trabajas en tu carpeta `~/curso-python/revisor/`, con el entorno virtual de la [Lección 1](01-instalacion.md) activado.

**Qué no hace esta lección.** No consulta ninguna red (los datos siguen siendo los simulados de la lección 5; la red llega en la [Lección 9](09-http-y-asyncio.md)) y no escribe pruebas (eso es la [Lección 8](08-pruebas-tipos-calidad.md)). Lo que se resuelve hoy es **cómo se convierte un conjunto de archivos en un programa que se instala, se ejecuta con un comando y se comunica con el resto del sistema**.

**Sobre las corridas.** Todas las salidas se obtuvieron con Python 3.14.8 y se repitieron con Python 3.12.12, de la misma línea 3.12 que trae Linux Mint 22. (El de Mint 22 es el 3.12.3, que es el que publica Ubuntu 24.04, su base: lo muestra la [página del paquete `python3.12` para Ubuntu 24.04 en Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12).) Son idénticas con una sola excepción, que se señala donde ocurre: el texto de un error de `argparse`. Las rutas que verás en los mensajes empiezan en `/home/tu_usuario/curso-python/`; la tuya empezará con tu propia carpeta. El proyecto completo está en [`programas/07-paquete-linea-de-comandos/fig07_01/`](https://github.com/HabilMX/curso-python/tree/main/programas/07-paquete-linea-de-comandos/fig07_01), en el repositorio del curso; las dos figuras sueltas (`fig07_02.py` y `fig07_03.py`) se ejecutan desde la carpeta de la lección.

## Al terminar vas a poder

- Explicar la diferencia entre un módulo y un paquete, y por qué el código vive en `src/revisor/` y no al lado del `pyproject.toml`.
- Ejecutar un paquete con `python -m revisor` y explicar qué hace `__main__.py`.
- Leer y escribir un `pyproject.toml` con sus tres tablas: `[build-system]`, `[project]` y `[project.scripts]`.
- Definir opciones de línea de comandos con `argparse`: una con valor por omisión, una con opciones cerradas y una `--version`.
- Hacer que un programa termine con un código de salida que diga qué ocurrió (0, 1 o 2), y leerlo en la terminal con `echo $?`.
- Mandar los mensajes de error a la salida de error y el reporte a la salida estándar, y comprobar la diferencia redirigiendo una de las dos.
- Instalar el paquete en modo editable con `pip install -e .` y explicar por qué un cambio en el código se nota sin reinstalar, pero un cambio en `pyproject.toml` no.

## El porqué antes del cómo

Piensa en cómo usarías el `revisor` en la vida real. Alguien de operación lo ejecuta cada mañana desde un programador de tareas, para saber si algún servicio amaneció caído. Ese programador de tareas no mira la tabla que se imprime: es un programa, y no sabe leer una tabla. Lo único que puede preguntarle a otro programa al terminar es una cosa: **«¿saliste bien o mal?»**. En Linux, esa respuesta es un número, el *código de salida*, y la convención es que 0 significa «todo bien» y cualquier otro número significa «algo pasó». Si el `revisor` no sabe contestar esa pregunta, la automatización es ciega. Y si además la persona quiere el reporte en JSON para pasárselo a otro sistema, necesita poder pedirlo con una opción, no editando un archivo.

Un programa que se ejecuta así, con opciones, con un código de salida y desde cualquier carpeta, es un **programa de línea de comandos**. Para serlo, hace falta estructura: no puedes hacerlo con seis archivos sueltos. Python tiene una forma estándar de armarlo, que consiste en tres piezas: un **paquete** (una carpeta que Python reconoce como una unidad importable), un archivo **`pyproject.toml`** que describe el proyecto para las herramientas, y un **comando de instalación** que deja todo disponible en tu entorno. Esas son las tres secciones de la lección, más la que cierra: cómo se comunica un programa con quien lo llamó, con códigos de salida y con dos canales de texto distintos.

La lección es mecánica, y eso es una advertencia justa: hay muchos nombres de archivo y muchas reglas que se aprenden haciéndolas, no leyéndolas. El mejor modo de seguirla es tener la terminal abierta en `~/curso-python/revisor/` e ir ejecutando cada paso. Al final, al ejecutar `python -m revisor --formato json` verás en pantalla el reporte en JSON, y al preguntar a la terminal cómo salió el programa con `echo $?`, verás un `1`, porque entre los servicios hay uno lento y uno caído. Hay muchas cosas escondidas en esa frase (una opción, un formato, un número que sale al final), y la lección las desenreda una por una.

## Los conceptos

### 7.1 Un paquete con diseño `src/`

#### 7.1.1 Módulo, paquete y cómo se encuentran

Ya sabes qué es un **módulo**: un archivo `.py` cuyo contenido otro archivo puede importar (lección 3). Hasta ahora tu `revisor` tiene cinco, y se importan con instrucciones como `from modelo import Servicio`. Eso funciona por una razón muy concreta que nunca se había nombrado: cuando ejecutas `python revisor.py`, Python busca los módulos que importes **en la carpeta donde está ese archivo**, y también en las carpetas de la biblioteca estándar y en las del entorno virtual donde `pip` instala cosas (una carpeta llamada `site-packages`). Esa lista de lugares se consulta en orden, y es lo que decide si un `import` encuentra lo que busca o falla con `ModuleNotFoundError`. Mientras todos tus archivos estén juntos, todo se encuentra. En cuanto algo se mueve o se ejecuta desde otro sitio, empieza a fallar.

Un **paquete** es una carpeta de módulos que Python trata como una unidad con nombre. Si hay una carpeta `revisor/` con un archivo `__init__.py` adentro y otros módulos, desde cualquier parte se puede escribir `from revisor.modelo import Servicio`, que se lee «del paquete `revisor`, el módulo `modelo`, importa `Servicio`». El punto separa los niveles. Este tipo de importación, que arranca siempre por el nombre del paquete, se llama **importación absoluta**, y es la única que usa este curso: es la más clara de leer, porque cualquiera que vea la línea sabe de dónde viene el nombre sin tener que adivinar en qué carpeta está el archivo. La [sección del tutorial sobre paquetes](https://docs.python.org/3/tutorial/modules.html#packages) explica el mecanismo con más detalle.

#### 7.1.2 Por qué `src/`

Lo que queda por decidir es **dónde** se pone la carpeta del paquete. La forma más obvia es al lado del `pyproject.toml`, en la raíz del proyecto. Pero hay una forma mejor, que es la que usa la guía oficial de empaquetado de Python: meterla en una subcarpeta llamada `src/`. Este es el diseño que vas a tener al terminar la lección:

```text
revisor/                      ← la carpeta del proyecto (~/curso-python/revisor/)
  pyproject.toml              ← describe el proyecto
  servicios.toml              ← los datos, como en la lección 5
  src/
    revisor/                  ← el paquete
      __init__.py
      __main__.py
      cli.py
      modelo.py
      revision.py
      formato.py
      configuracion.py
```

El nombre `revisor` aparece dos veces, y no es descuido: la de afuera es la carpeta del **proyecto** (lo que descargas, lo que contiene los archivos de configuración, las pruebas que vendrán en la lección 8), y la de adentro es el **paquete** (lo que Python importa). La ventaja de `src/` es que **te obliga a instalar el paquete antes de usarlo**. Si el paquete estuviera en la raíz, `python -m revisor` desde esa carpeta lo encontraría sin instalarlo, porque la carpeta actual siempre está en la lista de lugares donde Python busca. Y eso esconde errores: podrías tener un paquete que funciona en tu carpeta pero que, instalado, le faltan archivos, y no te enterarías hasta que lo usara otra persona. Con `src/`, la carpeta del paquete no está donde Python busca por omisión, así que ninguna copia se cuela por estar en la carpeta donde trabajas: para importar el paquete, antes hay que instalarlo.

Lo que `src/` no garantiza es que lo que ejecutas sea el paquete tal como se instalaría en otra computadora: eso depende de **cómo** lo instales. La instalación que usarás para desarrollar, la **editable** de 7.4.3, no copia el paquete a ningún lado: agrega la carpeta `src/` **entera** a la lista de lugares donde Python busca. Lo que se ejecuta entonces es tu carpeta, y cualquier archivo que esté en `src/` se puede importar, aunque no forme parte del paquete. Se midió con este mismo proyecto, con Python 3.14.8 y 3.12.12 y `hatchling` 1.32.4, agregando un archivo `src/suelto.py`, fuera de `src/revisor/`. Con la instalación editable, `import suelto` funciona desde cualquier carpeta; con la instalación normal (`pip install .`, sin `-e`), la misma línea termina en `ModuleNotFoundError: No module named 'suelto'`, porque el paquete construido solo lleva lo que está en `src/revisor/`. La [documentación de `pip`](https://pip.pypa.io/en/stable/topics/local-project-installs/) lo dice con todas sus letras: la instalación editable no copia ningún archivo, sino que «los archivos de la carpeta de desarrollo se agregan a la ruta de importación de Python»; y advierte que puede comportarse distinto de la normal, que es la que verá quien reciba tu programa. La de [`hatchling`](https://hatch.pypa.io/latest/config/build/#dev-mode) explica que, en una instalación editable, decide qué carpetas **completas** agrega a la ruta de búsqueda. Por eso la [guía de empaquetado](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) reparte los papeles así: la instalación editable se usa para desarrollar, y la normal, para probar. Este curso desarrolla con la editable, porque es la cómoda; la normal llega en la lección 11, cuando el `revisor` se empaqueta en un archivo y se instala con `pipx`. Y las pruebas de la lección 8 no cambian esta cuenta: corren contra lo que esté instalado, y con la instalación editable eso es tu carpeta `src/`, sea cual sea el modo en que `pytest` importe los archivos de prueba. También se midió: con la instalación editable, una prueba que importa `suelto` pasa con el modo por omisión de `pytest` y con el modo `importlib`, el que su [guía de buenas prácticas](https://docs.pytest.org/en/stable/explanation/goodpractices.html#which-import-mode) recomienda para proyectos nuevos; con la instalación normal, falla en los dos.

Esa misma guía de empaquetado discute las dos formas y sus compromisos; este curso adopta la de `src/` sin reservas.

#### 7.1.3 `__init__.py`, `__main__.py` y `python -m`

El paquete lleva dos archivos que no son parte de tu programa sino parte del mecanismo. El primero es `__init__.py`. Su sola presencia le dice a Python «esta carpeta es un paquete». Puede estar vacío; aquí lleva una frase entre comillas triples que describe el paquete, lo que se llama una cadena de documentación:

```python
# fig07_01/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

El segundo es `__main__.py`, que es lo que se ejecuta cuando alguien escribe `python -m revisor`. La opción `-m` (de *módulo*) le dice a Python «no ejecutes un archivo; ejecuta este paquete como un programa». Para un paquete, eso significa ejecutar su `__main__.py`. Todo el archivo es esto:

```python
# fig07_01/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

La primera línea importa la función `main` del módulo `cli` (que verás en 7.3). La segunda hace algo que parece un trámite pero es el centro de la lección: `raise SystemExit(main())`. Ya sabes qué es `raise` (lección 6): lanza una excepción. `SystemExit` es una excepción especial que Python ya trae, y que **nadie atrapa a propósito**: cuando sube hasta arriba, en lugar de imprimir un informe de error, Python termina el programa, y el valor con que la construyes se vuelve el **código de salida**. Entonces `main()` se ejecuta, **devuelve un número**, y ese número se vuelve el código con que el programa termina. Lo veremos con detalle en 7.4; por ahora basta saber que el `-m` busca esta pieza. La [documentación de `__main__`](https://docs.python.org/3/library/__main__.html#main-py-in-python-packages) y la de la [opción `-m`](https://docs.python.org/3/using/cmdline.html#cmdoption-m) lo cuentan en detalle.

#### 7.1.4 Mover los archivos

Los cuatro módulos que ya tenías (`modelo.py`, `revision.py`, `formato.py`, `configuracion.py`) pasan al paquete **sin cambiar una sola función**: las firmas son las mismas de la lección 6. Lo único que cambia son sus importaciones, que dejan de ser `from modelo import ...` para volverse `from revisor.modelo import ...`. El `revisor.py` plano se vuelve `cli.py` y se reescribe en 7.3. Y el guion `ver_json.py` desaparece, porque `--formato json` lo sustituye. Desde la carpeta del proyecto, con el entorno activado, estos son los pasos. Usan tres órdenes de la terminal que no habías visto, y conviene saber qué hace cada una antes de escribirla:

- **`mkdir -p src/revisor`** crea la carpeta `src` y, dentro, `revisor`, de una vez. Sin `-p`, `mkdir` se negaría a crear `revisor` porque `src` todavía no existe; con `-p` (*parents*, «los padres») crea también las carpetas intermedias que falten, y no se queja si ya existían.
- **`mv origen destino`** (*move*) **mueve** archivos, o les cambia el nombre. `mv modelo.py revision.py formato.py configuracion.py src/revisor/` mueve los cuatro archivos a esa carpeta (la barra final dice que el destino es una carpeta). `mv revisor.py src/revisor/cli.py` mueve y renombra a la vez. Si en el destino ya hay un archivo con ese nombre, `mv` lo reemplaza sin preguntar.
- **`rm archivo`** (*remove*) **borra** un archivo, y no lo manda a la papelera: no se recupera. Aquí borra `ver_json.py`, que ya no hace falta, y al final las copias `.bak` que deja `sed`. El `*` de `src/revisor/*.bak` quiere decir «todos los archivos de esa carpeta que terminan en `.bak`»; antes de un `rm` con `*`, un `ls` con el mismo patrón te muestra exactamente qué se va a borrar.

Estos son los pasos:

```bash
mkdir -p src/revisor
mv modelo.py revision.py formato.py configuracion.py src/revisor/
mv revisor.py src/revisor/cli.py
rm ver_json.py
sed -i.bak -E 's/^from (modelo|formato|configuracion|revision) import/from revisor.\1 import/' src/revisor/*.py
rm src/revisor/*.bak
```

El comando `sed` es un editor de texto sin ventana: busca en cada archivo las líneas que empiezan con `from modelo import` (o `formato`, `configuracion`, `revision`) y les antepone `revisor.`. Los parámetros `-i.bak` le piden que guarde una copia de seguridad de cada archivo con la terminación `.bak`, que se borra enseguida. Si prefieres no usarlo, editas a mano las líneas que dicen `from modelo import`, y verifica con esto lo que debe quedar en cada archivo:

| Archivo | Importaciones al terminar |
|---|---|
| `revision.py` | `from revisor.modelo import Resultado, Servicio, clasificar` |
| `formato.py` | `import json` y `from revisor.modelo import Estado, Resultado` |
| `configuracion.py` | `from revisor.modelo import Servicio, nombres_repetidos` (más las de la biblioteca estándar, sin cambio) |
| `modelo.py` | no importa nada de tu proyecto |

El `cli.py` se reescribe por completo en 7.3. Aún no puedes ejecutar nada: falta crear los tres archivos nuevos (`__init__.py`, `__main__.py` y `pyproject.toml`) y escribir `cli.py`. Sigue leyendo.

### 7.2 `pyproject.toml`: el proyecto descrito para las herramientas

Un paquete, por sí mismo, es solo una carpeta. Para que `pip` sepa instalarlo hace falta describirlo: cómo se llama, qué versión es, qué versión de Python necesita, qué comando crea. Eso se escribe en un archivo llamado `pyproject.toml` en la raíz del proyecto. Es un archivo TOML, el formato que aprendiste a leer en la lección 6, y es el mecanismo oficial: la [guía de empaquetado](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) lo describe como el lugar donde van los metadatos de un proyecto de Python. Este es el del `revisor`:

```toml fig07_01/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.6.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
revisor = "revisor.cli:main"
```

Tiene tres tablas, y cada una responde una pregunta distinta.

**`[build-system]`: ¿con qué se construye?** Instalar un paquete, aunque sea tuyo y local, implica un paso de construcción: leer el `pyproject.toml`, reunir los archivos, producir algo instalable. Ese trabajo lo hace una herramienta que se llama *backend de construcción*, y el proyecto debe decir cuál quiere. `requires` lista lo que hace falta descargar para construir, y `build-backend` nombra al backend. Aquí se usa `hatchling`, el que usa la guía oficial de empaquetado, y se pide la versión 1.27 o posterior (`>=1.27`). Hay un detalle que conviene saber de entrada: la primera vez que instales el paquete, `pip` **descarga `hatchling` de internet** a un entorno temporal para construirlo. Es una dependencia de *construcción*, no de tu programa: el `revisor` sigue sin depender de nada para funcionar. Pero sin conexión, la instalación fallaría en ese paso. Las reglas de esta tabla están en el [PEP 518](https://peps.python.org/pep-0518/) y la interfaz de los backends en el [PEP 517](https://peps.python.org/pep-0517/); `hatchling` tiene su [propia documentación](https://hatch.pypa.io/latest/).

**`[project]`: ¿qué es este proyecto?** Aquí van los datos que cualquiera esperaría en la ficha de un paquete. `name` es el nombre con que se instala. `version` es la versión: el curso la sube un paso en cada lección desde hoy (`0.6.0` es la de hoy, y la lección 11 la deja en `1.0.0`). `description` es una frase. `requires-python = ">=3.12"` dice qué versiones de Python lo pueden ejecutar: `pip` se negará a instalarlo en un Python más viejo, en lugar de dejarlo fallar con un `SyntaxError` incomprensible más tarde. Y `dependencies = []` es la lista de paquetes de terceros que tu programa necesita para correr: hoy, ninguno, y por eso está vacía. En la lección 9 aparecerá una. El estándar que define estos campos es el [PEP 621](https://peps.python.org/pep-0621/).

**`[project.scripts]`: ¿qué comando crea?** Esta es la tabla que convierte un paquete en una herramienta. La línea `revisor = "revisor.cli:main"` dice: «al instalar, crea en el entorno un comando que se llama `revisor`, y cuando alguien lo ejecute, que llame a la función `main` del módulo `revisor.cli`». La forma `paquete.modulo:función` es una convención que la [especificación de puntos de entrada](https://packaging.python.org/en/latest/specifications/entry-points/) fija. Cuando lo instales, el comando `revisor` quedará junto al `python` de tu entorno, y funcionará igual que `python -m revisor`. Y de nuevo: el valor que `main` devuelve se vuelve el código de salida del comando.

Copia el contenido en `pyproject.toml`, junto al `servicios.toml`, en la carpeta del proyecto. Todavía no puedes instalar: falta el centro del programa.

### 7.3 `argparse`: opciones de línea de comandos

#### 7.3.1 Qué recibe un programa desde la terminal

Cuando escribes `python -m revisor --formato json`, la terminal parte lo que tecleaste en palabras y se las entrega al programa como una lista de textos, que Python guarda en `sys.argv`. En esa lista, la primera posición es el nombre del programa y las demás son los argumentos: `["fig07_02.py", "--formato", "json"]`. Podrías recorrerla tú, con un `for`, y buscar a mano `--formato` y el texto que le sigue. Pero eso se vuelve tedioso pronto: ¿qué pasa si el usuario escribe la opción dos veces?, ¿si olvida el valor?, ¿si escribe `--formato=json` con un signo igual? Para no reescribir esas reglas en cada programa, la biblioteca estándar trae el módulo `argparse`, que las resuelve, genera la ayuda sola, y valida lo que el usuario escribe.

Mira un programa pequeño que lo demuestra, `fig07_02.py`. Declara dos opciones y las imprime:

```python
# fig07_02.py
import argparse

parser = argparse.ArgumentParser(description="Demostración de argparse.")
parser.add_argument("--config", default="servicios.toml")
parser.add_argument("--formato", choices=["tabla", "json"], default="tabla")

argumentos = parser.parse_args()
print(f"config = {argumentos.config}")
print(f"formato = {argumentos.formato}")
```

`argparse.ArgumentParser(description=...)` crea el **analizador** (*parser*): el objeto que sabrá interpretar la línea de comandos. Cada `add_argument` declara una opción: su nombre (con dos guiones al frente, la convención de las opciones largas), un valor por omisión (`default`) y, en la segunda, `choices`, la lista cerrada de valores permitidos. Por último, `parse_args()` lee `sys.argv`, comprueba todo y devuelve un objeto con un atributo por opción, de modo que `argumentos.formato` tiene el valor que escribió el usuario, o el de por omisión si no escribió nada. Ejecútalo sin opciones, y después con ellas:

```text
$ python fig07_02.py
config = servicios.toml
formato = tabla
```

```text
$ python fig07_02.py --formato json --config otro.toml
config = otro.toml
formato = json
```

Sin opciones valen los valores por omisión. Con ellas, valen los que escribiste, en el orden que quieras. Pero lo valioso es lo que `argparse` hace sin que lo pidas. Primero, la ayuda: `-h` y `--help` existen automáticamente.

```text
$ python fig07_02.py --help
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]

Demostración de argparse.

options:
  -h, --help            show this help message and exit
  --config CONFIG
  --formato {tabla,json}
```

Se arma a partir de lo que declaraste: el uso, la descripción, y cada opción con su lista de valores. (Las palabras fijas de `argparse`, como «options» o «show this help message and exit», están en inglés porque vienen de la biblioteca; los textos que tú escribes con `help=` y `description=` salen como los escribas, y eso es lo que haremos en el `revisor`.) Segundo, los errores: si el usuario escribe algo que no declaraste, `argparse` lo rechaza con un mensaje y termina el programa:

```text
$ python fig07_02.py --verbose
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]
fig07_02.py: error: unrecognized arguments: --verbose
```

El mensaje dice qué falló (`unrecognized arguments: --verbose`, «argumentos no reconocidos») y repite la línea de uso para que el usuario vea cómo es la forma correcta. Además termina el programa con un código de salida distinto de cero, concretamente el 2: la [documentación de `argparse`](https://docs.python.org/3/library/argparse.html#exiting-methods) lo establece para todo error de uso. Ese 2 será el del `revisor` cuando el uso sea inválido.

#### 7.3.2 El `cli.py` del `revisor`

Con eso en la mano, el módulo central del paquete se lee sin sobresaltos. `cli.py` («*command-line interface*», la interfaz de línea de comandos) reemplaza al `revisor.py` plano de la lección 6. Tiene dos funciones: una que arma el analizador y otra que es el programa. Léelo entero una vez:

```python
# fig07_01/src/revisor/cli.py
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

**`construir_parser`** devuelve el analizador, con tres opciones. `--config` recibe la ruta del archivo de configuración; `type=Path` le dice a `argparse` que convierta el texto que escriba el usuario en un `Path` (lección 6), y su valor por omisión es `Path("servicios.toml")`, el mismo de siempre. `--formato` tiene dos opciones cerradas, `tabla` y `json`, y por omisión `tabla`: si el usuario escribe cualquier otra cosa, `argparse` lo rechaza antes de que el resto de `main` llegue a ver el valor, y no hay que escribir un `if` para eso. Y `--version` usa `action="version"`, una acción predefinida que imprime un texto y termina: el texto es `revisor` seguido del número de versión, que se **lee de los metadatos del paquete instalado** con `importlib.metadata.version("revisor")`. Esto resuelve un problema muy común: el número de versión se escribiría en `pyproject.toml` y otra vez en el código, y las dos copias acabarían por diferir. Así existe en un solo lugar, el `pyproject.toml`. El argumento `prog="revisor"` fija el nombre que sale en el uso y en los errores; sin él, en Python 3.12 saldría `__main__.py`, el archivo que se ejecuta con `-m`, y en 3.14 saldría `python -m revisor`; con `prog`, las dos versiones dicen lo mismo.

**`main`** es el programa. Recibe una lista de argumentos opcional, `argv: list[str] | None = None`, y devuelve un entero. Si `argv` es `None`, `parse_args(None)` lee la línea de comandos real; si le pasas una lista, la usa en su lugar. Ese parámetro parece un lujo hoy y es una pieza clave en la lección 8, donde las pruebas llamarán a `main(["--formato", "json"])` sin tocar la terminal. El cuerpo es lo que ya conoces: lee los servicios con `leer_servicios(argumentos.config)`, y si falla con `ErrorDeConfiguracion`, imprime el mensaje y devuelve 2. Hay dos diferencias con la lección 6, y son las dos ideas de 7.4: el mensaje ahora sale con `file=sys.stderr` (a la salida de error, no a la estándar) y devuelve 2 en lugar de limpiar y seguir. Después revisa los servicios, y según `--formato` imprime la tabla de siempre o el JSON de `reporte_a_json`. Por último, decide el código de salida: arma la lista de los resultados cuyo estado **no** es `ARRIBA` (el operador `is not` es la negación de `is`, lección 3), y si está vacía devuelve 0, y si no, 1.

Para que quede explícito, los códigos de salida del `revisor` son estos tres, **los del curso entero**:

| Código | Qué significa |
|---|---|
| `0` | Todo está `ARRIBA`. |
| `1` | El `revisor` funcionó, pero algún servicio está `LENTO` o `CAIDO`. |
| `2` | El `revisor` no pudo revisar: el uso es inválido (lo decide `argparse`) o la configuración no sirve. |

La distinción entre 1 y 2 importa mucho. Un `1` es una respuesta: «revisé y encontré problemas». Un `2` es una falla del propio programa: «no pude ni revisar». Quien automatice el `revisor` los tratará distinto: con un `1` avisará a quien atiende los servicios; con un `2` avisará a quien mantiene el `revisor`.

### 7.4 Códigos de salida, dos canales de texto, y la instalación editable

#### 7.4.1 Los códigos de salida

Todo programa que termina le deja a quien lo llamó un número entero entre 0 y 255. Es el **código de salida** (*exit status*). Por convención de Unix, **0 significa éxito y cualquier otro número significa algún tipo de fallo**. No hay nada mágico: es un acuerdo, y todo el ecosistema de la terminal lo respeta. En la terminal (técnicamente, el intérprete de comandos, que en Linux Mint es `bash`) puedes preguntar el código del último comando con la variable especial `$?`, que se lee con `echo $?`. El estándar POSIX define cómo lo interpreta el intérprete de comandos en la [sección de estado de salida](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_08_02), y es lo que permite escribir cosas como `revisor && echo "todo bien"` (el `echo` solo corre si `revisor` terminó en 0) o `revisor || avisar.sh` (el segundo solo corre si el primero terminó con algo distinto de 0).

En Python, hay dos maneras de salir con un código. Una es llamar a `sys.exit(codigo)`, que levanta `SystemExit`. La otra es lo que ya viste en `__main__.py`: levantar `SystemExit` tú mismo. Hacen lo mismo, y la [documentación de `sys.exit`](https://docs.python.org/3/library/sys.html#sys.exit) y la de [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) lo explican. Lo que importa es el diseño: `main` **devuelve** el código en lugar de llamar a `sys.exit` por su cuenta, y es `__main__.py` quien lo convierte en una salida. Así `main` se puede llamar desde otro código (una prueba, por ejemplo) y devolver su número sin matar el proceso que lo llamó. Cuando alguien instala el paquete, el comando `revisor` que crea `[project.scripts]` hace lo mismo: llama a `main()` y sale con lo que devuelva.

#### 7.4.2 Dos canales: la salida estándar y la salida de error

Un programa tiene, desde que arranca, dos lugares donde escribir texto. La **salida estándar** (`stdout`) es el canal normal: lo que `print` escribe por omisión, y donde van los resultados. La **salida de error** (`stderr`) es un canal aparte para los avisos y los errores. En la terminal, ambos aparecen en la pantalla, uno junto al otro, y por eso parecen lo mismo. Pero son canales distintos, y esa diferencia se nota en cuanto redirigimos uno. Mira `fig07_03.py`, que escribe en los dos:

```python
# fig07_03.py
import sys

print("reporte: 4 servicios revisados")
print("aviso: reportes no respondió", file=sys.stderr)
```

`print(..., file=sys.stderr)` manda el texto a la salida de error en lugar de la estándar; `sys` es un módulo de la biblioteca estándar que da acceso a cosas del propio intérprete, entre ellas `sys.stderr` ([documentación](https://docs.python.org/3/library/sys.html#sys.stderr)). Ejecútalo tres veces:

```text
$ python fig07_03.py
reporte: 4 servicios revisados
aviso: reportes no respondió
```

```text
$ python fig07_03.py > /dev/null
aviso: reportes no respondió
```

```text
$ python fig07_03.py 2> /dev/null
reporte: 4 servicios revisados
```

La primera muestra las dos líneas. La segunda usa `>`, que **redirige la salida estándar** hacia otro lugar (aquí, `/dev/null`, un archivo especial de Linux que descarta todo lo que se le escribe): solo queda el aviso, que viaja por el otro canal. La tercera usa `2>`, que redirige el canal número 2, el de error, y deja pasar el reporte. (Los canales tienen número: 0 la entrada, 1 la estándar, 2 la de error.) Las [redirecciones del intérprete de comandos](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_07) son el mecanismo que lo permite.

Eso es lo que hace útil la separación. Cuando alguien ejecuta `revisor --formato json > reporte.json`, quiere que el archivo `reporte.json` contenga **solo el JSON**. Si el programa escribiera un mensaje de error por la salida estándar, el archivo quedaría con texto mezclado y dejaría de ser JSON válido. Con el error en `stderr`, el mensaje sale en la pantalla, el archivo queda limpio (o vacío, si el programa no llegó a producir nada) y el código de salida cuenta qué pasó. Por eso el `cli.py` manda los errores de configuración a `stderr` y el reporte a `stdout`.

Así se comporta el `revisor` ya instalado cuando se le da un archivo de configuración que no existe: el mensaje sale por la salida de error y el programa termina con el código 2.

```text
$ python -m revisor --config no-existe.toml
error de configuración: no existe el archivo no-existe.toml
$ echo $?
2
```

#### 7.4.3 Instalar en modo editable

Falta el paso que une todo: instalar el paquete. Antes, mira qué pasa si intentas ejecutarlo **sin** instalarlo. Con el entorno activo y parado en la carpeta del proyecto, con los archivos ya en su lugar:

```text
$ python -m revisor
/home/tu_usuario/curso-python/.venv/bin/python: No module named revisor
```

El mensaje, `No module named revisor`, es lo que cabía esperar de 7.1.2: Python buscó un módulo llamado `revisor` en la carpeta actual y en el entorno, y no lo encontró, porque el paquete está dentro de `src/`, una carpeta donde no busca. (La ruta del principio es la del `python` de tu entorno virtual; la tuya será la de tu carpeta.) No es un error de tu código: es lo que `src/` provoca a propósito, y se resuelve instalando.

La instalación se hace con `pip`, ya dentro del entorno, desde la carpeta del proyecto (donde está el `pyproject.toml`):

```bash
python -m pip install -e .
```

El punto final significa «el proyecto de esta carpeta», y `-e` («*editable*») pide una instalación **editable**. Verás varias líneas de avance, que cambian de una versión de `pip` a otra, y la última dice algo como esto:

```text
Successfully installed revisor-0.6.0
```

Si el mensaje es otro, lee la causa: lo más común es que no estés en la carpeta que tiene el `pyproject.toml`, o que no tengas conexión para que `pip` descargue `hatchling`.

¿Qué significa «editable»? Una instalación normal **copia** los archivos del paquete a la carpeta `site-packages` del entorno, y a partir de ahí el paquete instalado y tu carpeta de trabajo son dos cosas distintas: si editas tu código, el instalado no se entera. Una instalación editable, en cambio, deja en el entorno **un puntero hacia tu carpeta `src/`**, de modo que Python importa el código de donde está, tal como lo escribiste ([PEP 660](https://peps.python.org/pep-0660/); la [documentación de `pip`](https://pip.pypa.io/en/stable/topics/local-project-installs/) explica los dos tipos de instalación local). Es lo que quieres mientras desarrollas: cambias una línea, ejecutas, y ves el cambio, sin reinstalar. Con el paquete instalado, ejecútalo; esta vez el código de salida lo imprime `echo $?`:

```text
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
$ echo $?
1
```

Ahí está la tabla de siempre, con el resumen, y el código de salida es **1**, porque entre los cuatro servicios hay uno `LENTO` (`inventario`) y uno `CAIDO` (`reportes`). Es el comportamiento que se quería: el programa funcionó, y avisa que encontró problemas. La opción `--formato json` produce el reporte para máquinas, que es el contrato que fijó la lección 6:

```text
$ python -m revisor --formato json
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
$ echo $?
1
```

La opción `--version` lee el número de la instalación, y funciona porque instalaste el paquete:

```text
$ python -m revisor --version
revisor 0.6.0
```

Y `--help` te da la ayuda, armada con los textos que escribiste en `help=`:

```text
$ python -m revisor --help
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]

Revisa el estado de una lista de servicios.

options:
  -h, --help            show this help message and exit
  --config CONFIG       archivo TOML con la lista de servicios (por omisión:
                        servicios.toml)
  --formato {tabla,json}
                        forma del reporte (por omisión: tabla)
  --version             show program's version number and exit
```

Falta la mitad de lo que prometía `[project.scripts]`: el **comando** `revisor`. Se creó al instalar, junto al `python` del entorno, y con el entorno activo se ejecuta sin `python -m`:

```text
$ revisor --version
revisor 0.6.0
```

Lo que hace `-m` es útil porque funciona siempre, aun si el comando no estuviera a la vista. Pero el comando es como la gente usará el `revisor` en la lección 11, instalado con `pipx`.

Dos precisiones sobre lo que «editable» no cubre. La primera: **solo sigue al código, no a los metadatos**. Si cambias el contenido de un módulo, el cambio se ve de inmediato. Pero si cambias el `pyproject.toml` (por ejemplo, la versión, o un comando de `[project.scripts]`), el entorno sigue con los metadatos de la última instalación, hasta que vuelvas a ejecutar `python -m pip install -e .`. El ejercicio 4 lo comprueba. La segunda: la instalación editable vive en tu **entorno virtual**, así que un entorno nuevo (o uno recién creado) no tiene el `revisor` hasta que lo instales de nuevo. Es exactamente el comportamiento que se quiere: ninguna instalación se mezcla con el Python del sistema.

> **Recuadro opcional: `uv`.** Existe una herramienta más nueva, `uv`, que hace por su cuenta el trabajo de `venv` y de `pip`, y que es más rápida. Con ella, los mismos pasos se escriben `uv venv` (crea el entorno `.venv`) y `uv pip install -e .` (instala el proyecto en él). Además puede instalar otras versiones de Python: `uv python install 3.14` baja la 3.14 sin tocar el Python del sistema, lo que es la forma más cómoda de probar este curso en la versión más reciente además de en la 3.12 de Mint. La [guía de instalación de `uv`](https://docs.astral.sh/uv/getting-started/installation/) explica cómo conseguirlo, y su documentación sobre [versiones de Python](https://docs.astral.sh/uv/concepts/python-versions/) y sobre [la interfaz `uv pip`](https://docs.astral.sh/uv/pip/) cubre el resto. Este curso no lo exige: todo lo que ves aquí funciona con el `python` y el `pip` que ya tienes.

#### 7.4.4 El paso del proyecto: ensamblarlo todo

Si fuiste siguiendo la lección, tu carpeta `~/curso-python/revisor/` ya tiene el aspecto de 7.1.2. Estos son los pasos completos, en orden, para quien los quiera de corrido:

1. Crea `src/revisor/` y mueve a ella los cuatro módulos; renombra `revisor.py` a `cli.py` y borra `ver_json.py` (7.1.4).
2. Antepón `revisor.` a las importaciones de tus módulos (7.1.4).
3. Escribe `src/revisor/__init__.py` y `src/revisor/__main__.py` (7.1.3).
4. Escribe `pyproject.toml` (7.2).
5. Reescribe `src/revisor/cli.py` con `construir_parser` y `main` (7.3.2).
6. Con el entorno activado y desde la carpeta del proyecto, ejecuta `python -m pip install -e .` (7.4.3).
7. Prueba: `python -m revisor`, `python -m revisor --formato json`, `python -m revisor --version`, y después de cada uno, `echo $?`.

Hay una consecuencia de lo que acabas de hacer, que se ve al ejecutarlo desde **otra carpeta**. Súbete a la carpeta de arriba y ejecuta el mismo comando:

```text
$ python -m revisor
error de configuración: no existe el archivo servicios.toml
```

El paquete se encontró (está instalado en el entorno, ya no importa dónde estés), pero el archivo de configuración no: `--config` vale `servicios.toml` por omisión, una ruta relativa, y la carpeta de arriba no tiene uno. El mensaje es el que ya conoces de la lección 6, ahora en la salida de error y con código de salida 2. La opción `--config` existe justo para esto: `python -m revisor --config revisor/servicios.toml` funcionaría desde ahí. Dónde vive el código y dónde vive la configuración son dos preguntas distintas, y el programa las separa.

## El error que vas a ver

Esta lección tiene dos errores principales, los dos de la lista de arriba, y dos de apoyo que aparecen cuando algo del montaje se olvida.

**`No module named revisor`.** Ya lo viste en 7.4.3: ejecutar `python -m revisor` antes de `pip install -e .`. La causa es el diseño `src/`, y la corrección es instalar. Si ya instalaste y aun así aparece, comprueba que tienes el entorno activado: el mensaje empieza con la ruta del `python` que se usó, y si esa ruta es `/usr/bin/python3` en lugar de la de tu `.venv`, estás usando el Python del sistema, que no tiene tu paquete.

**El error de uso de `argparse`.** Pide un formato que no existe:

```text
$ python -m revisor --formato xml
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]
revisor: error: argument --formato: invalid choice: 'xml' (choose from 'tabla', 'json')
$ echo $?
2
```

Lee los dos renglones: el primero repite el uso, con las opciones que existen y sus valores permitidos entre llaves (`{tabla,json}`); el segundo dice cuál argumento falló y por qué: `invalid choice: 'xml'`, «opción inválida». Entre paréntesis, la lista de las válidas. El código de salida es 2, el que `argparse` usa siempre para un uso inválido. Un detalle de versión: este es el texto de Python 3.14, que muestra las opciones entre comillas, `('tabla', 'json')`. En Python 3.12 la lista sale sin comillas, `(choose from tabla, json)`. Es la única salida de la lección que difiere entre las dos versiones, y es un cambio en el formato del texto; el significado es el mismo.

**`ModuleNotFoundError: No module named 'modelo'`.** Aparece si moviste los archivos pero olvidaste cambiar alguna importación: el paquete se encuentra, pero uno de sus módulos sigue importando `modelo` a secas, y ya no existe un `modelo` suelto. El informe, abreviado:

```text
Traceback (most recent call last):
  ...
  File "src/revisor/__main__.py", line 2, in <module>
    from revisor.cli import main
  File "src/revisor/cli.py", line 9, in <module>
    from modelo import Estado
ModuleNotFoundError: No module named 'modelo'
```

Se lee de abajo hacia arriba, como siempre: la última línea dice qué módulo no se encontró (`modelo`); la línea de arriba, en qué archivo y en qué línea está el `import` que falla (`cli.py`, línea 9); y más arriba, la cadena de quién importó a quién. La corrección es `from revisor.modelo import Estado`. (El número de línea dependerá de cómo hayas escrito tu `cli.py`; lo que importa es el nombre del módulo de la última línea.)

**`importlib.metadata.PackageNotFoundError: No package metadata was found for revisor`.** Aparece si ejecutas el código sin haber instalado el paquete (por ejemplo, añadiendo `src` a la lista de lugares de búsqueda a mano). Los módulos se encuentran, pero `version("revisor")`, que `construir_parser` ejecuta siempre, busca los **metadatos** de una instalación, y no hay ninguna. Es la prueba de que el número de versión sale de la instalación y no del código: la solución es `python -m pip install -e .`, no esconder la línea. El informe termina así:

```text
importlib.metadata.PackageNotFoundError: No package metadata was found for revisor
```

## Lo que se hace mal

**Importar sin el nombre del paquete dentro de un paquete.** `from modelo import Servicio` funciona mientras los archivos están pegados y falla en cuanto el código se instala o se ejecuta con `-m`. Dentro del paquete se escribe siempre `from revisor.modelo import Servicio`.

**Arreglar las importaciones modificando `sys.path`.** Es una receta que circula: agregar a mano la carpeta del código a la lista de lugares de búsqueda para que los `import` funcionen. Resuelve el síntoma y esconde la causa, que es que el paquete no está instalado. Con `pip install -e .` no hace falta.

**Instalar con `pip` fuera del entorno virtual.** Ya sabes por qué no funciona en Linux Mint (lección 1): el Python del sistema no trae `pip` (`No module named pip`), y donde sí lo trae, la protección de la PEP 668 lo frena con `externally-managed-environment`. Y la salida que a veces se sugiere, forzarlo, rompe las herramientas del propio sistema. Se instala dentro del `.venv`, siempre.

**Escribir el número de versión en dos sitios.** Uno en `pyproject.toml` y otro en una constante del código: tarde o temprano difieren, y la versión que el programa dice ya no es la que se instaló. El número vive en el `pyproject.toml`, y el programa lo lee con `importlib.metadata`.

**Mandar los errores a la salida estándar.** Mezcla el aviso con el reporte, y `revisor --formato json > reporte.json` produce un archivo que no es JSON válido. Los errores, a `sys.stderr`.

**Terminar siempre con código 0.** Un programa que sale igual de bien con todo caído que con todo arriba no le sirve a ningún automatismo. El código de salida es parte del contrato del programa, tanto como el formato del reporte.

**Inventar códigos de salida sin documentarlos.** Un 3 para esto, un 4 para aquello, sin que nadie los conozca, obliga a quien automatice a leer el código fuente. Hay tres códigos y están en una tabla.

**Leer `sys.argv` a mano.** Funciona hasta que alguien escribe `--formato=json` en lugar de `--formato json`, o se olvida del valor, o pide la ayuda. `argparse` ya resolvió esos casos.

**Cambiar el `pyproject.toml` y no reinstalar.** La instalación editable sigue el código, no los metadatos. Si cambias la versión o un comando y el entorno sigue con lo anterior, falta un `python -m pip install -e .`.

## Ejercicios

### Ejercicio 1 — El reporte en JSON y su código

Con el paquete instalado, ejecuta `python -m revisor --formato json` y, justo después, `echo $?`. Antes de ejecutar, escribe qué esperas ver: cuántos servicios hay en el arreglo `servicios`, qué valor tiene `tiempo_ms` para `reportes`, y qué código de salida. Después, redirige la salida a un archivo con `python -m revisor --formato json > reporte.json` y mira el contenido de `reporte.json` con `cat reporte.json` (`cat` imprime en pantalla el contenido de un archivo). ¿Cambió el código de salida al redirigir?

### Ejercicio 2 — Los tres códigos

Provoca los tres códigos de salida del `revisor`, uno por uno, y compruébalos con `echo $?`: (a) un `0`, para lo que necesitas una configuración en la que todos los servicios estén `ARRIBA` (escribe un archivo `solo-arriba.toml` con un solo servicio, `pagos`, y úsalo con `--config`); (b) un `1`, con el `servicios.toml` de siempre; (c) un `2` por configuración inválida, con un `roto.toml` que tenga un servicio sin `nombre`; (d) otro `2`, ahora por uso inválido, con un valor de `--formato` que no exista. Para cada caso, escribe primero qué esperas ver y en qué canal aparece el mensaje.

### Ejercicio 3 — Dónde vive el código y dónde vive la configuración

Sal de la carpeta del proyecto con `cd ..` y ejecuta `python -m revisor`. ¿Qué mensaje obtienes y qué código de salida? Después ejecuta el mismo comando pasando la ruta de la configuración con `--config`. Explica con tus palabras por qué el paquete se encuentra desde cualquier carpeta pero el archivo de configuración no.

### Ejercicio 4 — Qué sigue y qué no sigue la instalación editable

Con el paquete instalado en modo editable: (a) en `src/revisor/formato.py`, cambia la palabra `promedio` del resumen por `media`, y ejecuta el `revisor` sin reinstalar: ¿se nota el cambio? Devuélvelo a como estaba. (b) En `pyproject.toml`, cambia la versión a `0.6.1`, y ejecuta `python -m revisor --version` sin reinstalar: ¿qué versión dice? (c) Ejecuta `python -m pip install -e .` y vuelve a pedir la versión. (d) Devuelve la versión a `0.6.0` y reinstala. Explica la diferencia entre (a) y (b).

## Soluciones

### Solución 1

La predicción: el arreglo `servicios` tiene **cuatro** elementos, uno por servicio; el de `reportes` tiene `"tiempo_ms": null` (no respondió, y `None` se escribe `null` en JSON); y el código de salida es **1**, por el servicio lento y el caído. La salida de `python -m revisor --formato json` es la que viste en 7.4.3, y el `echo $?` imprime `1`.

Al redirigir, el contenido de `reporte.json` es **exactamente el mismo JSON**: nada del terminal se mezcló con él, porque los avisos (si los hubiera) van por otro canal. Y el código de salida **no cambia**: redirigir mueve el texto, no el resultado. Esa es la propiedad que permite escribir `revisor --formato json > reporte.json || avisar.sh` y que el `||` siga funcionando.

### Solución 2

(a) Con un solo servicio que responde bien:

```toml
[[servicios]]
nombre = "pagos"
url = "https://pagos.example"
```

Ejecutado con `python -m revisor --config solo-arriba.toml`:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA      87ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 87ms
```

y `echo $?` imprime **0**. (Observa que el resumen dice «1 servicio» y «0 lentos»: el plural lo decide la cuenta, como en la lección 5.)

(b) Con el `servicios.toml` de siempre: la tabla de cuatro servicios y el código **1**.

(c) Con un `roto.toml` cuyo único servicio no tiene `nombre`:

```toml
[[servicios]]
url = "https://pagos.example"
```

Ejecutado con `python -m revisor --config roto.toml`, sale por la **salida de error** el mensaje `error de configuración: servicio 1: falta 'nombre'`, y el código es **2**. Para comprobar el canal, repite el comando con `2> /dev/null`: no aparece nada en pantalla, porque lo único que se imprimió iba por `stderr`; el código de salida sigue siendo 2.

(d) Con `python -m revisor --formato xml`, el error de `argparse` que ya viste: va por la salida de error, y el código es **2**.

### Solución 3

Desde la carpeta de arriba, `python -m revisor` imprime, por la salida de error, `error de configuración: no existe el archivo servicios.toml`, y el código de salida es **2**. Con `python -m revisor --config revisor/servicios.toml` el programa encuentra el archivo, imprime la tabla de cuatro servicios y sale con **1**.

La razón: el **paquete** se encuentra porque está instalado en el entorno, y el entorno no depende de la carpeta donde estés. En cambio `servicios.toml` es un archivo **de datos** con una ruta relativa, y una ruta relativa siempre se cuenta desde donde estás parado. Son dos mecanismos de búsqueda distintos: Python busca código en las carpetas del entorno; el programa busca la configuración donde se le diga. Por eso `--config` existe.

### Solución 4

(a) Sí se nota: el resumen dice `media 843ms` en lugar de `promedio 843ms`, sin reinstalar, porque la instalación editable importa el código desde tu carpeta `src/`. (b) No se nota: `--version` sigue diciendo `revisor 0.6.0`, porque la versión se lee de los metadatos que se guardaron en la última instalación, y editar el `pyproject.toml` no los actualiza. (c) Después de `python -m pip install -e .`, `--version` dice `revisor 0.6.1`. (d) Al devolver la versión a `0.6.0` y reinstalar, vuelve a decir `revisor 0.6.0`.

La diferencia: el **código** se importa desde donde está, cada vez que Python arranca; los **metadatos** (versión, comandos) se copian al entorno al instalar. Lo que `-e` evita es la copia del código, no la de los metadatos.

## Cómo sé que lo logré

- [ ] `python -m revisor` imprime la tabla de cuatro servicios con el resumen `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`, y `echo $?` imprime `1`.
- [ ] `python -m revisor --formato json` imprime el JSON con `"promedio_ms": 843`, y `python -m revisor --formato json > reporte.json` deja en el archivo un JSON válido y nada más.
- [ ] `python -m revisor --version` imprime `revisor 0.6.0`, y el comando `revisor --version` imprime lo mismo.
- [ ] `python -m revisor --formato xml` termina con el error de `argparse` y el código 2.
- [ ] `python -m revisor --config no-existe.toml` imprime `error de configuración: no existe el archivo no-existe.toml` y termina con 2; con `2> /dev/null`, no se ve nada en pantalla.
- [ ] Puedes explicar con tus palabras por qué `python -m revisor` falla con `No module named revisor` antes de instalar, y por qué eso es lo que `src/` pretende.
- [ ] Puedes decir qué canal usa cada mensaje del `revisor` (reporte, error de configuración, error de uso) y qué código acompaña a cada caso.
- [ ] Anotaste en tu bitácora qué parte del montaje (rutas, importaciones, instalación) te costó más.

## Resumen

Responde sin mirar la lección:

1. ¿Qué diferencia hay entre un módulo y un paquete, y qué lo vuelve un paquete?
2. ¿Qué ventaja tiene poner el paquete dentro de `src/`? ¿Qué pasaría con `python -m revisor` desde la raíz si no estuviera ahí?
3. ¿Qué ejecuta `python -m revisor`, y qué hace `raise SystemExit(main())`?
4. ¿Qué pregunta responde cada tabla del `pyproject.toml`: `[build-system]`, `[project]` y `[project.scripts]`?
5. ¿Por qué `pip install -e .` necesita internet la primera vez, si el `revisor` no tiene dependencias?
6. ¿Qué devuelve `parse_args()`? ¿Qué hace `argparse` cuando el usuario escribe una opción que no existe, y con qué código termina?
7. ¿Qué significan los códigos 0, 1 y 2 del `revisor`? ¿Cómo se lee el código de la última orden en la terminal?
8. ¿Qué diferencia hay entre la salida estándar y la salida de error? ¿Qué hacen `>` y `2>`?
9. ¿Qué sigue una instalación editable y qué no? ¿Cómo se actualiza lo que no sigue?
10. ¿De dónde sale el número que imprime `--version`, y por qué no se escribe en el código?

## Para leer más

- [Python, `argparse`](https://docs.python.org/3/library/argparse.html): la referencia completa del módulo (acciones, subcomandos, grupos de opciones). En inglés, como casi toda la documentación oficial. Consultado el 7 de octubre de 2026.
- [Python Packaging User Guide, «Writing your `pyproject.toml`»](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/): todos los campos de `[project]` y de `[project.scripts]`, y las razones del diseño. Consultado el 7 de octubre de 2026.
- [Python Packaging User Guide, «src layout vs flat layout»](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/): las dos formas de poner el paquete, comparadas con sus costos. Consultado el 7 de octubre de 2026.
- [Python, tutorial de módulos y paquetes](https://docs.python.org/3/tutorial/modules.html#packages): cómo se importa y cómo se organiza un paquete, con las importaciones absolutas y relativas. Consultado el 7 de octubre de 2026.
