# Lição 0 — O que é Python e o que NÃO é

**Tempo:** 90 min

**O que você constrói:** nada ainda (leitura)

**O que você aprende:** o que o Python faz com o seu arquivo (interpretador e *bytecode*); tipagem dinâmica, mas forte; as anotações de tipo não são impostas na execução; o que é o GIL, explicado sem medo; o que é um ambiente virtual e por que o curso usa o Python 3.14 e também o 3.12

**De onde você vem.** De lugar nenhum, e tudo bem. Você não precisa ter o Python instalado, nem ter escrito uma linha de código, nem saber o que é um ambiente virtual. Esta lição é **de leitura**: você não instala nada e não constrói nada ainda. Os programas que aparecem têm uma ou duas linhas, e cada um traz a saída que produz, de modo que você pode acompanhá-los sem um computador à frente. Se você já tem o `python3` no seu Linux Mint e quer testá-los, vá em frente; se não, a [Lição 1](01-instalacion.md) deixa tudo pronto.

**O que esta lição não faz.** Não ensina a programar nem a instalar. Ensina **o que é a coisa que você vai aprender**, e sobretudo o que ela *não* é, porque a maioria dos problemas de quem está começando em Python não vem da sintaxe, e sim de uma expectativa errada: achar que o Python avisa de um erro de tipos antes de rodar (não avisa), que “interpretado” quer dizer “sem compilar nada” (não é tão simples) ou que o GIL impede fazer qualquer coisa em paralelo (impede menos do que se pensa). Acertar as expectativas desde o início poupa semanas de confusão.

## Ao terminar, você vai conseguir

- Explicar, em quatro passos, o que o Python faz com um arquivo `.py` desde que você o executa até o resultado aparecer, e dizer o que é o *bytecode* e para que serve a pasta `__pycache__`.
- Dizer por que o Python é **dinâmico, mas forte** e prever o que acontece com `"142" + 1` e com `"142" + "1"` sem executá-los.
- Explicar por que `tiempo_ms: int = "rápido"` roda sem reclamar, e quem pode, sim, avisar dessa contradição.
- Descrever o GIL com as suas palavras, dizer quando ele afeta e quando não, e por que o `revisor` não precisa se preocupar com ele.
- Explicar o que é um ambiente virtual e por que ele existe, e justificar por que o curso é ensinado com o Python 3.14, mas todo o código roda também no 3.12.
- Ler a última linha de um *traceback* de `TypeError` e dizer o que ela conta.

## O porquê antes do como

Daqui a onze lições você terá escrito um programa chamado **`revisor`**. Ele recebe uma lista de serviços (o catálogo de produtos de uma loja, o sistema de pagamentos, o estoque), pergunta a todos ao mesmo tempo se estão funcionando e entrega uma tabela como esta:

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Leia-a como leria alguém de plantão às onze da noite. `catalogo` e `pagos` responderam rápido. `inventario` respondeu, mas demorou 2.3 segundos, o que é demais: está **lento**. `reportes` não respondeu: está **fora do ar** (`CAIDO`), e o detalhe diz por quê (`sin conexión`, isto é, “sem conexão”). Essa tabela é o destino do curso. Nesta lição você não a constrói, mas ela serve de material: cada dado dela é de uma classe diferente (o nome é texto, 142 é um número, o traço `—` representa que **não há dado**), e entender essas classes é justamente o que vem a seguir.

Antes de escrever uma única linha, é preciso responder três perguntas que todo iniciante se faz, ainda que nem sempre em voz alta. A primeira: **o que exatamente é o Python e o que ele faz com o que eu escrevo?** A segunda: **o que vai me avisar dos meus erros e o que não vai?** A terceira: **por que vejo gente discutindo sobre “o GIL”, “o ambiente virtual” e “qual versão você usa”?** As três têm resposta curta. A primeira: o Python é um programa que lê o seu texto e o executa. A segunda: quase nada avisa antes de o programa rodar, então você vai aprender a ler os erros em vez de temê-los. A terceira: são três decisões práticas que convém entender uma vez.

Um **programa** é uma lista de instruções escritas em um arquivo de texto. Uma **linguagem de programação** é o conjunto de regras com que essas instruções são escritas para que fiquem claras tanto para você quanto para o computador. O problema é que o computador, por dentro, só entende instruções minúsculas e numéricas (somar duas quantidades, copiar um valor de um lugar para outro) que se chamam **código de máquina** e dependem do processador. Ninguém escreve à mão em código de máquina. Sempre há algo no meio que **traduz**, e a grande diferença entre uma linguagem e outra está em *quando* e *como* traduz. O Python faz a sua tradução de um modo particular, e esse modo explica quase tudo o mais desta lição.

Um aviso de vocabulário antes de seguir. A palavra “Python” nomeia duas coisas diferentes. Uma é a **linguagem**: as regras de como se escreve, descritas em uma especificação pública. A outra é o **programa que executa essa linguagem** no seu computador, e o que quase todo mundo usa se chama **CPython** (o “C” é porque ele está escrito na linguagem C). Quando você digita `python3` em um terminal, está chamando o CPython. Existem outros executores (o PyPy, por exemplo), mas este curso, como quase todo o trabalho profissional, usa o CPython. Quando uma expressão como “o GIL” aparecer mais abaixo, será uma característica do CPython, não da linguagem em abstrato.

## Os conceitos

São quatro: o que o interpretador faz com o seu arquivo, o que significa a tipagem ser dinâmica, mas forte (com as anotações de tipo como terceiro ponto), o que é o GIL e o que é um ambiente virtual junto com as versões. Eles são explicados nessa ordem, cada um com um exemplo mínimo.

### 0.1 O interpretador e o *bytecode*

#### 0.1.1 O que acontece quando você executa um arquivo

Imagine que você salva isto em um arquivo chamado `lectura.py`:

```text
tiempo_ms = 142
print(tiempo_ms)
```

(Duas palavras de leitura adiantadas. `tiempo_ms = 142` quer dizer “guarde o número 142 sob o nome `tiempo_ms`”; o nome leva `_ms` porque é o tempo em milissegundos, e neste curso as unidades sempre vão no nome. `print(...)` quer dizer “mostre na tela o que vai entre parênteses”. A [Lição 2](02-valores-texto-decisiones.md) explica as duas a fundo.)

Para executá-lo, você digita em um terminal `python3 lectura.py`. O que acontece então tem quatro passos, e vale a pena conhecê-los porque cada um explica um comportamento que de outro modo parece mágica.

1. **O Python lê o texto.** Abre o arquivo e o percorre de cima a baixo, verificando se está bem escrito segundo as regras da linguagem. Se faltar fechar um parêntese, é aqui que isso se descobre, e o programa **não começa a rodar**: nem uma única linha anterior é executada. Você pode comprovar com um arquivo cuja primeira linha é `print("primera")` e cuja segunda tem um parêntese sem fechar: não aparece “primera”, só o erro `SyntaxError: '(' was never closed`. Ou seja, a verificação da forma acontece antes da execução.
2. **O Python traduz o texto para uma lista de instruções próprias.** Não para código de máquina, mas para um formato intermediário, mais simples que o seu texto e mais abstrato que o processador. Essa lista se chama ***bytecode***. A [documentação oficial](https://docs.python.org/pt-br/3/glossary.html#term-bytecode) o define como “a representação interna de um programa em Python no interpretador CPython”.
3. **Uma máquina virtual executa o *bytecode*.** “Virtual” significa que não é um aparelho físico, e sim um programa que se comporta como se fosse: pega cada instrução do *bytecode*, uma de cada vez, e faz o que ela diz. Essa máquina virtual é o coração do CPython, e é o que chamamos de **interpretador**.
4. **O resultado aparece**, neste caso o número `142` na sua tela.

Tudo isso acontece em uma fração de segundo cada vez que você executa o arquivo, sem que você precise pedir. Por isso se diz que o Python é uma linguagem **interpretada**: você executa o arquivo de texto diretamente, sem uma etapa prévia em que você mesmo gere um programa executável. A [documentação explica](https://docs.python.org/pt-br/3/glossary.html#term-interpreted) quase com essas palavras (“os arquivos-fontes podem ser executados diretamente sem necessidade explícita de se criar um arquivo executável”), e acrescenta logo em seguida uma ressalva honesta: a distinção entre interpretado e compilado pode ser “nebulosa devido à presença do compilador de *bytecode*”. É a ressalva que importa. O Python **sim** compila (o passo 2 é uma compilação), só que compila para um formato intermediário e faz isso por você, em silêncio, a cada vez.

O contraste com outras linguagens ajuda. Em Go ou em Rust você escreve o seu código, executa um compilador que produz um arquivo executável (código de máquina direto para o seu processador) e depois executa esse arquivo. O executável já não precisa do compilador nem da linguagem: você o copia para outro computador e ele roda. Em Python não existe esse arquivo final: o computador onde você quiser rodar o seu programa precisa **ter o Python instalado**, porque é o Python quem lê e executa o seu texto a cada vez. Essa é uma consequência prática que você verá a partir da Lição 1, e é o motivo de metade do que se aprende “em volta” do Python (versões, ambientes, instalação) ter a ver com esse fato.

#### 0.1.2 O que o Python guarda: `__pycache__` e os arquivos `.pyc`

Compilar para *bytecode* custa um pouco de tempo, e se o arquivo não mudou desde a última vez, repetir essa tradução é trabalho perdido. Por isso o Python guarda o resultado. A [documentação do glossário](https://docs.python.org/pt-br/3/glossary.html#term-bytecode) diz que o *bytecode* “também é mantido em cache em arquivos `.pyc` [...], de forma que executar um mesmo arquivo é mais rápido na segunda vez”. Esses arquivos vivem em uma pasta chamada `__pycache__`, junto ao seu código.

Há um detalhe que surpreende e que convém medir em vez de supor. Se você executa diretamente `python3 lectura.py`, **não** aparece nenhuma pasta `__pycache__`: o Python compila o arquivo que você deu para a memória, o executa e não guarda nada. A pasta aparece quando um arquivo é **importado** a partir de outro, isto é, quando um programa usa o conteúdo de outro arquivo (o `import` é explicado na [Lição 3](03-bucles-funciones-modulos.md)). Foi medido assim: executou-se um arquivo diretamente e contaram-se zero arquivos `.pyc`; executou-se outro que importava o primeiro e apareceu um. Se você quiser forçar a criação sem importar nada, existe `python3 -m py_compile lectura.py`. Um trecho, com as versões 3.12 e 3.14 da mesma máquina, deixa ver o nome que é gerado:

```text
$ python3.12 -m py_compile lectura.py
$ python3.14 -m py_compile lectura.py
$ ls __pycache__
lectura.cpython-312.pyc
lectura.cpython-314.pyc
```

Repare no nome: `lectura.cpython-312.pyc`. Ele diz qual era o arquivo (`lectura`), qual executor o gerou (`cpython`) e com qual versão (`312` é a 3.12). O *bytecode* de uma versão **não serve** em outra, e a [documentação avisa](https://docs.python.org/pt-br/3/glossary.html#term-bytecode): “não se espera que *bytecodes* sejam executados entre máquinas virtuais Python diferentes, nem que se mantenham estáveis entre versões de Python”. Por isso o Python guarda um arquivo diferente por versão e não mistura os de uma com os de outra.

Três consequências práticas:

- **É seguro apagar o `__pycache__`.** O Python o recria quando precisar. Ele não faz parte do seu programa, é um cache.
- **Ele não é guardado no repositório do projeto.** Um repositório é o lugar onde uma equipe guarda e compartilha o código de um programa, com o seu histórico de mudanças. Ali só vai o que você escreve; o `__pycache__` é um derivado do seu código e muda a cada versão do Python, então fica de fora.
- **Não é uma proteção.** Algumas pessoas acreditam que enviar só os `.pyc` esconde o código delas. Não é assim: os `.pyc` podem ser lidos de novo com ferramentas, e isso não é uma medida de segurança.

#### 0.1.3 Ver o *bytecode* (só por curiosidade)

O Python traz uma ferramenta, o módulo `dis`, que mostra o *bytecode* de um arquivo de forma legível. Você não precisa aprendê-lo, mas vê-lo uma vez tira o mistério. Este é o resultado no Python 3.12 para as duas linhas de `lectura.py`:

```text
$ python3.12 -m dis lectura.py
  0           0 RESUME                   0

  1           2 LOAD_CONST               0 (142)
              4 STORE_NAME               0 (tiempo_ms)

  2           6 PUSH_NULL
              8 LOAD_NAME                1 (print)
             10 LOAD_NAME                0 (tiempo_ms)
             12 CALL                     1
             20 POP_TOP
             22 RETURN_CONST             1 (None)
```

A coluna do meio são as instruções. `LOAD_CONST 142` significa “ponha o valor constante 142 à mão”, `STORE_NAME tiempo_ms` significa “guarde-o sob o nome `tiempo_ms`”, e as da linha 2 pedem o nome `print`, pedem o nome `tiempo_ms` e chamam a primeira com a segunda. Cada linha do seu texto vira duas, três ou quatro destas. E aqui está a razão de este bloco ser um **trecho** e não um programa do curso: *o bytecode muda entre versões*. Ao medi-lo no Python 3.14, a primeira instrução da linha 1 já não se chama `LOAD_CONST 142`, e sim `LOAD_SMALL_INT 142`, e a ordem de duas instruções da linha 2 é outra. O comportamento do programa é o mesmo; o idioma interno que a máquina virtual usa para descrevê-lo, não. O que você deve levar disto não é nenhuma dessas palavras, e sim a ideia: entre o seu texto e o resultado há uma lista de instruções intermediária que você não escreve e que o Python esconde de você.

#### 0.1.4 Por que isso importa para o `revisor`

Duas coisas. A primeira: o Python demora mais que um programa compilado para código de máquina para executar cálculos puros, porque cada instrução do *bytecode* passa pela máquina virtual. Em um programa que multiplica milhões de números isso se nota. Mas o `revisor` quase não calcula: **passa o tempo esperando** que uma rede responda. Enquanto espera 2.3 segundos pela resposta de `inventario`, a velocidade do Python é irrelevante. O que importará será esperar por todos os serviços ao mesmo tempo em vez de um depois do outro, e isso é um tema das lições 9 e 10. A segunda: como o Python precisa estar instalado onde o seu programa é executado, e como cada versão tem o seu próprio *bytecode* e o seu próprio comportamento, saber **qual Python você está usando** é uma pergunta que você fará com frequência. A resposta está no último ponto desta lição.

### 0.2 Tipagem dinâmica, mas forte

#### 0.2.1 O que é um tipo

Um **valor** é um dado concreto: o número `142`, o texto `"catalogo"`. O **tipo** de um valor é a classe de coisa que ele é: um número inteiro, um texto, um traço que significa “não há dado”. Um **nome** (ou variável) é um rótulo que você aponta para um valor, como `tiempo_ms` no exemplo anterior. Olhe a tabela do `revisor`: `catalogo` é um texto, `142` é um número, `—` é a ausência de dado. O tipo importa porque determina **o que se pode fazer** com o valor: os números se somam, os textos se colam um no outro. E a pergunta que distingue as linguagens é *quando e quem verifica* se o que você tenta fazer faz sentido para esse tipo.

#### 0.2.2 Dinâmico: o tipo vive no valor, não no nome

Em Python, **o tipo pertence ao valor, não ao nome**. Um nome pode apontar hoje para um número e amanhã para um texto, e ao Python tanto faz. A verificação de se uma operação faz sentido acontece **enquanto o programa roda**, justamente no momento de executar essa linha: é isso que significa **dinâmico**. Isso contrasta com as linguagens de tipagem estática (Go, Rust, Java), em que cada nome é declarado com o seu tipo e o compilador verifica tudo antes de executar.

Olhe a primeira figura. É uma única linha e é preciso lê-la peça por peça.

```python
# fig00_01.py
print(142 + 1, "142" + "1")
```

```text
$ python3 fig00_01.py
143 1421
```

A primeira linha é um **comentário**: tudo o que vem depois de um `#` é uma nota para humanos que o Python ignora. Aqui ela leva o nome da figura, para que você saiba que arquivo é. A segunda é a que executa. `print(a, b)` mostra os dois valores separados por um espaço, e por isso a saída traz duas coisas: `143` e `1421`. O interessante é que **ambas usam o mesmo sinal `+`** e dão resultados de natureza diferente.

- `142 + 1`: os dois são números (não levam aspas), e o `+` os **soma**: 143.
- `"142" + "1"`: o que vai entre aspas é **texto**, embora pareça um número. Um texto se escreve entre aspas, duplas ou simples. Aqui o `+` não soma: **cola** um texto no outro, e o resultado é o texto `1421`, que é mostrado sem as aspas.

O sinal é o mesmo, mas o que ele faz depende do tipo dos valores. É a primeira lição sobre tipos: `"142"` e `142` **parecem quase iguais e são coisas diferentes**. No `revisor`, o `142` da tabela é um número que pode ser comparado com 1000 para decidir se um serviço está lento; se por engano chegasse como o texto `"142"`, essa comparação não faria sentido.

Outra forma de ver o que é dinâmico é o mesmo nome mudar de tipo. Este trecho é válido em Python:

```text
lectura = 142
lectura = "rápido"
```

O nome `lectura` apontou primeiro para um número e depois para um texto. O Python não protesta, porque não há nenhum lugar onde você tenha dito “`lectura` é um número” e a regra se mantenha. Essa liberdade é cômoda para escrever rápido e perigosa para escrever com descuido, e por isso este curso, embora o Python não exija, vai ensinar você a ser organizado: um nome, uma classe de dado.

#### 0.2.3 Forte: o Python não adivinha o que você quis dizer

O Python ser dinâmico **não** quer dizer que seja permissivo. Ele é dinâmico **e forte**: quando você tenta uma operação que não faz sentido para aqueles tipos, o Python **não inventa uma conversão**; ele para e diz que há um erro. Vejamos a segunda figura, uma única linha que mistura um texto com um número.

```python
# fig00_02.py
print("142" + 1)
```

```text
$ python3 fig00_02.py
Traceback (most recent call last):
  File "fig00_02.py", line 2, in <module>
    print("142" + 1)
          ~~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

O programa **não imprimiu nada**: parou e mostrou um relatório de erro, que em Python se chama ***traceback*** (algo como “o rastro para trás”). Por ora, repare apenas na última linha: `TypeError: can only concatenate str (not "int") to str`. “`TypeError`” é a classe do erro (um problema de tipos); o que vem depois é a explicação em inglês. Traduzida: “só é possível concatenar (colar) um `str` (texto) com outro `str`, não com um `int` (número inteiro)”. O Python está dizendo que você tentou colar um texto com um número e que não sabe o que fazer. A seção “O erro que você vai ver” lê o resto do relatório linha por linha. (Na sua tela o caminho do arquivo será longo e completo; aqui ele é encurtado para o nome, para que se leia bem.)

Aqui está o **forte**. Outras linguagens, diante de `"142" + 1`, resolvem por conta própria: o JavaScript, por exemplo, converte o número em texto e devolve `"1421"` sem avisar. Isso pode parecer amável e é uma fonte clássica de erros, porque o programa segue rodando com um dado que ninguém esperava. O Python prefere a reclamação imediata à conversão silenciosa. Essa decisão joga a seu favor: o erro aparece **onde ocorre**, com o nome do problema e a linha exata, e não três funções adiante como um resultado estranho.

Junte as duas metades e você tem o comportamento completo. **Dinâmico**: a verificação de tipos acontece ao executar cada linha, não antes. **Forte**: quando essa verificação falha, o Python para em vez de adivinhar. Daí sai uma consequência que você deve ter presente: **um erro de tipos só aparece se essa linha chegar a ser executada**. Se o seu programa tem um ramo usado uma vez por mês, um erro de tipos escondido ali só será descoberto nesse dia. É um argumento a favor dos testes (lição 8) e das ferramentas que verificam o código sem executá-lo.

#### 0.2.4 As anotações de tipo: uma promessa que o Python não vigia

O Python permite *escrever* o tipo que você espera junto a um nome, e faz isso com uma sintaxe chamada **anotação**: `nome: tipo = valor`. A [documentação as chama de “dicas de tipo”](https://docs.python.org/pt-br/3/glossary.html#term-type-hint) (*type hints*) e diz duas coisas importantes: que são **opcionais** e que “não são forçadas pelo Python” (em inglês, *are not enforced*). Vejamos o que isso significa com a terceira figura:

```python
# fig00_03.py
tiempo_ms: int = "rápido"
print(tiempo_ms)
```

```text
$ python3 fig00_03.py
rápido
```

Leia com calma, porque ela contém uma contradição deliberada. A linha 2 diz: “o nome `tiempo_ms` é do tipo `int`” (`int` é a abreviatura de *integer*, inteiro, o tipo dos números sem decimais), e em seguida atribui a ele `"rápido"`, que é um texto. Uma linguagem de tipagem estática rejeitaria o programa. O Python **o executa sem reclamar** e mostra `rápido`. A anotação ficou escrita, mas ninguém a comparou com o valor.

Esta é a parte da lição que mais convém lembrar: **as anotações de tipo não são impostas na execução**. A especificação que as criou, a [PEP 484](https://peps.python.org/pep-0484/), diz isso sem rodeios (tradução nossa; a PEP só existe em inglês): *o Python continua sendo uma linguagem de tipagem dinâmica, e os autores não têm nenhuma intenção de tornar os tipos obrigatórios, nem mesmo por convenção*. Então, para que se escrevem?

- **Para que as pessoas as **leiam**.** Uma anotação documenta que classe de dado se espera em cada lugar e, ao contrário de um comentário, tem um formato que não apodrece facilmente.
- **Para que o editor as **use**.** Muitos editores mostram sugestões e avisam de contradições enquanto você escreve.
- **Para que uma ferramenta à parte as **verifique**.** Existem programas chamados verificadores de tipos (o mais conhecido é o `mypy`) que leem o seu código **sem executá-lo** e relatam que `tiempo_ms: int = "rápido"` é uma contradição. Eles são ensinados na [Lição 8](08-pruebas-tipos-calidad.md). A [documentação do `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) explica que a verificação dele é **gradual**: verifica as partes anotadas e deixa passar as que não estão.
- **Para que outras peças da linguagem as aproveitem.** Na [Lição 5](05-modelo-de-datos.md) você usará `dataclass`, uma ferramenta que lê as anotações para construir coisas; ali elas cumprem uma função real, embora continuem sem validar valores.

Dito de outro modo, em Python **há dois verificadores diferentes**: o interpretador (verifica ao executar, de maneira forte, mas tarde) e o verificador de tipos (verifica antes de executar, mas só se você o rodar e só o que você anotou). O interpretador nunca consulta as anotações para decidir se algo é válido. Se você vem do curso de [TypeScript](https://www.habil.mx/pt/cursos/typescript/) desta casa, o princípio é o mesmo de lá: os tipos escritos são uma promessa que uma ferramenta pode conferir, não uma barreira que o programa levanta ao rodar.

E há um limite que nenhuma anotação cruza: **os dados que vêm de fora**. Se o seu programa lê um arquivo de configuração e nele alguém escreve `"timeout_ms": "rápido"`, não importa o que você tenha anotado no seu código: o texto chegará tal qual. Esses dados precisam ser **validados** na entrada, com código que os compare de verdade, e isso se faz na [Lição 6](06-errores-archivos-datos.md). A anotação é uma promessa entre as partes do seu programa; a validação é o que protege do que o programa não controla.

Um último dado de atualidade, sem consequências para você: no Python 3.14 mudou *quando* as anotações são avaliadas (deixam de ser avaliadas no momento em que são definidas), segundo a [lista de novidades da versão](https://docs.python.org/pt-br/3/whatsnew/3.14.html). Para escrever código que rode igual no 3.12 e no 3.14, este curso evita depender dessa mudança, e avisa quando for preciso.

### 0.3 O GIL, explicado sem medo

Mais cedo ou mais tarde alguém vai lhe dizer “o Python não consegue fazer coisas em paralelo por causa do GIL”. A frase assusta e simplifica demais. Vamos por partes.

Primeiro, duas palavras. Uma **thread** (em português, “linha de execução”) é uma sequência de execução dentro de um programa: um programa pode ter várias, e em princípio cada uma pode avançar enquanto as outras esperam. E um **processador** moderno tem vários núcleos, que podem executar instruções no mesmo instante. Aproveitar vários núcleos com várias threads é o que se chama **paralelismo**.

O **GIL** (*Global Interpreter Lock*, “trava global do interpretador”) é uma regra do CPython. A [documentação o define](https://docs.python.org/pt-br/3/glossary.html#term-global-interpreter-lock) assim: é o mecanismo que garante que **apenas uma thread execute *bytecode* de Python por vez**. Ele existe porque simplifica o projeto do interpretador: as estruturas internas, como os dicionários, ficam protegidas de que duas threads as modifiquem ao mesmo tempo. O preço, diz a mesma definição, é que se perde boa parte do paralelismo das máquinas com vários processadores.

Traduzido para a prática, o GIL afeta de forma diferente duas classes de trabalho:

- **Trabalho de cálculo** (converter mil imagens, comprimir um arquivo grande): com threads de Python, ele não é repartido entre os núcleos; uma única thread calcula por vez. Aqui o GIL atrapalha.
- **Trabalho de espera** (perguntar a uma rede, ler um arquivo, esperar a resposta de um banco de dados): a thread que espera solta a trava enquanto não está executando Python, e outra pode avançar. Aqui o GIL quase não atrapalha. A [documentação do módulo `threading`](https://docs.python.org/pt-br/3/library/threading.html) diz assim: as threads continuam sendo um bom modelo quando se quer executar várias tarefas de **entrada/saída** ao mesmo tempo.

O `revisor` é do segundo tipo, **quase por completo**. O trabalho dele é esperar respostas da rede, não calcular. E, além disso, não usará threads: resolverá “perguntar a todos ao mesmo tempo” com o **`asyncio`**, que roda em uma única thread e alterna entre tarefas cada vez que uma delas começa a esperar. Nesse esquema o GIL nem entra na conversa. Você pode se esquecer dele enquanto usa este curso, mas não do dado: saber que ele existe permite que você não acredite na frase exagerada, nem a repita.

E se algum dia você quisesse cálculo em paralelo? Hoje existem dois caminhos que este curso não percorre: usar vários **processos** (cada um com o seu próprio interpretador e o seu próprio GIL) e, há pouco tempo, uma variante do CPython **sem GIL**. A história dessa variante, resumida: a [PEP 703](https://peps.python.org/pep-0703/) propôs tornar o GIL opcional e apareceu como experimento no 3.13; a [PEP 779](https://peps.python.org/pep-0779/) a declarou oficialmente **suportada** a partir do 3.14, mas **não é a opção padrão**: é um executável à parte, com um custo em velocidade quando se usa uma única thread, e muitas bibliotecas ainda estão se adaptando. É o que neste curso se chama de “o que vem por aí”: é mencionado, não é usado e não é recomendado para produção logo de saída.

### 0.4 O ambiente virtual e as versões

#### 0.4.1 O problema que um ambiente virtual resolve

Pense na sua cozinha. Você tem uma despensa da casa, onde vivem as coisas que toda a família usa: sal, óleo, arroz. Se você, para um experimento, começa a guardar ali potes estranhos, a trocar o arroz por outro tipo ou a tirar o óleo, atrapalha os demais e um dia alguém não conseguirá cozinhar. O sensato é ter a sua **prateleira própria** para os seus experimentos.

O Python que vem no seu Linux Mint é a despensa da casa. O sistema operacional o usa para as suas próprias ferramentas e depende de que as bibliotecas dele estejam em uma versão determinada. Se você instala ali pacotes seus, ou troca algum, corre o risco de quebrar algo do sistema. E há um segundo problema, independente do primeiro: **dois projetos seus podem precisar de versões diferentes da mesma biblioteca**. Se todos os pacotes vivem em um único lugar, um dos dois projetos perde.

A solução se chama **ambiente virtual** (*virtual environment*, *venv*): uma pasta com o seu próprio Python (no Linux, um atalho para o Python com o qual foi criada, não uma cópia; a Lição 1 mostra isso) e o seu próprio espaço para pacotes, isolada do resto. A [documentação oficial](https://docs.python.org/pt-br/3/glossary.html#term-virtual-environment) o define como um ambiente de execução isolado (“cooperativamente isolado”, precisa o original em inglês) que permite instalar e atualizar pacotes “sem interferir no comportamento de outras aplicações Python” do mesmo sistema. O que você instala dentro de um ambiente vive só ali; se algo der errado, você apaga a pasta do ambiente e o recria, e o sistema nem fica sabendo.

As distribuições de Linux levaram isso a sério. Desde que existe a especificação [PEP 668](https://peps.python.org/pep-0668/), uma distribuição pode marcar o seu Python como **“gerenciado externamente”**: significa que esse Python pertence ao gerenciador de pacotes do sistema e que o `pip` (a ferramenta do Python para instalar pacotes) deve se recusar a instalar qualquer coisa nele fora de um ambiente virtual. No seu Linux Mint a proteção é ainda mais direta: o Python dele nem sequer traz o `pip`. Você verá a recusa com os seus próprios olhos, e aprenderá a ler as duas formas que ela toma, na Lição 1. Por ora basta saber que **não é uma falha da sua instalação**: é uma proteção, e a saída correta é o ambiente virtual.

#### 0.4.2 As versões, e por que duas

As versões do Python têm três números: `3.14.8` se lê maior, menor e patch. O primeiro (3) está há anos sem mudar. O segundo (14) muda **uma vez por ano, em outubro**, e traz novidades. O terceiro (8) são correções de erros que não mudam o que a linguagem permite. Quando se diz “Python 3.12”, fala-se de uma linha de versões, e o patch pode ser qualquer um.

Há três fatos que sustentam as decisões do curso, todos medidos na data em que esta lição foi escrita (7 de outubro de 2026):

- **A versão estável vigente é a 3.14.** Foi lançada em 7 de outubro de 2025, e a [página oficial de downloads](https://www.python.org/downloads/) mostrava como a mais recente a 3.14.8, de 30 de setembro de 2026. A 3.15 estava programada para outubro deste ano segundo o [guia de desenvolvedores](https://devguide.python.org/versions/) e aparecia ainda em estado de pré-lançamento.
- **O Linux Mint 22.x traz o Python 3.12.** O Mint 22 e as suas atualizações (22.1, 22.2, 22.3) são construídos sobre a base do Ubuntu 24.04, com [suporte até abril de 2029](https://linuxmint.com/download_all.php), e essa base é a que decide o Python que vem instalado: a linha 3.12.
- **A 3.12 continua recebendo correções de segurança até outubro de 2028**, segundo o mesmo guia de desenvolvedores. Já a 3.10 chegou ao fim da vida em 1º de outubro de 2026: quem continua nela não recebe mais nem correções de segurança.

Daí a decisão: **o curso é ensinado com o Python 3.14 e todo o seu código roda também no 3.12**, o que vem no seu Mint. Cada programa das lições é executado com as duas versões e o seu resultado é comparado com o que você vê no texto. Isso tem um custo, que é não usar um punhado de novidades que só existem na 3.14, e uma vantagem decisiva: **você não precisa instalar nada especial** para seguir o curso, nem deixar de usar o Python do seu sistema. Se algum dia você quiser experimentar a 3.14, a Lição 7 conta uma forma cômoda de instalá-la.

Por isso, quando aparecer o comando `python3`, o que roda no seu Mint é a 3.12, e isso está correto. Um último aviso que vai lhe poupar uma tarde: em muitos sistemas o comando `python` (sem o 3) não existe, ou aponta para outra coisa. Ao terminar de ler esta lição você sabe a regra do curso: **fora de um ambiente virtual escreve-se `python3`; dentro do ambiente, `python` aponta para o Python do ambiente** (a Lição 1 confere isso com `which`).

## O erro que você vai ver

O único erro desta lição é o da figura 2, e convém lê-lo inteiro porque todos os relatórios de erro do Python têm a mesma forma. Aqui está ele de novo, com o nome de cada linha; não precisa executá-lo outra vez.

A primeira linha do relatório é `Traceback (most recent call last):`, que se traduz “rastro, a chamada mais recente por último”. É um sinal de que o que vem a seguir é uma lista de lugares, ordenada **do mais antigo ao mais recente**, e de que o que aconteceu está **no final**. Por isso a regra de ouro para ler um relatório de erro em Python é **começar pela última linha e subir**.

A última linha é `TypeError: can only concatenate str (not "int") to str`. Ela contém a **classe** do erro (`TypeError`) e a sua **mensagem**. `TypeError` quer dizer que uma operação recebeu um valor de um tipo que ela não admite. A mensagem diz exatamente qual: quis-se colar (`concatenate`) um `str` com algo que não era `str`, e sim um `int`. Só com isso você já sabe o que aconteceu e por quê.

Subindo uma linha você encontra o desenho do erro: `print("142" + 1)` na linha de código, e embaixo uma marca de til e acento circunflexo (`~~~~~~^~~`). Essa marca aponta **qual parte exata** da linha falhou: o `+` que une `"142"` com `1`. É uma ajuda que as versões recentes acrescentam, e poupa você de adivinhar em uma linha longa.

Suba mais uma linha: `File "fig00_02.py", line 2, in <module>`. Ela diz **em que arquivo**, **em que número de linha** e **dentro de quê**. A palavra `<module>` significa “no nível do arquivo, não dentro de uma função”; quando você conhecer as funções (Lição 3), aqui verá o nome da função em vez de `<module>`. A linha é a 2 porque a 1 é o comentário com o nome da figura.

A correção não é converter qualquer coisa em texto para o erro se calar. Primeiro decida o que você queria. Se queria somar, os dois devem ser números (`142 + 1` dá 143). Se queria montar uma mensagem de texto, os dois devem ser texto (`"142" + "1"`), e então o resultado é colado, não somado. O erro obrigou você a decidir o que cada dado representava. É isso que faz uma boa mensagem de erro.

## O que se faz errado

- **Acreditar que uma anotação valida o dado.** Escrever `tiempo_ms: int` não impede que `tiempo_ms` valha `"rápido"`. Se você precisa da garantia, é preciso um verificador de tipos (enquanto escreve) ou uma validação explícita (quando o dado vem de fora). A anotação sozinha não faz nenhuma das duas.
- **Corrigir um `TypeError` convertendo tudo em texto.** Pôr aspas ou chamar uma função de conversão até o erro desaparecer esconde que você misturou duas ideias. Pergunte primeiro o que cada valor deveria ser.
- **Dizer “o Python é interpretado, então não compila”.** Ele compila sim (para *bytecode*); faz isso por você e a cada execução. Dizer “sem compilar” leva a surpresas, como não entender o que é um `__pycache__` nem por que os erros de sintaxe aparecem antes da primeira linha.
- **Culpar o GIL por qualquer lentidão.** Um programa que espera por uma rede não é lento por causa do GIL: é lento porque espera, e isso se resolve esperando por todos ao mesmo tempo. Antes de culpar o GIL, meça o que o seu programa está fazendo enquanto demora.
- **Guardar o `__pycache__` no repositório, ou achar que é preciso protegê-lo.** É um cache do Python, derivado do seu código, diferente em cada versão. Fica de fora.
- **Instalar pacotes com `sudo pip` no Python do sistema.** É o atalho que deve ser recusado e o que leva a quebrar ferramentas do sistema. Cada pacote dos seus projetos vive em um ambiente virtual (Lição 1). Embora o `pip` ofereça uma opção para contornar a proteção da PEP 668, o curso **não** a ensina nem a usa.
- **Misturar `python` e `python3` sem saber qual é qual.** Diante de qualquer dúvida de “qual Python estou usando?”, a pergunta correta é `which`, e ela é respondida na próxima lição.

## Exercícios

### Exercício 1 — Os dados da tabela

Olhe a tabela do `revisor` do início. Para cada uma destas quatro células, diga se o dado é um **número**, um **texto** ou **nada** (ausência de dado): o `142` de `catalogo`, o `catalogo` da primeira coluna, o `—` do tempo de `reportes` e o `200` do detalhe de `pagos`. Depois responda: por que seria um problema o tempo de `inventario` chegar ao programa como o texto `"2300"` em vez do número 2300?

### Exercício 2 — Preveja antes de executar

Sem executar nada, escreva o que faz cada uma destas três linhas: a que mostra um resultado, a que mostra outro resultado diferente e a que falha. Para a que falha, escreva a **última linha** do relatório de erro.

```text
print(142 + 1)
print("142" + "1")
print(142 + "1")
```

### Exercício 3 — A promessa que ninguém vigia

Com a figura 3 diante de você (`tiempo_ms: int = "rápido"`), responda com as suas palavras: (a) por que o programa mostra `rápido` e não um erro? (b) Se você instalasse um verificador de tipos e o rodasse sobre esse arquivo, o que esperaria que ele dissesse? (c) Se o valor `"rápido"` chegasse de um arquivo de configuração e não de uma linha escrita por você, a anotação serviria de alguma coisa?

### Exercício 4 — Explique para um colega

Um colega de trabalho diz a você: “O Python é lento porque é interpretado e não consegue fazer nada em paralelo por causa do GIL, então para consultar muitos serviços é preciso usar outra linguagem”. Escreva a sua resposta em quatro ou cinco frases, corrigindo com precisão o que está incompleto ou exagerado e dizendo o que o `revisor` realmente faz durante quase todo o seu tempo.

## Soluções

### Solução 1

O `142` é um **número**; `catalogo` é um **texto**; o `—` representa que **não há dado** (o serviço não respondeu, então não há um tempo para medir); o `200` do detalhe é o código com que o serviço respondeu e, na tabela, é mostrado como texto, porque nessa coluna também podem aparecer coisas como `sin conexión` (essa coluna mistura as duas classes, e por isso o programa a tratará sempre como texto). O tempo de `inventario` chegar como o texto `"2300"` seria um problema porque o `revisor` o compara com o limiar de 1000 para decidir se o serviço está lento. Um texto não se compara de forma significativa com um número: o Python, por ser forte, pararia com um `TypeError` em vez de dar um veredito errado.

### Solução 2

A primeira linha soma dois números e mostra `143`. A segunda cola dois textos e mostra `1421`. A terceira falha, porque mistura um número com um texto; a última linha do relatório é `TypeError: unsupported operand type(s) for +: 'int' and 'str'`. A mensagem é diferente da da figura 2 porque aqui o número está à esquerda: o Python tenta primeiro somar e, como não consegue, diz que o operador `+` não admite um `int` com um `str`. O importante é a classe (`TypeError`) e entender que a causa é a mesma: dois tipos foram misturados.

### Solução 3

(a) Porque as anotações não são impostas na execução: o Python registrou a anotação `int`, mas nunca a comparou com o valor atribuído. (b) Que há uma contradição: declarou-se um `int` e atribuiu-se a ele um texto. O verificador lê o código sem executá-lo e compara as anotações com os valores. (c) Não: uma anotação é uma promessa entre partes do *seu* código. Um valor que chega de fora entra tal como vem, seja qual for o seu conteúdo, e só uma validação explícita na entrada (Lição 6) pode conferir que ele realmente é um número.

### Solução 4

Uma resposta possível: “É verdade que o Python executa mais devagar os cálculos puros, mas um programa que consulta serviços quase não calcula: passa o tempo esperando respostas da rede. O GIL impede que duas threads executem *bytecode* de Python ao mesmo tempo, mas uma thread que espera solta a trava, e de qualquer modo o `revisor` não usa threads e sim `asyncio`, que alterna tarefas em uma só. O que decide quanto demora é esperar por todos ao mesmo tempo em vez de um depois do outro: com quatro serviços que demoram 142, 2300 e 87 milissegundos (o quarto não responde), em série a soma dá cerca de 2.5 segundos e ao mesmo tempo demora perto do que demora o mais lento, uns 2.3. E se algum dia fizer falta cálculo pesado em paralelo, há outros caminhos, como vários processos.”

## Como sei que consegui

- [ ] Você consegue enumerar de memória os quatro passos entre executar um arquivo e ver o resultado (ler e verificar a forma, traduzir para *bytecode*, executar na máquina virtual, mostrar o resultado) e dizer em qual deles se detecta um parêntese sem fechar.
- [ ] Você consegue explicar para que serve o `__pycache__`, dizer por que é seguro apagá-lo e por que ele não é guardado no repositório.
- [ ] Você sabe prever que `print(142 + 1, "142" + "1")` mostra `143 1421`, e que `print("142" + 1)` termina em `TypeError`; e consegue explicar a diferença entre “dinâmico” e “forte” com esses dois exemplos.
- [ ] Você consegue dizer, sem olhar a lição, por que `tiempo_ms: int = "rápido"` não dá erro ao executar e que classe de ferramenta avisaria, sim.
- [ ] Você consegue explicar em duas frases o que é o GIL, quando ele afeta (cálculo com threads) e por que não afeta o `revisor`.
- [ ] Você consegue explicar com uma analogia própria o que é um ambiente virtual e por que o Linux Mint recusa o `pip install` no seu Python do sistema.
- [ ] Você consegue dizer qual versão do Python o Mint 22.x traz, qual é a vigente na data da lição, e por que o curso é ensinado com uma e roda nas duas.

## Resumo

Responda sem olhar a lição:

1. Que duas coisas significa a palavra “Python”? O que é o CPython?
2. O que é o *bytecode* e onde ele é guardado? Por que um `.pyc` da 3.12 não serve na 3.14?
3. Que diferença há entre tipagem dinâmica e tipagem forte? O que sai de combiná-las?
4. Quem verifica as anotações de tipo, e quem não as verifica?
5. O que é o GIL? Em que tipo de trabalho ele atrapalha e em qual quase não atrapalha?
6. Que problema um ambiente virtual resolve? Por que o Mint não deixa o `pip` instalar no Python do sistema?
7. Por que o curso é ensinado com a 3.14 e roda também na 3.12?

## Para ler mais

- [Glossário do Python](https://docs.python.org/pt-br/3/glossary.html) — as definições oficiais de *bytecode*, interpretado, GIL, ambiente virtual e dica de tipo que são citadas na lição, na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [PEP 484, “Type Hints”](https://peps.python.org/pep-0484/) — o documento que introduziu as anotações de tipo e diz que elas não são impostas na execução. Consultado em 7 de outubro de 2026.
- [PEP 668, “Marking Python base environments as externally managed”](https://peps.python.org/pep-0668/) — a origem do aviso `externally-managed-environment` que a próxima lição ensina você a reconhecer. Consultado em 7 de outubro de 2026.
- [Guia de desenvolvedores: estado das versões do Python](https://devguide.python.org/versions/) — qual versão está vigente, qual recebe segurança e quando cada uma termina. Consultado em 7 de outubro de 2026.
