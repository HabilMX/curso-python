# Lição 10 — Concorrência com limites e testes sem rede

**Tempo:** 2 × 90 min (a primeira sessão vai até o final de 10.2; a segunda começa em 10.3)

**O que você constrói:** o `revisor` concorrente e testado, versão 0.9.0

**O que você aprende:** `asyncio.TaskGroup`; `asyncio.timeout()` e `asyncio.Semaphore`; grupos de exceções (`ExceptionGroup`, `except*`) e por que uma falha não derruba o relatório; testes sem rede com `httpx.MockTransport` e `monkeypatch`

**De onde você vem.** Você traz o pacote da [Lição 9](09-http-y-asyncio.md): o `revisor` já consulta de verdade, com `httpx`, um tempo limite por serviço e uma função `revisar` que nunca deixa escapar um erro de rede. Mas faz isso **em fila**: `for` e `await`, um serviço de cada vez. Com os quatro serviços do laboratório a execução leva a soma das esperas, uns 2.5 segundos, e com vinte serviços de meio segundo levaria dez. Além disso tem uma dívida que a lição anterior disse de frente: os seus 21 testes não tocam em nada do que é novo, porque testar código que usa a rede você ainda não sabe fazer. Hoje as duas coisas são pagas. Você trabalha na sua pasta `~/curso-python/revisor/`, com o ambiente virtual ativado, e precisa ter à mão o `laboratorio.py` da lição 9 para a parte de medir.

**O que esta lição não faz.** Ela não muda o que o `revisor` imprime: a tabela e o JSON saem igual à Lição 9. O que muda é **quanto leva** e **quão seguro é**. Também não usa threads nem processos: toda a concorrência de hoje ocorre em uma única thread, que é o que convém quando o que se faz é esperar a rede. O relatório final com largura de coluna calculada, o registro de eventos (`logging`) e a instalação como comando são da [Lição 11](11-el-programa-terminado.md).

## Ao terminar, você vai conseguir

- Lançar várias consultas ao mesmo tempo com `asyncio.TaskGroup`, recolher os seus resultados na ordem da configuração e medir com o relógio que o total se parece com o serviço mais lento e não com a soma.
- Explicar por que uma tarefa só cede a vez em um `await`, e por que um `time.sleep` dentro de uma corrotina desfaz todo o ganho.
- Colocar um teto de tempo em uma operação inteira com `asyncio.timeout()` e dizer em que ele se distingue dos tempos limite do `httpx`.
- Limitar quantas consultas rodam ao mesmo tempo com `asyncio.Semaphore`, e explicar por que com 20 serviços e um limite de 10 o tempo é o dobro do que com limite 20.
- Ler um `ExceptionGroup` e capturar o que ele contém com `except*`; dizer por que `revisar` converte os erros de rede em resultados e por que **não** converte os erros de programação.
- Testar `revisar` e `revisar_todos` sem tocar na rede, com `httpx.MockTransport`, e testar `main` trocando uma função por outra com `monkeypatch`.
- Comprovar em vermelho um teste (quebrar o código, vê-lo falhar, consertá-lo) e ler a contagem do relatório do `pytest`.

## O porquê antes do como

Imagine que o `revisor` é usado pela equipe de plantão de uma empresa para verificar sessenta serviços a cada cinco minutos. Cada serviço saudável responde em meio segundo; os que estão fora do ar demoram a desistir até o seu tempo limite, digamos cinco segundos. Em fila, no melhor dia a execução leva trinta segundos, e no pior dia, com dez serviços fora do ar, leva setenta e cinco (cinquenta saudáveis a meio segundo, mais dez fora do ar a cinco segundos). Mas o computador não esteve trabalhando durante esses setenta e cinco segundos: esteve **esperando**. Mandou uma requisição, ficou olhando a parede até a resposta chegar, e só então mandou a seguinte. A rede não precisa que o programa faça fila: as sessenta requisições podem estar viajando ao mesmo tempo, e o programa só tem de recolher as respostas conforme chegam.

Isso é o que o `asyncio` faz bem, e por isso existe esta lição. Mas há três problemas escondidos atrás de “faça tudo ao mesmo tempo”, e cada um é um conceito de hoje.

O primeiro é **como se lançam e se recolhem** muitas consultas sem perder nenhuma. O Python 3.11 trouxe uma ferramenta pensada para isso, `asyncio.TaskGroup`, que dispara as tarefas, espera por todas antes de seguir e não deixa que nenhuma se perca pelo caminho.

O segundo é **até onde**. “Tudo ao mesmo tempo” com sessenta serviços é razoável. Com seis mil pode ser um ataque aos seus próprios servidores, ou o seu sistema operacional dizendo que não lhe dá mais conexões. É preciso um limite de quantas consultas rodam simultaneamente, e é preciso um teto de tempo para que nenhuma fique pendurada para sempre.

O terceiro é **o que acontece quando algo falha**. Em fila, um erro interrompe o programa no ponto exato em que ocorreu, e é fácil de entender. Com muitas tarefas ao mesmo tempo, uma falha pode afetar as demais, e o que o Python entrega a você não é uma exceção, e sim um **grupo** delas. Se você não o entende, um único serviço fora do ar pode derrubar o relatório inteiro, que é exatamente o contrário do que o `revisor` promete.

E por baixo de tudo, o quarto problema, o da confiança: um programa que faz tantas coisas ao mesmo tempo, com tempos e falhas misturados, **não pode ser testado à mão** de maneira repetível. Se para comprovar que “um serviço travado não derruba o relatório” você precisa travar um serviço de verdade, nunca vai comprovar duas vezes igual. A quarta parte da lição ensina a testar tudo isso sem rede: com um servidor de mentira que responde o que você disser, na hora, sempre igual.

## Os conceitos

### 10.1 `TaskGroup`: todas ao mesmo tempo

#### 10.1.1 O que custa esperar em fila

Antes de consertar algo é preciso medi-lo. Este primeiro programa não usa a rede: cada “serviço” é uma espera de verdade, feita com `asyncio.sleep`, que é a forma de dizer “não faça nada durante este tempo, mas me deixe fazer outra coisa enquanto isso”. As esperas são as de quatro serviços inventados, de um décimo a meio segundo, para que as execuções sejam curtas.

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

Leia `main` de cima para baixo. `time.perf_counter()` é o relógio para medir intervalos que você já usou na Lição 9: chama-se no começo e no final, e a subtração é o tempo decorrido. O `for` percorre o dicionário com `.items()` (que dá cada par nome-espera) e, para cada um, faz `await consultar(...)`. O `await` diz “espere aqui até esta corrotina terminar”; até que ela termine, o `for` não passa para a volta seguinte. Por isso as respostas saem na ordem em que foram pedidas, e por isso o total, 1.1 segundo, é a soma exata: 0.3 mais 0.5 mais 0.1 mais 0.2.

É o mesmo problema que você mediu na Lição 9 com o `revisor`: `await` sobre **uma corrotina sozinha** espera que ela termine antes de seguir. Não é um defeito do `await`; é o que ele significa. Para que duas esperas ocorram ao mesmo tempo é preciso que as duas **existam** ao mesmo tempo, e para isso serve uma tarefa.

#### 10.1.2 Uma tarefa: uma corrotina que já está em andamento

Uma **corrotina** é uma receita: `consultar("catalogo", 0.3)` não faz nada, só produz o objeto-receita, e a receita começa a ser executada quando alguém faz `await` nela. Uma **tarefa** (*task*) é uma corrotina à qual já se deu corda: o loop de eventos a tem anotada na sua lista de pendentes e a executa assim que puder, **sem que ninguém a esteja esperando ainda**. O **loop de eventos** (*event loop*) é a peça do `asyncio` que mantém essa lista: pega uma tarefa, a executa até esbarrar em um `await` que tem de esperar, a coloca em pausa, pega a seguinte, e assim sucessivamente, em uma única thread.

Com isso em mãos, a versão ao mesmo tempo:

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

Mudou uma única coisa: em vez de `await consultar(...)` dentro do `for`, faz-se `grupo.create_task(consultar(...))`. Isso **não espera**: registra a tarefa e volta em seguida, com um objeto `Task` na mão. Por isso o `for` (aqui, dentro de uma compreensão de lista, que é o `for` em uma linha da Lição 4) passa pelos quatro serviços num instante e deixa quatro tarefas pendentes. Veja a saída: os quatro “empieza” saem primeiro, seguidos, antes que nenhum responda. Depois respondem em ordem de **rapidez**, não de requisição: `pagos` (0.1 s), `reportes` (0.2 s), `catalogo` (0.3 s), `inventario` (0.5 s). E o total já não é 1.1 e sim 0.5: o do mais lento.

E o `async with asyncio.TaskGroup() as grupo:`? É o que torna isso seguro. Funciona como o `with` da Lição 6: ao **sair** do bloco, o grupo **espera que todas as tarefas que criou terminem**. Por isso a linha `print(f"a la vez: ...")`, que está depois do bloco, só é executada quando as quatro responderam. Você pode criar as tarefas onde quiser dentro do bloco; não pode esquecer nenhuma, porque o bloco não deixa você sair enquanto houver uma viva. Isso é o que a [documentação do `asyncio`](https://docs.python.org/pt-br/3/library/asyncio-task.html#task-groups) chama de *concorrência estruturada*: as tarefas nascem e morrem dentro de um bloco com recuo, assim como um `with` fecha o seu arquivo.

#### 10.1.3 Os resultados e a sua ordem

`create_task` devolve a tarefa, e a tarefa guarda o seu resultado. Depois do bloco, `tarea.result()` o entrega: se a tarefa terminou bem, o valor que a sua função devolveu; se falhou, lança de novo a exceção. Repare no detalhe que importa para o `revisor`: guardamos as tarefas **em uma lista, na ordem dos serviços**, e depois tiramos os resultados **percorrendo essa lista**. As respostas chegaram em desordem (pagos primeiro), mas a última linha da saída, `['catalogo', 'inventario', 'pagos', 'reportes']`, está na ordem da configuração. Essa ordem não é um luxo: um relatório em que as linhas mudam de lugar a cada execução é ilegível, e um JSON que se compara com o de ontem precisa estar na mesma ordem. A regra é simples: **a ordem em que chegam as respostas quem decide é a rede; a ordem em que se mostram quem decide é você**, e se decide guardando as tarefas em uma lista e não empilhando os resultados conforme vão terminando.

#### 10.1.4 Uma tarefa só cede a vez em um `await`

Falta uma peça para que o modelo mental esteja completo, e é a que mais produz erros. O loop de eventos roda **em uma única thread**. Quando ele executa uma tarefa, essa tarefa tem a thread inteira até que ela mesma a solte, e a solta unicamente em um `await` que tem de esperar. Entre dois `await`, mais ninguém roda. A isso se chama concorrência **cooperativa**: as tarefas cooperam cedendo a vez. Se uma tarefa não coopera, bloqueia todas. Veja o que acontece se em vez de `await asyncio.sleep(...)` se usa o `time.sleep(...)` de sempre, que é uma espera que **não cede nada**:

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

É o mesmo `TaskGroup` da figura anterior, com as quatro tarefas criadas igual. Mas o resultado é outro: elas são impressas na ordem em que foram criadas, não na de rapidez, e o total é 1.1 segundo, a soma. Por quê? Porque a primeira tarefa chegou a `time.sleep(0.3)`, e `time.sleep` detém **a thread**, e com a thread detida o loop de eventos não consegue nem passar para a tarefa seguinte. As outras três esperaram a sua vez, em fila, ainda que estejam em um `TaskGroup`. Este erro é especialmente traiçoeiro porque **o programa não falha**: dá o resultado correto, só que tão lento como se não houvesse concorrência. O comentário `# noqa: ASYNC251` está ali porque o `ruff` (a ferramenta da Lição 8) conhece este erro e o marca, embora não com o conjunto de regras do `revisor`: `ASYNC251` é da coleção `ASYNC`, a dos erros do `asyncio`, que não está no `select` do projeto (`E`, `F`, `I`, `B`, `UP`). Se você a pedir, `ruff check --select ASYNC` sobre esta figura sem esse comentário diz ``ASYNC251 Async functions should not call `time.sleep` ``. E se o seu código usa `asyncio` a sério, é uma boa candidata a entrar no seu `select`. Nesta figura o deixamos de propósito para mostrar o dano; no seu código real, o aviso do `ruff` é uma pista a seguir.

A regra prática: dentro de uma corrotina, tudo o que espera (rede, disco lento, tempo) deve ser um `await` sobre algo feito para o `asyncio`: `asyncio.sleep`, `httpx.AsyncClient`. Uma chamada normal que demora (um `time.sleep`, um cálculo longo, uma função do `requests`) não coopera e leva o loop inteiro junto. É a razão pela qual o curso usa `httpx` e não `requests`: o `httpx` sabe esperar sem bloquear. O capítulo da documentação sobre [como desenvolver com `asyncio`](https://docs.python.org/pt-br/3/library/asyncio-dev.html) traz o modo de depuração, que avisa quando uma tarefa retém a thread por tempo demais.

### 10.2 Limites: um teto de tempo e um limite de simultâneas

#### 10.2.1 `asyncio.timeout()`: o teto de uma operação inteira

Desde a Lição 9 você sabe que toda requisição deve levar um tempo limite: sem ele, um serviço travado faz o `revisor` esperar para sempre. O `httpx` já tem um, o que você passa com `httpx.Timeout(...)`. Então para que outro?

Porque os tempos limite do `httpx` medem **fases**, não o total. Segundo [a sua documentação](https://www.python-httpx.org/advanced/timeouts/), o `httpx` distingue quatro: o de **conexão** (quanto esperar para abrir o canal), o de **leitura** (quanto esperar o pedaço seguinte de dados), o de **escrita** e o de **espera de um canal livre no conjunto de conexões**. `httpx.Timeout(5.0)` põe esses quatro em 5 segundos, cada um por si. Um servidor que manda um byte a cada quatro segundos nunca dispara o de leitura —cada pedaço chega a tempo—, e a resposta pode levar minutos. O `httpx` não fez nada errado: cada fase cumpriu o seu limite. O que falta é um limite ao **conjunto**. Isso é o `asyncio.timeout()`, que existe desde o Python 3.11 e está na [documentação do `asyncio`](https://docs.python.org/pt-br/3/library/asyncio-task.html#timeouts):

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

O bloco `async with asyncio.timeout(1):` põe um relógio de 1 segundo em tudo o que ocorrer dentro. Lá dentro há uma espera de 10 segundos. Ao se cumprir o segundo, o `asyncio` **cancela** o que estiver esperando dentro do bloco e, ao sair, lança `TimeoutError` (uma exceção normal do Python, desde a 3.11; antes se chamava `asyncio.TimeoutError`, que hoje é só outro nome para a mesma). O `except TimeoutError` a captura, e o programa imprime o tempo que de fato esperou: 1.0 segundo, não 10. Aprenda os dois efeitos do bloco: **corta** a espera (não ficam tarefas penduradas) e **avisa** com uma exceção que você decide como tratar.

Os dois mecanismos não se atrapalham; se complementam. No `revisor` de hoje convivem: `httpx.Timeout` põe o limite em cada fase, e `asyncio.timeout` o do serviço completo. Os dois usam o `timeout_ms` do serviço, e qualquer um dos dois que se cumprir primeiro produz o mesmo resultado: “tiempo agotado”. Mais adiante, em 10.4, você verá uma das vantagens de ter os dois: o teto do `asyncio` funciona mesmo quando o `httpx` não participa.

#### 10.2.2 `asyncio.Semaphore`: quantas ao mesmo tempo, no máximo

Um **semáforo** (*semaphore*) é um contador de permissões. Cria-se com um número, `asyncio.Semaphore(2)`: há duas permissões. Quem quer entrar faz `async with semaforo:`; se resta uma permissão, a toma e entra, e se não, **espera** até que outro a devolva ao sair. É a entrada de um estacionamento com duas vagas: quando está cheio, o carro seguinte espera na rua até que um saia. A [documentação](https://docs.python.org/pt-br/3/library/asyncio-sync.html#semaphore) o descreve nesses termos. Vejamos seis serviços de meio segundo com espaço para dois ao mesmo tempo:

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

Leia a saída em grupos de quatro linhas. Entram o 1 e o 2; saem os dois meio segundo depois; só então entram o 3 e o 4, e assim por diante. Seis serviços, dois ao mesmo tempo: três rodadas de meio segundo, 1.5 segundo no total. Todas as tarefas foram criadas de uma vez no `TaskGroup`, mas quatro delas ficaram esperando em `async with semaforo` sem gastar nada. Repare também na ordem: o 3 entra antes do 4, o 5 antes do 6. No CPython o semáforo costuma atender na ordem em que chegaram, mas a [documentação](https://docs.python.org/pt-br/3/library/asyncio-sync.html#asyncio.Semaphore) não promete isso (promete para o `Lock`), então o seu programa não deve depender dessa ordem. O `revisor` não depende: a ordem do seu relatório vem da lista de serviços, não da ordem em que terminaram.

Quanto vale o limite correto? Depende de **quem recebe** as consultas. Se são seus próprios serviços, o que eles aguentam; se são de um terceiro, o que a documentação dele permitir; se são muitos e você não sabe, um número moderado. O `revisor` usa **10** por padrão e deixa o usuário mudá-lo com `--concurrencia`. O semáforo também protege a sua própria máquina: cada conexão aberta gasta um descritor de arquivo, e cada sistema operacional tem um teto. E o `httpx` limita por conta própria o conjunto de conexões abertas (100 por padrão, como diz [a sua documentação de limites](https://www.python-httpx.org/advanced/resource-limits/)), de modo que um limite maior que esse só faria as consultas esperarem em outra fila.

#### 10.2.3 Levar isso ao `revisor`

Toda a mudança desta metade cabe em três arquivos e um arquivo de dados novo. Primeiro a versão do pacote, `0.9.0` (a dependência do `httpx` já estava desde a 9):

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

Depois o coração, `revision.py`. Leia-o em três movimentos:

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

**Primeiro, `revisar`** (uma única consulta). Mudou muito pouco em relação à Lição 9: o `await cliente.get(...)` agora vive dentro de `async with asyncio.timeout(servicio.timeout_ms / 1000):`. A divisão por mil é porque `timeout_ms` está em milissegundos e `asyncio.timeout` quer segundos. No `except`, `(httpx.TimeoutException, TimeoutError)` captura os dois tempos esgotados: o de fase do `httpx` e o teto do `asyncio`. Com parênteses, porque no Python 3.12 um `except` com duas classes as leva dentro de uma tupla. O resto é igual: cada erro de rede se converte em um `Resultado` com o seu detalhe, e a função **nunca** deixa sair um erro de rede. Há uma exceção que `revisar` **não** captura de propósito e que merece um parágrafo: `asyncio.CancelledError`. É a forma como o `asyncio` avisa uma tarefa “você foi cancelada”. Se você a capturasse, engoliria a ordem de cancelar e o `TaskGroup` ou o `timeout` ficariam sem poder fazer o seu trabalho. Por isso o `except` nomeia classes concretas e nunca é um `except Exception` amplo: a regra da Lição 6 (nada de `except:` puro) agora tem mais uma razão.

**Segundo, `_revisar_con_limite`**: três linhas que tomam uma permissão do semáforo e verificam. Está **fora** de `revisar` por uma razão de medição. Se o semáforo estivesse dentro, o relógio de `revisar` começaria a correr antes de obter a permissão, e um serviço que esperou a sua vez meio segundo apareceria como “lento” sem sê-lo. Com a permissão fora, o tempo que `revisar` mede é o da consulta, e a espera na fila do semáforo não conta. O mesmo vale para o teto do `asyncio.timeout`: começa a contar quando a consulta começa, não quando a tarefa foi criada.

**Terceiro, `revisar_todos`**. A sua assinatura mudou: agora recebe `limite` (por padrão 10) e `transporte`, que por enquanto você pode ignorar (existe para 10.4: é a porta por onde os testes colocam um servidor de mentira). Linha por linha: se `limite` é menor que 1 lança `ValueError`, porque `Semaphore(0)` não explode: deixa todo mundo esperando uma permissão que nunca chega, e o programa fica travado sem dizer nada. Cria-se o semáforo. Abre-se **um único** `httpx.AsyncClient` para todas as consultas, porque um cliente mantém um conjunto de conexões reutilizáveis e abrir vinte clientes seria desperdício. Abre-se o `TaskGroup`, e a compreensão cria uma tarefa por serviço, **na ordem da lista**. Ao sair do bloco, todas terminaram. A última linha, fora dos `async with`, monta a lista de resultados percorrendo as tarefas nessa mesma ordem: assim o relatório respeita a configuração não importa quem respondeu primeiro.

Falta que o usuário possa escolher o limite. No `cli.py`:

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

Há duas coisas novas. `entero_positivo` é uma função que o `argparse` usa para converter e validar o texto que o usuário escreveu depois de `--concurrencia`: se não é um inteiro, ou é menor que 1, lança `argparse.ArgumentTypeError`, e o `argparse` o converte no seu erro de uso com código de saída **2**, o mesmo código que você já usava para “o uso é inválido”. Dois detalhes de escrita nessa função. `{texto!r}` dentro da f-string pede a *representação* do valor em vez do texto tal qual: um texto sai com as suas aspas (`'diez'`), e assim a mensagem deixa ver exatamente o que o usuário escreveu, mesmo que tenham sido espaços. E `raise ... from None` é o `raise ... from` da Lição 6 com a intenção contrária: em vez de conservar o erro original como causa, ele o **oculta**, porque o `ValueError` do `int` não diz nada a quem escreveu `--concurrencia diez` e a mensagem nova já diz tudo. Por fim, em `main` a chamada passou a ser `revisar_todos(servicios, limite=argumentos.concurrencia)`.

Para medir com algo mais interessante que quatro serviços, há um arquivo com vinte, todos apontando para a rota `/espera/500` do laboratório (cada um responde após meio segundo):

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

Com o laboratório rodando em outro terminal (`python laboratorio.py`, como na Lição 9), meça três vezes a mesma execução. `time` é um comando do terminal que executa o que vem depois dele e, no final, diz quanto levou; a linha `real` é o tempo do relógio de parede. Com `| tail -n 1` só se conserva a última linha do relatório, o resumo, para não ver vinte linhas:

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

Os números contam a história. Com `--concurrencia 1` (uma permissão, ou seja, em fila) leva **10.3 segundos**: vinte esperas de meio segundo. Com 10 leva **1.15**: vinte serviços, dez ao mesmo tempo, são duas rodadas de meio segundo. Com 20 leva **0.63**: uma única rodada. Por que 10 dá o dobro de 20 e não algo intermediário? Porque com limite 10 os primeiros dez ocupam as permissões durante meio segundo, e os outros dez **não podem começar** até que alguma seja liberada: duas rodadas seguidas. Com limite 20 cabem todos de uma vez. E por que 0.63 e não 0.5? Porque o relógio do `time` inclui o que não é espera de rede: iniciar o Python, importar o `httpx`, abrir as conexões. São entre 0.1 e 0.15 segundo que não dependem de quantos serviços haja. Se a sua máquina é mais lenta, os seus serão um pouco maiores; a **proporção** entre as três execuções é o que importa.

Com isso termina a primeira sessão. O que você tem é um `revisor` que consulta vários serviços ao mesmo tempo e não abusa. O que lhe falta é resistir às falhas e, sobretudo, **demonstrar** que as resiste.

### 10.3 Grupos de exceções: uma falha não derruba o relatório

#### 10.3.1 O que acontece quando uma tarefa falha

Até agora tudo saiu bem. O `TaskGroup` tem uma regra para quando não sai bem, e convém vê-la com os próprios olhos antes de lê-la: se **uma** das tarefas termina com uma exceção, o grupo **cancela as demais**. Veja o que acontece com um relatório de três tarefas, uma das quais quebra:

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

Há três tarefas dentro do grupo. `catalogo` espera 0.05 segundo e termina bem. `reportes` espera 0.1 e lança `ConnectionError` (a exceção do Python para uma conexão que não pôde ser feita; é a prima do `httpx.ConnectError` que o `revisor` usa). `inventario` espera 0.5 segundo. Veja a saída: `catalogo` terminou, `inventario` foi **cancelada** (nunca chegou a dizer “terminó”; o meio segundo que lhe faltava se perdeu), e a exceção de `reportes` saiu pelo `except*`.

No código há duas formas novas. A primeira está em `consulta_buena`: o `except asyncio.CancelledError:` imprime “cancelada” e depois faz `raise` sozinho. Um `raise` sem mais nada **lança de novo a exceção que está sendo tratada**; é necessário porque, como você viu em 10.2.3, engolir um cancelamento estraga o mecanismo. A segunda é `except*`, que merece a sua própria seção.

#### 10.3.2 `ExceptionGroup` e `except*`

Quando várias tarefas de um grupo falham ao mesmo tempo, o Python não pode lançar uma única exceção: seriam várias ao mesmo tempo. Por isso, desde a 3.11, existe `ExceptionGroup` ([PEP 654](https://peps.python.org/pep-0654/)): uma exceção que **contém outras exceções**, no seu atributo `.exceptions`, que é uma tupla (a coleção que não muda, da Lição 4). Um `TaskGroup` que sofreu falhas as empacota em um ao sair do bloco, ainda que tenha falhado uma só.

Um `except` normal captura pela classe da exceção que chega; como o que chega é um `ExceptionGroup`, um `except ConnectionError` não a reconheceria. Para isso foi criado o `except*` (com asterisco), que **abre o grupo**: `except* ConnectionError as grupo_de_errores` captura as exceções do grupo que são `ConnectionError`, as junta em um grupo novo e o deixa na variável. Por isso o `for error in grupo_de_errores.exceptions:` percorre essa tupla, e não um único erro. Se no grupo havia exceções de outras classes que nenhum `except*` capturou, elas seguem o seu caminho para cima. Um mesmo `try` pode ter vários `except*`, cada um para a sua classe, e cada um recebe o que é seu. O que você **não** pode fazer é misturar `except` e `except*` no mesmo `try`. A [documentação da linguagem](https://docs.python.org/pt-br/3/reference/compound_stmts.html#except-star) tem todas as regras; para o `revisor` basta o que você vê.

Repare no que o programa ganhou e perdeu. Ganhou limpeza: nenhuma tarefa ficou órfã, o grupo esperou que as canceladas terminassem de se cancelar, e o erro chegou organizado. Perdeu o relatório: `inventario` estava saudável e o seu resultado foi jogado fora. Em um `revisor` isso é inaceitável, porque a sua razão de ser é dizer o estado de **todos**.

#### 10.3.3 Uma falha de rede é um resultado, não uma exceção

A solução do `revisor` você já tem escrita, e agora pode entender por que está como está. `revisar` **captura** os erros de rede dentro da própria tarefa e os converte em um `Resultado` (`CAIDO`, com o seu detalhe). Do ponto de vista do `TaskGroup`, a tarefa terminou bem: devolveu um valor. Ninguém lança nada para cima, ninguém cancela ninguém, e o relatório sai completo com a linha de `reportes` dizendo “sin conexión”. É o princípio da lição: **uma falha esperada é um dado, não um incidente**. Um serviço fora do ar não é uma surpresa para um `revisor`; é parte do seu trabalho.

E todos os erros se convertem em dados? Não, e a diferença é o mais valioso desta seção. `revisar` captura **classes concretas do `httpx`**: os erros que o mundo exterior pode causar. Não captura um `ZeroDivisionError`, um `KeyError` ou um `TypeError`: esses são erros **do programa**, e escondê-los como se fossem “um serviço fora do ar” seria mentir. Se um serviço aparece como fora do ar porque o seu código tem um erro, você passará uma tarde procurando o problema na rede. Com o design de hoje, um erro de programação faz o que deve: interrompe o relatório, ruidosamente, com um relatório de erro que aponta a linha. Essa saída ruidosa é o que você vê na seção “O erro que você vai ver” mais abaixo, e é uma boa notícia, não uma má.

### 10.4 Testes sem rede

#### 10.4.1 Por que não se testa contra a rede

Para comprovar o parágrafo anterior (“um serviço fora do ar não derruba o relatório”) fazem falta serviços fora do ar, lentos, que devolvam 503 e que se desconectem, e as quatro coisas **ao mesmo tempo**. Os testes contra a rede real têm três problemas. São **lentos**: um teste de tempo limite de 5 segundos faz esperar 5 segundos quem roda a suíte. São **frágeis**: falham porque o wifi caiu, não porque o seu código esteja errado, e um vermelho que não significa nada faz as pessoas deixarem de olhar os vermelhos. E são **impossíveis de repetir**: você não pode pedir a um serviço real que caia justo agora. Por isso a regra é que **um teste unitário nunca sai para a rede**. A rede é substituída por um dublê: algo com a mesma forma que o real, mas que responde o que o teste lhe disser.

O artigo do [blog da Hábil sobre testes que detectam erros](https://www.habil.mx/pt/blog/testes-que-detectam-erros-cobertura-quality-gate/) conta por que um teste que se pode pôr vermelho à vontade vale mais do que dez que estão sempre verdes; e o que trata de [estilos de integração online, fila e evento](https://www.habil.mx/pt/blog/estilos-de-integracao-online-fila-evento/) mostra o mesmo problema do lado da arquitetura: separar quem pergunta de quem responde. Aqui você os separa com uma peça do `httpx`.

#### 10.4.2 `httpx.MockTransport`: um servidor de mentira

Um cliente HTTP tem duas metades: a que monta a requisição e entende a resposta, e o **transporte**, que é a que realmente toca a rede. O `httpx` deixa você trocar o transporte, e traz um feito para testes, [`httpx.MockTransport`](https://www.python-httpx.org/advanced/transports/#mock-transports): recebe uma função que, dada a requisição, **devolve a resposta** que você quiser. Nada sai do seu computador.

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

`atender` é a função de mentira: recebe um `httpx.Request` (a requisição, com o seu endereço em `.url`), imprime o que chegou e devolve um `httpx.Response` com o código 200 e o texto “todo bien”. `httpx.MockTransport(atender)` a envolve como transporte, e `httpx.AsyncClient(transport=transporte)` monta um cliente que, em vez de abrir uma conexão, a chama. O cliente faz `get("https://catalogo.example/estado")`, um endereço que não existe (`.example` é um domínio reservado que nunca resolve), e mesmo assim responde, porque nunca foi procurá-lo. Isso é o que `revisar_todos` oferece com o seu parâmetro `transporte`: recebe o transporte e o passa a `httpx.AsyncClient(transport=transporte)`. Quando vale `None` (o normal), o `httpx` usa o verdadeiro.

Um transporte de mentira pode fazer mais do que responder 200: pode devolver um 503 (`httpx.Response(503)`), ou **lançar** uma exceção de rede como se o cabo tivesse sido cortado (`raise httpx.ConnectError(...)`), ou até esperar, se a função é `async def`. Com essas quatro coisas se simula tudo o que o `revisor` tem de tolerar.

#### 10.4.3 Os seis testes de `revisar`

Um arquivo novo, `tests/test_revision.py`. Antes do código, o plano: os testes falam de um servidor de mentira que se comporta segundo o **nome do anfitrião** (a parte do endereço entre `https://` e a primeira barra). `facturacion.example` responde 503; `reportes.example` lança `ConnectError`; `notificaciones.example` lança `ReadTimeout` (a exceção do `httpx` para “o tempo de leitura se cumpriu”); qualquer outro responde 200.

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

Cada teste é uma função normal (não `async`): monta o que precisa e chama `asyncio.run(...)`, igual ao que faz `main`. Assim não é necessário nenhum complemento do `pytest` para rodar corrotinas, e o curso fica com o que você já conhece. `revisar_uno` é um auxiliar que abre um cliente com o transporte de mentira e verifica um único serviço. Os quatro primeiros testes percorrem os quatro desfechos de `revisar`: 200 rápido é `ARRIBA`; 503 é `CAIDO` e o detalhe é o código, `"503"`; um `ConnectError` é `CAIDO` com “sin conexión”; um `ReadTimeout` é `CAIDO` com “tiempo agotado”. O quinto, `test_la_mezcla_sale_completa_y_en_orden`, é o que demonstra a promessa da lição: passa a `revisar_todos` quatro serviços, um de cada tipo, e comprova que **voltaram os quatro, na ordem da configuração, cada um com o seu detalhe**. Se uma falha derrubasse o relatório, este teste ficaria vermelho. E o sexto, `test_una_direccion_invalida_no_tumba_a_los_demas`, cuida do quarto `except` da Lição 9: junta um serviço com o endereço impossível `http://999.1.1.1:8099/pagos` e um saudável, e exige que o primeiro saia com “dirección inválida” e o segundo com o seu `200`. Sem esse `except`, o `httpx.InvalidURL` escaparia da sua tarefa, o `TaskGroup` cancelaria o resto e o teste falharia com um grupo de exceções (10.3).

(Uma coisa que `LENTO` não tem aqui: não há teste desse estado, porque simular que passou mais de um segundo com um transporte de mentira distrai. O limiar de lentidão já está testado onde vive, em `clasificar`, com os seus sete casos da Lição 8.)

#### 10.4.4 Vê-lo em vermelho antes de acreditar nele

Um teste que você nunca viu falhar não demonstra nada: talvez passasse igual com o código quebrado. Então se comprova. Em uma cópia do projeto, apaga-se o ramo `except httpx.ConnectError` de `revisar`, de modo que um `ConnectError` caia no ramo geral e diga “error de red”. Roda-se:

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

Ficaram em vermelho **exatamente dois** testes: o que fala da conexão, e o da mistura (que inclui esse caso). A linha que diz `2 failed, 25 passed` dá a você o relatório que importa: não é um verde por acaso. Conserte o código e rode de novo:

```text
$ pytest -q
...........................                                              [100%]
27 passed in 0.03s
```

`27 passed`: os 21 da lição anterior mais os seis de hoje. Esse número se lê do relatório, não do código de saída, porque um código 0 não diz quantos testes rodaram: sai igual com 27 e com 2 se por engano você filtrou o resto. (A Lição 11 volta a isso com um caso concreto.)

Há um limite que convém dizer de frente. O teste do tempo esgotado faz o servidor de mentira **lançar** um `ReadTimeout`, ou seja, testa o ramo de `httpx.TimeoutException`. Não testa o **teto** do `asyncio.timeout`, que existe justamente para o caso em que o `httpx` não fica sabendo de nada. Esse teste faz falta, e é o Exercício 2: você o escreve, e comprovará que se o `asyncio.timeout` for retirado, ele fica vermelho.

#### 10.4.5 `monkeypatch` e a assinatura que você não deve mudar sem avisar

O `test_cli.py` já existia, com dois testes, e tinha um detalhe que hoje salta à vista. Esses testes chamam `main`, e `main` chama `revisar_todos`, que sai para a rede. Para que não faça isso, o curso usou `monkeypatch` (Lição 8): troca, durante um teste, um nome por outro, e ao terminar o teste o restaura. Aqui troca `revisor.cli.revisar_todos` por uma função falsa que devolve o que o teste precisa.

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

Note **onde** o nome é trocado: `"revisor.cli.revisar_todos"`, não `"revisor.revision.revisar_todos"`. O `cli.py` fez `from revisor.revision import revisar_todos`, então o `cli` tem **a sua própria cópia do nome**; se você trocasse o original em `revision`, o `cli` continuaria usando o seu. A regra do `monkeypatch`: troca-se o nome no lugar onde **é usado**, não no lugar onde foi definido.

E agora o importante desta versão: as duas funções falsas, `todos_caidos` e `todos_arriba` (cada uma definida dentro do seu teste), **aceitam `limite`**. Hoje `main` chama `revisar_todos(servicios, limite=argumentos.concurrencia)`, e um falso que não aceite esse argumento não é um dublê da função real: é outra função, e o teste quebra. Se na Lição 9 o seu falso era `async def todos_caidos(servicios)`, agora você tem de acrescentar o parâmetro. Você o vê em “O erro que você vai ver”. É uma lição mais geral: **um dublê deve ter a mesma assinatura do que substitui**, e quando você muda a assinatura da função real, os testes com dublês são a primeira coisa que quebra. Isso não é um incômodo; é o teste fazendo o seu trabalho, avisando que há outros que dependiam dessa assinatura.

#### 10.4.6 O projeto completo

Os arquivos que não mudaram nesta lição estão aqui para que a pasta `fig10_08/` esteja completa e você possa rodá-la. São os mesmos que você trazia da Lição 9:

<details>
<summary>Os arquivos que não mudam nesta lição</summary>


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

Com o laboratório rodando, a foto do projeto produz o mesmo relatório de sempre, mas desta vez os quatro serviços são consultados ao mesmo tempo, então o total é o do mais lento (`inventario`, 2.3 segundos) e não a soma:

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

Os tempos da coluna TIEMPO variarão um pouco na sua máquina; o ESTADO e o DETALLE não, porque o laboratório é feito para que saiam sempre iguais. E o código de saída, como na Lição 7, é 1: há um `LENTO` e um `CAIDO`.

**Para comparar.** O mesmo problema —lançar, esperar por todas, limitar, não perder o relatório por uma falha— está resolvido no [curso de Go](https://www.habil.mx/pt/cursos/go/) com `sync.WaitGroup` e no [curso de TypeScript](https://www.habil.mx/pt/cursos/typescript/) com `Promise.all` e `Promise.allSettled`. A ideia é a mesma; o que muda é onde vive a espera. Em Go cada tarefa é uma *goroutine*, uma thread leve que o escalonador do próprio Go (não o sistema operacional) distribui entre as threads do processador; em TypeScript e em Python é uma tarefa cooperativa em uma única thread. Comparar as três soluções ensina mais do que ler uma só.

## O erro que você vai ver

### `ExceptionGroup: unhandled errors in a TaskGroup`

É o que vai aparecer para você na primeira vez que tiver um erro de programação dentro de uma tarefa. A figura 9 o provoca: uma função que tira a média de uma lista e recebe uma **vazia**, de modo que divide por zero.

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

Duas tarefas dentro do grupo: uma tira a média de dois números, a outra de uma lista vazia. Isto é o que o Python diz (caminhos reduzidos ao seu nome, como em todo o curso; na sua máquina vêm completos e as linhas de `asyncio/` podem diferir conforme a versão do Python):

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

A primeira coisa: este *traceback* **não se lê como os das lições anteriores**, da última linha para cima. A última linha de cima, `+------------------------------------`, é decoração; a causa real está **dentro da caixa** marcada com `|`, no fundo. Leia-o assim:

1. A primeira linha, `+ Exception Group Traceback`, avisa você: o que segue é um grupo.
2. As linhas com `|` descem pelo caminho que a execução percorreu: o seu `asyncio.run(main())`, os passos internos do `asyncio` e, importante, o seu `main` na linha 10, no `async with asyncio.TaskGroup()`. É ali que o grupo, ao sair, empacotou o erro.
3. `ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` é o rótulo do grupo: “erros sem tratamento em um TaskGroup, uma subexceção”. O número entre parênteses diz quantas ele contém.
4. E **dentro da caixa** (`+-+---------------- 1 ----------------`) está a subexceção número 1 com o seu próprio *traceback*: `promedio`, linha 6, `ZeroDivisionError: division by zero`. **Essa é a causa**, e a que você tem de consertar. A linha do seu arquivo está na linha em que diz `fig10_09.py", line 6, in promedio`.

Note também o que aconteceu com a **outra** tarefa (`promedio([142, 87])`): não houve nada a cancelar. Como não tem nenhum `await`, rodou inteira, sem ceder a vez, e terminou com o seu `114.5` antes de a segunda começar. Se estivesse esperando algo, como `inventario` em `fig10_06.py`, o `TaskGroup` a teria cancelado mesmo estando saudável: isso é o grupo fazendo o seu trabalho.

O que fazer: consertar a causa (comprovar que a lista não está vazia), não esconder o erro. Resista à tentação de colocar um `except*` amplo para calá-lo: um erro de programação deve ser visto.

### `TypeError: ... got an unexpected keyword argument 'limite'`

O segundo erro de hoje é o de 10.4.5. Se o seu falso de `test_cli.py` é da Lição 9 e não aceita `limite`:

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

Leia de baixo para cima, como sempre: `TypeError`, “`todos_caidos()` recebeu um argumento nomeado inesperado, `limite`”. (O `test_con_servicios_caidos_sale_con_1.<locals>.` que antecede o nome quer dizer que essa função está definida **dentro** do teste.) A linha de cima (`src/revisor/cli.py:64`) diz quem o mandou: `main`. E a de mais acima, que o teste chamou `main`. A solução não está no `cli.py`: está no falso, que deve aceitar o mesmo que a função real.

## O que se faz errado

**Esperar com `time.sleep` dentro de uma corrotina.** Bloqueia a thread e desfaz a concorrência inteira, sem dar erro (10.1.4). Custo: um programa que parece concorrente e leva o mesmo que em fila. Detecta-se com o modo de depuração do `asyncio` e com o `ruff`, desde que você adicione a coleção `ASYNC` ao seu `select` (a do `revisor` não a traz; 10.1.4).

**Criar tarefas com `asyncio.create_task` e esquecer de guardá-las.** O Python só guarda uma referência **fraca** às tarefas soltas, e uma tarefa que ninguém referencia pode ser recolhida pelo coletor de lixo no meio da execução. A [documentação](https://docs.python.org/pt-br/3/library/asyncio-task.html#asyncio.create_task) avisa. Com `TaskGroup` não acontece, porque o grupo as guarda. Custo: tarefas que desaparecem sem erro.

**Não limitar a concorrência.** `TaskGroup` sem semáforo com mil serviços abre mil conexões ao mesmo tempo. Custo: você bate no limite do sistema operacional, ou satura o serviço que verifica, e o relatório falha por razões que não são as que mede.

**Capturar `Exception` (ou `BaseException`) dentro da tarefa para “que nunca falhe”.** Engole os erros de programação e, com `BaseException`, até o cancelamento. Custo: um relatório que mente (“serviço fora do ar”) quando quem falhou é o seu código.

**Engolir `CancelledError`.** Um `except asyncio.CancelledError:` que não volta a lançar a exceção deixa o `TaskGroup` e o `asyncio.timeout` sem poder cancelar. Custo: programas que não terminam ou que não respeitam o tempo limite. Se você a captura para limpar algo, faça `raise` no final.

**Testar contra a rede real.** Lentos, frágeis, impossíveis de repetir (10.4.1). Custo: vermelhos em que ninguém acredita.

**Um falso com outra assinatura.** O dublê que não aceita o que a função real aceita é outra função. Custo: testes que quebram quando a assinatura muda, ou, pior, que continuam passando sem testar nada porque ninguém os chamou com os argumentos novos.

**Medir com uma única execução.** Um único número não diz nada: a inicialização do Python, o aquecimento das conexões e o que o seu computador estiver fazendo nesse segundo se misturam. Meça várias vezes e compare a **proporção**.

## Exercícios

### Exercício 1 — Meça um limite que você não testou

Com `servicios-20.toml` e o laboratório rodando, meça com `--concurrencia 5` e com `--concurrencia 4`. **Antes de rodar**, preveja os tempos com o raciocínio das rodadas (quantas rodadas de meio segundo são necessárias com esse limite). Anote previsão e medição no seu diário de bordo e explique a diferença, se houver.

### Exercício 2 — O teste do teto

Escreva um teste para o teto do `asyncio.timeout`: um serviço com `timeout_ms = 100` cujo servidor de mentira **espera dez segundos** antes de responder. O teste deve passar em uma fração de segundo. Dica: a função que atende pode ser `async def` e usar `await asyncio.sleep(10)`. Depois, **verifique-o em vermelho**: tire o `asyncio.timeout` de `revisar` (deixe um `if True:` no lugar), rode o teste e anote quanto leva para falhar e por quê.

### Exercício 3 — Um tempo limite mais curto que a resposta

Copie `servicios.toml` e adicione `timeout_ms = 1500` ao serviço `inventario` (que no laboratório responde após 2.3 segundos). Preveja a linha de `inventario`, o resumo e quanto a execução levará, e compare com o que sai. O que mudou no `ESTADO` de `inventario`, e por quê?

### Exercício 4 — Provoque três erros e leia-os

Provoque, um por um: (a) em `fig10_09.py`, troque a lista vazia por `[100]` e rode (o que desapareceu?); depois volte a colocá-la e passe o `ZeroDivisionError` da tarefa por um `except*` que o capture e imprima uma mensagem; (b) rode `python -m revisor --concurrencia 0` e anote o código com `echo $?`; (c) tire `limite` de um dos falsos de `test_cli.py` e rode `pytest`. Para cada um, escreva em uma frase o que significa a mensagem.

## Soluções

### Solução 1

Com limite 5 e vinte serviços são necessárias quatro rodadas de meio segundo: 2.0 segundos mais a inicialização. Com limite 4 são necessárias cinco rodadas: 2.5 mais a inicialização. Uma execução de referência deu 2.15 e 2.67 segundos: a inicialização (os 0.15 a 0.2 s que não são espera) explica a diferença para 2.0 e 2.5. A regra geral: o tempo ≈ (número de serviços dividido pelo limite, arredondado para cima) vezes a espera de cada um, mais a inicialização.

### Solução 2

O teste é adicionado a `tests/test_revision.py` (ou a um arquivo próprio):

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

O servidor de mentira é `async def` e espera dez segundos; o transporte de mentira não aplica nenhum tempo limite do `httpx` (não há rede), de modo que o único que pode cortar é o teto do `asyncio.timeout`. Com o código completo, o teste passa em uma fração de segundo:

```text
$ pytest -q tests/test_techo.py
.                                                                        [100%]
1 passed in 0.12s
```

E com o `asyncio.timeout` retirado (o `if True:`), o teste **falha**, e leva dez segundos para falhar, porque ninguém corta a espera; o relatório mostra que `revisar` entregou `LENTO` com `'200'` depois de esperar dez segundos:

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

Isso demonstra que o teste depende da correção que diz testar. Os seis testes de `test_revision.py` não teriam notado essa regressão.

### Solução 3

`inventario` passa de `LENTO` a `CAIDO` com detalhe “tiempo agotado”: a sua resposta levava 2.3 segundos e o teto é 1.5, então é cortada antes. O resumo conta agora `2 caídos`, e a execução leva uns 1.6 segundo (o teto de 1.5 mais a inicialização) em vez de 2.4. Uma execução real:

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

Duas observações. A média muda (126 ms nesta execução; varia um pouco a cada uma), porque `inventario` já não contribui com tempo: um serviço que não respondeu não entra na média. E a execução é mais curta porque o mais lento já não é `inventario`, e sim o seu teto.

### Solução 4

(a) Com `[100]` em vez de `[]` já não há divisão por zero, o programa termina sem saída e sem erro: as duas tarefas se completaram. Com o `except*`:

```python
try:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))
except* ZeroDivisionError:
    print("una lista de tiempos venía vacía")
```

captura o erro e o programa imprime a mensagem em vez do *traceback*. (b) Sai `revisor: error: argument --concurrencia: debe ser al menos 1` e o código é 2: é um erro de uso, e quem o detecta é o `argparse` antes de rodar qualquer coisa. (c) `TypeError: ... todos_caidos() got an unexpected keyword argument 'limite'`: o falso não aceita o que `main` lhe manda.

## Como sei que consegui

- [ ] `fig10_02.py` imprime “a la vez: 0.5 s” e `fig10_01.py` imprime “en serie: 1.1 s”, e você consegue dizer por que o primeiro é o do mais lento e o segundo a soma.
- [ ] `fig10_03.py` imprime as respostas na ordem em que as tarefas foram criadas, não na ordem de rapidez, e você sabe explicar o que `time.sleep` faz que `asyncio.sleep` não faz.
- [ ] `fig10_05.py` mostra as rodadas de duas em duas e o total de 1.5 s.
- [ ] Na pasta `fig10_08/`, `pytest -q` termina com `27 passed` e não com outro número, e o faz com o laboratório desligado (essa é a graça de testar sem rede).
- [ ] `ruff check`, `ruff format --check` e `mypy` não apontam nada nessa pasta.
- [ ] Com `servicios-20.toml`, `--concurrencia 1` leva perto de 10 segundos, `--concurrencia 10` perto de 1.1 e `--concurrencia 20` perto de 0.6, e você consegue explicar por que 10 dá o dobro de 20.
- [ ] `python -m revisor --concurrencia 0` termina com código 2 e uma mensagem de uso.
- [ ] Você quebrou de propósito o ramo `ConnectError` de `revisar` e viu ficarem vermelhos exatamente dois testes; consertou, e voltaram os 27.
- [ ] Você consegue explicar com suas palavras a diferença entre o tempo limite do `httpx` e o `asyncio.timeout`, por que `revisar` captura `httpx.HTTPError` e **não** `Exception`, e por que o falso de `test_cli.py` tem de aceitar `limite`.

## Resumo

Responda sem olhar a lição:

1. Que diferença há entre uma corrotina e uma tarefa? O que faz `create_task` e o que faz a saída de um bloco `async with asyncio.TaskGroup()`?
2. Em que momento exato o loop de eventos pode passar de uma tarefa para outra? O que acontece com um `time.sleep` dentro de uma corrotina?
3. Se quatro serviços respondem em 0.3, 0.5, 0.1 e 0.2 segundos, quanto leva a execução em fila e quanto com um `TaskGroup`? E com um `Semaphore(2)`?
4. O que mede `httpx.Timeout` e o que mede `asyncio.timeout()`? Qual dos dois corta um servidor que manda um byte a cada quatro segundos?
5. Por que o semáforo é tomado **fora** de `revisar` e não dentro?
6. Quando uma tarefa de um `TaskGroup` lança uma exceção, o que acontece com as demais? O que recebe o código que está fora do bloco?
7. O que `except*` faz que `except` não faz? Qual é a diferença entre `revisar` converter um `ConnectError` em um `Resultado` e capturar um `ZeroDivisionError`?
8. Onde se troca o nome com `monkeypatch` se o `cli.py` fez `from revisor.revision import revisar_todos`? Por que o falso tem de aceitar `limite`?

## Para ler mais

- [Documentação do `asyncio`: corrotinas e tarefas](https://docs.python.org/pt-br/3/library/asyncio-task.html) — `TaskGroup`, `create_task`, `timeout()` e `sleep()` com todas as suas regras, incluindo o cancelamento. É a fonte desta lição. Consultado em 7 de outubro de 2026.
- [PEP 654, “Exception Groups and except\*”](https://peps.python.org/pep-0654/) — por que existem os grupos de exceções, com os casos que os motivaram. Mais técnico, mas a seção de motivação se lê bem. Consultado em 7 de outubro de 2026.
- [Documentação do `httpx`: transportes (`MockTransport`)](https://www.python-httpx.org/advanced/transports/) e [tempos limite](https://www.python-httpx.org/advanced/timeouts/) — as duas peças do `httpx` que você usou hoje. Consultado em 7 de outubro de 2026.
- [Documentação do `pytest`: `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — todas as formas de trocar um nome durante um teste e quando usar cada uma. Consultado em 7 de outubro de 2026.
