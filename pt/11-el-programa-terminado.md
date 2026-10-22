# Lição 11 — O programa terminado

**Tempo:** 2 × 90 min (a primeira sessão vai até o final de 11.2; a segunda começa em 11.3)

**O que você constrói:** o `revisor` completo, versão 1.0.0, instalado no seu computador como mais um comando

**O que você aprende:** o relatório como contrato (tabela com largura calculada e JSON testado); `logging` e `--verbose`; os códigos de saída revisitados; uma revisão de segurança (o endereço que outra pessoa escreve, `subprocess` sem `shell=True`, `secrets`, nem `eval` nem `pickle`); construir o pacote e instalá-lo com `pipx`

**De onde você vem.** Você traz o `revisor` da [Lição 10](10-concurrencia-pruebas-sin-red.md): um pacote que lê a sua configuração, consulta os serviços ao mesmo tempo, com tempo limite e com um teto de simultâneas, e que tem 27 testes que não tocam na rede. Funciona, e funciona bem. Mas ainda vive na sua pasta: roda-se com `python -m revisor` de onde está o código, e a sua tabela tem um defeito que você não viu porque todos os seus serviços têm nomes curtos: a coluna `SERVICIO` mede sempre 12 caracteres, e um serviço chamado `notificaciones-de-clientes` a transborda. Hoje tudo isso é fechado. Você trabalha na sua pasta `~/curso-python/revisor/`, com o ambiente virtual ativado e, para a última parte, com o `pipx` instalado.

**O que esta lição não faz.** Quase não traz conceitos novos de Python: é a lição em que você **junta** o que já sabe e comprova que está terminado. O que é novo é de ofício: o `logging`, que é a linguagem com que um programa conta o que faz sem sujar o seu relatório; o empacotamento final; e a revisão dos quatro hábitos de segurança que o curso foi semeando. O passo final não é mais uma lição: é a lista de sete comprovações com que o `pt/README.md` define quando o curso terminou, e esta lição as percorre **uma por uma**, com a saída real de cada uma.

## Ao terminar, você vai conseguir

- Explicar por que um relatório que outro programa lê é um contrato, e testar esse contrato com um teste que fica vermelho se alguém renomear um campo.
- Calcular a largura de uma coluna a partir dos dados e alinhar uma tabela mesmo que um nome seja longo.
- Usar `logging` em vez de `print` para o que o programa conta de si mesmo, e explicar por que o relatório vai para a saída padrão e o registro para a saída de erro.
- Dizer, para cada código de saída (0, 1 e 2), o que o `revisor` promete a quem o chama de um script.
- Nomear e evitar quatro riscos de segurança frequentes: um endereço que outra pessoa escreve, `subprocess` com `shell=True`, `eval` e `pickle` com dados de fora, e números “aleatórios” para segredos.
- Construir o pacote como um arquivo instalável (`.whl`), instalá-lo com o `pipx` e executá-lo de qualquer pasta.
- Comprovar, com um comando e uma saída para cada um, que o `revisor` cumpre os sete pontos de “Como você sabe que terminou”.

## O porquê antes do como

Quando alguém diz “já terminei o programa”, há pelo menos três coisas que pode estar querendo dizer. Que **funciona no seu computador**, hoje, com os seus dados. Que **outra pessoa pode instalá-lo e usá-lo** sem pedir ajuda. Ou que **se pode confiar nele**: que se algo der errado ele diz com clareza, que se algo mudar um teste fica sabendo antes de um usuário, que não fica travado, que não abre portas que não devia. As três são diferentes, e é muito comum entregar a primeira achando que é a terceira.

O curso começou com você, sentado diante de um `print("revisor: todavía no revisa nada")`, e termina nesta lição porque o `revisor` já tem de poder se virar sozinho. Para decidir se conseguiu, não basta a impressão de que “já ficou”: a impressão é a primeira coisa que falha. Por isso o programa do curso define o final com **sete comprovações** que se podem executar, não com uma opinião. São estas, e você vai percorrê-las uma por uma no final da lição:

1. O `pytest` termina em verde e o relatório diz quantos testes rodaram.
2. `ruff check`, `ruff format --check` e `mypy` não apontam nada.
3. Verifica 20 serviços ao mesmo tempo em um tempo próximo ao do mais lento, não ao da soma.
4. Um serviço fora do ar, lento ou que responde lixo não derruba o relatório.
5. Nenhuma requisição pode esperar para sempre.
6. Roda igual no Python 3.14 e no 3.12 do seu Mint.
7. Instala-se com `pipx install` e `revisor --help` funciona de outra pasta; sai com 0 se tudo está no ar e com 1 se não.

Dessas sete, o seu `revisor` já cumpre quase todas e talvez você não saiba. O que falta são três coisas: **medi-lo** (ninguém confia em “acho que sim”), **deixá-lo em um estado que outra pessoa possa usar** (o relatório, o registro, o empacotamento) e **revisar os hábitos de segurança** para que o ponto 4, “não derruba o relatório”, não seja só coisa de falhas acidentais, mas também de entradas hostis. As quatro partes da lição seguem essa ordem.

## Os conceitos

### 11.1 O relatório como contrato

#### 11.1.1 Quem lê o seu relatório

Até agora o relatório era lido por você, em um terminal. Mas um programa de linha de comando que sai com código 0 ou 1 é feito para que **outro programa** o chame: um script do plantão que roda a cada cinco minutos, uma tarefa de integração contínua que decide se deixa passar uma implantação. Esse outro programa não *lê* o relatório como você: o **interpreta**. Procura um campo com um nome e espera um tipo. Se amanhã alguém renomear `caido` para `caidos` no JSON, para uma pessoa é uma mudança de ortografia; para o script é um campo que desapareceu, e sem um teste que o pegue ninguém fica sabendo até o alarme das três da manhã não tocar.

A isso se chama **contrato**: a forma como o programa promete entregar o seu resultado, e que outros podem dar por certa. O `revisor` tem dois contratos. O **JSON** (definido na Lição 6) é para as máquinas: seus campos e seus tipos são fixos, e o `tiempo_ms` de um serviço que não respondeu é `null`, não `0` nem um texto. E o **código de saída** (definido na Lição 7) é para o shell e para qualquer script: `0` se todos os serviços estão `ARRIBA`; `1` se algum está `LENTO` ou `CAIDO`; `2` se o uso é inválido ou a configuração não presta. A tabela, em contrapartida, é para pessoas, e pode mudar de aspecto sem avisar ninguém.

Hoje se torna explícito o que antes era implícito: escreve-se um **teste que descreve o JSON inteiro**. E conserta-se um defeito da tabela.

#### 11.1.2 A largura de uma coluna se calcula, não se adivinha

Veja o defeito antes de consertá-lo. A Lição 2 fixou a largura da primeira coluna em 12 caracteres com `f"{nombre:<12}"`, e com os nomes da amostra (o mais longo, `inventario`, tem 10) ficava perfeito. Com um nome longo, o texto sai da sua coluna e empurra todas as outras. A solução é fazer com que a largura **dependa dos dados**: o mais longo dos nomes mais dois espaços de respiro, com um mínimo de 12 para que as tabelas curtas fiquem como sempre.

Há uma novidade de sintaxe. Uma f-string deixa você pôr a largura **dentro** da especificação, com outro par de chaves: `f"{nombre:<{ancho}}"` significa “alinhe `nombre` à esquerda em um campo de `ancho` caracteres”, onde `ancho` é uma variável. É o mesmo que `:<12`, com o 12 substituído por uma variável. Veja como fica o `formato.py` completo:

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

Três funções novas ou mudadas. `ancho_servicio` calcula a largura: uma compreensão tira o comprimento de cada nome, `max(..., default=0)` devolve o maior (o `default=0` é o que `max` devolve se a lista está vazia; sem ele, `max([])` lança `ValueError`), e somam-se dois. `max(ANCHO_MINIMO, ...)` impõe o mínimo. `encabezado` e `linea` recebem um `ancho` com valor padrão `ANCHO_MINIMO`; assim, todo código que as chamava sem largura (os seus testes da Lição 8, por exemplo) continua funcionando sem mudanças. E `tabla` junta tudo: calcula a largura **uma vez**, monta o cabeçalho, uma linha por resultado, uma linha em branco e o resumo, e os une com quebras de linha. (`renglones += [...]` acrescenta ao final da lista todos os elementos da outra, como vários `append` seguidos; e `"\n".join(...)` é o `join` da Lição 4 com a quebra de linha como separador.) Com os quatro serviços canônicos, o nome mais longo mede 10, `10 + 2 = 12` e a largura calculada é 12: a tabela sai **idêntica** à que você tinha, byte a byte. Só muda quando é preciso que mude.

#### 11.1.3 O JSON como contrato, testado

A segunda mudança é um teste. Leia-o completo: não é curto, e o seu comprimento é o ponto.

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

`CANONICOS` são os quatro resultados canônicos, montados à mão no teste; **não vêm da rede nem do laboratório**. `test_el_json_es_un_contrato` escreve o JSON esperado inteiro, campo por campo, como um dicionário, e o compara com `json.loads(reporte_a_json(CANONICOS))`. Há duas decisões que importam. A primeira: o teste compara **o que significa** o JSON (o dicionário que sai de `json.loads`) e não o **texto** (os espaços e a ordem das linhas), porque a um script que interpreta JSON tanto faz quantos espaços haja e importa muito quais são os campos. A segunda: o teste inclui o caso incômodo, `reportes` com `"tiempo_ms": None` (que em JSON é `null`), e o `promedio_ms` de 843. Se alguém trocar o `0` pelo `null`, ou tirar um campo, ou mudar o arredondamento da média, o teste fica vermelho.

O segundo teste novo, `test_la_tabla_se_alinea_con_un_nombre_largo`, acrescenta aos quatro canônicos um serviço com um nome de 26 caracteres (`[*CANONICOS, largo]` monta uma lista nova com os elementos de `CANONICOS`, que o asterisco “desempacota” um por um, e `largo` no final, sem tocar em `CANONICOS`) e comprova duas coisas: que a palavra `ESTADO` do cabeçalho comece na coluna 28 (26 mais os 2 de respiro) e que em cada linha de dados, nessa mesma coluna, haja um estado válido. Para a primeira usa `.index(...)`, um método dos textos que procura onde começa um pedaço dentro do texto e devolve a sua posição, contando a partir de 0 como os índices das listas: `lineas[0].index("ESTADO")` é a coluna onde `ESTADO` começa no cabeçalho (se não o encontrasse, falharia com `ValueError`). Esse `renglon[ancho : ancho + 6]` é uma fatia: a sintaxe `[inicio:fin]` toma os caracteres desde a posição `inicio` até a anterior a `fin`, então aqui são os seis que começam na coluna do estado, que é o que mede `"ARRIBA"`. O `in {"ARRIBA", "LENTO ", "CAIDO "}` tem um espaço no final de `"LENTO "` e de `"CAIDO "` porque esses estados medem cinco caracteres e a fatia toma seis.

Em um teste como este vale a pena perguntar se ele cumpre a vara da Lição 8: fica vermelho se quebrar o que diz testar? O Exercício 2 pede que você quebre o JSON de propósito e comprove.

### 11.2 `logging`: o que o programa conta de si mesmo

#### 11.2.1 Por que não `print`

O relatório é **o que o programa produz**. Mas um programa também tem coisas a contar sobre **o seu próprio trabalho**: “li 4 serviços”, “o serviço `pagos` respondeu em 87 ms”. Isso é informação para quem está investigando algo estranho, não para quem lê o relatório. Se essas mensagens são impressas com `print` ao lado do relatório, ficam misturadas com ele: o script que lê o JSON encontra linhas de diagnóstico no meio e deixa de poder interpretá-lo.

O mundo do Unix resolveu isso há décadas com dois canais: a **saída padrão** (*stdout*) é para o resultado do programa, e a **saída de erro** (*stderr*) é para tudo o mais que o programa tenha a dizer sobre si mesmo. Você já os usa: o relatório vai pela primeira, o `error de configuración: ...` vai pela segunda (Lição 7). O módulo [`logging`](https://docs.python.org/pt-br/3/library/logging.html) da biblioteca padrão é a forma ordenada de escrever no segundo canal, com uma vantagem sobre o `print`: cada mensagem tem um **nível** de importância, e você decide a partir de que nível quer ouvi-las, sem tocar no código que as escreve.

#### 11.2.2 Os níveis e um primeiro programa

Os níveis, de menos a mais grave: `DEBUG` (detalhe fino, para quem depura), `INFO` (o programa avança), `WARNING` (algo estranho, mas segue), `ERROR` (algo falhou) e `CRITICAL`. Por padrão, o `logging` só mostra a partir de `WARNING`. Um **logger** (*registrador*) é o objeto com quem você fala, e se pede por nome: `logging.getLogger("demo")`. Esta figura mostra tudo junto:

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

Linha por linha. `logging.basicConfig(stream=sys.stderr, format=...)` faz a configuração mínima: que as mensagens vão para `sys.stderr` (a saída de erro) e com o formato `NIVEL nombre: mensaje`. `registro.debug(...)` escreve uma mensagem de nível `DEBUG`, e não aparece, porque o nível padrão é `WARNING`: essa mensagem está **guardada no código, mas desligada**, que é a graça. `registro.warning("aviso: %s tardó %s ms", "inventario", 2300)` sim aparece. Repare em como se escreve: a mensagem leva marcadores `%s` e os valores vão **à parte**, como argumentos. É o formato `%` das strings, o antigo (`"%s" % x`), que o curso não usa em nenhum outro lugar; aqui você não o aplica: o `logging` o aplica por dentro, juntando a mensagem e os valores, e [a sua documentação](https://docs.python.org/pt-br/3/howto/logging.html#logging-variable-data) pede assim. Os valores são passados separadamente para que o `logging` só monte o texto **se a mensagem vai ser emitida**; com um `f"..."` o texto seria montado sempre, mesmo com o nível desligado, e em um programa que registra milhares de linhas essa diferença conta. E `registro.setLevel(logging.DEBUG)` baixa o nível, com o que o último `debug` já aparece. O programa imprimiu o relatório com `print(..., flush=True)`; o `flush=True` só obriga o texto a sair no momento, para que a ordem da saída documentada seja a mesma que você vê no terminal.

Um aviso de design, que vem do [guia oficial](https://docs.python.org/pt-br/3/howto/logging.html): o código de uma **biblioteca** (ou de um módulo do pacote) nunca configura o `logging`; só pede o seu logger e escreve. Quem configura é o **programa principal**, que é quem sabe para onde as mensagens devem ir. Por isso, no `revisor`, o `basicConfig` vive em `cli.py` e não em `revision.py`.

#### 11.2.3 `--verbose` no `revisor`

O `revisor` registra, em nível `DEBUG`, o resultado de cada serviço, e uma opção `--verbose` o liga. O `revision.py` pede o logger `"revisor"` no começo, e a sua função `revisar` agora é um invólucro: chama `_consultar` (o corpo de sempre, que não mudou) e registra o resultado antes de devolvê-lo.

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

Repare na separação: `_consultar` faz a consulta; `revisar` a faz e a **conta**. Assim o registro está em um único lugar e não repetido em cada `return`. No `cli.py`, três mudanças: a opção `--verbose` (com `action="store_true"`, que significa “se aparece, vale `True`; se não, `False`”, sem esperar um valor), uma função `configurar_logging` e a chamada a `tabla`:

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

`configurar_logging` faz três coisas. O `basicConfig` conecta o registro a `sys.stderr`. A linha `nivel = logging.DEBUG if verbose else logging.WARNING` é uma **expressão condicional**, um `if`/`else` que cabe em uma linha e que **dá um valor**: lê-se “`logging.DEBUG` se `verbose` é verdadeiro; se não, `logging.WARNING`”, e equivale a um `if`/`else` de quatro linhas que atribua `nivel` em cada ramo. E `logging.getLogger("revisor").setLevel(nivel)` põe o nível **apenas no logger do `revisor`**: `DEBUG` se pediram `--verbose`, `WARNING` se não. Essa distinção importa: se você tivesse posto o nível `DEBUG` no logger de **todos** (a raiz), o `httpx` e a biblioteca que ele usa por baixo escreveriam centenas de linhas próprias, e entre elas se perderia o que é seu. Além disso, cada opção traz agora o seu texto de ajuda em espanhol (`help=...`), porque a sétima comprovação pede que `revisor --help` sirva. (Os textos que o `argparse` põe por conta própria, como `options:` e `show this help message and exit`, saem em inglês; são da biblioteca.)

Veja a diferença com o laboratório rodando (de novo, os tempos variam na sua máquina):

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

Sem `--verbose`, o relatório sai igual a sempre e a saída de erro não diz nada. Com `--verbose` o registro aparece **no outro canal**. Para vê-los separadamente, redirecione-os para arquivos diferentes (é o Exercício 3): o relatório limpo em um e o registro em outro.

Um último comentário, de ofício. A ordem das linhas de registro é a ordem em que os serviços *terminam*, não a da configuração: `reportes` (que falha de imediato) sai primeiro. É outra razão para que o **relatório** não dependa do registro: o relatório é montado ordenado, a partir da lista; o registro é um diário do que foi acontecendo. O [artigo do blog sobre telemetria](https://www.habil.mx/pt/blog/telemetria-prometheus-loki-tempo-grafana-opentelemetry/) conta como se juntam, em um sistema de verdade, os registros de muitos programas como este.

> **Aqui termina a primeira sessão.** Você tem o relatório final (a tabela que calcula a sua largura e o JSON testado como contrato) e o registro com `--verbose`, cada um no seu canal. Antes da segunda sessão, rode os testes e o `revisor` com e sem `--verbose`, redirecionando cada canal para o seu arquivo. A segunda sessão não adiciona código ao `revisor`: revisa a segurança, o constrói e instala com o `pipx`, e comprova um por um os sete pontos de “Como você sabe que terminou”.

### 11.3 Revisão de segurança: quatro hábitos

O curso foi semeando a segurança onde estava o risco, não em um capítulo à parte: validar o que chega de fora (Lição 6), tratar o endereço do `urllib` com cuidado (Lição 9). Esta parte reúne os quatro hábitos para que você os tenha juntos. **Não adiciona código ao `revisor`**: o `revisor` já aplica o primeiro e não tem nenhum dos outros três. Eles são explicados porque você vai precisar deles assim que escrever o próximo programa, e porque o primeiro ganha um sentido novo agora que o programa é uma ferramenta que qualquer pessoa pode instalar.

#### 11.3.1 O endereço que outra pessoa escreve

O seu `revisor` faz uma requisição ao endereço que está em `servicios.toml`. Quem escreve esse arquivo decide **para onde vai o seu programa**. Se é só você, não há risco. Mas um programa é reutilizado, e amanhã esse arquivo pode vir de outra equipe, de uma página web ou de um formulário. A Lição 6 pôs uma defesa: `validar_servicio` só aceita endereços `http://` ou `https://` que passam pelas comprovações de `es_url_http` (esquema, servidor, porta e texto comum). Não é uma validação completa, e por isso a Lição 9 pôs uma segunda rede: se o `httpx` rejeita um endereço que passou, esse serviço sai como “dirección inválida” e os demais são verificados igual. Veja o que a primeira defesa faz com um endereço que não passa:

```text
$ python -m revisor --config raro.toml
error de configuración: servicio 1: 'url' debe ser una dirección http:// o https:// válida
$ echo $?
2
```

Um arquivo com `url = "file:///etc/passwd"` é rejeitado antes de fazer qualquer coisa: sai a mensagem de configuração e o código `2`. Sem essa validação, conforme a ferramenta que fizesse a requisição, `file://` poderia ler arquivos da sua própria máquina. E há uma variante mais sutil que a validação do esquema não cobre: um endereço `http://` que aponta **para dentro** da sua rede (para um serviço interno ou para o serviço de metadados de um servidor na nuvem) faz com que o *seu* programa, que está dentro, consulte algo que o autor do endereço não poderia alcançar de fora. Esse ataque se chama *server-side request forgery* (SSRF) e [a OWASP o descreve em detalhe](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). Para o `revisor`, que lê um arquivo de configuração que você escreve, é um risco baixo; para um serviço web que recebe endereços de usuários, é um risco central. A regra: **um endereço que vem de fora é um dado não confiável, e se valida (e se limita a um conjunto permitido) antes de ser usado**. O artigo do blog da Hábil sobre [segurança de APIs](https://www.habil.mx/pt/blog/seguranca-de-apis-cto-identidade-gateway-tokens/) leva essa regra ao nível da arquitetura.

#### 11.3.2 `subprocess`: uma lista, nunca um texto montado

Algum dia o seu programa vai querer executar outro programa do sistema (`ping`, `git`, `ls`). O módulo [`subprocess`](https://docs.python.org/pt-br/3/library/subprocess.html) faz isso, e tem duas formas de receber o comando, com consequências muito diferentes. Esta figura usa `echo` (que só imprime) para que você possa ver a diferença sem risco:

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

Nos dois casos, o “nome” é `catalogo; echo INYECTADO`: um texto em que alguém escreveu, depois do nome, um ponto e vírgula e **outro comando**. Com `shell=True`, o Python não executa o programa diretamente, e sim o entrega ao *shell* (o interpretador do terminal) como um texto para que o interprete, e o shell entende `;` como “termine este comando e execute outro”. O resultado: executaram-se **duas** coisas, e a segunda foi escolhida por quem escreveu o nome. Isso é uma *injeção de comandos*. Com uma **lista** (`["echo", "revisando", nombre]`) cada elemento é um argumento, o shell não intervém, e o `;` é apenas mais um caractere do texto. Se o comando tivesse sido `rm` em vez de `echo`, a diferença teria sido apagar os seus arquivos. A documentação do [`subprocess` na sua seção de segurança](https://docs.python.org/pt-br/3/library/subprocess.html#security-considerations) pede justamente isto; [a OWASP o explica com mais exemplos](https://owasp.org/www-community/attacks/Command_Injection). A regra: **lista de argumentos e sem `shell=True`; se o shell for necessário, o texto que chega a ele não pode conter nada que venha de fora**. O `check=True` faz com que um comando que falha lance uma exceção em vez de passar em silêncio.

#### 11.3.3 `eval` e `pickle`: executar o que chega de fora

`eval(texto)` pega um texto e o **executa como código Python**. Parece cômodo para converter “2 + 2” em 4, mas é preciso ver o que ele aceita:

```python
# fig11_03.py
texto_de_afuera = "__import__('sys').version_info.major"

print(eval(texto_de_afuera))
```

```text
$ python fig11_03.py
3
```

O “texto de fora” é uma instrução que importa um módulo e lê a sua versão do Python: nada nocivo, mas idêntico em forma ao que faria uma instrução que apague arquivos ou mande os seus dados para outro lugar. O `eval` não distingue. Qualquer dado que chegue de fora e passe por `eval` dá a quem o escreveu o controle do seu programa. Para converter texto em dados existem ferramentas que **só** entendem dados: `json.loads` (que você usa desde a 6) para JSON, `tomllib.loads` para TOML. Nem mesmo `ast.literal_eval`, a “versão segura” do `eval`, é uma defesa completa contra um texto hostil, como avisa [a sua documentação](https://docs.python.org/pt-br/3/library/ast.html#ast.literal_eval).

O `pickle` é o caso irmão. É o módulo que guarda objetos do Python em arquivo, e a sua [documentação](https://docs.python.org/pt-br/3/library/pickle.html) abre com um aviso em vermelho: *não é seguro*, porque desfazer um `pickle` pode executar código arbitrário. Um arquivo `pickle` que outra pessoa lhe manda é, na prática, um programa. Para dados que cruzam fronteiras, JSON. Não há figura de `pickle` no curso porque mostrá-lo exige escrever uma classe com métodos, e essa peça você não viu; com o aviso basta.

#### 11.3.4 `secrets`, não `random`

O módulo `random` produz números que *parecem* aleatórios mas que são calculados com uma fórmula a partir de uma **semente**: se você conhece a semente, conhece todos os números. Isso é uma virtude para uma simulação que você quer repetir, e um desastre para uma senha ou um token. Veja as duas coisas juntas:

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

Com a mesma semente (`random.seed(1)`), `random.random()` dá **exatamente o mesmo número** duas vezes: é `True`. Um atacante que adivinhe a semente (por exemplo, a hora em que o programa iniciou) reproduz todos os seus “segredos”. O [`secrets`](https://docs.python.org/pt-br/3/library/secrets.html) é feito para o contrário: toma o seu acaso do sistema operacional, o mesmo que ele usa para as chaves de criptografia. `secrets.token_hex(16)` dá 16 bytes aleatórios escritos em hexadecimal, ou seja, um texto de 32 caracteres (daí o `32`). A [documentação do `random`](https://docs.python.org/pt-br/3/library/random.html) diz isso no seu primeiro aviso: não usar para fins de segurança. A regra: **se o número é um segredo (token, senha, identificador que não devem poder adivinhar), `secrets`; se não, `random` está bem**.

### 11.4 Construir e instalar

#### 11.4.1 O que é um pacote instalável

Até agora o `revisor` é executado com `python -m revisor` a partir da pasta do projeto, e ficou instalado no seu ambiente com `pip install -e .` (a instalação **editável** da Lição 7, que não copia o código, e sim aponta para ele). Isso serve para desenvolver. Para entregá-lo a outra pessoa é preciso um **arquivo** que contenha o programa já empacotado. Em Python esse arquivo se chama [*wheel*](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), tem extensão `.whl` e é, por dentro, um arquivo comprimido com o seu código e os seus dados de instalação (nome, versão, dependências, e qual é o comando que deve ser criado). O nome conta uma história: `revisor-1.0.0-py3-none-any.whl` quer dizer “o pacote `revisor`, versão 1.0.0, para qualquer versão do Python 3, sem código compilado, em qualquer sistema”.

A versão sobe para `1.0.0` no `pyproject.toml`; é a única coisa que muda ali:

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

Constrói-se com o instalador de pacotes. Um detalhe: você não precisa do pacote `build` nem de nada novo; o `pip` já sabe construir uma *wheel* (o comando é [`pip wheel`](https://pip.pypa.io/en/stable/cli/pip_wheel/)). A opção `--no-deps` diz a ele que construa **somente o seu pacote** e não baixe as dependências, e `-w dist` que deixe o resultado na pasta `dist/`. O ponto final é “construa o projeto desta pasta”. Para montá-lo, o `pip` baixa por um momento a ferramenta de construção que você declarou em `[build-system]` (`hatchling`): é uma dependência de *construção*, não de execução, e não viaja dentro da *wheel*.

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

(A saída do `pip wheel` está reduzida: os `...` marcam linhas que foram retiradas, entre elas o download do `hatchling` e uma impressão digital `sha256` longa. O tamanho, `size`, depende do seu código, então o seu pode ser outro; o que importa é `Successfully built revisor`.)

Duas coisas a ler daqui. A *wheel* contém o pacote `revisor` (sete arquivos) e a sua pasta `dist-info` com os metadados; **não contém** `servicios.toml`, nem os testes, nem os arquivos de laboratório. É o correto: o programa não traz a sua configuração, quem o usa é que a traz. E a versão do nome do arquivo, `1.0.0`, saiu do `pyproject.toml`.

#### 11.4.2 `pipx`: instalar uma ferramenta, não uma biblioteca

Você poderia instalar a *wheel* com `pip install` dentro de um ambiente virtual, mas então o `revisor` só existiria enquanto esse ambiente estivesse ativado. Para uma **ferramenta** que você quer usar de qualquer pasta, como `git` ou `ruff`, a solução é o [`pipx`](https://pipx.pypa.io/stable/). O `pipx` cria um ambiente virtual **próprio para cada ferramenta**, instala ali o pacote com as suas dependências, e deixa o comando disponível no seu `PATH`. Cada ferramenta fica isolada das demais e do seu Python do sistema (que, lembre-se da Lição 1, não se deve tocar com `pip`).

No Linux Mint instala-se com o gerenciador de pacotes do sistema: `sudo apt install pipx` (o pacote está nos repositórios do Ubuntu 24.04, a base do Mint 22: [versão 1.4.3](https://packages.ubuntu.com/noble/pipx)), e depois `pipx ensurepath`, que adiciona a pasta dos comandos do `pipx` (`~/.local/bin`) ao seu `PATH`; abra um terminal novo para que ele perceba. Com isso, instalar o `revisor` é uma linha. A saída abaixo foi obtida com uma versão do `pipx` e do Python mais novas que as do seu Mint, então o texto pode diferir em detalhes: o que importa são as três últimas linhas. Foram retiradas as linhas de preparação do ambiente.

```text
$ pipx install dist/revisor-1.0.0-py3-none-any.whl
done!
  installed package revisor 1.0.0, installed using Python 3.14.8
  These apps are now available
    - revisor
```

O `pipx` criou o ambiente, instalou a *wheel* com as suas dependências (`httpx` e as dele) e deixou o comando `revisor`. Testá-lo a partir de **outra pasta** é o ponto. Esta execução é de uma pasta vazia:

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

Três coisas. `revisor --version` funciona de qualquer pasta e diz `revisor 1.0.0`; lembre-se de que esse número não está escrito no código, e sim que o `cli.py` o lê dos metadados do pacote instalado, que saem do `pyproject.toml`. Segunda: `revisor` sozinho, de uma pasta que não tem `servicios.toml`, termina com a mensagem de configuração e o código `2`. É a mesma lição da 6 (o caminho relativo depende de onde você está), e não é um defeito: é o correto para uma ferramenta, que não deve adivinhar onde está a sua configuração. Para isso existe `--config`. E terceira: com um `--config` válido, o relatório sai e o código é `1`, porque há um serviço `LENTO` e outro `CAIDO`.

#### 11.4.3 O que vem por aí, e ainda não é para você

Duas novidades do Python 3.14 ficam fora do curso de propósito, e convém que você saiba que existem. A primeira é o **interpretador sem GIL** (*free-threaded*): uma variante do Python que pode executar código Python em várias threads ao mesmo tempo; com a 3.14 passou a ser [oficialmente suportada](https://peps.python.org/pep-0779/), mas continua sendo uma compilação à parte e opcional, e muitas bibliotecas ainda não estão prontas. Para o `revisor` não muda nada, porque ele já faz esperas concorrentes em uma única thread e não é limitado pelo GIL. A segunda são as ***t-strings*** (strings de template, [PEP 750](https://peps.python.org/pep-0750/)): escrevem-se como uma f-string, mas com um `t` na frente, e em vez de um texto devolvem um objeto que separa o fixo do interpolado, útil para escapar HTML ou montar consultas SQL com segurança. Nenhuma das duas é necessária para o que você fez, nenhuma é usada no curso (e o código do curso tem de rodar no 3.12 do seu Mint, que não as tem), e as duas são explicadas na [lista de novidades do 3.14](https://docs.python.org/pt-br/3/whatsnew/3.14.html). Quando você precisar delas, já saberá ler essa documentação por conta própria, que é o que o curso se propôs.

## Os sete pontos, um por um

Aqui se fecha o curso. Cada ponto é um comando e uma saída; a saída abaixo é a real, da pasta `fig11_05/` com o laboratório rodando em outro terminal.

### Ponto 1 — o `pytest` termina em verde e diz quantos testes rodaram

Roda-se `pytest -q` e lê-se **a contagem do relatório**, a última linha. Nesta pasta deve dizer `30 passed`: os 27 da Lição 10 mais os três de hoje (o contrato do JSON, a tabela com um nome longo e `--version`).

Por que a contagem e não o código de saída: o código 0 do `pytest` só diz que *não houve falhas*, e é possível ter 0 falhas com quase nenhum teste rodando. Veja dois casos, medidos. Um: um arquivo com um único teste marcado para ser pulado.

```text
$ pytest -q tests/test_saltada.py
s                                                                        [100%]
1 skipped in 0.00s
$ echo $?
0
```

Código 0, e `1 skipped`: nada foi testado, e tudo parece bem. Dois: filtrar por nome.

```text
$ pytest -q -k sale_con
..                                                                       [100%]
2 passed, 28 deselected in 0.02s
$ echo $?
0
```

Também com código 0, mas `2 passed, 28 deselected`: de 30 testes rodaram dois. Quem só olha a cor verde ou o código não percebe; quem lê a contagem, sim. A [referência de códigos de saída do `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) os enumera (há um específico, o 5, para “nenhum teste foi coletado”, mas nem mesmo esse protege de um filtro que deixa passar dois). **Regra: o ponto 1 se cumpre quando você lê `30 passed` e esse 30 é o número que você esperava.**

### Pontos 2 e 6 — a qualidade, e que rode igual no 3.14 e no 3.12

Rodam-se as quatro ferramentas de qualidade, com cada versão do Python. Primeiro com o 3.14:

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

E exatamente o mesmo com o 3.12, a linha do seu Mint. A execução abaixo foi feita com Python 3.12.12; o do Mint 22 é o 3.12.3 (você viu isso na lição 1), então na sua tela a primeira linha dirá `Python 3.12.3`:

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

A única diferença é a linha de `python --version`. `ruff check` e `ruff format --check` não apontam nada (verificam 13 arquivos, o laboratório incluído) e `mypy` diz `Success`. Os 30 testes passam nas duas. Para repetir isto no seu Mint: o Python do sistema (3.12) você já tem no seu ambiente de sempre. Se você instalou o 3.14 com o `uv` (o quadro da Lição 7), crie um segundo ambiente com ele (`python3.14 -m venv .venv314`), ative-o e instale o projeto e as ferramentas com as versões de `herramientas/requisitos.txt`, e rode os mesmos quatro comandos. Se você não instalou o 3.14, o ponto 6 se cumpre *para a versão que você tem*, e a outra metade você comprova quando quiser: instala o 3.14 com o `uv` e repete estes quatro comandos. Ninguém a comprova por você; a saída acima é a de uma execução nas duas versões, e o que vale é a sua.

### Ponto 3 — 20 serviços ao mesmo tempo, no tempo do mais lento

Com os vinte serviços de meio segundo (`servicios-20.toml`), em fila e com todos ao mesmo tempo:

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

Em fila (`--concurrencia 1`): 10.2 segundos, a soma. Com `--concurrencia 20`: 0.61, perto do mais lento (0.5) mais a inicialização do Python. **O ponto 3 se cumpre** porque o tempo não é a soma das esperas: é da ordem da espera mais longa. Se a sua máquina marcar uns centésimos a mais, não importa; o que importa é que seja umas dezesseis vezes menos.

### Ponto 4 — um serviço fora do ar, lento ou que responde lixo não derruba o relatório

Com o laboratório você já viu isso em cada execução: `reportes` está fora do ar, `inventario` é lento, e os outros dois saem completos. Falta o terceiro tipo, o que **responde lixo**: algo que responde, mas não com HTTP válido. Isso não se pode pedir ao laboratório, mas sim a um transporte de mentira (Lição 10), que pode lançar a exceção que o `httpx` lança diante de uma resposta que não é HTTP (`httpx.RemoteProtocolError`). Esta figura junta cinco tipos de serviço em uma única execução: um saudável, um lento, um que responde lixo, um que devolve 503 e um travado de verdade (espera 30 segundos com um tempo limite de meio segundo).

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

Este programa **importa o pacote** `revisor`: roda com o ambiente onde você instalou o projeto (`pip install -e .` na pasta `fig11_05/`). Os seis serviços saem no relatório, na sua ordem, cada um com o que é seu: `lento` é `LENTO` (1.1 s), `basura` aparece como `CAIDO` com detalhe `error de red`, `caido` traz o seu `503`, e `colgado` desistiu com `tiempo agotado` sem esperar os 30 segundos. Nenhum derrubou os demais. E não é só coisa da simulação: se um servidor de verdade responde algo que não é HTTP (por exemplo, um programa que escuta em uma porta e responde um texto qualquer), o `httpx` lança um erro de protocolo, que é um `httpx.HTTPError`, e o `revisor` o reporta igual, como `error de red`. Os `0ms` de `catalogo` e `pagos` são porque o transporte de mentira responde na hora; com rede real seriam dezenas ou centenas. **O ponto 4 se cumpre.**

### Ponto 5 — nenhuma requisição espera para sempre

Duas comprovações. A primeira, no código: quantos lugares fazem uma requisição, e estão todos protegidos?

```text
$ grep -rn "cliente.get" src/revisor
src/revisor/revision.py:19:            respuesta = await cliente.get(servicio.url, timeout=limite)
```

Uma única requisição em todo o pacote, e está dentro de `async with asyncio.timeout(...)` e com `httpx.Timeout(...)` (você viu isso em `revision.py`). A segunda, com a execução: um serviço do laboratório que leva 10 segundos com `timeout_ms = 1000`, e outro que leva 8 segundos **sem** `timeout_ms` na configuração (usa o valor padrão, 5000):

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

O primeiro desiste aos 1.1 segundos; o segundo, aos 5.1. Nenhum esperou o que o servidor queria. **O ponto 5 se cumpre**, também para quem esquece de pôr o tempo limite na sua configuração, porque o valor padrão de `Servicio` é 5000 ms.

### Ponto 7 — instala-se com o `pipx` e usa-se de outra pasta

Você já fez isso em 11.4: `pipx install`, `revisor --version` e `revisor --help` de uma pasta qualquer. Falta comprovar o contrato dos códigos de saída: **0 se tudo está no ar, 1 se não**. Com os quatro serviços do laboratório você já viu o 1. Com um arquivo que só tem `pagos`:

```text
$ revisor --config bien.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA     102ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 102ms
$ echo $?
0
```

Código 0. E `revisor --help` funciona de qualquer pasta e mostra a ajuda das opções com o texto em espanhol que você pôs nelas em 11.2.3. **O ponto 7 se cumpre.**

Com os sete cumpridos, o `revisor` está terminado no sentido que o curso definiu no começo. Não porque seja perfeito, mas porque o que diz que faz, **ele faz e você pode comprovar**.

## O projeto completo

Os arquivos da pasta `fig11_05/` que não mudaram nesta lição estão aqui para que a pasta esteja completa e possa ser executada:

<details>
<summary>Os arquivos que não mudam nesta lição</summary>


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

E `tests/test_cli.py`, que mudou: ganhou o teste de `--version`.

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

O teste novo usa `capsys`, uma ferramenta do `pytest` irmã de `tmp_path` e `monkeypatch`: recolhe o que o programa **imprime** durante o teste, para poder comprová-lo. A sua anotação, `pytest.CaptureFixture[str]`, lê-se como as de coleções da Lição 4: `CaptureFixture` é o tipo dessa ferramenta, e `[str]` diz que o que ela recolhe é texto, assim como `list[str]` diz que a lista guarda textos. `main(["--version"])` imprime `revisor 1.0.0` e encerra o programa com `SystemExit` (é assim que o `argparse` funciona com `--version`), de modo que o teste o recebe com `pytest.raises(SystemExit)` (que comprova que o bloco lance essa exceção, e com `as salida` deixa você olhá-la) e depois lê o impresso com `capsys.readouterr().out`. Há uma armadilha neste teste que convém conhecer: o número `1.0.0` não sai do código, e sim dos **metadados do pacote instalado**, então depende de quando você instalou.

## O erro que você vai ver

### `AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'`

Você subiu a versão no `pyproject.toml` para `1.0.0`, rodou os testes e o de `--version` ficou vermelho dizendo que a versão é a velha:

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

Leia de baixo para cima: o teste esperava `revisor 1.0.0` e o programa disse `revisor 0.9.0`. Mas você **já mudou** o `pyproject.toml`. De onde sai, então, o `0.9.0`? Dos metadados da instalação editável que você fez antes: eles são gerados ao instalar, não ao mudar o arquivo. O `pyproject.toml` é a receita; a instalação é o prato já servido. A solução é instalar de novo:

```text
$ pip install -e .
$ pytest -q tests/test_cli.py
...                                                                      [100%]
3 passed in 0.02s
```

A regra: **quando você muda algo que o instalador lê (o nome, a versão, os comandos), instale de novo**. Isso não é um defeito do `pip`, é uma consequência de a versão viver em um único lugar (`pyproject.toml`), como se decidiu na Lição 7 para não repetir o número em dois arquivos.

### `bash: revisor: command not found`

Você instalou com o `pipx`, abre um terminal e escreve `revisor`:

```text
bash: revisor: command not found
```

O comando não é encontrado porque a pasta onde o `pipx` deixa os comandos (`~/.local/bin`) não está no seu `PATH`, que é a lista de pastas onde o terminal procura os programas. Resolve-se com `pipx ensurepath` e **abrindo um terminal novo**: a mudança só se aplica aos terminais que se abrem depois. (O texto exato do erro muda de um terminal para outro; o Linux Mint pode sugerir que você instale um pacote com esse nome, e não é o que você quer.)

### `error de configuración: no existe el archivo servicios.toml`

É o da Lição 6, e reaparece ao rodar `revisor` de uma pasta sem configuração (você viu em 11.4.2). Não há nada a consertar no código: passe `--config` com o caminho, ou rode o comando da pasta onde está o seu `servicios.toml`.

## O que se faz errado

**Deixar que a versão viva em dois lugares.** O número no `pyproject.toml` e outro escrito à mão em `cli.py` acabam divergindo. O `revisor` o lê do pacote instalado. Custo: um `--version` que mente.

**Misturar o registro com o relatório.** Imprimir diagnósticos com `print` entre as linhas do relatório. Custo: o script que lê o JSON recebe lixo e deixa de funcionar. O relatório vai pela saída padrão; o resto, por `logging` para a saída de erro.

**Configurar o `logging` dentro de um módulo do pacote.** Se `revision.py` chamasse `basicConfig`, importar o módulo mudaria o comportamento do programa que o importa. Custo: duas configurações brigando. Configura-se em um único lugar, no ponto de entrada.

**Pôr `DEBUG` no logger de todos.** Enche-se de linhas do `httpx` e o que é seu se perde. Sobe-se o nível só no logger próprio.

**Usar um `f"..."` em uma mensagem do `logging`.** Monta o texto mesmo com o nível desligado. Custo: trabalho desperdiçado em cada mensagem, que se nota quando são milhares.

**Mudar o formato do JSON sem avisar.** Renomear um campo, trocar o `null` por um `0`, reordenar sem motivo. Custo: tudo o que lê esse JSON quebra. Se o contrato muda, sobe-se a versão maior e avisa-se.

**`subprocess` com `shell=True` e um texto montado com dados de fora.** Custo: que outra pessoa execute comandos na sua máquina.

**`eval` ou `pickle` com dados que não são seus.** Custo: o mesmo.

**`random` para um segredo.** Custo: um token que outra pessoa pode reconstruir.

**Dar por terminado um programa que ninguém instalou como um usuário o instalaria.** Funciona no ambiente de desenvolvimento e falha na instalação porque falta um arquivo ou uma dependência. Constrói-se a *wheel* e testa-se **de outra pasta**, não a partir do código.

**Ler só a cor do `pytest`.** O verde com 2 testes de 30 é um verde. Lê-se a contagem.

## Exercícios

### Exercício 1 — Um nome longo de verdade

Escreva um `servicios-largo.toml` com dois serviços que apontem para o laboratório: `catalogo` e outro chamado `notificaciones-de-clientes` (26 caracteres). **Antes de rodar**, preveja em que coluna `ESTADO` vai começar e rode. Comprove que a tabela fica alinhada.

### Exercício 2 — Quebre o contrato

Em uma cópia de `fig11_05/`, renomeie em `formato.py` o campo `"caido"` do resumo do JSON para `"caidos"`. Rode `pytest -q --tb=short`. Anote quantos testes ficam vermelhos e qual. Conserte e rode de novo. Responda: o que teria acontecido com um script que lê `resumen.caido` se ninguém tivesse esse teste?

### Exercício 3 — Dois canais, dois arquivos

Rode `python -m revisor --verbose` redirecionando a saída padrão para `reporte.txt` e a de erro para `registro.txt` (no shell, `> archivo` redireciona a padrão e `2> archivo` a de erro). **Antes de rodar**, preveja o que haverá em cada arquivo. Depois veja o seu conteúdo.

### Exercício 4 — Uma linha de registro a mais

Adicione ao `revisor` uma mensagem de nível `DEBUG` em `main` que diga quantos serviços foram lidos da configuração. Deve aparecer com `--verbose` e não sem ele. Comprove que os 30 testes continuam passando, e que `ruff` e `mypy` continuam sem reportar nada.

## Soluções

### Solução 1

O nome mais longo mede 26; com os dois espaços de respiro a largura é 28, então `ESTADO` começa na coluna 28 (contando a partir de 0). A execução:

```text
$ python -m revisor --config servicios-largo.toml
SERVICIO                    ESTADO    TIEMPO  DETALLE
catalogo                    ARRIBA     172ms  200
notificaciones-de-clientes  ARRIBA      94ms  200

2 servicios · 2 arriba · 0 lentos · 0 caídos · promedio 133ms
```

A palavra `ESTADO` fica alinhada com `ARRIBA` nas duas linhas, e `catalogo` tem a sua coluna alargada igual à do outro. Com os serviços de sempre, a largura volta a ser 12.

### Solução 2

Fica vermelho **um** teste, `test_el_json_es_un_contrato`; os outros 29 passam:

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

O teste diz qual campo mudou (`'caidos': 1` contra `'caido': 1`). Sem ele, um script que lesse `resumen.caido` teria recebido um campo inexistente (`null` ou um erro, conforme a linguagem do script) e teria seguido, no melhor dos casos, tratando “0 caídos” como um bom resultado, justamente quando há um serviço fora do ar. É o tipo de erro que não dá as caras até o pior dia.

### Solução 3

Em `registro.txt` vão as quatro linhas `DEBUG revisor: ...` (o canal de erro); em `reporte.txt`, a tabela com o seu resumo (o canal padrão). Nenhuma das coisas se mistura com a outra:

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

### Solução 4

No `cli.py`, logo antes de `asyncio.run(...)`:

```python
logging.getLogger("revisor").debug("leídos %s servicios", len(servicios))
```

O módulo `logging` já está importado. Resultado, medido (a linha nova sai primeiro, porque é escrita antes de consultar qualquer coisa):

```text
$ python -m revisor --verbose 2>&1 >/dev/null | head -n 2
DEBUG revisor: leídos 4 servicios
DEBUG revisor: reportes: CAIDO, —, sin conexión
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
```

O primeiro comando precisa de uma leitura com calma, porque a ordem dos redirecionamentos importa e eles se aplicam da esquerda para a direita. `2>&1` diz “mande a saída de erro (o canal 2) para onde hoje vai a padrão (o canal 1)”, que nesse momento é o pipe `|` para o `head`. Depois, `>/dev/null` manda a saída **padrão** para o lixo. Resultado: o que chega ao `head` é só o registro, que saía pelo canal de erro, e o relatório é descartado. E `head -n 2` mostra apenas as duas primeiras linhas do que recebe. Se você escrevesse os dois redirecionamentos ao contrário, `>/dev/null 2>&1`, as duas saídas iriam para o lixo e você não veria nada.

Os 30 testes continuam passando, e `ruff check`, `ruff format` e `mypy` não dizem nada.

## Como sei que consegui

- [ ] `pytest -q` em `fig11_05/` termina com `30 passed`, e esse é o número que você esperava.
- [ ] `ruff check`, `ruff format --check` e `mypy` não apontam nada; os quatro comandos dão o mesmo resultado com Python 3.12 (e com 3.14 se você o tem).
- [ ] Com `servicios-20.toml`, `--concurrencia 1` leva perto de 10 segundos e `--concurrencia 20`, menos de um.
- [ ] `fig11_06.py` mostra seis serviços na sua ordem, com `LENTO`, `error de red`, `503` e `tiempo agotado` nas suas linhas, e nenhum derruba os demais.
- [ ] Um serviço que leva 10 segundos com `timeout_ms = 1000` é reportado como `tiempo agotado` em pouco mais de um segundo, e outro sem `timeout_ms` em pouco mais de cinco.
- [ ] `python -m pip wheel --no-deps -w dist .` produz `dist/revisor-1.0.0-py3-none-any.whl`, e `pipx install` desse arquivo deixa o comando `revisor`.
- [ ] De uma pasta que não é a do projeto, `revisor --version` diz `revisor 1.0.0`, `revisor --help` mostra a ajuda das opções e `revisor --config servicios.toml` termina com `echo $?` igual a `1` (há serviços `LENTO` e `CAIDO`) ou a `0` (todos no ar).
- [ ] Você sabe explicar por que o relatório vai para a saída padrão e o registro para a de erro; por que o JSON é testado como contrato; e por que `subprocess` recebe uma lista, `eval` não se usa com dados de fora e os segredos saem de `secrets`.

## Resumo

Responda sem olhar a lição:

1. Que duas coisas fazem com que o JSON do `revisor` seja um contrato, e que teste o protege?
2. Como se calcula a largura da primeira coluna? Por que com os quatro serviços canônicos a tabela sai idêntica à de antes?
3. Que diferença há entre a saída padrão e a saída de erro? Por que o relatório vai para uma e o registro para a outra?
4. Por que uma mensagem do `logging` leva `%s` e os valores à parte, e não uma f-string?
5. Por que o `basicConfig` está em `cli.py` e não em `revision.py`? Por que o nível é posto no logger `"revisor"` e não no de todos?
6. O que acontece com `subprocess.run(f"echo {x}", shell=True)` se `x` traz um `;`? E com uma lista?
7. Por que o `random` não serve para um token e o que você usa no lugar?
8. O que contém uma *wheel* e o que não contém? Por que uma ferramenta se instala com o `pipx` e não com o `pip` no Python do sistema?
9. Por que o teste de `--version` pode ficar vermelho mesmo que você tenha mudado o `pyproject.toml`? Como se conserta?
10. Enumere, de memória, as sete comprovações com que o curso termina e o comando de cada uma.

## Para ler mais

- [Documentação do `logging` e o seu guia básico](https://docs.python.org/pt-br/3/howto/logging.html) — níveis, loggers e configuração, com o padrão correto para bibliotecas e programas. Consultado em 7 de outubro de 2026.
- [Guia de empacotamento do Python: escrever o `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) e [`pipx`](https://pipx.pypa.io/stable/) — a fonte de todo o último trecho: o que vai no `pyproject.toml`, o que é uma *wheel* e como se instalam as ferramentas. Consultado em 7 de outubro de 2026.
- [Documentação do `subprocess`: considerações de segurança](https://docs.python.org/pt-br/3/library/subprocess.html#security-considerations) e [`secrets`](https://docs.python.org/pt-br/3/library/secrets.html) — os dois avisos oficiais de 11.3 com os seus exemplos. Consultado em 7 de outubro de 2026.
- [Novidades do Python 3.14](https://docs.python.org/pt-br/3/whatsnew/3.14.html) — o interpretador sem GIL, as *t-strings* e o resto do que é novo, para ler quando o curso ficar para trás. Consultado em 7 de outubro de 2026.
