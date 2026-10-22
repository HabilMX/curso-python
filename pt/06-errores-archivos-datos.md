# Lição 6 — Erros, arquivos e dados de fora

**Tempo:** 2 × 90 min (duas sessões; o corte fica entre as seções 6.2 e 6.3)

**O que você constrói:** a leitura da configuração do `revisor`: a lista de serviços deixa de estar escrita no código e passa a ser lida de um arquivo `servicios.toml`

**O que você aprende:** exceções (`try`, `except`, `else`, `finally`, uma exceção própria e `raise ... from`); ler um *traceback* de baixo para cima; arquivos com `with` e `pathlib`; UTF-8 explícito; os formatos TOML e JSON; validar o que chega de fora; e por que não se usam `eval` nem `pickle`

**De onde você vem.** Você traz o projeto da [Lição 5](05-modelo-de-datos.md): um `revisor` com o seu modelo de dados (`Servicio`, `Estado`, `Resultado`), a classificação com `match`, o relatório em tabela com o seu resumo, e a lista `SERVICIOS` escrita à mão dentro de `revisor.py`. Funciona, mas o exercício de projeto da lição 5 deixou um incômodo: para adicionar um serviço ao relatório é preciso **abrir o código Python e editá-lo**. Quem administra os serviços não tem por que saber programar, e quem programa não tem por que voltar a mexer no código toda vez que um endereço muda. Esta lição separa as duas coisas: os dados vão para um arquivo, e o programa aprende a lê-lo e a desconfiar dele. Você trabalha na sua pasta `~/curso-python/revisor/`, com o ambiente virtual ativado, e executa tudo com `python`.

**O que esta lição não faz.** Ela não consulta nenhuma rede: `revisar` continua usando os dados simulados da lição 5, e isso não muda até a [Lição 9](09-http-y-asyncio.md). Também não transforma o `revisor` em um comando com opções (`--config`, `--formato`): isso é o trabalho da [Lição 7](07-paquete-linea-de-comandos.md). Hoje o nome do arquivo está escrito em uma constante do programa. O que se resolve aqui é **como ler um arquivo de configuração sem que o programa quebre de formas incompreensíveis** quando o arquivo não existe, está mal escrito ou diz coisas que não fazem sentido.

**Sobre as execuções.** Para executar uma figura, entre na pasta da lição no repositório e rode `python fig06_01.py`; as figuras que vivem em uma pasta própria (`fig06_06/`, `fig06_07/`, `fig06_18/`) são executadas de dentro dela. Todas as saídas desta lição foram obtidas com Python 3.14.8 e repetidas com Python 3.12.12, da mesma linha 3.12 que vem com o Linux Mint 22. (O do Mint 22 é o 3.12.3, o que o Ubuntu 24.04, sua base, publica: é o que mostra a [página do pacote `python3.12` para o Ubuntu 24.04 no Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12).) São idênticas, exceto por umas marcas de sublinhado (`~~~~^^`) que o relatório de um erro traz em uma versão e não na outra; se na sua tela você vir mais ou menos marcas, é normal. Os programas estão em [`programas/06-errores-archivos-datos/`](https://github.com/HabilMX/curso-python/tree/main/programas/06-errores-archivos-datos), no repositório do curso.

## Ao terminar, você vai conseguir

- Ler o relatório de um erro (o *traceback*) de baixo para cima e dizer o que falhou, onde e quem chamou quem.
- Escrever um `try` com `except`, `else` e `finally`, capturando a exceção concreta que você sabe tratar e deixando as demais passarem.
- Definir uma exceção própria com uma linha de herança e lançá-la com `raise ... from`, de modo que o erro original não se perca.
- Abrir e ler um arquivo com `with` e com `pathlib.Path`, sempre com a codificação UTF-8 escrita, e explicar o que acontece se ela não estiver.
- Ler um arquivo TOML com `tomllib` e converter dados para JSON e de volta com `json`, lendo a linha e a coluna quando o JSON está errado.
- Validar dados de fora com `isinstance` e `urlsplit`, e explicar por que `True` passa por uma validação de inteiros feita de qualquer jeito.
- Explicar por que um texto que vem de fora nunca é passado para `eval` nem para `pickle`.

## O porquê antes do como

Abra o seu `revisor.py` da lição 5 e olhe a lista `SERVICIOS`. Toda vez que a equipe de operação quiser verificar um serviço novo, alguém tem de editar esse arquivo, salvar e executar de novo. Para o programador é um incômodo; para qualquer outra pessoa é um muro. E há um problema mais profundo: esse código e esses dados mudam **por razões diferentes e em ritmos diferentes**. O programa muda quando você descobre um erro ou quer uma função nova; a lista de serviços muda quando a empresa adiciona um serviço. Misturar as duas coisas em um arquivo obriga uma a esperar pela outra.

A solução é a de sempre: os dados vivem em um **arquivo de configuração**, um texto com regras que qualquer pessoa pode editar, e o programa o lê ao iniciar. Mas, assim que o programa lê algo que outra pessoa escreveu, ele entra em um terreno novo. Até a lição 5, cada dado do `revisor` foi escrito por você, no mesmo arquivo do código, e se estava errado você sabia na hora. Um arquivo de fora pode falhar de quatro formas, e as quatro são normais, não excepcionais:

1. **Não existe**, ou existe em outra pasta, diferente da que você imagina.
2. **Existe, mas está mal escrito**: falta uma aspa, sobra uma vírgula.
3. **Está bem escrito, mas falta algo**: um serviço sem nome, sem endereço.
4. **Está completo, mas diz algo absurdo**: um endereço que não é de uma página web, um tempo limite negativo, dois serviços com o mesmo nome.

Um programa sério distingue as quatro e diz à pessoa **qual delas aconteceu e como corrigi-la**, em vez de mostrar um relatório de erro de trinta linhas escrito para programadores. Isso se consegue com duas ferramentas que esta lição ensina juntas porque não se entendem separadamente: as **exceções** (como um programa avisa que algo deu errado, e como outro o captura) e a **validação** (como se verifica que o que chegou faz sentido).

O caminho tem duas sessões. A **primeira** cobre os conceitos 6.1 e 6.2: as exceções e os arquivos. Ao terminá-la, você saberá ler o relatório de um erro e abrir um arquivo de texto sem surpresas. A **segunda** cobre 6.3 e 6.4: os formatos (TOML e JSON) e a validação. Ao terminá-la, você terá o `revisor` lendo a sua lista de serviços de um arquivo e reclamando em linguagem clara quando o arquivo não presta. Com esse destino em mente, isto é o que você verá no final da lição ao executar o `revisor` de outra pasta, sem ter passado por onde está o arquivo (a mensagem é impressa em espanhol, como todos os textos do programa; em português: “erro de configuração: o arquivo servicios.toml não existe”):

```text
error de configuración: no existe el archivo servicios.toml
```

Uma mensagem de uma linha, em vez de um relatório de erro. Para chegar lá, é preciso entender primeiro o que é uma exceção.

## Os conceitos

### 6.1 Exceções

#### 6.1.1 O que é uma exceção e como se lê o seu relatório

Até agora, quando algo falhou nos seus programas, o Python parou e imprimiu um bloco de texto em vermelho, o *traceback* (neste curso, “o relatório do erro”). Você o leu pela primeira vez na [Lição 1](01-instalacion.md) e o viu em todas as lições. Agora vamos ver o que há por trás: esse relatório é o aviso de uma **exceção**, que é a forma que o Python tem de dizer “aqui aconteceu algo que não sei resolver”. Quando uma linha do programa não consegue fazer o que lhe foi pedido, ela **lança** uma exceção. A exceção sobe pelas funções que estavam em execução, da mais recente à mais antiga, procurando alguém que saiba o que fazer com ela. Se chegar ao topo sem que ninguém a capture, o programa para e o Python imprime o relatório.

Vamos provocar uma de propósito, com um caso que vai acontecer de verdade quando o `revisor` ler arquivos: um dado que deveria ser um número e chega com outra coisa. Para isso você precisa de uma função nova: `int(texto)` converte um texto em um número inteiro, assim como `str()` (lição 2) converte um valor em texto. `int("142")` dá o número 142. Mas o que `int("142 ms")` dá? Execute com `fig06_01.py`:

```python
# fig06_01.py
def leer_tiempo(texto: str) -> int:
    return int(texto)


def main() -> None:
    tiempo_ms = leer_tiempo("142 ms")
    print(f"tiempo: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

O programa define duas funções, `leer_tiempo` e `main`, e `main` chama `leer_tiempo` com um texto que traz as letras “ms” coladas. Execute:

```text
$ python fig06_01.py
Traceback (most recent call last):
  File "fig06_01.py", line 12, in <module>
    main()
    ~~~~^^
  File "fig06_01.py", line 7, in main
    tiempo_ms = leer_tiempo("142 ms")
  File "fig06_01.py", line 3, in leer_tiempo
    return int(texto)
ValueError: invalid literal for int() with base 10: '142 ms'
```

Este é o relatório, e vale a pena aprender a lê-lo bem, porque você vai lê-lo centenas de vezes. **Ele se lê de baixo para cima.** A **última linha** é a mais importante: `ValueError: invalid literal for int() with base 10: '142 ms'`. Ela diz duas coisas: o **tipo** da exceção, `ValueError` (“valor inválido”: o tipo do dado estava correto, um texto, mas o seu conteúdo não serve para o que se queria fazer), e uma **mensagem** que explica o que aconteceu. Em português: “texto inválido para converter em inteiro na base 10: '142 ms'”. A “base 10” é o sistema de numeração que todos usamos no dia a dia; a mensagem só diz que `int` esperava um número escrito com dígitos de 0 a 9 e encontrou, depois do 142, um espaço e as letras `ms`. (Os espaços no começo ou no fim não o incomodam: `int(" 142 ")` dá `142`; o que ele não aceita é qualquer coisa que não seja parte do número.)

As linhas de cima dizem **onde** aconteceu, e estão na ordem inversa à em que os fatos ocorreram. Cada par de linhas que começa com `File` é um **frame**: uma função que estava em execução. O último frame (`in leer_tiempo`, linha 3) é onde nasceu a exceção: a linha `return int(texto)`. O frame de cima (`in main`, linha 7) é quem chamou `leer_tiempo`. E o primeiro (`in <module>`, linha 12) é o próprio programa, que chamou `main()`. Leia o relatório como uma pilha de pratos: o prato de baixo é o mais recente, e é onde o problema começou. As linhas com `~~~~^^` são uma ajuda das versões recentes do Python ([PEP 657](https://peps.python.org/pep-0657/)): sublinham a parte exata da linha que falhou, para que você não precise adivinhar qual das três chamadas de uma linha longa foi.

Enquanto ninguém capturar a exceção, essa é a história completa: ela é lançada, sobe pela pilha, o programa morre. A [documentação oficial sobre erros e exceções](https://docs.python.org/pt-br/3/tutorial/errors.html) conta o mesmo com mais exemplos. Vejamos agora como capturá-la.

#### 6.1.2 `try`, `except`, `else` e `finally`

Capturar uma exceção é dizer ao Python: “tente isto; se falhar *desta* maneira, faça *aquilo* em vez de morrer”. Escreve-se com a instrução `try` (em inglês, “tentar”). Veja o programa `fig06_02.py`, que converte dois textos, um bom e um ruim:

```python
# fig06_02.py
def leer_tiempo(texto: str) -> int | None:
    try:
        tiempo_ms = int(texto)
    except ValueError:
        print(f"  '{texto}' no es un número entero")
        return None
    else:
        print(f"  '{texto}' se convirtió en {tiempo_ms}")
        return tiempo_ms
    finally:
        print("  (fin de la conversión)")


def main() -> None:
    for texto in ["142", "142 ms"]:
        print(f"leyendo '{texto}'")
        tiempo_ms = leer_tiempo(texto)
        print(f"  resultado: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_02.py
leyendo '142'
  '142' se convirtió en 142
  (fin de la conversión)
  resultado: 142
leyendo '142 ms'
  '142 ms' no es un número entero
  (fin de la conversión)
  resultado: None
```

São quatro blocos, e cada um tem uma regra clara:

- **`try:`** contém **somente** a linha que pode falhar, aqui `tiempo_ms = int(texto)`. Se não houver erro, o programa segue para o bloco `else`. Se houver, o Python abandona o `try` nessa mesma linha e salta para o `except` correspondente.
- **`except ValueError:`** contém o que se faz se o erro foi desse tipo. Neste caso, avisar que o texto não é um número e devolver `None` (o valor que, neste curso, significa “não há dado”). Entre o `except` e os dois-pontos vai o **tipo de exceção** que se captura; qualquer outro tipo passaria direto.
- **`else:`** (neste contexto, “se não houve erro”) é executado **somente se o `try` terminou sem exceção**. Aqui ele guarda o que se faz quando a conversão funcionou.
- **`finally:`** (“por fim”) é executado **sempre**: tenha havido erro ou não, tenha você devolvido um valor ou não. Serve para limpar, por exemplo fechar algo que foi aberto.

Repare na saída, porque ela contém uma surpresa que convém ver uma vez. Com o texto “142”, imprime-se primeiro “se convirtió en 142” (do `else`) e **depois** “(fin de la conversión)” (do `finally`), embora o `return tiempo_ms` do `else` apareça antes no código. Com “142 ms”, o `except` imprime o seu aviso, devolve `None`, e o `finally` **mesmo assim** é executado antes de a função terminar. Ou seja: o `finally` roda até quando o bloco já decidiu sair com `return`. Essa garantia é a razão da sua existência.

Restam duas perguntas razoáveis: por que um `else`, se o `print` e o `return` poderiam ir dentro do `try`? Porque **um `try` deve ser o menor possível**. Tudo o que você coloca dentro dele fica protegido pelo `except`, e se nessa linha a mais ocorrer um erro do mesmo tipo que você não esperava, o `except` o engoliria e você acreditaria que foi o erro que esperava. A regra é: no `try` vai **o que pode falhar da maneira que você sabe tratar**, e nada mais. O que deve acontecer se tudo deu certo vai no `else`.

A segunda pergunta: dá para capturar vários tipos? Dá, de duas maneiras. Uma é colocar vários blocos `except` um após o outro, cada um com o seu tipo e a sua resposta. A outra é colocar os tipos juntos **entre parênteses**, separados por vírgulas: `except (ValueError, TypeError):`, quando a resposta é a mesma. Escreva sempre os parênteses: no Python 3.12 eles são obrigatórios, e embora o Python 3.14 permita omiti-los quando o `except` não leva `as` ([PEP 758](https://peps.python.org/pep-0758/)), o código do curso roda nas duas versões.

#### 6.1.3 Capture a exceção concreta, nunca “qualquer uma”

Esta é a regra mais importante da seção, e se entende melhor vendo o que acontece quando ela é quebrada. Veja `fig06_03.py`. É a mesma função, mas com duas mudanças: o `except` diz `Exception` em vez de `ValueError`, e alguém escreveu errado um nome dentro do `try` (`stirp` em vez de `strip`, o método que remove espaços das pontas de um texto):

```python
# fig06_03.py
def leer_tiempo(texto: str) -> int | None:
    try:
        return int(texto.stirp())
    except Exception:  # noqa: BLE001
        print(f"'{texto}' no es un número entero")
        return None


def main() -> None:
    print(leer_tiempo("142"))


if __name__ == "__main__":
    main()
```

```text
$ python fig06_03.py
'142' no es un número entero
None
```

Veja o que aconteceu: o texto “142” é um número perfeitamente válido, e o programa disse que **não é**. A função não tem nada a ver com números: tem um erro de ortografia. Sem o `try`, o Python teria parado o programa com `AttributeError: 'str' object has no attribute 'stirp'. Did you mean: 'strip'?` (“um texto não tem o atributo `stirp`; você quis dizer `strip`?”), e você teria corrigido o erro de digitação em um minuto. Com um `except` largo demais, esse aviso virou uma mentira que aparece na tela, e o erro real fica enterrado até que alguém pergunte por que nenhum tempo é lido corretamente.

Para entender isso, é preciso saber que as exceções formam uma família. No topo está `BaseException`; abaixo dela, `Exception`, da qual pendem quase todos os erros que você vai encontrar; e dali saem os tipos concretos, alguns com parentes. `ValueError` é um deles. `KeyError` e `IndexError` (que você viu na lição 4) são filhos de `LookupError`. `FileNotFoundError` é um caso particular de `OSError`, a exceção dos problemas com o sistema operacional. `UnicodeDecodeError`, que você verá mais adiante, é um tipo de `ValueError`. A árvore completa está na [lista de exceções da documentação](https://docs.python.org/pt-br/3/library/exceptions.html). Capturar uma exceção captura **também todos os seus filhos**: por isso `except Exception` captura quase tudo, inclusive o `AttributeError` do erro de digitação, e por isso `except ValueError` captura também os erros de leitura de TOML e de JSON, como você verá em 6.3.

E há a pior versão: o `except:` **sem tipo**, chamado de “puro” (*bare*). Esse captura até o que está acima de `Exception`, inclusive o `KeyboardInterrupt` que o Python lança quando você pressiona `Ctrl`+`C` para interromper um programa. Um programa com um `except:` puro pode não morrer quando você pede. O [guia de estilo PEP 8](https://peps.python.org/pep-0008/#programming-recommendations) pede que se nomeiem as exceções concretas sempre que possível em vez de usá-lo, e que ele seja reservado para casos contados; neste curso a regra é mais estrita e não tem exceções: nunca.

As regras, então, são três. **Primeira:** capture o tipo concreto que você sabe tratar, com a resposta concreta que faz sentido. **Segunda:** se você não sabe o que fazer com um erro, **não o capture**: deixe-o subir, que o programa pare com o seu relatório, e alguém o verá. Um programa que para com um relatório claro é melhor do que um que continua funcionando com dados errados. **Terceira:** se você realmente precisa capturar `Exception` (por exemplo, na última linha de defesa de um programa que não deve cair), faça-o em um único lugar, registre o que aconteceu e não o deixe passar em silêncio. O comentário `# noqa: BLE001` que você vê em `fig06_03.py` é uma marca para o `ruff`, a ferramenta que verifica o estilo do código e que você conhecerá na [Lição 8](08-pruebas-tipos-calidad.md): ele diz “sei que esta linha captura uma exceção ampla demais, é de propósito”. A regra do `ruff` que reclama se chama justamente “captura de exceção cega” (*blind except*).

#### 6.1.4 Uma exceção própria e `raise ... from`

Até agora você capturou exceções que o Python já traz. Para o `revisor` falta mais uma, porque você precisa distinguir **“o arquivo de configuração tem um problema”** de **“o meu programa tem um erro”**. As duas situações merecem respostas diferentes: a primeira se explica à pessoa que escreveu o arquivo; a segunda é um defeito que deve parar o programa com o seu relatório, para que um programador o corrija. Se tudo fosse lançado como `ValueError`, o programa não poderia distinguir uma da outra.

A solução é uma exceção com nome próprio, que se define com uma linha de **herança**. Veja `fig06_04.py`:

```python
# fig06_04.py
class ErrorDeConfiguracion(Exception):
    """La configuración no se puede usar."""


def leer_timeout_ms(texto: str) -> int:
    try:
        return int(texto)
    except ValueError as error:
        mensaje = f"'timeout_ms' debe ser un entero, llegó '{texto}'"
        raise ErrorDeConfiguracion(mensaje) from error


def main() -> None:
    try:
        timeout_ms = leer_timeout_ms("cinco mil")
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        print(f"causa original: {error.__cause__}")
    else:
        print(f"timeout_ms = {timeout_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_04.py
error de configuración: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
causa original: invalid literal for int() with base 10: 'cinco mil'
```

A primeira instrução é nova na forma, embora você já tenha visto `class` na lição 5 como um “molde de dados”: `class ErrorDeConfiguracion(Exception):` define um molde novo chamado `ErrorDeConfiguracion`, e os parênteses dizem que ele **herda** de `Exception`. Herdar significa “é uma `Exception` e além disso tem o seu próprio nome”: tudo o que o Python sabe fazer com qualquer exceção (lançá-la, capturá-la, imprimir a sua mensagem, mostrar o seu relatório) ele sabe fazer com a sua, sem escrever mais nada. É um único nível de herança, e é tudo de que você precisa; o curso não entra em mais. O texto entre aspas triplas dentro da classe é uma **string de documentação** (*docstring*): uma frase que explica para que ela serve, e que o Python guarda para quem quiser consultá-la. Não é necessária nenhuma outra instrução dentro da classe.

A função `leer_timeout_ms` faz algo que você vai repetir em todo o curso: captura um erro de baixo nível (`ValueError`, de `int`) e o **traduz** para um do domínio do programa (`ErrorDeConfiguracion`), com uma mensagem que fala nos termos de quem escreveu a configuração: “'timeout_ms' debe ser un entero, llegó 'cinco mil'” (“'timeout_ms' deve ser um inteiro, chegou 'cinco mil'”). A mensagem do `int` (“invalid literal for int()…”) é útil para um programador, mas não para quem edita um arquivo de configuração. A instrução `raise` (em inglês, “levantar”) lança a exceção, e o final `from error` faz algo importante: **conserva o erro original como causa**. Essa causa fica guardada dentro da nova exceção, em `error.__cause__` (os dois sublinhados antes e depois são a forma como o Python marca nomes que reserva para si). A segunda linha da saída mostra isso: o programa imprimiu o seu aviso em espanhol e, à parte, a causa original em inglês, para o caso de ser necessária.

O que acontece se ninguém capturar a exceção? Veja `fig06_05.py`, que é o mesmo programa sem o `try` em `main`:

```text
$ python fig06_05.py
Traceback (most recent call last):
  File "fig06_05.py", line 8, in leer_timeout_ms
    return int(texto)
ValueError: invalid literal for int() with base 10: 'cinco mil'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "fig06_05.py", line 20, in <module>
    main()
    ~~~~^^
  File "fig06_05.py", line 15, in main
    timeout_ms = leer_timeout_ms("cinco mil")
  File "fig06_05.py", line 11, in leer_timeout_ms
    raise ErrorDeConfiguracion(mensaje) from error
ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
```

Este relatório tem **duas** partes separadas por uma frase: “The above exception was the direct cause of the following exception” (“a exceção de cima foi a causa direta da seguinte”). É a marca do `from error`. Lê-se como antes, de baixo para cima: a última linha, `ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'`, é o que chegou ao topo. Mas agora, além disso, o Python **conserva a história**: em cima está o `ValueError` original, com a sua linha exata (`return int(texto)`). Se você não tivesse escrito `from error`, o relatório diria em vez disso “During handling of the above exception, another exception occurred” (“durante o tratamento da exceção de cima, ocorreu outra”), que sugere um erro novo ocorrido dentro do tratamento de outro. O Python mostraria as duas exceções do mesmo jeito (a original fica guardada como *contexto*, no atributo `__context__`), mas o relatório não diria mais que uma foi **consequência** da outra: diria que a segunda aconteceu “enquanto isso”, como se fosse um acidente à parte. Com `from`, a original fica registrada como **causa** (`__cause__`), que é o que de fato aconteceu. A regra: **quando você traduz uma exceção, escreva sempre `from`**. Quem depurar o seu programa vai agradecer. A explicação da técnica está na [PEP 3134](https://peps.python.org/pep-3134/) e na [seção sobre encadeamento de exceções](https://docs.python.org/pt-br/3/tutorial/errors.html#exception-chaining) do tutorial.

Com isso você tem o vocabulário das exceções. Falta um lugar para usá-lo, e é o próximo: ler arquivos, onde as coisas falham por razões que você não controla.

### 6.2 Arquivos

#### 6.2.1 Abrir, ler, fechar: `with`

Um arquivo no disco não é “lido” sem mais nem menos: primeiro ele é **aberto**, o que pede ao sistema operacional um acesso a ele; depois o seu conteúdo é lido; e no fim ele é **fechado**, o que devolve o acesso. Um arquivo que é aberto e não é fechado consome recursos do sistema (cada programa só pode ter um número limitado deles abertos) e, se você estava escrevendo, pode deixar a última parte sem salvar. A forma mais cuidadosa de escrever isso, com o que você já sabe de `try`, seria esta:

```python
archivo = open("nota.txt", encoding="utf-8")
try:
    texto = archivo.read()
finally:
    archivo.close()
```

Funciona, e o `finally` garante o fechamento mesmo que `read()` falhe. Mas é muito ritual para algo tão frequente, e é fácil esquecer o `finally`. O Python oferece a instrução `with` (“com”), que faz exatamente isso por você. Veja `fig06_06/leer.py` e o arquivo `nota.txt` que ele lê:

```text fig06_06/nota.txt
Revisión de las 9:00
reportes: sin conexión
```

```python
# fig06_06/leer.py
with open("nota.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
    print(f"dentro del with: cerrado = {archivo.closed}")

print(f"fuera del with: cerrado = {archivo.closed}")
print(texto.splitlines())
```

```text
$ cd fig06_06
$ python leer.py
dentro del with: cerrado = False
fuera del with: cerrado = True
['Revisión de las 9:00', 'reportes: sin conexión']
```

`open("nota.txt", encoding="utf-8")` abre o arquivo e devolve um objeto que representa essa abertura. `with ... as archivo:` diz “enquanto este bloco durar, o arquivo se chama `archivo`; quando você sair do bloco, feche-o, aconteça o que acontecer”. A saída demonstra isso: dentro do `with`, `archivo.closed` (a pergunta “está fechado?”) diz `False`; assim que o bloco termina, diz `True`, e ninguém escreveu um `close()`. Se o bloco termina por uma exceção, o arquivo também é fechado: o `with` é, na prática, um `try`/`finally` escrito de forma abreviada. A [referência da instrução `with`](https://docs.python.org/pt-br/3/reference/compound_stmts.html#with) explica o mecanismo completo; para este curso basta a regra: **todo arquivo que você abrir, abra com `with`**.

`archivo.read()` devolve o conteúdo completo como um único texto. No programa se imprime `texto.splitlines()`, um método dos textos que os parte em uma lista com uma string por linha, e que remove as quebras de linha; assim você vê de relance que o arquivo tem duas linhas. Repare também em `encoding="utf-8"`: é uma parte do `open` que não é enfeite, e a sua razão é explicada em 6.2.3.

#### 6.2.2 `pathlib.Path`: um caminho como valor, não como texto

O nome do arquivo, `"nota.txt"`, é um **caminho** (*path*): o endereço de um arquivo dentro do disco. Até agora o escrevemos como texto, e para um único arquivo na pasta atual não há problema. Mas os caminhos têm regras próprias: no Linux e no macOS as pastas se separam com `/`, no Windows com `\`; um caminho pode ser **absoluto** (começa na raiz do disco, como `/home/ana/curso-python/revisor/servicios.toml`) ou **relativo** (conta-se a partir da pasta onde você está, como `servicios.toml`). Manipular caminhos como textos, com somas e recortes, quebra assim que qualquer uma dessas regras muda.

Para isso o módulo `pathlib` da biblioteca padrão oferece a classe `Path`: um valor que **sabe o que é um caminho**. Você constrói um com `Path("nota.txt")` e, a partir daí, ele tem operações próprias, que se invocam com um ponto, como os métodos de listas e dicionários que você já conhece. Veja `fig06_07/ruta.py`, que usa o mesmo `nota.txt`:

```python
# fig06_07/ruta.py
from pathlib import Path

ruta = Path("nota.txt")
print(ruta.name, ruta.suffix, ruta.exists())
print(Path("no-esta.txt").exists())

otra = Path("datos") / "servicios.toml"
print(otra)

texto = ruta.read_text(encoding="utf-8")
print(texto.splitlines())
```

```text
$ cd fig06_07
$ python ruta.py
nota.txt .txt True
False
datos/servicios.toml
['Revisión de las 9:00', 'reportes: sin conexión']
```

Linha por linha:

- `Path("nota.txt")` cria o caminho. Ainda não toca o disco: apenas descreve um endereço, exista o arquivo ou não.
- `ruta.name` é o nome do arquivo (`nota.txt`), `ruta.suffix` é a sua terminação com o ponto (`.txt`), e `ruta.exists()` pergunta ao disco se ele existe (`True`). A segunda linha faz a mesma pergunta sobre um arquivo que não está lá, e responde `False`: **perguntar se existe um arquivo que não está lá não lança nenhuma exceção**. (Uma sutileza de versão: no 3.12, se a pergunta esbarra em outro problema do sistema, como não ter permissão para olhar a pasta, `exists()` ainda pode lançar um `OSError`; a partir do 3.14 [ele responde `False` em todos esses casos](https://docs.python.org/pt-br/3/library/pathlib.html#pathlib.Path.exists).)
- `Path("datos") / "servicios.toml"` usa o operador `/` com um significado novo: **juntar** duas partes de um caminho com o separador que couber ao sistema. O resultado é impresso como `datos/servicios.toml` e não toca o disco. É muito mais seguro do que somar textos.
- `ruta.read_text(encoding="utf-8")` abre o arquivo, lê tudo, fecha e devolve o texto, em uma única chamada. É a forma que usaremos no `revisor` porque não deixa nada aberto. A [documentação do `pathlib`](https://docs.python.org/pt-br/3/library/pathlib.html) lista o resto do que um caminho pode fazer (listar pastas, criar arquivos); neste curso só é preciso o que você vê aqui.

Há uma consequência prática de os caminhos relativos serem “contados a partir de onde você está”: o mesmo programa, com o mesmo `Path("nota.txt")`, funciona ou não conforme a pasta de onde você o executa. O que acontece quando o arquivo não existe? Veja `fig06_08.py`, que tenta abrir um arquivo que não está lá:

```python
# fig06_08.py
with open("no-esta.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
print(texto)
```

```text
$ python fig06_08.py
Traceback (most recent call last):
  File "fig06_08.py", line 2, in <module>
    with open("no-esta.txt", encoding="utf-8") as archivo:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'
```

É lançada `FileNotFoundError` (“arquivo não encontrado”), uma exceção concreta que você pode capturar. O texto da mensagem, `[Errno 2] No such file or directory`, vem do sistema operacional e está em inglês: você não o controla, e por isso não o mostrará a quem usar o `revisor`. Em 6.4 o programa vai capturar essa exceção e traduzi-la para uma mensagem própria.

#### 6.2.3 Texto e bytes: por que sempre `encoding="utf-8"`

Um arquivo no disco não guarda letras: guarda **bytes**, números de 0 a 255. Para que esses números sejam texto, alguém tem de decidir qual número corresponde a qual letra. Essa decisão é a **codificação**, e existem muitas. A que domina hoje é o **UTF-8**: ele pode representar qualquer caractere de qualquer idioma, e as letras sem acento ocupam um único byte. Os caracteres com acento, como o “ó” de “conexión”, ocupam dois. Uma codificação antiga, a `latin-1`, representa o “ó” com um único byte, mas só serve para alguns poucos idiomas europeus. Ver é mais claro do que explicar. Execute `fig06_09.py`, que fabrica os bytes de um mesmo texto nas duas codificações:

```python
# fig06_09.py
texto = "sin conexión"

en_utf8 = texto.encode("utf-8")
en_latin1 = texto.encode("latin-1")

print(en_utf8)
print(en_latin1)
print(len(texto), len(en_utf8), len(en_latin1))
print(en_utf8.decode("utf-8"))
```

```text
$ python fig06_09.py
b'sin conexi\xc3\xb3n'
b'sin conexi\xf3n'
12 13 12
sin conexión
```

`texto.encode("utf-8")` converte um texto em bytes com essa codificação; os bytes são impressos com um `b` na frente (`b'sin conexi\xc3\xb3n'`), e `\xc3\xb3` são os dois bytes (em hexadecimal) que o UTF-8 usa para o “ó”. Com `latin-1` o “ó” é um único byte, `\xf3`. A terceira linha confirma isso com uma conta: o texto tem 12 caracteres; em UTF-8 são 13 bytes e em `latin-1`, 12. E `bytes.decode("utf-8")` faz o caminho inverso: de bytes para texto. Com os bytes de UTF-8 volta “sin conexión”.

Agora o problema. O que acontece se os bytes foram escritos em uma codificação e são lidos com outra? Execute `fig06_10.py`, que tenta ler como UTF-8 os bytes de `latin-1`. O `b` antes das aspas marca um literal de **bytes**, e `\xf3` escreve o byte cujo valor, em hexadecimal (o sistema de numeração em base 16 com que se costuma escrever bytes), é `f3`, ou seja, 243:

```python
# fig06_10.py
en_latin1 = b"sin conexi\xf3n"

print(en_latin1.decode("utf-8"))
```

```text
$ python fig06_10.py
Traceback (most recent call last):
  File "fig06_10.py", line 4, in <module>
    print(en_latin1.decode("utf-8"))
          ~~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10: invalid continuation byte
```

A última linha diz: “o codec `utf-8` não consegue decodificar o byte `0xf3` na posição 10: continuação inválida”. O byte `0xf3` é o do “ó” em `latin-1`, mas em UTF-8 esse valor significa “aqui começa um caractere de quatro bytes”, e o byte seguinte não tem a forma que corresponde a uma continuação. O Python, corretamente, se recusa a adivinhar. É um `UnicodeDecodeError`, que é um tipo de `ValueError`.

Isso explica por que se escreve `encoding="utf-8"` **sempre**: quando você não o escreve, o Python escolhe a codificação segundo a configuração do sistema onde roda, de acordo com [a documentação do `open`](https://docs.python.org/pt-br/3/library/functions.html#open). O mesmo programa pode ler bem um arquivo no seu computador e falhar no de um colega, porque a configuração é diferente. Se você o escreve, o programa se comporta igual em toda parte. E não é capricho: os dois formatos que você usará a seguir exigem UTF-8. A [especificação do TOML](https://toml.io/en/v1.0.0) diz que um documento TOML é um texto Unicode válido em UTF-8, e a [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) estabelece que o JSON trocado entre sistemas, fora dos ecossistemas fechados, deve usar UTF-8. Se você quiser entender mais o assunto de fundo, o [HOWTO de Unicode](https://docs.python.org/pt-br/3/howto/unicode.html) da documentação o conta passo a passo.

> **Aqui termina a primeira sessão.** Até este ponto você tem os conceitos 6.1 e 6.2: exceções e arquivos. Antes da segunda sessão, execute as figuras `fig06_01.py` a `fig06_10.py` e mude algo em cada uma: outro texto no lugar de “142 ms”, um `except` diferente, outro nome de arquivo. Provocar o erro você mesmo fixa mais do que lê-lo. A próxima sessão começa com os formatos.

### 6.3 Formatos: TOML e JSON

#### 6.3.1 O que é um formato e por que há dois

Um arquivo de texto com linhas soltas não basta para descrever uma lista de serviços, cada um com nome, endereço e talvez um tempo limite. É preciso um **formato**: um conjunto de regras que diz como se escreve cada coisa, para que qualquer programa possa lê-lo sem ambiguidades. Os dois formatos mais usados em Python e no resto do mundo para dados estruturados são o **TOML** e o **JSON**, e cumprem funções diferentes:

- O **TOML** foi pensado para que **uma pessoa o escreva e o leia**: permite comentários com `#`, não exige chaves nem vírgulas por todo lado, e é difícil escrevê-lo de forma ambígua. É o formato dos arquivos de configuração, e é o que o Python já usa para a configuração de projetos (você verá isso na lição 7, no `pyproject.toml`). O `revisor` lerá a sua lista de serviços de um arquivo TOML.
- O **JSON** foi pensado para que **dois programas troquem dados**. Não admite comentários e exige chaves, aspas e vírgulas, mas quase todas as linguagens sabem lê-lo e escrevê-lo. É o formato das respostas de quase qualquer serviço web, e o que o `revisor` usará para entregar o seu relatório a outros programas.

A biblioteca padrão do Python traz um módulo para cada um: `tomllib` (para ler TOML) e `json` (para ler e escrever JSON). Há uma assimetria que convém saber: o `tomllib` só **lê**. Para escrever TOML é preciso instalar uma biblioteca externa, e este curso não precisa dela porque nunca escreve configuração, só a lê.

#### 6.3.2 Ler TOML com `tomllib`

Um TOML é uma série de linhas `llave = valor` (chave = valor), com valores de poucos tipos: texto entre aspas duplas, números inteiros e decimais, `true` e `false`, e listas. Além disso tem **tabelas**, que agrupam chaves sob um nome entre colchetes. O que nos interessa é um caso particular: uma lista de tabelas, ou *array of tables*, que se escreve com **colchetes duplos**, `[[servicios]]`, e cada vez que o cabeçalho aparece começa um elemento novo da lista. É a forma natural de escrever “uma lista de serviços, cada um com os seus campos”. A [especificação do TOML](https://toml.io/en/v1.0.0#array-of-tables) tem a definição exata; com um exemplo se entende mais rápido. Veja `fig06_11.py`, que lê um TOML escrito dentro do próprio programa:

```python
# fig06_11.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
"""

datos = tomllib.loads(TEXTO)
print(datos)

segundo = datos["servicios"][1]
print(segundo["nombre"], segundo["timeout_ms"], type(segundo["timeout_ms"]))
print(segundo.get("proxy"))
```

```text
$ python fig06_11.py
{'servicios': [{'nombre': 'catalogo', 'url': 'https://catalogo.example'}, {'nombre': 'notificaciones', 'url': 'https://notificaciones.example', 'timeout_ms': 1000}]}
notificaciones 1000 <class 'int'>
None
```

Dois detalhes de leitura antes do resultado. O texto vai entre **aspas triplas** (`"""`...`"""`), que em Python servem para escrever um texto de várias linhas com as quebras de linha incluídas. E `tomllib.loads(TEXTO)` é a função que lê: o nome vem de *load string* (“carregar a partir de um texto”), e devolve um **dicionário**, uma estrutura que você já conhece. (Existe também `tomllib.load`, que lê de um arquivo aberto em modo binário; no `revisor` leremos o texto nós mesmos com `read_text` para controlar a codificação e os erros.)

Veja como ficou o dicionário. Há uma única chave, `'servicios'`, cujo valor é uma **lista com dois dicionários**: um para cada `[[servicios]]`. O segundo dicionário tem uma chave a mais, `timeout_ms`, e o seu valor é o número `1000`: a terceira linha da saída confirma que é um `int`. É assim que se lê qualquer dado de um TOML: `datos["servicios"]` é a lista, `datos["servicios"][1]` é o segundo serviço, `datos["servicios"][1]["nombre"]` é o seu nome. E a última linha da saída mostra algo que usaremos muito: `segundo.get("proxy")` pergunta por uma chave que **não existe** e devolve `None`, enquanto `segundo["proxy"]` teria lançado um `KeyError`. Para os dados opcionais (como `timeout_ms`), `.get` é a ferramenta.

E se o TOML estiver mal escrito? Veja `fig06_12.py`, onde na linha do nome falta a aspa de fechamento:

```python
# fig06_12.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo
url = "https://catalogo.example"
"""

try:
    tomllib.loads(TEXTO)
except tomllib.TOMLDecodeError as error:
    print(f"TOML inválido: {error}")
```

```text
$ python fig06_12.py
TOML inválido: Illegal character '\n' (at line 3, column 19)
```

`tomllib.TOMLDecodeError` é a exceção de um TOML inválido. A sua mensagem, `Illegal character '\n' (at line 3, column 19)`, diz “caractere ilegal, uma quebra de linha, na linha 3, coluna 19”: o texto começou com uma aspa e encontrou o fim da linha sem que ela fosse fechada. Repare que a mensagem leva você ao ponto exato, e que quem a diz é o próprio módulo. No `revisor` incluiremos essa mensagem tal qual no erro de configuração. As funções e as exceções deste módulo estão na [documentação do `tomllib`](https://docs.python.org/pt-br/3/library/tomllib.html); o módulo entrou na biblioteca padrão no Python 3.11 com a [PEP 680](https://peps.python.org/pep-0680/).

#### 6.3.3 Ler e escrever JSON com `json`

O JSON tem regras mais estritas e um vocabulário menor. Um objeto JSON se escreve entre chaves, com pares `"llave": valor`; uma lista, entre colchetes; os textos, entre aspas duplas (**sempre duplas**); os números, sem aspas; e existem três palavras: `true`, `false` e `null`. O Python tem um equivalente para cada peça, e o módulo `json` converte de um para o outro:

| JSON | Python |
|---|---|
| objeto `{...}` | `dict` |
| array `[...]` | `list` |
| texto `"..."` | `str` |
| número inteiro | `int` |
| número com decimais | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

As regras estritas são as do padrão; o módulo `json` do Python, por padrão, é um pouco mais permissivo, e [a sua documentação](https://docs.python.org/pt-br/3/library/json.html) diz isso abertamente: aceita e escreve `NaN`, `Infinity` e `-Infinity` (os “não é um número” e “infinito” dos `float`), que o padrão não admite, e se um objeto repete uma chave, fica com o último valor. Para o `revisor` isso não importa, porque seus números são inteiros; se algum dia você precisar de um JSON que qualquer outro programa aceite, `json.dumps(..., allow_nan=False)` se recusa a escrever esses valores.

A conversão de Python para JSON (**serializar**) se faz com `json.dumps` (“*dump string*”: despejar em texto), e a inversa (**desserializar**) com `json.loads`. Veja `fig06_13.py`, que usa um resultado do `revisor` como exemplo:

```python
# fig06_13.py
import json

resultado = {
    "nombre": "reportes",
    "estado": "CAIDO",
    "tiempo_ms": None,
    "detalle": "sin conexión",
    "activo": True,
}

texto = json.dumps(resultado, ensure_ascii=False, indent=2)
print(texto)

de_vuelta = json.loads(texto)
print(de_vuelta["tiempo_ms"] is None, de_vuelta == resultado)

print(json.dumps(resultado["detalle"]))
print(json.dumps(resultado["detalle"], ensure_ascii=False))
```

```text
$ python fig06_13.py
{
  "nombre": "reportes",
  "estado": "CAIDO",
  "tiempo_ms": null,
  "detalle": "sin conexión",
  "activo": true
}
True True
"sin conexi\u00f3n"
"sin conexión"
```

Quatro coisas a aprender com esta saída. Uma: `None` virou `null` e `True` virou `true`; o JSON não é Python, e cada linguagem tem a sua ortografia de “nada” e de “verdadeiro”. Duas: `indent=2` faz o `dumps` escrever o resultado em várias linhas com dois espaços de recuo, legível para uma pessoa; sem ele, sairia tudo em uma única linha compacta. Três: a comparação `de_vuelta == resultado` dá `True`, porque `loads` reconstrói o dicionário original, e `de_vuelta["tiempo_ms"] is None` também, porque `null` volta como `None`. E quatro, a mais sutil: as duas últimas linhas imprimem o mesmo texto, “sin conexión”, de duas maneiras. Por padrão, o `dumps` **escapa** todo caractere que não seja ASCII e escreve `"sin conexi\u00f3n"`, que é JSON válido, mas ilegível para uma pessoa. Com `ensure_ascii=False` ele escreve o “ó” tal qual. Como o `revisor` escreve em espanhol, o relatório JSON levará sempre `ensure_ascii=False`. Essa é a forma que o curso fixa para todo o relatório: `json.dumps(datos, ensure_ascii=False, indent=2)`.

Um aviso que se aprende melhor do jeito difícil. O `json.dumps` só entende os tipos da tabela acima (e a tupla, que ele escreve como array, igual a uma lista). Os dados do `revisor` estão em objetos próprios, `Resultado`, `Servicio` e `Estado`, e se você tentar `json.dumps(Estado.CAIDO)` obtém `TypeError: Object of type Estado is not JSON serializable` (“um objeto do tipo `Estado` não pode ser serializado para JSON”). A solução é montar primeiro um dicionário com tipos simples, usando `estado.value` para tirar o texto do `Enum`, e serializar esse dicionário. É o que a função `reporte_a_json` fará mais adiante.

E, como o TOML, o JSON também falha. Veja `fig06_14.py`, onde falta uma vírgula entre dois pares:

```python
# fig06_14.py
import json

TEXTO = """{
  "nombre": "pagos",
  "tiempo_ms": 87
  "estado": "ARRIBA"
}"""

try:
    json.loads(TEXTO)
except json.JSONDecodeError as error:
    print(f"mensaje: {error.msg}")
    print(f"línea {error.lineno}, columna {error.colno}")
    print(f"completo: {error}")
```

```text
$ python fig06_14.py
mensaje: Expecting ',' delimiter
línea 4, columna 3
completo: Expecting ',' delimiter: line 4 column 3 (char 43)
```

`json.JSONDecodeError` guarda o problema em três atributos úteis: `msg` (“era esperada uma vírgula como delimitador”), `lineno` (a linha) e `colno` (a coluna). Aqui, a linha 4, coluna 3: depois do `87` da linha anterior deveria vir uma vírgula, e o decodificador sentiu falta dela justamente ao começar o par seguinte. A mensagem completa, que se obtém ao imprimir o erro, traz ainda `char 43`, a posição contada desde o início. A [documentação do `json`](https://docs.python.org/pt-br/3/library/json.html) descreve todos os parâmetros de `dumps` e `loads`, e a [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) é a especificação do formato. O fato de `JSONDecodeError` ser também um `ValueError` diz algo que você já sabe de 6.1.3: um `except ValueError` o capturaria, junto com muitos outros erros que não têm a ver. É sempre melhor nomear o tipo concreto.

### 6.4 Validar o que chega de fora

#### 6.4.1 Por que é preciso validar, e onde

Um arquivo pode estar bem escrito e ser, mesmo assim, inútil. Este TOML é perfeitamente válido:

```toml
[[servicios]]
nombre = 42
url = "ftp://archivos.example"
timeout_ms = -3
```

Cada linha segue as regras do TOML. Mas o nome é um número, o endereço não é de uma página web, e o tempo limite é negativo. Se o programa o aceita sem olhar, o erro aparecerá mais adiante, longe da sua causa, em uma linha que não tem nada a ver com o arquivo: um `TypeError` ao tentar alinhar um nome, ou uma requisição que nunca sai. **Validar** é verificar, no momento em que os dados entram, que eles têm a forma e o sentido que o programa espera.

Há uma razão específica do Python para fazer isso à mão. Na [Lição 0](00-que-es-python.md) você viu que as anotações de tipo (`nombre: str`) **não são impostas na execução**: são uma nota para você e para as ferramentas, não um cadeado. Um `Servicio(nombre=42, ...)` é criado sem reclamar. Por isso a fronteira do programa, o ponto por onde entra o que vem de fora, é o lugar onde os tipos são verificados de verdade. Uma vez validados, o resto do programa pode confiar neles sem olhar de novo. Essa ideia, **validar na fronteira e confiar por dentro**, organiza todo o `revisor`: um único módulo, `configuracion.py`, se encarrega de desconfiar do exterior.

A regra de fundo é a que formula o [guia de validação de entradas da OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): o que chega de fora não é confiável até ser verificado, e a verificação que melhor funciona é uma **lista do que é permitido**: enumera-se o que vale e rejeita-se todo o resto, em vez de tentar enumerar tudo o que está errado.

#### 6.4.2 `isinstance` e a armadilha do `bool`

Para perguntar “este valor é deste tipo?” existe `isinstance(valor, tipo)`, uma função que devolve `True` ou `False`. `isinstance(5000, int)` é `True`; `isinstance("5000", int)` é `False`, porque o texto “5000” não é um inteiro, embora se pareça com um. Com ela se pode escrever a validação do tempo limite: “tem de ser um inteiro maior que zero”. E aqui há uma armadilha que merece a sua própria figura. Veja `fig06_15.py`:

```python
# fig06_15.py
print(isinstance(True, int))
print(isinstance(True, bool))
print(True + True)


def timeout_valido(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


for valor in [5000, 0, -1, True, "5000", 2.5]:
    print(valor, type(valor), timeout_valido(valor))
```

```text
$ python fig06_15.py
True
True
2
5000 <class 'int'> True
0 <class 'int'> False
-1 <class 'int'> False
True <class 'bool'> False
5000 <class 'str'> False
2.5 <class 'float'> False
```

As três primeiras linhas são a armadilha. `isinstance(True, int)` é **`True`**: em Python, um `bool` é um tipo de inteiro. `True` é literalmente o número 1, e `False` o 0, e por isso `True + True` dá `2`. Não é um acidente: é uma decisão de design antiga da linguagem, descrita na [documentação dos tipos embutidos](https://docs.python.org/pt-br/3/library/stdtypes.html#boolean-type-bool). A consequência, para você, é concreta. Uma validação ingênua como `isinstance(timeout_ms, int) and timeout_ms > 0` **aceita `true`** como tempo limite, porque `true` é um inteiro positivo: vale 1. Alguém que escreve `timeout_ms = true` no arquivo (uma confusão compreensível) obteria um tempo limite de um milissegundo sem que ninguém reclame.

A função `timeout_valido` do programa evita isso: pergunta `isinstance(valor, int)` **e além disso** `not isinstance(valor, bool)`. As últimas seis linhas da saída mostram o resultado com seis valores: o inteiro 5000 passa; o 0 e o -1 não passam pela condição `valor > 0`; `True` não passa; o texto `"5000"` não passa (é uma `str`); e o decimal `2.5` também não (é um `float`). Observe que o teste foi feito com uma **lista de valores representativos**, incluindo os casos estranhos: assim se testa uma validação, olhando justamente os valores que poderiam passar de fininho.

#### 6.4.3 Endereços: o esquema permitido

Outro dado de fora do `revisor` é o endereço (`url`) de cada serviço. Um endereço tem partes, e a primeira é o **esquema**: o que vem antes dos dois-pontos, e que diz qual protocolo usar (`https`, `http`, `ftp`, `file`...). Para um verificador de serviços web só dois fazem sentido: `http` e `https`. Por que isso importa tanto? Porque mais adiante o programa fará uma requisição a esse endereço, e com a biblioteca `urllib` um endereço `file:///...` faz o programa **ler um arquivo do disco** em vez de consultar um serviço, enquanto outros esquemas o fariam falar com outro tipo de servidor. Um arquivo de configuração que outra pessoa editou não deve poder conseguir isso.

A biblioteca padrão traz `urllib.parse.urlsplit`, que parte um endereço em seus componentes. Veja `fig06_16.py`, que testa seis endereços:

```python
# fig06_16.py
from urllib.parse import urlsplit

DIRECCIONES = [
    "https://catalogo.example",
    "http://127.0.0.1:8099/catalogo",
    "ftp://archivos.example",
    "file:///etc/hosts",
    "catalogo.example",
    "javascript:alert(1)",
]

for direccion in DIRECCIONES:
    esquema = urlsplit(direccion).scheme
    permitida = esquema in {"http", "https"}
    print(f"{direccion:<32} esquema='{esquema}' permitida={permitida}")
```

```text
$ python fig06_16.py
https://catalogo.example         esquema='https' permitida=True
http://127.0.0.1:8099/catalogo   esquema='http' permitida=True
ftp://archivos.example           esquema='ftp' permitida=False
file:///etc/hosts                esquema='file' permitida=False
catalogo.example                 esquema='' permitida=False
javascript:alert(1)              esquema='javascript' permitida=False
```

`urlsplit(direccion).scheme` é o esquema. A validação é uma pergunta de pertinência: `esquema in {"http", "https"}`, com o conjunto do que é permitido, como na lista de permitidos de que falamos. Observe os casos: os dois primeiros endereços passam; `ftp` e `file` não; `catalogo.example` (sem esquema) tem um esquema vazio e não passa; e `javascript:alert(1)` tem o esquema `javascript`, que também não. Note a escolha de design: **não** se escreveu uma lista de esquemas proibidos (`ftp`, `file`, `javascript`...), porque amanhã alguém inventa outro e ele passa. Escreveu-se a lista dos dois permitidos. O padrão que define como um endereço é partido é a [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), e as funções estão na [documentação do `urllib.parse`](https://docs.python.org/pt-br/3/library/urllib.parse.html).

Olhar só o esquema, no entanto, deixa passar duas classes de endereços quebrados, e convém vê-las. A primeira é um endereço sem servidor: `https://` sozinho, ou `http:catalogo` (sem as duas barras), têm o esquema correto, mas nenhum servidor para chamar. A segunda é pior: há endereços que o `urlsplit` nem sequer consegue partir. Com `http://[::1` (um colchete que abre e não fecha) o `urlsplit` não devolve nada: **lança** `ValueError: Invalid IPv6 URL`. E com `http://127.0.0.1:abc/`, o endereço é partido, mas ao pedir a porta (`.port`, o número que vem depois dos dois-pontos) sai `ValueError: Port could not be cast to integer value as 'abc'`. Se a validação não capturar esse `ValueError`, um arquivo de configuração mal escrito derruba o programa com um *traceback* em vez da mensagem clara que prometemos. A [documentação do `urllib.parse`](https://docs.python.org/pt-br/3/library/urllib.parse.html#urllib.parse.urlsplit) avisa: o `urlsplit` não valida, e colchetes sem par lançam `ValueError`.

Há uma terceira classe, mais escondida. No TOML, dentro de um texto entre aspas, `\n` é uma quebra de linha, de modo que `url = "http://127.0.0.1:8099/cata\nlogo"` chega ao Python com uma quebra de linha no meio. O `urlsplit` **a remove em silêncio** (a sua documentação diz isso: elimina as quebras de linha e as tabulações, como fazem os navegadores) e o endereço parece bom; mas a biblioteca que fará a requisição na lição 9, o `httpx`, a vê sim e a rejeita com um erro próprio, que não é um erro de rede. Algo parecido pode acontecer com letras que não são do inglês no nome do servidor, que o `httpx` precisa converter para uma forma especial e às vezes não consegue. A defesa simples é não aceitar, no arquivo de configuração, nada que não seja texto comum.

Por isso o `revisor` não pergunta diretamente pelo esquema, e sim com uma função pequena que reúne todas as perguntas:

```python
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
```

Lê-se de cima para baixo. O primeiro `if` descarta o que não é texto comum, com três métodos dos textos: `isascii()` é `True` se todos os caracteres são ASCII (as letras do inglês, os dígitos e os sinais de um teclado básico; um `é` já não é); `isprintable()` é `True` se nenhum é um caractere de controle, como a quebra de linha; e `" " in url` pergunta se há algum espaço. Se qualquer uma das três falha, o `revisor` não aceita o endereço. Atenção: isso não quer dizer que ele seja inválido na internet; `https://catálogo.example` é um endereço legítimo. É uma regra do `revisor`, mais estrita que a dos navegadores: na sua configuração, um nome assim se escreve na sua forma ASCII, a que começa com `xn--`. Depois, tudo vai dentro de um `try` porque tanto partir o endereço quanto ler a porta podem lançar `ValueError`, e para esta função esse erro tem uma única resposta: o endereço não serve, `False`. Lá dentro, três condições unidas com `and`: o esquema é um dos dois permitidos; `partes.hostname`, o nome do servidor, existe (em `https://` sozinho vale `None`); e a porta, se houver, é um número maior que 0. As três vão entre parênteses para poder distribuí-las em várias linhas. Um detalhe do `and` que aqui importa: ele avalia da esquerda para a direita e **para na primeira condição falsa**, de modo que a porta só é lida se as duas primeiras já foram cumpridas. Com isso, os seis endereços de `fig06_16.py` dão o mesmo resultado de antes, e todos os quebrados destes parágrafos saem `False`. O que esta validação não verifica é se o servidor existe ou responde: isso só se sabe ao consultá-lo, e é o trabalho do `revisor` a partir da lição 9. Também não garante que o `httpx` aceite tudo o que passa: `http://999.1.1.1:8099/pagos` tem esquema, servidor e porta, mas 999 não cabe em um endereço IP (cada parte vai de 0 a 255), e o `httpx` o rejeita. Por isso a lição 9, além de explicar por que `file://` é um risco concreto quando se usa o `urllib`, coloca uma segunda rede de proteção ao consultar: um endereço que o `httpx` não pode usar aparece no relatório como “dirección inválida” (endereço inválido), sem derrubar os demais.

#### 6.4.4 Por que não `eval` nem `pickle`

Com o vocabulário desta lição já se pode explicar algo que se vê em muitos programas de iniciantes e é um risco sério. Alguém pensa: “para ler uma lista de serviços não preciso de um formato; escrevo a lista como código Python em um arquivo, e o programa a executa”. Existe uma função que permite isso: `eval(texto)`, que pega um texto, o interpreta **como código** e devolve o seu resultado. Veja `fig06_17.py`, uma demonstração do que **não** se faz:

```python
# fig06_17.py
# DEMOSTRACIÓN de lo que NO se hace: eval con un texto que viene de fuera.
print(eval("2300 + 1"))

texto_de_fuera = "print('esto lo escribió otro y se ejecutó')"
eval(texto_de_fuera)
```

```text
$ python fig06_17.py
2301
esto lo escribió otro y se ejecutó
```

A primeira chamada parece inocente: `eval("2300 + 1")` calcula e devolve `2301`. A segunda mostra o problema: o texto que chegou de fora era uma **instrução**, e o `eval` a executou. Aqui foi um `print` inofensivo; poderia ter sido qualquer coisa que o Python saiba fazer: apagar arquivos, ler senhas, abrir uma conexão com outro computador. Quem controla o texto controla o programa. A [documentação do `eval`](https://docs.python.org/pt-br/3/library/functions.html#eval) diz isso sem rodeios: ele executa código arbitrário e restringir as funções que ele pode usar não é um mecanismo de segurança. Há uma variante mais cuidadosa, `ast.literal_eval`, que aceita apenas valores literais (números, textos, listas), mas a [documentação do módulo `ast`](https://docs.python.org/pt-br/3/library/ast.html#ast.literal_eval) avisa que também não é adequada para entradas não confiáveis: um texto muito grande ou muito aninhado pode esgotar a memória ou a pilha do Python.

O outro caso é o `pickle`, o módulo que guarda objetos do Python em um arquivo e os reconstrói depois. É cômodo, porque não é preciso montar um formato: guarda-se o objeto e recupera-se. Mas reconstruir um objeto pode executar código, e por isso a [documentação do `pickle`](https://docs.python.org/pt-br/3/library/pickle.html) abre com um aviso em destaque: **nunca carregue dados de uma fonte que não seja confiável**, porque um arquivo feito de propósito pode executar o que o seu autor quiser no seu computador. Nem sequer se mostra aqui como se faz, porque este curso não o usa. Essa classe de falha tem nome no catálogo de fraquezas de software: [CWE-502, desserialização de dados não confiáveis](https://cwe.mitre.org/data/definitions/502.html). A solução é a que você já tem: **os dados de fora se leem com formatos que só descrevem dados**. TOML e JSON descrevem valores, não instruções; por mais que alguém se esforce ao escrevê-los, `tomllib.loads` e `json.loads` só podem devolver dicionários, listas, textos, números e booleanos (mais `None` no JSON, e datas e horas no TOML, que o `tomllib` devolve como valores do módulo `datetime`). Nenhum desses tipos executa nada. Por isso o `revisor` os usa.

Que não executem nada não quer dizer que não possam causar dano de outra maneira. As documentações do [`tomllib`](https://docs.python.org/pt-br/3/library/tomllib.html) e do [`json`](https://docs.python.org/pt-br/3/library/json.html) trazem o mesmo aviso: um texto feito com má intenção (enorme, ou aninhado em milhares de níveis) pode fazer a leitura consumir muito processador e muita memória, e recomendam **limitar o tamanho** do que se lê. O `revisor` não faz isso, e é uma decisão consciente: lê um arquivo de configuração escrito por quem o usa, de umas poucas centenas de bytes. Mas se um programa seu recebe TOML ou JSON de outras pessoas (pela rede, de um formulário), o primeiro passo é verificar o tamanho antes de lê-lo, por exemplo com `ruta.stat().st_size`, que diz quantos bytes mede um arquivo, e rejeitar o que passar de um limite razoável.

Se você quiser seguir com a parte de segurança dos sistemas que expõem serviços, o blog da Hábil tem um artigo sobre [segurança de APIs: identidade, gateway e tokens](https://www.habil.mx/pt/blog/seguranca-de-apis-cto-identidade-gateway-tokens/). E se você tem interesse em ver como outra linguagem resolve este mesmo problema dos dados de fora com o mesmo `revisor`, o [curso de TypeScript](https://www.habil.mx/pt/cursos/typescript/) tem uma lição inteira para isso.

#### 6.4.5 O passo do projeto: o `revisor` lê a sua configuração

Você tem todas as peças. Falta montá-las. O `revisor` desta lição fica assim, na sua pasta `~/curso-python/revisor/`:

```text
revisor/
  servicios.toml      ← NUEVO: los datos, ahora fuera del código
  configuracion.py    ← NUEVO: lee, valida y traduce los errores
  formato.py          ← tiene una función más: reporte_a_json
  revisor.py          ← ya no tiene SERVICIOS escrito a mano
  modelo.py  revision.py   (sin cambios)
```

Comece pelos dados. Este é o arquivo `servicios.toml`, com os mesmos quatro serviços de sempre; é o que substitui a lista que você tinha no código:

```toml fig06_18/servicios.toml
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

Agora o módulo novo, `configuracion.py`. É o mais longo da lição, mas cada parte você já conhece. Leia-o completo uma vez, e depois ele é desmontado:

```python
# fig06_18/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from modelo import Servicio, nombres_repetidos


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


def tiene_credenciales(url: str) -> bool:
    partes = urlsplit(url)
    return partes.username is not None or partes.password is not None


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
    if tiene_credenciales(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' no debe llevar usuario ni clave"
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

A função `leer_servicios` recebe um caminho e devolve a lista de `Servicio`. Ela segue em quatro passos, e em cada um a regra é a mesma: **traduzir para o domínio da configuração todo erro que possa ter causa no arquivo**.

1. **Ler o texto.** `ruta.read_text(encoding="utf-8")` está dentro de um `try` com um único `except`, e é para `FileNotFoundError`. Esse é o único erro de leitura que sabe se explicar bem (“o arquivo não existe”), então é o único que se captura. Se o arquivo existe mas você não tem permissão para lê-lo, o erro é um `PermissionError`, e **ela não o captura**: a função não tem nada útil a dizer sobre isso, e é melhor que o programa pare com o relatório do sistema. (O exercício 4 pede que você amplie isso com outro erro, o da codificação.)
2. **Interpretar o TOML.** `tomllib.loads` vai no seu próprio `try` com o seu próprio `except`: se houver `TOMLDecodeError`, a mensagem do `tomllib` é incluída na nossa. Faz-se `raise ... from error` nos dois casos, pela razão de 6.1.4.
3. **Verificar a forma geral.** `datos.get("servicios")` busca a lista; se não for uma lista, ou estiver vazia, avisa-se que ela falta. Este passo protege contra um TOML que é válido mas não é o nosso.
4. **Verificar cada serviço.** Uma lista por compreensão (lição 4) chama `validar_servicio` para cada elemento, com a sua posição. A função `enumerate(lista, start=1)`, que você viu na lição 3, entrega a posição de cada elemento junto com o elemento; o parâmetro `start=1` faz a contagem começar em **1** em vez de 0, porque “o serviço 2” é a forma como uma pessoa fala. No fim, `nombres_repetidos` (lição 5) devolve o conjunto de nomes que aparecem mais de uma vez. Se não estiver vazio (`len(repetidos) > 0`, a mesma pergunta pelo tamanho que você já usou com as listas), avisa-se; `sorted(repetidos)` os coloca em ordem alfabética e `", ".join(...)` os une em um único texto separado por vírgulas (`join`, “juntar”, é um método dos textos que junta os elementos de uma lista usando esse texto como separador).

A função `validar_servicio` recebe `datos: object`, o tipo mais geral que existe, de propósito: **ela não sabe o que é**, porque vem de fora. A primeira coisa é verificar com `isinstance(datos, dict)` que seja um dicionário. Depois ela confere campo por campo, nesta ordem, e para no primeiro problema:

- o `nombre` deve existir e ser um texto que não esteja vazio (`nombre.strip() == ""` pega o texto que só tem espaços);
- a `url` deve existir e passar por `es_url_http`: esquema permitido, um servidor e, se tiver, uma porta válida (6.4.3), e além disso não deve levar usuário nem senha (`tiene_credenciales`): um endereço como `http://usuario:clave@...` traz um segredo, e o `revisor` não deve guardá-lo nem repeti-lo;
- `timeout_ms`, que é opcional, só é conferido se estiver presente (`"timeout_ms" not in datos`; o operador `in` pergunta se uma chave está no dicionário), e deve ser um inteiro maior que 0 que **não** seja `bool` (6.4.2).

Se tudo está bem, devolve um `Servicio`. Se não há `timeout_ms`, ela não o passa: o valor padrão de 5000 é posto pela definição de `Servicio`, que vem da lição 5. Cada mensagem de erro começa com `servicio N:` para que quem edita o arquivo saiba **qual** elemento revisar. As mensagens que o módulo produz são estas, com a posição contando a partir de 1:

| Caso | Mensagem |
|---|---|
| o arquivo não existe | `no existe el archivo servicios.toml` |
| TOML mal escrito | `servicios.toml no es TOML válido: <mensaje de tomllib>` |
| falta a lista | `falta la lista [[servicios]]` |
| falta um campo | `servicio 2: falta 'nombre'` |
| o serviço não é uma tabela | `servicio 2: debe ser una tabla` |
| nome vazio ou que não é texto | `servicio 2: 'nombre' debe ser un texto que no esté vacío` |
| url que não é um endereço http/https válido | `servicio 2: 'url' debe ser una dirección http:// o https:// válida` |
| url com usuário ou senha | `servicio 2: 'url' no debe llevar usuario ni clave` |
| tempo limite inválido | `servicio 3: 'timeout_ms' debe ser un entero mayor que 0` |
| nomes repetidos | `nombres repetidos: catalogo` |

O arquivo `formato.py` ganhou duas funções. Não mudou nenhuma das anteriores (`formatear_tiempo`, `encabezado`, `linea`, `contar`, `resumen`); só foram acrescentados `import json` e `from urllib.parse import urlsplit, urlunsplit` no começo e estas duas funções no final:

```python
def url_sin_secretos(url: str) -> str:
    partes = urlsplit(url)
    servidor = partes.netloc.rpartition("@")[2]
    return urlunsplit((partes.scheme, servidor, partes.path, "", ""))


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": url_sin_secretos(r.servicio.url),
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

É a aplicação direta de 6.3.3: monta-se um dicionário com tipos que o JSON entende (por isso `r.estado.value` e não `r.estado`), e serializa-se com `ensure_ascii=False, indent=2`. A média sai como `None` (que o JSON escreve `null`) quando nenhum serviço respondeu, porque não se pode tirar a média de nada. Repare também numa repetição que se deixa de propósito: as contas de `resumen` e as deste dicionário são as mesmas, calculadas duas vezes. Fez-se assim para não mexer no que já funciona na lição 5, mas é o mesmo problema com que esta lição começou, o de um dado calculado em dois lugares: se algum dia a regra da média mudar, será preciso mudá-la nos dois. Anote isso no seu diário de bordo: é o tipo de dívida que se paga na próxima vez que o relatório for tocado.

`url_sin_secretos` existe porque o relatório sai do seu programa: é salvo em um arquivo, colado em um chat, lido por outro programa. Se o endereço traz um segredo na consulta (`?token=...`) ou algo no fragmento (`#...`), o relatório não deve repeti-lo. `urlsplit` divide o endereço (6.4.3); `partes.netloc.rpartition("@")[2]` fica com o que vem depois do último `@`, isto é, o servidor e a porta sem usuário nem senha (`rpartition` divide o texto em três na última ocorrência do separador, e `[2]` é a parte da direita; se não houver `@`, é o texto inteiro); e `urlunsplit` volta a montar o endereço com o esquema, o servidor e o caminho, e com a consulta e o fragmento vazios. Assim, `http://127.0.0.1:1/estado?token=SECRETO#x` sai no relatório como `http://127.0.0.1:1/estado`. Um endereço com usuário ou senha nem chega aqui, porque `validar_servicio` o rejeita ao carregar; tirá-los também aqui é uma segunda rede. O endereço é redigido em vez de tirar o campo porque o JSON é um contrato (você verá isso depois da execução): quem o lê conta com que cada serviço traga sua `url`, e sem os segredos continua sabendo a que servidor e a que caminho cada entrada se refere.

Falta o programa principal. Assim fica o `revisor.py`, que perdeu a lista de serviços e ganhou uma constante com o caminho do arquivo:

```python
# fig06_18/revisor.py
from pathlib import Path

from configuracion import ErrorDeConfiguracion, leer_servicios
from formato import encabezado, linea, resumen
from revision import revisar_todos

RUTA_CONFIG = Path("servicios.toml")


def main() -> None:
    try:
        servicios = leer_servicios(RUTA_CONFIG)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        return

    resultados = revisar_todos(servicios)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

`RUTA_CONFIG = Path("servicios.toml")` é uma constante (maiúsculas, como `UMBRAL_LENTO_MS`) com o caminho relativo. Em `main`, a chamada a `leer_servicios` está dentro de um `try` que captura **somente** `ErrorDeConfiguracion`: é a exceção própria de 6.1.4, o único erro que este programa sabe explicar. Se ocorre, imprime `error de configuración: ` seguido da mensagem, e `return` encerra `main` sem seguir adiante. Qualquer outro erro (um `ZeroDivisionError` por um defeito, por exemplo) não é capturado, e para com o seu relatório para que alguém o corrija.

Atenção a uma consequência: quando avisa de um erro de configuração, o programa termina **com código de saída 0**, o que no terminal significa “tudo certo”. Para uma pessoa que lê a tela não importa; para outro programa que o chame e só olhe o código, parece um sucesso. É uma dívida que esta lição deixa de propósito, para não misturar assuntos: na [Lição 7](07-paquete-linea-de-comandos.md) esse ramo terminará com o código 2; aqui só se imprime. Execute:

```text
$ cd fig06_18
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

É o mesmo relatório da lição 5, com a mesma tabela e o mesmo resumo (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`), mas agora os quatro serviços vêm de `servicios.toml`. Se você adicionar um serviço ao arquivo, ele aparece na tabela sem tocar no Python (você verá um caso no exercício 1).

Para ver o JSON do relatório, o projeto traz um script de apoio, `ver_json.py`. Não faz parte do programa: apenas une a leitura da configuração, a verificação e `reporte_a_json`, para que você veja o resultado antes de existir, na lição 7, uma opção de linha de comando para pedi-lo:

```python
# fig06_18/ver_json.py
from configuracion import leer_servicios
from formato import reporte_a_json
from revision import revisar_todos
from revisor import RUTA_CONFIG

servicios = leer_servicios(RUTA_CONFIG)
print(reporte_a_json(revisar_todos(servicios)))
```

```text
$ python ver_json.py
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
```

É o JSON que o curso fixa para o relatório do `revisor`, e não muda nas lições seguintes: `servicios` é uma lista com uma entrada por serviço, `tiempo_ms` é `null` para o que não respondeu, e `resumen` repete as contas. Quem consumir esse relatório a partir de outro programa pode se apoiar nessa forma. A única coisa que o relatório muda no endereço é tirar os segredos: os quatro serviços de `servicios.toml` não trazem nenhum, e por isso sua `url` sai igual à do arquivo.

## O erro que você vai ver

A lição tem um erro principal, o do arquivo que não está onde você acha, e quatro mensagens de apoio que você já viu e que convém saber ler de relance.

**O erro principal.** Execute o `revisor` a partir da pasta **de cima**, a que contém `fig06_18`, em vez de entrar nela:

```text
$ python fig06_18/revisor.py
error de configuración: no existe el archivo servicios.toml
```

O programa encontra o código (você deu o caminho), mas `RUTA_CONFIG` é **relativa**: `Path("servicios.toml")` significa “o `servicios.toml` da pasta onde estou parado”, não “o que está junto do programa”. Da pasta de cima, esse arquivo não existe. Repare no que o programa fez bem: não mostrou um relatório de erro nem a exceção `FileNotFoundError` em inglês com o texto do sistema; mostrou a mensagem em espanhol que você escreveu, que diz o que falta. E é o mesmo erro que você verá qualquer dia, quando um script funcionar no seu computador e falhar em outro: nove em cada dez vezes o arquivo existe, mas **a pasta de onde ele é executado é outra**. Para saber em que pasta você está, o comando `pwd` diz. Na lição 7, `--config` deixará você indicar o caminho sem depender de onde você esteja.

**As quatro mensagens de apoio**, para ler de baixo para cima:

- `ValueError: invalid literal for int() with base 10: '142 ms'`: um texto que se quis converter em inteiro e não são só dígitos (`fig06_01.py`). Verifique que texto chegou.
- `FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'`: o caminho não aponta para nada. Verifique a pasta de trabalho e a ortografia (`fig06_08.py`).
- `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10`: o arquivo não está em UTF-8, e o byte que o Python menciona diz em que posição deixou de bater (`fig06_10.py`).
- `TypeError: Object of type Estado is not JSON serializable`: você tentou serializar um objeto próprio sem convertê-lo para tipos simples. Monte um dicionário com `.value`.

## O que se faz errado

**Escrever `except:` sem tipo, ou `except Exception:` por via das dúvidas.** Você já viu o custo em 6.1.3: um erro de ortografia se disfarça de outro erro; e com o `except:` puro, além disso, o programa pode não parar nem com `Ctrl`+`C`. A exceção concreta, sempre.

**Engolir o erro em silêncio.** Um `except ValueError: pass` (“não faça nada”) faz o programa seguir com dados que não existem. O tempo de `inventario` fica sem ser lido, o relatório sai com uma linha errada, e ninguém sabe por quê. Se você captura uma exceção, **faça algo com ela**: avise, traduza, devolva um valor definido. Se você não sabe o que fazer, não a capture.

**Um `try` enorme.** Colocar vinte linhas em um `try` para “proteger tudo” faz o `except` capturar erros que você não esperava, de linhas que não têm a ver, como em `fig06_03.py`. O `try` contém a linha que pode falhar da maneira que você conhece, e nada mais.

**Traduzir uma exceção sem `from`.** O relatório continua mostrando a original, mas já não como causa: fica “durante o tratamento da exceção anterior, ocorreu outra”, o que é pior para quem depura. Se você troca um erro por outro, `raise ... from error`.

**Abrir arquivos sem `with`.** Um `archivo = open(...)` sem o seu `close()` deixa o arquivo aberto se algo falhar antes de fechá-lo, e não se nota até o programa abrir centenas.

**Omitir `encoding="utf-8"`.** Funciona no seu computador e falha (ou, pior, lê mal os acentos) em outro. Escreva-o sempre.

**Juntar caminhos com `+` ou com `"/"` dentro de um texto.** Quebra assim que o sistema operacional muda ou sobra uma barra. Com `Path` e o operador `/` não é preciso pensar nisso.

**Validar com verdadeiro ou falso.** `if timeout_ms:` deixa passar `True` e, pior, **rejeita o `0`** com o mesmo gesto com que rejeita o vazio, sem distinguir os casos. Pergunte exatamente o que você quer saber: `isinstance(timeout_ms, int)` e `timeout_ms > 0`.

**Validar com `assert`.** A instrução `assert condicion` falha se a condição é falsa, e parece uma forma cômoda de validar. Mas o Python pode ser executado em um modo de otimização (`python -O`) no qual **todos os `assert` são ignorados**, segundo a [referência da instrução](https://docs.python.org/pt-br/3/reference/simple_stmts.html#assert). Uma validação que desaparece quando alguém otimiza o programa não valida nada. Os `assert` são para os testes, que você verá na lição 8; para os dados de fora se usa `if` e `raise`.

**Passar um dado de fora para `eval` ou `pickle`.** É deixar que o autor do arquivo decida o que o seu programa faz. Usa-se TOML ou JSON.

## Exercícios

### Exercício 1 — Adicione serviços sem tocar no código

Adicione ao seu `servicios.toml` os dois serviços extras do curso: `facturacion` (`https://facturacion.example`) e `notificaciones` (`https://notificaciones.example`, com `timeout_ms = 1000`). Como `revisar` continua usando dados simulados, adicione também a entrada deles em `SIMULADO` de `revision.py`, como no exercício 1 da lição 5: `facturacion` responde 503 em 95 ms, e `notificaciones` não responde (`tiempo agotado`, “tempo esgotado”). Antes de executar, **preveja** o resumo: quantos serviços há, quantos no ar, lentos e fora do ar, e qual é a média. Depois execute e compare. Você nota algo estranho na tabela?

### Exercício 2 — Um arquivo quebrado para cada erro

Crie uma cópia do seu `servicios.toml` chamada `roto.toml` e, mudando `RUTA_CONFIG` para `Path("roto.toml")`, escreva nela, um por um, arquivos que provoquem cada uma destas mensagens: (a) falta a lista `[[servicios]]`; (b) TOML mal escrito (esqueça uma aspa); (c) um serviço sem `nombre` na segunda posição; (d) um serviço com a url `ftp://archivos.example`; (e) `timeout_ms = 0` no terceiro serviço; (f) dois serviços com o nome `catalogo`. **Para cada um, escreva primeiro a mensagem que você espera** e compare depois com o que o `revisor` imprime. Anote no diário de bordo os que você não acertou.

### Exercício 3 — A armadilha do `bool`, ao vivo

Escreva um `roto.toml` com um único serviço que tenha `timeout_ms = true`. Execute o `revisor` e anote a mensagem. Agora mude, **temporariamente**, a validação de `timeout_ms` em `configuracion.py` para a versão ingênua (`not isinstance(timeout_ms, int) or timeout_ms <= 0`, sem a parte do `bool`) e execute de novo. O que acontece? Quem avisa? Restaure a versão correta e explique com suas palavras por que a ingênua deixa passar `true`.

### Exercício 4 — Um erro que a lista não tem

O `revisor` converte `FileNotFoundError` e `TOMLDecodeError` em `ErrorDeConfiguracion`, mas não `UnicodeDecodeError`. Provoque-o com um `servicios.toml` salvo em `latin-1`, outra codificação, sem perder o seu. Da pasta do projeto: (1) guarde uma cópia de segurança com `cp servicios.toml servicios-bien.toml` (`cp` copia um arquivo; se o destino já existe, ele o substitui sem perguntar, então escolha um nome que você não use); (2) faça outra cópia, `cp servicios.toml acento.toml`, e em `acento.toml`, logo abaixo da `url` do primeiro serviço, adicione a linha `descripcion = "catálogo de productos"`; (3) converta essa cópia para `latin-1` e escreva-a como `servicios.toml`: `iconv -f utf-8 -t latin1 acento.toml > servicios.toml` (`iconv` muda a codificação de um texto, e `>` escreve a sua saída no arquivo, **apagando antes o que ele tivesse**: por isso o passo 1). Execute o `revisor` e leia o relatório de baixo para cima. Depois amplie `leer_servicios` para que esse erro também se converta em `ErrorDeConfiguracion`, com uma mensagem que diga o que aconteceu, e execute o `revisor` de novo com o mesmo `servicios.toml` em `latin-1` para ver a sua mensagem em vez do *traceback*. Essa mensagem não está na tabela do projeto: é uma ampliação de prática, e o projeto das lições seguintes não a inclui. Só no final, quando você já viu a sua mensagem, restaure a sua configuração com `cp servicios-bien.toml servicios.toml`.

## Soluções

### Solução 1

Os dois serviços novos em `servicios.toml`, no final do arquivo:

```toml
[[servicios]]
nombre = "facturacion"
url = "https://facturacion.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
```

E as duas entradas novas de `SIMULADO` em `revision.py`, depois da de `reportes`:

```python
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
```

**Previsão.** Seis serviços. `catalogo` e `pagos` continuam no ar (2). `inventario` continua lento (1). `reportes` e `notificaciones` não responderam, e `facturacion` respondeu com 503, que a regra de classificação (um código maior ou igual a 400) marca como fora do ar: são 3 fora do ar. A média é calculada **somente com os que responderam**: `catalogo` (142), `inventario` (2300), `pagos` (87) e `facturacion` (95), que respondeu, ainda que com erro; a soma é 2624 e, dividida por 4, dá 656. Resultado esperado: `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`.

**Resultado.** Ao executar `python revisor.py`, sai:

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

A previsão coincide com o resumo. **O estranho** está na tabela: `notificaciones` tem 14 letras, e a coluna do nome tem uma largura fixa de 12 (`{nombre:<12}`), então o nome invade a coluna seguinte e gruda em “CAIDO”. `facturacion` cabe por pouco: tem 11 letras, e sobra um único espaço. Não é um erro desta lição: o formato foi escrito para os quatro nomes canônicos. A [Lição 11](11-el-programa-terminado.md) resolve isso calculando a largura a partir do nome mais longo. O importante neste exercício é outra coisa: você adicionou dois serviços **sem mudar uma linha de lógica**, que era o objetivo da lição.

### Solução 2

Cada arquivo quebrado e a mensagem que ele produz. Em (b) o nome do arquivo aparece na mensagem porque `leer_servicios` usa o caminho que recebe; se você testar com `servicios.toml`, dirá `servicios.toml`.

(a) Um arquivo sem a lista:

```toml
titulo = "nada"
```

Mensagem: `error de configuración: falta la lista [[servicios]]`

(b) Uma aspa de fechamento esquecida:

```toml
[[servicios]]
nombre = "catalogo
```

Mensagem: `error de configuración: roto.toml no es TOML válido: Illegal character '\n' (at line 2, column 19)`

(c) O segundo serviço não tem nome:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
url = "https://pagos.example"
```

Mensagem: `error de configuración: servicio 2: falta 'nombre'`

(d) Um endereço que não é web, no segundo serviço:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "archivos"
url = "ftp://archivos.example"
```

Mensagem: `error de configuración: servicio 2: 'url' debe ser una dirección http:// o https:// válida`

(e) Um tempo limite em zero, no terceiro serviço:

```toml
[[servicios]]
nombre = "a"
url = "https://a.example"

[[servicios]]
nombre = "b"
url = "https://b.example"

[[servicios]]
nombre = "c"
url = "https://c.example"
timeout_ms = 0
```

Mensagem: `error de configuración: servicio 3: 'timeout_ms' debe ser un entero mayor que 0`

(f) Dois serviços com o mesmo nome:

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "catalogo"
url = "https://otro.example"
```

Mensagem: `error de configuración: nombres repetidos: catalogo`

Três detalhes para depois de comparar. O erro do TOML (b) é o único cujo texto você não escreveu: vem do `tomllib` e traz a linha e a coluna. Em (a) a lista não falta pela metade: não há nada, e a mensagem diz exatamente isso. E em (f) o erro é detectado **depois** de validar cada serviço separadamente, porque seus nomes são válidos um a um; o defeito é da lista inteira. As mensagens foram obtidas executando cada arquivo com o módulo desta lição.

### Solução 3

Com a validação correta, a mensagem é a de sempre: `error de configuración: servicio 1: 'timeout_ms' debe ser un entero mayor que 0`.

Com a versão ingênua o `revisor` **não reclama**: imprime a sua tabela normal, e o resumo sai sem problema. O `Servicio` ficou com `timeout_ms=True`, e como `True` é o número 1, o tempo limite que o programa acredita ter é de um milissegundo. Ninguém avisa: é um erro que não faz barulho, e vai aparecer na lição 9, quando o `revisor` usar esse tempo limite: com um milissegundo de espera, quase qualquer requisição real se esgotaria, e o serviço sairia fora do ar por “tiempo agotado” sem motivo aparente. Isso acontece porque, em Python, `bool` é um tipo de inteiro (`isinstance(True, int)` é `True`), e a validação ingênua só pergunta isso. A versão correta acrescenta `isinstance(timeout_ms, bool)` para rejeitar os booleanos explicitamente.

### Solução 4

Ao executar com o arquivo em `latin-1`, a última linha do relatório é:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 85: invalid continuation byte
```

O byte `0xe1` é o “á” de “catálogo” em `latin-1`; a posição 85 é onde ele cai no arquivo, contando os bytes a partir de 0: é a que sai se você pôs a linha onde diz o exercício, e será outra se a pôs em outro lugar. As linhas de cima passam por `read_text` e pela biblioteca padrão: o erro nasce dentro da leitura, não no seu código, e você o vê subir pelas suas funções. Para convertê-lo, acrescenta-se um segundo `except` no primeiro passo de `leer_servicios`:

```python
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error
    except UnicodeDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no está guardado en UTF-8") from error
```

Com isso, o `revisor` imprime `error de configuración: servicios.toml no está guardado en UTF-8`. Observe que `UnicodeDecodeError` é um tipo de `ValueError`, mas não é preciso capturar `ValueError`: com o tipo concreto, um `ValueError` de outra causa não se disfarça.

## Como sei que consegui

- [ ] `python fig06_01.py` termina com o relatório do `ValueError`, e você consegue dizer qual função chamou qual, de baixo para cima, sem olhar a lição.
- [ ] `python fig06_03.py` diz que “142” não é um número, e você consegue explicar por que isso é uma mentira e qual linha do programa tem o erro de verdade.
- [ ] Em `fig06_05.py` você vê a frase “The above exception was the direct cause of the following exception”, e sabe qual instrução do código a produziu.
- [ ] De dentro de `fig06_18/`, `python revisor.py` imprime a tabela de quatro serviços com o resumo `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Da pasta de cima, `python fig06_18/revisor.py` imprime `error de configuración: no existe el archivo servicios.toml`, e você sabe explicar por quê.
- [ ] Os seis arquivos quebrados do exercício 2 produzem as seis mensagens da tabela, e você as previu antes de executar.
- [ ] `python ver_json.py` imprime um JSON com `null` no `tiempo_ms` de `reportes` e com `"promedio_ms": 843`.
- [ ] Você consegue explicar por que `isinstance(True, int)` é `True` e qual validação do `revisor` leva isso em conta.
- [ ] Você anotou no seu diário de bordo qual erro desta lição foi difícil de ler.

## Resumo

Responda sem olhar a lição:

1. De que lado se lê o relatório de um erro, e o que diz a sua última linha?
2. Que diferença há entre o `else` e o `finally` de um `try`? Qual dos dois é executado mesmo que haja um `return`?
3. Por que não se escreve `except:` sem tipo, nem `except Exception:` por via das dúvidas? O que acontece com o erro que você não sabe tratar?
4. O que faz `raise ... from error`, e o que acontece no relatório se você o omite?
5. O que um `with` garante? Por que se escreve `encoding="utf-8"` sempre?
6. O que `tomllib.loads` devolve? Que diferença há entre `datos["servicios"]` e `datos.get("servicios")` se a chave não existe?
7. Que três coisas diferenciam `json.dumps(x)` de `json.dumps(x, ensure_ascii=False, indent=2)`? Por que `json.dumps(Estado.CAIDO)` falha?
8. Por que `isinstance(True, int)` é `True`? Como se escreve a validação de um inteiro positivo que rejeita `true`?
9. Por que se valida o esquema de um endereço com uma lista do que é permitido e não com uma do que é proibido?
10. Que risco tem o `eval` com um texto que vem de fora, e que formato se usa no lugar dele?

## Para ler mais

- [Python, “Erros e exceções” (tutorial oficial)](https://docs.python.org/pt-br/3/tutorial/errors.html): `try`, `except`, `else`, `finally`, exceções próprias e encadeadas, com mais exemplos do que esta lição. Na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [Python, `tomllib`](https://docs.python.org/pt-br/3/library/tomllib.html) e [a especificação do TOML](https://toml.io/en/v1.0.0): o que o módulo lê e as regras do formato, incluindo as tabelas e as listas de tabelas. Consultado em 7 de outubro de 2026.
- [Python, `json`](https://docs.python.org/pt-br/3/library/json.html) e [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259): a biblioteca e a norma do formato. Consultado em 7 de outubro de 2026.
- [OWASP, “Input Validation Cheat Sheet”](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): por que se valida na fronteira e por que uma lista do que é permitido funciona melhor do que uma do que é proibido. Consultado em 7 de outubro de 2026.
