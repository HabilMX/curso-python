# Leçon 8 — Tests, types et qualité

**Durée :** 2 × 90 min (la première session va jusqu'à la fin de 8.3 ; la seconde commence en 8.4)

**Ce que tu construis :** le `revisor` avec 21 tests qui se lancent avec une commande, avec ses types vérifiés et son style surveillé

**Ce que tu apprends :** `pytest` (`assert`, le test vu au rouge avant le vert, `parametrize`, `tmp_path` et `monkeypatch`), le typage graduel avec `mypy`, `ruff` pour vérifier et formater, et à lire le décompte du rapport et non le code de sortie

**D'où tu viens.** Tu arrives avec le paquet de la [Leçon 7](07-paquete-linea-de-comandos.md) : le `revisor` vit dans `~/curso-python/revisor/` avec la disposition `src/`, s'installe avec `pip install -e .` et se lance avec `python -m revisor`. Avec les quatre services d'entraînement, il affiche le tableau du programme et sort avec le code 1, parce qu'il y en a un lent et un en panne. Ça fonctionne. Ce que tu n'as pas, c'est un moyen de **savoir que ça continue de fonctionner** après y avoir touché : jusqu'à aujourd'hui, la seule vérification était de le lancer et de regarder le tableau, et les yeux se fatiguent et ne voient pas ce qu'ils ne s'attendent pas à voir. Cette leçon te donne trois vérificateurs qui ne se fatiguent pas : un qui exécute ton code avec des données connues et compare la réponse, un autre qui lit ton code sans l'exécuter et vérifie que les données s'emboîtent, et un autre qui veille à ce qu'il soit écrit comme on écrit en Python.

**Ce que cette leçon ne fait pas.** Elle ne touche pas au réseau : le `revisor` continue de lire les données simulées de `SIMULADO`, et interroger de vrais services, c'est la [Leçon 9](09-http-y-asyncio.md). Elle ne teste pas non plus de code asynchrone ni ne simule le réseau, ce qui est la [Leçon 10](10-concurrencia-pruebas-sin-red.md), et elle ne mesure pas combien de code touche chaque test (la *couverture*) : c'est un nombre utile et facile à falsifier, et il ne sert à rien tant que tu ne sais pas ce que teste chaque test.

## À la fin, tu seras capable de

- Écrire un test avec `pytest` (un fichier `test_*.py`, une fonction `test_*` et un `assert`), le lancer et lire son rapport de haut en bas.
- Voir un test **au rouge avant le vert**, et expliquer pourquoi un test que tu n'as jamais vu échouer ne démontre rien.
- Dire combien de tests se sont exécutés en lisant le **rapport**, et expliquer pourquoi le code de sortie ne suffit pas : un `0` cohabite avec un test qui ne s'est jamais exécuté.
- Convertir un tableau de cas en un seul test avec `@pytest.mark.parametrize` et distinguer dans le rapport quelle ligne a échoué.
- Tester du code qui lit des fichiers avec `tmp_path` et du code qui dépend d'une autre fonction avec `monkeypatch`, en sachant **où** il faut remplacer.
- Vérifier les types du paquet avec `mypy` en mode strict et lire son message, et expliquer ce que veut dire que le typage de Python soit graduel.
- Vérifier et formater le code avec `ruff check` et `ruff format`, avec les trois outils configurés dans `pyproject.toml`.

## Le pourquoi avant le comment

Ouvre `src/revisor/modelo.py` et cherche, dans `clasificar`, la ligne qui décide quand un service est lent : `if tiempo_ms is not None and tiempo_ms >= umbral_ms:`. Imagine que demain, dans la précipitation, quelqu'un « corrige » ce `>=` et le laisse en `>` : un seul caractère. Lance le `revisor` avec les quatre services d'entraînement. **Le tableau sort identique.** `catalogo` met 142 ms, `inventario` 2300, `pagos` 87 et `reportes` ne répond pas ; aucun ne met exactement 1000 ms, la seule valeur où `>=` et `>` se comportent différemment. Le défaut existe, le programme tourne sans une erreur et le tableau a l'air parfait. Le jour où un service réel mettra juste 1000 ms (les temps de réponse s'amassent sur des nombres ronds plus qu'il n'y paraît), il restera « en marche » alors que la règle du cours dit qu'il est déjà « lent ».

La vérification que tu avais, regarder le tableau, **ne pouvait pas** trouver ce défaut, parce qu'elle ne pose aucune question sur les cas qui comptent. Ce qu'il faut, c'est écrire ces questions une fois (« un service qui répond 200 en 999 ms, est-il en marche ? et un qui répond 200 en 1000 ms, est-il lent ? ») et qu'une machine les répète chaque fois que tu touches au code, en moins d'une seconde. C'est cela, un **test** : un petit programme qui appelle ton code avec une entrée connue et vérifie que la réponse est celle qui doit être. Un ensemble de tests est un filet de sécurité : il te laisse modifier le code tranquillement, car si tu casses quelque chose, tu le sais sur-le-champ et tu sais où.

La leçon apporte trois outils, chacun avec sa question :

| Outil | La question à laquelle il répond | Comment il travaille |
|---|---|---|
| `pytest` | Le programme fait-il ce que j'ai dit, avec ces données ? | **Exécute** ton code et compare |
| `mypy` | Les données s'emboîtent-elles entre elles ? Ai-je passé un texte là où allait un nombre, ou ai-je oublié que quelque chose peut être `None` ? | **Lit** ton code sans l'exécuter |
| `ruff` | Est-ce écrit comme on écrit en Python, sans imports en trop ni pièges connus ? | **Lit** ton code et le reformate |

Aucun ne remplace les autres, et ensemble ils forment ce qu'on appelle dans une équipe une barrière de qualité (*quality gate*) : le changement qui ne les passe pas n'entre pas. Le blog de Hábil raconte à quoi ressemble cette discipline dans un projet d'équipe, dans [des tests qui attrapent les erreurs, couverture et barrières de qualité](https://www.habil.mx/fr/blog/tests-qui-attrapent-erreurs-couverture-quality-gate/). La première session utilise `pytest` jusqu'à avoir les 21 tests du `revisor` ; la seconde vérifie types et style et laisse les trois outils en place dans le projet.

### Prépare les outils

Ils s'installent avec `pip` (comme dans la Leçon 1, avec `python -m pip`, pour que ce soit le `pip` de l'environnement) dans l'environnement virtuel du cours, le même que tu as activé dans la [Leçon 1](01-instalacion.md) (le prompt affiche `(.venv)`) :

```bash
python -m pip install pytest==9.1.1 ruff==0.16.10 mypy==2.4.0
```

Les versions sont fixées exprès : les messages de `ruff` et de `mypy` changent de formulation d'une version à l'autre, et avec les mêmes versions, ce que tu vois sur ton écran est ce que tu vois ici. Ce sont les versions en vigueur au 7 octobre 2026 sur [PyPI](https://pypi.org/project/pytest/), et les mêmes figurent dans `herramientas/requisitos.txt` du dépôt du cours. Ce sont des outils de **développement** : le `revisor` n'en a pas besoin pour tourner, donc ils n'entrent pas dans la liste `dependencies` de `pyproject.toml`, qui reste vide jusqu'à la Leçon 9. Vérifie avec `pytest --version`, `ruff --version` et `mypy --version` ; si l'un d'eux dit « command not found », l'environnement virtuel n'est pas actif, le même faux pas que dans la Leçon 1.

## Les concepts

### 8.1 `pytest` : exécuter ton code avec des données connues

#### 8.1.1 Le premier test

[`pytest`](https://docs.pytest.org/en/stable/getting-started.html) est le programme qui cherche les tests, les exécute et te remet un rapport. Il n'est pas fourni avec Python : c'est un outil tiers, le plus utilisé du langage. [Ses règles pour trouver les tests](https://docs.pytest.org/en/stable/explanation/goodpractices.html) sont peu nombreuses : il cherche des fichiers appelés `test_*.py` ou `*_test.py` et, dedans, il exécute les fonctions dont le nom commence par `test`. Tout le reste, il l'ignore. Retiens cette règle : plus bas, ignorer en silence coûte cher.

Un test prépare une entrée, appelle le code que tu veux vérifier et se termine par un `assert`. Commence par le plus petit, sur la fonction `formatear_tiempo` de la Leçon 3. Pour que l'exemple tourne seul, dans un fichier, la fonction est copiée au-dessus de ses tests :

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

Les deux fonctions du bas sont les tests, et on les reconnaît à leur nom. Chacune contient un `assert`, le mot réservé qui signifie « j'affirme que ceci est vrai » : [`assert condición`](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) ne fait rien si la condition est vraie et, si elle est fausse, arrête la fonction avec un `AssertionError`. Appeler et affirmer : c'est tout ce qu'il faut. Deux détails de forme. Les noms sont des phrases qui disent **ce qu'on attend** : `test_sin_tiempo_va_una_raya` te dit, le jour où il passera au rouge, ce qui s'est cassé sans que tu ouvres le fichier. Et le `-> None` dit que la fonction ne renvoie rien, comme tout test : ou elle se termine en silence ou elle s'arrête avec une erreur (en 8.4, tu verras que `mypy` en mode strict l'exige).

Ce fichier ne s'appelle pas `test_*.py`, mais quand tu donnes à `pytest` le nom d'un fichier, il l'exécute même s'il ne respecte pas le motif. Avec l'environnement actif :

```text
$ pytest -q fig08_01.py
..                                                                       [100%]
2 passed in 0.00s
```

L'option `-q` (*quiet*, « silencieux ») demande un rapport court. La première ligne a un point par test réussi et, à droite, l'avancement. La dernière est le résumé : `2 passed`, « deux ont réussi ». **C'est la ligne que tu vas apprendre à lire avec une saine méfiance** : elle dit combien de tests se sont exécutés et ce qui s'est passé pour chacun.

#### 8.1.2 Le voir au rouge avant le vert

Un test qui réussit ne dit pas grand-chose : il réussit si le code est bon, mais aussi si le test ne vérifie rien. Il n'y a qu'une façon de savoir si un test vérifie quelque chose : **le voir échouer**. À partir d'aujourd'hui, chaque test, tu le vois au rouge avant de l'accepter au vert. Voici le défaut du début, écrit dans un fichier :

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

`clasificar` décide l'état à partir du code et du temps ; cette version courte renvoie du texte. Elle contient le défaut : elle utilise `>` là où la règle dit « mille millisecondes ou plus ». Les deux tests sont les questions de tout à l'heure. Lance-le et regarde aussi le code de sortie :

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

Lis le rapport de haut en bas. `.F` : le premier test a réussi et le second a échoué. La section `FAILURES` contient un bloc pour chaque échec, avec le nom du test, son code et une flèche `>` sur la ligne qui a échoué. Les lignes avec `E` sont l'erreur : `assert 'ARRIBA' == 'LENTO'`. C'est ce qu'a de spécial `pytest` : il réécrit tes `assert` pour que, en cas d'échec, ils montrent **les deux valeurs** comparées ([la documentation l'explique](https://docs.pytest.org/en/stable/how-to/assert.html)) ; avec un `assert` nu, tu n'aurais vu que `AssertionError`. Les lignes avec `-` et `+` détaillent la comparaison ; dans cette version de `pytest`, celle qui porte `-` est la valeur de droite du `==` (`LENTO`, ce que le test attendait) et celle qui porte `+` celle de gauche (`ARRIBA`, ce que le code a renvoyé). Ensuite viennent le fichier et la ligne (`fig08_02.py:18`), un résumé d'une ligne par échec, coupé à la largeur du terminal (c'est pourquoi il se termine par `=...`), et le décompte : `1 failed, 1 passed`.

Le `echo $?` affiche le **code de sortie** de la commande précédente : le nombre que tout programme laisse à sa fin pour dire au système comment ça s'est passé. Par convention, `0` veut dire « bien » et tout autre nombre « quelque chose a échoué ». Tu l'as utilisé dans la Leçon 7 avec le `revisor`. Ici, `pytest` est sorti avec `1` parce qu'il y a eu des tests en échec. Les scripts et les outils d'intégration continue lisent ce nombre pour décider s'ils continuent ou s'arrêtent.

La correction est de changer `>` en `>=` :

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

Deux ont réussi, code `0`. Remarque l'ordre : d'abord la question (le test du 1000), puis le rouge contre le code défectueux, et seulement ensuite la correction. Cet ordre est la garantie. Si tu l'avais écrit **après** avoir corrigé, tu ne saurais jamais s'il était capable de détecter le défaut. Quand tu ajoutes un test à du code qui fonctionne déjà, l'équivalent est de casser le code exprès un moment, de voir le rouge et d'annuler le changement. L'Exercice 1 le fait avec le vrai `revisor`.

#### 8.1.3 Le décompte se lit dans le rapport, pas dans le code de sortie

Voici le piège qui donne son nom à l'une des règles du cours. [La documentation de `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) définit ses codes de sortie : `0`, tous les tests **qui ont été collectés** ont réussi ; `1`, certains ont échoué ; `2`, l'utilisateur a interrompu ; `3`, erreur interne ; `4`, erreur d'usage ; `5`, aucun test n'a été collecté ; `6`, le maximum d'avertissements a été dépassé. Remarque la phrase du `0` : « ceux qui ont été collectés ». Un test que `pytest` n'a jamais collecté n'existe pas pour lui. Regarde un fichier où cela se produit :

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

Il y a quatre fonctions de test et un piège. La dernière s'appelle `prueba_sin_respuesta_es_caido`, pas `test_...`, et `pytest` **ne la voit pas**. Son `assert` est faux exprès (il affirme que l'absence de réponse est `"ARRIBA"`), donc si elle s'exécutait, elle échouerait. Lance-le ; ensuite demande à `pytest` d'énumérer seulement ce qu'il a trouvé (`--collect-only`) et de n'exécuter que les tests dont le nom contient un texte qui n'existe pas (`-k`) :

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

Le premier rapport dit `3 passed` et le code de sortie est `0` : vert sur toute la ligne, avec un test cassé que personne n'a exécuté. Un tableau de bord qui ne regarderait que le code de sortie dirait « tout va bien ». Qui lit le rapport voit `3` et, s'il en a écrit quatre, se demande où est passé le quatrième ; `--collect-only` le confirme, parce qu'il en énumère trois. Cela arrive dans n'importe quel projet : avec une fonction mal nommée, un fichier qui ne s'appelle pas `test_*.py` ou un changement de nom qui a laissé un test dehors. La dernière commande montre l'autre extrême : `3 deselected` et code `5`, « aucun n'a été collecté ». Là, `pytest` a bien prévenu, mais l'avertissement se perd si ton script se termine par `|| true` ou s'il y a un filtre (`| tail`, `| grep`) au milieu qui avale le code de sortie. D'où la règle :

> **Le nombre de tests se lit dans le rapport (« N passed »). Un `0` n'est pas la preuve que ce que tu croyais s'est exécuté. Compare toujours N avec le N que tu attends.**

Le `revisor` termine cette leçon avec 21 tests, et c'est ce nombre que tu vérifieras à la fin de chaque session. La Leçon 9 part de lui. Si un jour le rapport dit 20, peu importe qu'il soit au vert : quelque chose a disparu. (Un test peut aussi être marqué comme *ignoré*, `skipped`, et alors il ne réussit ni n'échoue : il apparaît seulement dans le résumé. Dans ce cours, on ne l'utilise pas ; si un test ne sert pas, on le corrige ou on le supprime.)

### 8.2 `parametrize` : un tableau de cas, un seul test

`clasificar` applique quatre règles et a une frontière (1000 ms) où se concentrent les erreurs. Pour la tester correctement, il te faut **sept cas** : deux rapides (142 et 999 ms, le plus lent qui soit encore en marche), deux lents (1000 ms, le premier qui l'est déjà, et 2300), deux en panne par code (503 et 404) et un sans réponse (`None`, `None`). Écrits comme des fonctions séparées, ce serait sept fonctions identiques à deux nombres et un texte près, avec sept endroits à toucher le jour où la règle changera.

Ce que tu veux, c'est écrire le test une fois et les cas comme un tableau. [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html) le fait. L'arobase est un **décorateur** : une ligne au-dessus d'une fonction qui la modifie (tu as déjà vu `@dataclass(frozen=True)` dans la Leçon 5, sur une classe). Ici, il dit à `pytest` d'exécuter la fonction une fois par ligne :

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

Le premier argument est la liste des **noms des paramètres**, qui doivent coïncider avec ceux de la fonction du dessous. Le second est la liste des **cas** : un tuple par cas, avec une valeur par nom. L'`esperado` va dans le tableau et n'est pas calculé dans la fonction : si le test utilisait la même formule que le code qu'il teste, deux erreurs identiques s'annuleraient et il passerait au vert sur un défaut. Lance-le et énumère ce qu'il a collecté :

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

`7 passed` : `pytest` a converti la fonction en **sept tests**, chacun avec un nom qui porte entre crochets les valeurs du cas (`test_clasificar[200-1000-LENTO]`). Ce nom compte quand quelque chose échoue. Regarde ce qui se passe si tu introduis le défaut du `>` dans ce tableau :

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

`1 failed, 6 passed`, et la ligne `..F....` dit que c'est la troisième ligne. Le nom, `test_clasificar[200-1000-LENTO]`, est le cas exact ; sous lui, `pytest` affiche les valeurs des paramètres de **ce** cas, et les six autres ont réussi : une ligne qui échoue n'arrête pas les autres. Ajouter un cas, c'est ajouter une ligne.

Maintenant le projet. Les vrais tests vivent dans un dossier `tests/` à côté de `src/`. Le premier couvre `clasificar` avec les sept cas, avec le vrai `Estado` :

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

Il compare avec `is` et non avec `==` : les membres d'un `Enum` sont uniques et `is` interroge l'identité, comme le `is None` de la Leçon 2. Et les paramètres portent des **annotations de type**, comme le code du paquet ; en 8.4, tu verras pourquoi. Le second couvre `formatear_tiempo` avec quatre cas : sans temps, un en millisecondes, le dernier qui l'est encore (999) et un en secondes :

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

Pour que `pytest` sache où chercher sans que tu le lui dises, le `pyproject.toml` gagne une section (le fichier complet est en 8.6) :

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` est la liste des dossiers où il cherche quand tu le lances sans arguments. Dans ce qui suit, la ligne `cd fig08_15` représente « être à l'intérieur du projet » ; toi, tu es déjà dans `~/curso-python/revisor/`, donc ne l'écris pas.

```text
$ cd fig08_15
$ pytest -q tests/test_modelo.py
.......                                                                  [100%]
7 passed in 0.01s
$ pytest -q tests/test_formato.py
....                                                                     [100%]
4 passed in 0.00s
```

Sept et quatre : onze jusqu'ici. Chaque rapport compte ce qu'il doit ; si tu additionnes mal, il te le dira.

### 8.3 `tmp_path` et `monkeypatch` : des tests qui ne salissent rien et ne dépendent de rien

`clasificar` et `formatear_tiempo` sont des fonctions pures : elles reçoivent des valeurs, renvoient une valeur et ne touchent à rien en dehors d'elles. Mais `leer_servicios` lit un fichier, et `main` lit des arguments, affiche et appelle la fonction qui interroge les services. Tester cela pose deux problèmes, et `pytest` apporte un outil pour chacun. Les deux sont des *fixtures*.

Une **fixture** est une fonction que `pytest` exécute pour toi avant un test pour lui remettre quelque chose dont il a besoin. Tu la demandes en la déclarant comme **paramètre** : si ton test est `test_algo(tmp_path)`, `pytest` voit le nom, cherche une fixture qui s'appelle ainsi, l'exécute et passe le résultat comme argument. Tu ne l'importes pas ni ne l'appelles ([la documentation le détaille](https://docs.pytest.org/en/stable/how-to/fixtures.html)).

#### 8.3.1 `tmp_path` : un dossier neuf pour chaque test

Pour tester que `leer_servicios` lit bien un fichier, il te faut un fichier. Si les tests utilisaient le `servicios.toml` de ton projet, tout changement de ce fichier casserait des tests qui n'ont rien à voir, et un test qui **écrit** salirait ton dossier. La fixture [`tmp_path`](https://docs.pytest.org/en/stable/how-to/tmp_path.html) remet un `Path` (celui de `pathlib`, de la Leçon 6) qui pointe vers un **dossier temporaire, neuf et vide, unique pour ce test** :

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

Le premier test monte un petit `servicios.toml` et vérifie que deux services sont comptés. Le second démontre l'isolation : il reçoit un dossier **vide**, même si le précédent vient d'écrire un fichier dans le sien. Pour le vérifier, il utilise deux choses de `pathlib` : `is_dir()` demande si le chemin est un dossier qui existe, et `iterdir()` parcourt ce qu'il y a dedans, un élément pour chaque fichier ou sous-dossier. Comme `iterdir()` livre les éléments un par un et non une liste, `list(...)` les rassemble dans une liste (comme tu l'as fait avec `list(tiempos_ms)` dans la Leçon 4), et la liste d'un dossier vide est `[]`.

```text
$ pytest -q fig08_07.py
..                                                                       [100%]
2 passed in 0.01s
```

Les dossiers vivent dans le répertoire temporaire du système, et `pytest` conserve ceux des trois dernières exécutions au cas où tu voudrais inspecter ce qu'a laissé un test en échec.

Avec cela, tu écris les tests de `leer_servicios` : un qui lit un fichier valide et sept qui le rejettent. Trois des sept protègent ce que tu as vu en 6.4.3 : `url mal formada` (avec `http://[::1`, `urlsplit` lance `ValueError`, et le test exige qu'elle arrive comme le message de configuration et non comme un *traceback* ; si tu supprimes le `try` de `es_url_http`, il passe au rouge), `url con salto` (un saut de ligne à l'intérieur de l'adresse ; il passe au rouge si tu supprimes `isprintable()`. Dans le tableau tu verras `\\n`, avec la double barre : dans une chaîne de Python, `\\` écrit une barre oblique inverse, donc le fichier TOML reçoit `\n`, et TOML la convertit en vrai saut de ligne) et `url con acento` (`https://catálogo.example` ; il passe au rouge si tu supprimes `isascii()`). Les sept partagent la même forme, donc elles vont dans un tableau, avec `ids=` pour que le rapport utilise des noms lisibles :

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

Le fichier valide est comparé à une liste qui contient un `Servicio` ; cela fonctionne parce que les `dataclass` comparent par contenu. Celles de rejet utilisent `with pytest.raises(ErrorDeConfiguracion) as informe:`, un `with` (celui de la Leçon 6) qui affirme le contraire d'un `assert` normal : que le code de l'intérieur **lance** cette exception. Si le bloc se termine sans rien lancer, `pytest` marque le test comme échoué avec `DID NOT RAISE`. Le `as informe` conserve l'exception ; `str(informe.value)` est le message que tu as écrit dans la Leçon 6, et le test le compare en entier. Vérifier le message et pas seulement le type distingue « a échoué pour la bonne raison » de « a échoué pour une raison quelconque ».

#### 8.3.2 `monkeypatch` : changer quelque chose seulement pendant la durée du test

Le `main` appelle `revisar_todos`, qui aujourd'hui lit `SIMULADO` et qui, à partir de la Leçon 9, interrogera le réseau. Pour tester seulement ce que `main` fait avec les résultats (quel code de sortie il renvoie), il convient de **remplacer** cette fonction par une fausse. La fixture [`monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) existe pour cela : `monkeypatch.setattr(destino, valor)` remplace un attribut, et **à la fin du test le laisse comme il était**. Regarde le mécanisme dans un petit fichier :

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

Il y a une variable de module, `UMBRAL_LENTO_MS`, et une fonction qui la lit. Le premier test utilise le seuil de toujours. Le deuxième **le change à 3000 pendant ce test** : `"fig08_08.UMBRAL_LENTO_MS"` est l'adresse de l'attribut, sous la forme `módulo.nombre` (ce module s'appelle comme le fichier, sans le `.py`) ; dans ce test, 1500 n'est plus lent. Le troisième vérifie qu'ensuite le seuil est redevenu 1000.

```text
$ pytest -q fig08_08.py
...                                                                      [100%]
3 passed in 0.00s
```

Les trois ont réussi, et celui qui compte est le troisième : le changement **ne reste pas**. Assigner la variable à la main la laisserait modifiée pour les tests suivants et produirait des échecs qui dépendent de l'ordre, parmi les plus difficiles à comprendre.

Maintenant le vrai test. `main` renvoie `0` si tout est en marche et `1` sinon. Pour tester les deux cas sans dépendre des données simulées, tu remplaces `revisar_todos` par une fonction fausse qui renvoie ce que tu décides :

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

Avant les tests, la constante `CONFIGURACION` est le texte d'un petit `servicios.toml`, entre triples guillemets, comme les textes de plusieurs lignes de la Leçon 6. La barre oblique inverse juste après les guillemets d'ouverture (`"""\`) évite que le texte commence par un saut de ligne : à la fin d'une ligne, dans un texte, `\` veut dire « cette ligne continue sur la suivante », donc la première ligne du texte est `[[servicios]]` et non une ligne vide. Pour le TOML, cela ne changerait rien, mais ainsi ce qu'écrit le test est exactement ce que tu vois.

Le premier test utilise les vraies données simulées avec une configuration qui inclut `reportes`, qui est en panne. Le deuxième remplace la fonction par `todos_arriba`, définie à l'intérieur du test parce que lui seul l'utilise, avec la même signature que la vraie : quand `main` l'appellera, il ne saura pas qu'elle est fausse.

Regarde bien la destination : `"revisor.cli.revisar_todos"`, le nom **à l'intérieur de `cli`**, et non celui de `revision`, où la fonction est définie. [La documentation de `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) le dit : il faut remplacer la référence que ton code utilise. Une instruction `from modulo import nombre` crée, à l'intérieur du module qui importe, un nom propre qui pointe vers la même fonction : deux noms pour une chose, et remplacer l'un ne change pas l'autre. `cli.py` commence par `from revisor.revision import revisar_todos`, donc `main` cherche `revisar_todos` parmi les noms de `cli`. Si tu remplaçais celui de `revision`, `cli` continuerait d'appeler la vraie. Dans « L'erreur que tu vas voir », tu le casses exprès.

Avec les quatre fichiers écrits, tu lances **le tout ensemble** pour la première fois. Tu sais déjà ce qu'il doit dire :

```text
$ cd fig08_15
$ pytest -q
.....................                                                    [100%]
21 passed in 0.02s
```

Vingt et un points et `21 passed` : 7 + 4 + 8 + 2. Ce nombre est le contrat avec la Leçon 9. **La première session s'arrête ici.** Quand tu reviendras, `pytest -q` est la première chose que tu lances, pour savoir que tu as laissé le projet comme tu le croyais.

### 8.4 `mypy` : des types qui se vérifient sans rien exécuter

#### 8.4.1 Les annotations ne sont pas imposées à l'exécution

Depuis la Leçon 3, tu écris des annotations comme `tiempo_ms: int | None`. La Leçon 0 a dit que **Python ne les utilise pas à l'exécution** : c'est de l'information pour qui lit et pour des outils externes, pas un ordre. La [PEP 484](https://peps.python.org/pep-0484/), qui les a introduites, le dit sans détour : les types ne sont pas vérifiés à l'exécution. On le voit avec quatre lignes :

```python
# fig08_09.py
def doble(tiempo_ms: int) -> int:
    return tiempo_ms * 2


print(doble("142"))
```

La signature dit que `doble` reçoit un entier, et l'appel lui passe le texte `"142"`. Lance-le et demande à `mypy` de le vérifier :

```text
$ python fig08_09.py
142142
$ mypy fig08_09.py
fig08_09.py:6: error: Argument 1 to "doble" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Python ne se plaint pas : `"142" * 2` est valide (il répète le texte) et le programme affiche `142142`, un résultat absurde pour un temps en millisecondes dont personne n'a été prévenu. [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) lit le fichier **sans l'exécuter**, compare chaque appel avec les annotations et se plaint. Son message a toujours la même structure : `archivo:línea: error: descripción  [código]`. Il dit où (ligne 6), quoi (l'argument 1 de `doble` est `str` et on attendait `int`) et, entre crochets, le code du type d'erreur (`arg-type`), utile pour le chercher. La dernière ligne compte les erreurs et les fichiers.

C'est le *typage graduel* : tu décides combien tu annotes, et `mypy` vérifie ce que tu as annoté. C'est la contrepartie de ce que fait TypeScript dans le [cours de Hábil](https://www.habil.mx/fr/cours/typescript/) : les types s'écrivent et se vérifient avant d'exécuter, mais ne sont pas un mécanisme du langage en cours d'exécution.

#### 8.4.2 Ce que `mypy` attrape : le `None` que tu as oublié

L'erreur la plus fréquente que `mypy` trouve est d'oublier que quelque chose peut être `None`. Le service `reportes` ne répond pas et son `tiempo_ms` est `None` : c'est pourquoi le champ est annoté `int | None`. Voici une fonction qui l'oublie (le programme attrape l'erreur seulement pour que tu voies le message sans bruit) :

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

Python s'en aperçoit quand il arrive au deuxième appel : `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`. Si cet appel était sur un chemin parcouru une fois par mois, l'erreur serait arrivée en production. `mypy` la trouve **sans rien exécuter**, à la ligne 3, et l'explique : `Unsupported operand types for / ("None" and "int")` et une note, `Left operand is of type "int | None"`. La solution n'est pas de faire taire `mypy` mais de décider ce qui doit se passer quand il n'y a pas de temps. Ici, renvoyer aussi `None`, et le dire dans le type de retour :

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

La fonction dit maintenant la vérité dans sa signature, `float | None`, et cette vérité a une conséquence : **quiconque utilise le résultat est obligé de vérifier si c'est `None`**, parce que `mypy` se plaindra s'il le traite comme un nombre. Au lieu d'une erreur cachée qui apparaît au petit matin, tu as une question gênante dans ton éditeur, ce qui est justement l'endroit où il convient de l'avoir.

#### 8.4.3 `match` et le cas qui manque

Dans la Leçon 5, tu as vu que `match` avec un `Enum` a un avantage que `mypy` exploite ici. Imagine que le `revisor` gagne un quatrième état, `DEGRADADO`, et qu'une fonction qui traduit les états en couleurs reste sans son `case` :

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

Python **ne prévient pas** : quand aucun `case` ne correspond, le `match` se termine sans rien faire, la fonction arrive à sa fin sans `return` et renvoie `None`. La quatrième ligne affiche `DEGRADADO -> None`, une couleur qui n'existe pas, et dans un vrai programme ce `None` voyagerait jusqu'à qui l'utilisera. `mypy` le voit sans rien exécuter : la signature promet un `str`, mais il y a un chemin (celui de `DEGRADADO`) qui se termine sans rien renvoyer, et c'est pourquoi il dit `Missing return statement`. Le message ne mentionne pas le membre qui manque, mais il désigne la fonction (`def semaforo`), et il suffit de comparer ses `case` avec les membres de l'`Enum` pour le trouver. C'est le filet de sécurité que promettait la Leçon 5 : tu ajoutes un membre, et `mypy` te signale chaque `match` qui est resté en arrière.

#### 8.4.4 Graduel : ce que tu n'annotes pas, `mypy` ne le vérifie pas, sauf si tu le lui demandes

[La documentation de `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) l'établit : une fonction sans annotations est considérée comme à typage dynamique, et par défaut `mypy` **ne vérifie pas son corps**. C'est une décision de conception pour pouvoir ajouter des types petit à petit à du vieux code. Regarde-le avec une fonction sans une seule annotation :

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

Sans options, `mypy` dit « Success » : `duplicar` n'a pas d'annotations et n'est pas vérifiée. Avec `--strict`, le même fichier donne deux erreurs : la fonction n'a pas d'annotations (`no-untyped-def`) et tu l'appelles depuis du code avec des types (`no-untyped-call`). Le mode strict est un raccourci qui active plusieurs vérifications à la fois ; [la documentation les liste](https://mypy.readthedocs.io/en/stable/command_line.html) : parmi elles `--disallow-untyped-defs` (toute fonction porte des annotations), `--check-untyped-defs` (vérifier aussi le corps de celles qui n'en ont pas), `--warn-return-any` et `--warn-unused-ignores`. La liste exacte peut changer d'une version à l'autre, c'est pourquoi la leçon fixe celle de `mypy`.

La règle du cours : **le projet est en mode strict dès le début** ; il est bien moins cher de maintenir les types que de les ajouter après. Cela se configure dans `pyproject.toml`, [où `mypy` le lit](https://mypy.readthedocs.io/en/stable/config_file.html) :

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

`python_version` est la version de Python contre laquelle vérifier (celle du Mint du cours), `strict = true` active le mode strict et `files` dit quoi vérifier quand tu le lances sans arguments : le paquet et aussi les tests, parce qu'un test mal typé cache des erreurs comme n'importe quel autre code.

#### 8.4.5 `mypy` dans le `revisor`

Avec la configuration en place, le projet entier se vérifie avec une commande. Tout le code du paquet et des tests porte des annotations (c'est pourquoi les tests se terminent par `-> None` et demandent `tmp_path: Path`) :

```text
$ cd fig08_15
$ mypy
Success: no issues found in 11 source files
```

`Success: no issues found in 11 source files` : sept fichiers du paquet (`__init__`, `__main__`, `cli`, `configuracion`, `formato`, `modelo` et `revision`) et quatre de tests. Lis le décompte comme tu l'as appris avec `pytest` : si un jour il dit `0 source files`, `mypy` n'a rien vérifié et le vert ne vaut rien. Pour le voir travailler sur le projet, fais l'Exercice 3 : change une annotation et regarde comment `mypy` te mène jusqu'à ceux qui l'utilisent. C'est son usage le plus précieux : quand tu changes la signature d'une fonction, il te dit tous les endroits à ajuster.

Un avertissement sur les issues de secours. `# type: ignore` dit à `mypy` de ne pas se plaindre de cette ligne, et le type `Any` éteint les vérifications sur une valeur. Ils existent pour des raisons légitimes (du code tiers sans types) et sont la façon la plus rapide de rendre l'outil inutile. La règle : **la plainte a presque toujours raison** ; avant de la faire taire, comprends ce qu'elle dit.

### 8.5 `ruff` : vérifier et formater

Le dernier outil ne sait rien de ton problème ni de tes types : il lit le code comme du texte et fait deux choses distinctes avec deux commandes. [`ruff`](https://docs.astral.sh/ruff/) est un seul programme qui couvre les deux rôles :

- **`ruff check`** est le *linter* (en français, « analyseur statique ») : il cherche des erreurs et de mauvaises pratiques connues, comme un import qui n'est pas utilisé ou une valeur par défaut partagée entre appels. [Chaque constat a un code](https://docs.astral.sh/ruff/linter/) d'une ou deux lettres et trois chiffres (`F401`, `E711`).
- **`ruff format`** est le *formateur* : il réécrit le code avec un format unique (espaces, sauts de ligne, guillemets, où l'on coupe une ligne longue). [Il imite celui de `Black`](https://docs.astral.sh/ruff/formatter/), le standard de la communauté, de sorte que ton code ressemble à celui de n'importe quel autre projet. Le meilleur, c'est ce qu'il **t'enlève** : la discussion sur le style se décide une fois et c'est la machine qui l'exécute.

Regarde les deux sur un fichier avec de vrais défauts. Il est désordonné exprès : c'est la seule chose du cours qui le soit.

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

Le programme tourne (il affiche les deux listes), et il a au moins cinq choses de travers. Comme tu es hors du projet et qu'il n'y a pas de `pyproject.toml` pour dire quelles règles appliquer, tu les lui passes avec `--select` ; `--output-format concise` demande une ligne par constat :

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

Le deuxième appel a affiché `['catalogo', 'pagos']` : le défaut de la Leçon 3 en action. La valeur par défaut `lista=[]` est **partagée** entre les appels, et `ruff` la voit d'avance comme `B006`. Il y a sept constats, chacun avec `archivo:línea:columna: CÓDIGO descripción`. La lettre du code est le nom de la collection de règles, que tu choisis avec `select` :

| Lettre | Ce qu'elle surveille | Un exemple ci-dessus |
|---|---|---|
| `E` | Style ([pycodestyle](https://peps.python.org/pep-0008/), le guide officiel) | `E401` plusieurs imports sur une ligne ; `E711` comparer avec `None` en utilisant `==` |
| `F` | Erreurs logiques simples ([Pyflakes](https://docs.astral.sh/ruff/rules/unused-import/)) | `F401` trois imports non utilisés |
| `I` | L'ordre des imports | `I001` bloc désordonné |
| `B` | Pièges connus ([bugbear](https://docs.astral.sh/ruff/rules/mutable-argument-default/)) | `B006` valeur par défaut mutable |
| `UP` | Moderniser la syntaxe pour ta version de Python | (aucun dans ce fichier) |

La documentation [recommande de commencer avec peu de règles](https://docs.astral.sh/ruff/linter/) (`E` et `F`), d'ajouter des groupes un par un et de choisir avec `select` pour que l'ensemble soit explicite et ne change pas tout seul à la mise à jour. Ces cinq sont l'ensemble du `revisor`.

La marque `[*]` dit que `ruff` sait corriger le constat tout seul ; le résumé compte cinq constats avec correction, et deux autres ont des corrections *non sûres* qui pourraient changer ce que fait le programme (comme celle de `B006`). `ruff` n'applique que les sûres, sauf si tu le lui demandes. `ruff format --check` est la question « est-ce formaté ? » : il a répondu que non, et montre ce qui changerait. Pour voir ce que ferait chacun sans toucher au fichier, il existe `--diff` :

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

Le premier montre la correction sûre : supprimer les deux lignes d'imports, qui sont entièrement en trop. Remarque qu'il dit `Would fix 4 errors`, pas cinq : les cinq constats avec `[*]` se trouvent sur les deux mêmes lignes, et leurs corrections se marchent dessus. En appliquant celles de `F401`, qui suppriment les imports non utilisés, la ligne disparaît et une autre des corrections (séparer `os` et `sys`, ou les ordonner) n'a plus rien à faire. C'est pourquoi il convient de regarder le `--diff` et pas seulement de compter les marques. Le `== None` et la valeur par défaut restent, parce que leurs corrections sont non sûres : c'est à toi de décider. Le second montre ce que ferait le formateur : deux lignes vides entre les fonctions, la convention. Ce que fait `ruff format` est mécanique et ne change pas ce que fait le programme.

#### 8.5.1 Dans le projet : la configuration

Les règles s'écrivent une fois dans `pyproject.toml`, comme celles de `pytest` et `mypy`, et alors `ruff check` et `ruff format` n'ont pas besoin d'arguments :

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

`target-version` dit pour quelle version de Python tu écris : la 3.12 du Mint, la plus ancienne que le cours admet. C'est important : `ruff` décide avec elle ce qui est « bibliothèque standard » en ordonnant les imports (`tomllib` l'est depuis la 3.11) et quelle syntaxe moderne suggérer. Dans ce projet, si tu ne l'écrivais pas, [`ruff` la prendrait](https://docs.astral.sh/ruff/settings/#target-version) dans `requires-python = ">=3.12"`, dans `[project]`, qui dit la même chose ; on l'écrit pour qu'elle soit visible à côté des règles. Sans l'une ni l'autre, `ruff` suppose la 3.10, et avec elle `tomllib` ne serait plus bibliothèque standard et finirait dans le bloc des paquets tiers. `select` va dans la sous-section `[tool.ruff.lint]`, [comme le documente `ruff`](https://docs.astral.sh/ruff/configuration/).

```text
$ cd fig08_15
$ ruff check
All checks passed!
$ ruff format --check
11 files already formatted
```

`All checks passed!` et tous les fichiers déjà formatés. Si tu lances `ruff check` sur du code qui n'est pas encore passé par le formateur, il est courant qu'il se plaigne de `E501` (ligne de plus de 88 caractères), et qu'un `ruff format` les résolve presque toutes, parce qu'il répartit sur plusieurs lignes les appels et les longues listes. C'est pourquoi l'ordre est toujours le même : **d'abord `ruff format`, ensuite `ruff check`**. Et si une règle du linter te paraît excessive, la réponse honnête est d'en discuter et de la retirer du `select` avec une raison, pas de la cacher avec un commentaire sur chaque ligne.

### 8.6 Le projet complet

L'instantané du projet à la fin de la leçon est le paquet de la Leçon 7 avec `version = "0.7.0"`, le dossier `tests/` (quatre fichiers que tu as déjà vus) et trois nouvelles sections de configuration. Le `pyproject.toml` complet :

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

Ce qui est nouveau par rapport à la Leçon 7, c'est la version et les trois dernières sections. Les autres fichiers **ne changent pas** ; ils sont répétés ici seulement pour que le projet soit complet et que tu puisses comparer avec les tiens si quelque chose ne coïncide pas :

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
from urllib.parse import urlsplit, urlunsplit

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

Réinstalle-le avec `pip install -e .` pour que l'environnement voie la nouvelle version. À partir d'aujourd'hui, chaque fois que tu termines un changement, tu répètes ce rituel, dans cet ordre :

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

## L'erreur que tu vas voir

### `ModuleNotFoundError: No module named 'revisor'`

C'est la première sur laquelle bute celui qui ouvre le projet dans un nouvel environnement. Les tests importent le paquet (`from revisor.modelo import clasificar`) et le paquet **n'est pas installé** dans l'environnement qui lance `pytest`. Le rapport ne commence pas par des points mais par un bloc `ERRORS` : l'erreur s'est produite lors de la *collecte* du fichier, avant d'exécuter quoi que ce soit. Version raccourcie (les longs chemins d'`importlib` sont notés `...`) :

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

Il se lit de bas en haut : la dernière ligne `E` est la cause, la précédente dit quelle ligne l'a provoquée (`from revisor.cli import main`, ligne 6 de `test_cli.py`) et les étapes intermédiaires, d'`importlib`, ne te servent pas. Le résumé compte quatre erreurs, une par fichier, et ne dit pas `0 passed`. La correction est `pip install -e .` depuis le dossier qui contient le `pyproject.toml` : le projet est bon, il faut l'installer.

### `fixture 'tmp_pth' not found`

C'est ce qui arrive si tu écris mal le nom d'une fixture, `tmp_pth` au lieu de `tmp_path`. Comme `pytest` la cherche par le nom du paramètre, un nom qui n'existe pas est une erreur de `pytest` et non de Python :

```text
___________________________ ERROR at setup of test_x ___________________________
file tests/test_x.py, line 4
  def test_x(tmp_pth: Path) -> None:
E       fixture 'tmp_pth' not found
>       available fixtures: anyio_backend, anyio_backend_name, ... tmp_path, ...
>       use 'pytest --fixtures [testpath]' for help on them.
```

Regarde l'en-tête : `ERROR at setup`, pas `FAILED`. Le test n'a même pas été exécuté ; il a échoué en *se préparant*. Le message te propose les fixtures disponibles (ici raccourcies), et `tmp_path` y est. (Les `anyio_*` apparaissent parce que `httpx`, que tu as installé dans la Leçon 1, apporte un plugin de `pytest` ; elles ne t'affectent pas.)

### Le test rouge qui remplace au mauvais endroit

Le plus instructif, parce qu'il n'est pas de syntaxe mais de raisonnement. Dans `tests/test_cli.py`, change la destination du `monkeypatch` de `revisor.cli.revisar_todos` en `revisor.revision.revisar_todos`, là où la fonction est définie, et lance les tests. Rapport réel, raccourci :

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

La ligne `E` dit `assert 1 == 0` et, dessous, que `main` a renvoyé `1`. La section `Captured stdout call` (ce que le code a affiché pendant le test, que `pytest` garde et montre seulement en cas d'échec) apporte l'indice décisif : **`reportes` apparaît en panne, avec les données de toujours**. Le remplacement n'a eu aucun effet, parce que `cli` a continué d'utiliser sa propre copie de `revisar_todos`. La morale est celle de la documentation : remplace le nom **là où il est utilisé**. Annule le changement avant de continuer.

## Ce qui se fait de travers

**Écrire un test qui ne peut pas échouer.** `assert clasificar(200, 142) is not None` réussit toujours, parce que `clasificar` ne renvoie jamais `None`. C'est la raison de l'habitude de 8.1.2. Coût : un filet avec un trou de la taille du test et la fausse tranquillité du vert.

**Laisser le test calculer la réponse avec la formule du code.** `assert formatear_tiempo(2300) == f"{2300 / 1000:.1f}s"` répète l'implémentation : si la formule est fausse, le test la copie. L'attendu s'écrit à la main, comme une donnée : `"2.3s"`.

**Copier la sortie actuelle comme valeur attendue sans la regarder.** Tu lances le code, tu vois qu'il renvoie `'ARRIBA'` et tu l'écris dans le test parce que « c'est ce qui sort ». Si c'était faux, tu as transformé le défaut en spécification, et le test le défend. L'attendu vient de la règle, jamais de ce que fait le code aujourd'hui.

**Ne regarder que le code de sortie.** C'est 8.1.3 : un `0` ne compte pas combien de tests se sont exécutés.

**Remplacer là où la fonction est définie et non là où elle est utilisée**, ou remplacer tant que le test n'exerce plus de code réel. Si tout l'intérieur de `main` est faux, la seule chose que tu testes, c'est le faux.

**Faire taire `mypy` avec `# type: ignore` ou avec `Any` pour que « ça passe ».** Tu gardes le défaut et tu retires l'avertissement. S'il y a une vraie exception, elle porte un commentaire avec le pourquoi.

**Annoter à moitié.** Une fonction avec des annotations sur deux paramètres et sans elles sur le troisième ne sort pas de la vérification : `mypy` vérifie bien son corps, mais le paramètre non annoté vaut `Any`, « n'importe quoi », et tout ce que tu fais avec lui passe sans questions. Avec `strict = true`, en plus, `mypy` le signale comme `[no-untyped-def]`. Tout ou rien ; dans ce cours, tout.

**Se battre avec le formateur.** Reformater à la main ce que `ruff format` a déjà décidé, ou désactiver une règle par paresse de la comprendre.

**Des tests qui dépendent de l'ordre, du disque ou du réseau.** Un test qui lit le vrai `servicios.toml`, ou qui ne réussit que si un autre s'est exécuté avant, échoue sur une autre machine sans explication. Avec `tmp_path` et `monkeypatch`, chaque test se suffit à lui-même.

## Exercices

### Exercice 1 — Casse, regarde le rouge, corrige

Dans `src/revisor/modelo.py`, change le `>=` de `if tiempo_ms is not None and tiempo_ms >= umbral_ms:` en `>`. Avant de lancer, **prédis** : combien de tests passeront au rouge et lequel ? Lance `pytest -q`. Ensuite lance `python -m revisor` et compare le tableau avec celui de toujours. Annule le changement et relance. Note dans ton journal de bord le nombre du rapport avant et après, et ce que t'a appris le tableau.

### Exercice 2 — Un nouveau test pour le code de sortie 2

`main` renvoie `2` quand le fichier de configuration n'existe pas. Écris dans `tests/test_cli.py` un test qui le vérifie : appelle `main(["--config", ...])` avec un chemin dans `tmp_path` vers un fichier que tu n'as pas créé, et affirme que le résultat est `2`. Avant de le garder, **vérifie qu'il peut échouer** : comment le mettrais-tu au rouge exprès ? Le rapport doit dire `22 passed`. Supprime-le à la fin (la Leçon 9 part de 21) et vérifie que ça redit 21.

### Exercice 3 — Que `mypy` te mène jusqu'à celui qui appelle

Dans `src/revisor/formato.py`, change `def formatear_tiempo(tiempo_ms: int | None) -> str:` en `def formatear_tiempo(tiempo_ms: int) -> str:`, sans rien toucher d'autre. Lance `mypy`. Combien d'erreurs sortent et dans quels fichiers ? Pourquoi y en a-t-il une dans `tests/test_formato.py`, que tu n'as pas touché ? Annule le changement.

### Exercice 4 — Le test qui manque

Il y a un changement d'un seul caractère dans `formatear_tiempo` que les 21 tests ne détectent **pas**. La frontière des mille millisecondes a son cas dans `clasificar`, mais celle-ci est la même frontière. Change `if tiempo_ms < 1000:` en `if tiempo_ms <= 1000:` et lance `pytest -q` : vert ou rouge ? Si c'est vert, écris le cas qui manque dans le tableau de `tests/test_formato.py`, vérifie qu'il passe maintenant au rouge, annule le changement du code et **supprime** le nouveau cas pour que le projet revienne à 21, le nombre avec lequel commence la Leçon 9.

## Solutions

### Solution 1

La prédiction correcte est **un** test rouge : `test_clasificar[200-1000-Estado.LENTO]`. Aucun autre ne touche exactement 1000. Rapport réel, raccourci :

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

`1 failed, 20 passed` fait 21 : le total est toujours là. Et le tableau de `python -m revisor`, avec le défaut en place, **sort identique** à celui de toujours : regarder le tableau ne trouve pas le défaut, le test oui. En annulant le changement, le rapport revient à `21 passed`.

### Solution 2

```python
def test_sin_archivo_de_configuracion_sale_con_2(tmp_path: Path) -> None:
    inexistente = tmp_path / "no-existe.toml"
    assert main(["--config", str(inexistente)]) == 2
```

Pour le voir au rouge, change le `2` en `0` et lance : il doit échouer avec `assert 2 == 0`, ce qui démontre qu'il regarde le vrai code de sortie. Avec la bonne version, `22 passed`. En le supprimant, `21 passed` doit revenir ; sinon, quelque chose est resté dans le fichier.

### Solution 3

Il sort **trois** erreurs, dans deux fichiers (`Found 3 errors in 2 files (checked 11 source files)`) :

```text
src/revisor/formato.py:23: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
src/revisor/formato.py:47: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
tests/test_formato.py:17: error: Argument 1 to "formatear_tiempo" has incompatible type "int | None"; expected "int"  [arg-type]
```

La première est dans `linea`, qui lui passe `resultado.tiempo_ms`, un `int | None`. La deuxième est dans `resumen`, qui lui passe la moyenne, qui peut aussi être `None` quand aucun service n'a répondu. La troisième est le test : son paramètre `tiempo_ms` est `int | None` (le tableau inclut le `None`) et il appelle la fonction avec lui. Les trois sont le même problème vu depuis trois endroits, et celui de la moyenne, tu ne t'en souvenais peut-être même pas : `mypy` te l'a montré sans que tu le cherches. En annulant le changement, on retrouve `Success: no issues found in 11 source files`.

### Solution 4

Le changement **passe au vert** (`21 passed`) : aucune des quatre lignes n'utilise 1000 (il y a un `None`, un 87, un 999 et un 2300). Avec `<=`, le 1000 sortirait comme `1000ms` au lieu de `1.0s` et personne ne le remarquerait. Le cas qui manque :

```python
        (1000, "1.0s"),
```

Avec lui, la mutation passe au rouge (`test_formatear_tiempo[1000-1.0s]` te dit lequel). Dans un projet à toi, tu le garderais sans y penser ; ici tu le supprimes seulement pour une raison de calendrier : la Leçon 9 compare son décompte avec 21. Ce que cette solution veut te laisser, c'est la question : **une suite au vert ne dit pas que le code est bon, elle dit que les questions que tu lui as posées ont une réponse**. Annule la correction et vérifie qu'elle passe au rouge : c'est la méthode.

## Comment savoir que j'ai réussi

- [ ] `pytest -q`, depuis la racine du projet, se termine avec `21 passed` (le nombre, pas seulement le vert).
- [ ] `mypy` se termine avec `Success: no issues found in 11 source files`.
- [ ] `ruff check` dit `All checks passed!` et `ruff format --check` dit que les 11 fichiers sont déjà formatés.
- [ ] Tu as changé `>=` en `>` dans `clasificar`, `pytest -q` a dit `1 failed, 20 passed`, et en annulant il est revenu à `21 passed`.
- [ ] Tu peux expliquer pourquoi un `echo $?` égal à `0` ne te dit pas combien de tests se sont exécutés, et ce que fait `--collect-only`.
- [ ] Tu peux expliquer pourquoi `monkeypatch.setattr` pointe vers `revisor.cli.revisar_todos` et non vers `revisor.revision.revisar_todos`.
- [ ] `pyproject.toml` a les trois sections (`[tool.pytest.ini_options]`, `[tool.ruff]` avec son `[tool.ruff.lint]` et `[tool.mypy]`) et `version = "0.7.0"`.

## Résumé

Réponds sans regarder la leçon :

1. Comment `pytest` reconnaît-il ce qu'est un test, et que se passe-t-il avec une fonction appelée `prueba_algo` ?
2. Pourquoi voit-on un test au rouge avant de l'accepter au vert ?
3. Quels codes de sortie a `pytest` pour « tout a réussi », « certains ont échoué » et « aucun n'a été collecté » ? Pourquoi le décompte se lit-il dans le rapport ?
4. Qu'est-ce que `@pytest.mark.parametrize` t'épargne et comment sais-tu quelle ligne a échoué ?
5. Qu'est-ce qu'une fixture et que remettent `tmp_path` et `monkeypatch` ?
6. Pourquoi `monkeypatch.setattr` pointe-t-il vers `revisor.cli.revisar_todos` ?
7. Que signifie que le typage de Python soit graduel et qu'est-ce qui change avec `strict = true` ?
8. Quelle différence y a-t-il entre `ruff check` et `ruff format`, et pourquoi lance-t-on le second en premier ?

## Pour aller plus loin

- [pytest, « Get Started »](https://docs.pytest.org/en/stable/getting-started.html) — le guide officiel, avec les règles de découverte et la lecture du rapport ; en anglais, comme presque toute la documentation de l'écosystème. Consulté le 7 octobre 2026.
- [mypy, « Getting started »](https://mypy.readthedocs.io/en/stable/getting_started.html) — ce que sont le typage dynamique et le typage statique, et comment introduire des types dans du code existant. Consulté le 7 octobre 2026.
- [Ruff, « The Ruff Linter »](https://docs.astral.sh/ruff/linter/) — comment on choisit les règles, ce que signifient les codes et ce qu'est une correction sûre. Consulté le 7 octobre 2026.
- [PEP 484, « Type Hints »](https://peps.python.org/pep-0484/) — le document qui a introduit les annotations de type et précise qu'elles ne sont pas vérifiées à l'exécution. Consulté le 7 octobre 2026.
