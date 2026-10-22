# Урок 10 — Съвместно изпълнение с ограничения и тестове без мрежа

**Време:** 2 × 90 минути (първата сесия стига до края на 10.2; втората започва от 10.3)

**Какво изграждаш:** `revisor`, който работи едновременно и е покрит с тестове, версия 0.9.0

**Какво научаваш:** `asyncio.TaskGroup`; `asyncio.timeout()` и `asyncio.Semaphore`; групи от изключения (`ExceptionGroup`, `except*`) и защо една грешка не събаря отчета; тестове без мрежа с `httpx.MockTransport` и `monkeypatch`

**Откъде идваш.** Носиш пакета от [Урок 9](09-http-y-asyncio.md): `revisor` вече пита наистина, с `httpx`, с времеви лимит за всяка услуга и с функция `revisar`, която никога не оставя мрежова грешка да излезе навън. Но го прави **един след друг**: `for` и `await`, по една услуга наведнъж. С четирите услуги на лабораторията изпълнението отнема сбора от чакането, около 2.5 секунди, а с двайсет услуги по половин секунда би отнело десет. Освен това има дълг, който предишният урок каза открито: неговите 21 теста не докосват нищо от новото, защото още не умееш да тестваш код, който използва мрежата. Днес се плащат и двете неща. Работиш в папката си `~/curso-python/revisor/`, с активирана виртуална среда, и трябва да имаш под ръка `laboratorio.py` от урок 9 за частта с измерването.

**Какво не прави този урок.** Не променя това, което `revisor` отпечатва: таблицата и JSON излизат същите като в Урок 9. Променя се **колко време отнема** и **колко е сигурен**. Не използва и нишки или процеси: цялото съвместно изпълнение днес става в една нишка, което е подходящо, когато се чака мрежата. Крайният отчет с изчислена ширина на колоните, журналът на събитията (`logging`) и инсталирането като команда са в [Урок 11](11-el-programa-terminado.md).

## След урока ще можеш да

- Пускаш няколко заявки едновременно с `asyncio.TaskGroup`, събираш резултатите им в реда на конфигурацията и измерваш с часовника, че общото време се доближава до най-бавната услуга, а не до сбора.
- Обясняваш защо задачата отстъпва реда само при `await` и защо `time.sleep` в корутина унищожава цялата печалба.
- Поставяш таван на времето на цяла операция с `asyncio.timeout()` и казваш с какво се различава от времевите лимити на `httpx`.
- Ограничаваш колко заявки вървят едновременно с `asyncio.Semaphore` и обясняваш защо при 20 услуги и ограничение 10 времето е двойно спрямо ограничение 20.
- Четеш `ExceptionGroup` и прихващаш съдържанието му с `except*`; казваш защо `revisar` превръща мрежовите грешки в резултати и защо **не** превръща програмните грешки.
- Тестваш `revisar` и `revisar_todos` без да докосваш мрежата, с `httpx.MockTransport`, и тестваш `main`, като подменяш една функция с друга чрез `monkeypatch`.
- Проверяваш тест в червено (чупиш кода, гледаш го как се проваля, оправяш го) и четеш броя в отчета на `pytest`.

## Защо, преди как

Представи си, че `revisor` се ползва от дежурния екип на една фирма, за да проверява шейсет услуги на всеки пет минути. Всяка здрава услуга отговаря за половин секунда; падналите се предават чак при своя времеви лимит, да кажем пет секунди. Един след друг, в най-добрия ден изпълнението отнема трийсет секунди, а в най-лошия, с десет паднали услуги, седемдесет и пет (петдесет здрави по половин секунда, плюс десет паднали по пет секунди). Но компютърът не е работил през тези седемдесет и пет секунди: той е **чакал**. Изпратил е заявка, гледал е стената, докато дойде отговорът, и едва тогава е изпратил следващата. Мрежата не изисква програмата да стои на опашка: шейсетте заявки могат да пътуват едновременно, а програмата само трябва да прибира отговорите, щом пристигнат.

Това е нещото, което `asyncio` прави добре, и затова съществува този урок. Но зад „направи всичко едновременно“ се крият три проблема и всеки е понятие за днес.

Първият е **как се пускат и как се събират** много заявки, без да се изгуби нито една. Python 3.11 донесе инструмент, създаден точно за това, `asyncio.TaskGroup`, който стартира задачите, изчаква всичките, преди да продължи, и не позволява нито една да се загуби по пътя.

Вторият е **докъде**. „Всичко едновременно“ при шейсет услуги е разумно. При шест хиляди може да се окаже нападение над собствените ти сървъри или твоята операционна система да каже, че повече връзки не ти дава. Трябва ограничение колко заявки вървят едновременно и таван на времето, за да не остане нито една да виси завинаги.

Третият е **какво става, когато нещо се провали**. Един след друг, грешката спира програмата точно там, където е настъпила, и е лесна за разбиране. При много задачи едновременно един провал може да засегне останалите, а това, което Python ти предава, не е изключение, а **група** от тях. Ако не го разбираш, една-единствена паднала услуга може да събори целия отчет, което е точно обратното на това, което `revisor` обещава.

А под всичко това е четвъртият проблем, този на доверието: програма, която върши толкова неща едновременно, със смесени времена и провали, **не може да се тества на ръка** по повторяем начин. Ако за да провериш, че „увиснала услуга не събаря отчета“, трябва наистина да закачиш една услуга, никога няма да го провериш два пъти по един и същи начин. Четвъртата част на урока учи как да тестваш всичко това без мрежа: с фалшив сървър, който отговаря каквото ти кажеш, мигновено, винаги по един и същи начин.

## Понятията

### 10.1 `TaskGroup`: всички едновременно

#### 10.1.1 Колко струва да чакаш един след друг

Преди да поправиш нещо, трябва да го измериш. Тази първа програма не използва мрежата: всяка „услуга“ е истинско чакане, направено с `asyncio.sleep`, което е начинът да кажеш „не прави нищо през това време, но ми позволи да върша друго междувременно“. Чаканията са на четири измислени услуги, от десета до половин секунда, за да са изпълненията кратки.

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

Прочети `main` отгоре надолу. `time.perf_counter()` е часовникът за измерване на интервали, който вече използва в Урок 9: вика се в началото и в края, а разликата е изминалото време. `for` обхожда речника с `.items()` (който ти дава всяка двойка име-чакане) и за всяка прави `await consultar(...)`. `await` казва „чакай тук, докато тази корутина свърши“; докато не свърши, `for` не преминава към следващата итерация. Затова отговорите излизат в реда, в който са поискани, и затова общото време, 1.1 секунди, е точният сбор: 0.3 плюс 0.5 плюс 0.1 плюс 0.2.

Това е същият проблем, който измери в Урок 9 с `revisor`: `await` върху **една-единствена корутина** изчаква тя да свърши, преди да продължи. Не е недостатък на `await`; това е значението му. За да се случат две чакания едновременно, трябва двете да **съществуват** едновременно, а за това служи задачата.

#### 10.1.2 Една задача: корутина, която вече е в движение

**Корутината** е рецепта: `consultar("catalogo", 0.3)` не прави нищо, само създава обекта-рецепта, а рецептата започва да се изпълнява, когато някой ѝ направи `await`. **Задачата** (*task*) е корутина, на която вече е навит часовникът: цикълът на събитията я е записал в списъка си с чакащи и я изпълнява, щом може, **без още никой да я чака**. **Цикълът на събитията** (*event loop*) е частта от `asyncio`, която води този списък: взема една задача, изпълнява я, докато се натъкне на `await`, който трябва да чака, поставя я на пауза, взема следващата и така нататък, в една нишка (thread).

С това в ръка, версията „едновременно“:

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

Променено е само едно нещо: вместо `await consultar(...)` вътре във `for`, се прави `grupo.create_task(consultar(...))`. Това **не чака**: регистрира задачата и се връща веднага, с обект `Task` в ръка. Затова `for` (тук, вътре в израз за построяване на списък, който е `for` на един ред от Урок 4) минава през четирите услуги за миг и оставя четири чакащи задачи. Виж изхода: четирите „empieza“ (започва) излизат първи, един след друг, преди някоя да е отговорила. После отговарят по ред на **бързина**, не на заявяване: `pagos` (0.1 s), `reportes` (0.2 s), `catalogo` (0.3 s), `inventario` (0.5 s). И общото време вече не е 1.1, а 0.5: това на най-бавната.

А `async with asyncio.TaskGroup() as grupo:`? Именно то прави всичко това безопасно. Действа като `with` от Урок 6: при **излизане** от блока групата **изчаква всички задачи, които е създала, да свършат**. Затова редът `print(f"a la vez: ...")`, който е след блока, се изпълнява едва когато и четирите са отговорили. Можеш да създаваш задачи където искаш вътре в блока; не можеш да забравиш нито една, защото блокът не те пуска да излезеш, докато има жива. Това е, което [документацията на `asyncio`](https://docs.python.org/3/library/asyncio-task.html#task-groups) нарича *структурирано съвместно изпълнение*: задачите се раждат и умират вътре в блок с отстъп, както `with` затваря своя файл.

#### 10.1.3 Резултатите и техният ред

`create_task` връща задачата, а задачата пази своя резултат. След блока `tarea.result()` ти го предава: ако задачата е завършила успешно, стойността, която е върнала функцията ѝ; ако се е провалила, хвърля отново изключението. Забележи детайла, който е важен за `revisor`: пазим задачите **в списък, в реда на услугите**, и после вадим резултатите, **обхождайки този списък**. Отговорите пристигнаха разбъркани (първо pagos), но последният ред на изхода, `['catalogo', 'inventario', 'pagos', 'reportes']`, е в реда на конфигурацията. Този ред не е лукс: отчет, в който редовете сменят мястото си при всяко изпълнение, е нечетлив, а JSON, който се сравнява с вчерашния, трябва да е в същия ред. Правилото е просто: **редът, в който пристигат отговорите, го определя мрежата; редът, в който се показват, го определяш ти**, и се определя, като пазиш задачите в списък, а не трупаш резултатите, както свършват.

#### 10.1.4 Задачата отстъпва реда само при `await`

Липсва още една част, за да е умственият модел пълен, и тя е тази, която причинява най-много грешки. Цикълът на събитията работи **в една нишка**. Когато изпълнява задача, тя държи цялата нишка, докато сама не я пусне, а я пуска единствено при `await`, който трябва да чака. Между два `await` никой друг не работи. Това се нарича **кооперативно** съвместно изпълнение: задачите си сътрудничат, като отстъпват реда. Ако една задача не си сътрудничи, блокира всички. Виж какво става, ако вместо `await asyncio.sleep(...)` се ползва обичайният `time.sleep(...)`, чакане, което **не отстъпва нищо**:

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

Това е същата `TaskGroup` като във фигурата преди нея, с четири задачи, създадени по същия начин. Но резултатът е друг: отпечатват се в реда, в който са създадени, не в реда на бързина, и общото време е 1.1 секунди, сборът. Защо? Защото първата задача стигна до `time.sleep(0.3)`, а `time.sleep` спира **нишката**, и със спряна нишка цикълът на събитията не може дори да мине към следващата задача. Другите три чакаха реда си, една след друга, макар да са в `TaskGroup`. Тази грешка е особено коварна, защото **програмата не се проваля**: дава верния резултат, само че толкова бавно, сякаш няма съвместно изпълнение. Коментарът `# noqa: ASYNC251` е там, защото `ruff` (инструментът от Урок 8) познава тази грешка и я отбелязва, макар и не с набора от правила на `revisor`: `ASYNC251` е от колекцията `ASYNC`, тази за грешките на `asyncio`, която не е в `select` на проекта (`E`, `F`, `I`, `B`, `UP`). Ако я поискаш, `ruff check --select ASYNC` върху тази фигура без този коментар казва ``ASYNC251 Async functions should not call `time.sleep` ``. И ако кодът ти използва `asyncio` сериозно, е добър кандидат да влезе в твоя `select`. В тази фигура го оставяме нарочно, за да покажем вредата; в истинския ти код предупреждението на `ruff` е следа, която да следваш.

Практическото правило: вътре в корутина всичко, което чака (мрежа, бавен диск, време), трябва да е `await` върху нещо, направено за `asyncio`: `asyncio.sleep`, `httpx.AsyncClient`. Обикновено извикване, което се бави (`time.sleep`, дълго изчисление, функция на `requests`), не си сътрудничи и отнася със себе си целия цикъл. Това е причината курсът да използва `httpx`, а не `requests`: `httpx` умее да чака, без да блокира. Главата от документацията за [разработка с `asyncio`](https://docs.python.org/3/library/asyncio-dev.html) съдържа режима за дебъгване, който предупреждава, когато задача държи нишката твърде дълго.

### 10.2 Ограничения: таван на времето и таван на едновременните

#### 10.2.1 `asyncio.timeout()`: таванът на цяла операция

От Урок 9 знаеш, че всяка заявка трябва да има времеви лимит: без него закачена услуга кара `revisor` да чака завинаги. `httpx` вече има такъв, който му подаваш с `httpx.Timeout(...)`. Тогава за какво още един?

Защото времевите лимити на `httpx` измерват **фази**, не общото. Според [неговата документация](https://www.python-httpx.org/advanced/timeouts/), `httpx` различава четири: този за **свързване** (колко да чака, за да отвори канала), този за **четене** (колко да чака следващото късче данни), този за **писане** и този за **чакане на свободен канал в пула от връзки**. `httpx.Timeout(5.0)` слага и четирите на 5 секунди, всеки поотделно. Сървър, който праща по един байт на четири секунди, никога не задейства този за четене — всяко късче пристига навреме — и отговорът може да се точи с минути. `httpx` не е сгрешил: всяка фаза е спазила лимита си. Липсва лимит върху **цялото**. Това е `asyncio.timeout()`, който съществува от Python 3.11 и е в [документацията на `asyncio`](https://docs.python.org/3/library/asyncio-task.html#timeouts):

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

Блокът `async with asyncio.timeout(1):` пуска часовник от 1 секунда върху всичко, което става вътре. Вътре има чакане от 10 секунди. Щом мине секундата, `asyncio` **отменя** това, което чака вътре в блока, и при излизане хвърля `TimeoutError` (нормално изключение на Python, от 3.11; преди се наричаше `asyncio.TimeoutError`, което днес е просто друго име за същото). `except TimeoutError` го прихваща и програмата отпечатва времето, което наистина е чакала: 1.0 секунди, не 10. Научи двата ефекта на блока: **прекъсва** чакането (задачите не остават закачени) и **известява** с изключение, което ти решаваш как да обработиш.

Двата механизма не си пречат; допълват се. В днешния `revisor` те съжителстват: `httpx.Timeout` слага лимит на всяка фаза, а `asyncio.timeout` на цялата услуга. И двата ползват `timeout_ms` на услугата, и който от двата настъпи пръв, дава същия резултат: „tiempo agotado“ (времето изтече). По-нататък, в 10.4, ще видиш едно от предимствата да имаш и двата: таванът на `asyncio` действа, дори когато `httpx` не участва.

#### 10.2.2 `asyncio.Semaphore`: колко едновременно, най-много

**Семафорът** (*semaphore*) е брояч на разрешения. Създава се с число, `asyncio.Semaphore(2)`: има две разрешения. Който иска да влезе, прави `async with semaforo:`; ако остава разрешение, взема го и влиза, а ако не, **чака**, докато друг го върне при излизане. Като входа на паркинг с две места: когато е пълен, следващата кола чака на улицата, докато излезе някоя. [Документацията](https://docs.python.org/3/library/asyncio-sync.html#semaphore) го описва точно така. Нека видим шест услуги по половин секунда с място за две едновременно:

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

Чети изхода на групи по четири реда. Влизат 1 и 2; излизат и двете половин секунда по-късно; едва тогава влизат 3 и 4, и така нататък. Шест услуги, по две едновременно: три партиди по половин секунда, общо 1.5 секунди. Всички задачи са създадени наведнъж в `TaskGroup`, но четири от тях останаха да чакат в `async with semaforo`, без да харчат нищо. Забележи и реда: 3 влиза преди 4, 5 преди 6. В CPython семафорът обикновено обслужва по реда на пристигане, но [документацията](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) не го обещава (за `Lock` го обещава), така че програмата ти не бива да зависи от този ред. `revisor` не зависи: редът на отчета му го дава списъкът с услуги, не редът, в който са свършили.

Колко е правилното ограничение? Зависи от **кой получава** заявките. Ако са твои собствени услуги, колкото издържат; ако са на трета страна, колкото позволява нейната документация; ако са много и не знаеш, умерено число. `revisor` ползва **10** по подразбиране и позволява на потребителя да го промени с `--concurrencia`. Семафорът пази и собствената ти машина: всяка отворена връзка харчи файлов дескриптор, а всяка операционна система има таван. А `httpx` сам ограничава пула от отворени връзки (100 по подразбиране, както казва [документацията му за ограниченията](https://www.python-httpx.org/advanced/resource-limits/)), така че ограничение по-голямо от това само би накарало заявките да чакат на друга опашка.

#### 10.2.3 Пренасяне в `revisor`

Цялата промяна на тази половина се побира в три файла и един нов файл с данни. Първо версията на пакета, `0.9.0` (зависимостта от `httpx` беше там още от 9):

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

После сърцето, `revision.py`. Чети го на три хода:

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

**Първо, `revisar`** (една-единствена заявка). Промени се съвсем малко спрямо Урок 9: `await cliente.get(...)` сега живее вътре в `async with asyncio.timeout(servicio.timeout_ms / 1000):`. Делението на хиляда е, защото `timeout_ms` е в милисекунди, а `asyncio.timeout` иска секунди. В `except`, `(httpx.TimeoutException, TimeoutError)` прихваща двата случая на изтекло време: този на фаза от `httpx` и тавана на `asyncio`. Със скоби, защото в Python 3.12 `except` с два класа ги поставя в кортеж (tuple). Останалото е същото: всяка мрежова грешка се превръща в `Resultado` със своя детайл, а функцията **никога** не оставя мрежова грешка да излезе. Има едно изключение, което `revisar` **не** прихваща нарочно и заслужава абзац: `asyncio.CancelledError`. Така `asyncio` съобщава на задачата „отмениха те“. Ако го прихванеш, ще погълнеш заповедта за отмяна и `TaskGroup` или `timeout` ще останат без възможност да си свършат работата. Затова `except` назовава конкретни класове и никога не е широк `except Exception`: правилото от Урок 6 (никакъв „гол“ `except:`) сега има още една причина.

**Второ, `_revisar_con_limite`**: три реда, които вземат разрешение от семафора и проверяват. Тя е **извън** `revisar` заради причина, свързана с измерването. Ако семафорът беше вътре, часовникът на `revisar` би започнал да тече преди да е получено разрешението, и услуга, която е чакала реда си половин секунда, би се появила като „бавна“, без да е. С разрешението отвън, времето, което измерва `revisar`, е това на заявката, а чакането в опашката на семафора не се брои. Същото важи за тавана на `asyncio.timeout`: започва да отброява, когато заявката започне, не когато задачата е създадена.

**Трето, `revisar_todos`**. Сигнатурата ѝ се промени: сега приема `limite` (по подразбиране 10) и `transporte`, който засега можеш да пренебрегнеш (съществува за 10.4: това е вратата, през която тестовете вкарват фалшив сървър). Ред по ред: ако `limite` е по-малко от 1, хвърля `ValueError`, защото `Semaphore(0)` не гръмва: оставя всички да чакат разрешение, което никога не идва, и програмата увисва, без да каже нищо. Създава се семафорът. Отваря се **един-единствен** `httpx.AsyncClient` за всички заявки, защото клиентът поддържа пул от повторно използваеми връзки, а отварянето на двайсет клиента би било разхищение. Отваря се `TaskGroup` и изразът за построяване създава една задача за всяка услуга, **в реда на списъка**. При излизане от блока всички са свършили. Последният ред, извън `async with`, съставя списъка с резултати, обхождайки задачите в същия този ред: така отчетът следва конфигурацията, без значение кой е отговорил пръв.

Остава потребителят да може да избира ограничението. В `cli.py`:

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

Има две нови неща. `entero_positivo` е функция, която `argparse` използва, за да преобразува и валидира текста, който потребителят е написал след `--concurrencia`: ако не е цяло число или е по-малко от 1, хвърля `argparse.ArgumentTypeError`, а `argparse` го превръща в своята грешка за употреба с код на изход **2**, същия, който вече ползваше за „употребата е невалидна“. Два детайла в написването на тази функция. `{texto!r}` вътре в f-string иска *представянето* на стойността вместо текста такъв, какъвто е: текстът излиза с кавичките си (`'diez'`), и така съобщението показва точно какво е написал потребителят, дори да са били интервали. И `raise ... from None` е `raise ... from` от Урок 6 с обратното намерение: вместо да запази оригиналната грешка като причина, я **скрива**, защото `ValueError` от `int` не казва нищо на този, който е написал `--concurrencia diez`, а новото съобщение вече казва всичко. Накрая, в `main` извикването стана `revisar_todos(servicios, limite=argumentos.concurrencia)`.

За да измерим с нещо по-интересно от четири услуги, има файл с двайсет, всички сочещи към маршрута `/espera/500` на лабораторията (всяка отговаря след половин секунда):

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

С лабораторията, пусната в друг терминал (`python laboratorio.py`, както в Урок 9), измери три пъти едно и също изпълнение. `time` е команда на терминала, която изпълнява това, което следва, и накрая казва колко е отнело; редът `real` е времето по стенния часовник. С `| tail -n 1` се запазва само последният ред на отчета, обобщението, за да не гледаш двайсет реда:

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

Числата разказват историята. С `--concurrencia 1` (едно разрешение, тоест един след друг) отнема **10.3 секунди**: двайсет чакания по половин секунда. С 10 отнема **1.15**: двайсет услуги, по десет едновременно, са две партиди по половин секунда. С 20 отнема **0.63**: една-единствена партида. А защо 10 дава двойното на 20, а не нещо междинно? Защото при ограничение 10 първите десет заемат разрешенията за половин секунда, а другите десет **не могат да започнат**, докато не се освободи някое: две партиди една след друга. При ограничение 20 се побират всички наведнъж. И защо 0.63, а не 0.5? Защото часовникът на `time` включва това, което не е чакане на мрежата: стартиране на Python, импортиране на `httpx`, отваряне на връзките. Това са между 0.1 и 0.15 секунди, които не зависят от броя на услугите. Ако твоята машина е по-бавна, твоите числа ще са малко по-големи; важна е **пропорцията** между трите изпълнения.

Така приключва първата сесия. Това, което имаш, е `revisor`, който пита няколко услуги едновременно и не злоупотребява. Това, което му липсва, е да издържа на провали и, преди всичко, да **докаже**, че издържа.

### 10.3 Групи от изключения: една грешка не събаря отчета

#### 10.3.1 Какво става, когато една задача се провали

Досега всичко мина добре. `TaskGroup` има правило за случая, когато не минава добре, и е добре да го видиш с очите си, преди да го прочетеш: ако **една** от задачите завърши с изключение, групата **отменя останалите**. Виж какво се случва с отчет от три задачи, една от които се чупи:

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

Вътре в групата има три задачи. `catalogo` чака 0.05 секунди и завършва успешно. `reportes` чака 0.1 и хвърля `ConnectionError` (изключението на Python за връзка, която не е могла да се осъществи; братовчед е на `httpx.ConnectError`, който ползва `revisor`). `inventario` чака 0.5 секунди. Виж изхода: `catalogo` завърши, `inventario` беше **отменена** (така и не стигна да каже „terminó“ (завърши); половин секундата, която ѝ оставаше, се загуби), а изключението на `reportes` излезе през `except*`.

В кода има две нови форми. Първата е в `consulta_buena`: `except asyncio.CancelledError:` отпечатва „cancelada“ (отменена) и после прави голо `raise`. `raise` без нищо повече **хвърля отново изключението, което се обработва**; необходимо е, защото, както видя в 10.2.3, поглъщането на отмяна разваля механизма. Втората е `except*`, която заслужава собствена секция.

#### 10.3.2 `ExceptionGroup` и `except*`

Когато няколко задачи от една група се провалят едновременно, Python не може да хвърли едно изключение: биха били няколко в един и същи момент. Затова от 3.11 съществува `ExceptionGroup` ([PEP 654](https://peps.python.org/pep-0654/)): изключение, което **съдържа други изключения**, в атрибута си `.exceptions`, който е кортеж (tuple, колекцията, която не се променя, от Урок 4). `TaskGroup`, който е претърпял провали, ги пакетира в такава група при излизане от блока, дори да се е провалила само една задача.

Обикновеният `except` прихваща по класа на изключението, което пристига; тъй като пристига `ExceptionGroup`, един `except ConnectionError` нямаше да я разпознае. За това е създаден `except*` (със звездичка), който **отваря групата**: `except* ConnectionError as grupo_de_errores` прихваща изключенията от групата, които са `ConnectionError`, събира ги в нова група и я оставя в променливата. Затова `for error in grupo_de_errores.exceptions:` обхожда този кортеж, а не една-единствена грешка. Ако в групата е имало изключения от други класове, които никой `except*` не е прихванал, те продължават нагоре по пътя си. Един и същи `try` може да има няколко `except*`, всеки за своя клас, и всеки получава своето. Това, което **не** можеш, е да смесиш `except` и `except*` в един и същи `try`. [Документацията на езика](https://docs.python.org/3/reference/compound_stmts.html#except-star) съдържа всички правила; за `revisor` стига това, което виждаш.

Забележи какво спечели и какво загуби програмата. Спечели чистота: никоя задача не остана безстопанствена, групата изчака отменените да свършат с отмяната си, и грешката пристигна подредена. Загуби отчета: `inventario` беше здрава и резултатът ѝ бе изхвърлен. В `revisor` това е неприемливо, защото смисълът му е да ти казва състоянието на **всички**.

#### 10.3.3 Мрежовата грешка е резултат, не изключение

Решението на `revisor` вече е написано и сега можеш да разбереш защо е такова. `revisar` **прихваща** мрежовите грешки в самата задача и ги превръща в `Resultado` (`CAIDO`, със своя детайл). От гледна точка на `TaskGroup` задачата е завършила успешно: върнала е стойност. Никой не хвърля нищо нагоре, никой не отменя никого и отчетът излиза пълен, с реда на `reportes`, който казва „sin conexión“ (без връзка). Това е принципът на урока: **очакваната грешка е част от данните, не инцидент**. Паднала услуга не е изненада за `revisor`; тя е част от работата му.

А всички ли грешки се превръщат в данни? Не, и разликата е най-ценното в тази секция. `revisar` прихваща **конкретни класове на `httpx`**: грешките, които външният свят може да причини. Не прихваща `ZeroDivisionError`, `KeyError` или `TypeError`: те са грешки **на програмата** и да ги скриеш, сякаш са „паднала услуга“, би било лъжа. Ако една услуга се появи като паднала, защото кодът ти има грешка, ще прекараш следобед, търсейки проблема в мрежата. С днешния дизайн програмната грешка прави каквото трябва: спира отчета, шумно, с доклад, който сочи реда. Този шумен изход е това, което виждаш в секцията „Грешката, която ще видиш“ по-долу, и е добра новина, не лоша.

### 10.4 Тестове без мрежа

#### 10.4.1 Защо не се тества срещу мрежата

За да провериш предишния абзац („паднала услуга не събаря отчета“), трябват паднали, бавни услуги, такива, които връщат 503 и такива, които се разкачват, и четирите неща **едновременно**. Тестовете срещу истинската мрежа имат три проблема. Първо, са **бавни**: тест на времеви лимит от 5 секунди кара този, който пуска пакета с тестове, да чака 5 секунди. Второ, са **крехки**: провалят се, защото е паднал wifi, не защото кодът ти е грешен, а червено, което не значи нищо, кара хората да спрат да гледат червеното. И трето, са **невъзможни за повтаряне**: не можеш да поискаш от истинска услуга да падне точно сега. Затова правилото е, че **модулният тест никога не излиза към мрежата**. Мрежата се замества с дубльор (test double): нещо със същата форма като истинското, но което отговаря каквото тестът му каже.

Статията в [блога на Hábil за тестовете, които хващат грешки](https://www.habil.mx/bg/blog/tests-that-catch-errors-coverage-quality-gate/) разказва защо тест, който можеш да зачервиш по желание, струва повече от десет, които винаги са зелени; а тази за [стиловете на интеграция: на линия, опашка и събитие](https://www.habil.mx/bg/blog/online-or-async-integration-styles/) показва същия проблем откъм архитектурата: отделяне на този, който пита, от този, който отговаря. Тук го отделяш с една част на `httpx`.

#### 10.4.2 `httpx.MockTransport`: фалшив сървър

HTTP клиентът има две половини: тази, която съставя заявката и разбира отговора, и **транспортът**, който наистина докосва мрежата. `httpx` ти позволява да смениш транспорта и носи един, направен за тестове, [`httpx.MockTransport`](https://www.python-httpx.org/advanced/transports/#mock-transports): получава функция, която, като ѝ се даде заявката, **връща отговора**, който ти поискаш. Нищо не излиза от компютъра ти.

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

`atender` е фалшивата функция: получава `httpx.Request` (заявката, с адреса си в `.url`), отпечатва какво ѝ е пристигнало и връща `httpx.Response` с код 200 и текста „todo bien“ (всичко е наред). `httpx.MockTransport(atender)` я обвива като транспорт, а `httpx.AsyncClient(transport=transporte)` съставя клиент, който вместо да отваря връзка, вика нея. Клиентът прави `get("https://catalogo.example/estado")`, адрес, който не съществува (`.example` е резервиран домейн, който никога не се разрешава), и въпреки това получава отговор, защото никога не е ходил да го търси. Това е, което `revisar_todos` предлага с параметъра си `transporte`: получава транспорта и го предава на `httpx.AsyncClient(transport=transporte)`. Когато е `None` (нормалното), `httpx` ползва истинския.

Фалшивият транспорт може да прави повече от отговор 200: може да върне 503 (`httpx.Response(503)`), или да **хвърли** мрежово изключение, сякаш кабелът е прекъснат (`raise httpx.ConnectError(...)`), или дори да чака, ако функцията е `async def`. С тези четири неща се симулира всичко, което `revisor` трябва да понесе.

#### 10.4.3 Шестте теста на `revisar`

Нов файл, `tests/test_revision.py`. Преди кода, планът: тестовете говорят с фалшив сървър, който се държи според **името на хоста** (частта от адреса между `https://` и първата наклонена черта). `facturacion.example` отговаря 503; `reportes.example` хвърля `ConnectError`; `notificaciones.example` хвърля `ReadTimeout` (изключението на `httpx` за „изтекло е времето за четене“); всеки друг отговаря 200.

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

Всеки тест е обикновена функция (не `async`): съставя каквото му трябва и вика `asyncio.run(...)`, както прави `main`. Така не е нужна никаква добавка на `pytest`, за да изпълнява корутини, и курсът остава с това, което вече познаваш. `revisar_uno` е помощна функция, която отваря клиент с фалшивия транспорт и проверява една-единствена услуга. Първите четири теста обхождат четирите изхода на `revisar`: бърз 200 е `ARRIBA`; 503 е `CAIDO` и детайлът е кодът, `"503"`; `ConnectError` е `CAIDO` със „sin conexión“ (без връзка); `ReadTimeout` е `CAIDO` с „tiempo agotado“ (времето изтече). Петият, `test_la_mezcla_sale_completa_y_en_orden`, е този, който доказва обещанието на урока: подава на `revisar_todos` четири услуги, по една от всеки вид, и проверява, че **са се върнали и четирите, в реда на конфигурацията, всяка със своя детайл**. Ако някоя грешка събореше отчета, този тест щеше да стане червен. А шестият, `test_una_direccion_invalida_no_tumba_a_los_demas`, пази четвъртия `except` от Урок 9: събира услуга с невъзможния адрес `http://999.1.1.1:8099/pagos` и една здрава и изисква първата да излезе с „dirección inválida“ (невалиден адрес), а втората с нейния `200`. Без този `except`, `httpx.InvalidURL` би избягала от задачата си, `TaskGroup` би отменил останалите и тестът би се провалил с група от изключения (10.3).

(Нещо, което липсва тук за `LENTO`: няма тест за това състояние, защото симулирането, че е минала повече от секунда, с фалшив транспорт отвлича вниманието. Прагът за бавност вече е тестван там, където живее, в `clasificar`, с неговите седем случая от Урок 8.)

#### 10.4.4 Да я видиш в червено, преди да ѝ повярваш

Тест, който никога не си виждал да се проваля, не доказва нищо: може би щеше да мине и с развален код. Затова се проверява. В копие на проекта се изтрива клонът `except httpx.ConnectError` на `revisar`, така че `ConnectError` да падне в общия клон и да каже „error de red“ (мрежова грешка). Изпълнява се:

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

Почервеняха **точно два** теста: този, който говори за връзката, и този за смесицата (който включва този случай). Редът `2 failed, 25 passed` ти дава отчета, който има значение: това не е зелено по случайност. Поправи кода и пусни отново:

```text
$ pytest -q
...........................                                              [100%]
27 passed in 0.03s
```

`27 passed`: 21-те от предишния урок плюс шестте от днес. Това число се чете от отчета, не от кода на изход, защото код 0 не ти казва колко теста са се изпълнили: излиза същото и с 27, и с 2, ако по погрешка си филтрирал останалите. (Урок 11 се връща към това с конкретен случай.)

Има граница, която е добре да се каже открито. Тестът за изтеклото време кара фалшивия сървър да **хвърли** `ReadTimeout`, тоест тества клона на `httpx.TimeoutException`. Не тества **тавана** на `asyncio.timeout`, който съществува точно за случая, когато `httpx` не разбира нищо. Този тест трябва да се напише и той е Упражнение 2: пишеш го ти и ще провериш, че ако се махне `asyncio.timeout`, става червен.

#### 10.4.5 `monkeypatch` и сигнатурата, която не бива да променяш без предупреждение

`test_cli.py` вече съществуваше, с два теста, и имаше детайл, който днес се набива на очи. Тези тестове викат `main`, а `main` вика `revisar_todos`, който излиза към мрежата. За да не го прави, курсът използва `monkeypatch` (Урок 8): сменя, по време на теста, едно име с друго, а когато тестът свърши, го възстановява. Тук сменя `revisor.cli.revisar_todos` с фалшива функция, която връща каквото тестът му трябва.

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

Забележи **къде** се сменя името: `"revisor.cli.revisar_todos"`, а не `"revisor.revision.revisar_todos"`. `cli.py` е направил `from revisor.revision import revisar_todos`, така че `cli` има **собствено копие на името**; ако смениш оригинала в `revision`, `cli` пак би използвал своето. Правилото на `monkeypatch`: името се сменя на мястото, където **се използва**, не там, където е дефинирано.

А сега важното за тази версия: двете фалшиви функции, `todos_caidos` и `todos_arriba` (всяка дефинирана вътре в своя тест), **приемат `limite`**. Днес `main` вика `revisar_todos(servicios, limite=argumentos.concurrencia)`, а фалшива функция, която не приема този аргумент, не е дубльор на истинската: е друга функция и тестът се чупи. Ако в Урок 9 твоята фалшива функция беше `async def todos_caidos(servicios)`, сега трябва да ѝ добавиш параметъра. Виждаш го в „Грешката, която ще видиш“. Това е по-общ урок: **дубльорът трябва да има същата сигнатура като това, което замества**, и когато промениш сигнатурата на истинската функция, тестовете с дубльори са първото, което се чупи. Това не е неприятност; това е тестът, който си върши работата и те предупреждава, че други са зависели от тази сигнатура.

#### 10.4.6 Целият проект

Файловете, които не се промениха в този урок, са тук, за да е папката `fig10_08/` пълна и да можеш да я изпълниш. Те са същите, които носеше от Урок 9:

<details>
<summary>Файловете, които не се променят в този урок</summary>


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

С лабораторията в ход, снимката на проекта дава същия отчет както винаги, но този път четирите услуги се питат едновременно, така че общото време е на най-бавната (`inventario`, 2.3 секунди), а не сборът:

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

Времената в колоната TIEMPO (време) ще се различават малко на твоята машина; ESTADO (състояние) и DETALLE (детайл) не, защото лабораторията е направена така, че да излизат винаги еднакви. А кодът на изход, както в Урок 7, е 1: има един `LENTO` и един `CAIDO`.

**За сравнение.** Същият проблем — да пуснеш, да изчакаш всички, да ограничиш, да не загубиш отчета заради провал — е решен в [курса по Go](https://www.habil.mx/bg/courses/go/) със `sync.WaitGroup` и в [курса по TypeScript](https://www.habil.mx/bg/courses/typescript/) с `Promise.all` и `Promise.allSettled`. Идеята е същата; променя се къде живее чакането. В Go всяка задача е *goroutine*, лека нишка, която се разпределя от планировчика на самия Go (не от операционната система) между нишките на процесора; в TypeScript и в Python е кооперативна задача в една нишка. Сравняването на трите решения учи повече от четенето само на едно.

## Грешката, която ще видиш

### `ExceptionGroup: unhandled errors in a TaskGroup`

Тя е, която ще ти излезе първия път, когато имаш програмна грешка вътре в задача. Фигура 9 я предизвиква: функция, която усреднява списък, а ѝ подават **празен**, така че дели на нула.

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

Две задачи вътре в групата: едната усреднява две числа, другата празен списък. Това казва Python (пътищата са съкратени до името си, както в целия курс; на твоята машина идват пълни, а редовете от `asyncio/` могат да се различават според версията на Python):

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

Първо: този *traceback* **не се чете като тези от предишните уроци**, от последния ред нагоре. Последният ред отгоре, `+------------------------------------`, е украса; истинската причина е **вътре в кутията**, обозначена с `|`, в дъното. Чети го така:

1. Първият ред, `+ Exception Group Traceback`, те предупреждава: това, което следва, е група.
2. Редовете с `|` слизат по пътя, който е изминало изпълнението: твоето `asyncio.run(main())`, вътрешните стъпки на `asyncio` и, важно, твоят `main` на ред 10, в `async with asyncio.TaskGroup()`. Там групата, при излизане, е пакетирала грешката.
3. `ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` е етикетът на групата: „необработени грешки в TaskGroup, едно подизключение“. Числото в скобите ти казва колко съдържа.
4. А **вътре в кутията** (`+-+---------------- 1 ----------------`) е подизключение номер 1 със собствен *traceback*: `promedio`, ред 6, `ZeroDivisionError: division by zero`. **Тя е причината** и нея трябва да поправиш. Редът от твоя файл е там, където пише `fig10_09.py", line 6, in promedio`.

Забележи и какво стана с **другата** задача (`promedio([142, 87])`): нямаше какво да се отменя. Тъй като няма никакъв `await`, тя се изпълни цялата, без да отстъпва реда, и завърши със своето `114.5`, преди втората да започне. Ако беше чакала нещо, като `inventario` във `fig10_06.py`, `TaskGroup` щеше да я отмени, макар и здрава: това е групата, която си върши работата.

Какво да правиш: поправи причината (провери, че списъкът не е празен), не крий грешката. Устой на изкушението да сложиш широк `except*`, за да я заглушиш: програмната грешка трябва да се вижда.

### `TypeError: ... got an unexpected keyword argument 'limite'`

Втората днешна грешка е тази от 10.4.5. Ако твоята фалшива функция в `test_cli.py` е от Урок 9 и не приема `limite`:

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

Чети я отдолу нагоре, както винаги: `TypeError`, „`todos_caidos()` получи неочакван именуван аргумент, `limite`“. (Частта `test_con_servicios_caidos_sale_con_1.<locals>.`, която предхожда името, означава, че тази функция е дефинирана **вътре** в теста.) Редът отгоре (`src/revisor/cli.py:64`) ти казва кой го е подал: `main`. А този по-горе, че тестът е извикал `main`. Решението не е в `cli.py`: е във фалшивата функция, която трябва да приема същото като истинската.

## Какво се прави погрешно

**Чакане с `time.sleep` вътре в корутина.** Блокира нишката и унищожава цялото съвместно изпълнение, без да даде грешка (10.1.4). Цена: програма, която изглежда съвместна, а отнема колкото един след друг. Открива се с режима за дебъгване на `asyncio` и с `ruff`, при условие че добавиш колекцията `ASYNC` към своя `select` (тази на `revisor` не я носи; 10.1.4).

**Създаване на задачи с `asyncio.create_task` и забравяне да се пазят.** Python пази само **слаба** препратка към самостоятелните задачи и задача, която никой не държи, може да бъде прибрана от събирача на боклук (garbage collector) по средата на изпълнението. [Документацията](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) предупреждава за това. С `TaskGroup` не се случва, защото групата ги пази. Цена: задачи, които изчезват без грешка.

**Липса на ограничение на съвместното изпълнение.** `TaskGroup` без семафор с хиляда услуги отваря хиляда връзки едновременно. Цена: удряш се в лимита на операционната система или претоварваш услугата, която проверяваш, и отчетът се проваля по причини, които не са тези, които измерва.

**Прихващане на `Exception` (или `BaseException`) вътре в задачата, „за да не се проваля никога“.** Изяжда програмните грешки и, с `BaseException`, дори отмяната. Цена: отчет, който лъже („услугата е паднала“), когато този, който се е провалил, е твоят код.

**Поглъщане на `CancelledError`.** Един `except asyncio.CancelledError:`, който не хвърля изключението отново, оставя `TaskGroup` и `asyncio.timeout` без възможност да отменят. Цена: програми, които не свършват или не уважават времевия лимит. Ако я прихващаш, за да почистиш нещо, направи `raise` накрая.

**Тестване срещу истинската мрежа.** Бавни, крехки, невъзможни за повтаряне (10.4.1). Цена: червени тестове, на които никой не вярва.

**Фалшива функция с друга сигнатура.** Дубльорът, който не приема това, което истинската функция приема, е друга функция. Цена: тестове, които се чупят, когато се промени сигнатурата, или, още по-лошо, които продължават да минават, без да тестват нищо, защото никой не ги е викал с новите аргументи.

**Измерване с едно-единствено изпълнение.** Едно число не казва нищо: стартирането на Python, загряването на връзките и това, което прави компютърът ти в тази секунда, се смесват. Измервай няколко пъти и сравнявай **пропорцията**.

## Упражнения

### Упражнение 1 — Измери ограничение, което не си пробвал

С `servicios-20.toml` и лабораторията в ход, измери с `--concurrencia 5` и с `--concurrencia 4`. **Преди да пуснеш**, предскажи времената с разсъждението за партидите (колко партиди по половин секунда са нужни с това ограничение). Запиши предсказанието и измерването в дневника си и обясни разликата, ако има такава.

### Упражнение 2 — Тестът на тавана

Напиши тест за тавана на `asyncio.timeout`: услуга с `timeout_ms = 100`, чийто фалшив сървър **чака десет секунди**, преди да отговори. Тестът трябва да мине за част от секундата. Подсказка: функцията, която обслужва, може да е `async def` и да използва `await asyncio.sleep(10)`. После го **провери в червено**: махни `asyncio.timeout` от `revisar` (остави вместо него `if True:`), пусни теста и запиши колко време отнема да се провали и защо.

### Упражнение 3 — Времеви лимит, по-кратък от отговора

Копирай `servicios.toml` и добави `timeout_ms = 1500` към услугата `inventario` (която в лабораторията отговаря след 2.3 секунди). Предскажи реда на `inventario`, обобщението и колко ще отнеме изпълнението, и го сравни с това, което излезе. Какво се промени в `ESTADO` на `inventario` и защо?

### Упражнение 4 — Предизвикай три грешки и ги прочети

Предизвикай, една по една: (а) във `fig10_09.py` смени празния списък с `[100]` и пусни (какво изчезна?); после го върни и прекарай `ZeroDivisionError` на задачата през `except*`, който го прихваща и отпечатва съобщение; (б) пусни `python -m revisor --concurrencia 0` и запиши кода с `echo $?`; (в) махни `limite` от една от фалшивите функции на `test_cli.py` и пусни `pytest`. За всяка напиши с едно изречение какво означава съобщението.

## Решения

### Решение 1

С ограничение 5 и двайсет услуги са нужни четири партиди по половин секунда: 2.0 секунди плюс стартирането. С ограничение 4 са нужни пет партиди: 2.5 плюс стартирането. Едно референтно изпълнение даде 2.15 и 2.67 секунди: стартирането (0.15 до 0.2 s, които не са чакане) обяснява разликата с 2.0 и 2.5. Общото правило: времето ≈ (броят на услугите, разделен на ограничението, закръглен нагоре) по чакането на всяка, плюс стартирането.

### Решение 2

Тестът се добавя към `tests/test_revision.py` (или към собствен файл):

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

Фалшивият сървър е `async def` и чака десет секунди; фалшивият транспорт не прилага никакъв времеви лимит на `httpx` (няма мрежа), така че единственият, който може да прекъсне, е таванът на `asyncio.timeout`. С пълния код тестът минава за част от секундата:

```text
$ pytest -q tests/test_techo.py
.                                                                        [100%]
1 passed in 0.12s
```

А с махнатия `asyncio.timeout` (`if True:`) тестът **се проваля** и му отнема десет секунди да се провали, защото никой не прекъсва чакането; отчетът показва, че `revisar` е върнала `LENTO` с `'200'` след като е чакала десет секунди:

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

Това доказва, че тестът зависи от поправката, която твърди, че тества. Шестте теста на `test_revision.py` нямаше да забележат тази регресия.

### Решение 3

`inventario` минава от `LENTO` към `CAIDO` с детайл „tiempo agotado“ (времето изтече): отговорът ѝ отнемаше 2.3 секунди, а таванът е 1.5, така че се прекъсва по-рано. Обобщението вече брои `2 caídos` (2 паднали), а изпълнението отнема около 1.6 секунди (таванът от 1.5 плюс стартирането) вместо 2.4. Едно истинско изпълнение:

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

Две наблюдения. Средното се променя (126 ms в това изпълнение; варира малко при всяко), защото `inventario` вече не добавя време: услуга, която не е отговорила, не влиза в средното. А изпълнението е по-кратко, защото най-бавното вече не е `inventario`, а нейният таван.

### Решение 4

(а) С `[100]` вместо `[]` вече няма деление на нула, програмата завършва без изход и без грешка: двете задачи са се изпълнили. С `except*`:

```python
try:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))
except* ZeroDivisionError:
    print("una lista de tiempos venía vacía")
```

прихваща грешката и програмата отпечатва съобщението вместо *traceback*. (б) Излиза `revisor: error: argument --concurrencia: debe ser al menos 1` (трябва да е поне 1) и кодът е 2: това е грешка за употреба и я открива `argparse`, преди да е тръгнало нещо. (в) `TypeError: ... todos_caidos() got an unexpected keyword argument 'limite'`: фалшивата функция не приема това, което `main` ѝ праща.

## Как разбирам, че съм успял

- [ ] `fig10_02.py` отпечатва „a la vez: 0.5 s“ (едновременно: 0.5 s) и `fig10_01.py` отпечатва „en serie: 1.1 s“ (един след друг: 1.1 s), и можеш да кажеш защо първото е времето на най-бавната, а второто сборът.
- [ ] `fig10_03.py` отпечатва отговорите в реда, в който са създадени задачите, не в реда на бързина, и можеш да обясниш какво прави `time.sleep`, което `asyncio.sleep` не прави.
- [ ] `fig10_05.py` показва партидите по две и общото време от 1.5 s.
- [ ] В папката `fig10_08/` `pytest -q` завършва с `27 passed` и не с друго число, и го прави с изключена лаборатория (това е смисълът на тестването без мрежа).
- [ ] `ruff check`, `ruff format --check` и `mypy` не докладват нищо в тази папка.
- [ ] С `servicios-20.toml`, `--concurrencia 1` отнема около 10 секунди, `--concurrencia 10` около 1.1 и `--concurrencia 20` около 0.6, и можеш да обясниш защо 10 дава двойното на 20.
- [ ] `python -m revisor --concurrencia 0` завършва с код 2 и съобщение за употреба.
- [ ] Счупи нарочно клона `ConnectError` на `revisar` и видя как точно два теста стават червени; поправи го и се върнаха 27-те.
- [ ] Можеш със свои думи да обясниш разликата между времевия лимит на `httpx` и `asyncio.timeout`, защо `revisar` прихваща `httpx.HTTPError` и **не** `Exception`, и защо фалшивата функция в `test_cli.py` трябва да приема `limite`.

## Обобщение

Отговори, без да гледаш урока:

1. Каква е разликата между корутина и задача? Какво прави `create_task` и какво прави излизането от блок `async with asyncio.TaskGroup()`?
2. В кой точно момент цикълът на събитията може да мине от една задача към друга? Какво става с `time.sleep` вътре в корутина?
3. Ако четири услуги отговарят за 0.3, 0.5, 0.1 и 0.2 секунди, колко отнема изпълнението един след друг и колко с `TaskGroup`? А със `Semaphore(2)`?
4. Какво измерва `httpx.Timeout` и какво измерва `asyncio.timeout()`? Кой от двата прекъсва сървър, който праща по един байт на четири секунди?
5. Защо семафорът се взема **извън** `revisar`, а не вътре?
6. Когато задача от `TaskGroup` хвърли изключение, какво става с останалите? Какво получава кодът, който е извън блока?
7. Какво прави `except*`, което `except` не прави? Каква е разликата между това `revisar` да превръща `ConnectError` в `Resultado` и да прихваща `ZeroDivisionError`?
8. Къде се сменя името с `monkeypatch`, ако `cli.py` е направил `from revisor.revision import revisar_todos`? Защо фалшивата функция трябва да приема `limite`?

## За допълнително четене

- [Документация на `asyncio`: корутини и задачи](https://docs.python.org/3/library/asyncio-task.html) — `TaskGroup`, `create_task`, `timeout()` и `sleep()` с всичките им правила, включително отмяната. Това е източникът на този урок. Посетено на 7 октомври 2026 г.
- [PEP 654, „Exception Groups and except\*“](https://peps.python.org/pep-0654/) — защо съществуват групите от изключения, със случаите, които са ги мотивирали. По-технически, но разделът за мотивацията се чете добре. Посетено на 7 октомври 2026 г.
- [Документация на `httpx`: транспорти (`MockTransport`)](https://www.python-httpx.org/advanced/transports/) и [времеви лимити](https://www.python-httpx.org/advanced/timeouts/) — двете части на `httpx`, които използва днес. Посетено на 7 октомври 2026 г.
- [Документация на `pytest`: `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — всички начини да смениш име по време на тест и кога да ползваш всеки. Посетено на 7 октомври 2026 г.
