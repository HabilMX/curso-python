# Урок 9 — HTTP и asyncio

**Време:** 2 × 90 минути (първата сесия стига до края на 9.2; втората обхваща 9.3, 9.4 и 9.5)

**Какво изграждаш:** `revisor`, който проверява истински услуги, една след друга, с времеви лимит (timeout) за всяка заявка

**Какво научаваш:** да поискаш страница с `urllib` и с `httpx`; какво казва един код на състоянието; защо всяка заявка има времеви лимит; корутини (`async def`, `await`, `asyncio.run`, `async with`); и защо един `await` сам, без никой друг, не прави нищо по-бързо

**Откъде идваш.** Носиш пакета от [Урок 8](08-pruebas-tipos-calidad.md): `revisor` с 21 теста, с проверени типове и с наблюдаван стил. Но в този пакет има една неудобна истина: **той никога не е питал никого**. Цифрите в таблицата (142 ms, 2.3 s, 87 ms) идват от един речник, `SIMULADO`, който ти самият си написал; програмата ти връща това, което си ѝ казал да каже. Днес го заменяш с истинска проверка: `revisor` праща заявка към всяка услуга, засича колко време ѝ трябва да отговори и класифицира това, което получава. За да се упражняваш, без да безпокоиш никоя истинска услуга, урокът ти дава учебен сървър, който работи на твоя собствен компютър.

**Какво не прави този урок.** Още не проверява услугите **едновременно**: прави го една след друга, а урокът те учи да измериш колко струва това. Обединяването им е [Урок 10](10-concurrencia-pruebas-sin-red.md). А новият код, този, който ползва мрежата, **няма тест**: проектът продължава да има 21-те теста от Урок 8, и урокът ти го казва направо, вместо да го крие. Как се тества мрежов код без мрежа е темата на Урок 10.

## След урока ще можеш да

- Обясниш какво е HTTP заявка, какво съдържа един отговор и какво означават кодовете на състоянието `2xx`, `4xx` и `5xx`.
- Поискаш адрес с `urllib.request` и с `httpx` и да кажеш с какво се различават, когато сървърът отговори `503` и когато не отговаря.
- Обясниш защо `urllib` приема адрес `file://` и защо валидацията от Урок 6 пречи на `revisor` да чете файлове от твоя компютър.
- Зададеш времеви лимит на една заявка и да знаеш кое изключение се хвърля, когато той изтече, и кое — когато няма към кого да се обърнеш.
- Напишеш корутина с `async def`, да я изпълниш с `asyncio.run`, да изчакаш друга с `await` и да обясниш защо извикването на една корутина **не** я изпълнява.
- Измериш с часовника, че проверката на услугите една след друга отнема сбора от времената им, и да обясниш защо един `await` сам не я ускорява.
- Прочетеш предупреждението `coroutine ... was never awaited` и съобщението на `mypy` „Maybe you forgot to use "await"?“.

## Защо, преди как

Представи си, че питаш колега в офиса дали платежната система работи. Той трябва да направи нещо подобно на това, което прави браузърът ти, когато отвориш страница: да попита онази машина за един адрес и да изчака отговора. Въпросът се нарича **заявка**, а отговорът — **отговор**. И двете следват общ език, **HTTP**, който се използва в целия уеб. Една заявка казва, всъщност, „дай ми това, което има на този адрес“ (методът `GET`, плюс адресът). Един отговор носи три неща: **код на състоянието**, трицифрено число, което обобщава как е минало всичко; **заглавни части** (headers), данни за отговора (какъв вид съдържание е, колко е голямо); и **тяло**, самото съдържание.

Най-важното за теб в отговора е кодът, а първата му цифра го класифицира. [Стандартът на HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) ги групира в пет семейства: `1xx` са информационни, `2xx` означават, че всичко е минало добре (`200` е „заповядай“), `3xx` са пренасочвания, `4xx` са грешки на този, който пита (`404`: този адрес не съществува) и `5xx` са грешки на сървъра (`503`: в момента не мога да те обслужа). За `revisor` една услуга може да завърши по **три** различни начина и всеки свършва в един ред на таблицата:

| Какво се случи | Какво вижда `revisor` | Как се записва в таблицата |
|---|---|---|
| Услугата отговори с код под 400 (`2xx` или `3xx`) | код и време | `ARRIBA`, или `LENTO`, ако е отнело 1000 ms или повече |
| Отговори с код `4xx` или `5xx` | код и време | `CAIDO`, с кода в детайла (`503`) |
| Не отговори | изключение: не е могло да се свърже или времето е изтекло | `CAIDO`, със `sin conexión` (без връзка) или `tiempo agotado` (времето е изтекло) |

`3xx` попадат в първия ред нарочно. Едно пренасочване казва „това, което търсиш, е на друг адрес“, а `httpx` [не го следва по подразбиране](https://www.python-httpx.org/quickstart/#redirection-and-history): връща отговора такъв, какъвто е, с неговия код. За `revisor` фактът, че една услуга отговаря с пренасочване, значи, че е жива и отговаря, а правилото, както винаги (паднала само при `400` или повече), я брои като работеща, с кода в детайла, за да го видиш.

Тази таблица е целият дизайн на урока. (HTTP е най-разпространеният стил, по който две програми си говорят, но не е единственият; ако те интересува какво следва след „поискай един адрес и прочети какво отговаря“, блогът на Hábil сравнява два стила в [REST или gRPC: кога кое да изберем](https://www.habil.mx/bg/blog/rest-or-grpc-when-to-use-each/).) Останалото е как се изпълнява всеки ред, без програмата да се срине: третият най-вече, защото услуга, която не отговаря, е точно случаят, заради който съществува `revisor`, и не може да бъде случаят, който го събаря.

Урокът има две половини. В първата сесия правиш една добре направена проверка: първо с библиотеката, която идва с Python, `urllib`, за да видиш как изглежда една заявка отвътре, а после с `httpx`, тази, която ползва курсът. Научаваш, че **всяка заявка има времеви лимит**. Във втората сесия стигаш до **корутините**, инструмента на Python за чакане, без да стоиш неподвижен, и пускаш `revisor` да проверява истински. Това е най-големият концептуален скок в курса; затова ритъмът на този урок е бавен нарочно.

### Учебният сървър

`revisor` има нужда от някого, когото да пита. Имената `catalogo.example` или `pagos.example`, които използва досега, са измислени адреси: суфиксът `.example` е [запазен за примери](https://www.rfc-editor.org/rfc/rfc2606) и никога не съществува в интернет. За да може всяка услуга да отговаря истински и винаги по един и същи начин, урокът включва `laboratorio.py`, малък сървър, който работи **на твоя компютър** и се прави на услугите от курса.

Ето целия файл. **Приеми го като черна кутия: ползва се, не се пише.** Построен е с клас и методи, неща, които този курс не преподава, и да го разбереш не е нужно за нищо от следващото. Копирай го както е в `~/curso-python/revisor/laboratorio.py`. Когато завършиш курса, можеш да се върнеш да го прочетеш; библиотеката, която ползва, [`http.server`](https://docs.python.org/3/library/http.server.html), е част от Python.

```python
# fig09_11/laboratorio.py
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

Важното в него е какво отговаря всеки маршрут, което казват таблицата `RUTAS` и функцията `buscar_ruta`. (Класът `Servidor` променя само едно число, `request_queue_size`: колко връзки могат да чакат ред едновременно, за да бъдат обслужени. Стойността по подразбиране, 5, е твърде малка, когато в Урок 10 `revisor` отвори двайсет връзки наведнъж, а тези, които не се побират в опашката, биха били отхвърлени, все едно услугата е паднала.)

| Маршрут | Какво отговаря | Колко време отнема |
|---|---|---|
| `/catalogo` | `200` | 142 ms |
| `/inventario` | `200` | 2300 ms |
| `/pagos` | `200` | 87 ms |
| `/facturacion` | `503` | 95 ms |
| `/notificaciones` | `200` | 10 секунди |
| `/espera/<ms>` | `200` | милисекундите, които поставиш на мястото на `<ms>` |

Това са същите числа като в таблицата от учебната програма, но вече произведени от истински сървър. Адресът е `127.0.0.1`, което значи „този същия компютър“, така че всичко, което се случва в урока, не напуска твоята машина. Има само едно изключение и почти сигурно не те засяга: ако в твоя терминал е настроен **прокси** (посредник, през който минават заявките, обичаен в някои офис мрежи, и който си проличава по това, че съществуват променливи като `HTTP_PROXY` или `ALL_PROXY`, с главни или малки букви; `env | grep -i proxy` ти ги показва), заявките към `127.0.0.1` също отиват към проксито и упражнението се проваля. `httpx` зачита `HTTP_PROXY`, `HTTPS_PROXY` и `ALL_PROXY`; `urllib` — само първите две. Поправя се, като им кажеш, че този адрес не минава през проксито, с `export NO_PROXY=127.0.0.1` във всеки терминал, в който пускаш програмите; [документацията на `httpx`](https://www.python-httpx.org/environment_variables/) обяснява тези променливи. Портът `8099` е „номерът на гишето“, на което слуша. И има нарочен капан: порт **`8098` не се обслужва от никого**. Там живее услугата `reportes`: да питаш гише, където няма никого, е най-вярният начин да симулираш паднала услуга и излиза винаги по един и същи начин.

Преди всяко упражнение в този урок включи сървъра **във втори терминал** (с активирана виртуална среда, от `~/curso-python/revisor/`) и го остави отворен:

```text
laboratorio en http://127.0.0.1:8099 (Ctrl+C para detenerlo)
```

Този ред е единственото, което отпечатва; когато приключиш с упражненията, `Ctrl`+`C` в онзи терминал го спира. Ако по грешка го оставиш изключен, ще видиш какво става: описано е в раздела „Грешката, която ще видиш“. В обичайния терминал продължаваш да пускаш програмите от урока.

## Понятията

### 9.1 HTTP: поискай един адрес и прочети какво отговаря

#### 9.1.1 С библиотеката, която Python вече носи

`urllib.request` идва с Python; не е нужно да инсталираш нищо. Основната ѝ функция, [`urlopen`](https://docs.python.org/3/library/urllib.request.html), получава адрес, прави заявката и връща отговора като обект, който може да се ползва с `with` (същият `with` от Урок 6, който затваря връзката накрая). Поискай каталога от учебния сървър:

```python
# fig09_01.py
import time
from urllib.request import urlopen

inicio = time.perf_counter()
with urlopen("http://127.0.0.1:8099/catalogo") as respuesta:
    print(respuesta.status, respuesta.reason)
    cuerpo = respuesta.read()
print(cuerpo)
print(cuerpo.decode("utf-8"))
tardo_ms = (time.perf_counter() - inicio) * 1000
print(f"tardó 142 ms o más: {tardo_ms >= 142}")
```

```text
$ python fig09_01.py
200 OK
b'ok'
ok
tardó 142 ms o más: True
```

Ред по ред. `respuesta.status` е кодът на състоянието, `200`, а `respuesta.reason` е фразата, която го придружава, `OK`. `respuesta.read()` връща тялото, а това, което излиза на втория ред, `b'ok'`, има отпред една `b`, която си струва да се обясни: мрежата не пренася текст, а **байтове**, числа от 0 до 255, и `read()` ти ги предава както са. За да ги превърнеш в текст, трябва да кажеш с какво кодиране са записани, а то е същото UTF-8 от Урок 6: `cuerpo.decode("utf-8")` дава обикновения `str`, `ok`. Последният ред проверява времето. [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) е високоточният часовник на Python: връща секундите като десетично число, а изваждането на две отчитания дава колко е траело това, което е между тях. Сървърът отделя 142 ms, за да отговори с каталога, така че заявката не е могла да отнеме по-малко. Отпечатването на точното време би накарало всяко изпълнение да даде различно число; `True` е това, което не се променя.

Забележи какво **липсва** в тази програма: никакъв времеви лимит. Ще го поправиш в 9.2, но запиши си го от сега като висящо обещание.

#### 9.1.2 Кодовете на състоянието и двете изключения на `urllib`

Да поискаш каталога е щастливият случай. `revisor` трябва да преживее другите два: услугата, която отговаря с грешка, и тази, която не отговаря. Тази програма проверява по една от всеки вид:

```python
# fig09_02.py
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DIRECCIONES = {
    "catalogo": "http://127.0.0.1:8099/catalogo",
    "facturacion": "http://127.0.0.1:8099/facturacion",
    "reportes": "http://127.0.0.1:8098/",
}

for nombre, direccion in DIRECCIONES.items():
    try:
        with urlopen(direccion) as respuesta:
            print(nombre, "respondió", respuesta.status)
    except HTTPError as error:
        print(nombre, "respondió con un error", error.code)
    except URLError as error:
        print(nombre, "no se pudo conectar:", type(error.reason).__name__)
```

```text
$ python fig09_02.py
catalogo respondió 200
facturacion respondió con un error 503
reportes no se pudo conectar: ConnectionRefusedError
```

`catalogo` излезе, както се очакваше. Но `facturacion`, която отговаря `503`, **не върна отговор: хвърли изключение**, `HTTPError`, и затова влезе в първия `except`. Това е дизайнерско решение на `urllib`, което отначало изненадва: за тази библиотека код `4xx` или `5xx` е изключение, а кодът, който носи, се чете в `error.code`. А `reportes`, където никой не слуша, хвърли `URLError`, което носи в `error.reason` истинската причина. Тук това е `ConnectionRefusedError` (връзката е отказана). Забележи, че програмата отпечатва само **името** на причината, `type(error.reason).__name__` (`type` дава класа на стойността, този от Урок 2, а `__name__` — неговото име като текст), а не съобщението. Съобщението на операционната система се променя между компютрите (в Linux казва `[Errno 111]`, в macOS `[Errno 61]`), а курсът реши, че детайлът, който показва `revisor`, никога да не бъде този текст: казва `sin conexión` (без връзка), еднакво навсякъде.

**Редът** на `except` е важен и е същият проблем от Урок 6. [`HTTPError` е подклас на `URLError`](https://docs.python.org/3/library/urllib.error.html): всеки `HTTPError` е също и `URLError`. Ако сложиш `except URLError` първи, той щеше да хване всичко и `except HTTPError` отдолу никога нямаше да се изпълни. Правилото е същото както винаги: **най-конкретното първо**.

#### 9.1.3 Адрес, който не е от интернет: `file://`

В `urlopen` има една изненада и тя е свързана със сигурността. Един адрес започва със **схема**, частта преди `://`: `http`, `https`, а също и `file`, което значи „файл от този същия компютър“. `urlopen` разбира схемата `file`:

```python
# fig09_03.py
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

archivo = Path("secreto.txt")
if archivo.exists():
    raise SystemExit("ya existe secreto.txt en esta carpeta; este ejemplo no lo pisa")
archivo.write_text("contraseña: 12345\n", encoding="utf-8")
direccion = archivo.resolve().as_uri()

with urlopen(direccion) as respuesta:
    print("urlopen leyó:", respuesta.read().decode("utf-8").strip())

esquema = urlsplit(direccion).scheme
print("esquema:", esquema, "| lo acepta el revisor:", esquema in {"http", "https"})
archivo.unlink()
```

```text
$ python fig09_03.py
urlopen leyó: contraseña: 12345
esquema: file | lo acepta el revisor: False
```

Програмата създава файл `secreto.txt` (и го изтрива накрая с `unlink()`, за да не остави нищо). Тъй като ще го презапише и после ще го изтрие, преди това проверява дали вече не съществува файл с това име: ако съществува, спира, без да го докосне, с `raise SystemExit(...)`, същото изключение от Урок 7, което този път носи текст вместо число; Python отпечатва този текст в изхода за грешки и завършва с код 1. После взема абсолютния път на файла с `resolve()`, съставя адреса му с [`.as_uri()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.as_uri) (който създава нещо като `file:///home/tu/secreto.txt`) и го подава на `urlopen`, който **го чете без да възразява**. Това е легитимна функция, но си представи `revisor` да чете адреси от един `servicios.toml`, написан от някой друг, и някой да сложи `file:///etc/passwd` вместо адреса на някоя услуга: програмата би прочела файла и би го третирала като „отговор“. Затова в Урок 6 валидацията изискваше схемата да е `http` или `https`, с [`urlsplit(url).scheme`](https://docs.python.org/3/library/urllib.parse.html) в `{"http", "https"}`; последният ред на тази програма прави същата проверка и отговаря `False` за `file`. Това не е стилова подробност: **адресът, който друг е написал, не се предава на една библиотека, без да се провери накъде сочи**. Това е вторият път, когато виждаш идеята, а в Урок 11 ще я преговориш.

#### 9.1.4 Защо курсът преминава към `httpx`

`urllib` върши работа, но самата документация на Python [препоръчва друг инструмент за нещо по-удобно](https://docs.python.org/3/library/urllib.request.html) („The Requests package is recommended for a higher-level HTTP client interface“). Този курс използва [`httpx`](https://www.python-httpx.org/), по четири конкретни причини, които ще видиш в този урок:

| | `urllib.request` | `httpx` |
|---|---|---|
| Един `503` | хвърля изключение | е нормален отговор, със своя код |
| Времеви лимит по подразбиране | никакъв | 5 секунди |
| Начини на използване | само синхронно (едно нещо наведнъж) | синхронно **и** асинхронно, със същия интерфейс |
| Адрес `file://` | го чете | го отхвърля |

`httpx` не идва с Python, но вече го имаш: инсталира го във виртуалната среда в Урок 1 и от днес нататък е единствената зависимост на `revisor`. Сравни с програмата на `urllib`:

```python
# fig09_04.py
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/facturacion")
print(respuesta.status_code, respuesta.reason_phrase)
print("es un error:", respuesta.is_error)

try:
    respuesta.raise_for_status()
except httpx.HTTPStatusError as error:
    print("raise_for_status avisó:", error.response.status_code)

try:
    httpx.get("file:///etc/hosts")
except httpx.UnsupportedProtocol as error:
    print("httpx no lo permite:", error)
```

```text
$ python fig09_04.py
503 Service Unavailable
es un error: True
raise_for_status avisó: 503
httpx no lo permite: Request URL is missing an 'http://' or 'https://' protocol.
```

`503` **не хвърли нищо**: `httpx.get` върна отговор като всеки друг, със `status_code`, `reason_phrase` и `is_error`, който е `True` за кодовете `4xx` и `5xx`. Ако предпочиташ грешката да се превръща в изключение, има `raise_for_status()`, който хвърля `httpx.HTTPStatusError`; програмата го показва, но `revisor` няма да го ползва. Един `503` не е провал на `revisor`: той е **стойността**, която `revisor` е дошъл да събере. Ако го третираш като изключение, ще го изкараш от нормалния път и ще те накара да го хванеш, за да го върнеш там, където е бил. А последната част потвърждава четвъртия ред на таблицата: `httpx` отхвърля `file://` с `UnsupportedProtocol`. Още една защита, не заместител на валидацията от Урок 6.

### 9.2 Времеви лимит: никоя заявка не чака вечно

Има въпрос, който не сме задавали: какво става, ако услугата **приеме** връзката и не отговори? Не я отхвърля, не я затваря: просто остава да „мисли“. Програмата ти застива там, докато нещо се промени. Ако това „нещо“ е прекъсване на мрежата или увиснала услуга, може да бъде **завинаги**. `revisor` съществува, за да открива увиснали услуги; `revisor`, който увисва заедно с тях, е по-лош от това да нямаш `revisor`. Затова правилото на този курс е само едно:

> **Всяка заявка има времеви лимит. Без изключения.**

Виж как стои `urllib` по подразбиране. Първият ред на програмата отпечатва глобалния времеви лимит на Python; после иска `/notificaciones`, което отнема 10 секунди, но този път с `timeout=1`, една секунда:

```python
# fig09_05.py
import socket
from urllib.request import urlopen

print("tiempo límite global:", socket.getdefaulttimeout())

try:
    urlopen("http://127.0.0.1:8099/notificaciones", timeout=1)
except TimeoutError as error:
    print("se acabó el tiempo:", error)
```

```text
$ python fig09_05.py
tiempo límite global: None
se acabó el tiempo: timed out
```

[`socket.getdefaulttimeout()`](https://docs.python.org/3/library/socket.html#socket.getdefaulttimeout) връща `None`: стандартната библиотека по подразбиране **няма никакъв времеви лимит** (документацията на [`urlopen`](https://docs.python.org/3/library/urllib.request.html) казва, че използва глобалната стойност). Без `timeout=` тази заявка щеше да остане десет секунди в чакане; срещу сървър, който никога не отговаря, нямаше да е свършила. С `timeout=1` чакането беше прекъснато на секундата и Python хвърли `TimeoutError`.

`httpx`, напротив, има времеви лимит от 5 секунди: [документацията](https://www.python-httpx.org/advanced/timeouts/) казва, че „хвърля `TimeoutException` след 5 секунди неактивност в мрежата“. Обърни внимание на две думи: *неактивност*, не общо време. Има четири различни времеви лимита: за **свързване** (`connect`), за **получаване** на парче от отговора (`read`), за **изпращане** (`write`) и за **взимане** на свободна връзка от групата (`pool`). Всеки от тях отчита колко чака *една операция*, а не колко трае целият обмен: сървър, който капе по един байт на всеки 4 секунди, никога не задейства `read` от 5 секунди, дори отговорът да се бави часове. Общият таван за услуга ще зададеш в Урок 10 с `asyncio.timeout()`; днес лимитът на всяка операция е достатъчен. Едно-единствено число в `httpx.Timeout(1.0)` задава и четирите на една секунда.

```python
# fig09_06.py
import httpx

print("httpx, por omisión:", httpx.Client().timeout)
limite = httpx.Timeout(1.0)

try:
    httpx.get("http://127.0.0.1:8099/notificaciones", timeout=limite)
except httpx.ReadTimeout:
    print("notificaciones: tiempo agotado")

try:
    httpx.get("http://127.0.0.1:8098/", timeout=limite)
except httpx.ConnectError:
    print("reportes: sin conexión")

print(issubclass(httpx.ReadTimeout, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.HTTPError))
```

```text
$ python fig09_06.py
httpx, por omisión: Timeout(timeout=5.0)
notificaciones: tiempo agotado
reportes: sin conexión
True
False
True
```

Първият ред показва стойността на `httpx` по подразбиране (`Timeout(timeout=5.0)`). След това две заявки с времеви лимит от една секунда, и всяка свършва с **различно** изключение, което е точно това, което `revisor` трябва да различава:

- `/notificaciones`, което отнема десет секунди, хвърли `httpx.ReadTimeout`: връзката се установи, но услугата не отговори навреме. Това е причината за „tiempo agotado“.
- Порт 8098, където не слуша никой, хвърли `httpx.ConnectError`: нямаше към кого да се свърже. Това е причината за „sin conexión“.

Последните три реда, с `issubclass` (което пита дали един клас е наследник на друг), потвърждават йерархията, [която документира `httpx`](https://www.python-httpx.org/exceptions/): `ReadTimeout` е `TimeoutException`; `ConnectError` **не** е; а `ConnectError` е `HTTPError`, класът-родител на почти всичко, което `httpx` може да хвърли. Това определя реда на `except` в `revisor`: първо `TimeoutException`, после `ConnectError`, а накрая `HTTPError`, за да събере останалото (например сървър, който затваря по средата на отговора). И трите клона връщат `Resultado` със състояние `CAIDO` и своя детайл (`tiempo agotado`, `sin conexión` или `error de red`). **Никога не оставят изключението да избяга.**

Откъде идва числото: всяка `Servicio` носи своя `timeout_ms`, по подразбиране 5000, в милисекунди. `httpx` иска секунди, затова `revisor` дели: `httpx.Timeout(servicio.timeout_ms / 1000)`. Единицата живее в името (`timeout_ms`) точно за да не се забрави това преобразуване. **Тук свършва първата сесия.**

### 9.3 Корутини: функции, които могат да чакат

#### 9.3.1 Една корутина не се изпълнява, когато я извикаш

Във втората сесия идва идеята, която се дава най-трудно. През 2.3-те секунди, които `inventario` се бави да отговори, програмата ти не прави нищо: чака. Цялото това време процесорът е свободен. Една **корутина** (coroutine) е функция, която може да **се паузира в мястото, където чака**, и да остави нещо друго да ползва това време. Пише се с `async def`, вместо с `def`:

```python
# fig09_07.py
async def saludar() -> str:
    return "hola"


print(saludar())
print("listo")
```

```text
$ python fig09_07.py
<coroutine object saludar at 0x...>
fig09_07.py:6: RuntimeWarning: coroutine 'saludar' was never awaited
  print(saludar())
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
listo
```

`saludar` е нормална функция във всичко освен в първата си дума. Но забележи какво отпечата `print(saludar())`: **не** казва `hola`. Казва `<coroutine object saludar at 0x...>`. Извикването на функция с `async def` не изпълнява тялото ѝ; създава **обект-корутина**, рецепта на пауза. [Документацията на `asyncio`](https://docs.python.org/3/library/asyncio-task.html) го казва така: извикването на една корутина не я планира за изпълнение, а в нейния пример `nested()` се извиква, без да бъде изчакана: обектът се създава, но тялото „изобщо няма да се изпълни“. И понеже обектът е изхвърлен на боклука, без никой да го изпълни, Python предупреждава: `RuntimeWarning: coroutine 'saludar' was never awaited`, „корутината `saludar` никога не е била изчакана“. Предупреждението включва реда от програмата, където е била извикана, и е **най-честият знак**, че си забравил един `await`.

#### 9.3.2 `asyncio.run`: стартът

Как се изпълнява тогава една корутина? Трябва ѝ координатор, който да я пусне, **цикълът на събитията** (event loop): малка програма, вътре в Python, която разпределя времето между паузираните корутини. Не го управляваш директно. [`asyncio.run`](https://docs.python.org/3/library/asyncio-runner.html) го създава, изпълнява корутината, която му дадеш, докато свърши, връща резултата ѝ и затваря цикъла:

```python
# fig09_08.py
import asyncio


async def saludar() -> str:
    return "hola"


print(asyncio.run(saludar()))
```

```text
$ python fig09_08.py
hola
```

Сега вече: `hola`. `asyncio.run` се пише само веднъж, във входа на програмата, и оттам нататък всичко останало се свързва с `await`. В `revisor` ще бъде в `cli.py`.

#### 9.3.3 `await` и `async with`: да изчакаш друга корутина

Вътре в една корутина `await` означава **„чакай тук тази друга работа да свърши и докато чакаш, остави цикъла да върши други неща“**. Това е явният начин да паузираш една корутина и работи само в рамките на функция с `async def`. (Има още два, които чакат, без да пишеш думата: `async with`, което ще видиш след малко, и `async for`, което курсът не ползва; [справочникът на езика](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement) обяснява, че отвътре и двете правят `await`.) Корутината, която най-често ще чакаш в курса, е заявка на `httpx`, и за това `httpx` носи [асинхронна версия на клиента](https://www.python-httpx.org/async/), `httpx.AsyncClient`, която се ползва с `async with`:

```python
# fig09_09.py
import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get("http://127.0.0.1:8099/pagos")
        print(respuesta.status_code)


asyncio.run(main())
```

```text
$ python fig09_09.py
200
```

`async with` е `with` от Урок 6 за ресурси, чието отваряне и затваряне **също** могат да чакат: създаването и затварянето на мрежовия клиент е операция от този вид. Вътре `cliente.get(...)` е корутина; `await` я изчаква и това, което се получава, е отговорът. Забележи, че отговорът е точно същият като при синхронния `httpx.get`: `status_code`, `is_error` и останалото. Разликата е в начина на чакане. А клиентът **се създава веднъж и се преизползва** за няколко заявки: да отваряш и затваряш по един за всяка проверка би било като да затваряш телефона и да набираш отново всеки път, когато зададеш въпрос.

### 9.4 Един `await` след друг не спестява време: серията

Ето най-разпространеното недоразумение за `asyncio`, и си струва да го разчистим с едно измерване. Един начинаещ чете „асинхронно“ и предполага „по-бързо“. Не е. Виж тази програма, която чака три пъти по половин секунда, една след друга, всяка с `await` ([`asyncio.sleep`](https://docs.python.org/3/library/asyncio-task.html#sleeping) е обичайното асинхронно чакане):

```python
# fig09_10.py
import asyncio
import time


async def esperar(nombre: str, segundos: float) -> str:
    await asyncio.sleep(segundos)
    return f"{nombre} esperó {segundos} s"


async def main() -> None:
    inicio = time.perf_counter()
    for nombre in ("catalogo", "inventario", "pagos"):
        print(await esperar(nombre, 0.5))
    total = time.perf_counter() - inicio
    print(f"en serie tarda la suma, 1.5 s o más: {1.5 <= total < 2.0}")


asyncio.run(main())
```

```text
$ python fig09_10.py
catalogo esperó 0.5 s
inventario esperó 0.5 s
pagos esperó 0.5 s
en serie tarda la suma, 1.5 s o más: True
```

Последният ред пита `1.5 <= total < 2.0`, двете неща наведнъж: `total` да е поне 1.5 и по-малко от 2. Трите чакания отнеха **сбора**: 1.5 секунди или повече. Нищо не спечели. Причината е в това, което `await` наистина прави: паузира **тази** корутина и предлага на цикъла да обслужи други, но в тази програма **няма други**. Цикълът предлага реда и никой не го взима. Това е същата [последователност, която показва документацията на Python](https://docs.python.org/3/library/asyncio-task.html): един `await`, следван от друг `await`, се изпълнява последователно. За да спечелиш време, трябват **няколко корутини, живи едновременно**, а това се постига със задачи (`asyncio.TaskGroup`), което е съдържанието на Урок 10.

Днешният `revisor` ще бъде, значи, асинхронна версия, която се държи **като синхронната**: проверява услугите една по една. Тогава за какво е? Първо, защото е междинната стъпка, която прави печалбата видима: Урок 10 измерва същата таблица от услуги последователно и паралелно и му трябва изходната точка. Второ, защото преминаването от `def` към `async def` засяга цялата верига от извиквания и е по-лесно да се разбере, ако го направиш преди да вкараш съвместно изпълнение. И трето, защото това, което е важно в тази стъпка, е всичко, което няма общо с времето: времеви лимити, изключения, класификация.

### 9.5 `revisor` проверява истински

С всичко казано дотук `revision.py` се пренаписва изцяло. `SIMULADO` се изтрива и двете функции стават корутини:

```python
# fig09_11/src/revisor/revision.py
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        respuesta = await cliente.get(servicio.url, timeout=limite)
    except httpx.TimeoutException:
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


async def revisar_todos(servicios: list[Servicio]) -> list[Resultado]:
    resultados: list[Resultado] = []
    async with httpx.AsyncClient() as cliente:
        for servicio in servicios:
            resultados.append(await revisar(cliente, servicio))
    return resultados
```

Чети `revisar` отгоре надолу. Получава **клиент** и **услуга**; клиентът идва отвън, за да се преизползва. Съставя `httpx.Timeout` с `timeout_ms` на услугата, записва часа с `time.perf_counter()` (високоточния часовник на Python) и прави заявката с `await`. Първите три `except` са тези от 9.2, **от най-конкретния към най-общия**, и всеки връща паднал `Resultado` със своя текст. Четвъртият хваща нещо, което не е мрежова грешка: адрес, който е минал валидацията от Урок 6, но който `httpx` не може да ползва. Случва се, например, с `http://999.1.1.1:8099/pagos`: за `urlsplit` това е адрес със сървър и порт, но всяка от четирите части на един IP адрес е от 0 до 255, а 999 не се побира, и `httpx` го отхвърля с `httpx.InvalidURL`, което **не** е наследник на `httpx.HTTPError` (казва го [йерархията му от изключения](https://www.python-httpx.org/exceptions/)). Други невъзможни имена на сървър завършват с `ValueError` от библиотеките, които `httpx` ползва отвътре. Без този `except` една-единствена такава услуга би съборила целия отчет с *traceback*; с него тя излиза на своя ред като `CAIDO`, с детайл `dirección inválida` (невалиден адрес), а останалите се проверяват както обикновено. `ValueError` се хваща тук, около едно-единствено извикване, а не в цялата програма: един `ValueError` от твоя собствен код, извън `try`, пак би я спрял със своя доклад, както трябва. Ако не е имало изключение, измерва колко време е минало (`round(... * 1000)` превръща секундите в цели милисекунди), класифицира със същата функция `clasificar` както винаги, която получава истинския код, и съставя `Resultado` с кода като детайл. Един `503` минава оттук: не е изключение, излиза с `clasificar(503, 95)` и се превръща в `CAIDO` с детайл `503`.

`revisar_todos` отваря **един** клиент с `async with` и обхожда услугите с един `for` и един `await` на итерация. Това е серията от 9.4, написана нарочно. Редът на резултатите е този от конфигурацията.

`main` в `cli.py` се променя само в един ред: извикването се обвива в `asyncio.run`.

```python
# fig09_11/src/revisor/cli.py
import argparse
import asyncio
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

    resultados = asyncio.run(revisar_todos(servicios))
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

За да има `asyncio.run` какво да изпълни, `revisar_todos(servicios)` без `await` произвежда корутина, а `asyncio.run` я пуска. Това е единственият `asyncio.run` в програмата. Тестовете продължават да викат `main` като нормална функция, така че **не е нужно да са корутини**; това е, което позволява да не се инсталира никакво разширение на `pytest` за асинхронен код. Останалите промени са данни. `pyproject.toml` се вдига до `0.8.0` и декларира първата зависимост на пакета, `httpx`:

```toml
dependencies = ["httpx>=0.28"]
```

Преинсталирай пакета (`pip install -e .`), за да види средата зависимостта и новата версия. А `servicios.toml` вече сочи към учебния сървър: същите четири имена, други адреси. (Целият проект е в 9.6.)

```toml fig09_11/servicios.toml
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

С отворен учебен сървър в другия терминал пусни `revisor` и виж кода на изход:

```text
$ cd fig09_11
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
$ echo $?
1
```

Това е таблицата от учебната програма, но вече **измерена**: `catalogo` и `pagos` работят с реални времена (сървърът чака 142 и 87 ms, а всяка заявка добавя няколко милисекунди мрежа, така че ще виждаш числа като 156 и 98, различни при всяко изпълнение), `inventario` е бавна с 2.3 s, `reportes` е паднала със `sin conexión` (в 8098 никой не слуша). Обобщението отчита две работещи, една бавна, една паднала, а кодът на изход е `1`, същият както винаги, по същата причина: има една бавна и една паднала. Променило се е, че сега е истина.

Колко време отнема? Последователно — сбора: 142 + 2300 + 87 са около 2.5 секунди чакане плюс времето, за да стартира Python и да зареди `httpx`. Измерено с командата `time` на терминала, едно пълно изпълнение трае около 2.7 секунди. Твоето ще даде близко число, не същото. Тази цифра е изходната точка на Урок 10. Измерва я Упражнение 1.

И тестовете: пусни ги.

```text
$ cd fig09_11
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

Те остават **21**. Единственият файл с тестове, който се промени, е `tests/test_cli.py`, и не от прищявка. Първият му тест ползваше симулираните данни, за да провери, че `main` връща `1`, а те вече не съществуват; и фалшивите функции на `monkeypatch` сега връщат корутина, защото истинската е корутина и `main` прави `asyncio.run` на каквото му върнат. Затова са `async def`:

```python
# fig09_11/tests/test_cli.py
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
    async def todos_caidos(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Едно предупреждение, което трябва да се каже на глас: **минава с `21 passed` и въпреки това новото няма нито един тест**. Нищо от току-що написаното (времевият лимит, класификацията на един `503`, `sin conexión`) не се упражнява в тези 21. Двата теста на `test_cli.py` заместват изцяло `revisar_todos`, така че мрежовият код дори не се докосва. Това е размерът на дупката и е причината за Урок 10: как се тества мрежов код без мрежа.

### 9.6 Целият проект

Снимката на проекта в края на урока. Файловете, които вече видя, са `laboratorio.py`, `servicios.toml`, `revision.py`, `cli.py` и `tests/test_cli.py`. `pyproject.toml` е този от Урок 8 с новата версия и новата зависимост:

```toml fig09_11/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.8.0"
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

Останалите файлове **не се променят** спрямо Урок 8 и се повтарят тук само за да е проектът цялостен:

```python
# fig09_11/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig09_11/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig09_11/src/revisor/modelo.py
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
# fig09_11/src/revisor/formato.py
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
# fig09_11/src/revisor/configuracion.py
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
# fig09_11/tests/test_modelo.py
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
# fig09_11/tests/test_formato.py
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
# fig09_11/tests/test_configuracion.py
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

Четирите проверки от Урок 8, които сега покриват и асинхронния код:

```text
$ cd fig09_11
$ ruff format --check
12 files already formatted
$ ruff check
All checks passed!
$ mypy
Success: no issues found in 11 source files
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

## Грешката, която ще видиш

### `RuntimeWarning: coroutine 'saludar' was never awaited`

Видя го в 9.3.1, с програмата `fig09_07.py`, и си струва да повторим как се чете. Предупреждението не е грешка: програмата **продължава** и завършва с код `0`, което е опасното, защото има едно предупреждение сред десетки редове и лесно се пропуска. Казва три неща: файла и реда, където си извикал корутината, без да я изчакаш (`fig09_07.py:6`, а отдолу отпечатва и самия ред, `print(saludar())`), коя корутина е била (`'saludar'`) и последствието: тялото ѝ никога не се е изпълнило. Лекарството почти винаги е една дума: да сложиш `await` пред извикването или да го подадеш на `asyncio.run`.

В проекта `mypy` те предупреждава **преди** да пуснеш. Махни `await` от реда `resultados.append(await revisar(cliente, servicio))` в `revisar_todos` и ето какво казва `mypy`:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
Found 1 error in 1 file (checked 11 source files)
```

Ти си казал на списъка, че пази `Resultado`, а му даваш `Coroutine`. И `mypy` се досеща с една бележка: „Maybe you forgot to use "await"?“ (Да не си забравил `await`?). Това е видът помощ, заради който са писани типовете в Урок 8. Ако пренебрегнеш предупреждението и пуснеш програмата, таблицата отпечатва заглавния си ред и спира с `AttributeError: 'coroutine' object has no attribute 'servicio'` (последният ред на *traceback*), следван от същия `RuntimeWarning` накрая.

### Всички услуги казват `sin conexión`

Ако забравиш да включиш учебния сървър, `revisor` не се срива; прави точно това, което трябва. Ето какво отпечатва при изключен сървър:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO          —  sin conexión
inventario  CAIDO          —  sin conexión
pagos       CAIDO          —  sin conexión
reportes    CAIDO          —  sin conexión

4 servicios · 0 arriba · 0 lentos · 4 caídos · promedio —
```

Няма `Traceback`. И четирите услуги са `CAIDO`, със `sin conexión` и без време (`—`), защото никой не отговаря на порт 8099, както и на 8098. Това е дизайнът в действие: услуга, която не отговаря, е **част от данните**, а не изключение, което събаря отчета. Сигналът за теб е, че `reportes` не би трябвало да е единствената паднала: ако и четирите са паднали, преди да търсиш грешка в кода си, провери дали вторият терминал още е отворен. (Забележи и средното: излиза като `—`, също както времето на всеки ред, защото няма времена, от които да се смята средно. Това е същото решение от Урок 2: това, което не е измерено, не струва `0`.)

### Тестът, който се чупи, защото фалшивата му функция вече не е корутина

Ако оставиш `tests/test_cli.py` такъв, какъвто беше в Урок 8, и промениш само `revision.py` и `cli.py`, `pytest -q` казва `1 failed, 20 passed`. Червеният е тестът, който ползва фалшивата функция с `def` вместо с `async def`. Последният ред на грешката сменя формулировката според версията на Python, но казва същото:

```text
ValueError: a coroutine was expected, got [Resultado(servicio=Servicio(nombre='catalogo', ...
```

(в Python 3.12) или

```text
TypeError: An asyncio.Future, a coroutine or an awaitable is required
```

(в 3.14). `asyncio.run(...)` получи **списък**, а очакваше корутина, защото `main` прави `asyncio.run(revisar_todos(servicios))`, а фалшивата функция, като е `def`, върна резултата директно. Поправката е тази, която видя: фалшивата функция да стане `async def`.

Но има нещо по-коварно. **Втори** стар тест, този, който се изпълняваше със симулираните данни, **остава зелен** и не би трябвало. Този тест ползваше адреси `https://catalogo.example` и очакваше `main` да върне `1`. Сега `main` праща истински заявки към тези измислени адреси, не успява да се свърже с нито един, отбелязва всички като паднали и връща `1`. Тестът минава, но **по съвсем друга причина** от тази, заради която е бил написан, и зависи от това, че `.example` никога не се разрешава и че мрежата ти бързо отговаря, че не съществува. Това става, когато един зелен тест поддържа нещо, което вече не е това, което казва: фалшивият вариант е заменен с тест, който не прави това, което името му обещава. Затова беше пренаписан с изричен фалшив обект.

## Какво се прави погрешно

**Заявка без времеви лимит.** Това е грешката, заради чието избягване съществува този урок. С `urllib`, без `timeout=`, програмата чака колкото е нужно, включително завинаги. С `httpx` лимитът по подразбиране е 5 s, но да разчиташ на стойност по подразбиране, без да го знаеш, значи да оставиш важно решение в ръцете на някой друг. `revisor` го задава винаги, за всяка услуга.

**Да хванеш `Exception` и да продължиш.** `except Exception: pass` около една заявка прави един `ReadTimeout`, един `ConnectError` и една програмна грешка да изглеждат еднакво: никак. `revisor` хваща три конкретни изключения, всяко със своя текст, и оставя всяко друго да се види.

**Да отпечатваш съобщението на операционната система.** `[Errno 111] Connection refused` се променя със системата и с езика; отчетът за една услуга не бива да сменя текста си според това къде се изпълнява. Детайлът е една от три фиксирани фрази.

**Да предполагаш, че `async` е по-бързо.** Опроверга го в 9.4: един `await` след друг сумира времената си. Една `async` функция без съвместно изпълнение е синхронна функция с повече церемония.

**Да извикаш корутина без `await`.** Предупреждението от 9.3.1. С `mypy` в строг режим се превръща в грешка на типовете, затова си струва да го пускаш.

**Да блокираш вътре в корутина.** Един `time.sleep(1)` вътре в `async def` спира **цялата** програма за една секунда: никой друг не може да напредва, защото цикълът е заседнал вътре в това извикване. Вътре в корутина чакането е `await asyncio.sleep(1)`. Същото важи за мрежовите библиотеки, които не са асинхронни, като `urllib` или `httpx.get`.

**Да създаваш клиент за всяка заявка.** `httpx.AsyncClient()` отваря група от връзки, които се преизползват. Да отваряш и затваряш по един при всяка проверка прахосва тази икономия; `revisor` отваря един в началото на `revisar_todos` и го споделя.

**Да третираш един `503` като провал на програмата.** Услуга, която отговаря с грешка, е резултатът от работата, а не инцидент на `revisor`. Затова се чете кодът и се класифицира; `raise_for_status()` би превърнал стойността в изключение.

**Да слагаш `0`, където не е имало отговор.** Една паднала услуга има `tiempo_ms=None`, не `0`: с нула средното възнаграждава падналата. Това е същият урок от Урок 2, в по-голям проект.

## Упражнения

### Упражнение 1 — Измери серията с часовника

С включен учебен сървър измери колко време отнема целият `revisor`: `time python -m revisor`. Преди да го пуснеш, **предвиди** числото от това, което знаеш: сбора от времето на всяка услуга. Пусни го три пъти и запиши трите в дневника си. Защо не са еднакви? Това число е изходната ти точка за Урок 10.

### Упражнение 2 — Махни времевия лимит на една заявка и виж защо е опасно

Напиши програма от шест реда, която използва `httpx.get` с `timeout=None` (което [изключва времевия лимит](https://www.python-httpx.org/advanced/timeouts/)) срещу `http://127.0.0.1:8099/espera/60000`, което отнема минута. Пусни я, остави да минат пет секунди и натисни `Ctrl`+`C`. Какво се отпечатва? Колко време би отнело да свърши сама? После сложи `timeout=2.0` и сравни.

### Упражнение 3 — Двете допълнителни услуги

Добави в своя `servicios.toml` `facturacion` (`http://127.0.0.1:8099/facturacion`) и `notificaciones` (`http://127.0.0.1:8099/notificaciones`, с `timeout_ms = 1000`). Преди да пуснеш, предвиди състоянието и детайла на всяка и какъв ще е редът на обобщението. Нещо в таблицата изглежда ли ти странно? Върни файла към четирите му услуги, когато приключиш.

### Упражнение 4 — Забрави един `await` нарочно

В `revisar_todos` махни `await` от `resultados.append(await revisar(cliente, servicio))`. Пусни `mypy`, после `python -m revisor` и прочети двата сигнала: какво казва всеки и кой дойде пръв. Върни `await`.

## Решения

### Решение 1

Предвиждането: 142 + 2300 + 87 = 2529 ms за трите, които отговарят, плюс времето, за да се опита да се свърже с `reportes` (няколко милисекунди, защото отхвърлят веднага), плюс стартирането на Python и на `httpx`. Това дава около **2.6 или 2.7 секунди** и това мери часовникът: едно референтно изпълнение даде 2.674 s. Трите изпълнения си приличат, но не са еднакви, защото сървърът, операционната система и мрежата добавят малки отклонения от по няколко милисекунди всеки път. Важен е редът на величината: около 2.5 секунди, защото **е сборът**. Ако Урок 10 успее да го доближи до 2.3 s (най-бавната услуга), ще е спечелил по-малко, отколкото изглежда, с четири услуги; затова силното измерване на този урок ползва двайсет.

### Решение 2

```python
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/espera/60000", timeout=None)
print(respuesta.status_code)
```

С `Ctrl`+`C` на петата секунда Python отпечатва *traceback*, който завършва с `KeyboardInterrupt`: прекъсна ти, не програмата. Щеше да отнеме **цяла минута**, за да свърши сама, без да отпечата нищо през това време. Срещу сървър, който никога не отговаря, никога нямаше да свърши: това значи „без времеви лимит“. С `timeout=2.0` програмата хвърля `httpx.ReadTimeout` на втората секунда. Този `ReadTimeout` е изключение, **което може да се хване**, и това прави `revisar`.

### Решение 3

Предвиждането: `facturacion` отговаря `503` за 95 ms, така че `CAIDO` с детайл `503` и време около 100 ms. `notificaciones` отнема 10 s, но лимитът ѝ е 1 s: `CAIDO` с `tiempo agotado` и без време. Обобщението: `6 servicios · 2 arriba · 1 lento · 3 caídos`. Ето какво отпечатва:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     160ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO      102ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 666ms
```

Странното е последният ред: `notificacionesCAIDO`, без разделител. Името е с 14 букви, а колоната `SERVICIO` е широка 12 (`{nombre:<12}`), така че прелива и се залепва за следващата. Това е реално ограничение на таблицата такава, каквато е днес, и е едно от нещата, които Урок 11 поправя, като изчислява ширината по най-дългото име. Отчети и времето: цялото изпълнение отне около 3.8 s вместо 2.7, защото `notificaciones` чака цялата си секунда, преди да се предаде. Всяка бавна или увиснала услуга добавя чакането си към серията, а това е, което Урок 10 идва да реши.

### Решение 4

`mypy` се оплаква **първи**, без да пуска нищо:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
```

При пускане на програмата се отпечатва заглавният ред и тя спира с `AttributeError: 'coroutine' object has no attribute 'servicio'`, защото списъкът съдържа корутини вместо резултати, а накрая се появява `RuntimeWarning: coroutine 'revisar' was never awaited`. Пръв дойде `mypy`, и то с причината и с препоръката; грешката по време на изпълнение показва само последствието. Това е аргументът в полза на това да пускаш `mypy` преди програмата.

## Как разбирам, че съм успял

- [ ] С включен учебен сървър `python -m revisor` отпечатва таблицата с четирите услуги, с `catalogo` и `pagos` работещи, `inventario` бавна (`2.3s`) и `reportes` паднала със `sin conexión`, а `echo $?` отпечатва `1`.
- [ ] С изключен сървър и четирите казват `CAIDO` и `sin conexión`, а програмата не отпечатва никакъв *traceback*.
- [ ] `pytest -q` казва `21 passed` (същото число като в Урок 8) и можеш да обясниш коя част от програмата **не** покрива нито един от 21-те.
- [ ] `mypy` казва `Success: no issues found in 11 source files`, `ruff check` казва `All checks passed!` и `ruff format --check` казва, че файловете вече са форматирани.
- [ ] Измери изпълнението с `time` и твоето число е близо до 2.7 секунди, и знаеш да обясниш защо е сборът, а не максимумът.
- [ ] Можеш да обясниш какво прави `await`, какво прави `asyncio.run` и защо `saludar()` само по себе си не отпечатва `hola`.
- [ ] Можеш да кажеш с кое изключение на `httpx` завършва услуга, която не отговаря, и с кое — такава, където никой не слуша, и защо един `503` не е изключение.

## Обобщение

Отговори, без да гледаш урока:

1. Какво носи един HTTP отговор и какви семейства кодове на състоянието има? Кои превръщат една услуга в `CAIDO`?
2. Какво прави `urllib`, когато сървърът отговори `503`, и какво прави `httpx`?
3. Защо `urlopen` приема адрес `file://` и какво го спира в `revisor`?
4. Какъв времеви лимит има `urllib` по подразбиране и какъв `httpx`?
5. Какво изключение на `httpx` произвежда услуга, която не отговаря, и какво — такава, където никой не слуша?
6. Какво прави `asyncio.run`? Какво става, ако извикаш функция с `async def` без `await` и без `asyncio.run`?
7. Защо три поредни `await` по половин секунда отнемат 1.5 s, а не 0.5 s?
8. Защо отчетът на Урок 9 продължава да казва `21 passed` и какво остави без тест?

## За допълнително четене

- [HTTPX, „Timeouts“](https://www.python-httpx.org/advanced/timeouts/) — четирите времеви лимита (`connect`, `read`, `write`, `pool`), стойността по подразбиране и как се изключват. На английски, както почти цялата документация на екосистемата. Посетено на 7 октомври 2026 г.
- [Python, „Coroutines and tasks“](https://docs.python.org/3/library/asyncio-task.html) — официалната документация на `asyncio`: корутини, `await`, задачи и предупреждението за корутина, която никога не е изчакана. Посетено на 7 октомври 2026 г.
- [RFC 9110, „HTTP Semantics“](https://www.rfc-editor.org/rfc/rfc9110.html) — стандартът на HTTP; разделът за кодовете на състоянието определя какво означава всяко число. Това е текст за справка, не за четене от край до край. Посетено на 7 октомври 2026 г.
- [PEP 492, „Coroutines with async and await syntax“](https://peps.python.org/pep-0492/) — документът, който въвежда `async` и `await`; обяснява защо са запазени думи на езика. Посетено на 7 октомври 2026 г.
