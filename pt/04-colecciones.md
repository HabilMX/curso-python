# Lição 4 — Coleções

**Tempo:** 2 × 90 min (a primeira sessão vai até o final de 4.2; a segunda começa em 4.3)

**O que você constrói:** o `revisor` sem listas paralelas: os dados de cada serviço viajam juntos, em um dicionário que se consulta pelo nome do serviço

**O que você aprende:** `list`, `tuple`, `dict` e `set`; compreensões; cópia contra referência; não mudar o que se percorre; `KeyError` e `IndexError`

**De onde você vem.** Você traz o projeto da [Lição 3](03-bucles-funciones-modulos.md): dois arquivos, `formato.py` e `revisor.py`. O primeiro sabe formatar o tempo e montar o cabeçalho e cada linha; o segundo guarda os dados, classifica cada serviço e percorre os quatro para imprimi-los. Funciona, e a tabela sai certa. Mas os dados dos serviços vivem em **três listas paralelas**, `NOMBRES`, `CODIGOS` e `TIEMPOS_MS`, que só se correspondem pela posição: o nome número 2 vai com o código número 2 e com o tempo número 2. No exercício da Lição 3 você acrescentou `facturacion` a duas listas, esqueceu a terceira, e viu o `IndexError` ou a linha errada que isso produz. Essa fragilidade é a que se elimina hoje.

**O que esta lição não faz.** Ainda não dá a cada serviço uma forma própria com nome (um `Servicio`, um `Estado`): isso é a [Lição 5](05-modelo-de-datos.md), que se apoia em tudo o de hoje. Tampouco lê a configuração de um arquivo (os serviços continuam escritos à mão no código; a [Lição 6](06-errores-archivos-datos.md) os tira dali), não captura erros com `try` e não consulta nenhum endereço da internet: os códigos e os tempos saem de uma tabela simulada dentro do programa.

Você trabalha na sua pasta `~/curso-python/revisor/`. Os programas pequenos da lição (os que não fazem parte do projeto) você pode guardá-los em uma subpasta `practica/` dentro dela, para que não se misturem com os arquivos do `revisor`. Todos os comandos supõem que o ambiente virtual da Lição 1 está ativo, então se escreve `python`, não `python3`.

## Ao terminar, você vai conseguir

- Escolher entre lista, tupla, dicionário e conjunto conforme o que você vai guardar e como vai buscar, e escrever cada uma com a sua anotação de tipo (`list[str]`, `dict[str, int | None]`, `set[str]`).
- Ler um `IndexError` e um `KeyError`, dizer que posição ou que chave faltou, e usar `.get` quando a ausência é um caso normal e não um erro.
- Reescrever um laço que monta uma lista como uma compreensão, e saber quando convém deixá-lo como laço.
- Prever o que acontece com `b = a` quando `a` é uma lista, copiar de forma rasa e profunda, e explicar por que mudar uma lista enquanto você a percorre dá resultados errados sem avisar.
- Reescrever o `revisor` sem listas paralelas: um dicionário que guarda, para cada nome, uma tupla com o seu código, o seu tempo e o seu erro, e um percurso que já não depende de três listas estarem alinhadas.

## O porquê antes do como

Abra o `revisor.py` da Lição 3 e veja como `inventario` é representado: o texto `"inventario"` em `NOMBRES[1]`, o número `200` em `CODIGOS[1]` e o número `2300` em `TIEMPOS_MS[1]`. Três valores que pertencem a uma mesma coisa, guardados em três lugares diferentes. Para acrescentar um serviço você tem que lembrar de mexer em três listas e de mexer nelas na mesma ordem, e o Python não avisa se você erra: se esquece a terceira, o programa falha ao chegar ao quinto serviço, ou pior, emparelha o código de um serviço com o tempo de outro e a tabela sai bem formatada e **errada**. É a regra de sempre em programação: um dado escrito em dois lugares acaba divergindo.

A solução é **um único lugar para cada dado**, e para isso são necessárias formas de agrupar valores. O Python traz quatro (lista, tupla, dicionário e conjunto), cada uma pensada para uma pergunta diferente: “em que ordem estão?”, “qual é o deste nome?”, “já vi este valor?”. Esta lição as apresenta uma por uma (4.1), junto com as duas ferramentas com que elas são construídas e manejadas sem surpresas: as compreensões (4.2) e o cuidado com as cópias (4.3). No final (4.4) você as usa para reescrever o `revisor`: os dados de cada serviço passam a viver juntos, sob o seu nome, e as três listas paralelas desaparecem. A lição seguinte dá o passo que falta, dar nome próprio às coisas do problema (um `Servicio`, um `Estado`), e para dá-lo precisa de tudo o de hoje.

No final da lição, o `revisor` fará isto:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

É exatamente a tabela da Lição 3, letra por letra, e é de propósito: o que muda hoje não é o que o programa imprime, e sim como ele guarda os seus dados por dentro. Uma mudança assim, que deixa o resultado idêntico e melhora a estrutura, tem uma vantagem enorme: confere-se comparando as duas saídas. O que o programa ganha não se vê na tabela, e sim ao modificá-lo, e você vai conferir isso no exercício 3: acrescentar um serviço deixa de ser uma operação sobre três listas que é preciso mexer na mesma ordem.

## Os conceitos

### 4.1 As quatro coleções

Uma **coleção** é um valor que guarda outros valores. O Python traz quatro de uso diário, e elas se distinguem por duas perguntas. A primeira: pode ser mudada depois de criada? O que pode ser mudado se chama **mutável**, e o que não pode, **imutável**; a lista, o dicionário e o conjunto são mutáveis, a tupla não. A segunda: como se encontra um elemento? Pela sua **posição** (lista e tupla), pelo seu **nome** (dicionário) ou simplesmente perguntando se **está ou não está** (conjunto). Veja cada uma com um exemplo do `revisor` e, no final, em 4.1.5, há uma tabela para decidir.

#### 4.1.1 A lista: valores em ordem

Você já usou a lista mínima na Lição 3: o literal com colchetes, `len`, `.append` e `lista[i]`. Aqui ela é vista completa. Uma **lista** guarda valores em uma ordem, pode ser mudada e se escreve entre colchetes. Salve o programa seguinte como `fig04_01.py` na sua pasta `practica/` e execute:

```python
# fig04_01.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]
print(nombres[0], nombres[3])
print(nombres[-1], nombres[-2])
print(nombres[1:3])
print(len(nombres))
print("pagos" in nombres, "gateway" in nombres)

nombres.append("facturacion")
print(nombres)
ultimo = nombres.pop()
print(ultimo, len(nombres))

tiempos_ms = [142, 2300, 87]
print(sorted(tiempos_ms), tiempos_ms)
tiempos_ms.sort()
print(tiempos_ms)
print(sum(tiempos_ms), min(tiempos_ms), max(tiempos_ms))
```

```text
$ python fig04_01.py
catalogo reportes
reportes pagos
['inventario', 'pagos']
4
True False
['catalogo', 'inventario', 'pagos', 'reportes', 'facturacion']
facturacion 4
[87, 142, 2300] [142, 2300, 87]
[87, 142, 2300]
2529 87 2300
```

Linha por linha:

- `nombres[0]` e `nombres[3]` pedem o primeiro e o quarto elemento. As posições, que se chamam **índices**, começam em **0**: com quatro elementos as posições válidas são 0, 1, 2 e 3. Por isso a última posição de uma lista de `len(nombres)` elementos é `len(nombres) - 1`, e não `len(nombres)`.
- `nombres[-1]` e `nombres[-2]` contam a partir do final: `-1` é o último, `-2` o penúltimo. É a forma cômoda de pedir “o último” sem calcular nada.
- `nombres[1:3]` é uma **fatia** (em inglês, *slice*): os elementos desde a posição 1 **até a 3 sem incluí-la**, isto é, as posições 1 e 2. Devolve uma lista nova com `['inventario', 'pagos']`. O “sem incluir” é uma regra que desconcerta uma vez e depois se usa sem pensar: `nombres[1:3]` tem `3 - 1 = 2` elementos, e `nombres[0:len(nombres)]` é a lista inteira. [O tutorial do Python](https://docs.python.org/pt-br/3/tutorial/introduction.html#lists) explica as fatias com mais exemplos.
- `len(nombres)` você já conhece. Junto com `sorted`, `sum`, `min` e `max` é uma das **funções embutidas** (*built-in*): vêm com o Python e são usadas sem importar nada.
- `"pagos" in nombres` é outra forma de usar a palavra `in`, a mesma que você já viu em `for ... in`: aqui responde `True` ou `False` conforme o valor **esteja** na lista. Cuidado, que com uma lista o Python a confere elemento por elemento; com listas curtas tanto faz, e em 4.1.4 você verá uma coleção muito mais rápida para essa pergunta.
- `nombres.append("facturacion")` acrescenta no final, e **muda a lista que já existe** (não cria outra). `nombres.pop()` tira o último elemento e o devolve, de modo que `ultimo` vale `"facturacion"` e a lista volta a ter quatro. Que `append` e `pop` modifiquem a lista que já existe é o que significa “mutável”, e tem consequências que você verá em 4.3.
- `sorted(tiempos_ms)` devolve uma lista **nova** ordenada e deixa a original como estava: por isso a segunda parte da linha continua mostrando `[142, 2300, 87]`. Já `tiempos_ms.sort()` ordena **a própria lista** e não devolve nada (a rigor, devolve `None`). [A documentação diz assim](https://docs.python.org/pt-br/3/library/stdtypes.html#mutable-sequence-types): para lembrar que ele age “por efeito colateral”, o `sort` não devolve a lista ordenada, e para pedir uma nova existe o `sorted`. Essa distinção entre “muda a que tenho” e “me dá uma nova” reaparece em todo o Python, e vira uma armadilha comum (você a verá em “O que se faz errado”).
- `sum`, `min` e `max` somam, buscam o menor e buscam o maior dos números da lista: 87 + 142 + 2300 = 2529, que é a soma de tempos que você usará no resumo.

Uma lista pode misturar qualquer coisa: textos, números, outras listas. No `revisor` convém que cada lista guarde **uma só classe de coisa** (só nomes, ou só tempos), porque assim você sabe o que esperar de cada elemento e porque as anotações de tipo de 4.1.5 expressam isso facilmente.

Agora, o erro. Pedir uma posição que não existe:

```python
# fig04_02.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]
print(nombres[4])
```

```text
$ python fig04_02.py
Traceback (most recent call last):
  File "fig04_02.py", line 3, in <module>
    print(nombres[4])
          ~~~~~~~^^^
IndexError: list index out of range
```

Leia o *traceback* como você aprendeu na Lição 1: da última linha para cima. `IndexError: list index out of range` diz que o índice está fora do intervalo da lista. Em cima, o Python aponta a linha e marca com um traço de `~` e `^` a expressão que falhou: `nombres[4]`. A lista tem quatro elementos, com posições de 0 a 3, e a 4 não existe. É o mesmo erro que a Lição 3 dava quando uma das três listas paralelas era mais curta que as outras. (O Python escreve no *traceback* o caminho completo do seu arquivo; nesta lição eles são encurtados para `File "fig04_02.py"` para que o texto fique igual para todos, e na sua tela você verá o caminho tal como está no seu computador.)

#### 4.1.2 A tupla: um grupo fixo de valores

Uma **tupla** parece uma lista com parênteses em vez de colchetes, mas tem uma diferença que muda para que serve: **não pode ser mudada**. Uma vez criada, as suas posições ficam fixas. E a diferença de uso é mais funda que a sintática: a lista é “uma quantidade variável de coisas do mesmo tipo” (quatro nomes, ou vinte), enquanto a tupla é “uma quantidade **fixa** de coisas que cada uma significa algo diferente pela sua posição”. O resultado de revisar um serviço, por exemplo, é sempre três coisas: o código, o tempo e o erro, se houve.

```python
# fig04_03.py
resultado = (200, 142, None)
print(resultado[0], resultado[1])
codigo, tiempo_ms, error = resultado
print(f"código {codigo}, tiempo {tiempo_ms}, error {error}")
print(len(resultado))

pares = [("catalogo", 142), ("pagos", 87)]
for nombre, ms in pares:
    print(f"{nombre} respondió en {ms}ms")

uno = (200,)
no_es_tupla = 200
print(type(uno), type(no_es_tupla))
```

```text
$ python fig04_03.py
200 142
código 200, tiempo 142, error None
3
catalogo respondió en 142ms
pagos respondió en 87ms
<class 'tuple'> <class 'int'>
```

- `resultado = (200, 142, None)` cria uma tupla de três elementos. Lê-se com índices igual a uma lista: `resultado[0]` é o código.
- `codigo, tiempo_ms, error = resultado` **desempacota** (em inglês, *unpacking*), o mesmo que fazia `for i, nombre in enumerate(...)` na Lição 3, em que cada volta entregava um par, que na verdade é uma tupla de dois: reparte os três elementos da tupla entre três nomes, em ordem. É muito mais legível que `resultado[0]`, `resultado[1]`, `resultado[2]`, porque cada valor recebe um nome que diz o que é.
- O `for nombre, ms in pares:` é o mesmo desempacotamento do `enumerate`, agora com os seus próprios pares: cada elemento de `pares` é uma tupla de dois, e `nombre` e `ms` recebem as suas metades. Você vai vê-lo outra vez assim que chegar aos dicionários.
- Uma tupla de **um único elemento** exige a vírgula: `(200,)` é uma tupla; `(200)` são uns parênteses em volta de um número, e é simplesmente `200`, como mostra o `type` da última linha. [O tutorial avisa deste caso](https://docs.python.org/pt-br/3/tutorial/datastructures.html#tuples-and-sequences) como uma estranheza da sintaxe. Na prática você quase não vai escrevê-la, mas vai lê-la, e confundi-la não avisa.

Se a quantidade de nomes não coincide com a de elementos, o Python recusa em vez de repartir a mais ou a menos em silêncio:

<!-- frag: desempaque.py -->
```python
codigo, tiempo_ms = (200, 142, None)
```

Ao executá-lo, a última linha do *traceback*, que é a que importa, diz “valores demais para desempacotar”. No Python 3.12:

```text
ValueError: too many values to unpack (expected 2)
```

e no 3.14 acrescenta quantos recebeu:

```text
ValueError: too many values to unpack (expected 2, got 3)
```

Quando uma função devolve “várias coisas”, o que ela devolve é uma tupla: `return codigo, tiempo_ms` cria uma tupla de dois, e quem chama a desempacota com `codigo, tiempo_ms = f(...)`.

E o que acontece se você tenta mudar uma?

```python
# fig04_04.py
resultado = (200, 142, None)
resultado[0] = 500
```

```text
$ python fig04_04.py
Traceback (most recent call last):
  File "fig04_04.py", line 3, in <module>
    resultado[0] = 500
    ~~~~~~~~~^^^
TypeError: 'tuple' object does not support item assignment
```

`TypeError: 'tuple' object does not support item assignment`: “o objeto tupla não admite atribuir a uma posição”. Não é uma falha, é a garantia da tupla: o que ela guardou, fica. Se você precisa de outra com um valor diferente, cria outra tupla. Essa garantia é útil para dados que descrevem um fato que já ocorreu, como o resultado de uma revisão. Mas repare no custo: `resultado[1]` não diz que é o tempo; só a sua memória diz. Quando uma tupla cresce para cinco ou seis elementos, ninguém lembra qual é qual. Essa é a limitação que o `dataclass` da Lição 5 resolve.

#### 4.1.3 O dicionário: valores com nome

Pense no que o `revisar` precisa para o serviço `pagos`: não “o terceiro elemento”, e sim “os dados de `pagos`”. Um **dicionário** (`dict`) guarda pares **chave: valor** e se consulta pela chave. Escreve-se entre chaves, e a chave e o valor vão separados por dois-pontos.

```python
# fig04_05.py
tiempos_ms = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
print(tiempos_ms["pagos"])
print(len(tiempos_ms))
print("pagos" in tiempos_ms, "gateway" in tiempos_ms)

print(tiempos_ms.get("gateway"))
print(tiempos_ms.get("gateway", "sin dato"))
print(tiempos_ms.get("reportes"))
print("reportes" in tiempos_ms, tiempos_ms.get("reportes"), tiempos_ms.get("gateway"))

tiempos_ms["facturacion"] = 95
for nombre, ms in tiempos_ms.items():
    print(nombre, ms)

print(list(tiempos_ms))
print(list(tiempos_ms.values()))
```

```text
$ python fig04_05.py
87
4
True False
None
sin dato
None
True None None
catalogo 142
inventario 2300
pagos 87
reportes None
facturacion 95
['catalogo', 'inventario', 'pagos', 'reportes', 'facturacion']
[142, 2300, 87, None, 95]
```

- `tiempos_ms["pagos"]` busca a chave `"pagos"` e devolve o seu valor, 87. Ao contrário de uma lista, aqui não importa em que lugar está: importa como se chama. As chaves são únicas (um dicionário não pode ter duas vezes `"pagos"`); os valores podem se repetir e ser de qualquer classe, até `None`, como o de `reportes`.
- `len(tiempos_ms)` conta os pares. `"pagos" in tiempos_ms` pergunta se **a chave** existe (não o valor), e é rápida mesmo que o dicionário seja enorme.
- `tiempos_ms.get("gateway")` é a forma de perguntar com calma. Com colchetes, uma chave que não existe é um erro (você o provoca mais abaixo, em “O erro que você vai ver”); com `.get`, devolve `None` se não a encontra, ou o valor que você puser como segundo argumento: `.get("gateway", "sin dato")` devolve `"sin dato"`.
- Atenção à linha de `reportes`, que é a armadilha deste método. `.get("reportes")` devolve `None`... e `.get("gateway")` também. **A mesma resposta para duas situações diferentes:** uma chave que não existe, e uma chave que existe e vale `None`. A penúltima linha deixa isso à vista: `"reportes" in tiempos_ms` é `True` mas o seu `.get` é `None`; `"gateway"` não está e o seu `.get` também é `None`. Quando a diferença importa, pergunta-se primeiro com `in`.
- `tiempos_ms["facturacion"] = 95` **acrescenta** um par se a chave não existia (e se existia, substitui o valor dela). Os dicionários, como as listas, podem ser mudados.
- `tiempos_ms.items()` entrega os pares um por um, cada um como uma tupla `(chave, valor)` (igual a como o `enumerate` entregava pares), e o `for nombre, ms in ...` os desempacota, como você viu na seção anterior. Os dicionários **lembram a ordem em que você acrescentou as chaves**: [a documentação garante](https://docs.python.org/pt-br/3/library/stdtypes.html#mapping-types-dict) (“dicionários preservam a ordem de inserção”), por isso `facturacion` sai no final.
- `list(tiempos_ms)` converte em lista o que se obtém ao percorrer o dicionário diretamente, e isso são **as chaves**. É importante lembrar: `for nombre in tiempos_ms:` percorre nomes, não pares. `tiempos_ms.values()` entrega os valores, e existe `tiempos_ms.keys()` para as chaves, mas quase nunca é preciso escrevê-lo.

Uma restrição que convém saber desde já: a chave de um dicionário deve ser algo que não mude. Textos, números e tuplas deles servem; uma lista não serve como chave. [O glossário chama de **hasheável**](https://docs.python.org/pt-br/3/glossary.html#term-hashable) (*hashable*) o que pode ser usado assim. Tentar isso dá um `TypeError: unhashable type: 'list'`, que você verá em 4.1.4 junto ao conjunto.

#### 4.1.4 O conjunto: “já vi?”

Um **conjunto** (`set`) guarda valores **sem repetir e sem ordem**. Serve para duas coisas: tirar repetidos, e perguntar “este valor está aí?” muito rápido. Quando você escreve `{"catalogo", "pagos"}`, com chaves e sem dois-pontos, é um conjunto.

```python
# fig04_06.py
registrados = ["catalogo", "pagos", "catalogo", "reportes", "pagos"]
unicos = set(registrados)
print(len(registrados), len(unicos))
print(sorted(unicos))

arriba = {"catalogo", "pagos"}
todos = {"catalogo", "inventario", "pagos", "reportes"}
print("pagos" in arriba)
print(sorted(todos - arriba))
print(sorted(todos & arriba))
print(sorted(arriba | {"gateway"}))
arriba.add("pagos")
arriba.add("inventario")
print(sorted(arriba))
print(type({}), type(set()))
```

```text
$ python fig04_06.py
5 3
['catalogo', 'pagos', 'reportes']
True
['inventario', 'reportes']
['catalogo', 'pagos']
['catalogo', 'gateway', 'pagos']
['catalogo', 'inventario', 'pagos']
<class 'dict'> <class 'set'>
```

- `set(registrados)` converte a lista em um conjunto e, de passagem, descarta as repetições: cinco nomes registrados, três diferentes. Esta é a forma mais curta de contar “quantos valores diferentes há”.
- O conjunto é impresso dentro de `sorted(...)` de propósito, e não é um enfeite: **um conjunto não tem ordem**, e para os textos a ordem em que o Python os mostra muda de uma execução para outra, porque [a documentação da linguagem explica](https://docs.python.org/pt-br/3/reference/datamodel.html#object.__hash__) que os valores `hash` dos textos levam um “sal” imprevisível que muda cada vez que o Python inicia. Ao medi-lo para esta lição, o mesmo conjunto `{"catalogo", "inventario", "pagos", "reportes"}` saiu em ordens diferentes de uma execução para outra, e por isso você verá `sorted` em cada impressão de um conjunto: para que a saída seja sempre a mesma. Regra prática: **nunca confie na ordem de um conjunto; se você precisa de ordem, converta com `sorted`**.
- Os operadores entre conjuntos são os da matemática: `-` é a **diferença** (o que está em um e não no outro: os que não estão no ar), `&` a **interseção** (o que está nos dois) e `|` a **união** (tudo o de ambos). `.add` acrescenta um valor e não acontece nada se ele já estava, que é justamente a graça: `arriba.add("pagos")` não duplica nada.
- A última linha é uma armadilha clássica. **`{}` vazio não é um conjunto vazio, é um dicionário vazio**: a sintaxe de chaves foi usada primeiro para dicionários. Para um conjunto vazio, `set()`. [O tutorial destaca isso](https://docs.python.org/pt-br/3/tutorial/datastructures.html#sets) e o `type` de cima o comprova.

Os elementos de um conjunto também devem ser hasheáveis, pela mesma razão que as chaves do dicionário: o Python os coloca segundo um número calculado do seu valor, e se o valor pudesse mudar, esse número também mudaria. Se você tenta pôr uma lista, a mensagem muda entre versões, e vale a pena ver as duas:

<!-- frag: hashable.py -->
```python
datos = {["catalogo"]: 1}
```

No Python 3.12 a última linha é esta:

```text
TypeError: unhashable type: 'list'
```

E no 3.14, que redige melhor o aviso, diz:

```text
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

As duas significam o mesmo: uma lista não pode ser chave. O que você deve lembrar é a palavra `unhashable`.

Um uso real no `revisor`: detectar nomes repetidos. Um conjunto de “os que já vi” e outro de “os que se repetem” resolvem isso em um único percurso. Mas essa função usa anotações de tipo para coleções, que é o que vem a seguir.

#### 4.1.5 Anotar as coleções e escolher a correta

Na Lição 3 você anotou tipos simples: `int`, `str`, `int | None`. Com coleções se acrescenta **de quê** é a coleção, entre colchetes: `list[str]` é “lista de textos”, `set[str]` é “conjunto de textos”, `dict[str, int | None]` é “dicionário cujas chaves são textos e cujos valores são inteiros ou `None`”, e `tuple[int | None, int | None, str | None]` é “tupla de três elementos: um inteiro ou `None`, outro inteiro ou `None`, e um texto ou `None`” (a tupla anota **cada posição**, porque cada uma significa algo). Lembre o que você aprendeu na Lição 0: o Python **não obriga** que as anotações sejam cumpridas na execução. São documentação que outra pessoa pode conferir (na Lição 8, o `mypy`); hoje servem para que o código diga o que espera.

Aqui está a função que detecta nomes repetidos, com anotações, e é a mesma que o modelo do `revisor` usará na Lição 5:

```python
# fig04_07.py
def nombres_repetidos(nombres: list[str]) -> set[str]:
    vistos: set[str] = set()
    repetidos: set[str] = set()
    for nombre in nombres:
        if nombre in vistos:
            repetidos.add(nombre)
        vistos.add(nombre)
    return repetidos


print(sorted(nombres_repetidos(["catalogo", "pagos", "catalogo", "reportes", "pagos"])))
print(sorted(nombres_repetidos(["catalogo", "inventario", "pagos", "reportes"])))
```

```text
$ python fig04_07.py
['catalogo', 'pagos']
[]
```

`vistos: set[str] = set()` anota uma variável ao criá-la: a sintaxe é `nombre: tipo = valor`. A anotação é necessária porque `set()` sozinho não diz de que é o conjunto. Para cada nome: se já estava em `vistos`, é acrescentado a `repetidos`; em qualquer caso é acrescentado a `vistos`. A segunda chamada devolve um conjunto vazio, que o `sorted` mostra como `[]`. Observe que a pergunta `nombre in vistos` é feita com um conjunto: seria igualmente correta com uma lista, mas com milhares de nomes o conjunto responde de imediato e a lista teria que conferi-los um por um.

Qual usar? Esta tabela você pode consultar toda vez que duvidar; quase sempre a resposta sai da primeira coluna.

| Se o que você guarda é... | Use | Busca-se por | Pode ser mudado? | Exemplo no `revisor` |
|---|---|---|---|---|
| uma quantidade variável de coisas do mesmo tipo, em uma ordem | `list` | posição | sim | os serviços a revisar |
| uma quantidade fixa de coisas, cada posição com o seu significado | `tuple` | posição | não | o trio (código, tempo, erro) |
| dados que se pedem por nome | `dict` | chave | sim | o tempo de cada serviço pelo seu nome |
| valores únicos, sem ordem, dos quais você pergunta “está aí?” | `set` | pertinência | sim | os nomes já vistos |

Se você duvida entre `list` e `set`, pergunte se a ordem importa ou se pode haver repetidos. Se duvida entre `dict` e `list`, pergunte se vai buscar por posição ou por nome. E se você se descobre escrevendo `resultado[2]` e tem que lembrar o que era o 2, é o sinal de que precisa de um nome para isso, que é o tema da Lição 5.

### 4.2 Compreensões

Montar uma lista nova a partir de outra é das tarefas mais comuns de um programa, e se escreve sempre igual: cria-se uma lista vazia, percorre-se a original, decide-se se cada elemento entra e acrescenta-se com `.append`. O Python tem uma forma compacta para isso, a **compreensão** (em inglês, *comprehension*). Veja as duas versões do mesmo trabalho:

```python
# fig04_08.py
tiempos_ms = [142, 2300, 87]

lentos: list[int] = []
for tiempo_ms in tiempos_ms:
    if tiempo_ms >= 1000:
        lentos.append(tiempo_ms)
print(lentos)

lentos = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms >= 1000]
print(lentos)

textos = [f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]
print(textos)
print(", ".join(textos))

por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
respondieron = {nombre: ms for nombre, ms in por_servicio.items() if ms is not None}
print(respondieron)
sin_respuesta = {nombre for nombre, ms in por_servicio.items() if ms is None}
print(sin_respuesta)
promedio_ms = round(sum(respondieron.values()) / len(respondieron))
print(promedio_ms)
```

```text
$ python fig04_08.py
[2300]
[2300]
['142ms', '2300ms', '87ms']
142ms, 2300ms, 87ms
{'catalogo': 142, 'inventario': 2300, 'pagos': 87}
{'reportes'}
843
```

A primeira metade é o laço de sempre: cria `lentos` vazia (anotada como lista de inteiros), percorre, filtra com `if` e acrescenta. A segunda metade faz o mesmo em **uma linha**:

```text
[ tiempo_ms   for tiempo_ms in tiempos_ms   if tiempo_ms >= 1000 ]
  ^qué pones   ^de dónde sale               ^condición (opcional)
```

Lê-se quase como uma frase: “monte uma lista com `tiempo_ms`, para cada `tiempo_ms` em `tiempos_ms`, se `tiempo_ms >= 1000`”. Tem três partes: **o que se põe** na lista nova (pode ser o mesmo elemento ou uma transformação dele, como `f"{tiempo_ms}ms"`), **de onde sai** (o `for`) e, opcional, **a condição** que decide se entra. [O tutorial do Python](https://docs.python.org/pt-br/3/tutorial/datastructures.html#list-comprehensions) a apresenta com a mesma estrutura. A variável do `for` vive só dentro da compreensão e não atrapalha do lado de fora.

Linha por linha do resto:

- `[f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]` não tem condição: transforma cada número em um texto. É uma versão simples do que fazia `formatear_tiempo` na Lição 3.
- `", ".join(textos)` é um método de texto novo: **une** os textos de uma lista pondo entre eles o texto sobre o qual é chamado. Aqui, uma vírgula e um espaço. Você vai precisar dele no resumo do `revisor`.
- Com chaves e um `chave: valor` se obtém uma **compreensão de dicionário**: `{nombre: ms for nombre, ms in por_servicio.items() if ms is not None}` constrói um dicionário novo com os serviços que têm tempo. Repare que a pergunta correta sobre `None` continua sendo `is not None`, como você aprendeu nas lições 2 e 3.
- Com chaves e um só valor se obtém uma **compreensão de conjunto**: os nomes cujo tempo é `None`. Só `reportes`.
- A última linha é a média real do resumo. `respondieron.values()` são os tempos dos que responderam (142, 2300 e 87); `sum(...)` os soma (2529); `len(respondieron)` é 3; a barra `/` divide e **sempre dá um número com decimais**, 843.0; e `round(...)` o arredonda para o inteiro mais próximo, 843. Todas as médias do curso são calculadas assim, sobre os que responderam: o quarto serviço não tem tempo para calcular a média. Uma nota sobre o `round`: quando o decimal é exatamente `.5`, [o Python arredonda para o inteiro **par**](https://docs.python.org/pt-br/3/library/functions.html#round), então `round(0.5)` é 0, `round(1.5)` é 2 e `round(2.5)` também é 2.

<!-- frag: redondeo.py -->
```python
print(round(0.5), round(1.5), round(2.5))
```

```text
0 2 2
```

(Para o `revisor` não importa, porque 2529 / 3 é exato, mas convém ter visto uma vez: é daquelas coisas que, se você não sabe, fazem você procurar um erro que não existe.)

Quando não usar uma compreensão? Quando ela fica difícil de ler. Uma condição simples ou uma transformação simples cabem bem; dois `for` aninhados ou três condições, não: nesse caso escreva o laço, que pode ser lido linha por linha. E nunca use uma compreensão só pelo que ela faz por fora (por exemplo, para chamar `print` em cada elemento): uma compreensão serve para **construir um valor**, não para executar ações.

> **Aqui termina a primeira sessão.** Você tem as quatro coleções e as compreensões: tudo o que é preciso para **guardar** os dados de outra maneira. Antes da segunda sessão, execute de novo as figuras de 4.1 e 4.2 e mude algo em cada uma (outro serviço, outra condição na compreensão) para prever o resultado antes de vê-lo. A segunda sessão trata do que surpreende ao **compartilhar** esses dados, e termina com o `revisor` sem listas paralelas.

### 4.3 Cópia contra referência, e não mudar o que se percorre

Esta seção explica o tropeço mais frequente de quem vem de outras linguagens, e o que mais tempo faz perder quando não se conhece. Chega agora porque só faz sentido quando você já tem listas e dicionários que podem ser mudados.

#### 4.3.1 Um nome é um rótulo, não uma caixa

Quando você escreve `a = [1, 2]`, o Python faz duas coisas: **cria** a lista em algum lugar da memória e **põe o rótulo `a`** nela. O rótulo não contém a lista; ele a **aponta**. Se depois você escreve `b = a`, não se cria uma segunda lista: põe-se um segundo rótulo, `b`, na **mesma**. Há uma lista e dois nomes para ela. (Na Lição 3, ao comparar `==` com `is`, você viu de passagem que `c = a` não copia a lista; aqui se vê que consequências isso tem quando essa lista muda.) [A documentação oficial explica](https://docs.python.org/pt-br/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) com este mesmo caso: as variáveis são nomes que se referem a objetos, e atribuir uma variável a outra não copia o objeto.

```python
# fig04_09.py
principales = ["catalogo", "pagos"]
respaldo = principales
respaldo.append("reportes")
print(principales)
print(principales is respaldo)

copia = principales.copy()
copia.append("inventario")
print(principales)
print(copia)
print(principales is copia)

a = 5
b = a
b = b + 1
print(a, b)
```

```text
$ python fig04_09.py
['catalogo', 'pagos', 'reportes']
True
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes', 'inventario']
False
5 6
```

- `respaldo = principales` põe um segundo rótulo. Ao fazer `respaldo.append("reportes")`, a lista **única** cresce, e por isso `principales` também já traz `reportes`. Ninguém “mexeu” em `principales`: é a mesma lista vista com outro nome. O `is` que você viu na Lição 3 confirma: `principales is respaldo` é `True` (são o mesmo objeto, não dois iguais).
- `principales.copy()` cria uma lista **nova** com os mesmos elementos. Agora sim há duas: acrescentar `inventario` a `copia` não mexe em `principales`, e `principales is copia` é `False`. Há outras duas formas de obter o mesmo, `list(principales)` e `principales[:]` (uma fatia completa); as três dão uma cópia. Use a que se leia mais claro, e neste curso é `.copy()`.
- Por que então `a = 5; b = a; b = b + 1` não deixa `a` em 6? Porque `b + 1` **não muda o 5**: cria um número novo, o 6, e move o rótulo `b` para ele. Os números e os textos são imutáveis: não há forma de mudá-los por dentro, então compartilhá-los entre dois nomes é inofensivo. A tupla também é, com um matiz: não deixa mudar o que há em cada posição, mas se uma posição guarda uma lista, **essa lista** sim pode mudar, e a tupla compartilhada “muda” com ela (`t = ([142], 87)` seguido de `t[0].append(5)` é válido). As tuplas do `revisor` só guardam números, textos e `None`, então para elas compartilhar é inofensivo. O perigo está no **mutável**: a lista, o dicionário e o conjunto, e tudo o que os leve dentro.

Um caso em que isso surpreende, e com o qual você já topou na Lição 3: **uma função que recebe uma lista recebe a própria lista, não uma cópia**.

```python
# fig04_10.py
def agregar_reportes(nombres: list[str]) -> None:
    nombres.append("reportes")


base = ["catalogo", "pagos"]
agregar_reportes(base)
print(base)
```

```text
$ python fig04_10.py
['catalogo', 'pagos', 'reportes']
```

A função não devolveu nada e no entanto `base` mudou. É exatamente o mecanismo da lista que “lembrava” das chamadas anteriores (`registrar_caido`, na Lição 3): o valor padrão `[]` era uma única lista, criada uma vez, que todas as chamadas compartilhavam. Com o de hoje você pode dizer de uma vez: uma função que recebe uma lista pode mudá-la, e isso é uma decisão de design que precisa ser tomada de olhos abertos. A convenção do Python segue o exemplo de `sort` e `sorted`: os métodos que **mudam** uma coleção (`append`, `sort`, `remove`) devolvem `None`, para que você não os confunda com os que devolvem algo novo, e os que devolvem algo novo (`sorted`, `copy`) não mexem no que receberam. A exceção útil é `pop`, que tira um elemento e além disso o devolve.

#### 4.3.2 Cópia rasa e cópia profunda

`.copy()` copia a lista de fora, mas **não copia o que a lista guarda**: se dentro há outras listas, a cópia e a original compartilham essas listas de dentro. A isso se chama cópia **rasa** (*shallow*); a alternativa é a **profunda** (*deep*), que copia também o de dentro, e é oferecida pelo módulo `copy` (traz-se com `import copy`, como você aprendeu na Lição 3). [A documentação dele define a diferença](https://docs.python.org/pt-br/3/library/copy.html): a rasa insere referências aos mesmos objetos; a profunda insere cópias, de forma recursiva.

```python
# fig04_11.py
import copy

grupos = [["catalogo", "pagos"], ["reportes"]]
superficial = grupos.copy()
superficial[1].append("inventario")
print(grupos)
print(grupos[1] is superficial[1])

grupos = [["catalogo", "pagos"], ["reportes"]]
profunda = copy.deepcopy(grupos)
profunda[1].append("inventario")
print(grupos)
print(profunda)
```

```text
$ python fig04_11.py
[['catalogo', 'pagos'], ['reportes', 'inventario']]
True
[['catalogo', 'pagos'], ['reportes']]
[['catalogo', 'pagos'], ['reportes', 'inventario']]
```

Com a cópia rasa, acrescentar a `superficial[1]` mudou também `grupos[1]`: as duas listas de fora são diferentes, mas a lista de dentro é **a mesma**, e o `is` confirma. Com `copy.deepcopy`, a de dentro também foi copiada, e `grupos` ficou intacta. Não use `deepcopy` por reflexo: copia tudo o que alcança, é mais lenta, e às vezes copia a mais o que devia ser compartilhado. Use-a quando você realmente precisar de duas estruturas aninhadas independentes. No `revisor` raramente será necessária, porque (você verá na Lição 5) os dados importantes não serão mudados: serão **substituídos** por outros.

#### 4.3.3 Não mude o que você está percorrendo

A última consequência do mutável é a mais traiçoeira, porque **não dá erro**. Se você tira elementos de uma lista enquanto a percorre com `for`, o percurso se desmonta. Tire os serviços cujo tempo é menor que 100 ms. (Para tirar um valor de uma lista usa-se `.remove(valor)`, que apaga a primeira ocorrência desse valor.)

```python
# fig04_12.py
tiempos_ms = [142, 2300, 87, 95]
for tiempo_ms in tiempos_ms:
    if tiempo_ms < 100:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

```text
$ python fig04_12.py
[142, 2300, 95]
```

Havia dois valores menores que 100, o 87 e o 95, e só o 87 foi tirado: o 95 ficou. Nenhuma linha falhou, e o resultado é incorreto. A razão: o `for` percorre a lista **por posição**, com um contador interno. Quando chega à posição 2 e vê o 87, o tira; os elementos que vinham depois se deslocam um lugar para a esquerda, o 95 passa a ocupar a posição 2, e o `for` segue com a posição 3, que já não existe. O 95 nunca é examinado, e ninguém avisa. [O próprio tutorial do Python previne disso](https://docs.python.org/pt-br/3/tutorial/controlflow.html#for-statements): o código que modifica uma coleção enquanto a percorre é difícil de acertar, e o mais simples é percorrer uma cópia ou montar uma coleção nova. Montar uma coleção nova é justamente o que faz uma compreensão:

```python
# fig04_13.py
tiempos_ms = [142, 2300, 87, 95]
rapidos = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms >= 100]
print(rapidos)
print(tiempos_ms)
```

```text
$ python fig04_13.py
[142, 2300]
[142, 2300, 87, 95]
```

Agora o resultado é o correto e, de brinde, a lista original fica como estava. Com um dicionário, o descuido de **acrescentar ou tirar chaves** enquanto o percorre sim dá erro, porque o Python o detecta:

```python
# fig04_14.py
tiempos_ms = {"catalogo": 142, "pagos": 87}
for nombre in tiempos_ms:
    tiempos_ms[nombre + "-copia"] = 0
```

```text
$ python fig04_14.py
Traceback (most recent call last):
  File "fig04_14.py", line 3, in <module>
    for nombre in tiempos_ms:
                  ^^^^^^^^^^
RuntimeError: dictionary changed size during iteration
```

`RuntimeError: dictionary changed size during iteration`: “o dicionário mudou de tamanho durante o percurso”. O `for nombre in tiempos_ms` percorre as chaves, e dentro você acrescentou uma; o Python percebeu e parou. Repare na palavra *tamanho*: mudar o **valor** de uma chave que já existe (`tiempos_ms[nombre] = 0`) não muda quantas chaves há e não dá erro; o que falha é acrescentar ou apagar chaves. As soluções são as mesmas: percorrer uma cópia (`for nombre in list(tiempos_ms):`) ou construir um dicionário novo com uma compreensão.

#### Antes do projeto

Antes de ir ao projeto, confira que você consegue fazer isto sem olhar a lição; é também o que dará fluidez ao que vem a seguir:

- Escrever um dicionário com os quatro serviços e seus tempos, ler um com colchetes e outro com `.get`, e explicar por que o `.get` de uma chave que vale `None` engana.
- Escrever uma compreensão que filtre uma lista, e a mesma coisa como laço.
- Dizer em voz alta o que imprime `b = a; b.append(1); print(a)` se `a` é uma lista, e o que muda se `a` é um número.
- Explicar por que `sorted(x)` e `x.sort()` não são a mesma coisa.

Com isso na mão, o projeto de hoje se lê sem surpresas.

### 4.4 O passo do projeto: o `revisor` sem listas paralelas

Junte o de hoje no projeto. A mudança vive inteira em `revisor.py`. O `formato.py` fica exatamente como a Lição 3 o deixou, porque o trabalho dele (dar forma de texto a um nome, um estado, um tempo e um detalhe) não mudou; é repetido aqui só para que a pasta da figura esteja completa:

```python
# fig04_15/formato.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(nombre: str, estado: str, tiempo_ms: int | None, detalle: str) -> str:
    tiempo = formatear_tiempo(tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

```python
# fig04_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
SERVICIOS = ["catalogo", "inventario", "pagos", "reportes"]
SIMULADO: dict[str, tuple[int | None, int | None, str | None]] = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str) -> str:
    sin_respuesta = (None, None, "sin conexión")
    codigo, tiempo_ms, error = SIMULADO.get(nombre, sin_respuesta)
    if codigo is not None:
        detalle = str(codigo)
    elif error is not None:
        detalle = error
    else:
        detalle = "sin conexión"
    estado = clasificar(codigo, tiempo_ms)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    renglones = [revisar(nombre) for nombre in SERVICIOS]
    print(encabezado())
    for renglon in renglones:
        print(renglon)


if __name__ == "__main__":
    main()
```

Leia o `revisor.py` por partes.

**Os dados.** Em vez das três listas há duas constantes. `SERVICIOS` é uma **lista** de nomes: os serviços que você quer revisar, na ordem em que quer vê-los na tabela. É uma lista porque a ordem importa e porque a quantidade pode crescer. `SIMULADO` é um **dicionário** que, para cada nome, guarda uma **tupla de três** com o que esse serviço “respondeu”: `(código, tiempo_ms, erro)`. É uma tupla porque são três coisas fixas que viajam sempre juntas e cada posição significa algo diferente, e a anotação `dict[str, tuple[int | None, int | None, str | None]]` diz isso com uma posição por elemento, como você viu em 4.1.5. A de `reportes` é `(None, None, "sin conexión")`: não houve código nem tempo, e o terceiro elemento conta por quê. Repare no que você ganhou: os três dados de `inventario` estão em **uma única linha**, sob o seu nome. Já não há como o código dele ficar emparelhado com o tempo de outro serviço.

Por que duas constantes e não uma? Porque respondem perguntas diferentes e vão seguir caminhos diferentes. `SERVICIOS` é **o que você quer revisar**: na Lição 6 deixará de estar escrito no código e será lido de um arquivo. `SIMULADO` faz o papel da **rede**: é o que cada serviço responde enquanto o programa ainda não sabe perguntar de verdade, e na Lição 9, quando o `revisor` consultar cada serviço, desaparece. Separá-los já ensina algo desde hoje: um serviço que está em `SERVICIOS` e não está em `SIMULADO` é um serviço que não respondeu.

**`revisar`** mudou de assinatura. Antes recebia o nome, o código e o tempo, que o `main` tinha que tirar de três listas na mesma posição; agora recebe **só o nome** e busca o resto por conta própria. A busca é `SIMULADO.get(nombre, sin_respuesta)`, com `.get` **de propósito**: um nome que não esteja em `SIMULADO` não é um engano do programa e sim um serviço do qual não há dados, e é tratado como fora do ar “sin conexión”. Por isso o valor padrão, `sin_respuesta`, é a mesma tupla que a de `reportes`. É o critério de 4.1.3: `.get` quando a ausência é um caso previsto, colchetes quando não deveria ocorrer. Depois, `codigo, tiempo_ms, error = ...` desempacota a tupla em três nomes (4.1.2), e o detalhe é decidido com a regra da Lição 2, ampliada com o terceiro dado: o código como texto se houve resposta; se não, o texto do erro; e se tampouco há erro, “sin conexión”. `clasificar` não mudou nem uma letra.

**`main`** monta primeiro a lista de linhas com uma compreensão, `[revisar(nombre) for nombre in SERVICIOS]` (4.2), e depois a imprime sob o cabeçalho. O percurso já não usa `range(len(...))` nem posições: percorre os nomes, um por um, como o primeiro `for` da Lição 3. E a ordem da tabela é a de `SERVICIOS`, não a de `SIMULADO`: quem decide o que se mostra e em que ordem é a lista do que você quer revisar.

Execute o projeto a partir da sua pasta:

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

A mesma tabela da Lição 3, como foi prometido. Compare-a com o exercício 1 daquela lição, o de `facturacion`: lá era preciso mexer em três listas na mesma ordem, e um esquecimento produzia um `IndexError` ou, pior, uma linha com dados de outro serviço. Agora um serviço é um nome em `SERVICIOS` e uma linha em `SIMULADO`, e se você esquece a linha, o serviço aparece como fora do ar “sin conexión”, que é a verdade: não há dados dele. Você confere isso no exercício 3.

Fica algo incômodo, e é o ponto de partida da Lição 5. Olhe a linha `codigo, tiempo_ms, error = SIMULADO.get(...)`: a tupla não diz o que é cada posição; só a sua memória diz. E `clasificar` continua devolvendo um texto, `"ARRIBA"`, `"LENTO"` ou `"CAIDO"`, que nada impede de escrever errado. Dar a cada coisa do problema um nome próprio que o Python reconheça é o tema da lição seguinte. Ali chega também a linha do resumo (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`): você já saberia contá-la com as compreensões de hoje, mas fica mais clara quando cada resultado for uma única coisa com nome.

## O erro que você vai ver

Nas seções anteriores você já provocou vários erros no lugar onde nascem (`IndexError`, `TypeError`, `ValueError`, `RuntimeError`). Aqui vai o que você mais vai encontrar ao trabalhar com dicionários, e no final uma tabela para reconhecê-los todos de relance.

### `KeyError: 'catalgo'`

Pedir a um dicionário uma chave que ele não tem. Escreva `catalgo` em vez de `catalogo`:

```python
# fig04_16.py
SIMULADO = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}
codigo, tiempo_ms, error = SIMULADO["catalgo"]
print(codigo, tiempo_ms, error)
```

```text
$ python fig04_16.py
Traceback (most recent call last):
  File "fig04_16.py", line 8, in <module>
    codigo, tiempo_ms, error = SIMULADO["catalgo"]
                               ~~~~~~~~^^^^^^^^^^^
KeyError: 'catalgo'
```

Leia de baixo para cima, como sempre. **A última linha:** `KeyError: 'catalgo'`. O tipo é `KeyError` (um erro de chave) e o texto entre aspas é **a chave que foi pedida e não existe**, tal qual você a escreveu; se você a compara com as chaves do dicionário, o erro de digitação salta aos olhos. **Uma linha acima:** o programa, com um traço de `~` e `^` sob a expressão que falhou, `SIMULADO["catalgo"]`. **Mais acima:** a linha e o arquivo. Aqui não há nenhuma função no meio, então o *traceback* é curto; com funções chamando umas às outras, seriam mais linhas, e se lê igual: a causa imediata está no final.

Duas perguntas antes de corrigir. A primeira: a chave deveria existir? Se sim, é um erro de digitação ou de dados, e o `KeyError` é **justamente o que você quer**: o programa parou no lugar exato do engano, sem deixar que um valor falso continuasse avançando. A segunda: é normal que às vezes não exista? Então o dicionário não se consulta com colchetes, e sim com `.get(chave, valor_padrão)` ou com um `in` prévio. Essa é a razão pela qual `revisar`, em 4.4, usa `.get`: um serviço que não tem dados simulados é um caso previsto. O que você **não** deve fazer é usar `.get` em toda parte “por via das dúvidas”: troca um erro claro por um `None` que falhará mais tarde e mais longe (a Lição 5 começa justamente com um caso assim). Capturar o erro com `try`/`except` é o tema da Lição 6.

### Os erros desta lição de relance

Quando um aparecer para você, procure aqui a última linha. Todos saíram das execuções desta lição.

| A última linha diz... | O que aconteceu | Onde você viu |
|---|---|---|
| `IndexError: list index out of range` | você pediu uma posição que não existe na lista | 4.1.1 |
| `KeyError: 'catalgo'` | você pediu uma chave que o dicionário não tem | acima |
| `TypeError: 'tuple' object does not support item assignment` | você quis mudar um elemento de uma tupla | 4.1.2 |
| `ValueError: too many values to unpack (expected 2...` | você desempacotou em mais ou menos nomes que elementos | 4.1.2 |
| `TypeError: unhashable type: 'list'` | você usou uma lista como chave ou elemento de conjunto | 4.1.4 |
| `RuntimeError: dictionary changed size during iteration` | você mudou o tamanho de um dicionário enquanto o percorria | 4.3.3 |

Os textos da tabela são os do Python 3.12, o do seu Mint. Dois mudam no 3.14, embora o erro seja o mesmo: o de desempacotar acrescenta quantos havia, `ValueError: too many values to unpack (expected 2, got 3)`, e o da lista como chave diz onde você a usou: `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')` (ou `as a set element`, se foi em um conjunto).

## O que se faz errado

Cada um destes descuidos tem um custo concreto, e a maioria não dá erro na primeira vez.

**Manter listas paralelas.** Três listas que se correspondem por posição se desencaixam com um esquecimento, e o sintoma aparece longe da causa: um `IndexError` no meio da tabela, ou uma linha com o tempo de outro serviço. O custo é o dia que se perde procurando por que o serviço número 4 diz 87 ms. Uma entrada por serviço em um dicionário, com os seus dados juntos, evita isso desde o design.

**Guardar o resultado de `.sort()`.** `.sort()` ordena a lista que já existe e devolve `None`. Quem escreve `ordenados = tiempos_ms.sort()` obtém uma variável que vale `None`, e o erro aparece onde ela for usada:

```python
# fig04_17.py
tiempos_ms = [142, 2300, 87]
ordenados = tiempos_ms.sort()
print(ordenados)
print(tiempos_ms)
```

```text
$ python fig04_17.py
None
[87, 142, 2300]
```

A lista sim ficou ordenada (a segunda linha), mas `ordenados` não a contém. Se for preciso uma cópia ordenada, `sorted(tiempos_ms)`; se for preciso ordenar a própria, `tiempos_ms.sort()` **sem** atribuir.

**Usar `.get` para tudo.** Troca um erro claro (`KeyError`, com a chave que falhou) por um `None` que se propaga e estoura mais tarde, em outro lugar e com outra mensagem. Use-o quando a ausência é um caso previsto, não para calar erros.

**Escrever `{}` esperando um conjunto vazio.** É um dicionário vazio, e a falha chega depois, na primeira operação de conjunto:

<!-- frag: llaves_vacias.py -->
```python
vistos = {}
vistos.add("catalogo")
```

A última linha do *traceback* diz:

```text
AttributeError: 'dict' object has no attribute 'add'
```

A forma correta é `vistos: set[str] = set()`. Um conjunto vazio se escreve com `set()`.

**Confiar na ordem de um conjunto.** Funciona “na maioria das vezes” nos testes de uma máquina e falha em outra, porque a ordem dos textos muda entre execuções. Se a ordem importa, `sorted(...)`. Se importa a ordem de chegada, uma lista ou um dicionário (que sim lembra a ordem de inserção).

**Copiar com `=`.** `respaldo = principales` não faz uma cópia: põe um segundo nome. O custo é modificar dados “de outro” sem perceber, e que o defeito apareça em um lugar que você não tocou. Para copiar, `.copy()`; para copiar o que está aninhado, `copy.deepcopy`.

**Mudar uma coleção enquanto a percorre.** Com uma lista não falha e pula elementos (4.3.3); com um dicionário, acrescentar ou tirar chaves falha com `RuntimeError`. Percorra uma cópia ou monte uma coleção nova com uma compreensão.

**Compreensões ilegíveis.** Uma compreensão com dois `for` e três condições cabe em uma linha mas não cabe na cabeça de quem a lê. Se você precisa lê-la duas vezes, é um laço. O custo é de manutenção: quem mexer nela depois (você, daqui a três meses) vai reescrevê-la.

**Uma tupla longa em vez de um nome.** Uma tupla de três elementos se lembra; uma de seis, não, e `resultado[4]` acaba significando o que cada um acredita. Se você se descobre escrevendo um comentário para lembrar o que é cada posição, é o sinal de que esses dados merecem um nome próprio, que é o que a Lição 5 traz.

## Exercícios

Tente cada um antes de olhar as soluções.

### Exercício 1 — Preveja, execute e corrija

Antes de executar qualquer coisa, **escreva no papel** o que cada `print` deste programa imprime. Depois execute-o na sua pasta `practica/` e compare com a sua previsão.

<!-- frag: ej1a.py -->
```python
a = ["catalogo", "pagos"]
b = a
b.append("reportes")
c = list(a)
c.remove("pagos")
print(a)
print(b)
print(c)
print(a is b, a is c)
```

Depois, este percurso tem o defeito de 4.3.3, mas com valores `None`. Preveja o que imprime, explique por que sai assim e corrija-o com uma compreensão.

<!-- frag: ej1b.py -->
```python
tiempos_ms = [142, None, None, 87]
for tiempo_ms in tiempos_ms:
    if tiempo_ms is None:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

### Exercício 2 — Três perguntas ao dicionário

Com este dicionário, escreva três compreensões: (a) a **lista** de nomes dos serviços cujo tempo é 1000 ms ou mais; (b) um **dicionário** com o tempo em segundos (milissegundos divididos por 1000) dos serviços que responderam; (c) o **conjunto** de nomes sem resposta. Cuide para que nenhuma compare `None` com um número.

<!-- frag: ej2_datos.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
```

### Exercício 3 — Um serviço a mais, e um esquecimento de propósito

Trabalhe sobre o `revisor` de 4.4. (a) Acrescente `"facturacion"` ao final de `SERVICIOS`, **sem** mexer em `SIMULADO`, e antes de executar preveja a linha dele. (b) Agora acrescente a `SIMULADO` a entrada de `facturacion`, que responde com o código 503 em 95 ms, e preveja de novo. (c) Por fim acrescente `notificaciones` nos dois lugares; em `SIMULADO`, com `(None, None, "tiempo agotado")`, porque não consegue responder a tempo. Preveja a linha dele e repare em como fica alinhada. Compare cada passo com o que acontecia no exercício 1 da Lição 3, quando você esquecia uma das três listas.

### Exercício 4 — Provoque três erros e leia-os

Abra o REPL com `python` a partir da sua pasta do `revisor` (o que você conheceu na Lição 1), importe `SIMULADO` com `from revisor import SIMULADO` e provoque estes três erros, um por um: (a) `SIMULADO["catalgo"]`; (b) a posição 3 de uma lista de três elementos; (c) mudar o primeiro elemento da tupla de `pagos` com `SIMULADO["pagos"][0] = 500`. Para cada um, escreva no seu diário de bordo a **última linha** e, com as suas palavras, o que quer dizer e como se corrige. Uma pergunta extra: por que o `import` não imprimiu a tabela?

## Soluções

### Solução 1

A primeira parte:

```text
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes']
['catalogo', 'reportes']
True False
```

`a` e `b` são **o mesmo objeto**: `b.append("reportes")` mudou ambos, e `a is b` é `True`. `c = list(a)` é uma cópia feita **depois** de `a` já ter `reportes`; ao tirar `"pagos"` de `c`, `a` e `b` não ficaram sabendo, e `a is c` é `False`. A segunda parte imprime:

```text
[142, None, 87]
```

O `None` da posição 1 é tirado; a lista se desloca para a esquerda, o segundo `None` passa para a posição 1, e o `for` segue com a posição 2, de modo que **nunca o examina**: fica um `None` em uma lista da qual você queria tirá-los todos. A correção monta uma lista nova:

<!-- frag: ej1c.py -->
```python
tiempos_ms = [142, None, None, 87]
tiempos_ms = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms is not None]
print(tiempos_ms)
```

```text
[142, 87]
```

### Solução 2

<!-- frag: ej2_solucion.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}

lentos = [n for n, ms in por_servicio.items() if ms is not None and ms >= 1000]
en_segundos = {n: ms / 1000 for n, ms in por_servicio.items() if ms is not None}
sin_respuesta = {n for n, ms in por_servicio.items() if ms is None}

print(lentos)
print(en_segundos)
print(sin_respuesta)
```

```text
['inventario']
{'catalogo': 0.142, 'inventario': 2.3, 'pagos': 0.087}
{'reportes'}
```

Três coisas a conferir. Em (a) a condição `ms is not None and ms >= 1000` pergunta primeiro por `None`: o `and` para assim que uma parte é falsa, então `None >= 1000` (que falharia com um `TypeError`) nunca chega a ser avaliado. Em (b) a divisão `ms / 1000` sempre dá um número com decimais, e por isso `2.3` e não `2`. Em (c) as chaves com um só valor e sem dois-pontos dão um conjunto; com um único elemento se vê como `{'reportes'}`.

### Solução 3

(a) Com `facturacion` em `SERVICIOS` e sem entrada em `SIMULADO`, o programa **não cai**: o `.get` não encontra o nome, devolve `sin_respuesta`, e a linha nova é a de um serviço fora do ar sem dados:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO          —  sin conexión
```

Compare com a Lição 3: lá, esquecer uma lista produzia um `IndexError` ou, pior, deslocava os dados de um serviço para outro. Aqui o esquecimento afeta **só** `facturacion`, e o que diz a linha dele é verdade: não há resposta dele.

(b) Com `"facturacion": (503, 95, None),` em `SIMULADO`, a linha dele passa a ser `facturacion CAIDO       95ms  503`: respondeu, mas com um código de erro, e a primeira regra de `clasificar` o marca como fora do ar embora tenha sido rápido. O nome tem 11 letras e cabe nas 12 colunas, com um único espaço de margem.

(c) As duas constantes ficam assim (com seis nomes, a lista já não cabe em uma linha de 88 caracteres e é repartida em várias, como as assinaturas longas da Lição 3):

```python
SERVICIOS = [
    "catalogo",
    "inventario",
    "pagos",
    "reportes",
    "facturacion",
    "notificaciones",
]
```

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

E a última linha sai assim:

```text
notificacionesCAIDO          —  tiempo agotado
```

O nome tem 14 letras e a coluna mede 12, então ele sai da sua casinha e fica **colado ao estado**. É uma limitação real do formato de hoje, e a Lição 11 a resolve calculando a largura a partir do nome mais longo. Observe também o detalhe: `tiempo agotado`, o terceiro elemento da tupla, porque não houve código.

### Solução 4

As três últimas linhas, cada uma medida:

```text
KeyError: 'catalgo'
```

`KeyError` com a chave pedida entre aspas: o dicionário não tem `catalgo`. Correção: escrever `catalogo`, ou `.get` se a ausência é normal.

```text
IndexError: list index out of range
```

`IndexError`: uma lista de três elementos tem as posições 0, 1 e 2. Correção: `lista[2]`, ou `lista[-1]` para o último.

```text
TypeError: 'tuple' object does not support item assignment
```

`TypeError`: uma tupla não se muda por dentro. Correção: se de fato mudou o que `pagos` respondeu, guarda-se uma tupla nova no dicionário, `SIMULADO["pagos"] = (500, 87, None)`; o dicionário sim pode ser mudado, a tupla não.

A pergunta extra: o `import` executou `revisor.py` de cima a baixo, mas a chamada a `main()` está dentro de `if __name__ == "__main__":`, e ao importar, `__name__` vale `revisor`. É a construção idiomática da Lição 3 fazendo o seu trabalho.

## Como sei que consegui

- [ ] Em `~/curso-python/revisor/`, `python revisor.py` imprime o cabeçalho e as quatro linhas, idênticos aos da Lição 3 e aos de `fig04_15`.
- [ ] No seu `revisor.py` já não existem `NOMBRES`, `CODIGOS` nem `TIEMPOS_MS`, nem nenhum `range(len(...))`.
- [ ] Com `facturacion` em `SERVICIOS` e sem entrada em `SIMULADO`, a linha dele diz `CAIDO` e `sin conexión`, e o programa não cai; ao acrescentá-lo a `SIMULADO`, diz `503`.
- [ ] Para o serviço `reportes`, `.get` dá `None` por duas razões possíveis, e você consegue dizer quais são e como distingui-las com `in`.
- [ ] Você consegue explicar com as suas palavras a diferença entre `b = a` e `b = a.copy()`, entre `sorted(x)` e `x.sort()`, e por que tirar elementos de uma lista enquanto a percorre pula algum sem avisar.
- [ ] Você anotou no [diário de bordo](bitacora.md) o que foi mais difícil para você: o que anotar ali é o que você deve revisar.

## Resumo

Responda sem olhar a lição:

1. Que pergunta responde cada coleção: a lista, a tupla, o dicionário e o conjunto? Quais podem ser mudadas?
2. Que diferença há entre `IndexError` e `KeyError`, e o que diz a última linha de cada um?
3. O que devolve `.get("reportes")` se `reportes` existe com o valor `None`? E se não existe? Como você distingue os dois casos?
4. Que três partes tem uma compreensão? Quando convém deixar um laço?
5. Se `a = [1, 2]` e você faz `b = a`, quantas listas há? O que muda com `b = a.copy()`? E com `copy.deepcopy`?
6. Por que tirar elementos de uma lista enquanto a percorre pula elementos sem dar erro?
7. No `revisor`, por que `SERVICIOS` e `SIMULADO` são duas coisas separadas, e o que acontece com um nome que está na primeira e não na segunda?

## Para ler mais

- [Python, “Estruturas de dados” (tutorial)](https://docs.python.org/pt-br/3/tutorial/datastructures.html) — listas, tuplas, conjuntos, dicionários e compreensões, com mais exemplos e na mesma ordem desta lição. Na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [Python, “Tipos embutidos”](https://docs.python.org/pt-br/3/library/stdtypes.html) — a referência de cada coleção: que operações admite e quais mudam o valor no lugar. É para consultar, não para ler de cabo a rabo. Consultado em 7 de outubro de 2026.
- [Python, módulo `copy`](https://docs.python.org/pt-br/3/library/copy.html) — a diferença entre a cópia rasa e a profunda, contada pela documentação oficial. Consultado em 7 de outubro de 2026.
- [Perguntas frequentes de programação: “Por que mudar a lista `y` também mudou a lista `x`?”](https://docs.python.org/pt-br/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) — a explicação oficial de cópia contra referência, com o mesmo caso de 4.3.1. Consultado em 7 de outubro de 2026.
