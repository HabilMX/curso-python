# Leçon 6 — Erreurs, fichiers et données extérieures

**Durée :** 2 × 90 min (deux sessions ; la coupure se situe entre les sections 6.2 et 6.3)

**Ce que tu construis :** la lecture de la configuration du `revisor` : la liste des services n'est plus écrite dans le code, elle se lit dans un fichier `servicios.toml`

**Ce que tu apprends :** les exceptions (`try`, `except`, `else`, `finally`, une exception personnalisée et `raise ... from`) ; lire un *traceback* de bas en haut ; les fichiers avec `with` et `pathlib` ; UTF-8 explicite ; les formats TOML et JSON ; valider ce qui arrive de l'extérieur ; et pourquoi on n'utilise ni `eval` ni `pickle`

**D'où tu viens.** Tu arrives avec le projet de la [Leçon 5](05-modelo-de-datos.md) : un `revisor` avec son modèle de données (`Servicio`, `Estado`, `Resultado`), la classification avec `match`, le rapport en tableau avec son récapitulatif, et la liste `SERVICIOS` écrite à la main dans `revisor.py`. Ça fonctionne, mais l'exercice de projet de la leçon 5 t'a laissé une gêne : pour ajouter un service au rapport, il faut **ouvrir le code Python et le modifier**. La personne qui administre les services n'a pas de raison de savoir programmer, et la personne qui programme n'a pas de raison de retoucher le code chaque fois qu'une adresse change. Cette leçon sépare les deux choses : les données vont dans un fichier, et le programme apprend à le lire et à s'en méfier. Tu travailles dans ton dossier `~/curso-python/revisor/`, avec l'environnement virtuel activé, et tu exécutes tout avec `python`.

**Ce que cette leçon ne fait pas.** Elle n'interroge aucun réseau : `revisar` continue d'utiliser les données simulées de la leçon 5, et cela ne change qu'à partir de la [Leçon 9](09-http-y-asyncio.md). Elle ne transforme pas non plus le `revisor` en une commande avec des options (`--config`, `--formato`) : c'est le travail de la [Leçon 7](07-paquete-linea-de-comandos.md). Aujourd'hui, le nom du fichier est écrit dans une constante du programme. Ce qui se résout ici, c'est **comment lire un fichier de configuration sans que le programme se casse de façons incompréhensibles** quand le fichier n'existe pas, est mal écrit ou dit des choses qui n'ont aucun sens.

**À propos des exécutions.** Pour exécuter une figure, entre dans le dossier de la leçon dans le dépôt et lance `python fig06_01.py` ; les figures qui vivent dans un dossier à elles (`fig06_06/`, `fig06_07/`, `fig06_18/`) s'exécutent depuis l'intérieur de celui-ci. Toutes les sorties de cette leçon ont été obtenues avec Python 3.14.8 et répétées avec Python 3.12.12, de la même série 3.12 que celle fournie avec Linux Mint 22. (Celui de Mint 22 est le 3.12.3, celui que publie Ubuntu 24.04, sa base : la [page du paquet `python3.12` pour Ubuntu 24.04 sur Launchpad](https://launchpad.net/ubuntu/noble/+source/python3.12) le montre.) Elles sont identiques, à une différence près : quelques marques de soulignement (`~~~~^^`) que le rapport d'une erreur contient dans une version et pas dans l'autre ; si tu vois plus ou moins de marques sur ton écran, c'est normal. Les programmes se trouvent dans [`programas/06-errores-archivos-datos/`](https://github.com/HabilMX/curso-python/tree/main/programas/06-errores-archivos-datos), dans le dépôt du cours.

## À la fin, tu seras capable de

- Lire le rapport d'une erreur (le *traceback*) de bas en haut et dire ce qui a échoué, où, et qui a appelé qui.
- Écrire un `try` avec `except`, `else` et `finally`, en attrapant l'exception précise que tu sais gérer et en laissant passer les autres.
- Définir une exception personnalisée avec une ligne d'héritage et la lever avec `raise ... from`, de façon que l'erreur d'origine ne se perde pas.
- Ouvrir et lire un fichier avec `with` et avec `pathlib.Path`, toujours avec l'encodage UTF-8 écrit explicitement, et expliquer ce qui se passe s'il ne l'est pas.
- Lire un fichier TOML avec `tomllib` et convertir des données en JSON et inversement avec `json`, en lisant la ligne et la colonne quand le JSON est mal formé.
- Valider des données extérieures avec `isinstance` et `urlsplit`, et expliquer pourquoi `True` passe une validation d'entiers faite à la légère.
- Expliquer pourquoi un texte qui vient de l'extérieur n'est jamais passé à `eval` ni à `pickle`.

## Le pourquoi avant le comment

Ouvre ton `revisor.py` de la leçon 5 et regarde la liste `SERVICIOS`. Chaque fois que l'équipe d'exploitation voudra vérifier un nouveau service, quelqu'un doit modifier ce fichier, l'enregistrer et relancer. Pour le programmeur, c'est une gêne ; pour toute autre personne, c'est un mur. Et il y a un problème plus profond : ce code et ces données changent **pour des raisons différentes et à des rythmes différents**. Le programme change quand tu découvres une erreur ou que tu veux une nouvelle fonction ; la liste des services change quand l'entreprise ajoute un service. Mélanger les deux dans un fichier oblige l'un à attendre l'autre.

La solution est la solution classique : les données vivent dans un **fichier de configuration**, un texte avec des règles que n'importe qui peut modifier, et le programme le lit au démarrage. Mais dès que le programme lit quelque chose qu'une autre personne a écrit, il entre dans un terrain nouveau. Jusqu'à la leçon 5, chaque donnée du `revisor`, c'est toi qui l'avais écrite, dans le même fichier que le code, et si elle était fausse, tu le savais à l'instant. Un fichier extérieur peut échouer de quatre façons, et les quatre sont normales, pas exceptionnelles :

1. **Il n'existe pas**, ou il existe dans un autre dossier que celui que tu crois.
2. **Il existe mais il est mal écrit** : il manque un guillemet, il y a une virgule en trop.
3. **Il est bien écrit mais il manque quelque chose** : un service sans nom, sans adresse.
4. **Il est complet mais dit quelque chose d'absurde** : une adresse qui n'est pas celle d'une page web, un délai d'attente négatif, deux services avec le même nom.

Un programme sérieux distingue les quatre cas et dit à la personne **lequel s'est produit et comment le corriger**, au lieu d'afficher un rapport d'erreur de trente lignes écrit pour des programmeurs. On y arrive avec deux outils que cette leçon enseigne ensemble parce qu'on ne les comprend pas séparément : les **exceptions** (comment un programme signale que quelque chose s'est mal passé, et comment un autre l'attrape) et la **validation** (comment on vérifie que ce qui est arrivé a du sens).

Le chemin comporte deux sessions. La **première** couvre les concepts 6.1 et 6.2 : les exceptions et les fichiers. À son terme, tu sauras lire un rapport d'erreur et ouvrir un fichier texte sans surprises. La **seconde** couvre 6.3 et 6.4 : les formats (TOML et JSON) et la validation. À son terme, tu auras un `revisor` qui lit sa liste de services dans un fichier et qui se plaint en espagnol clair quand le fichier ne convient pas. Avec cette destination en tête, voici ce que tu verras à la fin de la leçon en exécutant le `revisor` depuis un autre dossier, sans être passé par l'endroit où se trouve le fichier :

```text
error de configuración: no existe el archivo servicios.toml
```

Un message d'une ligne, au lieu d'un rapport d'erreur. Pour y arriver, il faut d'abord comprendre ce qu'est une exception.

## Les concepts

### 6.1 Exceptions

#### 6.1.1 Ce qu'est une exception et comment se lit son rapport

Jusqu'à maintenant, quand quelque chose a échoué dans tes programmes, Python s'est arrêté et a affiché un bloc de texte en rouge, le *traceback* (dans ce cours, « le rapport d'erreur »). Tu l'as lu pour la première fois dans la [Leçon 1](01-instalacion.md) et tu l'as vu dans chaque leçon. Voyons maintenant ce qu'il y a derrière : ce rapport est l'avis d'une **exception**, qui est la façon qu'a Python de dire « ici s'est produit quelque chose que je ne sais pas résoudre ». Quand une ligne du programme ne peut pas faire ce qu'on lui a demandé, elle **lève** une exception. L'exception remonte à travers les fonctions qui étaient en cours d'exécution, de la plus récente à la plus ancienne, en cherchant quelqu'un qui sache quoi en faire. Si elle arrive tout en haut sans que personne l'attrape, le programme s'arrête et Python affiche le rapport.

Provoquons-en une exprès, avec un cas qui se produira pour de vrai quand le `revisor` lira des fichiers : une donnée qui devrait être un nombre et qui arrive avec autre chose. Pour cela, il te faut une nouvelle fonction : `int(texto)` convertit un texte en nombre entier, comme `str()` (leçon 2) convertit une valeur en texte. `int("142")` donne le nombre 142. Mais que donne `int("142 ms")` ? Exécute-le avec `fig06_01.py` :

```python
# fig06_01.py
def leer_tiempo(texto: str) -> int:
    return int(texto)


def main() -> None:
    tiempo_ms = leer_tiempo("142 ms")
    print(f"tiempo: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

Le programme définit deux fonctions, `leer_tiempo` et `main`, et `main` appelle `leer_tiempo` avec un texte qui a les lettres « ms » collées. Exécute-le :

```text
$ python fig06_01.py
Traceback (most recent call last):
  File "fig06_01.py", line 12, in <module>
    main()
    ~~~~^^
  File "fig06_01.py", line 7, in main
    tiempo_ms = leer_tiempo("142 ms")
  File "fig06_01.py", line 3, in leer_tiempo
    return int(texto)
ValueError: invalid literal for int() with base 10: '142 ms'
```

Voici le rapport, et il vaut la peine d'apprendre à bien le lire, parce que tu vas le lire des centaines de fois. **Il se lit de bas en haut.** La **dernière ligne** est la plus importante : `ValueError: invalid literal for int() with base 10: '142 ms'`. Elle dit deux choses : le **type** de l'exception, `ValueError` (« valeur invalide » : le type de la donnée était correct, un texte, mais son contenu ne convient pas pour ce qu'on voulait faire), et un **message** qui explique ce qui s'est passé. En français : « littéral invalide pour int() en base 10 : '142 ms' ». La « base 10 » est le système de numération que nous utilisons tous les jours ; le message dit seulement que `int` attendait un nombre écrit avec des chiffres de 0 à 9 et a trouvé, après le 142, une espace et les lettres `ms`. (Les espaces au début ou à la fin ne la dérangent pas : `int(" 142 ")` donne `142` ; ce qu'elle n'accepte pas, c'est tout ce qui ne fait pas partie du nombre.)

Les lignes du dessus disent **où** cela s'est produit, et elles sont dans l'ordre inverse de celui dans lequel les choses se sont passées. Chaque paire de lignes qui commence par `File` est un **cadre** : une fonction qui était en cours d'exécution. Le dernier cadre (`in leer_tiempo`, ligne 3) est celui où l'exception est née : la ligne `return int(texto)`. Le cadre du dessus (`in main`, ligne 7) est celui qui a appelé `leer_tiempo`. Et le premier (`in <module>`, ligne 12) est le programme lui-même, qui a appelé `main()`. Lis le rapport comme une pile d'assiettes : l'assiette du bas est la plus récente, et c'est là que le problème a commencé. Les lignes avec `~~~~^^` sont une aide des versions récentes de Python ([PEP 657](https://peps.python.org/pep-0657/)) : elles soulignent la partie exacte de la ligne qui a échoué, pour que tu n'aies pas à deviner lequel des trois appels d'une longue ligne c'était.

Tant que personne n'attrape l'exception, c'est toute l'histoire : elle est levée, elle remonte la pile, le programme meurt. La [documentation officielle sur les erreurs et les exceptions](https://docs.python.org/3/tutorial/errors.html) raconte la même chose avec plus d'exemples. Voyons maintenant comment l'attraper.

#### 6.1.2 `try`, `except`, `else` et `finally`

Attraper une exception, c'est dire à Python : « essaie ceci ; si ça échoue de *cette* manière, fais *cette autre chose* au lieu de mourir ». On l'écrit avec l'instruction `try` (en anglais, « essaie »). Regarde le programme `fig06_02.py`, qui convertit deux textes, un bon et un mauvais :

```python
# fig06_02.py
def leer_tiempo(texto: str) -> int | None:
    try:
        tiempo_ms = int(texto)
    except ValueError:
        print(f"  '{texto}' no es un número entero")
        return None
    else:
        print(f"  '{texto}' se convirtió en {tiempo_ms}")
        return tiempo_ms
    finally:
        print("  (fin de la conversión)")


def main() -> None:
    for texto in ["142", "142 ms"]:
        print(f"leyendo '{texto}'")
        tiempo_ms = leer_tiempo(texto)
        print(f"  resultado: {tiempo_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_02.py
leyendo '142'
  '142' se convirtió en 142
  (fin de la conversión)
  resultado: 142
leyendo '142 ms'
  '142 ms' no es un número entero
  (fin de la conversión)
  resultado: None
```

Il y a quatre blocs, et chacun a une règle claire :

- **`try:`** contient **uniquement** la ligne qui peut échouer, ici `tiempo_ms = int(texto)`. S'il n'y a pas d'erreur, le programme passe au bloc `else`. S'il y en a une, Python abandonne le `try` à cette même ligne et saute au `except` qui correspond.
- **`except ValueError:`** contient ce que l'on fait si l'erreur était de ce type. Ici, signaler que le texte n'est pas un nombre et renvoyer `None` (la valeur qui, dans ce cours, signifie « il n'y a pas de donnée »). Entre le `except` et les deux-points se trouve le **type d'exception** que l'on attrape ; tout autre type passerait son chemin.
- **`else:`** (dans ce contexte, « s'il n'y a pas eu d'erreur ») s'exécute **seulement si le `try` s'est terminé sans exception**. Ici, il contient ce que l'on fait quand la conversion a fonctionné.
- **`finally:`** (« enfin ») s'exécute **toujours** : qu'il y ait eu une erreur ou non, que tu aies renvoyé une valeur ou non. On l'utilise pour nettoyer, par exemple fermer quelque chose qu'on avait ouvert.

Regarde bien la sortie, car elle contient une surprise qu'il convient de voir une fois. Avec le texte « 142 », on affiche d'abord « se convirtió en 142 » (du `else`) et **ensuite** « (fin de la conversión) » (du `finally`), alors que le `return tiempo_ms` du `else` apparaît avant dans le code. Avec « 142 ms », le `except` affiche son avertissement, renvoie `None`, et le `finally` s'exécute **quand même** avant que la fonction se termine. Autrement dit : `finally` s'exécute même quand le bloc a déjà décidé de sortir avec `return`. Cette garantie est sa raison d'être.

Deux questions raisonnables restent : pourquoi un `else`, si le `print` et le `return` pourraient aller dans le `try` ? Parce qu'**un `try` doit être aussi petit que possible**. Tout ce que tu mets dedans est protégé par le `except`, et si dans cette ligne en trop se produit une erreur du même type que tu n'attendais pas, le `except` l'avalerait et tu croirais que c'était l'erreur que tu attendais. La règle est : dans le `try` va **ce qui peut échouer de la manière que tu sais gérer**, et rien de plus. Ce qui doit se produire si tout s'est bien passé va dans le `else`.

La seconde question : peut-on attraper plusieurs types ? Oui, de deux façons. L'une consiste à mettre plusieurs blocs `except` les uns après les autres, chacun avec son type et sa réponse. L'autre consiste à mettre les types ensemble **entre parenthèses**, séparés par des virgules : `except (ValueError, TypeError):`, quand la réponse est la même. Écris toujours les parenthèses : en Python 3.12, elles sont obligatoires, et même si Python 3.14 permet de les omettre quand le `except` n'a pas de `as` ([PEP 758](https://peps.python.org/pep-0758/)), le code du cours tourne dans les deux versions.

#### 6.1.3 Attrape l'exception précise, jamais « n'importe laquelle »

C'est la règle la plus importante de la section, et on la comprend mieux en voyant ce qui se passe quand on la viole. Regarde `fig06_03.py`. C'est la même fonction, mais avec deux changements : le `except` dit `Exception` au lieu de `ValueError`, et quelqu'un a mal écrit un nom dans le `try` (`stirp` au lieu de `strip`, la méthode qui supprime les espaces aux extrémités d'un texte) :

```python
# fig06_03.py
def leer_tiempo(texto: str) -> int | None:
    try:
        return int(texto.stirp())
    except Exception:  # noqa: BLE001
        print(f"'{texto}' no es un número entero")
        return None


def main() -> None:
    print(leer_tiempo("142"))


if __name__ == "__main__":
    main()
```

```text
$ python fig06_03.py
'142' no es un número entero
None
```

Regarde ce qui s'est passé : le texte « 142 » est un nombre parfaitement valide, et le programme a dit qu'il **ne l'est pas**. La fonction n'a rien à voir avec les nombres : elle contient une faute d'orthographe. Sans le `try`, Python aurait arrêté le programme avec `AttributeError: 'str' object has no attribute 'stirp'. Did you mean: 'strip'?` (« un texte n'a pas l'attribut `stirp` ; voulais-tu dire `strip` ? »), et tu aurais corrigé la faute de frappe en une minute. Avec un `except` trop large, cet avertissement s'est transformé en un mensonge qui s'affiche à l'écran, et l'erreur réelle reste enterrée jusqu'à ce que quelqu'un demande pourquoi aucun temps ne se lit bien.

Pour le comprendre, il faut savoir que les exceptions forment une famille. Au sommet se trouve `BaseException` ; en dessous, `Exception`, dont dépendent presque toutes les erreurs que tu rencontreras ; et de là partent les types précis, certains avec des parents. `ValueError` en est un. `KeyError` et `IndexError` (que tu as vus dans la leçon 4) sont des enfants de `LookupError`. `FileNotFoundError` est un cas particulier de `OSError`, l'exception des problèmes avec le système d'exploitation. `UnicodeDecodeError`, que tu verras plus bas, est un type de `ValueError`. L'arbre complet se trouve dans la [liste des exceptions de la documentation](https://docs.python.org/3/library/exceptions.html). Attraper une exception attrape **aussi tous ses enfants** : c'est pourquoi `except Exception` attrape presque tout, y compris l'`AttributeError` de la faute de frappe, et c'est pourquoi `except ValueError` attrape aussi les erreurs de lecture de TOML et de JSON, comme tu le verras en 6.3.

Et il y a la pire version : le `except:` **sans type**, appelé « nu ». Celui-là attrape même ce qui est au-dessus de `Exception`, y compris le `KeyboardInterrupt` que Python lève quand tu appuies sur `Ctrl`+`C` pour arrêter un programme. Un programme avec un `except:` nu peut ne pas mourir quand tu le lui demandes. Le [guide de style PEP 8](https://peps.python.org/pep-0008/#programming-recommendations) demande de nommer les exceptions précises chaque fois que c'est possible au lieu de l'utiliser, et de le réserver à de rares cas ; dans ce cours, la règle est plus stricte et n'a pas d'exception : jamais.

Les règles sont donc trois. **Première :** attrape le type précis que tu sais gérer, avec la réponse précise qui a du sens. **Deuxième :** si tu ne sais pas quoi faire d'une erreur, **ne l'attrape pas** : laisse-la remonter, que le programme s'arrête avec son rapport, et quelqu'un le verra. Un programme qui s'arrête avec un rapport clair vaut mieux qu'un programme qui continue à fonctionner avec des données fausses. **Troisième :** si tu as vraiment besoin d'attraper `Exception` (par exemple, dans la dernière ligne de défense d'un programme qui ne doit pas tomber), fais-le à un seul endroit, enregistre ce qui s'est passé et ne le laisse pas passer en silence. Le commentaire `# noqa: BLE001` que tu vois dans `fig06_03.py` est une marque pour `ruff`, l'outil qui vérifie le style du code et que tu connaîtras dans la [Leçon 8](08-pruebas-tipos-calidad.md) : il lui dit « je sais que cette ligne attrape une exception trop large, c'est voulu ». La règle de `ruff` qui proteste s'appelle justement « attraper une exception aveugle ».

#### 6.1.4 Une exception personnalisée et `raise ... from`

Jusqu'ici, tu as attrapé des exceptions que Python fournit déjà. Pour le `revisor`, il en faut une de plus, parce que tu dois distinguer **« le fichier de configuration a un problème »** de **« mon programme a une erreur »**. Les deux situations méritent des réponses différentes : la première s'explique à la personne qui a écrit le fichier ; la seconde est un défaut qui doit arrêter le programme avec son rapport, pour qu'un programmeur le corrige. Si tout était levé comme `ValueError`, le programme ne pourrait pas distinguer l'une de l'autre.

La solution est une exception avec un nom à elle, qui se définit avec une ligne d'**héritage**. Regarde `fig06_04.py` :

```python
# fig06_04.py
class ErrorDeConfiguracion(Exception):
    """La configuración no se puede usar."""


def leer_timeout_ms(texto: str) -> int:
    try:
        return int(texto)
    except ValueError as error:
        mensaje = f"'timeout_ms' debe ser un entero, llegó '{texto}'"
        raise ErrorDeConfiguracion(mensaje) from error


def main() -> None:
    try:
        timeout_ms = leer_timeout_ms("cinco mil")
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        print(f"causa original: {error.__cause__}")
    else:
        print(f"timeout_ms = {timeout_ms}")


if __name__ == "__main__":
    main()
```

```text
$ python fig06_04.py
error de configuración: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
causa original: invalid literal for int() with base 10: 'cinco mil'
```

La première instruction est nouvelle dans sa forme, même si tu as déjà vu `class` dans la leçon 5 comme un « moule de données » : `class ErrorDeConfiguracion(Exception):` définit un nouveau moule qui s'appelle `ErrorDeConfiguracion`, et la parenthèse dit qu'il **hérite** de `Exception`. Hériter signifie « c'est une `Exception` et en plus elle a son propre nom » : tout ce que Python sait faire avec n'importe quelle exception (la lever, l'attraper, afficher son message, montrer son rapport), il sait le faire avec la tienne, sans rien écrire de plus. C'est un seul niveau d'héritage, et c'est tout ce dont tu as besoin ; le cours n'en dit pas davantage. Le texte entre triples guillemets dans la classe est une **chaîne de documentation** (*docstring*) : une phrase qui explique à quoi elle sert, et que Python conserve pour qui voudra la consulter. Aucune autre instruction n'est nécessaire dans la classe.

La fonction `leer_timeout_ms` fait quelque chose que tu répéteras dans tout le cours : elle attrape une erreur de bas niveau (`ValueError`, venue de `int`) et la **traduit** en une erreur du domaine du programme (`ErrorDeConfiguracion`), avec un message qui parle dans les termes de la personne qui a écrit la configuration : « 'timeout_ms' debe ser un entero, llegó 'cinco mil' ». Le message de `int` (« invalid literal for int()… ») est utile pour un programmeur, mais pas pour qui modifie un fichier de configuration. L'instruction `raise` (lever) lance l'exception, et la queue `from error` fait quelque chose d'important : elle **conserve l'erreur d'origine comme cause**. Cette cause reste enregistrée à l'intérieur de la nouvelle exception, dans `error.__cause__` (les deux tirets bas avant et après sont la façon dont Python marque les noms qu'il se réserve). La deuxième ligne de la sortie le montre : le programme a affiché son avertissement en espagnol et, à part, la cause d'origine en anglais, au cas où elle serait nécessaire.

Que se passe-t-il si personne n'attrape l'exception ? Regarde `fig06_05.py`, qui est le même programme sans le `try` dans `main` :

```text
$ python fig06_05.py
Traceback (most recent call last):
  File "fig06_05.py", line 8, in leer_timeout_ms
    return int(texto)
ValueError: invalid literal for int() with base 10: 'cinco mil'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "fig06_05.py", line 20, in <module>
    main()
    ~~~~^^
  File "fig06_05.py", line 15, in main
    timeout_ms = leer_timeout_ms("cinco mil")
  File "fig06_05.py", line 11, in leer_timeout_ms
    raise ErrorDeConfiguracion(mensaje) from error
ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'
```

Ce rapport a **deux** parties séparées par une phrase : « The above exception was the direct cause of the following exception » (« l'exception du dessus a été la cause directe de la suivante »). C'est la trace de `from error`. Il se lit comme avant, de bas en haut : la dernière ligne, `ErrorDeConfiguracion: 'timeout_ms' debe ser un entero, llegó 'cinco mil'`, est ce qui est arrivé tout en haut. Mais maintenant, en plus, Python **conserve l'histoire** : au-dessus se trouve le `ValueError` d'origine, avec sa ligne exacte (`return int(texto)`). Si tu n'avais pas écrit `from error`, le rapport dirait à la place « During handling of the above exception, another exception occurred » (« pendant le traitement de l'exception du dessus, une autre exception s'est produite »), ce qui suggère une nouvelle erreur survenue au milieu du traitement d'une autre. Python montrerait quand même les deux exceptions (l'originale reste enregistrée comme *contexte*, dans l'attribut `__context__`), mais le rapport ne dirait plus que l'une a été la **conséquence** de l'autre : il dirait que la seconde s'est produite « entre-temps », comme un accident à part. Avec `from`, l'originale est enregistrée comme **cause** (`__cause__`), ce qui est ce qui s'est vraiment passé. La règle : **quand tu traduis une exception, écris toujours `from`**. Celui qui déboguera ton programme t'en remerciera. L'explication de la technique se trouve dans la [PEP 3134](https://peps.python.org/pep-3134/) et dans la [section sur le chaînage des exceptions](https://docs.python.org/3/tutorial/errors.html#exception-chaining) du tutoriel.

Voilà le vocabulaire des exceptions. Il manque un endroit où l'utiliser, et c'est le suivant : lire des fichiers, où les choses échouent pour des raisons que tu ne contrôles pas.

### 6.2 Fichiers

#### 6.2.1 Ouvrir, lire, fermer : `with`

Un fichier sur le disque ne se « lit » pas comme ça : d'abord on l'**ouvre**, ce qui demande au système d'exploitation un accès à lui ; on lit son contenu ; et à la fin on le **ferme**, ce qui rend l'accès. Un fichier qu'on ouvre sans le fermer consomme des ressources du système (chaque programme ne peut en avoir qu'un nombre limité d'ouverts) et, si tu écrivais, il peut laisser la dernière partie non enregistrée. La façon la plus soigneuse de l'écrire, avec ce que tu sais déjà de `try`, serait celle-ci :

```python
archivo = open("nota.txt", encoding="utf-8")
try:
    texto = archivo.read()
finally:
    archivo.close()
```

Ça fonctionne, et le `finally` garantit la fermeture même si `read()` échoue. Mais c'est beaucoup de rituel pour quelque chose de si fréquent, et il est facile d'oublier le `finally`. Python offre l'instruction `with` (« avec »), qui fait exactement cela pour toi. Regarde `fig06_06/leer.py` et le fichier `nota.txt` qu'il lit :

```text fig06_06/nota.txt
Revisión de las 9:00
reportes: sin conexión
```

```python
# fig06_06/leer.py
with open("nota.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
    print(f"dentro del with: cerrado = {archivo.closed}")

print(f"fuera del with: cerrado = {archivo.closed}")
print(texto.splitlines())
```

```text
$ cd fig06_06
$ python leer.py
dentro del with: cerrado = False
fuera del with: cerrado = True
['Revisión de las 9:00', 'reportes: sin conexión']
```

`open("nota.txt", encoding="utf-8")` ouvre le fichier et renvoie un objet qui représente cette ouverture. `with ... as archivo:` dit « pendant la durée de ce bloc, le fichier s'appelle `archivo` ; quand tu sors du bloc, ferme-le, quoi qu'il arrive ». La sortie le démontre : dans le `with`, `archivo.closed` (la question « est-il fermé ? ») dit `False` ; dès que le bloc se termine, il dit `True`, et personne n'a écrit de `close()`. Si le bloc se termine par une exception, le fichier est aussi fermé : le `with` est, en fait, un `try`/`finally` écrit sous forme abrégée. La [référence de l'instruction `with`](https://docs.python.org/3/reference/compound_stmts.html#with) explique le mécanisme complet ; pour ce cours, la règle suffit : **tout fichier que tu ouvres, ouvre-le avec `with`**.

`archivo.read()` renvoie le contenu complet sous la forme d'un seul texte. Dans le programme, on affiche `texto.splitlines()`, une méthode des textes qui les découpe en une liste avec une chaîne par ligne, et qui retire les sauts de ligne ; ainsi tu vois d'un coup d'œil que le fichier a deux lignes. Remarque aussi `encoding="utf-8"` : c'est une partie du `open` qui n'est pas un ornement, et sa raison est expliquée en 6.2.3.

#### 6.2.2 `pathlib.Path` : un chemin comme valeur, pas comme texte

Le nom du fichier, `"nota.txt"`, est un **chemin** : l'adresse d'un fichier sur le disque. Jusqu'ici, nous l'avons écrit comme un texte, et pour un seul fichier dans le dossier courant, il n'y a pas de problème. Mais les chemins ont leurs propres règles : sous Linux et macOS, les dossiers se séparent par `/`, sous Windows par `\` ; un chemin peut être **absolu** (il commence à la racine du disque, comme `/home/ana/curso-python/revisor/servicios.toml`) ou **relatif** (il se compte depuis le dossier où tu es, comme `servicios.toml`). Manipuler des chemins comme des textes, avec des additions et des découpages, se casse dès que l'une de ces règles change.

Pour cela, le module `pathlib` de la bibliothèque standard offre la classe `Path` : une valeur qui **sait ce qu'est un chemin**. Tu en construis un avec `Path("nota.txt")` et dès lors il a ses propres opérations, qui s'invoquent avec un point, comme les méthodes des listes et des dictionnaires que tu connais déjà. Regarde `fig06_07/ruta.py`, qui utilise le même `nota.txt` :

```python
# fig06_07/ruta.py
from pathlib import Path

ruta = Path("nota.txt")
print(ruta.name, ruta.suffix, ruta.exists())
print(Path("no-esta.txt").exists())

otra = Path("datos") / "servicios.toml"
print(otra)

texto = ruta.read_text(encoding="utf-8")
print(texto.splitlines())
```

```text
$ cd fig06_07
$ python ruta.py
nota.txt .txt True
False
datos/servicios.toml
['Revisión de las 9:00', 'reportes: sin conexión']
```

Ligne par ligne :

- `Path("nota.txt")` crée le chemin. Il ne touche pas encore le disque : il décrit seulement une adresse, que le fichier existe ou non.
- `ruta.name` est le nom du fichier (`nota.txt`), `ruta.suffix` est sa terminaison avec le point (`.txt`), et `ruta.exists()` demande au disque s'il existe (`True`). La deuxième ligne pose la même question sur un fichier qui n'est pas là, et répond `False` : **demander si un fichier absent existe ne lève aucune exception**. (Une nuance de version : en 3.12, si la question se heurte à un autre problème du système, comme ne pas avoir la permission de regarder le dossier, `exists()` peut encore lancer un `OSError` ; depuis 3.14, elle [répond `False` dans tous ces cas](https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists).)
- `Path("datos") / "servicios.toml"` utilise l'opérateur `/` avec une nouvelle signification : **joindre** deux parties d'un chemin avec le séparateur qui convient au système. Le résultat s'affiche comme `datos/servicios.toml` et ne touche pas le disque. C'est beaucoup plus sûr que d'additionner des textes.
- `ruta.read_text(encoding="utf-8")` ouvre le fichier, lit tout, le ferme et renvoie le texte, en un seul appel. C'est la forme que nous utiliserons dans le `revisor` parce qu'elle ne laisse rien d'ouvert. La [documentation de `pathlib`](https://docs.python.org/3/library/pathlib.html) énumère le reste de ce qu'un chemin peut faire (lister des dossiers, créer des fichiers) ; dans ce cours, seul ce que tu vois ici est nécessaire.

Il y a une conséquence pratique au fait que les chemins relatifs « se comptent depuis l'endroit où tu es » : le même programme, avec le même `Path("nota.txt")`, fonctionne ou non selon le dossier depuis lequel tu l'exécutes. Que se passe-t-il quand le fichier n'existe pas ? Regarde `fig06_08.py`, qui essaie d'ouvrir un fichier absent :

```python
# fig06_08.py
with open("no-esta.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
print(texto)
```

```text
$ python fig06_08.py
Traceback (most recent call last):
  File "fig06_08.py", line 2, in <module>
    with open("no-esta.txt", encoding="utf-8") as archivo:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'
```

`FileNotFoundError` (« fichier introuvable ») est levée, une exception précise que tu peux attraper. Le texte du message, `[Errno 2] No such file or directory`, vient du système d'exploitation et est en anglais : tu ne le contrôles pas, et c'est pourquoi tu ne le montreras pas à qui utilisera le `revisor`. En 6.4, le programme attrapera cette exception et la traduira en un message à lui.

#### 6.2.3 Texte et octets : pourquoi toujours `encoding="utf-8"`

Un fichier sur le disque ne stocke pas des lettres : il stocke des **octets**, des nombres de 0 à 255. Pour que ces nombres soient du texte, quelqu'un doit décider quel nombre correspond à quelle lettre. Cette décision est l'**encodage**, et il en existe beaucoup. Celui qui domine aujourd'hui est **UTF-8** : il peut représenter n'importe quel caractère de n'importe quelle langue, et les lettres sans accent occupent un seul octet. Les caractères accentués, comme le « ó » de « conexión », en occupent deux. Un ancien encodage, `latin-1`, représente le « ó » avec un seul octet, mais il ne sert que pour quelques langues européennes. Le voir est plus clair que l'expliquer. Exécute `fig06_09.py`, qui fabrique les octets d'un même texte dans les deux encodages :

```python
# fig06_09.py
texto = "sin conexión"

en_utf8 = texto.encode("utf-8")
en_latin1 = texto.encode("latin-1")

print(en_utf8)
print(en_latin1)
print(len(texto), len(en_utf8), len(en_latin1))
print(en_utf8.decode("utf-8"))
```

```text
$ python fig06_09.py
b'sin conexi\xc3\xb3n'
b'sin conexi\xf3n'
12 13 12
sin conexión
```

`texto.encode("utf-8")` convertit un texte en octets avec cet encodage ; les octets s'affichent avec un `b` devant (`b'sin conexi\xc3\xb3n'`), et `\xc3\xb3` sont les deux octets (en hexadécimal) qu'UTF-8 utilise pour le « ó ». Avec `latin-1`, le « ó » est un seul octet, `\xf3`. La troisième ligne le confirme par un calcul : le texte a 12 caractères ; en UTF-8, cela fait 13 octets, et en `latin-1`, 12. Et `bytes.decode("utf-8")` fait le chemin inverse : des octets vers le texte. Avec les octets d'UTF-8, on retrouve « sin conexión ».

Maintenant le problème. Que se passe-t-il si les octets ont été écrits dans un encodage et lus avec un autre ? Exécute `fig06_10.py`, qui essaie de lire comme de l'UTF-8 les octets de `latin-1`. Le `b` avant les guillemets marque un littéral d'**octets**, et `\xf3` écrit l'octet dont la valeur, en hexadécimal (le système de numération en base 16 avec lequel on écrit d'habitude les octets), est `f3`, c'est-à-dire 243 :

```python
# fig06_10.py
en_latin1 = b"sin conexi\xf3n"

print(en_latin1.decode("utf-8"))
```

```text
$ python fig06_10.py
Traceback (most recent call last):
  File "fig06_10.py", line 4, in <module>
    print(en_latin1.decode("utf-8"))
          ~~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10: invalid continuation byte
```

La dernière ligne dit : « le codec `utf-8` ne peut pas décoder l'octet `0xf3` à la position 10 : continuation invalide ». L'octet `0xf3` est celui du « ó » en `latin-1`, mais en UTF-8 cette valeur signifie « ici commence un caractère de quatre octets » et l'octet suivant n'a pas la forme qui correspond à la continuation. Python, à juste titre, refuse de deviner. C'est un `UnicodeDecodeError`, qui est un type de `ValueError`.

Cela explique pourquoi on écrit `encoding="utf-8"` **toujours** : quand tu ne l'écris pas, Python choisit l'encodage selon la configuration du système où il tourne, d'après [la documentation de `open`](https://docs.python.org/3/library/functions.html#open). Le même programme peut lire correctement un fichier sur ton ordinateur et échouer sur celui d'un collègue, parce que la configuration est différente. Si tu l'écris, le programme se comporte de la même façon partout. Et ce n'est pas un caprice : les deux formats que tu vas utiliser exigent UTF-8. La [spécification de TOML](https://toml.io/en/v1.0.0) dit qu'un document TOML est un texte Unicode valide en UTF-8, et le [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) établit que le JSON échangé entre systèmes, hors des écosystèmes fermés, doit utiliser UTF-8. Si tu veux mieux comprendre le sujet de fond, le [HOWTO Unicode](https://docs.python.org/3/howto/unicode.html) de la documentation le raconte pas à pas.

> **La première session s'arrête ici.** Jusqu'à ce point, tu as les concepts 6.1 et 6.2 : exceptions et fichiers. Avant la deuxième session, exécute les figures `fig06_01.py` à `fig06_10.py` et change quelque chose dans chacune : un autre texte à la place de « 142 ms », un `except` différent, un autre nom de fichier. Provoquer l'erreur toi-même fixe plus que la lire. La session suivante commence par les formats.

### 6.3 Formats : TOML et JSON

#### 6.3.1 Ce qu'est un format et pourquoi il y en a deux

Un fichier texte avec des lignes isolées ne suffit pas à décrire une liste de services, chacun avec un nom, une adresse et peut-être un délai d'attente. Il faut un **format** : un ensemble de règles qui dit comment s'écrit chaque chose, pour que n'importe quel programme puisse le lire sans ambiguïté. Les deux formats les plus utilisés en Python et dans le reste du monde pour des données structurées sont **TOML** et **JSON**, et ils remplissent des fonctions différentes :

- **TOML** est pensé pour qu'**une personne l'écrive et le lise** : il permet les commentaires avec `#`, n'exige pas d'accolades ni de virgules partout, et il est difficile de l'écrire de façon ambiguë. C'est le format des fichiers de configuration, et c'est celui que Python utilise déjà pour la configuration des projets (tu le verras dans la leçon 7, dans `pyproject.toml`). Le `revisor` lira sa liste de services dans un fichier TOML.
- **JSON** est pensé pour que **deux programmes s'échangent des données**. Il n'admet pas les commentaires et exige des accolades, des guillemets et des virgules, mais presque tous les langages savent le lire et l'écrire. C'est le format des réponses de presque n'importe quel service web, et celui que le `revisor` utilisera pour livrer son rapport à d'autres programmes.

La bibliothèque standard de Python fournit un module pour chacun : `tomllib` (pour lire du TOML) et `json` (pour lire et écrire du JSON). Il y a une asymétrie qu'il vaut mieux connaître : `tomllib` ne fait que **lire**. Pour écrire du TOML, il faut installer une bibliothèque externe, et ce cours n'en a pas besoin parce qu'il n'écrit jamais de configuration, il la lit seulement.

#### 6.3.2 Lire du TOML avec `tomllib`

Un TOML est une série de lignes `llave = valor` (clé = valeur), avec des valeurs de quelques types : du texte entre guillemets doubles, des nombres entiers et décimaux, `true` et `false`, et des listes. Il a aussi des **tables**, qui regroupent des clés sous un nom entre crochets. Ce qui nous intéresse est un cas particulier : une liste de tables, ou *array of tables*, qui s'écrit avec des **doubles crochets**, `[[servicios]]`, et chaque fois que l'en-tête apparaît, un nouvel élément de la liste commence. C'est la forme naturelle pour écrire « une liste de services, chacun avec ses champs ». La [spécification de TOML](https://toml.io/en/v1.0.0#array-of-tables) en donne la définition exacte ; avec un exemple, on comprend plus vite. Regarde `fig06_11.py`, qui lit un TOML écrit à l'intérieur du programme lui-même :

```python
# fig06_11.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
"""

datos = tomllib.loads(TEXTO)
print(datos)

segundo = datos["servicios"][1]
print(segundo["nombre"], segundo["timeout_ms"], type(segundo["timeout_ms"]))
print(segundo.get("proxy"))
```

```text
$ python fig06_11.py
{'servicios': [{'nombre': 'catalogo', 'url': 'https://catalogo.example'}, {'nombre': 'notificaciones', 'url': 'https://notificaciones.example', 'timeout_ms': 1000}]}
notificaciones 1000 <class 'int'>
None
```

Deux détails de lecture avant le résultat. Le texte est entre **triples guillemets** (`"""`...`"""`), qui, en Python, servent à écrire un texte de plusieurs lignes avec les sauts de ligne inclus. Et `tomllib.loads(TEXTO)` est la fonction qui lit : le nom vient de *load string* (« charger depuis un texte »), et elle renvoie un **dictionnaire**, une structure que tu connais déjà. (Il existe aussi `tomllib.load`, qui lit depuis un fichier ouvert en mode binaire ; dans le `revisor`, nous lirons le texte nous-mêmes avec `read_text` pour contrôler l'encodage et les erreurs.)

Regarde comment le dictionnaire est fait. Il y a une seule clé, `'servicios'`, dont la valeur est une **liste de deux dictionnaires** : un pour chaque `[[servicios]]`. Le second dictionnaire a une clé de plus, `timeout_ms`, et sa valeur est le nombre `1000` : la troisième ligne de la sortie confirme que c'est un `int`. C'est ainsi que se lit n'importe quelle donnée d'un TOML : `datos["servicios"]` est la liste, `datos["servicios"][1]` est le deuxième service, `datos["servicios"][1]["nombre"]` est son nom. Et la dernière ligne de la sortie montre quelque chose que nous utiliserons beaucoup : `segundo.get("proxy")` interroge une clé qui **n'existe pas** et renvoie `None`, alors que `segundo["proxy"]` aurait levé un `KeyError`. Pour les données facultatives (comme `timeout_ms`), `.get` est l'outil.

Et si le TOML est mal écrit ? Regarde `fig06_12.py`, où il manque le guillemet fermant à la ligne du nom :

```python
# fig06_12.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo
url = "https://catalogo.example"
"""

try:
    tomllib.loads(TEXTO)
except tomllib.TOMLDecodeError as error:
    print(f"TOML inválido: {error}")
```

```text
$ python fig06_12.py
TOML inválido: Illegal character '\n' (at line 3, column 19)
```

`tomllib.TOMLDecodeError` est l'exception d'un TOML invalide. Son message, `Illegal character '\n' (at line 3, column 19)`, dit « caractère illégal, un saut de ligne, à la ligne 3, colonne 19 » : le texte a commencé par un guillemet et a trouvé la fin de la ligne sans qu'il ait été fermé. Remarque que le message te mène au point exact, et que c'est le module lui-même qui le dit. Dans le `revisor`, nous inclurons ce message tel quel dans l'erreur de configuration. Les fonctions et les exceptions de ce module se trouvent dans la [documentation de `tomllib`](https://docs.python.org/3/library/tomllib.html) ; le module est entré dans la bibliothèque standard en Python 3.11 avec la [PEP 680](https://peps.python.org/pep-0680/).

#### 6.3.3 Lire et écrire du JSON avec `json`

JSON a des règles plus strictes et un vocabulaire plus petit. Un objet JSON s'écrit entre accolades, avec des paires `"llave": valor` ; une liste, entre crochets ; les textes, entre guillemets doubles (**toujours doubles**) ; les nombres, sans guillemets ; et il existe trois mots : `true`, `false` et `null`. Python a un équivalent pour chaque élément, et le module `json` convertit de l'un à l'autre :

| JSON | Python |
|---|---|
| objet `{...}` | `dict` |
| tableau `[...]` | `list` |
| texte `"..."` | `str` |
| nombre entier | `int` |
| nombre à décimales | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Les règles strictes sont celles du standard ; le module `json` de Python, par défaut, est un peu plus permissif, et [sa documentation](https://docs.python.org/3/library/json.html) le dit franchement : il accepte et écrit `NaN`, `Infinity` et `-Infinity` (les « pas un nombre » et « infini » des `float`), que le standard n'admet pas, et si un objet répète une clé, il garde la dernière valeur. Pour le `revisor`, cela n'a pas d'importance, parce que ses nombres sont des entiers ; si un jour tu as besoin d'un JSON que n'importe quel autre programme accepte, `json.dumps(..., allow_nan=False)` refuse d'écrire ces valeurs.

La conversion de Python vers JSON (**sérialiser**) se fait avec `json.dumps` (« *dump string* » : déverser vers un texte), et l'inverse (**désérialiser**) avec `json.loads`. Regarde `fig06_13.py`, qui utilise un résultat du `revisor` comme exemple :

```python
# fig06_13.py
import json

resultado = {
    "nombre": "reportes",
    "estado": "CAIDO",
    "tiempo_ms": None,
    "detalle": "sin conexión",
    "activo": True,
}

texto = json.dumps(resultado, ensure_ascii=False, indent=2)
print(texto)

de_vuelta = json.loads(texto)
print(de_vuelta["tiempo_ms"] is None, de_vuelta == resultado)

print(json.dumps(resultado["detalle"]))
print(json.dumps(resultado["detalle"], ensure_ascii=False))
```

```text
$ python fig06_13.py
{
  "nombre": "reportes",
  "estado": "CAIDO",
  "tiempo_ms": null,
  "detalle": "sin conexión",
  "activo": true
}
True True
"sin conexi\u00f3n"
"sin conexión"
```

Quatre choses à apprendre de cette sortie. Une : `None` est devenu `null` et `True` est devenu `true` ; le JSON n'est pas du Python, et chaque langage a son orthographe de « rien » et de « vrai ». Deux : `indent=2` fait que `dumps` écrit le résultat sur plusieurs lignes avec deux espaces d'indentation, lisible pour une personne ; sans lui, tout sortirait sur une seule ligne compacte. Trois : la vérification `de_vuelta == resultado` donne `True`, parce que `loads` reconstruit le dictionnaire d'origine, et `de_vuelta["tiempo_ms"] is None` aussi, parce que `null` revient comme `None`. Et quatre, la plus fine : les deux dernières lignes affichent le même texte, « sin conexión », de deux façons. Par défaut, `dumps` **échappe** tout caractère qui n'est pas ASCII et écrit `"sin conexi\u00f3n"`, qui est du JSON valide mais illisible pour une personne. Avec `ensure_ascii=False`, il écrit le « ó » tel quel. Comme le `revisor` écrit en espagnol, le rapport JSON portera toujours `ensure_ascii=False`. C'est la forme que le cours fixe pour tout le rapport : `json.dumps(datos, ensure_ascii=False, indent=2)`.

Un avertissement qui s'apprend mieux à ses dépens. `json.dumps` ne comprend que les types du tableau ci-dessus (et le tuple, qu'il écrit comme un tableau, comme une liste). Les données du `revisor` sont dans des objets à nous, `Resultado`, `Servicio` et `Estado`, et si tu essaies `json.dumps(Estado.CAIDO)`, tu obtiens `TypeError: Object of type Estado is not JSON serializable` (« un objet de type `Estado` ne peut pas être sérialisé en JSON »). La solution est de construire d'abord un dictionnaire avec des types simples, en utilisant `estado.value` pour extraire le texte de l'`Enum`, et de sérialiser ce dictionnaire. C'est ce que fera la fonction `reporte_a_json` plus loin.

Et comme le TOML, le JSON échoue aussi. Regarde `fig06_14.py`, où il manque une virgule entre deux paires :

```python
# fig06_14.py
import json

TEXTO = """{
  "nombre": "pagos",
  "tiempo_ms": 87
  "estado": "ARRIBA"
}"""

try:
    json.loads(TEXTO)
except json.JSONDecodeError as error:
    print(f"mensaje: {error.msg}")
    print(f"línea {error.lineno}, columna {error.colno}")
    print(f"completo: {error}")
```

```text
$ python fig06_14.py
mensaje: Expecting ',' delimiter
línea 4, columna 3
completo: Expecting ',' delimiter: line 4 column 3 (char 43)
```

`json.JSONDecodeError` conserve le problème dans trois attributs utiles : `msg` (« une virgule était attendue comme délimiteur »), `lineno` (la ligne) et `colno` (la colonne). Ici, ligne 4, colonne 3 : après le `87` de la ligne précédente, il aurait fallu une virgule, et le décodeur a constaté son absence juste au début de la paire suivante. Le message complet, que l'on obtient en affichant l'erreur, porte en plus `char 43`, la position comptée depuis le début. La [documentation de `json`](https://docs.python.org/3/library/json.html) décrit tous les paramètres de `dumps` et `loads`, et le [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) est la spécification du format. Que `JSONDecodeError` soit aussi un `ValueError` te dit quelque chose que tu sais déjà depuis 6.1.3 : un `except ValueError` l'attraperait, avec beaucoup d'autres erreurs qui n'ont rien à voir. Il vaut toujours mieux nommer le type précis.

### 6.4 Valider ce qui arrive de l'extérieur

#### 6.4.1 Pourquoi il faut valider, et où

Un fichier peut être bien écrit et être pourtant inutile. Ce TOML est parfaitement valide :

```toml
[[servicios]]
nombre = 42
url = "ftp://archivos.example"
timeout_ms = -3
```

Chaque ligne suit les règles de TOML. Mais le nom est un nombre, l'adresse n'est pas celle d'une page web, et le délai d'attente est négatif. Si le programme l'accepte sans le regarder, l'erreur apparaîtra plus tard, loin de sa cause, sur une ligne qui n'a rien à voir avec le fichier : un `TypeError` en essayant d'aligner un nom, ou une requête qui ne part jamais. **Valider**, c'est vérifier, au moment où les données entrent, qu'elles ont la forme et le sens que le programme attend.

Il y a une raison propre à Python de le faire à la main. Dans la [Leçon 0](00-que-es-python.md), tu as vu que les annotations de type (`nombre: str`) **ne sont pas imposées à l'exécution** : c'est une note pour toi et pour les outils, pas un cadenas. Un `Servicio(nombre=42, ...)` se crée sans protester. C'est pourquoi la frontière du programme, le point où entre ce qui vient de l'extérieur, est l'endroit où l'on vérifie vraiment les types. Une fois validés, le reste du programme peut leur faire confiance sans regarder de nouveau. Cette idée, **valider à la frontière et faire confiance à l'intérieur**, organise tout le `revisor` : un seul module, `configuracion.py`, se charge de se méfier de l'extérieur.

La règle de fond est celle que formule le [guide de validation des entrées d'OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) : ce qui arrive de l'extérieur n'est pas digne de confiance tant qu'il n'a pas été vérifié, et la vérification qui fonctionne le mieux est une **liste de ce qui est permis** : on énumère ce qui est valable et on rejette tout le reste, au lieu d'essayer d'énumérer tout ce qui est faux.

#### 6.4.2 `isinstance` et le piège de `bool`

Pour demander « cette valeur est-elle de ce type ? », il existe `isinstance(valor, tipo)`, une fonction qui renvoie `True` ou `False`. `isinstance(5000, int)` est `True` ; `isinstance("5000", int)` est `False`, parce que le texte « 5000 » n'est pas un entier même s'il y ressemble. Avec elle, on peut écrire la validation du délai d'attente : « ce doit être un entier supérieur à zéro ». Et ici il y a un piège qui mérite sa propre figure. Regarde `fig06_15.py` :

```python
# fig06_15.py
print(isinstance(True, int))
print(isinstance(True, bool))
print(True + True)


def timeout_valido(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


for valor in [5000, 0, -1, True, "5000", 2.5]:
    print(valor, type(valor), timeout_valido(valor))
```

```text
$ python fig06_15.py
True
True
2
5000 <class 'int'> True
0 <class 'int'> False
-1 <class 'int'> False
True <class 'bool'> False
5000 <class 'str'> False
2.5 <class 'float'> False
```

Les trois premières lignes sont le piège. `isinstance(True, int)` est **`True`** : en Python, un `bool` est un type d'entier. `True` est littéralement le nombre 1, et `False` le 0, et c'est pourquoi `True + True` donne `2`. Ce n'est pas un accident : c'est une décision de conception ancienne du langage, décrite dans la [documentation des types intégrés](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool). La conséquence, pour toi, est concrète. Une validation naïve comme `isinstance(timeout_ms, int) and timeout_ms > 0` **accepte `true`** comme délai d'attente, parce que `true` est un entier positif : il vaut 1. Quelqu'un qui écrit `timeout_ms = true` dans le fichier (une confusion compréhensible) obtiendrait un délai d'attente d'une milliseconde sans que personne ne se plaigne.

La fonction `timeout_valido` du programme l'évite : elle demande `isinstance(valor, int)` **et en plus** `not isinstance(valor, bool)`. Les six dernières lignes de la sortie montrent le résultat avec six valeurs : l'entier 5000 passe ; le 0 et le -1 ne passent pas à cause de la condition `valor > 0` ; `True` ne passe pas ; le texte `"5000"` ne passe pas (c'est un `str`) ; et le décimal `2.5` non plus (c'est un `float`). Remarque que le test a été fait avec une **liste de valeurs représentatives**, y compris les cas bizarres : c'est ainsi qu'on teste une validation, en regardant justement les valeurs qui pourraient se glisser.

#### 6.4.3 Adresses : le schéma permis

Une autre donnée extérieure du `revisor` est l'adresse (`url`) de chaque service. Une adresse a des parties, et la première est le **schéma** : ce qui précède les deux-points, et qui dit quel protocole utiliser (`https`, `http`, `ftp`, `file`...). Pour un vérificateur de services web, seuls deux ont du sens : `http` et `https`. Pourquoi est-ce si important ? Parce que plus tard le programme fera une requête vers cette adresse, et avec la bibliothèque `urllib`, une adresse `file:///...` fait que le programme **lit un fichier du disque** au lieu d'interroger un service, alors que d'autres schémas le feraient parler à un autre type de serveur. Un fichier de configuration qu'une autre personne a modifié ne doit pas pouvoir obtenir cela.

La bibliothèque standard fournit `urllib.parse.urlsplit`, qui découpe une adresse en ses composants. Regarde `fig06_16.py`, qui teste six adresses :

```python
# fig06_16.py
from urllib.parse import urlsplit

DIRECCIONES = [
    "https://catalogo.example",
    "http://127.0.0.1:8099/catalogo",
    "ftp://archivos.example",
    "file:///etc/hosts",
    "catalogo.example",
    "javascript:alert(1)",
]

for direccion in DIRECCIONES:
    esquema = urlsplit(direccion).scheme
    permitida = esquema in {"http", "https"}
    print(f"{direccion:<32} esquema='{esquema}' permitida={permitida}")
```

```text
$ python fig06_16.py
https://catalogo.example         esquema='https' permitida=True
http://127.0.0.1:8099/catalogo   esquema='http' permitida=True
ftp://archivos.example           esquema='ftp' permitida=False
file:///etc/hosts                esquema='file' permitida=False
catalogo.example                 esquema='' permitida=False
javascript:alert(1)              esquema='javascript' permitida=False
```

`urlsplit(direccion).scheme` est le schéma. La validation est une question d'appartenance : `esquema in {"http", "https"}`, avec l'ensemble de ce qui est permis, comme dans la liste des permis dont nous avons parlé. Observe les cas : les deux premières adresses passent ; `ftp` et `file` non ; `catalogo.example` (sans schéma) a un schéma vide et ne passe pas ; et `javascript:alert(1)` a le schéma `javascript`, qui ne passe pas non plus. Note le choix de conception : on n'a **pas** écrit une liste de schémas interdits (`ftp`, `file`, `javascript`...), parce que demain quelqu'un en invente un autre et il se glisse. On a écrit la liste des deux permis. Le standard qui définit comment on découpe une adresse est le [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), et les fonctions se trouvent dans la [documentation de `urllib.parse`](https://docs.python.org/3/library/urllib.parse.html).

Ne regarder que le schéma, pourtant, laisse passer deux classes d'adresses cassées, et il faut les voir. La première est une adresse sans serveur : `https://` tout court, ou `http:catalogo` (sans les deux barres obliques), ont le bon schéma mais aucun serveur à appeler. La seconde est pire : il y a des adresses que `urlsplit` ne peut même pas découper. Avec `http://[::1` (un crochet qui s'ouvre et ne se ferme pas), `urlsplit` ne renvoie rien : il **lance** `ValueError: Invalid IPv6 URL`. Et avec `http://127.0.0.1:abc/`, l'adresse est découpée, mais quand on demande le port (`.port`, le nombre qui vient après les deux-points), on obtient `ValueError: Port could not be cast to integer value as 'abc'`. Si la validation n'attrape pas ce `ValueError`, un fichier de configuration mal écrit fait tomber le programme avec un *traceback* au lieu du message clair que nous avons promis. La [documentation de `urllib.parse`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit) le signale : `urlsplit` ne valide pas, et les crochets sans pendant lancent `ValueError`.

Il y a une troisième classe, plus cachée. En TOML, à l'intérieur d'un texte entre guillemets, `\n` est un saut de ligne, donc `url = "http://127.0.0.1:8099/cata\nlogo"` arrive à Python avec un saut de ligne au milieu. `urlsplit` **le supprime en silence** (sa documentation le dit : il retire les sauts de ligne et les tabulations, comme le font les navigateurs) et l'adresse semble bonne ; mais la bibliothèque qui fera la requête dans la leçon 9, `httpx`, le voit, elle, et la rejette avec une erreur à elle, qui n'est pas une erreur réseau. Quelque chose de semblable peut arriver avec des lettres qui ne sont pas de l'anglais dans le nom du serveur, que `httpx` doit convertir en une forme spéciale et ne le peut parfois pas. La défense simple est de n'accepter, dans le fichier de configuration, rien qui ne soit du texte ordinaire.

C'est pourquoi le `revisor` ne demande pas directement le schéma, mais utilise une petite fonction qui rassemble toutes les questions :

```python
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
```

Elle se lit de haut en bas. Le premier `if` écarte ce qui n'est pas du texte ordinaire, avec trois méthodes des textes : `isascii()` est `True` si tous les caractères sont ASCII (les lettres de l'anglais, les chiffres et les signes d'un clavier de base ; un `é` ne l'est déjà plus) ; `isprintable()` est `True` si aucun n'est un caractère de contrôle, comme le saut de ligne ; et `" " in url` demande s'il y a une espace quelque part. Si l'une des trois échoue, le `revisor` n'accepte pas l'adresse. Attention : cela ne veut pas dire qu'elle est invalide sur internet ; `https://catálogo.example` est une adresse légitime. C'est une règle du `revisor`, plus stricte que celle des navigateurs : dans sa configuration, un tel nom s'écrit sous sa forme ASCII, celle qui commence par `xn--`. Ensuite, tout va dans un `try`, parce que découper l'adresse comme lire le port peuvent lancer `ValueError`, et pour cette fonction cette erreur n'a qu'une réponse : l'adresse ne convient pas, `False`. À l'intérieur, trois conditions reliées par `and` : le schéma est l'un des deux permis ; `partes.hostname`, le nom du serveur, existe (dans `https://` tout court, il vaut `None`) ; et le port, s'il y en a un, est un nombre supérieur à 0. Les trois sont entre parenthèses pour pouvoir les répartir sur plusieurs lignes. Un détail de `and` qui importe ici : il évalue de gauche à droite et **s'arrête à la première condition fausse**, de sorte que le port n'est lu que si les deux premières sont déjà remplies. Avec cela, les six adresses de `fig06_16.py` donnent le même résultat qu'avant, et toutes les cassées de ces paragraphes sortent `False`. Ce que cette validation ne vérifie pas, c'est que le serveur existe ou répond : cela ne se sait qu'en l'interrogeant, et c'est le travail du `revisor` à partir de la leçon 9. Elle ne garantit pas non plus que `httpx` accepte tout ce qui passe : `http://999.1.1.1:8099/pagos` a un schéma, un serveur et un port, mais 999 ne tient pas dans une adresse IP (chaque partie va de 0 à 255), et `httpx` la rejette. C'est pourquoi la leçon 9, en plus d'expliquer pourquoi `file://` est un risque concret quand on utilise `urllib`, met un second filet à l'interrogation : une adresse que `httpx` ne peut pas utiliser sort dans le rapport comme « dirección inválida » (adresse invalide), sans faire tomber les autres.

#### 6.4.4 Pourquoi ni `eval` ni `pickle`

Avec le vocabulaire de cette leçon, on peut maintenant expliquer quelque chose qu'on voit dans beaucoup de programmes de débutants et qui est un risque sérieux. Quelqu'un pense : « pour lire une liste de services, je n'ai pas besoin d'un format ; j'écris la liste comme du code Python dans un fichier, et le programme l'exécute ». Il existe une fonction qui le permet : `eval(texto)`, qui prend un texte, l'interprète **comme du code** et renvoie son résultat. Regarde `fig06_17.py`, une démonstration de ce qu'il **ne** faut **pas** faire :

```python
# fig06_17.py
# DEMOSTRACIÓN de lo que NO se hace: eval con un texto que viene de fuera.
print(eval("2300 + 1"))

texto_de_fuera = "print('esto lo escribió otro y se ejecutó')"
eval(texto_de_fuera)
```

```text
$ python fig06_17.py
2301
esto lo escribió otro y se ejecutó
```

Le premier appel paraît innocent : `eval("2300 + 1")` calcule et renvoie `2301`. Le second montre le problème : le texte venu de l'extérieur était une **instruction**, et `eval` l'a exécutée. Ici, c'était un `print` inoffensif ; ç'aurait pu être n'importe quoi que Python sait faire : supprimer des fichiers, lire des mots de passe, ouvrir une connexion vers un autre ordinateur. Qui contrôle le texte contrôle le programme. La [documentation de `eval`](https://docs.python.org/3/library/functions.html#eval) le dit sans détour : il exécute du code arbitraire et restreindre les fonctions qu'il peut utiliser n'est pas un mécanisme de sécurité. Il existe une variante plus prudente, `ast.literal_eval`, qui n'accepte que des valeurs littérales (nombres, textes, listes), mais la [documentation du module `ast`](https://docs.python.org/3/library/ast.html#ast.literal_eval) avertit qu'elle ne convient pas non plus aux entrées non fiables : un texte très grand ou très imbriqué peut épuiser la mémoire ou la pile de Python.

L'autre cas est `pickle`, le module qui enregistre des objets Python dans un fichier et les reconstruit ensuite. C'est pratique, parce qu'il n'y a pas de format à monter : on enregistre l'objet et on le récupère. Mais reconstruire un objet peut exécuter du code, et c'est pourquoi la [documentation de `pickle`](https://docs.python.org/3/library/pickle.html) s'ouvre sur un avertissement en gros : **ne charge jamais de données d'une source qui n'est pas de confiance**, parce qu'un fichier fait exprès peut exécuter ce que veut son auteur sur ton ordinateur. On ne montre même pas ici comment on fait, parce que ce cours ne l'utilise pas. Ce genre de faille a un nom dans le catalogue des faiblesses logicielles : [CWE-502, désérialisation de données non fiables](https://cwe.mitre.org/data/definitions/502.html). La solution est celle que tu as déjà : **les données extérieures se lisent avec des formats qui ne décrivent que des données**. TOML et JSON décrivent des valeurs, pas des instructions ; quelque effort que l'on fasse pour les écrire, `tomllib.loads` et `json.loads` ne peuvent renvoyer que des dictionnaires, des listes, des textes, des nombres et des booléens (plus `None` en JSON, et des dates et des heures en TOML, que `tomllib` renvoie comme des valeurs du module `datetime`). Aucun de ces types n'exécute quoi que ce soit. C'est pourquoi le `revisor` les utilise.

Qu'ils n'exécutent rien ne veut pas dire qu'ils ne puissent pas faire de mal autrement. Les documentations de [`tomllib`](https://docs.python.org/3/library/tomllib.html) et de [`json`](https://docs.python.org/3/library/json.html) portent le même avertissement : un texte fait avec de mauvaises intentions (énorme, ou imbriqué sur des milliers de niveaux) peut faire que la lecture consomme beaucoup de processeur et beaucoup de mémoire, et elles recommandent de **limiter la taille** de ce que l'on lit. Le `revisor` ne le fait pas, et c'est une décision consciente : il lit un fichier de configuration qu'écrit celui qui l'utilise, de quelques centaines d'octets. Mais si un programme à toi reçoit du TOML ou du JSON d'autres personnes (par le réseau, d'un formulaire), la première chose est de vérifier la taille avant de le lire, par exemple avec `ruta.stat().st_size`, qui dit combien d'octets mesure un fichier, et de rejeter ce qui dépasse une limite raisonnable.

Si tu veux continuer avec la partie sécurité des systèmes qui exposent des services, le blog de Hábil a un article sur la [sécurité des API : identité, passerelle et jetons](https://www.habil.mx/fr/blog/securite-api-cto-identite-passerelle-jetons/). Et si tu veux voir comment un autre langage résout ce même problème des données extérieures avec le même `revisor`, le [cours de TypeScript](https://www.habil.mx/fr/cours/typescript/) a une leçon entière pour cela.

#### 6.4.5 L'étape du projet : le `revisor` lit sa configuration

Tu as toutes les pièces. Il reste à les assembler. Le `revisor` de cette leçon est ainsi, dans ton dossier `~/curso-python/revisor/` :

```text
revisor/
  servicios.toml      ← NUEVO: los datos, ahora fuera del código
  configuracion.py    ← NUEVO: lee, valida y traduce los errores
  formato.py          ← tiene una función más: reporte_a_json
  revisor.py          ← ya no tiene SERVICIOS escrito a mano
  modelo.py  revision.py   (sin cambios)
```

Commence par les données. Voici le fichier `servicios.toml`, avec les quatre mêmes services de toujours ; c'est lui qui remplace la liste que tu avais dans le code :

```toml fig06_18/servicios.toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "inventario"
url = "https://inventario.example"

[[servicios]]
nombre = "pagos"
url = "https://pagos.example"

[[servicios]]
nombre = "reportes"
url = "https://reportes.example"
```

Maintenant le nouveau module, `configuracion.py`. C'est le plus long de la leçon, mais tu connais déjà chaque partie. Lis-le en entier une fois, puis on le démonte :

```python
# fig06_18/configuracion.py
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from modelo import Servicio, nombres_repetidos


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


def tiene_credenciales(url: str) -> bool:
    partes = urlsplit(url)
    return partes.username is not None or partes.password is not None


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
    if tiene_credenciales(url):
        raise ErrorDeConfiguracion(
            f"servicio {posicion}: 'url' no debe llevar usuario ni clave"
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

La fonction `leer_servicios` reçoit un chemin et renvoie la liste de `Servicio`. Elle procède en quatre étapes, et dans chacune la règle est la même : **traduire dans le domaine de la configuration toute erreur dont la cause peut se trouver dans le fichier**.

1. **Lire le texte.** `ruta.read_text(encoding="utf-8")` est dans un `try` avec un seul `except`, pour `FileNotFoundError`. C'est la seule erreur de lecture qui sait s'expliquer clairement (« le fichier n'existe pas »), donc c'est la seule qu'on attrape. Si le fichier existe mais que tu n'as pas la permission de le lire, l'erreur est un `PermissionError`, et **elle ne l'attrape pas** : la fonction n'a rien d'utile à dire à ce sujet, et il vaut mieux que le programme s'arrête avec le rapport du système. (L'exercice 4 te demande de compléter cela avec une autre erreur, celle de l'encodage.)
2. **Interpréter le TOML.** `tomllib.loads` est dans son propre `try` avec son propre `except` : s'il y a un `TOMLDecodeError`, le message de `tomllib` est inclus dans le nôtre. On fait `raise ... from error` dans les deux cas, pour la raison de 6.1.4.
3. **Vérifier la forme générale.** `datos.get("servicios")` cherche la liste ; si ce n'est pas une liste, ou si elle est vide, on signale qu'elle manque. Cette étape protège contre un TOML qui est valide mais qui n'est pas le nôtre.
4. **Vérifier chaque service.** Une liste en compréhension (leçon 4) appelle `validar_servicio` pour chaque élément, avec sa position. La fonction `enumerate(lista, start=1)`, que tu as vue dans la leçon 3, fournit la position de chaque élément avec l'élément ; le paramètre `start=1` fait que le compte commence à **1** au lieu de 0, parce que « le service 2 » est la façon dont parle une personne. À la fin, `nombres_repetidos` (leçon 5) renvoie l'ensemble des noms qui apparaissent plus d'une fois. S'il n'est pas vide (`len(repetidos) > 0`, la même question de taille que tu as déjà utilisée avec les listes), on le signale ; `sorted(repetidos)` les met par ordre alphabétique et `", ".join(...)` les réunit en un seul texte séparé par des virgules (`join`, « joindre », est une méthode des textes qui rassemble les éléments d'une liste en utilisant ce texte comme séparateur).

La fonction `validar_servicio` reçoit `datos: object`, le type le plus général qui existe, exprès : **elle ne sait pas ce que c'est**, parce que cela vient de l'extérieur. La première chose est de vérifier avec `isinstance(datos, dict)` que c'est un dictionnaire. Ensuite elle vérifie champ par champ, dans cet ordre, et s'arrête au premier problème :

- le `nombre` doit exister et être un texte non vide (`nombre.strip() == ""` attrape le texte qui ne contient que des espaces) ;
- l'`url` doit exister et passer `es_url_http` : schéma permis, un serveur et, s'il y en a un, un port valide (6.4.3), et elle ne doit porter ni utilisateur ni mot de passe (`tiene_credenciales`) : une adresse comme `http://usuario:clave@...` contient un secret, et le `revisor` ne doit ni le garder ni le répéter ;
- `timeout_ms`, qui est facultatif, n'est vérifié que s'il est présent (`"timeout_ms" not in datos` ; l'opérateur `in` demande si une clé est dans le dictionnaire), et doit être un entier supérieur à 0 qui n'est **pas** un `bool` (6.4.2).

Si tout va bien, elle renvoie un `Servicio`. S'il n'y a pas de `timeout_ms`, elle ne le passe pas : la valeur par défaut de 5000 est posée par la définition de `Servicio`, qui vient de la leçon 5. Chaque message d'erreur commence par `servicio N:` pour que celui qui modifie le fichier sache **quel** élément vérifier. Les messages que produit le module sont ceux-ci, avec la position comptée à partir de 1 :

| Cas | Message |
|---|---|
| le fichier n'existe pas | `no existe el archivo servicios.toml` |
| TOML mal écrit | `servicios.toml no es TOML válido: <mensaje de tomllib>` |
| la liste manque | `falta la lista [[servicios]]` |
| un champ manque | `servicio 2: falta 'nombre'` |
| le service n'est pas une table | `servicio 2: debe ser una tabla` |
| nom vide ou qui n'est pas un texte | `servicio 2: 'nombre' debe ser un texto que no esté vacío` |
| url qui n'est pas une adresse http/https valide | `servicio 2: 'url' debe ser una dirección http:// o https:// válida` |
| url avec utilisateur ou mot de passe | `servicio 2: 'url' no debe llevar usuario ni clave` |
| délai d'attente invalide | `servicio 3: 'timeout_ms' debe ser un entero mayor que 0` |
| noms répétés | `nombres repetidos: catalogo` |

Le fichier `formato.py` a gagné deux fonctions. Aucune des précédentes n'a changé (`formatear_tiempo`, `encabezado`, `linea`, `contar`, `resumen`) ; on a seulement ajouté `import json` et `from urllib.parse import urlsplit, urlunsplit` au début et ces deux fonctions à la fin :

```python
def url_sin_secretos(url: str) -> str:
    partes = urlsplit(url)
    servidor = partes.netloc.rpartition("@")[2]
    return urlunsplit((partes.scheme, servidor, partes.path, "", ""))


def reporte_a_json(resultados: list[Resultado]) -> str:
    tiempos_ms = [r.tiempo_ms for r in resultados if r.tiempo_ms is not None]
    promedio_ms: int | None = None
    if len(tiempos_ms) > 0:
        promedio_ms = round(sum(tiempos_ms) / len(tiempos_ms))
    datos = {
        "servicios": [
            {
                "nombre": r.servicio.nombre,
                "url": url_sin_secretos(r.servicio.url),
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

C'est l'application directe de 6.3.3 : on construit un dictionnaire avec des types que JSON comprend (c'est pourquoi `r.estado.value` et non `r.estado`), et on le sérialise avec `ensure_ascii=False, indent=2`. La moyenne sort comme `None` (que JSON écrit `null`) quand aucun service n'a répondu, parce qu'on ne peut rien moyenner. Remarque aussi une répétition laissée exprès : les comptes de `resumen` et ceux de ce dictionnaire sont les mêmes, calculés deux fois. On l'a fait ainsi pour ne pas toucher à ce qui fonctionne déjà dans la leçon 5, mais c'est le même problème que celui par lequel cette leçon a commencé, celui d'une donnée calculée à deux endroits : si un jour la règle de la moyenne change, il faudra la changer aux deux. Note-le dans ton journal de bord : c'est le genre de dette qui se paie la prochaine fois qu'on touche au rapport.

`url_sin_secretos` existe parce que le rapport sort de ton programme : on l'enregistre dans un fichier, on le colle dans une discussion, un autre programme le lit. Si l'adresse porte un secret dans la requête (`?token=...`) ou quelque chose dans le fragment (`#...`), le rapport ne doit pas le répéter. `urlsplit` découpe l'adresse (6.4.3) ; `partes.netloc.rpartition("@")[2]` garde ce qui vient après le dernier `@`, c'est-à-dire le serveur et le port sans utilisateur ni mot de passe (`rpartition` coupe le texte en trois à la dernière apparition du séparateur, et `[2]` est la partie de droite ; s'il n'y a pas de `@`, c'est le texte entier) ; et `urlunsplit` recompose l'adresse avec le schéma, le serveur et le chemin, et avec une requête et un fragment vides. Ainsi, `http://127.0.0.1:1/estado?token=SECRETO#x` sort dans le rapport comme `http://127.0.0.1:1/estado`. Une adresse avec utilisateur ou mot de passe n'arrive même pas ici, parce que `validar_servicio` la rejette au chargement ; les retirer aussi ici est un second filet. On expurge l'adresse au lieu de retirer le champ parce que le JSON est un contrat (tu le verras après l'exécution) : qui le lit compte sur le fait que chaque service porte son `url`, et sans les secrets il sait toujours à quel serveur et à quel chemin se rapporte chaque entrée.

Il manque le programme principal. Voici `revisor.py`, qui a perdu la liste de services et gagné une constante avec le chemin du fichier :

```python
# fig06_18/revisor.py
from pathlib import Path

from configuracion import ErrorDeConfiguracion, leer_servicios
from formato import encabezado, linea, resumen
from revision import revisar_todos

RUTA_CONFIG = Path("servicios.toml")


def main() -> None:
    try:
        servicios = leer_servicios(RUTA_CONFIG)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        return

    resultados = revisar_todos(servicios)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
```

`RUTA_CONFIG = Path("servicios.toml")` est une constante (majuscules, comme `UMBRAL_LENTO_MS`) avec le chemin relatif. Dans `main`, l'appel à `leer_servicios` est dans un `try` qui attrape **seulement** `ErrorDeConfiguracion` : c'est l'exception personnalisée de 6.1.4, la seule erreur que ce programme sait expliquer. Si elle se produit, il affiche `error de configuración: ` suivi du message, et `return` termine `main` sans aller plus loin. Toute autre erreur (un `ZeroDivisionError` dû à un défaut, par exemple) n'est pas attrapée, et s'arrête avec son rapport pour que quelqu'un la corrige.

Attention à une conséquence : quand il signale une erreur de configuration, le programme se termine **avec le code de sortie 0**, celui qui dans le terminal signifie « tout va bien ». Pour une personne qui lit l'écran, cela n'a pas d'importance ; pour un autre programme qui l'appelle et ne regarde que le code, cela ressemble à un succès. C'est une dette que cette leçon laisse en connaissance de cause, pour ne pas mélanger les sujets : dans la [Leçon 7](07-paquete-linea-de-comandos.md), cette branche se terminera avec le code 2 ; ici, on se contente d'afficher. Exécute-le :

```text
$ cd fig06_18
$ python revisor.py
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión

4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms
```

C'est le même rapport que dans la leçon 5, avec le même tableau et le même récapitulatif (`4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`), mais maintenant les quatre services viennent de `servicios.toml`. Si tu ajoutes un service au fichier, il apparaît dans le tableau sans toucher à Python (tu verras un cas dans l'exercice 1).

Pour voir le JSON du rapport, le projet fournit un script d'appui, `ver_json.py`. Il ne fait pas partie du programme : il réunit seulement la lecture de la configuration, la vérification et `reporte_a_json`, pour que tu voies le résultat avant que, dans la leçon 7, il existe une option de ligne de commande pour le demander :

```python
# fig06_18/ver_json.py
from configuracion import leer_servicios
from formato import reporte_a_json
from revision import revisar_todos
from revisor import RUTA_CONFIG

servicios = leer_servicios(RUTA_CONFIG)
print(reporte_a_json(revisar_todos(servicios)))
```

```text
$ python ver_json.py
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
```

C'est le JSON que le cours fixe pour le rapport du `revisor`, et il ne change pas dans les leçons suivantes : `servicios` est une liste avec une entrée par service, `tiempo_ms` vaut `null` pour celui qui n'a pas répondu, et `resumen` reprend les comptes. Qui consomme ce rapport depuis un autre programme peut s'appuyer sur cette forme. La seule chose que le rapport change dans l'adresse, c'est qu'il en retire les secrets : les quatre services de `servicios.toml` n'en portent aucun, et c'est pourquoi leur `url` sort identique à celle du fichier.

## L'erreur que tu vas voir

La leçon a une erreur principale, celle du fichier qui n'est pas là où tu crois, et quatre messages d'appui que tu as déjà vus et qu'il convient de savoir lire d'un coup d'œil.

**L'erreur principale.** Exécute le `revisor` depuis le dossier **du dessus**, celui qui contient `fig06_18`, au lieu d'entrer dedans :

```text
$ python fig06_18/revisor.py
error de configuración: no existe el archivo servicios.toml
```

Le programme trouve le code (tu lui as donné le chemin), mais `RUTA_CONFIG` est **relatif** : `Path("servicios.toml")` signifie « le `servicios.toml` du dossier où je me trouve », pas « celui qui est à côté du programme ». Depuis le dossier du dessus, ce fichier n'existe pas. Remarque ce que le programme a bien fait : il n'a pas affiché de rapport d'erreur ni l'exception `FileNotFoundError` en anglais avec le texte du système ; il a affiché le message en espagnol que tu as écrit, qui dit ce qui manque. Et c'est la même erreur que tu verras un jour quelconque, quand un script fonctionnera sur ton ordinateur et échouera sur un autre : neuf fois sur dix, le fichier existe, mais **le dossier depuis lequel on exécute est un autre**. Pour savoir dans quel dossier tu te trouves, la commande `pwd` te le dit. Dans la leçon 7, `--config` te laissera indiquer le chemin sans dépendre de l'endroit où tu es.

**Les quatre messages d'appui**, à lire de bas en haut :

- `ValueError: invalid literal for int() with base 10: '142 ms'` : un texte qu'on a voulu convertir en entier et qui n'est pas fait uniquement de chiffres (`fig06_01.py`). Vérifie quel texte est arrivé.
- `FileNotFoundError: [Errno 2] No such file or directory: 'no-esta.txt'` : le chemin ne mène à rien. Vérifie le dossier de travail et l'orthographe (`fig06_08.py`).
- `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 10` : le fichier n'est pas en UTF-8, et l'octet que mentionne Python dit à quelle position ça a cessé de coller (`fig06_10.py`).
- `TypeError: Object of type Estado is not JSON serializable` : tu as essayé de sérialiser un objet à toi sans le convertir en types simples. Construis un dictionnaire avec `.value`.

## Ce qui se fait de travers

**Écrire `except:` sans type, ou `except Exception:` au cas où.** Tu as déjà vu le coût en 6.1.3 : une faute d'orthographe se déguise en une autre erreur ; et avec le `except:` nu, en plus, le programme peut ne pas s'arrêter même avec `Ctrl`+`C`. L'exception précise, toujours.

**Avaler l'erreur en silence.** Un `except ValueError: pass` (« ne fais rien ») fait que le programme continue avec des données qui n'existent pas. Le temps d'`inventario` reste non lu, le rapport sort avec une ligne fausse, et personne ne sait pourquoi. Si tu attrapes une exception, **fais quelque chose avec elle** : signale, traduis, renvoie une valeur définie. Si tu ne sais pas quoi faire, ne l'attrape pas.

**Un `try` énorme.** Mettre vingt lignes dans un `try` pour « tout protéger » fait que le `except` attrape des erreurs que tu n'attendais pas, de lignes qui n'ont rien à voir, comme dans `fig06_03.py`. Le `try` contient la ligne qui peut échouer de la manière que tu connais, et rien de plus.

**Traduire une exception sans `from`.** Le rapport continue à montrer l'originale, mais plus comme cause : il reste « pendant le traitement de l'exception précédente, une autre s'est produite », ce qui est pire pour celui qui débogue. Si tu remplaces une erreur par une autre, `raise ... from error`.

**Ouvrir des fichiers sans `with`.** Un `archivo = open(...)` sans son `close()` laisse le fichier ouvert si quelque chose échoue avant de le fermer, et cela ne se remarque que lorsque le programme en ouvre des centaines.

**Omettre `encoding="utf-8"`.** Ça marche sur ton ordinateur et ça échoue (ou, pire, ça lit mal les accents) sur un autre. Écris-le toujours.

**Joindre des chemins avec `+` ou avec `"/"` dans un texte.** Ça se casse dès que le système d'exploitation change ou qu'il y a une barre en trop. Avec `Path` et l'opérateur `/`, il n'y a pas à y penser.

**Valider avec le vrai ou le faux.** `if timeout_ms:` laisse passer `True` et, pire, **rejette le `0`** du même geste que celui avec lequel il rejette le vide, sans distinguer les cas. Demande exactement ce que tu veux savoir : `isinstance(timeout_ms, int)` et `timeout_ms > 0`.

**Valider avec `assert`.** L'instruction `assert condicion` échoue si la condition est fausse, et elle paraît une façon commode de valider. Mais Python peut s'exécuter dans un mode d'optimisation (`python -O`) dans lequel **tous les `assert` sont ignorés**, d'après la [référence de l'instruction](https://docs.python.org/3/reference/simple_stmts.html#assert). Une validation qui disparaît quand quelqu'un optimise le programme ne valide rien. Les `assert` sont pour les tests, que tu verras dans la leçon 8 ; pour les données extérieures, on utilise `if` et `raise`.

**Passer une donnée extérieure à `eval` ou à `pickle`.** C'est laisser l'auteur du fichier décider de ce que fait ton programme. On utilise TOML ou JSON.

## Exercices

### Exercice 1 — Ajoute des services sans toucher au code

Ajoute à ton `servicios.toml` les deux services supplémentaires du cours : `facturacion` (`https://facturacion.example`) et `notificaciones` (`https://notificaciones.example`, avec `timeout_ms = 1000`). Comme `revisar` utilise toujours des données simulées, ajoute-leur aussi leur entrée dans `SIMULADO` de `revision.py`, comme dans l'exercice 1 de la leçon 5 : `facturacion` répond 503 en 95 ms, et `notificaciones` ne répond pas (`tiempo agotado`). Avant d'exécuter, **prédis** le récapitulatif : combien de services il y a, combien en marche, lents et en panne, et quelle est la moyenne. Ensuite exécute et compare. Remarques-tu quelque chose de bizarre dans le tableau ?

### Exercice 2 — Un fichier cassé pour chaque erreur

Crée une copie de ton `servicios.toml` appelée `roto.toml` et, en changeant `RUTA_CONFIG` en `Path("roto.toml")`, écris-y, un par un, des fichiers qui provoquent chacun de ces messages : (a) la liste `[[servicios]]` manque ; (b) TOML mal écrit (oublie un guillemet) ; (c) un service sans `nombre` en deuxième position ; (d) un service avec l'url `ftp://archivos.example` ; (e) `timeout_ms = 0` dans le troisième service ; (f) deux services avec le nom `catalogo`. **Pour chacun, écris d'abord le message que tu attends** et compare ensuite avec ce qu'affiche le `revisor`. Note dans le journal de bord ceux que tu n'as pas devinés.

### Exercice 3 — Le piège de `bool`, en direct

Écris un `roto.toml` avec un seul service qui a `timeout_ms = true`. Exécute le `revisor` et note le message. Maintenant change, **temporairement**, la validation de `timeout_ms` dans `configuracion.py` pour la version naïve (`not isinstance(timeout_ms, int) or timeout_ms <= 0`, sans la partie sur `bool`) et exécute de nouveau. Que se passe-t-il ? Qui prévient ? Restaure la version correcte et explique avec tes mots pourquoi la naïve laisse passer `true`.

### Exercice 4 — Une erreur que la liste n'a pas

Le `revisor` convertit `FileNotFoundError` et `TOMLDecodeError` en `ErrorDeConfiguracion`, mais pas `UnicodeDecodeError`. Provoque-le avec un `servicios.toml` enregistré en `latin-1`, un autre encodage, sans perdre le tien. Depuis le dossier du projet : (1) enregistre une copie de sauvegarde avec `cp servicios.toml servicios-bien.toml` (`cp` copie un fichier ; si la destination existe déjà, il la remplace sans demander, alors choisis un nom que tu n'utilises pas) ; (2) fais une autre copie, `cp servicios.toml acento.toml`, et dans `acento.toml`, juste sous l'`url` du premier service, ajoute la ligne `descripcion = "catálogo de productos"` ; (3) convertis cette copie en `latin-1` et écris-la sous le nom `servicios.toml` : `iconv -f utf-8 -t latin1 acento.toml > servicios.toml` (`iconv` change l'encodage d'un texte, et `>` écrit sa sortie dans le fichier, **en effaçant d'abord ce qu'il contenait** : c'est pourquoi l'étape 1). Exécute le `revisor` et lis le rapport de bas en haut. Puis complète `leer_servicios` pour que cette erreur soit aussi convertie en `ErrorDeConfiguracion`, avec un message qui dise ce qui s'est passé, et exécute de nouveau le `revisor` avec le même `servicios.toml` en `latin-1` pour voir ton message à la place du *traceback*. Ce message ne figure pas dans le tableau du projet : c'est un prolongement d'entraînement, et le projet des leçons suivantes ne l'inclut pas. Seulement à la fin, quand tu as vu ton message, remets ta configuration avec `cp servicios-bien.toml servicios.toml`.

## Solutions

### Solution 1

Les deux nouveaux services dans `servicios.toml`, à la fin du fichier :

```toml
[[servicios]]
nombre = "facturacion"
url = "https://facturacion.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
```

Et les deux nouvelles entrées de `SIMULADO` dans `revision.py`, après celle de `reportes` :

```python
    "facturacion": (503, 95, None),
    "notificaciones": (None, None, "tiempo agotado"),
```

**Prédiction.** Six services. `catalogo` et `pagos` restent en marche (2). `inventario` reste lent (1). `reportes` et `notificaciones` n'ont pas répondu, et `facturacion` a répondu avec un 503, que la règle de classification (un code supérieur ou égal à 400) marque comme en panne : cela fait 3 en panne. La moyenne se calcule **seulement avec ceux qui ont répondu** : `catalogo` (142), `inventario` (2300), `pagos` (87) et `facturacion` (95), qui a répondu même avec une erreur ; la somme est 2624 et divisée par 4 elle donne 656. Résultat attendu : `6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms`.

**Résultat.** En exécutant `python revisor.py`, on obtient :

```text
SERVICIO    ESTADO    TIEMPO  DETALLE
catalogo    ARRIBA     142ms  200
inventario  LENTO       2.3s  200
pagos       ARRIBA      87ms  200
reportes    CAIDO          —  sin conexión
facturacion CAIDO       95ms  503
notificacionesCAIDO          —  tiempo agotado

6 servicios · 2 arriba · 1 lento · 3 caídos · promedio 656ms
```

La prédiction coïncide avec le récapitulatif. **Ce qui est bizarre** se trouve dans le tableau : `notificaciones` fait 14 lettres, et la colonne du nom a une largeur fixe de 12 (`{nombre:<12}`), donc le nom déborde sur la colonne suivante et se colle à « CAIDO ». `facturacion` tient de justesse : il a 11 lettres, et il reste une seule espace. Ce n'est pas une erreur de cette leçon : le format a été écrit pour les quatre noms canoniques. La [Leçon 11](11-el-programa-terminado.md) le résout en calculant la largeur à partir du nom le plus long. L'important de cet exercice est autre chose : tu as ajouté deux services **sans changer une ligne de logique**, ce qui était l'objectif de la leçon.

### Solution 2

Chaque fichier cassé et le message qu'il produit. Pour (b), le nom du fichier apparaît dans le message parce que `leer_servicios` utilise le chemin qu'elle reçoit ; si tu l'essaies avec `servicios.toml`, elle dira `servicios.toml`.

(a) Un fichier sans la liste :

```toml
titulo = "nada"
```

Message : `error de configuración: falta la lista [[servicios]]`

(b) Un guillemet fermant oublié :

```toml
[[servicios]]
nombre = "catalogo
```

Message : `error de configuración: roto.toml no es TOML válido: Illegal character '\n' (at line 2, column 19)`

(c) Le deuxième service n'a pas de nom :

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
url = "https://pagos.example"
```

Message : `error de configuración: servicio 2: falta 'nombre'`

(d) Une adresse qui n'est pas web, dans le deuxième service :

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "archivos"
url = "ftp://archivos.example"
```

Message : `error de configuración: servicio 2: 'url' debe ser una dirección http:// o https:// válida`

(e) Un délai d'attente à zéro, dans le troisième service :

```toml
[[servicios]]
nombre = "a"
url = "https://a.example"

[[servicios]]
nombre = "b"
url = "https://b.example"

[[servicios]]
nombre = "c"
url = "https://c.example"
timeout_ms = 0
```

Message : `error de configuración: servicio 3: 'timeout_ms' debe ser un entero mayor que 0`

(f) Deux services avec le même nom :

```toml
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "catalogo"
url = "https://otro.example"
```

Message : `error de configuración: nombres repetidos: catalogo`

Trois détails pour quand tu as comparé. L'erreur du TOML (b) est la seule dont tu n'as pas écrit le texte toi-même : il vient de `tomllib` et porte la ligne et la colonne. En (a), la liste ne manque pas à moitié : il n'y a rien, et le message dit exactement cela. Et en (f), l'erreur est détectée **après** avoir validé chaque service séparément, parce que leurs noms sont valides un à un ; le défaut est celui de la liste entière. Les messages ont été obtenus en exécutant chaque fichier avec le module de cette leçon.

### Solution 3

Avec la validation correcte, le message est celui de toujours : `error de configuración: servicio 1: 'timeout_ms' debe ser un entero mayor que 0`.

Avec la version naïve, le `revisor` **ne se plaint pas** : il affiche son tableau normal, et le récapitulatif sort sans problème. Le `Servicio` est resté avec `timeout_ms=True`, et comme `True` est le nombre 1, le délai d'attente que le programme croit avoir est d'une milliseconde. Personne ne prévient : c'est une erreur qui ne fait pas de bruit, et elle apparaîtra dans la leçon 9, quand le `revisor` utilisera ce délai d'attente : avec une milliseconde d'attente, presque n'importe quelle requête réelle expirerait, et le service sortirait en panne pour « tiempo agotado » (délai dépassé) sans motif apparent. Cela se produit parce que, en Python, `bool` est un type d'entier (`isinstance(True, int)` est `True`), et la validation naïve ne demande que cela. La version correcte ajoute `isinstance(timeout_ms, bool)` pour rejeter explicitement les booléens.

### Solution 4

En exécutant avec le fichier en `latin-1`, la dernière ligne du rapport est :

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 85: invalid continuation byte
```

L'octet `0xe1` est le « á » de « catálogo » en `latin-1` ; la position 85 est l'endroit où il tombe dans le fichier, en comptant les octets depuis 0 : c'est celle qui sort si tu as mis la ligne là où l'exercice le dit, et ce sera une autre si tu l'as mise ailleurs. Les lignes du dessus passent par `read_text` et la bibliothèque standard : l'erreur naît à l'intérieur de la lecture, pas dans ton code, et toi tu la vois remonter par tes fonctions. Pour la convertir, on ajoute un second `except` dans la première étape de `leer_servicios` :

```python
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"no existe el archivo {ruta}") from error
    except UnicodeDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no está guardado en UTF-8") from error
```

Avec cela, le `revisor` affiche `error de configuración: servicios.toml no está guardado en UTF-8`. Remarque que `UnicodeDecodeError` est un type de `ValueError`, mais qu'il n'est pas nécessaire d'attraper `ValueError` : avec le type précis, un `ValueError` d'une autre cause ne se déguise pas.

## Comment savoir que j'ai réussi

- [ ] `python fig06_01.py` se termine avec le rapport de `ValueError`, et tu peux dire quelle fonction en a appelé quelle, de bas en haut, sans regarder la leçon.
- [ ] `python fig06_03.py` dit que « 142 » n'est pas un nombre, et tu peux expliquer pourquoi c'est un mensonge et quelle ligne du programme contient la vraie erreur.
- [ ] Dans `fig06_05.py`, tu vois la phrase « The above exception was the direct cause of the following exception », et tu sais quelle instruction du code l'a produite.
- [ ] Depuis `fig06_18/`, `python revisor.py` affiche le tableau des quatre services avec le récapitulatif `4 servicios · 2 arriba · 1 lento · 1 caído · promedio 843ms`.
- [ ] Depuis le dossier du dessus, `python fig06_18/revisor.py` affiche `error de configuración: no existe el archivo servicios.toml`, et tu sais expliquer pourquoi.
- [ ] Les six fichiers cassés de l'exercice 2 produisent les six messages du tableau, et tu les as prédits avant d'exécuter.
- [ ] `python ver_json.py` affiche un JSON avec `null` dans le `tiempo_ms` de `reportes` et avec `"promedio_ms": 843`.
- [ ] Tu peux expliquer pourquoi `isinstance(True, int)` est `True` et quelle validation du `revisor` en tient compte.
- [ ] Tu as noté dans ton journal de bord quelle erreur de cette leçon t'a donné du mal à lire.

## Résumé

Réponds sans regarder la leçon :

1. De quel côté lit-on un rapport d'erreur, et que dit sa dernière ligne ?
2. Quelle différence y a-t-il entre le `else` et le `finally` d'un `try` ? Lequel s'exécute même s'il y a un `return` ?
3. Pourquoi n'écrit-on pas `except:` sans type, ni `except Exception:` au cas où ? Que se passe-t-il avec l'erreur que tu ne sais pas gérer ?
4. Que fait `raise ... from error`, et que se passe-t-il dans le rapport si tu l'omets ?
5. Que garantit un `with` ? Pourquoi écrit-on toujours `encoding="utf-8"` ?
6. Que renvoie `tomllib.loads` ? Quelle différence y a-t-il entre `datos["servicios"]` et `datos.get("servicios")` si la clé n'existe pas ?
7. Quelles trois choses distinguent `json.dumps(x)` de `json.dumps(x, ensure_ascii=False, indent=2)` ? Pourquoi `json.dumps(Estado.CAIDO)` échoue-t-il ?
8. Pourquoi `isinstance(True, int)` est-il `True` ? Comment s'écrit la validation d'un entier positif qui rejette `true` ?
9. Pourquoi valide-t-on le schéma d'une adresse avec une liste de ce qui est permis et non avec une liste de ce qui est interdit ?
10. Quel risque présente `eval` avec un texte qui vient de l'extérieur, et quel format utilise-t-on à la place ?

## Pour aller plus loin

- [Python, « Erreurs et exceptions » (tutoriel officiel)](https://docs.python.org/3/tutorial/errors.html) : `try`, `except`, `else`, `finally`, exceptions personnalisées et chaînées, avec plus d'exemples que cette leçon. En anglais, comme presque toute la documentation officielle. Consulté le 7 octobre 2026.
- [Python, `tomllib`](https://docs.python.org/3/library/tomllib.html) et [la spécification de TOML](https://toml.io/en/v1.0.0) : ce que le module lit et les règles du format, y compris les tables et les listes de tables. Consulté le 7 octobre 2026.
- [Python, `json`](https://docs.python.org/3/library/json.html) et [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) : la bibliothèque et la norme du format. Consulté le 7 octobre 2026.
- [OWASP, « Input Validation Cheat Sheet »](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) : pourquoi on valide à la frontière et pourquoi une liste de ce qui est permis fonctionne mieux qu'une liste de ce qui est interdit. Consulté le 7 octobre 2026.
