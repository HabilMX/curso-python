# Lição 3 — Laços, funções e módulos

**Tempo:** 2 × 90 min (duas sessões)

**O que você constrói:** a função `revisar()` e o percurso da lista: um `revisor` de dois arquivos que imprime o cabeçalho e as linhas dos quatro serviços

**O que você aprende:** quatro conceitos. Primeiro, os laços (`for`, `while`, `range`, `enumerate`) e a lista mínima para percorrer; segundo, as funções (`def`, parâmetros, valores padrão, `return`, anotações simples e a armadilha do valor padrão que é uma lista); terceiro, os nomes (onde vive cada variável, `UnboundLocalError`, e `==` contra `is`); quarto, os módulos (`import`, `from ... import` e `if __name__ == "__main__":`)

**De onde você vem.** Você traz o `revisor.py` da [Lição 2](02-valores-texto-decisiones.md): umas trinta linhas que guardam **um** serviço (`inventario`) em variáveis, o classificam com um `if`/`elif`/`else` e o imprimem em uma linha alinhada, sob o cabeçalho da tabela. Funciona, mas tem um problema que já foi visto no final daquela lição: para revisar os outros três serviços seria preciso copiar o bloco três vezes e mudar os valores de cada cópia. Hoje esse problema sai do caminho. Você continua trabalhando em `~/curso-python/revisor/`, com o ambiente virtual ativo, e os programas são executados com `python arquivo.py`.

**Como a lição se divide.** Ela é longa, e por isso são duas sessões de 90 minutos com um corte natural no meio. **A primeira sessão** são os pontos 3.1 e 3.2 (laços e funções) e termina com a figura `fig03_11`, o `revisor` completo em **um** arquivo. **A segunda sessão** são os pontos 3.3 e 3.4 (nomes e módulos), os erros, os exercícios e o `revisor` repartido em dois arquivos. Se faltar tempo na primeira, pare ao chegar a `fig03_11`: o que vem depois se entende melhor com esse programa funcionando e a cabeça descansada.

**O que esta lição não faz.** Não vê as listas a fundo: hoje você usa uma lista **mínima** (criá-la, perguntar quantos elementos tem, ler um pela sua posição e acrescentar um), o justo para percorrê-la. Os dicionários, as tuplas, os conjuntos e as compreensões são da [Lição 4](04-colecciones.md), e o modelo de dados com `Servicio` e `Estado`, da [Lição 5](05-modelo-de-datos.md). E ainda não há erros capturados (`try`), nem arquivos, nem rede.

## Ao terminar, você vai conseguir

- Percorrer uma lista com `for` de três maneiras (por valor, por posição com `range(len(...))` e com `enumerate`) e repetir com `while` sem cair em um laço infinito.
- Criar uma lista, perguntar o seu tamanho com `len`, ler um elemento pela sua posição (que começa em 0) e acrescentar um com `.append`.
- Escrever uma função com parâmetros, valor padrão e `return`, com anotações de tipo simples (`int`, `str`, `int | None`, `-> None`), e explicar que diferença há entre imprimir e devolver.
- Explicar por que um valor padrão que é uma lista “lembra” das chamadas anteriores, e corrigir isso com o padrão do `None`.
- Dizer onde vive cada variável (local ou global) e ler `UnboundLocalError`.
- Explicar a diferença entre `==` (são iguais?) e `is` (são o mesmo objeto?) e saber em que caso se usa `is`.
- Repartir um programa em dois arquivos com `import` e `from ... import`, e explicar para que serve `if __name__ == "__main__":`.

## O porquê antes do como

Veja o que seria preciso fazer hoje, com o que você sabe da Lição 2, para que o `revisor` revise os quatro serviços. Copiar o bloco de `inventario` três vezes e, em cada cópia, mudar o nome, o código e o tempo. São cem linhas quase idênticas. E depois alguém decide que um serviço é lento a partir dos 800 milissegundos, não dos 1000: é preciso encontrar a comparação em cada cópia e mudá-la. Se você esquece uma, três serviços são classificados com uma regra e o quarto com outra, e o relatório mente sem dar nenhum erro.

Esse é o problema de fundo, e é o mesmo em todos os programas: **a mesma lógica escrita várias vezes tende a divergir**. O Python (e todas as linguagens) traz três ferramentas para resolvê-lo, que são as três desta lição:

- **Repetir sem copiar.** Um *laço* executa o mesmo bloco uma vez para cada elemento de uma lista, ou enquanto uma condição se cumprir. É o ponto 3.1.
- **Dar nome a um pedaço de lógica.** Uma *função* encerra uma receita (por exemplo, “classificar um serviço”) sob um nome, para usá-la de qualquer parte com valores diferentes. É o ponto 3.2. O preço das funções é que agora é preciso saber **onde vive cada nome**: uma variável que você cria dentro de uma função não é a mesma que outra de mesmo nome do lado de fora. Isso é o ponto 3.3.
- **Repartir o programa em arquivos.** Um *módulo* é um arquivo de Python que outro arquivo pode usar. Quando o programa cresce, cada arquivo guarda uma só classe de coisas (aqui, um para o formato da tabela e outro para a lógica da revisão). É o ponto 3.4.

No final da lição, `python revisor.py` imprimirá a tabela de quatro serviços que você viu na Lição 2, sem o resumo (que precisa contar, e isso chega na Lição 5):

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Um aviso de design, para que você não o leia como descuido. Os dados dos quatro serviços vão em **três listas paralelas**: uma de nomes, uma de códigos e uma de tempos, onde a posição 2 de cada lista fala do mesmo serviço. É uma maneira frágil de guardar dados: se uma lista se desordena ou fica curta, nada avisa você. **Faz-se assim de propósito**, porque é o que se pode fazer com o que você sabe hoje, e porque a fragilidade é a razão de a Lição 4 existir. No primeiro exercício você vai quebrá-lo de propósito para vê-la.

## Os conceitos

### 3.1 Laços: repetir sem copiar

#### 3.1.1 A lista mínima

Para repetir algo com cada serviço é preciso uma lista de serviços, e os valores da Lição 2 guardam um único dado cada um. É preciso apresentar a lista. Aqui se vê o mínimo; a Lição 4 a estuda a fundo.

Uma **lista** é uma sequência ordenada de valores, escrita entre colchetes e com os elementos separados por vírgulas: `["catalogo", "inventario", "pagos", "reportes"]`. Uma lista pode misturar tipos (a dos códigos tem números e um `None`), e é guardada sob um nome como qualquer outro valor. Quatro operações bastam por ora, e as quatro estão na figura seguinte. Salve-a como `fig03_01.py`:

```python
# fig03_01.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]

print(nombres)
print(len(nombres))
print(nombres[0])
print(nombres[3])

nombres.append("facturacion")
print(len(nombres))
print(nombres[4])
```

```text
$ python fig03_01.py
['catalogo', 'inventario', 'pagos', 'reportes']
4
catalogo
reportes
5
facturacion
```

Linha por linha. `print(nombres)` mostra a lista completa, com os seus colchetes. `len(nombres)` devolve quantos elementos ela tem: quatro. O que vem a seguir é o que mais desconcerta o iniciante: **as posições começam em 0**. `nombres[0]` é o primeiro elemento (`catalogo`) e `nombres[3]` é o quarto (`reportes`). A razão de fundo é que a posição diz o quanto você se afasta do começo: o primeiro elemento está a zero passos. A consequência prática, de que você vai precisar em todo o curso, é que uma lista de quatro elementos tem as posições 0, 1, 2 e 3, e **não tem a posição 4**; a última posição é sempre `len(lista) - 1`.

A última parte da figura acrescenta um elemento: `nombres.append("facturacion")` o cola no final. O ponto e o parêntese significam que `append` é um *método* da lista, isto é, uma operação que a lista sabe fazer sobre si mesma (os métodos são as funções que “pertencem” a um valor, e você os verá mais com os textos e os dicionários). Depois de acrescentá-lo, `len` dá 5 e a posição 4 já existe. Repare que `append` **mudou a lista no lugar**: não devolveu uma lista nova, modificou a que já tinha. Os valores que podem mudar assim se chamam *mutáveis*, e essa propriedade volta a aparecer mais duas vezes nesta lição, então guarde-a na cabeça.

Um detalhe de estilo: nesta figura o nome da lista vai em minúsculas (`nombres`) porque ela muda, e nas figuras seguintes, quando as listas forem dados fixos do programa, irão em maiúsculas (`NOMBRES`), como o resto das constantes.

#### 3.1.2 `for`: fazer algo com cada elemento

O laço `for` executa um bloco uma vez para cada elemento de uma lista. Salve `fig03_02.py`:

```python
# fig03_02.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]

for nombre in nombres:
    print("revisando", nombre)

print("listo")
```

```text
$ python fig03_02.py
revisando catalogo
revisando inventario
revisando pagos
revisando reportes
listo
```

A primeira linha do laço se lê quase em português: “para cada `nombre` em `nombres`”. Termina com **dois-pontos**, e o bloco que repete vai **com indentação** (quatro espaços), igual a um `if`. O Python faz isto: pega o primeiro elemento da lista, o guarda sob o nome `nombre`, executa o bloco; pega o segundo, o guarda sob o mesmo nome, executa o bloco; e assim até acabarem. A última linha, `print("listo")`, está na margem esquerda: já não faz parte do bloco, e por isso é executada uma única vez no final. É a mesma regra da Lição 2: a indentação diz onde termina um bloco.

O nome `nombre` foi você quem escolheu. Poderia se chamar `x` ou `servicio`; mas um bom nome conta o que há dentro (a cada volta, `nombre` é *um* nome, e a lista é `nombres`, no plural). Esta é uma convenção muito útil: lista no plural, elemento no singular.

#### 3.1.3 `range`: percorrer por posição

Às vezes o valor não basta; você precisa da **posição** dele. Isso acontece com as listas paralelas do `revisor`: para saber o tempo do serviço que você está olhando, precisa da mesma posição na lista de tempos. Para isso existe o `range`: `range(4)` produz os números 0, 1, 2 e 3 (os quatro primeiros, começando em zero, sem incluir o 4). E como `len(NOMBRES)` vale 4, `range(len(NOMBRES))` produz exatamente as posições válidas da lista. Salve `fig03_03.py`:

```python
# fig03_03.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(3):
    print(i)

for i in range(len(NOMBRES)):
    print(i, NOMBRES[i], TIEMPOS_MS[i])
```

```text
$ python fig03_03.py
0
1
2
0 catalogo 142
1 inventario 2300
2 pagos 87
3 reportes None
```

O primeiro laço só imprime os números que `range(3)` produz: `0`, `1` e `2`. O segundo é o que importa: a cada volta, `i` vale uma posição, e as duas listas são lidas nessa mesma posição, `NOMBRES[i]` e `TIEMPOS_MS[i]`. Observe que isso **só funciona se as duas listas têm o mesmo tamanho**; se `TIEMPOS_MS` tivesse um elemento a menos, a última volta falharia. Esse é o defeito das listas paralelas, e há um exercício para ele.

Uma nota sobre os nomes: `i` é o costume universal para “uma posição” (vem de *index*, “índice”), e é dos poucos nomes de uma letra que se aceitam. Para todo o resto, nomes que digam o que são.

#### 3.1.4 `enumerate`: o valor e a sua posição juntos

Quando você precisa do valor **e** da posição, o `enumerate` entrega os dois de uma vez. A cada volta entrega um par, e a sintaxe `for i, nombre in enumerate(...)` põe o primeiro elemento do par em `i` e o segundo em `nombre`. A isso se chama *desempacotar*. Salve `fig03_04.py`:

```python
# fig03_04.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]

for i, nombre in enumerate(NOMBRES):
    print(i, nombre)

for numero, nombre in enumerate(NOMBRES, start=1):
    print(f"{numero}. {nombre}")
```

```text
$ python fig03_04.py
0 catalogo
1 inventario
2 pagos
3 reportes
1. catalogo
2. inventario
3. pagos
4. reportes
```

O primeiro laço imprime as posições a partir de 0 com o seu nome. O segundo usa um segundo argumento, `start=1`, para que a contagem comece em 1: assim se numeram as coisas para as pessoas. Esse `start=1` é um **argumento nomeado**, e você o entenderá melhor no ponto 3.2.

O `enumerate` é a maneira mais legível de percorrer **uma** lista com a sua posição. No `revisor` de hoje há **três** listas paralelas, então a posição é o que as une e o percurso é o de `range(len(NOMBRES))`; com três listas, o `enumerate` só ajuda com uma. Mas convém que você o conheça, porque assim que o `revisor` deixar para trás as listas paralelas (Lição 4), ele percorrerá **uma** única lista, e quando além disso for preciso a posição, o `enumerate` será a ferramenta natural (você o usará na Lição 6).

#### 3.1.5 `while`: repetir enquanto algo for verdadeiro

O `for` repete uma vez para cada elemento de algo que já existe. O `while` repete **enquanto uma condição for verdadeira**, sem saber de antemão quantas voltas serão. Pergunta de novo a condição antes de cada volta, e para quando a resposta é `False`. Salve `fig03_05.py`, que busca a posição do primeiro serviço que não respondeu:

```python
# fig03_05.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]

i = 0
while i < len(CODIGOS) and CODIGOS[i] is not None:
    i += 1

print("primer servicio sin respuesta, en la posición", i)
print(NOMBRES[i])
```

```text
$ python fig03_05.py
primer servicio sin respuesta, en la posición 3
reportes
```

Antes de começar, `i` vale 0. Cada volta pergunta duas coisas unidas com `and`: `i` ainda está dentro da lista? e o código nessa posição existe (`is not None`, que é a negação de `is None`)? Enquanto as duas forem verdadeiras, executa o bloco, que diz `i += 1`. Essa linha é a abreviação de `i = i + 1`: soma 1 e guarda o resultado no mesmo nome. Na posição 3 o código é `None`, a segunda pergunta falha e o laço termina com `i` valendo 3.

Repare na **ordem das duas perguntas**, porque é a lição 2 de novo. `i < len(CODIGOS)` vai primeiro para que, se `i` chegasse a valer 4, o `and` já fosse falso e o Python **não tentasse** ler `CODIGOS[4]`, que não existe. O curto-circuito protegeu você.

Com o `while` há um risco que o `for` não tem: **o laço infinito**. Se o bloco não muda nada do que a condição pergunta, a condição nunca se torna falsa e o programa fica dando voltas para sempre. Se você esquecesse o `i += 1` da figura, isso aconteceria. Quando um programa trava assim, a saída de emergência é `Ctrl`+`C` no terminal, que o interrompe. A regra para escrever um `while` é: **antes de executá-lo, localize a linha do bloco que aproxima a condição de ser falsa**. E quando for possível usar um `for`, use-o: o `for` termina por construção quando os elementos acabam.

#### 3.1.6 Acumular, pular e sair

Dois usos muito frequentes dos laços completam o ponto. O primeiro é **acumular**: percorrer os dados para tirar uma conta. Salve `fig03_06.py`, que soma os tempos dos serviços que responderam:

```python
# fig03_06.py
TIEMPOS_MS = [142, 2300, 87, None]

total = 0
respondieron = 0
for tiempo_ms in TIEMPOS_MS:
    if tiempo_ms is not None:
        total += tiempo_ms
        respondieron += 1

print("suma:", total, "ms")
print("respondieron:", respondieron)
print("promedio:", total / respondieron, "ms")
```

```text
$ python fig03_06.py
suma: 2529 ms
respondieron: 3
promedio: 843.0 ms
```

O padrão se repete em quase todos os programas: antes do laço, criam-se as variáveis que acumulam (`total` e `respondieron`, em zero); dentro do laço, são atualizadas; depois, são usadas. O `if` do bloco deixa de fora o serviço que não respondeu, cujo tempo é `None`; sem ele, `total += None` falharia com um `TypeError`, como o da Lição 2. A soma é 2529 (142 + 2300 + 87), responderam três, e a média dos que responderam é 843. Sai com um `.0` porque a divisão `/` sempre dá um decimal; a Lição 4 ensina a arredondá-la, e a 5 a usa no resumo da tabela.

O segundo uso é **controlar o laço de dentro** com duas palavras: `continue` pula para a volta seguinte sem terminar o bloco, e `break` sai do laço por completo. Salve `fig03_07.py`, que busca o primeiro serviço lento:

```python
# fig03_07.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(len(NOMBRES)):
    if TIEMPOS_MS[i] is None:
        continue
    if TIEMPOS_MS[i] >= 1000:
        print("primer servicio lento:", NOMBRES[i])
        break
```

```text
$ python fig03_07.py
primer servicio lento: inventario
```

Com `catalogo` (142 ms), o laço pergunta se ele tem tempo (sim), pergunta se é lento (não) e passa para a volta seguinte. Com `inventario` (2300), a segunda pergunta é verdadeira: imprime o nome e o `break` termina o laço, então `pagos` e `reportes` nem são olhados. Se o primeiro tivesse sido `reportes` (com `None`), o `continue` teria pulado essa volta antes de comparar `None >= 1000`, que explode. Use `break` e `continue` com moderação: são cômodos e escondem o fluxo do programa quando se abusa deles.

### 3.2 Funções: dar nome a uma receita

#### 3.2.1 Definir e chamar

Uma **função** é um bloco de código com nome que você pode executar quando quiser, quantas vezes quiser, com dados diferentes a cada vez. Você já usou funções que vêm com o Python: `print`, `len`, `range`, `type`, `str`. Agora vai escrever as suas, com a palavra `def` (“definir”). A primeira é a da formatação do tempo, que na Lição 2 estava escrita como um bloco `if` dentro do programa. Salve `fig03_08.py`:

```python
# fig03_08.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


print(formatear_tiempo(87))
print(formatear_tiempo(999))
print(formatear_tiempo(1000))
print(formatear_tiempo(2300))
print(formatear_tiempo(None))
```

```text
$ python fig03_08.py
87ms
999ms
1.0s
2.3s
—
```

Esta figura tem duas partes bem separadas, e entender a separação é o mais importante do ponto. **A definição** são as primeiras seis linhas, do `def` até o último `return`: explicam ao Python o que faz `formatear_tiempo`, mas **não a executam**. É como escrever uma receita em um cartão: a receita existe, mas ninguém cozinhou nada. **As chamadas** são as últimas cinco linhas: cada `formatear_tiempo(...)` pede ao Python que execute a receita com um dado concreto, e é aí que o trabalho é feito. Se você tirasse as chamadas, o programa rodaria sem imprimir nada.

A linha do `def` tem quatro partes. `def` anuncia a definição. `formatear_tiempo` é o nome (em minúsculas com sublinhado, como uma variável). Entre parênteses vão os **parâmetros**: os nomes que a função usa para se referir aos dados que recebe; aqui um, `tiempo_ms`. E no final, os dois-pontos e o bloco com indentação, o **corpo** da função. Uma distinção de vocabulário que muito se confunde: o **parâmetro** é o nome que aparece na definição (`tiempo_ms`), e o **argumento** é o valor que se passa na chamada (o `87`, o `999`). Cada vez que a função é chamada, os argumentos são atribuídos aos parâmetros e o corpo é executado.

A palavra **`return`** faz duas coisas ao mesmo tempo: **termina a função nesse ponto** e **entrega um valor** a quem a chamou. Por isso a função de cima não precisa de `elif` nem de `else`: se `tiempo_ms` é `None`, o primeiro `return` termina a função e as linhas seguintes nunca são executadas; se não é, segue-se com a pergunta seguinte. Compare com a versão da Lição 2: faz o mesmo, com menos ramos, porque cada `return` já fecha o caminho. O valor que ela devolve pode ser impresso, guardado em uma variável ou usado dentro de outra expressão, igual a qualquer outro valor.

Os casos da saída são os cinco que você vai testar em todo o curso: 87 é `87ms`; 999 é `999ms` (ainda menos de um segundo); **1000 é `1.0s`**, bem na borda; 2300 é `2.3s`; e `None`, que não tem tempo, é o travessão.

#### 3.2.2 Imprimir não é devolver

Um erro clássico do iniciante é confundir duas coisas que na tela se parecem: **imprimir** um valor e **devolvê-lo**. O `print` mostra algo no terminal e pronto; o `return` entrega o valor ao código que chamou a função, que pode fazer com ele o que quiser. Salve `fig03_09.py` para ver:

```python
# fig03_09.py
def decir_tiempo(tiempo_ms: int) -> None:
    print(f"{tiempo_ms}ms")


def dar_tiempo(tiempo_ms: int) -> str:
    return f"{tiempo_ms}ms"


a = decir_tiempo(87)
b = dar_tiempo(87)
print(a)
print(b)
print(type(a))
print(type(b))
```

```text
$ python fig03_09.py
87ms
None
87ms
<class 'NoneType'>
<class 'str'>
```

A primeira linha da saída (`87ms`) foi impressa por `decir_tiempo` ao ser chamada, dentro do seu corpo; nada mais. Mas `a`, o que essa função **devolveu**, é `None`: uma função que não tem `return` devolve `None` automaticamente. Já `dar_tiempo` não imprimiu nada; devolveu o texto, e `b` o guarda. Por isso as duas linhas seguintes imprimem `None` e `87ms`, e os tipos são `NoneType` e `str`. A regra prática: **uma função que calcula algo deve devolvê-lo, não imprimi-lo**, e quem a chama decide se o imprime. Uma função que imprime em vez de devolver é difícil de reutilizar e mais difícil de testar: a Lição 8 testa funções comparando o que devolvem com o que deviam devolver, e o que só se imprime também pode ser conferido, mas é preciso capturar o que sai na tela (a Lição 11 faz isso) em vez de comparar um valor.

#### 3.2.3 Valores padrão e argumentos nomeados

Às vezes um parâmetro quase sempre tem o mesmo valor. Em vez de exigi-lo em cada chamada, pode-se dar a ele um **valor padrão** na definição, com um sinal de igual: `umbral_ms: int = UMBRAL_LENTO_MS`. Se a chamada não o passa, usa-se esse valor; se passa, usa-se o novo. E quando uma chamada tem muitos argumentos, eles podem ser escritos **com nome** (`umbral_ms=100`) para não depender da ordem e para que se leia o que é cada um. [O tutorial oficial os explica com mais exemplos](https://docs.python.org/pt-br/3/tutorial/controlflow.html#more-on-defining-functions). Salve `fig03_10.py`, que é a classificação da Lição 2 convertida em função:

```python
# fig03_10.py
UMBRAL_LENTO_MS = 1000


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


print(clasificar(200, 142))
print(clasificar(200, 999))
print(clasificar(200, 1000))
print(clasificar(200, 2300))
print(clasificar(503, 95))
print(clasificar(None, None))
print(clasificar(200, 142, umbral_ms=100))
print(clasificar(codigo=200, tiempo_ms=2300))
```

```text
$ python fig03_10.py
ARRIBA
ARRIBA
LENTO
LENTO
CAIDO
CAIDO
LENTO
LENTO
```

A definição segue as quatro regras do `revisor`, na mesma ordem da Lição 2: primeiro, sem código ou com código de erro, CAIDO; depois, LENTO se houve resposta e o tempo chegou ao limiar; se não, ARRIBA. A pergunta `tiempo_ms is not None and ...` tem o `and` nessa ordem pela mesma razão de sempre, e como `tiempo_ms` admite `None` na sua anotação, o programa se protege embora, na prática, um serviço que respondeu sempre traga o seu tempo. A assinatura foi partida em três linhas porque não cabia em uma: é assim que o formatador automático do Python a escreve (a Lição 8 o apresenta), e é o normal quando a lista de parâmetros é longa.

As primeiras seis chamadas são os casos da tabela de regras, na ordem da saída: ARRIBA, ARRIBA, **LENTO na borda de 1000**, LENTO, CAIDO pelo código 503 (embora tenha respondido em 95 ms) e CAIDO por não haver resposta. Na sétima, `umbral_ms=100` **sobrescreve o valor padrão** só para essa chamada: 142 ms já é lento se o limite é 100. Na oitava, os dois argumentos vão com nome, e podem ser escritos em qualquer ordem. Se você esquece um argumento que não tem valor padrão, o Python reclama com `TypeError: clasificar() missing 1 required positional argument: 'tiempo_ms'`: “falta um argumento posicional obrigatório a `clasificar()`”.

#### 3.2.4 Anotações de tipo simples

Você terá reparado que os parâmetros e as funções levam coisas como `: int | None` e `-> str`. Chamam-se **anotações de tipo** e dizem que tipo de valor se espera e que tipo a função devolve. Escrevem-se assim:

- `tiempo_ms: int` — este parâmetro é um inteiro.
- `tiempo_ms: int | None` — este parâmetro é um inteiro **ou** `None` (a barra se lê “ou”). É a forma de dizer “pode não haver dado”.
- `-> str` — a função devolve um texto.
- `-> None` — a função não devolve nada útil (devolve `None`).
- `caidos: list[str]` — uma lista de textos. Os colchetes dizem o que há dentro da lista.

Um fato que você já viu na Lição 0 e que importa repetir: **o Python não impõe as anotações na execução**. Se você chama `clasificar("hola", "mundo")`, o programa não reclama dos tipos (reclama, talvez, mais adiante, por outro motivo). As anotações servem a dois leitores: às pessoas, que entendem o que cada função espera sem ler o corpo dela, e às ferramentas de revisão, que as conferem sem executar o código. A sintaxe chegou com [a PEP 3107](https://peps.python.org/pep-3107/), no Python 3.0, que deixou de propósito sem definir para que serviam; [a PEP 484](https://peps.python.org/pep-0484/) deu a elas o uso atual, os tipos, e diz com todas as letras que “no type checking happens at runtime”: ao executar, nenhum tipo é conferido. A ferramenta que as confere (`mypy`) chega na Lição 8; até lá você as escreve porque ajudam a ler e porque é muito mais fácil escrevê-las quando uma função nasce do que acrescentá-las depois.

#### 3.2.5 Um `revisor` completo em um só arquivo

Com as funções você já pode montar o percurso. Faltam mais duas funções: uma que monte a linha (`linea`) e outra que junte tudo para um serviço (`revisar`). E o cabeçalho, que também é uma função, porque assim se escreve uma só vez. Salve `fig03_11.py`, que reúne tudo em um arquivo:

```python
# fig03_11.py
UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


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


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str, codigo: int | None, tiempo_ms: int | None) -> str:
    estado = clasificar(codigo, tiempo_ms)
    if codigo is None:
        detalle = "sin conexión"
    else:
        detalle = str(codigo)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    print(encabezado())
    for i in range(len(NOMBRES)):
        print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))


main()
```

```text
$ python fig03_11.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Leia a figura de baixo para cima, porque assim se entende como as funções se apoiam. No final, `main()` é a chamada que põe tudo em marcha; `main` (“principal”) é o nome que por costume se dá à função que inicia o programa. Dentro de `main`, o laço `for i in range(len(NOMBRES))` percorre as posições das listas paralelas e, a cada volta, chama `revisar` com o nome, o código e o tempo dessa posição. `revisar` faz três coisas: pede o estado a `clasificar`, calcula o detalhe com o mesmo `if`/`else` da Lição 2 (o código como texto, ou “sin conexión”), e passa tudo a `linea`, que monta a linha com ajuda de `formatear_tiempo`. Cada função faz **uma coisa**, tem um nome que diz qual, e pode ser testada sozinha.

Há dois detalhes que convém notar. Um: as constantes (`UMBRAL_LENTO_MS` e as três listas) estão no começo do arquivo e as funções não as recebem como argumento. Uma função pode **ler** variáveis que estão definidas fora dela; o ponto 3.3 explica quando sim e quando não. Dois: o 1000 de `formatear_tiempo` (os milissegundos de um segundo) e o `UMBRAL_LENTO_MS` (o limite do que é lento) continuam sendo coisas diferentes, igual à Lição 2. E lembre de onde vem o `if`/`else` de `revisar`: quando o código é `None`, o detalhe é “sin conexión”, e o código de erro é mostrado tal qual, como `503`.

Aqui termina a primeira sessão. O que você leva: um programa que percorre os quatro serviços e que, para mudar o limiar ou o formato do tempo, tem um único lugar para mexer.

### 3.3 Nomes: onde vive cada variável, e `==` contra `is`

#### 3.3.1 Local e global

Quando o Python vê um nome, precisa saber **a qual variável ele se refere**. A regra se chama *escopo* (em inglês, *scope*), e [está no tutorial oficial](https://docs.python.org/pt-br/3/tutorial/classes.html#python-scopes-and-namespaces). Para esta lição bastam duas classes de nomes:

- **Global**: o que é criado no nível do arquivo, fora de qualquer função. `UMBRAL_LENTO_MS` e `NOMBRES` são globais.
- **Local**: o que é criado **dentro** de uma função, incluindo os seus parâmetros. Existe só enquanto a função é executada, e desaparece quando ela termina. Cada chamada à função cria os seus próprios nomes locais, à parte dos das outras chamadas.

Uma função pode **ler** nomes globais sem problema, mas os locais de uma função não são vistos de fora. Salve `fig03_12.py`:

```python
# fig03_12.py
UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    limite = UMBRAL_LENTO_MS
    return tiempo_ms >= limite


print(es_lento(2300))
print(es_lento(142))
```

```text
$ python fig03_12.py
True
False
```

Dentro de `es_lento`, `UMBRAL_LENTO_MS` é global e é lido com naturalidade; `tiempo_ms` e `limite` são locais. Fora da função, `limite` não existe. Se você acrescentar no final do programa uma linha `print(limite)`, o Python para com este erro (experimente e confira que a sua tela diz o mesmo):

<!-- frag: prueba_ambito.py -->
```python
UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    limite = UMBRAL_LENTO_MS
    return tiempo_ms >= limite


print(es_lento(2300))
print(limite)
```

```text
True
Traceback (most recent call last):
  File "prueba_ambito.py", line 10, in <module>
    print(limite)
          ^^^^^^
NameError: name 'limite' is not defined
```

A última linha é a que manda: `NameError`, o nome `limite` não está definido. A primeira linha da saída, `True`, é a que `es_lento(2300)` chegou a imprimir antes da queda. Este é o modo como o Python diz “neste lugar do programa, esse nome não existe”, e é o segundo erro mais comum do iniciante depois do dos dois-pontos. Quase sempre é uma de três coisas: você errou ao escrever o nome (lembre que as maiúsculas contam), usou o nome antes de criá-lo, ou o criou dentro de uma função e o procura do lado de fora.

#### 3.3.2 Atribuir dentro de uma função cria um nome local

Há uma regra do escopo que surpreende quase todos, e que produz o erro da seção seguinte. O que decide se um nome é local ou global **não é se ele existe do lado de fora, e sim se a função atribui um valor a ele em alguma parte do seu corpo**. Se dentro da função há uma atribuição a `total` (com `=` ou com `+=`, que é uma atribuição disfarçada), o Python decide, antes de executar qualquer coisa, que `total` é **local em toda essa função**. Mesmo que exista um `total` global, a função não mexe nele: usa um local, e se você o lê antes de atribuí-lo, ele ainda não tem valor.

Isso, que parece um capricho, protege os seus programas: uma função que muda variáveis globais sem que se note torna o programa impossível de entender (quem mudou `total`?). A maneira correta de uma função afetar o resto do programa é a que você já conhece: **recebe o que precisa como parâmetros e devolve o que calculou**. O Python tem uma palavra, `global`, que permite o contrário, e eu a menciono só para que você a reconheça quando a vir em código alheio. Neste curso ela não é usada.

#### 3.3.3 `==` contra `is`

O Python tem duas maneiras de perguntar se duas coisas são “a mesma coisa”, e significam coisas diferentes:

- **`a == b`** pergunta se **têm o mesmo valor**: são iguais?
- **`a is b`** pergunta se **são o mesmo objeto**: são literalmente a mesma coisa na memória, a mesma?

Há uma analogia útil: duas notas de cem reais são iguais em valor (`==`), mas não são a mesma nota (`is`). Salve `fig03_13.py`:

```python
# fig03_13.py
a = [200, 142]
b = [200, 142]
c = a

print(a == b)
print(a is b)
print(a is c)
```

```text
$ python fig03_13.py
True
False
True
```

`a` e `b` são duas listas **diferentes** com o mesmo conteúdo: são iguais (`True`), mas não são a mesma (`False`). Já `c = a` não copia a lista: faz com que `c` seja **outro nome para a mesma lista**, e por isso `a is c` é `True`. (O que acontece quando essa lista muda, e como se faz uma cópia de verdade, é o tema de “cópia contra referência” na Lição 4.)

Então, quando se usa cada uma? **Quase sempre `==`**, para comparar valores: códigos, textos, tempos. **`is` se reserva para `None`**: como no programa existe um único `None`, a pergunta correta é se o valor *é* esse objeto, e por isso a Lição 2 fez você escrever `codigo is None`. É o que pede o [guia de estilo](https://peps.python.org/pep-0008/#programming-recommendations). Com `True` e `False` nem sequer é preciso comparar: se `activo` já é um booleano, escreve-se `if activo:`, e o mesmo guia qualifica `if activo == True:` de incorreto e `if activo is True:` de pior.

O perigo está em usar `is` com números ou textos, porque às vezes **parece funcionar**. O Python, por eficiência, reutiliza o mesmo objeto para os números inteiros pequenos: [a documentação diz que guarda um para cada inteiro entre -5 e 256](https://docs.python.org/pt-br/3/c-api/long.html#c.PyLong_FromLong). Isso é um detalhe da implementação do CPython, o Python que você usa, e não uma promessa da linguagem. O REPL mostra:

```pycon
>>> a = 100
>>> b = 100
>>> a is b
True
>>> a = 1000
>>> b = 1000
>>> a is b
False
```

Com 100 a comparação sai certa por acidente; com 1000, errada. Uma comparação com `is` que funciona com uns números e não com outros é um erro esperando o dia de aparecer. O Python avisa quando vê algo assim. Se você salvar o programa seguinte e executá-lo, ele funciona, mas primeiro imprime um aviso:

<!-- frag: prueba_is.py -->
```python
codigo = 200
if codigo is 200:
    print("contestó bien")
```

```text
prueba_is.py:2: SyntaxWarning: "is" with 'int' literal. Did you mean "=="?
  if codigo is 200:
contestó bien
```

É um `SyntaxWarning`, um aviso, não um erro: o programa seguiu e terminou bem. Leia-o mesmo assim. Diz exatamente o que você fez de errado e o que queria fazer: `"is"` com um número literal, “você queria `==`?”. Os avisos são a maneira que o Python tem de dizer algo que hoje não explode, mas que amanhã pode mentir a você.

### 3.4 Módulos: repartir o programa em arquivos

#### 3.4.1 Um arquivo é um módulo

Um programa de cem linhas cabe em um arquivo; um de mil já não se lê bem. A solução de sempre é repartí-lo: cada arquivo guarda uma só classe de coisas, e os demais o usam. Em Python, **cada arquivo `.py` é um *módulo***, e um arquivo usa outro com a palavra **`import`**. O Python traz além disso centenas de módulos já escritos, a *biblioteca padrão*, que são importados do mesmo jeito (por exemplo, `statistics`, para estatística básica).

Há duas formas de importar, e as duas aparecem no `revisor`:

- **`import modulo`**: traz o módulo completo, e os seus nomes são usados com o prefixo do módulo: `modulo.nombre`. É a forma que deixa mais claro de onde vem cada coisa.
- **`from modulo import nombre1, nombre2`**: traz só esses nomes, e eles são usados diretamente, sem prefixo. É cômoda quando você só precisa de uma ou duas coisas.

Quando o Python importa um módulo, segundo [a documentação de módulos](https://docs.python.org/pt-br/3/tutorial/modules.html#the-module-search-path), primeiro olha se é um dos poucos módulos **embutidos** no próprio interpretador (como `sys`); se não é, o procura **na pasta do arquivo que está executando** e depois na biblioteca padrão e nos lugares onde o `pip` instala coisas. Por isso, para que `import formato` funcione, `formato.py` tem que estar na mesma pasta que `revisor.py`. Na primeira vez que você importa um módulo, o Python além disso o traduz para *bytecode* (lembre da Lição 0) e guarda o resultado em uma pasta chamada `__pycache__` junto a ele, para que na próxima vez carregue mais rápido. Essa pasta aparece sozinha; não a edite nem a guarde em nenhum repositório.

#### 3.4.2 `if __name__ == "__main__":`

Um arquivo pode ser duas coisas: um **programa** que se executa (`python revisor.py`) ou um **módulo** que outro arquivo importa. Às vezes é as duas. É preciso uma maneira de distinguir os dois casos, porque quando alguém importa o seu módulo não quer que o programa comece sozinho. O Python resolve isso com uma variável especial, `__name__` (com dois sublinhados de cada lado, que se leem “dunder”): **vale `"__main__"` quando o arquivo está sendo executado diretamente, e vale o nome do módulo quando foi importado**. [A documentação do módulo `__main__`](https://docs.python.org/pt-br/3/library/__main__.html) explica esse comportamento e a construção idiomática que o aproveita. Salve os dois arquivos da figura `fig03_14`, em uma pasta com esse nome:

```python
# fig03_14/medidas.py
print("medidas.py: __name__ vale", __name__)


def segundos(tiempo_ms: int) -> float:
    return tiempo_ms / 1000


if __name__ == "__main__":
    print("medidas.py se está ejecutando directamente")
    print(segundos(2300))
```

```python
# fig03_14/uso.py
import statistics

import medidas

print("uso.py: __name__ vale", __name__)
print(medidas.segundos(87))
print(statistics.mean([142, 2300, 87]))
```

Execute cada arquivo separadamente, a partir da pasta `fig03_14`:

```text
$ cd fig03_14
$ python medidas.py
medidas.py: __name__ vale __main__
medidas.py se está ejecutando directamente
2.3
$ python uso.py
medidas.py: __name__ vale medidas
uso.py: __name__ vale __main__
0.087
843
```

Quando `medidas.py` é executado diretamente, `__name__` vale `__main__`, e por isso o `if` do final se cumpre e as duas linhas de baixo são impressas. Quando `uso.py` é executado, o `import medidas` faz o Python **executar `medidas.py` de cima a baixo uma vez**, e desta vez `__name__` vale `medidas`, o nome do módulo, então o `if` não se cumpre e as duas linhas finais não saem. Depois `uso.py` segue, com o seu próprio `__name__` valendo `__main__`, e usa `medidas.segundos` com o prefixo do módulo. A última linha usa um módulo da biblioteca padrão: `statistics.mean` calcula a média da lista, e dá 843, o número que na figura `fig03_06` saiu com `.0` por dividir à mão.

Isso é o que significa essa construção idiomática:

```text
if __name__ == "__main__":
    main()
```

“Se este arquivo está sendo executado como programa, chame `main()`”. Se em vez disso alguém o importa, não faz nada, e as funções ficam disponíveis. É um costume de quase todo programa sério em Python, e é o que fecha o `revisor` abaixo.

#### 3.4.3 Partir o `revisor` em dois arquivos

Com tudo isso, o `revisor` fica repartido em dois módulos com uma divisão de responsabilidades clara. `formato.py` guarda **tudo o que tem a ver com o aspecto da tabela** (o formato do tempo, o cabeçalho e a linha). `revisor.py` guarda **tudo o que tem a ver com revisar** (os dados, a classificação e o percurso), e importa de `formato` o que precisa. Esta é a figura de projeto da lição: uma pasta `fig03_15` com dois arquivos. É o estado em que fica o seu `~/curso-python/revisor/` ao terminar a lição, e o ponto de partida da Lição 4.

```python
# fig03_15/formato.py
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
# fig03_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str, codigo: int | None, tiempo_ms: int | None) -> str:
    estado = clasificar(codigo, tiempo_ms)
    if codigo is None:
        detalle = "sin conexión"
    else:
        detalle = str(codigo)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    print(encabezado())
    for i in range(len(NOMBRES)):
        print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))


if __name__ == "__main__":
    main()
```

```text
$ cd fig03_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Observe três coisas. **Primeiro**, `from formato import encabezado, linea` traz só duas das três funções de `formato.py`: `formatear_tiempo` não é usada em `revisor.py` (quem a usa é `linea`, por dentro), e não é preciso trazê-la. **Segundo**, o programa imprime exatamente a mesma tabela que `fig03_11`, o de um só arquivo: partir um programa não muda o que ele faz, só onde vive cada peça. **Terceiro**, a última linha já não é `main()` sozinho, e sim a construção idiomática do ponto anterior; agora, se no futuro outro arquivo importar `revisor`, a tabela não será impressa sem querer. É justamente o que você vai precisar quando, mais adiante, escrever testes que importem as suas funções.

Depois de executá-lo, olhe o que apareceu na pasta:

```console
$ ls
formato.py  __pycache__  revisor.py
```

Esse `__pycache__` é o que o Python criou ao importar `formato`; ali guardou a versão em *bytecode*. (A ordem em que o `ls` arruma os nomes depende da configuração de idioma do seu terminal, então pode sair diferente para você.) Se ali dentro você vir um arquivo `formato.cpython-312.pyc`, o `312` é a versão do Python que o gerou; com outra versão, o número muda.

Um último detalhe de design: `formato.py` não sabe **nada** de serviços. Só recebe um nome, um estado, um tempo e um detalhe, e devolve texto. Essa ignorância é uma virtude: o módulo de formato pode continuar quase igual quando, nas lições 4 e 5, os dados mudarem de forma.

## O erro que você vai ver

Esta lição tem dois erros que são dela, e os dois se aprendem melhor provocando-os. Ambos foram copiados de uma execução real. E um lembrete para ler qualquer *traceback*: a última linha diz **o que** aconteceu; as de cima, **onde**, da mais recente (embaixo) à mais antiga (em cima) na cadeia de chamadas.

### `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`

É o erro do ponto 3.3.2. Salve este programa, que tenta acumular um total de dentro de uma função, e execute:

<!-- frag: prueba_total.py 312-distinto -->
```python
total = 0


def sumar_tiempo(tiempo_ms: int) -> None:
    total += tiempo_ms


sumar_tiempo(142)
print(total)
```

```text
Traceback (most recent call last):
  File "prueba_total.py", line 8, in <module>
    sumar_tiempo(142)
    ~~~~~~~~~~~~^^^^^
  File "prueba_total.py", line 5, in sumar_tiempo
    total += tiempo_ms
    ^^^^^
UnboundLocalError: cannot access local variable 'total' where it is not associated with a value
```

Uma nota sobre esta saída: é a do Python 3.14. No Python 3.12 a linha da chamada (`sumar_tiempo(142)`) não traz as marcas `~~~~^^^^^` embaixo; todo o resto, e em particular a última linha, é idêntico. É um bom exemplo de por que a leitura começa por baixo.

A última linha diz: não se pode acessar a variável local `total` porque ela ainda não tem valor associado. As duas de cima dizem **onde**: dentro de `sumar_tiempo`, na linha 5, que é `total += tiempo_ms`; e essa função foi chamada da linha 8 do programa. Por que falha? Porque `total += tiempo_ms` é uma atribuição (equivale a `total = total + tiempo_ms`), e pela regra do ponto 3.3.2 isso torna `total` uma variável **local** de toda a função; mas, para somar, a função precisa ler o valor atual de `total`, e o `total` local ainda não tem nenhum. O `total = 0` de fora é outra variável, e a função nem a olha.

A correção é a que prescreve a regra de ouro das funções: que receba o que precisa e devolva o que calcula. Por exemplo, `def sumar_tiempo(total: int, tiempo_ms: int) -> int: return total + tiempo_ms`, e no programa, `total = sumar_tiempo(total, 142)`. [A documentação oficial tem uma entrada de perguntas frequentes para este caso exato](https://docs.python.org/pt-br/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value), e [a de `UnboundLocalError`](https://docs.python.org/pt-br/3/library/exceptions.html#UnboundLocalError) o define como o erro que ocorre quando se faz referência a uma variável local de uma função que ainda não tem valor.

### A lista que lembra das chamadas anteriores

Este não é um erro com mensagem, e por isso é pior: o programa não cai, **dá uma resposta errada sem avisar**. É uma das armadilhas mais famosas do Python. Salve este programa, que leva a conta dos serviços fora do ar, e execute:

<!-- frag: prueba_recuerda.py -->
```python
def registrar_caido(nombre: str, caidos: list[str] = []) -> list[str]:
    caidos.append(nombre)
    return caidos


print(registrar_caido("reportes"))
print(registrar_caido("facturacion"))
print(registrar_caido("notificaciones"))
```

```text
['reportes']
['reportes', 'facturacion']
['reportes', 'facturacion', 'notificaciones']
```

Cada chamada era independente: nenhuma passou uma lista para a função. Esperava-se ver `['reportes']`, `['facturacion']` e `['notificaciones']`. Em vez disso, a lista **acumula** o que veio das chamadas anteriores. É como se a função tivesse memória.

A explicação vem de quando se avalia um valor padrão: **uma única vez, quando o Python executa o `def`, não cada vez que a função é chamada**. O `[]` de `caidos: list[str] = []` é criado uma vez, ao definir a função, e fica guardado junto a ela; cada chamada que não passa a sua própria lista usa **essa mesma lista**, e o `.append` a muda no lugar (lembre: as listas são mutáveis). Assim, o que a primeira chamada colocou, a segunda encontra. [O tutorial oficial avisa disso com este mesmo exemplo](https://docs.python.org/pt-br/3/tutorial/controlflow.html#default-argument-values), e [as perguntas frequentes](https://docs.python.org/pt-br/3/faq/programming.html#why-are-default-values-shared-between-objects) explicam por que é assim.

A regra é: **nunca use uma lista (nem um dicionário, nem nenhum outro valor mutável) como valor padrão**. O padrão correto usa `None` como sinal de “não me passaram nada” e cria a lista dentro da função, onde é criada nova a cada chamada. Salve `fig03_16.py`:

```python
# fig03_16.py
def registrar_caido(nombre: str, caidos: list[str] | None = None) -> list[str]:
    if caidos is None:
        caidos = []
    caidos.append(nombre)
    return caidos


print(registrar_caido("reportes"))
print(registrar_caido("facturacion"))
historial = []
registrar_caido("reportes", historial)
registrar_caido("facturacion", historial)
print(historial)
```

```text
$ python fig03_16.py
['reportes']
['facturacion']
['reportes', 'facturacion']
```

Agora as duas primeiras chamadas são independentes, como se esperava. E quando **sim** se quer acumular, quem chama diz isso explicitamente: cria a sua própria lista (`historial`) e a passa para a função, que a usa em vez de criar uma. O parâmetro admite `list[str] | None`, que se lê “uma lista de textos, ou nada”. Esse padrão (`None` por padrão e criar dentro) você verá em código alheio muitíssimas vezes. E esse defeito é tão conhecido que as ferramentas de revisão o detectam sozinhas: o `ruff`, que você verá na Lição 8, tem uma regra específica para ele (a B006) e pode apontá-lo antes de você executar o programa.

### `ModuleNotFoundError` e `ImportError`

Os dois erros do ponto de módulos. Se o nome de um módulo está escrito errado, ou o arquivo não está na pasta de onde se executa, o Python não o encontra:

<!-- frag: prueba_import1.py -->
```python
from formatos import encabezado

print(encabezado())
```

```text
Traceback (most recent call last):
  File "prueba_import1.py", line 1, in <module>
    from formatos import encabezado
ModuleNotFoundError: No module named 'formatos'
```

E se o módulo existe, mas o nome que você pede não está nele, o erro é outro:

<!-- frag: prueba_import2.py -->
```python
from formato import lineas

print(lineas)
```

```text
Traceback (most recent call last):
  File "prueba_import2.py", line 1, in <module>
    from formato import lineas
ImportError: cannot import name 'lineas' from 'formato' (/home/tu_usuario/curso-python/revisor/formato.py). Did you mean: 'linea'?
```

As duas mensagens são literais. A primeira diz que não há nenhum módulo chamado `formatos` (no exemplo escreveu-se um `s` a mais). A segunda diz que `formato` existe sim, mas não tem nada chamado `lineas`; o Python mostra o arquivo onde procurou (o caminho será o da sua máquina) e até sugere o nome que parece que você queria: `linea`. Diante de um `ModuleNotFoundError`, confira três coisas por ordem: como você escreveu o nome, se o arquivo está na pasta, e se você está na pasta correta quando executa o programa.

## O que se faz errado

**Imprimir em vez de devolver.** `def total(...): print(...)` parece funcionar enquanto você só quer ver o resultado. Custo: quando precisa usar o resultado em outra conta, ou testá-lo, descobre que a função devolveu `None`. As funções que calculam, devolvem.

**Usar uma lista como valor padrão.** É o erro de cima. Custo: dados que se misturam entre chamadas sem nenhuma mensagem de erro, e que aparecem em produção como um relatório com serviços que não deveriam estar.

**Mudar uma variável global de dentro de uma função.** Com `global` é possível, e o programa vira um labirinto: para entender que valor tem uma variável é preciso ler todas as funções. Se uma função precisa de um dado, que o receba; se produz um, que o devolva.

**Comparar com `is` coisas que não são `None`.** Pode funcionar com números pequenos e falhar com os grandes, ou dar um `SyntaxWarning` como o de cima. Comparar valores é `==`.

**Um `while` sem avanço.** Se o bloco não aproxima a condição de ser falsa, o programa nunca termina. Antes de executar um `while`, localize a linha que o faz avançar.

**Escrever `range(len(NOMBRES))` e depois mexer só em uma lista.** É a fragilidade das listas paralelas: se você acrescenta um serviço a `NOMBRES` e esquece de acrescentar o código ou o tempo dele, o programa falha (com um `IndexError`) ou, pior, imprime dados que não são desse serviço. O Exercício 1 mostra isso em ação. Não há correção com o que você sabe hoje: a correção é guardar cada serviço como uma única coisa, e é o tema da Lição 4.

**Dar ao seu arquivo o nome de um módulo da biblioteca padrão.** Se você cria `statistics.py` na pasta do projeto e outro arquivo faz `import statistics`, o Python encontra **primeiro** o seu (lembre a ordem de busca: a pasta do programa vem antes da biblioteca padrão; só os módulos embutidos no interpretador, como `sys`, se salvam, porque são buscados antes de qualquer pasta) e os nomes do módulo real deixam de existir. O sintoma é um erro do tipo `AttributeError: module 'statistics' has no attribute 'mean'` (as versões recentes do Python acrescentam no final uma sugestão de renomear o arquivo), e desconcerta muito porque o seu próprio código não tem nenhum erro. Evite os nomes `statistics`, `random`, `json`, `string`, `types` e os demais da biblioteca padrão.

**Pôr `main()` sozinho no final de um módulo.** Quando outro arquivo o importar, o programa começará sozinho. A construção idiomática `if __name__ == "__main__":` existe para isso.

**Copiar e colar uma função em vez de importá-la.** Se o mesmo código está em dois arquivos, cedo ou tarde um dos dois é corrigido e o outro não. O que se compartilha, se importa.

## Exercícios

### Exercício 1 — Acrescentar um serviço e esquecer uma lista

Em `fig03_15/revisor.py`, acrescente `facturacion` (código 503, tempo 95 ms) às listas. Faça isso duas vezes. **Primeira vez:** acrescente `"facturacion"` a `NOMBRES` e `503` a `CODIGOS`, mas **esqueça** `TIEMPOS_MS`. Preveja o que vai acontecer antes de executar. **Segunda vez:** acrescente os três dados, mas em uma ordem diferente: `503` no **começo** de `CODIGOS` e `95` no final de `TIEMPOS_MS`. Preveja, e depois compare com o que você vê. Qual das duas falhas é mais perigosa e por quê?

### Exercício 2 — Contar os serviços fora do ar

Escreva uma função `contar_caidos(codigos: list[int | None]) -> int` que receba a lista de códigos e devolva quantos serviços estão fora do ar segundo a regra de sempre (sem código, ou com código de 400 ou mais). Teste-a com `CODIGOS` (deve dar 1), com `[200, 503, None]` (deve dar 2) e com uma lista vazia `[]` (deve dar 0). Deve **devolver** o número, não imprimi-lo.

### Exercício 3 — Provocar os erros da lição

Em cópias do seu projeto, provoque um por um: (a) usar um nome local de fora da sua função; (b) um `total += x` dentro de uma função; (c) a lista que lembra; (d) `from formato import lineas`; (e) tirar `formato.py` da pasta. Para cada um, copie a última linha da mensagem, escreva o que significa e qual é a correção.

### Exercício 4 — O serviço mais lento

Escreva uma função `mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None` que devolva o **nome** do serviço com o maior tempo, ignorando os que não responderam (os que têm `None`). Se nenhum respondeu, deve devolver `None`. Com `NOMBRES` e `TIEMPOS_MS` deve devolver `"inventario"`. Dica: percorra por posição, guarde em duas variáveis o melhor tempo visto até agora e o seu nome, e atualize-as quando encontrar um tempo maior. Pense com que valor essas variáveis devem começar.

## Soluções

### Solução 1

Primeira falha, com `TIEMPOS_MS` mais curta que as outras duas listas: o laço passa pelos quatro primeiros serviços sem problema e, ao chegar ao quinto, `TIEMPOS_MS[4]` não existe.

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
Traceback (most recent call last):
  File "revisor.py", line 36, in <module>
    main()
    ~~~~^^
  File "revisor.py", line 32, in main
    print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))
                                          ~~~~~~~~~~^^^
IndexError: list index out of range
```

(É a saída do Python 3.14; no 3.12 não aparece a linha de marcas `~~~~^^` embaixo de `main()`, e todo o resto, incluídas as marcas de `TIEMPOS_MS[i]` e a última linha, é idêntico.)

A última linha diz que o índice está fora do intervalo da lista: você pediu uma posição que não existe. É o erro que as listas paralelas produzem quando uma fica curta.

Segunda falha, com os dados em uma ordem diferente: o programa **não falha**, e imprime isto:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO      142ms  503
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    ARRIBA         —  200
facturacion CAIDO       95ms  sin conexión
```

Veja como ficou cada linha. `catalogo` aparece CAIDO com código 503, embora funcione. `reportes`, que não respondeu, aparece ARRIBA com código 200 (e sem tempo, porque o tempo dele sim era `None`). `facturacion` aparece com “sin conexión”, quando na realidade respondeu com um 503 em 95 ms. Os códigos ficaram deslocados uma posição em relação aos tempos, e nada avisa. Esta é a mais perigosa: a primeira falha se vê; a segunda produz um relatório que parece válido e mente. Essa é a razão pela qual na Lição 4 cada serviço deixará de ser três números soltos em três listas para ser **uma única coisa** que não pode se desalinhar.

### Solução 2

```python
def contar_caidos(codigos: list[int | None]) -> int:
    caidos = 0
    for codigo in codigos:
        if codigo is None or codigo >= 400:
            caidos += 1
    return caidos
```

Com `CODIGOS` dá `1`, com `[200, 503, None]` dá `2` e com `[]` dá `0`: o laço não dá nenhuma volta e devolve o valor com que o contador começou. O `return` vai **fora** do laço (na margem do `for`); se você o pusesse dentro, a função terminaria na primeira volta. E a condição é a mesma de `clasificar`: primeiro `is None`, para que `None >= 400` nunca seja avaliado.

### Solução 3

(a) `NameError: name 'limite' is not defined` (ou o nome que você usar): o nome é local e do lado de fora não existe. Correção: devolver o valor com `return` e guardá-lo em uma variável de fora.

(b) `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`: a atribuição torna `total` local. Correção: recebê-lo como parâmetro e devolver o novo.

(c) A lista que acumula entre chamadas, sem nenhuma mensagem. Correção: `None` por padrão e criar a lista dentro.

(d) `ImportError: cannot import name 'lineas' from 'formato' (...)`: o módulo existe, mas não tem esse nome. Correção: escrever `linea`.

(e) Sem `formato.py` na pasta: `ModuleNotFoundError: No module named 'formato'`. Correção: pôr o arquivo onde está `revisor.py`, ou executar o programa a partir da pasta que o contém.

### Solução 4

```python
def mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None:
    mejor_nombre = None
    mejor_tiempo_ms = None
    for i in range(len(nombres)):
        tiempo_ms = tiempos_ms[i]
        if tiempo_ms is None:
            continue
        if mejor_tiempo_ms is None or tiempo_ms > mejor_tiempo_ms:
            mejor_nombre = nombres[i]
            mejor_tiempo_ms = tiempo_ms
    return mejor_nombre
```

Com os dados do `revisor` devolve `"inventario"`; com `[None, None]` devolve `None`. A chave está no valor de partida: as duas variáveis começam em `None`, que significa “ainda não vi ninguém”, e por isso a pergunta `mejor_tiempo_ms is None or ...` vai primeiro: o primeiro serviço que respondeu sempre ganha, e a partir daí se compara. Se você tivesse começado `mejor_tiempo_ms` em 0 funcionaria com estes dados, mas daria uma resposta absurda com uma lista de tempos negativos, e seria preciso decidir que nome devolver quando ninguém respondeu. `None` expressa isso sem inventar nada.

## Como sei que consegui

- [ ] A partir de `fig03_15` (ou da sua pasta `revisor/`), `python revisor.py` imprime o cabeçalho e as quatro linhas da tabela, idênticos aos da figura, incluído o travessão e “sin conexión” na de `reportes`.
- [ ] `python fig03_11.py` (tudo em um arquivo) e `python revisor.py` (em dois arquivos) imprimem exatamente o mesmo.
- [ ] Ao mudar `UMBRAL_LENTO_MS` para 100 em `revisor.py`, `catalogo` passa a LENTO sem que você mexa em nenhuma outra linha.
- [ ] Depois de executar o programa existe uma pasta `__pycache__` junto a `formato.py`, e você sabe dizer por quê.
- [ ] Você consegue provocar `UnboundLocalError` e `ImportError` de propósito e dizer, olhando só a última linha, o que aconteceu.
- [ ] Você consegue explicar com as suas palavras a diferença entre `print` e `return`, entre `==` e `is`, e entre um parâmetro e um argumento.
- [ ] Você consegue explicar por que a função `registrar_caido` da seção de erros “lembrava” e por que a versão com `None` não.

## Resumo

Responda sem olhar a lição:

1. A partir de que número começam as posições de uma lista, e qual é a última posição de uma lista de `n` elementos?
2. O que produz `range(len(NOMBRES))` se `NOMBRES` tem quatro elementos? E o que entrega o `enumerate` a cada volta?
3. Que risco tem um `while` que um `for` não tem, e como você o evita?
4. Que diferença há entre definir uma função e chamá-la? O que é um parâmetro e o que é um argumento?
5. O que devolve uma função que não tem `return`? Por que uma função que calcula deve devolver e não imprimir?
6. Quando se avalia um valor padrão, e por que isso faz com que uma lista como valor padrão “lembre”? Qual é o padrão correto?
7. O que decide se um nome é local ou global dentro de uma função? Por que `total += x` falha em uma função?
8. Que pergunta faz `==` e que pergunta faz `is`? Com que valor se usa `is`?
9. Que valor tem `__name__` quando você executa um arquivo diretamente, e qual quando o importam? Para que serve isso?
10. Por que as três listas paralelas do `revisor` são uma má ideia, e por que são usadas hoje?

## Para ler mais

- [O tutorial do Python, “Mais ferramentas de controle de fluxo”](https://docs.python.org/pt-br/3/tutorial/controlflow.html) — `for`, `range`, `break` e `continue`, `def`, valores padrão e argumentos nomeados, em um só capítulo. Documentação oficial. Consultado em 7 de outubro de 2026.
- [O tutorial do Python, “Módulos”](https://docs.python.org/pt-br/3/tutorial/modules.html) — `import`, `from ... import`, a ordem de busca e `__pycache__`. Consultado em 7 de outubro de 2026.
- [Perguntas frequentes de programação em Python](https://docs.python.org/pt-br/3/faq/programming.html) — as armadilhas desta lição (o valor padrão mutável, `UnboundLocalError`, `is` contra `==`), com a explicação da própria equipe do Python. Consultado em 7 de outubro de 2026.
- [PEP 8, o guia de estilo do Python](https://peps.python.org/pep-0008/) — nomes, indentação e o uso de `is` com `None`; é o guia que este curso segue. Consultado em 7 de outubro de 2026.
