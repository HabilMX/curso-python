# Урок 8 — Тестове, типове и качество

**Време:** 2 × 90 минути (първата сесия стига до края на 8.3; втората започва от 8.4)

**Какво изграждаш:** `revisor` с 21 теста, които се пускат с една команда, с проверени типове и с наблюдаван стил

**Какво научаваш:** `pytest` (`assert`, тестът, видян червен преди да е зелен, `parametrize`, `tmp_path` и `monkeypatch`), постепенно типизиране с `mypy`, `ruff` за проверка и форматиране и как да четеш броя от отчета, а не кода на изход

**Откъде идваш.** Носиш пакета от [Урок 7](07-paquete-linea-de-comandos.md): `revisor` живее в `~/curso-python/revisor/` с разположение `src/`, инсталира се с `pip install -e .` и се пуска с `python -m revisor`. С четирите учебни услуги отпечатва таблицата на учебната програма и излиза с код 1, защото една е бавна и една е паднала. Работи. Липсва ти начин да **знаеш, че продължава да работи** след като го пипнеш: досега единствената проверка беше да го пуснеш и да погледнеш таблицата, а очите се уморяват и не виждат онова, което не очакват да видят. Този урок ти дава трима проверяващи, които не се уморяват: единият изпълнява кода ти с известни данни и сравнява отговора, другият чете кода ти, без да го изпълнява, и проверява дали данните си пасват, а третият следи да е написан така, както се пише на Python.

**Какво не прави този урок.** Не засяга мрежата: `revisor` продължава да чете симулираните данни от `SIMULADO`, а запитването към истински услуги е [Урок 9](09-http-y-asyncio.md). Не тества и асинхронен код, нито симулира мрежата, това е [Урок 10](10-concurrencia-pruebas-sin-red.md), и не мери колко код докосва всеки тест (*покритието*): то е полезно число, което лесно се подправя, и не помага за нищо, докато не знаеш какво проверява всеки тест.

## След урока ще можеш да

- Напишеш тест с `pytest` (файл `test_*.py`, функция `test_*` и един `assert`), да го пуснеш и да четеш отчета му отгоре надолу.
- Видиш тест **червен, преди да е зелен**, и да обясниш защо тест, който никога не си виждал да се проваля, не доказва нищо.
- Кажеш колко теста са се изпълнили, като четеш **отчета**, и да обясниш защо кодът на изход не стига: `0` съжителства с тест, който никога не е бил изпълнен.
- Превърнеш таблица от случаи в един-единствен тест с `@pytest.mark.parametrize` и да различиш в отчета кой ред се е провалил.
- Тестваш код, който чете файлове, с `tmp_path`, и код, който зависи от друга функция, с `monkeypatch`, като знаеш **къде** трябва да се подмени.
- Провериш типовете на пакета с `mypy` в строг режим, да четеш съобщението му и да обясниш какво значи, че типизирането в Python е постепенно.
- Проверяваш и форматираш кода с `ruff check` и `ruff format`, с трите инструмента, настроени в `pyproject.toml`.

## Защо, преди как

Отвори `src/revisor/modelo.py` и в `clasificar` намери реда, който решава кога една услуга е бавна: `if tiempo_ms is not None and tiempo_ms >= umbral_ms:`. Представи си, че утре някой, забързан, „оправя“ това `>=` и го оставя `>`: един-единствен знак. Пусни `revisor` с четирите учебни услуги. **Таблицата излиза същата.** `catalogo` отнема 142 ms, `inventario` 2300, `pagos` 87, а `reportes` не отговаря; никоя не отнема точно 1000 ms, единствената стойност, при която `>=` и `>` се държат различно. Дефектът съществува, програмата работи без грешка и таблицата изглежда безупречна. В деня, когато истинска услуга се забави точно 1000 ms (времената за отговор се трупат около кръгли числа повече, отколкото изглежда), тя ще остане „работеща“, докато правилото на курса казва, че вече е „бавна“.

Проверката, която имаше, да гледаш таблицата, **не можеше** да намери този дефект, защото не задава въпроси за случаите, които имат значение. Трябва да напишеш тези въпроси веднъж („услуга, която отговаря 200 за 999 ms, работи ли? А тази, която отговаря 200 за 1000 ms, бавна ли е?“) и една машина да ги повтаря всеки път, когато пипнеш кода, за по-малко от секунда. Това е **тест**: малка програма, която извиква кода ти с известна входна стойност и проверява дали отговорът е такъв, какъвто трябва. Наборът от тестове е мрежа за безопасност: позволява ти да променяш кода спокойно, защото ако счупиш нещо, го разбираш веднага и знаеш къде.

Урокът носи три инструмента, всеки със своя въпрос:

| Инструмент | Въпросът, на който отговаря | Как работи |
|---|---|---|
| `pytest` | Прави ли програмата това, което казах, с тези данни? | **Изпълнява** кода ти и сравнява |
| `mypy` | Пасват ли данните си? Дали не съм подал текст там, където отива число, или не съм забравил, че нещо може да е `None`? | **Чете** кода ти, без да го изпълнява |
| `ruff` | Написан ли е така, както се пише на Python, без излишни импорти и познати уловки? | **Чете** кода ти и го преформатира |

Нито един не замества другите, а заедно са онова, което в един екип се нарича качествена врата (quality gate): промяната, която не ги премине, не влиза. Блогът на Hábil разказва как изглежда тази дисциплина в екипен проект, в [тестове, които хващат грешки, покритие и качествени врати](https://www.habil.mx/bg/blog/tests-that-catch-errors-coverage-quality-gate/). Първата сесия използва `pytest`, докато стигнеш до 21-те теста на `revisor`; втората проверява типове и стил и оставя трите инструмента поставени в проекта.

### Подготви инструментите

Инсталират се с `pip` (както в Урок 1, с `python -m pip`, за да е `pip` на средата) във виртуалната среда на курса, същата, която активира в [Урок 1](01-instalacion.md) (в подканата се вижда `(.venv)`):

```bash
python -m pip install pytest==9.1.1 ruff==0.16.10 mypy==2.4.0
```

Версиите са фиксирани нарочно: съобщенията на `ruff` и на `mypy` променят формулировката си между версиите, а със същите версии онова, което виждаш на екрана си, е онова, което виждаш тук. Това са актуалните към 7 октомври 2026 г. в [PyPI](https://pypi.org/project/pytest/), и същите са в `herramientas/requisitos.txt` на хранилището на курса. Това са инструменти за **разработка**: `revisor` не се нуждае от тях, за да работи, затова не влизат в списъка `dependencies` на `pyproject.toml`, който остава празен до Урок 9. Провери с `pytest --version`, `ruff --version` и `mypy --version`; ако някоя каже „command not found“ (командата не е намерена), виртуалната среда не е активна, същото препъване като в Урок 1.

## Понятията

### 8.1 `pytest`: изпълняване на кода ти с известни данни

#### 8.1.1 Първият тест

[`pytest`](https://docs.pytest.org/en/stable/getting-started.html) е програмата, която търси тестовете, изпълнява ги и ти връща отчет. Не идва с Python: това е инструмент на трета страна, най-използваният в езика. [Правилата му за намиране на тестове](https://docs.pytest.org/en/stable/explanation/goodpractices.html) са малко: търси файлове с име `test_*.py` или `*_test.py` и в тях изпълнява функциите, чието име започва с `test`. Всичко останало пренебрегва. Запомни това правило: по-нататък мълчаливото пренебрегване излиза скъпо.

Тестът подготвя входна стойност, извиква кода, който искаш да провериш, и завършва с `assert`. Започни с най-малкия, върху функцията `formatear_tiempo` от Урок 3. За да работи примерът сам, в един файл, функцията е копирана над тестовете си:

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

Двете функции отдолу са тестовете и се разпознават по името. Всяка съдържа по един `assert`, запазената дума, която значи „твърдя, че това е вярно“: [`assert condición`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) не прави нищо, ако условието е истина, а ако е лъжа, спира функцията с `AssertionError`. Извикваш и твърдиш: това е всичко, което трябва. Две подробности за формата. Имената са изречения, които казват **какво се очаква**: `test_sin_tiempo_va_una_raya` ти казва, в деня, когато почервенее, какво се е счупило, без да отваряш файла. А `-> None` казва, че функцията не връща нищо, като всеки тест: или свършва мълчаливо, или спира с грешка (в 8.4 ще видиш, че `mypy` в строг режим го изисква).

Този файл не се казва `test_*.py`, но когато подадеш на `pytest` името на файл, той го пуска, дори да не отговаря на шаблона. С активна среда:

```text
$ pytest -q fig08_01.py
..                                                                       [100%]
2 passed in 0.00s
```

Опцията `-q` (*quiet*, „тих“) иска кратък отчет. Първият ред има по една точка за всеки преминал тест и отдясно напредъка. Последният е обобщението: `2 passed`, „две преминаха“. **Това е редът, който ще се научиш да четеш със здравословно недоверие**: казва колко теста са се изпълнили и какво е станало с всеки.

#### 8.1.2 Да го видиш червен, преди да е зелен

Тест, който преминава, не казва много: преминава, ако кодът е наред, но и ако тестът не проверява нищо. Има само един начин да разбереш дали един тест проверява нещо: **да го видиш да се проваля**. От днес всеки тест го виждаш червен, преди да го приемеш за зелен. Ето дефекта от началото, написан във файл:

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

`clasificar` определя състоянието по кода и времето; тази съкратена версия връща текст. Има дефекта: използва `>` там, където правилото казва „хиляда милисекунди или повече“. Двата теста са въпросите от преди. Пусни го и виж също кода на изход:

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

Чети отчета отгоре надолу. `.F`: първият тест премина, а вторият се провали. Секцията `FAILURES` носи по един блок за всеки провал, с името на теста, неговия код и стрелка `>` на реда, който се е провалил. Редовете с `E` са грешката: `assert 'ARRIBA' == 'LENTO'`. Това е особеното на `pytest`: пренаписва твоите `assert`, така че при провал да покажат **двете сравнени стойности** ([документацията го обяснява](https://docs.pytest.org/en/stable/how-to/assert.html)); с гол `assert` би видял само `AssertionError`. Редовете с `-` и `+` разчленяват сравнението; в тази версия на `pytest` редът с `-` е стойността отдясно на `==` (`LENTO`, онова, което тестът е очаквал), а редът с `+` е тази отляво (`ARRIBA`, онова, което кодът е върнал). След това идват файлът и редът (`fig08_02.py:18`), обобщение от един ред за всеки провал, отрязано по ширината на терминала (затова свършва с `=...`), и броят: `1 failed, 1 passed`.

`echo $?` отпечатва **кода на изход** на предишната команда: числото, което всяка програма оставя при приключване, за да каже на системата как ѝ е минало. По конвенция `0` е „добре“, а всяко друго е „нещо се е провалило“. Използва го в Урок 7 с `revisor`. Тук `pytest` излезе с `1`, защото имаше провалени тестове. Скриптовете и инструментите за непрекъсната интеграция четат това число, за да решат дали продължават, или спират.

Поправката е да смениш `>` с `>=`:

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

Двата преминаха, код `0`. Обърни внимание на реда: първо въпросът (тестът за 1000), после червеното срещу кода с дефекта и чак тогава поправката. Този ред е гаранцията. Ако го беше написал **след** поправката, никога нямаше да знаеш дали е способен да засече дефекта. Когато добавяш тест към код, който вече работи, еквивалентът е да счупиш кода нарочно за миг, да видиш червеното и да върнеш промяната. Упражнение 1 го прави с истинския `revisor`.

#### 8.1.3 Броят се чете от отчета, не от кода на изход

Ето уловката, която дава име на едно от правилата на курса. [Документацията на `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) определя кодовете му на изход: `0`, всички тестове, **които са били събрани**, са преминали; `1`, някои са се провалили; `2`, потребителят е прекъснал; `3`, вътрешна грешка; `4`, грешка в употребата; `5`, не е бил събран нито един тест; `6`, надхвърлен е максималният брой предупреждения. Обърни внимание на фразата за `0`: „които са били събрани“. Тест, който `pytest` никога не е събрал, за него не съществува. Виж файл, където това се случва:

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

Има четири тестови функции и една уловка. Последната се казва `prueba_sin_respuesta_es_caido`, а не `test_...`, и `pytest` **не я вижда**. Нейният `assert` е нарочно лъжа (твърди, че липсата на отговор е `"ARRIBA"`), така че ако се изпълнеше, щеше да се провали. Пусни го; после поискай от `pytest` само да изброи онова, което е намерил (`--collect-only`), и да пусне само тестовете, чието име съдържа несъществуващ текст (`-k`):

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

Първият отчет казва `3 passed` и кодът на изход е `0`: зелено по цялата линия, с един счупен тест, който никой не е изпълнил. Табло, което гледа само кода на изход, би казало „всичко е наред“. Който чете отчета, вижда `3` и, ако е писал четири, се пита къде е отишъл четвъртият; `--collect-only` го потвърждава, защото изброява три. Случва се във всеки проект: с лошо наименувана функция, с файл, който не се казва `test_*.py`, или с преименуване, което е оставило тест вън. Последната команда показва другата крайност: `3 deselected` и код `5`, „не е събран нито един“. Там `pytest` е предупредил, но предупреждението се губи, ако скриптът ти свършва с `|| true` или ако по средата има филтър (`| tail`, `| grep`), който поглъща кода на изход. Оттам правилото:

> **Броят на тестовете се чете от отчета („N passed“). Едно `0` не е доказателство, че се е изпълнило онова, което си мислел. Винаги сравнявай N с N, което очакваш.**

`revisor` завършва този урок с 21 теста и това е числото, което ще проверяваш в края на всяка сесия. Урок 9 тръгва от него. Ако някой ден отчетът каже 20, няма значение, че е зелен: нещо е изчезнало. (Тестът може да се отбележи и като *пропуснат*, `skipped`, и тогава нито преминава, нито се проваля: само се появява в обобщението. В този курс не се използва; ако един тест не върши работа, поправя се или се изтрива.)

### 8.2 `parametrize`: таблица от случаи, един тест

`clasificar` прилага четири правила и има една граница (1000 ms), където се струпват грешките. За да я тестваш добре, са ти нужни **седем случая**: два бързи (142 и 999 ms, най-бавният, който още работи), два бавни (1000 ms, първият, който вече е такъв, и 2300), два паднали по код (503 и 404) и един без отговор (`None`, `None`). Написани като отделни функции, биха били седем функции, еднакви с изключение на две числа и един текст, със седем места за пипане в деня, когато правилото се промени.

Искаш да напишеш теста веднъж, а случаите като таблица. [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html) го прави. Знакът `@` въвежда **декоратор**: ред над една функция, който я променя (вече видя `@dataclass(frozen=True)` в Урок 5, върху клас). Тук казва на `pytest` да изпълни функцията по веднъж за всеки ред:

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

Първият аргумент е списъкът с **имената на параметрите**, които трябва да съвпадат с тези на функцията отдолу. Вторият е списъкът със **случаите**: по един кортеж за случай, със стойност за всяко име. `esperado` стои в таблицата, а не се изчислява вътре във функцията: ако тестът ползва същата формула като кода, който тества, две еднакви грешки ще се унищожат взаимно и тестът ще премине зелен върху дефект. Пусни го и изброй онова, което е събрал:

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

`7 passed`: `pytest` превърна функцията в **седем теста**, всеки с име, което носи в квадратни скоби стойностите на случая (`test_clasificar[200-1000-LENTO]`). Това име има значение, когато нещо се провали. Виж какво става, ако вмъкнеш дефекта с `>` в тази таблица:

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

`1 failed, 6 passed`, а редът `..F....` казва, че е бил третият ред. Името `test_clasificar[200-1000-LENTO]` е точният случай; под него `pytest` отпечатва стойностите на параметрите на **този** случай, а другите шест преминаха: ред, който се проваля, не спира останалите. Добавянето на случай е добавяне на един ред.

Сега проектът. Истинските тестове живеят в папка `tests/` до `src/`. Първият покрива `clasificar` със седемте случая, с истинския `Estado`:

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

Сравнява се с `is`, а не с `==`: членовете на един `Enum` са уникални и `is` пита за идентичността, като `is None` от Урок 2. И параметрите носят **анотации на тип**, като кода на пакета; в 8.4 ще видиш защо. Вторият покрива `formatear_tiempo` с четири случая: без време, едно в милисекунди, последното, което още е такова (999), и едно в секунди:

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

За да знае `pytest` къде да търси, без да му го казваш, `pyproject.toml` получава една секция (пълният файл е в 8.6):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` е списъкът с папки, където търси, когато го пуснеш без аргументи. В следващото редът `cd fig08_15` представлява „да си вътре в проекта“; ти вече си в `~/curso-python/revisor/`, така че не го пиши.

```text
$ cd fig08_15
$ pytest -q tests/test_modelo.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q tests/test_formato.py
....                                                                     [100%]
4 passed in 0.00s
```

Седем и четири: единайсет засега. Всеки отчет брои каквото трябва; ако сметнеш грешно, ще ти го каже.

### 8.3 `tmp_path` и `monkeypatch`: тестове, които не цапат и не зависят от нищо

`clasificar` и `formatear_tiempo` са чисти функции: получават стойности, връщат стойност и не докосват нищо извън себе си. Но `leer_servicios` чете файл, а `main` чете аргументи, отпечатва и извиква функцията, която пита услугите. Тестването на това поставя два проблема и `pytest` носи инструмент за всеки. И двата са *фикстури* (*fixtures*).

**Фикстура** е функция, която `pytest` изпълнява вместо теб преди един тест, за да му предаде нещо, от което се нуждае. Искаш я, като я декларираш като **параметър**: ако тестът ти е `test_algo(tmp_path)`, `pytest` вижда името, търси фикстура с такова име, изпълнява я и предава резултата като аргумент. Не я импортираш, нито я извикваш ([документацията го описва подробно](https://docs.pytest.org/en/stable/how-to/fixtures.html)).

#### 8.3.1 `tmp_path`: нова папка за всеки тест

За да провериш, че `leer_servicios` чете файл правилно, ти трябва файл. Ако тестовете ползваха `servicios.toml` от проекта ти, всяка промяна по този файл би счупила тестове, които нямат нищо общо с нея, а тест, който **пише**, би зацапал папката ти. Фикстурата [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html) предава `Path` (този от `pathlib`, от Урок 6), който сочи към **временна папка, нова и празна, единствена за този тест**:

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

Първият тест сглобява малък `servicios.toml` и проверява, че се броят две услуги. Вторият показва изолацията: получава **празна** папка, макар предишният току-що да е записал файл в своята. За да го провери, използва две неща от `pathlib`: `is_dir()` пита дали пътят е папка, която съществува, а `iterdir()` обхожда онова, което има вътре, по един елемент за всеки файл или подпапка. Тъй като `iterdir()` предава елементите един по един, а не списък, `list(...)` ги събира в списък (както направи с `list(tiempos_ms)` в Урок 4), а списъкът на празна папка е `[]`.

```text
$ pytest -q fig08_07.py
..                                                                       [100%]
2 passed in 0.01s
```

Папките живеят във временната директория на системата, а `pytest` пази тези от последните три изпълнения, ако искаш да огледаш какво е оставил един провален тест.

С това пишеш тестовете на `leer_servicios`: един, който чете валиден файл, и седем, които го отхвърлят. Три от седемте пазят онова, което видя в 6.4.3: `url mal formada` (с `http://[::1`, `urlsplit` хвърля `ValueError`, а тестът изисква да стигне като съобщение за конфигурация, а не като *traceback*; ако махнеш `try` от `es_url_http`, почервенява), `url con salto` (нов ред вътре в адреса; почервенява, ако махнеш `isprintable()`. В таблицата ще видиш `\\n`, с двойната черта: вътре в низ на Python `\\` пише обратна наклонена черта, така че файлът TOML получава `\n`, а TOML я превръща в истинския нов ред) и `url con acento` (`https://catálogo.example`; почервенява, ако махнеш `isascii()`). Седемте имат една и съща форма, затова отиват в таблица, с `ids=`, за да използва отчетът четими имена:

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

Валидният файл се сравнява със списък, който съдържа един `Servicio`; работи, защото `dataclass` се сравняват по съдържание. Тези за отхвърляне използват `with pytest.raises(ErrorDeConfiguracion) as informe:`, един `with` (този от Урок 6), който твърди обратното на обикновения `assert`: че кодът вътре **хвърля** това изключение. Ако блокът свърши, без да хвърли нищо, `pytest` отбелязва теста като провален с `DID NOT RAISE`. `as informe` пази изключението; `str(informe.value)` е съобщението, което написа в Урок 6, и тестът го сравнява цялото. Проверката на съобщението, а не само на типа, различава „провали се по правилната причина“ от „провали се по каквато и да е причина“.

#### 8.3.2 `monkeypatch`: промяна на нещо само докато трае тестът

`main` извиква `revisar_todos`, която днес чете `SIMULADO`, а от Урок 9 ще пита мрежата. За да тестваш само онова, което `main` прави с резултатите (какъв код на изход връща), удобно е да **подмениш** тази функция с фалшива. Фикстурата [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) съществува за това: `monkeypatch.setattr(destino, valor)` заменя един атрибут и **като свърши тестът, го оставя такъв, какъвто е бил**. Виж механизма в малък файл:

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

Има една променлива на модула, `UMBRAL_LENTO_MS`, и една функция, която я чете. Първият тест използва обичайния праг. Вторият **го променя на 3000 докато трае този тест**: `"fig08_08.UMBRAL_LENTO_MS"` е адресът на атрибута, във формата `módulo.nombre` (този модул се казва като файла, без `.py`); вътре в този тест 1500 вече не е бавно. Третият проверява, че след това прагът отново е бил 1000.

```text
$ pytest -q fig08_08.py
...                                                                      [100%]
3 passed in 0.00s
```

Трите преминаха, а важният е третият: промяната **не остава**. Присвояването на променливата на ръка би я оставило променена за следващите тестове и би дало провали, които зависят от реда, едни от най-трудните за разбиране.

Сега истинският тест. `main` връща `0`, ако всичко работи, и `1`, ако не. За да тестваш двата случая, без да зависиш от симулираните данни, подменяш `revisar_todos` с фалшива функция, която връща каквото ти решиш:

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

Преди тестовете константата `CONFIGURACION` е текстът на малък `servicios.toml`, между тройни кавички, като многоредовите текстове от Урок 6. Обратната черта веднага след отварящите кавички (`"""\`) не позволява текстът да започне с нов ред: в края на ред, вътре в текст, `\` значи „този ред продължава на следващия“, така че първият ред на текста е `[[servicios]]`, а не празен. На TOML би му било все едно, но така онова, което пише тестът, е точно онова, което виждаш.

Първият тест използва истинските симулирани данни с конфигурация, която включва `reportes`, която е паднала. Вторият подменя функцията с `todos_arriba`, дефинирана вътре в теста, защото само той я ползва, със същата сигнатура като истинската: когато `main` я извика, няма да знае, че е фалшива.

Вгледай се добре в целта: `"revisor.cli.revisar_todos"`, името **вътре в `cli`**, а не това на `revision`, където е дефинирана функцията. [Документацията на `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) го казва: трябва да се подмени референцията, която кодът ти използва. Инструкцията `from modulo import nombre` създава, вътре в модула, който импортира, собствено име, което сочи към същата функция: две имена за едно нещо, и подмяната на едното не променя другото. `cli.py` започва с `from revisor.revision import revisar_todos`, така че `main` търси `revisar_todos` сред имената на `cli`. Ако подмениш това на `revision`, `cli` ще продължи да вика истинската. В „Грешката, която ще видиш“ я чупиш нарочно.

С написаните четири файла пускаш **всичко заедно** за пръв път. Вече знаеш какво трябва да каже:

```text
$ cd fig08_15
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

Двайсет и една точки и `21 passed`: 7 + 4 + 8 + 2. Това число е договорът с Урок 9. **Тук свършва първата сесия.** Когато се върнеш, `pytest -q` е първото, което пускаш, за да знаеш, че си оставил проекта така, както си мислиш.

### 8.4 `mypy`: типове, които се проверяват, без да се изпълнява нищо

#### 8.4.1 Анотациите не се налагат при изпълнение

От Урок 3 пишеш анотации като `tiempo_ms: int | None`. Урок 0 каза, че **Python не ги използва при изпълнение**: те са информация за този, който чете, и за външни инструменти, не заповед. [PEP 484](https://peps.python.org/pep-0484/), който ги въведе, го казва без заобикалки: типовете не се проверяват по време на изпълнение. Вижда се с четири реда:

```python
# fig08_09.py
def doble(tiempo_ms: int) -> int:
    return tiempo_ms * 2


print(doble("142"))
```

Сигнатурата казва, че `doble` получава цяло число, а извикването ѝ подава текста `"142"`. Пусни го и поискай от `mypy` да го провери:

```text
$ python fig08_09.py
142142
$ mypy fig08_09.py
fig08_09.py:6: error: Argument 1 to "doble" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Python не се оплаква: `"142" * 2` е валидно (повтаря текста) и програмата отпечатва `142142`, абсурден резултат за време в милисекунди, за който никой не е предупредил. [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) чете файла **без да го изпълнява**, сравнява всяко извикване с анотациите и се оплаква. Съобщението му винаги има една и съща структура: `archivo:línea: error: descripción  [código]`. Казва къде (ред 6), какво (аргумент 1 на `doble` е `str`, а се е очаквал `int`) и, в квадратни скоби, кода на вида грешка (`arg-type`), полезен за търсене. Последният ред брои грешките и файловете.

Това е *постепенното типизиране* (*gradual typing*): ти решаваш колко анотираш, а `mypy` проверява онова, което си анотирал. Това е контрапартът на онова, което прави TypeScript в [нашия курс по TypeScript](https://www.habil.mx/bg/courses/typescript/): типовете се пишат и се проверяват преди изпълнение, но не са механизъм на езика по време на изпълнение.

#### 8.4.2 Какво хваща `mypy`: `None`, който си забравил

Най-честата грешка, която `mypy` намира, е да забравиш, че нещо може да е `None`. Услугата `reportes` не отговаря и нейното `tiempo_ms` е `None`: затова полето се анотира `int | None`. Ето функция, която го забравя (програмата улавя грешката сама, за да видиш съобщението без шум):

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

Python разбира едва когато стигне до второто извикване: `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`. Ако това извикване беше на път, който се минава веднъж месечно, грешката щеше да стигне до продукция. `mypy` я намира **без да пусне нищо**, на ред 3, и я обяснява: `Unsupported operand types for / ("None" and "int")` и една бележка, `Left operand is of type "int | None"`. Решението не е да заглушиш `mypy`, а да решиш какво трябва да стане, когато няма време. Тук, да върне и тя `None`, и да го каже в типа на връщане:

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

Функцията вече казва истината в сигнатурата си, `float | None`, и тази истина има последица: **всеки, който използва резултата, е задължен да провери дали е `None`**, защото `mypy` ще се оплаче, ако го третира като число. Вместо скрита грешка, която се появява призори, имаш неудобен въпрос в редактора си, който е точно мястото, където е удобно да го имаш.

#### 8.4.3 `match` и случаят, който липсва

В Урок 5 видя, че `match` заедно с `Enum` има предимство, което `mypy` използва тук. Представи си, че `revisor` получава четвърто състояние, `DEGRADADO`, и една функция, която превежда състоянията в цветове, остава без своя `case`:

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

Python **не предупреждава**: когато никой `case` не съвпадне, `match` свършва, без да направи нищо, функцията стига до края си без `return` и връща `None`. Четвъртият ред отпечатва `DEGRADADO -> None`, цвят, който не съществува, и в една истинска програма този `None` би пътувал до този, който го ползва. `mypy` го вижда, без да пуска нищо: сигнатурата обещава `str`, но има път (този на `DEGRADADO`), който свършва без да върне нищо, и затова казва `Missing return statement`. Съобщението не споменава члена, който липсва, но сочи функцията (`def semaforo`), и е достатъчно да сравниш нейните `case` с членовете на `Enum`, за да го намериш. Това е мрежата за безопасност, която обеща Урок 5: добавяш член, а `mypy` ти посочва всеки `match`, който е останал назад.

#### 8.4.4 Постепенно: онова, което не анотираш, `mypy` не проверява, освен ако не го поискаш

[Документацията на `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) го установява: функция без анотации се смята за динамично типизирана и по подразбиране `mypy` **не проверява тялото ѝ**. Това е дизайнерско решение, за да могат типовете да се добавят постепенно към стар код. Виж го с функция без нито една анотация:

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

Без опции `mypy` казва „Success“: `duplicar` няма анотации и не се проверява. С `--strict` същият файл дава две грешки: функцията няма анотации (`no-untyped-def`) и я викаш от код с типове (`no-untyped-call`). Строгият режим е пряк път, който включва наведнъж няколко проверки; [документацията ги изброява](https://mypy.readthedocs.io/en/stable/command_line.html): между тях `--disallow-untyped-defs` (всяка функция носи анотации), `--check-untyped-defs` (да се проверява и тялото на тези без анотации), `--warn-return-any` и `--warn-unused-ignores`. Точният списък може да се промени между версиите, затова урокът фиксира тази на `mypy`.

Правилото на курса: **проектът е в строг режим от самото начало**; много по-евтино е да поддържаш типовете, отколкото да ги добавяш после. Настройва се в `pyproject.toml`, [откъдето `mypy` го чете](https://mypy.readthedocs.io/en/stable/config_file.html):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`python_version` е срещу коя версия на Python да се проверява (тази на Mint от курса), `strict = true` включва строгия режим, а `files` казва какво да се проверява, когато го пуснеш без аргументи: пакетът и също тестовете, защото лошо типизиран тест крие грешки като всеки друг код.

#### 8.4.5 `mypy` в `revisor`

С поставената конфигурация целият проект се проверява с една команда. Целият код на пакета и на тестовете носи анотации (затова тестовете завършват с `-> None` и искат `tmp_path: Path`):

```text
$ cd fig08_15
$ mypy
Success: no issues found in 11 source files
```

`Success: no issues found in 11 source files`: седем файла на пакета (`__init__`, `__main__`, `cli`, `configuracion`, `formato`, `modelo` и `revision`) и четири на тестовете. Чети броя така, както се научи с `pytest`: ако някой ден каже `0 source files`, `mypy` не е проверил нищо и зеленото не струва. За да го видиш как работи върху проекта, направи Упражнение 3: смени една анотация и виж как `mypy` те води до тези, които я използват. Това е най-ценната му употреба: когато промениш сигнатурата на функция, той ти казва всички места, които трябва да нагодиш.

Едно предупреждение за аварийните изходи. `# type: ignore` казва на `mypy` да не се оплаква от този ред, а типът `Any` изключва проверките върху една стойност. Съществуват по законни причини (код на трети страни без типове) и са най-бързият начин да направиш инструмента безполезен. Правилото: **оплакването почти винаги е право**; преди да го заглушиш, разбери какво казва.

### 8.5 `ruff`: проверка и форматиране

Последният инструмент не знае нищо за твоя проблем, нито за твоите типове: чете кода като текст и прави две различни неща с две команди. [`ruff`](https://docs.astral.sh/ruff/) е една-единствена програма, която покрива двете роли:

- **`ruff check`** е *линтерът* (linter; на български „статичен анализатор“): търси познати грешки и лоши практики, като импорт, който не се ползва, или стойност по подразбиране, която се споделя между извикванията. [Всяка находка има код](https://docs.astral.sh/ruff/linter/) от една или две букви и три цифри (`F401`, `E711`).
- **`ruff format`** е *форматиращият инструмент*: пренаписва кода с единен формат (интервали, нови редове, кавички, къде се разчупва дълъг ред). [Имитира този на `Black`](https://docs.astral.sh/ruff/formatter/), стандарта на общността, така че кодът ти изглежда като този на всеки друг проект. Най-доброто е онова, което **ти отнема**: спорът за стила се решава веднъж и го изпълнява машината.

Виж и двата върху файл с истински дефекти. Разхвърлян е нарочно: единственият в курса, който е такъв.

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

Програмата работи (отпечатва двата списъка) и има поне пет неща наопаки. Тъй като си извън проекта и няма `pyproject.toml`, който да казва кои правила да се прилагат, ги подаваш с `--select`; `--output-format concise` иска по един ред за находка:

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

Второто извикване отпечата `['catalogo', 'pagos']`: дефектът от Урок 3 в действие. Стойността по подразбиране `lista=[]` се **споделя** между извикванията, а `ruff` я вижда предварително като `B006`. Седем са находките, всяка с `archivo:línea:columna: CÓDIGO descripción`. Буквата на кода е името на колекцията от правила, която избираш с `select`:

| Буква | Какво следи | Пример отгоре |
|---|---|---|
| `E` | Стил ([pycodestyle](https://peps.python.org/pep-0008/), официалното ръководство) | `E401` няколко импорта на един ред; `E711` сравнение с `None` чрез `==` |
| `F` | Прости логически грешки ([Pyflakes](https://docs.astral.sh/ruff/rules/unused-import/)) | `F401` три неизползвани импорта |
| `I` | Редът на импортите | `I001` разбъркан блок |
| `B` | Познати уловки ([bugbear](https://docs.astral.sh/ruff/rules/mutable-argument-default/)) | `B006` изменяема стойност по подразбиране |
| `UP` | Осъвременяване на синтаксиса до твоята версия на Python | (нито един в този файл) |

Документацията [препоръчва да се започне с малко правила](https://docs.astral.sh/ruff/linter/) (`E` и `F`), да се добавят групи по една и да се избира със `select`, за да е наборът явен и да не се променя сам при обновяване. Тези пет са наборът на `revisor`.

Маркировката `[*]` казва, че `ruff` знае да оправи находката сам; обобщението брои пет находки с поправка, а други две имат *несигурни* поправки, които биха могли да променят какво прави програмата (като тази на `B006`). `ruff` прилага само сигурните, освен ако не му кажеш друго. `ruff format --check` е въпросът „форматиран ли е?“: отговори, че не, и показва какво би променил. За да видиш какво би направил всеки, без да докосва файла, съществува `--diff`:

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

Първият показва сигурната поправка: изтриване на двата реда с импорти, които са излишни изцяло. Обърни внимание, че казва `Would fix 4 errors`, а не пет: петте находки с `[*]` са на същите два реда и поправките им се застъпват. При прилагане на тези на `F401`, които изтриват неизползваните импорти, редът изчезва и друга от поправките (разделянето на `os` и `sys`, или подреждането им) вече няма какво да прави. Затова си струва да гледаш `--diff`, а не само да броиш маркировки. `== None` и стойността по подразбиране остават, защото поправките им са несигурни: на теб се пада да решиш. Вторият показва какво би направил форматиращият инструмент: два празни реда между функциите, конвенцията. Това, което прави `ruff format`, е механично и не променя какво прави програмата.

#### 8.5.1 В проекта: конфигурацията

Правилата се пишат веднъж в `pyproject.toml`, като тези на `pytest` и `mypy`, и тогава `ruff check` и `ruff format` не се нуждаят от аргументи:

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`target-version` казва за коя версия на Python пишеш: 3.12 на Mint, най-старата, която курсът допуска. Има значение: `ruff` решава с нея кое е „стандартна библиотека“ при подреждане на импортите (`tomllib` е такава от 3.11) и какъв модерен синтаксис да предлага. В този проект, ако не я беше написал, [`ruff` би я взел](https://docs.astral.sh/ruff/settings/#target-version) от `requires-python = ">=3.12"`, в `[project]`, което казва същото; пише се, за да е на показ до правилата. Без нито едното, `ruff` предполага 3.10 и с нея `tomllib` вече не би бил стандартна библиотека и би свършил в блока на пакетите от трети страни. `select` отива в подсекцията `[tool.ruff.lint]`, [както го документира `ruff`](https://docs.astral.sh/ruff/configuration/).

```text
$ cd fig08_15
$ ruff check
All checks passed!
$ ruff format --check
11 files already formatted
```

`All checks passed!` и всички файлове вече форматирани. Ако пуснеш `ruff check` върху код, който още не е минал през форматиращия инструмент, обичайно е да се оплаче от `E501` (ред над 88 знака) и един `ruff format` да ги реши почти всички, защото разпределя на няколко реда дългите извиквания и списъци. Затова редът е винаги един и същ: **първо `ruff format`, после `ruff check`**. И ако някое правило на линтера ти се струва прекалено, честният отговор е да го обсъдиш и да го махнеш от `select` с причина, а не да го криеш с коментар на всеки ред.

### 8.6 Целият проект

Снимката на проекта в края на урока е пакетът от Урок 7 с `version = "0.7.0"`, папката `tests/` (четири файла, които вече видя) и три нови секции с конфигурация. Пълният `pyproject.toml`:

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

Новото спрямо Урок 7 са версията и последните три секции. Останалите файлове **не се променят**; повтарят се тук само за да е пълен проектът и да можеш да сравняваш със своите, ако нещо не съвпада:

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

Инсталирай го отново с `pip install -e .`, за да види средата новата версия. От днес, всеки път, когато завършиш промяна, повтаряш този ритуал, в този ред:

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

## Грешката, която ще видиш

### `ModuleNotFoundError: No module named 'revisor'`

Първата, в която се препъва този, който отваря проекта в нова среда. Тестовете импортират пакета (`from revisor.modelo import clasificar`), а пакетът **не е инсталиран** в средата, която пуска `pytest`. Отчетът не започва с точки, а с блок `ERRORS`: грешката е възникнала при *събирането* на файла, преди да се изпълни нещо. Съкратена версия (дългите пътища на `importlib` са заменени с `...`):

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

Чете се отдолу нагоре: последният ред с `E` е причината, предишният казва кой ред я е предизвикал (`from revisor.cli import main`, ред 6 на `test_cli.py`), а междинните стъпки, от `importlib`, не ти вършат работа. Обобщението брои четири грешки, по една на файл, и не казва `0 passed`. Поправката е `pip install -e .` от папката, която има `pyproject.toml`: проектът е наред, липсва само да се инсталира.

### `fixture 'tmp_pth' not found`

Това се случва, ако напишеш грешно името на една фикстура, `tmp_pth` вместо `tmp_path`. Тъй като `pytest` я търси по името на параметъра, име, което не съществува, е грешка на `pytest`, а не на Python:

```text
___________________________ ERROR at setup of test_x ___________________________
file tests/test_x.py, line 4
  def test_x(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: anyio_backend, anyio_backend_name, ... tmp_path, ...
>       use 'pytest --fixtures [testpath]' for help on them.
```

Погледни заглавието: `ERROR at setup`, не `FAILED`. Тестът дори не стигна да се изпълни: провали се при *подготовката*. Съобщението ти предлага наличните фикстури (тук съкратени) и там е `tmp_path`. (`anyio_*` се появяват, защото `httpx`, който инсталира в Урок 1, носи приставка за `pytest`; не те засягат.)

### Червеният тест, който подменя грешното място

Най-поучителният, защото не е синтактичен, а на разсъждение. В `tests/test_cli.py` смени целта на `monkeypatch` от `revisor.cli.revisar_todos` на `revisor.revision.revisar_todos`, където е дефинирана функцията, и пусни тестовете. Истински отчет, съкратен:

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

Редът `E` казва `assert 1 == 0` и, отдолу, че `main` е върнал `1`. Секцията `Captured stdout call` (онова, което кодът е отпечатал по време на теста, което `pytest` пази и показва само ако се провали) носи решаващата следа: **`reportes` се появява паднала, с обичайните данни**. Подмяната не е имала ефект, защото `cli` е продължил да ползва собственото си копие на `revisar_todos`. Поуката е тази на документацията: подменяй името **там, където се използва**. Върни промяната, преди да продължиш.

## Какво се прави погрешно

**Да напишеш тест, който не може да се провали.** `assert clasificar(200, 142) is not None` винаги преминава, защото `clasificar` никога не връща `None`. Това е причината за навика от 8.1.2. Цена: мрежа с дупка колкото теста и фалшивото спокойствие на зеленото.

**Да оставиш теста да изчисли отговора с формулата на кода.** `assert formatear_tiempo(2300) == f"{2300 / 1000:.1f}s"` повтаря реализацията: ако формулата е грешна, тестът я копира. Очакваното се пише на ръка, като данни: `"2.3s"`.

**Да копираш сегашния изход като очаквана стойност, без да го гледаш.** Пускаш кода, виждаш, че връща `'ARRIBA'`, и го пишеш в теста, защото „това излиза“. Ако е било грешно, превърнал си дефекта в спецификация и тестът го защитава. Очакваното идва от правилото, никога от онова, което кодът прави днес.

**Да гледаш само кода на изход.** Това е 8.1.3: едно `0` не брои колко теста са се изпълнили.

**Да подменяш там, където е дефинирана функцията, а не там, където се използва**, или да подменяш толкова, че тестът вече не упражнява истински код. Ако всичко вътре в `main` е фалшиво, единственото, което тестваш, е фалшивото.

**Да заглушиш `mypy` с `# type: ignore` или с `Any`, за да „мине“.** Оставяш дефекта и махаш предупреждението. Ако има истинско изключение, то носи коментар, който обяснява защо.

**Да анотираш наполовина.** Функция с анотации на два параметъра и без тях на третия не остава извън проверката: `mypy` проверява тялото ѝ, но параметърът без анотация е `Any`, „каквото и да е“, и всичко, което правиш с него, минава без въпроси. При `strict = true`, освен това, `mypy` го отбелязва като `[no-untyped-def]`. Или всичко, или нищо; в този курс, всичко.

**Да се бориш с форматиращия инструмент.** Да преформатираш на ръка онова, което `ruff format` вече е решил, или да изключиш правило от мързел да го разбереш.

**Тестове, които зависят от реда, от диска или от мрежата.** Тест, който чете истинския `servicios.toml`, или който преминава само ако друг се е изпълнил преди него, се проваля на друга машина без обяснение. С `tmp_path` и `monkeypatch` всеки тест си стига сам.

## Упражнения

### Упражнение 1 — Счупи, виж червеното, поправи

В `src/revisor/modelo.py` смени `>=` от `if tiempo_ms is not None and tiempo_ms >= umbral_ms:` на `>`. Преди да пуснеш, **предвиди**: колко теста ще почервенеят и кой? Пусни `pytest -q`. После пусни `python -m revisor` и сравни таблицата с обичайната. Върни промяната и пусни отново. Запиши в дневника си числото от отчета преди и след и какво те е научила таблицата.

### Упражнение 2 — Нов тест за кода на изход 2

`main` връща `2`, когато конфигурационният файл не съществува. Напиши в `tests/test_cli.py` тест, който го проверява: извикай `main(["--config", ...])` с път вътре в `tmp_path` към файл, който не си създал, и твърди, че резултатът е `2`. Преди да го оставиш, **провери, че може да се провали**: как би го направил червен нарочно? Отчетът трябва да каже `22 passed`. Изтрий го накрая (Урок 9 тръгва от 21) и провери, че пак казва 21.

### Упражнение 3 — Нека `mypy` те заведе до този, който вика

В `src/revisor/formato.py` смени `def formatear_tiempo(tiempo_ms: int | None) -> str:` на `def formatear_tiempo(tiempo_ms: int) -> str:`, без да пипаш нищо друго. Пусни `mypy`. Колко грешки излизат и в кои файлове? Защо има една в `tests/test_formato.py`, който не си пипал? Върни промяната.

### Упражнение 4 — Тестът, който липсва

Има промяна от един знак във `formatear_tiempo`, която 21-те теста **не** засичат. Границата от хиляда милисекунди има своя случай в `clasificar`, но това е същата граница. Смени `if tiempo_ms < 1000:` на `if tiempo_ms <= 1000:` и пусни `pytest -q`: зелено или червено? Ако е зелено, напиши липсващия случай в таблицата на `tests/test_formato.py`, провери, че сега почервенява, върни промяната в кода и **изтрий** новия случай, за да се върне проектът на 21, числото, с което започва Урок 9.

## Решения

### Решение 1

Вярната прогноза е **един** червен тест: `test_clasificar[200-1000-Estado.LENTO]`. Никой друг не докосва точно 1000. Истински отчет, съкратен:

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

`1 failed, 20 passed` прави 21: общият брой си е там. А таблицата на `python -m revisor`, с поставения дефект, **излиза същата** като обикновено: гледането на таблицата не намира дефекта, тестът го намира. Когато върнеш промяната, отчетът се връща на `21 passed`.

### Решение 2

```python
def test_sin_archivo_de_configuracion_sale_con_2(tmp_path: Path) -> None:
    inexistente = tmp_path / "no-existe.toml"
    assert main(["--config", str(inexistente)]) == 2
```

За да го видиш червен, смени `2` с `0` и пусни: трябва да се провали с `assert 2 == 0`, което доказва, че гледа истинския код на изход. С добрата версия, `22 passed`. Като го изтриеш, трябва да се върне `21 passed`; ако не, нещо е останало във файла.

### Решение 3

Излизат **три** грешки, в два файла (`Found 3 errors in 2 files (checked 11 source files)`):

```text
src/revisor/formato.py:23: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
src/revisor/formato.py:47: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
tests/test_formato.py:17: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
```

Първата е в `linea`, която му подава `resultado.tiempo_ms`, един `int | None`. Втората е в `resumen`, която му подава средното, което също може да е `None`, когато нито една услуга не е отговорила. Третата е тестът: параметърът му `tiempo_ms` е `int | None` (таблицата включва `None`) и вика функцията с него. И трите са един и същ проблем, видян от три места, а този със средното може дори да не си го помнил: `mypy` ти го показа, без да го търсиш. Когато върнеш промяната, се връща `Success: no issues found in 11 source files`.

### Решение 4

Промяната **преминава зелена** (`21 passed`): нито един от четирите реда не използва 1000 (има `None`, 87, 999 и 2300). С `<=` 1000 би излязло като `1000ms` вместо `1.0s` и никой нямаше да забележи. Липсващият случай:

```python
        (1000, "1.0s"),
```

С него мутацията почервенява (`test_formatear_tiempo[1000-1.0s]` ти казва кой е). В твой проект би го запазил без да мислиш; тук го изтриваш само по причина от календара: Урок 9 сравнява броя си с 21. Онова, което това решение иска да ти остави, е въпросът: **зелен набор от тестове не казва, че кодът е наред, казва, че въпросите, които си му задал, имат отговор**. Върни поправката и провери, че почервенява: това е методът.

## Как разбирам, че съм успял

- [ ] `pytest -q`, от корена на проекта, завършва с `21 passed` (числото, не само зеленото).
- [ ] `mypy` завършва с `Success: no issues found in 11 source files`.
- [ ] `ruff check` казва `All checks passed!` и `ruff format --check` казва, че 11-те файла вече са форматирани.
- [ ] Смени `>=` на `>` в `clasificar`, `pytest -q` каза `1 failed, 20 passed` и когато върна промяната, се върна на `21 passed`.
- [ ] Можеш да обясниш защо `echo $?` равно на `0` не ти казва колко теста са се изпълнили и какво прави `--collect-only`.
- [ ] Можеш да обясниш защо `monkeypatch.setattr` сочи към `revisor.cli.revisar_todos`, а не към `revisor.revision.revisar_todos`.
- [ ] `pyproject.toml` има трите секции (`[tool.pytest.ini_options]`, `[tool.ruff]` с неговата `[tool.ruff.lint]` и `[tool.mypy]`) и `version = "0.7.0"`.

## Обобщение

Отговори, без да гледаш урока:

1. Как `pytest` разпознава кое е тест и какво става с функция, наречена `prueba_algo`?
2. Защо се вижда един тест червен, преди да се приеме зелен?
3. Какви кодове на изход има `pytest` за „всичко премина“, „някой се провали“ и „не е събран нито един“? Защо броят се чете от отчета?
4. Какво ти спестява `@pytest.mark.parametrize` и как разбираш кой ред се е провалил?
5. Какво е фикстура и какво предават `tmp_path` и `monkeypatch`?
6. Защо `monkeypatch.setattr` сочи към `revisor.cli.revisar_todos`?
7. Какво значи, че типизирането в Python е постепенно, и какво се променя със `strict = true`?
8. Каква е разликата между `ruff check` и `ruff format` и защо вторият се пуска първи?

## За допълнително четене

- [pytest, „Get Started“](https://docs.pytest.org/en/stable/getting-started.html) — официалното ръководство, с правилата за откриване и четенето на отчета; на английски, както почти цялата документация на екосистемата. Посетено на 7 октомври 2026 г.
- [mypy, „Getting started“](https://mypy.readthedocs.io/en/stable/getting_started.html) — какво е динамичното и статичното типизиране и как да въведеш типове в съществуващ код. Посетено на 7 октомври 2026 г.
- [Ruff, „The Ruff Linter“](https://docs.astral.sh/ruff/linter/) — как се избират правила, какво значат кодовете и какво е сигурна поправка. Посетено на 7 октомври 2026 г.
- [PEP 484, „Type Hints“](https://peps.python.org/pep-0484/) — документът, който въведе анотациите на тип и уточнява, че не се проверяват при изпълнение. Посетено на 7 октомври 2026 г.
