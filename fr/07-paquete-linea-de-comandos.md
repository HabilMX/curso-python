# Leçon 7 — Un paquet en ligne de commande

**Durée :** 90 min

**Ce que tu construis :** le `revisor` comme un vrai paquet : un dossier structuré, un fichier `pyproject.toml` qui le décrit, une commande avec des options (`--config`, `--formato`, `--version`) et un code de sortie que d'autres programmes peuvent lire

**Ce que tu apprends :** la structure d'un paquet avec la disposition `src/` (`__init__.py`, `__main__.py`, imports absolus) ; `python -m revisor` ; `pyproject.toml` (`[build-system]`, `[project]`, `[project.scripts]`) ; `argparse` ; les codes de sortie ; la sortie standard contre la sortie d'erreur ; et l'installation éditable avec `pip install -e .`

**D'où tu viens.** Tu arrives avec le projet de la [Leçon 6](06-errores-archivos-datos.md) : un `revisor` qui ne porte plus les services écrits dans le code mais les lit dans `servicios.toml`, les valide, et se plaint en espagnol quand le fichier ne convient pas. Ce sont six fichiers dans un seul dossier (`revisor.py`, `modelo.py`, `revision.py`, `formato.py`, `configuracion.py` et le script d'appui `ver_json.py`) plus le `servicios.toml`. Ça fonctionne, avec trois limites qui se remarquent aujourd'hui. Première : **ça ne marche que si tu te trouves dans ce dossier** et que tu écris `python revisor.py` ; les modules se trouvent les uns les autres parce qu'ils sont collés, et le nom du fichier de configuration est écrit dans une constante du programme. Deuxième : **pour voir le rapport en JSON, il faut exécuter un autre script**, parce que le programme n'a aucun moyen de savoir ce que tu veux. Troisième : **le programme ne prévient personne s'il a trouvé des problèmes** : il se termine aussi bien quand tout est en marche que quand la moitié est en panne, et un script, un planificateur de tâches ou un système d'intégration continue ne peuvent pas savoir la différence. Tu travailles dans ton dossier `~/curso-python/revisor/`, avec l'environnement virtuel de la [Leçon 1](01-instalacion.md) activé.

**Ce que cette leçon ne fait pas.** Elle n'interroge aucun réseau (les données restent celles, simulées, de la leçon 5 ; le réseau arrive dans la [Leçon 9](09-http-y-asyncio.md)) et elle n'écrit pas de tests (c'est la [Leçon 8](08-pruebas-tipos-calidad.md)). Ce qui se résout aujourd'hui, c'est **comment un ensemble de fichiers devient un programme qui s'installe, s'exécute avec une commande et communique avec le reste du système**.

**À propos des exécutions.** Toutes les sorties ont été obtenues avec Python 3.14.8 et répétées avec Python 3.12.12, celui qui est fourni avec Linux Mint. Elles sont identiques à une seule exception près, signalée là où elle se produit : le texte d'une erreur d'`argparse`. Les chemins que tu verras dans les messages commencent par `/home/tu_usuario/curso-python/` ; le tien commencera par ton propre dossier. Le projet complet se trouve dans [`programas/07-paquete-linea-de-comandos/fig07_01/`](https://github.com/HabilMX/curso-python/tree/main/programas/07-paquete-linea-de-comandos/fig07_01), dans le dépôt du cours ; les deux figures isolées (`fig07_02.py` et `fig07_03.py`) s'exécutent depuis le dossier de la leçon.

## À la fin, tu seras capable de

- Expliquer la différence entre un module et un paquet, et pourquoi le code vit dans `src/revisor/` et non à côté du `pyproject.toml`.
- Exécuter un paquet avec `python -m revisor` et expliquer ce que fait `__main__.py`.
- Lire et écrire un `pyproject.toml` avec ses trois tables : `[build-system]`, `[project]` et `[project.scripts]`.
- Définir des options de ligne de commande avec `argparse` : une avec une valeur par défaut, une avec des choix fermés et une `--version`.
- Faire terminer un programme avec un code de sortie qui dit ce qui s'est passé (0, 1 ou 2), et le lire dans le terminal avec `echo $?`.
- Envoyer les messages d'erreur vers la sortie d'erreur et le rapport vers la sortie standard, et vérifier la différence en redirigeant l'une des deux.
- Installer le paquet en mode éditable avec `pip install -e .` et expliquer pourquoi un changement dans le code se remarque sans réinstaller, alors qu'un changement dans `pyproject.toml` ne se remarque pas.

## Le pourquoi avant le comment

Pense à la façon dont tu utiliserais le `revisor` dans la vie réelle. Quelqu'un de l'exploitation l'exécute chaque matin depuis un planificateur de tâches, pour savoir si un service est tombé pendant la nuit. Ce planificateur de tâches ne regarde pas le tableau qui s'affiche : c'est un programme, et il ne sait pas lire un tableau. La seule chose qu'il peut demander à un autre programme à sa fin, c'est une chose : **« es-tu sorti bien ou mal ? »**. Sous Linux, cette réponse est un nombre, le *code de sortie*, et la convention veut que 0 signifie « tout va bien » et que tout autre nombre signifie « quelque chose s'est passé ». Si le `revisor` ne sait pas répondre à cette question, l'automatisation est aveugle. Et si en plus la personne veut le rapport en JSON pour le passer à un autre système, elle doit pouvoir le demander avec une option, pas en modifiant un fichier.

Un programme qui s'exécute ainsi, avec des options, avec un code de sortie et depuis n'importe quel dossier, est un **programme en ligne de commande**. Pour l'être, il faut de la structure : on ne peut pas le faire avec six fichiers isolés. Python a une façon standard de le monter, qui consiste en trois pièces : un **paquet** (un dossier que Python reconnaît comme une unité importable), un fichier **`pyproject.toml`** qui décrit le projet pour les outils, et une **commande d'installation** qui rend le tout disponible dans ton environnement. Ce sont les trois sections de la leçon, plus celle qui la clôt : comment un programme communique avec qui l'a appelé, avec des codes de sortie et avec deux canaux de texte distincts.

La leçon est mécanique, et c'est un avertissement honnête : il y a beaucoup de noms de fichiers et beaucoup de règles qui s'apprennent en les faisant, pas en les lisant. La meilleure façon de la suivre est d'avoir le terminal ouvert dans `~/curso-python/revisor/` et d'exécuter chaque étape. À la fin, en exécutant `python -m revisor --formato json`, tu verras à l'écran le rapport en JSON, et en demandant au terminal comment le programme s'est terminé avec `echo $?`, tu verras un `1`, parce que parmi les services il y en a un lent et un en panne. Il y a beaucoup de choses cachées dans cette phrase (une option, un format, un nombre qui sort à la fin), et la leçon les démêle une à une.

## Les concepts

### 7.1 Un paquet avec la disposition `src/`

#### 7.1.1 Module, paquet et comment ils se trouvent

Tu sais déjà ce qu'est un **module** : un fichier `.py` dont un autre fichier peut importer le contenu (leçon 3). Jusqu'ici, ton `revisor` en a cinq, et ils s'importent avec des instructions comme `from modelo import Servicio`. Cela fonctionne pour une raison très concrète qui n'avait jamais été nommée : quand tu exécutes `python revisor.py`, Python cherche les modules que tu importes **dans le dossier où se trouve ce fichier**, et aussi dans les dossiers de la bibliothèque standard et dans ceux de l'environnement virtuel où `pip` installe des choses (un dossier appelé `site-packages`). Cette liste d'endroits est consultée dans l'ordre, et c'est elle qui décide si un `import` trouve ce qu'il cherche ou échoue avec `ModuleNotFoundError`. Tant que tous tes fichiers sont ensemble, tout se trouve. Dès que quelque chose est déplacé ou exécuté depuis un autre endroit, ça commence à échouer.

Un **paquet** est un dossier de modules que Python traite comme une unité avec un nom. S'il y a un dossier `revisor/` avec un fichier `__init__.py` dedans et d'autres modules, on peut écrire de n'importe où `from revisor.modelo import Servicio`, qui se lit « du paquet `revisor`, le module `modelo`, importe `Servicio` ». Le point sépare les niveaux. Ce type d'import, qui part toujours du nom du paquet, s'appelle **import absolu**, et c'est le seul que ce cours utilise : c'est le plus clair à lire, parce que quiconque voit la ligne sait d'où vient le nom sans avoir à deviner dans quel dossier se trouve le fichier. La [section du tutoriel sur les paquets](https://docs.python.org/3/tutorial/modules.html#packages) explique le mécanisme plus en détail.

#### 7.1.2 Pourquoi `src/`

Ce qui reste à décider, c'est **où** mettre le dossier du paquet. La façon la plus évidente est à côté du `pyproject.toml`, à la racine du projet. Mais il existe une meilleure façon, qui est celle qu'utilise le guide officiel d'empaquetage de Python : le mettre dans un sous-dossier appelé `src/`. Voici la disposition que tu auras à la fin de la leçon :

```text
revisor/                      ← la carpeta del proyecto (~/curso-python/revisor/)
  pyproject.toml              ← describe el proyecto
  servicios.toml              ← los datos, como en la lección 5
  src/
    revisor/                  ← el paquete
      __init__.py
      __main__.py
      cli.py
      modelo.py
      revision.py
      formato.py
      configuracion.py
```

Le nom `revisor` apparaît deux fois, et ce n'est pas une négligence : celui de l'extérieur est le dossier du **projet** (ce que tu télécharges, ce qui contient les fichiers de configuration, les tests qui viendront dans la leçon 8), et celui de l'intérieur est le **paquet** (ce que Python importe). L'avantage de `src/` est qu'il **t'oblige à installer le paquet avant de l'utiliser**. Si le paquet était à la racine, `python -m revisor` depuis ce dossier le trouverait sans l'installer, parce que le dossier courant est toujours dans la liste des endroits où Python cherche. Et cela cache des erreurs : tu pourrais avoir un paquet qui fonctionne dans ton dossier mais auquel, une fois installé, il manque des fichiers, et tu ne le saurais pas avant qu'une autre personne l'utilise. Avec `src/`, le dossier du paquet n'est pas là où Python cherche par défaut, donc ce que tu exécutes est toujours ce que tu as installé. Le [guide d'empaquetage](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) discute les deux formes et leurs compromis ; ce cours adopte celle de `src/` sans réserve.

#### 7.1.3 `__init__.py`, `__main__.py` et `python -m`

Le paquet comporte deux fichiers qui ne font pas partie de ton programme mais du mécanisme. Le premier est `__init__.py`. Sa seule présence dit à Python « ce dossier est un paquet ». Il peut être vide ; ici il contient une phrase entre triples guillemets qui décrit le paquet, ce qu'on appelle une chaîne de documentation :

```python
# fig07_01/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

Le second est `__main__.py`, ce qui s'exécute quand quelqu'un écrit `python -m revisor`. L'option `-m` (de *module*) dit à Python « n'exécute pas un fichier ; exécute ce paquet comme un programme ». Pour un paquet, cela signifie exécuter son `__main__.py`. Tout le fichier, c'est ceci :

```python
# fig07_01/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

La première ligne importe la fonction `main` du module `cli` (que tu verras en 7.3). La seconde fait quelque chose qui ressemble à une formalité mais qui est le centre de la leçon : `raise SystemExit(main())`. Tu sais déjà ce qu'est `raise` (leçon 6) : il lance une exception. `SystemExit` est une exception spéciale que Python fournit déjà, et que **personne n'attrape exprès** : quand elle remonte tout en haut, au lieu d'afficher un rapport d'erreur, Python termine le programme, et la valeur avec laquelle tu la construis devient le **code de sortie**. Donc `main()` s'exécute, **renvoie un nombre**, et ce nombre devient le code avec lequel le programme se termine. Nous le verrons en détail en 7.4 ; pour l'instant, il suffit de savoir que le `-m` cherche cette pièce. La [documentation de `__main__`](https://docs.python.org/3/library/__main__.html#main-py-in-python-packages) et celle de l'[option `-m`](https://docs.python.org/3/using/cmdline.html#cmdoption-m) le racontent en détail.

#### 7.1.4 Déplacer les fichiers

Les quatre modules que tu avais déjà (`modelo.py`, `revision.py`, `formato.py`, `configuracion.py`) passent dans le paquet **sans changer une seule fonction** : les signatures sont celles de la leçon 6. Les seules choses qui changent sont leurs imports, qui cessent d'être `from modelo import ...` pour devenir `from revisor.modelo import ...`. Le `revisor.py` à plat devient `cli.py` et se réécrit en 7.3. Et le script `ver_json.py` disparaît, parce que `--formato json` le remplace. Depuis le dossier du projet, avec l'environnement activé, voici les étapes. Elles utilisent trois commandes du terminal que tu n'avais pas vues, et il convient de savoir ce que fait chacune avant de l'écrire :

- **`mkdir -p src/revisor`** crée le dossier `src` et, dedans, `revisor`, d'un coup. Sans `-p`, `mkdir` refuserait de créer `revisor` parce que `src` n'existe pas encore ; avec `-p` (*parents*, « les parents »), il crée aussi les dossiers intermédiaires qui manquent, et ne se plaint pas s'ils existaient déjà.
- **`mv origen destino`** (*move*) **déplace** des fichiers, ou change leur nom. `mv modelo.py revision.py formato.py configuracion.py src/revisor/` déplace les quatre fichiers dans ce dossier (la barre finale dit que la destination est un dossier). `mv revisor.py src/revisor/cli.py` déplace et renomme à la fois. Si dans la destination il y a déjà un fichier avec ce nom, `mv` le remplace sans demander.
- **`rm archivo`** (*remove*) **supprime** un fichier, et ne l'envoie pas à la corbeille : il ne se récupère pas. Ici il supprime `ver_json.py`, qui ne sert plus, et à la fin les copies `.bak` que laisse `sed`. Le `*` de `src/revisor/*.bak` veut dire « tous les fichiers de ce dossier qui se terminent par `.bak` » ; avant un `rm` avec `*`, un `ls` avec le même motif te montre exactement ce qui va être supprimé.

Voici les étapes :

```bash
mkdir -p src/revisor
mv modelo.py revision.py formato.py configuracion.py src/revisor/
mv revisor.py src/revisor/cli.py
rm ver_json.py
sed -i.bak -E 's/^from (modelo|formato|configuracion|revision) import/from revisor.\1 import/' src/revisor/*.py
rm src/revisor/*.bak
```

La commande `sed` est un éditeur de texte sans fenêtre : elle cherche dans chaque fichier les lignes qui commencent par `from modelo import` (ou `formato`, `configuracion`, `revision`) et leur ajoute `revisor.` devant. Les paramètres `-i.bak` lui demandent de conserver une copie de sauvegarde de chaque fichier avec la terminaison `.bak`, qui est supprimée aussitôt. Si tu préfères ne pas l'utiliser, tu modifies à la main les lignes qui disent `from modelo import`, et vérifie avec ceci ce qui doit rester dans chaque fichier :

| Fichier | Imports une fois terminé |
|---|---|
| `revision.py` | `from revisor.modelo import Resultado, Servicio, clasificar` |
| `formato.py` | `import json` et `from revisor.modelo import Estado, Resultado` |
| `configuracion.py` | `from revisor.modelo import Servicio, nombres_repetidos` (plus ceux de la bibliothèque standard, sans changement) |
| `modelo.py` | n'importe rien de ton projet |

Le `cli.py` se réécrit entièrement en 7.3. Tu ne peux encore rien exécuter : il faut créer les trois nouveaux fichiers (`__init__.py`, `__main__.py` et `pyproject.toml`) et écrire `cli.py`. Continue à lire.

### 7.2 `pyproject.toml` : le projet décrit pour les outils

Un paquet, en lui-même, n'est qu'un dossier. Pour que `pip` sache l'installer, il faut le décrire : comment il s'appelle, quelle version il est, de quelle version de Python il a besoin, quelle commande il crée. Cela s'écrit dans un fichier appelé `pyproject.toml` à la racine du projet. C'est un fichier TOML, le format que tu as appris à lire dans la leçon 6, et c'est le mécanisme officiel : le [guide d'empaquetage](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) le décrit comme l'endroit où vont les métadonnées d'un projet Python. Voici celui du `revisor` :

```toml fig07_01/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.6.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
revisor = "revisor.cli:main"
```

Il a trois tables, et chacune répond à une question différente.

**`[build-system]` : avec quoi construit-on ?** Installer un paquet, même s'il est à toi et local, implique une étape de construction : lire le `pyproject.toml`, réunir les fichiers, produire quelque chose d'installable. Ce travail est fait par un outil qu'on appelle *backend de construction*, et le projet doit dire lequel il veut. `requires` liste ce qu'il faut télécharger pour construire, et `build-backend` nomme le backend. Ici on utilise `hatchling`, celui qu'utilise le guide officiel d'empaquetage, et on demande la version 1.27 ou postérieure (`>=1.27`). Il y a un détail qu'il vaut mieux connaître d'emblée : la première fois que tu installeras le paquet, `pip` **télécharge `hatchling` depuis internet** dans un environnement temporaire pour le construire. C'est une dépendance de *construction*, pas de ton programme : le `revisor` continue de ne dépendre de rien pour fonctionner. Mais sans connexion, l'installation échouerait à cette étape. Les règles de cette table sont dans la [PEP 518](https://peps.python.org/pep-0518/) et l'interface des backends dans la [PEP 517](https://peps.python.org/pep-0517/) ; `hatchling` a sa [propre documentation](https://hatch.pypa.io/latest/).

**`[project]` : qu'est-ce que ce projet ?** Ici vont les données que n'importe qui attendrait dans la fiche d'un paquet. `name` est le nom avec lequel il s'installe. `version` est la version : le cours la monte d'un cran à chaque leçon à partir d'aujourd'hui (`0.6.0` est celle d'aujourd'hui, et la leçon 11 la laisse à `1.0.0`). `description` est une phrase. `requires-python = ">=3.12"` dit quelles versions de Python peuvent l'exécuter : `pip` refusera de l'installer sur un Python plus ancien, au lieu de le laisser échouer avec un `SyntaxError` incompréhensible plus tard. Et `dependencies = []` est la liste des paquets tiers dont ton programme a besoin pour tourner : aujourd'hui, aucun, et c'est pourquoi elle est vide. Dans la leçon 9, il en apparaîtra un. Le standard qui définit ces champs est la [PEP 621](https://peps.python.org/pep-0621/).

**`[project.scripts]` : quelle commande crée-t-il ?** C'est la table qui transforme un paquet en outil. La ligne `revisor = "revisor.cli:main"` dit : « à l'installation, crée dans l'environnement une commande qui s'appelle `revisor`, et quand quelqu'un l'exécute, qu'elle appelle la fonction `main` du module `revisor.cli` ». La forme `paquete.modulo:función` est une convention que fixe la [spécification des points d'entrée](https://packaging.python.org/en/latest/specifications/entry-points/). Quand tu l'installeras, la commande `revisor` se trouvera à côté du `python` de ton environnement, et fonctionnera comme `python -m revisor`. Et encore une fois : la valeur que `main` renvoie devient le code de sortie de la commande.

Copie le contenu dans `pyproject.toml`, à côté du `servicios.toml`, dans le dossier du projet. Tu ne peux pas encore installer : il manque le centre du programme.

### 7.3 `argparse` : options de ligne de commande

#### 7.3.1 Ce que reçoit un programme depuis le terminal

Quand tu écris `python -m revisor --formato json`, le terminal découpe ce que tu as tapé en mots et les remet au programme sous la forme d'une liste de textes, que Python conserve dans `sys.argv`. Dans cette liste, la première position est le nom du programme et les autres sont les arguments : `["fig07_02.py", "--formato", "json"]`. Tu pourrais la parcourir toi-même, avec un `for`, et chercher à la main `--formato` et le texte qui le suit. Mais cela devient vite fastidieux : que se passe-t-il si l'utilisateur écrit l'option deux fois ? S'il oublie la valeur ? S'il écrit `--formato=json` avec un signe égal ? Pour ne pas réécrire ces règles dans chaque programme, la bibliothèque standard fournit le module `argparse`, qui les résout, génère l'aide tout seul, et valide ce que l'utilisateur écrit.

Regarde un petit programme qui le démontre, `fig07_02.py`. Il déclare deux options et les affiche :

```python
# fig07_02.py
import argparse

parser = argparse.ArgumentParser(description="Demostración de argparse.")
parser.add_argument("--config", default="servicios.toml")
parser.add_argument("--formato", choices=["tabla", "json"], default="tabla")

argumentos = parser.parse_args()
print(f"config = {argumentos.config}")
print(f"formato = {argumentos.formato}")
```

`argparse.ArgumentParser(description=...)` crée l'**analyseur** (*parser*) : l'objet qui saura interpréter la ligne de commande. Chaque `add_argument` déclare une option : son nom (avec deux tirets devant, la convention des options longues), une valeur par défaut (`default`) et, dans la seconde, `choices`, la liste fermée des valeurs permises. Enfin, `parse_args()` lit `sys.argv`, vérifie tout et renvoie un objet avec un attribut par option, de sorte que `argumentos.formato` a la valeur qu'a écrite l'utilisateur, ou celle par défaut s'il n'a rien écrit. Exécute-le sans options, puis avec elles :

```text
$ python fig07_02.py
config = servicios.toml
formato = tabla
```

```text
$ python fig07_02.py --formato json --config otro.toml
config = otro.toml
formato = json
```

Sans options, ce sont les valeurs par défaut qui valent. Avec elles, ce sont celles que tu as écrites, dans l'ordre que tu veux. Mais ce qui est précieux, c'est ce que fait `argparse` sans que tu le demandes. D'abord, l'aide : `-h` et `--help` existent automatiquement.

```text
$ python fig07_02.py --help
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]

Demostración de argparse.

options:
  -h, --help            show this help message and exit
  --config CONFIG
  --formato {tabla,json}
```

Elle est construite à partir de ce que tu as déclaré : l'usage, la description, et chaque option avec sa liste de valeurs. (Les mots fixes d'`argparse`, comme « options » ou « show this help message and exit », sont en anglais parce qu'ils viennent de la bibliothèque ; les textes que tu écris avec `help=` et `description=` sortent comme tu les écris, et c'est ce que nous ferons dans le `revisor`.) Ensuite, les erreurs : si l'utilisateur écrit quelque chose que tu n'as pas déclaré, `argparse` le rejette avec un message et termine le programme :

```text
$ python fig07_02.py --verbose
usage: fig07_02.py [-h] [--config CONFIG] [--formato {tabla,json}]
fig07_02.py: error: unrecognized arguments: --verbose
```

Le message dit ce qui a échoué (`unrecognized arguments: --verbose`, « arguments non reconnus ») et répète la ligne d'usage pour que l'utilisateur voie quelle est la forme correcte. Il termine en plus le programme avec un code de sortie différent de zéro, précisément le 2 : la [documentation d'`argparse`](https://docs.python.org/3/library/argparse.html#exiting-methods) l'établit pour toute erreur d'usage. Ce 2 sera celui du `revisor` quand l'usage est invalide.

#### 7.3.2 Le `cli.py` du `revisor`

Avec cela en main, le module central du paquet se lit sans sursaut. `cli.py` (« *command-line interface* », l'interface en ligne de commande) remplace le `revisor.py` à plat de la leçon 6. Il a deux fonctions : une qui monte l'analyseur et une autre qui est le programme. Lis-le en entier une fois :

```python
# fig07_01/src/revisor/cli.py
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

**`construir_parser`** renvoie l'analyseur, avec trois options. `--config` reçoit le chemin du fichier de configuration ; `type=Path` dit à `argparse` de convertir le texte qu'écrit l'utilisateur en un `Path` (leçon 6), et sa valeur par défaut est `Path("servicios.toml")`, la même de toujours. `--formato` a deux choix fermés, `tabla` et `json`, et par défaut `tabla` : si l'utilisateur écrit autre chose, `argparse` le rejette avant que le reste de `main` ne voie la valeur, et il n'y a pas de `if` à écrire pour cela. Et `--version` utilise `action="version"`, une action prédéfinie qui affiche un texte et termine : le texte est `revisor` suivi du numéro de version, qui se **lit dans les métadonnées du paquet installé** avec `importlib.metadata.version("revisor")`. Cela résout un problème très courant : le numéro de version serait écrit dans `pyproject.toml` et une seconde fois dans le code, et les deux copies finiraient par différer. Ainsi il n'existe qu'à un seul endroit, le `pyproject.toml`. L'argument `prog="revisor"` fixe le nom qui apparaît dans l'usage et dans les erreurs ; sans lui, en Python 3.12, on verrait `__main__.py`, le fichier qui s'exécute avec `-m`, et en 3.14 on verrait `python -m revisor` ; avec `prog`, les deux versions disent la même chose.

**`main`** est le programme. Il reçoit une liste d'arguments facultative, `argv: list[str] | None = None`, et renvoie un entier. Si `argv` est `None`, `parse_args(None)` lit la vraie ligne de commande ; si tu lui passes une liste, il l'utilise à la place. Ce paramètre ressemble aujourd'hui à un luxe et c'est une pièce clé dans la leçon 8, où les tests appelleront `main(["--formato", "json"])` sans toucher au terminal. Le corps est ce que tu connais déjà : il lit les services avec `leer_servicios(argumentos.config)`, et s'il échoue avec `ErrorDeConfiguracion`, il affiche le message et renvoie 2. Il y a deux différences avec la leçon 6, et ce sont les deux idées de 7.4 : le message sort maintenant avec `file=sys.stderr` (vers la sortie d'erreur, pas la standard) et il renvoie 2 au lieu de nettoyer et de continuer. Ensuite il vérifie les services, et selon `--formato` il affiche le tableau de toujours ou le JSON de `reporte_a_json`. Enfin, il décide du code de sortie : il construit la liste des résultats dont l'état **n'est pas** `ARRIBA` (l'opérateur `is not` est la négation de `is`, leçon 3), et si elle est vide il renvoie 0, sinon 1.

Pour que ce soit explicite, les codes de sortie du `revisor` sont ces trois, **ceux du cours entier** :

| Code | Ce que cela signifie |
|---|---|
| `0` | Tout est `ARRIBA`. |
| `1` | Le `revisor` a fonctionné, mais un service est `LENTO` ou `CAIDO`. |
| `2` | Le `revisor` n'a pas pu vérifier : l'usage est invalide (c'est `argparse` qui le décide) ou la configuration ne convient pas. |

La distinction entre 1 et 2 est très importante. Un `1` est une réponse : « j'ai vérifié et j'ai trouvé des problèmes ». Un `2` est une panne du programme lui-même : « je n'ai même pas pu vérifier ». Qui automatise le `revisor` les traitera différemment : avec un `1`, il préviendra la personne qui s'occupe des services ; avec un `2`, il préviendra la personne qui maintient le `revisor`.

### 7.4 Codes de sortie, deux canaux de texte, et l'installation éditable

#### 7.4.1 Les codes de sortie

Tout programme qui se termine laisse à celui qui l'a appelé un nombre entier entre 0 et 255. C'est le **code de sortie** (*exit status*). Par convention Unix, **0 signifie succès et tout autre nombre signifie un type d'échec**. Il n'y a rien de magique : c'est un accord, et tout l'écosystème du terminal le respecte. Dans le terminal (techniquement, l'interpréteur de commandes, qui sous Linux Mint est `bash`), tu peux demander le code de la dernière commande avec la variable spéciale `$?`, qui se lit avec `echo $?`. Le standard POSIX définit comment l'interpréteur de commandes l'interprète dans la [section sur l'état de sortie](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_08_02), et c'est ce qui permet d'écrire des choses comme `revisor && echo "todo bien"` (le `echo` ne s'exécute que si `revisor` s'est terminé par 0) ou `revisor || avisar.sh` (le second ne s'exécute que si le premier s'est terminé par autre chose que 0).

En Python, il y a deux façons de sortir avec un code. L'une est d'appeler `sys.exit(codigo)`, qui lève `SystemExit`. L'autre est ce que tu as déjà vu dans `__main__.py` : lever `SystemExit` toi-même. Elles font la même chose, et la [documentation de `sys.exit`](https://docs.python.org/3/library/sys.html#sys.exit) et celle de [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) l'expliquent. Ce qui importe, c'est la conception : `main` **renvoie** le code au lieu d'appeler `sys.exit` de son propre chef, et c'est `__main__.py` qui le convertit en sortie. Ainsi `main` peut être appelé depuis un autre code (un test, par exemple) et renvoyer son nombre sans tuer le processus qui l'a appelé. Quand quelqu'un installe le paquet, la commande `revisor` que crée `[project.scripts]` fait la même chose : elle appelle `main()` et sort avec ce qu'il renvoie.

#### 7.4.2 Deux canaux : la sortie standard et la sortie d'erreur

Un programme a, dès qu'il démarre, deux endroits où écrire du texte. La **sortie standard** (`stdout`) est le canal normal : ce que `print` écrit par défaut, et où vont les résultats. La **sortie d'erreur** (`stderr`) est un canal à part pour les avertissements et les erreurs. Dans le terminal, les deux apparaissent à l'écran, l'un à côté de l'autre, et c'est pourquoi ils semblent identiques. Mais ce sont des canaux distincts, et cette différence se remarque dès qu'on en redirige un. Regarde `fig07_03.py`, qui écrit dans les deux :

```python
# fig07_03.py
import sys

print("reporte: 4 servicios revisados")
print("aviso: reportes no respondió", file=sys.stderr)
```

`print(..., file=sys.stderr)` envoie le texte vers la sortie d'erreur au lieu de la standard ; `sys` est un module de la bibliothèque standard qui donne accès à des choses de l'interpréteur lui-même, parmi lesquelles `sys.stderr` ([documentation](https://docs.python.org/3/library/sys.html#sys.stderr)). Exécute-le trois fois :

```text
$ python fig07_03.py
reporte: 4 servicios revisados
aviso: reportes no respondió
```

```text
$ python fig07_03.py > /dev/null
aviso: reportes no respondió
```

```text
$ python fig07_03.py 2> /dev/null
reporte: 4 servicios revisados
```

La première montre les deux lignes. La deuxième utilise `>`, qui **redirige la sortie standard** vers un autre endroit (ici, `/dev/null`, un fichier spécial de Linux qui jette tout ce qu'on y écrit) : il ne reste que l'avertissement, qui voyage par l'autre canal. La troisième utilise `2>`, qui redirige le canal numéro 2, celui d'erreur, et laisse passer le rapport. (Les canaux ont un numéro : 0 l'entrée, 1 la standard, 2 celle d'erreur.) Les [redirections de l'interpréteur de commandes](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#tag_19_07) sont le mécanisme qui le permet.

C'est cela qui rend la séparation utile. Quand quelqu'un exécute `revisor --formato json > reporte.json`, il veut que le fichier `reporte.json` contienne **uniquement le JSON**. Si le programme écrivait un message d'erreur sur la sortie standard, le fichier se retrouverait avec du texte mélangé et cesserait d'être du JSON valide. Avec l'erreur sur `stderr`, le message sort à l'écran, le fichier reste propre (ou vide, si le programme n'a rien pu produire) et le code de sortie dit ce qui s'est passé. C'est pourquoi le `cli.py` envoie les erreurs de configuration vers `stderr` et le rapport vers `stdout`.

Voici comment se comporte le `revisor` déjà installé quand on lui donne un fichier de configuration qui n'existe pas : le message sort par la sortie d'erreur et le programme se termine avec le code 2.

```text
$ python -m revisor --config no-existe.toml
error de configuración: no existe el archivo no-existe.toml
$ echo $?
2
```

#### 7.4.3 Installer en mode éditable

Il manque l'étape qui unit le tout : installer le paquet. Avant cela, regarde ce qui se passe si tu essaies de l'exécuter **sans** l'installer. Avec l'environnement actif et placé dans le dossier du projet, avec les fichiers déjà à leur place :

```text
$ python -m revisor
/home/tu_usuario/curso-python/.venv/bin/python: No module named revisor
```

Le message, `No module named revisor`, est ce qu'on pouvait attendre d'après 7.1.2 : Python a cherché un module appelé `revisor` dans le dossier courant et dans l'environnement, et ne l'a pas trouvé, parce que le paquet est dans `src/`, un dossier où il ne cherche pas. (Le chemin au début est celui du `python` de ton environnement virtuel ; le tien sera celui de ton dossier.) Ce n'est pas une erreur de ton code : c'est ce que `src/` provoque exprès, et cela se résout en installant.

L'installation se fait avec `pip`, dans l'environnement, depuis le dossier du projet (là où se trouve le `pyproject.toml`) :

```bash
python -m pip install -e .
```

Le point final signifie « le projet de ce dossier », et `-e` (« *editable* ») demande une installation **éditable**. Tu verras plusieurs lignes d'avancement, qui changent d'une version de `pip` à l'autre, et la dernière dit quelque chose comme ceci :

```text
Successfully installed revisor-0.6.0
```

Si le message est autre, lis la cause : le plus courant est que tu ne sois pas dans le dossier qui contient le `pyproject.toml`, ou que tu n'aies pas de connexion pour que `pip` télécharge `hatchling`.

Que signifie « éditable » ? Une installation normale **copie** les fichiers du paquet dans le dossier `site-packages` de l'environnement, et à partir de là le paquet installé et ton dossier de travail sont deux choses distinctes : si tu modifies ton code, l'installé ne le sait pas. Une installation éditable, en revanche, laisse dans l'environnement **un pointeur vers ton dossier `src/`**, de sorte que Python importe le code d'où il se trouve, tel que tu l'as écrit ([PEP 660](https://peps.python.org/pep-0660/) ; la [documentation de `pip`](https://pip.pypa.io/en/stable/topics/local-project-installs/) explique les deux types d'installation locale). C'est ce que tu veux pendant que tu développes : tu changes une ligne, tu exécutes, et tu vois le changement, sans réinstaller. Avec le paquet installé, exécute-le ; cette fois, le code de sortie, c'est `echo $?` qui l'affiche :

```text
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
$ echo $?
1
```

Voilà le tableau de toujours, avec le récapitulatif, et le code de sortie est **1**, parce que parmi les quatre services il y en a un `LENTO` (`inventario`) et un `CAIDO` (`reportes`). C'est le comportement voulu : le programme a fonctionné, et il signale qu'il a trouvé des problèmes. L'option `--formato json` produit le rapport pour les machines, qui est le contrat qu'a fixé la leçon 6 :

```text
$ python -m revisor --formato json
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
$ echo $?
1
```

L'option `--version` lit le numéro de l'installation, et elle fonctionne parce que tu as installé le paquet :

```text
$ python -m revisor --version
revisor 0.6.0
```

Et `--help` te donne l'aide, construite avec les textes que tu as écrits dans `help=` :

```text
$ python -m revisor --help
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]

Revisa el estado de una lista de servicios.

options:
  -h, --help            show this help message and exit
  --config CONFIG       archivo TOML con la lista de servicios (por omisión:
                        servicios.toml)
  --formato {tabla,json}
                        forma del reporte (por omisión: tabla)
  --version             show program's version number and exit
```

Il manque la moitié de ce que promettait `[project.scripts]` : la **commande** `revisor`. Elle a été créée à l'installation, à côté du `python` de l'environnement, et avec l'environnement actif elle s'exécute sans `python -m` :

```text
$ revisor --version
revisor 0.6.0
```

Ce que fait `-m` est utile parce qu'il fonctionne toujours, même si la commande n'était pas visible. Mais la commande est la façon dont les gens utiliseront le `revisor` dans la leçon 11, installé avec `pipx`.

Deux précisions sur ce que « éditable » ne couvre pas. La première : **il ne suit que le code, pas les métadonnées**. Si tu changes le contenu d'un module, le changement se voit immédiatement. Mais si tu changes le `pyproject.toml` (par exemple, la version, ou une commande de `[project.scripts]`), l'environnement reste avec les métadonnées de la dernière installation, jusqu'à ce que tu exécutes de nouveau `python -m pip install -e .`. L'exercice 4 le vérifie. La seconde : l'installation éditable vit dans ton **environnement virtuel**, donc un nouvel environnement (ou un environnement fraîchement créé) n'a pas le `revisor` tant que tu ne l'as pas installé de nouveau. C'est exactement le comportement voulu : aucune installation ne se mélange avec le Python du système.

> **Encadré facultatif : `uv`.** Il existe un outil plus récent, `uv`, qui fait de son côté le travail de `venv` et de `pip`, et qui est plus rapide. Avec lui, les mêmes étapes s'écrivent `uv venv` (crée l'environnement `.venv`) et `uv pip install -e .` (installe le projet dedans). Il peut aussi installer d'autres versions de Python : `uv python install 3.14` télécharge la 3.14 sans toucher au Python du système, ce qui est la façon la plus commode d'essayer ce cours dans la version la plus récente en plus de la 3.12 de Mint. Le [guide d'installation d'`uv`](https://docs.astral.sh/uv/getting-started/installation/) explique comment l'obtenir, et sa documentation sur les [versions de Python](https://docs.astral.sh/uv/concepts/python-versions/) et sur l'[interface `uv pip`](https://docs.astral.sh/uv/pip/) couvre le reste. Ce cours ne l'exige pas : tout ce que tu vois ici fonctionne avec le `python` et le `pip` que tu as déjà.

#### 7.4.4 L'étape du projet : tout assembler

Si tu as suivi la leçon, ton dossier `~/curso-python/revisor/` a déjà l'aspect de 7.1.2. Voici les étapes complètes, dans l'ordre, pour qui les veut d'une traite :

1. Crée `src/revisor/` et déplace-y les quatre modules ; renomme `revisor.py` en `cli.py` et supprime `ver_json.py` (7.1.4).
2. Ajoute `revisor.` devant les imports de tes modules (7.1.4).
3. Écris `src/revisor/__init__.py` et `src/revisor/__main__.py` (7.1.3).
4. Écris `pyproject.toml` (7.2).
5. Réécris `src/revisor/cli.py` avec `construir_parser` et `main` (7.3.2).
6. Avec l'environnement activé et depuis le dossier du projet, exécute `python -m pip install -e .` (7.4.3).
7. Teste : `python -m revisor`, `python -m revisor --formato json`, `python -m revisor --version`, et après chacun, `echo $?`.

Il y a une conséquence de ce que tu viens de faire, qui se voit en l'exécutant depuis **un autre dossier**. Monte dans le dossier du dessus et exécute la même commande :

```text
$ python -m revisor
error de configuración: no existe el archivo servicios.toml
```

Le paquet a été trouvé (il est installé dans l'environnement, peu importe maintenant où tu es), mais le fichier de configuration non : `--config` vaut `servicios.toml` par défaut, un chemin relatif, et le dossier du dessus n'en a pas. Le message est celui que tu connais déjà de la leçon 6, maintenant sur la sortie d'erreur et avec le code de sortie 2. L'option `--config` existe justement pour cela : `python -m revisor --config revisor/servicios.toml` fonctionnerait depuis là. Où vit le code et où vit la configuration sont deux questions distinctes, et le programme les sépare.

## L'erreur que tu vas voir

Cette leçon a deux erreurs principales, toutes deux de la liste ci-dessus, et deux d'appui qui apparaissent quand on oublie quelque chose du montage.

**`No module named revisor`.** Tu l'as déjà vue en 7.4.3 : exécuter `python -m revisor` avant `pip install -e .`. La cause est la disposition `src/`, et la correction est d'installer. Si tu as déjà installé et que ça apparaît quand même, vérifie que l'environnement est activé : le message commence par le chemin du `python` qui a été utilisé, et si ce chemin est `/usr/bin/python3` au lieu de celui de ton `.venv`, tu utilises le Python du système, qui n'a pas ton paquet.

**L'erreur d'usage d'`argparse`.** Demande un format qui n'existe pas :

```text
$ python -m revisor --formato xml
usage: revisor [-h] [--config CONFIG] [--formato {tabla,json}] [--version]
revisor: error: argument --formato: invalid choice: 'xml' (choose from 'tabla', 'json')
$ echo $?
2
```

Lis les deux lignes : la première répète l'usage, avec les options qui existent et leurs valeurs permises entre accolades (`{tabla,json}`) ; la seconde dit quel argument a échoué et pourquoi : `invalid choice: 'xml'`, « choix invalide ». Entre parenthèses, la liste des choix valides. Le code de sortie est 2, celui qu'`argparse` utilise toujours pour un usage invalide. Un détail de version : c'est le texte de Python 3.14, qui montre les choix entre guillemets, `('tabla', 'json')`. En Python 3.12, la liste sort sans guillemets, `(choose from tabla, json)`. C'est la seule sortie de la leçon qui diffère entre les deux versions, et c'est un changement dans le format du texte ; le sens est le même.

**`ModuleNotFoundError: No module named 'modelo'`.** Elle apparaît si tu as déplacé les fichiers mais oublié de changer un import : le paquet est trouvé, mais l'un de ses modules continue d'importer `modelo` tout court, et il n'existe plus de `modelo` isolé. Le rapport, abrégé :

```text
Traceback (most recent call last):
  ...
  File "src/revisor/__main__.py", line 2, in <module>
    from revisor.cli import main
  File "src/revisor/cli.py", line 9, in <module>
    from modelo import Estado
ModuleNotFoundError: No module named 'modelo'
```

Il se lit de bas en haut, comme toujours : la dernière ligne dit quel module n'a pas été trouvé (`modelo`) ; la ligne du dessus, dans quel fichier et à quelle ligne se trouve l'`import` qui échoue (`cli.py`, ligne 9) ; et plus haut, la chaîne de qui a importé qui. La correction est `from revisor.modelo import Estado`. (Le numéro de ligne dépendra de la façon dont tu as écrit ton `cli.py` ; ce qui importe, c'est le nom du module de la dernière ligne.)

**`importlib.metadata.PackageNotFoundError: No package metadata was found for revisor`.** Elle apparaît si tu exécutes le code sans avoir installé le paquet (par exemple, en ajoutant `src` à la main à la liste des endroits de recherche). Les modules sont trouvés, mais `version("revisor")`, que `construir_parser` exécute toujours, cherche les **métadonnées** d'une installation, et il n'y en a aucune. C'est la preuve que le numéro de version vient de l'installation et non du code : la solution est `python -m pip install -e .`, pas de cacher la ligne. Le rapport se termine ainsi :

```text
importlib.metadata.PackageNotFoundError: No package metadata was found for revisor
```

## Ce qui se fait de travers

**Importer sans le nom du paquet à l'intérieur d'un paquet.** `from modelo import Servicio` fonctionne tant que les fichiers sont collés et échoue dès que le code s'installe ou s'exécute avec `-m`. À l'intérieur du paquet, on écrit toujours `from revisor.modelo import Servicio`.

**Arranger les imports en modifiant `sys.path`.** C'est une recette qui circule : ajouter à la main le dossier du code à la liste des endroits de recherche pour que les `import` fonctionnent. Cela résout le symptôme et cache la cause, qui est que le paquet n'est pas installé. Avec `pip install -e .`, ce n'est pas nécessaire.

**Installer avec `pip` hors de l'environnement virtuel.** Tu sais déjà pourquoi cela ne marche pas sous Linux Mint (leçon 1) : le Python du système ne fournit pas `pip` (`No module named pip`), et là où il le fournit, la protection de la PEP 668 le bloque avec `externally-managed-environment`. Et la sortie qu'on suggère parfois, le forcer, casse les outils du système lui-même. On installe dans le `.venv`, toujours.

**Écrire le numéro de version à deux endroits.** Un dans `pyproject.toml` et un autre dans une constante du code : tôt ou tard ils diffèrent, et la version que dit le programme n'est plus celle qui a été installée. Le numéro vit dans le `pyproject.toml`, et le programme le lit avec `importlib.metadata`.

**Envoyer les erreurs vers la sortie standard.** Cela mélange l'avertissement avec le rapport, et `revisor --formato json > reporte.json` produit un fichier qui n'est pas du JSON valide. Les erreurs, vers `sys.stderr`.

**Toujours terminer avec le code 0.** Un programme qui sort aussi bien avec tout en panne qu'avec tout en marche ne sert à aucun automatisme. Le code de sortie fait partie du contrat du programme, autant que le format du rapport.

**Inventer des codes de sortie sans les documenter.** Un 3 pour ceci, un 4 pour cela, sans que personne ne les connaisse, oblige celui qui automatise à lire le code source. Il y a trois codes et ils sont dans un tableau.

**Lire `sys.argv` à la main.** Cela marche jusqu'à ce que quelqu'un écrive `--formato=json` au lieu de `--formato json`, ou oublie la valeur, ou demande l'aide. `argparse` a déjà résolu ces cas.

**Changer le `pyproject.toml` sans réinstaller.** L'installation éditable suit le code, pas les métadonnées. Si tu changes la version ou une commande et que l'environnement reste avec l'ancien, il manque un `python -m pip install -e .`.

## Exercices

### Exercice 1 — Le rapport en JSON et son code

Avec le paquet installé, exécute `python -m revisor --formato json` et, juste après, `echo $?`. Avant d'exécuter, écris ce que tu t'attends à voir : combien de services il y a dans le tableau `servicios`, quelle valeur a `tiempo_ms` pour `reportes`, et quel code de sortie. Ensuite, redirige la sortie vers un fichier avec `python -m revisor --formato json > reporte.json` et regarde le contenu de `reporte.json` avec `cat reporte.json` (`cat` affiche à l'écran le contenu d'un fichier). Le code de sortie a-t-il changé en redirigeant ?

### Exercice 2 — Les trois codes

Provoque les trois codes de sortie du `revisor`, un par un, et vérifie-les avec `echo $?` : (a) un `0`, pour lequel il te faut une configuration où tous les services sont `ARRIBA` (écris un fichier `solo-arriba.toml` avec un seul service, `pagos`, et utilise-le avec `--config`) ; (b) un `1`, avec le `servicios.toml` de toujours ; (c) un `2` pour configuration invalide, avec un `roto.toml` qui a un service sans `nombre` ; (d) un autre `2`, cette fois pour usage invalide, avec une valeur de `--formato` qui n'existe pas. Pour chaque cas, écris d'abord ce que tu t'attends à voir et sur quel canal apparaît le message.

### Exercice 3 — Où vit le code et où vit la configuration

Sors du dossier du projet avec `cd ..` et exécute `python -m revisor`. Quel message obtiens-tu et quel code de sortie ? Ensuite exécute la même commande en passant le chemin de la configuration avec `--config`. Explique avec tes mots pourquoi le paquet est trouvé depuis n'importe quel dossier mais pas le fichier de configuration.

### Exercice 4 — Ce que suit et ne suit pas l'installation éditable

Avec le paquet installé en mode éditable : (a) dans `src/revisor/formato.py`, change le mot `promedio` du récapitulatif en `media`, et exécute le `revisor` sans réinstaller : le changement se remarque-t-il ? Remets-le comme il était. (b) Dans `pyproject.toml`, change la version en `0.6.1`, et exécute `python -m revisor --version` sans réinstaller : quelle version dit-il ? (c) Exécute `python -m pip install -e .` et redemande la version. (d) Remets la version à `0.6.0` et réinstalle. Explique la différence entre (a) et (b).

## Solutions

### Solution 1

La prédiction : le tableau `servicios` a **quatre** éléments, un par service ; celui de `reportes` a `"tiempo_ms": null` (il n'a pas répondu, et `None` s'écrit `null` en JSON) ; et le code de sortie est **1**, à cause du service lent et du service en panne. La sortie de `python -m revisor --formato json` est celle que tu as vue en 7.4.3, et le `echo $?` affiche `1`.

En redirigeant, le contenu de `reporte.json` est **exactement le même JSON** : rien du terminal ne s'y est mélangé, parce que les avertissements (s'il y en avait) vont par un autre canal. Et le code de sortie **ne change pas** : rediriger déplace le texte, pas le résultat. C'est la propriété qui permet d'écrire `revisor --formato json > reporte.json || avisar.sh` et que le `||` continue de fonctionner.

### Solution 2

(a) Avec un seul service qui répond bien :

```toml
[[servicios]]
nombre = "pagos"
url = "https://pagos.example"
```

Exécuté avec `python -m revisor --config solo-arriba.toml` :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA      87ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 87ms
```

et `echo $?` affiche **0**. (Remarque que le récapitulatif dit « 1 servicio » et « 0 lentos » : le pluriel est décidé par le compte, comme dans la leçon 5.)

(b) Avec le `servicios.toml` de toujours : le tableau de quatre services et le code **1**.

(c) Avec un `roto.toml` dont l'unique service n'a pas de `nombre` :

```toml
[[servicios]]
url = "https://pagos.example"
```

Exécuté avec `python -m revisor --config roto.toml`, il sort par la **sortie d'erreur** le message `error de configuración: servicio 1: falta 'nombre'`, et le code est **2**. Pour vérifier le canal, répète la commande avec `2> /dev/null` : rien n'apparaît à l'écran, parce que la seule chose qui a été affichée passait par `stderr` ; le code de sortie reste 2.

(d) Avec `python -m revisor --formato xml`, l'erreur d'`argparse` que tu as déjà vue : elle passe par la sortie d'erreur, et le code est **2**.

### Solution 3

Depuis le dossier du dessus, `python -m revisor` affiche, par la sortie d'erreur, `error de configuración: no existe el archivo servicios.toml`, et le code de sortie est **2**. Avec `python -m revisor --config revisor/servicios.toml`, le programme trouve le fichier, affiche le tableau de quatre services et sort avec **1**.

La raison : le **paquet** est trouvé parce qu'il est installé dans l'environnement, et l'environnement ne dépend pas du dossier où tu es. En revanche `servicios.toml` est un fichier **de données** avec un chemin relatif, et un chemin relatif se compte toujours depuis l'endroit où l'on se trouve. Ce sont deux mécanismes de recherche distincts : Python cherche du code dans les dossiers de l'environnement ; le programme cherche la configuration là où on le lui dit. C'est pourquoi `--config` existe.

### Solution 4

(a) Oui, ça se remarque : le récapitulatif dit `media 843ms` au lieu de `promedio 843ms`, sans réinstaller, parce que l'installation éditable importe le code depuis ton dossier `src/`. (b) Ça ne se remarque pas : `--version` continue de dire `revisor 0.6.0`, parce que la version se lit dans les métadonnées enregistrées lors de la dernière installation, et modifier le `pyproject.toml` ne les met pas à jour. (c) Après `python -m pip install -e .`, `--version` dit `revisor 0.6.1`. (d) En remettant la version à `0.6.0` et en réinstallant, il dit de nouveau `revisor 0.6.0`.

La différence : le **code** est importé d'où il se trouve, chaque fois que Python démarre ; les **métadonnées** (version, commandes) sont copiées dans l'environnement à l'installation. Ce que `-e` évite, c'est la copie du code, pas celle des métadonnées.

## Comment savoir que j'ai réussi

- [ ] `python -m revisor` affiche le tableau des quatre services avec le récapitulatif `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`, et `echo $?` affiche `1`.
- [ ] `python -m revisor --formato json` affiche le JSON avec `"promedio_ms": 843`, et `python -m revisor --formato json > reporte.json` laisse dans le fichier un JSON valide et rien d'autre.
- [ ] `python -m revisor --version` affiche `revisor 0.6.0`, et la commande `revisor --version` affiche la même chose.
- [ ] `python -m revisor --formato xml` se termine avec l'erreur d'`argparse` et le code 2.
- [ ] `python -m revisor --config no-existe.toml` affiche `error de configuración: no existe el archivo no-existe.toml` et se termine avec 2 ; avec `2> /dev/null`, rien ne s'affiche à l'écran.
- [ ] Tu peux expliquer avec tes mots pourquoi `python -m revisor` échoue avec `No module named revisor` avant l'installation, et pourquoi c'est ce que `src/` vise.
- [ ] Tu peux dire quel canal utilise chaque message du `revisor` (rapport, erreur de configuration, erreur d'usage) et quel code accompagne chaque cas.
- [ ] Tu as noté dans ton journal de bord quelle partie du montage (chemins, imports, installation) t'a donné le plus de mal.

## Résumé

Réponds sans regarder la leçon :

1. Quelle différence y a-t-il entre un module et un paquet, et qu'est-ce qui en fait un paquet ?
2. Quel avantage y a-t-il à mettre le paquet dans `src/` ? Que se passerait-il avec `python -m revisor` depuis la racine s'il n'y était pas ?
3. Qu'exécute `python -m revisor`, et que fait `raise SystemExit(main())` ?
4. À quelle question répond chaque table du `pyproject.toml` : `[build-system]`, `[project]` et `[project.scripts]` ?
5. Pourquoi `pip install -e .` a-t-il besoin d'internet la première fois, si le `revisor` n'a pas de dépendances ?
6. Que renvoie `parse_args()` ? Que fait `argparse` quand l'utilisateur écrit une option qui n'existe pas, et avec quel code se termine-t-il ?
7. Que signifient les codes 0, 1 et 2 du `revisor` ? Comment lit-on le code de la dernière commande dans le terminal ?
8. Quelle différence y a-t-il entre la sortie standard et la sortie d'erreur ? Que font `>` et `2>` ?
9. Que suit une installation éditable et que ne suit-elle pas ? Comment met-on à jour ce qu'elle ne suit pas ?
10. D'où vient le numéro qu'affiche `--version`, et pourquoi ne l'écrit-on pas dans le code ?

## Pour aller plus loin

- [Python, `argparse`](https://docs.python.org/3/library/argparse.html) : la référence complète du module (actions, sous-commandes, groupes d'options). En anglais, comme presque toute la documentation officielle. Consulté le 7 octobre 2026.
- [Python Packaging User Guide, « Writing your `pyproject.toml` »](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) : tous les champs de `[project]` et de `[project.scripts]`, et les raisons de la conception. Consulté le 7 octobre 2026.
- [Python Packaging User Guide, « src layout vs flat layout »](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) : les deux façons de placer le paquet, comparées avec leurs coûts. Consulté le 7 octobre 2026.
- [Python, tutoriel sur les modules et les paquets](https://docs.python.org/3/tutorial/modules.html#packages) : comment on importe et comment on organise un paquet, avec les imports absolus et relatifs. Consulté le 7 octobre 2026.
