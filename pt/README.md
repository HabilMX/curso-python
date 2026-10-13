# Curso de Python — do zero a um programa que revisa muitos serviços ao mesmo tempo

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Para quem é:** quem nunca programou, ou já copiou scripts que funcionam sem saber por quê. Nada é pressuposto: nem que você tenha o Python instalado, nem que saiba o que é um ambiente virtual. Cada conceito é explicado quando aparece, e se explica por que ele existe, e não só como se escreve.

**O que você vai saber ao terminar:** escrever um programa completo, com testes e várias tarefas ao mesmo tempo, entender o que escreveu e conseguir explicá-lo a outra pessoa. E ficar com o critério para ler a documentação do Python por conta própria, que é a verdadeira prova.

**Para onde segue:** o mesmo problema, o `revisor`, está resolvido nos cursos de [Go](https://www.habil.mx/pt/cursos/go/), [Rust](https://www.habil.mx/pt/cursos/rust/) e [TypeScript](https://www.habil.mx/pt/cursos/typescript/) desta casa. Quando você terminar este, comparar a sua solução com as deles ensina mais do que começar do zero.

**O que você precisa antes de começar:** um computador com Linux Mint e saber abrir um terminal. Nada mais. A [Lição 1](01-instalacion.md) prepara tudo do zero.

## O projeto que você vai construir

O **`revisor`**: um programa de linha de comando que recebe uma lista de serviços, consulta **todos ao mesmo tempo** e entrega um relatório em tabela ou em JSON.

    $ revisor --config servicios.toml --formato tabla
    SERVICIO    ESTADO    TIEMPO  DETALLE
    catalogo    ARRIBA     160ms  200
    inventario  LENTO       2.3s  200
    pagos       ARRIBA      90ms  200
    reportes    CAIDO          —  sin conexión

    4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms

Ele começa na lição 2 com um cabeçalho e um único serviço, e cresce a cada lição até ser um pacote que se instala como qualquer comando. Parece pequeno e não é: para escrevê-lo bem você precisa de funções, coleções, erros, arquivos, testes, tipos, HTTP e tarefas concorrentes.

## As doze lições

| Lição | | O que você constrói | O que você aprende |
|---|---|---|---|
| 0 | [O que é Python e o que NÃO é](00-que-es-python.md) | nada ainda (leitura) | interpretador e *bytecode*; tipagem dinâmica, mas forte; as anotações não são impostas; o GIL; ambientes virtuais; versões |
| 1 | [Instalar o Python no seu Linux Mint](01-instalacion.md) | o ambiente e o seu primeiro script | o `python3` do sistema; `externally-managed-environment`; `venv`; `pip`; o REPL; o primeiro *traceback* |
| 2 | [Valores, texto e decisões](02-valores-texto-decisiones.md) | o cabeçalho do `revisor` e a classificação de um serviço | três conceitos: números, strings, booleanos e `None`; f-strings; `if`/`elif`/`else` e a indentação |
| 3 | [Laços, funções e módulos](03-bucles-funciones-modulos.md) | a função `revisar()` e o percurso da lista | `for`, `while`; `==` contra `is`; `def`; escopo; o argumento mutável padrão; `import`; `__main__` |
| 4 | [Coleções](04-colecciones.md) | o `revisor` sem listas paralelas: os dados de cada serviço, juntos | `list`, `dict`, `tuple`, `set`; compreensões; cópia contra referência; `KeyError` e `IndexError` |
| 5 | [O modelo de dados](05-modelo-de-datos.md) | o modelo `Servicio` / `Estado` e o relatório com o seu resumo | `dataclass`; `Enum`; `match` e `case` |
| 6 | [Erros, arquivos e dados de fora](06-errores-archivos-datos.md) | a leitura da configuração | `try`/`except`; ler um *traceback*; `with`; `pathlib`; UTF-8; `json` e `tomllib`; validar; nada de `eval` nem `pickle` |
| 7 | [Um pacote com linha de comando](07-paquete-linea-de-comandos.md) | o `revisor` como pacote | `pyproject.toml`; `python -m revisor`; `argparse`; códigos de saída; instalação editável com `pip`; `uv` como quadro opcional |
| 8 | [Testes, tipos e qualidade](08-pruebas-tipos-calidad.md) | o `revisor` com testes | `pytest` e tabela de casos; `tmp_path`; `monkeypatch`; tipagem gradual com `mypy`; `ruff` |
| 9 | [HTTP e asyncio](09-http-y-asyncio.md) | o `revisor` que consulta de verdade | `urllib` e `httpx`; tempos limite; `async` e `await`; `asyncio.run` |
| 10 | [Concorrência com limites e testes sem rede](10-concurrencia-pruebas-sin-red.md) | o `revisor` concorrente e testado | `TaskGroup`; `timeout`; `Semaphore`; grupos de exceções; rede simulada nos testes |
| 11 | [O programa terminado](11-el-programa-terminado.md) | o `revisor` completo, instalável | relatório em tabela e JSON; `logging`; segurança; construir e instalar com `pipx` |

No final de cada lição há exercícios com as suas soluções e uma seção “Para ler mais”; as fontes do que se afirma têm link no próprio texto, onde são usadas. E o [diário de bordo](https://github.com/HabilMX/curso-python/blob/main/pt/bitacora.md) é seu: anote ali o que foi difícil para você.

**Para seguir lendo:** no blog da Hábil, [testes que detectam erros](https://www.habil.mx/pt/blog/testes-que-detectam-erros-cobertura-quality-gate/) e [segurança de APIs](https://www.habil.mx/pt/blog/seguranca-de-apis-cto-identidade-gateway-tokens/).

## Três critérios que atravessam todo o curso

**O erro é conteúdo, não um acidente.** Cada lição provoca de propósito o erro que você vai ver, mostra o *traceback* real e ensina a lê-lo, da última linha para cima. Saber ler um erro é metade de saber programar.

**O ambiente é real.** Trabalha-se no Linux Mint com o Python que o sistema traz e as suas regras, não em um caderno no navegador. Todo o código roda no Python 3.14 e também no 3.12, que é o do Mint.

**Os testes e a segurança não são lições, são costumes.** Os dados de fora são validados na 6, os testes chegam na 8 e um teste não conta até você vê-lo falhar, e o endereço que alguém escreve em um arquivo é tratado como o que é na 9 e na 11.

## Como você sabe que terminou

O curso não acaba quando você termina de ler a lição 11, e sim quando o seu `revisor` cumpre estas sete coisas:

1. **O `pytest` termina em verde e o relatório diz quantos testes rodaram.** Conte-os pelo relatório, não pelo código de saída: um verde com zero testes parece igual a um verde de verdade.
2. **`ruff check` e `ruff format --check` não apontam nada, e o `mypy` tampouco.**
3. **Revisa 20 serviços ao mesmo tempo em um tempo próximo ao do mais lento**, não à soma de todos. Você mede com o relógio, em série e em paralelo.
4. **Um serviço fora do ar, lento ou que responde lixo não derruba o relatório:** aparece na sua linha com o seu erro, e o resto sai completo.
5. **Nenhuma requisição pode esperar para sempre:** todas têm tempo limite.
6. **Roda igual no Python 3.14 e no 3.12 do seu Mint.**
7. **Instala-se com `pipx install` e `revisor --help` funciona a partir de outra pasta.** Sai com código 0 se tudo está no ar e 1 se não.
