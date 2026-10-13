# Lição 5 — O modelo de dados

**Tempo:** 90 min

**O que você constrói:** o modelo do `revisor` (`Servicio`, `Estado`, `Resultado`) e o seu relatório completo, com tabela e resumo

**O que você aprende:** moldes de dados com `class` e `@dataclass(frozen=True)`; `Enum`; `match` e `case`, com curinga e com guardas; o relatório com a sua linha de resumo

**De onde você vem.** Você traz o projeto da [Lição 4](04-colecciones.md): dois arquivos, `formato.py` e `revisor.py`, já sem listas paralelas. Em `revisor.py`, `SERVICIOS` é a lista de nomes que você quer revisar e `SIMULADO` é um dicionário que guarda, para cada nome, uma tupla `(código, tiempo_ms, erro)`. Funciona e já não se desalinha. Mas a Lição 4 terminou com três incômodos anotados. A tupla não diz o que é cada posição: o segundo elemento é o tempo porque você lembra, não porque o código diga. `clasificar` devolve um texto (`"ARRIBA"`, `"LENTO"`, `"CAIDO"`) e nada impede de escrever `"ARIBA"` sem que o Python proteste. E a tabela ainda não tem a sua linha de resumo.

**O que esta lição não faz.** Não lê a configuração de um arquivo (os quatro serviços continuam escritos à mão; a [Lição 6](06-errores-archivos-datos.md) os tira dali), não captura erros com `try` e não define métodos próprios nas classes. Tampouco consulta nenhum endereço da internet: os códigos e os tempos continuam saindo de `SIMULADO`.

Você trabalha na sua pasta `~/curso-python/revisor/`, com o ambiente virtual ativo. Os programas pequenos vão, como na Lição 4, na subpasta `practica/`.

## Ao terminar, você vai conseguir

- Declarar `Servicio` e `Resultado` como `@dataclass(frozen=True)` e `Estado` como `Enum`, e explicar o que se ganha em comparação com uma tupla, um dicionário ou um texto solto.
- Construir uma instância com os campos por posição ou por nome, ler os campos com um ponto e fabricar outra com `replace` em vez de mudar a que você tem.
- Classificar um serviço com `match` e `case`, com curinga e com guardas (`case c if c >= 400`), sem cair na armadilha do nome que captura.
- Ler `FrozenInstanceError`, o `ValueError` de um `dataclass` com uma lista como valor padrão e o de um `Enum` ao qual se pede um valor que ele não tem.
- Montar o `revisor` de quatro arquivos e reproduzir a sua tabela com o resumo `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.

## O porquê antes do como

Veja como o `revisor` fala hoje das coisas do seu problema. Um serviço é um **nome solto** dentro de uma lista. O que ele respondeu é uma **tupla anônima**, `(200, 2300, None)`. E o seu estado é um **texto**, `"LENTO"`. As três formas funcionam, e as três têm o mesmo defeito: o Python não sabe o que significam. Não sabe que o segundo elemento da tupla é um tempo, nem que `"LENTO"` é um de apenas três valores possíveis. Para o Python são uma tupla e um texto como quaisquer outros, e por isso um erro de digitação (escrever `"ARIBA"`, ou pedir `respuesta[2]` querendo o tempo) não falha onde ocorre: infiltra-se pelo programa e produz uma tabela errada sem uma única mensagem.

A solução é dar a cada coisa do problema **um nome próprio que o Python reconheça**. Um serviço já não será “um texto em uma lista” e sim um `Servicio`, com campos que se chamam `nombre`, `url` e `timeout_ms`; um estado já não será um texto que pode ser escrito errado, e sim um `Estado.LENTO` que o Python reconhece ou rejeita; e o que saiu de revisar um serviço será um `Resultado`. A essa forma que damos, no programa, ao que o problema trata, chamamos aqui **o modelo de dados**. (Atenção, que não é a mesma coisa que a seção “Data model” da documentação do Python, que fala de como a linguagem funciona por dentro; aqui “modelo” é o nosso.)

O caminho tem três ferramentas e uma montagem. O `dataclass` (5.1) fabrica moldes de dados; o `Enum` (5.2) fecha a lista de valores permitidos; o `match` (5.3) decide entre muitos casos com clareza; e em 5.4 se juntam no projeto, que ganha além disso a sua linha de resumo. No final da lição, o `revisor` fará isto:

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

É a tabela de sempre, agora com uma linha em branco e um resumo, e produzida a partir de objetos com nome em vez de tuplas e textos soltos. Repare que o cabeçalho e as quatro linhas saem idênticos aos das lições 3 e 4, e que o resumo é novo: para contar quantos estão no ar, quantos lentos e quantos fora do ar, e tirar a média, são necessárias as compreensões da Lição 4, agora aplicadas a resultados que já sabem o que são.

## Os conceitos

### 5.1 Um molde para cada serviço: `class` e `@dataclass`

#### 5.1.1 Por que a tupla e o dicionário não bastam

Com o que você já sabe, um serviço poderia ser uma tupla, `("catalogo", "https://catalogo.example", 5000)`, ou um dicionário, `{"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}`. A tupla, como você viu na Lição 4, não diz o que é cada posição. O dicionário diz, mas tem outro problema: as chaves são textos que você escreve de memória, e um erro de digitação não se nota onde ocorre.

<!-- frag: dict_typo.py -->
```python
servicio = {"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}
print(servicio.get("nmbre"))
```

```text
None
```

Escrever `"nmbre"` em vez de `"nombre"` não quebrou nada: o `.get` devolveu `None`, e esse `None` vai se infiltrando pelo programa até que algo falhe três funções depois, longe da causa. O que queremos é que esse erro de digitação **falhe ali mesmo**, com uma mensagem que o diga. Isso quem dá é um tipo próprio.

#### 5.1.2 Uma classe como molde

Uma **classe** é um molde para fabricar valores que têm todos a mesma forma. Cada valor fabricado com o molde se chama uma **instância**. Pense na forma de um biscoito: a forma é uma só e os biscoitos são muitos. No `revisor` o molde é `Servicio`, e `catalogo`, `inventario` e `pagos` são três instâncias. Aqui você só vai usar as classes como moldes de dados: sem métodos, sem herança (com uma exceção de sintaxe que você verá em 5.2). A palavra `class` seguida de um nome e dois-pontos abre o molde, e embaixo, com indentação, declara-se **um campo por linha**, com o formato `nome: tipo`.

O Python tem uma ferramenta, o módulo `dataclasses`, que fabrica quase tudo o que um molde de dados precisa: a forma de construir cada instância, a de mostrá-la ao imprimir e a de compará-la com `==`. Ela é ativada com uma linha logo acima da classe, que começa com `@` e se chama **decorador**: é uma marca que pede ao Python que processe a classe com essa ferramenta antes de entregá-la. [A documentação do módulo](https://docs.python.org/pt-br/3/library/dataclasses.html) o descreve assim: o decorador acrescenta os métodos gerados à classe que decora. Aqui é usado como `@dataclass(frozen=True)`, onde `frozen=True` (congelado) pede além disso que as instâncias **não possam ser mudadas**, como uma tupla. Salve isto como `fig05_01.py`:

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

- `from dataclasses import dataclass` traz do módulo `dataclasses` só a ferramenta de que você precisa, com a forma `from ... import` da Lição 3.
- As duas linhas em branco antes e depois da classe são convenção de estilo ([PEP 8](https://peps.python.org/pep-0008/#blank-lines)), não sintaxe; o formatador que você verá na Lição 8 as exige.
- `nombre: str` e `url: str` declaram dois campos de texto. `timeout_ms: int = 5000` declara um campo inteiro com **valor padrão**: se ao construir você não o dá, vale 5000, o tempo limite do `httpx` que o `revisor` usará mais adiante. Os campos com valor padrão vão **no final**, igual aos parâmetros com valor padrão de uma função.
- `Servicio("catalogo", "https://catalogo.example")` **constrói** uma instância: chama-se o molde como se fosse uma função, com os campos na ordem em que foram declarados. Também se pode dar cada campo pelo seu nome, como em `notificaciones`, que além disso muda o tempo limite para 1000. Por nome se lê melhor quando são mais de dois ou três campos.
- `print(catalogo)` mostra `Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)`: a forma de imprimir também foi gerada pelo `dataclass`, e por isso uma instância que você imprime durante uma depuração se entende sozinha. Com uma tupla sem nomes você teria visto `('catalogo', 'https://catalogo.example', 5000)`.
- `catalogo.timeout_ms` lê um campo com um ponto. Se você escreve mal o nome (`catalogo.timeout`), o Python falha ali mesmo com `AttributeError`, que é o que queríamos.
- `catalogo == igual` é `True` porque `==` compara **campo por campo**: são duas instâncias separadas com os mesmos dados. `catalogo is igual` é `False` porque são dois objetos diferentes. É o `==` contra `is` da Lição 3, com um caso real: `==` pergunta “valem o mesmo?”, `is` pergunta “são a mesma coisa?”.
- As duas últimas linhas são para que você não se descuide. `Servicio(nombre=5, url=None)` **é construído sem protestar**, embora `nombre` devesse ser texto e `url` também. É o que você aprendeu na Lição 0: as anotações não são impostas na execução. O `dataclass` usa as anotações só para saber que campos há e em que ordem: [a documentação esclarece](https://docs.python.org/pt-br/3/library/dataclasses.html) que, salvo duas exceções que você não usará, nada no decorador examina o tipo anotado. Quem sim as confere é uma ferramenta à parte, o `mypy`, na Lição 8.

#### 5.1.3 Congelado: para mudar, cria-se outro

O que faz o `frozen=True`? Proíbe atribuir a um campo. Veja o que acontece se você tenta:

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

Deste *traceback* mostra-se apenas a última linha, que é a que importa: no meio ele passa por uma linha que o `dataclasses` gera por dentro e que não é igual no 3.12 e no 3.14. Diz “não é possível atribuir ao campo `timeout_ms`”. Como com a tupla, é uma garantia e não uma falha. [A documentação](https://docs.python.org/pt-br/3/library/dataclasses.html#frozen-instances) a chama de emulação de instâncias somente leitura.

Por que você quereria isso? Porque o resultado de revisar um serviço é um **fato**: “às 10:42, `inventario` demorou 2300 ms”. Ninguém deveria poder corrigi-lo depois sem deixar rastro. E porque, quando nas lições 9 e 10 várias tarefas lerem os mesmos serviços ao mesmo tempo, que nenhuma possa mudá-los evita toda uma classe de erros. E se de fato você precisa de outra versão de um serviço, não a edita: **fabrica outra** com `dataclasses.replace`, que copia uma instância mudando apenas os campos que você indicar:

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

O `replace` não mexeu em `catalogo`: devolveu `catalogo_corto`, uma instância nova. E a última linha mostra outra vantagem do imutável: uma instância congelada pode ser posta em um **conjunto** (ou ser chave de um dicionário), porque já não muda: é hasheável no sentido da Lição 4 (4.1.4), **desde que todos os seus campos sejam**. O Python calcula a sua impressão digital a partir dos campos, e os de `Servicio` são textos e inteiros. Duas instâncias iguais contam como uma só: `{catalogo, repetido}` tem um elemento.

Um aviso que se conecta com a cópia contra referência da Lição 4: `frozen` proíbe reatribuir o **campo**, mas não torna imutável o que o campo contém. Um campo que guarde uma lista continua podendo mudar por dentro (`servicio.etiquetas.append(...)`), porque a lista continua sendo mutável. E tem um segundo efeito: uma instância assim já não pode ser posta em um conjunto, porque a impressão digital é calculada com todos os campos e uma lista não tem impressão digital; a tentativa falha com `TypeError: unhashable type: 'list'` (no 3.14 o texto acrescenta `cannot use ... as a set element`). Por isso no `revisor` os campos são de tipos imutáveis: textos, inteiros, `None`.

### 5.2 `Enum`: uma lista fechada de valores

Veja outro problema parecido. O `clasificar` da Lição 3 devolve o texto `"ARRIBA"`, `"LENTO"` ou `"CAIDO"`, e quem o usa compara contra textos. Se um é escrito errado:

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

O programa não falhou: disse que o serviço **não** estava no ar, quando o que aconteceu é que alguém escreveu um R a menos. É o mesmo erro de digitação de 5.1.1, agora em um valor. O que se precisa é de uma lista **fechada** de valores permitidos, com nomes que o Python reconheça, e isso é um `Enum` (de “enumeração”). [O módulo `enum`](https://docs.python.org/pt-br/3/library/enum.html) o define como um conjunto de nomes simbólicos ligados a valores únicos.

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

- `class Estado(Enum):` abre um molde, igual a `Servicio`, mas com `(Enum)` entre parênteses: assim se diz ao Python “este molde se baseia em `Enum`”, ou seja, que é uma enumeração. Os parênteses depois do nome significam “esta classe parte daquela outra”. No código que você escreve neste curso você só os verá com `Enum` e, na Lição 6, com `Exception` (o laboratório da Lição 9 também os usa, mas esse programa você o executa sem escrevê-lo); para o que você precisa basta lê-lo como “uma classe da família `Enum`”.
- Dentro há uma linha por **membro**: `ARRIBA = "ARRIBA"` dá o nome do membro (à esquerda, sempre em maiúsculas por convenção) e o seu **valor** (à direita). Aqui o valor é o mesmo texto que é impresso na tabela, sem acento e em maiúsculas, que é também como o JSON da Lição 6 o guardará.
- `Estado.LENTO` é um membro. O `print` o mostra com o nome da sua classe na frente: `Estado.LENTO`. `.name` é o seu nome (`LENTO`) e `.value` o seu valor (`LENTO`). Quando o relatório quer a palavra para a tabela, usa `.value`.
- `Estado("CAIDO")` vai em sentido contrário: busca o membro cujo **valor** é esse texto. Se não há nenhum, falha na hora (você vê daqui a pouco).
- `estado is Estado.LENTO` é `True`: [os membros são comparados por identidade](https://docs.python.org/pt-br/3/howto/enum.html#comparisons), e cada membro existe uma única vez. E `estado == "LENTO"` é **`False`**: o membro `Estado.LENTO` e o texto `"LENTO"` são coisas diferentes, embora se imprimam quase igual. Isso surpreende quase todo mundo na primeira vez. Compara-se sempre contra membros (`estado == Estado.LENTO`), nunca contra o texto.
- `for posible in Estado:` percorre os membros na ordem em que foram declarados.

Agora o erro de digitação, nas suas duas variantes. Escrever `Estado.ARIBA` falha na hora, no ponto exato do erro:

<!-- frag: enum_typo.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


print(Estado.ARIBA)
```

A última linha do *traceback* é:

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

O Python até adivinha o que você queria escrever. O que importa é que o erro ocorre na linha do deslize e não três funções depois. E buscar por valor um texto que não existe:

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

`ValueError: 'ROTO' is not a valid Estado`. Os dois erros dizem o mesmo com palavras diferentes: “esse membro não existe”. Repare que são exatamente o tipo de falha que queríamos: cedo, clara e com o nome do culpado.

### 5.3 `match` e `case`: decidir entre muitos casos

A Lição 2 ensinou a você `if`/`elif`/`else`. Quando os ramos são muitos e todos perguntam pelo **mesmo valor**, uma cadeia longa de `elif` fica difícil de ler, e para isso o Python traz, desde a versão 3.10, a instrução `match`. É muito poderosa (a [documentação oficial](https://docs.python.org/pt-br/3/reference/compound_stmts.html#the-match-statement) dedica a ela uma seção inteira, e a [PEP 636](https://peps.python.org/pep-0636/) é um tutorial), mas aqui você vai usar apenas a parte mais simples dela. Veja primeiro uma função que descreve um código de status, e que ainda não é a do `revisor`:

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

Como se lê:

- `match codigo:` diz “vou comparar este valor” (o **sujeito**). Cada `case` embaixo é um **padrão** com o qual o Python o testa, **de cima para baixo**, e fica com **o primeiro que encaixar**: executa o bloco dele e não olha os demais. Por isso a ordem importa.
- `case None`, `case 200`, `case 404` são padrões **literais**: encaixam se o sujeito vale isso. O primeiro pergunta por `None` com identidade, como ensinaram a você na Lição 2, e os demais com igualdade.
- `case 301 | 302` é **um ou outro**: a barra vertical significa “ou”. Encaixa com qualquer um dos dois códigos.
- `case c if c >= 500` é o que merece atenção. Primeiro `c` é um padrão de **captura**: um nome solto encaixa com *qualquer* coisa e, de passagem, guarda o sujeito nessa variável, então dentro do bloco `c` vale o código. Depois, `if c >= 500` é uma **guarda**: uma condição extra que deve ser cumprida para que o caso valha. Se não for cumprida, o Python segue para o próximo `case`. [A documentação](https://docs.python.org/pt-br/3/reference/compound_stmts.html#guards) descreve assim: se o padrão falha, a guarda nem é avaliada; se encaixa, a guarda é avaliada, e o caso só é escolhido se esta for verdadeira. Por isso o 418 passa batido pelo caso de 500 (é menor) e cai no seguinte, `c >= 400`.
- `case _:` é o **curinga**: o sublinhado encaixa com tudo e não guarda nada. Vai no final e recolhe o que nenhum caso anterior pegou (aqui, o 100).

A classificação completa dos serviços do `revisor` são quatro regras, que você já conhece da Lição 2: sem código está fora do ar; código de 400 ou mais está fora do ar; se respondeu e demorou 1000 ms ou mais está lento; se não, está no ar. Escreve-se com o mesmo molde, e devolve membros de `Estado` em vez de textos. Isto é o que ficará em `modelo.py`:

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

Leia-a de cima para baixo, que é como o Python faz. O primeiro `case` pega “sem código” e o segundo, com a sua guarda, pega “código de 400 ou mais”: as duas primeiras regras, e as duas dão `CAIDO`. O que chega ao `case _` já sabemos que respondeu bem (há código e é menor que 400), e ali só resta decidir entre as outras duas regras com um `if` da Lição 2: se o tempo existe e é pelo menos o limiar, `LENTO`; se não, `ARRIBA`. Conferir `tiempo_ms is not None` antes de comparar é necessário porque um código pode existir sem tempo, e comparar `None >= 1000` falha com um `TypeError`. Observe também que a ordem dos casos **é** a lógica: se você pusesse o caso do 400 antes do de `None`, `None >= 400` falharia. No projeto de 5.4 a função vive em `modelo.py`, junto às classes que você definiu em 5.1 e 5.2.

Agora a armadilha mais famosa do `match`. Em um padrão, **um nome solto não compara, captura**. Se você quer comparar contra uma constante, não basta escrever o nome dela:

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

Este programa **nem sequer inicia**: o Python o rejeita ao lê-lo, com um `SyntaxError`. `case LIMITE:` não pergunta “o código vale 400?”; diz “qualquer coisa encaixa, e guarde-a em uma variável chamada `LIMITE`”. Como encaixa com tudo, o `case _` de baixo nunca seria alcançado, e por isso a mensagem diz `name capture 'LIMITE' makes remaining patterns unreachable` (“a captura do nome torna inalcançáveis os padrões restantes”). O Python só avisa porque depois de `case LIMITE:` há outro caso. Se `case LIMITE:` fosse o último, não avisaria de nada: [a documentação](https://docs.python.org/pt-br/3/reference/compound_stmts.html#irrefutable-case-blocks) permite um caso que sempre encaixa (chama-o de irrefutável) desde que vá no final, e o programa rodaria com um curinga disfarçado de constante, devolvendo `True` para qualquer código. Você pode conferir: com um `case LIMITE:` no final, `es_error(5)` devolve `True`. A regra prática: para comparar contra uma constante, usa-se um nome **com ponto**, como `Estado.CAIDO`; o ponto diz ao Python que é um valor e não um nome novo, e [os chama de padrões de valor](https://docs.python.org/pt-br/3/reference/compound_stmts.html#value-patterns).

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

Aqui `Estado.ARRIBA` leva ponto, então compara. É o uso mais natural do `match` junto a um `Enum`: um caso por membro, sem curinga. E traz uma vantagem que o `mypy` aproveita na Lição 8: se algum dia você acrescentar um membro novo a `Estado` e esquecer o seu `case`, o verificador de tipos aponta.

### 5.4 Montar o `revisor`

Junte tudo no projeto. Ao terminar você terá quatro arquivos em `~/curso-python/revisor/`: `modelo.py` (novo), `revision.py` (novo), `formato.py` (muda) e `revisor.py` (muda). Cada arquivo tem uma razão de existir: `modelo.py` diz **que coisas existem** (o serviço, o estado, o resultado) e como se classifica; `revision.py` **revisa** um serviço; `formato.py` **dá forma de texto** a um resultado, e `revisor.py` é o ponto de entrada que os junta.

O primeiro é o modelo:

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

As quatro peças, uma por uma.

**`modelo.py`.** Reúne tudo o das seções 5.1 a 5.3. As constantes e as classes vão em cima, porque `clasificar` as usa. `Resultado` é um segundo molde que já não guarda textos soltos: guarda **um `Servicio`** (o que foi revisado), **um `Estado`**, o tempo (`int | None`, porque um serviço fora do ar não tem) e o detalhe. Observe a composição: um molde pode ter campos cujo tipo é outro molde. `clasificar` é a que você escreveu em 5.3, só que a lista de parâmetros é repartida em linhas porque a linha do `def` não cabe nos 88 caracteres que o estilo pede (a vírgula no final da lista de parâmetros faz parte dessa forma de arrumar). E `nombres_repetidos` é a da Lição 4 (4.1.5), só que agora recebe uma lista de `Servicio` e olha o campo `servicio.nombre`.

**`revision.py`.** É um módulo novo, mas o conteúdo dele não é: `SIMULADO` é o dicionário da Lição 4, que sai de `revisor.py` e se muda para cá, com a mesma tupla de três `(código, tiempo_ms, erro)` para cada nome. `revisar` muda de assinatura outra vez: agora recebe um `Servicio` e devolve um `Resultado`, em vez de receber um nome e devolver uma linha já montada. O de dentro é o que você já conhece: busca com `.get` (um nome que não esteja em `SIMULADO` é um serviço sem dados, e sai fora do ar “sin conexión”), desempacota a tupla em três nomes, decide o `detalle` com a mesma regra (o código como texto se houve resposta, e se não, o texto do erro), classifica e devolve um `Resultado`. Que `revisar` já não monte a linha é a separação que buscávamos: revisar é uma coisa e mostrar é outra, e cada uma vive no seu módulo. `revisar_todos` é uma compreensão: uma lista de `Resultado`, um por serviço, na mesma ordem. Quando na Lição 9 o programa consultar de verdade, `SIMULADO` desaparece e `revisar` continua devolvendo o mesmo.

**`formato.py`.** `formatear_tiempo` e `encabezado` ficam como nas lições 3 e 4. (Se você os escreveu de outra forma mas a saída era a mesma, deixe-os como estão.) O que muda é `linea`, que **muda de assinatura**: antes recebia quatro valores soltos e agora recebe um único `Resultado`, e tira dele o que precisa. Isso é o que buscávamos: já não é preciso passar quatro coisas na ordem correta. As duas funções novas são `contar` e `resumen`. `contar` acrescenta um “s” quando a quantidade não é um: `contar(1, "caído")` dá `1 caído` e `contar(3, "caído")` dá `3 caídos`. `resumen` conta o total com `len`, usa três compreensões para contar quantos há de cada estado, tira com uma quarta os tempos dos que responderam, calcula a média **só se houver algum** (com `len(tiempos_ms) > 0`, porque dividir por zero falharia) e junta as partes com `" · ".join(partes)`. A anotação `promedio_ms: int | None = None` diz que começa sem valor e que pode acabar sendo um inteiro; se nenhum serviço respondeu, o resumo diz `promedio —`.

**`revisor.py`.** `SERVICIOS` deixa de ser uma lista de nomes e passa a ser uma **lista de `Servicio`**: os quatro canônicos, escritos à mão, cada um com o seu nome e o seu endereço (o tempo limite fica no valor padrão). Para acrescentar um serviço você escreve um `Servicio(...)` e, enquanto os dados forem simulados, a linha dele em `SIMULADO`, igual à Lição 4. `main` revisa todos, imprime o cabeçalho, uma linha por resultado, uma linha em branco (a que o `print()` sem argumentos escreve) e o resumo. Os `from ... import` funcionam porque os quatro arquivos estão na mesma pasta, como na Lição 3.

Execute o projeto a partir da sua pasta:

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

É a tabela das lições 3 e 4, com uma linha em branco e o resumo. Se as colunas não saem alinhadas, o culpado quase sempre é um espaço a mais ou a menos dentro de uma das f-strings; confira que sejam idênticas às do texto. E se o resumo conta mal, compare cada compreensão com a da lição: as três que contam estados só mudam o membro de `Estado`.

Com isso o `revisor` já tem o seu **modelo**: o `Servicio` que se revisa, o `Estado` em que fica e o `Resultado` que une as duas coisas com o que foi medido. Mas há algo que continua incômodo, e você vai senti-lo no exercício 1: a lista de serviços está **dentro do código**. Para revisar outro serviço é preciso abrir `revisor.py` e editar. A [Lição 6](06-errores-archivos-datos.md) a tira para um arquivo de configuração, e com ele chegam os erros que merecem a sua própria lição.

## O erro que você vai ver

Nas seções anteriores você já provocou vários erros no lugar onde nascem (`FrozenInstanceError`, `AttributeError`, `ValueError`, `SyntaxError`). Aqui vai o que você mais vai encontrar ao escrever moldes com `dataclass`, e no final uma tabela para reconhecê-los todos de relance.

### `ValueError: mutable default <class 'list'> for field ... is not allowed`

É o mesmo problema do argumento mutável padrão da Lição 3, agora em um campo de `dataclass`. Se você põe uma lista como valor padrão:

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

A última linha diz: “um valor padrão mutável (`list`) para o campo `etiquetas` não é permitido: use `default_factory`”. (Aqui também se mostra apenas a última linha: entre ela e o seu arquivo o *traceback* passa por linhas internas de `dataclasses.py` que mudam entre uma versão do Python e outra, e não ajudam a ler o erro. O que conta é o tipo, `ValueError`, e a mensagem, que além disso diz a você como corrigir.) O Python protege você de algo que em uma função normal acontecia em silêncio: uma única lista compartilhada por todas as instâncias. A solução é uma **fábrica**: em vez de “esta lista”, você diz “chame `list` cada vez que for preciso uma nova”.

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

Cada instância tem a sua própria lista, e por isso `pagos` não ficou sabendo da etiqueta de `catalogo`. De passagem se vê o que foi avisado em 5.1.3: a instância está congelada, e mesmo assim `catalogo.etiquetas.append(...)` funcionou, porque o `frozen` impede reatribuir o campo, não mudar a lista que ele contém. Por isso no `revisor` não se usam listas como campos.

### Os erros desta lição de relance

Quando um aparecer para você, procure aqui a última linha. Todos saíram das execuções desta lição.

| A última linha diz... | O que aconteceu | Onde você viu |
|---|---|---|
| `dataclasses.FrozenInstanceError: cannot assign to field '...'` | você tentou atribuir a um campo de uma instância congelada | 5.1.3 |
| `ValueError: mutable default ... use default_factory` | você pôs uma lista como valor padrão de um campo | acima |
| `AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?` | você pediu um membro de `Enum` que não existe | 5.2 |
| `ValueError: 'ROTO' is not a valid Estado` | você buscou por valor um membro que não existe | 5.2 |
| `SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable` | você escreveu um nome solto onde queria comparar | 5.3 |

## O que se faz errado

Cada um destes descuidos tem um custo concreto, e a maioria não dá erro na primeira vez.

**Guardar um registro em um dicionário ou em uma tupla quando você já tem um molde.** Uma tupla de seis elementos obriga a lembrar qual é qual; um dicionário com chaves de texto transforma os erros de digitação em `None`s distantes. Se os dados têm uma forma fixa, essa forma merece um nome: `@dataclass`.

**Achar que um `dataclass` valida os seus campos.** `Servicio(nombre=5, url=None)` é construído sem protestar (5.1.2): as anotações dizem o que você espera, mas não o conferem na execução. O custo é um dado ruim que viaja por todo o programa até falhar longe. O que chega de fora se valida na entrada, e isso é a Lição 6.

**Deixar textos soltos onde já há um `Enum`.** Este é o mais traiçoeiro. Se você muda `clasificar` para que devolva `Estado.LENTO` mas em outra parte do programa fica um `if estado == "LENTO"`, essa comparação **nunca será verdadeira** (5.2: um membro não é igual ao seu texto), e o programa seguirá rodando sem avisar. Quando você migrar de textos para um `Enum`, procure todos os lugares que comparam.

**Escrever `case NOMBRE:` querendo comparar.** Captura, não compara. Se você quer comparar contra uma constante, use um nome com ponto (`Estado.CAIDO`) ou uma guarda (`case c if c == LIMITE`).

**Pôr uma coleção mutável como campo de um molde congelado.** O `frozen` protege o campo, não o que o campo contém: uma lista guardada em uma instância congelada pode continuar sendo mudada por dentro (`fig05_08.py`). O custo é uma garantia que parece existir e não existe. No `revisor` os campos são textos, inteiros, `None` e outros moldes congelados.

**Construir instâncias por posição quando são muitos campos.** `Servicio("notificaciones", "https://notificaciones.example", 1000)` se lê; com seis campos, ninguém sabe qual é o quarto. Com mais de dois ou três, por nome: `Servicio(nombre=..., url=..., timeout_ms=...)`.

## Exercícios

Tente cada um antes de olhar as soluções.

### Exercício 1 — Dois serviços a mais, e uma média só dos que estão no ar

(a) Acrescente os dois serviços extras do `revisor` à versão de 5.4: `facturacion` (responde com código 503 em 95 ms) e `notificaciones` (com tempo limite de 1000 ms, não consegue resposta: “tiempo agotado”). Você precisa mexer em **dois** lugares. Antes de executar, preveja as duas últimas linhas da saída: a da linha de `notificaciones` e o resumo. (b) Acrescente ao final de `main` uma linha que imprima a média dos tempos dos serviços `ARRIBA` somente, sem arredondar. O conveniente é fazê-lo com uma compreensão.

### Exercício 2 — Provoque quatro erros e leia-os

Abra o REPL com `python` a partir da sua pasta do `revisor`, importe o que for preciso de `modelo` e provoque estes quatro erros, um por um: (a) atribuir `timeout_ms` a uma instância de `Servicio`; (b) `Estado("ROTO")`; (c) `Estado.ARIBA`; (d) em um arquivo da sua pasta `practica/`, um `dataclass` com um campo `etiquetas: list[str] = []`. Para cada um, escreva no seu diário de bordo a **última linha** e, com as suas palavras, o que quer dizer e como se corrige.

### Exercício 3 — Um código sem tempo

O que devolve `clasificar(200, None)`, isto é, um serviço que respondeu com 200 mas do qual não há tempo medido? Preveja duas vezes: com o `clasificar` da Lição 3 (o que devolve textos) e com o de hoje (o do `match`). Depois confira a partir da sua pasta do `revisor`, com `from modelo import clasificar`. Por que a regra dá esse resultado e não `LENTO`? E por fim: o que aconteceria se você tirasse da condição a parte `tiempo_ms is not None`?

## Soluções

### Solução 1

(a) Em `revision.py`, `SIMULADO` ganha duas linhas:

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

E em `revisor.py`, `SERVICIOS` ganha dois serviços:

```python
    Servicio("reportes", "https://reportes.example"),
    Servicio("facturacion", "https://facturacion.example"),
    Servicio("notificaciones", "https://notificaciones.example", timeout_ms=1000),
]
```

A saída completa:

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

O resumo é `6 servicios · 2 arriba · 1 lento · 3 caídos`, e a média sai 656 ms porque é calculada pelos **quatro que tiveram tempo** (142, 2300, 87 e 95, que somam 2624, dividido por 4). Observe que `facturacion` conta na média embora esteja fora do ar: respondeu, com um 503 e 95 ms. `notificaciones` não tem tempo e não conta. Observe também a linha de `notificaciones`: é o mesmo transbordamento que você viu na Lição 4, com o nome colado ao estado porque mede 14 letras e a coluna 12; a Lição 11 o resolve calculando a largura a partir do nome mais longo. E a terceira observação é a que abre caminho para a lição seguinte: para revisar dois serviços a mais você teve que **editar o código**, em dois arquivos.

(b) Importa-se `Estado` e acrescenta-se a compreensão ao final de `main`:

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

A última linha da saída é:

```text
114.5
```

(142 e 87 somam 229, dividido por 2 são 114.5.) A condição `r.tiempo_ms is not None` não é um enfeite. Um serviço `ARRIBA` pode não ter tempo: `clasificar(200, None)` devolve `Estado.ARRIBA`, porque sem tempo medido não há evidência de lentidão. Se esse `None` chegasse ao `sum`, o programa falharia com um `TypeError`. E além disso `tiempo_ms` está anotado como `int | None`, e quem ler o código (ou o `mypy`, na Lição 8) precisa ver que o `None` já foi descartado antes de somar.

### Solução 2

As quatro últimas linhas, cada uma medida:

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

`FrozenInstanceError`: a instância está congelada. Correção: não atribuir; fabricar outra com `replace(servicio, timeout_ms=...)`.

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError`: não existe um membro de `Estado` com valor `ROTO`. Correção: usar um dos três valores permitidos, ou `Estado.CAIDO` diretamente, que nem sequer passa pelo texto.

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

`AttributeError`: `Estado` não tem um membro chamado `ARIBA`, e o Python sugere o que se parece. Correção: o que ele sugere. É o erro de digitação que o `Enum` veio pegar, e ele o pega na linha onde ocorre.

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

`ValueError` ao **definir** a classe, antes de criar qualquer instância. Correção: `etiquetas: list[str] = field(default_factory=list)`, como em `fig05_08.py`.

### Solução 3

As duas versões devolvem **ARRIBA**: a da Lição 3, o texto `"ARRIBA"`; a de hoje, `Estado.ARRIBA`. A partir da pasta do `revisor`:

<!-- frag: codigo_sin_tiempo.py -->
```python
from modelo import clasificar

print(clasificar(200, None))
```

```text
Estado.ARRIBA
```

A razão está na terceira regra, que é a mesma desde a Lição 2: um serviço é `LENTO` se **respondeu e demorou** 1000 ms ou mais. Com `None` não há tempo medido, então não há evidência de lentidão, e a única coisa que se sabe é que respondeu com um código bom: `ARRIBA`. As duas versões tratam o caso igual porque as duas perguntam `tiempo_ms is not None` antes de comparar. No `revisor` esse caso não ocorre (um serviço que respondeu sempre traz o seu tempo), mas `tiempo_ms` está anotado como `int | None`, e a função tem que dar uma resposta para tudo o que a sua assinatura admite.

Se você tirasse `tiempo_ms is not None`, a comparação `None >= 1000` chegaria a ser avaliada e o programa pararia com:

```text
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

É o mesmo erro da Lição 2, quando as perguntas estavam na ordem errada.

## Como sei que consegui

- [ ] Em `~/curso-python/revisor/`, `python revisor.py` imprime sete linhas (o cabeçalho, quatro linhas, uma linha em branco e o resumo), e a última é `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Com os dois serviços extras do exercício 1, a última linha é `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`, e a linha de `notificaciones` sai com o nome colado ao estado (e você sabe por quê).
- [ ] No REPL, atribuir `timeout_ms` a um `Servicio` falha com `dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'`, e `Estado("ROTO")` falha com `ValueError: 'ROTO' is not a valid Estado`.
- [ ] Você consegue escrever de memória `clasificar` com `match`: sem código é `CAIDO`, um código de 400 ou mais é `CAIDO`, um tempo de 1000 ou mais é `LENTO`, e o resto é `ARRIBA`.
- [ ] Você consegue explicar com as suas palavras a diferença entre `==` e `is` para dois `Servicio` iguais, por que `Estado.LENTO == "LENTO"` é `False` e o que faz o `replace`.
- [ ] Você anotou no [diário de bordo](bitacora.md) o que foi mais difícil para você: o que anotar ali é o que você deve revisar.

## Resumo

Responda sem olhar a lição:

1. O que é uma classe e o que é uma instância? O que o `@dataclass` acrescenta a uma classe, e o que acrescenta o `frozen=True`?
2. O que se ganha com `@dataclass(frozen=True)` em comparação com um dicionário ou uma tupla? O que faz o `replace`?
3. O que compara `==` entre dois `Servicio`, e o que compara `is`?
4. Por que `Estado.LENTO == "LENTO"` dá `False`, e como se obtém o texto de um membro?
5. Em que ordem o `match` testa os seus casos, e o que faz o curinga `case _`?
6. Em um `match`, o que faz um nome solto como `case LIMITE:`? Como se compara contra uma constante?
7. Por que `linea` mudou de assinatura nesta lição, e o que ganhou com a mudança?

## Para ler mais

- [Python, “dataclasses”](https://docs.python.org/pt-br/3/library/dataclasses.html) — a referência completa do módulo: `frozen`, `field`, `replace` e tudo o que esta lição não usou. Na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [PEP 557, “Data Classes”](https://peps.python.org/pep-0557/) — o documento que propôs o `dataclass` e explica para que casos foi pensado e para quais não. Consultado em 7 de outubro de 2026.
- [Python, “Enum HOWTO”](https://docs.python.org/pt-br/3/howto/enum.html) — o guia oficial das enumerações, do básico aos tipos derivados. Consultado em 7 de outubro de 2026.
- [PEP 636, “Structural Pattern Matching: Tutorial”](https://peps.python.org/pep-0636/) — o tutorial oficial do `match`, que vai bastante mais longe do que esta lição. Consultado em 7 de outubro de 2026.
