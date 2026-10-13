# Leçon 1 — Installer Python sur ton Linux Mint

**Durée :** 90 min

**Ce que tu construis :** l'environnement virtuel du cours, ton premier script (`hola.py`) et le fichier où vivra le `revisor`

**Ce que tu apprends :** le `python3` du système et pourquoi il n'installe pas de paquets (`No module named pip` et l'avertissement `externally-managed-environment`) ; créer, activer et désactiver un environnement virtuel (`venv`) ; `pip` dans l'environnement ; le REPL et l'exécution d'un fichier ; lire le premier *traceback*

**D'où tu viens.** De la [Leçon 0](00-que-es-python.md), qui était une leçon de lecture : tu sais déjà que Python lit ton fichier, le traduit en *bytecode* et l'exécute ; que les types sont vérifiés à l'exécution et non avant ; que le GIL ne va pas te gêner ; et qu'il existe quelque chose qu'on appelle environnement virtuel, qui protège le Python de ton système. Aujourd'hui, tu cesses de lire et tu passes au terminal. Tu travailles sur un ordinateur sous **Linux Mint 22.x** (n'importe laquelle de ses versions, de la 22 à la 22.3, qui partagent la même base) avec un terminal ouvert. Presque rien de ce que tu feras ne demande des droits d'administrateur : tout au plus une ligne (contenant deux commandes d'administrateur), et seulement si ton Mint ne fournit pas la pièce qui crée les environnements virtuels (tu le verras en 1.2.2). Mieux encore, l'une des choses que tu apprendras aujourd'hui est à **ne pas** installer de paquets Python avec ces droits.

**Ce que cette leçon ne fait pas.** Elle n'enseigne pas encore le langage : le `print` que tu vas utiliser est expliqué en une ligne et la [Leçon 2](02-valores-texto-decisiones.md) l'étudie à fond. Elle n'installe pas non plus `uv` ni `pipx`, d'autres outils que tu verras plus tard : aujourd'hui on utilise ce que le système fournit déjà, parce que comprendre l'environnement avec les pièces de base est ce qui te permettra ensuite de comprendre pourquoi les autres outils existent.

## À la fin, tu seras capable de

- Vérifier quel Python ton Mint fournit (`python3 --version`) et d'où il s'exécute (`which python3`).
- Tenter volontairement d'installer un paquet dans le Python du système, lire la réponse et expliquer pourquoi Mint protège son Python, à quoi ressemble l'avertissement `externally-managed-environment` sur les systèmes qui ont bien `pip`, et quelle est la bonne sortie.
- Créer l'environnement virtuel du cours avec `python3 -m venv`, l'activer, vérifier avec `which python` que tu es dedans, installer un paquet avec `pip` et le désactiver.
- Écrire une expression dans le REPL, en sortir et distinguer quand le REPL convient et quand un fichier convient.
- Créer et exécuter `hola.py` et `revisor/revisor.py`, dans et hors de l'environnement, et noter quel `python` a été utilisé dans chaque cas.
- Lire un *traceback* de `NameError` de la dernière ligne vers le haut et dire quel mot mal écrit l'a causé.

## Le pourquoi avant le comment

Pour faire le premier pas avec le `revisor`, il faut une base solide : un Python qui fonctionne, un endroit où ranger les paquets dont le cours aura besoin et un dossier où vivra le projet. Si cette base est improvisée, les problèmes apparaissent plus tard et sous la forme la plus confuse possible : un paquet qui « s'est installé » mais qu'on ne trouve pas, une version de Python qui n'est pas celle que tu croyais, une commande qui marchait hier et plus aujourd'hui. Cette leçon existe pour que cela ne t'arrive pas.

Pense à aménager un atelier avant de construire un meuble. Ce n'est pas la partie excitante, mais cela décide si le reste sera propre. Dans l'atelier Python, il y a trois choses à préparer. La **première** est de savoir quel Python tu as et à qui il est : ton Mint en fournit déjà un, et il est à lui, pas à toi. La **deuxième** est de créer ton propre espace de travail, l'environnement virtuel, où tu peux installer et casser des choses sans conséquences. La **troisième** est de vérifier que tout fonctionne en exécutant le plus petit programme possible.

Il y a une raison de plus de bien le faire maintenant : **le faux pas que tu vas voir aujourd'hui est le même que tu auras dans un vrai travail**. Presque tous ceux qui installent Python sur un Linux moderne tombent, tôt ou tard, sur un Python du système qui refuse d'installer des paquets : sur ton Mint, parce qu'il n'a même pas `pip` ; sur d'autres systèmes, avec un message qui dit `externally-managed-environment`. Beaucoup de gens le lisent comme un obstacle, cherchent sur internet comment le contourner et finissent par utiliser une option qui brise la protection du système. Ce cours fait l'inverse : il **provoque le refus volontairement**, le lit ligne par ligne et montre que c'est une aide, pas un mur. Qui le comprend une fois le résout en dix secondes pour le reste de sa vie.

### Le minimum de terminal dont tu as besoin aujourd'hui

Le terminal est une fenêtre où tu écris des commandes au lieu de cliquer. Sur Mint, on l'ouvre avec le raccourci `Ctrl + Alt + T`, ou en cherchant « Terminal » dans le menu. Dans ce cours, les lignes qui commencent par `$` sont ce que **tu écris**, et les autres sont ce que l'ordinateur répond. Le `$` lui-même ne s'écrit pas : c'est le symbole que le terminal t'affiche pour indiquer qu'il attend une commande. Les commandes d'aujourd'hui sont peu nombreuses :

- `pwd` (*print working directory*) : affiche dans quel dossier tu te trouves.
- `ls` : liste ce qu'il y a dans le dossier actuel.
- `cd carpeta` : te déplace dans ce dossier. `cd ..` remonte d'un niveau et `cd` seul te ramène à ton dossier personnel.
- `mkdir carpeta` : crée un dossier.
- `which nombre` : affiche **quel fichier** serait exécuté si tu écrivais ce nom. C'est l'outil qui répond à « quel Python suis-je en train d'utiliser ? ».
- `~` : c'est un raccourci vers ton dossier personnel, celui qui contient tes documents. `~/curso-python` veut dire « le dossier `curso-python` dans ton dossier personnel ».

Si l'une d'elles est nouvelle pour toi, essaie-la maintenant dans ton terminal avant de continuer : écris `pwd`, appuie sur Entrée, et compare avec ce qui est dit. Cela ne casse rien.

## Les concepts

Ils sont quatre : le Python du système et l'erreur qui le protège ; l'environnement virtuel avec `pip` ; le REPL et les fichiers ; et le premier *traceback*. Chacun se termine par quelque chose que tu peux vérifier sur ton écran.

### 1.1 Le `python3` du système et l'erreur `externally-managed-environment`

#### 1.1.1 Quel Python tu as

Ouvre un terminal et écris :

```text
$ python3 --version
Python 3.12.3
```

La sortie que tu verras est de la forme `Python 3.12.x` : le dernier nombre (le correctif) dépend des mises à jour que ton Mint a reçues. Ce qui compte, c'est le `3.12`. C'est la version avec laquelle le cours travaille, et comme tu l'as vu dans la leçon précédente, tout le code s'exécute aussi en 3.14. Si ton terminal dit autre chose (une 3.10 ou une 3.11), le cours fonctionnera presque certainement de la même façon, mais la 3.10 est arrivée en fin de vie le 1er octobre 2026 ; note-le dans le [journal de bord](bitacora.md) et continue.

Demande maintenant **d'où vient** ce Python :

```text
$ which python3
/usr/bin/python3
```

`/usr/bin/` est le dossier où le système range ses propres programmes. Que ton `python3` s'y trouve signifie que **c'est celui de Mint** : c'est la distribution qui l'a installé, c'est le gestionnaire de paquets (`apt`) qui le met à jour et plusieurs outils du système en dépendent. C'est le « garde-manger commun » de la leçon précédente.

Si tu es sur un autre système (un macOS, ou un Linux avec un Python installé d'une autre manière), `which` affichera un autre chemin. Ce n'est pas grave, mais l'erreur de la prochaine section peut être différente ou ne pas apparaître, et ce cours est écrit pour Mint.

#### 1.1.2 Tenter d'installer quelque chose, et le système qui dit non

`pip` est l'outil de Python pour installer des **paquets** : des bibliothèques de code que d'autres personnes ont écrites et publiées dans un catalogue public appelé **PyPI**, pour que tu n'aies pas à les écrire toi-même. Le cours aura besoin plus tard d'un paquet appelé `httpx`, qui sert à interroger des services par le réseau. Nous allons essayer de l'installer, **volontairement, de la mauvaise façon** : avec le Python du système, en dehors de tout environnement. Sur un Linux Mint 22 fraîchement installé, voici ce qui se passe :

```text
$ python3 -m pip install httpx
/usr/bin/python3: No module named pip
```

La commande se lit : « exécute le module `pip` avec Python (`-m` veut dire *module*) et demande-lui d'installer `httpx` ». On écrit `python3 -m pip` et non simplement `pip` pour une raison qu'explique la [documentation de pip](https://pip.pypa.io/en/stable/getting-started/) : ainsi tu t'assures que le `pip` qui s'exécute est celui **de ce Python**, et non un autre présent sur ton système.

La réponse se lit comme n'importe quel rapport d'erreur, par la fin : `No module named pip`, « il n'y a aucun module appelé `pip` ». Avant les deux-points vient celui qui parle : `/usr/bin/python3`, le Python du système. Ce n'est pas une défaillance de ta part ni du cours. Dans la famille Debian et Ubuntu, dont vient Mint, `pip` est un paquet distinct du système (`python3-pip`), et un Mint fraîchement installé ne le fournit pas. Ce Python est administré par le gestionnaire de paquets du système, pas par toi. Le résultat pratique est celui qui compte : **en dehors d'un environnement, on n'installe rien**. Dans l'environnement virtuel, que tu vas créer dans un instant, `pip` est inclus.

#### 1.1.3 L'avertissement que tu verras si un jour tu installes le `pip` du système

Il existe une seconde protection, plus explicite, et il convient que tu la reconnaisses parce que c'est celle que tu rencontreras sur presque n'importe quel Linux moderne où `pip` existe bien dans le système (par exemple, si un jour tu installes le paquet `python3-pip` de Mint, ou sur une autre distribution). **Ne la provoque pas** : il n'est pas nécessaire d'installer quoi que ce soit pour la comprendre. Là-bas, la même commande ne dit pas `No module named pip`, mais un message qui commence ainsi :

```text
error: externally-managed-environment
```

Voici ce que dit la spécification qui en est la cause, [PEP 668](https://peps.python.org/pep-0668/) : les outils de Python « ne devraient pas installer ni supprimer de paquets dans le contexte global de l'interpréteur, par défaut », lorsque cet interpréteur est administré par un autre gestionnaire de paquets. Le mécanisme est simple : la distribution laisse un fichier appelé `EXTERNALLY-MANAGED` dans le dossier de la bibliothèque standard de son Python, et `pip` le cherche avant d'installer. S'il le trouve, il s'arrête. On peut demander ce dossier à Python :

```text
$ python3 -c "import sysconfig; print(sysconfig.get_path('stdlib'))"
```

Elle affiche le chemin de la bibliothèque standard de ton Python, un dossier dont le nom se termine par `python3.12` ; la spécification dit que c'est là que va le fichier marqueur.

Cette commande est une recette à recopier telle quelle ; tu n'as pas besoin de la comprendre en entier aujourd'hui, mais de savoir ce que fait chaque morceau. `-c` signifie « exécute ce texte comme un programme » : c'est une façon rapide de poser une question isolée à Python sans créer de fichier. Le texte entre guillemets comporte **deux instructions**, séparées par le point-virgule `;`, qui en Python permet d'écrire deux instructions sur la même ligne (dans les fichiers du cours on ne l'utilise pas : chaque instruction va sur sa ligne). La première, `import sysconfig`, apporte un **module**, un ensemble d'outils livré avec Python et qui n'est pas disponible tant que tu ne le demandes pas ; la [Leçon 3](03-bucles-funciones-modulos.md) explique `import` à fond. La seconde, `print(sysconfig.get_path('stdlib'))`, demande à ce module le chemin (*path*) de la bibliothèque standard (*stdlib*) et l'affiche avec `print`.

Le message complet, de plus, **te dit quoi faire**, et c'est pourquoi c'est une leçon et non un mur. La spécification permet à la distribution de mettre son propre texte d'aide dans le fichier marqueur, donc le corps change d'un système à l'autre ; en général, il suggère trois sorties : installer le paquet avec le gestionnaire du système s'il existe une version empaquetée, créer un environnement virtuel sinon, ou utiliser `pipx` si ce que tu veux installer est une application et non une bibliothèque. Pour ce que fait le cours, la sortie est la deuxième : **un environnement virtuel**. Dans la section « L'erreur que tu vas voir », tu as un exemple complet, lu par morceaux.

Il y a en outre une quatrième sortie, et `pip` te la dit lui-même dans la note par laquelle il clôt le message : une option appelée `--break-system-packages`, qui désactive la protection et permet d'installer quand même. La spécification admet qu'elle doit exister, et elle existe. **Ce cours ne l'enseigne pas et ne l'utilise pas.** C'est l'équivalent d'enlever la serrure parce que tu n'as pas trouvé la clé : cela marche jusqu'à ce qu'un paquet que tu as installé écrase une bibliothèque dont le système avait besoin, et alors des outils qui n'ont rien à voir avec ton projet tombent en panne. La clé existe et s'appelle environnement virtuel.

### 1.2 L'environnement virtuel : créer, activer, utiliser `pip`, désactiver

#### 1.2.1 Créer l'environnement

D'abord le dossier du cours. Tout ce que tu feras vivra dans `~/curso-python/` :

```text
$ mkdir ~/curso-python
$ cd ~/curso-python
$ python3 -m venv .venv
```

La troisième ligne est celle qui crée l'environnement. Elle se lit : « exécute le module `venv` avec `python3` et crée un environnement dans un dossier appelé `.venv` ». Le point au début du nom rend le dossier « caché » par convention : il n'apparaît pas dans un `ls` normal. C'est le nom habituel des environnements et certains outils le reconnaissent d'eux-mêmes. Quand tout se passe bien, **il n'affiche rien** ; dans le terminal, le silence est un succès.

L'environnement vit dans `~/curso-python/.venv`, **pas** à l'intérieur du dossier du projet `revisor/` que tu créeras plus bas. Il y a une raison : la documentation du module [`venv`](https://docs.python.org/3/library/venv.html) dit qu'un environnement est considéré comme « jetable » (il doit être facile de le supprimer et de le recréer de zéro) et qu'« on ne place pas de code de projet à l'intérieur de l'environnement ». Le garder à part du code est la façon la plus propre d'y satisfaire.

#### 1.2.2 Si ton Mint ne fournit pas la pièce des environnements

Sur un Mint 22 fraîchement installé, il est fort probable que la troisième ligne ne se passe **pas** en silence, mais avec ce message :

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

Lis-le par morceaux. La première phrase dit ce qui s'est passé : l'environnement « n'a pas été créé avec succès » parce qu'il manque `ensurepip`, la pièce qui place `pip` dans chaque nouvel environnement. La deuxième dit pourquoi : dans les systèmes de la famille Debian et Ubuntu, dont vient Mint, cette pièce arrive dans un paquet distinct. La troisième te donne la commande exacte, `apt install python3.12-venv`, et la suivante t'avertit de deux choses : que tu auras peut-être besoin de `sudo` et qu'après l'installation, il faut **recréer** l'environnement. La dernière ligne, `Failing command`, dit quelle commande interne a échoué ; tu n'as rien à en faire.

Remarque le mot « recréer », car il cache un piège. Bien que le message dise que l'environnement n'a pas été créé, **le dossier `.venv` est bel et bien resté sur le disque**, à moitié fait : il contient `pyvenv.cfg`, les dossiers `lib` et `include` et, dans `bin`, seulement les raccourcis vers Python (`python`, `python3` et `python3.12`). Il lui manque deux choses : `pip` et le script `activate`. C'est pourquoi on ne peut pas encore l'utiliser : `source .venv/bin/activate` répondrait `No such file or directory` (« aucun fichier de ce nom »), un message qui ne mentionne pas l'environnement et qui déconcerte si tu ne sais pas ce qui s'est passé.

La sortie tient en deux commandes :

```text
$ sudo apt update && sudo apt install python3.12-venv
$ python3 -m venv .venv
```

- **`sudo apt update && sudo apt install python3.12-venv`.** `apt` est le gestionnaire de paquets du système, celui qui installe et met à jour les programmes de Mint. `sudo` signifie « exécute cette commande avec des droits d'administrateur » : installer quelque chose pour tout le système en demande, donc le terminal te demandera **ton mot de passe** (pendant que tu le tapes, rien n'apparaît à l'écran, pas même des astérisques ; c'est normal). La ligne est en réalité deux commandes reliées par `&&`, qui veut dire « et, si la première a réussi, la seconde ». La première, `apt update`, n'installe rien : elle télécharge la liste à jour des paquets disponibles, pour que la seconde trouve la version en vigueur (avec une vieille liste, `apt` peut ne pas trouver le paquet ou choisir une version qui n'existe plus). La seconde installe `python3.12-venv` ; `apt` t'avertira qu'il installe **trois** paquets (`python3.12-venv` et deux dont il dépend : `python3-pip-whl`, qui apporte le `pip` qui ira dans chaque environnement, et `python3-setuptools-whl`, un autre outil d'empaquetage que le cours n'utilise pas) et te demandera si tu continues : réponds `s` (ou `y`, si ton Mint est en anglais ; sur un Mint en français, `o`) puis Entrée. Ici tu n'installes pas un paquet Python avec `pip`, mais un programme du système qui complète le Python du système, et c'est pourquoi cela relève bien d'`apt`. En dehors de cette ligne, le cours ne réutilise `sudo` que dans la [Leçon 11](11-el-programa-terminado.md), pour installer `pipx`, et c'est du même type.
- **`python3 -m venv .venv`**, de nouveau, sur le même dossier. Cette fois, cela doit se passer en silence. Il n'est pas nécessaire de supprimer le dossier à moitié fait : `venv` le réutilise et complète ce qui manquait, le script `activate` et `pip`.

Vérifie que cette fois l'environnement fournit son `pip`, en l'appelant par son chemin (sans rien activer encore) :

```text
$ .venv/bin/python -m pip --version
pip 24.0 from /home/tu_usuario/curso-python/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

`pip 24.0` est la version que Mint 22 met dans les nouveaux environnements ; ce qui compte, c'est qu'il réponde avec une version et un chemin **à l'intérieur de `.venv`**, et non avec `No module named pip`. Si ta première exécution de `python3 -m venv .venv` n'a rien affiché, rien dans cette section ne te concerne : ton environnement était déjà complet.

Voyons ce qui a été créé. Regarde à l'intérieur du dossier avec `ls .venv` :

```text
$ ls .venv
bin  include  lib  lib64  pyvenv.cfg
```

Il y a cinq entrées, mais quatre choses distinctes : `lib64` n'est pas un dossier de plus mais un raccourci vers `lib`, que `venv` crée sur les Linux 64 bits pour les programmes qui cherchent leurs bibliothèques sous ce nom. `bin` contient les programmes de l'environnement : son propre `python`, son propre `pip`, et les scripts d'activation. `lib` est l'endroit où seront rangés les paquets que tu installeras. `include` contient des fichiers de support que ce cours n'utilise pas. Et `pyvenv.cfg` est un petit fichier texte qui pointe vers le Python avec lequel l'environnement a été créé ; la [documentation du module](https://docs.python.org/3/library/venv.html) explique qu'il porte une clé `home` avec cet emplacement. Tu peux le lire avec `cat .venv/pyvenv.cfg`.

Une conséquence importante : le `python` de l'environnement est **un raccourci vers le Python avec lequel il a été créé**, pas une copie indépendante. C'est pourquoi, si un jour tu changes ou mets à jour le Python du système, l'environnement peut se retrouver cassé et il faudra le recréer. Et c'est pour cela même qu'**on ne déplace ni ne copie** un environnement vers un autre dossier ou un autre ordinateur : la documentation le dit en toutes lettres (« n'est pas considéré comme déplaçable ni copiable » ; on le recrée à destination). Les programmes installés dans un environnement conservent sur leur première ligne le chemin absolu de leur interpréteur ; si l'environnement est déplacé, ce chemin ne pointe plus vers rien. Recréer un environnement coûte dix secondes. Apprendre à le faire sans crainte est l'objectif.

#### 1.2.3 Activer l'environnement

Créer l'environnement ne l'utilise pas encore. Pour que ton terminal utilise **son** Python au lieu de celui du système, il faut l'**activer** :

```text
$ source .venv/bin/activate
(.venv) $
```

`source` est une commande du terminal qui exécute un script « à l'intérieur » du terminal actuel (au lieu d'en ouvrir un nouveau). Le script `activate` change trois choses, **uniquement dans ce terminal** : il ajoute un préfixe à l'invite du système, `(.venv)`, qui est ton signal visuel que tu es dedans ; il ajuste la liste des dossiers où le terminal cherche les programmes (la variable `PATH`), en plaçant `.venv/bin` en premier ; et il crée une variable, `VIRTUAL_ENV`, avec le chemin de l'environnement, pour que d'autres programmes sachent dans lequel tu es (`echo $VIRTUAL_ENV` l'affiche). Il rend en outre disponible la commande `deactivate`, qui défait tout. C'est le changement de `PATH` qui fait que `python` se met à signifier « le Python de l'environnement ». La [documentation](https://docs.python.org/fr/3/tutorial/venv.html) le résume : l'activation « modifie aussi l'environnement afin, lorsque vous tapez `python`, d'exécuter la version spécifique de Python installée dans l'environnement ».

Vérifie-le, c'est ce qui compte. Avec l'environnement actif, demande quel est le `python` :

```text
(.venv) $ which python
/home/tu_usuario/curso-python/.venv/bin/python
(.venv) $ python --version
Python 3.12.3
```

Remarque deux choses. La première : maintenant `python` (sans le 3) **existe**, et il pointe **à l'intérieur de ton environnement**. En dehors d'un environnement, sur ton Mint la commande `python` **n'existe pas** : seul `python3` existe (`which python` n'affiche rien). Si tu l'écris et que le terminal te dit qu'il ne le trouve pas ou te suggère `python3`, c'est normal. La règle, pour tout le cours : **hors de l'environnement, `python3` ; dans l'environnement activé, `python`**. La seconde : la version est la même qu'avant, parce que l'environnement a été créé avec ce Python. Si tu avais créé l'environnement avec `python3.14`, `python --version` dirait 3.14. **L'environnement décide de la version ; tu l'as choisie en le créant.**

Ce couple de commandes, `which python` et `python --version`, est la routine de sécurité de tout le cours. Avant de soupçonner ton code, vérifie quel Python s'exécute.

#### 1.2.4 Installer un paquet : cette fois, c'est bon

Avec l'environnement actif, la même commande qui avait été refusée fonctionne :

```text
(.venv) $ python -m pip install httpx
Collecting httpx
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
...
Successfully installed anyio-4.15.1 certifi-2026.7.22 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 typing_extensions-4.16.0
```

(Les lignes intermédiaires sont coupées. Les numéros de version que tu verras sont ceux en vigueur le jour où tu installeras, donc ils ne coïncideront presque certainement pas avec ceux-ci ; ce qui compte, c'est la ligne finale `Successfully installed`.)

Ce qui s'est passé : `pip` a téléchargé `httpx` et aussi six autres paquets dont `httpx` a besoin pour fonctionner. On les appelle des **dépendances** : des paquets dont un autre dépend. Tout est tombé **dans `.venv/lib`**, sans toucher au Python du système. Vérifie-le avec :

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

La liste montre ce qu'il y a **dans cet environnement**. Si tu ouvres maintenant un autre terminal (sans rien activer) et que tu demandes la liste avec `python3 -m pip list`, tu ne verras pas `httpx` (sur ton Mint, d'ailleurs, la réponse sera `No module named pip`) : ce que tu installes dans un environnement n'existe pas en dehors. Voilà à quoi ressemble l'isolation. Un avertissement peut aussi apparaître à la fin de l'installation, disant quelque chose comme `[notice] A new release of pip is available` : il est informatif. Mettre `pip` à jour n'est pas nécessaire pour le cours.

Une remarque sur `httpx` : aucun programme du cours ne l'utilise avant la [Leçon 9](09-http-y-asyncio.md). Nous l'installons aujourd'hui **uniquement pour démontrer `pip`**, avec un vrai paquet qui a des dépendances, et pour que tu voies la différence entre installer dans l'environnement et en dehors.

#### 1.2.5 Désactiver, et l'habitude à prendre

```text
(.venv) $ deactivate
$ which python
```

`deactivate` rétablit l'état antérieur du terminal : le préfixe `(.venv)` disparaît et `python` redevient ce qu'il était (sur Mint, comme nous l'avons vu, normalement rien). Fermer le terminal a le même effet, et c'est de là que vient l'**habitude à prendre** : chaque fois que tu ouvres un nouveau terminal pour travailler sur le cours, il faut réactiver l'environnement :

```text
$ cd ~/curso-python
$ source .venv/bin/activate
(.venv) $
```

Deux lignes, toujours les mêmes, et le préfixe `(.venv)` comme confirmation. Presque tous les « ça ne marche pas » de cette étape se résolvent en regardant si le préfixe est à l'écran.

Il y a une autre façon d'utiliser un environnement sans l'activer, et il convient de savoir qu'elle existe : appeler le Python de l'environnement par son chemin complet, `~/curso-python/.venv/bin/python hola.py`. La [documentation](https://docs.python.org/3/library/venv.html) le confirme : il n'est pas nécessaire d'activer l'environnement, il suffit d'indiquer le chemin de son interpréteur. Activer est un confort (on écrit `python` au lieu du long chemin), pas une obligation.

### 1.3 Le REPL et l'exécution d'un fichier

Il y a deux manières de parler à Python, et elles servent à des choses différentes.

#### 1.3.1 Le REPL : une conversation

Avec l'environnement actif, écris seulement `python` et Entrée. Python n'exécute pas un fichier ; il ouvre une **conversation** : il t'affiche un symbole `>>>` et attend une instruction. On appelle cela le REPL (de *read-eval-print loop* : il lit ce que tu écris, l'évalue, affiche le résultat et se remet à attendre). Essaie ainsi (tu écris ce qui suit `>>>` ; la ligne de bienvenue des premières lignes change selon ta version) :

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

Parcours la conversation. `142 + 1` renvoie `143`, sans besoin de `print` : le REPL affiche à ta place la valeur de ce que tu écris. `"reportes"` revient avec des guillemets simples, parce que c'est ainsi que Python montre un texte quand il le représente. `tiempo_ms = 142` est une affectation et ne renvoie rien ; ensuite, écrire `tiempo_ms` renvoie `142` : **le REPL se souvient** de ce que tu lui as dit tant que tu ne le fermes pas. La quatrième est l'erreur que tu connais déjà de la Leçon 0, `TypeError`, et observe-la : le REPL **ne se ferme pas** à cause de l'erreur. Il montre le rapport et se remet à attendre. Cela le rend idéal pour se tromper et apprendre. Pour en sortir, on écrit `exit()` (ou son jumeau `quit()`) ou on appuie sur `Ctrl + D` ; la [documentation](https://docs.python.org/3/tutorial/interpreter.html) donne `Ctrl + D` comme la forme principale et `quit()` comme alternative.

Deux détails de version, pour que tu ne sois pas déconcerté si ton écran a un autre aspect. Le REPL de **la 3.13 et suivantes** est renouvelé : il a de la couleur et l'édition sur plusieurs lignes, et le nom qu'il affiche dans un rapport d'erreur est `<python-input-0>` au lieu de `<stdin>`, ainsi que la ligne même qui a échoué. Et le REPL de la 3.12, celui de ton Mint, est le simple REPL ci-dessus. Rien de ce qu'on fait dans le cours ne dépend de cette différence.

À quoi sert le REPL ? À **essayer des idées rapides** : « que fait cette opération ? », « comment s'appelait cette fonction ? ». À quoi **ne** sert-il pas ? À écrire des programmes. Ce que tu dis dans le REPL se perd quand tu en sors ; il ne reste aucun fichier. Un programme est un texte qu'on enregistre, qu'on corrige et qu'on ré-exécute. Pour cela, il y a les fichiers.

#### 1.3.2 Un fichier : ton premier script

Un **script** est un fichier texte contenant des instructions Python qui s'exécute du début à la fin. Pour le créer, tu as besoin d'un éditeur de texte. Mint en fournit un appelé **Xed** (il apparaît dans le menu comme « Éditeur de texte »). Il convient de le configurer une fois : dans ses préférences, active **insérer des espaces au lieu des tabulations** et mets la largeur de tabulation à 4. Python accorde beaucoup d'importance aux espaces en début de ligne (la [Leçon 2](02-valores-texto-decisiones.md) t'explique pourquoi), et mélanger tabulations et espaces est une source classique d'erreurs que nous préférons éviter dès le premier jour. Si tu préfères le terminal, `nano hola.py` ouvre un éditeur simple : écris, enregistre avec `Ctrl + O` et Entrée, quitte avec `Ctrl + X`.

Crée le fichier `~/curso-python/hola.py` avec ce contenu :

```python
# fig01_01.py
print("Hola, Python")
```

```text
$ cd ~/curso-python
$ python3 hola.py
Hola, Python
```

Le nom `fig01_01.py` de la première ligne est l'étiquette de la figure dans le cours (dans le dépôt du cours, le fichier s'appelle ainsi) ; **toi, tu l'enregistres sous le nom `hola.py`**, et c'est pourquoi la commande est `python3 hola.py`. La première ligne est un commentaire (elle commence par `#`, Python l'ignore) et tu peux l'omettre. La seconde est le programme. `print` est une **fonction** que Python fournit déjà : elle affiche à l'écran ce qui se trouve entre les parenthèses. Ce qui est entre guillemets est un **texte**, comme tu l'as vu dans la leçon précédente. C'est toute l'explication dont tu as besoin aujourd'hui ; la Leçon 2 va au fond des choses.

Exécute-le deux fois : une **sans** l'environnement actif et une **avec**. Hors de l'environnement, la commande est `python3 hola.py`. Dedans, c'est `python hola.py`, parce que dans l'environnement `python` existe et pointe vers son Python. Dans les deux cas, la sortie est `Hola, Python` ; ce qui change, sans que tu le remarques, c'est **quel Python l'a exécuté**. Cette différence est invisible tant que tout fonctionne et décisive quand quelque chose échoue, et c'est pourquoi il y a un exercice à la fin pour la noter.

Voici maintenant le deuxième fichier d'aujourd'hui, le premier du projet. Crée le dossier du `revisor` et le fichier où il grandira :

```text
$ mkdir ~/curso-python/revisor
```

```python
# fig01_02.py
print("revisor: todavía no revisa nada")
```

Il s'enregistre sous `~/curso-python/revisor/revisor.py` (l'étiquette `fig01_02.py` n'est, encore une fois, que le nom de la figure). Pour l'exécuter, entre d'abord dans son dossier, car `python3 revisor.py` cherche le fichier dans le dossier où tu te trouves :

```text
$ cd ~/curso-python/revisor
$ python3 revisor.py
revisor: todavía no revisa nada
```

C'est un programme d'une ligne, exprès : l'important est que **le fichier existe, s'exécute et soit le point de départ**. À partir de la Leçon 2, il grandit jusqu'à devenir le programme complet. Le mot « todavía » (« pas encore ») est une promesse.

### 1.4 Le premier *traceback*

Dans la Leçon 0, tu as vu un rapport d'erreur et tu as lu sa dernière ligne. Aujourd'hui, tu le lis en entier, avec une erreur que tu vas commettre tôt ou tard, et très souvent : mal écrire le nom de quelque chose. Ce programme contient une coquille délibérée. Cette fois, enregistre-le sous le nom de la figure, `~/curso-python/fig01_03.py`, pour que le rapport de ton écran coïncide avec celui d'en dessous :

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

(Sur ton écran, le chemin du fichier sera le chemin complet ; ici il est raccourci au nom.)

**La règle pour lire un rapport d'erreur de Python : de la dernière ligne vers le haut.** On répond à trois questions, dans cet ordre.

**Quelle sorte d'erreur est-ce ?** Regarde le début de la dernière ligne : `NameError`. Un `NameError` se produit quand tu utilises un nom que Python ne connaît pas. La Leçon 0 a expliqué qu'un nom est une étiquette qui pointe vers une valeur ; Python a quelques noms d'origine (comme `print`) et d'autres que tu crées par une affectation. `pirnt` n'est ni l'un ni l'autre.

**Que dit-elle exactement ?** Le reste de la dernière ligne : `name 'pirnt' is not defined`, « le nom `pirnt` n'est pas défini ». Et l'aide : `Did you mean: 'print'?`, « voulais-tu dire `print` ? ». Python a comparé le nom inconnu à ceux qu'il connaît, en a trouvé un très ressemblant et te le suggère. Cette suggestion, qui pour ce type d'erreur est identique dans les versions 3.12 et 3.14, résout la plus grande partie des faux pas d'un débutant.

**Où cela s'est-il passé ?** Les lignes du dessus. `File "fig01_03.py", line 2, in <module>` donne le fichier et la ligne (la 2, parce que la 1 est le commentaire). En dessous, Python répète le texte de cette ligne de ton code, et les accents circonflexes `^^^^^` désignent le mot exact : cinq caractères, justement `pirnt`.

Fais ce que dit la suggestion : remplace `pirnt` par `print`, enregistre et ré-exécute. Avec cette petite cérémonie (lire, comprendre, corriger, recommencer), tu vas travailler pendant le reste du cours. Une erreur ne veut pas dire que tu as mal fait ; elle veut dire que Python te répond avec précision.

## L'erreur que tu vas voir

Aujourd'hui, il y a trois messages qu'il faut savoir lire : tu en as déjà vu deux et le troisième est un avertissement pour plus tard.

**`NameError`** est celui de la section précédente. Variantes que tu verras : une majuscule là où il n'en faut pas (`Print("hola")` donne `NameError: name 'Print' is not defined. Did you mean: 'print'?`, car Python distingue majuscules et minuscules), une lettre en trop, un nom que tu as oublié de définir. Dans tous les cas, cela se lit pareil.

**`No module named pip`** est la réponse de ton Mint en 1.1.2, et son parent, le message d'`ensurepip` de 1.2.2, est celle d'un environnement auquel manque la même pièce. Les deux disent en toutes lettres ce qui manque, et les deux se résolvent sans toucher au Python du système : le premier, en travaillant dans l'environnement ; le second, en installant `python3.12-venv` et en recréant l'environnement sur le dossier à moitié fait.

**`externally-managed-environment`** est l'avertissement de 1.1.3 : tu ne le verras pas sur un Mint fraîchement installé, mais bien le jour où tu installeras le `pip` du système, ou sur une autre distribution. La première ligne, `error: externally-managed-environment`, est mise par `pip` : la PEP 668 ne fixe pas ce texte, elle exige seulement que l'installateur refuse avec une erreur et montre le message que la distribution a écrit dans son fichier marqueur (ou, s'il n'y en a pas, un message propre suggérant un environnement virtuel). Le corps, par conséquent, est écrit par chaque système. Comme exemple réel, voici le message complet que donne le Python de Homebrew sur un macOS (le gestionnaire de paquets de là-bas s'appelle `brew` ; sur Mint ce serait `apt`) :

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

Lis-le comme tu lis un *traceback*, sans crainte, par morceaux. La première ligne est la **classe** : `externally-managed-environment`, « environnement géré en externe ». La deuxième, `This environment is externally managed`, donne la raison : ce Python appartient à un autre gestionnaire. La troisième ouvre la liste des sorties. **Premièrement**, installer le paquet avec le gestionnaire du système (ici `brew` ; sur Mint ce serait `apt`), pourvu que le paquet y existe. **Deuxièmement**, si le paquet n'est pas dans le gestionnaire, créer un environnement virtuel et utiliser `python3 -m pip` à l'intérieur : les trois lignes qu'il montre sont exactement `venv`, `source ... activate` et `pip install`, que tu viens d'utiliser. **Troisièmement**, si ce que tu veux est une *application* (et non une bibliothèque à utiliser dans ton code), `pipx`, qui crée un environnement isolé pour chaque application. Le `revisor` finira par s'installer ainsi, dans la [Leçon 11](11-el-programa-terminado.md).

Sous les trois sorties viennent encore deux paragraphes écrits par Homebrew : comment « rétablir le comportement précédent » avec `--break-system-packages` et l'avertissement, en majuscules, que le faire peut casser l'installation. Et les deux dernières lignes ne sont plus de la distribution mais de `pip` : une `note:` qui mentionne de nouveau `--break-system-packages` « au risque de casser ton installation de Python ou ton système d'exploitation », et une `hint:` qui renvoie à la PEP 668. Que l'option apparaisse deux fois ne la rend pas recommandable : elle apparaît pour que tu saches qu'elle existe et ce qu'elle coûte, ce que dit la section suivante.

Le corps est un guide de résolution écrit par celui qui administre ce Python, et il change d'un système à l'autre ; ce qui ne change pas, parce que c'est `pip` qui le met et non la distribution, c'est la première ligne et la note finale. **Lis-le chaque fois qu'il apparaît** : il t'évite de chercher sur internet, et la plupart des réponses d'internet pour cette erreur recommandent le raccourci qui brise la protection.

## Ce qui se fait de travers

- **Utiliser `sudo pip install`.** Cela installe dans le Python du système avec des droits d'administrateur. C'est la façon la plus rapide d'écraser une bibliothèque dont Mint a besoin et de le découvrir des semaines plus tard. Chaque paquet va dans un environnement virtuel.
- **Utiliser `--break-system-packages` pour que « ça marche enfin ».** Cela désactive exactement la protection qui t'aide. Le cours ne l'enseigne pas et ne l'utilise pas. Si tu la vois dans une réponse d'internet, ignore-la.
- **Installer sans voir le préfixe `(.venv)`.** Si tu as ouvert un nouveau terminal et oublié d'activer, l'installation est refusée (parce que tu es hors de l'environnement) ou, sur un système sans protection, elle se fait au mauvais endroit. La routine est de regarder le préfixe avant d'installer et de vérifier avec `which python` au moindre doute.
- **Déplacer ou copier le dossier `.venv`.** Un environnement conserve des chemins absolus et ne survit pas à un changement de dossier. On le supprime et on le recrée avec `python3 -m venv .venv` ; on réinstalle les paquets. Il est jetable par conception.
- **Mettre le code du projet à l'intérieur de l'environnement.** L'environnement contient Python et les paquets ; ton code vit à côté, dans `revisor/`. Ainsi, supprimer l'environnement ne te coûte pas une seule ligne de ce qui est à toi.
- **Mélanger tabulations et espaces dans l'éditeur.** Python utilise les espaces du début de ligne pour structurer le programme, et mélanger les deux types donne des erreurs difficiles à voir. Configure ton éditeur à 4 espaces, aujourd'hui, avant d'écrire du vrai code.
- **Écrire la commande `python` hors de l'environnement et en conclure que « Python n'est pas installé ».** Ce qui manque, c'est l'alias `python` : hors de l'environnement, on écrit `python3`. Que `python` n'existe pas sur un Mint fraîchement installé est normal.
- **Rester des heures sur une erreur sans la lire.** Un rapport de Python dit presque toujours quoi et où. L'habitude de commencer par la dernière ligne résout la plupart des cas.

## Exercices

### Exercice 1 — Ton environnement, mesuré

Exécute dans un terminal sans environnement actif : `python3 --version` et `which python3`. Puis active l'environnement et exécute `python --version`, `which python` et `python -m pip --version`. Écris dans ton [journal de bord](bitacora.md) les cinq sorties et une phrase qui répond : qu'est-ce qui a changé entre `which python3` dehors et `which python` dedans, et pourquoi ?

### Exercice 2 — Provoque le refus et lis-le

Désactive l'environnement (`deactivate`) et exécute `python3 -m pip install httpx`. Note dans le journal de bord la réponse exacte et explique avec tes mots qui parle (ce qui se trouve avant les deux-points) et ce qu'il dit. Lis ensuite l'exemple d'`externally-managed-environment` de la section « L'erreur que tu vas voir » et écris ce que dit chacune de ses trois premières parties (la classe, la raison, la liste des sorties). Enfin, active l'environnement et refais l'installation. Décris ce qui a changé et ce que tu as vérifié avec `python -m pip list`.

### Exercice 3 — Le `revisor` dans et hors de l'environnement

Crée `~/curso-python/revisor/revisor.py` avec la ligne de la figure 2 et entre dans son dossier (`cd ~/curso-python/revisor`). Exécute-le **sans** l'environnement (avec `python3 revisor.py`) et **avec** (avec `python revisor.py`). Avant chaque exécution, lance `which python3` ou `which python` selon le cas, et note dans le journal de bord quel Python a été utilisé à chaque fois. Le résultat est-il sorti différent ?

### Exercice 4 — Provoque une nouvelle erreur et lis-la

Sans toucher à l'environnement, crée un fichier avec la ligne `Print("hola")` (avec un P majuscule). Avant de l'exécuter, prédis la dernière ligne du rapport. Exécute-le et compare. Provoque ensuite une seconde erreur différente : crée un fichier de deux lignes, `print("primera")` et `print("hola)` (la seconde sans le guillemet fermant), et regarde quelle classe d'erreur apparaît. Est-ce que `primera` arrive à s'afficher ?

## Solutions

### Solution 1

Une sortie typique est `Python 3.12.x`, `/usr/bin/python3`, `Python 3.12.x`, `/home/tu_usuario/curso-python/.venv/bin/python` et un `pip` avec le chemin `.venv/lib/python3.12/site-packages/pip`. Ce qui a changé entre dehors et dedans, c'est **le chemin** : dehors, c'est `/usr/bin/python3`, le Python du système ; dedans, c'est celui qui se trouve dans `.venv/bin/`, celui de l'environnement. Cela a changé parce qu'`activate` a mis `.venv/bin` au début de la liste des endroits où le terminal cherche des programmes ; c'est pourquoi `python` (qui n'existait même pas dehors) se met à signifier « celui de l'environnement ». La version est la même parce que l'environnement a été créé avec le `python3` du système.

### Solution 2

Hors de l'environnement, ton Mint répond `/usr/bin/python3: No module named pip` : c'est le Python du système qui parle et qui dit qu'il n'a pas `pip`, donc là on n'installe rien. Dans l'exemple d'`externally-managed-environment`, la classe est `externally-managed-environment` : le type de problème. La raison est que ce Python est administré par un autre gestionnaire de paquets, et que `pip` respecte la marque `EXTERNALLY-MANAGED` laissée par celui qui l'a installé. La liste des sorties est : installer avec le gestionnaire du système si le paquet y existe, créer un environnement virtuel pour les bibliothèques, ou `pipx` pour les applications. En activant l'environnement et en recommençant, l'installation se termine : dans l'environnement il y a `pip`, et sa protection ne s'applique pas parce qu'il ne touche pas là au Python du système. `python -m pip list` montre `httpx` et ses dépendances dans la liste de l'environnement, et non dans celle du système.

### Solution 3

Il doit sortir `revisor: todavía no revisa nada` dans les deux cas. Ce qui change, c'est le Python : sans environnement, `which python3` donne `/usr/bin/python3` ; avec environnement, `which python` donne le chemin dans `.venv/bin/`. Le résultat ne change pas parce que le programme n'utilise que `print`, qui ne dépend d'aucun paquet ; la différence deviendra visible quand un programme importera quelque chose d'installé dans l'environnement (à partir de la Leçon 9) : ce programme ne fonctionnerait qu'avec l'environnement actif. Savoir quel Python tu as utilisé est ce qui te permet de comprendre pourquoi.

### Solution 4

Avec `Print("hola")`, la dernière ligne est `NameError: name 'Print' is not defined. Did you mean: 'print'?` : Python distingue majuscules et minuscules. Avec `print("hola)`, l'erreur change de classe : il apparaît un `SyntaxError: unterminated string literal (detected at line 2)`, qui veut dire « texte non terminé », parce qu'il manque le guillemet qui le ferme. `primera` n'est **pas** affiché : l'erreur se produit avant d'exécuter quoi que ce soit. C'est une erreur de forme, et Python la détecte à l'étape où il lit et traduit le fichier (la première des quatre étapes de la Leçon 0). Ce n'est pas un `NameError`, qui ne se découvre qu'en arrivant à cette ligne quand le programme est déjà en marche. La Leçon 2 étudie cette erreur à fond.

## Comment savoir que j'ai réussi

- [ ] `python3 --version` affiche une version qui commence par `Python 3.` et tu l'as notée dans le journal de bord.
- [ ] `python3 -m pip install httpx`, avec l'environnement **désactivé**, se termine par `No module named pip`, tu sais expliquer sans regarder la leçon ce que cela signifie et quelle est la bonne sortie, et tu reconnaîtrais l'avertissement `externally-managed-environment` si un jour tu le voyais.
- [ ] Le dossier `~/curso-python/.venv` existe ; avec l'environnement actif, l'invite du terminal commence par `(.venv)`, et `which python` affiche un chemin qui se termine par `.venv/bin/python`.
- [ ] Avec l'environnement actif, `python -m pip list` affiche `httpx` ; avec l'environnement désactivé, `python3 -m pip list` répond `No module named pip` : hors de l'environnement il n'y a pas de `pip`, et donc pas non plus de `httpx`.
- [ ] `python3 hola.py` hors de l'environnement et `python hola.py` dedans affichent `Hola, Python`.
- [ ] `~/curso-python/revisor/revisor.py` existe et, à l'exécution, affiche `revisor: todavía no revisa nada`.
- [ ] Tu sais lire, sans demander d'aide, le rapport de `NameError` de la figure 3 : tu dis quel mot a échoué, à quelle ligne et quelle suggestion Python a donnée.
- [ ] Tu peux dire, sans regarder, pourquoi l'environnement ne se déplace ni ne se copie, et pourquoi on n'installe jamais rien avec `sudo pip`.

## Résumé

Réponds sans regarder la leçon :

1. Quel est le Python fourni avec ton Mint, à qui est-il, et comment vérifies-tu d'où il s'exécute ?
2. Que dit `externally-managed-environment`, qui le met, et quelles sont les trois sorties qu'il suggère ? Laquelle utilise le cours ?
3. Quelles trois choses `source .venv/bin/activate` change-t-il dans ton terminal, et comment sais-tu que tu es dedans ?
4. Pourquoi l'environnement vit-il en dehors du dossier `revisor/` et pourquoi ne se déplace-t-il ni ne se copie-t-il ?
5. Quelle différence y a-t-il entre le REPL et un fichier ? Quand utilises-tu chacun ?
6. Dans quel ordre lit-on un rapport d'erreur de Python, et à quelles trois questions répond-il ?
7. Quel Python utilise `python` dans l'environnement et quel Python utilise `python3` en dehors ?

## Pour aller plus loin

- [Tutoriel Python : Environnements virtuels et paquets](https://docs.python.org/fr/3/tutorial/venv.html) — le guide officiel de `venv` et `pip`, avec les commandes de cette leçon, dans sa traduction française officielle (une partie reste en anglais). Consulté le 7 octobre 2026.
- [PEP 668, « Marking Python base environments as externally managed »](https://peps.python.org/pep-0668/) — la spécification qui explique le fichier `EXTERNALLY-MANAGED` et le refus de `pip`. Consulté le 7 octobre 2026.
- [Documentation du module `venv`](https://docs.python.org/3/library/venv.html) — ce qu'est `pyvenv.cfg`, pourquoi un environnement est jetable et pourquoi il ne se déplace pas. Consulté le 7 octobre 2026.
- [pip : premiers pas](https://pip.pypa.io/en/stable/getting-started/) — vérifier que `pip` est installé, installer un paquet et pourquoi on l'invoque sous la forme `python -m pip`. Consulté le 7 octobre 2026.
