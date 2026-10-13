# Leçon 4 — Collections

**Durée :** 2 × 90 min (la première session va jusqu'à la fin de 4.2 ; la seconde commence en 4.3)

**Ce que tu construis :** le `revisor` sans listes parallèles : les données de chaque service voyagent ensemble, dans un dictionnaire qu'on interroge par le nom du service

**Ce que tu apprends :** `list`, `tuple`, `dict` et `set` ; les compréhensions ; copie contre référence ; ne pas modifier ce qu'on parcourt ; `KeyError` et `IndexError`

**D'où tu viens.** Tu arrives avec le projet de la [Leçon 3](03-bucles-funciones-modulos.md) : deux fichiers, `formato.py` et `revisor.py`. Le premier sait mettre en forme le temps et composer l'en-tête et chaque ligne ; le second range les données, classe chaque service et parcourt les quatre pour les imprimer. Cela fonctionne, et le tableau sort correctement. Mais les données des services vivent dans **trois listes parallèles**, `NOMBRES`, `CODIGOS` et `TIEMPOS_MS`, qui ne se correspondent que par la position : le nom numéro 2 va avec le code numéro 2 et avec le temps numéro 2. Dans l'exercice de la Leçon 3, tu as ajouté `facturacion` à deux listes, oublié la troisième, et vu l'`IndexError` ou la ligne erronée que cela produit. C'est cette fragilité qu'on supprime aujourd'hui.

**Ce que cette leçon ne fait pas.** Elle ne donne pas encore à chaque service une forme propre avec un nom (un `Servicio`, un `Estado`) : c'est la [Leçon 5](05-modelo-de-datos.md), qui s'appuie sur tout ce qui est vu aujourd'hui. Elle ne lit pas non plus la configuration depuis un fichier (les services restent écrits à la main dans le code ; la [Leçon 6](06-errores-archivos-datos.md) les en sort), n'intercepte pas d'erreurs avec `try` et n'interroge aucune adresse d'internet : les codes et les temps sortent d'un tableau simulé à l'intérieur du programme.

Tu travailles dans ton dossier `~/curso-python/revisor/`. Les petits programmes de la leçon (ceux qui ne font pas partie du projet) tu peux les enregistrer dans un sous-dossier `practica/` à l'intérieur, pour qu'ils ne se mélangent pas aux fichiers du `revisor`. Toutes les commandes supposent que l'environnement virtuel de la Leçon 1 est actif, donc on écrit `python`, et non `python3`.

## À la fin, tu seras capable de

- Choisir entre liste, tuple, dictionnaire et ensemble selon ce que tu vas ranger et la façon dont tu vas le chercher, et écrire chacun avec son annotation de type (`list[str]`, `dict[str, int | None]`, `set[str]`).
- Lire un `IndexError` et un `KeyError`, dire quelle position ou quelle clé a manqué, et utiliser `.get` quand l'absence est un cas normal et non une erreur.
- Réécrire une boucle qui construit une liste sous la forme d'une compréhension, et savoir quand il vaut mieux la laisser en boucle.
- Prédire ce qui se passe avec `b = a` quand `a` est une liste, copier de façon superficielle et profonde, et expliquer pourquoi modifier une liste pendant qu'on la parcourt donne des résultats faux sans prévenir.
- Réécrire le `revisor` sans listes parallèles : un dictionnaire qui range, pour chaque nom, un tuple avec son code, son temps et son erreur, et un parcours qui ne dépend plus de l'alignement de trois listes.

## Le pourquoi avant le comment

Ouvre le `revisor.py` de la Leçon 3 et regarde comment est représenté `inventario` : le texte `"inventario"` dans `NOMBRES[1]`, le nombre `200` dans `CODIGOS[1]` et le nombre `2300` dans `TIEMPOS_MS[1]`. Trois valeurs qui appartiennent à une même chose, rangées à trois endroits différents. Pour ajouter un service, il faut te souvenir de toucher trois listes et de les toucher dans le même ordre, et Python ne te prévient pas si tu te trompes : si tu oublies la troisième, le programme échoue en arrivant au cinquième service, ou pire, il associe le code d'un service au temps d'un autre et le tableau sort bien formaté et **faux**. C'est la règle de toujours en programmation : une donnée écrite à deux endroits finit par différer.

La solution est **un seul endroit pour chaque donnée**, et pour cela il faut des formes de regrouper des valeurs. Python en fournit quatre (liste, tuple, dictionnaire et ensemble), chacune pensée pour une question différente : « dans quel ordre sont-ils ? », « quel est celui de ce nom ? », « ai-je déjà vu cette valeur ? ». Cette leçon les présente une par une (4.1), avec les deux outils qui permettent de les construire et de les manier sans surprises : les compréhensions (4.2) et la prudence avec les copies (4.3). À la fin (4.4), tu les utilises pour réécrire le `revisor` : les données de chaque service vivent désormais ensemble, sous leur nom, et les trois listes parallèles disparaissent. La leçon suivante fait le pas qui manque, donner un nom propre aux choses du problème (un `Servicio`, un `Estado`), et pour le faire elle a besoin de tout ce qui est vu aujourd'hui.

À la fin de la leçon, le `revisor` fera ceci :

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

C'est exactement le tableau de la Leçon 3, lettre pour lettre, et c'est voulu : ce qui change aujourd'hui n'est pas ce que le programme imprime, mais la façon dont il range ses données à l'intérieur. Un changement de ce genre, qui laisse le résultat identique et améliore la structure, a un énorme avantage : il se vérifie en comparant les deux sorties. Ce que gagne le programme ne se voit pas dans le tableau mais quand on le modifie, et tu le vérifieras dans l'exercice 3 : ajouter un service cesse d'être une opération sur trois listes qu'il faut toucher dans le même ordre.

## Les concepts

### 4.1 Les quatre collections

Une **collection** est une valeur qui range d'autres valeurs. Python en fournit quatre d'usage quotidien, et on les distingue par deux questions. La première : peut-on la modifier après l'avoir créée ? Ce qu'on peut modifier s'appelle **mutable**, et ce qu'on ne peut pas, **immuable** ; la liste, le dictionnaire et l'ensemble sont mutables, le tuple non. La seconde : comment trouve-t-on un élément ? Par sa **position** (liste et tuple), par son **nom** (dictionnaire) ou simplement en demandant s'il **y est ou n'y est pas** (ensemble). Vois chacune avec un exemple du `revisor` et, à la fin, en 4.1.5, il y a un tableau pour décider.

#### 4.1.1 La liste : des valeurs en ordre

Tu as déjà utilisé la liste minimale dans la Leçon 3 : le littéral avec crochets, `len`, `.append` et `lista[i]`. Ici on la voit complète. Une **liste** range des valeurs dans un ordre, peut être modifiée et s'écrit entre crochets. Enregistre le programme suivant sous le nom `fig04_01.py` dans ton dossier `practica/` et exécute-le :

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

Ligne par ligne :

- `nombres[0]` et `nombres[3]` demandent le premier et le quatrième élément. Les positions, qu'on appelle **indices**, commencent à **0** : avec quatre éléments, les positions valides sont 0, 1, 2 et 3. C'est pourquoi la dernière position d'une liste de `len(nombres)` éléments est `len(nombres) - 1`, et non `len(nombres)`.
- `nombres[-1]` et `nombres[-2]` comptent depuis la fin : `-1` est le dernier, `-2` l'avant-dernier. C'est la manière commode de demander « le dernier » sans rien calculer.
- `nombres[1:3]` est une **tranche** (en anglais, *slice*) : les éléments depuis la position 1 **jusqu'à la 3 non incluse**, c'est-à-dire les positions 1 et 2. Elle renvoie une nouvelle liste avec `['inventario', 'pagos']`. Le « non incluse » est une règle qui déconcerte une fois et qu'ensuite on utilise sans y penser : `nombres[1:3]` a `3 - 1 = 2` éléments, et `nombres[0:len(nombres)]` est la liste entière. [Le tutoriel Python](https://docs.python.org/3/tutorial/introduction.html#lists) explique les tranches avec plus d'exemples.
- `len(nombres)`, tu la connais déjà. Avec `sorted`, `sum`, `min` et `max`, c'est l'une des **fonctions intégrées** (*built-in*) : elles viennent avec Python et s'utilisent sans rien importer.
- `"pagos" in nombres` est une autre façon d'utiliser le mot `in`, le même que tu as déjà vu dans `for ... in` : ici il répond `True` ou `False` selon que la valeur **est** dans la liste ou non. Attention, avec une liste Python la vérifie élément par élément ; avec de courtes listes, cela ne change rien, et en 4.1.4 tu verras une collection beaucoup plus rapide pour cette question.
- `nombres.append("facturacion")` ajoute à la fin, et **modifie la liste qui existe déjà** (il n'en crée pas une autre). `nombres.pop()` retire le dernier élément et le renvoie, de sorte que `ultimo` vaut `"facturacion"` et que la liste a de nouveau quatre éléments. Que `append` et `pop` modifient la liste qui existe déjà, c'est ce que signifie « mutable », et cela a des conséquences que tu verras en 4.3.
- `sorted(tiempos_ms)` renvoie une **nouvelle** liste triée et laisse l'originale comme elle était : c'est pourquoi la seconde partie de la ligne montre toujours `[142, 2300, 87]`. En revanche `tiempos_ms.sort()` trie **la liste elle-même** et ne renvoie rien (à strictement parler, il renvoie `None`). [La documentation le dit ainsi](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types) : pour te rappeler qu'il agit « par effet de bord », `sort` ne renvoie pas la liste triée, et pour en demander une nouvelle il existe `sorted`. Cette distinction entre « il change celle que j'ai » et « il m'en donne une nouvelle » revient dans tout Python, et devient un piège courant (tu la verras dans « Ce qui se fait de travers »).
- `sum`, `min` et `max` additionnent, cherchent le plus petit et cherchent le plus grand des nombres de la liste : 87 + 142 + 2300 = 2529, qui est la somme des temps que tu utiliseras dans le récapitulatif.

Une liste peut mélanger n'importe quoi : textes, nombres, autres listes. Dans le `revisor`, il convient que chaque liste ne range qu'**une seule sorte de chose** (que des noms, ou que des temps), parce qu'ainsi tu sais à quoi t'attendre de chaque élément et parce que les annotations de type de 4.1.5 l'expriment facilement.

Maintenant, l'erreur. Demander une position qui n'existe pas :

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

Lis le *traceback* comme tu l'as appris dans la Leçon 1 : de la dernière ligne vers le haut. `IndexError: list index out of range` dit que l'indice est hors de la plage de la liste. Au-dessus, Python te désigne la ligne et marque avec une rangée de `~` et de `^` l'expression qui a échoué : `nombres[4]`. La liste a quatre éléments, avec des positions de 0 à 3, et la 4 n'existe pas. C'est la même erreur que te donnait la Leçon 3 quand l'une des trois listes parallèles était plus courte que les autres. (Python écrit dans le *traceback* le chemin complet de ton fichier ; dans cette leçon on le raccourcit en `File "fig04_02.py"` pour que le texte soit le même pour tous, et sur ton écran tu verras le chemin tel qu'il est sur ton ordinateur.)

#### 4.1.2 Le tuple : un groupe fixe de valeurs

Un **tuple** ressemble à une liste avec des parenthèses au lieu de crochets, mais il a une différence qui change à quoi il sert : **on ne peut pas le modifier**. Une fois créé, ses positions restent fixes. Et la différence d'usage est plus profonde que la syntaxe : la liste est « une quantité variable de choses du même type » (quatre noms, ou vingt), tandis que le tuple est « une quantité **fixe** de choses qui signifient chacune quelque chose de différent par leur position ». Le résultat de la vérification d'un service, par exemple, est toujours trois choses : le code, le temps et l'erreur s'il y en a eu une.

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

- `resultado = (200, 142, None)` crée un tuple de trois éléments. Il se lit avec des indices comme une liste : `resultado[0]` est le code.
- `codigo, tiempo_ms, error = resultado` **déballe** (en anglais, *unpacking*), comme le faisait `for i, nombre in enumerate(...)` dans la Leçon 3, où chaque tour fournissait un couple, qui est en réalité un tuple de deux : il répartit les trois éléments du tuple entre trois noms, dans l'ordre. C'est beaucoup plus lisible que `resultado[0]`, `resultado[1]`, `resultado[2]`, parce que chaque valeur reçoit un nom qui dit ce qu'elle est.
- Le `for nombre, ms in pares:` est le même déballage qu'`enumerate`, maintenant avec tes propres couples : chaque élément de `pares` est un tuple de deux, et `nombre` et `ms` reçoivent ses moitiés. Tu le reverras dès que tu arriveras aux dictionnaires.
- Un tuple d'**un seul élément** exige la virgule : `(200,)` est un tuple ; `(200)` ce sont des parenthèses autour d'un nombre, et c'est simplement `200`, comme le montre le `type` de la dernière ligne. [Le tutoriel signale ce cas](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) comme une bizarrerie de la syntaxe. En pratique, tu ne l'écriras presque pas, mais tu la liras, et la confondre ne prévient pas.

Si le nombre de noms ne coïncide pas avec celui des éléments, Python le rejette au lieu de répartir en trop ou en moins en silence :

<!-- frag: desempaque.py -->
```python
codigo, tiempo_ms = (200, 142, None)
```

À l'exécution, la dernière ligne du *traceback*, qui est celle qui compte, dit « trop de valeurs à déballer ». En Python 3.12 :

```text
ValueError: too many values to unpack (expected 2)
```

et en 3.14 elle ajoute combien il en a reçu :

```text
ValueError: too many values to unpack (expected 2, got 3)
```

Quand une fonction renvoie « plusieurs choses », ce qu'elle renvoie est un tuple : `return codigo, tiempo_ms` crée un tuple de deux, et celui qui appelle le déballe avec `codigo, tiempo_ms = f(...)`.

Et que se passe-t-il si tu essaies d'en modifier un ?

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

`TypeError: 'tuple' object does not support item assignment` : « l'objet tuple n'admet pas l'affectation à une position ». Ce n'est pas une défaillance, c'est la garantie du tuple : ce qu'il a rangé, reste. Si tu as besoin d'un autre avec une valeur différente, tu crées un autre tuple. Cette garantie est utile pour des données qui décrivent un fait qui a déjà eu lieu, comme le résultat d'une vérification. Mais remarque le coût : `resultado[1]` ne dit pas que c'est le temps ; seule ta mémoire le dit. Quand un tuple grandit jusqu'à cinq ou six éléments, personne ne se rappelle lequel est lequel. C'est la limitation que résout le `dataclass` de la Leçon 5.

#### 4.1.3 Le dictionnaire : des valeurs avec un nom

Pense à ce dont a besoin `revisar` pour le service `pagos` : pas « le troisième élément », mais « les données de `pagos` ». Un **dictionnaire** (`dict`) range des paires **clé : valeur** et s'interroge par la clé. Il s'écrit entre accolades, et la clé et la valeur sont séparées par deux-points.

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

- `tiempos_ms["pagos"]` cherche la clé `"pagos"` et renvoie sa valeur, 87. À la différence d'une liste, ici peu importe à quelle place elle se trouve : ce qui compte, c'est son nom. Les clés sont uniques (un dictionnaire ne peut pas avoir deux fois `"pagos"`) ; les valeurs peuvent se répéter et être de n'importe quelle sorte, même `None`, comme celle de `reportes`.
- `len(tiempos_ms)` compte les paires. `"pagos" in tiempos_ms` demande si **la clé** existe (pas la valeur), et c'est rapide même si le dictionnaire est énorme.
- `tiempos_ms.get("gateway")` est la manière de demander avec calme. Avec des crochets, une clé qui n'existe pas est une erreur (tu la provoques plus bas, dans « L'erreur que tu vas voir ») ; avec `.get`, il renvoie `None` s'il ne la trouve pas, ou la valeur que tu lui donnes comme second argument : `.get("gateway", "sin dato")` renvoie `"sin dato"`.
- Attention à la ligne de `reportes`, qui est le piège de cette méthode. `.get("reportes")` renvoie `None`... et `.get("gateway")` aussi. **La même réponse pour deux situations différentes :** une clé qui n'existe pas, et une clé qui existe et vaut `None`. L'avant-dernière ligne le met en évidence : `"reportes" in tiempos_ms` est `True` mais son `.get` est `None` ; `"gateway"` n'y est pas et son `.get` est aussi `None`. Quand la différence compte, on demande d'abord avec `in`.
- `tiempos_ms["facturacion"] = 95` **ajoute** une paire si la clé n'existait pas (et si elle existait, remplace sa valeur). Les dictionnaires, comme les listes, peuvent être modifiés.
- `tiempos_ms.items()` fournit les paires une par une, chacune sous forme de tuple `(clave, valor)` (comme `enumerate` fournissait des couples), et le `for nombre, ms in ...` les déballe, comme tu l'as vu dans la section précédente. Les dictionnaires **se souviennent de l'ordre dans lequel tu as ajouté les clés** : [la documentation le garantit](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) (« les dictionnaires préservent l'ordre d'insertion »), c'est pourquoi `facturacion` sort en dernier.
- `list(tiempos_ms)` convertit en liste ce qu'on obtient en parcourant directement le dictionnaire, et ce sont **les clés**. Il est important de s'en souvenir : `for nombre in tiempos_ms:` parcourt des noms, pas des paires. `tiempos_ms.values()` fournit les valeurs, et `tiempos_ms.keys()` existe pour les clés, mais il n'est presque jamais nécessaire de l'écrire.

Une restriction qu'il convient de connaître dès maintenant : la clé d'un dictionnaire doit être quelque chose qui ne change pas. Les textes, les nombres et les tuples de ceux-ci conviennent ; une liste ne convient pas comme clé. [Le glossaire appelle **hachable**](https://docs.python.org/fr/3/glossary.html#term-hashable) (*hashable*) ce qui peut être utilisé ainsi. L'essayer donne un `TypeError: unhashable type: 'list'`, que tu verras en 4.1.4 à côté de l'ensemble.

#### 4.1.4 L'ensemble : « l'ai-je déjà vu ? »

Un **ensemble** (`set`) range des valeurs **sans répétition et sans ordre**. Il sert à deux choses : retirer les doublons, et demander « cette valeur y est-elle ? » très rapidement. Quand tu écris `{"catalogo", "pagos"}`, avec des accolades et sans deux-points, c'est un ensemble.

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

- `set(registrados)` convertit la liste en ensemble et, au passage, écarte les répétitions : cinq noms enregistrés, trois distincts. C'est la façon la plus courte de compter « combien de valeurs différentes il y a ».
- L'ensemble est imprimé dans `sorted(...)` exprès, et ce n'est pas un ornement : **un ensemble n'a pas d'ordre**, et pour les textes l'ordre dans lequel Python les montre change d'une exécution à l'autre, parce que [la documentation du langage explique](https://docs.python.org/3/reference/datamodel.html#object.__hash__) que les valeurs de `hash` des textes portent un « sel » imprévisible qui change à chaque démarrage de Python. En le mesurant pour cette leçon, le même ensemble `{"catalogo", "inventario", "pagos", "reportes"}` est sorti dans des ordres différents d'une exécution à l'autre, et c'est pourquoi tu verras `sorted` à chaque impression d'un ensemble : pour que la sortie soit toujours la même. Règle pratique : **ne te fie jamais à l'ordre d'un ensemble ; si tu as besoin d'un ordre, convertis-le avec `sorted`**.
- Les opérateurs entre ensembles sont ceux des mathématiques : `-` est la **différence** (ce qui est dans l'un et pas dans l'autre : ceux qui ne sont pas en marche), `&` l'**intersection** (ce qui est dans les deux) et `|` l'**union** (tout ce qui est dans l'un ou l'autre). `.add` ajoute une valeur et il ne se passe rien si elle y était déjà, ce qui est justement l'intérêt : `arriba.add("pagos")` ne duplique rien.
- La dernière ligne est un piège classique. **`{}` vide n'est pas un ensemble vide, c'est un dictionnaire vide** : la syntaxe des accolades a d'abord été utilisée pour les dictionnaires. Pour un ensemble vide, `set()`. [Le tutoriel le souligne](https://docs.python.org/3/tutorial/datastructures.html#sets) et le `type` ci-dessus le vérifie.

Les éléments d'un ensemble doivent eux aussi être hachables, pour la même raison que les clés du dictionnaire : Python les place d'après un nombre calculé à partir de leur valeur, et si la valeur pouvait changer, ce nombre aussi. Si tu essaies d'y mettre une liste, le message change d'une version à l'autre, et cela vaut la peine de voir les deux :

<!-- frag: hashable.py -->
```python
datos = {["catalogo"]: 1}
```

En Python 3.12, la dernière ligne est celle-ci :

```text
TypeError: unhashable type: 'list'
```

Et en 3.14, qui rédige mieux l'avertissement, elle dit :

```text
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

Les deux signifient la même chose : une liste ne peut pas être une clé. Ce que tu dois retenir est le mot `unhashable`.

Un usage réel dans le `revisor` : détecter des noms répétés. Un ensemble de « ceux que j'ai déjà vus » et un autre de « ceux qui se répètent » le résolvent en un seul parcours. Mais cette fonction utilise des annotations de type pour les collections, ce qui est l'étape suivante.

#### 4.1.5 Annoter les collections et choisir la bonne

Dans la Leçon 3, tu as annoté des types simples : `int`, `str`, `int | None`. Avec les collections, on ajoute **de quoi** est faite la collection, entre crochets : `list[str]` est « liste de textes », `set[str]` est « ensemble de textes », `dict[str, int | None]` est « dictionnaire dont les clés sont des textes et les valeurs des entiers ou `None` », et `tuple[int | None, int | None, str | None]` est « tuple de trois éléments : un entier ou `None`, un autre entier ou `None`, et un texte ou `None` » (le tuple annote **chaque position**, parce que chacune signifie quelque chose). Rappelle-toi ce que tu as appris dans la Leçon 0 : Python **n'oblige pas** les annotations à être respectées à l'exécution. Ce sont de la documentation que quelqu'un d'autre peut vérifier (dans la Leçon 8, `mypy`) ; aujourd'hui elles servent à ce que le code dise ce qu'il attend.

Voici la fonction qui détecte les noms répétés, avec ses annotations, et c'est la même que le modèle du `revisor` utilisera dans la Leçon 5 :

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

`vistos: set[str] = set()` annote une variable à sa création : la syntaxe est `nombre: tipo = valor`. L'annotation est nécessaire parce que `set()` seul ne dit pas de quoi est fait l'ensemble. Pour chaque nom : s'il était déjà dans `vistos`, il est ajouté à `repetidos` ; dans tous les cas il est ajouté à `vistos`. Le second appel renvoie un ensemble vide, que `sorted` montre comme `[]`. Remarque que la question `nombre in vistos` se pose avec un ensemble : elle serait tout aussi correcte avec une liste, mais avec des milliers de noms l'ensemble répond immédiatement et la liste devrait les vérifier un par un.

Lequel utiliser ? Ce tableau, tu peux le consulter chaque fois que tu hésites ; presque toujours la réponse sort de la première colonne.

| Si ce que tu ranges est... | Utilise | On cherche par | Peut-on le modifier ? | Exemple dans le `revisor` |
|---|---|---|---|---|
| une quantité variable de choses du même type, dans un ordre | `list` | position | oui | les services à vérifier |
| une quantité fixe de choses, chaque position avec son sens | `tuple` | position | non | le trio (code, temps, erreur) |
| des données qu'on demande par nom | `dict` | clé | oui | le temps de chaque service par son nom |
| des valeurs uniques, sans ordre, dont tu demandes « y est-il ? » | `set` | appartenance | oui | les noms déjà vus |

Si tu hésites entre `list` et `set`, demande-toi si l'ordre compte ou s'il peut y avoir des doublons. Si tu hésites entre `dict` et `list`, demande-toi si tu vas chercher par position ou par nom. Et si tu te surprends à écrire `resultado[2]` en devant te rappeler ce qu'était le 2, c'est le signe qu'il te faut un nom pour cela, ce qui est le sujet de la Leçon 5.

### 4.2 Compréhensions

Construire une nouvelle liste à partir d'une autre est l'une des tâches les plus courantes d'un programme, et elle s'écrit toujours de la même façon : on crée une liste vide, on parcourt l'originale, on décide si chaque élément y entre et on l'ajoute avec `.append`. Python a une forme compacte pour cela, la **compréhension** (en anglais, *comprehension*). Regarde les deux versions du même travail :

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

La première moitié est la boucle de toujours : elle crée `lentos` vide (annotée comme liste d'entiers), parcourt, filtre avec `if` et ajoute. La seconde moitié fait la même chose en **une seule ligne** :

```text
[ tiempo_ms   for tiempo_ms in tiempos_ms   if tiempo_ms >= 1000 ]
  ^qué pones   ^de dónde sale               ^condición (opcional)
```

Elle se lit presque comme une phrase : « construis une liste avec `tiempo_ms`, pour chaque `tiempo_ms` dans `tiempos_ms`, si `tiempo_ms >= 1000` ». Elle a trois parties : **ce qu'on met** dans la nouvelle liste (ce peut être le même élément ou une transformation de celui-ci, comme `f"{tiempo_ms}ms"`), **d'où cela vient** (le `for`) et, facultative, **la condition** qui décide si cela entre. [Le tutoriel Python](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions) la présente avec la même structure. La variable du `for` ne vit qu'à l'intérieur de la compréhension et ne gêne pas à l'extérieur.

Ligne par ligne pour le reste :

- `[f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]` n'a pas de condition : elle transforme chaque nombre en texte. C'est une version simple de ce que faisait `formatear_tiempo` dans la Leçon 3.
- `", ".join(textos)` est une nouvelle méthode de texte : elle **réunit** les textes d'une liste en plaçant entre eux le texte sur lequel on l'appelle. Ici, une virgule et une espace. Tu en auras besoin dans le récapitulatif du `revisor`.
- Avec des accolades et un `clave: valor`, on obtient une **compréhension de dictionnaire** : `{nombre: ms for nombre, ms in por_servicio.items() if ms is not None}` construit un nouveau dictionnaire avec les services qui ont bien un temps. Remarque que la bonne question sur `None` reste `is not None`, comme tu l'as appris dans les leçons 2 et 3.
- Avec des accolades et une seule valeur, on obtient une **compréhension d'ensemble** : les noms dont le temps est `None`. Seulement `reportes`.
- La dernière ligne est la vraie moyenne du récapitulatif. `respondieron.values()` sont les temps de ceux qui ont répondu (142, 2300 et 87) ; `sum(...)` les additionne (2529) ; `len(respondieron)` est 3 ; la barre `/` divise et **donne toujours un nombre avec des décimales**, 843.0 ; et `round(...)` l'arrondit à l'entier le plus proche, 843. Toutes les moyennes du cours se calculent ainsi, sur ceux qui ont répondu : le quatrième service n'a pas de temps à moyenner. Une note sur `round` : quand la décimale est exactement `.5`, [Python arrondit à l'entier **pair**](https://docs.python.org/3/library/functions.html#round), donc `round(0.5)` vaut 0, `round(1.5)` vaut 2 et `round(2.5)` vaut aussi 2.

<!-- frag: redondeo.py -->
```python
print(round(0.5), round(1.5), round(2.5))
```

```text
0 2 2
```

(Pour le `revisor`, cela n'a pas d'importance, parce que 2529 / 3 est exact, mais il convient de l'avoir vu une fois : c'est de ces choses qui, si tu ne les sais pas, te font chercher une erreur qui n'existe pas.)

Quand ne pas utiliser une compréhension ? Quand elle devient difficile à lire. Une condition simple ou une transformation simple y tiennent bien ; deux `for` imbriqués ou trois conditions, non : dans ce cas écris la boucle, qui peut se lire ligne par ligne. Et n'utilise jamais une compréhension uniquement pour ce qu'elle fait à l'extérieur (par exemple, pour appeler `print` sur chaque élément) : une compréhension sert à **construire une valeur**, pas à exécuter des actions.

> **Ici se termine la première session.** Tu as les quatre collections et les compréhensions : tout ce qu'il faut pour **ranger** les données autrement. Avant la deuxième session, ré-exécute les figures de 4.1 et 4.2 et change quelque chose dans chacune (un autre service, une autre condition dans la compréhension) pour prédire le résultat avant de le voir. La deuxième session traite de ce qui surprend quand on **partage** ces données, et se termine avec le `revisor` sans listes parallèles.

### 4.3 Copie contre référence, et ne pas modifier ce qu'on parcourt

Cette section explique le faux pas le plus fréquent de ceux qui viennent d'autres langages, et celui qui fait perdre le plus de temps quand on ne le connaît pas. Elle arrive maintenant parce qu'elle n'a de sens que lorsque tu as déjà des listes et des dictionnaires qu'on peut modifier.

#### 4.3.1 Un nom est une étiquette, pas une boîte

Quand tu écris `a = [1, 2]`, Python fait deux choses : il **crée** la liste quelque part en mémoire et **pose l'étiquette `a`** dessus. L'étiquette ne contient pas la liste ; elle la **désigne**. Si ensuite tu écris `b = a`, aucune seconde liste n'est créée : on pose une seconde étiquette, `b`, sur la **même**. Il y a une liste et deux noms pour elle. (Dans la Leçon 3, en comparant `==` avec `is`, tu as vu en passant que `c = a` ne copie pas la liste ; ici on voit les conséquences quand cette liste change.) [La documentation officielle l'explique](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) avec ce même cas : les variables sont des noms qui se réfèrent à des objets, et affecter une variable à une autre ne copie pas l'objet.

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

- `respaldo = principales` pose une seconde étiquette. En faisant `respaldo.append("reportes")`, la liste **unique** grandit, et c'est pourquoi `principales` porte aussi `reportes`. Personne n'a « touché » `principales` : c'est la même liste vue sous un autre nom. Le `is` que tu as vu dans la Leçon 3 le confirme : `principales is respaldo` est `True` (c'est le même objet, pas deux objets égaux).
- `principales.copy()` crée une **nouvelle** liste avec les mêmes éléments. Maintenant il y en a bien deux : ajouter `inventario` à `copia` ne touche pas `principales`, et `principales is copia` est `False`. Il existe deux autres manières d'obtenir la même chose, `list(principales)` et `principales[:]` (une tranche complète) ; les trois donnent une copie. Utilise celle qui se lit le plus clairement, et dans ce cours c'est `.copy()`.
- Pourquoi alors `a = 5; b = a; b = b + 1` ne laisse-t-il pas `a` à 6 ? Parce que `b + 1` **ne change pas le 5** : il crée un nouveau nombre, le 6, et déplace l'étiquette `b` dessus. Les nombres et les textes sont immuables : il n'y a aucun moyen de les modifier de l'intérieur, donc les partager entre deux noms est inoffensif. Le tuple l'est aussi, avec une nuance : il ne permet pas de changer ce qu'il y a à chaque position, mais si une position range une liste, **cette liste** peut bien changer, et le tuple partagé « change » avec elle (`t = ([142], 87)` suivi de `t[0].append(5)` est valide). Les tuples du `revisor` ne rangent que des nombres, des textes et `None`, donc pour eux partager est inoffensif. Le danger est dans ce qui est **mutable** : la liste, le dictionnaire et l'ensemble, et tout ce qui les porte à l'intérieur.

Un cas où cela surprend, et que tu as déjà rencontré dans la Leçon 3 : **une fonction qui reçoit une liste reçoit la liste elle-même, pas une copie**.

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

La fonction n'a rien renvoyé et pourtant `base` a changé. C'est exactement le mécanisme de la liste qui « se souvenait » des appels précédents (`registrar_caido`, dans la Leçon 3) : la valeur par défaut `[]` était une seule liste, créée une fois, que tous les appels partageaient. Avec ce qui est vu aujourd'hui, tu peux le dire d'un coup : une fonction qui reçoit une liste peut la modifier, et c'est une décision de conception qu'il faut prendre les yeux ouverts. La convention de Python suit l'exemple de `sort` et `sorted` : les méthodes qui **modifient** une collection (`append`, `sort`, `remove`) renvoient `None`, pour que tu ne les confondes pas avec celles qui renvoient quelque chose de nouveau, et celles qui renvoient quelque chose de nouveau (`sorted`, `copy`) ne touchent pas à ce qu'elles ont reçu. L'exception utile est `pop`, qui retire un élément et le renvoie aussi.

#### 4.3.2 Copie superficielle et copie profonde

`.copy()` copie la liste de l'extérieur, mais **ne copie pas ce que la liste range** : si à l'intérieur il y a d'autres listes, la copie et l'original partagent ces listes de l'intérieur. Cela s'appelle copie **superficielle** (*shallow*) ; l'alternative est la **profonde** (*deep*), qui copie aussi l'intérieur, et c'est le module `copy` qui l'offre (on l'apporte avec `import copy`, comme tu l'as appris dans la Leçon 3). [Sa documentation définit la différence](https://docs.python.org/3/library/copy.html) : la superficielle insère des références aux mêmes objets ; la profonde insère des copies, de façon récursive.

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

Avec la copie superficielle, ajouter à `superficial[1]` a aussi changé `grupos[1]` : les deux listes de l'extérieur sont distinctes, mais la liste de l'intérieur est **la même**, et le `is` le confirme. Avec `copy.deepcopy`, celle de l'intérieur a aussi été copiée, et `grupos` est restée intacte. N'utilise pas `deepcopy` par réflexe : elle copie tout ce qu'elle atteint, elle est plus lente, et parfois elle copie en trop ce qui devait être partagé. Utilise-la quand tu as vraiment besoin de deux structures imbriquées indépendantes. Dans le `revisor`, elle sera rarement nécessaire, parce que (tu le verras dans la Leçon 5) les données importantes ne seront pas modifiées : elles seront **remplacées** par d'autres.

#### 4.3.3 Ne modifie pas ce que tu parcours

La dernière conséquence du mutable est la plus traîtresse, parce qu'elle **ne donne pas d'erreur**. Si tu retires des éléments d'une liste pendant que tu la parcours avec `for`, le parcours se détraque. Retire les services dont le temps est inférieur à 100 ms. (Pour retirer une valeur d'une liste on utilise `.remove(valor)`, qui supprime la première occurrence de cette valeur.)

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

Il y avait deux valeurs inférieures à 100, le 87 et le 95, et seul le 87 a été retiré : le 95 est resté. Aucune ligne n'a échoué, et le résultat est incorrect. La raison : le `for` parcourt la liste **par position**, avec un compteur interne. Quand il arrive à la position 2 et voit le 87, il le retire ; les éléments qui venaient après se décalent d'une place vers la gauche, le 95 vient occuper la position 2, et le `for` continue avec la position 3, qui n'existe plus. Le 95 n'est jamais examiné, et personne ne le signale. [Le tutoriel Python lui-même met en garde contre cela](https://docs.python.org/3/tutorial/controlflow.html#for-statements) : le code qui modifie une collection pendant qu'il la parcourt est difficile à réussir, et le plus simple est de parcourir une copie ou de construire une nouvelle collection. Construire une nouvelle collection est justement ce que fait une compréhension :

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

Maintenant le résultat est le bon et, en prime, la liste originale reste comme elle était. Avec un dictionnaire, l'étourderie d'**ajouter ou retirer des clés** pendant que tu le parcours donne bien une erreur, parce que Python la détecte :

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

`RuntimeError: dictionary changed size during iteration` : « le dictionnaire a changé de taille pendant le parcours ». Le `for nombre in tiempos_ms` parcourt les clés, et dedans tu en as ajouté une ; Python s'en est aperçu et s'est arrêté. Remarque le mot *taille* : changer la **valeur** d'une clé qui existe déjà (`tiempos_ms[nombre] = 0`) ne change pas le nombre de clés et ne donne pas d'erreur ; ce qui échoue, c'est d'ajouter ou de supprimer des clés. Les solutions sont les mêmes : parcourir une copie (`for nombre in list(tiempos_ms):`) ou construire un nouveau dictionnaire avec une compréhension.

#### Avant le projet

Avant d'aller au projet, vérifie que tu peux faire ceci sans regarder la leçon ; c'est aussi ce qui donnera de l'aisance pour la suite :

- Écrire un dictionnaire avec les quatre services et leurs temps, en lire un avec des crochets et un autre avec `.get`, et expliquer pourquoi `.get` d'une clé qui vaut `None` trompe.
- Écrire une compréhension qui filtre une liste, et la même chose sous forme de boucle.
- Dire à voix haute ce qu'imprime `b = a; b.append(1); print(a)` si `a` est une liste, et ce qui change si `a` est un nombre.
- Expliquer pourquoi `sorted(x)` et `x.sort()` ne sont pas la même chose.

Avec cela en main, le projet d'aujourd'hui se lit sans surprises.

### 4.4 L'étape du projet : le `revisor` sans listes parallèles

Rassemble ce qui est vu aujourd'hui dans le projet. Le changement tient tout entier dans `revisor.py`. `formato.py` reste exactement comme l'a laissé la Leçon 3, parce que son travail (donner une forme de texte à un nom, un état, un temps et un détail) n'a pas changé ; il est répété ici seulement pour que le dossier de la figure soit complet :

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

Lis `revisor.py` par morceaux.

**Les données.** À la place des trois listes, il y a deux constantes. `SERVICIOS` est une **liste** de noms : les services que tu veux vérifier, dans l'ordre où tu veux les voir dans le tableau. C'est une liste parce que l'ordre compte et que la quantité peut croître. `SIMULADO` est un **dictionnaire** qui, pour chaque nom, range un **tuple de trois** avec ce que ce service « a répondu » : `(código, tiempo_ms, error)`. C'est un tuple parce que ce sont trois choses fixes qui voyagent toujours ensemble et que chaque position signifie quelque chose de différent, et l'annotation `dict[str, tuple[int | None, int | None, str | None]]` le dit avec une position par élément, comme tu l'as vu en 4.1.5. Celui de `reportes` est `(None, None, "sin conexión")` : il n'y a eu ni code ni temps, et le troisième élément dit pourquoi. Remarque ce que tu as gagné : les trois données d'`inventario` sont sur **une seule ligne**, sous son nom. Il n'y a plus aucun moyen que son code se retrouve associé au temps d'un autre service.

Pourquoi deux constantes et non une ? Parce qu'elles répondent à des questions différentes et vont suivre des chemins différents. `SERVICIOS` est **ce que tu veux vérifier** : dans la Leçon 6, elle cessera d'être écrite dans le code et sera lue depuis un fichier. `SIMULADO` joue le rôle du **réseau** : c'est ce que chaque service répond tant que le programme ne sait pas encore interroger pour de vrai, et dans la Leçon 9, quand le `revisor` interrogera chaque service, elle disparaît. Les séparer enseigne déjà quelque chose dès aujourd'hui : un service qui est dans `SERVICIOS` et pas dans `SIMULADO` est un service qui n'a pas répondu.

**`revisar`** a changé de signature. Avant, elle recevait le nom, le code et le temps, que `main` devait tirer de trois listes à la même position ; maintenant elle reçoit **seulement le nom** et cherche le reste par elle-même. La recherche est `SIMULADO.get(nombre, sin_respuesta)`, avec `.get` **exprès** : un nom qui n'est pas dans `SIMULADO` n'est pas une erreur du programme mais un service dont on n'a pas de données, et il est traité comme en panne « sin conexión ». C'est pourquoi la valeur par défaut, `sin_respuesta`, est le même tuple que celui de `reportes`. C'est le critère de 4.1.3 : `.get` quand l'absence est un cas prévu, des crochets quand elle ne devrait pas se produire. Ensuite, `codigo, tiempo_ms, error = ...` déballe le tuple en trois noms (4.1.2), et le détail se décide avec la règle de la Leçon 2, élargie avec la troisième donnée : le code sous forme de texte s'il y a eu réponse ; sinon, le texte de l'erreur ; et s'il n'y a pas non plus d'erreur, « sin conexión ». `clasificar` n'a pas changé d'une lettre.

**`main`** construit d'abord la liste des lignes avec une compréhension, `[revisar(nombre) for nombre in SERVICIOS]` (4.2), puis l'imprime sous l'en-tête. Le parcours n'utilise plus `range(len(...))` ni de positions : il parcourt les noms, un par un, comme le premier `for` de la Leçon 3. Et l'ordre du tableau est celui de `SERVICIOS`, pas celui de `SIMULADO` : celui qui décide de ce qui s'affiche et dans quel ordre, c'est la liste de ce que tu veux vérifier.

Exécute le projet depuis son dossier :

```text
$ cd fig04_15
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Le même tableau que la Leçon 3, comme promis. Compare-le avec l'exercice 1 de cette leçon-là, celui de `facturacion` : là-bas il fallait toucher trois listes dans le même ordre, et un oubli produisait un `IndexError` ou, pire, une ligne avec les données d'un autre service. Maintenant un service est un nom dans `SERVICIOS` et une ligne dans `SIMULADO`, et si tu oublies la ligne, le service apparaît comme en panne « sin conexión », ce qui est la vérité : on n'a pas de données sur lui. Tu le vérifies dans l'exercice 3.

Il reste quelque chose de gênant, et c'est le point de départ de la Leçon 5. Regarde la ligne `codigo, tiempo_ms, error = SIMULADO.get(...)` : le tuple ne dit pas ce qu'est chaque position ; seule ta mémoire le dit. Et `clasificar` renvoie toujours un texte, `"ARRIBA"`, `"LENTO"` ou `"CAIDO"`, que rien n'empêche d'écrire de travers. Donner à chaque chose du problème un nom propre que Python reconnaît est le sujet de la leçon suivante. C'est là qu'arrive aussi la ligne du récapitulatif (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`) : tu saurais déjà la compter avec les compréhensions d'aujourd'hui, mais elle sera plus claire quand chaque résultat sera une seule chose avec un nom.

## L'erreur que tu vas voir

Dans les sections précédentes, tu as déjà provoqué plusieurs erreurs à l'endroit où elles naissent (`IndexError`, `TypeError`, `ValueError`, `RuntimeError`). Voici celle que tu rencontreras le plus en travaillant avec des dictionnaires, et à la fin un tableau pour toutes les reconnaître d'un coup d'œil.

### `KeyError: 'catalgo'`

Demander à un dictionnaire une clé qu'il n'a pas. Écris `catalgo` au lieu de `catalogo` :

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

Lis-le de bas en haut, comme toujours. **La dernière ligne :** `KeyError: 'catalgo'`. Le type est `KeyError` (une erreur de clé) et le texte entre guillemets est **la clé qu'on a demandée et qui n'existe pas**, telle que tu l'as écrite ; si tu la compares aux clés du dictionnaire, la faute de frappe saute aux yeux. **Une ligne plus haut :** le programme, avec une rangée de `~` et de `^` sous l'expression qui a échoué, `SIMULADO["catalgo"]`. **Plus haut :** la ligne et le fichier. Ici il n'y a aucune fonction entre les deux, donc le *traceback* est court ; avec des fonctions qui s'appellent entre elles, il y aurait plus de lignes, et il se lit pareil : la cause immédiate est à la fin.

Deux questions avant de corriger. La première : la clé devrait-elle exister ? Si oui, c'est une faute de frappe ou de données, et le `KeyError` est **exactement ce que tu veux** : le programme s'est arrêté à l'endroit précis de l'erreur, sans laisser une fausse valeur continuer d'avancer. La seconde : est-il normal qu'elle n'existe parfois pas ? Alors le dictionnaire ne s'interroge pas avec des crochets, mais avec `.get(clave, valor_por_omisión)` ou avec un `in` préalable. C'est la raison pour laquelle `revisar`, en 4.4, utilise `.get` : un service qui n'a pas de données simulées est un cas prévu. Ce que tu **ne** dois **pas** faire, c'est utiliser `.get` partout « au cas où » : il remplace une erreur claire par un `None` qui échouera plus tard et plus loin (la Leçon 5 commence justement par un cas comme celui-là). Intercepter l'erreur avec `try`/`except` est le sujet de la Leçon 6.

### Les erreurs de cette leçon d'un coup d'œil

Quand l'une t'apparaît, cherche ici la dernière ligne. Toutes sont sorties des exécutions de cette leçon.

| La dernière ligne dit... | Ce qui s'est passé | Où tu l'as vue |
|---|---|---|
| `IndexError: list index out of range` | tu as demandé une position qui n'existe pas dans la liste | 4.1.1 |
| `KeyError: 'catalgo'` | tu as demandé une clé que le dictionnaire n'a pas | ci-dessus |
| `TypeError: 'tuple' object does not support item assignment` | tu as voulu modifier un élément d'un tuple | 4.1.2 |
| `ValueError: too many values to unpack (expected 2...` | tu as déballé dans plus ou moins de noms que d'éléments | 4.1.2 |
| `TypeError: unhashable type: 'list'` | tu as utilisé une liste comme clé ou élément d'ensemble | 4.1.4 |
| `RuntimeError: dictionary changed size during iteration` | tu as changé la taille d'un dictionnaire pendant que tu le parcourais | 4.3.3 |

Les textes du tableau sont ceux de Python 3.12, celui de ton Mint. Deux changent en 3.14, bien que l'erreur soit la même : celui du déballage ajoute combien il y en avait, `ValueError: too many values to unpack (expected 2, got 3)`, et celui de la liste comme clé dit où tu l'as utilisée : `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')` (ou `as a set element`, si c'était dans un ensemble).

## Ce qui se fait de travers

Chacune de ces négligences a un coût concret, et la plupart ne donnent pas d'erreur la première fois.

**Maintenir des listes parallèles.** Trois listes qui se correspondent par position se désalignent à cause d'un oubli, et le symptôme apparaît loin de la cause : un `IndexError` au milieu du tableau, ou une ligne avec le temps d'un autre service. Le coût est la journée perdue à chercher pourquoi le service numéro 4 dit 87 ms. Une entrée par service dans un dictionnaire, avec ses données ensemble, l'évite dès la conception.

**Ranger le résultat de `.sort()`.** `.sort()` trie la liste qui existe déjà et renvoie `None`. Qui écrit `ordenados = tiempos_ms.sort()` obtient une variable qui vaut `None`, et l'erreur apparaît là où on l'utilise :

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

La liste a bien été triée (la deuxième ligne), mais `ordenados` ne la contient pas. S'il faut une copie triée, `sorted(tiempos_ms)` ; s'il faut trier la liste elle-même, `tiempos_ms.sort()` **sans** affecter.

**Utiliser `.get` pour tout.** Il remplace une erreur claire (`KeyError`, avec la clé qui a échoué) par un `None` qui se propage et explose plus tard, ailleurs et avec un autre message. Utilise-le quand l'absence est un cas prévu, pas pour faire taire des erreurs.

**Écrire `{}` en attendant un ensemble vide.** C'est un dictionnaire vide, et l'échec arrive après, à la première opération d'ensemble :

<!-- frag: llaves_vacias.py -->
```python
vistos = {}
vistos.add("catalogo")
```

La dernière ligne du *traceback* dit :

```text
AttributeError: 'dict' object has no attribute 'add'
```

La bonne forme est `vistos: set[str] = set()`. Un ensemble vide s'écrit avec `set()`.

**Se fier à l'ordre d'un ensemble.** Cela marche « la plupart du temps » dans les tests d'une machine et échoue sur une autre, parce que l'ordre des textes change entre les exécutions. Si l'ordre compte, `sorted(...)`. Si c'est l'ordre d'arrivée qui t'importe, une liste ou un dictionnaire (qui, lui, se souvient de l'ordre d'insertion).

**Copier avec `=`.** `respaldo = principales` ne fait pas de copie : il pose un second nom. Le coût est de modifier des données « d'un autre » sans t'en rendre compte, et que le défaut apparaisse à un endroit que tu n'as pas touché. Pour copier, `.copy()` ; pour copier ce qui est imbriqué, `copy.deepcopy`.

**Modifier une collection pendant qu'on la parcourt.** Avec une liste, cela n'échoue pas et saute des éléments (4.3.3) ; avec un dictionnaire, ajouter ou retirer des clés échoue avec `RuntimeError`. Parcours une copie ou construis une nouvelle collection avec une compréhension.

**Des compréhensions illisibles.** Une compréhension avec deux `for` et trois conditions tient sur une ligne mais ne tient pas dans la tête de celui qui la lit. Si tu dois la lire deux fois, c'est une boucle. Le coût est de maintenance : celui qui la touchera ensuite (toi, dans trois mois) la réécrira.

**Un long tuple au lieu d'un nom.** Un tuple de trois éléments se retient ; un de six, non, et `resultado[4]` finit par signifier ce que chacun croit. Si tu te surprends à écrire un commentaire pour te rappeler ce qu'est chaque position, c'est le signe que ces données méritent un nom propre, ce qu'apporte la Leçon 5.

## Exercices

Essaie chacun avant de regarder les solutions.

### Exercice 1 — Prédis, exécute et corrige

Avant d'exécuter quoi que ce soit, **écris sur papier** ce qu'imprime chaque `print` de ce programme. Exécute-le ensuite dans ton dossier `practica/` et compare avec ta prédiction.

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

Ensuite, ce parcours a le défaut de 4.3.3, mais avec des valeurs `None`. Prédis ce qu'il imprime, explique pourquoi il sort ainsi et corrige-le avec une compréhension.

<!-- frag: ej1b.py -->
```python
tiempos_ms = [142, None, None, 87]
for tiempo_ms in tiempos_ms:
    if tiempo_ms is None:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
```

### Exercice 2 — Trois questions au dictionnaire

Avec ce dictionnaire, écris trois compréhensions : (a) la **liste** des noms des services dont le temps est de 1000 ms ou plus ; (b) un **dictionnaire** avec le temps en secondes (millisecondes divisées par 1000) des services qui ont bien répondu ; (c) l'**ensemble** des noms sans réponse. Veille à ce qu'aucune ne compare `None` avec un nombre.

<!-- frag: ej2_datos.py -->
```python
por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
```

### Exercice 3 — Un service de plus, et un oubli volontaire

Travaille sur le `revisor` de 4.4. (a) Ajoute `"facturacion"` à la fin de `SERVICIOS`, **sans** toucher `SIMULADO`, et avant d'exécuter, prédis sa ligne. (b) Ajoute maintenant à `SIMULADO` l'entrée de `facturacion`, qui répond avec le code 503 en 95 ms, et prédis à nouveau. (c) Enfin, ajoute `notificaciones` aux deux endroits ; dans `SIMULADO`, avec `(None, None, "tiempo agotado")`, parce qu'il n'arrive pas à répondre à temps. Prédis sa ligne et remarque comment elle se retrouve alignée. Compare chaque étape avec ce qui se passait dans l'exercice 1 de la Leçon 3, quand tu oubliais l'une des trois listes.

### Exercice 4 — Provoque trois erreurs et lis-les

Ouvre le REPL avec `python` depuis ton dossier du `revisor` (celui que tu as connu dans la Leçon 1), importe `SIMULADO` avec `from revisor import SIMULADO` et provoque ces trois erreurs, une par une : (a) `SIMULADO["catalgo"]` ; (b) la position 3 d'une liste de trois éléments ; (c) modifier le premier élément du tuple de `pagos` avec `SIMULADO["pagos"][0] = 500`. Pour chacune, écris dans ton journal de bord la **dernière ligne** et, avec tes mots, ce qu'elle veut dire et comment on la corrige. Une question en plus : pourquoi l'`import` n'a-t-il pas imprimé le tableau ?

## Solutions

### Solution 1

La première partie :

```text
['catalogo', 'pagos', 'reportes']
['catalogo', 'pagos', 'reportes']
['catalogo', 'reportes']
True False
```

`a` et `b` sont **le même objet** : `b.append("reportes")` a changé les deux, et `a is b` est `True`. `c = list(a)` est une copie faite **après** que `a` avait déjà `reportes` ; en retirant `"pagos"` de `c`, `a` et `b` ne s'en sont pas aperçus, et `a is c` est `False`. La seconde partie imprime :

```text
[142, None, 87]
```

Le `None` de la position 1 est retiré ; la liste se décale vers la gauche, le second `None` passe à la position 1, et le `for` continue avec la position 2, de sorte qu'il **ne l'examine jamais** : il reste un `None` dans une liste dont tu voulais tous les retirer. La correction construit une nouvelle liste :

<!-- frag: ej1c.py -->
```python
tiempos_ms = [142, None, None, 87]
tiempos_ms = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms is not None]
print(tiempos_ms)
```

```text
[142, 87]
```

### Solution 2

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

Trois choses à vérifier. En (a), la condition `ms is not None and ms >= 1000` interroge d'abord `None` : `and` s'arrête dès qu'une partie est fausse, donc `None >= 1000` (qui échouerait avec un `TypeError`) n'est jamais évalué. En (b), la division `ms / 1000` donne toujours un nombre avec des décimales, et c'est pourquoi `2.3` et non `2`. En (c), les accolades avec une seule valeur et sans deux-points donnent un ensemble ; avec un seul élément, il apparaît sous la forme `{'reportes'}`.

### Solution 3

(a) Avec `facturacion` dans `SERVICIOS` et sans entrée dans `SIMULADO`, le programme **ne plante pas** : `.get` ne trouve pas le nom, renvoie `sin_respuesta`, et la nouvelle ligne est celle d'un service en panne sans données :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO          —  sin conexión
```

Compare avec la Leçon 3 : là-bas, oublier une liste produisait un `IndexError` ou, pire, décalait les données d'un service à l'autre. Ici l'oubli n'affecte **que** `facturacion`, et ce que dit sa ligne est vrai : il n'y a pas de réponse de lui.

(b) Avec `"facturacion": (503, 95, None),` dans `SIMULADO`, sa ligne devient `facturacion CAIDO       95ms  503` : il a répondu, mais avec un code d'erreur, et la première règle de `clasificar` le marque en panne même s'il a été rapide. Le nom a 11 lettres et tient dans les 12 colonnes, avec une seule espace de marge.

(c) Les deux constantes deviennent ainsi (avec six noms, la liste ne tient plus sur une ligne de 88 caractères et se répartit sur plusieurs, comme les longues signatures de la Leçon 3) :

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

Et la dernière ligne sort ainsi :

```text
notificacionesCAIDO          —  tiempo agotado
```

Le nom a 14 lettres et la colonne en mesure 12, donc il déborde de sa case et se retrouve **collé à l'état**. C'est une vraie limitation du format d'aujourd'hui, et la Leçon 11 la résout en calculant la largeur à partir du nom le plus long. Remarque aussi le détail : `tiempo agotado`, le troisième élément du tuple, parce qu'il n'y a pas eu de code.

### Solution 4

Les trois dernières lignes, chacune mesurée :

```text
KeyError: 'catalgo'
```

`KeyError` avec la clé demandée entre guillemets : le dictionnaire n'a pas `catalgo`. Correction : écrire `catalogo`, ou `.get` si l'absence est normale.

```text
IndexError: list index out of range
```

`IndexError` : une liste de trois éléments a les positions 0, 1 et 2. Correction : `lista[2]`, ou `lista[-1]` pour le dernier.

```text
TypeError: 'tuple' object does not support item assignment
```

`TypeError` : un tuple ne se modifie pas de l'intérieur. Correction : si ce que `pagos` a répondu a vraiment changé, on range un nouveau tuple dans le dictionnaire, `SIMULADO["pagos"] = (500, 87, None)` ; le dictionnaire peut être modifié, le tuple non.

La question en plus : l'`import` a exécuté `revisor.py` de haut en bas, mais l'appel à `main()` est à l'intérieur de `if __name__ == "__main__":`, et à l'import, `__name__` vaut `revisor`. C'est l'idiome de la Leçon 3 qui fait son travail.

## Comment savoir que j'ai réussi

- [ ] Dans `~/curso-python/revisor/`, `python revisor.py` imprime l'en-tête et les quatre lignes, identiques à celles de la Leçon 3 et à celles de `fig04_15`.
- [ ] Dans ton `revisor.py`, il n'existe plus de `NOMBRES`, de `CODIGOS` ni de `TIEMPOS_MS`, ni aucun `range(len(...))`.
- [ ] Avec `facturacion` dans `SERVICIOS` et sans entrée dans `SIMULADO`, sa ligne dit `CAIDO` et `sin conexión`, et le programme ne plante pas ; en l'ajoutant à `SIMULADO`, elle dit `503`.
- [ ] Pour le service `reportes`, `.get` donne `None` pour deux raisons possibles, et tu peux dire lesquelles et comment les distinguer avec `in`.
- [ ] Tu peux expliquer avec tes mots la différence entre `b = a` et `b = a.copy()`, entre `sorted(x)` et `x.sort()`, et pourquoi retirer des éléments d'une liste pendant qu'on la parcourt en saute un sans prévenir.
- [ ] Tu as noté dans le [journal de bord](bitacora.md) ce qui t'a donné le plus de mal : ce que tu notes là est ce que tu dois revoir.

## Résumé

Réponds sans regarder la leçon :

1. À quelle question répond chaque collection : la liste, le tuple, le dictionnaire et l'ensemble ? Lesquelles peut-on modifier ?
2. Quelle différence y a-t-il entre `IndexError` et `KeyError`, et que dit la dernière ligne de chacun ?
3. Que renvoie `.get("reportes")` si `reportes` existe avec la valeur `None` ? Et s'il n'existe pas ? Comment distingues-tu les deux cas ?
4. Quelles trois parties a une compréhension ? Quand vaut-il mieux laisser une boucle ?
5. Si `a = [1, 2]` et que tu fais `b = a`, combien de listes y a-t-il ? Qu'est-ce qui change avec `b = a.copy()` ? Et avec `copy.deepcopy` ?
6. Pourquoi retirer des éléments d'une liste pendant qu'on la parcourt saute-t-il des éléments sans donner d'erreur ?
7. Dans le `revisor`, pourquoi `SERVICIOS` et `SIMULADO` sont-ils deux choses séparées, et que devient un nom qui est dans la première et pas dans la seconde ?

## Pour aller plus loin

- [Python, « Structures de données » (tutoriel)](https://docs.python.org/3/tutorial/datastructures.html) — listes, tuples, ensembles, dictionnaires et compréhensions, avec plus d'exemples et dans le même ordre que cette leçon. En anglais, comme presque toute la documentation officielle. Consulté le 7 octobre 2026.
- [Python, « Types intégrés »](https://docs.python.org/3/library/stdtypes.html) — la référence de chaque collection : quelles opérations elle admet et lesquelles modifient la valeur sur place. C'est à consulter, pas à lire d'une traite. Consulté le 7 octobre 2026.
- [Python, module `copy`](https://docs.python.org/3/library/copy.html) — la différence entre la copie superficielle et la copie profonde, racontée par la documentation officielle. Consulté le 7 octobre 2026.
- [Questions fréquentes sur la programmation : « Pourquoi changer la liste `y` a-t-il aussi changé la liste `x` ? »](https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x) — l'explication officielle de copie contre référence, avec le même cas que 4.3.1. Consulté le 7 octobre 2026.
