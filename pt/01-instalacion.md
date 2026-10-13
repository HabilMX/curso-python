# Lição 1 — Instalar o Python no seu Linux Mint

**Tempo:** 90 min

**O que você constrói:** o ambiente virtual do curso, o seu primeiro script (`hola.py`) e o arquivo onde viverá o `revisor`

**O que você aprende:** o `python3` do sistema e por que ele não instala pacotes (`No module named pip` e o aviso `externally-managed-environment`); criar, ativar e desativar um ambiente virtual (`venv`); o `pip` dentro do ambiente; o REPL e executar um arquivo; ler o primeiro *traceback*

**De onde você vem.** Da [Lição 0](00-que-es-python.md), que foi de leitura: você já sabe que o Python lê o seu arquivo, o traduz para *bytecode* e o executa; que os tipos são verificados ao rodar e não antes; que o GIL não vai atrapalhar você; e que existe algo chamado ambiente virtual que protege o Python do seu sistema. Hoje você deixa de ler e passa para o terminal. Você trabalha em um computador com **Linux Mint 22.x** (qualquer uma das suas versões, da 22 à 22.3, que compartilham a mesma base) e com um terminal aberto. Quase nada do que você fará exige permissões de administrador: no máximo uma linha (com dois comandos de administrador dentro), e só se o seu Mint não trouxer a peça que cria ambientes virtuais (você verá em 1.2.2). Mais ainda, uma das coisas que você aprenderá hoje é a **não** instalar pacotes de Python com essas permissões.

**O que esta lição não faz.** Não ensina ainda a linguagem: o `print` que você vai usar é explicado em uma linha e a [Lição 2](02-valores-texto-decisiones.md) o estuda a fundo. Também não instala o `uv` nem o `pipx`, outras ferramentas que você verá mais adiante: hoje se usa o que o sistema já traz, porque entender o ambiente com as peças básicas é o que depois permite entender por que as demais ferramentas existem.

## Ao terminar, você vai conseguir

- Conferir qual Python o seu Mint traz (`python3 --version`) e de onde ele roda (`which python3`).
- Tentar de propósito instalar um pacote no Python do sistema, ler a resposta e explicar por que o Mint protege o seu Python, como o aviso `externally-managed-environment` aparece nos sistemas que trazem `pip`, e qual é a saída correta.
- Criar o ambiente virtual do curso com `python3 -m venv`, ativá-lo, conferir com `which python` que você está dentro, instalar um pacote com `pip` e desativá-lo.
- Escrever uma expressão no REPL, sair dele e distinguir quando convém o REPL e quando convém um arquivo.
- Criar e executar `hola.py` e `revisor/revisor.py`, dentro e fora do ambiente, e anotar qual `python` foi usado em cada caso.
- Ler um *traceback* de `NameError` da última linha para cima e dizer qual palavra escrita errada o causou.

## O porquê antes do como

Para dar o primeiro passo com o `revisor` é preciso uma base firme: um Python que funcione, um lugar onde guardar os pacotes de que o curso vai precisar e uma pasta onde o projeto viverá. Se essa base é improvisada, os problemas aparecem mais tarde e na forma mais confusa possível: um pacote que “foi instalado”, mas não é encontrado, uma versão do Python que não é a que você pensava, um comando que funcionava ontem e hoje não. Esta lição existe para que isso não aconteça com você.

Pense em montar uma oficina antes de construir um móvel. Não é a parte emocionante, mas decide se o resto sai limpo. Na oficina do Python há três coisas a preparar. A **primeira** é saber qual Python você tem e de quem ele é: o seu Mint já traz um, e é dele, não seu. A **segunda** é criar o seu próprio espaço de trabalho, o ambiente virtual, onde você pode instalar e quebrar coisas sem consequências. A **terceira** é conferir que tudo funciona executando o menor programa possível.

Há mais uma razão para fazer bem agora, e é que **o tropeço que você vai ver hoje é o mesmo que terá em um trabalho real**. Quase todo mundo que instala Python em um Linux moderno se depara, cedo ou tarde, com um Python do sistema que se recusa a instalar pacotes: no seu Mint, porque ele nem sequer traz o `pip`; em outros sistemas, com uma mensagem que diz `externally-managed-environment`. Muita gente lê isso como um obstáculo, procura na internet como contorná-lo e acaba usando uma opção que quebra a proteção do sistema. Este curso faz o contrário: **provoca a recusa de propósito**, a lê linha por linha e mostra que é uma ajuda, não um muro. Quem entende isso uma vez o resolve em dez segundos pelo resto da vida.

### O mínimo do terminal de que você precisa hoje

O terminal é uma janela onde você escreve comandos em vez de clicar. No Mint ele se abre com o atalho `Ctrl + Alt + T`, ou procurando “Terminal” no menu. Neste curso, as linhas que começam com `$` são o que **você digita**, e as demais são o que o computador responde. O `$` em si não se digita: é o símbolo que o terminal mostra para indicar que está esperando um comando. Os comandos de hoje são poucos:

- `pwd` (*print working directory*): mostra em que pasta você está.
- `ls`: lista o que há na pasta atual.
- `cd pasta`: leva você para essa pasta. `cd ..` sobe um nível e `cd` sem nada leva você para a sua pasta pessoal.
- `mkdir pasta`: cria uma pasta.
- `which nome`: mostra **qual arquivo** seria executado se você digitasse esse nome. É a ferramenta que responde “qual Python estou usando?”.
- `~`: é um atalho para a sua pasta pessoal, a que contém os seus documentos. `~/curso-python` quer dizer “a pasta `curso-python` dentro da sua pasta pessoal”.

Se algum destes for novo para você, experimente agora no seu terminal antes de seguir: digite `pwd`, pressione Enter e compare com o que ele diz. Não quebra nada.

## Os conceitos

São quatro: o Python do sistema e o erro que ele protege; o ambiente virtual com o `pip`; o REPL e os arquivos; e o primeiro *traceback*. Cada um termina com algo que você pode conferir na sua tela.

### 1.1 O `python3` do sistema e o erro `externally-managed-environment`

#### 1.1.1 Qual Python você tem

Abra um terminal e digite:

```text
$ python3 --version
Python 3.12.3
```

A saída que você verá é da forma `Python 3.12.x`: o último número (o patch) depende das atualizações que o seu Mint recebeu. O que importa é o `3.12`. Essa é a versão com a qual o curso trabalha e, como você viu na lição anterior, todo o código roda também na 3.14. Se o seu terminal disser outra coisa (uma 3.10 ou uma 3.11), o curso quase com certeza funcionará igual, mas a 3.10 chegou ao fim da vida em 1º de outubro de 2026; anote isso no [diário de bordo](bitacora.md) e siga em frente.

Agora pergunte **de onde vem** esse Python:

```text
$ which python3
/usr/bin/python3
```

`/usr/bin/` é a pasta onde o sistema guarda os seus próprios programas. O seu `python3` estar ali significa que **é o do Mint**: foi instalado pela distribuição, é atualizado pelo gerenciador de pacotes (`apt`) e várias ferramentas do sistema dependem dele. É a “despensa da casa” da lição anterior.

Se você está em outro sistema (um macOS, ou um Linux com Python instalado de outra maneira), o `which` mostrará outro caminho. Não tem problema, mas o erro da próxima seção pode ser diferente ou não aparecer, e este curso foi escrito para o Mint.

#### 1.1.2 Tentar instalar algo, e o sistema dizer que não

O `pip` é a ferramenta do Python para instalar **pacotes**: bibliotecas de código que outras pessoas escreveram e publicaram em um catálogo público chamado **PyPI**, para que você não precise escrevê-las. O curso precisará mais adiante de um pacote chamado `httpx`, que serve para consultar serviços pela rede. Vamos tentar instalá-lo, **de propósito, da forma errada**: com o Python do sistema, fora de qualquer ambiente. Em um Linux Mint 22 recém-instalado, isto é o que acontece:

```text
$ python3 -m pip install httpx
/usr/bin/python3: No module named pip
```

O comando se lê: “execute o módulo `pip` com o Python (`-m` quer dizer *módulo*) e peça a ele que instale o `httpx`”. Escreve-se `python3 -m pip` e não só `pip` por uma razão que a [documentação do pip](https://pip.pypa.io/en/stable/getting-started/) explica: assim você garante que o `pip` executado é o **desse Python**, e não outro que exista no seu sistema.

A resposta se lê como qualquer relatório de erro, pelo final: `No module named pip`, “não há nenhum módulo chamado `pip`”. Antes dos dois-pontos vem quem fala: `/usr/bin/python3`, o Python do sistema. Não é uma falha sua nem do curso. Na família Debian e Ubuntu, de onde vem o Mint, o `pip` é um pacote à parte do sistema (`python3-pip`), e um Mint recém-instalado não o traz. Esse Python é administrado pelo gerenciador de pacotes do sistema, não por você. O resultado prático é o que importa: **fora de um ambiente não se instala nada**. Dentro do ambiente virtual, que você criará daqui a pouco, o `pip` vem incluído.

#### 1.1.3 O aviso que você verá se um dia instalar o `pip` do sistema

Há uma segunda proteção, mais explícita, e convém que você a reconheça porque é a que encontrará em quase qualquer Linux moderno em que haja `pip` no sistema (por exemplo, se um dia você instalar o pacote `python3-pip` do Mint, ou em outra distribuição). **Não a provoque**: não é preciso instalar nada para entendê-la. Ali, o mesmo comando não diz `No module named pip`, e sim uma mensagem que começa assim:

```text
error: externally-managed-environment
```

Isto é o que diz a especificação que o causa, a [PEP 668](https://peps.python.org/pep-0668/): as ferramentas de Python “não deveriam instalar nem remover pacotes no contexto global do interpretador, por padrão” (tradução nossa; a PEP só existe em inglês), quando esse interpretador é administrado por outro gerenciador de pacotes. O mecanismo é simples: a distribuição deixa um arquivo chamado `EXTERNALLY-MANAGED` na pasta da biblioteca padrão do seu Python, e o `pip` o procura antes de instalar. Se o encontra, ele para. Essa pasta pode ser perguntada ao Python:

```text
$ python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))"
```

Ele imprime o caminho da biblioteca padrão do seu Python, uma pasta cujo nome termina em `python3.12`; a especificação diz que é ali que vai o arquivo marcador.

Esse comando é uma receita para copiar tal qual; você não precisa entendê-lo inteiro hoje, mas sim saber o que faz cada pedaço. `-c` significa “execute este texto como programa”: é uma forma rápida de fazer uma pergunta avulsa ao Python sem criar um arquivo. O texto entre aspas são **duas instruções**, separadas pelo ponto e vírgula `;`, que em Python permite escrever duas instruções na mesma linha (nos arquivos do curso não se usa: cada instrução vai na sua linha). A primeira, `import sysconfig`, traz um **módulo**, um conjunto de ferramentas que vem com o Python e que não está disponível até que você o peça; a [Lição 3](03-bucles-funciones-modulos.md) explica o `import` a fundo. A segunda, `print(sysconfig.get_path('stdlib'))`, pede a esse módulo o caminho (*path*) da biblioteca padrão (*stdlib*) e o mostra com `print`.

A mensagem completa, além disso, **diz a você o que fazer**, e por isso é uma lição e não um muro. A especificação permite que a distribuição ponha o seu próprio texto de ajuda dentro do arquivo marcador, então o corpo muda de um sistema para outro; o habitual é que sugira três saídas: instalar o pacote com o gerenciador do sistema se houver versão empacotada, criar um ambiente virtual se não houver, ou usar o `pipx` se o que você quer instalar é uma aplicação e não uma biblioteca. Para o que o curso faz, a saída é a segunda: **um ambiente virtual**. Na seção “O erro que você vai ver” há um exemplo completo, lido por partes.

Há ainda uma quarta saída, e o `pip` mesmo a diz na nota com que encerra a mensagem: uma opção chamada `--break-system-packages`, que desativa a proteção e deixa instalar de qualquer jeito. A especificação admite que ela deve existir, e ela existe. **Este curso não a ensina nem a usa.** É o equivalente a tirar a fechadura porque você não achou a chave: funciona até que um pacote que você instalou pisa em uma biblioteca de que o sistema precisava, e então falham ferramentas que não têm nada a ver com o seu projeto. A chave existe e se chama ambiente virtual.

### 1.2 O ambiente virtual: criar, ativar, usar o `pip`, desativar

#### 1.2.1 Criar o ambiente

Primeiro a pasta do curso. Tudo o que você fizer viverá dentro de `~/curso-python/`:

```text
$ mkdir ~/curso-python
$ cd ~/curso-python
$ python3 -m venv .venv
```

A terceira linha é a que cria o ambiente. Lê-se: “execute o módulo `venv` com o `python3` e crie um ambiente em uma pasta chamada `.venv`”. O ponto no início do nome faz com que a pasta seja “oculta” por convenção: não aparece em um `ls` normal. É o nome habitual dos ambientes e algumas ferramentas o reconhecem sozinhas. Quando tudo dá certo, **não imprime nada**; no terminal, o silêncio é sucesso.

O ambiente vive em `~/curso-python/.venv`, **não** dentro da pasta do projeto `revisor/` que você criará mais abaixo. Há uma razão: a documentação do módulo [`venv`](https://docs.python.org/pt-br/3/library/venv.html) diz que um ambiente é considerado “descartável” (deve ser simples apagá-lo e recriá-lo do zero) e que “você não coloca nenhum código de projeto no ambiente”. Mantê-lo separado do código é a forma mais limpa de cumprir isso.

#### 1.2.2 Se o seu Mint não traz a peça dos ambientes

Em um Mint 22 recém-instalado, o mais provável é que a terceira linha **não** saia em silêncio, e sim com esta mensagem:

```text
$ python3 -m venv .venv
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /home/tu_usuario/curso-python/.venv/bin/python3
```

Leia por partes. A primeira frase diz o que aconteceu: o ambiente “não foi criado com sucesso” porque falta o `ensurepip`, a peça que põe o `pip` dentro de cada ambiente novo. A segunda diz por quê: nos sistemas da família Debian e Ubuntu, de onde vem o Mint, essa peça chega em um pacote à parte. A terceira dá a você o comando exato, `apt install python3.12-venv`, e a seguinte avisa de duas coisas: que talvez você precise de `sudo` e que, depois de instalar, é preciso **recriar** o ambiente. A última linha, `Failing command`, diz qual comando interno falhou; você não precisa fazer nada com ela.

Repare na palavra “recriar”, porque ela esconde uma armadilha. Embora a mensagem diga que o ambiente não foi criado, **a pasta `.venv` ficou sim no disco**, pela metade: tem `pyvenv.cfg`, as pastas `lib` e `include` e, dentro de `bin`, só os atalhos para o Python (`python`, `python3` e `python3.12`). Faltam duas coisas: o `pip` e o script `activate`. Por isso ainda não pode ser usado: `source .venv/bin/activate` responderia `No such file or directory` (“não existe esse arquivo”), uma mensagem que não menciona o ambiente e que desconcerta se você não sabe o que aconteceu.

A saída são dois comandos:

```text
$ sudo apt update && sudo apt install python3.12-venv
$ python3 -m venv .venv
```

- **`sudo apt update && sudo apt install python3.12-venv`.** O `apt` é o gerenciador de pacotes do sistema, o que instala e atualiza os programas do Mint. `sudo` significa “execute este comando com permissões de administrador”: instalar algo para todo o sistema as exige, então o terminal pedirá **a sua senha** (enquanto você a digita, nada aparece na tela, nem asteriscos; é normal). A linha são na verdade dois comandos unidos por `&&`, que quer dizer “e, se o primeiro deu certo, o segundo”. O primeiro, `apt update`, não instala nada: baixa a lista atualizada dos pacotes disponíveis, para que o segundo encontre a versão vigente (com uma lista velha, o `apt` pode não encontrar o pacote ou escolher uma versão que já não existe). O segundo instala o `python3.12-venv`; o `apt` avisará que instala **três** pacotes (`python3.12-venv` e dois dos quais ele depende: `python3-pip-whl`, que traz o `pip` que irá em cada ambiente, e `python3-setuptools-whl`, outra ferramenta de empacotamento que o curso não usa) e perguntará se você continua: responda `s` (ou `y`, se o seu Mint estiver em inglês) e Enter. Aqui você não instala um pacote de Python com o `pip`, e sim um programa do sistema que completa o Python do sistema, e por isso é assunto do `apt`. Fora desta linha, o curso só volta a usar `sudo` na [Lição 11](11-el-programa-terminado.md), para instalar o `pipx`, e é do mesmo tipo.
- **`python3 -m venv .venv`**, outra vez, sobre a mesma pasta. Agora sim deve sair em silêncio. Não é preciso apagar a pasta pela metade: o `venv` a reaproveita e completa o que faltava, o script `activate` e o `pip`.

Confira que desta vez o ambiente traz o seu `pip`, chamando-o pelo seu caminho (ainda sem ativar nada):

```text
$ .venv/bin/python -m pip --version
pip 24.0 from /home/tu_usuario/curso-python/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

`pip 24.0` é a versão que o Mint 22 põe nos ambientes novos; o que importa é que ele responda com uma versão e um caminho **dentro de `.venv`**, e não com `No module named pip`. Se a sua primeira execução de `python3 -m venv .venv` não imprimiu nada, nada desta seção diz respeito a você: o seu ambiente já estava completo.

Vejamos o que foi criado. Olhe dentro da pasta com `ls .venv`:

```text
$ ls .venv
bin  include  lib  lib64  pyvenv.cfg
```

Há cinco entradas, mas quatro coisas diferentes: `lib64` não é uma pasta a mais, e sim um atalho para `lib`, que o `venv` cria nos Linux de 64 bits para os programas que procuram as suas bibliotecas com esse nome. `bin` contém os programas do ambiente: o seu próprio `python`, o seu próprio `pip` e os scripts de ativação. `lib` é onde serão guardados os pacotes que você instalar. `include` guarda arquivos de apoio que este curso não usa. E `pyvenv.cfg` é um arquivo de texto pequeno que aponta para o Python com o qual o ambiente foi criado; a [documentação do módulo](https://docs.python.org/pt-br/3/library/venv.html) explica que ele leva uma chave `home` com essa localização. Você pode lê-lo com `cat .venv/pyvenv.cfg`.

Uma consequência importante: o `python` do ambiente é **um atalho para o Python com o qual foi criado**, não uma cópia independente. Por isso, se algum dia você mudar ou atualizar o Python do sistema, o ambiente pode ficar quebrado e será preciso recriá-lo. E por isso mesmo **um ambiente não se move nem se copia** para outra pasta ou para outro computador: a documentação diz isso com todas as letras (“não é considerado móvel ou copiável”; ele é recriado no destino). Os programas instalados em um ambiente guardam na primeira linha o caminho absoluto do seu interpretador; se o ambiente é movido, esse caminho já não aponta para nada. Recriar um ambiente custa dez segundos. Aprender a fazer isso sem medo é o objetivo.

#### 1.2.3 Ativar o ambiente

Criar o ambiente ainda não o usa. Para que o seu terminal use o **Python dele** em vez do do sistema, é preciso **ativá-lo**:

```text
$ source .venv/bin/activate
(.venv) $
```

`source` é um comando do terminal que executa um script “dentro” do terminal atual (em vez de abrir um novo). O script `activate` muda três coisas, **só nesse terminal**: acrescenta um prefixo ao prompt, `(.venv)`, que é o seu sinal visual de que você está dentro; ajusta a lista de pastas onde o terminal procura os programas (a variável `PATH`), pondo primeiro `.venv/bin`; e cria uma variável, `VIRTUAL_ENV`, com o caminho do ambiente, para que outros programas saibam em qual você está (`echo $VIRTUAL_ENV` a mostra). Além disso deixa disponível o comando `deactivate`, que desfaz tudo. É a mudança do `PATH` que faz o `python` passar a significar “o Python do ambiente”. A [documentação](https://docs.python.org/pt-br/3/tutorial/venv.html) resume isso: ativar modifica o ambiente para que, ao executar `python`, se use a versão do Python própria daquele ambiente.

Confira, que é o que importa. Com o ambiente ativo, pergunte qual é o `python`:

```text
(.venv) $ which python
/home/tu_usuario/curso-python/.venv/bin/python
(.venv) $ python --version
Python 3.12.3
```

Repare em duas coisas. A primeira: agora o `python` (sem o 3) **existe**, e aponta **para dentro do seu ambiente**. Fora de um ambiente, no seu Mint o comando `python` **não existe**: só existe `python3` (`which python` não imprime nada). Se você o digitar e o terminal disser que não o encontra ou sugerir `python3`, é o esperado. A regra, para todo o curso: **fora do ambiente, `python3`; dentro do ambiente ativado, `python`**. A segunda: a versão é a mesma de antes, porque o ambiente foi criado com esse Python. Se você tivesse criado o ambiente com `python3.14`, `python --version` diria 3.14. **O ambiente decide a versão; você a escolheu ao criá-lo.**

Esse par de comandos, `which python` e `python --version`, é a rotina de segurança de todo o curso. Antes de suspeitar do seu código, confira qual Python está rodando.

#### 1.2.4 Instalar um pacote: agora sim

Com o ambiente ativo, o mesmo comando que antes foi recusado funciona:

```text
(.venv) $ python -m pip install httpx
Collecting httpx
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
...
Successfully installed anyio-4.15.1 certifi-2026.7.22 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 typing_extensions-4.16.0
```

(As linhas intermediárias foram cortadas. Os números de versão que você verá são os vigentes no dia em que instalar, então quase com certeza não coincidem com estes; o que importa é a linha final `Successfully installed`.)

O que aconteceu: o `pip` baixou o `httpx` e também outros seis pacotes de que o `httpx` precisa para funcionar. Eles se chamam **dependências**: pacotes dos quais outro depende. Tudo caiu **dentro de `.venv/lib`**, sem tocar no Python do sistema. Confira com:

```text
(.venv) $ python -m pip list
Package           Version
----------------- ---------
anyio             4.15.1
certifi           2026.7.22
h11               0.16.0
httpcore          1.0.9
httpx             0.28.1
idna              3.20
pip               24.0
typing_extensions 4.16.0
```

A lista mostra o que há **neste ambiente**. Se agora você abrir outro terminal (sem ativar nada) e pedir a lista com `python3 -m pip list`, não verá o `httpx` (no seu Mint, aliás, a resposta será `No module named pip`): o que você instala em um ambiente não existe fora dele. Assim se vê o isolamento. Também pode aparecer um aviso no final da instalação que diz algo como `[notice] A new release of pip is available`: é informativo. Atualizar o `pip` não é necessário para o curso.

Uma nota sobre o `httpx`: nenhum programa do curso o usa antes da [Lição 9](09-http-y-asyncio.md). Nós o instalamos hoje **só para demonstrar o `pip`**, com um pacote real que tem dependências, e para que você veja a diferença entre instalar dentro do ambiente e fora dele.

#### 1.2.5 Desativar, e o hábito que é preciso adquirir

```text
(.venv) $ deactivate
$ which python
```

`deactivate` restaura o estado anterior do terminal: o prefixo `(.venv)` desaparece e `python` volta a significar o que significava (no Mint, como vimos, normalmente nada). Fechar o terminal tem o mesmo efeito, e por isso surge o **hábito que é preciso adquirir**: cada vez que você abrir um terminal novo para trabalhar no curso, é preciso ativar o ambiente de novo:

```text
$ cd ~/curso-python
$ source .venv/bin/activate
(.venv) $
```

Duas linhas, sempre as mesmas, e o prefixo `(.venv)` como confirmação. Quase todos os “não funciona” desta etapa se resolvem olhando se o prefixo está na tela.

Há outra forma de usar um ambiente sem ativá-lo, e convém saber que ela existe: chamar o Python do ambiente pelo seu caminho completo, `~/curso-python/.venv/bin/python hola.py`. A [documentação](https://docs.python.org/pt-br/3/library/venv.html) confirma: não é necessário ativar o ambiente, basta indicar o caminho do seu interpretador. Ativar é uma comodidade (escreve-se `python` em vez do caminho longo), não um requisito.

### 1.3 O REPL e executar um arquivo

Há duas maneiras de falar com o Python, e elas servem para coisas diferentes.

#### 1.3.1 O REPL: uma conversa

Com o ambiente ativo, digite só `python` e Enter. O Python não executa um arquivo; abre uma **conversa**: mostra um símbolo `>>>` e espera uma instrução. A isso se chama REPL (de *read-eval-print loop*: lê o que você digita, avalia, imprime o resultado e volta a esperar). Experimente assim (você digita o que vem depois de `>>>`; a linha de boas-vindas das primeiras linhas muda com a sua versão):

```text
(.venv) $ python
Python 3.12.3 (main, ...) [GCC ...] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 142 + 1
143
>>> "reportes"
'reportes'
>>> tiempo_ms = 142
>>> tiempo_ms
142
>>> print("142" + 1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can only concatenate str (not "int") to str
>>> exit()
(.venv) $
```

Percorra a conversa. `142 + 1` devolve `143`, sem necessidade de `print`: o REPL imprime por você o valor do que você digitar. `"reportes"` volta com aspas simples, porque é assim que o Python mostra um texto quando o representa. `tiempo_ms = 142` é uma atribuição e não devolve nada; depois, digitar `tiempo_ms` devolve `142`: **o REPL lembra** o que você disse enquanto você não o fechar. A quarta é o erro que você já conhece da Lição 0, `TypeError`, e observe: o REPL **não se fecha** por causa do erro. Mostra o relatório e volta a esperar. Isso o torna ideal para errar e aprender. Para sair, digita-se `exit()` (ou o seu gêmeo `quit()`) ou pressiona-se `Ctrl + D`; a [documentação](https://docs.python.org/pt-br/3/tutorial/interpreter.html) dá `Ctrl + D` como a forma principal e `quit()` como alternativa.

Dois detalhes de versão, para que você não estranhe se a sua tela parecer diferente. O REPL do **3.13 em diante** é renovado: tem cor e edição de várias linhas, e o nome que mostra em um relatório de erro é `<python-input-0>` em vez de `<stdin>`, além da própria linha que falhou. E o REPL do 3.12, o do seu Mint, é o simples de cima. Nada do que se faz no curso depende dessa diferença.

Para que serve o REPL? Para **testar ideias rápidas**: “o que faz esta operação?”, “como se chamava esta função?”. Para que **não** serve? Para escrever programas. O que você diz no REPL se perde quando você sai; não fica nenhum arquivo. Um programa é um texto que se guarda, se corrige e se executa de novo. Para isso existem os arquivos.

#### 1.3.2 Um arquivo: o seu primeiro script

Um **script** é um arquivo de texto com instruções de Python que é executado do começo ao fim. Para criá-lo você precisa de um editor de texto. O Mint traz um chamado **Xed** (aparece no menu como “Editor de texto”). Convém configurá-lo uma vez: nas preferências dele, ative **inserir espaços em vez de tabulações** e ponha a largura da tabulação em 4. O Python dá muita importância aos espaços no começo das linhas (a [Lição 2](02-valores-texto-decisiones.md) explica por quê), e misturar tabulações com espaços é uma fonte clássica de erros que preferimos evitar desde o primeiro dia. Se você prefere o terminal, `nano hola.py` abre um editor simples: escreva, salve com `Ctrl + O` e Enter, saia com `Ctrl + X`.

Crie o arquivo `~/curso-python/hola.py` com este conteúdo:

```python
# fig01_01.py
print("Hola, Python")
```

```text
$ cd ~/curso-python
$ python3 hola.py
Hola, Python
```

O nome `fig01_01.py` da primeira linha é o rótulo da figura dentro do curso (no repositório do curso o arquivo se chama assim); **você o salva como `hola.py`**, e por isso o comando é `python3 hola.py`. A primeira linha é um comentário (começa com `#`, o Python a ignora) e você pode omiti-la. A segunda é o programa. `print` é uma **função** que o Python já traz: mostra na tela o que vai entre parênteses. O que vai entre aspas é um **texto**, como você viu na lição anterior. Essa é toda a explicação de que você precisa hoje; a Lição 2 vai a fundo.

Execute-o duas vezes: uma **sem** o ambiente ativo e outra **com** ele. Fora do ambiente o comando é `python3 hola.py`. Dentro é `python hola.py`, porque dentro do ambiente o `python` existe e aponta para o Python dele. Nos dois casos, a saída é `Hola, Python`; o que muda, sem que você note, é **qual Python o executou**. Essa diferença é invisível enquanto tudo funciona e decisiva quando algo falha, e por isso há um exercício no final para anotá-la.

Com isso aparece o segundo arquivo de hoje, o primeiro do projeto. Crie a pasta do `revisor` e o arquivo onde ele crescerá:

```text
$ mkdir ~/curso-python/revisor
```

```python
# fig01_02.py
print("revisor: todavía no revisa nada")
```

Ele é salvo como `~/curso-python/revisor/revisor.py` (o rótulo `fig01_02.py` é, de novo, só o nome da figura). Para executá-lo, entre primeiro na pasta dele, porque `python3 revisor.py` procura o arquivo na pasta onde você está:

```text
$ cd ~/curso-python/revisor
$ python3 revisor.py
revisor: todavía no revisa nada
```

É um programa de uma linha, de propósito: o importante é que **o arquivo exista, rode e seja o ponto de partida**. A partir da Lição 2 ele cresce até ser o programa completo. A palavra “todavía” (“ainda”) é uma promessa.

### 1.4 O primeiro *traceback*

Na Lição 0 você viu um relatório de erro e leu a sua última linha. Hoje você o lê completo, com um erro que cometerá logo e muitas vezes: escrever errado o nome de algo. Este programa tem um erro de digitação deliberado. Desta vez salve-o com o nome da figura, `~/curso-python/fig01_03.py`, para que o relatório da sua tela coincida com o de baixo:

```python
# fig01_03.py
pirnt("hola")
```

```text
$ cd ~/curso-python
$ python3 fig01_03.py
Traceback (most recent call last):
  File "fig01_03.py", line 2, in <module>
    pirnt("hola")
    ^^^^^
NameError: name 'pirnt' is not defined. Did you mean: 'print'?
```

(Na sua tela, o caminho do arquivo será o caminho completo; aqui ele é encurtado para o nome.)

**A regra para ler um relatório de erro do Python: da última linha para cima.** Respondem-se três perguntas, nesta ordem.

**Que classe de erro é?** Olhe o começo da última linha: `NameError`. Um `NameError` ocorre quando você usa um nome que o Python não conhece. A Lição 0 explicou que um nome é um rótulo que aponta para um valor; o Python tem alguns nomes de fábrica (como `print`) e outros que você cria com uma atribuição. `pirnt` não é nenhum dos dois.

**O que ele diz exatamente?** O resto da última linha: `name 'pirnt' is not defined`, “o nome `pirnt` não está definido”. E a ajuda: `Did you mean: 'print'?`, “você quis dizer `print`?”. O Python comparou o nome desconhecido com os que ele conhece, encontrou um muito parecido e o sugere a você. Essa sugestão, que para este tipo de erro é idêntica nas versões 3.12 e 3.14, resolve a maior parte dos tropeços de um iniciante.

**Onde aconteceu?** As linhas de cima. `File "fig01_03.py", line 2, in <module>` diz o arquivo e a linha (a 2, porque a 1 é o comentário). Embaixo, o Python repete o texto dessa linha do seu código, e os acentos circunflexos `^^^^^` apontam a palavra exata: cinco caracteres, justo `pirnt`.

Faça o que a sugestão diz: troque `pirnt` por `print`, salve e execute de novo. Com essa pequena cerimônia (ler, entender, corrigir, repetir) você trabalhará o resto do curso. Um erro não significa que você fez algo errado; significa que o Python está respondendo a você com precisão.

## O erro que você vai ver

Hoje há três mensagens que convém saber ler: duas você já viu e a terceira é um aviso para depois.

**`NameError`** é o da seção anterior. Variantes que você verá: uma maiúscula onde não cabe (`Print("hola")` dá `NameError: name 'Print' is not defined. Did you mean: 'print'?`, porque o Python distingue entre maiúsculas e minúsculas), uma letra a mais, um nome que você esqueceu de definir. Em todos os casos se lê igual.

**`No module named pip`** é a resposta do seu Mint em 1.1.2, e o seu parente, a mensagem do `ensurepip` de 1.2.2, é a de um ambiente ao qual falta a mesma peça. Os dois dizem com todas as letras o que falta, e os dois se resolvem sem tocar no Python do sistema: o primeiro, trabalhando dentro do ambiente; o segundo, instalando o `python3.12-venv` e criando de novo o ambiente sobre a pasta pela metade.

**`externally-managed-environment`** é o aviso de 1.1.3: você não o verá em um Mint recém-instalado, mas sim no dia em que instalar o `pip` do sistema, ou em outra distribuição. A primeira linha, `error: externally-managed-environment`, é posta pelo `pip`: a PEP 668 não fixa esse texto, só exige que o instalador se recuse com um erro e mostre a mensagem que a distribuição escreveu no seu arquivo marcador (ou, se não houver, uma própria que sugira um ambiente virtual). O corpo, por isso, é escrito por cada sistema. Como exemplo real, esta é a mensagem completa que o Python do Homebrew dá em um macOS (o gerenciador de pacotes de lá se chama `brew`; no Mint seria `apt`):

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.

    If you wish to install a Python library that isn't in Homebrew,
    use a virtual environment:

    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz

    If you wish to install a Python application that isn't in Homebrew,
    it may be easiest to use 'pipx install xyz', which will manage a
    virtual environment for you. You can install pipx with

    brew install pipx

    You may restore the old behavior of pip by passing
    the '--break-system-packages' flag to pip, or by adding
    'break-system-packages = true' to your pip.conf file. The latter
    will permanently disable this error.

    If you disable this error, we STRONGLY recommend that you additionally
    pass the '--user' flag to pip, or set 'user = true' in your pip.conf
    file. Failure to do this can result in a broken Homebrew installation.

    Read more about this behavior here: <https://peps.python.org/pep-0668/>

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

Leia como você lê um *traceback*, sem medo, por partes. A primeira linha é a **classe**: `externally-managed-environment`, “ambiente administrado externamente”. A segunda, `This environment is externally managed`, dá a razão: este Python pertence a outro gerenciador. A terceira abre a lista de saídas. **Primeiro**, instalar o pacote com o gerenciador do sistema (aqui `brew`; no Mint seria `apt`), sempre que o pacote exista ali. **Segundo**, se o pacote não está no gerenciador, criar um ambiente virtual e usar `python3 -m pip` dentro dele: as três linhas que ela mostra são exatamente `venv`, `source ... activate` e `pip install`, que você acabou de usar. **Terceiro**, se o que você quer é uma *aplicação* (não uma biblioteca para usar no seu código), o `pipx`, que cria um ambiente isolado para cada aplicação. O `revisor` acabará sendo instalado assim, na [Lição 11](11-el-programa-terminado.md).

Abaixo das três saídas vêm mais dois parágrafos que o Homebrew escreveu: como “restaurar o comportamento anterior” com `--break-system-packages` e o aviso, em maiúsculas, de que fazer isso pode quebrar a instalação. E as duas últimas linhas já não são da distribuição, e sim do `pip`: uma `note:` que volta a mencionar `--break-system-packages` “por sua conta e risco de quebrar a sua instalação do Python ou o seu sistema operacional”, e uma `hint:` que remete à PEP 668. A opção aparecer duas vezes não a torna recomendável: ela aparece para que você saiba que existe e o que custa, que é o que diz a seção seguinte.

O corpo é um guia de resolução escrito por quem administra esse Python, e muda de um sistema para outro; o que não muda, porque quem põe é o `pip` e não a distribuição, é a primeira linha e a nota final. **Leia-o toda vez que aparecer**: poupa você de procurar na internet, e a maioria das respostas da internet para este erro recomenda o atalho que quebra a proteção.

## O que se faz errado

- **Usar `sudo pip install`.** Instala no Python do sistema com permissões de administrador. É a forma mais rápida de pisar em uma biblioteca de que o Mint precisa e só descobrir semanas depois. Cada pacote vai dentro de um ambiente virtual.
- **Usar `--break-system-packages` para que “já funcione”.** Desativa exatamente a proteção que ajuda você. O curso não o ensina nem o usa. Se você o vir em uma resposta da internet, ignore-a.
- **Instalar sem ver o prefixo `(.venv)`.** Se você abriu um terminal novo e esqueceu de ativar, a instalação é recusada (porque você está fora do ambiente) ou, em um sistema sem proteção, ocorre no lugar errado. A rotina é olhar o prefixo antes de instalar e conferir com `which python` na dúvida.
- **Mover ou copiar a pasta `.venv`.** Um ambiente guarda caminhos absolutos e não sobrevive a uma mudança de pasta. É apagado e recriado com `python3 -m venv .venv`; os pacotes são instalados de novo. É descartável por projeto.
- **Pôr o código do projeto dentro do ambiente.** O ambiente contém o Python e os pacotes; o seu código vive ao lado, em `revisor/`. Assim, apagar o ambiente não custa a você nem uma linha do que é seu.
- **Misturar tabulações e espaços no editor.** O Python usa os espaços do começo da linha para estruturar o programa, e misturar os dois tipos dá erros difíceis de ver. Configure o seu editor para 4 espaços, hoje, antes de escrever código de verdade.
- **Digitar o comando `python` fora do ambiente e concluir que “o Python não está instalado”.** O que falta é o alias `python`: fora do ambiente se digita `python3`. Que `python` não exista em um Mint recém-instalado é normal.
- **Ficar horas com um erro sem lê-lo.** Um relatório do Python quase sempre diz o que e onde. O hábito de começar pela última linha resolve a maioria.

## Exercícios

### Exercício 1 — O seu ambiente, medido

Execute em um terminal sem ambiente ativo: `python3 --version` e `which python3`. Depois ative o ambiente e execute `python --version`, `which python` e `python -m pip --version`. Escreva no seu [diário de bordo](bitacora.md) as cinco saídas e uma frase que responda: o que mudou entre `which python3` fora e `which python` dentro, e por quê?

### Exercício 2 — Provoque a recusa e leia-a

Desative o ambiente (`deactivate`) e execute `python3 -m pip install httpx`. Anote no diário de bordo a resposta exata e explique com as suas palavras quem fala (o que vem antes dos dois-pontos) e o que diz. Depois leia o exemplo de `externally-managed-environment` da seção “O erro que você vai ver” e escreva o que diz cada uma das suas três primeiras partes (a classe, a razão, a lista de saídas). Por fim, ative o ambiente e repita a instalação. Descreva o que mudou e o que você conferiu com `python -m pip list`.

### Exercício 3 — O `revisor` dentro e fora do ambiente

Crie `~/curso-python/revisor/revisor.py` com a linha da figura 2 e entre na pasta dele (`cd ~/curso-python/revisor`). Execute-o **sem** o ambiente (com `python3 revisor.py`) e **com** ele (com `python revisor.py`). Antes de cada execução, rode `which python3` ou `which python` conforme o caso, e anote no diário de bordo qual Python foi usado cada vez. O resultado saiu diferente?

### Exercício 4 — Provoque um erro novo e leia-o

Sem tocar no ambiente, crie um arquivo com a linha `Print("hola")` (com P maiúsculo). Antes de executá-lo, preveja a última linha do relatório. Execute e compare. Depois provoque um segundo erro diferente: crie um arquivo de duas linhas, `print("primera")` e `print("hola)` (a segunda sem a aspa de fechamento), e veja que classe de erro aparece. Chega a ser mostrado `primera`?

## Soluções

### Solução 1

Uma saída típica é `Python 3.12.x`, `/usr/bin/python3`, `Python 3.12.x`, `/home/tu_usuario/curso-python/.venv/bin/python` e um `pip` com o caminho de `.venv/lib/python3.12/site-packages/pip`. O que mudou entre fora e dentro é **o caminho**: fora é `/usr/bin/python3`, o Python do sistema; dentro é o que está em `.venv/bin/`, o do ambiente. Mudou porque o `activate` pôs `.venv/bin` no começo da lista de lugares onde o terminal procura programas; por isso o `python` (que fora nem sequer existia) passa a significar “o do ambiente”. A versão é a mesma porque o ambiente foi criado com o `python3` do sistema.

### Solução 2

Fora do ambiente, o seu Mint responde `/usr/bin/python3: No module named pip`: fala o Python do sistema e diz que não tem `pip`, então ali não se instala nada. No exemplo de `externally-managed-environment`, a classe é `externally-managed-environment`: o tipo de problema. A razão é que esse Python é administrado por outro gerenciador de pacotes, e o `pip` respeita a marca `EXTERNALLY-MANAGED` que deixou quem o instalou. A lista de saídas é: instalar com o gerenciador do sistema se o pacote existir ali, criar um ambiente virtual para bibliotecas, ou `pipx` para aplicações. Ao ativar o ambiente e repetir, a instalação se completa: dentro do ambiente há `pip`, e a proteção dele não se aplica porque ali ele não está tocando no Python do sistema. `python -m pip list` mostra o `httpx` e as suas dependências na lista do ambiente, e não na do sistema.

### Solução 3

Deve sair `revisor: todavía no revisa nada` nos dois casos. O que muda é o Python: sem ambiente, `which python3` dá `/usr/bin/python3`; com ambiente, `which python` dá o caminho dentro de `.venv/bin/`. O resultado não muda porque o programa só usa `print`, que não depende de nenhum pacote; a diferença se tornará visível quando um programa importar algo instalado no ambiente (a partir da Lição 9): esse programa funcionaria só com o ambiente ativo. Saber qual Python você usou é o que permite entender por quê.

### Solução 4

Com `Print("hola")` a última linha é `NameError: name 'Print' is not defined. Did you mean: 'print'?`: o Python distingue maiúsculas de minúsculas. Com `print("hola)` o erro muda de classe: aparece um `SyntaxError: unterminated string literal (detected at line 2)`, que significa “texto sem terminar”, porque falta a aspa que o fecha. `primera` **não** é mostrado: o erro ocorre antes de executar qualquer coisa. É um erro de forma, e o Python o detecta no passo em que lê e traduz o arquivo (o primeiro dos quatro passos da Lição 0). Não é um `NameError`, que só é descoberto ao chegar a essa linha com o programa já em andamento. A Lição 2 estuda esse erro a fundo.

## Como sei que consegui

- [ ] `python3 --version` mostra uma versão que começa com `Python 3.` e você a anotou no diário de bordo.
- [ ] `python3 -m pip install httpx`, com o ambiente **desativado**, termina com `No module named pip`, você sabe explicar sem olhar a lição o que isso significa e qual é a saída correta, e reconheceria o aviso `externally-managed-environment` se um dia o visse.
- [ ] Existe a pasta `~/curso-python/.venv`; com o ambiente ativo, o prompt do terminal começa com `(.venv)`, e `which python` mostra um caminho que termina em `.venv/bin/python`.
- [ ] Com o ambiente ativo, `python -m pip list` mostra o `httpx`; com o ambiente desativado, `python3 -m pip list` responde `No module named pip`: fora do ambiente não há `pip`, e portanto tampouco `httpx`.
- [ ] `python3 hola.py` fora do ambiente e `python hola.py` dentro mostram `Hola, Python`.
- [ ] `~/curso-python/revisor/revisor.py` existe e, ao executá-lo, mostra `revisor: todavía no revisa nada`.
- [ ] Você sabe ler, sem pedir ajuda, o relatório de `NameError` da figura 3: diz qual palavra falhou, em que linha e que sugestão o Python deu.
- [ ] Você consegue dizer, sem olhar, por que o ambiente não se move nem se copia, e por que nunca se instala com `sudo pip`.

## Resumo

Responda sem olhar a lição:

1. Qual é o Python que vem com o seu Mint, de quem ele é, e como você confere de onde ele roda?
2. O que diz `externally-managed-environment`, quem o põe, e quais são as três saídas que sugere? Qual é a que o curso usa?
3. Que três coisas o `source .venv/bin/activate` muda no seu terminal, e como você sabe que está dentro?
4. Por que o ambiente vive fora da pasta `revisor/` e por que não se move nem se copia?
5. Que diferença há entre o REPL e um arquivo? Quando você usa cada um?
6. Em que ordem se lê um relatório de erro do Python, e que três perguntas ele responde?
7. Qual Python o `python` usa dentro do ambiente e qual Python o `python3` usa fora?

## Para ler mais

- [Tutorial do Python: Ambientes virtuais e pacotes](https://docs.python.org/pt-br/3/tutorial/venv.html) — o guia oficial do `venv` e do `pip`, com os comandos desta lição. Na tradução oficial para o português do Brasil. Consultado em 7 de outubro de 2026.
- [PEP 668, “Marking Python base environments as externally managed”](https://peps.python.org/pep-0668/) — a especificação que explica o arquivo `EXTERNALLY-MANAGED` e a recusa do `pip`. Consultado em 7 de outubro de 2026.
- [Documentação do módulo `venv`](https://docs.python.org/pt-br/3/library/venv.html) — o que é o `pyvenv.cfg`, por que um ambiente é descartável e por que não se move. Consultado em 7 de outubro de 2026.
- [pip: primeiros passos](https://pip.pypa.io/en/stable/getting-started/) — conferir que o `pip` está instalado, instalar um pacote e por que ele é invocado como `python -m pip`. Consultado em 7 de outubro de 2026.
