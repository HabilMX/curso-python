# Leçon 11 — Le programme terminé

**Durée :** 2 × 90 min (la première session va jusqu'à la fin de 11.2 ; la seconde commence en 11.3)

**Ce que tu construis :** le `revisor` complet, version 1.0.0, installé sur ton ordinateur comme une commande de plus

**Ce que tu apprends :** le rapport comme contrat (tableau à largeur calculée et JSON testé) ; `logging` et `--verbose` ; les codes de sortie revus ; une révision de sécurité (l'adresse qu'un autre écrit, `subprocess` sans `shell=True`, `secrets`, ni `eval` ni `pickle`) ; construire le paquet et l'installer avec `pipx`

**D'où tu viens.** Tu arrives avec le `revisor` de la [Leçon 10](10-concurrencia-pruebas-sin-red.md) : un paquet qui lit sa configuration, interroge les services à la fois, avec un délai d'attente et un plafond de simultanées, et qui a 27 tests qui ne touchent pas au réseau. Ça fonctionne, et ça fonctionne bien. Mais il vit encore dans ton dossier : il se lance avec `python -m revisor` depuis l'endroit où se trouve le code, et son tableau a un défaut que tu n'as pas vu parce que tous tes services ont des noms courts : la colonne `SERVICIO` mesure toujours 12 caractères, et un service appelé `notificaciones-de-clientes` la fait déborder. Aujourd'hui, tout cela se referme. Tu travailles dans ton dossier `~/curso-python/revisor/`, avec l'environnement virtuel activé et, pour la dernière partie, avec `pipx` installé.

**Ce que cette leçon ne fait pas.** Elle n'apporte presque pas de nouveaux concepts de Python : c'est la leçon où tu **rassembles** ce que tu sais déjà et où tu vérifies que c'est terminé. Ce qui est nouveau relève du métier : `logging`, qui est le langage avec lequel un programme raconte ce qu'il fait sans salir son rapport ; l'empaquetage final ; et la révision des quatre habitudes de sécurité que le cours a semées. L'étape finale n'est pas une leçon de plus : c'est la liste de sept vérifications avec laquelle `fr/README.md` définit quand le cours est terminé, et cette leçon les parcourt **une par une**, avec la vraie sortie de chacune.

## À la fin, tu seras capable de

- Expliquer pourquoi un rapport qu'un autre programme lit est un contrat, et tester ce contrat avec un test qui passe au rouge si quelqu'un renomme un champ.
- Calculer la largeur d'une colonne à partir des données et aligner un tableau même si un nom est long.
- Utiliser `logging` à la place de `print` pour ce que le programme raconte de lui-même, et expliquer pourquoi le rapport va sur la sortie standard et le journal sur la sortie d'erreur.
- Dire, pour chaque code de sortie (0, 1 et 2), ce que le `revisor` promet à celui qui l'appelle depuis un script.
- Nommer et éviter quatre risques de sécurité fréquents : une adresse qu'un autre écrit, `subprocess` avec `shell=True`, `eval` et `pickle` avec des données extérieures, et des nombres « aléatoires » pour des secrets.
- Construire le paquet comme un fichier installable (`.whl`), l'installer avec `pipx` et l'exécuter depuis n'importe quel dossier.
- Vérifier, avec une commande et une sortie pour chacun, que le `revisor` remplit les sept points de « Comment savoir que tu as terminé ».

## Le pourquoi avant le comment

Quand quelqu'un dit « j'ai terminé le programme », il y a au moins trois choses qu'il peut vouloir dire. Que **ça fonctionne sur son ordinateur**, aujourd'hui, avec ses données. Que **quelqu'un d'autre peut l'installer et l'utiliser** sans lui demander d'aide. Ou qu'**on peut lui faire confiance** : que si quelque chose se passe mal il le dit clairement, que si quelque chose change un test s'en aperçoit avant un utilisateur, qu'il ne reste pas bloqué, qu'il n'ouvre pas des portes qu'il ne devait pas. Les trois sont distinctes, et il est très courant de livrer la première en croyant que c'est la troisième.

Le cours a commencé par toi, assis devant un `print("revisor: todavía no revisa nada")`, et il se termine dans cette leçon parce que le `revisor` doit maintenant pouvoir se débrouiller seul. Pour décider s'il y est parvenu, l'impression que « c'est bon » ne suffit pas : l'impression est la première chose qui échoue. C'est pourquoi le programme définit la fin avec **sept vérifications** qu'on peut exécuter, pas avec une opinion. Les voici, et tu vas les parcourir une par une à la fin de la leçon :

1. `pytest` se termine au vert et le rapport dit combien de tests se sont exécutés.
2. `ruff check`, `ruff format --check` et `mypy` ne signalent rien.
3. Il vérifie 20 services à la fois en un temps proche de celui du plus lent, pas de celui de la somme.
4. Un service en panne, lent ou qui répond n'importe quoi ne fait pas tomber le rapport.
5. Aucune requête ne peut attendre pour toujours.
6. Il tourne pareil sous Python 3.14 et sous le 3.12 de ton Mint.
7. Il s'installe avec `pipx install` et `revisor --help` fonctionne depuis un autre dossier ; il sort avec 0 si tout est en marche et avec 1 sinon.

De ces sept, ton `revisor` en remplit déjà presque toutes et tu ne le sais peut-être pas. Ce qui manque, ce sont trois choses : **le mesurer** (personne ne fait confiance à « je crois que oui »), **le laisser dans un état qu'un autre puisse utiliser** (le rapport, le journal, l'empaquetage) et **réviser les habitudes de sécurité** pour que le point 4, « ne fait pas tomber le rapport », ne soit pas seulement affaire de pannes accidentelles mais aussi d'entrées hostiles. Les quatre parties de la leçon suivent cet ordre.

## Les concepts

### 11.1 Le rapport comme contrat

#### 11.1.1 Qui lit ton rapport

Jusqu'à maintenant, le rapport, c'était toi qui le lisais, dans un terminal. Mais un programme en ligne de commande qui sort avec le code 0 ou 1 est fait pour qu'**un autre programme** l'appelle : un script d'astreinte qui tourne toutes les cinq minutes, une tâche d'intégration continue qui décide si elle laisse passer un déploiement. Cet autre programme ne *lit* pas le rapport comme toi : il l'**interprète**. Il cherche un champ avec un nom et en attend un type. Si demain quelqu'un renomme `caido` en `caidos` dans le JSON, pour une personne c'est un changement d'orthographe ; pour le script, c'est un champ qui a disparu, et sans un test qui l'attrape, personne ne s'en aperçoit jusqu'à ce que l'alarme de trois heures du matin ne sonne pas.

Cela s'appelle un **contrat** : la façon dont le programme promet de livrer son résultat, et que d'autres peuvent tenir pour certaine. Le `revisor` a deux contrats. Le **JSON** (défini dans la Leçon 6) est pour les machines : ses champs et ses types sont fixes, et le `tiempo_ms` d'un service qui n'a pas répondu est `null`, pas `0` ni un texte. Et le **code de sortie** (défini dans la Leçon 7) est pour le shell et pour n'importe quel script : `0` si tous les services sont `ARRIBA` ; `1` si l'un est `LENTO` ou `CAIDO` ; `2` si l'usage est invalide ou si la configuration ne convient pas. Le tableau, en revanche, est pour les personnes, et peut changer d'aspect sans prévenir personne.

Aujourd'hui, on rend explicite ce qui était implicite : on écrit un **test qui décrit le JSON en entier**. Et on corrige un défaut du tableau.

#### 11.1.2 La largeur d'une colonne se calcule, elle ne se devine pas

Regarde le défaut avant de le corriger. La Leçon 2 a fixé la largeur de la première colonne à 12 caractères avec `f"{nombre:<12}"`, et avec les noms de l'échantillon (le plus long, `inventario`, en a 10), c'était parfait. Avec un nom long, le texte déborde de sa colonne et pousse toutes les autres. La solution est de faire en sorte que la largeur **dépende des données** : le plus long des noms plus deux espaces de marge, avec un minimum de 12 pour que les tableaux courts aient l'air de toujours.

Il y a une nouveauté de syntaxe. Une f-string te laisse mettre la largeur **à l'intérieur** de la spécification, avec une autre paire d'accolades : `f"{nombre:<{ancho}}"` signifie « aligne `nombre` à gauche dans un champ de `ancho` caractères », où `ancho` est une variable. C'est la même chose que `:<12`, avec le 12 remplacé par une variable. Regarde comment `formato.py` est fait en entier :

```python
# fig11_05/src/revisor/formato.py
import json

from revisor.modelo import Estado, Resultado

ANCHO_MINIMO = 12


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado(ancho: int = ANCHO_MINIMO) -> str:
    return f"{'SERVICIO':<{ancho}}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(resultado: Resultado, ancho: int = ANCHO_MINIMO) -> str:
    nombre = resultado.servicio.nombre
    estado = resultado.estado.value
    tiempo = formatear_tiempo(resultado.tiempo_ms)
    return f"{nombre:<{ancho}}{estado:<10}{tiempo:>6}  {resultado.detalle}"


def ancho_servicio(resultados: list[Resultado]) -> int:
    mas_largo = max([len(r.servicio.nombre) for r in resultados], default=0)
    return max(ANCHO_MINIMO, mas_largo + 2)


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


def tabla(resultados: list[Resultado]) -> str:
    ancho = ancho_servicio(resultados)
    renglones = [encabezado(ancho)]
    renglones += [linea(resultado, ancho) for resultado in resultados]
    renglones += ["", resumen(resultados)]
    return "\n".join(renglones)


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

Trois fonctions nouvelles ou modifiées. `ancho_servicio` calcule la largeur : une compréhension extrait la longueur de chaque nom, `max(..., default=0)` renvoie la plus grande (le `default=0` est ce que `max` renvoie si la liste est vide ; sans lui, `max([])` lance `ValueError`), et on lui ajoute deux. `max(ANCHO_MINIMO, ...)` impose le minimum. `encabezado` et `linea` reçoivent un `ancho` avec une valeur par défaut `ANCHO_MINIMO` ; ainsi, tout code qui les appelait sans largeur (tes tests de la Leçon 8, par exemple) continue de fonctionner sans changement. Et `tabla` rassemble le tout : elle calcule la largeur **une fois**, monte l'en-tête, une ligne par résultat, une ligne vide et le récapitulatif, et les joint avec des sauts de ligne. (`renglones += [...]` ajoute à la fin de la liste tous les éléments de l'autre, comme plusieurs `append` à la suite ; et `"\n".join(...)` est le `join` de la Leçon 4 avec le saut de ligne comme séparateur.) Avec les quatre services canoniques, le nom le plus long en mesure 10, `10 + 2 = 12` et la largeur calculée est 12 : le tableau sort **identique** à celui que tu avais, octet pour octet. Il ne change que lorsqu'il faut qu'il change.

#### 11.1.3 Le JSON comme contrat, testé

Le second changement est un test. Lis-le en entier : il n'est pas court, et sa longueur est le point.

```python
# fig11_05/tests/test_formato.py
import json

import pytest

from revisor.formato import formatear_tiempo, reporte_a_json, tabla
from revisor.modelo import Estado, Resultado, Servicio


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [(None, "—"), (87, "87ms"), (999, "999ms"), (2300, "2.3s")],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado


def servicio(nombre: str) -> Servicio:
    return Servicio(nombre, f"https://{nombre}.example")


CANONICOS = [
    Resultado(servicio("catalogo"), Estado.ARRIBA, 142, "200"),
    Resultado(servicio("inventario"), Estado.LENTO, 2300, "200"),
    Resultado(servicio("pagos"), Estado.ARRIBA, 87, "200"),
    Resultado(servicio("reportes"), Estado.CAIDO, None, "sin conexión"),
]


def test_el_json_es_un_contrato() -> None:
    esperado = {
        "servicios": [
            {
                "nombre": "catalogo",
                "url": "https://catalogo.example",
                "estado": "ARRIBA",
                "tiempo_ms": 142,
                "detalle": "200",
            },
            {
                "nombre": "inventario",
                "url": "https://inventario.example",
                "estado": "LENTO",
                "tiempo_ms": 2300,
                "detalle": "200",
            },
            {
                "nombre": "pagos",
                "url": "https://pagos.example",
                "estado": "ARRIBA",
                "tiempo_ms": 87,
                "detalle": "200",
            },
            {
                "nombre": "reportes",
                "url": "https://reportes.example",
                "estado": "CAIDO",
                "tiempo_ms": None,
                "detalle": "sin conexión",
            },
        ],
        "resumen": {
            "total": 4,
            "arriba": 2,
            "lento": 1,
            "caido": 1,
            "promedio_ms": 843,
        },
    }
    assert json.loads(reporte_a_json(CANONICOS)) == esperado


def test_la_tabla_se_alinea_con_un_nombre_largo() -> None:
    largo = Resultado(servicio("notificaciones-de-clientes"), Estado.ARRIBA, 50, "200")
    lineas = tabla([*CANONICOS, largo]).splitlines()
    ancho = len("notificaciones-de-clientes") + 2
    assert lineas[0].index("ESTADO") == ancho
    for renglon in lineas[1:6]:
        assert renglon[ancho : ancho + 6] in {"ARRIBA", "LENTO ", "CAIDO "}
```

`CANONICOS` sont les quatre résultats canoniques, montés à la main dans le test ; **ils ne viennent ni du réseau ni du laboratoire**. `test_el_json_es_un_contrato` écrit le JSON attendu en entier, champ par champ, comme un dictionnaire, et le compare avec `json.loads(reporte_a_json(CANONICOS))`. Deux décisions comptent. La première : le test compare **ce que signifie** le JSON (le dictionnaire qui sort de `json.loads`) et non le **texte** (les espaces et l'ordre des lignes), parce qu'un script qui interprète du JSON se moque du nombre d'espaces et se soucie beaucoup des champs. La seconde : le test inclut le cas gênant, `reportes` avec `"tiempo_ms": None` (qui en JSON est `null`), et le `promedio_ms` de 843. Si quelqu'un change le `0` en `null`, ou retire un champ, ou change l'arrondi de la moyenne, le test passe au rouge.

Le second nouveau test, `test_la_tabla_se_alinea_con_un_nombre_largo`, ajoute aux quatre canoniques un service avec un nom de 26 caractères (`[*CANONICOS, largo]` monte une nouvelle liste avec les éléments de `CANONICOS`, que l'astérisque « déballe » un par un, et `largo` à la fin, sans toucher à `CANONICOS`) et vérifie deux choses : que le mot `ESTADO` de l'en-tête commence à la colonne 28 (26 plus les 2 de marge) et que dans chaque ligne de données, à cette même colonne, il y a un état valide. Pour la première, il utilise `.index(...)`, une méthode des textes qui cherche où commence un morceau dans le texte et renvoie sa position, en comptant à partir de 0 comme les indices des listes : `lineas[0].index("ESTADO")` est la colonne où commence `ESTADO` dans l'en-tête (s'il ne le trouvait pas, il échouerait avec `ValueError`). Ce `renglon[ancho : ancho + 6]` est une tranche : la syntaxe `[inicio:fin]` prend les caractères depuis la position `inicio` jusqu'à celle qui précède `fin`, donc ici ce sont les six qui commencent à la colonne de l'état, ce que mesure `"ARRIBA"`. Le `in {"ARRIBA", "LENTO ", "CAIDO "}` a une espace à la fin de `"LENTO "` et de `"CAIDO "` parce que ces états mesurent cinq caractères et que la tranche en prend six.

Dans un test comme celui-ci, il vaut la peine de se demander s'il respecte la barre de la Leçon 8 : passe-t-il au rouge si l'on casse ce qu'il dit tester ? L'Exercice 2 te demande de casser le JSON exprès et de le vérifier.

### 11.2 `logging` : ce que le programme raconte de lui-même

#### 11.2.1 Pourquoi pas `print`

Le rapport est **ce que le programme produit**. Mais un programme a aussi des choses à raconter sur **son propre travail** : « j'ai lu 4 services », « le service `pagos` a répondu en 87 ms ». C'est de l'information pour qui enquête sur quelque chose de bizarre, pas pour qui lit le rapport. Si ces messages sont affichés avec `print` à côté du rapport, ils se mélangent avec lui : le script qui lit le JSON trouve des lignes de diagnostic au milieu et cesse de pouvoir l'interpréter.

Le monde d'Unix a résolu cela il y a des décennies avec deux canaux : la **sortie standard** (*stdout*) est pour le résultat du programme, et la **sortie d'erreur** (*stderr*) est pour tout le reste que le programme a à dire sur lui-même. Tu les utilises déjà : le rapport passe par la première, le `error de configuración: ...` passe par la seconde (Leçon 7). Le module [`logging`](https://docs.python.org/3/library/logging.html) de la bibliothèque standard est la façon ordonnée d'écrire sur le second canal, avec un avantage sur `print` : chaque message a un **niveau** d'importance, et c'est toi qui décides à partir de quel niveau tu veux les entendre, sans toucher au code qui les écrit.

#### 11.2.2 Les niveaux et un premier programme

Les niveaux, du moins grave au plus grave : `DEBUG` (détail fin, pour qui débogue), `INFO` (le programme avance), `WARNING` (quelque chose d'étrange, mais ça continue), `ERROR` (quelque chose a échoué) et `CRITICAL`. Par défaut, `logging` n'affiche qu'à partir de `WARNING`. Un **enregistreur** (*logger*) est l'objet auquel tu parles, et on le demande par son nom : `logging.getLogger("demo")`. Cette figure montre le tout ensemble :

```python
# fig11_01.py
import logging
import sys

logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
registro = logging.getLogger("demo")

print("este renglón es el reporte: va a la salida estándar", flush=True)
registro.debug("detalle fino: nadie lo ve con el nivel por omisión")
registro.warning("aviso: %s tardó %s ms", "inventario", 2300)
registro.setLevel(logging.DEBUG)
registro.debug("ahora sí aparece, porque subí el detalle")
```

```text
$ python fig11_01.py
este renglón es el reporte: va a la salida estándar
WARNING demo: aviso: inventario tardó 2300 ms
DEBUG demo: ahora sí aparece, porque subí el detalle
```

Ligne par ligne. `logging.basicConfig(stream=sys.stderr, format=...)` fait la configuration minimale : que les messages aillent vers `sys.stderr` (la sortie d'erreur) et avec le format `NIVEL nombre: mensaje`. `registro.debug(...)` écrit un message de niveau `DEBUG`, et il n'apparaît pas, parce que le niveau par défaut est `WARNING` : ce message est **gardé dans le code mais éteint**, ce qui est tout l'intérêt. `registro.warning("aviso: %s tardó %s ms", "inventario", 2300)` apparaît bien. Remarque comment il s'écrit : le message porte des marqueurs `%s` et les valeurs vont **à part**, comme arguments. C'est le format `%` des chaînes, l'ancien (`"%s" % x`), que le cours n'utilise nulle part ailleurs ; ici ce n'est pas toi qui l'appliques : `logging` l'applique en interne, en réunissant le message et les valeurs, et [sa documentation](https://docs.python.org/3/howto/logging.html#logging-variable-data) le demande ainsi. Les valeurs sont passées séparément pour que `logging` ne monte le texte **que si le message va être émis** ; avec un `f"..."`, le texte serait toujours monté, même si le niveau est éteint, et dans un programme qui journalise des milliers de lignes, cette différence compte. Et `registro.setLevel(logging.DEBUG)` baisse le niveau, ce qui fait apparaître le dernier `debug`. Le programme a affiché le rapport avec `print(..., flush=True)` ; le `flush=True` oblige seulement le texte à sortir sur-le-champ, pour que l'ordre de la sortie documentée soit le même que celui que tu vois dans le terminal.

Un avertissement de conception, qui vient du [guide officiel](https://docs.python.org/3/howto/logging.html) : le code d'une **bibliothèque** (ou d'un module du paquet) ne configure jamais `logging` ; il demande seulement son enregistreur et écrit. Celui qui configure est le **programme principal**, qui sait où doivent aller les messages. C'est pourquoi, dans le `revisor`, `basicConfig` vit dans `cli.py` et non dans `revision.py`.

#### 11.2.3 `--verbose` dans le `revisor`

Le `revisor` journalise, au niveau `DEBUG`, le résultat de chaque service, et une option `--verbose` l'active. `revision.py` demande l'enregistreur `"revisor"` au début, et sa fonction `revisar` est maintenant une enveloppe : elle appelle `_consultar` (le corps de toujours, qui n'a pas changé) et journalise le résultat avant de le renvoyer.

```python
# fig11_05/src/revisor/revision.py
import asyncio
import logging
import time

import httpx

from revisor.formato import formatear_tiempo
from revisor.modelo import Estado, Resultado, Servicio, clasificar

registro = logging.getLogger("revisor")


async def _consultar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
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


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    resultado = await _consultar(cliente, servicio)
    registro.debug(
        "%s: %s, %s, %s",
        servicio.nombre,
        resultado.estado.value,
        formatear_tiempo(resultado.tiempo_ms),
        resultado.detalle,
    )
    return resultado


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

Remarque la séparation : `_consultar` fait l'interrogation ; `revisar` la fait et la **raconte**. Ainsi le journal est à un seul endroit et non répété dans chaque `return`. Dans `cli.py`, trois changements : l'option `--verbose` (avec `action="store_true"`, ce qui signifie « si elle apparaît, elle vaut `True` ; sinon, `False` », sans attendre de valeur), une fonction `configurar_logging` et l'appel à `tabla` :

```python
# fig11_05/src/revisor/cli.py
import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from pathlib import Path

from revisor.configuracion import ErrorDeConfiguracion, leer_servicios
from revisor.formato import reporte_a_json, tabla
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="escribe en la salida de error el detalle de cada revisión",
    )
    return parser


def configurar_logging(verbose: bool) -> None:
    logging.basicConfig(stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    nivel = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger("revisor").setLevel(nivel)


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)
    configurar_logging(argumentos.verbose)

    try:
        servicios = leer_servicios(argumentos.config)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}", file=sys.stderr)
        return 2

    resultados = asyncio.run(revisar_todos(servicios, limite=argumentos.concurrencia))
    if argumentos.formato == "json":
        print(reporte_a_json(resultados))
    else:
        print(tabla(resultados))

    problemas = [r for r in resultados if r.estado is not Estado.ARRIBA]
    if len(problemas) == 0:
        return 0
    return 1
```

`configurar_logging` fait trois choses. `basicConfig` branche le journal sur `sys.stderr`. La ligne `nivel = logging.DEBUG if verbose else logging.WARNING` est une **expression conditionnelle**, un `if`/`else` qui tient sur une ligne et qui **donne une valeur** : elle se lit « `logging.DEBUG` si `verbose` est vrai ; sinon, `logging.WARNING` », et équivaut à un `if`/`else` de quatre lignes qui affecte `nivel` dans chaque branche. Et `logging.getLogger("revisor").setLevel(nivel)` met le niveau **seulement à l'enregistreur du `revisor`** : `DEBUG` s'ils ont demandé `--verbose`, `WARNING` sinon. Cette distinction compte : si tu avais mis le niveau `DEBUG` sur l'enregistreur de **tous** (la racine), `httpx` et la bibliothèque qu'il utilise en dessous écriraient des centaines de lignes à eux, et ce qui est à toi s'y perdrait. En plus, chaque option porte maintenant son texte d'aide en espagnol (`help=...`), parce que la septième vérification demande que `revisor --help` serve. (Les textes qu'`argparse` met de son côté, comme `options:` et `show this help message and exit`, sortent en anglais ; ils sont de la bibliothèque.)

Regarde la différence avec le laboratoire qui tourne (encore une fois, les temps varient sur ta machine) :

```text
$ cd fig11_05
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 854ms
```

Sans `--verbose`, le rapport sort comme toujours et la sortie d'erreur ne dit rien. Avec `--verbose`, le journal apparaît **sur l'autre canal**. Pour les voir séparément, redirige-les vers des fichiers différents (c'est l'Exercice 3) : le rapport propre dans l'un et le journal dans l'autre.

Un dernier commentaire, de métier. L'ordre des lignes du journal est l'ordre dans lequel les services *terminent*, pas celui de la configuration : `reportes` (qui échoue immédiatement) sort en premier. C'est une raison de plus pour que le **rapport** ne dépende pas du journal : le rapport est monté dans l'ordre, à partir de la liste ; le journal est un carnet de ce qui s'est passé au fur et à mesure. L'[entrée du blog sur la télémétrie](https://www.habil.mx/fr/blog/telemetrie-prometheus-loki-tempo-grafana-opentelemetry/) raconte comment, dans un vrai système, on rassemble les journaux de nombreux programmes comme celui-ci.

> **La première session s'arrête ici.** Tu as le rapport final (le tableau qui calcule sa largeur et le JSON testé comme contrat) et le journal avec `--verbose`, chacun sur son canal. Avant la seconde session, lance les tests et le `revisor` avec et sans `--verbose`, en redirigeant chaque canal vers son fichier. La seconde session n'ajoute pas de code au `revisor` : elle révise la sécurité, le construit et l'installe avec `pipx`, et vérifie un par un les sept points de « Comment savoir que tu as terminé ».

### 11.3 Révision de sécurité : quatre habitudes

Le cours a semé la sécurité là où était le risque, pas dans un chapitre à part : valider ce qui arrive de l'extérieur (Leçon 6), traiter avec soin l'adresse d'`urllib` (Leçon 9). Cette partie rassemble les quatre habitudes pour que tu les aies ensemble. **Elle n'ajoute pas de code au `revisor`** : le `revisor` applique déjà la première et n'a aucune des trois autres. On les explique parce que tu en auras besoin dès que tu écriras le programme suivant, et parce que la première prend un sens nouveau maintenant que le programme est un outil que n'importe qui peut installer.

#### 11.3.1 L'adresse qu'un autre écrit

Ton `revisor` fait une requête vers l'adresse qui est dans `servicios.toml`. Qui écrit ce fichier décide **où va ton programme**. Si c'est seulement toi, il n'y a pas de risque. Mais un programme se réutilise, et demain ce fichier peut venir d'une autre équipe, d'une page web ou d'un formulaire. La Leçon 6 a mis une défense : `validar_servicio` n'accepte que les adresses `http://` ou `https://` qui passent les vérifications d'`es_url_http` (schéma, serveur, port et texte ordinaire). Ce n'est pas une validation complète, et c'est pourquoi la Leçon 9 a mis un second filet : si `httpx` rejette une adresse qui est passée, ce service sort comme « dirección inválida » et les autres sont vérifiés quand même. Regarde ce que fait la première défense avec une adresse qui ne passe pas :

```text
$ python -m revisor --config raro.toml
error de configuración: servicio 1: 'url' debe ser una dirección http:// o https:// válida
$ echo $?
2
```

Un fichier avec `url = "file:///etc/passwd"` est rejeté avant de rien faire : le message de configuration sort et le code `2`. Sans cette validation, selon l'outil qui ferait la requête, `file://` pourrait lire des fichiers de ta propre machine. Et il y a une variante plus subtile que la validation du schéma ne couvre pas : une adresse `http://` qui pointe **vers l'intérieur** de ton réseau (vers un service interne ou vers le service de métadonnées d'un serveur dans le cloud) fait que *ton* programme, qui est dedans, interroge quelque chose que l'auteur de l'adresse ne pourrait pas atteindre de l'extérieur. Cette attaque s'appelle *server-side request forgery* (SSRF) et [OWASP la décrit en détail](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery). Pour le `revisor`, qui lit un fichier de configuration que tu écris, c'est un risque faible ; pour un service web qui reçoit des adresses d'utilisateurs, c'est un risque central. La règle : **une adresse qui vient de l'extérieur est une donnée non fiable, et elle se valide (et se limite à un ensemble permis) avant d'être utilisée**. L'entrée du blog de Hábil sur la [sécurité des API](https://www.habil.mx/fr/blog/securite-api-cto-identite-passerelle-jetons/) porte cette règle au niveau de l'architecture.

#### 11.3.2 `subprocess` : une liste, jamais un texte monté

Un jour, ton programme voudra exécuter un autre programme du système (`ping`, `git`, `ls`). Le module [`subprocess`](https://docs.python.org/3/library/subprocess.html) le fait, et il a deux façons de recevoir la commande, avec des conséquences très différentes. Cette figure utilise `echo` (qui ne fait qu'afficher) pour que tu puisses voir la différence sans risque :

```python
# fig11_02.py
import subprocess

nombre = "catalogo; echo INYECTADO"

print("--- con shell=True y un texto armado ---", flush=True)
subprocess.run(f"echo revisando {nombre}", shell=True, check=True)

print("--- con una lista y sin shell ---", flush=True)
subprocess.run(["echo", "revisando", nombre], check=True)
```

```text
$ python fig11_02.py
--- con shell=True y un texto armado ---
revisando catalogo
INYECTADO
--- con una lista y sin shell ---
revisando catalogo; echo INYECTADO
```

Dans les deux cas, le « nom » est `catalogo; echo INYECTADO` : un texte où quelqu'un a écrit, après le nom, un point-virgule et **une autre commande**. Avec `shell=True`, Python n'exécute pas directement le programme, mais le donne au *shell* (l'interpréteur du terminal) comme un texte à interpréter, et le shell comprend `;` comme « termine cette commande et exécute une autre ». Le résultat : **deux** choses se sont exécutées, et la seconde a été choisie par celui qui a écrit le nom. C'est une *injection de commandes*. Avec une **liste** (`["echo", "revisando", nombre]`), chaque élément est un argument, le shell n'intervient pas, et le `;` n'est qu'un caractère de plus du texte. Si la commande avait été `rm` au lieu d'`echo`, la différence aurait été d'effacer tes fichiers. La documentation de [`subprocess` dans sa section sécurité](https://docs.python.org/3/library/subprocess.html#security-considerations) demande justement cela ; [OWASP l'explique avec plus d'exemples](https://owasp.org/www-community/attacks/Command_Injection). La règle : **liste d'arguments et sans `shell=True` ; si le shell est nécessaire, le texte qui lui arrive ne peut rien contenir qui vienne de l'extérieur**. Le `check=True` fait qu'une commande qui échoue lance une exception au lieu de passer en silence.

#### 11.3.3 `eval` et `pickle` : exécuter ce qui arrive de l'extérieur

`eval(texto)` prend un texte et l'**exécute comme du code Python**. Il paraît commode pour convertir « 2 + 2 » en 4, mais il faut voir ce qu'il accepte :

```python
# fig11_03.py
texto_de_afuera = "__import__('sys').version_info.major"

print(eval(texto_de_afuera))
```

```text
$ python fig11_03.py
3
```

Le « texte de l'extérieur » est une instruction qui importe un module et lit sa version de Python : rien de nuisible, mais identique en forme à ce que ferait une instruction qui efface des fichiers ou envoie tes données ailleurs. `eval` ne fait pas de distinction. Toute donnée qui arrive de l'extérieur et passe par `eval` donne à celui qui l'a écrite le contrôle de ton programme. Pour convertir du texte en données, il existe des outils qui ne comprennent **que** des données : `json.loads` (que tu utilises depuis la 6) pour le JSON, `tomllib.loads` pour le TOML. Même `ast.literal_eval`, la « version sûre » d'`eval`, n'est pas une défense complète contre un texte hostile, comme l'avertit [sa documentation](https://docs.python.org/3/library/ast.html#ast.literal_eval).

`pickle` est le cas frère. C'est le module qui enregistre des objets Python dans un fichier, et sa [documentation](https://docs.python.org/3/library/pickle.html) s'ouvre sur un avertissement en rouge : *il n'est pas sûr*, parce que défaire un `pickle` peut exécuter du code arbitraire. Un fichier `pickle` qu'une autre personne t'envoie est, en pratique, un programme. Pour des données qui traversent des frontières, JSON. Il n'y a pas de figure de `pickle` dans le cours parce que le montrer exige d'écrire une classe avec des méthodes, et cette pièce, tu ne l'as pas vue ; l'avertissement suffit.

#### 11.3.4 `secrets`, pas `random`

Le module `random` produit des nombres qui *ont l'air* aléatoires mais qui se calculent avec une formule à partir d'une **graine** : si tu connais la graine, tu connais tous les nombres. C'est une vertu pour une simulation que tu veux répéter, et un désastre pour un mot de passe ou un jeton. Regarde les deux choses ensemble :

```python
# fig11_04.py
import random
import secrets

random.seed(1)
primero = random.random()
random.seed(1)
segundo = random.random()
print("random con la misma semilla:", primero == segundo)

token = secrets.token_hex(16)
print("secrets, largo del token:", len(token))
```

```text
$ python fig11_04.py
random con la misma semilla: True
secrets, largo del token: 32
```

Avec la même graine (`random.seed(1)`), `random.random()` donne **exactement le même nombre** deux fois : c'est `True`. Un attaquant qui devine la graine (par exemple, l'heure à laquelle le programme a démarré) reproduit tous tes « secrets ». [`secrets`](https://docs.python.org/3/library/secrets.html) est fait pour le contraire : il tire son aléa du système d'exploitation, le même qu'il utilise pour les clés de chiffrement. `secrets.token_hex(16)` donne 16 octets aléatoires écrits en hexadécimal, c'est-à-dire un texte de 32 caractères (d'où le `32`). La [documentation de `random`](https://docs.python.org/3/library/random.html) le dit dans son premier avertissement : à ne pas utiliser à des fins de sécurité. La règle : **si le nombre est un secret (jeton, mot de passe, identifiant qu'on ne doit pas pouvoir deviner), `secrets` ; sinon, `random` convient**.

### 11.4 Construire et installer

#### 11.4.1 Ce qu'est un paquet installable

Jusqu'à maintenant, le `revisor` s'exécute avec `python -m revisor` depuis le dossier du projet, et il a été installé dans ton environnement avec `pip install -e .` (l'installation **éditable** de la Leçon 7, qui ne copie pas le code mais pointe vers lui). Cela sert pour développer. Pour le remettre à une autre personne, il faut un **fichier** qui contienne le programme déjà emballé. En Python, ce fichier s'appelle une [*wheel*](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), a l'extension `.whl` et est, à l'intérieur, un fichier compressé avec ton code et ses données d'installation (nom, version, dépendances, et quelle commande doit être créée). Le nom raconte une histoire : `revisor-1.0.0-py3-none-any.whl` veut dire « le paquet `revisor`, version 1.0.0, pour n'importe quelle version de Python 3, sans code compilé, sur n'importe quel système ».

La version monte à `1.0.0` dans le `pyproject.toml` ; c'est la seule chose qui change là :

```toml fig11_05/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "1.0.0"
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

On le construit avec l'installateur de paquets. Un détail : tu n'as besoin ni du paquet `build` ni de rien de nouveau ; `pip` sait déjà construire une *wheel* (la commande est [`pip wheel`](https://pip.pypa.io/en/stable/cli/pip_wheel/)). L'option `--no-deps` lui dit de construire **seulement ton paquet** et de ne pas télécharger les dépendances, et `-w dist` de laisser le résultat dans le dossier `dist/`. Le point final est « construis le projet de ce dossier ». Pour le monter, `pip` télécharge un instant l'outil de construction que tu as déclaré dans `[build-system]` (`hatchling`) : c'est une dépendance de *construction*, pas d'exécution, et elle ne voyage pas dans la *wheel*.

```text
$ python -m pip wheel --no-deps -w dist .
Processing /home/tu_usuario/curso-python/revisor
  Installing build dependencies: started
...
Building wheels for collected packages: revisor
  Building wheel for revisor (pyproject.toml): started
  Building wheel for revisor (pyproject.toml): finished with status 'done'
  Created wheel for revisor: filename=revisor-1.0.0-py3-none-any.whl size=6397 sha256=...
  Stored in directory: ...
Successfully built revisor
$ ls dist
revisor-1.0.0-py3-none-any.whl
$ unzip -Z1 dist/revisor-1.0.0-py3-none-any.whl
revisor/__init__.py
revisor/__main__.py
revisor/cli.py
revisor/configuracion.py
revisor/formato.py
revisor/modelo.py
revisor/revision.py
revisor-1.0.0.dist-info/METADATA
revisor-1.0.0.dist-info/WHEEL
revisor-1.0.0.dist-info/entry_points.txt
revisor-1.0.0.dist-info/RECORD
```

(La sortie de `pip wheel` est raccourcie : les `...` marquent des lignes qui ont été retirées, parmi lesquelles le téléchargement de `hatchling` et une longue empreinte `sha256`. La taille, `size`, dépend de ton code, donc la tienne peut être autre ; ce qui compte, c'est `Successfully built revisor`.)

Deux choses à lire ici. La *wheel* contient le paquet `revisor` (sept fichiers) et son dossier `dist-info` avec les métadonnées ; elle **ne contient pas** `servicios.toml`, ni les tests, ni les fichiers du laboratoire. C'est ce qu'il faut : le programme n'apporte pas sa configuration, c'est celui qui l'utilise qui l'apporte. Et la version dans le nom du fichier, `1.0.0`, est sortie du `pyproject.toml`.

#### 11.4.2 `pipx` : installer un outil, pas une bibliothèque

Tu pourrais installer la *wheel* avec `pip install` dans un environnement virtuel, mais alors le `revisor` n'existerait que tant que cet environnement serait activé. Pour un **outil** que tu veux utiliser depuis n'importe quel dossier, comme `git` ou `ruff`, la solution est [`pipx`](https://pipx.pypa.io/stable/). `pipx` crée un environnement virtuel **propre à chaque outil**, y installe le paquet avec ses dépendances, et rend la commande disponible dans ton `PATH`. Chaque outil reste isolé des autres et de ton Python du système (qui, souviens-toi de la Leçon 1, ne doit pas être touché avec `pip`).

Sous Linux Mint, il s'installe avec le gestionnaire de paquets du système : `sudo apt install pipx` (le paquet est dans les dépôts d'Ubuntu 24.04, la base de Mint 22 : [version 1.4.3](https://packages.ubuntu.com/noble/pipx)), puis `pipx ensurepath`, qui ajoute le dossier des commandes de `pipx` (`~/.local/bin`) à ton `PATH` ; ouvre un nouveau terminal pour qu'il le remarque. Avec cela, installer le `revisor` tient en une ligne. La sortie ci-dessous a été obtenue avec une version de `pipx` et de Python plus récentes que celles de ton Mint, donc le texte peut différer dans les détails : ce qui compte, ce sont les trois dernières lignes. Les lignes de préparation de l'environnement ont été retirées.

```text
$ pipx install dist/revisor-1.0.0-py3-none-any.whl
done!
  installed package revisor 1.0.0, installed using Python 3.14.8
  These apps are now available
    - revisor
```

`pipx` a créé l'environnement, installé la *wheel* avec ses dépendances (`httpx` et les siennes) et laissé la commande `revisor`. L'essayer depuis **un autre dossier** est le but. Cette exécution est faite depuis un dossier vide :

```text
$ revisor --version
revisor 1.0.0
$ echo $?
0
$ revisor
error de configuración: no existe el archivo servicios.toml
$ echo $?
2
$ revisor --config servicios.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     159ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      91ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
$ echo $?
1
```

Trois choses. `revisor --version` fonctionne depuis n'importe quel dossier et dit `revisor 1.0.0` ; rappelle-toi que ce nombre n'est pas écrit dans le code, mais que `cli.py` le lit dans les métadonnées du paquet installé, qui sortent du `pyproject.toml`. Deuxièmement : `revisor` tout court, depuis un dossier qui n'a pas de `servicios.toml`, se termine avec le message de configuration et le code `2`. C'est la même leçon que celle de la 6 (le chemin relatif dépend de l'endroit où tu es), et ce n'est pas un défaut : c'est ce qu'il faut pour un outil, qui ne doit pas deviner où est ta configuration. C'est pour cela qu'existe `--config`. Et troisièmement : avec un `--config` valide, le rapport sort et le code est `1`, parce qu'il y a un service `LENTO` et un autre `CAIDO`.

#### 11.4.3 Ce qui vient, et qui n'est pas encore pour toi

Deux nouveautés de Python 3.14 restent hors du cours exprès, et il convient que tu saches qu'elles existent. La première est l'**interpréteur sans GIL** (*free-threaded*) : une variante de Python qui peut exécuter du code Python dans plusieurs threads en même temps ; avec la 3.14, elle est devenue [officiellement prise en charge](https://peps.python.org/pep-0779/), mais cela reste une compilation à part et facultative, et beaucoup de bibliothèques ne sont pas encore prêtes. Pour le `revisor`, rien ne change, parce qu'il fait déjà des attentes concurrentes dans un seul thread et n'est pas limité par le GIL. La seconde, ce sont les ***t-strings*** (chaînes de gabarit, [PEP 750](https://peps.python.org/pep-0750/)) : elles s'écrivent comme une f-string mais avec un `t` devant, et au lieu d'un texte elles renvoient un objet qui sépare le fixe de l'interpolé, utile pour échapper du HTML ou monter des requêtes SQL en sécurité. Aucune des deux n'est nécessaire pour ce que tu as fait, aucune n'est utilisée dans le cours (et le code du cours doit tourner sous le 3.12 de ton Mint, qui ne les a pas), et toutes deux sont expliquées dans [la liste des nouveautés de 3.14](https://docs.python.org/3/whatsnew/3.14.html). Quand tu en auras besoin, tu sauras déjà lire cette documentation par toi-même, ce que le cours s'était proposé.

## Les sept points, un par un

C'est ici que le cours se referme. Chaque point est une commande et une sortie ; la sortie ci-dessous est la vraie, du dossier `fig11_05/` avec le laboratoire qui tourne dans un autre terminal.

### Point 1 — `pytest` se termine au vert et dit combien de tests se sont exécutés

On lance `pytest -q` et on lit **le décompte du rapport**, la dernière ligne. Dans ce dossier, il doit dire `30 passed` : les 27 de la Leçon 10 plus les trois d'aujourd'hui (le contrat du JSON, le tableau avec un nom long et `--version`).

Pourquoi le décompte et pas le code de sortie : le code 0 de `pytest` dit seulement qu'*il n'y a pas eu d'échecs*, et on peut avoir 0 échec avec presque aucun test qui tourne. Regarde deux cas, mesurés. Un : un fichier avec un seul test marqué pour être sauté.

```text
$ pytest -q tests/test_saltada.py
s                                                                        [100%]
1 skipped in 0.00s
$ echo $?
0
```

Code 0, et `1 skipped` : rien n'a été testé, et tout a l'air bien. Deux : filtrer par nom.

```text
$ pytest -q -k sale_con
..                                                                       [100%]
2 passed, 28 deselected in 0.02s
$ echo $?
0
```

Aussi avec le code 0, mais `2 passed, 28 deselected` : sur 30 tests, deux ont tourné. Qui ne regarde que la couleur verte ou le code ne le remarque pas ; qui lit le décompte, si. La [référence des codes de sortie de `pytest`](https://docs.pytest.org/en/stable/reference/exit-codes.html) les énumère (il y en a un spécifique, le 5, pour « aucun test collecté », mais même celui-là ne protège pas d'un filtre qui en laisse passer deux). **Règle : le point 1 est rempli quand tu lis `30 passed` et que ce 30 est le nombre que tu attendais.**

### Points 2 et 6 — la qualité, et le fait que ça tourne pareil sous 3.14 et sous 3.12

On lance les quatre outils de qualité, avec chaque version de Python. D'abord avec 3.14 :

```text
$ python --version
Python 3.14.8
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

Et exactement la même chose avec 3.12, la série de ton Mint. L'exécution ci-dessous a été faite avec Python 3.12.12 ; celui de Mint 22 est le 3.12.3 (tu l'as vu dans la leçon 1), donc sur ton écran la première ligne dira `Python 3.12.3` :

```text
$ python --version
Python 3.12.12
$ pytest -q
..............................                                           [100%]
30 passed in 0.05s
$ ruff check
All checks passed!
$ ruff format --check
13 files already formatted
$ mypy
Success: no issues found in 12 source files
```

La seule différence est la ligne de `python --version`. `ruff check` et `ruff format --check` ne signalent rien (ils vérifient 13 fichiers, le laboratoire inclus) et `mypy` dit `Success`. Les 30 tests passent dans les deux. Pour répéter cela sur ton Mint : le Python du système (3.12), tu l'as déjà dans ton environnement de toujours. Si tu as installé 3.14 avec `uv` (l'encadré de la Leçon 7), crée un second environnement avec lui (`python3.14 -m venv .venv314`), active-le et installe le projet et les outils avec les versions de `herramientas/requisitos.txt`, puis lance les quatre mêmes commandes. Si tu n'as pas installé 3.14, le point 6 est rempli *pour la version que tu as*, et l'autre moitié, tu la vérifies quand tu veux : tu installes 3.14 avec `uv` et tu répètes ces quatre commandes. Personne ne la vérifie à ta place ; la sortie ci-dessus est celle d'une exécution dans les deux versions, et ce qui compte, c'est la tienne.

### Point 3 — 20 services à la fois, dans le temps du plus lent

Avec les vingt services d'une demi-seconde (`servicios-20.toml`), en file et tous à la fois :

```text
$ time python -m revisor --config servicios-20.toml --concurrencia 1 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 504ms

real	0m10.169s
user	0m0.093s
sys	0m0.020s

$ time python -m revisor --config servicios-20.toml --concurrencia 20 | tail -n 1
20 servicios · 20 arriba · 0 lentos · 0 caídos · promedio 509ms

real	0m0.606s
user	0m0.083s
sys	0m0.018s
```

En file (`--concurrencia 1`) : 10.2 secondes, la somme. Avec `--concurrencia 20` : 0.61, proche du plus lent (0.5) plus le démarrage de Python. **Le point 3 est rempli** parce que le temps n'est pas la somme des attentes : il est de l'ordre de la plus longue attente. Si ta machine marque quelques centièmes de plus, peu importe ; ce qui compte, c'est que ce soit environ seize fois moins.

### Point 4 — un service en panne, lent ou qui répond n'importe quoi ne fait pas tomber le rapport

Avec le laboratoire, tu l'as déjà vu à chaque exécution : `reportes` est en panne, `inventario` est lent, et les deux autres sortent complets. Il manque le troisième type, celui qui **répond n'importe quoi** : quelque chose qui répond, mais pas avec du HTTP valide. Cela ne peut pas se demander au laboratoire, mais bien à un faux transport (Leçon 10), qui peut lancer l'exception qu'`httpx` lance face à une réponse qui n'est pas du HTTP (`httpx.RemoteProtocolError`). Cette figure réunit cinq types de service en une seule exécution : un sain, un lent, un qui répond n'importe quoi, un qui renvoie 503 et un vraiment bloqué (il attend 30 secondes avec un délai d'attente d'une demi-seconde).

```python
# fig11_06.py
import asyncio

import httpx
from revisor.formato import tabla
from revisor.modelo import Servicio
from revisor.revision import revisar_todos

SERVICIOS = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("lento", "https://lento.example"),
    Servicio("basura", "https://basura.example"),
    Servicio("caido", "https://caido.example"),
    Servicio("colgado", "https://colgado.example", timeout_ms=500),
    Servicio("pagos", "https://pagos.example"),
]


async def atender(peticion: httpx.Request) -> httpx.Response:
    anfitrion = peticion.url.host
    if anfitrion == "lento.example":
        await asyncio.sleep(1.1)
    if anfitrion == "colgado.example":
        await asyncio.sleep(30)
    if anfitrion == "basura.example":
        raise httpx.RemoteProtocolError("lo que llegó no es HTTP", request=peticion)
    if anfitrion == "caido.example":
        return httpx.Response(503)
    return httpx.Response(200)


async def main() -> None:
    transporte = httpx.MockTransport(atender)
    resultados = await revisar_todos(SERVICIOS, transporte=transporte)
    print(tabla(resultados))


asyncio.run(main())
```

```text
$ python fig11_06.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA       0ms  200
lento       LENTO       1.1s  200
basura      CAIDO          —  error de red
caido       CAIDO        0ms  503
colgado     CAIDO          —  tiempo agotado
pagos       ARRIBA       0ms  200

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 275ms
```

Ce programme **importe le paquet** `revisor` : il tourne avec l'environnement où tu as installé le projet (`pip install -e .` dans le dossier `fig11_05/`). Les six services sortent dans le rapport, dans leur ordre, chacun avec ce qui est à lui : `lento` est `LENTO` (1.1 s), `basura` apparaît comme `CAIDO` avec le détail `error de red`, `caido` porte son `503`, et `colgado` a renoncé avec `tiempo agotado` sans attendre les 30 secondes. Aucun n'a fait tomber les autres. Et ce n'est pas seulement affaire de simulation : si un vrai serveur répond quelque chose qui n'est pas du HTTP (par exemple, un programme qui écoute sur un port et répond un texte quelconque), `httpx` lance une erreur de protocole, qui est un `httpx.HTTPError`, et le `revisor` la rapporte pareil, comme `error de red`. Les `0ms` de `catalogo` et `pagos` viennent de ce que le faux transport répond instantanément ; avec un vrai réseau, ce seraient des dizaines ou des centaines. **Le point 4 est rempli.**

### Point 5 — aucune requête n'attend pour toujours

Deux vérifications. La première, dans le code : combien d'endroits font une requête, et sont-ils tous protégés ?

```text
$ grep -rn "cliente.get" src/revisor
src/revisor/revision.py:19:            respuesta = await cliente.get(servicio.url, timeout=limite)
```

Une seule requête dans tout le paquet, et elle est à l'intérieur d'`async with asyncio.timeout(...)` et avec `httpx.Timeout(...)` (tu l'as vu dans `revision.py`). La seconde, avec l'exécution : un service du laboratoire qui met 10 secondes avec `timeout_ms = 1000`, et un autre qui met 8 secondes **sans** `timeout_ms` dans la configuration (il utilise la valeur par défaut, 5000) :

```text
$ time python -m revisor --config servicios-limite.toml
SERVICIO        ESTADO    TIEMPO  DETALLE
notificaciones  CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m1.127s
user	0m0.106s
sys	0m0.022s

$ time python -m revisor --config servicios-sin-limite.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
colgado     CAIDO          —  tiempo agotado

1 servicio · 0 arriba · 0 lentos · 1 caído · promedio —

real	0m5.141s
user	0m0.115s
sys	0m0.027s
```

Le premier renonce à 1.1 seconde ; le second, à 5.1. Aucun n'a attendu ce que voulait le serveur. **Le point 5 est rempli**, aussi pour qui oublie de mettre le délai d'attente dans sa configuration, parce que la valeur par défaut de `Servicio` est de 5000 ms.

### Point 7 — il s'installe avec `pipx` et s'utilise depuis un autre dossier

Tu l'as déjà fait en 11.4 : `pipx install`, `revisor --version` et `revisor --help` depuis un dossier quelconque. Il reste à vérifier le contrat des codes de sortie : **0 si tout est en marche, 1 sinon**. Avec les quatre services du laboratoire, tu as déjà vu le 1. Avec un fichier qui n'a que `pagos` :

```text
$ revisor --config bien.toml
SERVICIO    ESTADO    TIEMPO  DETALLE
pagos       ARRIBA     102ms  200

1 servicio · 1 arriba · 0 lentos · 0 caídos · promedio 102ms
$ echo $?
0
```

Code 0. Et `revisor --help` fonctionne depuis n'importe quel dossier et montre l'aide des options avec le texte en espagnol que tu leur as mis en 11.2.3. **Le point 7 est rempli.**

Avec les sept remplis, le `revisor` est terminé au sens que le cours a défini au début. Pas parce qu'il est parfait, mais parce que ce qu'il dit faire, **il le fait et tu peux le vérifier**.

## Le projet complet

Les fichiers du dossier `fig11_05/` qui n'ont pas changé dans cette leçon sont ici pour que le dossier soit complet et puisse être lancé :

<details>
<summary>Les fichiers qui ne changent pas dans cette leçon</summary>


```toml fig11_05/servicios.toml
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
# fig11_05/laboratorio.py
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

```toml fig11_05/servicios-20.toml
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

```python
# fig11_05/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig11_05/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig11_05/src/revisor/modelo.py
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
# fig11_05/src/revisor/configuracion.py
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
# fig11_05/tests/test_modelo.py
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
# fig11_05/tests/test_configuracion.py
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

```python
# fig11_05/tests/test_revision.py
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

</details>

Et `tests/test_cli.py`, qui a changé : il a gagné le test de `--version`.

```python
# fig11_05/tests/test_cli.py
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


def test_version_dice_1_0_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as salida:
        main(["--version"])
    assert salida.value.code == 0
    assert capsys.readouterr().out == "revisor 1.0.0\n"


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

Le nouveau test utilise `capsys`, un outil de `pytest` frère de `tmp_path` et `monkeypatch` : il recueille ce que le programme **affiche** pendant le test, pour pouvoir le vérifier. Son annotation, `pytest.CaptureFixture[str]`, se lit comme celles des collections de la Leçon 4 : `CaptureFixture` est le type de cet outil, et `[str]` dit que ce qu'il recueille est du texte, comme `list[str]` dit que la liste contient des textes. `main(["--version"])` affiche `revisor 1.0.0` et termine le programme avec `SystemExit` (c'est ainsi que fonctionne `argparse` avec `--version`), de sorte que le test le reçoit avec `pytest.raises(SystemExit)` (qui vérifie que le bloc lance cette exception, et avec `as salida` te laisse la regarder) puis lit ce qui a été affiché avec `capsys.readouterr().out`. Il y a un piège dans ce test qu'il convient de connaître : le nombre `1.0.0` ne sort pas du code mais des **métadonnées du paquet installé**, donc il dépend du moment où tu as installé.

## L'erreur que tu vas voir

### `AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'`

Tu as monté la version dans `pyproject.toml` à `1.0.0`, lancé les tests et celui de `--version` est passé au rouge en disant que la version est l'ancienne :

```text
$ pytest -q --tb=short tests/test_cli.py
F..                                                                      [100%]
=================================== FAILURES ===================================
___________________________ test_version_dice_1_0_0 ____________________________
tests/test_cli.py:24: in test_version_dice_1_0_0
    assert capsys.readouterr().out == "revisor 1.0.0\n"
E   AssertionError: assert 'revisor 0.9.0\n' == 'revisor 1.0.0\n'
E     
E     - revisor 1.0.0
E     ?         ^ ^
E     + revisor 0.9.0
E     ?         ^ ^
=========================== short test summary info ============================
FAILED tests/test_cli.py::test_version_dice_1_0_0 - AssertionError: assert 'r...
1 failed, 2 passed in 0.04s
```

Lis-le de bas en haut : le test attendait `revisor 1.0.0` et le programme a dit `revisor 0.9.0`. Mais toi, tu **as déjà changé** le `pyproject.toml`. D'où vient alors le `0.9.0` ? Des métadonnées de l'installation éditable que tu as faite avant : elles sont générées à l'installation, pas quand on change le fichier. Le `pyproject.toml` est la recette ; l'installation est le plat déjà servi. La solution est de réinstaller :

```text
$ pip install -e .
$ pytest -q tests/test_cli.py
...                                                                      [100%]
3 passed in 0.02s
```

La règle : **quand tu changes quelque chose que l'installateur lit (le nom, la version, les commandes), réinstalle**. Ce n'est pas un défaut de `pip`, c'est une conséquence de ce que la version vit à un seul endroit (`pyproject.toml`), comme il a été décidé dans la Leçon 7 pour ne pas répéter le nombre dans deux fichiers.

### `bash: revisor: command not found`

Tu as installé avec `pipx`, tu ouvres un terminal et tu écris `revisor` :

```text
bash: revisor: command not found
```

La commande n'est pas trouvée parce que le dossier où `pipx` laisse les commandes (`~/.local/bin`) n'est pas dans ton `PATH`, qui est la liste des dossiers où le terminal cherche les programmes. Cela se corrige avec `pipx ensurepath` et **en ouvrant un nouveau terminal** : le changement ne s'applique qu'aux terminaux ouverts après. (Le texte exact de l'erreur change d'un terminal à l'autre ; Linux Mint peut te suggérer d'installer un paquet de ce nom, et ce n'est pas ce que tu veux.)

### `error de configuración: no existe el archivo servicios.toml`

C'est celle de la Leçon 6, et elle réapparaît en lançant `revisor` depuis un dossier sans configuration (tu l'as vu en 11.4.2). Il n'y a rien à corriger dans le code : passe `--config` avec le chemin, ou lance la commande depuis le dossier où se trouve ton `servicios.toml`.

## Ce qui se fait de travers

**Laisser la version vivre à deux endroits.** Le nombre dans `pyproject.toml` et un autre écrit à la main dans `cli.py` finissent par différer. Le `revisor` le lit dans le paquet installé. Coût : un `--version` qui ment.

**Mélanger le journal avec le rapport.** Afficher des diagnostics avec `print` entre les lignes du rapport. Coût : le script qui lit le JSON reçoit des déchets et cesse de fonctionner. Le rapport passe par la sortie standard ; le reste, par `logging` vers la sortie d'erreur.

**Configurer `logging` à l'intérieur d'un module du paquet.** Si `revision.py` appelait `basicConfig`, importer le module changerait le comportement du programme qui l'importe. Coût : deux configurations qui se battent. On configure à un seul endroit, au point d'entrée.

**Mettre `DEBUG` sur l'enregistreur de tous.** On se remplit de lignes d'`httpx` et ce qui est à toi se perd. On ne monte le niveau que sur l'enregistreur propre.

**Utiliser un `f"..."` dans un message de `logging`.** Il monte le texte même si le niveau est éteint. Coût : du travail gaspillé à chaque message, qui se remarque quand il y en a des milliers.

**Changer le format du JSON sans prévenir.** Renommer un champ, changer le `null` en un `0`, réordonner sans raison. Coût : tout ce qui lit ce JSON se casse. Si le contrat change, on monte la version majeure et on prévient.

**`subprocess` avec `shell=True` et un texte monté avec des données extérieures.** Coût : qu'un autre exécute des commandes sur ta machine.

**`eval` ou `pickle` avec des données qui ne sont pas les tiennes.** Coût : le même.

**`random` pour un secret.** Coût : un jeton qu'un autre peut reconstruire.

**Considérer comme terminé un programme que personne n'a installé comme l'installerait un utilisateur.** Il fonctionne dans l'environnement de développement et échoue à l'installation parce qu'il manque un fichier ou une dépendance. On construit la *wheel* et on l'essaie **depuis un autre dossier**, pas depuis le code.

**Ne lire que la couleur de `pytest`.** Le vert avec 2 tests sur 30 est un vert. On lit le décompte.

## Exercices

### Exercice 1 — Un vrai nom long

Écris un `servicios-largo.toml` avec deux services qui pointent vers le laboratoire : `catalogo` et un autre appelé `notificaciones-de-clientes` (26 caractères). **Avant de lancer**, prédis à quelle colonne commencera `ESTADO` et lance-le. Vérifie que le tableau est bien aligné.

### Exercice 2 — Casse le contrat

Dans une copie de `fig11_05/`, renomme dans `formato.py` le champ `"caido"` du récapitulatif du JSON en `"caidos"`. Lance `pytest -q --tb=short`. Note combien de tests passent au rouge et lequel. Répare et relance. Réponds : qu'aurait-il pu se passer avec un script qui lit `resumen.caido` si personne n'avait eu ce test ?

### Exercice 3 — Deux canaux, deux fichiers

Lance `python -m revisor --verbose` en redirigeant la sortie standard vers `reporte.txt` et celle d'erreur vers `registro.txt` (dans le shell, `> archivo` redirige la standard et `2> archivo` celle d'erreur). **Avant de lancer**, prédis ce qu'il y aura dans chaque fichier. Ensuite regarde leur contenu.

### Exercice 4 — Une ligne de journal de plus

Ajoute au `revisor` un message de niveau `DEBUG` dans `main` qui dise combien de services ont été lus dans la configuration. Il doit apparaître avec `--verbose` et pas sans lui. Vérifie que les 30 tests continuent de passer, et que `ruff` et `mypy` continuent de ne rien signaler.

## Solutions

### Solution 1

Le nom le plus long en mesure 26 ; avec les deux espaces de marge, la largeur est 28, donc `ESTADO` commence à la colonne 28 (en comptant à partir de 0). L'exécution :

```text
$ python -m revisor --config servicios-largo.toml
SERVICIO                    ESTADO    TIEMPO  DETALLE
catalogo                    ARRIBA     172ms  200
notificaciones-de-clientes  ARRIBA      94ms  200

2 servicios · 2 arriba · 0 lentos · 0 caídos · promedio 133ms
```

Le mot `ESTADO` est aligné avec `ARRIBA` sur les deux lignes, et `catalogo` a sa colonne élargie comme l'autre. Avec les services de toujours, la largeur redevient 12.

### Solution 2

**Un** test passe au rouge, `test_el_json_es_un_contrato` ; les 29 autres passent :

```text
$ pytest -q --tb=short
...............F..............                                           [100%]
=================================== FAILURES ===================================
_________________________ test_el_json_es_un_contrato __________________________
tests/test_formato.py:70: in test_el_json_es_un_contrato
    assert json.loads(reporte_a_json(CANONICOS)) == esperado
E   AssertionError: assert {'servicios':...dos': 1, ...}} == {'servicios':...ido': 1, ...}}
E     
E     Omitting 1 identical items, use -vv to show
E     Differing items:
E     {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caidos': 1, ...}} != {'resumen': {'total': 4, 'arriba': 2, 'lento': 1, 'caido': 1, ...}}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_formato.py::test_el_json_es_un_contrato - AssertionError: a...
1 failed, 29 passed in 0.04s
```

Le test te dit quel champ a changé (`'caidos': 1` contre `'caido': 1`). Sans lui, un script qui lirait `resumen.caido` aurait reçu un champ inexistant (`null` ou une erreur, selon le langage du script) et aurait continué, dans le meilleur des cas, en traitant « 0 en panne » comme un bon résultat, justement quand il y a un service en panne. C'est le genre d'erreur qui ne se montre pas avant le pire jour.

### Solution 3

Dans `registro.txt` vont les quatre lignes `DEBUG revisor: ...` (le canal d'erreur) ; dans `reporte.txt`, le tableau avec son récapitulatif (le canal standard). Aucune des deux choses ne se mélange avec l'autre :

```text
$ python -m revisor --verbose > reporte.txt 2> registro.txt
$ cat registro.txt
DEBUG revisor: reportes: CAIDO, —, sin conexión
DEBUG revisor: pagos: ARRIBA, 92ms, 200
DEBUG revisor: catalogo: ARRIBA, 158ms, 200
DEBUG revisor: inventario: LENTO, 2.3s, 200
$ cat reporte.txt
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     158ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 853ms
```

### Solution 4

Dans `cli.py`, juste avant `asyncio.run(...)` :

```python
logging.getLogger("revisor").debug("leídos %s servicios", len(servicios))
```

Le module `logging` est déjà importé. Résultat, mesuré (la nouvelle ligne sort en premier, parce qu'elle est écrite avant d'interroger quoi que ce soit) :

```text
$ python -m revisor --verbose 2>&1 >/dev/null | head -n 2
DEBUG revisor: leídos 4 servicios
DEBUG revisor: reportes: CAIDO, —, sin conexión
$ pytest -q
..............................                                           [100%]
30 passed in 0.04s
```

La première commande demande une lecture tranquille, parce que l'ordre des redirections compte et qu'elles s'appliquent de gauche à droite. `2>&1` dit « envoie la sortie d'erreur (le canal 2) là où va aujourd'hui la standard (le canal 1) », qui à ce moment-là est le tube `|` vers `head`. Ensuite, `>/dev/null` envoie la sortie **standard** à la poubelle. Résultat : ce qui arrive à `head`, c'est seulement le journal, qui sortait par le canal d'erreur, et le rapport est écarté. Et `head -n 2` ne montre que les deux premières lignes de ce qu'il reçoit. Si tu écrivais les deux redirections à l'envers, `>/dev/null 2>&1`, les deux sorties iraient à la poubelle et tu ne verrais rien.

Les 30 tests continuent de passer, et `ruff check`, `ruff format` et `mypy` ne disent rien.

## Comment savoir que j'ai réussi

- [ ] `pytest -q` dans `fig11_05/` se termine avec `30 passed`, et c'est le nombre que tu attendais.
- [ ] `ruff check`, `ruff format --check` et `mypy` ne signalent rien ; les quatre commandes donnent le même résultat avec Python 3.12 (et avec 3.14 si tu l'as).
- [ ] Avec `servicios-20.toml`, `--concurrencia 1` prend près de 10 secondes et `--concurrencia 20`, moins d'une.
- [ ] `fig11_06.py` montre six services dans leur ordre, avec `LENTO`, `error de red`, `503` et `tiempo agotado` dans leurs lignes, et aucun ne fait tomber les autres.
- [ ] Un service qui met 10 secondes avec `timeout_ms = 1000` est rapporté comme `tiempo agotado` en un peu plus d'une seconde, et un autre sans `timeout_ms` en un peu plus de cinq.
- [ ] `python -m pip wheel --no-deps -w dist .` produit `dist/revisor-1.0.0-py3-none-any.whl`, et `pipx install` de ce fichier laisse la commande `revisor`.
- [ ] Depuis un dossier qui n'est pas celui du projet, `revisor --version` dit `revisor 1.0.0`, `revisor --help` montre l'aide des options et `revisor --config servicios.toml` se termine avec `echo $?` égal à `1` (il y a des services `LENTO` et `CAIDO`) ou à `0` (tous en marche).
- [ ] Tu sais expliquer pourquoi le rapport va sur la sortie standard et le journal sur celle d'erreur ; pourquoi le JSON se teste comme un contrat ; et pourquoi `subprocess` reçoit une liste, `eval` ne s'utilise pas avec des données extérieures et les secrets sortent de `secrets`.

## Résumé

Réponds sans regarder la leçon :

1. Quelles deux choses font que le JSON du `revisor` est un contrat, et quel test le protège ?
2. Comment calcule-t-on la largeur de la première colonne ? Pourquoi, avec les quatre services canoniques, le tableau sort-il identique à celui d'avant ?
3. Quelle différence y a-t-il entre la sortie standard et la sortie d'erreur ? Pourquoi le rapport va-t-il sur l'une et le journal sur l'autre ?
4. Pourquoi un message de `logging` porte-t-il `%s` et les valeurs à part, et non une f-string ?
5. Pourquoi `basicConfig` est-il dans `cli.py` et non dans `revision.py` ? Pourquoi le niveau se met-il sur l'enregistreur `"revisor"` et non sur celui de tous ?
6. Que se passe-t-il avec `subprocess.run(f"echo {x}", shell=True)` si `x` contient un `;` ? Et avec une liste ?
7. Pourquoi `random` ne convient-il pas pour un jeton et qu'utilises-tu à la place ?
8. Que contient une *wheel* et que ne contient-elle pas ? Pourquoi installe-t-on un outil avec `pipx` et non avec `pip` dans le Python du système ?
9. Pourquoi le test de `--version` peut-il passer au rouge même si tu as changé le `pyproject.toml` ? Comment cela se corrige-t-il ?
10. Énumère, de mémoire, les sept vérifications avec lesquelles le cours se termine et la commande de chacune.

## Pour aller plus loin

- [Documentation de `logging` et son guide de base](https://docs.python.org/3/howto/logging.html) — niveaux, enregistreurs et configuration, avec le bon modèle pour les bibliothèques et les programmes. Consulté le 7 octobre 2026.
- [Guide d'empaquetage de Python : écrire le `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) et [`pipx`](https://pipx.pypa.io/stable/) — la source de tout le dernier tronçon : ce qui va dans le `pyproject.toml`, ce qu'est une *wheel* et comment s'installent les outils. Consulté le 7 octobre 2026.
- [Documentation de `subprocess` : considérations de sécurité](https://docs.python.org/3/library/subprocess.html#security-considerations) et [`secrets`](https://docs.python.org/3/library/secrets.html) — les deux avertissements officiels de 11.3 avec leurs exemples. Consulté le 7 octobre 2026.
- [Nouveautés de Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — l'interpréteur sans GIL, les *t-strings* et le reste des nouveautés, à lire quand le cours sera derrière toi. Consulté le 7 octobre 2026.
