# Lição 2 — Valores, texto e decisões

**Tempo:** 90 min

**O que você constrói:** o cabeçalho do `revisor` e a classificação de **um** serviço: o estado, o tempo e o detalhe dele, impressos em uma linha de tabela

**O que você aprende:** três conceitos. Primeiro, os valores e os nomes (números, texto, verdadeiro ou falso, e `None`); segundo, o texto com formatação (as f-strings); terceiro, as decisões com `if`, `elif` e `else`, e a indentação como parte da sintaxe

**De onde você vem.** Você traz a [Lição 1](01-instalacion.md): tem a pasta `~/curso-python/` com o seu ambiente virtual `.venv`, o ambiente ativo (o *prompt* mostra `(.venv)`) e, dentro de `~/curso-python/revisor/`, um arquivo `revisor.py` de uma única linha que imprime “revisor: todavía no revisa nada” (“revisor: ainda não revisa nada”). Isso é tudo o que o seu programa faz até hoje: não revisa nada. Nesta lição ele começa a revisar, para um serviço. Todos os comandos são escritos como se você estivesse em `~/curso-python/revisor/`, e o programa é executado com `python arquivo.py`. Salve cada figura da lição com o nome que ela traz na primeira linha (`fig02_01.py`, `fig02_02.py`, e assim por diante), nessa mesma pasta.

**O que esta lição não faz.** Ainda não há listas, nem funções, nem repetições. O `revisor` de hoje conhece **um** único serviço, guardado em algumas variáveis, e o classifica uma vez. Revisar os quatro ao mesmo tempo, e repetir o mesmo código sem copiá-lo, é o tema da [Lição 3](03-bucles-funciones-modulos.md). Hoje se resolve primeiro o menor: **o que é um dado, como se escreve uma linha da tabela e como o programa decide se um serviço está no ar, lento ou fora do ar**.

## Ao terminar, você vai conseguir

- Guardar um dado com um nome e dizer de que tipo ele é (`int`, `float`, `str`, `bool` ou `None`), com a função `type()`.
- Calcular com os operadores de aritmética e de comparação, combinar condições com `and`, `or` e `not`, e perguntar se um valor é `None` com `is`.
- Montar um texto com uma f-string e alinhar colunas com `:<12`, `:>6` e `:.1f`.
- Escrever um `if`/`elif`/`else`, explicar por que a indentação é parte da sintaxe e por que a ordem dos ramos muda o resultado.
- Classificar um serviço como ARRIBA, LENTO ou CAIDO (no ar, lento ou fora do ar) com as quatro regras do `revisor` e imprimir a linha dele com o cabeçalho da tabela.
- Ler três erros do iniciante, `SyntaxError: expected ':'`, `IndentationError` e `TypeError` ao somar texto com um número, e dizer o que os causou.

## O porquê antes do como

Imagine que você trabalha em uma equipe que mantém quatro serviços dentro de uma empresa: o catálogo de produtos, o estoque, os pagamentos e os relatórios. Numa segunda-feira de manhã alguém pergunta o mesmo que se pergunta todas as segundas: “quais estão funcionando?”. Hoje você descobre isso abrindo quatro endereços no navegador e olhando. O `revisor`, o projeto que você vai construir neste curso, faz essa pergunta por você e responde com uma tabela como esta:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Olhe a tabela com olhos de programador e verá que cada célula é **um dado de uma classe diferente**. `catalogo` é um texto. `142` é uma quantidade. `ARRIBA` é uma de três palavras possíveis. E o tempo de `reportes` é... nada: esse serviço não respondeu, então não há um tempo para mostrar, e isso precisa poder ser expresso de alguma maneira que não seja escrever um zero (um serviço que não respondeu não respondeu em zero milissegundos). Se um programa vai produzir esta tabela, precisa de três coisas, e são as três desta lição:

- **Representar os dados** com a classe correta: texto para o nome, números para o código e o tempo, um valor especial para “não há dado”. É o conceito 2.1.
- **Montar a linha**: colar o nome, o estado e o tempo em colunas alinhadas, e converter 2300 milissegundos em `2.3s`. É o conceito 2.2.
- **Decidir**: se o serviço respondeu com um código de erro, está CAIDO; se respondeu bem, mas demorou mil milissegundos ou mais, está LENTO; se não, está ARRIBA. É o conceito 2.3.

No final da lição você terá um `revisor.py` de umas trinta linhas que, para o serviço `inventario`, imprime exatamente estas duas linhas:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

São duas linhas das cinco da tabela, mas são as que importam: o cabeçalho, que não muda mais em todo o curso, e um serviço completo, com as suas três decisões. Quando na Lição 3 você aprender a repetir, os outros três serviços sairão com o mesmo código.

Uma última ideia antes de começar, porque vai servir a você em todo o curso. Um programa é uma lista de instruções que o Python executa **uma depois da outra, de cima para baixo**. Quando uma instrução falha, o Python para nela e diz qual foi; quando uma instrução não pede nada especial, o Python passa para a seguinte. Não há mágica por baixo: se você quer saber o que um programa faz, leia-o como o Python o lê, de cima para baixo e uma linha de cada vez. É isso que você vai fazer com cada figura.

## Os conceitos

### 2.1 Valores e nomes

#### 2.1.1 Os valores e seus tipos

Um **valor** é um dado concreto: o número 2300, o texto `"inventario"`, o “sim” de “respondeu?”. Todo valor tem um **tipo**, que é a classe de dado que ele é e que determina o que se pode fazer com ele: com os números se soma, com os textos se cola. O Python tem muitos tipos; hoje você precisa de cinco, e os cinco aparecem no `revisor`.

- **`int`** (inteiro): um número sem decimais. O código de resposta de um serviço (`200`, `503`) e o tempo em milissegundos (`2300`) são inteiros. [A documentação do Python](https://docs.python.org/pt-br/3/library/stdtypes.html#numeric-types-int-float-complex) os chama de “tipos numéricos”; os inteiros não têm um tamanho máximo com que você precise se preocupar.
- **`float`** (decimal): um número com ponto decimal, como `2.3`. Chama-se assim por “ponto flutuante”, a maneira como os computadores guardam os decimais. Mais abaixo você verá uma surpresa que vem com eles.
- **`str`** (string, cadeia de texto): uma sequência de caracteres entre aspas, simples ou duplas, como `"inventario"`. Neste curso elas são escritas com aspas duplas. Um texto pode ter acentos e símbolos (`"sin conexión"`, `"—"`): o Python 3 guarda o texto em Unicode.
- **`bool`** (booleano): apenas dois valores possíveis, `True` e `False`, com a primeira letra maiúscula. É a resposta a uma pergunta de sim ou não, como “o serviço respondeu?”. Leva o nome de George Boole, o matemático que formalizou a lógica do verdadeiro e do falso.
- **`None`**: o valor que significa “não há nada aqui”. É o único valor do seu próprio tipo, que se chama `NoneType`. Você vai usá-lo para o tempo e o código de um serviço que não respondeu, e é a resposta correta a “quanto demorou?” quando a resposta é “não há resposta”.

A função `type()` diz a você o tipo de qualquer valor. E o `print()` pode receber vários valores separados por vírgulas: imprime-os na mesma linha, com um espaço entre eles. Com as duas coisas você pode ver os cinco tipos juntos. Salve esta figura como `fig02_01.py` e execute:

```python
# fig02_01.py
nombre = "inventario"
codigo = 200
tiempo_ms = 2300
tiempo_s = tiempo_ms / 1000
respondio = True
error = None

print(nombre, type(nombre))
print(codigo, type(codigo))
print(tiempo_ms, type(tiempo_ms))
print(tiempo_s, type(tiempo_s))
print(respondio, type(respondio))
print(error, type(error))
```

```text
$ python fig02_01.py
inventario <class 'str'>
200 <class 'int'>
2300 <class 'int'>
2.3 <class 'float'>
True <class 'bool'>
None <class 'NoneType'>
```

Linha por linha. A primeira linha, a que começa com `#`, é um **comentário**: o Python ignora tudo o que vai de um `#` até o fim da linha. Serve para que as pessoas leiam notas, e neste curso a primeira linha de cada figura é um comentário com o nome dela (`# fig02_01.py`), para que você saiba como salvá-la. As seis linhas seguintes **criam variáveis**, que é o tema do ponto seguinte; repare apenas em que cada uma guarda um valor de um tipo diferente. `tiempo_ms / 1000` divide 2300 por 1000 e dá `2.3`, um `float`, embora os dois números da conta fossem inteiros: a divisão `/` sempre dá um decimal. Depois, seis `print` mostram cada valor e o seu tipo. A saída diz `<class 'str'>`, `<class 'int'>` e assim por diante: em Python, “tipo” e “classe” são a mesma ideia, e a palavra *class* na resposta não obriga você a saber mais nada de classes por ora (elas chegam na Lição 5).

Duas coisas em que reparar. Primeira: `200` e `"200"` **não são a mesma coisa**. O primeiro é um número, e com ele se pode comparar e somar; o segundo é um texto de três caracteres que por acaso são dígitos, e com ele não se pode calcular. Quando na tabela você vir `200` na coluna DETALLE, ali ele é um texto (é um pedaço de uma linha que se imprime), mas na variável `codigo` é um número. Segunda: `None` **não é** `0`, nem `""` (o texto vazio), nem `False`. É um valor diferente, que diz “aqui não há dado”. Um serviço fora do ar que não devolveu código não tem “código zero”: não tem código.

#### 2.1.2 Os nomes e a atribuição

Uma **variável** é um nome que aponta para um valor. Cria-se com o sinal de igual:

```python
tiempo_ms = 2300
```

Essa linha se chama **atribuição** e se lê da direita para a esquerda: primeiro se calcula o valor da direita (2300) e depois se dá a ele o nome da esquerda (`tiempo_ms`). O sinal `=` **não significa “é igual a”** como na matemática; significa “guarde isto sob esse nome”. A pergunta de se duas coisas são iguais se escreve com dois sinais, `==`, e você a verá daqui a pouco. Confundir os dois é um dos tropeços mais comuns do iniciante, e o Python protege você da maioria: `if codigo = 200:` é um erro de sintaxe, porque dentro de um `if` só cabe uma pergunta.

Um nome pode mudar de valor quando você quiser: `tiempo_ms = 2300` e mais abaixo `tiempo_ms = 87` fazem com que o nome aponte agora para o 87. O valor anterior simplesmente deixa de ter nome. E um valor pode ter vários nomes ao mesmo tempo, embora isso só importe de verdade quando os valores podem ser modificados por dentro, e essa história começa na Lição 4.

As regras para escrever um nome são poucas:

- Leva letras, dígitos e sublinhado (`_`), e **não pode começar com um dígito**: `1servicio` não serve, `servicio1` serve.
- Não pode ser uma **palavra reservada**, dessas que o Python usa para a sua própria sintaxe (`if`, `else`, `None`, `True`...). Você verá o resto conforme precisar.
- **As maiúsculas contam**: `Nombre` e `nombre` são dois nomes diferentes. Se você escrever um onde queria o outro, o Python não dirá “você errou a maiúscula”, dirá que o nome não existe.

E há também **convenções**, que não são obrigatórias mas que todo o mundo do Python segue, porque estão no [guia de estilo oficial, a PEP 8](https://peps.python.org/pep-0008/#naming-conventions): os nomes de variáveis vão em minúsculas com sublinhado entre as palavras (`tiempo_ms`, chamado *snake_case*), e os nomes de valores que **não vão mudar** (as constantes) vão em maiúsculas (`UMBRAL_LENTO_MS`). O Python não impede que você mude uma “constante”; a maiúscula é um aviso para quem ler o código.

Este curso acrescenta duas regras próprias, que você verá em cada figura. **Os identificadores vão em espanhol, sem acentos nem `ñ`**: `nombre`, `tiempo_ms`, `estado`. O Python aceita acentos nos nomes, mas eles se digitam mal em teclados alheios e complicam o compartilhamento do código. E **as unidades vão no nome**: `tiempo_ms`, nunca `tiempo` sozinho. Quando alguém lê `tiempo = 2300`, não sabe se são milissegundos, segundos ou minutos; quando lê `tiempo_ms = 2300`, sabe. É um costume que evita erros caros: [a NASA atribuiu a falha da sonda Mars Climate Orbiter a um erro de navegação](https://science.nasa.gov/mission/mars-climate-orbiter/), causado por não converter unidades inglesas em métricas entre o programa de terra e o da nave.

#### 2.1.3 Operadores: calcular, comparar e combinar

Um **operador** é um símbolo que faz algo com valores. Há três famílias e as três servem ao `revisor`.

Os de **aritmética** calculam: `+` soma, `-` subtrai, `*` multiplica, `/` divide e sempre devolve um `float`, `//` divide e fica com a parte inteira, `%` dá o resto da divisão e `**` eleva a uma potência. Os de **comparação** perguntam e sempre respondem com um `bool`: `==` (igual), `!=` (diferente), `<`, `<=`, `>` e `>=`. E os **lógicos** combinam perguntas: `and` é verdadeiro só se as duas são verdadeiras, `or` é verdadeiro se pelo menos uma é, e `not` inverte a resposta. Salve `fig02_02.py`:

```python
# fig02_02.py
UMBRAL_LENTO_MS = 1000
tiempo_ms = 2300
codigo = 200

# Aritmética
print(tiempo_ms / 1000)
print(tiempo_ms // 1000)
print(tiempo_ms % 1000)
print(tiempo_ms + 100)
print(2**3)

# Comparaciones
print(tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200)
print(codigo != 200)

# Lógicos
print(codigo >= 400 or tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200 and tiempo_ms < UMBRAL_LENTO_MS)
contesto_bien = codigo < 400
print(not contesto_bien)
```

```text
$ python fig02_02.py
2.3
2
300
2400
8
True
True
False
True
False
False
```

As cinco primeiras linhas de saída são aritmética: 2300 dividido por 1000 dá `2.3`; a divisão inteira dá `2` (quantos segundos completos cabem em 2300 ms) e o resto dá `300` (os milissegundos que sobram); somar 100 dá `2400`, e `2**3` é dois ao cubo, `8`. As três seguintes são comparações: 2300 é sim maior ou igual ao limiar de 1000 (`True`), o código é sim 200 (`True`) e portanto não é diferente de 200 (`False`). As últimas três combinam: a primeira diz “o código é de erro **ou** o tempo passou do limiar?”, e como o segundo é verdadeiro, o `or` inteiro é; a segunda diz “respondeu bem **e** rápido?”, e como não foi rápido, é falsa; a terceira guarda em uma variável a resposta a “o código é menor que 400?” (`True`) e a inverte com `not`, e por isso dá `False`. Observe que uma comparação pode ser guardada em uma variável igual a um número: o seu valor é um `bool`.

Observe um detalhe da figura que se repetirá em todo o curso: o limiar está em uma variável com nome em maiúsculas, `UMBRAL_LENTO_MS = 1000`, e as comparações o usam pelo nome. Se amanhã a equipe decidir que um serviço é lento a partir de 800 ms, você muda **uma** linha. Se tivesse escrito `1000` em cada comparação, teria que encontrar todas.

Dois esclarecimentos sobre os operadores. A primeira é a **precedência**: como na matemática, `*` e `/` são feitos antes de `+` e `-`, e o Python faz as comparações antes de `not`, `and` e `or`. Quando tiver dúvidas, use parênteses. A segunda é que **`and` e `or` não avaliam o que não precisam**. Em `A or B`, se `A` já é verdadeira, o Python nem olha `B`, porque o resultado já não pode mudar; em `A and B`, se `A` é falsa, também não olha `B`. Isso se chama *avaliação de curto-circuito* e não é um detalhe de erudito: daqui a alguns minutos vai evitar que o `revisor` exploda com o serviço `reportes`.

Um aviso sobre os decimais, que eu prometi. Olhe esta sessão do REPL (o interpretador interativo da Lição 1):

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> 10 / 2
5.0
```

A primeira resposta parece um erro do Python e não é. Os computadores guardam os decimais em binário, e alguns decimais simples, como 0.1, não têm uma representação exata em binário; são guardados aproximados, e a soma de duas aproximações dá uma aproximação ligeiramente diferente do 0.3 que você esperava. [O tutorial oficial dedica um capítulo a isso](https://docs.python.org/pt-br/3/tutorial/floatingpoint.html) e lembra que não é um defeito do Python nem do seu código: é como funcionam os números de ponto flutuante em binário, a representação que quase todos os computadores usam (e, com eles, quase todas as linguagens). A consequência prática: **não compare com `==` o resultado de uma conta com decimais esperando um valor exato**. No `revisor` isso quase não afeta você, porque os tempos são inteiros (milissegundos), e por isso estão em milissegundos e não em segundos com decimais. A segunda resposta mostra outro costume: `10 / 2` dá `5.0`, não `5`. A `/` sempre devolve um `float`.

#### 2.1.4 `None`, `is` e as conversões com `str()` e `int()`

Para perguntar se um valor é `None`, o Python tem um operador específico: **`is`**. Escreve-se `valor is None`, e o seu contrário é `valor is not None`. É a forma correta de fazer isso, e a que usa [o guia de estilo](https://peps.python.org/pep-0008/#programming-recommendations), que pede para comparar com `None` sempre com `is` ou `is not`, nunca com `==`. O motivo, dito em uma frase: em todo o programa **existe um único `None`**, então o que se pergunta não é “se parece com `None`?”, e sim “é *o* `None`?”. (A diferença completa entre `==` e `is` é o tema da Lição 3; por ora fique com a regra.)

Há também duas funções que convertem entre tipos. `str(valor)` devolve o texto que representa um valor: `str(503)` é `"503"`. E `int(texto)` faz o contrário: `int("503")` é `503`. Você vai precisar delas em dois lugares: `str(codigo)` para pôr um código dentro da linha da tabela, e mais adiante `int(...)` para converter o que chega de fora, que quase sempre chega como texto. Salve `fig02_03.py`:

```python
# fig02_03.py
codigo = None
tiempo_ms = None

print(codigo is None)
print(codigo is not None)

codigo = 503
print(codigo is None)
print("código: " + str(codigo))
print(type(str(codigo)))
print(type(int("503")))
```

```text
$ python fig02_03.py
True
False
False
código: 503
<class 'str'>
<class 'int'>
```

Enquanto `codigo` valia `None`, a primeira pergunta dá `True` e a segunda `False`. Quando se atribui 503 a ele, o serviço já tem código e a pergunta dá `False`. Depois, `"código: " + str(codigo)` cola dois textos com `+` (aos textos, o `+` os une) e funciona **porque `str(codigo)` converteu o número em texto antes**. As duas últimas linhas confirmam que `str(503)` é um `str` e que `int("503")` é um `int`. Guarde esta ideia: o Python não converte entre tipos por você. Se você tenta colar um texto com um número, ele reclama, e essa reclamação é um dos erros da seção “O erro que você vai ver”.

### 2.2 Texto com formatação: as f-strings

#### 2.2.1 Por que não colar com `+`

É preciso montar uma linha da tabela: o nome, o estado, o tempo e o detalhe, em colunas alinhadas. Com o que você já sabe, a maneira seria colar textos com `+`, convertendo cada número com `str()`, e calcular à mão quantos espaços faltam para completar cada coluna. Dá para fazer, e sai ilegível e frágil: cada peça nova é outro `+` e outro `str()`, e mudar a largura de uma coluna obriga a recontar espaços.

O Python tem uma ferramenta pensada para isso: as **f-strings** (*formatted string literals*). Uma f-string é um texto que começa com a letra `f` antes das aspas, e que aceita **expressões entre chaves**: o Python calcula o que há dentro de cada par de chaves e põe o resultado no texto. Elas são explicadas na [referência da linguagem](https://docs.python.org/pt-br/3/reference/lexical_analysis.html#f-strings). Existem outras duas formas mais antigas de formatar texto, o operador `%` e o método `.format()`. Você as encontrará em código velho, então convém reconhecê-las, mas este curso não as usa e você não precisa aprendê-las: as f-strings fazem tudo o que elas fazem e se leem melhor.

#### 2.2.2 Pôr valores e contas no texto

O mais simples é pôr um nome entre chaves: `f"{nombre} respondió"`. Mas o que vai entre chaves pode ser qualquer expressão, até uma conta: `f"{tiempo_ms * 2}"` calcula o dobro e o insere. Isso elimina por completo o `str()` do ponto anterior: a f-string converte em texto o que você insere, sem que você peça.

#### 2.2.3 A especificação de formato: largura, alinhamento e decimais

Depois da expressão, e separada por dois-pontos, pode-se escrever uma **especificação de formato** que diz ao Python como mostrar o valor. Hoje você precisa de três, e [a linguagem de formatação completa está na documentação](https://docs.python.org/pt-br/3/library/string.html#format-specification-mini-language):

- **`:<12`**: ocupa **12 caracteres** e alinha o valor à **esquerda** (`<`), preenchendo com espaços à direita.
- **`:>6`**: ocupa **6 caracteres** e alinha o valor à **direita** (`>`), preenchendo à esquerda.
- **`:.1f`**: mostra um número **decimal com um dígito** depois do ponto (`f` de *fixed*, ponto fixo).

Salve `fig02_04.py`. Na saída, os campos são cercados por colchetes para que você veja onde cada um começa e termina:

```python
# fig02_04.py
nombre = "inventario"
tiempo_ms = 2300

print(f"{nombre} respondió en {tiempo_ms} ms")
print(f"el doble: {tiempo_ms * 2}")
print(f"en segundos: {tiempo_ms / 1000}")
print(f"[{nombre:<12}]")
print(f"[{nombre:>12}]")
print(f"[{87:>6}]")
print(f"[{tiempo_ms / 1000:.1f}s]")
print(f"[{1000 / 1000:.1f}s]")
```

```text
$ python fig02_04.py
inventario respondió en 2300 ms
el doble: 4600
en segundos: 2.3
[inventario  ]
[  inventario]
[    87]
[2.3s]
[1.0s]
```

As três primeiras linhas já não precisam de explicação: o nome e o tempo são inseridos tal qual, a conta é calculada e inserida, e `2300 / 1000` sai como `2.3`. As seguintes ensinam a largura: `inventario` tem dez caracteres, e com `:<12` fica com dois espaços depois (veja onde cai o colchete de fechamento); com `:>12`, os dois espaços vão antes. Com `{87:>6}` o 87 ocupa seis posições, alinhado à direita, e por isso há quatro espaços antes. As duas últimas mostram `.1f`: `2.3` já tinha um decimal, e `1000 / 1000`, que é `1.0`, mantém o seu `.0` (o Python arredonda para o número de decimais pedido, não os tira).

Isto é o que você precisa para montar uma linha da tabela. O modelo do `revisor`, que não mudará em todo o curso, é:

```text
f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

Leia-o da esquerda para a direita: o nome do serviço em 12 colunas, alinhado à esquerda; o estado em 10, à esquerda; o tempo em 6, à direita (os números se alinham melhor pela direita, para que as unidades fiquem uma embaixo da outra); dois espaços fixos, e o detalhe, que vai no final e não precisa de largura. E o cabeçalho da tabela usa **o mesmo modelo**, com os títulos no lugar dos dados. Um detalhe de escrita: o cabeçalho vai entre aspas duplas e, dentro das chaves, os títulos levam aspas simples (`{'SERVICIO':<12}`). Desde o Python 3.12 você poderia repetir as duplas dentro das chaves e funcionaria (a [PEP 701](https://peps.python.org/pep-0701/) permitiu), mas alterná-las se lê melhor, porque a olho nu se distingue onde termina a f-string e onde começa o texto de dentro, e além disso funciona em versões anteriores do Python.

### 2.3 Decisões: `if`, `elif`, `else` e a indentação

#### 2.3.1 Uma pergunta e um bloco

Um programa que sempre faz a mesma coisa não serve para revisar serviços. Precisa **decidir**: se acontece tal coisa, fazer isto; se não, aquilo. Em Python a decisão se escreve com `if`:

```text
if <pregunta>:
    <lo que se hace si la respuesta es verdadera>
```

A pergunta é qualquer expressão que dê um `bool`, como as da seção anterior. Depois da pergunta vai um sinal de **dois-pontos** (`:`), que diz ao Python “aqui começa o que depende da pergunta”. E o que depende dela vai nas linhas seguintes, **deslocado para a direita**. A esse conjunto de linhas se chama um **bloco**.

Aqui vem uma característica do Python que o distingue da maioria das linguagens e que às vezes surpreende o iniciante: **a indentação é parte da sintaxe**. Em outras linguagens os blocos são delimitados com chaves ou com palavras como `begin` e `end`, e o recuo é uma questão de estilo. Em Python **o recuo é o que diz onde o bloco começa e onde termina**. As linhas que estão deslocadas a mesma quantidade pertencem ao mesmo bloco; quando uma linha volta para a margem esquerda, o bloco terminou. [A referência da linguagem o define com precisão](https://docs.python.org/pt-br/3/reference/lexical_analysis.html#indentation), e a regra prática da PEP 8 é: **quatro espaços por nível**, e nunca misturar tabulações com espaços. Configure o seu editor para que a tecla Tab insira quatro espaços, e não pense mais nisso.

Salve `fig02_05.py`:

```python
# fig02_05.py
codigo = 503

if codigo >= 400:
    print("el servicio contestó con un error")
else:
    print("el servicio contestó bien")

print("fin de la revisión")
```

```text
$ python fig02_05.py
el servicio contestó con un error
fin de la revisión
```

Com `codigo = 503`, a pergunta `codigo >= 400` é verdadeira e o primeiro bloco é executado. O `else` (em português, “senão”) é o ramo que se executa quando a resposta é falsa; não leva pergunta, mas sim os seus dois-pontos. Repare na última linha: está **na margem esquerda**, fora dos dois blocos, e por isso é executada sempre, seja qual for o código. Tente mudar `codigo` para `200` e confira que muda a primeira linha da saída, mas a última não. Se alguma vez uma linha for executada “quando não devia” (ou não for executada quando devia), olhe primeiro o recuo dela: em Python, é ali que começam 80 % dessas surpresas.

#### 2.3.2 `elif`: várias perguntas em cadeia

Um serviço não tem dois estados e sim três, e as decisões do `revisor` são encadeadas: primeiro se pergunta se está fora do ar; se não, se pergunta se está lento; e se tampouco, está no ar. Para isso existe `elif`, contração de *else if*, “senão, e se...”. Uma cadeia `if`/`elif`/`else` funciona assim: **o Python avalia as perguntas de cima para baixo, executa o bloco da primeira que for verdadeira e pula todas as demais**. Se nenhuma for, executa o `else`, se houver. De uma cadeia sempre se executa, no máximo, um bloco.

As regras do `revisor` para classificar um serviço, que são as mesmas desta lição até a última, são quatro:

1. Se **não houve código** (não houve resposta), está **CAIDO**.
2. Se o código é **400 ou mais** (o servidor respondeu, mas com erro), está **CAIDO**; o detalhe será o próprio código, por exemplo `503`.
3. Se respondeu bem e demorou **1000 ms ou mais**, está **LENTO**.
4. Se não, está **ARRIBA**.

As duas primeiras têm o mesmo resultado, e podem ser juntadas em uma única pergunta com `or`. Salve `fig02_06.py`:

```python
# fig02_06.py
UMBRAL_LENTO_MS = 1000
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

print(estado)
```

```text
$ python fig02_06.py
LENTO
```

Para `inventario`, com código 200 e 2300 ms, a primeira pergunta é falsa (o código existe e não chega a 400), a segunda é verdadeira (2300 é maior ou igual a 1000), e o estado fica em `"LENTO"`. Experimente com outros valores: `codigo = 503` dá `CAIDO`; `tiempo_ms = 142` dá `ARRIBA`.

#### 2.3.3 A ordem das perguntas importa

Há uma razão pela qual a pergunta do código vai **primeiro**, e é a mesma que se prometeu com o curto-circuito. Pense em `reportes`: não respondeu, então o seu `codigo` é `None` e o seu `tiempo_ms` também. Com a cadeia de cima, a primeira pergunta (`codigo is None or ...`) é verdadeira assim que o Python olha o `is None`, e **já não avalia** a segunda metade do `or`, que teria falhado: `None >= 400` não faz sentido. E como o primeiro ramo foi cumprido, tampouco se avalia o `elif`, que perguntaria `None >= 1000`. O serviço fica CAIDO sem que o Python compare um `None` com um número.

Se você puser as perguntas em outra ordem, a cadeia deixa de ser segura. Esse erro é um dos de “O que se faz errado”, e vale a pena provocá-lo no Exercício 4. A regra de fundo: **em uma cadeia de `elif`, ordene as perguntas da mais específica ou mais perigosa para a mais geral**, de modo que cada ramo possa dar por certo o que os anteriores descartaram. No `elif`, você já sabe que o serviço respondeu e com um código menor que 400, então `tiempo_ms` tem um valor.

#### 2.3.4 Tudo junto: a linha de um serviço

Você já tem tudo o que é necessário. Falta calcular as outras duas colunas com o mesmo mecanismo. O **tempo** é um texto que depende do valor: se não houve tempo, um traço (`"—"`); se foi menos de um segundo, milissegundos colados à unidade (`"142ms"`); se foi um segundo ou mais, segundos com um decimal (`"2.3s"`). Observe que o 1000 daqui **não é o limiar de lento**: é a quantidade de milissegundos que há em um segundo. Eles se parecem no valor e significam coisas diferentes, e por isso o primeiro tem nome (o limiar pode mudar) e o segundo não (um segundo sempre tem mil milissegundos). E o **detalhe** é o código convertido em texto, ou `"sin conexión"` se não houve código.

Esta é a figura da lição, o seu novo `revisor.py`. Salve-a com o nome `fig02_07.py` para compará-la e também como `revisor.py`, que substitui a linha da Lição 1:

```python
# fig02_07.py
UMBRAL_LENTO_MS = 1000

nombre = "inventario"
url = "https://inventario.example"  # todavía no se usa: la ocupará la lección 9
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

if tiempo_ms is None:
    tiempo = "—"
elif tiempo_ms < 1000:  # 1000 ms es un segundo, no el umbral de lento
    tiempo = f"{tiempo_ms}ms"
else:
    tiempo = f"{tiempo_ms / 1000:.1f}s"

if codigo is None:
    detalle = "sin conexión"
else:
    detalle = str(codigo)

print(f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}")
print(f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}")
```

```text
$ python fig02_07.py
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

Leia como o Python lê. As primeiras cinco linhas guardam os dados de um serviço; `url` é o endereço do serviço e ainda não é impresso, mas o projeto já o carrega, assim como o domínio `.example`, que é um nome reservado que nunca chega a nenhuma página real (nenhum programa deste curso toca a internet até a Lição 9). O primeiro bloco `if` calcula `estado` com as regras de cima. O segundo calcula `tiempo`, o texto da coluna: se `tiempo_ms is None` põe o traço, se é menor que 1000 cola `ms` ao número e se não o converte em segundos com um decimal. O terceiro calcula `detalle`. As duas últimas linhas imprimem o cabeçalho e a linha com o modelo da seção 2.2: o mesmo padrão, com títulos na primeira e com as variáveis na segunda.

Troque as cinco variáveis pelas de outro serviço e execute o programa de novo: não é preciso mexer em mais nada. É disso que trata o Exercício 1, e daí vem a lição seguinte: copiar e colar esse bloco para cada serviço seria absurdo, e o Python tem ferramentas para não fazer isso.

## O erro que você vai ver

Nesta seção você vai provocar de propósito os três erros que o iniciante vê primeiro. Os três foram copiados de uma execução real. Quando o programa falha, o Python imprime um relatório do erro que se chama ***traceback***, e a regra, desde a Lição 1, é a mesma: **lê-se da última linha para cima**. A última linha diz o que aconteceu; as de cima dizem onde. Os caminhos completos dos arquivos que você verá na sua tela serão diferentes dos que este texto mostra (aqui são abreviados para o nome do arquivo).

### `TypeError: can only concatenate str (not "int") to str`

Salve `fig02_08.py`, que tenta colar um texto com um número:

```python
# fig02_08.py
nombre = "inventario"
tiempo_ms = 2300
print("respondió en " + tiempo_ms)
```

```text
$ python fig02_08.py
Traceback (most recent call last):
  File "fig02_08.py", line 4, in <module>
    print("respondió en " + tiempo_ms)
          ~~~~~~~~~~~~~~~~^~~~~~~~~~~
TypeError: can only concatenate str (not "int") to str
```

A última linha diz: um `TypeError` (um erro de tipo) com a mensagem “só é possível concatenar `str` (não `int`) a `str`”. Concatenar é colar. O `+` entre dois textos os cola, mas aqui o segundo era um número, e o Python não sabe como colar um texto com um número: não vai adivinhar se você queria “2300” ou um cálculo. As linhas de cima dizem **onde**: `line 4`, e embaixo a linha do programa com umas marcas que apontam a operação que falhou. A correção é fazer a conversão você mesmo, com `str(tiempo_ms)`, ou melhor, não colar nada: `print(f"respondió en {tiempo_ms}")`. [A documentação do `TypeError`](https://docs.python.org/pt-br/3/library/exceptions.html#TypeError) diz que essa exceção é “levantada quando uma operação ou função é aplicada a um objeto de tipo inadequado”, que é exatamente isto.

### `SyntaxError: expected ':'`

Salve `fig02_09.py`, um `if` em que alguém esqueceu os dois-pontos:

```python
# fig02_09.py
codigo = 503
if codigo >= 400
    print("CAIDO")
```

```text
$ python fig02_09.py
  File "fig02_09.py", line 3
    if codigo >= 400
                    ^
SyntaxError: expected ':'
```

Um `SyntaxError` é um erro de **sintaxe**: o Python nem sequer começou a executar o programa, porque o leu inteiro antes e encontrou algo que não é Python válido. Por isso a saída **não** diz `Traceback`: não há um percurso de execução para mostrar, só o lugar do problema. A mensagem, `expected ':'`, diz o que ele esperava: dois-pontos. A seta de baixo (`^`) aponta o lugar onde ele percebeu, o fim da linha do `if`. Quando você vir um `SyntaxError`, olhe a linha indicada e também a **anterior**, porque às vezes o esquecimento está antes (um parêntese sem fechar, por exemplo, faz falhar a linha seguinte).

### `IndentationError: expected an indented block after 'if' statement on line 3`

Salve `fig02_10.py`: agora os dois-pontos estão, mas a linha de baixo ficou na margem:

```python
# fig02_10.py
codigo = 503
if codigo >= 400:
print("CAIDO")
```

```text
$ python fig02_10.py
  File "fig02_10.py", line 4
    print("CAIDO")
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 3
```

`IndentationError` é uma variante do `SyntaxError` para os problemas de recuo. A mensagem é literal: depois de um `if` (o da linha 3) esperava-se um bloco com recuo, e a linha 4 não o tem. Os dois-pontos no final do `if` prometiam um bloco, e o Python o exige. É o lembrete da seção 2.3: **os dois-pontos e o recuo andam juntos**. A correção é afastar `print("CAIDO")` quatro espaços para a direita.

## O que se faz errado

**Pôr as perguntas na ordem errada.** É o erro mais traiçoeiro desta lição, porque parece razoável e falha justamente com o serviço que mais importa. Salve `fig02_11.py`, onde a pergunta do tempo vai antes da do código:

```python
# fig02_11.py
UMBRAL_LENTO_MS = 1000
codigo = None
tiempo_ms = None

if tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"

print(estado)
```

```text
$ python fig02_11.py
Traceback (most recent call last):
  File "fig02_11.py", line 6, in <module>
    if tiempo_ms >= UMBRAL_LENTO_MS:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

A mensagem, `'>=' not supported between instances of 'NoneType' and 'int'`, diz: o operador `>=` não está definido entre um `NoneType` (o `None`) e um `int` (o 1000). Com serviços que responderam, o programa funciona e você não percebe; com `reportes`, que não respondeu, explode. Custo: um `revisor` que cai justamente quando um serviço está fora do ar, que é quando você mais precisa dele. A cura é a regra da seção 2.3: primeiro o ramo que descarta os dados que faltam.

**Escrever `=` onde vai `==`.** `if codigo = 200:` é um `SyntaxError`, e a mensagem do Python adivinha: *invalid syntax. Maybe you meant '==' or ':=' instead of '='?* A atribuição guarda; a comparação pergunta. Não podem ser trocadas.

**Comparar com `None` usando `==`.** Funciona nos casos simples e é o que alerta [a PEP 8](https://peps.python.org/pep-0008/#programming-recommendations): com `None` usa-se sempre `is` ou `is not`. As ferramentas de revisão que você conhecerá na Lição 8 também apontam isso.

**Guardar um número como texto.** `codigo = "200"` parece o mesmo que `codigo = 200`, e já não é: `"200" >= 400` explode com outro `TypeError`, e `"200" + "1"` dá `"2001"`. O que é uma quantidade se guarda como número, sem aspas.

**Representar “não respondeu” com `0` ou com um texto.** `tiempo_ms = 0` diz “respondeu em zero milissegundos”, que é a resposta mais rápida possível, justamente o contrário da verdade; e um texto como `"sin respuesta"` não pode ser comparado com 1000. Um dado que falta se guarda como `None`, e o programa decide o que fazer com ele.

**Escrever `tiempo` sozinho.** Uma variável chamada `tiempo` não diz se são segundos ou milissegundos. Ponha a unidade no nome, e quando um número for uma quantidade com unidade, que o nome a carregue.

**Escrever o mesmo número em três lugares.** Se o limiar de lento está escrito como `1000` em cada comparação e amanhã muda para 800, você esquecerá uma. Dá-se um nome uma vez (`UMBRAL_LENTO_MS`) e usa-se pelo nome.

**Misturar tabulações e espaços.** O Python 3 se recusa a executar um bloco cujo recuo mistura os dois de maneira inconsistente, com um `TabError: inconsistent use of tabs and spaces in indentation`. O seu editor pode fazer isso sem avisar; configure-o para que Tab insira quatro espaços.

## Exercícios

### Exercício 1 — Os outros três serviços e um extra

Troque as cinco variáveis do seu `revisor.py` pelas de cada um dos outros três serviços, e **antes de executar cada vez, escreva em um papel a linha que você espera**:

| nome | url | código | tiempo_ms |
|---|---|---|---|
| `catalogo` | `https://catalogo.example` | 200 | 142 |
| `pagos` | `https://pagos.example` | 200 | 87 |
| `reportes` | `https://reportes.example` | `None` | `None` |

Depois teste com `facturacion` (`https://facturacion.example`), que responde com o código 503 em 95 ms. A sua previsão coincidiu nos quatro? Se não, que parte das regras você aplicou de modo diferente?

### Exercício 2 — Mover o limiar

Com o serviço `catalogo` (200, 142 ms), mude `UMBRAL_LENTO_MS` para 100 e preveja o estado. Depois deixe-o em 2500 e preveja o estado de `inventario` (200, 2300 ms). Explique em uma frase por que mudar **uma única linha** mudou o resultado nos dois casos.

### Exercício 3 — Provocar os três erros

Em uma cópia do seu programa, provoque um por um estes três erros e copie a mensagem exata da última linha: (a) tire os dois-pontos de um `elif`; (b) tire o recuo da linha que segue o `else`; (c) troque o `str(codigo)` de `detalle` por `"código " + codigo`. Para cada um, escreva o que a mensagem significa e qual é a correção.

### Exercício 4 — O mesmo ao contrário, e como salvá-lo

Parta de `fig02_11.py` (o das perguntas na ordem errada, que explode com `None`). Sem mudar a ordem dos dois primeiros ramos, corrija a **primeira pergunta** para que já não exploda com `reportes`. Dica: é preciso perguntar primeiro se `tiempo_ms` existe e depois compará-lo, e o operador que une duas perguntas obrigando que as duas se cumpram é `and`. Depois explique por que esta solução funciona graças ao curto-circuito.

## Soluções

### Solução 1

As previsões corretas, e o que o programa imprime com cada serviço (o cabeçalho é o mesmo de sempre):

```text
catalogo    ARRIBA     142ms  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
```

O de `facturacion` é o que mais se erra. Com o código 503, a primeira pergunta (`codigo >= 400`) é verdadeira, então o estado é CAIDO **embora tenha respondido em 95 ms**, que seria rapidíssimo. O tempo continua sendo mostrado (`95ms`) porque existe, e o detalhe é o código, `503`. Além disso, `facturacion` tem onze letras e cabe nas doze colunas do nome, mas quase sem margem: por isso a linha dele fica colada ao estado.

### Solução 2

Com `UMBRAL_LENTO_MS = 100`, o estado de `catalogo` (142 ms) passa de ARRIBA a **LENTO**: 142 já é maior ou igual a 100. Com o limiar em 2500, `inventario` (2300 ms) passa de LENTO a **ARRIBA**: 2300 já não chega a 2500. Nos dois casos o resultado mudou porque o limiar foi escrito uma única vez e todas as comparações o usam pelo nome; se o 1000 estivesse repetido em cada pergunta, seria preciso mudá-lo em todas.

### Solução 3

(a) Sem os dois-pontos do `elif`: `SyntaxError: expected ':'`. O Python esperava os dois-pontos que anunciam o bloco. Correção: pô-los no final da linha do `elif`.

(b) Sem recuo depois do `else`: `IndentationError: expected an indented block after 'else' statement on line N`, onde `N` é o número da linha do `else`. Correção: quatro espaços antes da linha que depende do `else`.

(c) `"código " + codigo`, com `codigo` valendo 200: `TypeError: can only concatenate str (not "int") to str`. Correção: `"código " + str(codigo)` ou, melhor, uma f-string: `f"código {codigo}"`.

### Solução 4

A primeira pergunta passa a ser `tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS`:

```python
if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"
```

Funciona pelo curto-circuito: com `tiempo_ms = None`, a primeira metade (`tiempo_ms is not None`) é falsa, e como um `and` com uma metade falsa já não pode ser verdadeiro, o Python **não avalia** a segunda metade, que era a que explodia. Mas atenção: esta versão é pior que a original em um caso. Com `codigo = 503` e `tiempo_ms = 2300`, um serviço que respondeu **lento e com erro** ficaria LENTO em vez de CAIDO, porque o ramo do tempo ganha do ramo do código. Corrigir o sintoma sem ordenar os ramos mudou as regras sem querer. É a melhor razão para deixar a pergunta do código primeiro.

## Como sei que consegui

- [ ] `python revisor.py` imprime exatamente duas linhas: `SERVICIO    ESTADO    TIEMPO  DETALLE` e `inventario  LENTO       2.3s  200`, com as colunas alinhadas como na figura `fig02_07.py`.
- [ ] Ao trocar as variáveis pelas de `reportes` (`codigo = None`, `tiempo_ms = None`), o programa imprime `reportes    CAIDO          —  sin conexión` e **não** termina com um *traceback*.
- [ ] Com `facturacion` (503, 95 ms) o estado é CAIDO e o detalhe é `503`.
- [ ] Você consegue provocar de propósito `SyntaxError: expected ':'`, `IndentationError` e `TypeError: can only concatenate str (not "int") to str`, e dizer em uma frase o que diz a última linha de cada um.
- [ ] Você consegue explicar com as suas palavras a diferença entre `=` e `==`, entre `200` e `"200"`, e entre `None` e `0`.
- [ ] Você consegue explicar por que a pergunta do código vai antes da do tempo na cadeia `if`/`elif`/`else`.

## Resumo

Responda sem olhar a lição:

1. Que tipo o `type()` devolve para `142`, para `2.3`, para `"142"`, para `True` e para `None`?
2. O que faz `=` e o que faz `==`? E por que `UMBRAL_LENTO_MS` vai em maiúsculas?
3. O que dão `10 / 2`, `7 // 2` e `7 % 2`? Por que `0.1 + 0.2` não dá `0.3`?
4. Como se pergunta se um valor é `None`, e por que não se usa `==`?
5. O que significam `:<12`, `:>6` e `:.1f` dentro de uma f-string?
6. Em uma cadeia `if`/`elif`/`else`, quantos blocos são executados no máximo, e qual? O que faz a indentação?
7. O que é o curto-circuito de `or` e de `and`, e que problema ele evita no `revisor`?
8. Qual é a última linha de um `SyntaxError` por esquecer os dois-pontos, e por que esse erro não mostra um *traceback*?

## Para ler mais

- [O tutorial do Python, “Uma introdução informal ao Python”](https://docs.python.org/pt-br/3/tutorial/introduction.html) — números, texto e variáveis, com a sessão interativa que você reconhecerá da Lição 1. Documentação oficial. Consultado em 7 de outubro de 2026.
- [O tutorial do Python, “Mais ferramentas de controle de fluxo”](https://docs.python.org/pt-br/3/tutorial/controlflow.html#if-statements) — a seção sobre `if`, `elif` e `else`. Consultado em 7 de outubro de 2026.
- [PEP 8, o guia de estilo do Python](https://peps.python.org/pep-0008/) — as convenções de nomes, de recuo e de comparação com `None` que este curso usa. Consultado em 7 de outubro de 2026.
- [Mini-linguagem de especificação de formato](https://docs.python.org/pt-br/3/library/string.html#format-specification-mini-language) — tudo o que pode ir depois dos dois-pontos em uma f-string; não é um texto para aprender de cabo a rabo, e sim para consultar. Consultado em 7 de outubro de 2026.
