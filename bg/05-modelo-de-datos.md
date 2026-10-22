# Урок 5 — Моделът на данните

**Време:** 90 минути

**Какво изграждаш:** модела на `revisor` (`Servicio`, `Estado`, `Resultado`) и неговия пълен отчет, с таблица и обобщение

**Какво научаваш:** шаблони за данни с `class` и `@dataclass(frozen=True)`; `Enum`; `match` и `case`, с джокер и с гардове (guards); отчета с реда на обобщението

**Откъде идваш.** Носиш проекта от [Урок 4](04-colecciones.md): два файла, `formato.py` и `revisor.py`, вече без паралелни списъци. В `revisor.py` `SERVICIOS` е списъкът с имена, които искаш да проверяваш, а `SIMULADO` е речник, който за всяко име пази кортеж `(código, tiempo_ms, error)`. Работи и вече не се разминава. Но Урок 4 завърши с три отбелязани неудобства. Кортежът не казва какво е всяка позиция: вторият елемент е времето, защото ти го помниш, а не защото кодът го казва. `clasificar` връща текст (`"ARRIBA"`, `"LENTO"`, `"CAIDO"`) и нищо не пречи да се напише `"ARIBA"`, без Python да протестира. И таблицата още няма реда на обобщението.

**Какво не прави този урок.** Не чете конфигурацията от файл (четирите услуги продължават да са написани на ръка; [Урок 6](06-errores-archivos-datos.md) ги изважда оттам), не прихваща грешки с `try` и не дефинира собствени методи в класовете. Нито пита някой интернет адрес: кодовете и времената продължават да идват от `SIMULADO`.

Работиш в папката си `~/curso-python/revisor/`, с активна виртуална среда. Малките програми са, както в Урок 4, в подпапката `practica/`.

## След урока ще можеш да

- Декларираш `Servicio` и `Resultado` като `@dataclass(frozen=True)` и `Estado` като `Enum` и да обясниш какво се печели в сравнение с кортеж, речник или отделен текст.
- Построиш инстанция с полетата по позиция или по име, да ги четеш с точка и да направиш друга с `replace`, вместо да променяш тази, която имаш.
- Класифицираш услуга с `match` и `case`, с джокер и с гардове (`case c if c >= 400`), без да паднеш в клопката с името, което улавя (captures).
- Прочетеш `FrozenInstanceError`, `ValueError` на `dataclass` със списък като стойност по подразбиране и този на `Enum`, от който се иска стойност, която няма.
- Построиш `revisor` от четири файла и да възпроизведеш неговата таблица с обобщението `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.

## Защо, преди как

Виж как днес `revisor` говори за нещата от своята задача. Една услуга е **отделно име** вътре в списък. Това, което е отговорила, е **анонимен кортеж**, `(200, 2300, None)`. А нейното състояние е **текст**, `"LENTO"`. И трите форми работят и трите имат един и същ недостатък: Python не знае какво значат. Не знае, че вторият елемент на кортежа е време, нито че `"LENTO"` е една от само три възможни стойности. За Python са кортеж и текст като всички други и затова печатна грешка (да напишеш `"ARIBA"` или да поискаш `respuesta[2]`, като искаш времето) не се проваля там, където се случва: промъква се през програмата и произвежда грешна таблица без нито едно съобщение.

Решението е да дадеш на всяко нещо от задачата **собствено име, което Python разпознава**. Една услуга вече няма да е „текст в списък“, а `Servicio`, с полета, наречени `nombre`, `url` и `timeout_ms`; едно състояние вече няма да е текст, който може да се напише погрешно, а `Estado.LENTO`, което Python разпознава или отхвърля; а това, което е излязло от проверката на една услуга, ще е `Resultado`. Тази форма, която даваме в програмата на онова, с което се занимава задачата, я наричаме тук **моделът на данните**. (Внимание, не е същото като раздела „Data model“ в документацията на Python, който говори за това как работи езикът отвътре; тук „модел“ е нашият.)

Пътят има три инструмента и едно сглобяване. `dataclass` (5.1) произвежда шаблони за данни; `Enum` (5.2) затваря списъка с позволени стойности; `match` (5.3) решава между много случаи ясно; а в 5.4 се събират в проекта, който печели и своя ред на обобщението. В края на урока `revisor` ще прави това:

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

Това е таблицата, каквато винаги, сега с празен ред и обобщение и произведена от обекти с име вместо от кортежи и отделни текстове. Обърни внимание, че заглавието и четирите реда излизат идентични с тези от уроци 3 и 4, а обобщението е новото: за да се преброи колко работят, колко са бавни и колко паднали и да се извади средното, трябват изразите за построяване от Урок 4, сега приложени върху резултати, които вече знаят какво са.

## Понятията

### 5.1 Шаблон за всяка услуга: `class` и `@dataclass`

#### 5.1.1 Защо кортежът и речникът не стигат

С това, което вече знаеш, една услуга би могла да е кортеж, `("catalogo", "https://catalogo.example", 5000)`, или речник, `{"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}`. Кортежът, както видя в Урок 4, не казва какво е всяка позиция. Речникът го казва, но има друг проблем: ключовете са текстове, които пишеш по памет, и печатната грешка не си личи там, където се случва.

<!-- frag: dict_typo.py -->
```python
servicio = {"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}
print(servicio.get("nmbre"))
```

```text
None
```

Да напишеш `"nmbre"` вместо `"nombre"` не счупи нищо: `.get` върна `None` и този `None` ще се промъква през програмата, докато нещо се провали три функции по-нататък, далече от причината. Това, което искаме, е тази печатна грешка да **се провали на самото място**, със съобщение, което я казва. Това го дава собствен тип.

#### 5.1.2 Класът като шаблон

**Класът** е шаблон за правене на стойности, които имат всички една и съща форма. Всяка стойност, направена с шаблона, се нарича **инстанция**. Помисли за формичката за сладки: формата е една, а сладките са много. В `revisor` шаблонът е `Servicio`, а `catalogo`, `inventario` и `pagos` са три инстанции. Тук ще използваш класовете само като шаблони за данни: без методи, без наследяване (с едно изключение в синтаксиса, което ще видиш в 5.2). Думата `class`, следвана от име и двоеточие, отваря шаблона, а под нея, с отстъп, се декларира **по едно поле на ред**, във формата `nombre: tipo`.

Python има инструмент, модулът `dataclasses`, който произвежда почти всичко, от което се нуждае един шаблон за данни: начина за построяване на всяка инстанция, този за показването ѝ при отпечатване и този за сравняването ѝ с `==`. Включва се с един ред точно над класа, който започва с `@` и се нарича **декоратор**: това е знак, който иска от Python да обработи класа с този инструмент, преди да го предаде. [Документацията на модула](https://docs.python.org/3/library/dataclasses.html) го описва така: декораторът добавя генерираните методи към класа, който декорира. Тук се използва като `@dataclass(frozen=True)`, където `frozen=True` (замразен) иска освен това инстанциите **да не могат да се променят**, като кортеж. Запиши това като `fig05_01.py`:

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

- `from dataclasses import dataclass` внася от модула `dataclasses` само инструмента, който ти трябва, с формата `from ... import` от Урок 3.
- Двата празни реда преди и след класа са конвенция за стил ([PEP 8](https://peps.python.org/pep-0008/#blank-lines)), не синтаксис; форматиращият инструмент, който ще видиш в Урок 8, ги изисква.
- `nombre: str` и `url: str` декларират две текстови полета. `timeout_ms: int = 5000` декларира целочислено поле със **стойност по подразбиране**: ако при построяването не я дадеш, е 5000, времевият лимит на `httpx`, който `revisor` ще използва по-нататък. Полетата със стойност по подразбиране са **накрая**, както параметрите със стойност по подразбиране на една функция.
- `Servicio("catalogo", "https://catalogo.example")` **построява** инстанция: шаблонът се вика като функция, с полетата в реда, в който са декларирани. Може да се даде и всяко поле по име, както в `notificaciones`, което освен това сменя времевия лимит на 1000. По име се чете по-добре, когато са повече от две-три полета.
- `print(catalogo)` показва `Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)`: начинът за отпечатване също е генериран от `dataclass` и затова инстанция, която отпечатваш при дебъгване, се разбира сама. С кортеж без имена би видял `('catalogo', 'https://catalogo.example', 5000)`.
- `catalogo.timeout_ms` чете поле с точка. Ако напишеш името погрешно (`catalogo.timeout`), Python се проваля на самото място с `AttributeError`, което искахме.
- `catalogo == igual` е `True`, защото `==` сравнява **поле по поле**: това са две отделни инстанции със същите данни. `catalogo is igual` е `False`, защото са два различни обекта. Това е `==` срещу `is` от Урок 3, с истински случай: `==` пита „имат ли една и съща стойност?“, `is` пита „едно и също нещо ли са?“.
- Последните два реда са, за да не се доверяваш прекалено. `Servicio(nombre=5, url=None)` **се построява, без да протестира**, макар `nombre` да трябва да е текст и `url` също. Това е, което научи в Урок 0: анотациите не се налагат при изпълнение. `dataclass` използва анотациите само за да знае какви полета има и в какъв ред: [документацията уточнява](https://docs.python.org/3/library/dataclasses.html), че, освен две изключения, които няма да използваш, нищо в декоратора не изследва анотирания тип. Който ги проверява, е отделен инструмент, `mypy`, в Урок 8.

#### 5.1.3 Замразен: за да промениш, се създава друг

Какво прави `frozen=True`? Забранява присвояването към поле. Виж какво става, ако опиташ:

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

От този *traceback* се показва само последният ред, който е важният: по средата минава през ред, който `dataclasses` генерира отвътре и който не е еднакъв в 3.12 и в 3.14. Казва „не може да се присвоява на полето `timeout_ms`“. Както с кортежа, това е гаранция, а не повреда. [Документацията](https://docs.python.org/3/library/dataclasses.html#frozen-instances) го нарича емулация на инстанции само за четене.

Защо би искал това? Защото резултатът от проверката на една услуга е **факт**: „в 10:42 `inventario` се забави 2300 ms“. Никой не бива да може да го поправя после, без да остави следа. И защото, когато в уроци 9 и 10 няколко задачи четат едни и същи услуги едновременно, това, че никоя не може да ги променя, избягва цял клас грешки. А ако наистина ти трябва друга версия на една услуга, не я редактираш: **правиш друга** с `dataclasses.replace`, която копира инстанция, като променя само полетата, които ѝ посочиш:

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

`replace` не пипна `catalogo`: върна `catalogo_corto`, нова инстанция. А последният ред показва друго предимство на неизменяемото: замразена инстанция може да се сложи в **множество** (или да е ключ на речник), защото вече не се променя: е *hashable* в смисъла на Урок 4 (4.1.4), **стига всички нейни полета да са**. Python изчислява нейния отпечатък от полетата, а тези на `Servicio` са текстове и цели числа. Две равни инстанции се броят за една: `{catalogo, repetido}` има един елемент.

Предупреждение, което се свързва с копие срещу препратка от Урок 4: `frozen` забранява повторното присвояване на **полето**, но не прави неизменяемо това, което полето съдържа. Поле, което пази списък, продължава да може да се променя отвътре (`servicio.etiquetas.append(...)`), защото списъкът продължава да е изменяем. И има втори ефект: такава инстанция вече не може да се сложи в множество, защото отпечатъкът се изчислява от всички полета, а списъкът няма отпечатък; опитът се проваля с `TypeError: unhashable type: 'list'` (в 3.14 текстът добавя `cannot use ... as a set element`). Затова в `revisor` полетата са от неизменяеми типове: текстове, цели числа, `None`.

### 5.2 `Enum`: затворен списък от стойности

Виж друг подобен проблем. `clasificar` от Урок 3 връща текста `"ARRIBA"`, `"LENTO"` или `"CAIDO"`, а който го използва, сравнява с текстове. Ако се напише един погрешно:

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

Програмата не се провали: каза, че услугата **не** работи, когато в действителност някой е написал едно R по-малко. Това е същата печатна грешка от 5.1.1, сега в стойност. Нужен е **затворен** списък от позволени стойности, с имена, които Python разпознава, и това е `Enum` (от „enumeration“, изброяване). [Модулът `enum`](https://docs.python.org/3/library/enum.html) го определя като набор от символични имена, свързани с уникални стойности.

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

- `class Estado(Enum):` отваря шаблон, както `Servicio`, но с `(Enum)` между скобите: така се казва на Python „този шаблон се основава на `Enum`“, тоест е изброим тип. Скобите след името значат „този клас тръгва от онзи друг“. В кода, който пишеш в този курс, ще ги видиш само с `Enum` и, в Урок 6, с `Exception` (лабораторията в Урок 9 също ги използва, но тази програма я пускаш, без да я пишеш); за това, което ти трябва, стига да го четеш като „клас от семейството на `Enum`“.
- Вътре има по един ред на **член**: `ARRIBA = "ARRIBA"` дава името на члена (вляво, винаги с главни букви по конвенция) и неговата **стойност** (вдясно). Тук стойността е същият текст, който се отпечатва в таблицата, без ударение и с главни букви, което е и начинът, по който ще го пази JSON-ът в Урок 6.
- `Estado.LENTO` е член. `print` го показва с името на класа отпред: `Estado.LENTO`. `.name` е неговото име (`LENTO`) и `.value` неговата стойност (`LENTO`). Когато отчетът иска думата за таблицата, използва `.value`.
- `Estado("CAIDO")` върви в обратна посока: търси члена, чиято **стойност** е този текст. Ако няма такъв, се проваля веднага (ще го видиш след малко).
- `estado is Estado.LENTO` е `True`: [членовете се сравняват по идентичност](https://docs.python.org/3/howto/enum.html#comparisons) и всеки член съществува само веднъж. А `estado == "LENTO"` е **`False`**: членът `Estado.LENTO` и текстът `"LENTO"` са различни неща, макар да се отпечатват почти еднакво. Това изненадва почти всички първия път. Сравнява се винаги с членове (`estado == Estado.LENTO`), никога с текста.
- `for posible in Estado:` обхожда членовете в реда, в който са декларирани.

Сега печатната грешка, в двата ѝ варианта. Да напишеш `Estado.ARIBA` се проваля мигновено, на точното място на грешката:

<!-- frag: enum_typo.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


print(Estado.ARIBA)
```

Последният ред на *traceback* е:

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

Python дори отгатва какво си искал да напишеш. Важното е, че грешката се случва на реда на грешката, а не три функции по-късно. И търсене по стойност на текст, който не съществува:

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

`ValueError: 'ROTO' is not a valid Estado`. Двете грешки казват едно и също с различни думи: „този член не съществува“. Забележи, че са точно онзи вид повреда, който искахме: рано, ясно и с името на виновника.

### 5.3 `match` и `case`: решаване между много случаи

Урок 2 те научи на `if`/`elif`/`else`. Когато клоновете са много и всички питат за **същата стойност**, дълга верига от `elif` става трудна за четене и за това Python носи, от версия 3.10, инструкцията `match`. Много е мощна ([официалната документация](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement) ѝ посвещава цял раздел, а [PEP 636](https://peps.python.org/pep-0636/) е учебно ръководство), но тук ще използваш само най-простата ѝ част. Виж първо функция, която описва код на състояние и която още не е тази на `revisor`:

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

Как се чете:

- `match codigo:` казва „ще сравнявам тази стойност“ (**субектът**). Всеки `case` отдолу е **шаблон**, с който Python я изпробва, **отгоре надолу**, и се задържа на **първия, който пасне**: изпълнява неговия блок и не поглежда другите. Затова редът има значение.
- `case None`, `case 200`, `case 404` са **литерални** шаблони: пасват, ако субектът е това. Първият пита за `None` по идентичност, както те научиха в Урок 2, а останалите по равенство.
- `case 301 | 302` е **единият или другият**: вертикалната черта значи „или“. Пасва с който и да е от двата кода.
- `case c if c >= 500` е този, който заслужава внимание. Първо `c` е шаблон за **улавяне** (capture): отделно име пасва с *всичко* и, между другото, запазва субекта в тази променлива, така че вътре в блока `c` е кодът. После `if c >= 500` е **гард** (guard): допълнително условие, което трябва да е изпълнено, за да важи случаят. Ако не е изпълнено, Python продължава със следващия `case`. [Документацията](https://docs.python.org/3/reference/compound_stmts.html#guards) го описва така: ако шаблонът не пасне, гардът дори не се оценява; ако пасне, гардът се оценява и случаят се избира само ако той е верен. Затова 418 минава покрай случая за 500 (по-малко е) и пада в следващия, `c >= 400`.
- `case _:` е **джокерът**: долната черта пасва с всичко и не запазва нищо. Стои накрая и събира това, което никой предишен случай не е уловил (тук, 100).

Пълната класификация на услугите на `revisor` са четири правила, които вече познаваш от Урок 2: без код е паднала; код 400 или повече е паднала; ако е отговорила и се е забавила 1000 ms или повече е бавна; иначе работи. Пише се със същия шаблон и връща членове на `Estado` вместо текстове. Това ще остане в `modelo.py`:

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

Чети я отгоре надолу, както го прави Python. Първият `case` улавя „без код“, а вторият, със своя гард, улавя „код 400 или повече“: първите две правила, и двете дават `CAIDO`. Това, което стига до `case _`, вече знаем, че е отговорило добре (има код и е под 400), и там остава само да се реши между другите две правила с `if` от Урок 2: ако времето съществува и е поне прагът, `LENTO`; иначе, `ARRIBA`. Да провериш `tiempo_ms is not None`, преди да сравниш, е необходимо, защото код може да съществува без време, а сравнението `None >= 1000` се проваля с `TypeError`. Забележи и че редът на случаите **е** логиката: ако сложиш случая за 400 преди този за `None`, `None >= 400` би се провалило. В проекта от 5.4 функцията живее в `modelo.py`, до класовете, които дефинира в 5.1 и 5.2.

Сега най-известната клопка на `match`. В един шаблон **отделно име не сравнява, а улавя**. Ако искаш да сравниш с константа, не стига да напишеш нейното име:

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

Тази програма **дори не стартира**: Python я отхвърля при четенето ѝ, със `SyntaxError`. `case LIMITE:` не пита „кодът 400 ли е?“; казва „всичко пасва и го запази в променлива, наречена `LIMITE`“. Тъй като пасва с всичко, `case _` отдолу никога не би бил достигнат и затова съобщението казва `name capture 'LIMITE' makes remaining patterns unreachable` („улавянето на името прави недостижими останалите шаблони“). Python предупреждава само защото след `case LIMITE:` има друг случай. Ако `case LIMITE:` беше последният, нямаше да предупреди за нищо: [документацията](https://docs.python.org/3/reference/compound_stmts.html#irrefutable-case-blocks) допуска случай, който пасва винаги (нарича го неопровержим), стига да е накрая, и програмата би работила с джокер, преоблечен като константа, връщайки `True` за всеки код. Можеш да го провериш: с `case LIMITE:` накрая `es_error(5)` връща `True`. Практическото правило: за да сравниш с константа, се използва име **с точка**, като `Estado.CAIDO`; точката казва на Python, че е стойност, а не ново име, и [ги нарича шаблони за стойност](https://docs.python.org/3/reference/compound_stmts.html#value-patterns).

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

Тук `Estado.ARRIBA` носи точка, така че сравнява. Това е най-естественото използване на `match` заедно с `Enum`: един случай на член, без джокер. И носи предимство, което `mypy` използва в Урок 8: ако един ден добавиш нов член към `Estado` и забравиш неговия `case`, средството за проверка на типове го посочва.

### 5.4 Сглобяване на `revisor`

Събери всичко в проекта. Накрая ще имаш четири файла в `~/curso-python/revisor/`: `modelo.py` (нов), `revision.py` (нов), `formato.py` (променя се) и `revisor.py` (променя се). Всеки файл има причина да съществува: `modelo.py` казва **какви неща има** (услугата, състоянието, резултатът) и как се класифицират; `revision.py` **проверява** една услуга; `formato.py` **дава текстова форма** на един резултат, а `revisor.py` е входната точка, която ги събира.

Първият е моделът:

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

Четирите части, една по една.

**`modelo.py`.** Събира всичко от разделите 5.1 до 5.3. Константите и класовете са отгоре, защото `clasificar` ги използва. `Resultado` е втори шаблон, който вече не пази отделни текстове: пази **една `Servicio`** (тази, която е проверена), **едно `Estado`**, времето (`int | None`, защото паднала услуга няма) и детайла. Забележи композицията: един шаблон може да има полета, чийто тип е друг шаблон. `clasificar` е тази, която написа в 5.3, само че списъкът с параметри е разпределен на редове, защото редът с `def` не се побира в 88-те знака, които изисква стилът (запетаята накрая на списъка с параметри е част от този начин за подреждане). А `nombres_repetidos` е тази от Урок 4 (4.1.5), само че сега получава списък от `Servicio` и гледа полето `servicio.nombre`.

**`revision.py`.** Нов модул е, но съдържанието му не е ново: `SIMULADO` е речникът от Урок 4, който напуска `revisor.py` и се мести тук, със същия кортеж от три `(código, tiempo_ms, error)` за всяко име. `revisar` отново сменя сигнатурата си: сега получава `Servicio` и връща `Resultado`, вместо да получава име и да връща вече съставен ред. Вътре е това, което вече познаваш: търси с `.get` (име, което го няма в `SIMULADO`, е услуга без данни и излиза паднала „sin conexión“), разопакова кортежа в три имена, решава `detalle` със същото правило (кодът като текст, ако е имало отговор, а иначе текстът на грешката), класифицира и връща `Resultado`. Това, че `revisar` вече не съставя реда, е разделението, което търсехме: да проверяваш е едно, да показваш е друго, и всяко живее в своя модул. `revisar_todos` е израз за построяване: списък от `Resultado`, по един на услуга, в същия ред. Когато в Урок 9 програмата пита истински, `SIMULADO` изчезва, а `revisar` продължава да връща същото.

**`formato.py`.** `formatear_tiempo` и `encabezado` остават както в уроци 3 и 4. (Ако си ги написал по друг начин, но изходът е бил същият, остави ги както са.) Това, което се променя, е `linea`, която **сменя сигнатурата си**: преди получаваше четири отделни стойности, а сега получава един-единствен `Resultado` и вади от него каквото ѝ трябва. Това е, което търсехме: вече не трябва да подаваш четири неща в правилния ред. Двете нови функции са `contar` и `resumen`. `contar` добавя „s“, когато количеството не е едно: `contar(1, "caído")` дава `1 caído`, а `contar(3, "caído")` дава `3 caídos`. `resumen` брои общото с `len`, използва три израза за построяване, за да преброи колко има от всяко състояние, с четвърти вади времената на отговорилите, изчислява средното **само ако има някое** (с `len(tiempos_ms) > 0`, защото деленето на нула би се провалило) и събира частите с `" · ".join(partes)`. Анотацията `promedio_ms: int | None = None` казва, че започва без стойност и може да се окаже цяло число; ако никоя услуга не е отговорила, обобщението казва `promedio —`.

**`revisor.py`.** `SERVICIOS` престава да бъде списък от имена и става **списък от `Servicio`**: четирите канонични, написани на ръка, всяка със своето име и своя адрес (времевият лимит остава в стойността по подразбиране). За да добавиш услуга, пишеш `Servicio(...)` и, докато данните са симулирани, нейния ред в `SIMULADO`, както в Урок 4. `main` проверява всички, отпечатва заглавието, ред за всеки резултат, празен ред (този, който `print()` без аргументи пише) и обобщението. `from ... import` работят, защото четирите файла са в същата папка, както в Урок 3.

Пусни проекта от неговата папка:

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

Това е таблицата от уроци 3 и 4, с празен ред и обобщение. Ако колоните не ти излизат подравнени, виновникът почти винаги е излишен или липсващ интервал в една от f-strings; провери дали са идентични с тези от текста. А ако обобщението брои погрешно, сравни всеки израз за построяване с този от урока: трите, които броят състояния, сменят само члена на `Estado`.

С това `revisor` вече има свой **модел**: `Servicio`, която се проверява, `Estado`, в което остава, и `Resultado`, който свързва двете неща с измереното. Но има нещо, което продължава да е неудобно, и ще го усетиш в упражнение 1: списъкът с услуги е **вътре в кода**. За да провериш друга услуга, трябва да отвориш `revisor.py` и да редактираш. [Урок 6](06-errores-archivos-datos.md) го изважда в конфигурационен файл и с него идват грешките, които заслужават собствен урок.

## Грешката, която ще видиш

В предишните раздели вече предизвика няколко грешки на мястото, където се раждат (`FrozenInstanceError`, `AttributeError`, `ValueError`, `SyntaxError`). Ето онази, която най-често ще срещаш, като пишеш шаблони с `dataclass`, а накрая една таблица, за да ги разпознаеш всичките с един поглед.

### `ValueError: mutable default <class 'list'> for field ... is not allowed`

Това е същият проблем с изменяемия аргумент по подразбиране от Урок 3, сега в поле на `dataclass`. Ако му сложиш списък като стойност по подразбиране:

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

Последният ред казва: „изменяема стойност по подразбиране (`list`) за полето `etiquetas` не е позволена: използвай `default_factory`“. (Тук също се показва само последният ред: между него и твоя файл *traceback* минава през вътрешни редове на `dataclasses.py`, които се променят между версиите на Python и не ти помагат да прочетеш грешката. Важното е типът, `ValueError`, и съобщението, което освен това ти казва как да го поправиш.) Python те пази от нещо, което в обикновена функция ставаше мълчаливо: един-единствен списък, споделен от всички инстанции. Решението е **фабрика**: вместо „този списък“ казваш „викай `list` всеки път, когато трябва нов“.

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

Всяка инстанция има собствен списък и затова `pagos` не разбра за етикета на `catalogo`. Между другото се вижда това, за което беше предупредено в 5.1.3: инстанцията е замразена и въпреки това `catalogo.etiquetas.append(...)` проработи, защото `frozen` пречи на повторното присвояване на полето, не на промяната на списъка, който съдържа. Затова в `revisor` не се използват списъци като полета.

### Грешките на този урок с един поглед

Когато ти се появи една, потърси тук последния ред. Всички излязоха от изпълненията на този урок.

| Последният ред казва... | Какво е станало | Къде го видя |
|---|---|---|
| `dataclasses.FrozenInstanceError: cannot assign to field '...'` | опитал си да присвоиш на поле на замразена инстанция | 5.1.3 |
| `ValueError: mutable default ... use default_factory` | сложил си списък като стойност по подразбиране на поле | горе |
| `AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?` | поискал си член на `Enum`, който не съществува | 5.2 |
| `ValueError: 'ROTO' is not a valid Estado` | потърсил си по стойност член, който не съществува | 5.2 |
| `SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable` | написал си отделно име, където си искал да сравниш | 5.3 |

## Какво се прави погрешно

Всяка от тези небрежности има конкретна цена и повечето не дават грешка от първия път.

**Да пазиш запис в речник или в кортеж, когато вече имаш шаблон.** Кортеж от шест елемента те принуждава да помниш кой е кой; речник с текстови ключове превръща печатните грешки в далечни `None`. Ако данните имат фиксирана форма, тази форма заслужава име: `@dataclass`.

**Да вярваш, че `dataclass` валидира полетата си.** `Servicio(nombre=5, url=None)` се построява, без да протестира (5.1.2): анотациите казват какво очакваш, но не го проверяват при изпълнение. Цената е лоша стойност, която пътува през цялата програма, докато се провали далече. Това, което идва отвън, се валидира при влизането и това е Урок 6.

**Да оставиш отделни текстове там, където вече има `Enum`.** Това е най-коварното. Ако промениш `clasificar`, за да връща `Estado.LENTO`, но на друго място в програмата остане `if estado == "LENTO"`, това сравнение **никога няма да е вярно** (5.2: един член не е равен на своя текст) и програмата ще продължи да работи, без да предупреди. Когато мигрираш от текстове към `Enum`, намери всички места, които сравняват.

**Да напишеш `case NOMBRE:`, искайки да сравниш.** Улавя, не сравнява. Ако искаш да сравниш с константа, използвай име с точка (`Estado.CAIDO`) или гард (`case c if c == LIMITE`).

**Да слагаш изменяема колекция като поле на замразен шаблон.** `frozen` пази полето, не това, което полето съдържа: списък, запазен в замразена инстанция, може да продължи да се променя отвътре (`fig05_08.py`). Цената е гаранция, която изглежда, че съществува, и не съществува. В `revisor` полетата са текстове, цели числа, `None` и други замразени шаблони.

**Да построяваш инстанции по позиция, когато полетата са много.** `Servicio("notificaciones", "https://notificaciones.example", 1000)` се чете; с шест полета никой не знае кое е четвъртото. С повече от две-три, по име: `Servicio(nombre=..., url=..., timeout_ms=...)`.

## Упражнения

Опитай всяко, преди да погледнеш решенията.

### Упражнение 1 — Още две услуги и средно само на тези, които работят

(а) Добави двете допълнителни услуги на `revisor` към версията от 5.4: `facturacion` (отговаря с код 503 за 95 ms) и `notificaciones` (с времеви лимит 1000 ms, не получава отговор: „tiempo agotado“). Трябва да пипнеш **две** места. Преди да пуснеш, предвиди последните два реда на изхода: този на реда на `notificaciones` и обобщението. (б) Добави накрая на `main` ред, който отпечатва средното на времената само на услугите `ARRIBA`, без закръгляне. Удобно е да го направиш с израз за построяване.

### Упражнение 2 — Предизвикай четири грешки и ги прочети

Отвори REPL с `python` от папката на `revisor`, внеси от `modelo` каквото ти трябва и предизвикай тези четири грешки, една по една: (а) присвояване на `timeout_ms` на инстанция на `Servicio`; (б) `Estado("ROTO")`; (в) `Estado.ARIBA`; (г) във файл в папката ти `practica/`, `dataclass` с поле `etiquetas: list[str] = []`. За всяка запиши в дневника си **последния ред** и, със свои думи, какво значи и как се поправя.

### Упражнение 3 — Код без време

Какво връща `clasificar(200, None)`, тоест услуга, която е отговорила с 200, но за която няма измерено време? Предвиди го два пъти: с `clasificar` от Урок 3 (тази, която връща текстове) и с днешната (тази с `match`). После го провери от папката на `revisor`, с `from modelo import clasificar`. Защо правилото дава този резултат, а не `LENTO`? И накрая: какво би станало, ако махнеш от условието частта `tiempo_ms is not None`?

## Решения

### Решение 1

(а) В `revision.py` `SIMULADO` печели два реда:

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

А в `revisor.py` `SERVICIOS` печели две услуги:

```python
    Servicio("reportes", "https://reportes.example"),
    Servicio("facturacion", "https://facturacion.example"),
    Servicio("notificaciones", "https://notificaciones.example", timeout_ms=1000),
]
```

Пълният изход:

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

Обобщението е `6 servicios · 2 arriba · 1 lento · 3 caídos`, а средното излиза 656 ms, защото го изчисляват **четирите, които са имали време** (142, 2300, 87 и 95, които правят 2624, разделени на 4). Забележи, че `facturacion` се брои в средното, макар да е паднала: отговорила е, с 503 и 95 ms. `notificaciones` няма време и не се брои. Забележи и реда на `notificaciones`: това е същото преливане, което видя в Урок 4, с името, залепено за състоянието, защото има 14 букви, а колоната е 12; Урок 11 го решава, като изчислява ширината от най-дългото име. И третото наблюдение е това, което дава повод за следващия урок: за да провериш още две услуги, трябваше да **редактираш кода**, в два файла.

(б) Внася се `Estado` и се добавя изразът за построяване накрая на `main`:

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

Последният ред на изхода е:

```text
114.5
```

(142 и 87 правят 229, разделени на 2 са 114.5.) Условието `r.tiempo_ms is not None` не е украшение. Услуга `ARRIBA` може да няма време: `clasificar(200, None)` връща `Estado.ARRIBA`, защото без измерено време няма доказателство за бавност. Ако този `None` стигне до `sum`, програмата ще се провали с `TypeError`. А освен това `tiempo_ms` е анотирано като `int | None` и който чете кода (или `mypy`, в Урок 8), трябва да види, че `None` вече е отхвърлен, преди да се събира.

### Решение 2

Последните четири реда, всеки измерен:

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

`FrozenInstanceError`: инстанцията е замразена. Поправка: да не се присвоява; да се направи друга с `replace(servicio, timeout_ms=...)`.

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError`: не съществува член на `Estado` със стойност `ROTO`. Поправка: да се използва една от трите позволени стойности или направо `Estado.CAIDO`, което дори не минава през текста.

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

`AttributeError`: `Estado` няма член, наречен `ARIBA`, и Python подсказва този, който прилича. Поправка: този, който подсказва. Това е печатната грешка, която `Enum` дойде да улови, и я улавя на реда, където се случва.

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

`ValueError` при **дефинирането** на класа, преди да е създадена никаква инстанция. Поправка: `etiquetas: list[str] = field(default_factory=list)`, както във `fig05_08.py`.

### Решение 3

И двете версии връщат **ARRIBA**: тази от Урок 3, текста `"ARRIBA"`; днешната, `Estado.ARRIBA`. От папката на `revisor`:

<!-- frag: codigo_sin_tiempo.py -->
```python
from modelo import clasificar

print(clasificar(200, None))
```

```text
Estado.ARRIBA
```

Причината е в третото правило, което е същото от Урок 2: една услуга е `LENTO`, ако **е отговорила и се е забавила** 1000 ms или повече. С `None` няма измерено време, така че няма доказателство за бавност, а единственото, което се знае, е, че е отговорила с добър код: `ARRIBA`. Двете версии третират случая еднакво, защото и двете питат `tiempo_ms is not None`, преди да сравнят. В `revisor` този случай не се среща (услуга, която е отговорила, винаги носи своето време), но `tiempo_ms` е анотирано като `int | None` и функцията трябва да даде отговор за всичко, което нейната сигнатура допуска.

Ако махнеш `tiempo_ms is not None`, сравнението `None >= 1000` би стигнало да се оцени и програмата щеше да спре с:

```text
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

Това е същата грешка от Урок 2, когато въпросите бяха в лош ред.

## Как разбирам, че съм успял

- [ ] В `~/curso-python/revisor/` `python revisor.py` отпечатва седем реда (заглавието, четири реда, празен ред и обобщението), а последният е `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] С двете допълнителни услуги от упражнение 1 последният ред е `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`, а редът на `notificaciones` излиза с името, залепено за състоянието (и знаеш защо).
- [ ] В REPL присвояването на `timeout_ms` на `Servicio` се проваля с `dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'`, а `Estado("ROTO")` се проваля с `ValueError: 'ROTO' is not a valid Estado`.
- [ ] Можеш да напишеш по памет `clasificar` с `match`: без код е `CAIDO`, код 400 или повече е `CAIDO`, време 1000 или повече е `LENTO`, а останалото е `ARRIBA`.
- [ ] Можеш да обясниш със свои думи разликата между `==` и `is` за две равни `Servicio`, защо `Estado.LENTO == "LENTO"` е `False` и какво прави `replace`.
- [ ] Записа в [дневника](bitacora.md) какво ти костваше най-много: това, което запишеш там, е онова, което трябва да повториш.

## Обобщение

Отговори, без да гледаш урока:

1. Какво е клас и какво е инстанция? Какво добавя `@dataclass` към един клас и какво добавя `frozen=True`?
2. Какво се печели с `@dataclass(frozen=True)` в сравнение с речник или кортеж? Какво прави `replace`?
3. Какво сравнява `==` между две `Servicio` и какво сравнява `is`?
4. Защо `Estado.LENTO == "LENTO"` дава `False` и как се получава текстът на един член?
5. В какъв ред изпробва `match` своите случаи и какво прави джокерът `case _`?
6. В един `match`, какво прави отделно име като `case LIMITE:`? Как се сравнява с константа?
7. Защо `linea` смени сигнатурата си в този урок и какво спечели от промяната?

## За допълнително четене

- [Python, „dataclasses“](https://docs.python.org/3/library/dataclasses.html) — пълният справочник на модула: `frozen`, `field`, `replace` и всичко, което този урок не използва. На английски, като почти цялата официална документация. Посетено на 7 октомври 2026 г.
- [PEP 557, „Data Classes“](https://peps.python.org/pep-0557/) — документът, който предложи `dataclass` и обяснява за какви случаи е измислен и за какви не. Посетено на 7 октомври 2026 г.
- [Python, „Enum HOWTO“](https://docs.python.org/3/howto/enum.html) — официалното ръководство за изброимите типове, от основите до производните типове. Посетено на 7 октомври 2026 г.
- [PEP 636, „Structural Pattern Matching: Tutorial“](https://peps.python.org/pep-0636/) — официалното учебно ръководство за `match`, който стига доста по-далече от този урок. Посетено на 7 октомври 2026 г.
