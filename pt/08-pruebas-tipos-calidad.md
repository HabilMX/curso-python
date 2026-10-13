# Lição 8 — Testes, tipos e qualidade

**Tempo:** 2 × 90 min (a primeira sessão vai até o final de 8.3; a segunda começa em 8.4)

**O que você constrói:** o `revisor` com 21 testes que se rodam com um comando, com os tipos verificados e o estilo vigiado

**O que você aprende:** `pytest` (`assert`, o teste visto em vermelho antes de verde, `parametrize`, `tmp_path` e `monkeypatch`), tipagem gradual com `mypy`, `ruff` para verificar e formatar, e a ler a contagem do relatório e não o código de saída

**De onde você vem.** Você traz o pacote da [Lição 7](07-paquete-linea-de-comandos.md): o `revisor` vive em `~/curso-python/revisor/` com layout `src/`, é instalado com `pip install -e .` e é executado com `python -m revisor`. Com os quatro serviços de prática ele imprime a tabela do programa do curso e sai com código 1, porque há um lento e um fora do ar. Funciona. O que você não tem é uma forma de **saber que ele continua funcionando** depois de mexer nele: até hoje a única comprovação era rodá-lo e olhar a tabela, e os olhos se cansam e não veem o que não esperam ver. Esta lição lhe dá três verificadores que não se cansam: um que executa o seu código com dados conhecidos e compara a resposta, outro que lê o seu código sem executá-lo e comprova que os dados se encaixam, e outro que vigia que ele esteja escrito como se escreve em Python.

**O que esta lição não faz.** Ela não toca a rede: o `revisor` continua lendo os dados simulados de `SIMULADO`, e consultar serviços de verdade é a [Lição 9](09-http-y-asyncio.md). Também não testa código assíncrono nem simula a rede, que é a [Lição 10](10-concurrencia-pruebas-sin-red.md), nem mede quanto código cada teste toca (a *cobertura*): é um número útil e fácil de falsear, e não serve de nada até você saber o que cada teste testa.

## Ao terminar, você vai conseguir

- Escrever um teste com `pytest` (um arquivo `test_*.py`, uma função `test_*` e um `assert`), rodá-lo e ler o seu relatório de cima para baixo.
- Ver um teste **em vermelho antes de verde**, e explicar por que um teste que você nunca viu falhar não demonstra nada.
- Dizer quantos testes rodaram lendo o **relatório**, e explicar por que o código de saída não basta: um `0` convive com um teste que nunca foi executado.
- Converter uma tabela de casos em um único teste com `@pytest.mark.parametrize` e distinguir no relatório qual linha falhou.
- Testar código que lê arquivos com `tmp_path` e código que depende de outra função com `monkeypatch`, sabendo **onde** é preciso aplicar o patch.
- Verificar os tipos do pacote com `mypy` em modo estrito e ler a sua mensagem, e explicar o que quer dizer que a tipagem do Python seja gradual.
- Verificar e formatar o código com `ruff check` e `ruff format`, com as três ferramentas configuradas no `pyproject.toml`.

## O porquê antes do como

Abra `src/revisor/modelo.py` e procure, dentro de `clasificar`, a linha que decide quando um serviço é lento: `if tiempo_ms is not None and tiempo_ms >= umbral_ms:`. Imagine que amanhã, com pressa, alguém “conserta” esse `>=` e o deixa em `>`: um único caractere. Rode o `revisor` com os quatro serviços de prática. **A tabela sai idêntica.** `catalogo` leva 142 ms, `inventario` 2300, `pagos` 87 e `reportes` não responde; nenhum leva exatamente 1000 ms, o único valor em que `>=` e `>` se comportam de forma diferente. O defeito existe, o programa roda sem um erro e a tabela parece perfeita. No dia em que um serviço real levar justamente 1000 ms (os tempos de resposta se acumulam em números redondos mais do que parece), ele ficará “no ar” quando a regra do curso diz que já é “lento”.

A comprovação que você tinha, olhar a tabela, **não podia** encontrar esse defeito, porque não pergunta nada sobre os casos que importam. O que é preciso é escrever essas perguntas uma vez (“um serviço que responde 200 em 999 ms, está no ar? e um que responde 200 em 1000 ms, está lento?”) e que uma máquina as repita toda vez que você mexer no código, em menos de um segundo. Isso é um **teste**: um programa pequeno que chama o seu código com uma entrada conhecida e comprova que a resposta é a que deve ser. Um conjunto de testes é uma rede de segurança: deixa você mudar o código com calma, porque se quebrar algo você sabe na hora e sabe onde.

A lição traz três ferramentas, cada uma com a sua pergunta:

| Ferramenta | A pergunta que responde | Como trabalha |
|---|---|---|
| `pytest` | O programa faz o que eu disse, com estes dados? | **Executa** o seu código e compara |
| `mypy` | Os dados se encaixam entre si? Passei um texto onde ia um número, ou esqueci que algo pode ser `None`? | **Lê** o seu código sem executá-lo |
| `ruff` | Está escrito como se escreve em Python, sem importações sobrando nem armadilhas conhecidas? | **Lê** o seu código e o reformata |

Nenhuma substitui as outras, e juntas são o que em uma equipe se chama de portão de qualidade (*quality gate*): a mudança que não passa por elas não entra. O blog da Hábil conta como essa disciplina se parece em um projeto de equipe, em [testes que detectam erros, cobertura e portões de qualidade](https://www.habil.mx/pt/blog/testes-que-detectam-erros-cobertura-quality-gate/). A primeira sessão usa o `pytest` até ter os 21 testes do `revisor`; a segunda verifica tipos e estilo e deixa as três ferramentas instaladas no projeto.

### Prepare as ferramentas

Elas são instaladas com o `pip` (como na Lição 1, com `python -m pip`, para que seja o `pip` do ambiente) dentro do ambiente virtual do curso, o mesmo que você ativou na [Lição 1](01-instalacion.md) (o prompt mostra `(.venv)`):

```bash
python -m pip install pytest==9.1.1 ruff==0.16.10 mypy==2.4.0
```

As versões vão fixas de propósito: as mensagens do `ruff` e do `mypy` mudam de redação entre versões, e com as mesmas versões o que você vê na sua tela é o que você vê aqui. São as vigentes em 7 de outubro de 2026 no [PyPI](https://pypi.org/project/pytest/), e as mesmas estão em `herramientas/requisitos.txt` do repositório do curso. São ferramentas de **desenvolvimento**: o `revisor` não precisa delas para rodar, então não entram na lista `dependencies` do `pyproject.toml`, que continua vazia até a Lição 9. Confira com `pytest --version`, `ruff --version` e `mypy --version`; se alguma disser “command not found”, o ambiente virtual não está ativo, o mesmo tropeço da Lição 1.

## Os conceitos

### 8.1 `pytest`: executar o seu código com dados conhecidos

#### 8.1.1 O primeiro teste

O [`pytest`](https://docs.pytest.org/en/stable/getting-started.html) é o programa que procura os testes, os executa e lhe entrega um relatório. Não vem com o Python: é uma ferramenta de terceiros, a mais usada da linguagem. [As suas regras para encontrar testes](https://docs.pytest.org/en/stable/explanation/goodpractices.html) são poucas: ele procura arquivos chamados `test_*.py` ou `*_test.py` e, dentro deles, executa as funções cujo nome começa com `test`. Todo o resto ele ignora. Guarde essa regra: mais adiante, ignorar em silêncio sai caro.

Um teste prepara uma entrada, chama o código que você quer comprovar e termina com um `assert`. Comece pelo menor, sobre a função `formatear_tiempo` da Lição 3. Para que o exemplo rode sozinho, em um arquivo, a função vai copiada acima dos seus testes:

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

As duas funções de baixo são os testes, e se reconhecem pelo nome. Cada uma contém um `assert`, a palavra reservada que significa “afirmo que isto é verdade”: [`assert condición`](https://docs.python.org/pt-br/3/reference/simple_stmts.html#the-assert-statement) não faz nada se a condição é verdadeira e, se é falsa, interrompe a função com um `AssertionError`. Chamar e afirmar: isso é tudo o que é preciso. Dois detalhes de forma. Os nomes são frases que dizem **o que se espera**: `test_sin_tiempo_va_una_raya` diz, no dia em que ficar vermelho, o que quebrou sem você abrir o arquivo. E o `-> None` diz que a função não devolve nada, como todo teste: ou termina em silêncio ou é interrompida com um erro (em 8.4 você verá que o `mypy` em modo estrito exige isso).

Este arquivo não se chama `test_*.py`, mas quando você dá ao `pytest` o nome de um arquivo, ele o roda mesmo que não cumpra o padrão. Com o ambiente ativo:

```text
$ pytest -q fig08_01.py
..                                                                       [100%]
2 passed in 0.00s
```

A opção `-q` (*quiet*, “silencioso”) pede um relatório curto. A primeira linha tem um ponto para cada teste que passou e, à direita, o andamento. A última é o resumo: `2 passed`, “dois passaram”. **Essa é a linha que você vai aprender a ler com uma desconfiança saudável**: diz quantos testes foram executados e o que aconteceu com cada um.

#### 8.1.2 Vê-lo em vermelho antes de verde

Um teste que passa não diz muito: ele passa se o código está certo, mas também se o teste não comprova nada. Só há uma maneira de saber se um teste comprova algo: **vê-lo falhar**. A partir de hoje, cada teste você vê em vermelho antes de aceitá-lo em verde. Aqui está o defeito do começo, escrito dentro de um arquivo:

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

`clasificar` decide o estado a partir do código e do tempo; esta versão curta devolve texto. Tem o defeito: usa `>` onde a regra diz “mil milissegundos ou mais”. Os dois testes são as perguntas de antes. Rode-o e olhe também o código de saída:

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

Leia o relatório de cima para baixo. `.F`: o primeiro teste passou e o segundo falhou. A seção `FAILURES` traz um bloco para cada falha, com o nome do teste, o seu código e uma seta `>` na linha que falhou. As linhas com `E` são o erro: `assert 'ARRIBA' == 'LENTO'`. Isso é o especial do `pytest`: ele reescreve os seus `assert` para que, ao falhar, mostrem **os dois valores** comparados ([a documentação explica isso](https://docs.pytest.org/en/stable/how-to/assert.html)); com um `assert` puro você teria visto apenas `AssertionError`. As linhas com `-` e `+` detalham a comparação; nesta versão do `pytest`, a que leva `-` é o valor da direita do `==` (`LENTO`, o que o teste esperava) e a que leva `+` o da esquerda (`ARRIBA`, o que o código devolveu). Depois vêm o arquivo e a linha (`fig08_02.py:18`), um resumo de uma linha por falha, cortado na largura do terminal (por isso termina em `=...`), e a contagem: `1 failed, 1 passed`.

O `echo $?` imprime o **código de saída** do comando anterior: o número que todo programa deixa ao terminar para dizer ao sistema como foi. Por convenção, `0` é “bem” e qualquer outro é “algo falhou”. Você o usou na Lição 7 com o `revisor`. Aqui o `pytest` saiu com `1` porque houve testes que falharam. Os scripts e as ferramentas de integração contínua leem esse número para decidir se seguem ou param.

A correção é trocar `>` por `>=`:

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

Dois passaram, código `0`. Repare na ordem: primeiro a pergunta (o teste do 1000), depois o vermelho contra o código com defeito, e só então a correção. Essa ordem é a garantia. Se você a tivesse escrito **depois** de corrigir, nunca saberia se ela era capaz de detectar o defeito. Quando você adicionar um teste a um código que já funciona, o equivalente é quebrar o código de propósito por um momento, ver o vermelho e desfazer a mudança. O Exercício 1 faz isso com o `revisor` real.

#### 8.1.3 A contagem se lê do relatório, não do código de saída

Aqui está a armadilha que dá nome a uma das regras do curso. [A documentação do `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) define os seus códigos de saída: `0`, todos os testes **que foram coletados** passaram; `1`, alguns falharam; `2`, o usuário interrompeu; `3`, erro interno; `4`, erro de uso; `5`, nenhum teste foi coletado; `6`, o máximo de avisos foi superado. Repare na frase do `0`: “os que foram coletados”. Um teste que o `pytest` nunca coletou não existe para ele. Veja um arquivo onde isso acontece:

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

Há quatro funções de teste e uma armadilha. A última se chama `prueba_sin_respuesta_es_caido`, não `test_...`, e o `pytest` **não a vê**. O seu `assert` é falso de propósito (afirma que a ausência de resposta é `"ARRIBA"`), então se ela fosse executada falharia. Rode-o; depois peça ao `pytest` que apenas enumere o que encontrou (`--collect-only`) e que rode só os testes cujo nome contenha um texto que não existe (`-k`):

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

O primeiro relatório diz `3 passed` e o código de saída é `0`: verde em toda a linha, com um teste quebrado que ninguém executou. Um quadro que só olhasse o código de saída diria “tudo certo”. Quem lê o relatório vê `3` e, se escreveu quatro, se pergunta onde foi parar o quarto; `--collect-only` confirma, porque enumera três. Acontece em qualquer projeto: com uma função mal nomeada, um arquivo que não se chama `test_*.py` ou uma mudança de nome que deixou um teste de fora. O último comando mostra o outro extremo: `3 deselected` e código `5`, “nenhum foi coletado”. Aí o `pytest` sim avisou, mas o aviso se perde se o seu script termina com `|| true` ou se há um filtro (`| tail`, `| grep`) no meio que engole o código de saída. Daí a regra:

> **O número de testes se lê do relatório (“N passed”). Um `0` não é evidência de que rodou o que você achava. Compare sempre N com o N que você espera.**

O `revisor` termina esta lição com 21 testes, e esse número é o que você vai comprovar no final de cada sessão. A Lição 9 parte dele. Se um dia o relatório disser 20, não importa que esteja em verde: algo desapareceu. (Um teste também pode ser marcado como *ignorado*, `skipped`, e então nem passa nem falha: só aparece no resumo. Neste curso isso não se usa; se um teste não serve, ele é consertado ou apagado.)

### 8.2 `parametrize`: uma tabela de casos, um único teste

`clasificar` aplica quatro regras e tem uma fronteira (1000 ms) onde se concentram os erros. Para testá-la bem você precisa de **sete casos**: dois rápidos (142 e 999 ms, o mais lento que ainda está no ar), dois lentos (1000 ms, o primeiro que já é, e 2300), dois fora do ar por código (503 e 404) e um sem resposta (`None`, `None`). Escritos como funções separadas seriam sete funções idênticas exceto por dois números e um texto, com sete lugares para mexer no dia em que a regra mudar.

O que você quer é escrever o teste uma vez e os casos como uma tabela. O [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html) faz isso. A arroba é um **decorador**: uma linha acima de uma função que a modifica (você já viu `@dataclass(frozen=True)` na Lição 5, sobre uma classe). Aqui ele diz ao `pytest` que execute a função uma vez para cada linha:

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

O primeiro argumento é a lista de **nomes dos parâmetros**, que devem coincidir com os da função de baixo. O segundo é a lista de **casos**: uma tupla por caso, com um valor para cada nome. O `esperado` vai na tabela e não calculado dentro da função: se o teste usasse a mesma fórmula do código que testa, dois erros iguais se cancelariam e ele passaria em verde sobre um defeito. Rode-o e enumere o que coletou:

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

`7 passed`: o `pytest` converteu a função em **sete testes**, cada um com um nome que leva entre colchetes os valores do caso (`test_clasificar[200-1000-LENTO]`). Esse nome importa quando algo falha. Veja o que acontece se você colocar o defeito do `>` nesta tabela:

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

`1 failed, 6 passed`, e a linha `..F....` diz que foi a terceira linha. O nome, `test_clasificar[200-1000-LENTO]`, é o caso exato; sob ele, o `pytest` imprime os valores dos parâmetros **desse** caso, e os outros seis passaram: uma linha que falha não interrompe as demais. Adicionar um caso é adicionar uma linha.

Agora o projeto. Os testes reais vivem em uma pasta `tests/` junto de `src/`. O primeiro cobre `clasificar` com os sete casos, com o `Estado` verdadeiro:

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

Compara com `is` e não com `==`: os membros de um `Enum` são únicos e `is` pergunta pela identidade, como o `is None` da Lição 2. E os parâmetros levam **anotações de tipo**, como o código do pacote; em 8.4 você verá por quê. O segundo cobre `formatear_tiempo` com quatro casos: sem tempo, um em milissegundos, o último que ainda é (999) e um em segundos:

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

Para que o `pytest` saiba onde procurar sem que você diga, o `pyproject.toml` ganha uma seção (o arquivo completo está em 8.6):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` é a lista de pastas onde ele procura quando você o roda sem argumentos. No que segue, a linha `cd fig08_15` representa “estar dentro do projeto”; você já está em `~/curso-python/revisor/`, então não a escreva.

```text
$ cd fig08_15
$ pytest -q tests/test_modelo.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q tests/test_formato.py
....                                                                     [100%]
4 passed in 0.00s
```

Sete e quatro: onze até agora. Cada relatório conta o que deve; se você somar errado, ele lhe dirá.

### 8.3 `tmp_path` e `monkeypatch`: testes que não sujam nem dependem de nada

`clasificar` e `formatear_tiempo` são funções puras: recebem valores, devolvem um valor e não tocam em nada fora de si. Mas `leer_servicios` lê um arquivo, e `main` lê argumentos, imprime e chama a função que consulta os serviços. Testar isso levanta dois problemas, e o `pytest` traz uma ferramenta para cada um. Ambas são *fixtures*.

Uma **fixture** é uma função que o `pytest` executa por você antes de um teste para entregar a ele algo de que precisa. Você a pede declarando-a como **parâmetro**: se o seu teste é `test_algo(tmp_path)`, o `pytest` vê o nome, procura uma fixture que se chame assim, a executa e passa o resultado como argumento. Você não a importa nem a chama ([a documentação detalha isso](https://docs.pytest.org/en/stable/how-to/fixtures.html)).

#### 8.3.1 `tmp_path`: uma pasta nova para cada teste

Para testar que `leer_servicios` lê bem um arquivo, você precisa de um arquivo. Se os testes usassem o `servicios.toml` do seu projeto, qualquer mudança nesse arquivo quebraria testes que não têm nada a ver, e um teste que **escreve** sujaria a sua pasta. A fixture [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html) entrega um `Path` (o do `pathlib`, da Lição 6) que aponta para uma **pasta temporária, nova e vazia, única para esse teste**:

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

O primeiro teste monta um `servicios.toml` pequeno e comprova que dois serviços são contados. O segundo demonstra o isolamento: recebe uma pasta **vazia**, ainda que o anterior acabe de escrever um arquivo na dele. Para comprová-lo usa duas coisas do `pathlib`: `is_dir()` pergunta se o caminho é uma pasta que existe, e `iterdir()` percorre o que há dentro dela, um elemento por arquivo ou subpasta. Como `iterdir()` entrega os elementos um por um e não uma lista, `list(...)` os junta em uma lista (como você fez com `list(tiempos_ms)` na Lição 4), e a lista de uma pasta vazia é `[]`.

```text
$ pytest -q fig08_07.py
..                                                                       [100%]
2 passed in 0.01s
```

As pastas vivem no diretório temporário do sistema, e o `pytest` conserva as das últimas três execuções caso você queira inspecionar o que um teste que falhou deixou.

Com isso você escreve os testes de `leer_servicios`: um que lê um arquivo válido e sete que o rejeitam. Três dos sete protegem o que você viu em 6.4.3: `url mal formada` (com `http://[::1`, `urlsplit` lança `ValueError`, e o teste exige que chegue como a mensagem de configuração e não como um *traceback*; se você tirar o `try` de `es_url_http`, fica vermelho), `url con salto` (uma quebra de linha dentro do endereço; fica vermelho se você tirar `isprintable()`. Na tabela você verá `\\n`, com a barra dupla: dentro de uma string de Python, `\\` escreve uma barra invertida, de modo que o arquivo TOML recebe `\n`, e o TOML a converte na quebra de linha de verdade) e `url con acento` (`https://catálogo.example`; fica vermelho se você tirar `isascii()`). As sete compartilham a forma, então vão em uma tabela, com `ids=` para que o relatório use nomes legíveis:

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

O arquivo válido é comparado com uma lista que contém um `Servicio`; funciona porque os `dataclass` comparam pelo conteúdo. Os de rejeição usam `with pytest.raises(ErrorDeConfiguracion) as informe:`, um `with` (o da Lição 6) que afirma o contrário de um `assert` normal: que o código de dentro **lança** essa exceção. Se o bloco termina sem lançar nada, o `pytest` marca o teste como falho com `DID NOT RAISE`. O `as informe` guarda a exceção; `str(informe.value)` é a mensagem que você escreveu na Lição 6, e o teste a compara inteira. Comprovar a mensagem e não só o tipo distingue “falhou pela razão correta” de “falhou por qualquer razão”.

#### 8.3.2 `monkeypatch`: mudar algo somente enquanto o teste dura

O `main` chama `revisar_todos`, que hoje lê `SIMULADO` e a partir da Lição 9 consultará a rede. Para testar somente o que `main` faz com os resultados (que código de saída devolve), convém **substituir** essa função por uma falsa. A fixture [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) existe para isso: `monkeypatch.setattr(destino, valor)` substitui um atributo, e **ao terminar o teste o deixa como estava**. Veja o mecanismo em um arquivo pequeno:

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

Há uma variável de módulo, `UMBRAL_LENTO_MS`, e uma função que a lê. O primeiro teste usa o limiar de sempre. O segundo **o muda para 3000 durante esse teste**: `"fig08_08.UMBRAL_LENTO_MS"` é o endereço do atributo, com a forma `módulo.nombre` (este módulo se chama como o arquivo, sem o `.py`); dentro desse teste, 1500 já não é lento. O terceiro comprova que depois o limiar voltou a valer 1000.

```text
$ pytest -q fig08_08.py
...                                                                      [100%]
3 passed in 0.00s
```

Os três passaram, e o que importa é o terceiro: a mudança **não fica**. Atribuir a variável à mão a deixaria mudada para os testes seguintes e produziria falhas que dependem da ordem, das mais difíceis de entender.

Agora o teste real. `main` devolve `0` se tudo está no ar e `1` se não. Para testar os dois casos sem depender dos dados simulados, você substitui `revisar_todos` por uma função falsa que devolve o que você decidir:

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

Antes dos testes, a constante `CONFIGURACION` é o texto de um `servicios.toml` pequeno, entre aspas triplas, como os textos de várias linhas da Lição 6. A barra invertida logo depois das aspas que abrem (`"""\`) evita que o texto comece com uma quebra de linha: no final de uma linha, dentro de um texto, `\` quer dizer “esta linha continua na seguinte”, de modo que a primeira linha do texto é `[[servicios]]` e não uma vazia. Ao TOML tanto faria, mas assim o que o teste escreve é exatamente o que você vê.

O primeiro teste usa os dados simulados reais com uma configuração que inclui `reportes`, que está fora do ar. O segundo substitui a função por `todos_arriba`, definida dentro do teste porque só ele a usa, com a mesma assinatura da verdadeira: quando `main` a chamar, não saberá que é falsa.

Olhe bem o destino: `"revisor.cli.revisar_todos"`, o nome **dentro de `cli`**, e não o de `revision`, onde a função é definida. [A documentação do `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) diz isso: é preciso aplicar o patch na referência que o seu código usa. Uma instrução `from modulo import nombre` cria, dentro do módulo que importa, um nome próprio que aponta para a mesma função: dois nomes para uma coisa, e substituir um não muda o outro. O `cli.py` começa com `from revisor.revision import revisar_todos`, então o `main` procura `revisar_todos` entre os nomes de `cli`. Se você aplicasse o patch no de `revision`, o `cli` continuaria chamando a verdadeira. Em “O erro que você vai ver” você o quebra de propósito.

Com os quatro arquivos escritos, você roda **tudo junto** pela primeira vez. Você já sabe o que deve dizer:

```text
$ cd fig08_15
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

Vinte e um pontos e `21 passed`: 7 + 4 + 8 + 2. Esse número é o contrato com a Lição 9. **Aqui termina a primeira sessão.** Quando você voltar, `pytest -q` é a primeira coisa que você roda, para saber que deixou o projeto como achava.

### 8.4 `mypy`: tipos que se verificam sem executar nada

#### 8.4.1 As anotações não são impostas na execução

Desde a Lição 3 você escreve anotações como `tiempo_ms: int | None`. A Lição 0 disse que **o Python não as usa ao executar**: são informação para quem lê e para ferramentas externas, não uma ordem. A [PEP 484](https://peps.python.org/pep-0484/), que as introduziu, diz isso sem rodeios: não se verificam tipos em tempo de execução. Vê-se com quatro linhas:

```python
# fig08_09.py
def doble(tiempo_ms: int) -> int:
    return tiempo_ms * 2


print(doble("142"))
```

A assinatura diz que `doble` recebe um inteiro, e a chamada lhe passa o texto `"142"`. Rode-o e peça ao `mypy` que o verifique:

```text
$ python fig08_09.py
142142
$ mypy fig08_09.py
fig08_09.py:6: error: Argument 1 to "doble" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

O Python não reclama: `"142" * 2` é válido (repete o texto) e o programa imprime `142142`, um resultado absurdo para um tempo em milissegundos que ninguém avisou. O [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) lê o arquivo **sem executá-lo**, compara cada chamada com as anotações e reclama. A sua mensagem tem sempre a mesma estrutura: `archivo:línea: error: descripción  [código]` (arquivo, linha, descrição, código). Diz onde (linha 6), o quê (o argumento 1 de `doble` é `str` e se esperava `int`) e, entre colchetes, o código do tipo de erro (`arg-type`), útil para pesquisá-lo. A última linha conta erros e arquivos.

Isso é a *tipagem gradual*: você decide quanto anota, e o `mypy` verifica o que você anotou. É a contrapartida do que o TypeScript faz no [curso desta casa](https://www.habil.mx/pt/cursos/typescript/): os tipos são escritos e verificados antes de rodar, mas não são um mecanismo da linguagem em execução.

#### 8.4.2 O que o `mypy` pega: o `None` que você esqueceu

O erro mais frequente que o `mypy` encontra é esquecer que algo pode ser `None`. O serviço `reportes` não responde e o seu `tiempo_ms` é `None`: por isso o campo é anotado `int | None`. Aqui está uma função que o esquece (o programa captura o erro só para que você veja a mensagem sem ruído):

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

O Python fica sabendo quando chega à segunda chamada: `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`. Se essa chamada estivesse em um caminho percorrido uma vez por mês, o erro teria chegado à produção. O `mypy` o encontra **sem rodar nada**, na linha 3, e o explica: `Unsupported operand types for / ("None" and "int")` e uma nota, `Left operand is of type "int | None"`. A solução não é calar o `mypy`, e sim decidir o que deve acontecer quando não há tempo. Aqui, devolver `None` também, e dizê-lo no tipo de retorno:

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

A função agora diz a verdade na sua assinatura, `float | None`, e essa verdade tem uma consequência: **todo aquele que usar o resultado fica obrigado a verificar se é `None`**, porque o `mypy` reclamará se o tratar como número. Em vez de um erro escondido que aparece de madrugada, você tem uma pergunta incômoda no seu editor, que é justamente onde convém tê-la.

#### 8.4.3 `match` e o caso que falta

Na Lição 5 você viu que `match` junto a um `Enum` tem uma vantagem que o `mypy` aproveita aqui. Imagine que o `revisor` ganha um quarto estado, `DEGRADADO`, e uma função que traduz estados em cores fica sem o seu `case`:

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

O Python **não avisa**: quando nenhum `case` coincide, o `match` termina sem fazer nada, a função chega ao seu final sem um `return` e devolve `None`. A quarta linha imprime `DEGRADADO -> None`, uma cor que não existe, e em um programa real esse `None` viajaria até quem o use. O `mypy` vê isso sem rodar nada: a assinatura promete um `str`, mas há um caminho (o de `DEGRADADO`) que termina sem devolver nada, e por isso diz `Missing return statement`. A mensagem não menciona o membro que falta, mas aponta a função (`def semaforo`), e basta comparar os seus `case` com os membros do `Enum` para encontrá-lo. É a rede de segurança que a Lição 5 prometia: você adiciona um membro, e o `mypy` aponta cada `match` que ficou para trás.

#### 8.4.4 Gradual: o que você não anota, o `mypy` não verifica, a menos que você peça

[A documentação do `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) estabelece: uma função sem anotações é considerada de tipagem dinâmica, e por padrão o `mypy` **não verifica o seu corpo**. É uma decisão de design para poder adicionar tipos aos poucos a código antigo. Veja com uma função sem uma única anotação:

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

Sem opções, o `mypy` diz “Success”: `duplicar` não tem anotações e não é verificada. Com `--strict`, o mesmo arquivo dá dois erros: a função não tem anotações (`no-untyped-def`) e você a chama de código com tipos (`no-untyped-call`). O modo estrito é um atalho que liga várias verificações de uma vez; [a documentação as lista](https://mypy.readthedocs.io/en/stable/command_line.html): entre elas `--disallow-untyped-defs` (toda função leva anotações), `--check-untyped-defs` (verificar também o corpo das que não levam), `--warn-return-any` e `--warn-unused-ignores`. A lista exata pode mudar entre versões, por isso a lição fixa a do `mypy`.

A regra do curso: **o projeto vai em modo estrito desde o princípio**; é muito mais barato manter os tipos do que adicioná-los depois. Configura-se no `pyproject.toml`, [onde o `mypy` o lê](https://mypy.readthedocs.io/en/stable/config_file.html):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`python_version` é contra qual versão do Python verificar (a do Mint do curso), `strict = true` liga o modo estrito e `files` diz o que verificar quando você o roda sem argumentos: o pacote e também os testes, porque um teste mal tipado esconde erros igual a qualquer outro código.

#### 8.4.5 `mypy` no `revisor`

Com a configuração posta, o projeto inteiro é verificado com um comando. Todo o código do pacote e dos testes leva anotações (por isso os testes terminam em `-> None` e pedem `tmp_path: Path`):

```text
$ cd fig08_15
$ mypy
Success: no issues found in 11 source files
```

`Success: no issues found in 11 source files`: sete arquivos do pacote (`__init__`, `__main__`, `cli`, `configuracion`, `formato`, `modelo` e `revision`) e quatro de testes. Leia a contagem como você aprendeu com o `pytest`: se um dia disser `0 source files`, o `mypy` não verificou nada e o verde não vale. Para vê-lo trabalhar sobre o projeto, faça o Exercício 3: mude uma anotação e veja como o `mypy` leva você até quem a usa. É o seu uso mais valioso: quando você muda a assinatura de uma função, ele diz todos os lugares que você deve ajustar.

Um aviso sobre as saídas de emergência. `# type: ignore` diz ao `mypy` que não reclame daquela linha, e o tipo `Any` desliga as verificações sobre um valor. Existem por razões legítimas (código de terceiros sem tipos) e são a forma mais rápida de tornar a ferramenta inútil. A regra: **a reclamação quase sempre tem razão**; antes de calá-la, entenda o que ela diz.

### 8.5 `ruff`: verificar e formatar

A última ferramenta não sabe nada do seu problema nem dos seus tipos: lê o código como texto e faz duas coisas diferentes com dois comandos. O [`ruff`](https://docs.astral.sh/ruff/) é um único programa que cobre os dois papéis:

- **`ruff check`** é o *linter* (em português, “analisador estático”): procura erros e más práticas conhecidas, como uma importação que não se usa ou um valor padrão que é compartilhado entre chamadas. [Cada achado tem um código](https://docs.astral.sh/ruff/linter/) de uma ou duas letras e três dígitos (`F401`, `E711`).
- **`ruff format`** é o *formatador*: reescreve o código com um formato único (espaços, quebras de linha, aspas, onde se parte uma linha longa). [Imita o do `Black`](https://docs.astral.sh/ruff/formatter/), o padrão da comunidade, de modo que o seu código se parece com o de qualquer outro projeto. O melhor é o que ele **tira de você**: a discussão sobre estilo se decide uma vez e a máquina a executa.

Veja ambos sobre um arquivo com defeitos reais. Está desarrumado de propósito: é o único do curso que está.

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

O programa roda (imprime as duas listas), e tem pelo menos cinco coisas erradas. Como você está fora do projeto e não há `pyproject.toml` dizendo que regras aplicar, você as passa com `--select`; `--output-format concise` pede uma linha por achado:

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

A segunda chamada imprimiu `['catalogo', 'pagos']`: o defeito da Lição 3 em ação. O valor padrão `lista=[]` é **compartilhado** entre chamadas, e o `ruff` o vê de antemão como `B006`. São sete achados, cada um com `archivo:línea:columna: CÓDIGO descripción` (arquivo, linha, coluna, código, descrição). A letra do código é o nome da coleção de regras, que você escolhe com `select`:

| Letra | O que vigia | Um exemplo de cima |
|---|---|---|
| `E` | Estilo ([pycodestyle](https://peps.python.org/pep-0008/), o guia oficial) | `E401` várias importações em uma linha; `E711` comparar com `None` usando `==` |
| `F` | Erros lógicos simples ([Pyflakes](https://docs.astral.sh/ruff/rules/unused-import/)) | `F401` três importações sem uso |
| `I` | A ordem das importações | `I001` bloco desordenado |
| `B` | Armadilhas conhecidas ([bugbear](https://docs.astral.sh/ruff/rules/mutable-argument-default/)) | `B006` valor padrão mutável |
| `UP` | Modernizar a sintaxe para a sua versão do Python | (nenhum neste arquivo) |

A documentação [recomenda começar com poucas regras](https://docs.astral.sh/ruff/linter/) (`E` e `F`), adicionar grupos um de cada vez e escolher com `select` para que o conjunto seja explícito e não mude sozinho ao atualizar. Essas cinco são o conjunto do `revisor`.

A marca `[*]` diz que o `ruff` sabe corrigir o achado sozinho; o resumo conta cinco achados com correção, e outros dois têm correções *inseguras* que poderiam mudar o que o programa faz (como a de `B006`). O `ruff` só aplica as seguras, a menos que você peça. `ruff format --check` é a pergunta “está formatado?”: respondeu que não, e mostra o que mudaria. Para ver o que cada um faria sem tocar no arquivo existe `--diff`:

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

O primeiro mostra a correção segura: apagar as duas linhas de importações, que sobram inteiras. Repare que diz `Would fix 4 errors`, não cinco: os cinco achados com `[*]` estão nas mesmas duas linhas, e as suas correções se atropelam. Ao aplicar as de `F401`, que apagam as importações sem uso, a linha desaparece e outra das correções (separar `os` e `sys`, ou ordená-los) já não tem nada a fazer. Por isso convém olhar o `--diff` e não só contar marcas. O `== None` e o valor padrão ficam, porque as suas correções são inseguras: cabe a você decidir. O segundo mostra o que o formatador faria: duas linhas em branco entre funções, a convenção. O que o `ruff format` faz é mecânico e não muda o que o programa faz.

#### 8.5.1 No projeto: a configuração

As regras são escritas uma vez no `pyproject.toml`, como as do `pytest` e do `mypy`, e então `ruff check` e `ruff format` não precisam de argumentos:

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`target-version` diz para qual versão do Python você escreve: a 3.12 do Mint, a mais velha que o curso admite. Importa: o `ruff` decide com ela o que é “biblioteca padrão” ao ordenar importações (`tomllib` é desde a 3.11) e que sintaxe moderna sugerir. Neste projeto, se você não a escrevesse, [o `ruff` a tomaria](https://docs.astral.sh/ruff/settings/#target-version) de `requires-python = ">=3.12"`, em `[project]`, que diz o mesmo; escreve-se para que fique à vista junto das regras. Sem nenhuma das duas, o `ruff` supõe a 3.10, e com ela `tomllib` já não seria biblioteca padrão e acabaria no bloco de pacotes de terceiros. O `select` vai na subseção `[tool.ruff.lint]`, [como o `ruff` documenta](https://docs.astral.sh/ruff/configuration/).

```text
$ cd fig08_15
$ ruff check
All checks passed!
$ ruff format --check
11 files already formatted
```

`All checks passed!` e todos os arquivos já formatados. Se você roda `ruff check` sobre código que ainda não passou pelo formatador, é comum que ele reclame de `E501` (linha com mais de 88 caracteres), e que um `ruff format` resolva quase todas, porque reparte em várias linhas as chamadas e as listas longas. Por isso a ordem é sempre a mesma: **primeiro `ruff format`, depois `ruff check`**. E se uma regra do linter lhe parece excessiva, a resposta honesta é discuti-la e tirá-la do `select` com uma razão, não escondê-la com um comentário em cada linha.

### 8.6 O projeto completo

A foto do projeto ao terminar a lição é o pacote da Lição 7 com `version = "0.7.0"`, a pasta `tests/` (quatro arquivos que você já viu) e três seções novas de configuração. O `pyproject.toml` completo:

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

O novo em relação à Lição 7 é a versão e as três últimas seções. Os demais arquivos **não mudam**; repetem-se aqui só para que o projeto esteja completo e você possa comparar com os seus se algo não coincidir:

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

Reinstale-o com `pip install -e .` para que o ambiente veja a versão nova. A partir de hoje, toda vez que você terminar uma mudança, repete este ritual, nesta ordem:

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

## O erro que você vai ver

### `ModuleNotFoundError: No module named 'revisor'`

É o primeiro com que tropeça quem abre o projeto em um ambiente novo. Os testes importam o pacote (`from revisor.modelo import clasificar`) e o pacote **não está instalado** no ambiente que roda o `pytest`. O relatório não começa com pontos, e sim com um bloco `ERRORS`: o erro ocorreu ao *coletar* o arquivo, antes de executar qualquer coisa. Versão reduzida (os caminhos longos do `importlib` vão como `...`):

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

Lê-se de baixo para cima: a última linha `E` é a causa, a anterior diz que linha a provocou (`from revisor.cli import main`, linha 6 de `test_cli.py`) e os passos intermediários, do `importlib`, não lhe servem. O resumo conta quatro erros, um por arquivo, e não diz `0 passed`. A correção é `pip install -e .` a partir da pasta que tem o `pyproject.toml`: o projeto está bem, falta instalá-lo.

### `fixture 'tmp_pth' not found`

É o que acontece se você escreve errado o nome de uma fixture, `tmp_pth` em vez de `tmp_path`. Como o `pytest` a procura pelo nome do parâmetro, um nome que não existe é um erro do `pytest` e não do Python:

```text
___________________________ ERROR at setup of test_x ___________________________
file tests/test_x.py, line 4
  def test_x(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: anyio_backend, anyio_backend_name, ... tmp_path, ...
>       use 'pytest --fixtures [testpath]' for help on them.
```

Olhe o cabeçalho: `ERROR at setup`, não `FAILED`. O teste nem chegou a ser executado; falhou ao *se preparar*. A mensagem oferece as fixtures disponíveis (aqui reduzidas), e ali está `tmp_path`. (As `anyio_*` aparecem porque o `httpx`, que você instalou na Lição 1, traz um complemento do `pytest`; não afetam você.)

### O teste vermelho que aplica o patch no lugar errado

O mais educativo, porque não é de sintaxe e sim de raciocínio. Em `tests/test_cli.py`, mude o destino do `monkeypatch` de `revisor.cli.revisar_todos` para `revisor.revision.revisar_todos`, onde a função é definida, e rode os testes. Relatório real, reduzido:

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

A linha `E` diz `assert 1 == 0` e, embaixo, que `main` devolveu `1`. A seção `Captured stdout call` (o que o código imprimiu durante o teste, que o `pytest` guarda e mostra só se falhar) traz a pista decisiva: **`reportes` aparece fora do ar, com os dados de sempre**. O patch não teve efeito, porque o `cli` continuou usando a sua própria cópia de `revisar_todos`. A moral da história é a da documentação: aplique o patch no nome **onde ele é usado**. Desfaça a mudança antes de seguir.

## O que se faz errado

**Escrever um teste que não pode falhar.** `assert clasificar(200, 142) is not None` passa sempre, porque `clasificar` nunca devolve `None`. É a razão do costume de 8.1.2. Custo: uma rede com um buraco do tamanho do teste e a falsa tranquilidade do verde.

**Deixar que o teste calcule a resposta com a fórmula do código.** `assert formatear_tiempo(2300) == f"{2300 / 1000:.1f}s"` repete a implementação: se a fórmula está errada, o teste a copia. O esperado se escreve à mão, como dado: `"2.3s"`.

**Copiar a saída atual como valor esperado sem olhá-la.** Você roda o código, vê que devolve `'ARRIBA'` e o escreve no teste porque “é o que sai”. Se estava errado, você converteu o defeito na especificação, e o teste o defende. O esperado sai da regra, nunca do que o código faz hoje.

**Olhar só o código de saída.** É 8.1.3: um `0` não conta quantos testes rodaram.

**Aplicar o patch onde a função é definida e não onde é usada**, ou aplicar patch demais, de modo que o teste já não exercita código real. Se tudo o que há dentro de `main` é falso, a única coisa que você testa é o falso.

**Calar o `mypy` com `# type: ignore` ou com `Any` para que “passe”.** Você deixa o defeito e tira o aviso. Se há uma exceção real, ela leva um comentário com o porquê.

**Anotar pela metade.** Uma função com anotações em dois parâmetros e sem elas no terceiro não fica fora da verificação: o `mypy` sim verifica o seu corpo, mas o parâmetro sem anotação vale `Any`, “qualquer coisa”, e tudo o que você fizer com ele passa sem perguntas. Com `strict = true`, além disso, o `mypy` o assinala como `[no-untyped-def]`. Ou tudo ou nada; neste curso, tudo.

**Brigar com o formatador.** Reformatar à mão o que o `ruff format` já decidiu, ou desativar uma regra por preguiça de entendê-la.

**Testes que dependem da ordem, do disco ou da rede.** Um teste que lê o `servicios.toml` real, ou que só passa se outro rodou antes, falha em outra máquina sem explicação. Com `tmp_path` e `monkeypatch`, cada teste basta a si mesmo.

## Exercícios

### Exercício 1 — Quebre, veja o vermelho, conserte

Em `src/revisor/modelo.py`, troque o `>=` de `if tiempo_ms is not None and tiempo_ms >= umbral_ms:` por `>`. Antes de rodar, **preveja**: quantos testes ficarão vermelhos e qual? Rode `pytest -q`. Depois rode `python -m revisor` e compare a tabela com a de sempre. Desfaça a mudança e rode de novo. Anote no seu diário de bordo o número do relatório antes e depois, e o que a tabela lhe ensinou.

### Exercício 2 — Um teste novo para o código de saída 2

`main` devolve `2` quando o arquivo de configuração não existe. Escreva em `tests/test_cli.py` um teste que comprove isso: chame `main(["--config", ...])` com um caminho dentro de `tmp_path` para um arquivo que você não criou, e afirme que o resultado é `2`. Antes de deixá-lo, **comprove que ele pode falhar**: como você o poria em vermelho de propósito? O relatório deve dizer `22 passed`. Apague-o ao terminar (a Lição 9 parte de 21) e comprove que volta a dizer 21.

### Exercício 3 — Que o `mypy` leve você até quem chama

Em `src/revisor/formato.py`, troque `def formatear_tiempo(tiempo_ms: int | None) -> str:` por `def formatear_tiempo(tiempo_ms: int) -> str:`, sem mexer em mais nada. Rode o `mypy`. Quantos erros saem e em que arquivos? Por que há um em `tests/test_formato.py`, que você não tocou? Desfaça a mudança.

### Exercício 4 — O teste que falta

Há uma mudança de um único caractere em `formatear_tiempo` que os 21 testes **não** detectam. A fronteira dos mil milissegundos tem o seu caso em `clasificar`, mas esta é a mesma fronteira. Troque `if tiempo_ms < 1000:` por `if tiempo_ms <= 1000:` e rode `pytest -q`: verde ou vermelho? Se for verde, escreva o caso que falta na tabela de `tests/test_formato.py`, comprove que agora fica vermelho, desfaça a mudança no código e **apague** o caso novo para que o projeto volte a 21, o número com que a Lição 9 começa.

## Soluções

### Solução 1

A previsão correta é **um** teste vermelho: `test_clasificar[200-1000-Estado.LENTO]`. Nenhum outro toca o 1000 exato. Relatório real, reduzido:

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

`1 failed, 20 passed` soma 21: o total continua ali. E a tabela de `python -m revisor`, com o defeito posto, **sai idêntica** à de sempre: olhar a tabela não encontra o defeito, o teste sim. Ao desfazer a mudança, o relatório volta a `21 passed`.

### Solução 2

```python
def test_sin_archivo_de_configuracion_sale_con_2(tmp_path: Path) -> None:
    inexistente = tmp_path / "no-existe.toml"
    assert main(["--config", str(inexistente)]) == 2
```

Para vê-lo em vermelho, troque o `2` por um `0` e rode: deve falhar com `assert 2 == 0`, o que demonstra que ele olha o código de saída real. Com a versão boa, `22 passed`. Ao apagá-lo deve voltar `21 passed`; se não, algo ficou no arquivo.

### Solução 3

Saem **três** erros, em dois arquivos (`Found 3 errors in 2 files (checked 11 source files)`):

```text
src/revisor/formato.py:22: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
src/revisor/formato.py:46: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
tests/test_formato.py:17: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
```

O primeiro está em `linea`, que lhe passa `resultado.tiempo_ms`, um `int | None`. O segundo está em `resumen`, que lhe passa a média, que também pode ser `None` quando nenhum serviço respondeu. O terceiro é o teste: o seu parâmetro `tiempo_ms` é `int | None` (a tabela inclui o `None`) e chama a função com ele. Os três são o mesmo problema visto de três lugares, e o da média talvez você nem lembrasse: o `mypy` mostrou sem que você procurasse. Ao desfazer a mudança volta `Success: no issues found in 11 source files`.

### Solução 4

A mudança **passa em verde** (`21 passed`): nenhuma das quatro linhas usa 1000 (há um `None`, um 87, um 999 e um 2300). Com `<=`, o 1000 sairia como `1000ms` em vez de `1.0s` e ninguém notaria. O caso que falta:

```python
        (1000, "1.0s"),
```

Com ele, a mutação fica vermelha (`test_formatear_tiempo[1000-1.0s]` diz qual). Em um projeto seu você o conservaria sem pensar; aqui você o apaga só por uma razão de calendário: a Lição 9 compara a sua contagem com 21. O que esta solução quer deixar para você é a pergunta: **uma suíte verde não diz que o código está certo, diz que as perguntas que você lhe fez têm resposta**. Reverta a correção e comprove que fica vermelho: esse é o método.

## Como sei que consegui

- [ ] `pytest -q`, a partir da raiz do projeto, termina com `21 passed` (o número, não só o verde).
- [ ] `mypy` termina com `Success: no issues found in 11 source files`.
- [ ] `ruff check` diz `All checks passed!` e `ruff format --check` diz que os 11 arquivos já estão formatados.
- [ ] Você trocou `>=` por `>` em `clasificar`, `pytest -q` disse `1 failed, 20 passed`, e ao desfazer voltou a `21 passed`.
- [ ] Você consegue explicar por que um `echo $?` igual a `0` não diz quantos testes rodaram, e o que faz `--collect-only`.
- [ ] Você consegue explicar por que `monkeypatch.setattr` aponta para `revisor.cli.revisar_todos` e não para `revisor.revision.revisar_todos`.
- [ ] O `pyproject.toml` tem as três seções (`[tool.pytest.ini_options]`, `[tool.ruff]` com o seu `[tool.ruff.lint]` e `[tool.mypy]`) e `version = "0.7.0"`.

## Resumo

Responda sem olhar a lição:

1. Como o `pytest` reconhece o que é um teste, e o que acontece com uma função chamada `prueba_algo`?
2. Por que se vê um teste em vermelho antes de aceitá-lo em verde?
3. Que códigos de saída o `pytest` tem para “tudo passou”, “algum falhou” e “nenhum foi coletado”? Por que a contagem se lê do relatório?
4. O que o `@pytest.mark.parametrize` poupa de trabalho e como você sabe qual linha falhou?
5. O que é uma fixture e o que entregam `tmp_path` e `monkeypatch`?
6. Por que `monkeypatch.setattr` aponta para `revisor.cli.revisar_todos`?
7. O que significa que a tipagem do Python seja gradual e o que muda com `strict = true`?
8. Que diferença há entre `ruff check` e `ruff format`, e por que se roda primeiro o segundo?

## Para ler mais

- [pytest, “Get Started”](https://docs.pytest.org/en/stable/getting-started.html) — o guia oficial, com as regras de descoberta e a leitura do relatório; em inglês, como quase toda a documentação do ecossistema. Consultado em 7 de outubro de 2026.
- [mypy, “Getting started”](https://mypy.readthedocs.io/en/stable/getting_started.html) — o que são a tipagem dinâmica e a estática, e como introduzir tipos em código existente. Consultado em 7 de outubro de 2026.
- [Ruff, “The Ruff Linter”](https://docs.astral.sh/ruff/linter/) — como se escolhem regras, o que significam os códigos e o que é uma correção segura. Consultado em 7 de outubro de 2026.
- [PEP 484, “Type Hints”](https://peps.python.org/pep-0484/) — o documento que introduziu as anotações de tipo e esclarece que não são verificadas ao executar. Consultado em 7 de outubro de 2026.
