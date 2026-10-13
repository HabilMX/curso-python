# Leçon 3 — Boucles, fonctions et modules

**Durée :** 2 × 90 min (deux sessions)

**Ce que tu construis :** la fonction `revisar()` et le parcours de la liste : un `revisor` en deux fichiers qui imprime l'en-tête et les lignes des quatre services

**Ce que tu apprends :** quatre concepts. D'abord, les boucles (`for`, `while`, `range`, `enumerate`) et la liste minimale pour parcourir ; ensuite, les fonctions (`def`, paramètres, valeurs par défaut, `return`, annotations simples et le piège de la valeur par défaut qui est une liste) ; puis les noms (où vit chaque variable, `UnboundLocalError`, et `==` contre `is`) ; enfin, les modules (`import`, `from ... import` et `if __name__ == "__main__":`)

**D'où tu viens.** Tu arrives avec le `revisor.py` de la [Leçon 2](02-valores-texto-decisiones.md) : une trentaine de lignes qui rangent **un** service (`inventario`) dans des variables, le classent avec un `if`/`elif`/`else` et l'impriment sur une ligne alignée, sous l'en-tête du tableau. Cela fonctionne, mais il y a un problème qu'on a déjà vu à la fin de cette leçon-là : pour vérifier les trois autres services, il faudrait copier le bloc trois fois et changer les valeurs de chaque copie. Aujourd'hui, on écarte ce problème. Tu continues de travailler dans `~/curso-python/revisor/`, avec l'environnement virtuel actif, et les programmes s'exécutent avec `python archivo.py`.

**Comment la leçon est répartie.** Elle est longue, et c'est pourquoi il y a deux sessions de 90 minutes avec une coupure naturelle au milieu. **La première session** correspond aux sections 3.1 et 3.2 (boucles et fonctions) et se termine avec la figure `fig03_11`, le `revisor` complet dans **un** seul fichier. **La deuxième session** correspond aux sections 3.3 et 3.4 (noms et modules), aux erreurs, aux exercices et au `revisor` réparti en deux fichiers. Si tu manques de temps dans la première, arrête-toi en arrivant à `fig03_11` : ce qui suit se comprend mieux quand ce programme fonctionne et que tu t'es reposé.

**Ce que cette leçon ne fait pas.** Elle ne voit pas les listes à fond : aujourd'hui tu utilises une liste **minimale** (la créer, demander combien d'éléments elle a, en lire un par sa position et en ajouter un), juste ce qu'il faut pour la parcourir. Les dictionnaires, les tuples, les ensembles et les compréhensions relèvent de la [Leçon 4](04-colecciones.md), et le modèle de données avec `Servicio` et `Estado`, de la [Leçon 5](05-modelo-de-datos.md). Et il n'y a pas encore d'erreurs interceptées (`try`), ni de fichiers, ni de réseau.

## À la fin, tu seras capable de

- Parcourir une liste avec `for` de trois manières (par valeur, par position avec `range(len(...))` et avec `enumerate`) et répéter avec `while` sans tomber dans une boucle infinie.
- Créer une liste, demander sa taille avec `len`, lire un élément par sa position (qui commence à 0) et en ajouter un avec `.append`.
- Écrire une fonction avec des paramètres, une valeur par défaut et `return`, avec des annotations de type simples (`int`, `str`, `int | None`, `-> None`), et expliquer la différence entre imprimer et renvoyer.
- Expliquer pourquoi une valeur par défaut qui est une liste « se souvient » des appels précédents, et le corriger avec le schéma du `None`.
- Dire où vit chaque variable (locale ou globale) et lire `UnboundLocalError`.
- Expliquer la différence entre `==` (sont-ils égaux ?) et `is` (sont-ils le même objet ?) et savoir dans quel cas on utilise `is`.
- Répartir un programme en deux fichiers avec `import` et `from ... import`, et expliquer à quoi sert `if __name__ == "__main__":`.

## Le pourquoi avant le comment

Regarde ce qu'il faudrait faire aujourd'hui, avec ce que tu sais de la Leçon 2, pour que le `revisor` vérifie les quatre services. Copier le bloc d'`inventario` trois fois, et dans chaque copie changer le nom, le code et le temps. Cela fait cent lignes presque identiques. Et puis quelqu'un décide qu'un service est lent à partir de 800 millisecondes, et non de 1000 : il faut retrouver la comparaison dans chaque copie et la changer. Si tu en oublies une, trois services sont classés avec une règle et le quatrième avec une autre, et le rapport ment sans donner aucune erreur.

C'est le problème de fond, et il est le même dans tous les programmes : **la même logique écrite plusieurs fois tend à diverger**. Python (comme tous les langages) fournit trois outils pour le résoudre, qui sont les trois de cette leçon :

- **Répéter sans copier.** Une *boucle* exécute le même bloc une fois pour chaque élément d'une liste, ou tant qu'une condition est remplie. C'est la section 3.1.
- **Donner un nom à un morceau de logique.** Une *fonction* enferme une recette (par exemple, « classer un service ») sous un nom, pour l'utiliser de n'importe où avec des valeurs différentes. C'est la section 3.2. Le prix des fonctions est qu'il faut maintenant savoir **où vit chaque nom** : une variable que tu crées dans une fonction n'est pas la même qu'une autre portant le même nom à l'extérieur. C'est la section 3.3.
- **Répartir le programme en fichiers.** Un *module* est un fichier Python qu'un autre fichier peut utiliser. Quand le programme grandit, chaque fichier ne contient qu'une seule sorte de choses (ici, l'un pour le format du tableau et l'autre pour la logique de la vérification). C'est la section 3.4.

À la fin de la leçon, `python revisor.py` imprimera le tableau de quatre services que tu as vu dans la Leçon 2, sans le récapitulatif (qui a besoin de compter, et cela arrive dans la Leçon 5) :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Un avertissement de conception, pour que tu ne le prennes pas pour une négligence. Les données des quatre services vont dans **trois listes parallèles** : une de noms, une de codes et une de temps, où la position 2 de chaque liste parle du même service. C'est une manière fragile de ranger des données : si une liste se désordonne ou se retrouve trop courte, rien ne te prévient. **C'est fait ainsi exprès**, parce que c'est ce qu'on peut faire avec ce que tu sais aujourd'hui, et parce que cette fragilité est la raison pour laquelle la Leçon 4 existe. Dans le premier exercice, tu vas la casser exprès pour la voir.

## Les concepts

### 3.1 Boucles : répéter sans copier

#### 3.1.1 La liste minimale

Pour répéter quelque chose avec chaque service, il faut une liste de services, et les valeurs de la Leçon 2 ne gardent chacune qu'une seule donnée. Il faut présenter la liste. Ici on voit le minimum ; la Leçon 4 l'étudie à fond.

Une **liste** est une suite ordonnée de valeurs, écrite entre crochets, avec les éléments séparés par des virgules : `["catalogo", "inventario", "pagos", "reportes"]`. Une liste peut mélanger des types (celle des codes contient des nombres et un `None`), et elle se range sous un nom comme n'importe quelle autre valeur. Quatre opérations suffisent pour l'instant, et les quatre sont dans la figure suivante. Enregistre-la sous le nom `fig03_01.py` :

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

Ligne par ligne. `print(nombres)` affiche la liste complète, avec ses crochets. `len(nombres)` renvoie combien d'éléments elle a : quatre. Ce qui vient ensuite est ce qui déconcerte le plus le débutant : **les positions commencent à 0**. `nombres[0]` est le premier élément (`catalogo`) et `nombres[3]` est le quatrième (`reportes`). La raison de fond est que la position dit de combien tu t'éloignes du début : le premier élément est à zéro pas. La conséquence pratique, dont tu auras besoin dans tout le cours, est qu'une liste de quatre éléments a les positions 0, 1, 2 et 3, et **n'a pas de position 4** ; la dernière position est toujours `len(lista) - 1`.

La dernière partie de la figure ajoute un élément : `nombres.append("facturacion")` le colle à la fin. Le point et la parenthèse signifient que `append` est une *méthode* de la liste, c'est-à-dire une opération que la liste sait faire sur elle-même (les méthodes sont les fonctions qui « appartiennent » à une valeur, et tu en verras davantage avec les textes et les dictionnaires). Après l'ajout, `len` donne 5 et la position 4 existe. Remarque que `append` a **modifié la liste sur place** : il n'a pas renvoyé une nouvelle liste, il a modifié celle qu'il avait déjà. Les valeurs qui peuvent changer ainsi s'appellent *mutables*, et cette propriété revient encore deux fois dans cette leçon, alors garde-la en tête.

Un détail de style : dans cette figure, le nom de la liste est en minuscules (`nombres`) parce qu'elle change, et dans les figures suivantes, quand les listes seront des données fixes du programme, elles seront en majuscules (`NOMBRES`), comme le reste des constantes.

#### 3.1.2 `for` : faire quelque chose avec chaque élément

La boucle `for` exécute un bloc une fois pour chaque élément d'une liste. Enregistre `fig03_02.py` :

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

La première ligne de la boucle se lit presque en français : « pour chaque `nombre` dans `nombres` ». Elle se termine par des **deux-points**, et le bloc qu'elle répète va **avec retrait** (quatre espaces), comme un `if`. Voici ce que fait Python : il prend le premier élément de la liste, le range sous le nom `nombre`, exécute le bloc ; il prend le deuxième, le range sous le même nom, exécute le bloc ; et ainsi de suite jusqu'à épuisement. La dernière ligne, `print("listo")`, est à la marge gauche : elle ne fait plus partie du bloc, et c'est pourquoi elle ne s'exécute qu'une fois à la fin. C'est la même règle que dans la Leçon 2 : le retrait dit où finit un bloc.

Le nom `nombre`, c'est toi qui l'as choisi. Il pourrait s'appeler `x` ou `servicio` ; mais un bon nom raconte ce qu'il y a dedans (à chaque tour, `nombre` est *un* nom, et la liste est `nombres`, au pluriel). C'est une convention très utile : liste au pluriel, élément au singulier.

#### 3.1.3 `range` : parcourir par position

Parfois la valeur ne te suffit pas ; il te faut sa **position**. C'est le cas avec les listes parallèles du `revisor` : pour connaître le temps du service que tu regardes, il te faut la même position dans la liste des temps. Pour cela existe `range` : `range(4)` produit les nombres 0, 1, 2 et 3 (les quatre premiers, en commençant à zéro, sans inclure le 4). Et comme `len(NOMBRES)` vaut 4, `range(len(NOMBRES))` produit exactement les positions valides de la liste. Enregistre `fig03_03.py` :

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

La première boucle imprime seulement les nombres que `range(3)` produit : `0`, `1` et `2`. La seconde est celle qui compte : à chaque tour, `i` vaut une position, et les deux listes sont lues à cette même position, `NOMBRES[i]` et `TIEMPOS_MS[i]`. Remarque que cela **ne fonctionne que si les deux listes ont la même longueur** ; si `TIEMPOS_MS` avait un élément de moins, le dernier tour échouerait. C'est le défaut des listes parallèles, et il y a un exercice pour lui.

Une note sur les noms : `i` est l'habitude universelle pour « une position » (de *index*, « indice »), et c'est l'un des rares noms d'une lettre qu'on accepte. Pour tout le reste, des noms qui disent ce que c'est.

#### 3.1.4 `enumerate` : la valeur et sa position ensemble

Quand tu as besoin de la valeur **et** de la position, `enumerate` te donne les deux à la fois. À chaque tour, il fournit un couple, et la syntaxe `for i, nombre in enumerate(...)` met le premier élément du couple dans `i` et le second dans `nombre`. Cela s'appelle *déballer* (*unpacking*). Enregistre `fig03_04.py` :

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

La première boucle imprime les positions depuis 0 avec leur nom. La seconde utilise un second argument, `start=1`, pour que le compte commence à 1 : c'est ainsi qu'on numérote les choses pour les personnes. Ce `start=1` est un **argument nommé**, et tu le comprendras mieux dans la section 3.2.

`enumerate` est la manière la plus lisible de parcourir **une** liste avec sa position. Dans le `revisor` d'aujourd'hui, il y a **trois** listes parallèles, donc la position est ce qui les relie et le parcours est celui de `range(len(NOMBRES))` ; avec trois listes, `enumerate` n'aide que pour une. Mais il convient que tu le connaisses, parce que dès que le `revisor` aura laissé derrière lui les listes parallèles (Leçon 4), il parcourra **une** seule liste, et quand il faudra en plus la position, `enumerate` sera l'outil naturel (tu l'utiliseras dans la Leçon 6).

#### 3.1.5 `while` : répéter tant que quelque chose est vrai

`for` répète une fois pour chaque élément de quelque chose qui existe déjà. `while` répète **tant qu'une condition est vraie**, sans savoir à l'avance combien il y aura de tours. Il pose de nouveau la condition avant chaque tour, et s'arrête quand la réponse est `False`. Enregistre `fig03_05.py`, qui cherche la position du premier service qui n'a pas répondu :

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

Avant de commencer, `i` vaut 0. Chaque tour pose deux questions reliées par `and` : `i` est-il encore à l'intérieur de la liste ? et le code à cette position existe-t-il (`is not None`, qui est la négation de `is None`) ? Tant que les deux sont vraies, il exécute le bloc, qui dit `i += 1`. Cette ligne est l'abréviation de `i = i + 1` : elle ajoute 1 et range le résultat sous le même nom. À la position 3, le code est `None`, la seconde question échoue et la boucle se termine avec `i` valant 3.

Remarque **l'ordre des deux questions**, parce que c'est de nouveau la leçon 2. `i < len(CODIGOS)` va en premier pour que, si `i` en venait à valoir 4, le `and` soit déjà faux et que Python **n'essaie pas** de lire `CODIGOS[4]`, qui n'existe pas. Le court-circuit t'a protégé.

Avec `while`, il y a un risque que `for` n'a pas : **la boucle infinie**. Si le bloc ne change rien de ce que la condition interroge, la condition ne devient jamais fausse et le programme tourne en rond pour toujours. Si tu oubliais le `i += 1` de la figure, c'est ce qui arriverait. Quand un programme se bloque ainsi, la sortie de secours est `Ctrl`+`C` dans le terminal, qui l'interrompt. La règle pour écrire un `while` : **avant de l'exécuter, repère la ligne du bloc qui rapproche la condition d'être fausse**. Et quand on peut utiliser un `for`, utilise-le : le `for` se termine par construction quand les éléments sont épuisés.

#### 3.1.6 Accumuler, sauter et sortir

Deux usages très fréquents des boucles complètent la section. Le premier est d'**accumuler** : parcourir les données pour en tirer un compte. Enregistre `fig03_06.py`, qui additionne les temps des services qui ont répondu :

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

Le schéma se répète dans presque tous les programmes : avant la boucle, on crée les variables qui accumulent (`total` et `respondieron`, à zéro) ; dans la boucle, on les met à jour ; après, on les utilise. Le `if` du bloc laisse de côté le service qui n'a pas répondu, dont le temps est `None` ; sans lui, `total += None` échouerait avec un `TypeError`, comme celui de la Leçon 2. La somme est 2529 (142 + 2300 + 87), trois ont répondu, et la moyenne de ceux qui ont répondu est 843. Elle sort avec un `.0` parce que la division `/` donne toujours un décimal ; la Leçon 4 t'apprend à l'arrondir, et la 5 l'utilise dans le récapitulatif du tableau.

Le second usage est de **contrôler la boucle de l'intérieur** avec deux mots : `continue` saute au tour suivant sans terminer le bloc, et `break` sort entièrement de la boucle. Enregistre `fig03_07.py`, qui cherche le premier service lent :

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

Avec `catalogo` (142 ms), la boucle demande s'il a un temps (oui), demande s'il est lent (non) et passe au tour suivant. Avec `inventario` (2300), la seconde question est vraie : elle imprime le nom et `break` termine la boucle, de sorte que `pagos` et `reportes` ne sont même pas regardés. Si le premier avait été `reportes` (avec `None`), le `continue` aurait sauté ce tour avant de comparer `None >= 1000`, qui explose. Utilise `break` et `continue` avec modération : ils sont commodes et cachent le flux du programme quand on en abuse.

### 3.2 Fonctions : donner un nom à une recette

#### 3.2.1 Définir et appeler

Une **fonction** est un bloc de code avec un nom que tu peux exécuter quand tu veux, autant de fois que tu veux, avec des données différentes à chaque fois. Tu as déjà utilisé des fonctions qui viennent avec Python : `print`, `len`, `range`, `type`, `str`. Maintenant tu vas écrire les tiennes, avec le mot `def` (« définir »). La première est celle du format du temps, qui dans la Leçon 2 était écrite comme un bloc `if` à l'intérieur du programme. Enregistre `fig03_08.py` :

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

Cette figure a deux parties bien séparées, et comprendre la séparation est le plus important de la section. **La définition**, ce sont les six premières lignes, du `def` jusqu'au dernier `return` : elles expliquent à Python ce que fait `formatear_tiempo`, mais **ne l'exécutent pas**. C'est comme écrire une recette sur une fiche : la recette existe, mais personne n'a encore rien cuisiné. **Les appels**, ce sont les cinq dernières lignes : chaque `formatear_tiempo(...)` demande à Python d'exécuter la recette avec une donnée concrète, et c'est là que le travail se fait. Si tu retirais les appels, le programme s'exécuterait sans rien imprimer.

La ligne du `def` a quatre parties. `def` annonce la définition. `formatear_tiempo` est le nom (en minuscules avec tiret bas, comme une variable). Entre parenthèses vont les **paramètres** : les noms que la fonction utilise pour désigner les données qu'elle reçoit ; ici un seul, `tiempo_ms`. Et à la fin, les deux-points et le bloc avec retrait, le **corps** de la fonction. Une distinction de vocabulaire qu'on confond beaucoup : le **paramètre** est le nom qui apparaît dans la définition (`tiempo_ms`), et l'**argument** est la valeur qu'on passe dans l'appel (le `87`, le `999`). Chaque fois qu'on appelle la fonction, les arguments sont affectés aux paramètres et le corps s'exécute.

Le mot **`return`** fait deux choses à la fois : il **termine la fonction à cet endroit** et **remet une valeur** à celui qui l'a appelée. C'est pourquoi la fonction ci-dessus n'a besoin ni de `elif` ni de `else` : si `tiempo_ms` est `None`, le premier `return` termine la fonction et les lignes suivantes ne s'exécutent jamais ; sinon, on continue avec la question suivante. Compare avec la version de la Leçon 2 : elle fait la même chose, avec moins de branches, parce que chaque `return` ferme déjà le chemin. La valeur qu'elle renvoie peut être imprimée, rangée dans une variable ou utilisée dans une autre expression, comme n'importe quelle autre valeur.

Les cas de la sortie sont les cinq que tu essaieras dans tout le cours : 87 donne `87ms` ; 999 donne `999ms` (encore moins d'une seconde) ; **1000 donne `1.0s`**, juste à la limite ; 2300 donne `2.3s` ; et `None`, qui n'a pas de temps, donne le long tiret.

#### 3.2.2 Imprimer n'est pas renvoyer

Une erreur classique du débutant est de confondre deux choses qui se ressemblent à l'écran : **imprimer** une valeur et la **renvoyer**. `print` affiche quelque chose dans le terminal et c'est fini ; `return` remet la valeur au code qui a appelé la fonction, qui peut en faire ce qu'il veut. Enregistre `fig03_09.py` pour le voir :

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

La première ligne de la sortie (`87ms`) a été imprimée par `decir_tiempo` lorsqu'elle a été appelée, dans son corps ; rien de plus. Mais `a`, ce que cette fonction a **renvoyé**, est `None` : une fonction qui n'a pas de `return` renvoie `None` automatiquement. En revanche, `dar_tiempo` n'a rien imprimé ; elle a renvoyé le texte, et `b` le garde. C'est pourquoi les deux lignes suivantes impriment `None` et `87ms`, et les types sont `NoneType` et `str`. La règle pratique : **une fonction qui calcule quelque chose doit le renvoyer, pas l'imprimer**, et c'est celui qui l'appelle qui décide s'il l'imprime. Une fonction qui imprime au lieu de renvoyer est difficile à réutiliser et plus difficile à tester : la Leçon 8 teste des fonctions en comparant ce qu'elles renvoient avec ce qu'elles devaient renvoyer, et ce qui n'est qu'imprimé peut aussi se vérifier, mais il faut capturer ce qui sort à l'écran (la Leçon 11 le fait) au lieu de comparer une valeur.

#### 3.2.3 Valeurs par défaut et arguments nommés

Parfois un paramètre a presque toujours la même valeur. Au lieu de l'exiger à chaque appel, on peut lui donner une **valeur par défaut** dans la définition, avec un signe égal : `umbral_ms: int = UMBRAL_LENTO_MS`. Si l'appel ne le passe pas, cette valeur est utilisée ; s'il le passe, la nouvelle est utilisée. Et quand un appel a beaucoup d'arguments, on peut les écrire **avec leur nom** (`umbral_ms=100`) pour ne pas dépendre de l'ordre et pour qu'on lise ce qu'est chacun. [Le tutoriel officiel les explique avec plus d'exemples](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions). Enregistre `fig03_10.py`, qui est la classification de la Leçon 2 transformée en fonction :

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

La définition suit les quatre règles du `revisor`, dans le même ordre que dans la Leçon 2 : d'abord, sans code ou avec un code d'erreur, CAIDO ; ensuite, LENTO s'il y a eu une réponse et que le temps a atteint le seuil ; sinon, ARRIBA. La question `tiempo_ms is not None and ...` a le `and` dans cet ordre pour la même raison que toujours, et comme `tiempo_ms` admet `None` dans son annotation, le programme se protège même si, en pratique, un service qui a répondu apporte toujours son temps. La signature a été coupée en trois lignes parce qu'elle ne tenait pas sur une : c'est ainsi que l'écrit le formateur automatique de Python (la Leçon 8 le présente), et c'est normal quand la liste de paramètres est longue.

Les six premiers appels sont les cas du tableau de règles, dans l'ordre de la sortie : ARRIBA, ARRIBA, **LENTO à la limite de 1000**, LENTO, CAIDO à cause du code 503 (même s'il a répondu en 95 ms) et CAIDO faute de réponse. Dans le septième, `umbral_ms=100` **remplace la valeur par défaut** seulement pour cet appel : 142 ms est déjà lent si la limite est 100. Dans le huitième, les deux arguments sont nommés, et peuvent s'écrire dans n'importe quel ordre. Si tu oublies un argument qui n'a pas de valeur par défaut, Python le réclame avec `TypeError: clasificar() missing 1 required positional argument: 'tiempo_ms'` : « il manque à `clasificar()` un argument positionnel obligatoire ».

#### 3.2.4 Annotations de type simples

Tu auras remarqué que les paramètres et les fonctions portent des choses comme `: int | None` et `-> str`. On les appelle des **annotations de type** et elles disent quel type de valeur est attendu et quel type la fonction renvoie. Elles s'écrivent ainsi :

- `tiempo_ms: int` — ce paramètre est un entier.
- `tiempo_ms: int | None` — ce paramètre est un entier **ou** `None` (la barre se lit « ou »). C'est la façon de dire « il peut ne pas y avoir de donnée ».
- `-> str` — la fonction renvoie un texte.
- `-> None` — la fonction ne renvoie rien d'utile (elle renvoie `None`).
- `caidos: list[str]` — une liste de textes. Les crochets disent ce qu'il y a dans la liste.

Un fait que tu as déjà vu dans la Leçon 0 et qu'il importe de répéter : **Python n'impose pas les annotations à l'exécution**. Si tu appelles `clasificar("hola", "mundo")`, le programme ne se plaint pas des types (il se plaint, peut-être, plus loin, pour une autre raison). Les annotations servent à deux lecteurs : aux personnes, qui comprennent ce qu'attend chaque fonction sans lire son corps, et aux outils de vérification, qui les contrôlent sans exécuter le code. La syntaxe est arrivée avec [la PEP 3107](https://peps.python.org/pep-3107/), dans Python 3.0, qui a laissé exprès indéfini à quoi elles servaient ; [la PEP 484](https://peps.python.org/pep-0484/) leur a donné leur usage actuel, les types, et dit en toutes lettres que « no type checking happens at runtime » : à l'exécution, aucun type n'est vérifié. L'outil qui les contrôle (`mypy`) arrive dans la Leçon 8 ; d'ici là tu les écris parce qu'elles aident à lire et parce qu'il est beaucoup plus facile de les écrire à la naissance d'une fonction que de les ajouter après.

#### 3.2.5 Un `revisor` complet dans un seul fichier

Avec les fonctions, tu peux déjà monter le parcours. Il manque deux fonctions de plus : une qui compose la ligne (`linea`) et une autre qui met tout ensemble pour un service (`revisar`). Et l'en-tête, qui est aussi une fonction, parce que c'est ainsi qu'on ne l'écrit qu'une fois. Enregistre `fig03_11.py`, qui réunit tout dans un fichier :

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

Lis la figure de bas en haut, parce que c'est ainsi qu'on comprend comment les fonctions s'appuient les unes sur les autres. À la fin, `main()` est l'appel qui met tout en marche ; `main` (« principal ») est le nom que, par habitude, on donne à la fonction qui démarre le programme. Dans `main`, la boucle `for i in range(len(NOMBRES))` parcourt les positions des listes parallèles et, à chaque tour, appelle `revisar` avec le nom, le code et le temps de cette position. `revisar` fait trois choses : elle demande l'état à `clasificar`, calcule le détail avec le même `if`/`else` de la Leçon 2 (le code en texte, ou « sin conexión »), et passe le tout à `linea`, qui compose la ligne à l'aide de `formatear_tiempo`. Chaque fonction fait **une seule chose**, porte un nom qui dit laquelle, et peut être testée seule.

Il y a deux détails à noter. Un : les constantes (`UMBRAL_LENTO_MS` et les trois listes) sont au début du fichier et les fonctions ne les reçoivent pas en argument. Une fonction peut **lire** des variables définies à l'extérieur d'elle ; la section 3.3 explique quand oui et quand non. Deux : le 1000 de `formatear_tiempo` (les millisecondes d'une seconde) et `UMBRAL_LENTO_MS` (la limite du lent) restent des choses distinctes, comme dans la Leçon 2. Et rappelle-toi d'où vient le `if`/`else` de `revisar` : quand le code est `None`, le détail est « sin conexión », et le code d'erreur s'affiche tel quel, comme `503`.

Ici se termine la première session. Ce que tu en emportes : un programme qui parcourt les quatre services et qui, pour changer le seuil ou le format du temps, n'a qu'un seul endroit où toucher.

### 3.3 Noms : où vit chaque variable, et `==` contre `is`

#### 3.3.1 Locale et globale

Quand Python voit un nom, il doit savoir **à quelle variable il se réfère**. La règle s'appelle *portée* (en anglais, *scope*), et [elle est dans le tutoriel officiel](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces). Pour cette leçon, deux sortes de noms suffisent :

- **Globale** : celle qui est créée au niveau du fichier, en dehors de toute fonction. `UMBRAL_LENTO_MS` et `NOMBRES` sont globales.
- **Locale** : celle qui est créée **à l'intérieur** d'une fonction, y compris ses paramètres. Elle n'existe que pendant que la fonction s'exécute, et disparaît quand elle se termine. Chaque appel de la fonction crée ses propres noms locaux, distincts de ceux des autres appels.

Une fonction peut **lire** des noms globaux sans problème, mais les noms locaux d'une fonction ne se voient pas de l'extérieur. Enregistre `fig03_12.py` :

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

Dans `es_lento`, `UMBRAL_LENTO_MS` est globale et se lit naturellement ; `tiempo_ms` et `limite` sont locales. En dehors de la fonction, `limite` n'existe pas. Si tu ajoutes à la fin du programme une ligne `print(limite)`, Python s'arrête avec cette erreur (essaie et vérifie que ton écran dit la même chose) :

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

La dernière ligne est celle qui commande : `NameError`, le nom `limite` n'est pas défini. La première ligne de la sortie, `True`, est celle qu'`es_lento(2300)` a eu le temps d'imprimer avant la chute. C'est la façon dont Python te dit « à cet endroit du programme, ce nom n'existe pas », et c'est la deuxième erreur la plus courante du débutant après celle des deux-points. C'est presque toujours l'une de trois choses : tu t'es trompé en écrivant le nom (rappelle-toi que les majuscules comptent), tu as utilisé le nom avant de le créer, ou tu l'as créé dans une fonction et tu le cherches à l'extérieur.

#### 3.3.2 Affecter dans une fonction crée un nom local

Il y a une règle de portée qui surprend presque tout le monde, et qui produit l'erreur de la section suivante. Ce qui décide si un nom est local ou global **n'est pas s'il existe à l'extérieur, mais si la fonction lui affecte une valeur quelque part dans son corps**. Si dans la fonction il y a une affectation à `total` (avec `=` ou avec `+=`, qui est une affectation déguisée), Python décide, avant d'exécuter quoi que ce soit, que `total` est **local dans toute cette fonction**. Même s'il existe un `total` global, la fonction n'y touche pas : elle en utilise un local, et si tu le lis avant de l'affecter, il n'a pas encore de valeur.

Cela, qui ressemble à un caprice, protège tes programmes : une fonction qui change des variables globales sans qu'on le remarque rend le programme impossible à comprendre (qui a changé `total` ?). La bonne manière pour une fonction d'agir sur le reste du programme est celle que tu connais déjà : **elle reçoit ce dont elle a besoin comme paramètres et renvoie ce qu'elle a calculé**. Python a un mot, `global`, qui permet le contraire, et je le mentionne seulement pour que tu le reconnaisses quand tu le verras dans du code d'autrui. Dans ce cours, il n'est pas utilisé.

#### 3.3.3 `==` contre `is`

Python a deux manières de demander si deux choses sont « la même », et elles signifient des choses différentes :

- **`a == b`** demande si **elles ont la même valeur** : sont-elles égales ?
- **`a is b`** demande si **elles sont le même objet** : sont-elles littéralement la même chose en mémoire, la même ?

Il y a une analogie utile : deux billets de cent pesos sont égaux en valeur (`==`), mais ne sont pas le même billet (`is`). Enregistre `fig03_13.py` :

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

`a` et `b` sont deux listes **distinctes** avec le même contenu : elles sont égales (`True`) mais ne sont pas la même (`False`). En revanche `c = a` ne copie pas la liste : il fait que `c` soit **un autre nom pour la même liste**, et c'est pourquoi `a is c` est `True`. (Ce qui se passe quand cette liste change, et comment on fait une vraie copie, est le sujet de « copie contre référence » dans la Leçon 4.)

Alors, quand utilise-t-on chacun ? **Presque toujours `==`**, pour comparer des valeurs : codes, textes, temps. **`is` est réservé à `None`** : comme il n'existe qu'un seul `None` dans le programme, la bonne question est de savoir si la valeur *est* cet objet, et c'est pourquoi la Leçon 2 t'a fait écrire `codigo is None`. C'est ce que demande le [guide de style](https://peps.python.org/pep-0008/#programming-recommendations). Avec `True` et `False`, il n'est même pas nécessaire de comparer : si `activo` est déjà un booléen, on écrit `if activo:`, et le même guide qualifie `if activo == True:` d'incorrect et `if activo is True:` de pire.

Le danger est d'utiliser `is` avec des nombres ou des textes, parce que parfois **cela semble fonctionner**. Python, par efficacité, réutilise le même objet pour les petits nombres entiers : [la documentation dit qu'il en garde un pour chaque entier entre -5 et 256](https://docs.python.org/3/c-api/long.html#c.PyLong_FromLong). C'est un détail d'implémentation de CPython, le Python que tu utilises, et non une promesse du langage. Le REPL le montre :

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

Avec 100, la comparaison réussit par accident ; avec 1000, non. Une comparaison avec `is` qui marche avec certains nombres et pas avec d'autres est une erreur qui attend son jour de sortie. Python te prévient quand il voit quelque chose comme cela. Si tu enregistres le programme suivant et que tu l'exécutes, il fonctionne, mais il imprime d'abord un avertissement :

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

C'est un `SyntaxWarning`, un avertissement, pas une erreur : le programme a continué et s'est bien terminé. Lis-le quand même. Il dit exactement ce que tu as mal fait et ce que tu voulais faire : `"is"` avec un nombre littéral, « tu voulais `==` ? ». Les avertissements sont la manière qu'a Python de te dire quelque chose qui n'explose pas aujourd'hui mais qui peut te mentir demain.

### 3.4 Modules : répartir le programme en fichiers

#### 3.4.1 Un fichier est un module

Un programme de cent lignes tient dans un fichier ; un de mille ne se lit plus bien. La solution de toujours est de le répartir : chaque fichier contient une seule sorte de choses, et les autres l'utilisent. En Python, **chaque fichier `.py` est un *module***, et un fichier en utilise un autre avec le mot **`import`**. Python fournit en outre des centaines de modules déjà écrits, la *bibliothèque standard*, qui s'importent de la même façon (par exemple, `statistics`, pour la statistique de base).

Il y a deux formes d'importer, et les deux apparaissent dans le `revisor` :

- **`import modulo`** : apporte le module entier, et ses noms s'utilisent avec le préfixe du module : `modulo.nombre`. C'est la forme qui rend le plus clair d'où vient chaque chose.
- **`from modulo import nombre1, nombre2`** : n'apporte que ces noms, qui s'utilisent directement, sans préfixe. Elle est commode quand tu n'as besoin que d'une ou deux choses.

Quand Python importe un module, selon [la documentation des modules](https://docs.python.org/3/tutorial/modules.html#the-module-search-path), il regarde d'abord si c'est l'un des rares modules **intégrés** à l'interpréteur lui-même (comme `sys`) ; sinon, il le cherche **dans le dossier du fichier qu'il exécute** puis dans la bibliothèque standard et dans les endroits où `pip` installe des choses. C'est pourquoi, pour que `import formato` fonctionne, `formato.py` doit se trouver dans le même dossier que `revisor.py`. La première fois que tu importes un module, Python le traduit aussi en *bytecode* (rappelle-toi la Leçon 0) et range le résultat dans un dossier appelé `__pycache__` à côté de lui, pour que la prochaine fois il se charge plus vite. Ce dossier apparaît tout seul ; ne le modifie pas et ne le range dans aucun dépôt.

#### 3.4.2 `if __name__ == "__main__":`

Un fichier peut être deux choses : un **programme** qu'on exécute (`python revisor.py`) ou un **module** qu'un autre fichier importe. Parfois, il est les deux. Il faut une manière de distinguer les deux cas, parce que quand quelqu'un importe ton module, il ne veut pas que le programme démarre tout seul. Python le résout avec une variable spéciale, `__name__` (avec deux tirets bas de chaque côté, qui se lisent « dunder ») : **elle vaut `"__main__"` quand le fichier est exécuté directement, et elle vaut le nom du module quand il a été importé**. [La documentation du module `__main__`](https://docs.python.org/3/library/__main__.html) explique ce comportement et l'idiome qui en profite. Enregistre les deux fichiers de la figure `fig03_14`, dans un dossier portant ce nom :

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

Exécute chaque fichier séparément, depuis le dossier `fig03_14` :

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

Quand on exécute `medidas.py` directement, `__name__` vaut `__main__`, et c'est pourquoi le `if` de la fin est satisfait et que les deux lignes du bas sont imprimées. Quand on exécute `uso.py`, le `import medidas` fait que Python **exécute `medidas.py` de haut en bas une fois**, et cette fois `__name__` vaut `medidas`, le nom du module, donc le `if` n'est pas satisfait et les deux dernières lignes ne sortent pas. Ensuite `uso.py` continue, avec son propre `__name__` valant `__main__`, et utilise `medidas.segundos` avec le préfixe du module. La dernière ligne utilise un module de la bibliothèque standard : `statistics.mean` calcule la moyenne de la liste, et donne 843, le chiffre qui dans la figure `fig03_06` était sorti avec `.0` à cause de la division à la main.

C'est ce que signifie l'idiome :

```text
if __name__ == "__main__":
    main()
```

« Si ce fichier est exécuté comme programme, appelle `main()` ». Si en revanche quelqu'un l'importe, il ne fait rien, et les fonctions restent disponibles. C'est une habitude de presque tout programme sérieux en Python, et c'est celle qui clôt le `revisor` ci-dessous.

#### 3.4.3 Couper le `revisor` en deux fichiers

Avec tout cela, le `revisor` se retrouve réparti en deux modules avec une division claire des responsabilités. `formato.py` contient **tout ce qui concerne l'apparence du tableau** (le format du temps, l'en-tête et la ligne). `revisor.py` contient **tout ce qui concerne la vérification** (les données, la classification et le parcours), et importe de `formato` ce dont il a besoin. Voici la figure de projet de la leçon : un dossier `fig03_15` avec deux fichiers. C'est l'état dans lequel reste ton `~/curso-python/revisor/` à la fin de la leçon, et le point de départ de la Leçon 4.

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

Remarque trois choses. **Premièrement**, `from formato import encabezado, linea` n'apporte que deux des trois fonctions de `formato.py` : `formatear_tiempo` n'est pas utilisée dans `revisor.py` (c'est `linea` qui l'utilise, à l'intérieur), et il n'est pas nécessaire de l'apporter. **Deuxièmement**, le programme imprime exactement le même tableau que `fig03_11`, celui d'un seul fichier : couper un programme ne change pas ce qu'il fait, seulement où vit chaque pièce. **Troisièmement**, la dernière ligne n'est plus `main()` tout court mais l'idiome de la section précédente ; maintenant, si à l'avenir un autre fichier importe `revisor`, le tableau ne sera pas imprimé sans le vouloir. C'est justement ce dont tu auras besoin quand, plus tard, tu écriras des tests qui importent tes fonctions.

Après l'avoir exécuté, regarde ce qui est apparu dans le dossier :

```console
$ ls
formato.py  __pycache__  revisor.py
```

Ce `__pycache__` est celui que Python a créé en important `formato` ; il y a rangé la version en *bytecode*. (L'ordre dans lequel `ls` range les noms dépend de la configuration de langue de ton terminal, donc il peut sortir différent chez toi.) Si tu vois là-dedans un fichier `formato.cpython-312.pyc`, le `312` est la version de Python qui l'a généré ; avec une autre version, le nombre change.

Un dernier détail de conception : `formato.py` ne sait **rien** des services. Il reçoit seulement un nom, un état, un temps et un détail, et renvoie du texte. Cette ignorance est une vertu : le module de format peut rester presque pareil quand, dans les leçons 4 et 5, les données changeront de forme.

## L'erreur que tu vas voir

Cette leçon a deux erreurs qui lui sont propres, et les deux s'apprennent mieux en les provoquant. Les deux sont copiées d'une exécution réelle. Et un rappel pour lire n'importe quel *traceback* : la dernière ligne dit **ce qui** s'est passé ; celles du dessus, **où**, de la plus récente (en bas) à la plus ancienne (en haut) dans la chaîne d'appels.

### `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value`

C'est l'erreur de la section 3.3.2. Enregistre ce programme, qui tente d'accumuler un total depuis l'intérieur d'une fonction, et exécute-le :

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

Une note sur cette sortie : c'est celle de Python 3.14. En Python 3.12, la ligne de l'appel (`sumar_tiempo(142)`) ne porte pas les marques `~~~~^^^^^` en dessous ; tout le reste, et en particulier la dernière ligne, est identique. C'est un bon exemple de la raison pour laquelle la lecture commence par le bas.

La dernière ligne dit : on ne peut pas accéder à la variable locale `total` parce qu'elle n'a pas encore de valeur associée. Les deux du dessus disent **où** : dans `sumar_tiempo`, à la ligne 5, qui est `total += tiempo_ms` ; et cette fonction a été appelée depuis la ligne 8 du programme. Pourquoi échoue-t-elle ? Parce que `total += tiempo_ms` est une affectation (elle équivaut à `total = total + tiempo_ms`), et d'après la règle de la section 3.3.2 cela fait de `total` une variable **locale** de toute la fonction ; mais pour additionner, la fonction doit lire la valeur actuelle de `total`, et le `total` local n'en a encore aucune. Le `total = 0` de l'extérieur est une autre variable, et la fonction ne la regarde même pas.

La correction est celle que prescrit la règle d'or des fonctions : qu'elle reçoive ce dont elle a besoin et renvoie ce qu'elle calcule. Par exemple, `def sumar_tiempo(total: int, tiempo_ms: int) -> int: return total + tiempo_ms`, et dans le programme, `total = sumar_tiempo(total, 142)`. [La documentation officielle a une entrée de questions fréquentes pour ce cas exact](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value), et [celle d'`UnboundLocalError`](https://docs.python.org/3/library/exceptions.html#UnboundLocalError) la définit comme l'erreur qui se produit quand on fait référence à une variable locale d'une fonction qui n'a pas encore de valeur.

### La liste qui se souvient des appels précédents

Ce n'est pas une erreur avec un message, et c'est pourquoi c'est pire : le programme ne plante pas, il **donne une réponse fausse sans prévenir**. C'est l'un des pièges les plus célèbres de Python. Enregistre ce programme, qui tient le compte des services en panne, et exécute-le :

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

Chaque appel était indépendant : aucun n'a passé de liste à la fonction. On s'attendait à voir `['reportes']`, `['facturacion']` et `['notificaciones']`. À la place, la liste **accumule** ce qui vient des appels précédents. C'est comme si la fonction avait de la mémoire.

L'explication vient du moment où une valeur par défaut est évaluée : **une seule fois, quand Python exécute le `def`, et non à chaque appel de la fonction**. Le `[]` de `caidos: list[str] = []` est créé une fois, à la définition de la fonction, et reste rangé à côté d'elle ; chaque appel qui ne passe pas sa propre liste utilise **cette même liste**, et `.append` la modifie sur place (rappelle-toi : les listes sont mutables). Ainsi, ce que le premier appel y a mis, le deuxième le retrouve. [Le tutoriel officiel le signale avec ce même exemple](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values), et [les questions fréquentes](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects) expliquent pourquoi il en est ainsi.

La règle est : **n'utilise jamais une liste (ni un dictionnaire, ni aucune autre valeur mutable) comme valeur par défaut**. Le bon schéma utilise `None` comme signal « on ne m'a rien passé » et crée la liste dans la fonction, où elle est créée neuve à chaque appel. Enregistre `fig03_16.py` :

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

Maintenant les deux premiers appels sont indépendants, comme on s'y attendait. Et quand on **veut** accumuler, la personne qui appelle le dit explicitement : elle crée sa propre liste (`historial`) et la passe à la fonction, qui l'utilise au lieu d'en créer une. Le paramètre admet `list[str] | None`, qui se lit « une liste de textes, ou rien ». Ce schéma (`None` par défaut et création à l'intérieur) tu le verras très souvent dans du code d'autrui. Et ce défaut est si connu que les outils de vérification le détectent d'eux-mêmes : `ruff`, que tu verras dans la Leçon 8, a une règle spécifique pour lui (la B006) et peut le signaler avant que tu n'exécutes le programme.

### `ModuleNotFoundError` et `ImportError`

Les deux erreurs de la section des modules. Si le nom d'un module est mal écrit, ou si le fichier n'est pas dans le dossier d'où l'on exécute, Python ne le trouve pas :

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

Et si le module existe mais que le nom que tu demandes n'y est pas, l'erreur est autre :

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

Les deux messages sont littéraux. Le premier dit qu'il n'y a aucun module appelé `formatos` (dans l'exemple on a écrit un `s` de trop). Le second dit que `formato` existe bien, mais qu'il n'a rien qui s'appelle `lineas` ; Python te montre le fichier où il a cherché (le chemin sera celui de ta machine) et te suggère même le nom que tu semblais vouloir : `linea`. Face à un `ModuleNotFoundError`, vérifie trois choses dans l'ordre : comment tu as écrit le nom, si le fichier est dans le dossier, et si tu te trouves dans le bon dossier quand tu exécutes le programme.

## Ce qui se fait de travers

**Imprimer au lieu de renvoyer.** `def total(...): print(...)` semble fonctionner tant que tu veux seulement voir le résultat. Coût : quand tu as besoin d'utiliser le résultat dans un autre calcul, ou de le tester, tu découvres que la fonction a renvoyé `None`. Les fonctions qui calculent, renvoient.

**Utiliser une liste comme valeur par défaut.** C'est l'erreur ci-dessus. Coût : des données qui se mélangent entre les appels sans aucun message d'erreur, et qui apparaissent en production sous la forme d'un rapport avec des services qui ne devraient pas y être.

**Changer une variable globale depuis une fonction.** Avec `global` c'est possible, et le programme devient un labyrinthe : pour comprendre quelle valeur a une variable, il faut lire toutes les fonctions. Si une fonction a besoin d'une donnée, qu'elle la reçoive ; si elle en produit une, qu'elle la renvoie.

**Comparer avec `is` des choses qui ne sont pas `None`.** Cela peut fonctionner avec de petits nombres et échouer avec les grands, ou donner un `SyntaxWarning` comme celui ci-dessus. Comparer des valeurs, c'est `==`.

**Un `while` sans progression.** Si le bloc ne rapproche pas la condition d'être fausse, le programme ne se termine jamais. Avant d'exécuter un `while`, repère la ligne qui le fait avancer.

**Écrire `range(len(NOMBRES))` puis ne toucher qu'une seule liste.** C'est la fragilité des listes parallèles : si tu ajoutes un service à `NOMBRES` et oublies d'ajouter son code ou son temps, le programme échoue (avec un `IndexError`) ou, pire, imprime des données qui ne sont pas de ce service. L'Exercice 1 le montre en action. Il n'y a pas de remède avec ce que tu sais aujourd'hui : le remède est de ranger chaque service comme une seule chose, et c'est le sujet de la Leçon 4.

**Nommer ton fichier comme un module de la bibliothèque standard.** Si tu crées `statistics.py` dans le dossier du projet et qu'un autre fichier fait `import statistics`, Python trouve **d'abord** le tien (rappelle-toi l'ordre de recherche : le dossier du programme passe avant la bibliothèque standard ; seuls les modules intégrés à l'interpréteur, comme `sys`, y échappent, parce qu'on les cherche avant n'importe quel dossier) et les noms du vrai module cessent d'exister. Le symptôme est une erreur du type `AttributeError: module 'statistics' has no attribute 'mean'` (les versions récentes de Python ajoutent à la fin une suggestion de renommer le fichier), et il déconcerte beaucoup parce que ton propre code n'a aucune erreur. Évite les noms `statistics`, `random`, `json`, `string`, `types` et les autres de la bibliothèque standard.

**Mettre `main()` tout court à la fin d'un module.** Quand un autre fichier l'importera, le programme démarrera tout seul. L'idiome `if __name__ == "__main__":` existe pour cela.

**Copier-coller une fonction au lieu de l'importer.** Si le même code est dans deux fichiers, tôt ou tard l'un des deux est corrigé et l'autre non. Ce qui est partagé, on l'importe.

## Exercices

### Exercice 1 — Ajouter un service et oublier une liste

Dans `fig03_15/revisor.py`, ajoute `facturacion` (code 503, temps 95 ms) aux listes. Fais-le deux fois. **Première fois :** ajoute `"facturacion"` à `NOMBRES` et `503` à `CODIGOS`, mais **oublie** `TIEMPOS_MS`. Prédis ce qui va se passer avant de l'exécuter. **Seconde fois :** ajoute les trois données mais dans un ordre différent : `503` au **début** de `CODIGOS` et `95` à la fin de `TIEMPOS_MS`. Prédis, puis compare avec ce que tu vois. Laquelle des deux défaillances est la plus dangereuse et pourquoi ?

### Exercice 2 — Compter les services en panne

Écris une fonction `contar_caidos(codigos: list[int | None]) -> int` qui reçoive la liste des codes et renvoie combien de services sont en panne selon la règle de toujours (sans code, ou avec un code de 400 ou plus). Teste-la avec `CODIGOS` (elle doit donner 1), avec `[200, 503, None]` (elle doit donner 2) et avec une liste vide `[]` (elle doit donner 0). Elle doit **renvoyer** le nombre, pas l'imprimer.

### Exercice 3 — Provoquer les erreurs de la leçon

Dans des copies de ton projet, provoque une par une : (a) utiliser un nom local depuis l'extérieur de sa fonction ; (b) un `total += x` dans une fonction ; (c) la liste qui se souvient ; (d) `from formato import lineas` ; (e) retirer `formato.py` du dossier. Pour chacune, copie la dernière ligne du message, écris ce qu'elle signifie et quelle est la correction.

### Exercice 4 — Le service le plus lent

Écris une fonction `mas_lento(nombres: list[str], tiempos_ms: list[int | None]) -> str | None` qui renvoie le **nom** du service avec le plus grand temps, en ignorant ceux qui n'ont pas répondu (ceux qui ont `None`). Si aucun n'a répondu, elle doit renvoyer `None`. Avec `NOMBRES` et `TIEMPOS_MS`, elle doit renvoyer `"inventario"`. Indice : parcours par position, garde dans deux variables le meilleur temps vu jusqu'ici et son nom, et mets-les à jour quand tu trouves un temps plus grand. Réfléchis à la valeur avec laquelle ces variables doivent commencer.

## Solutions

### Solution 1

Première défaillance, avec `TIEMPOS_MS` plus courte que les deux autres listes : la boucle passe sans problème par les quatre premiers services et, en arrivant au cinquième, `TIEMPOS_MS[4]` n'existe pas.

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

(C'est la sortie de Python 3.14 ; en 3.12, la ligne de marques `~~~~^^` sous `main()` n'apparaît pas, et tout le reste, y compris les marques de `TIEMPOS_MS[i]` et la dernière ligne, est identique.)

La dernière ligne dit que l'indice est hors de la plage de la liste : tu as demandé une position qui n'existe pas. C'est l'erreur que produisent les listes parallèles quand l'une se retrouve trop courte.

Seconde défaillance, avec les données dans un ordre différent : le programme **n'échoue pas**, et imprime ceci :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO      142ms  503
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    ARRIBA         —  200
facturacion CAIDO       95ms  sin conexión
```

Regarde comment chaque ligne est sortie. `catalogo` apparaît CAIDO avec le code 503, alors qu'il fonctionne. `reportes`, qui n'a pas répondu, apparaît ARRIBA avec le code 200 (et sans temps, parce que son temps était bien `None`). `facturacion` apparaît avec « sin conexión », alors qu'en réalité il a répondu avec un 503 en 95 ms. Les codes sont décalés d'une position par rapport aux temps, et rien ne prévient. C'est la plus dangereuse : la première défaillance se voit ; la seconde produit un rapport qui semble valide et ment. C'est la raison pour laquelle dans la Leçon 4 chaque service cessera d'être trois nombres épars dans trois listes pour devenir **une seule chose** qui ne peut pas se décaler.

### Solution 2

```python
def contar_caidos(codigos: list[int | None]) -> int:
    caidos = 0
    for codigo in codigos:
        if codigo is None or codigo >= 400:
            caidos += 1
    return caidos
```

Avec `CODIGOS`, elle donne `1`, avec `[200, 503, None]` elle donne `2` et avec `[]` elle donne `0` : la boucle ne fait aucun tour et renvoie la valeur avec laquelle le compteur avait commencé. Le `return` va **en dehors** de la boucle (à la marge du `for`) ; si tu le mettais dedans, la fonction se terminerait au premier tour. Et la condition est la même que dans `clasificar` : d'abord `is None`, pour que `None >= 400` ne soit jamais évalué.

### Solution 3

(a) `NameError: name 'limite' is not defined` (ou le nom que tu utilises) : le nom est local et n'existe pas à l'extérieur. Correction : renvoyer la valeur avec `return` et la ranger dans une variable à l'extérieur.

(b) `UnboundLocalError: cannot access local variable 'total' where it is not associated with a value` : l'affectation rend `total` local. Correction : le recevoir comme paramètre et renvoyer le nouveau.

(c) La liste qui accumule entre les appels, sans aucun message. Correction : `None` par défaut et créer la liste à l'intérieur.

(d) `ImportError: cannot import name 'lineas' from 'formato' (...)` : le module existe mais n'a pas ce nom. Correction : écrire `linea`.

(e) Sans `formato.py` dans le dossier : `ModuleNotFoundError: No module named 'formato'`. Correction : mettre le fichier là où est `revisor.py`, ou exécuter le programme depuis le dossier qui le contient.

### Solution 4

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

Avec les données du `revisor`, elle renvoie `"inventario"` ; avec `[None, None]` elle renvoie `None`. La clé est dans la valeur de départ : les deux variables commencent à `None`, ce qui signifie « je n'ai encore vu personne », et c'est pourquoi la question `mejor_tiempo_ms is None or ...` va en premier : le premier service qui a répondu gagne toujours, et à partir de là on compare. Si tu avais fait commencer `mejor_tiempo_ms` à 0, cela fonctionnerait avec ces données, mais donnerait une réponse absurde avec une liste de temps négatifs, et il faudrait décider quel nom renvoyer quand personne n'a répondu. `None` exprime cela sans rien inventer.

## Comment savoir que j'ai réussi

- [ ] Depuis `fig03_15` (ou depuis ton dossier `revisor/`), `python revisor.py` imprime l'en-tête et les quatre lignes du tableau, identiques à celles de la figure, y compris le long tiret et « sin conexión » sur celle de `reportes`.
- [ ] `python fig03_11.py` (tout dans un fichier) et `python revisor.py` (en deux fichiers) impriment exactement la même chose.
- [ ] En changeant `UMBRAL_LENTO_MS` en 100 dans `revisor.py`, `catalogo` passe à LENTO sans que tu touches aucune autre ligne.
- [ ] Après avoir exécuté le programme, il existe un dossier `__pycache__` à côté de `formato.py`, et tu sais dire pourquoi.
- [ ] Tu peux provoquer `UnboundLocalError` et `ImportError` exprès et dire, en ne regardant que la dernière ligne, ce qui s'est passé.
- [ ] Tu peux expliquer avec tes mots la différence entre `print` et `return`, entre `==` et `is`, et entre un paramètre et un argument.
- [ ] Tu peux expliquer pourquoi la fonction `registrar_caido` de la section des erreurs « se souvenait » et pourquoi la version avec `None` non.

## Résumé

Réponds sans regarder la leçon :

1. À partir de quel nombre commencent les positions d'une liste, et quelle est la dernière position d'une liste de `n` éléments ?
2. Que produit `range(len(NOMBRES))` si `NOMBRES` a quatre éléments ? Et que fournit `enumerate` à chaque tour ?
3. Quel risque a un `while` qu'un `for` n'a pas, et comment l'évites-tu ?
4. Quelle différence y a-t-il entre définir une fonction et l'appeler ? Qu'est-ce qu'un paramètre et qu'est-ce qu'un argument ?
5. Que renvoie une fonction qui n'a pas de `return` ? Pourquoi une fonction qui calcule doit-elle renvoyer et non imprimer ?
6. Quand une valeur par défaut est-elle évaluée, et pourquoi cela fait-il qu'une liste comme valeur par défaut « se souvienne » ? Quel est le bon schéma ?
7. Qu'est-ce qui décide si un nom est local ou global dans une fonction ? Pourquoi `total += x` échoue-t-il dans une fonction ?
8. Quelle question pose `==` et quelle question pose `is` ? Avec quelle valeur utilise-t-on `is` ?
9. Quelle valeur a `__name__` quand tu exécutes un fichier directement, et laquelle quand on l'importe ? À quoi cela sert-il ?
10. Pourquoi les trois listes parallèles du `revisor` sont-elles une mauvaise idée, et pourquoi les utilise-t-on aujourd'hui ?

## Pour aller plus loin

- [Le tutoriel Python, « Plus d'outils de contrôle de flux »](https://docs.python.org/3/tutorial/controlflow.html) — `for`, `range`, `break` et `continue`, `def`, valeurs par défaut et arguments nommés, dans un seul chapitre. Documentation officielle. Consulté le 7 octobre 2026.
- [Le tutoriel Python, « Modules »](https://docs.python.org/3/tutorial/modules.html) — `import`, `from ... import`, l'ordre de recherche et `__pycache__`. Consulté le 7 octobre 2026.
- [Questions fréquentes sur la programmation en Python](https://docs.python.org/3/faq/programming.html) — les pièges de cette leçon (la valeur par défaut mutable, `UnboundLocalError`, `is` contre `==`), avec l'explication de l'équipe de Python elle-même. Consulté le 7 octobre 2026.
- [PEP 8, le guide de style de Python](https://peps.python.org/pep-0008/) — noms, retrait et usage de `is` avec `None` ; c'est le guide que suit ce cours. Consulté le 7 octobre 2026.
