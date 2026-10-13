# Leçon 0 — Ce qu'est Python et ce qu'il n'est PAS

**Durée :** 90 min

**Ce que tu construis :** rien pour l'instant (lecture)

**Ce que tu apprends :** ce que Python fait de ton fichier (interpréteur et *bytecode*) ; typage dynamique mais fort ; les annotations de type ne sont pas imposées à l'exécution ; ce qu'est le GIL, expliqué sans peur ; ce qu'est un environnement virtuel et pourquoi le cours utilise Python 3.14 et aussi 3.12

**D'où tu viens.** De nulle part, et c'est très bien. Il n'est pas nécessaire que tu aies Python installé, que tu aies déjà écrit une ligne de code ni que tu saches ce qu'est un environnement virtuel. Cette leçon est **une leçon de lecture** : tu n'installes rien et tu ne construis encore rien. Les programmes qui apparaissent font une ou deux lignes, et chacun vient avec la sortie qu'il produit, de sorte que tu peux les suivre sans ordinateur sous les yeux. Si tu as déjà `python3` sur ton Linux Mint et que tu veux les essayer, vas-y ; sinon, la [Leçon 1](01-instalacion.md) prépare tout.

**Ce que cette leçon ne fait pas.** Elle n'apprend ni à programmer ni à installer. Elle apprend **ce qu'est la chose que tu vas apprendre**, et surtout ce qu'elle n'est *pas*, parce que la plupart des problèmes d'un débutant en Python ne viennent pas de la syntaxe mais d'une attente erronée : croire que Python signale une erreur de types avant de s'exécuter (il ne le fait pas), que « interprété » veut dire « sans rien compiler » (ce n'est pas si simple) ou que le GIL empêche de faire quoi que ce soit en parallèle (il empêche moins qu'on ne le croit). Bien poser les attentes dès le départ évite des semaines de confusion.

## À la fin, tu seras capable de

- Expliquer, en quatre étapes, ce que Python fait d'un fichier `.py` depuis son exécution jusqu'à l'apparition du résultat, et dire ce qu'est le *bytecode* et à quoi sert le dossier `__pycache__`.
- Dire pourquoi Python est **dynamique mais fort** et prédire ce qui se passe avec `"142" + 1` et avec `"142" + "1"` sans les exécuter.
- Expliquer pourquoi `tiempo_ms: int = "rápido"` s'exécute sans se plaindre, et qui peut signaler cette contradiction.
- Décrire le GIL avec tes propres mots, dire quand il gêne et quand il ne gêne pas, et pourquoi le `revisor` n'a pas à s'en préoccuper.
- Expliquer ce qu'est un environnement virtuel et pourquoi il existe, et justifier pourquoi le cours est enseigné avec Python 3.14 alors que tout le code s'exécute aussi en 3.12.
- Lire la dernière ligne d'un *traceback* de `TypeError` et dire ce qu'elle t'apprend.

## Le pourquoi avant le comment

Dans onze leçons, tu auras écrit un programme appelé le **`revisor`**. Il reçoit une liste de services (le catalogue de produits d'une boutique, son système de paiement, son inventaire), demande à tous en même temps s'ils fonctionnent et rend un tableau comme celui-ci :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
```

Lis-le comme le lirait quelqu'un d'astreinte à onze heures du soir. `catalogo` et `pagos` ont répondu vite. `inventario` a répondu, mais en 2.3 secondes, ce qui est trop : il est **lent**. `reportes` n'a pas répondu : il est **en panne**, et le détail dit pourquoi (`sin conexión`, « sans connexion »). Ce tableau est la destination du cours. Dans cette leçon, tu ne le construis pas, mais il te sert de matière : chaque donnée y est d'une nature différente (le nom est du texte, 142 est un nombre, le tiret `—` représente **l'absence de donnée**), et comprendre ces natures est exactement ce qui vient ensuite.

Avant d'écrire la moindre ligne, il faut répondre à trois questions que tout débutant se pose, même si ce n'est pas toujours à voix haute. La première : **qu'est-ce que Python exactement, et que fait-il de ce que j'écris ?** La deuxième : **qu'est-ce qui va me signaler mes erreurs, et qu'est-ce qui ne le fera pas ?** La troisième : **pourquoi vois-je des gens débattre du « GIL », de « l'environnement virtuel » et de « la version que tu utilises » ?** Les trois ont une réponse courte. La première : Python est un programme qui lit ton texte et l'exécute. La deuxième : presque rien ne te signale quoi que ce soit avant que le programme s'exécute, donc tu vas apprendre à lire les erreurs plutôt qu'à les craindre. La troisième : ce sont trois décisions pratiques qu'il convient de comprendre une fois pour toutes.

Un **programme** est une liste d'instructions écrites dans un fichier texte. Un **langage de programmation** est l'ensemble des règles avec lesquelles on écrit ces instructions pour qu'elles soient claires aussi bien pour toi que pour l'ordinateur. Le problème, c'est qu'à l'intérieur, l'ordinateur ne comprend que de minuscules instructions numériques (additionner deux quantités, copier une valeur d'un endroit à un autre) qu'on appelle **code machine**, et qui dépendent du processeur. Personne n'écrit à la main en code machine. Il y a toujours quelque chose entre les deux qui **traduit**, et la grande différence entre un langage et un autre tient à *quand* et *comment* il traduit. Python fait sa traduction d'une façon particulière, et cette façon explique presque tout le reste de cette leçon.

Un avertissement de vocabulaire avant de poursuivre. Le mot « Python » désigne deux choses différentes. L'une est le **langage** : les règles d'écriture, décrites dans une spécification publique. L'autre est le **programme qui exécute ce langage** sur ton ordinateur, et celui que presque tout le monde utilise s'appelle **CPython** (le « C » vient du fait qu'il est écrit en langage C). Quand tu tapes `python3` dans un terminal, tu appelles CPython. Il existe d'autres exécuteurs (PyPy, par exemple), mais ce cours, comme presque tout le travail professionnel, utilise CPython. Quand une expression comme « le GIL » apparaîtra plus bas, ce sera une caractéristique de CPython, pas du langage dans l'abstrait.

## Les concepts

Ils sont quatre : ce que l'interpréteur fait de ton fichier, ce que signifie que le typage soit dynamique mais fort (avec les annotations de type comme troisième volet), ce qu'est le GIL, et ce qu'est un environnement virtuel avec les versions. Ils sont expliqués dans cet ordre, chacun avec un exemple minimal.

### 0.1 L'interpréteur et le *bytecode*

#### 0.1.1 Ce qui se passe quand tu exécutes un fichier

Imagine que tu enregistres ceci dans un fichier appelé `lectura.py` :

```text
tiempo_ms = 142
print(tiempo_ms)
```

(Deux mots de lecture par avance. `tiempo_ms = 142` veut dire « range le nombre 142 sous le nom `tiempo_ms` » ; le nom porte `_ms` parce que c'est le temps en millisecondes, et dans ce cours les unités figurent toujours dans le nom. `print(...)` veut dire « affiche à l'écran ce qui se trouve entre les parenthèses ». La [Leçon 2](02-valores-texto-decisiones.md) explique les deux en détail.)

Pour l'exécuter, tu tapes `python3 lectura.py` dans un terminal. Ce qui se passe alors comporte quatre étapes, et il vaut la peine de les connaître parce que chacune explique un comportement qui, autrement, ressemble à de la magie.

1. **Python lit le texte.** Il ouvre le fichier et le parcourt de haut en bas, en vérifiant qu'il est bien écrit selon les règles du langage. S'il manque une parenthèse fermante, c'est ici qu'on le découvre, et le programme **ne commence pas à s'exécuter** : pas une seule ligne précédente n'est exécutée. Tu peux le vérifier avec un fichier dont la première ligne est `print("primera")` et dont la deuxième contient une parenthèse non fermée : « primera » n'apparaît pas, seule apparaît l'erreur `SyntaxError: '(' was never closed`. Autrement dit, la vérification de la forme a lieu avant l'exécution.
2. **Python traduit le texte en une liste d'instructions qui lui sont propres.** Pas en code machine, mais en un format intermédiaire, plus simple que ton texte et plus abstrait que le processeur. Cette liste s'appelle ***bytecode***. La [documentation officielle](https://docs.python.org/fr/3/glossary.html#term-bytecode) le définit comme « la représentation interne à CPython d'un programme Python ».
3. **Une machine virtuelle exécute le *bytecode*.** « Virtuelle » signifie que ce n'est pas un appareil physique mais un programme qui se comporte comme s'il en était un : il prend chaque instruction du *bytecode*, une par une, et fait ce qu'elle dit. Cette machine virtuelle est le cœur de CPython, et c'est ce que nous appelons l'**interpréteur**.
4. **Le résultat apparaît**, ici le nombre `142` sur ton écran.

Tout cela se passe en une fraction de seconde à chaque exécution du fichier, sans que tu aies à le demander. C'est pourquoi on dit que Python est un langage **interprété** : tu exécutes directement le fichier texte, sans étape préalable où tu génères toi-même un programme exécutable. La [documentation l'explique](https://docs.python.org/fr/3/glossary.html#term-interpreted) presque dans ces mots (« les fichiers sources peuvent être exécutés directement, sans avoir à compiler un fichier exécutable intermédiaire »), et y ajoute une réserve honnête : la frontière entre interprété et compilé est « floue en raison de la présence d'un compilateur en code intermédiaire ». C'est la réserve qui compte. Python compile **bel et bien** (l'étape 2 est une compilation), simplement il compile vers un format intermédiaire, et il le fait pour toi, en silence, à chaque fois.

Le contraste avec d'autres langages aide. En Go ou en Rust, tu écris ton code, tu lances un compilateur qui produit un fichier exécutable (du code machine directement pour ton processeur), puis tu lances ce fichier. L'exécutable n'a plus besoin du compilateur ni du langage : tu le copies sur un autre ordinateur et il tourne. En Python, il n'y a pas ce fichier final : l'ordinateur où tu veux exécuter ton programme a besoin d'**avoir Python installé**, parce que c'est Python qui lit et exécute ton texte à chaque fois. C'est une conséquence pratique que tu verras à partir de la Leçon 1, et c'est la raison pour laquelle la moitié de ce qu'on apprend « autour » de Python (versions, environnements, installation) tient à ce fait.

#### 0.1.2 Ce que Python conserve : `__pycache__` et les fichiers `.pyc`

Compiler en *bytecode* prend un peu de temps, et si le fichier n'a pas changé depuis la dernière fois, refaire cette traduction est du travail perdu. C'est pourquoi Python conserve le résultat. La [documentation du glossaire](https://docs.python.org/fr/3/glossary.html#term-bytecode) dit que le *bytecode* « est mis en cache dans un fichier `.pyc` de manière à ce qu'une seconde exécution soit plus rapide ». Ces fichiers vivent dans un dossier appelé `__pycache__`, à côté de ton code.

Il y a un détail qui surprend et qu'il vaut mieux mesurer que supposer. Si tu exécutes directement `python3 lectura.py`, **aucun** dossier `__pycache__` n'apparaît : Python compile le fichier que tu lui as donné en mémoire, l'exécute et ne conserve rien. Le dossier apparaît quand un fichier est **importé** depuis un autre, c'est-à-dire quand un programme utilise le contenu d'un autre fichier (`import` est expliqué dans la [Leçon 3](03-bucles-funciones-modulos.md)). On l'a mesuré ainsi : on a exécuté un fichier directement et on a compté zéro fichier `.pyc` ; on en a exécuté un autre qui importait le premier et il en est apparu un. Si tu veux forcer la création sans rien importer, il existe `python3 -m py_compile lectura.py`. Un extrait, avec les versions 3.12 et 3.14 de la même machine, laisse voir le nom généré :

```text
$ python3.12 -m py_compile lectura.py
$ python3.14 -m py_compile lectura.py
$ ls __pycache__
lectura.cpython-312.pyc
lectura.cpython-314.pyc
```

Regarde le nom : `lectura.cpython-312.pyc`. Il dit quel fichier c'était (`lectura`), quel exécuteur l'a généré (`cpython`) et avec quelle version (`312` est la 3.12). Le *bytecode* d'une version **ne sert pas** dans une autre, et la [documentation le signale](https://docs.python.org/fr/3/glossary.html#term-bytecode) : le code intermédiaire « n'a pas vocation à fonctionner sur différentes machines virtuelles Python ou à être stable entre différentes versions de Python ». C'est pourquoi Python conserve un fichier distinct par version et ne mélange pas ceux de l'une avec ceux de l'autre.

Trois conséquences pratiques :

- **`__pycache__` peut être supprimé sans risque.** Python le recrée quand il en a besoin. Il ne fait pas partie de ton programme, c'est un cache.
- **On ne le conserve pas dans le dépôt du projet.** Un dépôt est l'endroit où une équipe conserve et partage le code d'un programme, avec l'historique de ses modifications. On n'y met que ce que tu écris toi-même ; `__pycache__` est un dérivé de ton code et change avec chaque version de Python, donc on le laisse de côté.
- **Ce n'est pas une protection.** Certaines personnes croient qu'envoyer seulement les `.pyc` cache leur code. Ce n'est pas le cas : les `.pyc` peuvent être relus avec des outils, et ce n'est pas une mesure de sécurité.

#### 0.1.3 Voir le *bytecode* (juste par curiosité)

Python fournit un outil, le module `dis`, qui affiche le *bytecode* d'un fichier sous une forme lisible. Tu n'as pas besoin de l'apprendre, mais le voir une fois lève le mystère. Voici le résultat en Python 3.12 pour les deux lignes de `lectura.py` :

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

La colonne du milieu contient les instructions. `LOAD_CONST 142` signifie « mets la valeur constante 142 sous la main », `STORE_NAME tiempo_ms` signifie « range-la sous le nom `tiempo_ms` », et celles de la ligne 2 demandent le nom `print`, demandent le nom `tiempo_ms` et appellent la première avec la seconde. Chaque ligne de ton texte devient deux, trois ou quatre de celles-ci. Et voici la raison pour laquelle ce bloc est un **extrait** et non un programme du cours : *le bytecode change d'une version à l'autre*. En le mesurant en Python 3.14, la première instruction de la ligne 1 ne s'appelle plus `LOAD_CONST 142` mais `LOAD_SMALL_INT 142`, et l'ordre de deux instructions de la ligne 2 est différent. Le comportement du programme est le même ; la langue interne que la machine virtuelle utilise pour le décrire, non. Ce que tu dois retenir de tout cela n'est aucun de ces mots mais l'idée : entre ton texte et le résultat, il y a une liste d'instructions intermédiaire que tu n'écris pas et que Python te cache.

#### 0.1.4 Pourquoi cela compte pour le `revisor`

Deux choses. La première : Python met plus de temps qu'un programme compilé en code machine à exécuter des calculs purs, parce que chaque instruction du *bytecode* passe par la machine virtuelle. Dans un programme qui multiplie des millions de nombres, cela se remarque. Mais le `revisor` ne calcule presque pas : il **passe son temps à attendre** qu'un réseau réponde. Pendant qu'il attend 2.3 secondes la réponse d'`inventario`, la vitesse de Python n'a aucune importance. Ce qui comptera, ce sera d'attendre tous les services en même temps plutôt que l'un après l'autre, et c'est le sujet des leçons 9 et 10. La seconde : comme Python doit être installé là où ton programme s'exécute, et comme chaque version a son propre *bytecode* et son propre comportement, savoir **quel Python tu utilises** est une question que tu te poseras souvent. La réponse se trouve dans le dernier volet de cette leçon.

### 0.2 Typage dynamique, mais fort

#### 0.2.1 Ce qu'est un type

Une **valeur** est une donnée concrète : le nombre `142`, le texte `"catalogo"`. Le **type** d'une valeur est la sorte de chose qu'elle est : un nombre entier, un texte, un tiret qui signifie « il n'y a pas de donnée ». Un **nom** (ou variable) est une étiquette que tu fais pointer vers une valeur, comme `tiempo_ms` dans l'exemple précédent. Regarde le tableau du `revisor` : `catalogo` est un texte, `142` est un nombre, `—` est l'absence de donnée. Le type compte parce qu'il détermine **ce qu'on peut faire** avec la valeur : les nombres s'additionnent, les textes se collent les uns aux autres. Et la question qui distingue les langages est de savoir *quand et par qui* on vérifie que ce que tu essaies de faire a un sens pour ce type.

#### 0.2.2 Dynamique : le type vit dans la valeur, pas dans le nom

En Python, **le type appartient à la valeur, pas au nom**. Un nom peut pointer aujourd'hui vers un nombre et demain vers un texte, et Python s'en moque. La vérification qu'une opération a un sens a lieu **pendant que le programme s'exécute**, au moment même d'exécuter cette ligne : c'est ce que signifie **dynamique**. Cela contraste avec les langages à typage statique (Go, Rust, Java), où chaque nom est déclaré avec son type et où le compilateur vérifie tout avant d'exécuter.

Regarde la première figure. Elle tient en une seule ligne et il faut la lire morceau par morceau.

```python
# fig00_01.py
print(142 + 1, "142" + "1")
```

```text
$ python3 fig00_01.py
143 1421
```

La première ligne est un **commentaire** : tout ce qui suit un `#` est une note pour les humains que Python ignore. Ici, elle porte le nom de la figure, pour que tu saches de quel fichier il s'agit. La deuxième est celle qui s'exécute. `print(a, b)` affiche les deux valeurs séparées par une espace, et c'est pourquoi la sortie comporte deux éléments : `143` et `1421`. Ce qui est intéressant, c'est que **les deux utilisent le même signe `+`** et donnent des résultats de nature différente.

- `142 + 1` : les deux sont des nombres (sans guillemets), et `+` les **additionne** : 143.
- `"142" + "1"` : ce qui est entre guillemets est du **texte**, même si cela ressemble à un nombre. Un texte s'écrit entre guillemets, doubles ou simples. Ici `+` n'additionne pas : il **colle** un texte à l'autre, et le résultat est le texte `1421`, qui s'affiche sans les guillemets.

Le signe est le même, mais ce qu'il fait dépend du type des valeurs. C'est la première leçon sur les types : `"142"` et `142` **se ressemblent presque et sont des choses différentes**. Dans le `revisor`, le `142` du tableau est un nombre qu'on peut comparer à 1000 pour décider si un service est lent ; si par erreur il arrivait sous forme de texte `"142"`, cette comparaison n'aurait aucun sens.

Une autre façon de voir le côté dynamique est de laisser le même nom changer de type. Cet extrait est valide en Python :

```text
lectura = 142
lectura = "rápido"
```

Le nom `lectura` a d'abord pointé vers un nombre, puis vers un texte. Python ne proteste pas, parce qu'il n'y a aucun endroit où tu aies dit « `lectura` est un nombre » et où cette règle soit maintenue. Cette liberté est commode pour écrire vite et dangereuse pour écrire avec négligence, et c'est pourquoi ce cours, même si Python ne l'exige pas, t'apprendra à être ordonné : un nom, une sorte de donnée.

#### 0.2.3 Fort : Python ne devine pas ce que tu voulais dire

Que Python soit dynamique ne veut **pas** dire qu'il soit permissif. Il est dynamique **et fort** : quand tu tentes une opération qui n'a pas de sens pour ces types, Python **n'invente pas de conversion** ; il s'arrête et te dit qu'il y a une erreur. Voyons la deuxième figure, une seule ligne qui mélange un texte et un nombre.

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

Le programme **n'a rien affiché** : il s'est arrêté et a montré un rapport d'erreur, qui s'appelle en Python un ***traceback*** (quelque chose comme « la trace vers l'arrière »). Pour l'instant, regarde seulement la dernière ligne : `TypeError: can only concatenate str (not "int") to str`. « `TypeError` » est la classe de l'erreur (un problème de types) ; ce qui suit est l'explication, en anglais. Traduite : « on ne peut concaténer (coller) un `str` (texte) qu'avec un autre `str`, pas avec un `int` (nombre entier) ». Python te dit que tu as essayé de coller un texte avec un nombre et qu'il ne sait pas quoi faire. La section « L'erreur que tu vas voir » lit le reste du rapport ligne par ligne. (Sur ton écran, le chemin du fichier sera long et complet ; ici il est raccourci au nom pour que ce soit lisible.)

Voici le côté **fort**. D'autres langages, face à `"142" + 1`, tranchent de leur propre chef : JavaScript, par exemple, convertit le nombre en texte et renvoie `"1421"` sans prévenir. Cela peut sembler aimable et c'est une source classique d'erreurs, parce que le programme continue de s'exécuter avec une donnée que personne n'attendait. Python préfère la plainte immédiate à la conversion silencieuse. Cette décision joue en ta faveur : l'erreur apparaît **là où elle se produit**, avec le nom du problème et la ligne exacte, et non trois fonctions plus loin sous la forme d'un résultat bizarre.

Rassemble les deux moitiés et tu obtiens le comportement complet. **Dynamique** : la vérification des types a lieu à l'exécution de chaque ligne, pas avant. **Fort** : quand cette vérification échoue, Python s'arrête au lieu de deviner. Il en découle une conséquence à garder en tête : **une erreur de types n'apparaît que si cette ligne finit par s'exécuter**. Si ton programme a une branche utilisée une fois par mois, une erreur de types cachée là ne sera pas découverte avant ce jour-là. C'est un argument en faveur des tests (leçon 8) et des outils qui vérifient le code sans l'exécuter.

#### 0.2.4 Les annotations de type : une promesse que Python ne surveille pas

Python permet d'*écrire* le type que tu attends à côté d'un nom, et il le fait avec une syntaxe appelée **annotation** : `nombre: tipo = valor`. La [documentation les appelle « indications de type »](https://docs.python.org/fr/3/glossary.html#term-type-hint) (*type hints*) et dit deux choses importantes : qu'elles sont **facultatives** et que « Python ne les impose pas » (en anglais, *are not enforced*). Voyons ce que cela signifie avec la troisième figure :

```python
# fig00_03.py
tiempo_ms: int = "rápido"
print(tiempo_ms)
```

```text
$ python3 fig00_03.py
rápido
```

Lis-la calmement, car elle contient une contradiction délibérée. La ligne 2 dit : « le nom `tiempo_ms` est de type `int` » (`int` est l'abréviation d'*integer*, entier, le type des nombres sans décimales), puis lui assigne `"rápido"`, qui est un texte. Un langage à typage statique rejetterait le programme. Python **l'exécute sans se plaindre** et affiche `rápido`. L'annotation est restée écrite, mais personne ne l'a comparée à la valeur.

C'est la partie de la leçon qu'il vaut le mieux retenir : **les annotations de type ne sont pas imposées à l'exécution**. La spécification qui les a créées, [PEP 484](https://peps.python.org/pep-0484/), le dit sans détour : *Python reste un langage à typage dynamique, et les auteurs n'ont aucune intention de rendre les types obligatoires, même par convention*. Alors, pourquoi les écrit-on ?

- **Pour que les personnes les **lisent**.** Une annotation documente quelle sorte de donnée est attendue à chaque endroit, et à la différence d'un commentaire, elle a un format qui ne se périme pas facilement.
- **Pour que l'éditeur les **utilise**.** De nombreux éditeurs affichent des suggestions et signalent les contradictions pendant que tu écris.
- **Pour qu'un outil à part les **vérifie**.** Il existe des programmes appelés vérificateurs de types, le plus connu étant `mypy`, qui lisent ton code **sans l'exécuter** et signalent que `tiempo_ms: int = "rápido"` est une contradiction. Ils sont enseignés dans la [Leçon 8](08-pruebas-tipos-calidad.md). La [documentation de `mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) explique que sa vérification est **graduelle** : elle vérifie les parties annotées et laisse passer celles qui ne le sont pas.
- **Pour que d'autres éléments du langage en profitent.** Dans la [Leçon 5](05-modelo-de-datos.md), tu utiliseras `dataclass`, un outil qui lit les annotations pour construire des choses ; là, elles remplissent une vraie fonction, même si elles ne valident toujours pas les valeurs.

Autrement dit, en Python **il y a deux vérificateurs différents** : l'interpréteur (il vérifie à l'exécution, de façon forte mais tardive) et le vérificateur de types (il vérifie avant l'exécution, mais seulement si tu le lances et seulement ce que tu as annoté). L'interpréteur ne consulte jamais les annotations pour décider si quelque chose est valide. Si tu viens du cours de [TypeScript](https://www.habil.mx/fr/cours/typescript/) de Hábil, le principe est le même que là-bas : les types écrits sont une promesse qu'un outil peut contrôler, pas une barrière que le programme dresse à l'exécution.

Et il y a une limite qu'aucune annotation ne franchit : **les données qui viennent de l'extérieur**. Si ton programme lit un fichier de configuration et que quelqu'un y écrit `"timeout_ms": "rápido"`, peu importe ce que tu as annoté dans ton code : le texte arrivera tel quel. Ces données, il faut les **valider** à l'entrée, avec du code qui les compare vraiment, et cela se fait dans la [Leçon 6](06-errores-archivos-datos.md). L'annotation est une promesse entre les parties de ton programme ; la validation est ce qui protège de ce que le programme ne contrôle pas.

Une dernière information d'actualité, sans conséquence pour toi : en Python 3.14, *le moment* où les annotations sont évaluées a changé (elles cessent d'être évaluées au moment de leur définition), d'après la [liste des nouveautés de la version](https://docs.python.org/3/whatsnew/3.14.html). Pour écrire du code qui s'exécute à l'identique en 3.12 et en 3.14, ce cours évite de dépendre de ce changement, et le signale quand c'est nécessaire.

### 0.3 Le GIL, expliqué sans peur

Tôt ou tard, quelqu'un te dira « Python ne peut pas faire de choses en parallèle à cause du GIL ». La phrase fait peur et simplifie trop. Allons-y par étapes.

D'abord, deux mots. Un **thread** (*fil d'exécution*) est une ligne d'exécution à l'intérieur d'un programme : un programme peut en avoir plusieurs, et en principe chacun peut avancer pendant que les autres attendent. Et un **processeur** moderne a plusieurs cœurs, qui peuvent exécuter des instructions au même instant. Profiter de plusieurs cœurs avec plusieurs threads, c'est ce qu'on appelle le **parallélisme**.

Le **GIL** (*Global Interpreter Lock*, « verrou global de l'interpréteur ») est une règle de CPython. La [documentation le définit](https://docs.python.org/fr/3/glossary.html#term-global-interpreter-lock) ainsi : c'est le mécanisme qui garantit qu'**un seul thread exécute du *bytecode* Python à la fois**. Il existe parce qu'il simplifie la conception de l'interpréteur : les structures internes, comme les dictionnaires, sont protégées contre la modification simultanée par deux threads. Le prix, dit la même définition, est qu'on perd une bonne partie du parallélisme des machines à plusieurs processeurs.

Traduit dans la pratique, le GIL affecte de façon différente deux sortes de travail :

- **Travail de calcul** (convertir mille images, compresser un gros fichier) : avec des threads Python, il n'est pas réparti entre les cœurs ; un seul thread calcule à la fois. Ici le GIL gêne.
- **Travail d'attente** (interroger un réseau, lire un fichier, attendre la réponse d'une base de données) : le thread qui attend relâche le verrou tant qu'il n'exécute pas de Python, et un autre peut avancer. Ici le GIL ne gêne presque pas. La [documentation du module `threading`](https://docs.python.org/3/library/threading.html) le dit ainsi : les threads restent un bon modèle quand on veut exécuter plusieurs tâches d'**entrée/sortie** en même temps.

Le `revisor` est du second type, **presque entièrement**. Son travail est d'attendre des réponses du réseau, pas de calculer. Et de plus, il n'utilisera pas de threads : il résoudra « interroger tout le monde en même temps » avec **`asyncio`**, qui tourne dans un seul thread et alterne entre les tâches chaque fois que l'une se met à attendre. Dans ce schéma, le GIL n'entre même pas dans la conversation. Tu peux l'oublier pendant ce cours, mais pas l'information : savoir qu'il existe te permet de ne pas croire, ni répéter, la phrase exagérée.

Et si un jour tu voulais du calcul en parallèle ? Il existe aujourd'hui deux chemins que ce cours ne parcourt pas : utiliser plusieurs **processus** (chacun avec son propre interpréteur et son propre GIL) et, depuis peu, une variante de CPython **sans GIL**. L'histoire de cette variante, en résumé : [PEP 703](https://peps.python.org/pep-0703/) a proposé de rendre le GIL optionnel et elle est apparue comme expérience en 3.13 ; [PEP 779](https://peps.python.org/pep-0779/) l'a déclarée officiellement **prise en charge** à partir de la 3.14, mais **ce n'est pas l'option par défaut** : c'est un exécutable à part, avec un coût en vitesse quand on n'utilise qu'un seul thread, et de nombreuses bibliothèques sont encore en cours d'adaptation. C'est ce qu'on appelle dans ce cours « ce qui vient » : on le mentionne, on ne l'utilise pas et on ne le recommande pas pour la production d'emblée.

### 0.4 L'environnement virtuel et les versions

#### 0.4.1 Le problème que résout un environnement virtuel

Pense à ta cuisine. Tu as un garde-manger commun, où vivent les choses que toute la famille utilise : sel, huile, riz. Si, pour une expérience, tu te mets à y ranger de drôles de bocaux, à changer le riz pour un autre type ou à retirer l'huile, tu gênes les autres et un jour quelqu'un ne pourra plus cuisiner. Le plus sensé est d'avoir ton **étagère à toi** pour tes expériences.

Le Python que ton Linux Mint fournit est le garde-manger commun. Le système d'exploitation l'utilise pour ses propres outils, et il dépend de ce que ses bibliothèques soient dans une version déterminée. Si tu y installes des paquets à toi, ou si tu en changes un, tu cours le risque de casser quelque chose du système. Et il y a un second problème, indépendant du premier : **deux de tes projets peuvent avoir besoin de versions différentes de la même bibliothèque**. Si tous les paquets vivent au même endroit, l'un des deux projets perd.

La solution s'appelle **environnement virtuel** (*virtual environment*, *venv*) : un dossier avec son propre Python (sous Linux, un raccourci vers le Python avec lequel il a été créé, pas une copie ; la Leçon 1 le montre) et son propre espace pour les paquets, isolé du reste. La [documentation officielle](https://docs.python.org/fr/3/glossary.html#term-virtual-environment) le définit comme un environnement d'exécution « isolé (en mode coopératif) » qui permet d'installer et de mettre à jour des paquets « sans interférer avec d'autres applications Python fonctionnant sur le même système ». Ce que tu installes dans un environnement n'y vit qu'à cet endroit ; si quelque chose se passe mal, tu supprimes le dossier de l'environnement et tu le recrées, et le système ne s'en aperçoit même pas.

Les distributions Linux ont pris cela au sérieux. Depuis l'existence de la spécification [PEP 668](https://peps.python.org/pep-0668/), une distribution peut marquer son Python comme **« géré en externe »** : cela signifie que ce Python appartient au gestionnaire de paquets du système et que `pip` (l'outil de Python pour installer des paquets) doit refuser d'y installer quoi que ce soit en dehors d'un environnement virtuel. Sur ton Linux Mint, la protection est encore plus directe : son Python n'a même pas `pip`. Tu verras ce refus de tes propres yeux, et tu apprendras à lire les deux formes qu'il prend, dans la Leçon 1. Pour l'instant, il suffit de savoir que **ce n'est pas une défaillance de ton installation** : c'est une protection, et la bonne sortie est l'environnement virtuel.

#### 0.4.2 Les versions, et pourquoi deux

Les versions de Python ont trois nombres : `3.14.8` se lit majeur, mineur et correctif. Le premier (3) n'a pas changé depuis des années. Le second (14) change **une fois par an, en octobre**, et apporte des nouveautés. Le troisième (8) correspond aux corrections d'erreurs qui ne changent pas ce que le langage permet. Quand on dit « Python 3.12 », on parle d'une lignée de versions, et le correctif peut être n'importe lequel.

Trois faits soutiennent les décisions du cours, tous mesurés à la date où cette leçon a été écrite (7 octobre 2026) :

- **La version stable en vigueur est la 3.14.** Elle est sortie le 7 octobre 2025, et la [page officielle de téléchargement](https://www.python.org/downloads/) affichait comme dernière la 3.14.8, du 30 septembre 2026. La 3.15 était prévue pour octobre de cette année selon le [guide du développeur](https://devguide.python.org/versions/) et apparaissait encore à l'état de préversion.
- **Linux Mint 22.x fournit Python 3.12.** Mint 22 et ses mises à jour (22.1, 22.2, 22.3) sont construites sur la base d'Ubuntu 24.04, avec un [support jusqu'en avril 2029](https://linuxmint.com/download_all.php), et c'est cette base qui décide du Python fourni : la lignée 3.12.
- **La 3.12 continue de recevoir des correctifs de sécurité jusqu'en octobre 2028**, selon le même guide du développeur. En revanche, la 3.10 est arrivée en fin de vie le 1er octobre 2026 : qui y reste ne reçoit plus même de correctifs de sécurité.

De là vient la décision : **le cours est enseigné avec Python 3.14 et tout son code s'exécute aussi en 3.12**, celui que fournit ton Mint. Chaque programme des leçons est exécuté avec les deux versions et son résultat est comparé à celui que tu vois dans le texte. Cela a un coût, qui est de ne pas utiliser une poignée de nouveautés qui n'existent qu'en 3.14, et un avantage décisif : **tu n'as rien de spécial à installer** pour suivre le cours, ni à cesser d'utiliser le Python de ton système. Si un jour tu veux essayer la 3.14, la Leçon 7 te présente une façon commode de l'installer.

Ainsi, quand la commande `python3` apparaîtra, ce qui tourne sur ton Mint est la 3.12, et c'est normal. Un dernier avertissement qui t'épargnera un après-midi : sur beaucoup de systèmes, la commande `python` (sans le 3) n'existe pas, ou pointe vers autre chose. En terminant cette leçon, tu connais la règle du cours : **en dehors d'un environnement virtuel, on écrit `python3` ; dans l'environnement, `python` pointe vers le Python de l'environnement** (la Leçon 1 le vérifie avec `which`).

## L'erreur que tu vas voir

La seule erreur de cette leçon est celle de la figure 2, et il convient de la lire en entier parce que tous les rapports d'erreur de Python ont la même forme. La voici de nouveau, avec le nom de chaque ligne ; il n'est pas nécessaire de la ré-exécuter.

La première ligne du rapport est `Traceback (most recent call last):`, qui se traduit « trace, appel le plus récent en dernier ». C'est un signe que ce qui suit est une liste d'endroits, ordonnée **du plus ancien au plus récent**, et que ce qui s'est produit se trouve **à la fin**. C'est pourquoi la règle d'or pour lire un rapport d'erreur en Python est de **commencer par la dernière ligne et de remonter**.

La dernière ligne est `TypeError: can only concatenate str (not "int") to str`. Elle contient la **classe** de l'erreur (`TypeError`) et son **message**. `TypeError` veut dire qu'une opération a reçu une valeur d'un type qu'elle n'admet pas. Le message dit exactement lequel : on a voulu coller (`concatenate`) un `str` avec quelque chose qui n'était pas un `str`, mais un `int`. Avec cela seul, tu sais déjà ce qui s'est passé et pourquoi.

En remontant d'une ligne, tu trouves le dessin de l'erreur : `print("142" + 1)` dans la ligne de code, et dessous une marque faite de tildes et d'un accent circonflexe (`~~~~~~^~~`). Cette marque indique **quelle partie exacte** de la ligne a échoué : le `+` qui relie `"142"` à `1`. C'est une aide que les versions récentes ajoutent, et elle t'évite de deviner dans une longue ligne.

Remonte encore d'une ligne : `File "fig00_02.py", line 2, in <module>`. Elle te dit **dans quel fichier**, **à quel numéro de ligne** et **à l'intérieur de quoi**. Le mot `<module>` signifie « au niveau du fichier, pas à l'intérieur d'une fonction » ; quand tu connaîtras les fonctions (Leçon 3), tu verras ici le nom de la fonction à la place de `<module>`. La ligne est la 2 parce que la 1 est le commentaire portant le nom de la figure.

La correction n'est pas de convertir n'importe quoi en texte pour faire taire l'erreur. Décide d'abord ce que tu voulais. Si tu voulais additionner, les deux doivent être des nombres (`142 + 1` donne 143). Si tu voulais composer un message de texte, les deux doivent être du texte (`"142" + "1"`), et alors le résultat est collé, pas additionné. L'erreur t'a obligé à décider ce que chaque donnée représentait. C'est ce que fait un bon message d'erreur.

## Ce qui se fait de travers

- **Croire qu'une annotation valide la donnée.** Écrire `tiempo_ms: int` n'empêche pas que `tiempo_ms` vaille `"rápido"`. Si tu as besoin de la garantie, il faut un vérificateur de types (pendant que tu écris) ou une validation explicite (quand la donnée vient de l'extérieur). L'annotation seule ne fait ni l'un ni l'autre.
- **Corriger un `TypeError` en convertissant tout en texte.** Mettre des guillemets ou appeler une fonction de conversion jusqu'à ce que l'erreur disparaisse cache le fait que tu as mélangé deux idées. Demande-toi d'abord ce que chaque valeur devrait être.
- **Dire « Python est interprété, donc il ne compile pas ».** Il compile (en *bytecode*) ; il le fait pour toi et à chaque exécution. Dire « sans compiler » mène à des surprises, comme ne pas comprendre ce qu'est un `__pycache__` ni pourquoi les erreurs de syntaxe apparaissent avant la première ligne.
- **Accuser le GIL de toute lenteur.** Un programme qui attend un réseau n'est pas lent à cause du GIL : il est lent parce qu'il attend, et cela se règle en attendant tout le monde en même temps. Avant d'accuser le GIL, mesure ce que fait ton programme pendant qu'il tarde.
- **Conserver `__pycache__` dans le dépôt, ou croire qu'il faut le protéger.** C'est un cache de Python, dérivé de ton code, différent à chaque version. On le laisse de côté.
- **Installer des paquets avec `sudo pip` dans le Python du système.** C'est le raccourci qu'il faut refuser et celui qui conduit à casser des outils du système. Chaque paquet de tes projets vit dans un environnement virtuel (Leçon 1). Même si `pip` offre une option pour contourner la protection de PEP 668, le cours ne l'enseigne **pas** et ne l'utilise pas.
- **Mélanger `python` et `python3` sans savoir lequel est lequel.** Au moindre doute du type « quel Python suis-je en train d'utiliser ? », la bonne question est `which`, et la réponse vient dans la prochaine leçon.

## Exercices

### Exercice 1 — Les données du tableau

Regarde le tableau du `revisor` au début. Pour chacune de ces quatre cellules, dis si sa donnée est un **nombre**, un **texte** ou **rien** (absence de donnée) : le `142` de `catalogo`, le `catalogo` de la première colonne, le `—` du temps de `reportes`, et le `200` du détail de `pagos`. Réponds ensuite : pourquoi serait-ce un problème que le temps d'`inventario` arrive dans le programme sous la forme du texte `"2300"` au lieu du nombre 2300 ?

### Exercice 2 — Prédis avant d'exécuter

Sans rien exécuter, écris ce que fait chacune de ces trois lignes : celle qui affiche un résultat, celle qui affiche un autre résultat différent et celle qui échoue. Pour celle qui échoue, écris la **dernière ligne** du rapport d'erreur.

```text
print(142 + 1)
print("142" + "1")
print(142 + "1")
```

### Exercice 3 — La promesse que personne ne surveille

Avec la figure 3 sous les yeux (`tiempo_ms: int = "rápido"`), réponds avec tes propres mots : (a) pourquoi le programme affiche-t-il `rápido` et non une erreur ? (b) Si tu installais un vérificateur de types et le lançais sur ce fichier, que t'attendrais-tu à ce qu'il dise ? (c) Si la valeur `"rápido"` arrivait d'un fichier de configuration et non d'une ligne écrite par toi, l'annotation servirait-elle à quelque chose ?

### Exercice 4 — Explique-le à un collègue

Un collègue te dit : « Python est lent parce qu'il est interprété et ne peut rien faire en parallèle à cause du GIL, donc pour interroger beaucoup de services il faut utiliser un autre langage ». Écris ta réponse en quatre ou cinq phrases, en corrigeant avec précision ce qui est incomplet ou exagéré et en disant ce que fait réellement le `revisor` presque tout son temps.

## Solutions

### Solution 1

Le `142` est un **nombre** ; `catalogo` est un **texte** ; le `—` représente qu'**il n'y a pas de donnée** (le service n'a pas répondu, donc il n'y a pas de temps à mesurer) ; le `200` du détail est le code avec lequel le service a répondu et, dans le tableau, il est affiché comme du texte, parce que dans cette colonne peuvent aussi apparaître des choses comme `sin conexión` (cette colonne mélange les deux sortes, et c'est pourquoi le programme la traitera toujours comme du texte). Que le temps d'`inventario` arrive sous la forme du texte `"2300"` serait un problème parce que le `revisor` le compare au seuil de 1000 pour décider si le service est lent. Un texte ne se compare pas de façon significative à un nombre : Python, étant fort, s'arrêterait avec un `TypeError` au lieu de rendre un verdict faux.

### Solution 2

La première ligne additionne deux nombres et affiche `143`. La deuxième colle deux textes et affiche `1421`. La troisième échoue, parce qu'elle mélange un nombre et un texte ; la dernière ligne du rapport est `TypeError: unsupported operand type(s) for +: 'int' and 'str'`. Le message est différent de celui de la figure 2 parce qu'ici le nombre est à gauche : Python essaie d'abord d'additionner et, ne pouvant pas, dit que l'opérateur `+` n'admet pas un `int` avec un `str`. L'important est la classe (`TypeError`) et de comprendre que la cause est la même : deux types ont été mélangés.

### Solution 3

(a) Parce que les annotations ne sont pas imposées à l'exécution : Python a enregistré l'annotation `int` mais ne l'a jamais comparée à la valeur assignée. (b) Qu'il y a une contradiction : on a déclaré un `int` et on lui a assigné un texte. Le vérificateur lit le code sans l'exécuter et compare les annotations aux valeurs. (c) Non : une annotation est une promesse entre des parties de *ton* code. Une valeur qui arrive de l'extérieur entre telle qu'elle vient, quel que soit son contenu, et seule une validation explicite à l'entrée (Leçon 6) peut vérifier que c'est bien un nombre.

### Solution 4

Une réponse possible : « Il est vrai que Python exécute plus lentement les calculs purs, mais un programme qui interroge des services ne calcule presque pas : il passe son temps à attendre des réponses du réseau. Le GIL empêche deux threads d'exécuter du *bytecode* Python en même temps, mais un thread qui attend relâche le verrou, et de toute façon le `revisor` n'utilise pas de threads mais `asyncio`, qui alterne des tâches dans un seul. Ce qui décide du temps que cela prend, c'est d'attendre tout le monde en même temps plutôt que l'un après l'autre : avec quatre services qui mettent 142, 2300 et 87 millisecondes (le quatrième ne répond pas), en série cela fait près de 2.5 secondes et en simultané cela prend à peu près ce que prend le plus lent, environ 2.3. Et si un jour il fallait du calcul lourd en parallèle, il existe d'autres chemins, comme plusieurs processus. »

## Comment savoir que j'ai réussi

- [ ] Tu peux énumérer de mémoire les quatre étapes entre l'exécution d'un fichier et la vue du résultat (lire et vérifier la forme, traduire en *bytecode*, exécuter dans la machine virtuelle, afficher le résultat) et dire à laquelle on détecte une parenthèse non fermée.
- [ ] Tu peux expliquer à quoi sert `__pycache__`, dire pourquoi on peut le supprimer sans risque et pourquoi on ne le conserve pas dans le dépôt.
- [ ] Tu sais prédire que `print(142 + 1, "142" + "1")` affiche `143 1421`, et que `print("142" + 1)` se termine par un `TypeError` ; et tu peux expliquer la différence entre « dynamique » et « fort » avec ces deux exemples.
- [ ] Tu peux dire, sans regarder la leçon, pourquoi `tiempo_ms: int = "rápido"` ne donne pas d'erreur à l'exécution et quelle sorte d'outil la signalerait.
- [ ] Tu peux expliquer en deux phrases ce qu'est le GIL, quand il gêne (calcul avec des threads) et pourquoi il ne gêne pas le `revisor`.
- [ ] Tu peux expliquer avec une analogie à toi ce qu'est un environnement virtuel et pourquoi Linux Mint refuse `pip install` dans son Python du système.
- [ ] Tu peux dire quelle version de Python fournit Mint 22.x, laquelle est en vigueur à la date de la leçon, et pourquoi le cours est enseigné avec l'une et s'exécute sur les deux.

## Résumé

Réponds sans regarder la leçon :

1. Quelles deux choses le mot « Python » désigne-t-il ? Qu'est-ce que CPython ?
2. Qu'est-ce que le *bytecode* et où est-il conservé ? Pourquoi un `.pyc` de 3.12 ne sert-il pas en 3.14 ?
3. Quelle différence y a-t-il entre typage dynamique et typage fort ? Que donne leur combinaison ?
4. Qui vérifie les annotations de type, et qui ne les vérifie pas ?
5. Qu'est-ce que le GIL ? Dans quel type de travail gêne-t-il, et dans lequel presque pas ?
6. Quel problème résout un environnement virtuel ? Pourquoi Mint ne laisse-t-il pas `pip` installer dans son Python du système ?
7. Pourquoi le cours est-il enseigné avec la 3.14 et s'exécute-t-il aussi en 3.12 ?

## Pour aller plus loin

- [Glossaire de Python](https://docs.python.org/fr/3/glossary.html) — les définitions officielles de *bytecode*, interprété, GIL, environnement virtuel et indication de type citées dans la leçon, d'après la traduction française officielle (certaines entrées n'y sont encore qu'en anglais). Consulté le 7 octobre 2026.
- [PEP 484, « Type Hints »](https://peps.python.org/pep-0484/) — le document qui a introduit les annotations de type et qui dit qu'elles ne sont pas imposées à l'exécution. Consulté le 7 octobre 2026.
- [PEP 668, « Marking Python base environments as externally managed »](https://peps.python.org/pep-0668/) — l'origine de l'avertissement `externally-managed-environment` que la prochaine leçon t'apprend à reconnaître. Consulté le 7 octobre 2026.
- [Guide du développeur : état des versions de Python](https://devguide.python.org/versions/) — quelle version est en vigueur, laquelle reçoit des correctifs de sécurité et quand chacune se termine. Consulté le 7 octobre 2026.
