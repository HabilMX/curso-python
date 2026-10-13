# Leçon 9 — HTTP et asyncio

**Durée :** 2 × 90 min (la première session va jusqu'à la fin de 9.2 ; la seconde couvre 9.3, 9.4 et 9.5)

**Ce que tu construis :** le `revisor` qui interroge de vrais services, l'un après l'autre, avec un délai d'attente sur chaque requête

**Ce que tu apprends :** demander une page avec `urllib` et avec `httpx` ; ce que dit un code d'état ; pourquoi toute requête porte un délai d'attente ; les coroutines (`async def`, `await`, `asyncio.run`, `async with`) ; et pourquoi un `await` seul, sans personne d'autre, ne rend rien plus rapide

**D'où tu viens.** Tu arrives avec le paquet de la [Leçon 8](08-pruebas-tipos-calidad.md) : le `revisor` avec 21 tests, ses types vérifiés et son style surveillé. Mais il y a une vérité inconfortable dans ce paquet : **il n'a jamais interrogé personne**. Les chiffres du tableau (142 ms, 2.3 s, 87 ms) sortent d'un dictionnaire, `SIMULADO`, que tu as écrit toi-même ; le programme te renvoie ce que tu lui as dit de dire. Aujourd'hui, tu le remplaces par une vraie interrogation : le `revisor` envoie une requête à chaque service, chronomètre le temps qu'il met à répondre et classe ce qu'il reçoit. Pour t'entraîner sans déranger aucun vrai service, la leçon te donne un serveur d'entraînement qui tourne sur ton propre ordinateur.

**Ce que cette leçon ne fait pas.** Elle n'interroge pas encore les services **en même temps** : elle le fait l'un après l'autre, et la leçon t'apprend à mesurer ce que cela coûte. Les réunir, c'est la [Leçon 10](10-concurrencia-pruebas-sin-red.md). Et le nouveau code, celui qui utilise le réseau, **n'a pas de test** : le projet a toujours les 21 tests de la Leçon 8, et la leçon te le dit franchement au lieu de le cacher. Tester du code réseau sans réseau est le sujet de la Leçon 10.

## À la fin, tu seras capable de

- Expliquer ce qu'est une requête HTTP, ce que contient une réponse et ce que signifient les codes d'état `2xx`, `4xx` et `5xx`.
- Demander une adresse avec `urllib.request` et avec `httpx`, et dire en quoi ils diffèrent quand le serveur répond `503` et quand il ne répond pas.
- Expliquer pourquoi `urllib` accepte une adresse `file://`, et pourquoi la validation de la Leçon 6 empêche le `revisor` de lire des fichiers de ton ordinateur.
- Mettre un délai d'attente à une requête, savoir quelle exception est lancée quand il est écoulé et laquelle quand il n'y a personne à appeler.
- Écrire une coroutine avec `async def`, l'exécuter avec `asyncio.run` et en attendre une autre avec `await`, et expliquer pourquoi appeler une coroutine ne l'exécute **pas**.
- Mesurer avec l'horloge qu'interroger les services l'un après l'autre prend la somme de leurs temps, et expliquer pourquoi un `await` seul ne l'accélère pas.
- Lire l'avertissement `coroutine ... was never awaited` et le message de `mypy` « Maybe you forgot to use "await"? ».

## Le pourquoi avant le comment

Imagine que tu demandes à un collègue de bureau si le système de paiements fonctionne. Il doit faire quelque chose de semblable à ce que fait ton navigateur quand tu ouvres une page : interroger cette machine à une adresse et attendre la réponse. La question s'appelle **requête** et la réponse, **réponse**. Toutes deux suivent un langage commun, **HTTP**, qui est celui qu'utilise tout le web. Une requête dit, en substance, « donne-moi ce qu'il y a à cette adresse » (la méthode `GET`, plus l'adresse). Une réponse apporte trois choses : un **code d'état**, un nombre à trois chiffres qui résume comment tout s'est passé ; des **en-têtes**, des données sur la réponse (de quel type de contenu il s'agit, combien il mesure) ; et un **corps**, le contenu lui-même.

Ce qui t'importe le plus dans la réponse, c'est le code, et son premier chiffre le classe. [Le standard HTTP](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes) les regroupe en cinq familles : les `1xx` sont informatifs, les `2xx` veulent dire que tout s'est bien passé (`200` est « voici »), les `3xx` sont des redirections, les `4xx` sont des erreurs de celui qui demande (`404` : cette adresse n'existe pas) et les `5xx` sont des erreurs du serveur (`503` : là, maintenant, je ne peux pas te servir). Pour le `revisor`, un service peut se terminer de **trois façons** différentes, et chacune aboutit à une ligne du tableau :

| Ce qui s'est passé | Ce que voit le `revisor` | Comment cela apparaît dans le tableau |
|---|---|---|
| Le service a répondu avec un code inférieur à 400 (`2xx`, ou un `3xx`) | un code et un temps | `ARRIBA`, ou `LENTO` s'il a mis 1000 ms ou plus |
| Il a répondu avec un code `4xx` ou `5xx` | un code et un temps | `CAIDO`, avec le code dans le détail (`503`) |
| Il n'a pas répondu | une exception : impossible de se connecter, ou le délai est écoulé | `CAIDO`, avec `sin conexión` ou `tiempo agotado` |

Les `3xx` tombent dans la première ligne exprès. Une redirection dit « ce que tu cherches est à une autre adresse », et `httpx` [ne la suit pas par défaut](https://www.python-httpx.org/quickstart/#redirection-and-history) : il renvoie la réponse telle quelle, avec son code. Pour le `revisor`, qu'un service réponde par une redirection veut dire qu'il est vivant et qu'il répond, et la règle de toujours (en panne seulement avec `400` ou plus) le compte comme en marche, avec le code dans le détail pour que tu le voies.

Ce tableau est toute la conception de la leçon. (HTTP est le style le plus courant pour que deux programmes se parlent, mais pas le seul ; si tu es curieux de savoir ce qui vient après « demander une adresse et lire ce qu'elle répond », le blog de Hábil compare deux styles dans [REST ou gRPC : quand choisir l'un ou l'autre](https://www.habil.mx/fr/blog/rest-ou-grpc-quand-choisir-chacun/).) Le reste, c'est comment faire chaque ligne sans que le programme tombe : la troisième surtout, parce qu'un service qui ne répond pas est justement le cas que le `revisor` existe pour détecter, et ça ne peut pas être le cas qui le fait tomber.

La leçon a deux moitiés. Dans la première session, tu fais une interrogation bien faite : d'abord avec la bibliothèque fournie avec Python, `urllib`, pour voir à quoi ressemble une requête de l'intérieur, puis avec `httpx`, celle qu'utilise le cours. Tu apprends que **toute requête porte un délai d'attente**. Dans la seconde session, tu arrives aux **coroutines**, l'outil de Python pour attendre sans rester planté, et tu fais interroger pour de vrai le `revisor`. C'est le plus grand saut conceptuel du cours ; c'est pourquoi le rythme de cette leçon est lent exprès.

### Le serveur d'entraînement

Le `revisor` a besoin de quelqu'un à interroger. Les noms `catalogo.example` ou `pagos.example` que tu as utilisés jusqu'ici sont des adresses inventées : le suffixe `.example` est [réservé aux exemples](https://www.rfc-editor.org/rfc/rfc2606) et n'existe jamais sur internet. Pour que chaque service réponde pour de vrai, et toujours de la même façon, la leçon inclut `laboratorio.py`, un petit serveur qui tourne **sur ton ordinateur** et fait semblant d'être les services du cours.

Voici le fichier complet. **Prends-le comme une boîte noire : on l'utilise, on ne l'écrit pas.** Il est construit avec une classe et des méthodes, des choses que ce cours n'enseigne pas, et le comprendre n'est nécessaire pour rien de ce qui suit. Copie-le tel quel dans `~/curso-python/revisor/laboratorio.py`. Quand tu auras terminé le cours, tu pourras le relire ; la bibliothèque qu'il utilise, [`http.server`](https://docs.python.org/3/library/http.server.html), fait partie de Python.

```python
# fig09_11/laboratorio.py
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

Ce qui importe en lui, c'est ce que répond chaque chemin, ce que disent le tableau `RUTAS` et la fonction `buscar_ruta`. (La classe `Servidor` ne change qu'un nombre, `request_queue_size` : combien de connexions peuvent attendre leur tour en même temps pour être servies. La valeur d'usine, 5, devient trop petite quand, dans la Leçon 10, le `revisor` ouvrira vingt connexions d'un coup, et celles qui ne tiennent pas dans la file seraient rejetées comme si le service était en panne.)

| Chemin | Ce qu'il répond | Combien de temps il met |
|---|---|---|
| `/catalogo` | `200` | 142 ms |
| `/inventario` | `200` | 2300 ms |
| `/pagos` | `200` | 87 ms |
| `/facturacion` | `503` | 95 ms |
| `/notificaciones` | `200` | 10 secondes |
| `/espera/<ms>` | `200` | les millisecondes que tu mets à la place de `<ms>` |

Ce sont les mêmes nombres que ceux du tableau du programme, maintenant produits par un vrai serveur. L'adresse est `127.0.0.1`, qui veut dire « cet ordinateur-ci », donc ce qui se passe dans la leçon ne sort pas de ta machine. Il y a une seule exception, et elle ne te concerne presque sûrement pas : si dans ton terminal un **proxy** est configuré (un intermédiaire par lequel passent les requêtes, courant dans certains réseaux de bureau, et qui se remarque parce qu'il existe des variables comme `HTTP_PROXY` ou `ALL_PROXY`, en majuscules ou en minuscules ; `env | grep -i proxy` te les montre), les requêtes vers `127.0.0.1` partent aussi vers le proxy, et la pratique échoue. `httpx` tient compte de `HTTP_PROXY`, `HTTPS_PROXY` et `ALL_PROXY` ; `urllib`, seulement des deux premières. Cela se corrige en leur disant que cette adresse ne passe pas par le proxy, avec `export NO_PROXY=127.0.0.1` dans chaque terminal où tu lances les programmes ; la [documentation de `httpx`](https://www.python-httpx.org/environment_variables/) explique ces variables. Le port `8099` est le « numéro de guichet » sur lequel il écoute. Et il y a un piège délibéré : le port **`8098` n'est servi par personne**. C'est là que vit le service `reportes` : interroger un guichet où il n'y a personne est la façon la plus fidèle de simuler un service en panne, et ça sort toujours pareil.

Avant chaque exercice de cette leçon, allume le serveur **dans un second terminal** (avec l'environnement virtuel activé, depuis `~/curso-python/revisor/`) et laisse-le ouvert :

```text
laboratorio en http://127.0.0.1:8099 (Ctrl+C para detenerlo)
```

Cette ligne est la seule chose qu'il affiche ; quand tu as fini de t'entraîner, `Ctrl`+`C` dans ce terminal l'arrête. Si par erreur tu le laisses éteint, tu verras ce qui se passe : c'est dans « L'erreur que tu vas voir ». Dans le terminal de toujours, tu continues à lancer les programmes de la leçon.

## Les concepts

### 9.1 HTTP : demander une adresse et lire ce qu'elle répond

#### 9.1.1 Avec la bibliothèque que Python fournit déjà

`urllib.request` est fourni avec Python ; il n'y a rien à installer. Sa fonction principale, [`urlopen`](https://docs.python.org/3/library/urllib.request.html), reçoit une adresse, fait la requête et renvoie la réponse sous la forme d'un objet qu'on peut utiliser avec `with` (le même `with` que dans la Leçon 6, qui ferme la connexion à la fin). Demande-lui le catalogue au serveur d'entraînement :

```python
# fig09_01.py
import time
from urllib.request import urlopen

inicio = time.perf_counter()
with urlopen("http://127.0.0.1:8099/catalogo") as respuesta:
    print(respuesta.status, respuesta.reason)
    cuerpo = respuesta.read()
print(cuerpo)
print(cuerpo.decode("utf-8"))
tardo_ms = (time.perf_counter() - inicio) * 1000
print(f"tardó 142 ms o más: {tardo_ms >= 142}")
```

```text
$ python fig09_01.py
200 OK
b'ok'
ok
tardó 142 ms o más: True
```

Ligne par ligne. `respuesta.status` est le code d'état, `200`, et `respuesta.reason` est la phrase qui l'accompagne, `OK`. `respuesta.read()` renvoie le corps, et ce qui sort à la deuxième ligne, `b'ok'`, a un `b` devant qu'il convient d'expliquer : le réseau ne transporte pas du texte mais des **octets**, des nombres de 0 à 255, et `read()` te les remet tels quels. Pour les convertir en texte, il faut dire avec quel encodage ils ont été écrits, qui est le même UTF-8 que dans la Leçon 6 : `cuerpo.decode("utf-8")` donne le `str` normal, `ok`. La dernière ligne vérifie le temps. [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) est l'horloge haute précision de Python : elle renvoie les secondes sous forme de décimal, et soustraire deux lectures donne ce qu'a duré ce qu'il y a entre elles. Le serveur prend 142 ms pour répondre au catalogue, donc la requête ne pouvait pas durer moins. Afficher le temps exact ferait que chaque exécution donnerait un nombre différent ; le `True` est ce qui ne change pas.

Remarque ce qu'il n'y a **pas** dans ce programme : aucun délai d'attente. Tu le corrigeras en 9.2, mais note-le dès maintenant comme une promesse en suspens.

#### 9.1.2 Les codes d'état, et les deux exceptions d'`urllib`

Demander le catalogue, c'est le cas heureux. Le `revisor` doit survivre aux deux autres : le service qui répond par une erreur et celui qui ne répond pas. Ce programme interroge un service de chaque type :

```python
# fig09_02.py
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DIRECCIONES = {
    "catalogo": "http://127.0.0.1:8099/catalogo",
    "facturacion": "http://127.0.0.1:8099/facturacion",
    "reportes": "http://127.0.0.1:8098/",
}

for nombre, direccion in DIRECCIONES.items():
    try:
        with urlopen(direccion) as respuesta:
            print(nombre, "respondió", respuesta.status)
    except HTTPError as error:
        print(nombre, "respondió con un error", error.code)
    except URLError as error:
        print(nombre, "no se pudo conectar:", type(error.reason).__name__)
```

```text
$ python fig09_02.py
catalogo respondió 200
facturacion respondió con un error 503
reportes no se pudo conectar: ConnectionRefusedError
```

`catalogo` est sorti comme prévu. Mais `facturacion`, qui répond `503`, **n'a pas renvoyé de réponse : il a lancé une exception**, `HTTPError`, et c'est pourquoi il est entré dans le premier `except`. C'est une décision de conception d'`urllib` qui surprend au début : pour cette bibliothèque, un code `4xx` ou `5xx` est une exception, et le code qu'elle porte se lit dans `error.code`. Et `reportes`, où personne n'écoute, a lancé `URLError`, qui apporte dans `error.reason` la vraie cause. Ici c'est `ConnectionRefusedError` (la connexion a été refusée). Remarque que le programme n'affiche que le **nom** de la cause, `type(error.reason).__name__` (`type` donne la classe de la valeur, celle de la Leçon 2, et `__name__` son nom comme texte), et non le message. Le message du système d'exploitation change d'un ordinateur à l'autre (sous Linux il dit `[Errno 111]`, sous macOS `[Errno 61]`), et le cours a décidé que le détail que montre le `revisor` ne soit jamais ce texte : il dit `sin conexión`, pareil partout.

L'**ordre** des `except` compte et c'est le même problème que dans la Leçon 6. [`HTTPError` est une sous-classe de `URLError`](https://docs.python.org/3/library/urllib.error.html) : tout `HTTPError` est aussi un `URLError`. Si tu mettais le `except URLError` en premier, il attraperait tout et le `except HTTPError` du dessous ne s'exécuterait jamais. La règle est celle de toujours : **le plus spécifique d'abord**.

#### 9.1.3 Une adresse qui n'est pas d'internet : `file://`

Il y a une surprise dans `urlopen`, et elle concerne la sécurité. Une adresse commence par un **schéma**, la partie avant `://` : `http`, `https`, et aussi `file`, qui veut dire « un fichier de cet ordinateur-ci ». `urlopen` comprend le schéma `file` :

```python
# fig09_03.py
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

archivo = Path("secreto.txt")
if archivo.exists():
    raise SystemExit("ya existe secreto.txt en esta carpeta; este ejemplo no lo pisa")
archivo.write_text("contraseña: 12345\n", encoding="utf-8")
direccion = archivo.resolve().as_uri()

with urlopen(direccion) as respuesta:
    print("urlopen leyó:", respuesta.read().decode("utf-8").strip())

esquema = urlsplit(direccion).scheme
print("esquema:", esquema, "| lo acepta el revisor:", esquema in {"http", "https"})
archivo.unlink()
```

```text
$ python fig09_03.py
urlopen leyó: contraseña: 12345
esquema: file | lo acepta el revisor: False
```

Le programme crée un fichier `secreto.txt` (et le supprime à la fin avec `unlink()`, pour ne rien laisser). Comme il va l'écraser puis le supprimer, il demande d'abord s'il en existe déjà un avec ce nom : s'il existe, il s'arrête sans y toucher, avec `raise SystemExit(...)`, la même exception que dans la Leçon 7, qui porte cette fois un texte au lieu d'un nombre ; Python affiche ce texte sur la sortie d'erreur et termine avec le code 1. Ensuite il prend le chemin absolu du fichier avec `resolve()`, construit son adresse avec [`.as_uri()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.as_uri) (qui produit quelque chose comme `file:///home/tu/secreto.txt`) et la donne à `urlopen`, qui **le lit sans protester**. C'est une fonction légitime, mais imagine le `revisor` lisant les adresses d'un `servicios.toml` qu'une autre personne a écrit, et que quelqu'un mette `file:///etc/passwd` à la place de l'adresse d'un service : le programme lirait le fichier et le traiterait comme une « réponse ». C'est pourquoi, dans la Leçon 6, la validation exigeait que le schéma soit `http` ou `https`, avec [`urlsplit(url).scheme`](https://docs.python.org/3/library/urllib.parse.html) dans `{"http", "https"}` ; la dernière ligne de ce programme fait cette même vérification et répond `False` pour `file`. Ce n'est pas un détail de style : **l'adresse que quelqu'un d'autre écrit ne se remet pas à une bibliothèque sans vérifier où elle pointe**. C'est la deuxième fois que tu vois l'idée, et dans la Leçon 11 tu la reverras.

#### 9.1.4 Pourquoi le cours passe à `httpx`

`urllib` fait l'affaire, mais la documentation même de Python [recommande un autre outil pour quelque chose de plus commode](https://docs.python.org/3/library/urllib.request.html) (« The Requests package is recommended for a higher-level HTTP client interface »). Ce cours utilise [`httpx`](https://www.python-httpx.org/), pour quatre raisons concrètes que tu verras dans cette leçon :

| | `urllib.request` | `httpx` |
|---|---|---|
| Un `503` | lance une exception | est une réponse normale, avec son code |
| Délai d'attente par défaut | aucun | 5 secondes |
| Façons de l'utiliser | seulement synchrone (une chose à la fois) | synchrone **et** asynchrone, avec la même interface |
| Une adresse `file://` | la lit | la rejette |

`httpx` n'est pas fourni avec Python, mais tu l'as déjà : tu l'as installé dans l'environnement virtuel dans la Leçon 1, et à partir d'aujourd'hui c'est la seule dépendance du `revisor`. Compare avec le programme d'`urllib` :

```python
# fig09_04.py
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/facturacion")
print(respuesta.status_code, respuesta.reason_phrase)
print("es un error:", respuesta.is_error)

try:
    respuesta.raise_for_status()
except httpx.HTTPStatusError as error:
    print("raise_for_status avisó:", error.response.status_code)

try:
    httpx.get("file:///etc/hosts")
except httpx.UnsupportedProtocol as error:
    print("httpx no lo permite:", error)
```

```text
$ python fig09_04.py
503 Service Unavailable
es un error: True
raise_for_status avisó: 503
httpx no lo permite: Request URL is missing an 'http://' or 'https://' protocol.
```

Le `503` **n'a rien lancé** : `httpx.get` a renvoyé une réponse comme n'importe quelle autre, avec `status_code`, `reason_phrase` et un `is_error` qui vaut `True` pour les codes `4xx` et `5xx`. Si tu préfères qu'une erreur devienne une exception, il existe `raise_for_status()`, qui lance `httpx.HTTPStatusError` ; le programme le démontre, mais le `revisor` ne l'utilisera pas. Un `503` n'est pas un échec du `revisor` : c'est la **donnée** que le `revisor` est venu recueillir. Le traiter comme une exception le sortirait du chemin normal et obligerait à l'attraper pour le remettre là où il était. Et la dernière partie confirme la quatrième ligne du tableau : `httpx` rejette `file://` avec `UnsupportedProtocol`. Une défense de plus, qui ne remplace pas la validation de la Leçon 6.

### 9.2 Délai d'attente : aucune requête n'attend pour toujours

Il y a une question que nous n'avons pas posée : que se passe-t-il si le service **accepte** la connexion et ne répond pas ? Il ne la rejette pas, il ne la ferme pas : il reste simplement à réfléchir. Ton programme reste là, planté, jusqu'à ce que quelque chose change. Si ce « quelque chose » est une panne réseau ou un service bloqué, cela peut être **pour toujours**. Le `revisor` existe pour détecter les services bloqués ; un `revisor` qui se bloque avec eux est pire que de ne pas avoir de `revisor`. C'est pourquoi la règle de ce cours est une seule :

> **Toute requête porte un délai d'attente. Sans exception.**

Regarde comment est `urllib` par défaut. La première ligne du programme affiche le délai d'attente global de Python ; ensuite il demande `/notificaciones`, qui met 10 secondes, mais cette fois avec `timeout=1`, une seconde :

```python
# fig09_05.py
import socket
from urllib.request import urlopen

print("tiempo límite global:", socket.getdefaulttimeout())

try:
    urlopen("http://127.0.0.1:8099/notificaciones", timeout=1)
except TimeoutError as error:
    print("se acabó el tiempo:", error)
```

```text
$ python fig09_05.py
tiempo límite global: None
se acabó el tiempo: timed out
```

[`socket.getdefaulttimeout()`](https://docs.python.org/3/library/socket.html#socket.getdefaulttimeout) renvoie `None` : la bibliothèque standard, par défaut, **n'a aucun délai d'attente** (la documentation d'[`urlopen`](https://docs.python.org/3/library/urllib.request.html) dit qu'elle utilise la valeur globale). Sans `timeout=`, cette requête aurait attendu dix secondes ; contre un serveur qui ne répond jamais, elle ne se serait pas terminée. Avec `timeout=1`, l'attente a été coupée à la seconde et Python a lancé `TimeoutError`.

`httpx`, en revanche, a un délai d'attente de 5 secondes : [la documentation](https://www.python-httpx.org/advanced/timeouts/) dit qu'il « lance une `TimeoutException` après 5 secondes d'inactivité sur le réseau ». Remarque deux mots : *inactivité*, pas temps total. Il y a quatre délais d'attente distincts : pour **se connecter** (`connect`), pour **recevoir** un morceau de la réponse (`read`), pour **envoyer** (`write`) et pour **obtenir** une connexion libre du groupe (`pool`). Chacun compte combien attend *une opération*, pas combien dure tout l'échange : un serveur qui goutte un octet toutes les 4 secondes ne déclenche jamais le `read` de 5 secondes même si la réponse prend des heures. Le plafond total par service, tu le mettras dans la Leçon 10 avec `asyncio.timeout()` ; aujourd'hui, celui de chaque opération suffit. Un seul nombre dans `httpx.Timeout(1.0)` fixe les quatre à une seconde.

```python
# fig09_06.py
import httpx

print("httpx, por omisión:", httpx.Client().timeout)
limite = httpx.Timeout(1.0)

try:
    httpx.get("http://127.0.0.1:8099/notificaciones", timeout=limite)
except httpx.ReadTimeout:
    print("notificaciones: tiempo agotado")

try:
    httpx.get("http://127.0.0.1:8098/", timeout=limite)
except httpx.ConnectError:
    print("reportes: sin conexión")

print(issubclass(httpx.ReadTimeout, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.TimeoutException))
print(issubclass(httpx.ConnectError, httpx.HTTPError))
```

```text
$ python fig09_06.py
httpx, por omisión: Timeout(timeout=5.0)
notificaciones: tiempo agotado
reportes: sin conexión
True
False
True
```

La première ligne montre la valeur par défaut de `httpx` (`Timeout(timeout=5.0)`). Ensuite, deux requêtes avec un délai d'attente d'une seconde, et chacune se termine par une exception **différente**, ce qui est justement ce que le `revisor` doit distinguer :

- `/notificaciones`, qui met dix secondes, a lancé `httpx.ReadTimeout` : la connexion s'est établie, mais le service n'a pas répondu à temps. C'est la cause de « tiempo agotado » (délai dépassé).
- Le port 8098, où personne n'écoute, a lancé `httpx.ConnectError` : il n'y avait personne à qui se connecter. C'est la cause de « sin conexión » (sans connexion).

Les trois dernières lignes, avec `issubclass` (qui demande si une classe est fille d'une autre), confirment la hiérarchie [que documente `httpx`](https://www.python-httpx.org/exceptions/) : `ReadTimeout` est une `TimeoutException` ; `ConnectError` ne l'est **pas** ; et `ConnectError` est bien un `HTTPError`, la classe mère de presque tout ce que `httpx` peut lancer. Cela décide l'ordre des `except` du `revisor` : d'abord `TimeoutException`, puis `ConnectError`, et à la fin `HTTPError` pour ramasser ce qui reste (un serveur qui ferme au milieu d'une réponse, par exemple). Les trois branches renvoient un `Resultado` avec l'état `CAIDO` et son détail (`tiempo agotado`, `sin conexión` ou `error de red`). **Elles ne laissent jamais s'échapper l'exception.**

D'où vient le nombre : chaque `Servicio` porte son `timeout_ms`, par défaut 5000, en millisecondes. `httpx` veut des secondes, donc le `revisor` divise : `httpx.Timeout(servicio.timeout_ms / 1000)`. L'unité vit dans le nom (`timeout_ms`) précisément pour que cette conversion ne soit pas oubliée. **La première session s'arrête ici.**

### 9.3 Coroutines : des fonctions qui peuvent attendre

#### 9.3.1 Une coroutine ne s'exécute pas quand on l'appelle

Dans la seconde session arrive l'idée la plus difficile. Pendant les 2.3 secondes que met `inventario` à répondre, ton programme ne fait rien : il attend. Tout ce temps, le processeur est libre. Une **coroutine** est une fonction qui peut **se mettre en pause à l'endroit où elle attend** et laisser autre chose utiliser ce temps. Elle s'écrit avec `async def`, au lieu de `def` :

```python
# fig09_07.py
async def saludar() -> str:
    return "hola"


print(saludar())
print("listo")
```

```text
$ python fig09_07.py
<coroutine object saludar at 0x...>
fig09_07.py:6: RuntimeWarning: coroutine 'saludar' was never awaited
  print(saludar())
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
listo
```

`saludar` est une fonction normale en tout sauf dans son premier mot. Mais remarque ce qu'a affiché `print(saludar())` : il ne dit **pas** `hola`. Il dit `<coroutine object saludar at 0x...>`. Appeler une fonction `async def` n'exécute pas son corps ; cela crée un **objet coroutine**, une recette en pause. [La documentation d'`asyncio`](https://docs.python.org/3/library/asyncio-task.html) le dit ainsi : appeler une coroutine ne la planifie pas pour l'exécution, et dans son exemple `nested()` est appelée sans être attendue : l'objet est créé, mais le corps « ne s'exécutera pas du tout ». Et comme l'objet a été jeté à la poubelle sans que personne l'exécute, Python prévient : `RuntimeWarning: coroutine 'saludar' was never awaited`, « la coroutine `saludar` n'a jamais été attendue ». L'avertissement inclut la ligne du programme où elle a été appelée et c'est **le signal le plus courant** que tu as oublié un `await`.

#### 9.3.2 `asyncio.run` : le démarrage

Comment exécute-t-on alors une coroutine ? Il lui faut un coordinateur qui la fasse tourner, la **boucle d'événements** (*event loop*) : un petit programme, à l'intérieur de Python, qui répartit le temps entre les coroutines en pause. Tu ne la manipules pas directement. [`asyncio.run`](https://docs.python.org/3/library/asyncio-runner.html) la crée, exécute la coroutine que tu lui donnes jusqu'à ce qu'elle se termine, renvoie son résultat et ferme la boucle :

```python
# fig09_08.py
import asyncio


async def saludar() -> str:
    return "hola"


print(asyncio.run(saludar()))
```

```text
$ python fig09_08.py
hola
```

Cette fois oui : `hola`. `asyncio.run` s'écrit une seule fois, à l'entrée du programme, et à partir de là tout le reste s'enchaîne avec `await`. Dans le `revisor`, il sera dans `cli.py`.

#### 9.3.3 `await` et `async with` : attendre une autre coroutine

À l'intérieur d'une coroutine, `await` signifie **« attends ici que cette autre chose se termine, et pendant que tu attends, laisse la boucle faire d'autres choses »**. C'est la façon explicite de mettre une coroutine en pause, et elle ne fonctionne qu'à l'intérieur d'une fonction `async def`. (Il y en a deux autres, qui attendent sans que tu écrives le mot : `async with`, que tu verras dans un instant, et `async for`, que le cours n'utilise pas ; [la référence du langage](https://docs.python.org/3/reference/compound_stmts.html#the-async-with-statement) explique qu'à l'intérieur ils font `await`.) La coroutine que tu attendras le plus dans le cours est une requête d'`httpx`, et pour cela `httpx` fournit [une version asynchrone du client](https://www.python-httpx.org/async/), `httpx.AsyncClient`, qui s'utilise avec un `async with` :

```python
# fig09_09.py
import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get("http://127.0.0.1:8099/pagos")
        print(respuesta.status_code)


asyncio.run(main())
```

```text
$ python fig09_09.py
200
```

`async with` est le `with` de la Leçon 6 pour des ressources dont l'ouverture et la fermeture **peuvent aussi** attendre : créer et fermer le client réseau est une opération de ce genre. À l'intérieur, `cliente.get(...)` est une coroutine ; `await` l'attend, et ce qu'on obtient, c'est la réponse. Remarque que la réponse est exactement la même que dans le `httpx.get` synchrone : `status_code`, `is_error` et le reste. La différence est dans la façon d'attendre. Et le client **se crée une fois et se réutilise** pour plusieurs requêtes : en ouvrir et en fermer un par interrogation, ce serait comme raccrocher et recomposer le numéro chaque fois que tu poses une question.

### 9.4 Un `await` après l'autre n'économise pas de temps : la série

Voici le malentendu le plus répandu sur `asyncio`, et il convient de le démonter avec une mesure. Un débutant lit « asynchrone » et suppose « plus rapide ». Ça ne l'est pas. Regarde ce programme, qui attend trois fois une demi-seconde, l'une après l'autre, chacune avec `await` ([`asyncio.sleep`](https://docs.python.org/3/library/asyncio-task.html#sleeping) est l'attente asynchrone de toujours) :

```python
# fig09_10.py
import asyncio
import time


async def esperar(nombre: str, segundos: float) -> str:
    await asyncio.sleep(segundos)
    return f"{nombre} esperó {segundos} s"


async def main() -> None:
    inicio = time.perf_counter()
    for nombre in ("catalogo", "inventario", "pagos"):
        print(await esperar(nombre, 0.5))
    total = time.perf_counter() - inicio
    print(f"en serie tarda la suma, 1.5 s o más: {1.5 <= total < 2.0}")


asyncio.run(main())
```

```text
$ python fig09_10.py
catalogo esperó 0.5 s
inventario esperó 0.5 s
pagos esperó 0.5 s
en serie tarda la suma, 1.5 s o más: True
```

La dernière ligne demande `1.5 <= total < 2.0`, les deux choses à la fois : que `total` soit au moins 1.5 et moins de 2. Les trois attentes ont pris la **somme** : 1.5 seconde ou plus. Tu n'as rien gagné. La raison est dans ce que `await` fait vraiment : il met **cette** coroutine en pause et offre à la boucle de s'occuper d'autres, mais dans ce programme **il n'y en a pas d'autres**. La boucle offre le tour et personne ne le prend. C'est la même [séquence que montre la documentation de Python](https://docs.python.org/3/library/asyncio-task.html) : un `await` suivi d'un autre `await` s'exécute en série. Pour gagner du temps, il faut **plusieurs coroutines vivantes en même temps**, et cela s'obtient avec des tâches (`asyncio.TaskGroup`), qui est le contenu de la Leçon 10.

Le `revisor` d'aujourd'hui sera donc une version asynchrone qui se comporte **comme la synchrone** : elle interroge les services un par un. À quoi bon, alors ? D'abord, parce que c'est l'étape intermédiaire qui rend le gain visible : la Leçon 10 mesure le même tableau de services en série et en parallèle, et elle a besoin du point de départ. Ensuite, parce que passer de `def` à `async def` touche toute la chaîne d'appels, et c'est plus facile à comprendre en le faisant avant d'introduire la concurrence. Et enfin, parce que ce qui importe dans cette étape, c'est tout ce qui n'a rien à voir avec le temps : délais d'attente, exceptions, classification.

### 9.5 Le `revisor` interroge pour de vrai

Avec tout ce qui précède, `revision.py` se réécrit entièrement. On supprime `SIMULADO`, et les deux fonctions deviennent des coroutines :

```python
# fig09_11/src/revisor/revision.py
import time

import httpx

from revisor.modelo import Estado, Resultado, Servicio, clasificar


async def revisar(cliente: httpx.AsyncClient, servicio: Servicio) -> Resultado:
    limite = httpx.Timeout(servicio.timeout_ms / 1000)
    inicio = time.perf_counter()
    try:
        respuesta = await cliente.get(servicio.url, timeout=limite)
    except httpx.TimeoutException:
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


async def revisar_todos(servicios: list[Servicio]) -> list[Resultado]:
    resultados: list[Resultado] = []
    async with httpx.AsyncClient() as cliente:
        for servicio in servicios:
            resultados.append(await revisar(cliente, servicio))
    return resultados
```

Lis `revisar` de haut en bas. Elle reçoit un **client** et un **service** ; le client vient de l'extérieur pour qu'il soit réutilisé. Elle monte le `httpx.Timeout` avec le `timeout_ms` du service, note l'heure avec `time.perf_counter()` (l'horloge haute précision de Python) et fait la requête avec `await`. Les trois premiers `except` sont ceux de 9.2, **du plus spécifique au plus général**, et chacun renvoie un `Resultado` en panne avec son texte. Le quatrième attrape quelque chose qui n'est pas une erreur réseau : une adresse qui a passé la validation de la Leçon 6 mais que `httpx` ne peut pas utiliser. Cela arrive, par exemple, avec `http://999.1.1.1:8099/pagos` : pour `urlsplit`, c'est une adresse avec un serveur et un port, mais chacune des quatre parties d'une adresse IP va de 0 à 255, et 999 ne tient pas, et `httpx` la rejette avec `httpx.InvalidURL`, qui n'est **pas** fille de `httpx.HTTPError` (c'est ce que dit [sa hiérarchie d'exceptions](https://www.python-httpx.org/exceptions/)). D'autres noms de serveur impossibles se terminent par un `ValueError` des bibliothèques qu'`httpx` utilise en interne. Sans ce `except`, un seul de ces services ferait tomber le rapport entier avec un *traceback* ; avec lui, il sort dans sa ligne comme `CAIDO`, avec le détail `dirección inválida`, et les autres sont vérifiés quand même. Le `ValueError` est attrapé ici, autour d'un seul appel, et non dans tout le programme : un `ValueError` de ton propre code, hors du `try`, continuerait de l'arrêter avec son rapport, comme il se doit. S'il n'y a pas eu d'exception, elle mesure combien de temps s'est écoulé (`round(... * 1000)` convertit les secondes en millisecondes entières), classe avec la même fonction `clasificar` de toujours, qui reçoit le vrai code, et monte le `Resultado` avec le code comme détail. Un `503` passe par ici : ce n'est pas une exception, il sort avec `clasificar(503, 95)` et devient `CAIDO` avec le détail `503`.

`revisar_todos` ouvre **un** client avec `async with` et parcourt les services avec un `for` et un `await` par tour. C'est la série de 9.4, écrite exprès. L'ordre des résultats est celui de la configuration.

`main` dans `cli.py` ne change que sur une ligne : l'appel est enveloppé dans `asyncio.run`.

```python
# fig09_11/src/revisor/cli.py
import argparse
import asyncio
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

    resultados = asyncio.run(revisar_todos(servicios))
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

Pour qu'`asyncio.run` ait quelque chose à exécuter, `revisar_todos(servicios)` sans `await` produit une coroutine, et `asyncio.run` la fait tourner. C'est le seul `asyncio.run` du programme. Les tests continuent d'appeler `main` comme une fonction normale, donc **ils n'ont pas besoin d'être des coroutines** ; c'est ce qui permet de n'installer aucun plugin de `pytest` pour le code asynchrone. Les autres changements sont des données. Le `pyproject.toml` monte à `0.8.0` et déclare la première dépendance du paquet, `httpx` :

```toml
dependencies = ["httpx>=0.28"]
```

Réinstalle le paquet (`pip install -e .`) pour que l'environnement voie la dépendance et la nouvelle version. Et le `servicios.toml` pointe maintenant vers le serveur d'entraînement : les mêmes quatre noms, d'autres adresses. (Le projet complet est en 9.6.)

```toml fig09_11/servicios.toml
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

Avec le serveur d'entraînement ouvert dans l'autre terminal, lance le `revisor` et regarde le code de sortie :

```text
$ cd fig09_11
$ python -m revisor
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     155ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      94ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 852ms
$ echo $?
1
```

C'est le tableau du programme, maintenant **mesuré** : `catalogo` et `pagos` en marche avec de vrais temps (le serveur attend 142 et 87 ms, et chaque requête ajoute quelques millisecondes de réseau, donc tu verras des nombres comme 156 et 98, différents à chaque exécution), `inventario` lent avec 2.3 s, `reportes` en panne avec `sin conexión` (personne n'écoute sur le 8098). Le récapitulatif compte deux en marche, un lent, un en panne, et le code de sortie est `1`, le même de toujours, pour la même raison : il y a un lent et un en panne. Ce qui a changé, c'est que maintenant c'est vrai.

Combien de temps cela prend-il ? En série, la somme : 142 + 2300 + 87 font environ 2.5 secondes d'attente plus le temps que met Python à démarrer et à charger `httpx`. Mesurée avec la commande `time` du terminal, une exécution complète dure environ 2.7 secondes. La tienne donnera un nombre proche, pas égal. Ce chiffre est le point de départ de la Leçon 10. L'Exercice 1 le mesure.

Et les tests : lance-les.

```text
$ cd fig09_11
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

Il y en a toujours **21**. Le seul fichier de tests qui a changé est `tests/test_cli.py`, et pas par caprice. Son premier test utilisait les données simulées pour vérifier que `main` renvoie `1`, et elles n'existent plus ; et les fonctions fausses du `monkeypatch` renvoient maintenant une coroutine, parce que la vraie est une coroutine et que `main` fait `asyncio.run` de ce qu'on lui renvoie. C'est pourquoi elles sont `async def` :

```python
# fig09_11/tests/test_cli.py
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
    async def todos_caidos(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.CAIDO, None, "sin conexión") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_caidos)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 1


def test_con_todos_arriba_sale_con_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def todos_arriba(servicios: list[Servicio]) -> list[Resultado]:
        return [Resultado(s, Estado.ARRIBA, 100, "200") for s in servicios]

    monkeypatch.setattr("revisor.cli.revisar_todos", todos_arriba)
    archivo = tmp_path / "servicios.toml"
    archivo.write_text(CONFIGURACION, encoding="utf-8")
    assert main(["--config", str(archivo)]) == 0
```

Un avertissement qu'il faut dire à voix haute : **`21 passed` s'affiche et pourtant le nouveau code n'a pas un seul test**. Rien de ce que tu viens d'écrire (le délai d'attente, la classification d'un `503`, le `sin conexión`) n'est exercé dans ces 21. Les deux tests de `test_cli.py` remplacent `revisar_todos` en entier, donc le code réseau n'est même pas touché. Voilà la taille du trou, et c'est la raison de la Leçon 10 : comment tester du code réseau sans réseau.

### 9.6 Le projet complet

L'instantané du projet à la fin de la leçon. Les fichiers que tu as déjà vus sont `laboratorio.py`, `servicios.toml`, `revision.py`, `cli.py` et `tests/test_cli.py`. Le `pyproject.toml` est celui de la Leçon 8 avec la version et la nouvelle dépendance :

```toml fig09_11/pyproject.toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "revisor"
version = "0.8.0"
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

Les autres fichiers **ne changent pas** par rapport à la Leçon 8, et sont répétés ici seulement pour que le projet soit complet :

```python
# fig09_11/src/revisor/__init__.py
"""Revisa el estado de una lista de servicios y entrega un reporte."""
```

```python
# fig09_11/src/revisor/__main__.py
from revisor.cli import main

raise SystemExit(main())
```

```python
# fig09_11/src/revisor/modelo.py
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
# fig09_11/src/revisor/formato.py
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
# fig09_11/src/revisor/configuracion.py
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
# fig09_11/tests/test_modelo.py
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
# fig09_11/tests/test_formato.py
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
# fig09_11/tests/test_configuracion.py
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

Les quatre vérifications de la Leçon 8, qui couvrent maintenant aussi le code asynchrone :

```text
$ cd fig09_11
$ ruff format --check
12 files already formatted
$ ruff check
All checks passed!
$ mypy
Success: no issues found in 11 source files
$ pytest -q
.....................                                                    [100%]
21 passed in 0.03s
```

## L'erreur que tu vas voir

### `RuntimeWarning: coroutine 'saludar' was never awaited`

Tu l'as vue en 9.3.1, avec le programme `fig09_07.py`, et il vaut la peine de répéter comment elle se lit. L'avertissement n'est pas une erreur : le programme **continue** et se termine avec le code `0`, ce qui est le danger, parce qu'il y a un avertissement parmi des dizaines de lignes et qu'il est facile de le laisser passer. Il dit trois choses : le fichier et la ligne où tu as appelé la coroutine sans l'attendre (`fig09_07.py:6`, et dessous il affiche la ligne elle-même, `print(saludar())`), quelle coroutine c'était (`'saludar'`), et la conséquence : son corps ne s'est jamais exécuté. Le remède est presque toujours un mot : mettre `await` devant l'appel, ou la passer à `asyncio.run`.

Dans le projet, `mypy` te prévient **avant** d'exécuter. Retire le `await` de la ligne `resultados.append(await revisar(cliente, servicio))` dans `revisar_todos`, et voici ce que dit `mypy` :

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
Found 1 error in 1 file (checked 11 source files)
```

Tu avais dit à la liste qu'elle gardait des `Resultado`, et tu lui donnes une `Coroutine`. Et `mypy` le devine avec une note : « As-tu oublié le `await` ? ». C'est le genre d'aide pour laquelle on a écrit les types dans la Leçon 8. Si tu ignores l'avertissement et que tu lances le programme, le tableau affiche son en-tête et s'arrête avec `AttributeError: 'coroutine' object has no attribute 'servicio'` (la dernière ligne du *traceback*), suivie du même `RuntimeWarning` à la fin.

### Tous les services disent `sin conexión`

Si tu oublies d'allumer le serveur d'entraînement, le `revisor` ne tombe pas ; il fait exactement ce qu'il doit. Voici ce qu'il affiche avec le serveur éteint :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    CAIDO          —  sin conexión
inventario  CAIDO          —  sin conexión
pagos       CAIDO          —  sin conexión
reportes    CAIDO          —  sin conexión

4 servicios · 0 arriba · 0 lentos · 4 caídos · promedio —
```

Il n'y a pas de `Traceback`. Les quatre services sont `CAIDO`, avec `sin conexión` et sans temps (`—`), parce que personne ne répond sur le port 8099, comme sur le 8098. C'est la conception qui fonctionne : un service qui ne répond pas est une **donnée**, pas une exception qui fait tomber le rapport. Le signal pour toi est que `reportes` ne devrait pas être le seul en panne : si les quatre le sont, avant de chercher une erreur dans ton code, regarde si le second terminal est toujours ouvert. (Remarque aussi la moyenne : elle sort comme `—`, comme le temps de chaque ligne, parce qu'il n'y a pas de temps à moyenner. C'est la même décision que dans la Leçon 2 : ce qui n'a pas été mesuré ne vaut pas `0`.)

### Le test qui casse parce que son faux a cessé d'être une coroutine

Si tu laisses `tests/test_cli.py` comme il était dans la Leçon 8, et que tu ne changes que `revision.py` et `cli.py`, `pytest -q` dit `1 failed, 20 passed`. Le rouge est le test qui utilise le faux avec `def` au lieu de `async def`. La dernière ligne de l'erreur change de formulation selon ta version de Python, mais dit la même chose :

```text
ValueError: a coroutine was expected, got [Resultado(servicio=Servicio(nombre='catalogo', ...
```

(en Python 3.12) ou

```text
TypeError: An asyncio.Future, a coroutine or an awaitable is required
```

(en 3.14). `asyncio.run(...)` a reçu une **liste** et attendait une coroutine, parce que `main` fait `asyncio.run(revisar_todos(servicios))` et que le faux, étant `def`, a renvoyé le résultat directement. La correction est celle que tu as vue : rendre le faux `async def`.

Mais il y a quelque chose de plus subtil. Un **second** vieux test, celui qui tournait avec les données simulées, **reste au vert**, et il ne devrait pas. Ce test utilisait des adresses `https://catalogo.example` et attendait que `main` renvoie `1`. Maintenant `main` fait de vraies requêtes vers ces adresses inventées, n'arrive à se connecter à aucune, les marque toutes en panne et renvoie `1`. Le test passe, mais **pour une raison complètement différente** de celle pour laquelle il a été écrit, et il dépend de ce que `.example` ne se résolve jamais et de ce que ton réseau réponde vite que ça n'existe pas. C'est ce qui arrive quand un test vert soutient quelque chose qui n'est plus ce qu'il dit : on a remplacé le faux par un test qui ne fait pas ce que son nom promet. C'est pourquoi il a été réécrit avec un faux explicite.

## Ce qui se fait de travers

**Faire une requête sans délai d'attente.** C'est l'erreur que cette leçon existe pour éviter. Avec `urllib`, sans `timeout=`, le programme attend ce qu'il faut, y compris pour toujours. Avec `httpx`, la limite par défaut est de 5 s, mais dépendre d'une valeur par défaut sans le savoir, c'est laisser une décision importante aux mains d'un autre. Le `revisor` la fixe toujours, par service.

**Attraper `Exception` et continuer.** `except Exception: pass` autour d'une requête fait qu'un `ReadTimeout`, un `ConnectError` et une erreur de programmation se voient identiques : rien. Le `revisor` attrape trois exceptions précises, chacune avec son texte, et laisse toute autre se voir.

**Afficher le message du système d'exploitation.** `[Errno 111] Connection refused` change avec le système et avec la langue ; le rapport d'un service ne doit pas changer de texte selon l'endroit où il s'exécute. Le détail est l'une de trois phrases fixes.

**Supposer qu'`async` est plus rapide.** Tu l'as démonté en 9.4 : un `await` après l'autre additionne leurs temps. Une fonction `async` sans concurrence est une fonction synchrone avec plus de cérémonie.

**Appeler une coroutine sans `await`.** L'avertissement de 9.3.1. Avec `mypy` en mode strict, cela devient une erreur de types, c'est pourquoi il convient de le lancer.

**Bloquer à l'intérieur d'une coroutine.** Un `time.sleep(1)` à l'intérieur d'une `async def` arrête **tout** le programme une seconde : personne d'autre ne peut avancer, parce que la boucle est coincée dans cet appel. À l'intérieur d'une coroutine, l'attente est `await asyncio.sleep(1)`. Même chose pour les bibliothèques réseau qui ne sont pas asynchrones, comme `urllib` ou `httpx.get`.

**Créer un client par requête.** `httpx.AsyncClient()` ouvre un groupe de connexions qui sont réutilisées. En ouvrir et en fermer un à chaque interrogation jette cette économie ; le `revisor` en ouvre un au début de `revisar_todos` et le partage.

**Traiter un `503` comme s'il était une panne du programme.** Un service qui répond par une erreur est le résultat du travail, pas un incident du `revisor`. C'est pourquoi on lit le code et on classe ; `raise_for_status()` transformerait la donnée en exception.

**Mettre `0` là où il n'y a pas eu de réponse.** Un service en panne a `tiempo_ms=None`, pas `0` : avec zéro, la moyenne récompense celui qui est en panne. C'est la même leçon que dans la Leçon 2, dans un projet plus grand.

## Exercices

### Exercice 1 — Mesure la série avec l'horloge

Avec le serveur d'entraînement allumé, mesure combien de temps met le `revisor` complet : `time python -m revisor`. Avant de le lancer, **prédis** le nombre à partir de ce que tu sais : la somme de ce que met chaque service. Lance-le trois fois et note les trois dans ton journal de bord. Pourquoi ne sont-elles pas identiques ? Ce nombre est ton point de départ pour la Leçon 10.

### Exercice 2 — Retire le délai d'attente à une requête et vois pourquoi c'est dangereux

Écris un programme de six lignes qui utilise `httpx.get` avec `timeout=None` (qui [désactive le délai d'attente](https://www.python-httpx.org/advanced/timeouts/)) contre `http://127.0.0.1:8099/espera/60000`, qui met une minute. Lance-le, laisse passer cinq secondes et appuie sur `Ctrl`+`C`. Qu'est-ce qui s'affiche ? Combien de temps aurait-il mis à se terminer seul ? Ensuite mets-lui `timeout=2.0` et compare.

### Exercice 3 — Les deux services de plus

Ajoute à ton `servicios.toml` `facturacion` (`http://127.0.0.1:8099/facturacion`) et `notificaciones` (`http://127.0.0.1:8099/notificaciones`, avec `timeout_ms = 1000`). Avant de lancer, prédis l'état et le détail de chacun, et quelle sera la ligne du récapitulatif. Quelque chose te paraît-il bizarre dans le tableau ? Remets le fichier à ses quatre services à la fin.

### Exercice 4 — Oublie un `await` exprès

Dans `revisar_todos`, retire le `await` de `resultados.append(await revisar(cliente, servicio))`. Lance `mypy`, puis `python -m revisor`, et lis les deux signaux : que dit chacun, et lequel est arrivé en premier. Remets le `await`.

## Solutions

### Solution 1

La prédiction : 142 + 2300 + 87 = 2529 ms pour les trois qui répondent, plus ce que met la tentative de connexion avec `reportes` (quelques millisecondes, parce qu'ils refusent immédiatement), plus le démarrage de Python et d'`httpx`. Cela donne environ **2.6 ou 2.7 secondes**, et c'est ce que mesure l'horloge : une exécution de référence a donné 2.674 s. Les trois exécutions sont semblables mais pas identiques parce que le serveur, le système d'exploitation et le réseau ajoutent de petites variations de quelques millisecondes à chaque fois. L'important est l'ordre de grandeur : environ 2.5 secondes, parce que **c'est la somme**. Si la Leçon 10 réussit à le rapprocher de 2.3 s (le service le plus lent), elle aura gagné moins qu'il n'y paraît avec quatre services ; c'est pourquoi la mesure forte de cette leçon en utilise vingt.

### Solution 2

```python
import httpx

respuesta = httpx.get("http://127.0.0.1:8099/espera/60000", timeout=None)
print(respuesta.status_code)
```

Avec `Ctrl`+`C` à cinq secondes, Python affiche un *traceback* qui se termine par `KeyboardInterrupt` : c'est toi qui as interrompu, pas le programme. Il aurait mis **une minute entière** à se terminer seul, sans rien afficher entre-temps. Contre un serveur qui ne répond jamais, il ne se serait jamais terminé : c'est ce que signifie « sans délai d'attente ». Avec `timeout=2.0`, le programme lance `httpx.ReadTimeout` au bout de deux secondes. Ce `ReadTimeout` est une exception **qu'on peut attraper**, et c'est ce que fait `revisar`.

### Solution 3

La prédiction : `facturacion` répond `503` en 95 ms, donc `CAIDO` avec le détail `503` et un temps d'environ 100 ms. `notificaciones` met 10 s mais sa limite est de 1 s : `CAIDO` avec `tiempo agotado` et sans temps. Le récapitulatif : `6 servicios · 2 arriba · 1 lento · 3 caídos`. Voici ce qu'il affiche :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     160ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      92ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO      102ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 666ms
```

Ce qui est bizarre, c'est la dernière ligne : `notificacionesCAIDO`, sans séparation. Le nom a 14 lettres et la colonne `SERVICIO` en mesure 12 (`{nombre:<12}`), donc il déborde et se colle à la suivante. C'est une vraie limite du tableau tel qu'il est aujourd'hui, et c'est l'une des choses que la Leçon 11 corrige en calculant la largeur à partir du nom le plus long. Compte aussi le temps : l'exécution entière a pris environ 3.8 s au lieu de 2.7, parce que `notificaciones` attend sa seconde complète avant de renoncer. Chaque service lent ou bloqué ajoute son attente à la série, ce que la Leçon 10 vient résoudre.

### Solution 4

`mypy` se plaint **en premier**, sans rien exécuter :

```text
src/revisor/revision.py:31: error: Argument 1 to "append" of "list" has incompatible type "Coroutine[Any, Any, Resultado]"; expected "Resultado"  [arg-type]
src/revisor/revision.py:31: note: Maybe you forgot to use "await"?
```

En lançant le programme, l'en-tête s'affiche et il s'arrête avec `AttributeError: 'coroutine' object has no attribute 'servicio'`, parce que la liste contient des coroutines au lieu de résultats, et à la fin apparaît `RuntimeWarning: coroutine 'revisar' was never awaited`. C'est `mypy` qui est arrivé en premier, et il l'a fait avec la cause et avec la suggestion ; l'erreur à l'exécution ne montre que la conséquence. C'est l'argument en faveur de lancer `mypy` avant le programme.

## Comment savoir que j'ai réussi

- [ ] Avec le serveur d'entraînement allumé, `python -m revisor` affiche le tableau de quatre services avec `catalogo` et `pagos` en marche, `inventario` lent (`2.3s`) et `reportes` en panne avec `sin conexión`, et `echo $?` affiche `1`.
- [ ] Avec le serveur éteint, les quatre disent `CAIDO` et `sin conexión`, et le programme n'affiche aucun *traceback*.
- [ ] `pytest -q` dit `21 passed` (le même nombre que dans la Leçon 8), et tu peux expliquer quelle partie du programme aucun des 21 ne couvre.
- [ ] `mypy` dit `Success: no issues found in 11 source files`, `ruff check` dit `All checks passed!` et `ruff format --check` dit que les fichiers sont déjà formatés.
- [ ] Tu as mesuré l'exécution avec `time` et ton nombre est proche de 2.7 secondes, et tu sais expliquer pourquoi c'est la somme et non le maximum.
- [ ] Tu peux expliquer ce que fait `await`, ce que fait `asyncio.run` et pourquoi `saludar()` tout court n'affiche pas `hola`.
- [ ] Tu peux dire avec quelle exception d'`httpx` se termine un service qui ne répond pas et avec laquelle un service où personne n'écoute, et pourquoi un `503` n'est pas une exception.

## Résumé

Réponds sans regarder la leçon :

1. Qu'apporte une réponse HTTP, et quelles familles de codes d'état y a-t-il ? Lesquelles rendent un service `CAIDO` ?
2. Que fait `urllib` quand le serveur répond `503`, et que fait `httpx` ?
3. Pourquoi `urlopen` accepte-t-il une adresse `file://`, et qu'est-ce qui l'arrête dans le `revisor` ?
4. Quel délai d'attente a `urllib` par défaut, et lequel `httpx` ?
5. Quelle exception d'`httpx` produit un service qui ne répond pas, et laquelle un service où personne n'écoute ?
6. Que fait `asyncio.run` ? Que se passe-t-il si tu appelles une fonction `async def` sans `await` ni `asyncio.run` ?
7. Pourquoi trois `await` de suite d'une demi-seconde prennent-ils 1.5 s et non 0.5 s ?
8. Pourquoi le rapport de la Leçon 9 dit-il toujours `21 passed` et qu'a-t-il laissé sans test ?

## Pour aller plus loin

- [HTTPX, « Timeouts »](https://www.python-httpx.org/advanced/timeouts/) — les quatre délais d'attente (`connect`, `read`, `write`, `pool`), la valeur par défaut et comment les désactiver. En anglais, comme presque toute la documentation de l'écosystème. Consulté le 7 octobre 2026.
- [Python, « Coroutines and tasks »](https://docs.python.org/3/library/asyncio-task.html) — la documentation officielle d'`asyncio` : coroutines, `await`, tâches et l'avertissement de la coroutine jamais attendue. Consulté le 7 octobre 2026.
- [RFC 9110, « HTTP Semantics »](https://www.rfc-editor.org/rfc/rfc9110.html) — le standard HTTP ; la section des codes d'état définit ce que veut dire chaque nombre. C'est un texte à consulter, pas à lire d'une traite. Consulté le 7 octobre 2026.
- [PEP 492, « Coroutines with async and await syntax »](https://peps.python.org/pep-0492/) — le document qui a introduit `async` et `await` ; il explique pourquoi ce sont des mots réservés du langage. Consulté le 7 octobre 2026.
