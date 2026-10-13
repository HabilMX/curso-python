# Leçon 5 — Le modèle de données

**Durée :** 90 min

**Ce que tu construis :** le modèle du `revisor` (`Servicio`, `Estado`, `Resultado`) et son rapport complet, avec tableau et récapitulatif

**Ce que tu apprends :** des moules de données avec `class` et `@dataclass(frozen=True)` ; `Enum` ; `match` et `case`, avec joker et avec gardes ; le rapport avec sa ligne de récapitulatif

**D'où tu viens.** Tu arrives avec le projet de la [Leçon 4](04-colecciones.md) : deux fichiers, `formato.py` et `revisor.py`, déjà sans listes parallèles. Dans `revisor.py`, `SERVICIOS` est la liste de noms que tu veux vérifier et `SIMULADO` est un dictionnaire qui range, pour chaque nom, un tuple `(código, tiempo_ms, error)`. Cela fonctionne et ne se désaligne plus. Mais la Leçon 4 s'est terminée sur trois gênes notées. Le tuple ne dit pas ce qu'est chaque position : le deuxième élément est le temps parce que tu t'en souviens, pas parce que le code le dit. `clasificar` renvoie un texte (`"ARRIBA"`, `"LENTO"`, `"CAIDO"`) et rien n'empêche d'écrire `"ARIBA"` sans que Python proteste. Et le tableau n'a pas encore sa ligne de récapitulatif.

**Ce que cette leçon ne fait pas.** Elle ne lit pas la configuration depuis un fichier (les quatre services restent écrits à la main ; la [Leçon 6](06-errores-archivos-datos.md) les en sort), n'intercepte pas d'erreurs avec `try` et ne définit pas de méthodes propres dans les classes. Elle n'interroge pas non plus d'adresse d'internet : les codes et les temps continuent de sortir de `SIMULADO`.

Tu travailles dans ton dossier `~/curso-python/revisor/`, avec l'environnement virtuel actif. Les petits programmes vont, comme dans la Leçon 4, dans le sous-dossier `practica/`.

## À la fin, tu seras capable de

- Déclarer `Servicio` et `Resultado` comme `@dataclass(frozen=True)` et `Estado` comme `Enum`, et expliquer ce qu'on y gagne face à un tuple, un dictionnaire ou un texte isolé.
- Construire une instance avec les champs par position ou par nom, les lire avec un point, et fabriquer une autre instance avec `replace` au lieu de modifier celle que tu as.
- Classer un service avec `match` et `case`, avec joker et avec gardes (`case c if c >= 400`), sans tomber dans le piège du nom qui capture.
- Lire `FrozenInstanceError`, le `ValueError` d'un `dataclass` avec une liste comme valeur par défaut et celui d'un `Enum` auquel on demande une valeur qu'il n'a pas.
- Monter le `revisor` en quatre fichiers et reproduire son tableau avec le récapitulatif `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.

## Le pourquoi avant le comment

Regarde comment le `revisor` parle aujourd'hui des choses de son problème. Un service est un **nom isolé** dans une liste. Ce qu'il a répondu est un **tuple anonyme**, `(200, 2300, None)`. Et son état est un **texte**, `"LENTO"`. Les trois formes fonctionnent, et les trois ont le même défaut : Python ne sait pas ce qu'elles signifient. Il ne sait pas que le deuxième élément du tuple est un temps, ni que `"LENTO"` est l'une de seulement trois valeurs possibles. Pour Python, ce sont un tuple et un texte comme n'importe quels autres, et c'est pourquoi une faute de frappe (écrire `"ARIBA"`, ou demander `respuesta[2]` en voulant le temps) n'échoue pas là où elle se produit : elle se glisse dans le programme et produit un tableau faux sans un seul message.

La solution est de donner à chaque chose du problème **un nom propre que Python reconnaît**. Un service ne sera plus « un texte dans une liste » mais un `Servicio`, avec des champs qui s'appellent `nombre`, `url` et `timeout_ms` ; un état ne sera plus un texte qu'on peut mal écrire, mais un `Estado.LENTO` que Python reconnaît ou rejette ; et ce qui est sorti de la vérification d'un service sera un `Resultado`. Cette forme que nous donnons, dans le programme, à ce que traite le problème, nous l'appelons ici **le modèle de données**. (Attention, ce n'est pas la même chose que la section « Data model » de la documentation de Python, qui parle du fonctionnement interne du langage ; ici « modèle » est le nôtre.)

Le chemin comporte trois outils et un assemblage. `dataclass` (5.1) fabrique des moules de données ; `Enum` (5.2) ferme la liste des valeurs permises ; `match` (5.3) décide entre plusieurs cas avec clarté ; et en 5.4 ils se rejoignent dans le projet, qui gagne en plus sa ligne de récapitulatif. À la fin de la leçon, le `revisor` fera ceci :

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

C'est le tableau de toujours, maintenant avec une ligne vide et un récapitulatif, et produit à partir d'objets avec un nom au lieu de tuples et de textes isolés. Remarque que l'en-tête et les quatre lignes sortent identiques à ceux des leçons 3 et 4, et que le récapitulatif est nouveau : pour compter combien sont en marche, combien lents et combien en panne, et obtenir la moyenne, il faut les compréhensions de la Leçon 4, maintenant appliquées à des résultats qui savent déjà ce qu'ils sont.

## Les concepts

### 5.1 Un moule pour chaque service : `class` et `@dataclass`

#### 5.1.1 Pourquoi le tuple et le dictionnaire ne suffisent pas

Avec ce que tu sais déjà, un service pourrait être un tuple, `("catalogo", "https://catalogo.example", 5000)`, ou un dictionnaire, `{"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}`. Le tuple, comme tu l'as vu dans la Leçon 4, ne dit pas ce qu'est chaque position. Le dictionnaire le dit, mais il a un autre problème : les clés sont des textes que tu écris de mémoire, et une faute de frappe ne se remarque pas là où elle se produit.

<!-- frag: dict_typo.py -->
```python
servicio = {"nombre": "catalogo", "url": "https://catalogo.example", "timeout_ms": 5000}
print(servicio.get("nmbre"))
```

```text
None
```

Écrire `"nmbre"` au lieu de `"nombre"` n'a rien cassé : `.get` a renvoyé `None`, et ce `None` va se glisser dans le programme jusqu'à ce que quelque chose échoue trois fonctions plus loin, loin de la cause. Ce que nous voulons, c'est que cette faute de frappe **échoue sur-le-champ**, avec un message qui le dit. C'est ce que donne un type propre.

#### 5.1.2 Une classe comme moule

Une **classe** est un moule pour fabriquer des valeurs qui ont toutes la même forme. Chaque valeur fabriquée avec le moule s'appelle une **instance**. Pense au moule d'un biscuit : la forme est unique et les biscuits sont nombreux. Dans le `revisor`, le moule est `Servicio`, et `catalogo`, `inventario` et `pagos` sont trois instances. Ici, tu n'utiliseras les classes que comme moules de données : sans méthodes, sans héritage (avec une exception de syntaxe que tu verras en 5.2). Le mot `class` suivi d'un nom et de deux-points ouvre le moule, et en dessous, avec retrait, on déclare **un champ par ligne**, au format `nombre: tipo`.

Python a un outil, le module `dataclasses`, qui fabrique presque tout ce dont un moule de données a besoin : la manière de construire chaque instance, celle de l'afficher à l'impression et celle de la comparer avec `==`. Il s'active avec une ligne juste au-dessus de la classe, qui commence par `@` et s'appelle **décorateur** : c'est une marque qui demande à Python de traiter la classe avec cet outil avant de la livrer. [La documentation du module](https://docs.python.org/3/library/dataclasses.html) le décrit ainsi : le décorateur ajoute les méthodes générées à la classe qu'il décore. Ici il s'utilise sous la forme `@dataclass(frozen=True)`, où `frozen=True` (gelé) demande en plus que les instances **ne puissent pas être modifiées**, comme un tuple. Enregistre ceci sous le nom `fig05_01.py` :

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

- `from dataclasses import dataclass` apporte du module `dataclasses` seulement l'outil dont tu as besoin, avec la forme `from ... import` de la Leçon 3.
- Les deux lignes vides avant et après la classe sont une convention de style ([PEP 8](https://peps.python.org/pep-0008/#blank-lines)), pas de la syntaxe ; le formateur que tu verras dans la Leçon 8 les exige.
- `nombre: str` et `url: str` déclarent deux champs de texte. `timeout_ms: int = 5000` déclare un champ entier avec **valeur par défaut** : si tu ne la donnes pas à la construction, il vaut 5000, le délai d'attente de `httpx` que le `revisor` utilisera plus tard. Les champs avec valeur par défaut vont **à la fin**, comme les paramètres avec valeur par défaut d'une fonction.
- `Servicio("catalogo", "https://catalogo.example")` **construit** une instance : on appelle le moule comme une fonction, avec les champs dans l'ordre où ils ont été déclarés. On peut aussi donner chaque champ par son nom, comme dans `notificaciones`, qui change en plus le délai d'attente en 1000. Par nom, cela se lit mieux quand il y a plus de deux ou trois champs.
- `print(catalogo)` affiche `Servicio(nombre='catalogo', url='https://catalogo.example', timeout_ms=5000)` : la manière d'imprimer a aussi été générée par `dataclass`, et c'est pourquoi une instance que tu imprimes pendant un débogage se comprend toute seule. Avec un tuple sans noms, tu aurais vu `('catalogo', 'https://catalogo.example', 5000)`.
- `catalogo.timeout_ms` lit un champ avec un point. Si tu écris mal le nom (`catalogo.timeout`), Python échoue sur-le-champ avec `AttributeError`, ce que nous voulions.
- `catalogo == igual` est `True` parce que `==` compare **champ par champ** : ce sont deux instances séparées avec les mêmes données. `catalogo is igual` est `False` parce que ce sont deux objets différents. C'est le `==` contre `is` de la Leçon 3, avec un cas réel : `==` demande « valent-elles la même chose ? », `is` demande « est-ce la même chose ? ».
- Les deux dernières lignes sont là pour que tu ne te fies pas trop. `Servicio(nombre=5, url=None)` **se construit sans protester**, alors que `nombre` devrait être du texte et `url` aussi. C'est ce que tu as appris dans la Leçon 0 : les annotations ne sont pas imposées à l'exécution. `dataclass` n'utilise les annotations que pour savoir quels champs il y a et dans quel ordre : [la documentation précise](https://docs.python.org/3/library/dataclasses.html) que, sauf deux exceptions que tu n'utiliseras pas, rien dans le décorateur n'examine le type annoté. Celui qui les vérifie, c'est un outil à part, `mypy`, dans la Leçon 8.

#### 5.1.3 Gelé : pour changer, on en crée un autre

Que fait `frozen=True` ? Il interdit d'affecter à un champ. Regarde ce qui se passe si tu essaies :

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

De ce *traceback*, on ne montre que la dernière ligne, qui est celle qui compte : entre les deux, il passe par une ligne que `dataclasses` génère à l'intérieur et qui n'est pas identique en 3.12 et en 3.14. Elle dit « on ne peut pas affecter au champ `timeout_ms` ». Comme avec le tuple, c'est une garantie et non une défaillance. [La documentation](https://docs.python.org/3/library/dataclasses.html#frozen-instances) l'appelle émulation d'instances en lecture seule.

Pourquoi voudrais-tu cela ? Parce que le résultat de la vérification d'un service est un **fait** : « à 10:42, `inventario` a mis 2300 ms ». Personne ne devrait pouvoir le corriger après coup sans laisser de trace. Et parce que, quand dans les leçons 9 et 10 plusieurs tâches liront les mêmes services en même temps, qu'aucune ne puisse les modifier évite toute une classe d'erreurs. Et si tu as vraiment besoin d'une autre version d'un service, tu ne l'édites pas : tu en **fabriques une autre** avec `dataclasses.replace`, qui copie une instance en ne changeant que les champs que tu indiques :

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

`replace` n'a pas touché `catalogo` : il a renvoyé `catalogo_corto`, une nouvelle instance. Et la dernière ligne montre un autre avantage de l'immuable : une instance gelée peut être mise dans un **ensemble** (ou servir de clé de dictionnaire), parce qu'elle ne change plus : elle est hachable au sens de la Leçon 4 (4.1.4), **pourvu que tous ses champs le soient**. Python calcule son empreinte à partir des champs, et ceux de `Servicio` sont des textes et des entiers. Deux instances égales comptent pour une seule : `{catalogo, repetido}` a un élément.

Un avertissement qui se relie à la copie contre référence de la Leçon 4 : `frozen` interdit de réaffecter le **champ**, mais ne rend pas immuable ce que le champ contient. Un champ qui range une liste peut toujours changer de l'intérieur (`servicio.etiquetas.append(...)`), parce que la liste reste mutable. Et cela a un second effet : une instance de ce genre ne peut plus être mise dans un ensemble, parce que l'empreinte se calcule avec tous les champs et qu'une liste n'a pas d'empreinte ; la tentative échoue avec `TypeError: unhashable type: 'list'` (en 3.14, le texte ajoute `cannot use ... as a set element`). C'est pourquoi, dans le `revisor`, les champs sont de types immuables : textes, entiers, `None`.

### 5.2 `Enum` : une liste fermée de valeurs

Regarde un autre problème semblable. `clasificar` de la Leçon 3 renvoie le texte `"ARRIBA"`, `"LENTO"` ou `"CAIDO"`, et celui qui l'utilise compare avec des textes. Si on en écrit un de travers :

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

Le programme n'a pas échoué : il a dit que le service n'était **pas** en marche, alors que ce qui s'est passé, c'est que quelqu'un a écrit un R de moins. C'est la même faute de frappe qu'en 5.1.1, maintenant dans une valeur. Ce qu'il faut, c'est une liste **fermée** de valeurs permises, avec des noms que Python reconnaît, et c'est un `Enum` (d'« énumération »). [Le module `enum`](https://docs.python.org/3/library/enum.html) le définit comme un ensemble de noms symboliques liés à des valeurs uniques.

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

- `class Estado(Enum):` ouvre un moule, comme `Servicio`, mais avec `(Enum)` entre parenthèses : c'est ainsi qu'on dit à Python « ce moule est basé sur `Enum` », c'est-à-dire que c'est une énumération. Les parenthèses après le nom signifient « cette classe part de cette autre ». Dans le code que tu écris dans ce cours, tu ne les verras qu'avec `Enum` et, dans la Leçon 6, avec `Exception` (le laboratoire de la Leçon 9 les utilise aussi, mais ce programme, tu l'exécutes sans l'écrire) ; pour ce dont tu as besoin, il suffit de lire cela comme « une classe de la famille `Enum` ».
- À l'intérieur, il y a une ligne par **membre** : `ARRIBA = "ARRIBA"` donne le nom du membre (à gauche, toujours en majuscules par convention) et sa **valeur** (à droite). Ici la valeur est le même texte que celui qui est imprimé dans le tableau, sans accent et en majuscules, qui est aussi la manière dont le JSON de la Leçon 6 le rangera.
- `Estado.LENTO` est un membre. `print` l'affiche avec le nom de sa classe devant : `Estado.LENTO`. `.name` est son nom (`LENTO`) et `.value` sa valeur (`LENTO`). Quand le rapport veut le mot pour le tableau, il utilise `.value`.
- `Estado("CAIDO")` va dans le sens contraire : il cherche le membre dont la **valeur** est ce texte. S'il n'y en a aucun, il échoue sur-le-champ (tu le vois dans un instant).
- `estado is Estado.LENTO` est `True` : [les membres se comparent par identité](https://docs.python.org/3/howto/enum.html#comparisons), et chaque membre n'existe qu'une seule fois. Et `estado == "LENTO"` est **`False`** : le membre `Estado.LENTO` et le texte `"LENTO"` sont des choses différentes, même s'ils s'impriment presque pareil. Cela surprend presque tout le monde la première fois. On compare toujours avec des membres (`estado == Estado.LENTO`), jamais avec le texte.
- `for posible in Estado:` parcourt les membres dans l'ordre où ils ont été déclarés.

Maintenant la faute de frappe, dans ses deux variantes. Écrire `Estado.ARIBA` échoue instantanément, au point exact de l'erreur :

<!-- frag: enum_typo.py -->
```python
from enum import Enum


class Estado(Enum):
    ARRIBA = "ARRIBA"
    LENTO = "LENTO"
    CAIDO = "CAIDO"


print(Estado.ARIBA)
```

La dernière ligne du *traceback* est :

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

Python devine même ce que tu voulais écrire. Ce qui compte, c'est que l'erreur se produit à la ligne de la faute de frappe et non trois fonctions plus loin. Et chercher par valeur un texte qui n'existe pas :

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

`ValueError: 'ROTO' is not a valid Estado`. Les deux erreurs disent la même chose avec des mots différents : « ce membre n'existe pas ». Remarque que ce sont exactement le genre de défaillance que nous voulions : précoce, claire et avec le nom du coupable.

### 5.3 `match` et `case` : décider entre plusieurs cas

La Leçon 2 t'a appris `if`/`elif`/`else`. Quand les branches sont nombreuses et interrogent toutes la **même valeur**, une longue chaîne de `elif` devient difficile à lire, et pour cela Python fournit, depuis la version 3.10, l'instruction `match`. Elle est très puissante (la [documentation officielle](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement) lui consacre une section entière, et la [PEP 636](https://peps.python.org/pep-0636/) en est un tutoriel), mais ici tu n'utiliseras que sa partie la plus simple. Regarde d'abord une fonction qui décrit un code d'état, et qui n'est pas encore celle du `revisor` :

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

Comment elle se lit :

- `match codigo:` dit « je vais comparer cette valeur » (le **sujet**). Chaque `case` en dessous est un **motif** avec lequel Python l'essaie, **de haut en bas**, et il garde **le premier qui convient** : il exécute son bloc et ne regarde pas les autres. C'est pourquoi l'ordre compte.
- `case None`, `case 200`, `case 404` sont des motifs **littéraux** : ils conviennent si le sujet vaut cela. Le premier interroge `None` par identité, comme on te l'a appris dans la Leçon 2, et les autres par égalité.
- `case 301 | 302` est **l'un ou l'autre** : la barre verticale signifie « ou ». Il convient avec n'importe lequel des deux codes.
- `case c if c >= 500` est celui qui mérite l'attention. D'abord `c` est un motif de **capture** : un nom isolé convient à *n'importe quoi* et, au passage, range le sujet dans cette variable, donc dans le bloc `c` vaut le code. Ensuite, `if c >= 500` est une **garde** : une condition supplémentaire qui doit être remplie pour que le cas vaille. Si elle n'est pas remplie, Python passe au `case` suivant. [La documentation](https://docs.python.org/3/reference/compound_stmts.html#guards) le décrit ainsi : si le motif échoue, la garde n'est même pas évaluée ; s'il convient, la garde est évaluée, et le cas n'est choisi que si elle est vraie. C'est pourquoi le 418 ne s'arrête pas au cas de 500 (il est inférieur) et tombe dans le suivant, `c >= 400`.
- `case _:` est le **joker** : le tiret bas convient à tout et ne range rien. Il va à la fin et recueille ce qu'aucun cas précédent n'a attrapé (ici, le 100).

La classification complète des services du `revisor` tient en quatre règles, que tu connais déjà depuis la Leçon 2 : sans code, il est en panne ; code de 400 ou plus, en panne ; s'il a répondu et mis 1000 ms ou plus, lent ; sinon, il est en marche. Elle s'écrit avec le même moule, et renvoie des membres de `Estado` au lieu de textes. Voici ce qui restera dans `modelo.py` :

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

Lis-la de haut en bas, comme le fait Python. Le premier `case` attrape « sans code » et le second, avec sa garde, attrape « code de 400 ou plus » : les deux premières règles, et les deux donnent `CAIDO`. Ce qui arrive au `case _`, nous savons déjà qu'il a répondu correctement (il y a un code et il est inférieur à 400), et là il ne reste qu'à décider entre les deux autres règles avec un `if` de la Leçon 2 : si le temps existe et vaut au moins le seuil, `LENTO` ; sinon, `ARRIBA`. Vérifier `tiempo_ms is not None` avant de comparer est nécessaire parce qu'un code peut exister sans temps, et comparer `None >= 1000` échoue avec un `TypeError`. Remarque aussi que l'ordre des cas **est** la logique : si tu mettais le cas du 400 avant celui de `None`, `None >= 400` échouerait. Dans le projet de 5.4, la fonction vit dans `modelo.py`, à côté des classes que tu as définies en 5.1 et 5.2.

Voici maintenant le piège le plus célèbre de `match`. Dans un motif, **un nom isolé ne compare pas, il capture**. Si tu veux comparer avec une constante, il ne suffit pas d'écrire son nom :

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

Ce programme **ne démarre même pas** : Python le rejette à la lecture, avec un `SyntaxError`. `case LIMITE:` ne demande pas « le code vaut-il 400 ? » ; il dit « tout convient, et range-le dans une variable appelée `LIMITE` ». Comme il convient à tout, le `case _` du dessous ne serait jamais atteint, et c'est pourquoi le message dit `name capture 'LIMITE' makes remaining patterns unreachable` (« la capture du nom rend inatteignables les motifs restants »). Python ne prévient que parce qu'après `case LIMITE:` il y a un autre cas. Si `case LIMITE:` était le dernier, il ne préviendrait de rien : [la documentation](https://docs.python.org/3/reference/compound_stmts.html#irrefutable-case-blocks) permet un cas qui convient toujours (elle l'appelle irréfutable) pourvu qu'il soit à la fin, et le programme s'exécuterait avec un joker déguisé en constante, renvoyant `True` pour n'importe quel code. Tu peux le vérifier : avec un `case LIMITE:` à la fin, `es_error(5)` renvoie `True`. La règle pratique : pour comparer avec une constante, on utilise un nom **avec un point**, comme `Estado.CAIDO` ; le point dit à Python que c'est une valeur et non un nouveau nom, et [elle les appelle motifs de valeur](https://docs.python.org/3/reference/compound_stmts.html#value-patterns).

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

Ici `Estado.ARRIBA` porte un point, donc il compare. C'est l'usage le plus naturel de `match` avec un `Enum` : un cas par membre, sans joker. Et il apporte un avantage que `mypy` exploite dans la Leçon 8 : si un jour tu ajoutes un nouveau membre à `Estado` et oublies son `case`, le vérificateur de types le signale.

### 5.4 Monter le `revisor`

Rassemble tout dans le projet. À la fin, tu auras quatre fichiers dans `~/curso-python/revisor/` : `modelo.py` (nouveau), `revision.py` (nouveau), `formato.py` (change) et `revisor.py` (change). Chaque fichier a sa raison d'exister : `modelo.py` dit **quelles choses il y a** (le service, l'état, le résultat) et comment on classe ; `revision.py` **vérifie** un service ; `formato.py` **donne une forme de texte** à un résultat, et `revisor.py` est le point d'entrée qui les rassemble.

Le premier est le modèle :

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

Les quatre pièces, une par une.

**`modelo.py`.** Il réunit tout ce qui est vu dans les sections 5.1 à 5.3. Les constantes et les classes vont en haut, parce que `clasificar` les utilise. `Resultado` est un second moule qui ne range plus de textes isolés : il range **un `Servicio`** (celui qui a été vérifié), **un `Estado`**, le temps (`int | None`, parce qu'un service en panne n'en a pas) et le détail. Remarque la composition : un moule peut avoir des champs dont le type est un autre moule. `clasificar` est celle que tu as écrite en 5.3, sauf que la liste de paramètres est répartie sur plusieurs lignes parce que la ligne du `def` ne tient pas dans les 88 caractères que demande le style (la virgule à la fin de la liste de paramètres fait partie de cette façon de disposer). Et `nombres_repetidos` est celle de la Leçon 4 (4.1.5), sauf que maintenant elle reçoit une liste de `Servicio` et regarde le champ `servicio.nombre`.

**`revision.py`.** C'est un nouveau module, mais son contenu ne l'est pas : `SIMULADO` est le dictionnaire de la Leçon 4, qui quitte `revisor.py` et déménage ici, avec le même tuple de trois `(código, tiempo_ms, error)` pour chaque nom. `revisar` change de signature une fois de plus : maintenant elle reçoit un `Servicio` et renvoie un `Resultado`, au lieu de recevoir un nom et de renvoyer une ligne déjà composée. Ce qu'il y a dedans, tu le connais déjà : elle cherche avec `.get` (un nom qui n'est pas dans `SIMULADO` est un service sans données, et il sort en panne « sin conexión »), déballe le tuple en trois noms, décide le `detalle` avec la même règle (le code sous forme de texte s'il y a eu réponse, et sinon, le texte de l'erreur), classe et renvoie un `Resultado`. Que `revisar` ne compose plus la ligne, c'est la séparation que nous cherchions : vérifier est une chose et montrer en est une autre, et chacune vit dans son module. `revisar_todos` est une compréhension : une liste de `Resultado`, un par service, dans le même ordre. Quand dans la Leçon 9 le programme interrogera pour de vrai, `SIMULADO` disparaît et `revisar` continue de renvoyer la même chose.

**`formato.py`.** `formatear_tiempo` et `encabezado` restent comme dans les leçons 3 et 4. (Si tu les as écrits d'une autre manière mais que la sortie était la même, laisse-les comme ils sont.) Ce qui change, c'est `linea`, qui **change de signature** : avant, elle recevait quatre valeurs isolées et maintenant elle reçoit un seul `Resultado`, et en tire ce dont elle a besoin. C'est ce que nous cherchions : il n'y a plus à passer quatre choses dans le bon ordre. Les deux nouvelles fonctions sont `contar` et `resumen`. `contar` ajoute un « s » quand la quantité n'est pas un : `contar(1, "caído")` donne `1 caído` et `contar(3, "caído")` donne `3 caídos`. `resumen` compte le total avec `len`, utilise trois compréhensions pour compter combien il y en a de chaque état, tire avec une quatrième les temps de ceux qui ont répondu, calcule la moyenne **seulement s'il y en a** (avec `len(tiempos_ms) > 0`, parce que diviser par zéro échouerait) et assemble les parties avec `" · ".join(partes)`. L'annotation `promedio_ms: int | None = None` dit qu'elle commence sans valeur et qu'elle peut finir par être un entier ; si aucun service n'a répondu, le récapitulatif dit `promedio —`.

**`revisor.py`.** `SERVICIOS` cesse d'être une liste de noms et devient une **liste de `Servicio`** : les quatre canoniques, écrits à la main, chacun avec son nom et son adresse (le délai d'attente reste à la valeur par défaut). Pour ajouter un service, tu écris un `Servicio(...)` et, tant que les données sont simulées, sa ligne dans `SIMULADO`, comme dans la Leçon 4. `main` vérifie tous les services, imprime l'en-tête, une ligne par résultat, une ligne vide (celle qu'écrit `print()` sans argument) et le récapitulatif. Les `from ... import` fonctionnent parce que les quatre fichiers sont dans le même dossier, comme dans la Leçon 3.

Exécute le projet depuis son dossier :

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

C'est le tableau des leçons 3 et 4, avec une ligne vide et le récapitulatif. Si les colonnes ne sortent pas alignées, le coupable est presque toujours une espace en trop ou en moins à l'intérieur de l'une des f-strings ; vérifie qu'elles sont identiques à celles du texte. Et si le récapitulatif compte mal, compare chaque compréhension avec celle de la leçon : les trois qui comptent les états ne changent que le membre de `Estado`.

Avec cela, le `revisor` a déjà son **modèle** : le `Servicio` qu'on vérifie, l'`Estado` dans lequel il se retrouve et le `Resultado` qui unit les deux choses avec ce qui a été mesuré. Mais il y a encore quelque chose de gênant, et tu le sentiras dans l'exercice 1 : la liste de services est **dans le code**. Pour vérifier un autre service, il faut ouvrir `revisor.py` et éditer. La [Leçon 6](06-errores-archivos-datos.md) la sort vers un fichier de configuration, et avec lui arrivent les erreurs qui méritent leur propre leçon.

## L'erreur que tu vas voir

Dans les sections précédentes, tu as déjà provoqué plusieurs erreurs à l'endroit où elles naissent (`FrozenInstanceError`, `AttributeError`, `ValueError`, `SyntaxError`). Voici celle que tu rencontreras le plus en écrivant des moules avec `dataclass`, et à la fin un tableau pour toutes les reconnaître d'un coup d'œil.

### `ValueError: mutable default <class 'list'> for field ... is not allowed`

C'est le même problème de l'argument mutable par défaut de la Leçon 3, maintenant dans un champ de `dataclass`. Si tu mets une liste comme valeur par défaut :

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

La dernière ligne dit : « une valeur par défaut mutable (`list`) pour le champ `etiquetas` n'est pas permise : utilise `default_factory` ». (Ici aussi, on ne montre que la dernière ligne : entre elle et ton fichier, le *traceback* passe par des lignes internes de `dataclasses.py` qui changent d'une version de Python à l'autre, et qui ne t'aident pas à lire l'erreur. Ce qui compte, c'est le type, `ValueError`, et le message, qui te dit en plus comment le corriger.) Python te protège de quelque chose qui, dans une fonction normale, se passait en silence : une seule liste partagée par toutes les instances. La solution est une **fabrique** : au lieu de « cette liste », tu dis « appelle `list` chaque fois qu'il en faut une nouvelle ».

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

Chaque instance a sa propre liste, et c'est pourquoi `pagos` ne s'est pas aperçu de l'étiquette de `catalogo`. Au passage, on voit ce qui avait été annoncé en 5.1.3 : l'instance est gelée, et pourtant `catalogo.etiquetas.append(...)` a fonctionné, parce que `frozen` empêche de réaffecter le champ, pas de modifier la liste qu'il contient. C'est pourquoi dans le `revisor` on n'utilise pas de listes comme champs.

### Les erreurs de cette leçon d'un coup d'œil

Quand l'une t'apparaît, cherche ici la dernière ligne. Toutes sont sorties des exécutions de cette leçon.

| La dernière ligne dit... | Ce qui s'est passé | Où tu l'as vue |
|---|---|---|
| `dataclasses.FrozenInstanceError: cannot assign to field '...'` | tu as tenté d'affecter à un champ d'une instance gelée | 5.1.3 |
| `ValueError: mutable default ... use default_factory` | tu as mis une liste comme valeur par défaut d'un champ | ci-dessus |
| `AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?` | tu as demandé un membre d'`Enum` qui n'existe pas | 5.2 |
| `ValueError: 'ROTO' is not a valid Estado` | tu as cherché par valeur un membre qui n'existe pas | 5.2 |
| `SyntaxError: name capture 'LIMITE' makes remaining patterns unreachable` | tu as écrit un nom isolé là où tu voulais comparer | 5.3 |

## Ce qui se fait de travers

Chacune de ces négligences a un coût concret, et la plupart ne donnent pas d'erreur la première fois.

**Ranger un enregistrement dans un dictionnaire ou dans un tuple quand tu as déjà un moule.** Un tuple de six éléments oblige à se souvenir de lequel est lequel ; un dictionnaire avec des clés de texte transforme les fautes de frappe en `None` lointains. Si les données ont une forme fixe, cette forme mérite un nom : `@dataclass`.

**Croire qu'un `dataclass` valide ses champs.** `Servicio(nombre=5, url=None)` se construit sans protester (5.1.2) : les annotations disent ce que tu attends, mais ne le vérifient pas à l'exécution. Le coût est une mauvaise donnée qui voyage dans tout le programme jusqu'à ce qu'elle échoue loin de là. Ce qui vient de l'extérieur se valide à l'entrée, et c'est la Leçon 6.

**Laisser des textes isolés là où il y a déjà un `Enum`.** C'est le plus traître. Si tu changes `clasificar` pour qu'elle renvoie `Estado.LENTO` mais qu'ailleurs dans le programme il reste un `if estado == "LENTO"`, cette comparaison **ne sera jamais vraie** (5.2 : un membre n'est pas égal à son texte), et le programme continuera de tourner sans prévenir. Quand tu migres des textes vers un `Enum`, cherche tous les endroits qui comparent.

**Écrire `case NOMBRE:` en voulant comparer.** Cela capture, ne compare pas. Si tu veux comparer avec une constante, utilise un nom avec un point (`Estado.CAIDO`) ou une garde (`case c if c == LIMITE`).

**Mettre une collection mutable comme champ d'un moule gelé.** `frozen` protège le champ, pas ce que le champ contient : une liste rangée dans une instance gelée peut continuer d'être modifiée de l'intérieur (`fig05_08.py`). Le coût est une garantie qui semble exister et n'existe pas. Dans le `revisor`, les champs sont des textes, des entiers, `None` et d'autres moules gelés.

**Construire des instances par position quand il y a beaucoup de champs.** `Servicio("notificaciones", "https://notificaciones.example", 1000)` se lit ; avec six champs, personne ne sait lequel est le quatrième. Au-delà de deux ou trois, par nom : `Servicio(nombre=..., url=..., timeout_ms=...)`.

## Exercices

Essaie chacun avant de regarder les solutions.

### Exercice 1 — Deux services de plus, et une moyenne seulement de ceux qui sont en marche

(a) Ajoute les deux services supplémentaires du `revisor` à la version de 5.4 : `facturacion` (répond avec le code 503 en 95 ms) et `notificaciones` (avec un délai d'attente de 1000 ms, n'obtient pas de réponse : « tiempo agotado »). Tu dois toucher **deux** endroits. Avant d'exécuter, prédis les deux dernières lignes de la sortie : celle de la ligne de `notificaciones` et le récapitulatif. (b) Ajoute à la fin de `main` une ligne qui imprime la moyenne des temps des services `ARRIBA` seulement, sans arrondir. Le plus indiqué est de le faire avec une compréhension.

### Exercice 2 — Provoque quatre erreurs et lis-les

Ouvre le REPL avec `python` depuis ton dossier du `revisor`, importe ce qu'il faut de `modelo` et provoque ces quatre erreurs, une par une : (a) affecter `timeout_ms` à une instance de `Servicio` ; (b) `Estado("ROTO")` ; (c) `Estado.ARIBA` ; (d) dans un fichier de ton dossier `practica/`, un `dataclass` avec un champ `etiquetas: list[str] = []`. Pour chacune, écris dans ton journal de bord la **dernière ligne** et, avec tes mots, ce qu'elle veut dire et comment on la corrige.

### Exercice 3 — Un code sans temps

Que renvoie `clasificar(200, None)`, c'est-à-dire un service qui a répondu avec 200 mais dont on n'a pas de temps mesuré ? Prédis-le deux fois : avec la `clasificar` de la Leçon 3 (celle qui renvoie des textes) et avec celle d'aujourd'hui (celle de `match`). Vérifie ensuite depuis ton dossier du `revisor`, avec `from modelo import clasificar`. Pourquoi la règle donne-t-elle ce résultat et non `LENTO` ? Et enfin : que se passerait-il si tu retirais de la condition la partie `tiempo_ms is not None` ?

## Solutions

### Solution 1

(a) Dans `revision.py`, `SIMULADO` gagne deux lignes :

```python
    "reportes": (None, None, "sin conexión"),
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
}
```

Et dans `revisor.py`, `SERVICIOS` gagne deux services :

```python
    Servicio("reportes", "https://reportes.example"),
    Servicio("facturacion", "https://facturacion.example"),
    Servicio("notificaciones", "https://notificaciones.example", timeout_ms=1000),
]
```

La sortie complète :

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

Le récapitulatif est `6 servicios · 2 arriba · 1 lento · 3 caídos`, et la moyenne sort à 656 ms parce qu'elle est calculée par les **quatre qui ont eu un temps** (142, 2300, 87 et 95, qui font 2624, divisé par 4). Remarque que `facturacion` compte dans la moyenne même s'il est en panne : il a répondu, avec un 503 et 95 ms. `notificaciones` n'a pas de temps et ne compte pas. Remarque aussi la ligne de `notificaciones` : c'est le même débordement que tu as vu dans la Leçon 4, avec le nom collé à l'état parce qu'il mesure 14 lettres et la colonne 12 ; la Leçon 11 le résout en calculant la largeur à partir du nom le plus long. Et la troisième observation est celle qui amène la leçon suivante : pour vérifier deux services de plus, tu as dû **éditer le code**, dans deux fichiers.

(b) On importe `Estado` et on ajoute la compréhension à la fin de `main` :

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

La dernière ligne de la sortie est :

```text
114.5
```

(142 et 87 font 229, divisé par 2 cela donne 114.5.) La condition `r.tiempo_ms is not None` n'est pas un ornement. Un service `ARRIBA` peut ne pas avoir de temps : `clasificar(200, None)` renvoie `Estado.ARRIBA`, parce que sans temps mesuré il n'y a pas de preuve de lenteur. Si ce `None` arrivait à `sum`, le programme échouerait avec un `TypeError`. Et de plus `tiempo_ms` est annoté comme `int | None`, et celui qui lit le code (ou `mypy`, dans la Leçon 8) a besoin de voir que le `None` a déjà été écarté avant d'additionner.

### Solution 2

Les quatre dernières lignes, chacune mesurée :

```text
dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'
```

`FrozenInstanceError` : l'instance est gelée. Correction : ne pas affecter ; en fabriquer une autre avec `replace(servicio, timeout_ms=...)`.

```text
ValueError: 'ROTO' is not a valid Estado
```

`ValueError` : il n'existe pas de membre d'`Estado` avec la valeur `ROTO`. Correction : utiliser l'une des trois valeurs permises, ou `Estado.CAIDO` directement, qui ne passe même pas par le texte.

```text
AttributeError: type object 'Estado' has no attribute 'ARIBA'. Did you mean: 'ARRIBA'?
```

`AttributeError` : `Estado` n'a pas de membre appelé `ARIBA`, et Python suggère celui qui lui ressemble. Correction : celui qu'il suggère. C'est la faute de frappe que l'`Enum` est venu attraper, et il l'attrape à la ligne où elle se produit.

```text
ValueError: mutable default <class 'list'> for field etiquetas is not allowed: use default_factory
```

`ValueError` à la **définition** de la classe, avant de créer la moindre instance. Correction : `etiquetas: list[str] = field(default_factory=list)`, comme dans `fig05_08.py`.

### Solution 3

Les deux versions renvoient **ARRIBA** : celle de la Leçon 3, le texte `"ARRIBA"` ; celle d'aujourd'hui, `Estado.ARRIBA`. Depuis le dossier du `revisor` :

<!-- frag: codigo_sin_tiempo.py -->
```python
from modelo import clasificar

print(clasificar(200, None))
```

```text
Estado.ARRIBA
```

La raison est dans la troisième règle, qui est la même depuis la Leçon 2 : un service est `LENTO` s'il a **répondu et mis** 1000 ms ou plus. Avec `None`, il n'y a pas de temps mesuré, donc pas de preuve de lenteur, et la seule chose qu'on sait est qu'il a répondu avec un bon code : `ARRIBA`. Les deux versions traitent le cas de la même façon parce que les deux demandent `tiempo_ms is not None` avant de comparer. Dans le `revisor`, ce cas ne se produit pas (un service qui a répondu apporte toujours son temps), mais `tiempo_ms` est annoté comme `int | None`, et la fonction doit donner une réponse pour tout ce que sa signature admet.

Si tu retirais `tiempo_ms is not None`, la comparaison `None >= 1000` arriverait à être évaluée et le programme s'arrêterait avec :

```text
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
```

C'est la même erreur que dans la Leçon 2, quand les questions étaient dans le mauvais ordre.

## Comment savoir que j'ai réussi

- [ ] Dans `~/curso-python/revisor/`, `python revisor.py` imprime sept lignes (l'en-tête, quatre lignes, une ligne vide et le récapitulatif), et la dernière est `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Avec les deux services supplémentaires de l'exercice 1, la dernière ligne est `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`, et la ligne de `notificaciones` sort avec le nom collé à l'état (et tu sais pourquoi).
- [ ] Dans le REPL, affecter `timeout_ms` à un `Servicio` échoue avec `dataclasses.FrozenInstanceError: cannot assign to field 'timeout_ms'`, et `Estado("ROTO")` échoue avec `ValueError: 'ROTO' is not a valid Estado`.
- [ ] Tu peux écrire de mémoire `clasificar` avec `match` : sans code c'est `CAIDO`, un code de 400 ou plus c'est `CAIDO`, un temps de 1000 ou plus c'est `LENTO`, et le reste est `ARRIBA`.
- [ ] Tu peux expliquer avec tes mots la différence entre `==` et `is` pour deux `Servicio` égaux, pourquoi `Estado.LENTO == "LENTO"` est `False` et ce que fait `replace`.
- [ ] Tu as noté dans le [journal de bord](bitacora.md) ce qui t'a donné le plus de mal : ce que tu notes là est ce que tu dois revoir.

## Résumé

Réponds sans regarder la leçon :

1. Qu'est-ce qu'une classe et qu'est-ce qu'une instance ? Qu'ajoute `@dataclass` à une classe, et qu'ajoute `frozen=True` ?
2. Qu'y gagne-t-on avec `@dataclass(frozen=True)` face à un dictionnaire ou à un tuple ? Que fait `replace` ?
3. Que compare `==` entre deux `Servicio`, et que compare `is` ?
4. Pourquoi `Estado.LENTO == "LENTO"` donne-t-il `False`, et comment obtient-on le texte d'un membre ?
5. Dans quel ordre `match` essaie-t-il ses cas, et que fait le joker `case _` ?
6. Dans un `match`, que fait un nom isolé comme `case LIMITE:` ? Comment compare-t-on avec une constante ?
7. Pourquoi `linea` a-t-elle changé de signature dans cette leçon, et qu'y a-t-elle gagné ?

## Pour aller plus loin

- [Python, « dataclasses »](https://docs.python.org/3/library/dataclasses.html) — la référence complète du module : `frozen`, `field`, `replace` et tout ce que cette leçon n'a pas utilisé. En anglais, comme presque toute la documentation officielle. Consulté le 7 octobre 2026.
- [PEP 557, « Data Classes »](https://peps.python.org/pep-0557/) — le document qui a proposé `dataclass` et explique pour quels cas il a été pensé et pour lesquels non. Consulté le 7 octobre 2026.
- [Python, « Enum HOWTO »](https://docs.python.org/3/howto/enum.html) — le guide officiel des énumérations, des bases jusqu'aux types dérivés. Consulté le 7 octobre 2026.
- [PEP 636, « Structural Pattern Matching: Tutorial »](https://peps.python.org/pep-0636/) — le tutoriel officiel de `match`, qui va bien plus loin que cette leçon. Consulté le 7 octobre 2026.
