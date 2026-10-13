# Leçon 10 — Concurrence avec limites et tests sans réseau

**Durée :** 2 × 90 min (la première session va jusqu'à la fin de 10.2 ; la seconde commence en 10.3)

**Ce que tu construis :** le `revisor` concurrent et testé, version 0.9.0

**Ce que tu apprends :** `asyncio.TaskGroup` ; `asyncio.timeout()` et `asyncio.Semaphore` ; les groupes d'exceptions (`ExceptionGroup`, `except*`) et pourquoi une panne ne fait pas tomber le rapport ; les tests sans réseau avec `httpx.MockTransport` et `monkeypatch`

**D'où tu viens.** Tu arrives avec le paquet de la [Leçon 9](09-http-y-asyncio.md) : le `revisor` interroge déjà pour de vrai, avec `httpx`, un délai d'attente par service et une fonction `revisar` qui ne laisse jamais échapper une erreur réseau. Mais il le fait **en file** : `for` et `await`, un service à la fois. Avec les quatre services du laboratoire, l'exécution prend la somme des attentes, environ 2.5 secondes, et avec vingt services d'une demi-seconde elle prendrait dix secondes. En plus, il a une dette que la leçon précédente a dite franchement : ses 21 tests ne touchent à rien du nouveau, parce que tester du code qui utilise le réseau, tu ne sais pas encore le faire. Aujourd'hui, on règle les deux. Tu travailles dans ton dossier `~/curso-python/revisor/`, avec l'environnement virtuel activé, et il te faut avoir sous la main le `laboratorio.py` de la leçon 9 pour la partie mesure.

**Ce que cette leçon ne fait pas.** Elle ne change pas ce que le `revisor` affiche : le tableau et le JSON sortent comme dans la Leçon 9. Ce qui change, c'est **combien de temps ça prend** et **à quel point c'est sûr**. Elle n'utilise pas non plus de threads ni de processus : toute la concurrence d'aujourd'hui se passe dans un seul thread, ce qui convient quand ce qu'on fait est attendre le réseau. Le rapport final avec la largeur de colonne calculée, le journal d'événements (`logging`) et l'installation comme commande sont dans la [Leçon 11](11-el-programa-terminado.md).

## À la fin, tu seras capable de

- Lancer plusieurs interrogations à la fois avec `asyncio.TaskGroup`, recueillir leurs résultats dans l'ordre de la configuration et mesurer avec l'horloge que le total ressemble au service le plus lent et non à la somme.
- Expliquer pourquoi une tâche ne cède la main que sur un `await`, et pourquoi un `time.sleep` à l'intérieur d'une coroutine annule tout le gain.
- Mettre un plafond de temps à toute une opération avec `asyncio.timeout()` et dire en quoi il se distingue des délais d'attente d'`httpx`.
- Limiter combien d'interrogations tournent en même temps avec `asyncio.Semaphore`, et expliquer pourquoi avec 20 services et une limite de 10 le temps est le double de celui avec une limite de 20.
- Lire un `ExceptionGroup` et attraper ce qu'il contient avec `except*` ; dire pourquoi `revisar` convertit les erreurs réseau en résultats et pourquoi il ne convertit **pas** les erreurs de programmation.
- Tester `revisar` et `revisar_todos` sans toucher au réseau, avec `httpx.MockTransport`, et tester `main` en remplaçant une fonction par une autre avec `monkeypatch`.
- Vérifier au rouge un test (casser le code, le voir échouer, le corriger) et lire le décompte du rapport de `pytest`.

## Le pourquoi avant le comment

Imagine que le `revisor` est utilisé par l'astreinte d'une entreprise pour vérifier soixante services toutes les cinq minutes. Chaque service sain répond en une demi-seconde ; les services en panne mettent à renoncer jusqu'à leur délai d'attente, disons cinq secondes. En file, le meilleur jour l'exécution prend trente secondes, et le pire jour, avec dix services en panne, elle en prend soixante-quinze (cinquante sains à une demi-seconde, plus dix en panne à cinq secondes). Mais l'ordinateur n'a pas travaillé pendant ces soixante-quinze secondes : il a **attendu**. Il a envoyé une requête, est resté à regarder le mur jusqu'à l'arrivée de la réponse, et seulement alors a envoyé la suivante. Le réseau n'a pas besoin que le programme fasse la queue : les soixante requêtes peuvent voyager en même temps, et le programme n'a qu'à recueillir les réponses au fur et à mesure qu'elles arrivent.

C'est ce qu'`asyncio` fait bien, et c'est pourquoi cette leçon existe. Mais il y a trois problèmes cachés derrière « fais tout à la fois », et chacun est un concept d'aujourd'hui.

Le premier est **comment on les lance et on les recueille** sans en perdre aucune. Python 3.11 a apporté un outil pensé pour cela, `asyncio.TaskGroup`, qui démarre les tâches, les attend toutes avant de continuer et ne laisse aucune se perdre en chemin.

Le deuxième est **jusqu'où**. « Tout à la fois » avec soixante services est raisonnable. Avec six mille, ce peut être une attaque contre tes propres serveurs, ou ton système d'exploitation qui dit qu'il ne te donne plus de connexions. Il faut une limite du nombre d'interrogations qui tournent simultanément, et il faut un plafond de temps pour qu'aucune ne reste bloquée pour toujours.

Le troisième est **ce qui se passe quand quelque chose échoue**. En file, une erreur arrête le programme à l'endroit exact où elle s'est produite, et c'est facile à comprendre. Avec beaucoup de tâches à la fois, une panne peut affecter les autres, et ce que Python te remet n'est pas une exception mais un **groupe** d'exceptions. Si tu ne le comprends pas, un seul service en panne peut faire tomber le rapport entier, ce qui est exactement le contraire de ce que le `revisor` promet.

Et sous tout cela, le quatrième problème, celui de la confiance : un programme qui fait autant de choses à la fois, avec des temps et des pannes mélangés, **ne peut pas se tester à la main** de manière répétable. Si, pour vérifier qu'« un service bloqué ne fait pas tomber le rapport », il te faut bloquer un vrai service, tu ne le vérifieras jamais deux fois de la même façon. La quatrième partie de la leçon enseigne à tester tout cela sans réseau : avec un faux serveur qui répond ce que tu dis, instantanément, toujours pareil.

## Les concepts

### 10.1 `TaskGroup` : toutes à la fois

#### 10.1.1 Ce que coûte attendre en file

Avant de réparer quelque chose, il faut le mesurer. Ce premier programme n'utilise pas le réseau : chaque « service » est une vraie attente, faite avec `asyncio.sleep`, qui est la façon de dire « ne fais rien pendant ce temps, mais laisse-moi faire autre chose entre-temps ». Les attentes sont celles de quatre services inventés, d'un dixième à une demi-seconde, pour que les exécutions soient courtes.

```python
# fig10_01.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    for nombre, espera_s in ESPERAS_S.items():
        await consultar(nombre, espera_s)
    print(f"en serie: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_01.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
en serie: 1.1 s
```

Lis `main` de haut en bas. `time.perf_counter()` est l'horloge pour mesurer des intervalles que tu as déjà utilisée dans la Leçon 9 : on l'appelle au début et à la fin, et la soustraction est le temps écoulé. Le `for` parcourt le dictionnaire avec `.items()` (qui te donne chaque paire nom-attente) et, pour chacune, fait `await consultar(...)`. Le `await` dit « attends ici que cette coroutine se termine » ; tant qu'elle n'est pas terminée, le `for` ne passe pas au tour suivant. C'est pourquoi les réponses sortent dans l'ordre où elles ont été demandées, et c'est pourquoi le total, 1.1 seconde, est la somme exacte : 0.3 plus 0.5 plus 0.1 plus 0.2.

C'est le même problème que tu as mesuré dans la Leçon 9 avec le `revisor` : `await` sur **une coroutine seule** attend qu'elle se termine avant de continuer. Ce n'est pas un défaut du `await` ; c'est ce qu'il signifie. Pour que deux attentes se produisent en même temps, il faut que les deux **existent** en même temps, et c'est à cela que sert une tâche.

#### 10.1.2 Une tâche : une coroutine déjà en marche

Une **coroutine** est une recette : `consultar("catalogo", 0.3)` ne fait rien, elle produit seulement l'objet-recette, et la recette commence à s'exécuter quand quelqu'un lui fait `await`. Une **tâche** (*task*) est une coroutine à qui on a déjà donné de la corde : la boucle d'événements l'a notée dans sa liste de choses en attente et l'exécute dès qu'elle peut, **sans que personne l'attende encore**. La **boucle d'événements** (*event loop*) est la pièce d'`asyncio` qui tient cette liste : elle prend une tâche, l'exécute jusqu'à ce qu'elle tombe sur un `await` qui doit attendre, la met en pause, prend la suivante, et ainsi de suite, dans un seul thread.

Avec cela en main, la version à la fois :

```python
# fig10_02.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    print(f"{nombre}: empieza")
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        tareas = [
            grupo.create_task(consultar(nombre, espera_s))
            for nombre, espera_s in ESPERAS_S.items()
        ]
    print(f"a la vez: {time.perf_counter() - inicio:.1f} s")
    print([tarea.result() for tarea in tareas])


asyncio.run(main())
```

```text
$ python fig10_02.py
catalogo: empieza
inventario: empieza
pagos: empieza
reportes: empieza
pagos: respondió
reportes: respondió
catalogo: respondió
inventario: respondió
a la vez: 0.5 s
['catalogo', 'inventario', 'pagos', 'reportes']
```

Une seule chose a changé : au lieu de `await consultar(...)` dans le `for`, on fait `grupo.create_task(consultar(...))`. Cela **n'attend pas** : cela enregistre la tâche et revient aussitôt, avec un objet `Task` en main. C'est pourquoi le `for` (ici, à l'intérieur d'une liste en compréhension, qui est le `for` sur une ligne de la Leçon 4) passe sur les quatre services en un instant et laisse quatre tâches en attente. Regarde la sortie : les quatre « empieza » sortent d'abord, à la suite, avant qu'aucun ne réponde. Ensuite ils répondent par ordre de **rapidité**, pas de requête : `pagos` (0.1 s), `reportes` (0.2 s), `catalogo` (0.3 s), `inventario` (0.5 s). Et le total n'est plus 1.1 mais 0.5 : celui du plus lent.

Et le `async with asyncio.TaskGroup() as grupo:` ? C'est ce qui rend cela sûr. Il fonctionne comme le `with` de la Leçon 6 : en **sortant** du bloc, le groupe **attend que toutes les tâches qu'il a créées se terminent**. C'est pourquoi la ligne `print(f"a la vez: ...")`, qui est après le bloc, ne s'exécute que lorsque les quatre ont répondu. Tu peux créer les tâches où tu veux dans le bloc ; tu ne peux en oublier aucune, parce que le bloc ne te laisse pas sortir tant qu'il y en a une vivante. C'est ce que la [documentation d'`asyncio`](https://docs.python.org/3/library/asyncio-task.html#task-groups) appelle la *concurrence structurée* : les tâches naissent et meurent à l'intérieur d'un bloc indenté, comme un `with` ferme son fichier.

#### 10.1.3 Les résultats et leur ordre

`create_task` renvoie la tâche, et la tâche garde son résultat. Après le bloc, `tarea.result()` te le remet : si la tâche s'est bien terminée, la valeur que sa fonction a renvoyée ; si elle a échoué, il lance de nouveau l'exception. Remarque le détail qui importe pour le `revisor` : nous gardons les tâches **dans une liste, dans l'ordre des services**, puis nous sortons les résultats **en parcourant cette liste**. Les réponses sont arrivées en désordre (pagos en premier), mais la dernière ligne de la sortie, `['catalogo', 'inventario', 'pagos', 'reportes']`, est dans l'ordre de la configuration. Cet ordre n'est pas un luxe : un rapport où les lignes changent de place à chaque exécution est illisible, et un JSON qu'on compare à celui d'hier doit être dans le même ordre. La règle est simple : **l'ordre dans lequel arrivent les réponses, c'est le réseau qui le décide ; l'ordre dans lequel elles s'affichent, c'est toi qui le décides**, et cela se décide en gardant les tâches dans une liste et non en empilant les résultats au fur et à mesure qu'ils se terminent.

#### 10.1.4 Une tâche ne cède la main que sur un `await`

Il manque une pièce pour que le modèle mental soit complet, et c'est celle qui produit le plus d'erreurs. La boucle d'événements tourne **dans un seul thread**. Quand elle exécute une tâche, cette tâche a le thread entier jusqu'à ce qu'elle le lâche elle-même, et elle ne le lâche que sur un `await` qui doit attendre. Entre deux `await`, personne d'autre ne tourne. Cela s'appelle la concurrence **coopérative** : les tâches coopèrent en cédant la main. Si une tâche ne coopère pas, elle bloque toutes les autres. Regarde ce qui se passe si, au lieu de `await asyncio.sleep(...)`, on utilise le `time.sleep(...)` de toujours, qui est une attente qui **ne cède rien** :

```python
# fig10_03.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    time.sleep(espera_s)  # noqa: ASYNC251
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for nombre, espera_s in ESPERAS_S.items():
            grupo.create_task(consultar(nombre, espera_s))
    print(f"TaskGroup con time.sleep: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_03.py
catalogo: respondió
inventario: respondió
pagos: respondió
reportes: respondió
TaskGroup con time.sleep: 1.1 s
```

C'est le même `TaskGroup` que dans la figure précédente, avec les quatre tâches créées de la même façon. Mais le résultat est autre : elles s'affichent dans l'ordre où elles ont été créées, pas dans celui de rapidité, et le total est de 1.1 seconde, la somme. Pourquoi ? Parce que la première tâche est arrivée à `time.sleep(0.3)`, et `time.sleep` arrête **le thread**, et avec le thread arrêté la boucle d'événements ne peut même pas passer à la tâche suivante. Les trois autres ont attendu leur tour, en file, bien qu'elles soient dans un `TaskGroup`. Cette erreur est particulièrement traîtresse parce que **le programme n'échoue pas** : il donne le bon résultat, seulement aussi lentement que s'il n'y avait pas de concurrence. Le commentaire `# noqa: ASYNC251` est là parce que `ruff` (l'outil de la Leçon 8) connaît cette erreur et la signale, mais pas avec l'ensemble de règles du `revisor` : `ASYNC251` fait partie de la collection `ASYNC`, celle des erreurs d'`asyncio`, qui n'est pas dans le `select` du projet (`E`, `F`, `I`, `B`, `UP`). Si tu la demandes, `ruff check --select ASYNC` sur cette figure sans ce commentaire dit ``ASYNC251 Async functions should not call `time.sleep` ``. Et si ton code utilise `asyncio` sérieusement, c'est une bonne candidate pour entrer dans ton `select`. Dans cette figure, nous le laissons exprès pour montrer le dégât ; dans ton vrai code, l'avertissement de `ruff` est une piste à suivre.

La règle pratique : à l'intérieur d'une coroutine, tout ce qui attend (réseau, disque lent, temps) doit être un `await` sur quelque chose fait pour `asyncio` : `asyncio.sleep`, `httpx.AsyncClient`. Un appel normal qui prend du temps (un `time.sleep`, un long calcul, une fonction de `requests`) ne coopère pas et emporte toute la boucle avec lui. C'est la raison pour laquelle le cours utilise `httpx` et non `requests` : `httpx` sait attendre sans bloquer. Le chapitre de la documentation sur [comment développer avec `asyncio`](https://docs.python.org/3/library/asyncio-dev.html) apporte le mode de débogage, qui prévient quand une tâche retient le thread trop longtemps.

### 10.2 Limites : un plafond de temps et un maximum de simultanées

#### 10.2.1 `asyncio.timeout()` : le plafond d'une opération entière

Depuis la Leçon 9, tu sais que toute requête doit porter un délai d'attente : sans lui, un service bloqué fait attendre le `revisor` pour toujours. `httpx` en a déjà un, celui que tu lui passes avec `httpx.Timeout(...)`. Alors pourquoi un autre ?

Parce que les délais d'attente d'`httpx` mesurent des **phases**, pas le total. Selon [sa documentation](https://www.python-httpx.org/advanced/timeouts/), `httpx` en distingue quatre : celui de **connexion** (combien attendre pour ouvrir le canal), celui de **lecture** (combien attendre le morceau de données suivant), celui d'**écriture** et celui d'**attente d'un canal libre dans l'ensemble des connexions**. `httpx.Timeout(5.0)` met ces quatre à 5 secondes, chacun de son côté. Un serveur qui envoie un octet toutes les quatre secondes ne déclenche jamais celui de lecture —chaque morceau arrive à temps—, et la réponse peut prendre des minutes. `httpx` n'a rien fait de mal : chaque phase a respecté sa limite. Ce qui manque, c'est une limite sur l'**ensemble**. C'est `asyncio.timeout()`, qui existe depuis Python 3.11 et se trouve dans la [documentation d'`asyncio`](https://docs.python.org/3/library/asyncio-task.html#timeouts) :

```python
# fig10_04.py
import asyncio
import time


async def servicio_colgado() -> None:
    await asyncio.sleep(10)


async def main() -> None:
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(1):
            await servicio_colgado()
    except TimeoutError:
        print(f"tiempo agotado tras {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_04.py
tiempo agotado tras 1.0 s
```

Le bloc `async with asyncio.timeout(1):` met une horloge de 1 seconde à tout ce qui se passe dedans. Dedans, il y a une attente de 10 secondes. Quand la seconde est écoulée, `asyncio` **annule** ce qui attend dans le bloc et, en sortant, lance `TimeoutError` (une exception normale de Python, depuis la 3.11 ; avant, elle s'appelait `asyncio.TimeoutError`, qui n'est plus aujourd'hui qu'un autre nom pour la même). Le `except TimeoutError` l'attrape, et le programme affiche le temps qu'il a vraiment attendu : 1.0 seconde, pas 10. Retiens les deux effets du bloc : il **coupe** l'attente (les tâches ne restent pas bloquées) et il **prévient** avec une exception dont tu décides comment la traiter.

Les deux mécanismes ne se gênent pas ; ils se complètent. Dans le `revisor` d'aujourd'hui, ils cohabitent : `httpx.Timeout` met la limite à chaque phase, et `asyncio.timeout` celle du service complet. Les deux utilisent le `timeout_ms` du service, et celui des deux qui est atteint le premier produit le même résultat : « tiempo agotado ». Plus loin, en 10.4, tu verras l'un des avantages d'avoir les deux : le plafond d'`asyncio` fonctionne même quand `httpx` ne participe pas.

#### 10.2.2 `asyncio.Semaphore` : combien à la fois, au maximum

Un **sémaphore** (*semaphore*) est un compteur de permis. Il se crée avec un nombre, `asyncio.Semaphore(2)` : il y a deux permis. Qui veut entrer fait `async with semaforo:` ; s'il reste un permis, il le prend et entre, et sinon il **attend** qu'un autre le rende en sortant. C'est l'entrée d'un parking de deux places : quand il est plein, la voiture suivante attend dans la rue jusqu'à ce qu'une sorte. La [documentation](https://docs.python.org/3/library/asyncio-sync.html#semaphore) le décrit en ces termes. Voyons six services d'une demi-seconde avec de la place pour deux à la fois :

```python
# fig10_05.py
import asyncio
import time


async def consultar(semaforo: asyncio.Semaphore, numero: int) -> None:
    async with semaforo:
        print(f"servicio {numero}: entra")
        await asyncio.sleep(0.5)
        print(f"servicio {numero}: sale")


async def main() -> None:
    semaforo = asyncio.Semaphore(2)
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for numero in range(1, 7):
            grupo.create_task(consultar(semaforo, numero))
    print(f"seis servicios, de dos en dos: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
```

```text
$ python fig10_05.py
servicio 1: entra
servicio 2: entra
servicio 1: sale
servicio 2: sale
servicio 3: entra
servicio 4: entra
servicio 3: sale
servicio 4: sale
servicio 5: entra
servicio 6: entra
servicio 5: sale
servicio 6: sale
seis servicios, de dos en dos: 1.5 s
```

Lis la sortie par groupes de quatre lignes. Le 1 et le 2 entrent ; ils sortent une demi-seconde plus tard ; c'est seulement alors qu'entrent le 3 et le 4, et ainsi de suite. Six services, deux à la fois : trois lots d'une demi-seconde, 1.5 seconde au total. Toutes les tâches ont été créées d'un coup dans le `TaskGroup`, mais quatre d'entre elles sont restées à attendre sur `async with semaforo` sans rien dépenser. Remarque aussi l'ordre : le 3 entre avant le 4, le 5 avant le 6. Dans CPython, le sémaphore sert en général dans l'ordre d'arrivée, mais la [documentation](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore) ne le promet pas (elle le promet pour `Lock`), donc ton programme ne doit pas dépendre de cet ordre. Le `revisor` n'en dépend pas : l'ordre de son rapport est donné par la liste des services, pas par l'ordre dans lequel ils ont terminé.

Combien vaut la bonne limite ? Cela dépend de **qui reçoit** les interrogations. Si ce sont tes propres services, ce qu'ils supportent ; si ce sont ceux d'un tiers, ce que permet sa documentation ; si ce sont beaucoup et que tu ne sais pas, un nombre modéré. Le `revisor` utilise **10** par défaut et laisse l'utilisateur le changer avec `--concurrencia`. Le sémaphore protège aussi ta propre machine : chaque connexion ouverte dépense un descripteur de fichier, et chaque système d'exploitation a un plafond. Et `httpx` limite de son côté l'ensemble des connexions ouvertes (100 par défaut, comme le dit [sa documentation sur les limites](https://www.python-httpx.org/advanced/resource-limits/)), donc une limite supérieure à celle-là ne ferait qu'amener les interrogations à attendre dans une autre file.

#### 10.2.3 L'apporter dans le `revisor`

Tout le changement de cette moitié tient dans trois fichiers et un nouveau fichier de données. D'abord la version du paquet, `0.9.0` (la dépendance à `httpx` existait déjà depuis la 9) :

```toml fig10_08/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.9.0"
description = "Revisa el estado de una lista de servicios"
requires-python = ">=3.12"
dependencies = ["httpx>=0.28"]

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

Ensuite le cœur, `revision.py`. Lis-le en trois temps :

```python
# fig10_08/src/revisor/revision.py
import asyncio
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(servicio.timeout_ms / 1000):
            respuesta = await cliente.get(servicio.url, timeout=limite)
    except (httpx.TimeoutException, TimeoutError):
        return Resultado(servicio, Estado.CAIDO, None, "tiempo agotado")
    except httpx.ConnectError:
        return Resultado(servicio, Estado.CAIDO, None, "sin conexión")
    except httpx.HTTPError:
        return Resultado(servicio, Estado.CAIDO, None, "error de red")
    except (httpx.InvalidURL, ValueError):
        return Resultado(servicio, Estado.CAIDO, None, "dirección inválida")
    tiempo_ms = round((time.perf_counter() - inicio) * 1000)
    estado = clasificar(respuesta.status_code, tiempo_ms)
    return Resultado(servicio, estado, tiempo_ms, str(respuesta.status_code))


async def _revisar_con_limite(
    semaforo: asyncio.Semaphore, cliente: httpx.AsyncClient, servicio: Servicio
) -> Resultado:
    async with semaforo:
        return await revisar(cliente, servicio)


async def revisar_todos(
    servicios: list[Servicio],
    limite: int = 10,
    transporte: httpx.AsyncBaseTransport | None = None,
) -> list[Resultado]:
    if limite < 1:
        raise ValueError("el límite debe ser al menos 1")
    semaforo = asyncio.Semaphore(limite)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        async with asyncio.TaskGroup() as grupo:
            tareas = [
                grupo.create_task(_revisar_con_limite(semaforo, cliente, servicio))
                for servicio in servicios
            ]
    return [tarea.result() for tarea in tareas]
```

**Premièrement, `revisar`** (une seule interrogation). Elle a très peu changé par rapport à la Leçon 9 : le `await cliente.get(...)` vit maintenant à l'intérieur de `async with asyncio.timeout(servicio.timeout_ms / 1000):`. La division par mille vient de ce que `timeout_ms` est en millisecondes et qu'`asyncio.timeout` veut des secondes. Dans le `except`, `(httpx.TimeoutException, TimeoutError)` attrape les deux délais dépassés : celui de phase d'`httpx` et le plafond d'`asyncio`. Avec des parenthèses, parce que, en Python 3.12, un `except` à deux classes les porte dans un tuple. Le reste est pareil : chaque erreur réseau est convertie en un `Resultado` avec son détail, et la fonction ne laisse **jamais** sortir une erreur réseau. Il y a une exception que `revisar` n'attrape **pas** exprès et qui mérite un paragraphe : `asyncio.CancelledError`. C'est la façon dont `asyncio` prévient une tâche « on t'a annulée ». Si tu l'attrapais, tu avalerais l'ordre d'annuler et le `TaskGroup` ou le `timeout` ne pourraient plus faire leur travail. C'est pourquoi le `except` nomme des classes précises et n'est jamais un `except Exception` large : la règle de la Leçon 6 (pas de `except:` nu) a maintenant une raison de plus.

**Deuxièmement, `_revisar_con_limite`** : trois lignes qui prennent un permis du sémaphore et vérifient. Elle est **hors** de `revisar` pour une raison de mesure. Si le sémaphore était dedans, l'horloge de `revisar` commencerait à tourner avant d'obtenir le permis, et un service qui aurait attendu son tour une demi-seconde apparaîtrait comme « lent » sans l'être. Avec le permis dehors, le temps que `revisar` mesure est celui de l'interrogation, et l'attente dans la file du sémaphore n'est pas comptée. Il en va de même pour le plafond d'`asyncio.timeout` : il commence à compter quand l'interrogation commence, pas quand la tâche a été créée.

**Troisièmement, `revisar_todos`**. Sa signature a changé : elle reçoit maintenant `limite` (par défaut 10) et `transporte`, que tu peux ignorer pour l'instant (il existe pour 10.4 : c'est la porte par laquelle les tests font entrer un faux serveur). Ligne par ligne : si `limite` est inférieur à 1, elle lance `ValueError`, parce que `Semaphore(0)` n'explose pas : il laisse tout le monde à attendre un permis qui n'arrive jamais, et le programme reste bloqué sans rien dire. On crée le sémaphore. On ouvre **un seul** `httpx.AsyncClient` pour toutes les interrogations, parce qu'un client maintient un ensemble de connexions réutilisables et qu'ouvrir vingt clients serait du gaspillage. On ouvre le `TaskGroup`, et la compréhension crée une tâche par service, **dans l'ordre de la liste**. En sortant du bloc, toutes ont terminé. La dernière ligne, hors des `async with`, monte la liste des résultats en parcourant les tâches dans ce même ordre : ainsi le rapport respecte la configuration quel que soit celui qui a répondu le premier.

Il reste à ce que l'utilisateur puisse choisir la limite. Dans `cli.py` :

```python
# fig10_08/src/revisor/cli.py
import argparse
import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import encabezado, linea, reporte_a_json, resumen
from revisor.modelo import Estado
from revisor.revision import revisar_todos


def entero_positivo(texto: str) -> int:
    try:
        numero = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{texto!r} no es un entero") from None
    if numero < 1:
        raise argparse.ArgumentTypeError("debe ser al menos 1")
    return numero


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
        "--concurrencia",
        type=entero_positivo,
        default=10,
        help="cuántos servicios se consultan a la vez (por omisión: 10)",
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

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
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

Il y a deux choses nouvelles. `entero_positivo` est une fonction qu'`argparse` utilise pour convertir et valider le texte que l'utilisateur a écrit après `--concurrencia` : si ce n'est pas un entier, ou s'il est inférieur à 1, elle lance `argparse.ArgumentTypeError`, et `argparse` la convertit en son erreur d'usage avec le code de sortie **2**, le même code que tu utilisais déjà pour « l'usage est invalide ». Deux détails d'écriture dans cette fonction. `{texto!r}` dans la f-string demande la *représentation* de la valeur au lieu du texte tel quel : un texte sort avec ses guillemets (`'diez'`), et ainsi le message laisse voir exactement ce qu'a écrit l'utilisateur, même si c'étaient des espaces. Et `raise ... from None` est le `raise ... from` de la Leçon 6 avec l'intention contraire : au lieu de conserver l'erreur d'origine comme cause, il la **cache**, parce que le `ValueError` de `int` ne dit rien à qui a écrit `--concurrencia diez` et que le nouveau message dit déjà tout. Enfin, dans `main`, l'appel est devenu `revisar_todos(servicios, limite=argumentos.concurrencia)`.

Pour mesurer avec quelque chose de plus intéressant que quatre services, il y a un fichier avec vingt, tous pointant vers le chemin `/espera/500` du laboratoire (chacun répond après une demi-seconde) :

```toml fig10_08/servicios-20.toml
[[servicios]]
nombre = "servicio01"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio02"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio03"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio04"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio05"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio06"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio07"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio08"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio09"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio10"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio11"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio12"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio13"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio14"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio15"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio16"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio17"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio18"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio19"
url = "http://127.0.0.1:8099/espera/500"

[[servicios]]
nombre = "servicio20"
url = "http://127.0.0.1:8099/espera/500"
```

Avec le laboratoire qui tourne dans un autre terminal (`python laboratorio.py`, comme dans la Leçon 9), mesure trois fois la même exécution. `time` est une commande du terminal qui exécute ce qui la suit et, à la fin, dit combien de temps cela a pris ; la ligne `real` est le temps de l'horloge murale. Avec `| tail -n 1`, on ne garde que la dernière ligne du rapport, le récapitulatif, pour ne pas voir vingt lignes :

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 507ms

real	0m10.263s
user	0m0.154s
sys	0m0.029s

$ time python -m revisor --config servicios-20.toml --concurrencia 10 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m1.146s
user	0m0.115s
sys	0m0.024s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 514ms

real	0m0.627s
user	0m0.104s
sys	0m0.019s
```

Les nombres racontent l'histoire. Avec `--concurrencia 1` (un permis, c'est-à-dire en file), cela prend **10.3 secondes** : vingt attentes d'une demi-seconde. Avec 10, cela prend **1.15** : vingt services, dix à la fois, font deux lots d'une demi-seconde. Avec 20, cela prend **0.63** : un seul lot. Pourquoi 10 donne-t-il le double de 20 et non quelque chose d'intermédiaire ? Parce qu'avec la limite 10, les dix premiers occupent les permis pendant une demi-seconde, et les dix autres **ne peuvent pas commencer** avant qu'un permis ne se libère : deux lots à la suite. Avec la limite 20, tous tiennent d'un coup. Et pourquoi 0.63 et pas 0.5 ? Parce que l'horloge de `time` inclut ce qui n'est pas de l'attente réseau : démarrer Python, importer `httpx`, ouvrir les connexions. Cela fait entre 0.1 et 0.15 seconde qui ne dépendent pas du nombre de services. Si ta machine est plus lente, les tiens seront un peu plus grands ; c'est la **proportion** entre les trois exécutions qui compte.

Avec cela se termine la première session. Ce que tu as, c'est un `revisor` qui interroge plusieurs services à la fois et n'abuse pas. Ce qui lui manque, c'est de résister aux pannes et, surtout, de **démontrer** qu'il y résiste.

### 10.3 Groupes d'exceptions : une panne ne fait pas tomber le rapport

#### 10.3.1 Ce qui se passe quand une tâche échoue

Jusqu'ici, tout s'est bien passé. Le `TaskGroup` a une règle pour quand ça ne se passe pas bien, et il convient de la voir de ses yeux avant de la lire : si **une** des tâches se termine par une exception, le groupe **annule les autres**. Regarde ce qui arrive à un rapport avec trois tâches, dont l'une se casse :

```python
# fig10_06.py
import asyncio


async def consulta_buena(nombre: str, espera_s: float) -> None:
    try:
        await asyncio.sleep(espera_s)
        print(f"{nombre}: terminó")
    except asyncio.CancelledError:
        print(f"{nombre}: cancelada")
        raise


async def consulta_rota(nombre: str) -> None:
    await asyncio.sleep(0.1)
    raise ConnectionError(f"{nombre}: sin conexión")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as grupo:
            grupo.create_task(consulta_buena("catalogo", 0.05))
            grupo.create_task(consulta_rota("reportes"))
            grupo.create_task(consulta_buena("inventario", 0.5))
    except* ConnectionError as grupo_de_errores:
        for error in grupo_de_errores.exceptions:
            print(f"falló: {error}")
    print("fin")


asyncio.run(main())
```

```text
$ python fig10_06.py
catalogo: terminó
inventario: cancelada
falló: reportes: sin conexión
fin
```

Il y a trois tâches dans le groupe. `catalogo` attend 0.05 seconde et se termine bien. `reportes` attend 0.1 et lance `ConnectionError` (l'exception de Python pour une connexion qui n'a pas pu se faire ; c'est le cousin du `httpx.ConnectError` qu'utilise le `revisor`). `inventario` attend 0.5 seconde. Regarde la sortie : `catalogo` a terminé, `inventario` a été **annulée** (elle n'a jamais dit « terminó » ; la demi-seconde qui lui restait a été perdue), et l'exception de `reportes` est sortie par le `except*`.

Dans le code, il y a deux formes nouvelles. La première est dans `consulta_buena` : le `except asyncio.CancelledError:` affiche « cancelada » puis fait un `raise` tout court. Un `raise` sans rien d'autre **relance l'exception qui est en cours de traitement** ; c'est nécessaire parce que, comme tu l'as vu en 10.2.3, avaler une annulation abîme le mécanisme. La seconde est `except*`, qui mérite sa propre section.

#### 10.3.2 `ExceptionGroup` et `except*`

Quand plusieurs tâches d'un groupe échouent en même temps, Python ne peut pas lancer une seule exception : il y en aurait plusieurs à la fois. C'est pourquoi existe depuis la 3.11 `ExceptionGroup` ([PEP 654](https://peps.python.org/pep-0654/)) : une exception qui **contient d'autres exceptions**, dans son attribut `.exceptions`, qui est un tuple (la collection qui ne change pas, de la Leçon 4). Un `TaskGroup` qui a subi des pannes les emballe dans un seul en sortant du bloc, même si une seule a échoué.

Un `except` normal attrape par la classe de l'exception qui arrive ; comme ce qui arrive est un `ExceptionGroup`, un `except ConnectionError` ne la reconnaîtrait pas. Pour cela on a créé `except*` (avec astérisque), qui **ouvre le groupe** : `except* ConnectionError as grupo_de_errores` attrape les exceptions du groupe qui sont des `ConnectionError`, les rassemble dans un nouveau groupe et le laisse dans la variable. C'est pourquoi le `for error in grupo_de_errores.exceptions:` parcourt ce tuple, et non une seule erreur. S'il y avait dans le groupe des exceptions d'autres classes qu'aucun `except*` n'a attrapées, elles continuent leur chemin vers le haut. Un même `try` peut avoir plusieurs `except*`, chacun pour sa classe, et chacun reçoit ce qui est à lui. Ce que tu **ne** peux **pas** faire, c'est mélanger `except` et `except*` dans le même `try`. La [documentation du langage](https://docs.python.org/3/reference/compound_stmts.html#except-star) a toutes les règles ; pour le `revisor`, ce que tu vois suffit.

Remarque ce qu'a gagné et perdu le programme. Il a gagné en propreté : aucune tâche n'est restée orpheline, le groupe a attendu que les annulées finissent de s'annuler, et l'erreur est arrivée en ordre. Il a perdu le rapport : `inventario` était saine et son résultat a été jeté. Dans un `revisor`, c'est inacceptable, parce que sa raison d'être est de te dire l'état de **tous**.

#### 10.3.3 Une panne réseau est un résultat, pas une exception

La solution du `revisor`, tu l'as déjà écrite, et maintenant tu peux comprendre pourquoi elle est comme elle est. `revisar` **attrape** les erreurs réseau à l'intérieur de la tâche elle-même et les convertit en un `Resultado` (`CAIDO`, avec son détail). Du point de vue du `TaskGroup`, la tâche s'est bien terminée : elle a renvoyé une valeur. Personne ne lance rien vers le haut, personne n'annule personne, et le rapport sort complet avec la ligne de `reportes` disant « sin conexión ». C'est le principe de la leçon : **une panne attendue est une donnée, pas un incident**. Un service en panne n'est pas une surprise pour un `revisor` ; ça fait partie de son travail.

Et toutes les erreurs se convertissent-elles en données ? Non, et la différence est ce qu'il y a de plus précieux dans cette section. `revisar` attrape des **classes précises d'`httpx`** : les erreurs que le monde extérieur peut causer. Il n'attrape pas un `ZeroDivisionError`, un `KeyError` ou un `TypeError` : ce sont des erreurs **du programme**, et les cacher comme si c'étaient « un service en panne » serait mentir. Si un service apparaît en panne parce que ton code a une erreur, tu passeras un après-midi à chercher le problème dans le réseau. Avec la conception d'aujourd'hui, une erreur de programmation fait ce qu'elle doit : elle arrête le rapport, bruyamment, avec un rapport qui pointe vers la ligne. Cette sortie bruyante est ce que tu vois dans la section « L'erreur que tu vas voir » plus bas, et c'est une bonne nouvelle, pas une mauvaise.

### 10.4 Tests sans réseau

#### 10.4.1 Pourquoi on ne teste pas contre le réseau

Pour vérifier le paragraphe précédent (« un service en panne ne fait pas tomber le rapport »), il faut des services en panne, lents, qui renvoient 503 et qui se déconnectent, et ces quatre choses **à la fois**. Les tests contre le vrai réseau ont trois problèmes. Ils sont **lents** : un test de délai d'attente de 5 secondes fait attendre 5 secondes celui qui lance la suite. Ils sont **fragiles** : ils échouent parce que le wifi est tombé, pas parce que ton code est faux, et un rouge qui ne signifie rien fait que les gens cessent de regarder les rouges. Et ils sont **impossibles à répéter** : tu ne peux pas demander à un vrai service de tomber juste maintenant. C'est pourquoi la règle est qu'**un test unitaire ne sort jamais vers le réseau**. Le réseau est remplacé par une doublure : quelque chose qui a la même forme que le réel, mais qui répond ce que le test lui dit.

L'entrée du [blog de Hábil sur les tests qui attrapent les erreurs](https://www.habil.mx/fr/blog/tests-qui-attrapent-erreurs-couverture-quality-gate/) raconte pourquoi un test qu'on peut mettre au rouge à volonté vaut plus que dix qui sont toujours au vert ; et celle qui traite des [styles d'intégration en ligne, file et événement](https://www.habil.mx/fr/blog/styles-integration-en-ligne-file-attente-evenement/) montre le même problème du côté de l'architecture : séparer celui qui demande de celui qui répond. Ici, tu les sépares avec une pièce d'`httpx`.

#### 10.4.2 `httpx.MockTransport` : un faux serveur

Un client HTTP a deux moitiés : celle qui monte la requête et comprend la réponse, et le **transport**, qui est celle qui touche vraiment le réseau. `httpx` te laisse changer le transport, et en fournit un fait pour les tests, [`httpx.MockTransport`](https://www.python-httpx.org/advanced/transports/#mock-transports) : il reçoit une fonction qui, étant donné la requête, **renvoie la réponse** que tu veux. Rien ne sort de ton ordinateur.

```python
# fig10_07.py
import asyncio

import httpx


def atender(peticion: httpx.Request) -> httpx.Response:
    print(f"el servidor de mentira recibió: GET {peticion.url}")
    return httpx.Response(200, text="todo bien")


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    async with httpx.AsyncClient(transport=transporte) as cliente:
        respuesta = await cliente.get("https://catalogo.example/estado")
        print(respuesta.status_code, respuesta.text)


asyncio.run(main())
```

```text
$ python fig10_07.py
el servidor de mentira recibió: GET https://catalogo.example/estado
200 todo bien
```

`atender` est la fonction fausse : elle reçoit un `httpx.Request` (la requête, avec son adresse dans `.url`), affiche ce qui lui est arrivé et renvoie une `httpx.Response` avec le code 200 et le texte « todo bien ». `httpx.MockTransport(atender)` l'enveloppe comme transport, et `httpx.AsyncClient(transport=transporte)` monte un client qui, au lieu d'ouvrir une connexion, l'appelle. Le client fait `get("https://catalogo.example/estado")`, une adresse qui n'existe pas (`.example` est un domaine réservé qui ne se résout jamais), et pourtant il répond, parce qu'il n'est jamais allé la chercher. C'est ce que `revisar_todos` offre avec son paramètre `transporte` : elle reçoit le transport et le passe à `httpx.AsyncClient(transport=transporte)`. Quand il vaut `None` (le cas normal), `httpx` utilise le vrai.

Un faux transport peut faire plus que répondre 200 : il peut renvoyer un 503 (`httpx.Response(503)`), ou **lancer** une exception réseau comme si le câble avait été coupé (`raise httpx.ConnectError(...)`), ou même attendre, si la fonction est `async def`. Avec ces quatre choses, on simule tout ce que le `revisor` doit tolérer.

#### 10.4.3 Les six tests de `revisar`

Un nouveau fichier, `tests/test_revision.py`. Avant le code, le plan : les tests parlent d'un faux serveur qui se comporte selon le **nom de l'hôte** (la partie de l'adresse entre `https://` et la première barre oblique). `facturacion.example` répond 503 ; `reportes.example` lance `ConnectError` ; `notificaciones.example` lance `ReadTimeout` (l'exception d'`httpx` pour « le délai de lecture s'est écoulé ») ; tout autre répond 200.

```python
# fig10_08/tests/test_revision.py
import asyncio

import httpx

from revisor.modelo import Estado, Resultado, Servicio
from revisor.revision import revisar, revisar_todos

CATALOGO = Servicio("catalogo", "https://catalogo.example")
PAGOS = Servicio("pagos", "https://pagos.example")
FACTURACION = Servicio("facturacion", "https://facturacion.example")
REPORTES = Servicio("reportes", "https://reportes.example")
NOTIFICACIONES = Servicio("notificaciones", "https://notificaciones.example", 1000)


def atender(peticion: httpx.Request) -> httpx.Response:
    """Un servidor de mentira: contesta según el nombre del anfitrión."""
    anfitrion = peticion.url.host
    if anfitrion == "facturacion.example":
        return httpx.Response(503)
    if anfitrion == "reportes.example":
        raise httpx.ConnectError("sin ruta", request=peticion)
    if anfitrion == "notificaciones.example":
        raise httpx.ReadTimeout("muy lento", request=peticion)
    return httpx.Response(200)


async def revisar_uno(servicio: Servicio) -> Resultado:
    async with httpx.AsyncClient(transport=httpx.MockTransport(atender)) as cliente:
        return await revisar(cliente, servicio)


def test_200_rapido_es_arriba() -> None:
    resultado = asyncio.run(revisar_uno(CATALOGO))
    assert resultado.estado is Estado.ARRIBA
    assert resultado.detalle == "200"


def test_503_es_caido_con_el_codigo() -> None:
    resultado = asyncio.run(revisar_uno(FACTURACION))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "503"


def test_sin_conexion_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(REPORTES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "sin conexión"


def test_tiempo_agotado_es_caido() -> None:
    resultado = asyncio.run(revisar_uno(NOTIFICACIONES))
    assert resultado.estado is Estado.CAIDO
    assert resultado.detalle == "tiempo agotado"


def test_la_mezcla_sale_completa_y_en_orden() -> None:
    servicios = [CATALOGO, FACTURACION, REPORTES, NOTIFICACIONES]
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos(servicios, transporte=transporte))
    assert [r.servicio.nombre for r in resultados] == [
        "catalogo",
        "facturacion",
        "reportes",
        "notificaciones",
    ]
    assert [r.detalle for r in resultados] == [
        "200",
        "503",
        "sin conexión",
        "tiempo agotado",
    ]


def test_una_direccion_invalida_no_tumba_a_los_demas() -> None:
    mala = Servicio("mala", "http://999.1.1.1:8099/pagos")
    transporte = httpx.MockTransport(atender)
    resultados = asyncio.run(revisar_todos([mala, CATALOGO], transporte=transporte))
    assert [r.detalle for r in resultados] == ["dirección inválida", "200"]
```

Chaque test est une fonction normale (pas `async`) : elle monte ce dont elle a besoin et appelle `asyncio.run(...)`, comme le fait `main`. Ainsi aucun plugin de `pytest` n'est nécessaire pour faire tourner des coroutines, et le cours reste avec ce que tu connais déjà. `revisar_uno` est un auxiliaire qui ouvre un client avec le faux transport et vérifie un seul service. Les quatre premiers tests parcourent les quatre dénouements de `revisar` : 200 rapide est `ARRIBA` ; 503 est `CAIDO` et le détail est le code, `"503"` ; un `ConnectError` est `CAIDO` avec « sin conexión » ; un `ReadTimeout` est `CAIDO` avec « tiempo agotado ». Le cinquième, `test_la_mezcla_sale_completa_y_en_orden`, est celui qui démontre la promesse de la leçon : il passe à `revisar_todos` quatre services, un de chaque type, et vérifie que **les quatre sont revenus, dans l'ordre de la configuration, chacun avec son détail**. Si une panne faisait tomber le rapport, ce test passerait au rouge. Et le sixième, `test_una_direccion_invalida_no_tumba_a_los_demas`, veille sur le quatrième `except` de la Leçon 9 : il réunit un service avec l'adresse impossible `http://999.1.1.1:8099/pagos` et un sain, et exige que le premier sorte avec « dirección inválida » et le second avec son `200`. Sans ce `except`, l'`httpx.InvalidURL` s'échapperait de sa tâche, le `TaskGroup` annulerait le reste et le test échouerait avec un groupe d'exceptions (10.3).

(Une chose que `LENTO` n'a pas ici : il n'y a pas de test de cet état, parce que simuler qu'il s'est écoulé plus d'une seconde avec un faux transport distrait. Le seuil de lenteur est déjà testé là où il vit, dans `clasificar`, avec ses sept cas de la Leçon 8.)

#### 10.4.4 La voir au rouge avant d'y croire

Un test que tu n'as jamais vu échouer ne démontre rien : peut-être réussirait-il pareil avec le code cassé. On le vérifie donc. Dans une copie du projet, on supprime la branche `except httpx.ConnectError` de `revisar`, de sorte qu'un `ConnectError` tombe dans la branche générale et dise « error de red ». On lance :

```text
$ pytest -q --tb=short
.......................F.F.                                              [100%]
=================================== FAILURES ===================================
__________________________ test_sin_conexion_es_caido __________________________
tests/test_revision.py:48: in test_sin_conexion_es_caido
    assert resultado.detalle == "sin conexión"
E   AssertionError: assert 'error de red' == 'sin conexión'
E     
E     - sin conexión
E     + error de red
___________________ test_la_mezcla_sale_completa_y_en_orden ____________________
tests/test_revision.py:67: in test_la_mezcla_sale_completa_y_en_orden
    assert [r.detalle for r in resultados] == [
E   AssertionError: assert ['200', '503'...empo agotado'] == ['200', '503'...empo agotado']
E     
E     At index 2 diff: 'error de red' != 'sin conexión'
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_revision.py::test_sin_conexion_es_caido - AssertionError: a...
FAILED tests/test_revision.py::test_la_mezcla_sale_completa_y_en_orden - Asse...
2 failed, 25 passed in 0.04s
```

**Exactement deux** tests sont passés au rouge : celui qui parle de la connexion, et celui du mélange (qui inclut ce cas). Celui qui dit `2 failed, 25 passed` te donne le rapport qui compte : ce n'est pas un vert de hasard. Répare le code et relance :

```text
$ pytest -q
...........................                                              [100%]
27 passed in 0.03s
```

`27 passed` : les 21 de la leçon précédente plus les six d'aujourd'hui. Ce nombre se lit dans le rapport, pas dans le code de sortie, parce qu'un code 0 ne te dit pas combien de tests se sont exécutés : il sort pareil avec 27 qu'avec 2 si par erreur tu as filtré le reste. (La Leçon 11 y revient avec un cas concret.)

Il y a une limite qu'il convient de dire franchement. Le test du délai dépassé fait que le faux serveur **lance** un `ReadTimeout`, c'est-à-dire qu'il teste la branche d'`httpx.TimeoutException`. Il ne teste pas le **plafond** d'`asyncio.timeout`, qui existe précisément pour le cas où `httpx` ne s'aperçoit de rien. Ce test est nécessaire, et c'est l'Exercice 2 : tu l'écris toi-même, et tu vérifieras que si l'on retire l'`asyncio.timeout`, il passe au rouge.

#### 10.4.5 `monkeypatch` et la signature que tu ne dois pas changer sans prévenir

`test_cli.py` existait déjà, avec deux tests, et il avait un détail qui saute aux yeux aujourd'hui. Ces tests appellent `main`, et `main` appelle `revisar_todos`, qui sort vers le réseau. Pour qu'il ne le fasse pas, le cours a utilisé `monkeypatch` (Leçon 8) : il change, pendant un test, un nom par un autre, et à la fin du test il le restaure. Ici il remplace `revisor.cli.revisar_todos` par une fonction fausse qui renvoie ce dont le test a besoin.

```python
# fig10_08/tests/test_cli.py
from pathlib import Path

import pytest

from revisor.cli import main
from revisor.modelo import Estado, Resultado, Servicio

CONFIGURACION = """\
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
"""


def test_con_servicios_caidos_sale_con_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_caidos(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(
        servicios: list[Servicio], limite: int = 10
    ) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Note **où** le nom est changé : `"revisor.cli.revisar_todos"`, pas `"revisor.revision.revisar_todos"`. `cli.py` a fait `from revisor.revision import revisar_todos`, donc `cli` a **sa propre copie du nom** ; si tu changeais l'original dans `revision`, `cli` continuerait d'utiliser le sien. La règle de `monkeypatch` : on change le nom à l'endroit où **il est utilisé**, pas à l'endroit où il a été défini.

Et maintenant l'important de cette version : les deux fonctions fausses, `todos_caidos` et `todos_arriba` (chacune définie à l'intérieur de son test), **acceptent `limite`**. Aujourd'hui `main` appelle `revisar_todos(servicios, limite=argumentos.concurrencia)`, et un faux qui n'accepte pas cet argument n'est pas une doublure de la vraie fonction : c'est une autre fonction, et le test se casse. Si dans la Leçon 9 ton faux était `async def todos_caidos(servicios)`, il te faut maintenant lui ajouter le paramètre. Tu le vois dans « L'erreur que tu vas voir ». C'est une leçon plus générale : **une doublure doit avoir la même signature que ce qu'elle remplace**, et quand tu changes la signature de la vraie fonction, les tests avec des doublures sont la première chose qui se casse. Ce n'est pas une corvée ; c'est le test qui fait son travail, en te prévenant que d'autres dépendaient de cette signature.

#### 10.4.6 Le projet complet

Les fichiers qui n'ont pas changé dans cette leçon sont ici pour que le dossier `fig10_08/` soit complet et que tu puisses le lancer. Ce sont les mêmes que tu apportais de la Leçon 9 :

<details>
<summary>Les fichiers qui ne changent pas dans cette leçon</summary>


```toml fig10_08/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "http://127.0.0.1:8099/catalogo"

[[servicios]]
nombre = "inventario"
url = "http://127.0.0.1:8099/inventario"

[[servicios]]
nombre = "pagos"
url = "http://127.0.0.1:8099/pagos"

[[servicios]]
nombre = "reportes"
url = "http://127.0.0.1:8098/"
```

```python
# fig10_08/laboratorio.py
"""Servidor de práctica del curso: contesta como si fuera cada servicio del revisor.

Se corre aparte (python laboratorio.py) y se deja abierto mientras practicas.
No necesitas entender cómo está escrito; lo que importa son sus rutas.
"""

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PUERTO = 8099

# ruta -> (código de la respuesta, milisegundos que tarda en contestar)
RUTAS: dict[str, tuple[int, int]] = {
    "/catalogo": (200, 142),
    "/inventario": (200, 2300),
    "/pagos": (200, 87),
    "/facturacion": (503, 95),
    "/notificaciones": (200, 10000),
}


class Laboratorio(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        codigo, espera_ms = self.buscar_ruta()
        time.sleep(espera_ms / 1000)
        cuerpo = b"ok" if codigo == 200 else b"error"
        try:
            self.send_response(codigo)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        except OSError:
            pass  # quien preguntó se cansó de esperar y colgó

    def buscar_ruta(self) -> tuple[int, int]:
        if self.path.startswith("/espera/"):
            texto = self.path.removeprefix("/espera/")
            if texto.isdigit():
                return 200, int(texto)
        return RUTAS.get(self.path, (404, 0))

    def log_message(self, format: str, *args: object) -> None:
        """No imprime una línea por cada petición."""


class Servidor(ThreadingHTTPServer):
    request_queue_size = 128  # conexiones que pueden esperar turno (de fábrica: 5)


def main() -> None:
    servidor = Servidor(("127.0.0.1", PUERTO), Laboratorio)
    print(f"laboratorio en http://127.0.0.1:{PUERTO} (Ctrl+C para detenerlo)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("laboratorio detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
```

```python
# fig10_08/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig10_08/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig10_08/src/revisor/modelo.py
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
# fig10_08/src/revisor/formato.py
import json

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


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": r.servicio.url,
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
# fig10_08/src/revisor/configuracion.py
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
# fig10_08/tests/test_modelo.py
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

```python
# fig10_08/tests/test_formato.py
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

```python
# fig10_08/tests/test_configuracion.py
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

</details>

Avec le laboratoire qui tourne, l'instantané du projet produit le même rapport de toujours, mais cette fois les quatre services sont interrogés à la fois, donc le total est celui du plus lent (`inventario`, 2.3 secondes) et non la somme :

```text
$ cd fig10_08
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
```

Les temps de la colonne TIEMPO varieront un peu sur ta machine ; l'ESTADO et le DETALLE non, parce que le laboratoire est fait pour que cela sorte toujours pareil. Et le code de sortie, comme dans la Leçon 7, est 1 : il y a un `LENTO` et un `CAIDO`.

**Pour comparer.** Le même problème —lancer, attendre toutes, limiter, ne pas perdre le rapport à cause d'une panne— est résolu dans le [cours de Go](https://www.habil.mx/fr/cours/go/) avec `sync.WaitGroup` et dans le [cours de TypeScript](https://www.habil.mx/fr/cours/typescript/) avec `Promise.all` et `Promise.allSettled`. L'idée est la même ; ce qui change, c'est où vit l'attente. En Go, chaque tâche est une *goroutine*, un thread léger que l'ordonnanceur de Go lui-même (et non le système d'exploitation) répartit entre les threads du processeur ; en TypeScript et en Python, c'est une tâche coopérative dans un seul thread. Comparer les trois solutions enseigne plus que d'en lire une seule.

## L'erreur que tu vas voir

### `ExceptionGroup: unhandled errors in a TaskGroup`

C'est celle qui te sortira la première fois que tu auras une erreur de programmation à l'intérieur d'une tâche. La figure 9 la provoque : une fonction qui fait la moyenne d'une liste et à qui on passe une liste **vide**, de sorte qu'elle divise par zéro.

```python
# fig10_09.py
import asyncio


async def promedio(tiempos_ms: list[int]) -> float:
    return sum(tiempos_ms) / len(tiempos_ms)


async def main() -> None:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))


asyncio.run(main())
```

Deux tâches dans le groupe : l'une fait la moyenne de deux nombres, l'autre d'une liste vide. Voici ce que dit Python (chemins raccourcis à leur nom, comme dans tout le cours ; sur ta machine ils sont complets et les lignes d'`asyncio/` peuvent différer selon la version de Python) :

```text
$ python fig10_09.py
  + Exception Group Traceback (most recent call last):
  |   File "fig10_09.py", line 15, in <module>
  |     asyncio.run(main())
  |     ~~~~~~~~~~~^^^^^^^^
  |   File "asyncio/runners.py", line 205, in run
  |     return runner.run(main)
  |            ~~~~~~~~~~^^^^^^
  |   File "asyncio/runners.py", line 128, in run
  |     return self._loop.run_until_complete(task)
  |            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  |   File "asyncio/base_events.py", line 720, in run_until_complete
  |     return future.result()
  |            ~~~~~~~~~~~~~^^
  |   File "fig10_09.py", line 10, in main
  |     async with asyncio.TaskGroup() as grupo:
  |                ~~~~~~~~~~~~~~~~~^^
  |   File "asyncio/taskgroups.py", line 72, in __aexit__
  |     return await self._aexit(et, exc)
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "asyncio/taskgroups.py", line 174, in _aexit
  |     raise BaseExceptionGroup(
  |     ...<2 lines>...
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "fig10_09.py", line 6, in promedio
    |     return sum(tiempos_ms) / len(tiempos_ms)
    |            ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~
    | ZeroDivisionError: division by zero
    +------------------------------------
```

D'abord : ce *traceback* **ne se lit pas comme ceux des leçons précédentes**, de la dernière ligne vers le haut. La dernière ligne du dessus, `+------------------------------------`, est de la décoration ; la vraie cause est **à l'intérieur de la boîte** marquée par `|`, tout au fond. Lis-le ainsi :

1. La première ligne, `+ Exception Group Traceback`, te prévient : ce qui suit est un groupe.
2. Les lignes avec `|` descendent par le chemin qu'a parcouru l'exécution : ton `asyncio.run(main())`, les étapes internes d'`asyncio` et, important, ton `main` à la ligne 10, dans le `async with asyncio.TaskGroup()`. C'est là que le groupe, en sortant, a emballé l'erreur.
3. `ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` est l'étiquette du groupe : « erreurs non traitées dans un TaskGroup, une sous-exception ». Le nombre entre parenthèses te dit combien il en contient.
4. Et **à l'intérieur de la boîte** (`+-+---------------- 1 ----------------`) se trouve la sous-exception numéro 1 avec son propre *traceback* : `promedio`, ligne 6, `ZeroDivisionError: division by zero`. **C'est la cause**, et c'est celle que tu dois corriger. La ligne de ton fichier est à la ligne où il est dit `fig10_09.py", line 6, in promedio`.

Note aussi ce qui s'est passé avec l'**autre** tâche (`promedio([142, 87])`) : il n'y avait rien à annuler. Comme elle n'a aucun `await`, elle s'est exécutée en entier, sans céder la main, et s'est terminée avec son `114.5` avant que la seconde ne commence. Si elle avait été en train d'attendre quelque chose, comme `inventario` dans `fig10_06.py`, le `TaskGroup` l'aurait annulée même si elle était saine : c'est le groupe qui fait son travail.

Que faire : corriger la cause (vérifier que la liste n'est pas vide), ne pas cacher l'erreur. Résiste à la tentation de mettre un `except*` large pour la faire taire : une erreur de programmation doit se voir.

### `TypeError: ... got an unexpected keyword argument 'limite'`

La deuxième erreur d'aujourd'hui est celle de 10.4.5. Si ton faux de `test_cli.py` date de la Leçon 9 et n'accepte pas `limite` :

```text
$ pytest -q --tb=short -x tests/test_cli.py
F
=================================== FAILURES ===================================
_____________________ test_con_servicios_caidos_sale_con_1 _____________________
tests/test_cli.py:29: in test_con_servicios_caidos_sale_con_1
    assert main(["--config", str(archivo)]) == 1
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/revisor/cli.py:64: in main
    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: test_con_servicios_caidos_sale_con_1.<locals>.todos_caidos() got an unexpected keyword argument 'limite'
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_con_servicios_caidos_sale_con_1 - TypeError: t...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 0.03s
```

Lis-le de bas en haut, comme toujours : `TypeError`, « `todos_caidos()` a reçu un argument nommé inattendu, `limite` ». (Le `test_con_servicios_caidos_sale_con_1.<locals>.` qui précède le nom veut dire que cette fonction est définie **à l'intérieur** du test.) La ligne du dessus (`src/revisor/cli.py:64`) te dit qui l'a envoyé : `main`. Et celle de plus haut, que le test a appelé `main`. La solution n'est pas dans `cli.py` : elle est dans le faux, qui doit accepter la même chose que la vraie fonction.

## Ce qui se fait de travers

**Attendre avec `time.sleep` à l'intérieur d'une coroutine.** Cela bloque le thread et défait toute la concurrence, sans donner d'erreur (10.1.4). Coût : un programme qui semble concurrent et prend le même temps qu'en file. On le détecte avec le mode de débogage d'`asyncio` et avec `ruff`, à condition d'ajouter la collection `ASYNC` à ton `select` (celle du `revisor` ne l'a pas ; 10.1.4).

**Créer des tâches avec `asyncio.create_task` et oublier de les garder.** Python ne garde qu'une référence **faible** aux tâches isolées, et une tâche que personne ne référence peut être ramassée par le ramasse-miettes en pleine exécution. La [documentation](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) le signale. Avec `TaskGroup`, cela n'arrive pas, parce que le groupe les garde. Coût : des tâches qui disparaissent sans erreur.

**Ne pas limiter la concurrence.** Un `TaskGroup` sans sémaphore avec mille services ouvre mille connexions à la fois. Coût : tu te heurtes à la limite du système d'exploitation, ou tu satures le service que tu vérifies, et le rapport échoue pour des raisons qui ne sont pas celles qu'il mesure.

**Attraper `Exception` (ou `BaseException`) dans la tâche pour qu'elle « n'échoue jamais ».** Cela avale les erreurs de programmation et, avec `BaseException`, même l'annulation. Coût : un rapport qui ment (« service en panne ») quand celui qui a échoué est ton code.

**Avaler `CancelledError`.** Un `except asyncio.CancelledError:` qui ne relance pas l'exception laisse le `TaskGroup` et `asyncio.timeout` sans moyen d'annuler. Coût : des programmes qui ne se terminent pas ou qui ne respectent pas le délai d'attente. Si tu l'attrapes pour nettoyer quelque chose, fais `raise` à la fin.

**Tester contre le vrai réseau.** Lents, fragiles, impossibles à répéter (10.4.1). Coût : des rouges auxquels personne ne croit.

**Un faux avec une autre signature.** La doublure qui n'accepte pas ce que la vraie fonction accepte est une autre fonction. Coût : des tests qui se cassent quand la signature change, ou, pire, qui continuent de passer sans rien tester parce que personne ne les a appelés avec les nouveaux arguments.

**Mesurer avec une seule exécution.** Un seul nombre ne dit rien : le démarrage de Python, le réchauffement des connexions et ce que fait ton ordinateur à cette seconde-là se mélangent. Mesure plusieurs fois et compare la **proportion**.

## Exercices

### Exercice 1 — Mesure une limite que tu n'as pas testée

Avec `servicios-20.toml` et le laboratoire qui tourne, mesure avec `--concurrencia 5` et avec `--concurrencia 4`. **Avant de lancer**, prédis les temps avec le raisonnement des lots (combien de lots d'une demi-seconde faut-il avec cette limite). Note prédiction et mesure dans ton journal de bord et explique la différence, s'il y en a une.

### Exercice 2 — Le test du plafond

Écris un test pour le plafond d'`asyncio.timeout` : un service avec `timeout_ms = 100` dont le faux serveur **attend dix secondes** avant de répondre. Le test doit passer en une fraction de seconde. Indice : la fonction qui répond peut être `async def` et utiliser `await asyncio.sleep(10)`. Ensuite, **vérifie-le au rouge** : retire l'`asyncio.timeout` de `revisar` (laisse un `if True:` à sa place), lance le test et note combien de temps il met à échouer et pourquoi.

### Exercice 3 — Un délai d'attente plus court que la réponse

Copie `servicios.toml` et ajoute `timeout_ms = 1500` au service `inventario` (qui dans le laboratoire répond après 2.3 secondes). Prédis la ligne d'`inventario`, le récapitulatif et combien de temps prendra l'exécution, et compare avec ce qui sort. Qu'est-ce qui a changé dans l'`ESTADO` d'`inventario`, et pourquoi ?

### Exercice 4 — Provoque trois erreurs et lis-les

Provoque, une par une : (a) dans `fig10_09.py`, change la liste vide en `[100]` et lance (qu'est-ce qui a disparu ?) ; puis remets-la et fais passer le `ZeroDivisionError` de la tâche par un `except*` qui l'attrape et affiche un message ; (b) lance `python -m revisor --concurrencia 0` et note le code avec `echo $?` ; (c) retire `limite` à l'un des faux de `test_cli.py` et lance `pytest`. Pour chacune, écris en une phrase ce que signifie le message.

## Solutions

### Solution 1

Avec la limite 5 et vingt services, il faut quatre lots d'une demi-seconde : 2.0 secondes plus le démarrage. Avec la limite 4, il faut cinq lots : 2.5 plus le démarrage. Une exécution de référence a donné 2.15 et 2.67 secondes : le démarrage (les 0.15 à 0.2 s qui ne sont pas de l'attente) explique la différence avec 2.0 et 2.5. La règle générale : le temps ≈ (nombre de services divisé par la limite, arrondi vers le haut) fois l'attente de chacun, plus le démarrage.

### Solution 2

Le test s'ajoute à `tests/test_revision.py` (ou à un fichier à part) :

```python
import asyncio

import httpx

from revisor.modelo import Estado, Servicio
from revisor.revision import revisar


async def colgado(peticion: httpx.Request) -> httpx.Response:
    await asyncio.sleep(10)
    return httpx.Response(200)


async def revisar_colgado() -> tuple[Estado, str]:
    servicio = Servicio("colgado", "https://colgado.example", 100)
    async with httpx.AsyncClient(transport=httpx.MockTransport(colgado)) as cliente:
        resultado = await revisar(cliente, servicio)
    return resultado.estado, resultado.detalle


def test_el_techo_corta_lo_que_httpx_no_ve() -> None:
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
```

Le faux serveur est `async def` et attend dix secondes ; le faux transport n'applique aucun délai d'attente d'`httpx` (il n'y a pas de réseau), donc le seul qui peut couper est le plafond d'`asyncio.timeout`. Avec le code complet, le test passe en une fraction de seconde :

```text
$ pytest -q tests/test_techo.py
.                                                                        [100%]
1 passed in 0.12s
```

Et avec l'`asyncio.timeout` retiré (le `if True:`), le test **échoue**, et met dix secondes à échouer, parce que personne ne coupe l'attente ; le rapport montre que `revisar` a livré `LENTO` avec `'200'` après avoir attendu dix secondes :

```text
$ pytest -q --tb=short tests/test_techo.py
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_el_techo_corta_lo_que_httpx_no_ve ____________________
tests/test_techo.py:22: in test_el_techo_corta_lo_que_httpx_no_ve
    assert asyncio.run(revisar_colgado()) == (Estado.CAIDO, "tiempo agotado")
E   AssertionError: assert (<Estado.LENT...ENTO'>, '200') == (<Estado.CAID...empo agotado')
E     
E     At index 0 diff: <Estado.LENTO: 'LENTO'> != <Estado.CAIDO: 'CAIDO'>
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_techo.py::test_el_techo_corta_lo_que_httpx_no_ve - Assertio...
1 failed in 10.04s
```

Cela démontre que le test dépend de la correction qu'il dit tester. Les six tests de `test_revision.py` n'auraient pas remarqué cette régression.

### Solution 3

`inventario` passe de `LENTO` à `CAIDO` avec le détail « tiempo agotado » : sa réponse mettait 2.3 secondes et le plafond est 1.5, donc elle est coupée avant. Le récapitulatif compte maintenant `2 caídos`, et l'exécution dure environ 1.6 seconde (le plafond de 1.5 plus le démarrage) au lieu de 2.4. Une exécution réelle :

```text
$ time python -m revisor --config servicios-corto.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  CAIDO          —  tiempo agotado
pagos       ARRIBA      95ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 0 lentos · 2 caídos · promedio 126ms

real	0m1.634s
user	0m0.110s
sys	0m0.019s
```

Deux observations. La moyenne change (126 ms dans cette exécution ; elle varie un peu à chaque fois), parce qu'`inventario` n'apporte plus de temps : un service qui n'a pas répondu n'entre pas dans la moyenne. Et l'exécution est plus courte parce que le plus lent n'est plus `inventario` mais son plafond.

### Solution 4

(a) Avec `[100]` à la place de `[]`, il n'y a plus de division par zéro, le programme se termine sans sortie et sans erreur : les deux tâches se sont achevées. Avec le `except*` :

```python
try:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))
except* ZeroDivisionError:
    print("una lista de tiempos venía vacía")
```

il attrape l'erreur et le programme affiche le message au lieu du *traceback*. (b) Il sort `revisor: error: argument --concurrencia: debe ser al menos 1` et le code est 2 : c'est une erreur d'usage, et c'est `argparse` qui la détecte avant que quoi que ce soit ne tourne. (c) `TypeError: ... todos_caidos() got an unexpected keyword argument 'limite'` : le faux n'accepte pas ce que `main` lui envoie.

## Comment savoir que j'ai réussi

- [ ] `fig10_02.py` affiche « a la vez: 0.5 s » et `fig10_01.py` affiche « en serie: 1.1 s », et tu peux dire pourquoi le premier est celui du plus lent et le second la somme.
- [ ] `fig10_03.py` affiche les réponses dans l'ordre où les tâches ont été créées, pas dans l'ordre de rapidité, et tu sais expliquer ce que fait `time.sleep` que `asyncio.sleep` ne fait pas.
- [ ] `fig10_05.py` montre les lots de deux en deux et le total de 1.5 s.
- [ ] Dans le dossier `fig10_08/`, `pytest -q` se termine avec `27 passed` et non avec un autre nombre, et il le fait avec le laboratoire éteint (c'est tout l'intérêt de tester sans réseau).
- [ ] `ruff check`, `ruff format --check` et `mypy` ne signalent rien dans ce dossier.
- [ ] Avec `servicios-20.toml`, `--concurrencia 1` prend près de 10 secondes, `--concurrencia 10` près de 1.1 et `--concurrencia 20` près de 0.6, et tu peux expliquer pourquoi 10 donne le double de 20.
- [ ] `python -m revisor --concurrencia 0` se termine avec le code 2 et un message d'usage.
- [ ] Tu as cassé exprès la branche `ConnectError` de `revisar` et vu passer au rouge exactement deux tests ; tu l'as réparée et les 27 sont revenus.
- [ ] Tu peux expliquer avec tes mots la différence entre le délai d'attente d'`httpx` et `asyncio.timeout`, pourquoi `revisar` attrape `httpx.HTTPError` et **pas** `Exception`, et pourquoi le faux de `test_cli.py` doit accepter `limite`.

## Résumé

Réponds sans regarder la leçon :

1. Quelle différence y a-t-il entre une coroutine et une tâche ? Que fait `create_task` et que fait la sortie d'un bloc `async with asyncio.TaskGroup()` ?
2. À quel moment exact la boucle d'événements peut-elle passer d'une tâche à une autre ? Que se passe-t-il avec un `time.sleep` à l'intérieur d'une coroutine ?
3. Si quatre services répondent en 0.3, 0.5, 0.1 et 0.2 seconde, combien de temps prend l'exécution en file et combien avec un `TaskGroup` ? Et avec un `Semaphore(2)` ?
4. Que mesure `httpx.Timeout` et que mesure `asyncio.timeout()` ? Lequel des deux coupe un serveur qui envoie un octet toutes les quatre secondes ?
5. Pourquoi le sémaphore se prend-il **hors** de `revisar` et non dedans ?
6. Quand une tâche d'un `TaskGroup` lance une exception, qu'arrive-t-il aux autres ? Que reçoit le code qui est hors du bloc ?
7. Que fait `except*` que ne fait pas `except` ? Quelle différence y a-t-il entre `revisar` qui convertit un `ConnectError` en un `Resultado` et qui attrape un `ZeroDivisionError` ?
8. Où change-t-on le nom avec `monkeypatch` si `cli.py` a fait `from revisor.revision import revisar_todos` ? Pourquoi le faux doit-il accepter `limite` ?

## Pour aller plus loin

- [Documentation d'`asyncio` : coroutines et tâches](https://docs.python.org/3/library/asyncio-task.html) — `TaskGroup`, `create_task`, `timeout()` et `sleep()` avec toutes leurs règles, y compris l'annulation. C'est la source de cette leçon. Consulté le 7 octobre 2026.
- [PEP 654, « Exception Groups and except\* »](https://peps.python.org/pep-0654/) — pourquoi les groupes d'exceptions existent, avec les cas qui les ont motivés. Plus technique, mais la section sur la motivation se lit bien. Consulté le 7 octobre 2026.
- [Documentation d'`httpx` : transports (`MockTransport`)](https://www.python-httpx.org/advanced/transports/) et [délais d'attente](https://www.python-httpx.org/advanced/timeouts/) — les deux pièces d'`httpx` que tu as utilisées aujourd'hui. Consulté le 7 octobre 2026.
- [Documentation de `pytest` : `monkeypatch`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — toutes les façons de changer un nom pendant un test et quand utiliser chacune. Consulté le 7 octobre 2026.
