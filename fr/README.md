# Cours de Python — de zéro à un programme qui vérifie de nombreux services à la fois

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**À qui il s'adresse :** à qui n'a jamais programmé, ou a copié des scripts qui fonctionnent sans savoir pourquoi. On ne suppose rien : ni que tu aies Python installé, ni que tu saches ce qu'est un environnement virtuel. Chaque concept est expliqué quand il apparaît, et on explique pourquoi il existe, pas seulement comment il s'écrit.

**Ce que tu sauras à la fin :** écrire un programme complet, avec des tests et plusieurs tâches à la fois, comprendre ce que tu as écrit et pouvoir l'expliquer à quelqu'un d'autre. Et garder le discernement pour lire la documentation de Python par toi-même, ce qui est la véritable épreuve.

**La suite :** le même problème, le `revisor`, est résolu dans les cours de [Go](https://www.habil.mx/fr/cours/go/), de [Rust](https://www.habil.mx/fr/cours/rust/) et de [TypeScript](https://www.habil.mx/fr/cours/typescript/) de Hábil. Quand tu auras terminé celui-ci, comparer ta solution avec les leurs apprend plus que de repartir de zéro.

**Ce dont tu as besoin avant de commencer :** un ordinateur avec Linux Mint et savoir ouvrir un terminal. Rien de plus. La [Leçon 1](01-instalacion.md) prépare tout depuis zéro.

## Le projet que tu vas construire

Le **`revisor`** : un programme en ligne de commande qui reçoit une liste de services, les interroge **tous à la fois** et rend un rapport sous forme de tableau ou de JSON.

    $ revisor --config servicios.toml --formato tabla
    SERVICIO    ESTADO    TIEMPO  DETALLE
    catalogo    ARRIBA     160ms  200
    inventario  LENTO       2.3s  200
    pagos       ARRIBA      90ms  200
    reportes    CAIDO          —  sin conexión

    4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms

Il commence à la leçon 2 avec un en-tête et un seul service, et grandit à chaque leçon jusqu'à devenir un paquet qui s'installe comme n'importe quelle commande. Il paraît petit et ne l'est pas : pour l'écrire correctement, tu as besoin de fonctions, de collections, d'erreurs, de fichiers, de tests, de types, de HTTP et de tâches concurrentes.

## Les douze leçons

| Leçon | | Ce que tu construis | Ce que tu apprends |
|---|---|---|---|
| 0 | [Ce qu'est Python et ce qu'il n'est PAS](00-que-es-python.md) | rien pour l'instant (lecture) | interpréteur et *bytecode* ; typage dynamique mais fort ; les annotations ne sont pas imposées ; le GIL ; environnements virtuels ; versions |
| 1 | [Installer Python sur ton Linux Mint](01-instalacion.md) | l'environnement et ton premier script | le `python3` du système ; `externally-managed-environment` ; `venv` ; `pip` ; le REPL ; le premier *traceback* |
| 2 | [Valeurs, texte et décisions](02-valores-texto-decisiones.md) | l'en-tête du `revisor` et la classification d'un service | trois concepts : nombres, chaînes, booléens et `None` ; f-strings ; `if`/`elif`/`else` et l'indentation |
| 3 | [Boucles, fonctions et modules](03-bucles-funciones-modulos.md) | la fonction `revisar()` et le parcours de la liste | `for`, `while` ; `==` contre `is` ; `def` ; portée ; l'argument mutable par défaut ; `import` ; `__main__` |
| 4 | [Collections](04-colecciones.md) | le `revisor` sans listes parallèles : les données de chaque service, ensemble | `list`, `dict`, `tuple`, `set` ; compréhensions ; copie contre référence ; `KeyError` et `IndexError` |
| 5 | [Le modèle de données](05-modelo-de-datos.md) | le modèle `Servicio` / `Estado` et le rapport avec son récapitulatif | `dataclass` ; `Enum` ; `match` et `case` |
| 6 | [Erreurs, fichiers et données extérieures](06-errores-archivos-datos.md) | la lecture de la configuration | `try`/`except` ; lire un *traceback* ; `with` ; `pathlib` ; UTF-8 ; `json` et `tomllib` ; valider ; ni `eval` ni `pickle` |
| 7 | [Un paquet en ligne de commande](07-paquete-linea-de-comandos.md) | le `revisor` comme paquet | `pyproject.toml` ; `python -m revisor` ; `argparse` ; codes de sortie ; installation éditable avec `pip` ; `uv` en encadré facultatif |
| 8 | [Tests, types et qualité](08-pruebas-tipos-calidad.md) | le `revisor` avec des tests | `pytest` et table de cas ; `tmp_path` ; `monkeypatch` ; typage graduel avec `mypy` ; `ruff` |
| 9 | [HTTP et asyncio](09-http-y-asyncio.md) | le `revisor` qui interroge pour de vrai | `urllib` et `httpx` ; délais d'attente ; `async` et `await` ; `asyncio.run` |
| 10 | [Concurrence avec limites et tests sans réseau](10-concurrencia-pruebas-sin-red.md) | le `revisor` concurrent et testé | `TaskGroup` ; `timeout` ; `Semaphore` ; groupes d'exceptions ; réseau simulé dans les tests |
| 11 | [Le programme terminé](11-el-programa-terminado.md) | le `revisor` complet, installable | rapport en tableau et JSON ; `logging` ; sécurité ; construire et installer avec `pipx` |

À la fin de chaque leçon, il y a des exercices avec leurs solutions et une section « Pour aller plus loin » ; les sources de ce qui est affirmé sont liées dans le texte, là où elles sont utilisées. Et le [journal de bord](https://github.com/HabilMX/curso-python/blob/main/fr/bitacora.md) est à toi : note-y ce qui t'a donné du mal.

**Pour continuer à lire :** sur le blog de Hábil, [des tests qui attrapent les erreurs](https://www.habil.mx/fr/blog/tests-qui-attrapent-erreurs-couverture-quality-gate/) et [la sécurité des API](https://www.habil.mx/fr/blog/securite-api-cto-identite-passerelle-jetons/). Et dans les cours : si tu sais déjà programmer et que tu veux du Java moderne, le [cours de Java](https://github.com/HabilMX/curso-java).

## Trois critères qui traversent tout le cours

**L'erreur est un contenu, pas un accident.** Chaque leçon provoque exprès l'erreur que tu vas voir, montre le vrai *traceback* et apprend à le lire, de la dernière ligne vers le haut. Savoir lire une erreur, c'est la moitié de savoir programmer.

**L'environnement est réel.** On travaille sur Linux Mint avec le Python que le système fournit et ses règles, pas dans un notebook ouvert dans le navigateur. Tout le code s'exécute en Python 3.14 et aussi en 3.12, qui est celui de Mint.

**Les tests et la sécurité ne sont pas des leçons, ce sont des habitudes.** Les données extérieures se valident dans la 6, les tests arrivent dans la 8 et un test ne compte pas tant que tu ne l'as pas vu échouer, et l'adresse que quelqu'un écrit dans un fichier est traitée pour ce qu'elle est dans la 9 et la 11.

## Comment savoir que tu as terminé

Le cours ne se termine pas quand tu as lu la leçon 11, mais quand ton `revisor` remplit ces sept points :

1. **`pytest` se termine au vert et le rapport dit combien de tests ont été exécutés.** Compte-les dans le rapport, pas d'après le code de sortie : un vert avec zéro test ressemble à un vrai vert.
2. **`ruff check` et `ruff format --check` ne signalent rien, et `mypy` non plus.**
3. **Il vérifie 20 services à la fois en un temps proche de celui du plus lent**, pas de la somme de tous. Tu le mesures toi-même, avec l'horloge, en série et en parallèle.
4. **Un service en panne, lent ou qui répond n'importe quoi ne fait pas tomber le rapport :** il apparaît sur sa ligne avec son erreur, et le reste sort complet.
5. **Aucune requête ne peut attendre éternellement :** toutes ont un délai d'attente.
6. **Il s'exécute pareil en Python 3.14 et dans le 3.12 de ton Mint.**
7. **Il s'installe avec `pipx install` et `revisor --help` fonctionne depuis un autre dossier.** Il sort avec le code 0 si tout est en marche et 1 sinon.
