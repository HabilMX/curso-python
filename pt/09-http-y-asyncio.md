# Lição 9 — HTTP e asyncio

**Tempo:** 2 × 90 min (a primeira sessão vai até o final de 9.2; a segunda cobre 9.3, 9.4 e 9.5)

**O que você constrói:** o `revisor` que consulta serviços de verdade, um após o outro, com tempo limite em cada requisição

**O que você aprende:** pedir uma página com `urllib` e com `httpx`; o que diz um código de status; por que toda requisição leva tempo limite; corrotinas (`async def`, `await`, `asyncio.run`, `async with`); e por que um `await` sozinho, sem mais ninguém, não torna nada mais rápido

**De onde você vem.** Você traz o pacote da [Lição 8](08-pruebas-tipos-calidad.md): o `revisor` com 21 testes, os tipos verificados e o estilo vigiado. Mas há uma verdade incômoda nesse pacote: **ele nunca consultou ninguém**. As cifras da tabela (142 ms, 2.3 s, 87 ms) saem de um dicionário, `SIMULADO`, que você mesmo escreveu; o programa devolve o que você mandou ele dizer. Hoje você o troca por uma consulta real: o `revisor` faz uma requisição a cada serviço, cronometra quanto ele leva para responder e classifica o que recebe. Para praticar sem incomodar nenhum serviço de verdade, a lição lhe dá um servidor de prática que roda no seu próprio computador.

**O que esta lição não faz.** Ela ainda não consulta os serviços **ao mesmo tempo**: faz isso um após o outro, e a lição ensina você a medir quanto isso custa. Juntá-los é a [Lição 10](10-concurrencia-pruebas-sin-red.md). E o código novo, o que usa a rede, **não tem teste**: o projeto continua tendo os 21 testes da Lição 8, e a lição diz isso de frente em vez de escondê-lo. Testar código de rede sem rede é o tema da Lição 10.

## Ao terminar, você vai conseguir

- Explicar o que é uma requisição HTTP, o que contém uma resposta e o que significam os códigos de status `2xx`, `4xx` e `5xx`.
- Pedir um endereço com `urllib.request` e com `httpx`, e dizer em que se diferenciam quando o servidor responde `503` e quando não responde.
- Explicar por que o `urllib` aceita um endereço `file://`, e por que a validação da Lição 6 evita que o `revisor` leia arquivos do seu computador.
- Colocar tempo limite em uma requisição, saber que exceção é lançada quando ele se esgota e qual quando não há a quem chamar.
- Escrever uma corrotina com `async def`, executá-la com `asyncio.run` e esperar outra com `await`, e explicar por que chamar uma corrotina **não** a executa.
- Medir com o relógio que consultar os serviços um após o outro leva a soma dos seus tempos, e explicar por que um `await` sozinho não o acelera.
- Ler o aviso `coroutine ... was never awaited` e a mensagem do `mypy` “Maybe you forgot to use "await"?”.

## O porquê antes do como

Imagine que você pergunta a um colega de escritório se o sistema de pagamentos está funcionando. Ele tem de fazer algo parecido com o que o seu navegador faz quando você abre uma página: perguntar a essa máquina por um endereço e esperar a resposta. A pergunta se chama **requisição** e a resposta, **resposta**. Ambas seguem uma linguagem comum, o **HTTP**, que é a que toda a web usa. Uma requisição diz, em essência, “me dê o que há neste endereço” (o método `GET`, mais o endereço). Uma resposta traz três coisas: um **código de status**, um número de três algarismos que resume como tudo saiu; uns **cabeçalhos**, dados sobre a resposta (que tipo de conteúdo é, quanto mede); e um **corpo**, o próprio conteúdo.

O que mais importa para você na resposta é o código, e o seu primeiro algarismo o classifica. [O padrão do HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) os agrupa em cinco famílias: os `1xx` são informativos, os `2xx` querem dizer que saiu bem (`200` é “aqui está”), os `3xx` são redirecionamentos, os `4xx` são erros de quem pergunta (`404`: esse endereço não existe) e os `5xx` são erros do servidor (`503`: agora não posso atender você). Para o `revisor`, um serviço pode terminar de **três formas** diferentes, e cada uma acaba em uma linha da tabela:

| O que aconteceu | O que o `revisor` vê | Como fica na tabela |
|---|---|---|
| O serviço respondeu com um código menor que 400 (`2xx`, ou um `3xx`) | um código e um tempo | `ARRIBA`, ou `LENTO` se levou 1000 ms ou mais |
| Respondeu com um código `4xx` ou `5xx` | um código e um tempo | `CAIDO`, com o código no detalhe (`503`) |
| Não respondeu | uma exceção: não foi possível conectar, ou o tempo se esgotou | `CAIDO`, com `sin conexión` ou `tiempo agotado` |

Os `3xx` caem na primeira linha de propósito. Um redirecionamento diz “o que você procura está em outro endereço”, e o `httpx` [não o segue por padrão](https://www.python-httpx.org/quickstart/#redirection-and-history): devolve a resposta tal qual, com o seu código. Para o `revisor`, que um serviço responda com um redirecionamento quer dizer que está vivo e respondendo, e a regra de sempre (fora do ar somente com `400` ou mais) o conta como no ar, com o código no detalhe para você ver.

Essa tabela é todo o design da lição. (O HTTP é o estilo mais comum para dois programas conversarem, mas não o único; se você tem interesse no que vem depois de “pedir um endereço e ler o que responde”, o blog da Hábil compara dois estilos em [REST ou gRPC: quando convém cada um](https://www.habil.mx/pt/blog/rest-ou-grpc-quando-convem-cada-um/).) O resto é como se faz cada linha sem que o programa caia: a terceira, sobretudo, porque um serviço que não responde é justamente o caso que o `revisor` existe para detectar, e não pode ser o caso que o derrube.

A lição tem duas metades. Na primeira sessão você faz uma consulta bem-feita: primeiro com a biblioteca que vem com o Python, o `urllib`, para ver como é uma requisição por dentro, e depois com o `httpx`, a que o curso usa. Você aprende que **toda requisição leva um tempo limite**. Na segunda sessão você chega às **corrotinas**, a ferramenta do Python para esperar sem ficar parado, e coloca o `revisor` para consultar de verdade. É o salto conceitual maior do curso; por isso o ritmo desta lição é lento de propósito.

### O servidor de prática

O `revisor` precisa de alguém a quem perguntar. Os nomes `catalogo.example` ou `pagos.example` que você usou até agora são endereços inventados: o sufixo `.example` está [reservado para exemplos](https://www.rfc-editor.org/rfc/rfc2606) e nunca existe na internet. Para que cada serviço responda de verdade, e sempre igual, a lição inclui o `laboratorio.py`, um pequeno servidor que roda **no seu computador** e finge ser os serviços do curso.

Aqui está o arquivo completo. **Tome-o como uma caixa-preta: usa-se, não se escreve.** Ele é construído com uma classe e métodos, coisas que este curso não ensina, e entendê-lo não é necessário para nada do que segue. Copie-o tal qual para `~/curso-python/revisor/laboratorio.py`. Quando terminar o curso você pode voltar a lê-lo; a biblioteca que ele usa, [`http.server`](https://docs.python.org/pt-br/3/library/http.server.html), faz parte do Python.

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

O que importa nele é o que cada rota responde, que é o que dizem a tabela `RUTAS` e a função `buscar_ruta`. (A classe `Servidor` só muda um número, `request_queue_size`: quantas conexões podem esperar a vez ao mesmo tempo para serem atendidas. O valor de fábrica, 5, fica curto quando, na Lição 10, o `revisor` abrir vinte conexões de uma vez, e as que não couberem na fila seriam rejeitadas como se o serviço estivesse fora do ar.)

| Rota | O que responde | Quanto leva |
|---|---|---|
| `/catalogo` | `200` | 142 ms |
| `/inventario` | `200` | 2300 ms |
| `/pagos` | `200` | 87 ms |
| `/facturacion` | `503` | 95 ms |
| `/notificaciones` | `200` | 10 segundos |
| `/espera/<ms>` | `200` | os milissegundos que você colocar no lugar de `<ms>` |

São os mesmos números da tabela do programa do curso, agora produzidos por um servidor de verdade. O endereço é `127.0.0.1`, que significa “este mesmo computador”, de modo que o que acontece na lição não sai da sua máquina. Há uma única exceção, e quase certamente não é o seu caso: se no seu terminal há um **proxy** configurado (um intermediário pelo qual passam as requisições, comum em algumas redes de escritório, e que se nota porque existem variáveis como `HTTP_PROXY` ou `ALL_PROXY`, em maiúsculas ou minúsculas; `env | grep -i proxy` mostra elas), as requisições para `127.0.0.1` também vão para o proxy, e a prática falha. O `httpx` respeita `HTTP_PROXY`, `HTTPS_PROXY` e `ALL_PROXY`; o `urllib`, só as duas primeiras. Resolve-se dizendo a eles que esse endereço não passa pelo proxy, com `export NO_PROXY=127.0.0.1` em cada terminal onde você rodar os programas; a [documentação do `httpx`](https://www.python-httpx.org/environment_variables/) explica essas variáveis. A porta `8099` é o “número do guichê” em que ele escuta. E há uma armadilha deliberada: a porta **`8098` ninguém atende**. Ali vive o serviço `reportes`: perguntar a um guichê onde não há ninguém é a forma mais fiel de simular um serviço fora do ar, e sempre sai igual.

Antes de cada exercício desta lição, ligue o servidor **em um segundo terminal** (com o ambiente virtual ativado, a partir de `~/curso-python/revisor/`) e deixe-o aberto:

```text
laboratorio en http://127.0.0.1:8099 (Ctrl+C para detenerlo)
```

Essa linha é a única coisa que ele imprime; quando você terminar de praticar, `Ctrl`+`C` nesse terminal o desliga. Se por engano você o deixar desligado, já verá o que acontece: está em “O erro que você vai ver”. No terminal de sempre você segue rodando os programas da lição.

## Os conceitos

### 9.1 HTTP: pedir um endereço e ler o que responde

#### 9.1.1 Com a biblioteca que o Python já traz

O `urllib.request` vem com o Python; não é preciso instalar nada. A sua função principal, [`urlopen`](https://docs.python.org/pt-br/3/library/urllib.request.html), recebe um endereço, faz a requisição e devolve a resposta como um objeto que pode ser usado com `with` (o mesmo `with` da Lição 6, que fecha a conexão ao terminar). Peça o catálogo ao servidor de prática:

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

Linha por linha. `respuesta.status` é o código de status, `200`, e `respuesta.reason` é a frase que o acompanha, `OK`. `respuesta.read()` devolve o corpo, e o que sai na segunda linha, `b'ok'`, tem um `b` na frente que convém explicar: a rede não transporta texto, e sim **bytes**, números de 0 a 255, e `read()` os entrega tal qual. Para convertê-los em texto é preciso dizer com que codificação foram escritos, que é o mesmo UTF-8 da Lição 6: `cuerpo.decode("utf-8")` dá o `str` normal, `ok`. A última linha comprova o tempo. [`time.perf_counter()`](https://docs.python.org/pt-br/3/library/time.html#time.perf_counter) é o relógio de alta precisão do Python: devolve os segundos como um decimal, e subtrair duas leituras dá o que levou o que há entre elas. O servidor leva 142 ms para responder o catálogo, então a requisição não podia levar menos. Imprimir o tempo exato faria cada execução dar um número diferente; o `True` é o que não muda.

Repare no que **não** há neste programa: nenhum tempo limite. Você o corrigirá em 9.2, mas anote desde já como uma promessa pendente.

#### 9.1.2 Os códigos de status, e as duas exceções do `urllib`

Pedir o catálogo é o caso feliz. O `revisor` precisa sobreviver aos outros dois: o serviço que responde com um erro e o que não responde. Este programa consulta um de cada tipo:

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

`catalogo` saiu como se esperava. Mas `facturacion`, que responde `503`, **não devolveu uma resposta: lançou uma exceção**, `HTTPError`, e por isso entrou no primeiro `except`. É uma decisão de design do `urllib` que surpreende no começo: para esta biblioteca, um código `4xx` ou `5xx` é uma exceção, e o código que ele leva se lê em `error.code`. E `reportes`, onde ninguém escuta, lançou `URLError`, que traz em `error.reason` a causa real. Aqui é `ConnectionRefusedError` (a conexão foi recusada). Repare que o programa imprime apenas o **nome** da causa, `type(error.reason).__name__` (`type` dá a classe do valor, a da Lição 2, e `__name__` o seu nome como texto), e não a mensagem. A mensagem do sistema operacional muda entre computadores (no Linux diz `[Errno 111]`, no macOS `[Errno 61]`), e o curso decidiu que o detalhe que o `revisor` mostra nunca seja esse texto: diz `sin conexión`, igual em toda parte.

A **ordem** dos `except` importa e é o mesmo problema da Lição 6. [`HTTPError` é uma subclasse de `URLError`](https://docs.python.org/pt-br/3/library/urllib.error.html): todo `HTTPError` é também um `URLError`. Se você pusesse o `except URLError` primeiro, ele capturaria tudo e o `except HTTPError` de baixo nunca seria executado. A regra é a de sempre: **o mais específico primeiro**.

#### 9.1.3 Um endereço que não é da internet: `file://`

Há uma surpresa no `urlopen`, e tem a ver com segurança. Um endereço começa com um **esquema**, a parte antes de `://`: `http`, `https`, e também `file`, que significa “um arquivo deste mesmo computador”. O `urlopen` entende o esquema `file`:

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

O programa cria um arquivo `secreto.txt` (e o apaga no final com `unlink()`, para não deixar nada). Como ele vai sobrescrevê-lo e depois apagá-lo, antes pergunta se já existe um com esse nome: se existe, para sem tocá-lo, com `raise SystemExit(...)`, a mesma exceção da Lição 7, que desta vez leva um texto em vez de um número; o Python imprime esse texto na saída de erro e termina com código 1. Depois toma o caminho absoluto do arquivo com `resolve()`, monta o seu endereço com [`.as_uri()`](https://docs.python.org/pt-br/3/library/pathlib.html#pathlib.Path.as_uri) (que produz algo como `file:///home/tu/secreto.txt`) e o dá ao `urlopen`, que **o lê sem protestar**. É uma função legítima, mas imagine o `revisor` lendo endereços de um `servicios.toml` que outra pessoa escreveu, e alguém coloca `file:///etc/passwd` no lugar do endereço de um serviço: o programa leria o arquivo e o trataria como uma “resposta”. Por isso, na Lição 6, a validação exigia que o esquema fosse `http` ou `https`, com [`urlsplit(url).scheme`](https://docs.python.org/pt-br/3/library/urllib.parse.html) dentro de `{"http", "https"}`; a última linha deste programa faz essa mesma comprovação e responde `False` para `file`. Não é um detalhe de estilo: **o endereço que outra pessoa escreve não se entrega a uma biblioteca sem comprovar para onde aponta**. É a segunda vez que você vê a ideia, e na Lição 11 você a revisará.

#### 9.1.4 Por que o curso passa ao `httpx`

O `urllib` serve, mas a própria documentação do Python [recomenda outra ferramenta para algo mais cômodo](https://docs.python.org/pt-br/3/library/urllib.request.html) (“The Requests package is recommended for a higher-level HTTP client interface”). Este curso usa o [`httpx`](https://www.python-httpx.org/), por quatro razões concretas que você verá nesta lição:

| | `urllib.request` | `httpx` |
|---|---|---|
| Um `503` | lança uma exceção | é uma resposta normal, com o seu código |
| Tempo limite padrão | nenhum | 5 segundos |
| Formas de usá-la | só síncrona (uma coisa de cada vez) | síncrona **e** assíncrona, com a mesma interface |
| Um endereço `file://` | o lê | o rejeita |

O `httpx` não vem com o Python, mas você já o tem: instalou-o dentro do ambiente virtual na Lição 1, e a partir de hoje é a única dependência do `revisor`. Compare com o programa do `urllib`:

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

O `503` **não lançou nada**: `httpx.get` devolveu uma resposta como qualquer outra, com `status_code`, `reason_phrase` e um `is_error` que vale `True` para os códigos `4xx` e `5xx`. Se você prefere que um erro vire exceção, existe `raise_for_status()`, que lança `httpx.HTTPStatusError`; o programa demonstra isso, mas o `revisor` não o usará. Um `503` não é uma falha do `revisor`: é o **dado** que o `revisor` veio coletar. Tratá-lo como exceção o tiraria do caminho normal e obrigaria a capturá-lo para recolocá-lo onde estava. E a última parte confirma a quarta linha da tabela: o `httpx` rejeita `file://` com `UnsupportedProtocol`. Uma defesa a mais, não substituta da validação da Lição 6.

### 9.2 Tempo limite: nenhuma requisição espera para sempre

Há uma pergunta que não fizemos: o que acontece se o serviço **aceita** a conexão e não responde? Não a rejeita, não a fecha: simplesmente fica pensando. O seu programa fica ali, parado, até que algo mude. Se esse “algo” é uma queda de rede ou um serviço travado, pode ser **para sempre**. O `revisor` existe para detectar serviços travados; um `revisor` que trava com eles é pior do que não ter `revisor`. Por isso a regra deste curso é uma só:

> **Toda requisição leva um tempo limite. Sem exceções.**

Veja como está o `urllib` por padrão. A primeira linha do programa imprime o tempo limite global do Python; depois pede `/notificaciones`, que leva 10 segundos, mas agora com `timeout=1`, um segundo:

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

[`socket.getdefaulttimeout()`](https://docs.python.org/pt-br/3/library/socket.html#socket.getdefaulttimeout) devolve `None`: a biblioteca padrão, por padrão, **não tem nenhum tempo limite** (a documentação do [`urlopen`](https://docs.python.org/pt-br/3/library/urllib.request.html) diz que usa o valor global). Sem `timeout=`, essa requisição teria ficado dez segundos esperando; contra um servidor que nunca responde, não teria terminado. Com `timeout=1` a espera foi cortada em um segundo e o Python lançou `TimeoutError`.

O `httpx`, em contrapartida, traz um tempo limite de 5 segundos: [a documentação](https://www.python-httpx.org/advanced/timeouts/) diz que “lança uma `TimeoutException` depois de 5 segundos de inatividade na rede”. Observe duas palavras: *inatividade*, não tempo total. Há quatro tempos limite diferentes: para **conectar** (`connect`), para **receber** um pedaço da resposta (`read`), para **enviar** (`write`) e para **conseguir** uma conexão livre do grupo (`pool`). Cada um conta quanto espera *uma operação*, não quanto dura toda a troca: um servidor que pinga um byte a cada 4 segundos nunca dispara o `read` de 5 segundos ainda que a resposta leve horas. O teto total por serviço você o porá na Lição 10 com `asyncio.timeout()`; hoje, o de cada operação é suficiente. Um único número em `httpx.Timeout(1.0)` fixa os quatro em um segundo.

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

A primeira linha mostra o valor padrão do `httpx` (`Timeout(timeout=5.0)`). Depois, duas requisições com tempo limite de um segundo, e cada uma termina com uma exceção **diferente**, que é justamente o que o `revisor` precisa distinguir:

- `/notificaciones`, que leva dez segundos, lançou `httpx.ReadTimeout`: a conexão foi estabelecida, mas o serviço não respondeu a tempo. É a causa de “tiempo agotado”.
- A porta 8098, onde ninguém escuta, lançou `httpx.ConnectError`: não houve a quem se conectar. É a causa de “sin conexión”.

As três últimas linhas, com `issubclass` (que pergunta se uma classe é filha de outra), confirmam a hierarquia [que o `httpx` documenta](https://www.python-httpx.org/exceptions/): `ReadTimeout` é uma `TimeoutException`; `ConnectError` **não** é; e `ConnectError` sim é uma `HTTPError`, a classe mãe de quase tudo o que o `httpx` pode lançar. Isso decide a ordem dos `except` do `revisor`: primeiro `TimeoutException`, depois `ConnectError`, e no final `HTTPError` para recolher o que sobrar (um servidor que fecha no meio de uma resposta, por exemplo). As três ramificações devolvem um `Resultado` com estado `CAIDO` e o seu detalhe (`tiempo agotado`, `sin conexión` ou `error de red`). **Nunca deixam a exceção escapar.**

De onde sai o número: cada `Servicio` traz o seu `timeout_ms`, por padrão 5000, em milissegundos. O `httpx` quer segundos, então o `revisor` divide: `httpx.Timeout(servicio.timeout_ms / 1000)`. A unidade vive no nome (`timeout_ms`) justamente para que essa conversão não seja esquecida. **Aqui termina a primeira sessão.**

### 9.3 Corrotinas: funções que podem esperar

#### 9.3.1 Uma corrotina não é executada ao chamá-la

Na segunda sessão chega a ideia que mais custa. Durante os 2.3 segundos que `inventario` leva para responder, o seu programa não faz nada: espera. Todo esse tempo, o processador está livre. Uma **corrotina** é uma função que pode **pausar no ponto em que espera** e deixar que outra coisa use esse tempo. Escreve-se com `async def`, em vez de `def`:

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

`saludar` é uma função normal em tudo menos na sua primeira palavra. Mas repare no que `print(saludar())` imprimiu: **não** diz `hola`. Diz `<coroutine object saludar at 0x...>`. Chamar uma função `async def` não executa o seu corpo; cria um **objeto corrotina**, uma receita em pausa. [A documentação do `asyncio`](https://docs.python.org/pt-br/3/library/asyncio-task.html) diz assim: chamar uma corrotina não a programa para ser executada, e no seu exemplo `nested()` é chamada sem ser esperada: o objeto é criado, mas o corpo “não será executado de forma alguma”. E como o objeto foi jogado no lixo sem que ninguém o executasse, o Python avisa: `RuntimeWarning: coroutine 'saludar' was never awaited`, “a corrotina `saludar` nunca foi esperada”. O aviso inclui a linha do programa onde foi chamada e é **o sinal mais comum** de que você esqueceu um `await`.

#### 9.3.2 `asyncio.run`: o ponto de partida

Como se executa, então, uma corrotina? Ela precisa de um coordenador que a rode, o **loop de eventos** (*event loop*): um programa pequeno, dentro do Python, que reparte o tempo entre as corrotinas pausadas. Você não o maneja diretamente. [`asyncio.run`](https://docs.python.org/pt-br/3/library/asyncio-runner.html) o cria, executa a corrotina que você lhe der até ela terminar, devolve o seu resultado e fecha o loop:

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

Agora sim: `hola`. O `asyncio.run` se escreve uma única vez, na entrada do programa, e a partir dali todo o resto se encadeia com `await`. No `revisor` ficará em `cli.py`.

#### 9.3.3 `await` e `async with`: esperar outra corrotina

Dentro de uma corrotina, `await` significa **“espere aqui até que esta outra coisa termine, e enquanto espera, deixe o loop fazer outras coisas”**. É a forma explícita de pausar uma corrotina, e só funciona dentro de uma função `async def`. (Há outras duas, que esperam sem que você escreva a palavra: `async with`, que você verá em um momento, e `async for`, que o curso não usa; [a referência da linguagem](https://docs.python.org/pt-br/3/reference/compound_stmts.html#the-async-with-statement) explica que por dentro elas fazem `await`.) A corrotina que você mais vai esperar no curso é uma requisição do `httpx`, e para isso o `httpx` traz [uma versão assíncrona do cliente](https://www.python-httpx.org/async/), `httpx.AsyncClient`, que se usa com um `async with`:

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

`async with` é o `with` da Lição 6 para recursos cuja abertura e fechamento **também** podem esperar: criar e fechar o cliente de rede é uma operação desse tipo. Dentro, `cliente.get(...)` é uma corrotina; o `await` a espera, e o que se obtém é a resposta. Observe que a resposta é exatamente a mesma do `httpx.get` síncrono: `status_code`, `is_error` e o resto. A diferença está em como se espera. E o cliente **é criado uma vez e reutilizado** para várias requisições: abrir e fechar um por consulta seria como desligar e discar de novo cada vez que você faz uma pergunta.

### 9.4 Um `await` após o outro não poupa tempo: a série

Aqui está o mal-entendido mais difundido sobre o `asyncio`, e convém desmontá-lo com uma medição. Um iniciante lê “assíncrono” e supõe “mais rápido”. Não é. Veja este programa, que espera três vezes meio segundo, uma após a outra, cada uma com `await` ([`asyncio.sleep`](https://docs.python.org/pt-br/3/library/asyncio-task.html#sleeping) é a espera assíncrona de sempre):

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

A última linha pergunta `1.5 <= total < 2.0`, as duas coisas ao mesmo tempo: que `total` seja pelo menos 1.5 e menos de 2. As três esperas levaram a **soma**: 1.5 segundo ou mais. Você não ganhou nada. A razão está no que `await` faz de verdade: pausa **esta** corrotina e oferece ao loop atender outras, mas neste programa **não há outras**. O loop oferece a vez e ninguém a toma. É a mesma [sequência que a documentação do Python mostra](https://docs.python.org/pt-br/3/library/asyncio-task.html): um `await` seguido de outro `await` se executa em série. Para ganhar tempo são necessárias **várias corrotinas vivas ao mesmo tempo**, e isso se consegue com tarefas (`asyncio.TaskGroup`), que é o conteúdo da Lição 10.

O `revisor` de hoje, então, será uma versão assíncrona que se comporta **como a síncrona**: consulta os serviços um de cada vez. Para quê, então? Primeiro, porque é o passo intermediário que torna visível o ganho: a Lição 10 mede a mesma tabela de serviços em série e em paralelo, e precisa do ponto de partida. Segundo, porque mudar de `def` para `async def` toca toda a cadeia de chamadas, e é mais fácil de entender fazendo isso antes de colocar concorrência. E terceiro, porque o que importa neste passo é tudo o que não tem a ver com o tempo: tempos limite, exceções, classificação.

### 9.5 O `revisor` consulta de verdade

Com tudo o que veio antes, o `revision.py` é reescrito por inteiro. O `SIMULADO` é apagado, e as duas funções viram corrotinas:

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

Leia `revisar` de cima para baixo. Recebe um **cliente** e um **serviço**; o cliente vem de fora para que seja reutilizado. Monta o `httpx.Timeout` com o `timeout_ms` do serviço, anota a hora com `time.perf_counter()` (o relógio de alta precisão do Python) e faz a requisição com `await`. Os três primeiros `except` são os de 9.2, **do mais específico ao mais geral**, e cada um devolve um `Resultado` fora do ar com o seu texto. O quarto captura algo que não é um erro de rede: um endereço que passou pela validação da Lição 6 mas que o `httpx` não pode usar. Acontece, por exemplo, com `http://999.1.1.1:8099/pagos`: para o `urlsplit` é um endereço com servidor e porta, mas cada uma das quatro partes de um endereço IP vai de 0 a 255, e 999 não cabe, e o `httpx` o rejeita com `httpx.InvalidURL`, que **não** é filha de `httpx.HTTPError` (diz isso [a sua hierarquia de exceções](https://www.python-httpx.org/exceptions/)). Outros nomes de servidor impossíveis terminam em um `ValueError` das bibliotecas que o `httpx` usa por dentro. Sem este `except`, um único desses serviços derrubaria o relatório inteiro com um *traceback*; com ele, aparece na sua linha como `CAIDO`, com o detalhe `dirección inválida`, e os demais são verificados igual. O `ValueError` é capturado aqui, em torno de uma única chamada, e não no programa todo: um `ValueError` do seu próprio código, fora do `try`, continuaria o interrompendo com o seu relatório, como deve ser. Se não houve exceção, mede quanto passou (`round(... * 1000)` converte segundos em milissegundos inteiros), classifica com a mesma função `clasificar` de sempre, que recebe o código real, e monta o `Resultado` com o código como detalhe. Um `503` passa por aqui: não é exceção, sai com `clasificar(503, 95)` e se converte em `CAIDO` com detalhe `503`.

`revisar_todos` abre **um** cliente com `async with` e percorre os serviços com um `for` e um `await` por volta. É a série de 9.4, escrita de propósito. A ordem dos resultados é a da configuração.

O `main` em `cli.py` só muda em uma linha: a chamada é envolvida em `asyncio.run`.

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

Para que o `asyncio.run` tenha algo a executar, `revisar_todos(servicios)` sem `await` produz uma corrotina, e o `asyncio.run` a roda. É o único `asyncio.run` do programa. Os testes continuam chamando `main` como uma função normal, então **não precisam ser corrotinas**; isso é o que permite não instalar nenhum complemento do `pytest` para código assíncrono. As outras mudanças são dados. O `pyproject.toml` sobe para `0.8.0` e declara a primeira dependência do pacote, o `httpx`:

```toml
dependencies = ["httpx>=0.28"]
```

Reinstale o pacote (`pip install -e .`) para que o ambiente veja a dependência e a versão nova. E o `servicios.toml` aponta agora para o servidor de prática: os mesmos quatro nomes, outros endereços. (O projeto completo está em 9.6.)

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

Com o servidor de prática aberto no outro terminal, rode o `revisor` e olhe o código de saída:

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

É a tabela do programa do curso, agora **medida**: `catalogo` e `pagos` no ar com tempos reais (o servidor espera 142 e 87 ms, e cada requisição acrescenta uns milissegundos de rede, então você verá números como 156 e 98, diferentes a cada execução), `inventario` lento com 2.3 s, `reportes` fora do ar com `sin conexión` (ninguém escuta na 8098). O resumo conta dois no ar, um lento, um fora do ar, e o código de saída é `1`, o mesmo de sempre, pela mesma razão: há um lento e um fora do ar. O que mudou é que agora é verdade.

Quanto leva? Em série, a soma: 142 + 2300 + 87 são uns 2.5 segundos de espera mais o que leva para iniciar o Python e carregar o `httpx`. Medida com o comando `time` do terminal, uma execução completa dura uns 2.7 segundos. A sua dará um número próximo, não igual. Essa cifra é o ponto de partida da Lição 10. Quem a mede é o Exercício 1.

E os testes: rode-os.

```text
$ cd fig09_11
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

Continuam sendo **21**. O único arquivo de testes que mudou é `tests/test_cli.py`, e não por capricho. O seu primeiro teste usava os dados simulados para comprovar que `main` devolve `1`, e eles já não existem; e as funções falsas do `monkeypatch` agora devolvem uma corrotina, porque a verdadeira é uma corrotina e `main` faz `asyncio.run` do que lhe devolverem. Por isso são `async def`:

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

Um aviso que é preciso dizer em voz alta: **passa `21 passed` e, no entanto, o que é novo não tem um único teste**. Nada do que você acabou de escrever (o tempo limite, a classificação de um `503`, o `sin conexión`) é exercitado nesses 21. Os dois testes de `test_cli.py` substituem `revisar_todos` por completo, então o código de rede nem é tocado. Esse é o tamanho do buraco, e é o motivo da Lição 10: como testar código de rede sem rede.

### 9.6 O projeto completo

A foto do projeto ao terminar a lição. Os arquivos que você já viu são `laboratorio.py`, `servicios.toml`, `revision.py`, `cli.py` e `tests/test_cli.py`. O `pyproject.toml` é o da Lição 8 com a versão e a dependência novas:

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

Os demais arquivos **não mudam** em relação à Lição 8, e se repetem aqui só para que o projeto esteja completo:

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

As quatro verificações da Lição 8, que agora também cobrem o código assíncrono:

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

## O erro que você vai ver

### `RuntimeWarning: coroutine 'saludar' was never awaited`

Você o viu em 9.3.1, com o programa `fig09_07.py`, e vale a pena repetir como se lê. O aviso não é um erro: o programa **segue** e termina com código `0`, que é o perigoso, porque há um aviso entre dezenas de linhas e é fácil deixá-lo passar. Diz três coisas: o arquivo e a linha onde você chamou a corrotina sem esperá-la (`fig09_07.py:6`, e embaixo imprime a própria linha, `print(saludar())`), qual corrotina foi (`'saludar'`), e a consequência: o seu corpo nunca foi executado. A cura quase sempre é uma palavra: colocar `await` na frente da chamada, ou passá-la a `asyncio.run`.

No projeto, o `mypy` avisa você **antes** de rodar. Tire o `await` da linha `resultados.append(await revisar(cliente, servicio))` em `revisar_todos`, e isto é o que o `mypy` diz:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
Found 1 error in 1 file (checked 11 source files)
```

Você tinha dito à lista que guardava `Resultado`, e está lhe dando uma `Coroutine`. E o `mypy` adivinha com uma nota: “Esqueceu o `await`?”. É o tipo de ajuda pela qual os tipos foram escritos na Lição 8. Se você ignora o aviso e roda o programa, a tabela imprime o seu cabeçalho e para com `AttributeError: 'coroutine' object has no attribute 'servicio'` (a última linha do *traceback*), seguido do mesmo `RuntimeWarning` no final.

### Todos os serviços dizem `sin conexión`

Se você esquece de ligar o servidor de prática, o `revisor` não cai; faz exatamente o que deve. Isto é o que ele imprime com o servidor desligado:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO          —  sin conexión
inventario  CAIDO          —  sin conexión
pagos       CAIDO          —  sin conexión
reportes    CAIDO          —  sin conexión

4 servicios · 0 arriba · 0 lentos · 4 caídos · promedio —
```

Não há `Traceback`. Os quatro serviços estão `CAIDO`, com `sin conexión` e sem tempo (`—`), porque ninguém responde na porta 8099, igual à 8098. Isto é o design funcionando: um serviço que não responde é um **dado**, não uma exceção que derruba o relatório. O sinal para você é que `reportes` não deveria ser o único fora do ar: se os quatro estão, antes de procurar um erro no seu código, veja se o segundo terminal continua aberto. (Repare também na média: sai como `—`, igual ao tempo de cada linha, porque não há tempos para tirar a média. É a mesma decisão da Lição 2: o que não foi medido não vale `0`.)

### O teste que quebra porque o seu falso deixou de ser uma corrotina

Se você deixa `tests/test_cli.py` como estava na Lição 8, e só muda `revision.py` e `cli.py`, o `pytest -q` diz `1 failed, 20 passed`. O vermelho é o teste que usa o falso com `def` em vez de `async def`. A última linha do erro muda de redação conforme a sua versão do Python, mas diz o mesmo:

```text
ValueError: a coroutine was expected, got [Resultado(servicio=Servicio(nombre='catalogo', ...
```

(no Python 3.12) ou

```text
TypeError: An asyncio.Future, a coroutine or an awaitable is required
```

(no 3.14). O `asyncio.run(...)` recebeu uma **lista** e esperava uma corrotina, porque `main` faz `asyncio.run(revisar_todos(servicios))` e o falso, por ser `def`, devolveu o resultado direto. A correção é a que você viu: fazer o falso `async def`.

Mas há algo mais sutil. Um **segundo** teste antigo, o que rodava com os dados simulados, **continua em verde**, e não deveria. Esse teste usava endereços `https://catalogo.example` e esperava que `main` devolvesse `1`. Agora `main` faz requisições de verdade a esses endereços inventados, não consegue conectar a nenhum, marca todos como fora do ar e devolve `1`. O teste passa, mas **por uma razão completamente diferente** da que o escreveu, e depende de que `.example` nunca resolva e de que a sua rede responda rápido que não existe. É o que acontece quando um teste verde sustenta algo que já não é o que diz: o falso foi substituído por um teste que não faz o que o seu nome promete. Por isso ele foi reescrito com um falso explícito.

## O que se faz errado

**Fazer uma requisição sem tempo limite.** É o erro que esta lição existe para evitar. Com o `urllib`, sem `timeout=`, o programa espera o que for preciso, inclusive para sempre. Com o `httpx`, o limite padrão é 5 s, mas depender de um valor padrão sem saber é deixar uma decisão importante nas mãos de outro. O `revisor` o fixa sempre, por serviço.

**Capturar `Exception` e seguir.** `except Exception: pass` em torno de uma requisição faz um `ReadTimeout`, um `ConnectError` e um erro de programação parecerem idênticos: nada. O `revisor` captura três exceções concretas, cada uma com o seu texto, e deixa qualquer outra aparecer.

**Imprimir a mensagem do sistema operacional.** `[Errno 111] Connection refused` muda com o sistema e com o idioma; o relatório de um serviço não deve mudar de texto conforme onde é executado. O detalhe é uma de três frases fixas.

**Supor que `async` é mais rápido.** Você desmontou isso em 9.4: um `await` após o outro soma os seus tempos. Uma função `async` sem concorrência é uma função síncrona com mais cerimônia.

**Chamar uma corrotina sem `await`.** O aviso de 9.3.1. Com o `mypy` em modo estrito vira um erro de tipos, por isso convém rodá-lo.

**Bloquear dentro de uma corrotina.** Um `time.sleep(1)` dentro de uma `async def` para **todo** o programa por um segundo: ninguém mais pode avançar, porque o loop está preso dentro dessa chamada. Dentro de uma corrotina, a espera é `await asyncio.sleep(1)`. O mesmo vale para as bibliotecas de rede que não são assíncronas, como o `urllib` ou o `httpx.get`.

**Criar um cliente por requisição.** `httpx.AsyncClient()` abre um grupo de conexões que são reutilizadas. Abrir e fechar um a cada consulta joga fora essa economia; o `revisor` abre um no início de `revisar_todos` e o compartilha.

**Tratar um `503` como se fosse uma falha do programa.** Um serviço que responde com erro é o resultado do trabalho, não um incidente do `revisor`. Por isso se lê o código e se classifica; `raise_for_status()` converteria o dado em exceção.

**Colocar `0` onde não houve resposta.** Um serviço fora do ar tem `tiempo_ms=None`, não `0`: com zero, a média premia o que está fora do ar. É a mesma lição da Lição 2, em um projeto maior.

## Exercícios

### Exercício 1 — Meça a série com o relógio

Com o servidor de prática ligado, meça quanto o `revisor` completo leva: `time python -m revisor`. Antes de rodá-lo, **preveja** o número a partir do que você sabe: a soma do que cada serviço leva. Rode-o três vezes e anote as três no seu diário de bordo. Por que não são idênticas? Esse número é o seu ponto de partida para a Lição 10.

### Exercício 2 — Tire o tempo limite de uma requisição e veja por que é perigoso

Escreva um programa de seis linhas que use `httpx.get` com `timeout=None` (que [desativa o tempo limite](https://www.python-httpx.org/advanced/timeouts/)) contra `http://127.0.0.1:8099/espera/60000`, que leva um minuto. Rode-o, deixe passar cinco segundos e pressione `Ctrl`+`C`. O que é impresso? Quanto teria levado para terminar sozinho? Depois coloque `timeout=2.0` e compare.

### Exercício 3 — Os dois serviços a mais

Adicione ao seu `servicios.toml` `facturacion` (`http://127.0.0.1:8099/facturacion`) e `notificaciones` (`http://127.0.0.1:8099/notificaciones`, com `timeout_ms = 1000`). Antes de rodar, preveja o estado e o detalhe de cada um, e qual será a linha do resumo. Algo na tabela lhe parece estranho? Devolva o arquivo aos seus quatro serviços ao terminar.

### Exercício 4 — Esqueça um `await` de propósito

Em `revisar_todos`, tire o `await` de `resultados.append(await revisar(cliente, servicio))`. Rode o `mypy`, depois `python -m revisor`, e leia os dois sinais: o que diz cada um, e qual chegou primeiro. Restitua o `await`.

## Soluções

### Solução 1

A previsão: 142 + 2300 + 87 = 2529 ms para os três que respondem, mais o que leva para tentar conectar com `reportes` (uns milissegundos, porque rejeitam de imediato), mais a inicialização do Python e do `httpx`. Isso dá uns **2.6 ou 2.7 segundos**, e é o que o relógio mede: uma execução de referência deu 2.674 s. As três execuções são parecidas, mas não idênticas, porque o servidor, o sistema operacional e a rede acrescentam pequenas variações de uns milissegundos a cada vez. O importante é a ordem de grandeza: uns 2.5 segundos, porque **é a soma**. Se a Lição 10 conseguir que seja próximo de 2.3 s (o serviço mais lento), terá ganhado menos do que parece com quatro serviços; por isso a medição forte dessa lição usa vinte.

### Solução 2

```python
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/espera/60000", timeout=None)
print(respuesta.status_code)
```

Com `Ctrl`+`C` aos cinco segundos, o Python imprime um *traceback* que termina em `KeyboardInterrupt`: quem interrompeu foi você, não o programa. Teria levado **um minuto inteiro** para terminar sozinho, sem imprimir nada nesse meio-tempo. Contra um servidor que nunca responde, não teria terminado nunca: é isso que significa “sem tempo limite”. Com `timeout=2.0` o programa lança `httpx.ReadTimeout` aos dois segundos. Esse `ReadTimeout` é uma exceção **que sim se pode capturar**, que é o que `revisar` faz.

### Solução 3

A previsão: `facturacion` responde `503` em 95 ms, então `CAIDO` com detalhe `503` e tempo de uns 100 ms. `notificaciones` leva 10 s mas o seu limite é de 1 s: `CAIDO` com `tiempo agotado` e sem tempo. O resumo: `6 servicios · 2 arriba · 1 lento · 3 caídos`. Isto é o que imprime:

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

O estranho é a última linha: `notificacionesCAIDO`, sem separação. O nome tem 14 letras e a coluna `SERVICIO` mede 12 (`{nombre:<12}`), então transborda e gruda na seguinte. É um limite real da tabela como está hoje, e é uma das coisas que a Lição 11 corrige calculando a largura a partir do nome mais longo. Conte também o tempo: a execução inteira levou uns 3.8 s em vez de 2.7, porque `notificaciones` espera o seu segundo completo antes de desistir. Cada serviço lento ou travado acrescenta a sua espera à série, que é o que a Lição 10 vem resolver.

### Solução 4

O `mypy` reclama **primeiro**, sem rodar nada:

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
```

Ao rodar o programa, imprime-se o cabeçalho e ele para com `AttributeError: 'coroutine' object has no attribute 'servicio'`, porque a lista tem corrotinas em vez de resultados, e no final aparece `RuntimeWarning: coroutine 'revisar' was never awaited`. Chegou primeiro o `mypy`, e o fez com a causa e com a sugestão; o erro em tempo de execução só mostra a consequência. É o argumento a favor de rodar o `mypy` antes do programa.

## Como sei que consegui

- [ ] Com o servidor de prática ligado, `python -m revisor` imprime a tabela de quatro serviços com `catalogo` e `pagos` no ar, `inventario` lento (`2.3s`) e `reportes` fora do ar com `sin conexión`, e `echo $?` imprime `1`.
- [ ] Com o servidor desligado, os quatro dizem `CAIDO` e `sin conexión`, e o programa não imprime nenhum *traceback*.
- [ ] `pytest -q` diz `21 passed` (o mesmo número da Lição 8), e você consegue explicar que parte do programa **nenhum** dos 21 cobre.
- [ ] `mypy` diz `Success: no issues found in 11 source files`, `ruff check` diz `All checks passed!` e `ruff format --check` diz que os arquivos já estão formatados.
- [ ] Você mediu a execução com `time` e o seu número está perto de 2.7 segundos, e sabe explicar por que é a soma e não o máximo.
- [ ] Você consegue explicar o que faz `await`, o que faz `asyncio.run` e por que `saludar()` sozinho não imprime `hola`.
- [ ] Você consegue dizer com que exceção do `httpx` termina um serviço que não responde e com qual um onde ninguém escuta, e por que um `503` não é uma exceção.

## Resumo

Responda sem olhar a lição:

1. O que traz uma resposta HTTP, e que famílias de código de status existem? Quais deixam um serviço `CAIDO`?
2. O que o `urllib` faz quando o servidor responde `503`, e o que faz o `httpx`?
3. Por que o `urlopen` aceita um endereço `file://`, e o que o detém no `revisor`?
4. Que tempo limite o `urllib` tem por padrão, e qual o `httpx`?
5. Que exceção do `httpx` produz um serviço que não responde, e qual um onde ninguém escuta?
6. O que faz `asyncio.run`? O que acontece se você chama uma função `async def` sem `await` nem `asyncio.run`?
7. Por que três `await` seguidos de meio segundo levam 1.5 s e não 0.5 s?
8. Por que o relatório da Lição 9 continua dizendo `21 passed` e o que ficou sem testar?

## Para ler mais

- [HTTPX, “Timeouts”](https://www.python-httpx.org/advanced/timeouts/) — os quatro tempos limite (`connect`, `read`, `write`, `pool`), o valor padrão e como desativá-los. Em inglês, como quase toda a documentação do ecossistema. Consultado em 7 de outubro de 2026.
- [Python, “Coroutines and tasks”](https://docs.python.org/pt-br/3/library/asyncio-task.html) — a documentação oficial do `asyncio`: corrotinas, `await`, tarefas e o aviso da corrotina nunca esperada. Consultado em 7 de outubro de 2026.
- [RFC 9110, “HTTP Semantics”](https://www.rfc-editor.org/rfc/rfc9110.html) — o padrão do HTTP; a seção de códigos de status define o que cada número quer dizer. É um texto para consultar, não para ler de cabo a rabo. Consultado em 7 de outubro de 2026.
- [PEP 492, “Coroutines with async and await syntax”](https://peps.python.org/pep-0492/) — o documento que introduziu `async` e `await`; explica por que são palavras reservadas da linguagem. Consultado em 7 de outubro de 2026.
