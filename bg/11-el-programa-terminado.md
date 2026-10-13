# Урок 11 — Завършената програма

**Време:** 2 × 90 минути (първата сесия стига до края на 11.2; втората започва в 11.3)

**Какво изграждаш:** пълния `revisor`, версия 1.0.0, инсталиран на твоя компютър като поредната команда

**Какво научаваш:** отчета като договор (таблица с изчислена ширина и тестван JSON); `logging` и `--verbose`; кодовете на изход, преговорени; преглед на сигурността (адресът, който друг въвежда, `subprocess` без `shell=True`, `secrets`, нито `eval`, нито `pickle`); изграждане на пакета и инсталирането му с `pipx`

**Откъде идваш.** Носиш `revisor` от [Урок 10](10-concurrencia-pruebas-sin-red.md): пакет, който чете конфигурацията си, проверява услугите едновременно, с времеви лимит и с таван на едновременните заявки, и който има 27 теста, които не докосват мрежата. Работи, и работи добре. Но още живее в твоята папка: пуска се с `python -m revisor` оттам, където е кодът, а таблицата му има недостатък, който не си видял, защото всичките ти услуги имат къси имена: колоната `SERVICIO` е винаги широка 12 знака, а услуга на име `notificaciones-de-clientes` я прелива. Днес всичко това се затваря. Работиш в папката си `~/curso-python/revisor/`, с активирана виртуална среда и, за последната част, с инсталиран `pipx`.

**Какво не прави този урок.** Почти не въвежда нови понятия от Python: това е урокът, в който **събираш** онова, което вече знаеш, и проверяваш, че е завършено. Новото е занаятчийско: `logging`, езикът, с който една програма разказва какво прави, без да цапа отчета си; финалното пакетиране; и преговорът на четирите навика за сигурност, които курсът постепенно засяваше. Последната стъпка не е още един урок: това е списъкът от седем проверки, с които `es/README.md` определя кога курсът е приключил, а този урок ги преминава **една по една**, с реалния изход на всяка.

## След урока ще можеш да

- Да обясниш защо отчетът, който друга програма чете, е договор, и да тестваш този договор с тест, който става червен, ако някой преименува поле.
- Да изчисляваш ширината на колона от данните и да подравняваш таблица, дори когато едно име е дълго.
- Да използваш `logging` вместо `print` за онова, което програмата разказва за себе си, и да обясниш защо отчетът отива към стандартния изход, а журналът към изхода за грешки.
- Да кажеш за всеки код на изход (0, 1 и 2) какво обещава `revisor` на онзи, който го вика от скрипт.
- Да назовеш и избягваш четири често срещани риска за сигурността: адрес, който друг въвежда, `subprocess` с `shell=True`, `eval` и `pickle` с данни отвън, и „случайни“ числа за тайни.
- Да изградиш пакета като инсталируем файл (`.whl`), да го инсталираш с `pipx` и да го изпълняваш от коя да е папка.
- Да провериш, с по една команда и един изход за всяка, че `revisor` изпълнява седемте точки от „Как разбираш, че си завършил“.

## Защо, преди как

Когато някой каже „готов съм с програмата“, може да има предвид поне три неща. Че **работи на неговия компютър**, днес, с неговите данни. Че **друг човек може да я инсталира и използва** без да иска помощ. Или че **може да ѝ се има доверие**: че ако нещо се обърка, го казва ясно, че ако нещо се промени, един тест го научава преди потребителя, че не увисва, че не отваря врати, които не е трябвало. Трите са различни и е много обичайно да се предаде първото с убеждението, че е третото.

Курсът започна от теб, седнал пред един `print("revisor: todavía no revisa nada")`, и завършва в този урок, защото `revisor` вече трябва да се справя сам. За да се прецени дали е успял, не стига впечатлението, че „вече е готово“: впечатлението е първото, което се проваля. Затова програмата определя края със **седем проверки**, които могат да се изпълнят, а не с мнение. Ето ги, и ще ги преминеш една по една в края на урока:

1. `pytest` завършва зелено и отчетът казва колко теста са се изпълнили.
2. `ruff check`, `ruff format --check` и `mypy` не докладват нищо.
3. Проверява 20 услуги едновременно за време, близко до това на най-бавната, а не до сбора.
4. Паднала, бавна или отговаряща с боклук услуга не събаря отчета.
5. Никоя заявка не може да чака вечно.
6. Работи по един и същ начин на Python 3.14 и на 3.12 от твоя Mint.
7. Инсталира се с `pipx install` и `revisor --help` работи от друга папка; излиза с 0, ако всичко работи, и с 1, ако не е така.

От тези седем твоят `revisor` вече изпълнява почти всички, а може и да не го знаеш. Липсват три неща: **да се измери** (никой не се доверява на „мисля, че да“), **да се остави в състояние, което друг може да използва** (отчетът, журналът, пакетирането) и **да се прегледат навиците за сигурност**, за да не е точка 4, „не събаря отчета“, само въпрос на случайни повреди, а и на враждебни входни данни. Четирите части на урока следват този ред.

## Понятията

### 11.1 Отчетът като договор

#### 11.1.1 Кой чете твоя отчет

Досега отчета го четеше ти, в терминал. Но програма от командния ред, която излиза с код 0 или 1, е направена така, че **друга програма** да я вика: скрипт на дежурството, който се изпълнява на всеки пет минути, задача за непрекъсната интеграция, която решава дали да пусне едно внедряване. Тази друга програма не *чете* отчета като теб: тя го **интерпретира**. Търси поле с име и очаква тип. Ако утре някой преименува `caido` на `caidos` в JSON, за човека това е правописна промяна; за скрипта е поле, което е изчезнало, и без тест, който да го хване, никой не разбира нищо, докато една нощ в три часа алармата не остане безмълвна, когато е трябвало да звъни.

На това му се казва **договор**: начинът, по който програмата обещава да предаде резултата си и който другите могат да приемат за верен. `revisor` има два договора. **JSON** (определен в Урок 6) е за машините: полетата и типовете му са фиксирани, а `tiempo_ms` на услуга, която не е отговорила, е `null`, не `0` и не текст. А **кодът на изход** (определен в Урок 7) е за командния интерпретатор (shell) и за всеки скрипт: `0`, ако всички услуги са `ARRIBA`; `1`, ако някоя е `LENTO` или `CAIDO`; `2`, ако употребата е невалидна или конфигурацията не става. Таблицата, напротив, е за хората и може да промени вида си, без да предупреждава никого.

Днес се прави явно онова, което досега беше подразбиращо се: пише се **тест, който описва целия JSON**. И се поправя един недостатък на таблицата.

#### 11.1.2 Ширината на колоната се изчислява, не се налучква

Виж недостатъка, преди да го поправиш. Урок 2 фиксира ширината на първата колона на 12 знака с `f"{nombre:<12}"`, и с имената от примера (най-дългото, `inventario`, е с 10) излизаше съвършено. С дълго име текстът излиза от колоната си и бута всички останали. Решението е ширината да **зависи от данните**: най-дългото от имената плюс два интервала въздух, с минимум 12, за да изглеждат късите таблици както винаги.

Има едно синтактично новство. Една f-string ти позволява да сложиш ширината **вътре** в спецификацията, с още една двойка скоби: `f"{nombre:<{ancho}}"` означава „подравни `nombre` отляво в поле от `ancho` знака“, където `ancho` е променлива. Същото е като `:<12`, само че 12 е заменено с променлива. Виж как изглежда целият `formato.py`:

```python
# fig11_05/src/revisor/formato.py
import json

from revisor.modelo import Estado, Resultado

ANCHO_MINIMO = 12


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado(ancho: int = ANCHO_MINIMO) -> str:
    return f"{'SERVICIO':<{ancho}}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(resultado: Resultado, ancho: int = ANCHO_MINIMO) -> str:
    nombre = resultado.servicio.nombre
    estado = resultado.estado.value
    tiempo = formatear_tiempo(resultado.tiempo_ms)
    return f"{nombre:<{ancho}}{estado:<10}{tiempo:>6}  {resultado.detalle}"


def ancho_servicio(resultados: list[Resultado]) -> int:
    mas_largo = max([len(r.servicio.nombre) for r in resultados], default=0)
    return max(ANCHO_MINIMO, mas_largo + 2)


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


def tabla(resultados: list[Resultado]) -> str:
    ancho = ancho_servicio(resultados)
    renglones = [encabezado(ancho)]
    renglones += [linea(resultado, ancho) for resultado in resultados]
    renglones += ["", resumen(resultados)]
    return "\n".join(renglones)


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

Три нови или променени функции. `ancho_servicio` изчислява ширината: един израз за построяване (comprehension) взема дължината на всяко име, `max(..., default=0)` връща най-голямата (`default=0` е онова, което `max` връща, ако списъкът е празен; без него `max([])` хвърля `ValueError`) и се добавят две. `max(ANCHO_MINIMO, ...)` налага минимума. `encabezado` и `linea` получават `ancho` със стойност по подразбиране `ANCHO_MINIMO`; така целият код, който ги викаше без ширина (например тестовете ти от Урок 8), продължава да работи без промени. А `tabla` свързва всичко: изчислява ширината **веднъж**, изгражда заглавния ред, по един ред за всеки резултат, един празен ред и обобщението, и ги съединява с нови редове. (`renglones += [...]` добавя в края на списъка всички елементи на другия, като няколко поредни `append`; а `"\n".join(...)` е `join` от Урок 4 с новия ред за разделител.) С четирите канонични услуги най-дългото име е с 10, `10 + 2 = 12` и изчислената ширина е 12: таблицата излиза **идентична** с онази, която имаше, байт по байт. Променя се само когато трябва да се промени.

#### 11.1.3 JSON като договор, тестван

Втората промяна е един тест. Прочети го цял: не е кратък и дължината му е смисълът.

```python
# fig11_05/tests/test_formato.py
import json

import pytest

from revisor.formato import formatear_tiempo, reporte_a_json, tabla
from revisor.modelo import Estado, Resultado, Servicio


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [(None, "—"), (87, "87ms"), (999, "999ms"), (2300, "2.3s")],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado


def servicio(nombre: str) -> Servicio:
    return Servicio(nombre, f"https://{nombre}.example")


CANONICOS = [
    Resultado(servicio("catalogo"), Estado.ARRIBA, 142, "200"),
    Resultado(servicio("inventario"), Estado.LENTO, 2300, "200"),
    Resultado(servicio("pagos"), Estado.ARRIBA, 87, "200"),
    Resultado(servicio("reportes"), Estado.CAIDO, None, "sin conexión"),
]


def test_el_json_es_un_contrato() -> None:
    esperado = {
        "servicios": [
            {
                "nombre": "catalogo",
                "url": "https://catalogo.example",
                "estado": "ARRIBA",
                "tiempo_ms": 142,
                "detalle": "200",
            },
            {
                "nombre": "inventario",
                "url": "https://inventario.example",
                "estado": "LENTO",
                "tiempo_ms": 2300,
                "detalle": "200",
            },
            {
                "nombre": "pagos",
                "url": "https://pagos.example",
                "estado": "ARRIBA",
                "tiempo_ms": 87,
                "detalle": "200",
            },
            {
                "nombre": "reportes",
                "url": "https://reportes.example",
                "estado": "CAIDO",
                "tiempo_ms": None,
                "detalle": "sin conexión",
            },
        ],
        "resumen": {
            "total": 4,
            "arriba": 2,
            "lento": 1,
            "caido": 1,
            "promedio_ms": 843,
        },
    }
    assert json.loads(reporte_a_json(CANONICOS)) == esperado


def test_la_tabla_se_alinea_con_un_nombre_largo() -> None:
    largo = Resultado(servicio("notificaciones-de-clientes"), Estado.ARRIBA, 50, "200")
    lineas = tabla([*CANONICOS, largo]).splitlines()
    ancho = len("notificaciones-de-clientes") + 2
    assert lineas[0].index("ESTADO") == ancho
    for renglon in lineas[1:6]:
        assert renglon[ancho : ancho + 6] in {"ARRIBA", "LENTO ", "CAIDO "}
```

`CANONICOS` са четирите канонични резултата, сглобени на ръка в теста; **не идват от мрежата, нито от лабораторията**. `test_el_json_es_un_contrato` записва очаквания JSON изцяло, поле по поле, като речник, и го сравнява с `json.loads(reporte_a_json(CANONICOS))`. Има две решения, които имат значение. Първото: тестът сравнява **какво означава** JSON (речникът, който излиза от `json.loads`), а не **текста** (интервалите и реда на редовете), защото на скрипт, който интерпретира JSON, му е все едно колко интервала има, а му пука много кои са полетата. Второто: тестът включва неудобния случай, `reportes` с `"tiempo_ms": None` (което в JSON е `null`), и `promedio_ms` от 843. Ако някой смени `0` с `null`, или махне поле, или промени закръглението на средното, тестът става червен.

Вторият нов тест, `test_la_tabla_se_alinea_con_un_nombre_largo`, добавя към четирите канонични една услуга с име от 26 знака (`[*CANONICOS, largo]` изгражда нов списък с елементите на `CANONICOS`, които звездичката „разопакова“ един по един, и `largo` накрая, без да докосва `CANONICOS`) и проверява две неща: че думата `ESTADO` от заглавния ред започва в колона 28 (26 плюс 2 въздух) и че във всеки ред с данни, в същата колона, има валидно състояние. За първото използва `.index(...)`, метод на текстовете, който търси откъде започва едно парче в текста и връща позицията му, броейки от 0 като индексите на списъците: `lineas[0].index("ESTADO")` е колоната, от която започва `ESTADO` в заглавния ред (ако не го намери, би се провалил с `ValueError`). Този `renglon[ancho : ancho + 6]` е срез: синтаксисът `[inicio:fin]` взема знаците от позиция `inicio` до предходната на `fin`, така че тук са шестте, които започват в колоната на състоянието, колкото е дълго `"ARRIBA"`. В `in {"ARRIBA", "LENTO ", "CAIDO "}` има интервал накрая на `"LENTO "` и на `"CAIDO "`, защото тези състояния са с пет знака, а срезът взема шест.

В тест като този си струва да се запиташ дали отговаря на критерия от Урок 8: става ли червен, ако се счупи онова, което твърди, че проверява? Упражнение 2 те моли да счупиш JSON нарочно и да го провериш.

### 11.2 `logging`: онова, което програмата разказва за себе си

#### 11.2.1 Защо не `print`

Отчетът е **онова, което програмата произвежда**. Но една програма има и неща за разказване за **собствената си работа**: „прочетох 4 услуги“, „услугата `pagos` отговори за 87 ms“. Това е информация за онзи, който проучва нещо странно, не за онзи, който чете отчета. Ако тези съобщения се отпечатват с `print` до отчета, те се смесват с него: скриптът, който чете JSON, намира диагностични редове по средата и вече не може да го интерпретира.

Светът на Unix реши това преди десетилетия с два канала: **стандартният изход** (*stdout*) е за резултата на програмата, а **изходът за грешки** (*stderr*) е за всичко останало, което програмата има да каже за себе си. Вече ги ползваш: отчетът върви през първия, `error de configuración: ...` върви през втория (Урок 7). Модулът [`logging`](https://docs.python.org/3/library/logging.html) на стандартната библиотека е подреденият начин да се пише във втория канал, с едно предимство пред `print`: всяко съобщение има **ниво** на важност, а ти решаваш от кое ниво искаш да ги чуваш, без да пипаш кода, който ги пише.

#### 11.2.2 Нивата и една първа програма

Нивата, от по-малко към по-сериозно: `DEBUG` (фин детайл, за онзи, който дебъгва), `INFO` (програмата напредва), `WARNING` (нещо странно, но продължава), `ERROR` (нещо се провали) и `CRITICAL`. По подразбиране `logging` показва само от `WARNING` нагоре. **Регистраторът** (*logger*) е обектът, с който говориш, и се иска по име: `logging.getLogger("demo")`. Тази фигура показва всичко заедно:

```python
# fig11_01.py
import logging
import sys

logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
registro = logging.getLogger("demo")

print("este renglón es el reporte: va a la salida estándar", flush=True)
registro.debug("detalle fino: nadie lo ve con el nivel por omisión")
registro.warning("aviso: %s tardó %s ms", "inventario", 2300)
registro.setLevel(logging.DEBUG)
registro.debug("ahora sí aparece, porque subí el detalle")
```

```text
$ python fig11_01.py
este renglón es el reporte: va a la salida estándar
WARNING demo: aviso: inventario tardó 2300 ms
DEBUG demo: ahora sí aparece, porque subí el detalle
```

Ред по ред. `logging.basicConfig(stream=sys.stderr, format=...)` прави минималната конфигурация: съобщенията да отиват към `sys.stderr` (изхода за грешки) и с формат `NIVEL nombre: mensaje`. `registro.debug(...)` записва съобщение от ниво `DEBUG` и то не се появява, защото нивото по подразбиране е `WARNING`: това съобщение е **запазено в кода, но изключено**, и в това е хитростта. `registro.warning("aviso: %s tardó %s ms", "inventario", 2300)` се появява. Обърни внимание как е написано: съобщението носи маркери `%s`, а стойностите вървят **отделно**, като аргументи. Това е форматът с `%` на низовете, старият (`"%s" % x`), който курсът не използва никъде другаде; тук не го прилагаш ти: `logging` го прилага отвътре, като съединява съобщението и стойностите, и [документацията му](https://docs.python.org/3/howto/logging.html#logging-variable-data) го изисква така. Стойностите се подават отделно, за да сглоби `logging` текста **само ако съобщението ще бъде изведено**; с `f"..."` текстът би се сглобявал винаги, дори нивото да е изключено, а в програма, която записва хиляди редове, тази разлика се усеща. А `registro.setLevel(logging.DEBUG)` сваля нивото, с което последният `debug` вече се появява. Програмата отпечата отчета с `print(..., flush=True)`; `flush=True` само принуждава текста да излезе веднага, за да е редът на документирания изход същият като онзи, който виждаш в терминала.

Едно предупреждение за дизайна, което идва от [официалното ръководство](https://docs.python.org/3/howto/logging.html): кодът на една **библиотека** (или на модул от пакета) никога не конфигурира `logging`; само си иска регистратора и пише. Конфигурира **главната програма**, която знае накъде трябва да отиват съобщенията. Затова в `revisor` `basicConfig` живее в `cli.py`, а не в `revision.py`.

#### 11.2.3 `--verbose` в `revisor`

`revisor` записва, на ниво `DEBUG`, резултата на всяка услуга, а опцията `--verbose` го включва. `revision.py` иска регистратора `"revisor"` в началото, а функцията му `revisar` вече е обвивка: вика `_consultar` (обичайното тяло, което не се промени) и записва резултата, преди да го върне.

```python
# fig11_05/src/revisor/revision.py
import asyncio
import logging
import time

import httpx

from revisor.formato import formatear_tiempo
from revisor.modelo import Estado, Resultado, Servicio, clasificar

registro = logging.getLogger("revisor")


async def _consultar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
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


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    resultado = await _consultar(cliente, servicio)
    registro.debug(
        "%s: %s, %s, %s",
        servicio.nombre,
        resultado.estado.value,
        formatear_tiempo(resultado.tiempo_ms),
        resultado.detalle,
    )
    return resultado


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

Обърни внимание на разделението: `_consultar` прави проверката; `revisar` я прави и я **разказва**. Така журналът е на едно място, а не повторен във всеки `return`. В `cli.py` има три промени: опцията `--verbose` (с `action="store_true"`, което означава „ако се появи, е `True`; ако не, `False`“, без да чака стойност), функцията `configurar_logging` и извикването на `tabla`:

```python
# fig11_05/src/revisor/cli.py
import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import reporte_a_json, tabla
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="escribe en la salida de error el detalle de cada revisión",
    )
    return parser


def configurar_logging(verbose: bool) -> None:
    logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    nivel = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger("revisor").setLevel(nivel)


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)
    configurar_logging(argumentos.verbose)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
    if argumentos.formato == "json":
        print(reporte_a_json(resultados))
    else:
        print(tabla(resultados))

    problemas = [r for r in resultados if r.estado is not Estado.ARRIBA]
    if len(problemas) == 0:
        return 0
    return 1
```

`configurar_logging` прави три неща. `basicConfig` свързва журнала със `sys.stderr`. Редът `nivel = logging.DEBUG if verbose else logging.WARNING` е **условен израз**, `if`/`else`, който се събира в един ред и **дава стойност**: чете се „`logging.DEBUG`, ако `verbose` е истина; иначе `logging.WARNING`“, и е равностоен на `if`/`else` от четири реда, който присвоява `nivel` във всеки клон. А `logging.getLogger("revisor").setLevel(nivel)` задава нивото **само на регистратора на `revisor`**: `DEBUG`, ако са поискали `--verbose`, `WARNING`, ако не. Тази разлика има значение: ако беше задал ниво `DEBUG` на регистратора на **всички** (корена), `httpx` и библиотеката, която използва отдолу, щяха да запишат стотици собствени редове и сред тях твоето щеше да се загуби. Освен това всяка опция вече носи помощния си текст на испански (`help=...`), защото седмата проверка изисква `revisor --help` да върши работа. (Текстовете, които `argparse` слага от само себе си, като `options:` и `show this help message and exit`, излизат на английски; те са на библиотеката.)

Виж разликата с работеща лаборатория (отново, времената варират на твоята машина):

```text
$ cd fig11_05
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 854ms
```

Без `--verbose` отчетът излиза както винаги и изходът за грешки не казва нищо. С `--verbose` журналът се появява **в другия канал**. За да ги видиш поотделно, пренасочи ги към различни файлове (това е Упражнение 3): чистия отчет в единия и журнала в другия.

Един последен коментар, занаятчийски. Редът на журналните редове е редът, в който услугите *приключват*, а не този от конфигурацията: `reportes` (което се проваля веднага) излиза първо. Това е още една причина **отчетът** да не зависи от журнала: отчетът се сглобява подреден, от списъка; журналът е дневникът на онова, което е ставало. [Статията в блога за телеметрията](https://www.habil.mx/bg/blog/telemetry-prometheus-loki-tempo-grafana-opentelemetry/) разказва как в една истинска система се събират журналите на много програми като тази.

> **Тук свършва първата сесия.** Имаш крайния отчет (таблицата, която изчислява ширината си, и JSON, тестван като договор) и журнала с `--verbose`, всеки в своя канал. Преди втората сесия пусни тестовете и `revisor` със и без `--verbose`, като пренасочиш всеки канал към негов файл. Втората сесия не добавя код към `revisor`: преговаря сигурността, изгражда го и го инсталира с `pipx` и проверява една по една седемте точки от „Как разбираш, че си завършил“.

### 11.3 Преговор на сигурността: четири навика

Курсът засяваше сигурността там, където беше рискът, а не в отделна глава: да се валидира онова, което идва отвън (Урок 6), да се третира адресът на `urllib` внимателно (Урок 9). Тази част събира четирите навика, за да ги имаш наведнъж. **Не добавя код към `revisor`**: `revisor` вече прилага първия и няма никой от другите три. Обясняват се, защото ще ти трябват, щом напишеш следващата програма, и защото първият придобива нов смисъл сега, когато програмата е инструмент, който всеки може да инсталира.

#### 11.3.1 Адресът, който друг въвежда

Твоят `revisor` прави заявка към адреса, който е в `servicios.toml`. Който пише този файл, решава **къде отива твоята програма**. Ако си само ти, няма риск. Но една програма се използва повторно и утре този файл може да дойде от друг екип, от уеб страница или от форма. Урок 6 постави една защита: `validar_servicio` приема само адреси `http://` или `https://`, които минават проверките на `es_url_http` (схема, сървър, порт и обикновен текст). Не е пълна валидация и затова Урок 9 постави втора мрежа: ако `httpx` отхвърли адрес, който е минал, тази услуга излиза като „dirección inválida“ (невалиден адрес) и останалите се проверяват въпреки това. Виж какво прави първата защита с адрес, който не минава:

```text
$ python -m revisor --config raro.toml
error de configuración: servicio 1: 'url' debe ser una dirección http:// o https:// válida
$ echo $?
2
```

Файл с `url = "file:///etc/passwd"` се отхвърля, преди да се направи каквото и да е: излиза съобщението за конфигурация и кодът `2`. Без тази валидация, според инструмента, който прави заявката, `file://` би могъл да чете файлове от собствената ти машина. И има един по-тънък вариант, който валидацията на схемата не покрива: адрес `http://`, който сочи **навътре** в твоята мрежа (към вътрешна услуга или към услугата за метаданни на сървър в облака), кара *твоята* програма, която е вътре, да запитва нещо, до което авторът на адреса не би могъл да стигне отвън. Тази атака се нарича *server-side request forgery* (SSRF) и [OWASP я описва подробно](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). За `revisor`, който чете конфигурационен файл, написан от теб, рискът е нисък; за уеб услуга, която получава адреси от потребители, е централен. Правилото: **адрес, който идва отвън, е ненадеждни данни и се валидира (и се ограничава до позволено множество), преди да се използва**. Статията на Hábil в блога за [сигурността на API](https://www.habil.mx/bg/blog/api-security-cto-identity-gateway-tokens/) издига това правило до нивото на архитектурата.

#### 11.3.2 `subprocess`: списък, никога сглобен текст

Някой ден програмата ти ще поиска да изпълни друга програма от системата (`ping`, `git`, `ls`). Модулът [`subprocess`](https://docs.python.org/3/library/subprocess.html) го прави и има два начина да получи командата, с много различни последици. Тази фигура използва `echo` (който само отпечатва), за да видиш разликата без риск:

```python
# fig11_02.py
import subprocess

nombre = "catalogo; echo INYECTADO"

print("--- con shell=True y un texto armado ---", flush=True)
subprocess.run(f"echo revisando {nombre}", shell=True, check=True)

print("--- con una lista y sin shell ---", flush=True)
subprocess.run(["echo", "revisando", nombre], check=True)
```

```text
$ python fig11_02.py
--- con shell=True y un texto armado ---
revisando catalogo
INYECTADO
--- con una lista y sin shell ---
revisando catalogo; echo INYECTADO
```

И в двата случая „името“ е `catalogo; echo INYECTADO`: текст, в който някой е написал след името точка и запетая и **още една команда**. С `shell=True` Python не изпълнява програмата директно, а я подава на *командния интерпретатор* (shell, интерпретатора на терминала) като текст, за да го интерпретира, а той разбира `;` като „завърши тази команда и изпълни друга“. Резултатът: изпълниха се **две** неща, и второто го избра онзи, който написа името. Това е *инжектиране на команди*. Със **списък** (`["echo", "revisando", nombre]`) всеки елемент е аргумент, командният интерпретатор не се намесва и `;` е просто още един знак от текста. Ако командата беше `rm` вместо `echo`, разликата би била да се изтрият файловете ти. Документацията на [`subprocess` в раздела ѝ за сигурност](https://docs.python.org/3/library/subprocess.html#security-considerations) изисква точно това; [OWASP го обяснява с повече примери](https://owasp.org/www-community/attacks/Command_Injection). Правилото: **списък от аргументи и без `shell=True`; ако командният интерпретатор е нужен, текстът, който стига до него, не може да съдържа нищо, което идва отвън**. `check=True` кара команда, която се проваля, да хвърли изключение, вместо да мине безшумно.

#### 11.3.3 `eval` и `pickle`: изпълняване на онова, което идва отвън

`eval(texto)` взема текст и го **изпълнява като код на Python**. Изглежда удобно за превръщането на „2 + 2“ в 4, но трябва да се види какво приема:

```python
# fig11_03.py
texto_de_afuera = "__import__('sys').version_info.major"

print(eval(texto_de_afuera))
```

```text
$ python fig11_03.py
3
```

„Текстът отвън“ е инструкция, която импортира модул и чете версията му на Python: нищо вредно, но идентична по форма с онова, което би направила инструкция, която трие файлове или праща данните ти другаде. `eval` не различава. Всички данни, които идват отвън и минат през `eval`, дават на онзи, който ги е написал, контрол над твоята програма. За да се превърне текст в данни, има инструменти, които разбират **само** данни: `json.loads` (който използваш от 6) за JSON, `tomllib.loads` за TOML. Дори `ast.literal_eval`, „безопасната версия“ на `eval`, не е пълна защита срещу враждебен текст, както предупреждава [документацията му](https://docs.python.org/3/library/ast.html#ast.literal_eval).

`pickle` е братският случай. Това е модулът, който записва обекти на Python във файл, и [документацията му](https://docs.python.org/3/library/pickle.html) започва с предупреждение в червено: *не е сигурен*, защото разпакетирането на един `pickle` може да изпълни произволен код. Файл `pickle`, който ти праща друг човек, на практика е програма. За данни, които пресичат граници, JSON. В курса няма фигура за `pickle`, защото показването му изисква да се напише клас с методи, а това парче още не си виждал; с предупреждението стига.

#### 11.3.4 `secrets`, не `random`

Модулът `random` произвежда числа, които *изглеждат* случайни, но се изчисляват по формула от една **начална стойност** (seed): ако знаеш началната стойност, знаеш всички числа. Това е добродетел за симулация, която искаш да повториш, и бедствие за парола или токен. Виж двете неща заедно:

```python
# fig11_04.py
import random
import secrets

random.seed(1)
primero = random.random()
random.seed(1)
segundo = random.random()
print("random con la misma semilla:", primero == segundo)

token = secrets.token_hex(16)
print("secrets, largo del token:", len(token))
```

```text
$ python fig11_04.py
random con la misma semilla: True
secrets, largo del token: 32
```

С една и съща начална стойност (`random.seed(1)`) `random.random()` дава **точно същото число** два пъти: `True`. Нападател, който познае началната стойност (например часа, в който е тръгнала програмата), възпроизвежда всичките ти „тайни“. [`secrets`](https://docs.python.org/3/library/secrets.html) е направен за обратното: взема случайността си от операционната система, същата, която използва за ключовете за шифроване. `secrets.token_hex(16)` дава 16 случайни байта, записани в шестнайсетичен вид, тоест текст от 32 знака (оттам `32`). [Документацията на `random`](https://docs.python.org/3/library/random.html) го казва в първото си предупреждение: да не се използва за цели на сигурността. Правилото: **ако числото е тайна (токен, парола, идентификатор, който не трябва да може да се налучка), `secrets`; ако не, `random` е наред**.

### 11.4 Изграждане и инсталиране

#### 11.4.1 Какво е инсталируем пакет

Досега `revisor` се изпълнява с `python -m revisor` от папката на проекта и беше инсталиран във виртуалната ти среда с `pip install -e .` (**редактируемата** инсталация от Урок 7, която не копира кода, а сочи към него). Това върши работа за разработка. За да го предадеш на друг човек, трябва един **файл**, който съдържа програмата вече опакована. В Python този файл се нарича [*wheel*](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), има разширение `.whl` и вътре е компресиран архив с твоя код и данните му за инсталиране (име, версия, зависимости и коя е командата, която трябва да се създаде). Името разказва история: `revisor-1.0.0-py3-none-any.whl` означава „пакетът `revisor`, версия 1.0.0, за коя да е версия на Python 3, без компилиран код, на коя да е система“.

Версията се вдига на `1.0.0` в `pyproject.toml`; това е единственото, което се променя там:

```toml fig11_05/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "1.0.0"
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

Изгражда се с инсталатора на пакети. Една подробност: не ти трябват нито пакетът `build`, нито нещо ново; `pip` вече умее да изгради *wheel* (командата е [`pip wheel`](https://pip.pypa.io/en/stable/cli/pip_wheel/)). Опцията `--no-deps` му казва да изгради **само твоя пакет** и да не сваля зависимостите, а `-w dist` да остави резултата в папката `dist/`. Точката накрая е „изгради проекта от тази папка“. За да го сглоби, `pip` сваля за малко инструмента за изграждане, който си декларирал в `[build-system]` (`hatchling`): това е зависимост на *изграждането*, не на изпълнението, и не пътува вътре в *wheel*.

```text
$ python -m pip wheel --no-deps -w dist .
Processing /home/tu_usuario/curso-python/revisor
  Installing build dependencies: started
...
Building wheels for collected packages: revisor
  Building wheel for revisor (pyproject.toml): started
  Building wheel for revisor (pyproject.toml): finished with status 'done'
  Created wheel for revisor: filename=revisor-1.0.0-py3-none-any.whl size=6397 sha256=...
  Stored in directory: ...
Successfully built revisor
$ ls dist
revisor-1.0.0-py3-none-any.whl
$ unzip -Z1 dist/revisor-1.0.0-py3-none-any.whl
revisor/__init__.py
revisor/__main__.py
revisor/cli.py
revisor/configuracion.py
revisor/formato.py
revisor/modelo.py
revisor/revision.py
revisor-1.0.0.dist-info/METADATA
revisor-1.0.0.dist-info/WHEEL
revisor-1.0.0.dist-info/entry_points.txt
revisor-1.0.0.dist-info/RECORD
```

(Изходът на `pip wheel` е съкратен: `...` отбелязват редове, които са махнати, между тях изтеглянето на `hatchling` и дълъг отпечатък `sha256`. Размерът, `size`, зависи от твоя код, така че твоят може да е друг; важното е `Successfully built revisor`.)

Две неща за четене оттук. *Wheel* съдържа пакета `revisor` (седем файла) и папката си `dist-info` с метаданните; **не съдържа** `servicios.toml`, нито тестовете, нито файловете на лабораторията. Така е правилно: програмата не носи конфигурацията си, носи я онзи, който я използва. И версията в името на файла, `1.0.0`, излезе от `pyproject.toml`.

#### 11.4.2 `pipx`: инсталиране на инструмент, не на библиотека

Би могъл да инсталираш *wheel* с `pip install` във виртуална среда, но тогава `revisor` би съществувал само докато тази среда е активирана. За един **инструмент**, който искаш да използваш от коя да е папка, като `git` или `ruff`, решението е [`pipx`](https://pipx.pypa.io/stable/). `pipx` създава **собствена виртуална среда за всеки инструмент**, инсталира там пакета със зависимостите му и оставя командата достъпна в твоя `PATH`. Всеки инструмент остава изолиран от другите и от системния ти Python (който, спомни си от Урок 1, не бива да се пипа с `pip`).

На Linux Mint се инсталира със системния мениджър на пакети: `sudo apt install pipx` (пакетът е в хранилищата на Ubuntu 24.04, основата на Mint 22: [версия 1.4.3](https://packages.ubuntu.com/noble/pipx)), и после `pipx ensurepath`, който добавя папката с командите на `pipx` (`~/.local/bin`) към твоя `PATH`; отвори нов терминал, за да го забележи. С това инсталирането на `revisor` е един ред. Изходът отдолу е получен с по-нова версия на `pipx` и на Python от тези на твоя Mint, така че текстът може да се различава в подробности: важни са последните три реда. Махнати са редовете за подготовката на средата.

```text
$ pipx install dist/revisor-1.0.0-py3-none-any.whl
done!
  installed package revisor 1.0.0, installed using Python 3.14.8
  These apps are now available
    - revisor
```

`pipx` създаде средата, инсталира *wheel* със зависимостите му (`httpx` и неговите) и остави командата `revisor`. Да я изпробваш от **друга папка** е смисълът. Това изпълнение е от празна папка:

```text
$ revisor --version
revisor 1.0.0
$ echo $?
0
$ revisor
error de configuración: no existe el archivo servicios.toml
$ echo $?
2
$ revisor --config servicios.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      91ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
$ echo $?
1
```

Три неща. `revisor --version` работи от коя да е папка и казва `revisor 1.0.0`; помни, че този номер не е написан в кода, а `cli.py` го чете от метаданните на инсталирания пакет, които идват от `pyproject.toml`. Второ: `revisor` голо, от папка, която няма `servicios.toml`, завършва със съобщението за конфигурация и кода `2`. Това е същият урок като този от 6 (относителният път зависи от това къде си) и не е недостатък: така е правилно за един инструмент, който не бива да налучква къде е конфигурацията ти. За това съществува `--config`. И трето: с валиден `--config` отчетът излиза и кодът е `1`, защото има една услуга `LENTO` и друга `CAIDO`.

#### 11.4.3 Какво предстои и още не е за теб

Две новости на Python 3.14 остават извън курса нарочно и е добре да знаеш, че съществуват. Първата е **интерпретаторът без GIL** (*free-threaded*): вариант на Python, който може да изпълнява код на Python в няколко нишки едновременно; с 3.14 стана [официално поддържан](https://peps.python.org/pep-0779/), но остава отделна, незадължителна компилация, а много библиотеки още не са готови. За `revisor` не променя нищо, защото той вече прави едновременно чакане в една нишка и не е ограничен от GIL. Втората са ***t-strings*** (шаблонни низове, [PEP 750](https://peps.python.org/pep-0750/)): пишат се като f-string, но с `t` отпред, и вместо текст връщат обект, който отделя фиксираното от интерполираното, полезен за екраниране на HTML или за безопасно сглобяване на SQL заявки. Нито една от двете не е необходима за онова, което направи, нито една не се използва в курса (а кодът на курса трябва да работи на 3.12 от твоя Mint, който ги няма), и двете са обяснени в [списъка с новостите на 3.14](https://docs.python.org/3/whatsnew/3.14.html). Когато ти трябват, вече ще умееш да четеш тази документация сам, а това е, което курсът си постави.

## Седемте точки, една по една

Тук курсът се затваря. Всяка точка е една команда и един изход; изходът отдолу е реалният, от папката `fig11_05/` с работеща лаборатория в друг терминал.

### Точка 1 — `pytest` завършва зелено и казва колко теста са се изпълнили

Пуска се `pytest -q` и се чете **броят от отчета**, последният ред. В тази папка трябва да казва `30 passed`: 27-те от Урок 10 плюс трите от днес (договорът на JSON, таблицата с дълго име и `--version`).

Защо броят, а не кодът на изход: кодът 0 на `pytest` казва само че *не е имало провали*, а може да има 0 провала с почти никой тест, който да се изпълнява. Виж два случая, измерени. Първи: файл с един-единствен тест, маркиран да бъде пропуснат.

```text
$ pytest -q tests/test_saltada.py
s                                                                        [100%]
1 skipped in 0.00s
$ echo $?
0
```

Код 0 и `1 skipped`: нищо не се е тествало, а всичко изглежда наред. Втори: филтриране по име.

```text
$ pytest -q -k sale_con
..                                                                       [100%]
2 passed, 28 deselected in 0.02s
$ echo $?
0
```

Също с код 0, но `2 passed, 28 deselected`: от 30 теста са се изпълнили два. Който гледа само зеления цвят или кода, не го забелязва; който чете броя, да. [Справочникът с кодовете на изход на `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) ги изброява (има един специфичен, 5, за „не е събран никакъв тест“, но дори той не пази от филтър, който пропуска два). **Правило: точка 1 е изпълнена, когато четеш `30 passed` и това 30 е числото, което си очаквал.**

### Точки 2 и 6 — качеството и да работи по един и същ начин на 3.14 и на 3.12

Пускат се четирите инструмента за качество, с всяка версия на Python. Първо с 3.14:

```text
$ python --version
Python 3.14.8
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

И точно същото с 3.12, който е този на твоя Mint:

```text
$ python --version
Python 3.12.12
$ pytest -q
..............................                                           [100%]
30 passed in 0.05s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

Единствената разлика е редът с `python --version`. `ruff check` и `ruff format --check` не докладват нищо (проверяват 13 файла, лабораторията включена) и `mypy` казва `Success`. 30-те теста минават и в двете. За да повториш това на твоя Mint: системният Python (3.12) вече го имаш в обичайната си среда. Ако си инсталирал 3.14 с `uv` (рамката от Урок 7), създай втора среда с него (`python3.14 -m venv .venv314`), активирай я и инсталирай проекта и инструментите с версиите от `herramientas/requisitos.txt`, и пусни същите четири команди. Ако не си инсталирал 3.14, точка 6 се изпълнява *за версията, която имаш*, а другата половина я проверяваш ти, когато поискаш: инсталираш 3.14 с `uv` и повтаряш тези четири команди. Никой не я проверява вместо теб; изходът отгоре е от изпълнение на двете версии, а значение има твоят.

### Точка 3 — 20 услуги едновременно, за времето на най-бавната

С двайсетте услуги по половин секунда (`servicios-20.toml`), последователно и всички наведнъж:

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 504ms

real	0m10.169s
user	0m0.093s
sys	0m0.020s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 509ms

real	0m0.606s
user	0m0.083s
sys	0m0.018s
```

Последователно (`--concurrencia 1`): 10.2 секунди, сборът. С `--concurrencia 20`: 0.61, близо до най-бавната (0.5) плюс стартирането на Python. **Точка 3 е изпълнена**, защото времето не е сборът на чакането: от порядъка на най-дългото чакане е. Ако машината ти показва няколко стотни повече, няма значение; важното е да са около шестнайсет пъти по-малко.

### Точка 4 — паднала, бавна или отговаряща с боклук услуга не събаря отчета

С лабораторията вече го видя при всяко изпълнение: `reportes` е паднала, `inventario` е бавна, а другите две излизат пълни. Остава третият вид, този, който **отговаря с боклук**: нещо, което отговаря, но не с валиден HTTP. Това не може да се поиска от лабораторията, но може от един фалшив транспорт (Урок 10), който може да хвърли изключението, което `httpx` хвърля пред отговор, който не е HTTP (`httpx.RemoteProtocolError`). Тази фигура събира пет вида услуга в едно изпълнение: една здрава, една бавна, една, която отговаря с боклук, една, която връща 503, и една наистина увиснала (чака 30 секунди при времеви лимит от половин секунда).

```python
# fig11_06.py
import asyncio

import httpx
from revisor.formato import tabla
from revisor.modelo import Servicio
from revisor.revision import revisar_todos

SERVICIOS = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("lento", "https://lento.example"),
    Servicio("basura", "https://basura.example"),
    Servicio("caido", "https://caido.example"),
    Servicio("colgado", "https://colgado.example", timeout_ms=500),
    Servicio("pagos", "https://pagos.example"),
]


async def atender(peticion: httpx.Request) -> httpx.Response:
    anfitrion = peticion.url.host
    if anfitrion == "lento.example":
        await asyncio.sleep(1.1)
    if anfitrion == "colgado.example":
        await asyncio.sleep(30)
    if anfitrion == "basura.example":
        raise httpx.RemoteProtocolError("lo que llegó no es HTTP", request=peticion)
    if anfitrion == "caido.example":
        return httpx.Response(503)
    return httpx.Response(200)


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    resultados = await revisar_todos(SERVICIOS, transporte=transporte)
    print(tabla(resultados))


asyncio.run(main())
```

```text
$ python fig11_06.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA       0ms  200
lento       LENTO       1.1s  200
basura      CAIDO          —  error de red
caido       CAIDO        0ms  503
colgado     CAIDO          —  tiempo agotado
pagos       ARRIBA       0ms  200

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 275ms
```

Тази програма **импортира пакета** `revisor`: върви със средата, в която си инсталирал проекта (`pip install -e .` в папката `fig11_05/`). Шестте услуги излизат в отчета, в техния ред, всяка със своето: `lento` е `LENTO` (1.1 s), `basura` се появява като `CAIDO` с детайл `error de red`, `caido` носи своето `503`, а `colgado` се предаде с `tiempo agotado` без да чака 30-те секунди. Никоя не събори другите. И не е само работа на симулацията: ако истински сървър отговори нещо, което не е HTTP (например програма, която слуша на един порт и отговаря с произволен текст), `httpx` хвърля грешка на протокола, която е `httpx.HTTPError`, и `revisor` я докладва все пак, като `error de red`. `0ms` на `catalogo` и `pagos` са, защото фалшивият транспорт отговаря мигновено; с истинска мрежа биха били десетки или стотици. **Точка 4 е изпълнена.**

### Точка 5 — никоя заявка не чака вечно

Две проверки. Първата, в кода: на колко места се прави заявка и всички ли са защитени?

```text
$ grep -rn "cliente.get" src/revisor
src/revisor/revision.py:19:            respuesta = await cliente.get(servicio.url, timeout=limite)
```

Една-единствена заявка в целия пакет и тя е вътре в `async with asyncio.timeout(...)` и с `httpx.Timeout(...)` (видя го в `revision.py`). Втората, с изпълнение: една услуга на лабораторията, която се бави 10 секунди с `timeout_ms = 1000`, и друга, която се бави 8 секунди **без** `timeout_ms` в конфигурацията (използва стойността по подразбиране, 5000):

```text
$ time python -m revisor --config servicios-limite.toml
SERVICIO        ESTADO    TIEMPO  DETALLE
notificaciones  CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m1.127s
user	0m0.106s
sys	0m0.022s

$ time python -m revisor --config servicios-sin-limite.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
colgado     CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m5.141s
user	0m0.115s
sys	0m0.027s
```

Първата се предава на 1.1 секунди; втората, на 5.1. Никоя не чака толкова, колкото е искал сървърът. **Точка 5 е изпълнена**, и за онзи, който забрави да сложи времеви лимит в конфигурацията си, защото стойността по подразбиране на `Servicio` е 5000 ms.

### Точка 7 — инсталира се с `pipx` и се използва от друга папка

Вече го направи в 11.4: `pipx install`, `revisor --version` и `revisor --help` от коя да е папка. Остава да се провери договорът на кодовете на изход: **0, ако всичко работи, 1, ако не**. С четирите услуги на лабораторията вече видя 1. С файл, който има само `pagos`:

```text
$ revisor --config bien.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA     102ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 102ms
$ echo $?
0
```

Код 0. И `revisor --help` работи от коя да е папка и показва помощта за опциите с текста на испански, който им сложи в 11.2.3. **Точка 7 е изпълнена.**

С изпълнени седемте `revisor` е завършен в смисъла, който курсът определи в началото. Не защото е съвършен, а защото онова, което казва, че прави, **го прави и можеш да го провериш**.

## Целият проект

Файловете от папката `fig11_05/`, които не се промениха в този урок, са тук, за да е папката пълна и да може да се пусне:

<details>
<summary>Файловете, които не се променят в този урок</summary>


```toml fig11_05/servicios.toml
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
# fig11_05/laboratorio.py
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

```toml fig11_05/servicios-20.toml
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

```python
# fig11_05/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig11_05/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig11_05/src/revisor/modelo.py
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
# fig11_05/src/revisor/configuracion.py
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
# fig11_05/tests/test_modelo.py
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
# fig11_05/tests/test_configuracion.py
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

```python
# fig11_05/tests/test_revision.py
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

</details>

И `tests/test_cli.py`, който се промени: получи теста за `--version`.

```python
# fig11_05/tests/test_cli.py
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


def test_version_dice_1_0_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as salida:
        main(["--version"])
    assert salida.value.code == 0
    assert capsys.readouterr().out == "revisor 1.0.0\n"


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

Новият тест използва `capsys`, инструмент на `pytest`, брат на `tmp_path` и `monkeypatch`: събира онова, което програмата **отпечатва** по време на теста, за да може да се провери. Анотацията му, `pytest.CaptureFixture[str]`, се чете като тези за колекциите от Урок 4: `CaptureFixture` е типът на този инструмент, а `[str]` казва, че онова, което събира, е текст, както `list[str]` казва, че списъкът съдържа текстове. `main(["--version"])` отпечатва `revisor 1.0.0` и прекратява програмата със `SystemExit` (така работи `argparse` с `--version`), така че тестът го получава с `pytest.raises(SystemExit)` (което проверява, че блокът хвърля това изключение, и с `as salida` ти позволява да го разгледаш) и после чете отпечатаното с `capsys.readouterr().out`. В този тест има един капан, който е добре да познаваш: номерът `1.0.0` не идва от кода, а от **метаданните на инсталирания пакет**, така че зависи от това кога си инсталирал.

## Грешката, която ще видиш

### `AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'`

Вдигна версията в `pyproject.toml` на `1.0.0`, пусна тестовете и тестът за `--version` стана червен, като казва, че версията е старата:

```text
$ pytest -q --tb=short tests/test_cli.py
F..                                                                      [100%]
=================================== FAILURES ===================================
___________________________ test_version_dice_1_0_0 ____________________________
tests/test_cli.py:24: in test_version_dice_1_0_0
    assert capsys.readouterr().out == "revisor 1.0.0\n"
E   AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'
E     
E     - revisor 1.0.0
E     ?         ^ ^
E     + revisor 0.9.0
E     ?         ^ ^
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_version_dice_1_0_0 - AssertionError: assert 'r...
1 failed, 2 passed in 0.04s
```

Прочети го отдолу нагоре: тестът очакваше `revisor 1.0.0`, а програмата каза `revisor 0.9.0`. Но ти **вече промени** `pyproject.toml`. Откъде тогава е `0.9.0`? От метаданните на редактируемата инсталация, която направи преди: те се генерират при инсталиране, не при промяна на файла. `pyproject.toml` е рецептата; инсталацията е вече сервираното ястие. Решението е да инсталираш отново:

```text
$ pip install -e .
$ pytest -q tests/test_cli.py
...                                                                      [100%]
3 passed in 0.02s
```

Правилото: **когато промениш нещо, което инсталаторът чете (името, версията, командите), инсталирай отново**. Това не е недостатък на `pip`, а последица от това, че версията живее на едно място (`pyproject.toml`), както беше решено в Урок 7, за да не се повтаря номерът в два файла.

### `bash: revisor: command not found`

Инсталира го с `pipx`, отваряш терминал и пишеш `revisor`:

```text
bash: revisor: command not found
```

Командата не се намира, защото папката, в която `pipx` оставя командите (`~/.local/bin`), не е в твоя `PATH`, който е списъкът от папки, в които терминалът търси програмите. Поправя се с `pipx ensurepath` и **отваряне на нов терминал**: промяната се прилага само за терминалите, които се отварят след това. (Точният текст на грешката се различава от терминал на терминал; Linux Mint може да ти предложи да инсталираш пакет с това име и това не е, което искаш.)

### `error de configuración: no existe el archivo servicios.toml`

Това е от Урок 6 и се появява отново, като пуснеш `revisor` от папка без конфигурация (видя го в 11.4.2). Няма какво да се поправя в кода: подай `--config` с пътя или пусни командата от папката, в която е твоят `servicios.toml`.

## Какво се прави погрешно

**Версията да живее на две места.** Номерът в `pyproject.toml` и друг, написан на ръка в `cli.py`, накрая се различават. `revisor` го чете от инсталирания пакет. Цена: `--version`, който лъже.

**Смесване на журнала с отчета.** Отпечатване на диагностика с `print` между редовете на отчета. Цена: скриптът, който чете JSON, получава боклук и спира да работи. Отчетът отива към стандартния изход; останалото, през `logging`, към изхода за грешки.

**Конфигуриране на `logging` вътре в модул на пакета.** Ако `revision.py` викаше `basicConfig`, импортирането на модула би променило поведението на програмата, която го импортира. Цена: две конфигурации, които се бият. Конфигурира се на едно място, във входната точка.

**Задаване на `DEBUG` на регистратора на всички.** Препълва се с редове от `httpx` и твоето се губи. Нивото се вдига само на собствения регистратор.

**Използване на `f"..."` в съобщение на `logging`.** Сглобява текста, дори нивото да е изключено. Цена: хабена работа при всяко съобщение, която личи, когато са хиляди.

**Промяна на формата на JSON без предупреждение.** Преименуване на поле, замяна на `null` с `0`, пренареждане без причина. Цена: всичко, което чете този JSON, се чупи. Ако договорът се промени, вдига се главната версия и се предупреждава.

**`subprocess` с `shell=True` и текст, сглобен с данни отвън.** Цена: друг да изпълнява команди на твоята машина.

**`eval` или `pickle` с данни, които не са твои.** Цена: същата.

**`random` за тайна.** Цена: токен, който друг може да възстанови.

**Една програма да се смята за завършена, без никой да я е инсталирал така, както би я инсталирал потребител.** Работи в средата за разработка и се проваля при инсталация, защото липсва файл или зависимост. Изгражда се *wheel* и се изпробва **от друга папка**, не от кода.

**Четене само на цвета на `pytest`.** Зеленото с 2 теста от 30 е зелено. Чете се броят.

## Упражнения

### Упражнение 1 — Наистина дълго име

Напиши `servicios-largo.toml` с две услуги, които сочат към лабораторията: `catalogo` и друга на име `notificaciones-de-clientes` (26 знака). **Преди да пуснеш**, предскажи в коя колона ще започне `ESTADO` и го пусни. Провери, че таблицата е подравнена.

### Упражнение 2 — Счупи договора

В копие на `fig11_05/` преименувай във `formato.py` полето `"caido"` от обобщението на JSON на `"caidos"`. Пусни `pytest -q --tb=short`. Запиши колко теста стават червени и кой. Поправи и пусни отново. Отговори: какво би станало със скрипт, който чете `resumen.caido`, ако никой не беше имал този тест?

### Упражнение 3 — Два канала, два файла

Пусни `python -m revisor --verbose`, като пренасочиш стандартния изход към `reporte.txt`, а изхода за грешки към `registro.txt` (в командния интерпретатор `> archivo` пренасочва стандартния, а `2> archivo` този за грешки). **Преди да пуснеш**, предскажи какво ще има във всеки файл. След това виж съдържанието им.

### Упражнение 4 — Още един ред в журнала

Добави към `revisor` съобщение от ниво `DEBUG` в `main`, което казва колко услуги са прочетени от конфигурацията. Трябва да се появява с `--verbose` и да не се появява без него. Провери, че 30-те теста продължават да минават и че `ruff` и `mypy` продължават да не докладват нищо.

## Решения

### Решение 1

Най-дългото име е с 26; с двата интервала въздух ширината е 28, така че `ESTADO` започва в колона 28 (броейки от 0). Изпълнението:

```text
$ python -m revisor --config servicios-largo.toml
SERVICIO                    ESTADO    TIEMPO  DETALLE
catalogo                    ARRIBA     172ms  200
notificaciones-de-clientes  ARRIBA      94ms  200

2 servicios · 2 arriba · 0 lentos · 0 caídos · promedio 133ms
```

Думата `ESTADO` е подравнена с `ARRIBA` в двата реда, а колоната на `catalogo` е разширена също като при другата. С обичайните услуги ширината отново е 12.

### Решение 2

Червен става **един** тест, `test_el_json_es_un_contrato`; другите 29 минават:

```text
$ pytest -q --tb=short
...............F..............                                           [100%]
=================================== FAILURES ===================================
_________________________ test_el_json_es_un_contrato __________________________
tests/test_formato.py:70: in test_el_json_es_un_contrato
    assert json.loads(reporte_a_json(CANONICOS)) == esperado
E   AssertionError: assert {'servicios':...dos': 1, ...}} == {'servicios':...ido': 1, ...}}
E     
E     Omitting 1 identical items, use -vv to show
E     Differing items:
E     {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caidos': 1, ...}} != {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caido': 1, ...}}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_formato.py::test_el_json_es_un_contrato - AssertionError: a...
1 failed, 29 passed in 0.04s
```

Тестът ти казва кое поле се е променило (`'caidos': 1` срещу `'caido': 1`). Без него скрипт, който четеше `resumen.caido`, би получил несъществуващо поле (`null` или грешка, според езика на скрипта) и би продължил, в най-добрия случай, като третира „0 паднали“ като добър резултат, точно когато има паднала услуга. Това е видът грешка, която не се показва до най-лошия ден.

### Решение 3

В `registro.txt` са четирите реда `DEBUG revisor: ...` (каналът за грешки); в `reporte.txt` е таблицата с обобщението ѝ (стандартният канал). Нищо не се смесва с нищо:

```text
$ python -m revisor --verbose > reporte.txt 2> registro.txt
$ cat registro.txt
DEBUG revisor: reportes: CAIDO, —, sin conexión
DEBUG revisor: pagos: ARRIBA, 92ms, 200
DEBUG revisor: catalogo: ARRIBA, 158ms, 200
DEBUG revisor: inventario: LENTO, 2.3s, 200
$ cat reporte.txt
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
```

### Решение 4

В `cli.py`, точно преди `asyncio.run(...)`:

```python
logging.getLogger("revisor").debug("leídos %s servicios", len(servicios))
```

Модулът `logging` вече е импортиран. Резултат, измерен (новият ред излиза първи, защото се записва, преди да се запита каквото и да е):

```text
$ python -m revisor --verbose 2>&1 >/dev/null | head -n 2
DEBUG revisor: leídos 4 servicios
DEBUG revisor: reportes: CAIDO, —, sin conexión
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
```

Първата команда иска спокойно четене, защото редът на пренасочванията има значение и те се прилагат отляво надясно. `2>&1` казва „прати изхода за грешки (канал 2) там, където днес отива стандартният (канал 1)“, който в този момент е тръбата `|` към `head`. После `>/dev/null` праща **стандартния** изход в боклука. Резултат: онова, което стига до `head`, е само журналът, който излизаше през канала за грешки, а отчетът се изхвърля. А `head -n 2` показва само първите два реда от онова, което получава. Ако напишеш двете пренасочвания наобратно, `>/dev/null 2>&1`, двата изхода биха отишли в боклука и нищо нямаше да видиш.

30-те теста продължават да минават, а `ruff check`, `ruff format` и `mypy` не казват нищо.

## Как разбирам, че съм успял

- [ ] `pytest -q` във `fig11_05/` завършва с `30 passed` и това е числото, което си очаквал.
- [ ] `ruff check`, `ruff format --check` и `mypy` не докладват нищо; четирите команди дават един и същ резултат с Python 3.12 (и с 3.14, ако го имаш).
- [ ] С `servicios-20.toml` `--concurrencia 1` отнема около 10 секунди, а `--concurrencia 20`, по-малко от една.
- [ ] `fig11_06.py` показва шест услуги в техния ред, с `LENTO`, `error de red`, `503` и `tiempo agotado` в техните редове, и никоя не събаря другите.
- [ ] Услуга, която се бави 10 секунди с `timeout_ms = 1000`, се докладва като `tiempo agotado` за малко повече от секунда, а друга без `timeout_ms`, за малко повече от пет.
- [ ] `python -m pip wheel --no-deps -w dist .` произвежда `dist/revisor-1.0.0-py3-none-any.whl` и `pipx install` на този файл оставя командата `revisor`.
- [ ] От папка, която не е на проекта, `revisor --version` казва `revisor 1.0.0`, `revisor --help` показва помощта за опциите и `revisor --config servicios.toml` завършва с `echo $?` равно на `1` (има услуги `LENTO` и `CAIDO`) или на `0` (всички работят).
- [ ] Умееш да обясниш защо отчетът отива към стандартния изход, а журналът към този за грешки; защо JSON се тества като договор; и защо `subprocess` получава списък, `eval` не се използва с данни отвън и тайните идват от `secrets`.

## Обобщение

Отговори, без да поглеждаш урока:

1. Кои две неща правят JSON на `revisor` договор и кой тест го пази?
2. Как се изчислява ширината на първата колона? Защо с четирите канонични услуги таблицата излиза идентична с предишната?
3. Каква е разликата между стандартния изход и изхода за грешки? Защо отчетът отива към единия, а журналът към другия?
4. Защо едно съобщение на `logging` носи `%s` и стойностите отделно, а не f-string?
5. Защо `basicConfig` е в `cli.py`, а не в `revision.py`? Защо нивото се задава на регистратора `"revisor"`, а не на този на всички?
6. Какво става с `subprocess.run(f"echo {x}", shell=True)`, ако `x` носи `;`? А със списък?
7. Защо `random` не става за токен и какво използваш вместо него?
8. Какво съдържа една *wheel* и какво не? Защо един инструмент се инсталира с `pipx`, а не с `pip` в системния Python?
9. Защо тестът за `--version` може да стане червен, въпреки че си променил `pyproject.toml`? Как се поправя?
10. Изброй наизуст седемте проверки, с които курсът завършва, и командата на всяка.

## За допълнително четене

- [Документация на `logging` и основното ѝ ръководство](https://docs.python.org/3/howto/logging.html) — нива, регистратори и конфигурация, с правилния шаблон за библиотеки и програми. Посетено на 7 октомври 2026 г.
- [Ръководство за пакетиране на Python: писане на `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) и [`pipx`](https://pipx.pypa.io/stable/) — източникът на целия последен участък: какво влиза в `pyproject.toml`, какво е *wheel* и как се инсталират инструментите. Посетено на 7 октомври 2026 г.
- [Документация на `subprocess`: съображения за сигурност](https://docs.python.org/3/library/subprocess.html#security-considerations) и [`secrets`](https://docs.python.org/3/library/secrets.html) — двете официални предупреждения от 11.3 с техните примери. Посетено на 7 октомври 2026 г.
- [Новости в Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — интерпретаторът без GIL, *t-strings* и останалото ново, за четене, когато курсът остане назад. Посетено на 7 октомври 2026 г.
