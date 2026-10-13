# Leçon 2 — Valeurs, texte et décisions

**Durée :** 90 min

**Ce que tu construis :** l'en-tête du `revisor` et la classification d'**un** service : son état, son temps et son détail, imprimés sur une ligne de tableau

**Ce que tu apprends :** trois concepts. D'abord, les valeurs et les noms (nombres, texte, vrai ou faux, et `None`) ; ensuite, le texte formaté (les f-strings) ; enfin, les décisions avec `if`, `elif` et `else`, et l'indentation comme partie de la syntaxe

**D'où tu viens.** Tu arrives de la [Leçon 1](01-instalacion.md) : tu as le dossier `~/curso-python/` avec son environnement virtuel `.venv`, l'environnement actif (l'invite affiche `(.venv)`) et, dans `~/curso-python/revisor/`, un fichier `revisor.py` d'une seule ligne qui imprime « revisor: todavía no revisa nada » (« revisor : ne vérifie encore rien »). C'est tout ce que fait ton programme jusqu'à aujourd'hui : il ne vérifie rien. Dans cette leçon, il commence à le faire, pour un service. Toutes les commandes s'écrivent comme si tu te trouvais dans `~/curso-python/revisor/`, et le programme s'exécute avec `python archivo.py`. Enregistre chaque figure de la leçon sous le nom qu'elle porte sur sa première ligne (`fig02_01.py`, `fig02_02.py`, et ainsi de suite), dans ce même dossier.

**Ce que cette leçon ne fait pas.** Il n'y a pas encore de listes, ni de fonctions, ni de répétitions. Le `revisor` d'aujourd'hui ne connaît qu'**un** seul service, rangé dans quelques variables, et le classe une fois. Vérifier les quatre à la fois, et répéter le même code sans le copier, c'est le sujet de la [Leçon 3](03-bucles-funciones-modulos.md). Aujourd'hui, on règle d'abord le plus petit : **ce qu'est une donnée, comment s'écrit une ligne du tableau et comment le programme décide si un service est en marche, lent ou en panne**.

## À la fin, tu seras capable de

- Ranger une donnée sous un nom et dire de quel type elle est (`int`, `float`, `str`, `bool` ou `None`), avec la fonction `type()`.
- Calculer avec les opérateurs d'arithmétique et de comparaison, combiner des conditions avec `and`, `or` et `not`, et demander si une valeur est `None` avec `is`.
- Composer un texte avec une f-string et aligner des colonnes avec `:<12`, `:>6` et `:.1f`.
- Écrire un `if`/`elif`/`else`, expliquer pourquoi l'indentation fait partie de la syntaxe et pourquoi l'ordre des branches change le résultat.
- Classer un service comme ARRIBA, LENTO ou CAIDO avec les quatre règles du `revisor` et imprimer sa ligne avec l'en-tête du tableau.
- Lire trois erreurs de débutant, `SyntaxError: expected ':'`, `IndentationError` et `TypeError` en additionnant un texte avec un nombre, et dire ce qui les a causées.

## Le pourquoi avant le comment

Imagine que tu travailles dans une équipe qui maintient quatre services dans une entreprise : le catalogue de produits, l'inventaire, les paiements et les rapports. Un lundi matin, quelqu'un pose la question qu'on pose tous les lundis : « lesquels fonctionnent ? ». Aujourd'hui, tu le découvres en ouvrant quatre adresses dans le navigateur et en regardant. Le `revisor`, le projet que tu vas construire dans ce cours, pose cette question à ta place et te répond avec un tableau comme celui-ci :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Regarde le tableau avec des yeux de programmeur et tu verras que chaque cellule est **une donnée d'une sorte différente**. `catalogo` est un texte. `142` est une quantité. `ARRIBA` est l'un de trois mots possibles. Et le temps de `reportes` est... rien : ce service n'a pas répondu, donc il n'y a pas de temps à afficher, et il faut pouvoir l'exprimer d'une manière qui ne soit pas d'écrire un zéro (un service qui n'a pas répondu n'a pas répondu en zéro milliseconde). Si un programme doit produire ce tableau, il a besoin de trois choses, et ce sont les trois de cette leçon :

- **Représenter les données** avec la bonne sorte : du texte pour le nom, des nombres pour le code et le temps, une valeur spéciale pour « il n'y a pas de donnée ». C'est le concept 2.1.
- **Composer la ligne** : coller le nom, l'état et le temps en colonnes alignées, et convertir 2300 millisecondes en `2.3s`. C'est le concept 2.2.
- **Décider** : si le service a répondu avec un code d'erreur, il est CAIDO ; s'il a répondu correctement mais a mis mille millisecondes ou plus, il est LENTO ; sinon, il est ARRIBA. C'est le concept 2.3.

À la fin de la leçon, tu auras un `revisor.py` d'une trentaine de lignes qui, pour le service `inventario`, imprime exactement ces deux lignes :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
inventario  LENTO       2.3s  200
```

Ce sont deux lignes des cinq du tableau, mais ce sont celles qui comptent : l'en-tête, qui ne change plus de tout le cours, et un service complet, avec ses trois décisions. Quand tu apprendras à répéter dans la Leçon 3, les trois autres services sortiront avec le même code.

Une dernière idée avant de commencer, parce qu'elle va te servir pendant tout le cours. Un programme est une liste d'instructions que Python exécute **l'une après l'autre, de haut en bas**. Quand une instruction échoue, Python s'arrête sur elle et te dit laquelle c'était ; quand une instruction ne demande rien de spécial, Python passe à la suivante. Il n'y a pas de magie en dessous : si tu veux savoir ce que fait un programme, lis-le comme le lit Python, de haut en bas et une ligne à la fois. C'est ce que tu vas faire avec chaque figure.

## Les concepts

### 2.1 Valeurs et noms

#### 2.1.1 Les valeurs et leurs types

Une **valeur** est une donnée concrète : le nombre 2300, le texte `"inventario"`, le « oui » de « a-t-il répondu ? ». Toute valeur a un **type**, qui est la sorte de donnée qu'elle est et qui détermine ce qu'on peut en faire : avec les nombres on additionne, avec les textes on colle. Python a beaucoup de types ; aujourd'hui tu en as besoin de cinq, et les cinq apparaissent dans le `revisor`.

- **`int`** (entier) : un nombre sans décimales. Le code de réponse d'un service (`200`, `503`) et le temps en millisecondes (`2300`) sont des entiers. [La documentation de Python](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) les appelle « types numériques » ; les entiers n'ont pas de taille maximale que tu aies à surveiller.
- **`float`** (décimal) : un nombre avec un point décimal, comme `2.3`. Son nom vient de *floating point* (« virgule flottante »), la manière dont les ordinateurs rangent les décimaux. Plus bas, tu verras une surprise qui vient avec eux.
- **`str`** (chaîne de texte, *string*) : une suite de caractères entre guillemets, simples ou doubles, comme `"inventario"`. Dans ce cours, on les écrit avec des guillemets doubles. Un texte peut contenir des accents et des symboles (`"sin conexión"`, `"—"`) : Python 3 stocke le texte en Unicode.
- **`bool`** (booléen) : seulement deux valeurs possibles, `True` et `False`, avec la première lettre en majuscule. C'est la réponse à une question par oui ou non, comme « le service a-t-il répondu ? ». Il porte le nom de George Boole, le mathématicien qui a formalisé la logique du vrai et du faux.
- **`None`** : la valeur qui signifie « il n'y a rien ici ». C'est la seule valeur de son propre type, qui s'appelle `NoneType`. Tu vas l'utiliser pour le temps et le code d'un service qui n'a pas répondu, et c'est la bonne réponse à « combien de temps a-t-il mis ? » quand la réponse est « il n'y a pas de réponse ».

La fonction `type()` te dit le type de n'importe quelle valeur. Et `print()` peut recevoir plusieurs valeurs séparées par des virgules : il les imprime sur la même ligne, avec une espace entre elles. Avec ces deux choses, tu peux voir les cinq types ensemble. Enregistre cette figure sous le nom `fig02_01.py` et exécute-la :

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

Ligne par ligne. La première ligne, celle qui commence par `#`, est un **commentaire** : Python ignore tout ce qui va d'un `#` jusqu'à la fin de la ligne. Il sert à ce que les personnes lisent des notes, et dans ce cours la première ligne de chaque figure est un commentaire avec son nom (`# fig02_01.py`), pour que tu saches comment l'enregistrer. Les six lignes suivantes **créent des variables**, qui est le sujet du paragraphe suivant ; remarque seulement que chacune range une valeur d'un type différent. `tiempo_ms / 1000` divise 2300 par 1000 et donne `2.3`, un `float`, même si les deux nombres du calcul étaient des entiers : la division `/` donne toujours un décimal. Ensuite, six `print` affichent chaque valeur et son type. La sortie dit `<class 'str'>`, `<class 'int'>` et ainsi de suite : en Python, « type » et « classe » sont la même idée, et le mot *class* dans la réponse ne t'oblige pas à en savoir plus sur les classes pour le moment (elles arrivent dans la Leçon 5).

Deux choses à retenir. Première : `200` et `"200"` **ne sont pas la même chose**. Le premier est un nombre, et avec lui on peut comparer et additionner ; le second est un texte de trois caractères qui se trouvent être des chiffres, et avec lui on ne peut pas calculer. Quand tu vois `200` dans la colonne DETALLE du tableau, c'est là un texte (c'est un morceau d'une ligne qu'on imprime), mais dans la variable `codigo` c'est un nombre. Seconde : `None` **n'est pas** `0`, ni `""` (le texte vide), ni `False`. C'est une valeur à part, qui dit « ici il n'y a pas de donnée ». Un service en panne qui n'a renvoyé aucun code n'a pas de « code zéro » : il n'a pas de code.

#### 2.1.2 Les noms et l'affectation

Une **variable** est un nom qui pointe vers une valeur. Elle se crée avec le signe égal :

```python
tiempo_ms = 2300
```

Cette ligne s'appelle une **affectation** et se lit de droite à gauche : d'abord on calcule la valeur de droite (2300), puis on lui donne le nom de gauche (`tiempo_ms`). Le signe `=` **ne signifie pas « est égal à »** comme en mathématiques ; il signifie « range ceci sous ce nom ». La question de savoir si deux choses sont égales s'écrit avec deux signes, `==`, et tu la verras dans un instant. Confondre les deux est l'un des faux pas les plus courants du débutant, et Python te protège de la plupart : `if codigo = 200:` est une erreur de syntaxe, parce que dans un `if` seule une question a sa place.

Un nom peut changer de valeur quand tu veux : `tiempo_ms = 2300` puis, plus bas, `tiempo_ms = 87` font que le nom pointe maintenant vers 87. L'ancienne valeur cesse simplement d'avoir un nom. Et une valeur peut avoir plusieurs noms à la fois, même si cela n'a vraiment d'importance que lorsque les valeurs peuvent être modifiées de l'intérieur, et cette histoire commence dans la Leçon 4.

Les règles pour écrire un nom sont peu nombreuses :

- Il contient des lettres, des chiffres et le tiret bas (`_`), et **ne peut pas commencer par un chiffre** : `1servicio` ne convient pas, `servicio1` oui.
- Il ne peut pas être un **mot réservé**, de ceux que Python utilise pour sa propre syntaxe (`if`, `else`, `None`, `True`...). Tu verras les autres au fur et à mesure.
- **Les majuscules comptent** : `Nombre` et `nombre` sont deux noms différents. Si tu en écris un là où tu voulais l'autre, Python ne te dira pas « tu t'es trompé de majuscule », il te dira que le nom n'existe pas.

Et il y a aussi des **conventions**, qui ne sont pas obligatoires mais que tout le monde de Python suit, parce qu'elles sont dans [le guide de style officiel, la PEP 8](https://peps.python.org/pep-0008/#naming-conventions) : les noms de variables s'écrivent en minuscules avec un tiret bas entre les mots (`tiempo_ms`, ce qu'on appelle *snake_case*), et les noms de valeurs qui **ne vont pas changer** (les constantes) s'écrivent en majuscules (`UMBRAL_LENTO_MS`). Python n'empêche pas de changer une « constante » ; la majuscule est un avertissement pour celui qui lit le code.

Ce cours ajoute deux règles propres, que tu verras dans chaque figure. **Les identifiants sont en espagnol, sans accents ni `ñ`** : `nombre`, `tiempo_ms`, `estado`. Python accepte les accents dans les noms, mais ils s'écrivent mal sur des claviers étrangers et compliquent le partage du code. Et **les unités vont dans le nom** : `tiempo_ms`, jamais `tiempo` tout court. Quand quelqu'un lit `tiempo = 2300`, il ne sait pas si ce sont des millisecondes, des secondes ou des minutes ; quand il lit `tiempo_ms = 2300`, il le sait. C'est une habitude qui évite des erreurs coûteuses : [la NASA a attribué l'échec de la sonde Mars Climate Orbiter à une erreur de navigation](https://science.nasa.gov/mission/mars-climate-orbiter/), causée par le fait de ne pas avoir converti des unités anglaises en unités métriques entre le programme au sol et celui du vaisseau.

#### 2.1.3 Opérateurs : calculer, comparer et combiner

Un **opérateur** est un symbole qui fait quelque chose avec des valeurs. Il y a trois familles et les trois servent au `revisor`.

Ceux d'**arithmétique** calculent : `+` additionne, `-` soustrait, `*` multiplie, `/` divise et renvoie toujours un `float`, `//` divise et ne garde que la partie entière, `%` donne le reste de la division et `**` élève à une puissance. Ceux de **comparaison** posent des questions et répondent toujours par un `bool` : `==` (égal), `!=` (différent), `<`, `<=`, `>` et `>=`. Et les **logiques** combinent des questions : `and` n'est vrai que si les deux sont vraies, `or` est vrai si au moins une l'est, et `not` inverse la réponse. Enregistre `fig02_02.py` :

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

Les cinq premières lignes de sortie sont de l'arithmétique : 2300 divisé par 1000 donne `2.3` ; la division entière donne `2` (combien de secondes entières tiennent dans 2300 ms) et le reste donne `300` (les millisecondes qui restent) ; ajouter 100 donne `2400`, et `2**3` est deux au cube, `8`. Les trois suivantes sont des comparaisons : 2300 est bien supérieur ou égal au seuil de 1000 (`True`), le code est bien 200 (`True`) et par conséquent il n'est pas différent de 200 (`False`). Les trois dernières combinent : la première dit « le code est-il une erreur **ou** le temps a-t-il dépassé le seuil ? », et comme la seconde partie est vraie, le `or` entier l'est ; la deuxième dit « a-t-il répondu correctement **et** vite ? », et comme ce n'était pas rapide, elle est fausse ; la troisième range dans une variable la réponse à « le code est-il inférieur à 400 ? » (`True`) et l'inverse avec `not`, et c'est pourquoi elle donne `False`. Remarque qu'une comparaison peut être rangée dans une variable comme un nombre : sa valeur est un `bool`.

Remarque un détail de la figure qui reviendra dans tout le cours : le seuil est dans une variable au nom en majuscules, `UMBRAL_LENTO_MS = 1000`, et les comparaisons l'utilisent par son nom. Si demain l'équipe décide qu'un service est lent à partir de 800 ms, tu changes **une** ligne. Si tu avais écrit `1000` dans chaque comparaison, il faudrait les retrouver toutes.

Deux précisions sur les opérateurs. La première est la **priorité** : comme en mathématiques, `*` et `/` s'effectuent avant `+` et `-`, et Python fait les comparaisons avant `not`, `and` et `or`. Quand tu as un doute, utilise des parenthèses. La seconde est que **`and` et `or` n'évaluent pas ce dont ils n'ont pas besoin**. Dans `A or B`, si `A` est déjà vraie, Python ne regarde même pas `B`, parce que le résultat ne peut plus changer ; dans `A and B`, si `A` est fausse, il ne regarde pas `B` non plus. Cela s'appelle l'*évaluation en court-circuit* et ce n'est pas un détail d'érudit : dans quelques minutes, elle va éviter que le `revisor` n'explose avec le service `reportes`.

Un avertissement sur les décimaux, que j'avais promis. Regarde cette session du REPL (l'interpréteur interactif de la Leçon 1) :

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> 10 / 2
5.0
```

La première réponse ressemble à une erreur de Python et n'en est pas une. Les ordinateurs rangent les décimaux en binaire, et certains décimaux simples, comme 0.1, n'ont pas de représentation exacte en binaire ; ils sont rangés de façon approchée, et la somme de deux approximations donne une approximation légèrement différente du 0.3 que tu attendais. [Le tutoriel officiel y consacre un chapitre](https://docs.python.org/3/tutorial/floatingpoint.html) et rappelle que ce n'est pas un défaut de Python ni de ton code : c'est la façon dont fonctionnent les nombres à virgule flottante en binaire, la représentation qu'utilisent presque tous les ordinateurs (et, avec eux, presque tous les langages). La conséquence pratique : **ne compare pas avec `==` le résultat d'un calcul avec des décimaux en attendant une valeur exacte**. Dans le `revisor`, cela ne te concerne presque pas, parce que les temps sont des entiers (des millisecondes), et c'est pourquoi ils sont en millisecondes et non en secondes avec décimales. La deuxième réponse enseigne une autre habitude : `10 / 2` donne `5.0`, pas `5`. Le `/` renvoie toujours un `float`.

#### 2.1.4 `None`, `is` et les conversions avec `str()` et `int()`

Pour demander si une valeur est `None`, Python a un opérateur spécifique : **`is`**. Il s'écrit `valor is None`, et son contraire est `valor is not None`. C'est la bonne façon de le faire, et c'est celle qu'emploie [le guide de style](https://peps.python.org/pep-0008/#programming-recommendations), qui demande de toujours comparer avec `None` au moyen de `is` ou `is not`, jamais avec `==`. La raison, en une phrase : dans tout le programme **il n'existe qu'un seul `None`**, donc ce qu'on demande n'est pas « ressemble-t-il à `None` ? » mais « est-ce *le* `None` ? ». (La différence complète entre `==` et `is` est le sujet de la Leçon 3 ; pour l'instant, retiens la règle.)

Il y a aussi deux fonctions qui convertissent entre types. `str(valor)` renvoie le texte qui représente une valeur : `str(503)` est `"503"`. Et `int(texto)` fait l'inverse : `int("503")` est `503`. Tu en auras besoin à deux endroits : `str(codigo)` pour mettre un code dans la ligne du tableau, et plus tard `int(...)` pour convertir ce qui arrive de l'extérieur, qui arrive presque toujours sous forme de texte. Enregistre `fig02_03.py` :

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

Tant que `codigo` valait `None`, la première question donne `True` et la seconde `False`. Quand on lui affecte 503, le service a déjà un code et la question donne `False`. Ensuite, `"código: " + str(codigo)` colle deux textes avec `+` (pour les textes, `+` les réunit) et fonctionne **parce que `str(codigo)` a converti le nombre en texte avant**. Les deux dernières lignes confirment que `str(503)` est un `str` et que `int("503")` est un `int`. Retiens cette idée : Python ne convertit pas entre types à ta place. Si tu essaies de coller un texte avec un nombre, il te le reproche, et cette plainte est l'une des erreurs de la section « L'erreur que tu vas voir ».

### 2.2 Texte formaté : les f-strings

#### 2.2.1 Pourquoi ne pas coller avec `+`

Il faut composer une ligne du tableau : le nom, l'état, le temps et le détail, en colonnes alignées. Avec ce que tu sais déjà, la manière serait de coller des textes avec `+`, en convertissant chaque nombre avec `str()`, et de calculer à la main combien d'espaces manquent pour compléter chaque colonne. C'est possible, et le résultat est illisible et fragile : chaque nouvelle pièce est un autre `+` et un autre `str()`, et changer la largeur d'une colonne oblige à recompter les espaces.

Python a un outil conçu pour cela : les **f-strings** (*formatted string literals*). Une f-string est un texte qui commence par la lettre `f` avant les guillemets, et qui accepte des **expressions entre accolades** : Python calcule ce qu'il y a dans chaque paire d'accolades et insère le résultat dans le texte. Elles sont expliquées dans [la référence du langage](https://docs.python.org/3/reference/lexical_analysis.html#f-strings). Il existe deux autres formes plus anciennes de formater du texte, l'opérateur `%` et la méthode `.format()`. Tu les trouveras dans du vieux code, donc il convient de les reconnaître, mais ce cours ne les utilise pas et tu n'as pas besoin de les apprendre : les f-strings font tout ce qu'elles font et se lisent mieux.

#### 2.2.2 Mettre des valeurs et des calculs dans le texte

Le plus simple est de mettre un nom entre accolades : `f"{nombre} respondió"`. Mais ce qui va entre accolades peut être n'importe quelle expression, même un calcul : `f"{tiempo_ms * 2}"` calcule le double et l'insère. Cela élimine complètement le `str()` de la section précédente : la f-string convertit en texte ce que tu insères, sans que tu le lui demandes.

#### 2.2.3 La spécification de format : largeur, alignement et décimales

Après l'expression, et séparée par deux-points, on peut écrire une **spécification de format** qui dit à Python comment afficher la valeur. Aujourd'hui tu en as besoin de trois, et [le langage de format complet est dans la documentation](https://docs.python.org/3/library/string.html#format-specification-mini-language) :

- **`:<12`** : occupe **12 caractères** et aligne la valeur à **gauche** (`<`), en remplissant avec des espaces à droite.
- **`:>6`** : occupe **6 caractères** et aligne la valeur à **droite** (`>`), en remplissant à gauche.
- **`:.1f`** : affiche un nombre **décimal avec un chiffre** après le point (`f` de *fixed*, virgule fixe).

Enregistre `fig02_04.py`. Les accolades sont entourées de crochets dans la sortie pour que tu voies où commence et où se termine chaque champ :

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

Les trois premières lignes n'ont plus besoin d'explication : le nom et le temps sont insérés tels quels, le calcul est effectué et inséré, et `2300 / 1000` sort comme `2.3`. Les suivantes enseignent la largeur : `inventario` a dix caractères, et avec `:<12` il reste avec deux espaces après (regarde où tombe le crochet fermant) ; avec `:>12`, les deux espaces vont avant. Avec `{87:>6}`, le 87 occupe six positions, aligné à droite, et c'est pourquoi il y a quatre espaces avant. Les deux dernières montrent `.1f` : `2.3` avait déjà une décimale, et `1000 / 1000`, qui est `1.0`, garde son `.0` (Python l'arrondit au nombre de décimales demandé, il ne les supprime pas).

C'est ce dont tu as besoin pour composer une ligne du tableau. Le modèle du `revisor`, qui ne changera pas de tout le cours, est :

```text
f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"
```

Lis-le de gauche à droite : le nom du service sur 12 colonnes, aligné à gauche ; l'état sur 10, à gauche ; le temps sur 6, à droite (les nombres s'alignent mieux par la droite, pour que les unités tombent les unes sous les autres) ; deux espaces fixes, et le détail, qui va à la fin et n'a pas besoin de largeur. Et l'en-tête du tableau utilise **le même modèle**, avec les titres à la place des données. Un détail d'écriture : l'en-tête est entre guillemets doubles et, à l'intérieur des accolades, les titres portent des guillemets simples (`{'SERVICIO':<12}`). Depuis Python 3.12, tu pourrais répéter les doubles à l'intérieur des accolades et cela fonctionnerait (la [PEP 701](https://peps.python.org/pep-0701/) l'a permis), mais les alterner se lit mieux, parce qu'à première vue on distingue où se termine la f-string et où commence le texte de l'intérieur, et en plus cela fonctionne dans les versions antérieures de Python.

### 2.3 Décisions : `if`, `elif`, `else` et l'indentation

#### 2.3.1 Une question et un bloc

Un programme qui fait toujours la même chose ne sert pas à vérifier des services. Il doit **décider** : si telle chose arrive, faire ceci ; sinon, cela. En Python, la décision s'écrit avec `if` :

```text
if <pregunta>:
    <lo que se hace si la respuesta es verdadera>
```

La question est n'importe quelle expression qui donne un `bool`, comme celles de la section précédente. Après la question vient un signe de **deux-points** (`:`), qui dit à Python « ici commence ce qui dépend de la question ». Et ce qui en dépend va dans les lignes suivantes, **décalé vers la droite**. Cet ensemble de lignes s'appelle un **bloc**.

Voici une caractéristique de Python qui le distingue de la plupart des langages et qui surprend parfois le débutant : **l'indentation fait partie de la syntaxe**. Dans d'autres langages, les blocs sont délimités par des accolades ou par des mots comme `begin` et `end`, et le retrait est une question de style. En Python, **c'est le retrait qui dit où commence et où se termine le bloc**. Les lignes décalées de la même quantité appartiennent au même bloc ; quand une ligne revient à la marge gauche, le bloc est terminé. [La référence du langage le définit avec précision](https://docs.python.org/3/reference/lexical_analysis.html#indentation), et la règle pratique de la PEP 8 est : **quatre espaces par niveau**, et ne jamais mélanger tabulations et espaces. Configure ton éditeur pour que la touche Tab insère quatre espaces, et n'y pense plus.

Enregistre `fig02_05.py` :

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

Avec `codigo = 503`, la question `codigo >= 400` est vraie et le premier bloc s'exécute. Le `else` (en espagnol, « si no », c'est-à-dire « sinon ») est la branche qui s'exécute quand la réponse est fausse ; il ne porte pas de question, mais il a bien ses deux-points. Remarque la dernière ligne : elle est **à la marge gauche**, en dehors des deux blocs, et c'est pourquoi elle s'exécute toujours, quel que soit le code. Essaie de changer `codigo` en `200` et vérifie que la première ligne de la sortie change, mais pas la dernière. Si une ligne s'exécute un jour « quand elle ne devait pas » (ou ne s'exécute pas quand elle le devait), regarde d'abord son retrait : en Python, c'est là que commencent 80 % de ces surprises.

#### 2.3.2 `elif` : plusieurs questions en chaîne

Un service n'a pas deux états mais trois, et les décisions du `revisor` sont enchaînées : d'abord on demande s'il est en panne ; sinon, on demande s'il est lent ; et si ce n'est pas le cas non plus, il est en marche. Pour cela existe `elif`, contraction de *else if*, « sinon, et si... ». Une chaîne `if`/`elif`/`else` fonctionne ainsi : **Python évalue les questions de haut en bas, exécute le bloc de la première qui est vraie et saute toutes les autres**. Si aucune ne l'est, il exécute le `else`, s'il y en a un. D'une chaîne, on exécute toujours au plus un bloc.

Les règles du `revisor` pour classer un service, qui sont les mêmes de cette leçon jusqu'à la dernière, sont au nombre de quatre :

1. Si **il n'y a pas eu de code** (pas de réponse), il est **CAIDO**.
2. Si le code est **400 ou plus** (le serveur a répondu, mais avec une erreur), il est **CAIDO** ; le détail sera le code lui-même, par exemple `503`.
3. S'il a répondu correctement et mis **1000 ms ou plus**, il est **LENTO**.
4. Sinon, il est **ARRIBA**.

Les deux premières ont le même résultat, et peuvent se réunir en une seule question avec `or`. Enregistre `fig02_06.py` :

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

Pour `inventario`, avec le code 200 et 2300 ms, la première question est fausse (le code existe et n'atteint pas 400), la seconde est vraie (2300 est supérieur ou égal à 1000), et l'état devient `"LENTO"`. Essaie avec d'autres valeurs : `codigo = 503` donne `CAIDO` ; `tiempo_ms = 142` donne `ARRIBA`.

#### 2.3.3 L'ordre des questions compte

Il y a une raison pour laquelle la question du code vient **en premier**, et c'est la même que celle qui avait été promise avec le court-circuit. Pense à `reportes` : il n'a pas répondu, donc son `codigo` est `None` et son `tiempo_ms` aussi. Avec la chaîne du dessus, la première question (`codigo is None or ...`) est vraie dès que Python regarde le `is None`, et il **n'évalue plus** la seconde moitié du `or`, qui aurait échoué : `None >= 400` n'a aucun sens. Et comme la première branche a été satisfaite, le `elif` n'est pas évalué non plus, lui qui demanderait `None >= 1000`. Le service reste CAIDO sans que Python compare un `None` avec un nombre.

Si tu mets les questions dans un autre ordre, la chaîne cesse d'être sûre. Cette erreur est l'une de celles de « Ce qui se fait de travers », et cela vaut la peine de la provoquer dans l'Exercice 4. La règle de fond : **dans une chaîne de `elif`, ordonne les questions de la plus spécifique ou la plus dangereuse à la plus générale**, de façon que chaque branche puisse tenir pour acquis ce que les précédentes ont écarté. Dans le `elif`, tu sais déjà que le service a répondu avec un code inférieur à 400, donc `tiempo_ms` a une valeur.

#### 2.3.4 Tout ensemble : la ligne d'un service

Tu as maintenant tout le nécessaire. Il reste à calculer les deux autres colonnes avec le même mécanisme. Le **temps** est un texte qui dépend de la valeur : s'il n'y a pas eu de temps, un tiret (`"—"`) ; s'il a été de moins d'une seconde, des millisecondes collées à l'unité (`"142ms"`) ; s'il a été d'une seconde ou plus, des secondes avec une décimale (`"2.3s"`). Remarque que le 1000 d'ici **n'est pas le seuil de lenteur** : c'est la quantité de millisecondes qu'il y a dans une seconde. Ils se ressemblent par la valeur et signifient des choses différentes, et c'est pourquoi le premier a un nom (le seuil peut changer) et le second non (une seconde a toujours mille millisecondes). Et le **détail** est le code converti en texte, ou `"sin conexión"` s'il n'y a pas eu de code.

Voici la figure de la leçon, ton nouveau `revisor.py`. Enregistre-la sous le nom `fig02_07.py` pour la comparer et aussi sous le nom `revisor.py`, qui remplace la ligne de la Leçon 1 :

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

Lis-la comme la lit Python. Les cinq premières lignes rangent les données d'un service ; `url` est l'adresse du service et n'est pas encore imprimée, mais le projet la porte déjà, comme le domaine `.example`, qui est un nom réservé qui n'aboutit jamais à aucune vraie page (aucun programme de ce cours ne touche à internet avant la Leçon 9). Le premier bloc `if` calcule `estado` avec les règles du dessus. Le second calcule `tiempo`, le texte de la colonne : si `tiempo_ms is None` il met le tiret, s'il est inférieur à 1000 il colle `ms` au nombre et sinon il le convertit en secondes avec une décimale. Le troisième calcule `detalle`. Les deux dernières lignes impriment l'en-tête et la ligne avec le modèle de la section 2.2 : le même schéma, avec les titres dans le premier et avec les variables dans le second.

Change les cinq variables pour celles d'un autre service et exécute de nouveau le programme : il n'y a rien d'autre à toucher. C'est l'objet de l'Exercice 1, et c'est de là que vient la leçon suivante : copier et coller ce bloc pour chaque service serait absurde, et Python a des outils pour ne pas le faire.

## L'erreur que tu vas voir

Dans cette section, tu vas provoquer volontairement les trois erreurs que le débutant voit en premier. Les trois sont copiées d'une exécution réelle. Quand le programme échoue, Python imprime un rapport de l'erreur qui s'appelle ***traceback***, et la règle, depuis la Leçon 1, est la même : **on le lit de la dernière ligne vers le haut**. La dernière ligne dit ce qui s'est passé ; celles du dessus disent où. Les chemins complets des fichiers que tu verras sur ton écran seront différents de ceux que montre ce texte (ici ils sont abrégés au nom du fichier).

### `TypeError: can only concatenate str (not "int") to str`

Enregistre `fig02_08.py`, qui tente de coller un texte avec un nombre :

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

La dernière ligne dit : un `TypeError` (une erreur de type) avec le message « on ne peut concaténer que `str` (pas `int`) à `str` ». Concaténer, c'est coller. Le `+` entre deux textes les colle, mais ici le second était un nombre, et Python ne sait pas comment coller un texte avec un nombre : il ne va pas deviner si tu voulais « 2300 » ou un calcul. Les lignes du dessus te disent **où** : `line 4`, et en dessous la ligne du programme avec des marques qui désignent l'opération qui a échoué. La correction est de faire la conversion toi-même, avec `str(tiempo_ms)`, ou mieux, de ne rien coller : `print(f"respondió en {tiempo_ms}")`. [La documentation de `TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) le décrit comme « une opération ou une fonction appliquée à un objet d'un type inapproprié », ce qui est exactement le cas.

### `SyntaxError: expected ':'`

Enregistre `fig02_09.py`, un `if` auquel on a oublié les deux-points :

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

Un `SyntaxError` est une erreur de **syntaxe** : Python n'a même pas commencé à exécuter le programme, parce qu'il l'a lu en entier avant et a trouvé quelque chose qui n'est pas du Python valide. C'est pourquoi la sortie ne dit **pas** `Traceback` : il n'y a pas de parcours d'exécution à montrer, seulement l'endroit du problème. Le message, `expected ':'`, dit ce qu'il attendait : des deux-points. La flèche du dessous (`^`) désigne l'endroit où il s'en est rendu compte, la fin de la ligne du `if`. Quand tu vois un `SyntaxError`, regarde la ligne indiquée et aussi la **précédente**, parce que parfois l'oubli est avant (une parenthèse non fermée, par exemple, fait échouer la ligne suivante).

### `IndentationError: expected an indented block after 'if' statement on line 3`

Enregistre `fig02_10.py` : maintenant les deux-points sont là, mais la ligne du dessous est restée à la marge :

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

`IndentationError` est une variante de `SyntaxError` pour les problèmes de retrait. Le message est littéral : après un `if` (celui de la ligne 3) on attendait un bloc indenté, et la ligne 4 n'en a pas. Les deux-points à la fin du `if` promettaient un bloc, et Python l'exige. C'est le rappel de la section 2.3 : **les deux-points et le retrait vont ensemble**. La correction est de décaler `print("CAIDO")` de quatre espaces vers la droite.

## Ce qui se fait de travers

**Mettre les questions dans le mauvais ordre.** C'est l'erreur la plus traîtresse de cette leçon, parce qu'elle semble raisonnable et échoue justement avec le service qui compte le plus. Enregistre `fig02_11.py`, où la question du temps passe avant celle du code :

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

Le message, `'>=' not supported between instances of 'NoneType' and 'int'`, dit : l'opérateur `>=` n'est pas défini entre un `NoneType` (le `None`) et un `int` (le 1000). Avec des services qui ont répondu, le programme fonctionne et tu ne t'en aperçois pas ; avec `reportes`, qui n'a pas répondu, il explose. Coût : un `revisor` qui plante justement quand un service est en panne, c'est-à-dire quand tu en as le plus besoin. Le remède est la règle de la section 2.3 : d'abord la branche qui écarte les données manquantes.

**Écrire `=` là où il faut `==`.** `if codigo = 200:` est un `SyntaxError`, et le message de Python le devine : *invalid syntax. Maybe you meant '==' or ':=' instead of '='?* L'affectation range ; la comparaison interroge. On ne peut pas les intervertir.

**Comparer avec `None` en utilisant `==`.** Cela fonctionne dans les cas simples et c'est ce que déconseille [la PEP 8](https://peps.python.org/pep-0008/#programming-recommendations) : avec `None`, on utilise toujours `is` ou `is not`. Les outils de contrôle que tu connaîtras dans la Leçon 8 le signalent aussi.

**Ranger un nombre sous forme de texte.** `codigo = "200"` ressemble à `codigo = 200`, et ce n'est déjà plus pareil : `"200" >= 400` explose avec un autre `TypeError`, et `"200" + "1"` donne `"2001"`. Ce qui est une quantité se range comme un nombre, sans guillemets.

**Représenter « il n'a pas répondu » par `0` ou par un texte.** `tiempo_ms = 0` dit « il a répondu en zéro milliseconde », ce qui est la réponse la plus rapide possible, exactement le contraire de la vérité ; et un texte comme `"sin respuesta"` ne peut pas être comparé à 1000. Une donnée qui manque se range comme `None`, et le programme décide quoi en faire.

**Écrire `tiempo` tout court.** Une variable appelée `tiempo` ne dit pas si ce sont des secondes ou des millisecondes. Mets l'unité dans le nom, et quand un nombre est une quantité avec une unité, que le nom la porte.

**Écrire le même nombre à trois endroits.** Si le seuil de lenteur est écrit `1000` dans chaque comparaison et que demain il passe à 800, tu en oublieras une. On le nomme une fois (`UMBRAL_LENTO_MS`) et on l'utilise par son nom.

**Mélanger tabulations et espaces.** Python 3 refuse d'exécuter un bloc dont le retrait mélange les deux de manière incohérente, avec un `TabError: inconsistent use of tabs and spaces in indentation`. Ton éditeur peut le faire sans te prévenir ; configure-le pour que Tab insère quatre espaces.

## Exercices

### Exercice 1 — Les trois autres services et un en plus

Change les cinq variables de ton `revisor.py` pour celles de chacun des trois autres services, et **avant d'exécuter à chaque fois, écris sur une feuille la ligne que tu attends** :

| nombre | url | código | tiempo_ms |
|---|---|---|---|
| `catalogo` | `https://catalogo.example` | 200 | 142 |
| `pagos` | `https://pagos.example` | 200 | 87 |
| `reportes` | `https://reportes.example` | `None` | `None` |

Essaie ensuite avec `facturacion` (`https://facturacion.example`), qui répond avec le code 503 en 95 ms. Ta prédiction a-t-elle coïncidé pour les quatre ? Sinon, quelle partie des règles as-tu appliquée différemment ?

### Exercice 2 — Déplacer le seuil

Avec le service `catalogo` (200, 142 ms), change `UMBRAL_LENTO_MS` en 100 et prédis l'état. Puis laisse-le à 2500 et prédis l'état d'`inventario` (200, 2300 ms). Explique en une phrase pourquoi changer **une seule ligne** a changé le résultat dans les deux cas.

### Exercice 3 — Provoquer les trois erreurs

Dans une copie de ton programme, provoque un par un ces trois erreurs et copie le message exact de la dernière ligne : (a) supprime les deux-points d'un `elif` ; (b) supprime le retrait de la ligne qui suit le `else` ; (c) remplace le `str(codigo)` de `detalle` par `"código " + codigo`. Pour chacune, écris ce que signifie le message et quelle est la correction.

### Exercice 4 — La même chose à l'envers, et comment la rattraper

Pars de `fig02_11.py` (celui des questions dans le mauvais ordre, qui explose avec `None`). Sans changer l'ordre des deux premières branches, corrige la **première question** pour qu'elle n'explose plus avec `reportes`. Indice : il faut demander d'abord que `tiempo_ms` existe puis le comparer, et l'opérateur qui réunit deux questions en obligeant les deux à être satisfaites est `and`. Explique ensuite pourquoi cette solution fonctionne grâce au court-circuit.

## Solutions

### Solution 1

Les prédictions correctes, et ce qu'imprime le programme avec chaque service (l'en-tête est le même que d'habitude) :

```text
catalogo    ARRIBA     142ms  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
```

Celui de `facturacion` est celui qu'on rate le plus. Avec le code 503, la première question (`codigo >= 400`) est vraie, donc l'état est CAIDO **même s'il a répondu en 95 ms**, ce qui serait très rapide. Le temps continue de s'afficher (`95ms`) parce qu'il existe, et le détail est le code, `503`. De plus, `facturacion` a onze lettres et tient dans les douze colonnes du nom, mais presque sans marge : c'est pourquoi sa ligne est collée à l'état.

### Solution 2

Avec `UMBRAL_LENTO_MS = 100`, l'état de `catalogo` (142 ms) passe d'ARRIBA à **LENTO** : 142 est déjà supérieur ou égal à 100. Avec le seuil à 2500, `inventario` (2300 ms) passe de LENTO à **ARRIBA** : 2300 n'atteint plus 2500. Dans les deux cas, le résultat a changé parce que le seuil a été écrit une seule fois et que toutes les comparaisons l'utilisent par son nom ; si le 1000 était répété dans chaque question, il faudrait le changer partout.

### Solution 3

(a) Sans les deux-points du `elif` : `SyntaxError: expected ':'`. Python attendait les deux-points qui annoncent le bloc. Correction : les mettre à la fin de la ligne du `elif`.

(b) Sans retrait après le `else` : `IndentationError: expected an indented block after 'else' statement on line N`, où `N` est le numéro de la ligne du `else`. Correction : quatre espaces avant la ligne qui dépend du `else`.

(c) `"código " + codigo`, avec `codigo` valant 200 : `TypeError: can only concatenate str (not "int") to str`. Correction : `"código " + str(codigo)` ou, mieux, une f-string : `f"código {codigo}"`.

### Solution 4

La première question devient `tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS` :

```python
if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"
```

Cela fonctionne grâce au court-circuit : avec `tiempo_ms = None`, la première moitié (`tiempo_ms is not None`) est fausse, et comme un `and` dont une moitié est fausse ne peut plus être vrai, Python **n'évalue pas** la seconde moitié, celle qui explosait. Mais attention : cette version est pire que l'originale dans un cas. Avec `codigo = 503` et `tiempo_ms = 2300`, un service qui a répondu **lentement et avec une erreur** resterait LENTO au lieu de CAIDO, parce que la branche du temps l'emporte sur celle du code. Corriger le symptôme sans ordonner les branches a changé les règles sans le vouloir. C'est la meilleure raison de laisser la question du code en premier.

## Comment savoir que j'ai réussi

- [ ] `python revisor.py` imprime exactement deux lignes : `SERVICIO    ESTADO    TIEMPO  DETALLE` et `inventario  LENTO       2.3s  200`, avec les colonnes alignées comme dans la figure `fig02_07.py`.
- [ ] Quand tu changes les variables pour celles de `reportes` (`codigo = None`, `tiempo_ms = None`), le programme imprime `reportes    CAIDO          —  sin conexión` et ne se termine **pas** par un *traceback*.
- [ ] Avec `facturacion` (503, 95 ms), l'état est CAIDO et le détail est `503`.
- [ ] Tu peux provoquer volontairement `SyntaxError: expected ':'`, `IndentationError` et `TypeError: can only concatenate str (not "int") to str`, et dire en une phrase ce que dit la dernière ligne de chacun.
- [ ] Tu peux expliquer avec tes mots la différence entre `=` et `==`, entre `200` et `"200"`, et entre `None` et `0`.
- [ ] Tu peux expliquer pourquoi la question du code vient avant celle du temps dans la chaîne `if`/`elif`/`else`.

## Résumé

Réponds sans regarder la leçon :

1. Quel type `type()` renvoie-t-il pour `142`, pour `2.3`, pour `"142"`, pour `True` et pour `None` ?
2. Que fait `=` et que fait `==` ? Et pourquoi `UMBRAL_LENTO_MS` est-il en majuscules ?
3. Que donnent `10 / 2`, `7 // 2` et `7 % 2` ? Pourquoi `0.1 + 0.2` ne donne-t-il pas `0.3` ?
4. Comment demande-t-on si une valeur est `None`, et pourquoi n'utilise-t-on pas `==` ?
5. Que signifient `:<12`, `:>6` et `:.1f` dans une f-string ?
6. Dans une chaîne `if`/`elif`/`else`, combien de blocs s'exécutent au plus, et lequel ? Que fait l'indentation ?
7. Qu'est-ce que le court-circuit de `or` et de `and`, et quel problème évite-t-il dans le `revisor` ?
8. Quelle est la dernière ligne d'un `SyntaxError` dû à l'oubli des deux-points, et pourquoi cette erreur n'affiche-t-elle pas de *traceback* ?

## Pour aller plus loin

- [Le tutoriel Python, « Une introduction informelle »](https://docs.python.org/3/tutorial/introduction.html) — nombres, texte et variables, avec la session interactive que tu reconnaîtras de la Leçon 1. Documentation officielle. Consulté le 7 octobre 2026.
- [Le tutoriel Python, « Plus d'outils de contrôle de flux »](https://docs.python.org/3/tutorial/controlflow.html#if-statements) — la section sur `if`, `elif` et `else`. Consulté le 7 octobre 2026.
- [PEP 8, le guide de style de Python](https://peps.python.org/pep-0008/) — les conventions de noms, de retrait et de comparaison avec `None` qu'utilise ce cours. Consulté le 7 octobre 2026.
- [Mini-langage de spécification de format](https://docs.python.org/3/library/string.html#format-specification-mini-language) — tout ce qui peut aller après les deux-points dans une f-string ; ce n'est pas un texte à lire d'une traite mais à consulter. Consulté le 7 octobre 2026.
