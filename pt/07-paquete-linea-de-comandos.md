# Lição 7 — Um pacote com linha de comando

**Tempo:** 90 min

**O que você constrói:** o `revisor` como um pacote de verdade: uma pasta com estrutura, um arquivo `pyproject.toml` que o descreve, um comando com opções (`--config`, `--formato`, `--version`) e um código de saída que outros programas podem ler

**O que você aprende:** a estrutura de um pacote com layout `src/` (`__init__.py`, `__main__.py`, importações absolutas); `python -m revisor`; `pyproject.toml` (`[build-system]`, `[project]`, `[project.scripts]`); `argparse`; os códigos de saída; a saída padrão em contraste com a saída de erro; e a instalação editável com `pip install -e .`

**De onde você vem.** Você traz o projeto da [Lição 6](06-errores-archivos-datos.md): um `revisor` que já não leva os serviços escritos no código, mas os lê de `servicios.toml`, os valida e reclama em espanhol quando o arquivo não presta. São seis arquivos em uma única pasta (`revisor.py`, `modelo.py`, `revision.py`, `formato.py`, `configuracion.py` e o script de apoio `ver_json.py`) mais o `servicios.toml`. Funciona, com três limitações que hoje se notam. Primeira: **só funciona se você estiver parado nessa pasta** e escrever `python revisor.py`; os módulos se encontram porque estão juntos, e o nome do arquivo de configuração está escrito em uma constante do programa. Segunda: **para ver o relatório em JSON é preciso executar outro script**, porque o programa não tem como você dizer o que quer. Terceira: **o programa não avisa ninguém se encontrou problemas**: termina igualmente bem quando tudo está no ar e quando metade está fora do ar, e um script, um agendador de tarefas ou um sistema de integração contínua não conseguem saber a diferença. Você trabalha na sua pasta `~/curso-python/revisor/`, com o ambiente virtual da [Lição 1](01-instalacion.md) ativado.

**O que esta lição não faz.** Ela não consulta nenhuma rede (os dados continuam sendo os simulados da lição 5; a rede chega na [Lição 9](09-http-y-asyncio.md)) e não escreve testes (isso é a [Lição 8](08-pruebas-tipos-calidad.md)). O que se resolve hoje é **como um conjunto de arquivos se converte em um programa que se instala, se executa com um comando e se comunica com o resto do sistema**.

**Sobre as execuções.** Todas as saídas foram obtidas com Python 3.14.8 e repetidas com Python 3.12.12, o que vem com o Linux Mint. São idênticas com uma única exceção, que é assinalada onde ocorre: o texto de um erro do `argparse`. Os caminhos que você verá nas mensagens começam em `/home/tu_usuario/curso-python/`; o seu começará com a sua própria pasta. O projeto completo está em [`programas/07-paquete-linea-de-comandos/fig07_01/`](https://github.com/HabilMX/curso-python/tree/main/programas/07-paquete-linea-de-comandos/fig07_01), no repositório do curso; as duas figuras soltas (`fig07_02.py` e `fig07_03.py`) são executadas a partir da pasta da lição.

## Ao terminar, você vai conseguir

- Explicar a diferença entre um módulo e um pacote, e por que o código vive em `src/revisor/` e não ao lado do `pyproject.toml`.
- Executar um pacote com `python -m revisor` e explicar o que faz o `__main__.py`.
- Ler e escrever um `pyproject.toml` com as suas três tabelas: `[build-system]`, `[project]` e `[project.scripts]`.
- Definir opções de linha de comando com `argparse`: uma com valor padrão, uma com opções fechadas e uma `--version`.
- Fazer um programa terminar com um código de saída que diga o que aconteceu (0, 1 ou 2), e lê-lo no terminal com `echo $?`.
- Mandar as mensagens de erro para a saída de erro e o relatório para a saída padrão, e comprovar a diferença redirecionando uma das duas.
- Instalar o pacote em modo editável com `pip install -e .` e explicar por que uma mudança no código é notada sem reinstalar, mas uma mudança no `pyproject.toml` não.

## O porquê antes do como

Pense em como você usaria o `revisor` na vida real. Alguém da operação o executa toda manhã a partir de um agendador de tarefas, para saber se algum serviço amanheceu fora do ar. Esse agendador de tarefas não olha a tabela que é impressa: é um programa, e não sabe ler uma tabela. A única coisa que ele pode perguntar a outro programa ao terminar é uma só: **“você terminou bem ou mal?”**. No Linux, essa resposta é um número, o *código de saída*, e a convenção é que 0 significa “tudo certo” e qualquer outro número significa “algo aconteceu”. Se o `revisor` não sabe responder a essa pergunta, a automação fica cega. E se, além disso, a pessoa quer o relatório em JSON para passá-lo a outro sistema, precisa poder pedi-lo com uma opção, não editando um arquivo.

Um programa que é executado assim, com opções, com um código de saída e de qualquer pasta, é um **programa de linha de comando**. Para sê-lo, é preciso estrutura: não dá para fazê-lo com seis arquivos soltos. O Python tem uma forma padrão de montá-lo, que consiste em três peças: um **pacote** (uma pasta que o Python reconhece como uma unidade importável), um arquivo **`pyproject.toml`** que descreve o projeto para as ferramentas, e um **comando de instalação** que deixa tudo disponível no seu ambiente. Essas são as três seções da lição, mais a que fecha: como um programa se comunica com quem o chamou, com códigos de saída e com dois canais de texto diferentes.

A lição é mecânica, e isso é um aviso justo: há muitos nomes de arquivo e muitas regras que se aprendem fazendo, não lendo. O melhor modo de acompanhá-la é ter o terminal aberto em `~/curso-python/revisor/` e ir executando cada passo. No final, ao executar `python -m revisor --formato json`, você verá na tela o relatório em JSON, e ao perguntar ao terminal como o programa terminou com `echo $?`, você verá um `1`, porque entre os serviços há um lento e um fora do ar. Há muitas coisas escondidas nessa frase (uma opção, um formato, um número que sai no final), e a lição as desenrola uma por uma.

## Os conceitos

### 7.1 Um pacote com layout `src/`

#### 7.1.1 Módulo, pacote e como se encontram

Você já sabe o que é um **módulo**: um arquivo `.py` cujo conteúdo outro arquivo pode importar (lição 3). Até agora o seu `revisor` tem cinco, e eles são importados com instruções como `from modelo import Servicio`. Isso funciona por uma razão muito concreta que nunca tinha sido nomeada: quando você executa `python revisor.py`, o Python procura os módulos que você importa **na pasta onde está esse arquivo**, e também nas pastas da biblioteca padrão e nas do ambiente virtual onde o `pip` instala coisas (uma pasta chamada `site-packages`). Essa lista de lugares é consultada em ordem, e é ela que decide se um `import` encontra o que procura ou falha com `ModuleNotFoundError`. Enquanto todos os seus arquivos estiverem juntos, tudo é encontrado. Assim que algo é movido ou executado de outro lugar, começa a falhar.

Um **pacote** é uma pasta de módulos que o Python trata como uma unidade com nome. Se há uma pasta `revisor/` com um arquivo `__init__.py` dentro e outros módulos, de qualquer parte se pode escrever `from revisor.modelo import Servicio`, que se lê “do pacote `revisor`, o módulo `modelo`, importe `Servicio`”. O ponto separa os níveis. Esse tipo de importação, que começa sempre pelo nome do pacote, chama-se **importação absoluta**, e é a única que este curso usa: é a mais clara de ler, porque qualquer pessoa que vê a linha sabe de onde vem o nome sem precisar adivinhar em que pasta está o arquivo. A [seção do tutorial sobre pacotes](https://docs.python.org/pt-br/3/tutorial/modules.html#packages) explica o mecanismo com mais detalhe.

#### 7.1.2 Por que `src/`

O que resta decidir é **onde** colocar a pasta do pacote. A forma mais óbvia é ao lado do `pyproject.toml`, na raiz do projeto. Mas há uma forma melhor, que é a que usa o guia oficial de empacotamento do Python: colocá-la em uma subpasta chamada `src/`. Este é o layout que você terá ao terminar a lição:

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

O nome `revisor` aparece duas vezes, e não é descuido: a de fora é a pasta do **projeto** (o que você baixa, o que contém os arquivos de configuração, os testes que virão na lição 8), e a de dentro é o **pacote** (o que o Python importa). A vantagem do `src/` é que ele **obriga você a instalar o pacote antes de usá-lo**. Se o pacote estivesse na raiz, `python -m revisor` a partir dessa pasta o encontraria sem instalá-lo, porque a pasta atual está sempre na lista de lugares onde o Python procura. E isso esconde erros: você poderia ter um pacote que funciona na sua pasta mas que, instalado, fica sem alguns arquivos, e você não perceberia até outra pessoa usá-lo. Com `src/`, a pasta do pacote não está onde o Python procura por padrão, de modo que o que você executa é sempre o que você instalou. O [guia de empacotamento](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) discute as duas formas e seus compromissos; este curso adota a do `src/` sem reservas.

#### 7.1.3 `__init__.py`, `__main__.py` e `python -m`

O pacote leva dois arquivos que não são parte do seu programa, mas parte do mecanismo. O primeiro é `__init__.py`. A sua simples presença diz ao Python “esta pasta é um pacote”. Pode estar vazio; aqui ele leva uma frase entre aspas triplas que descreve o pacote, o que se chama de string de documentação (*docstring*):

```python
# fig07_01/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

O segundo é `__main__.py`, que é o que é executado quando alguém escreve `python -m revisor`. A opção `-m` (de *módulo*) diz ao Python “não execute um arquivo; execute este pacote como um programa”. Para um pacote, isso significa executar o seu `__main__.py`. O arquivo inteiro é este:

```python
# fig07_01/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

A primeira linha importa a função `main` do módulo `cli` (que você verá em 7.3). A segunda faz algo que parece uma formalidade, mas é o centro da lição: `raise SystemExit(main())`. Você já sabe o que é `raise` (lição 6): lança uma exceção. `SystemExit` é uma exceção especial que o Python já traz, e que **ninguém captura de propósito**: quando ela sobe até o topo, em vez de imprimir um relatório de erro, o Python encerra o programa, e o valor com que você a constrói se torna o **código de saída**. Então `main()` é executada, **devolve um número**, e esse número se torna o código com que o programa termina. Veremos isso em detalhe em 7.4; por ora basta saber que o `-m` procura esta peça. A [documentação do `__main__`](https://docs.python.org/pt-br/3/library/__main__.html#main-py-in-python-packages) e a da [opção `-m`](https://docs.python.org/pt-br/3/using/cmdline.html#cmdoption-m) contam isso em detalhe.

#### 7.1.4 Mover os arquivos

Os quatro módulos que você já tinha (`modelo.py`, `revision.py`, `formato.py`, `configuracion.py`) passam para o pacote **sem mudar uma única função**: as assinaturas são as mesmas da lição 6. A única coisa que muda são as suas importações, que deixam de ser `from modelo import ...` para se tornar `from revisor.modelo import ...`. O `revisor.py` plano se torna `cli.py` e é reescrito em 7.3. E o script `ver_json.py` desaparece, porque `--formato json` o substitui. Da pasta do projeto, com o ambiente ativado, estes são os passos. Eles usam três comandos do terminal que você não tinha visto, e convém saber o que cada um faz antes de escrevê-lo:

- **`mkdir -p src/revisor`** cria a pasta `src` e, dentro, `revisor`, de uma vez. Sem `-p`, o `mkdir` se recusaria a criar `revisor` porque `src` ainda não existe; com `-p` (*parents*, “os pais”) ele cria também as pastas intermediárias que faltem, e não reclama se elas já existiam.
- **`mv origen destino`** (*move*; origem e destino) **move** arquivos, ou muda o nome deles. `mv modelo.py revision.py formato.py configuracion.py src/revisor/` move os quatro arquivos para essa pasta (a barra final diz que o destino é uma pasta). `mv revisor.py src/revisor/cli.py` move e renomeia ao mesmo tempo. Se no destino já existe um arquivo com esse nome, o `mv` o substitui sem perguntar.
- **`rm archivo`** (*remove*; archivo = arquivo) **apaga** um arquivo, e não o manda para a lixeira: não se recupera. Aqui apaga `ver_json.py`, que já não é necessário, e no final as cópias `.bak` que o `sed` deixa. O `*` de `src/revisor/*.bak` quer dizer “todos os arquivos dessa pasta que terminam em `.bak`”; antes de um `rm` com `*`, um `ls` com o mesmo padrão mostra exatamente o que vai ser apagado.

Estes são os passos:

```bash
mkdir -p src/revisor
mv modelo.py revision.py formato.py configuracion.py src/revisor/
mv revisor.py src/revisor/cli.py
rm ver_json.py
sed -i.bak -E 's/^from (modelo|formato|configuracion|revision) import/from revisor.\1 import/' src/revisor/*.py
rm src/revisor/*.bak
```

O comando `sed` é um editor de texto sem janela: procura em cada arquivo as linhas que começam com `from modelo import` (ou `formato`, `configuracion`, `revision`) e antepõe a elas `revisor.`. Os parâmetros `-i.bak` pedem que ele guarde uma cópia de segurança de cada arquivo com a terminação `.bak`, que é apagada em seguida. Se você preferir não usá-lo, edite à mão as linhas que dizem `from modelo import`, e verifique com isto o que deve ficar em cada arquivo:

| Arquivo | Importações ao terminar |
|---|---|
| `revision.py` | `from revisor.modelo import Resultado, Servicio, clasificar` |
| `formato.py` | `import json` e `from revisor.modelo import Estado, Resultado` |
| `configuracion.py` | `from revisor.modelo import Servicio, nombres_repetidos` (mais as da biblioteca padrão, sem mudança) |
| `modelo.py` | não importa nada do seu projeto |

O `cli.py` é reescrito por completo em 7.3. Você ainda não pode executar nada: falta criar os três arquivos novos (`__init__.py`, `__main__.py` e `pyproject.toml`) e escrever o `cli.py`. Continue lendo.

### 7.2 `pyproject.toml`: o projeto descrito para as ferramentas

Um pacote, por si só, é apenas uma pasta. Para que o `pip` saiba instalá-lo é preciso descrevê-lo: como se chama, que versão é, que versão do Python ele precisa, que comando cria. Isso se escreve em um arquivo chamado `pyproject.toml` na raiz do projeto. É um arquivo TOML, o formato que você aprendeu a ler na lição 6, e é o mecanismo oficial: o [guia de empacotamento](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) o descreve como o lugar onde vão os metadados de um projeto Python. Este é o do `revisor`:

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

Tem três tabelas, e cada uma responde a uma pergunta diferente.

**`[build-system]`: com o que se constrói?** Instalar um pacote, mesmo que seja seu e local, implica um passo de construção: ler o `pyproject.toml`, reunir os arquivos, produzir algo instalável. Esse trabalho é feito por uma ferramenta chamada *backend de construção*, e o projeto deve dizer qual quer. `requires` lista o que é preciso baixar para construir, e `build-backend` nomeia o backend. Aqui se usa o `hatchling`, o que o guia oficial de empacotamento usa, e se pede a versão 1.27 ou posterior (`>=1.27`). Há um detalhe que convém saber de antemão: na primeira vez que você instalar o pacote, o `pip` **baixa o `hatchling` da internet** para um ambiente temporário para construí-lo. É uma dependência de *construção*, não do seu programa: o `revisor` continua sem depender de nada para funcionar. Mas sem conexão, a instalação falharia nesse passo. As regras desta tabela estão na [PEP 518](https://peps.python.org/pep-0518/) e a interface dos backends na [PEP 517](https://peps.python.org/pep-0517/); o `hatchling` tem a sua [própria documentação](https://hatch.pypa.io/latest/).

**`[project]`: o que é este projeto?** Aqui vão os dados que qualquer pessoa esperaria na ficha de um pacote. `name` é o nome com que ele é instalado. `version` é a versão: o curso a sobe um passo em cada lição a partir de hoje (`0.6.0` é a de hoje, e a lição 11 a deixa em `1.0.0`). `description` é uma frase. `requires-python = ">=3.12"` diz que versões do Python podem executá-lo: o `pip` se recusará a instalá-lo em um Python mais velho, em vez de deixá-lo falhar com um `SyntaxError` incompreensível mais tarde. E `dependencies = []` é a lista de pacotes de terceiros de que o seu programa precisa para rodar: hoje, nenhum, e por isso está vazia. Na lição 9 aparecerá uma. O padrão que define estes campos é a [PEP 621](https://peps.python.org/pep-0621/).

**`[project.scripts]`: que comando cria?** Esta é a tabela que converte um pacote em uma ferramenta. A linha `revisor = "revisor.cli:main"` diz: “ao instalar, crie no ambiente um comando chamado `revisor`, e quando alguém o executar, que ele chame a função `main` do módulo `revisor.cli`”. A forma `paquete.modulo:función` é uma convenção que a [especificação de pontos de entrada](https://packaging.python.org/en/latest/specifications/entry-points/) fixa. Quando você o instalar, o comando `revisor` ficará junto do `python` do seu ambiente, e funcionará igual a `python -m revisor`. E de novo: o valor que `main` devolve se torna o código de saída do comando.

Copie o conteúdo para `pyproject.toml`, junto do `servicios.toml`, na pasta do projeto. Você ainda não pode instalar: falta o centro do programa.

### 7.3 `argparse`: opções de linha de comando

#### 7.3.1 O que um programa recebe do terminal

Quando você escreve `python -m revisor --formato json`, o terminal parte o que você digitou em palavras e as entrega ao programa como uma lista de textos, que o Python guarda em `sys.argv`. Nessa lista, a primeira posição é o nome do programa e as demais são os argumentos: `["fig07_02.py", "--formato", "json"]`. Você poderia percorrê-la, com um `for`, e procurar à mão `--formato` e o texto que vem depois. Mas isso logo se torna tedioso: o que acontece se o usuário escrever a opção duas vezes? Se esquecer o valor? Se escrever `--formato=json` com um sinal de igual? Para não reescrever essas regras em cada programa, a biblioteca padrão traz o módulo `argparse`, que as resolve, gera a ajuda sozinho e valida o que o usuário escreve.

Veja um programa pequeno que demonstra isso, `fig07_02.py`. Ele declara duas opções e as imprime:

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

`argparse.ArgumentParser(description=...)` cria o **analisador** (*parser*): o objeto que saberá interpretar a linha de comando. Cada `add_argument` declara uma opção: o seu nome (com dois hifens na frente, a convenção das opções longas), um valor padrão (`default`) e, na segunda, `choices`, a lista fechada de valores permitidos. Por fim, `parse_args()` lê `sys.argv`, confere tudo e devolve um objeto com um atributo por opção, de modo que `argumentos.formato` tem o valor que o usuário escreveu, ou o padrão se não escreveu nada. Execute-o sem opções, e depois com elas:

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

Sem opções valem os valores padrão. Com elas, valem os que você escreveu, na ordem que quiser. Mas o valioso é o que o `argparse` faz sem que você peça. Primeiro, a ajuda: `-h` e `--help` existem automaticamente.

```text
$ python fig07_02.py --help
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]

Demostración de argparse.

options:
  -h, --help            show this help message and exit
  --config CONFIG
  --formato {tabla,json}
```

Ela é montada a partir do que você declarou: o uso, a descrição, e cada opção com a sua lista de valores. (As palavras fixas do `argparse`, como “options” ou “show this help message and exit”, estão em inglês porque vêm da biblioteca; os textos que você escreve com `help=` e `description=` saem como você os escrever, e é isso que faremos no `revisor`.) Segundo, os erros: se o usuário escreve algo que você não declarou, o `argparse` o rejeita com uma mensagem e encerra o programa:

```text
$ python fig07_02.py --verbose
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]
fig07_02.py: error: unrecognized arguments: --verbose
```

A mensagem diz o que falhou (`unrecognized arguments: --verbose`, “argumentos não reconhecidos”) e repete a linha de uso para que o usuário veja como é a forma correta. Além disso, encerra o programa com um código de saída diferente de zero, concretamente o 2: a [documentação do `argparse`](https://docs.python.org/pt-br/3/library/argparse.html#exiting-methods) estabelece isso para todo erro de uso. Esse 2 será o do `revisor` quando o uso for inválido.

#### 7.3.2 O `cli.py` do `revisor`

Com isso em mãos, o módulo central do pacote se lê sem sobressaltos. O `cli.py` (“*command-line interface*”, a interface de linha de comando) substitui o `revisor.py` plano da lição 6. Tem duas funções: uma que monta o analisador e outra que é o programa. Leia-o inteiro uma vez:

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

**`construir_parser`** devolve o analisador, com três opções. `--config` recebe o caminho do arquivo de configuração; `type=Path` diz ao `argparse` que converta o texto que o usuário escrever em um `Path` (lição 6), e o seu valor padrão é `Path("servicios.toml")`, o mesmo de sempre. `--formato` tem duas opções fechadas, `tabla` e `json`, e por padrão `tabla`: se o usuário escrever qualquer outra coisa, o `argparse` a rejeita antes que o resto de `main` chegue a ver o valor, e não é preciso escrever um `if` para isso. E `--version` usa `action="version"`, uma ação predefinida que imprime um texto e termina: o texto é `revisor` seguido do número da versão, que é **lido dos metadados do pacote instalado** com `importlib.metadata.version("revisor")`. Isso resolve um problema muito comum: o número da versão seria escrito no `pyproject.toml` e outra vez no código, e as duas cópias acabariam por divergir. Assim ele existe em um único lugar, o `pyproject.toml`. O argumento `prog="revisor"` fixa o nome que aparece no uso e nos erros; sem ele, no Python 3.12 apareceria `__main__.py`, o arquivo que é executado com `-m`, e no 3.14 apareceria `python -m revisor`; com `prog`, as duas versões dizem o mesmo.

**`main`** é o programa. Recebe uma lista opcional de argumentos, `argv: list[str] | None = None`, e devolve um inteiro. Se `argv` é `None`, `parse_args(None)` lê a linha de comando real; se você passa uma lista, ele a usa no lugar. Esse parâmetro parece um luxo hoje e é uma peça-chave na lição 8, onde os testes chamarão `main(["--formato", "json"])` sem tocar no terminal. O corpo é o que você já conhece: lê os serviços com `leer_servicios(argumentos.config)`, e se falha com `ErrorDeConfiguracion`, imprime a mensagem e devolve 2. Há duas diferenças em relação à lição 6, e são as duas ideias de 7.4: a mensagem agora sai com `file=sys.stderr` (para a saída de erro, não para a padrão) e devolve 2 em vez de limpar e seguir. Depois verifica os serviços e, conforme `--formato`, imprime a tabela de sempre ou o JSON de `reporte_a_json`. Por fim, decide o código de saída: monta a lista dos resultados cujo estado **não** é `ARRIBA` (o operador `is not` é a negação de `is`, lição 3), e se ela está vazia devolve 0, e se não, 1.

Para que fique explícito, os códigos de saída do `revisor` são estes três, **os do curso inteiro**:

| Código | O que significa |
|---|---|
| `0` | Tudo está `ARRIBA`. |
| `1` | O `revisor` funcionou, mas algum serviço está `LENTO` ou `CAIDO`. |
| `2` | O `revisor` não conseguiu verificar: o uso é inválido (quem decide é o `argparse`) ou a configuração não presta. |

A distinção entre 1 e 2 importa muito. Um `1` é uma resposta: “verifiquei e encontrei problemas”. Um `2` é uma falha do próprio programa: “nem consegui verificar”. Quem automatizar o `revisor` os tratará de forma diferente: com um `1` avisará quem atende os serviços; com um `2` avisará quem mantém o `revisor`.

### 7.4 Códigos de saída, dois canais de texto e a instalação editável

#### 7.4.1 Os códigos de saída

Todo programa que termina deixa para quem o chamou um número inteiro entre 0 e 255. É o **código de saída** (*exit status*). Por convenção do Unix, **0 significa sucesso e qualquer outro número significa algum tipo de falha**. Não há nada de mágico: é um acordo, e todo o ecossistema do terminal o respeita. No terminal (tecnicamente, o interpretador de comandos, que no Linux Mint é o `bash`) você pode perguntar o código do último comando com a variável especial `$?`, que se lê com `echo $?`. O padrão POSIX define como o interpretador de comandos o interpreta na [seção de status de saída](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_08_02), e é o que permite escrever coisas como `revisor && echo "todo bien"` (o `echo` só roda se o `revisor` terminou em 0) ou `revisor || avisar.sh` (o segundo só roda se o primeiro terminou com algo diferente de 0).

Em Python, há duas maneiras de sair com um código. Uma é chamar `sys.exit(codigo)`, que lança `SystemExit`. A outra é o que você já viu em `__main__.py`: lançar `SystemExit` você mesmo. Fazem o mesmo, e a [documentação do `sys.exit`](https://docs.python.org/pt-br/3/library/sys.html#sys.exit) e a da [`SystemExit`](https://docs.python.org/pt-br/3/library/exceptions.html#SystemExit) explicam isso. O que importa é o design: `main` **devolve** o código em vez de chamar `sys.exit` por conta própria, e é o `__main__.py` quem o converte em uma saída. Assim `main` pode ser chamada de outro código (um teste, por exemplo) e devolver o seu número sem matar o processo que a chamou. Quando alguém instala o pacote, o comando `revisor` que `[project.scripts]` cria faz o mesmo: chama `main()` e sai com o que ela devolver.

#### 7.4.2 Dois canais: a saída padrão e a saída de erro

Um programa tem, desde que inicia, dois lugares onde escrever texto. A **saída padrão** (`stdout`) é o canal normal: o que `print` escreve por padrão, e onde vão os resultados. A **saída de erro** (`stderr`) é um canal à parte para os avisos e os erros. No terminal, ambos aparecem na tela, um junto do outro, e por isso parecem a mesma coisa. Mas são canais diferentes, e essa diferença se nota assim que redirecionamos um. Veja `fig07_03.py`, que escreve nos dois:

```python
# fig07_03.py
import sys

print("reporte: 4 servicios revisados")
print("aviso: reportes no respondió", file=sys.stderr)
```

`print(..., file=sys.stderr)` manda o texto para a saída de erro em vez da padrão; `sys` é um módulo da biblioteca padrão que dá acesso a coisas do próprio interpretador, entre elas `sys.stderr` ([documentação](https://docs.python.org/pt-br/3/library/sys.html#sys.stderr)). Execute-o três vezes:

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

A primeira mostra as duas linhas. A segunda usa `>`, que **redireciona a saída padrão** para outro lugar (aqui, `/dev/null`, um arquivo especial do Linux que descarta tudo o que se escreve nele): só sobra o aviso, que viaja pelo outro canal. A terceira usa `2>`, que redireciona o canal número 2, o de erro, e deixa passar o relatório. (Os canais têm número: 0 a entrada, 1 a padrão, 2 a de erro.) Os [redirecionamentos do interpretador de comandos](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_07) são o mecanismo que permite isso.

É isso que torna útil a separação. Quando alguém executa `revisor --formato json > reporte.json`, quer que o arquivo `reporte.json` contenha **somente o JSON**. Se o programa escrevesse uma mensagem de erro pela saída padrão, o arquivo ficaria com texto misturado e deixaria de ser JSON válido. Com o erro em `stderr`, a mensagem sai na tela, o arquivo fica limpo (ou vazio, se o programa não chegou a produzir nada) e o código de saída conta o que aconteceu. Por isso o `cli.py` manda os erros de configuração para `stderr` e o relatório para `stdout`.

Assim se comporta o `revisor` já instalado quando recebe um arquivo de configuração que não existe: a mensagem sai pela saída de erro e o programa termina com o código 2.

```text
$ python -m revisor --config no-existe.toml
error de configuración: no existe el archivo no-existe.toml
$ echo $?
2
```

#### 7.4.3 Instalar em modo editável

Falta o passo que une tudo: instalar o pacote. Antes, veja o que acontece se você tentar executá-lo **sem** instalá-lo. Com o ambiente ativo e parado na pasta do projeto, com os arquivos já no lugar:

```text
$ python -m revisor
/home/tu_usuario/curso-python/.venv/bin/python: No module named revisor
```

A mensagem, `No module named revisor`, é o que se podia esperar de 7.1.2: o Python procurou um módulo chamado `revisor` na pasta atual e no ambiente, e não o encontrou, porque o pacote está dentro de `src/`, uma pasta onde ele não procura. (O caminho do começo é o do `python` do seu ambiente virtual; o seu será o da sua pasta.) Não é um erro do seu código: é o que o `src/` provoca de propósito, e se resolve instalando.

A instalação se faz com o `pip`, já dentro do ambiente, a partir da pasta do projeto (onde está o `pyproject.toml`):

```bash
python -m pip install -e .
```

O ponto final significa “o projeto desta pasta”, e `-e` (“*editable*”) pede uma instalação **editável**. Você verá várias linhas de andamento, que mudam de uma versão do `pip` para outra, e a última diz algo como isto:

```text
Successfully installed revisor-0.6.0
```

Se a mensagem for outra, leia a causa: o mais comum é que você não esteja na pasta que tem o `pyproject.toml`, ou que não tenha conexão para o `pip` baixar o `hatchling`.

O que significa “editável”? Uma instalação normal **copia** os arquivos do pacote para a pasta `site-packages` do ambiente, e a partir daí o pacote instalado e a sua pasta de trabalho são duas coisas diferentes: se você edita o seu código, o instalado não fica sabendo. Uma instalação editável, em contrapartida, deixa no ambiente **um ponteiro para a sua pasta `src/`**, de modo que o Python importa o código de onde ele está, tal como você o escreveu ([PEP 660](https://peps.python.org/pep-0660/); a [documentação do `pip`](https://pip.pypa.io/en/stable/topics/local-project-installs/) explica os dois tipos de instalação local). É o que você quer enquanto desenvolve: muda uma linha, executa e vê a mudança, sem reinstalar. Com o pacote instalado, execute-o; desta vez o código de saída é impresso por `echo $?`:

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

Aí está a tabela de sempre, com o resumo, e o código de saída é **1**, porque entre os quatro serviços há um `LENTO` (`inventario`) e um `CAIDO` (`reportes`). É o comportamento que se queria: o programa funcionou, e avisa que encontrou problemas. A opção `--formato json` produz o relatório para máquinas, que é o contrato que a lição 6 fixou:

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

A opção `--version` lê o número da instalação, e funciona porque você instalou o pacote:

```text
$ python -m revisor --version
revisor 0.6.0
```

E `--help` dá a ajuda, montada com os textos que você escreveu em `help=`:

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

Falta metade do que `[project.scripts]` prometia: o **comando** `revisor`. Ele foi criado ao instalar, junto do `python` do ambiente, e com o ambiente ativo é executado sem `python -m`:

```text
$ revisor --version
revisor 0.6.0
```

O que o `-m` faz é útil porque funciona sempre, mesmo que o comando não estivesse à vista. Mas o comando é como as pessoas usarão o `revisor` na lição 11, instalado com o `pipx`.

Dois esclarecimentos sobre o que “editável” não cobre. A primeira: **ele só acompanha o código, não os metadados**. Se você muda o conteúdo de um módulo, a mudança é vista de imediato. Mas se você muda o `pyproject.toml` (por exemplo, a versão, ou um comando de `[project.scripts]`), o ambiente continua com os metadados da última instalação, até você executar de novo `python -m pip install -e .`. O exercício 4 comprova isso. A segunda: a instalação editável vive no seu **ambiente virtual**, então um ambiente novo (ou recém-criado) não tem o `revisor` até você instalá-lo de novo. É exatamente o comportamento que se quer: nenhuma instalação se mistura com o Python do sistema.

> **Quadro opcional: `uv`.** Existe uma ferramenta mais nova, o `uv`, que faz por conta própria o trabalho do `venv` e do `pip`, e que é mais rápida. Com ela, os mesmos passos se escrevem `uv venv` (cria o ambiente `.venv`) e `uv pip install -e .` (instala o projeto nele). Além disso, ela pode instalar outras versões do Python: `uv python install 3.14` baixa a 3.14 sem tocar no Python do sistema, o que é a forma mais cômoda de testar este curso na versão mais recente além da 3.12 do Mint. O [guia de instalação do `uv`](https://docs.astral.sh/uv/getting-started/installation/) explica como obtê-lo, e a sua documentação sobre [versões do Python](https://docs.astral.sh/uv/concepts/python-versions/) e sobre [a interface `uv pip`](https://docs.astral.sh/uv/pip/) cobre o resto. Este curso não o exige: tudo o que você vê aqui funciona com o `python` e o `pip` que você já tem.

#### 7.4.4 O passo do projeto: montar tudo

Se você foi acompanhando a lição, a sua pasta `~/curso-python/revisor/` já tem o aspecto de 7.1.2. Estes são os passos completos, em ordem, para quem os quiser de uma vez:

1. Crie `src/revisor/` e mova para ela os quatro módulos; renomeie `revisor.py` para `cli.py` e apague `ver_json.py` (7.1.4).
2. Anteponha `revisor.` às importações dos seus módulos (7.1.4).
3. Escreva `src/revisor/__init__.py` e `src/revisor/__main__.py` (7.1.3).
4. Escreva `pyproject.toml` (7.2).
5. Reescreva `src/revisor/cli.py` com `construir_parser` e `main` (7.3.2).
6. Com o ambiente ativado e a partir da pasta do projeto, execute `python -m pip install -e .` (7.4.3).
7. Teste: `python -m revisor`, `python -m revisor --formato json`, `python -m revisor --version`, e depois de cada um, `echo $?`.

Há uma consequência do que você acabou de fazer, que se vê ao executá-lo a partir de **outra pasta**. Suba para a pasta de cima e execute o mesmo comando:

```text
$ python -m revisor
error de configuración: no existe el archivo servicios.toml
```

O pacote foi encontrado (está instalado no ambiente, já não importa onde você esteja), mas o arquivo de configuração não: `--config` vale `servicios.toml` por padrão, um caminho relativo, e a pasta de cima não tem um. A mensagem é a que você já conhece da lição 6, agora na saída de erro e com código de saída 2. A opção `--config` existe justamente para isto: `python -m revisor --config revisor/servicios.toml` funcionaria dali. Onde vive o código e onde vive a configuração são duas perguntas diferentes, e o programa as separa.

## O erro que você vai ver

Esta lição tem dois erros principais, os dois da lista acima, e dois de apoio que aparecem quando algo da montagem é esquecido.

**`No module named revisor`.** Você já viu em 7.4.3: executar `python -m revisor` antes do `pip install -e .`. A causa é o layout `src/`, e a correção é instalar. Se você já instalou e mesmo assim aparece, verifique se tem o ambiente ativado: a mensagem começa com o caminho do `python` que foi usado, e se esse caminho é `/usr/bin/python3` em vez do do seu `.venv`, você está usando o Python do sistema, que não tem o seu pacote.

**O erro de uso do `argparse`.** Peça um formato que não existe:

```text
$ python -m revisor --formato xml
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]
revisor: error: argument --formato: invalid choice: 'xml' (choose from 'tabla', 'json')
$ echo $?
2
```

Leia as duas linhas: a primeira repete o uso, com as opções que existem e os seus valores permitidos entre chaves (`{tabla,json}`); a segunda diz qual argumento falhou e por quê: `invalid choice: 'xml'`, “escolha inválida”. Entre parênteses, a lista das válidas. O código de saída é 2, o que o `argparse` usa sempre para um uso inválido. Um detalhe de versão: este é o texto do Python 3.14, que mostra as opções entre aspas, `('tabla', 'json')`. No Python 3.12 a lista sai sem aspas, `(choose from tabla, json)`. É a única saída da lição que difere entre as duas versões, e é uma mudança no formato do texto; o significado é o mesmo.

**`ModuleNotFoundError: No module named 'modelo'`.** Aparece se você moveu os arquivos mas esqueceu de mudar alguma importação: o pacote é encontrado, mas um dos seus módulos continua importando `modelo` sem mais, e já não existe um `modelo` solto. O relatório, abreviado:

```text
Traceback (most recent call last):
  ...
  File "src/revisor/__main__.py", line 2, in <module>
    from revisor.cli import main
  File "src/revisor/cli.py", line 9, in <module>
    from modelo import Estado
ModuleNotFoundError: No module named 'modelo'
```

Lê-se de baixo para cima, como sempre: a última linha diz qual módulo não foi encontrado (`modelo`); a linha de cima, em que arquivo e em que linha está o `import` que falha (`cli.py`, linha 9); e mais acima, a cadeia de quem importou quem. A correção é `from revisor.modelo import Estado`. (O número da linha dependerá de como você escreveu o seu `cli.py`; o que importa é o nome do módulo da última linha.)

**`importlib.metadata.PackageNotFoundError: No package metadata was found for revisor`.** Aparece se você executa o código sem ter instalado o pacote (por exemplo, adicionando `src` à lista de lugares de busca à mão). Os módulos são encontrados, mas `version("revisor")`, que `construir_parser` executa sempre, procura os **metadados** de uma instalação, e não há nenhuma. É a prova de que o número da versão sai da instalação e não do código: a solução é `python -m pip install -e .`, não esconder a linha. O relatório termina assim:

```text
importlib.metadata.PackageNotFoundError: No package metadata was found for revisor
```

## O que se faz errado

**Importar sem o nome do pacote dentro de um pacote.** `from modelo import Servicio` funciona enquanto os arquivos estão juntos e falha assim que o código é instalado ou executado com `-m`. Dentro do pacote se escreve sempre `from revisor.modelo import Servicio`.

**Consertar as importações modificando `sys.path`.** É uma receita que circula: adicionar à mão a pasta do código à lista de lugares de busca para que os `import` funcionem. Resolve o sintoma e esconde a causa, que é que o pacote não está instalado. Com `pip install -e .` não é preciso.

**Instalar com `pip` fora do ambiente virtual.** Você já sabe por que não funciona no Linux Mint (lição 1): o Python do sistema não traz o `pip` (`No module named pip`), e onde o traz, a proteção da PEP 668 o barra com `externally-managed-environment`. E a saída que às vezes se sugere, forçá-lo, quebra as ferramentas do próprio sistema. Instala-se dentro do `.venv`, sempre.

**Escrever o número da versão em dois lugares.** Um no `pyproject.toml` e outro em uma constante do código: mais cedo ou mais tarde divergem, e a versão que o programa diz já não é a que foi instalada. O número vive no `pyproject.toml`, e o programa o lê com `importlib.metadata`.

**Mandar os erros para a saída padrão.** Mistura o aviso com o relatório, e `revisor --formato json > reporte.json` produz um arquivo que não é JSON válido. Os erros, para `sys.stderr`.

**Terminar sempre com código 0.** Um programa que sai igualmente bem com tudo fora do ar e com tudo no ar não serve a nenhuma automação. O código de saída é parte do contrato do programa, tanto quanto o formato do relatório.

**Inventar códigos de saída sem documentá-los.** Um 3 para isto, um 4 para aquilo, sem que ninguém os conheça, obriga quem automatiza a ler o código-fonte. Há três códigos e estão em uma tabela.

**Ler `sys.argv` à mão.** Funciona até alguém escrever `--formato=json` em vez de `--formato json`, ou esquecer o valor, ou pedir a ajuda. O `argparse` já resolveu esses casos.

**Mudar o `pyproject.toml` e não reinstalar.** A instalação editável acompanha o código, não os metadados. Se você muda a versão ou um comando e o ambiente continua com o anterior, falta um `python -m pip install -e .`.

## Exercícios

### Exercício 1 — O relatório em JSON e o seu código

Com o pacote instalado, execute `python -m revisor --formato json` e, logo em seguida, `echo $?`. Antes de executar, escreva o que você espera ver: quantos serviços há no array `servicios`, que valor tem `tiempo_ms` para `reportes`, e que código de saída. Depois, redirecione a saída para um arquivo com `python -m revisor --formato json > reporte.json` e veja o conteúdo de `reporte.json` com `cat reporte.json` (`cat` imprime na tela o conteúdo de um arquivo). O código de saída mudou ao redirecionar?

### Exercício 2 — Os três códigos

Provoque os três códigos de saída do `revisor`, um por um, e comprove-os com `echo $?`: (a) um `0`, para o qual você precisa de uma configuração em que todos os serviços estejam `ARRIBA` (escreva um arquivo `solo-arriba.toml` com um único serviço, `pagos`, e use-o com `--config`); (b) um `1`, com o `servicios.toml` de sempre; (c) um `2` por configuração inválida, com um `roto.toml` que tenha um serviço sem `nombre`; (d) outro `2`, agora por uso inválido, com um valor de `--formato` que não exista. Para cada caso, escreva primeiro o que você espera ver e em que canal aparece a mensagem.

### Exercício 3 — Onde vive o código e onde vive a configuração

Saia da pasta do projeto com `cd ..` e execute `python -m revisor`. Que mensagem você obtém e que código de saída? Depois execute o mesmo comando passando o caminho da configuração com `--config`. Explique com suas palavras por que o pacote é encontrado a partir de qualquer pasta, mas o arquivo de configuração não.

### Exercício 4 — O que a instalação editável acompanha e o que não acompanha

Com o pacote instalado em modo editável: (a) em `src/revisor/formato.py`, troque a palavra `promedio` do resumo por `media`, e execute o `revisor` sem reinstalar: a mudança se nota? Devolva-a ao que estava. (b) No `pyproject.toml`, mude a versão para `0.6.1`, e execute `python -m revisor --version` sem reinstalar: que versão ele diz? (c) Execute `python -m pip install -e .` e peça a versão de novo. (d) Devolva a versão para `0.6.0` e reinstale. Explique a diferença entre (a) e (b).

## Soluções

### Solução 1

A previsão: o array `servicios` tem **quatro** elementos, um por serviço; o de `reportes` tem `"tiempo_ms": null` (não respondeu, e `None` se escreve `null` em JSON); e o código de saída é **1**, pelo serviço lento e pelo que está fora do ar. A saída de `python -m revisor --formato json` é a que você viu em 7.4.3, e o `echo $?` imprime `1`.

Ao redirecionar, o conteúdo de `reporte.json` é **exatamente o mesmo JSON**: nada do terminal se misturou com ele, porque os avisos (se houvesse) vão por outro canal. E o código de saída **não muda**: redirecionar move o texto, não o resultado. Essa é a propriedade que permite escrever `revisor --formato json > reporte.json || avisar.sh` e que o `||` continue funcionando.

### Solução 2

(a) Com um único serviço que responde bem:

```toml
[[servicios]]
nombre = "pagos"
url = "https://pagos.example"
```

Executado com `python -m revisor --config solo-arriba.toml`:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA      87ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 87ms
```

e `echo $?` imprime **0**. (Observe que o resumo diz “1 servicio” e “0 lentos”: o plural é decidido pela contagem, como na lição 5.)

(b) Com o `servicios.toml` de sempre: a tabela de quatro serviços e o código **1**.

(c) Com um `roto.toml` cujo único serviço não tem `nombre`:

```toml
[[servicios]]
url = "https://pagos.example"
```

Executado com `python -m revisor --config roto.toml`, sai pela **saída de erro** a mensagem `error de configuración: servicio 1: falta 'nombre'`, e o código é **2**. Para comprovar o canal, repita o comando com `2> /dev/null`: não aparece nada na tela, porque a única coisa que foi impressa ia por `stderr`; o código de saída continua sendo 2.

(d) Com `python -m revisor --formato xml`, o erro do `argparse` que você já viu: vai pela saída de erro, e o código é **2**.

### Solução 3

Da pasta de cima, `python -m revisor` imprime, pela saída de erro, `error de configuración: no existe el archivo servicios.toml`, e o código de saída é **2**. Com `python -m revisor --config revisor/servicios.toml` o programa encontra o arquivo, imprime a tabela de quatro serviços e sai com **1**.

A razão: o **pacote** é encontrado porque está instalado no ambiente, e o ambiente não depende da pasta onde você está. Já `servicios.toml` é um arquivo **de dados** com um caminho relativo, e um caminho relativo é sempre contado a partir de onde você está parado. São dois mecanismos de busca diferentes: o Python procura código nas pastas do ambiente; o programa procura a configuração onde lhe disserem. Por isso o `--config` existe.

### Solução 4

(a) Sim, a mudança se nota: o resumo diz `media 843ms` em vez de `promedio 843ms`, sem reinstalar, porque a instalação editável importa o código da sua pasta `src/`. (b) Não se nota: `--version` continua dizendo `revisor 0.6.0`, porque a versão é lida dos metadados que foram guardados na última instalação, e editar o `pyproject.toml` não os atualiza. (c) Depois de `python -m pip install -e .`, `--version` diz `revisor 0.6.1`. (d) Ao devolver a versão para `0.6.0` e reinstalar, volta a dizer `revisor 0.6.0`.

A diferença: o **código** é importado de onde está, cada vez que o Python inicia; os **metadados** (versão, comandos) são copiados para o ambiente ao instalar. O que o `-e` evita é a cópia do código, não a dos metadados.

## Como sei que consegui

- [ ] `python -m revisor` imprime a tabela de quatro serviços com o resumo `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`, e `echo $?` imprime `1`.
- [ ] `python -m revisor --formato json` imprime o JSON com `"promedio_ms": 843`, e `python -m revisor --formato json > reporte.json` deixa no arquivo um JSON válido e nada mais.
- [ ] `python -m revisor --version` imprime `revisor 0.6.0`, e o comando `revisor --version` imprime o mesmo.
- [ ] `python -m revisor --formato xml` termina com o erro do `argparse` e o código 2.
- [ ] `python -m revisor --config no-existe.toml` imprime `error de configuración: no existe el archivo no-existe.toml` e termina com 2; com `2> /dev/null`, não se vê nada na tela.
- [ ] Você consegue explicar com suas palavras por que `python -m revisor` falha com `No module named revisor` antes de instalar, e por que isso é o que o `src/` pretende.
- [ ] Você consegue dizer que canal cada mensagem do `revisor` usa (relatório, erro de configuração, erro de uso) e que código acompanha cada caso.
- [ ] Você anotou no seu diário de bordo qual parte da montagem (caminhos, importações, instalação) lhe deu mais trabalho.

## Resumo

Responda sem olhar a lição:

1. Que diferença há entre um módulo e um pacote, e o que faz de uma pasta um pacote?
2. Que vantagem tem colocar o pacote dentro de `src/`? O que aconteceria com `python -m revisor` a partir da raiz se ele não estivesse ali?
3. O que `python -m revisor` executa, e o que faz `raise SystemExit(main())`?
4. Que pergunta cada tabela do `pyproject.toml` responde: `[build-system]`, `[project]` e `[project.scripts]`?
5. Por que o `pip install -e .` precisa de internet na primeira vez, se o `revisor` não tem dependências?
6. O que `parse_args()` devolve? O que o `argparse` faz quando o usuário escreve uma opção que não existe, e com que código termina?
7. O que significam os códigos 0, 1 e 2 do `revisor`? Como se lê o código do último comando no terminal?
8. Que diferença há entre a saída padrão e a saída de erro? O que fazem `>` e `2>`?
9. O que uma instalação editável acompanha e o que não acompanha? Como se atualiza o que ela não acompanha?
10. De onde sai o número que `--version` imprime, e por que ele não é escrito no código?

## Para ler mais

- [Python, `argparse`](https://docs.python.org/pt-br/3/library/argparse.html): a referência completa do módulo (ações, subcomandos, grupos de opções). Na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [Python Packaging User Guide, “Writing your `pyproject.toml`”](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/): todos os campos de `[project]` e de `[project.scripts]`, e as razões do design. Consultado em 7 de outubro de 2026.
- [Python Packaging User Guide, “src layout vs flat layout”](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/): as duas formas de colocar o pacote, comparadas com os seus custos. Consultado em 7 de outubro de 2026.
- [Python, tutorial de módulos e pacotes](https://docs.python.org/pt-br/3/tutorial/modules.html#packages): como se importa e como se organiza um pacote, com as importações absolutas e relativas. Consultado em 7 de outubro de 2026.
