# simp2puml

Outil en ligne de commande pour convertir des diagrammes SIMP vers PlantUML, et expérimentalement de PlantUML vers SIMP. Python ≥ 3.11 ; aucune dépendance tierce à l’exécution. Le modèle commun conserve les identités, classifieurs, membres, relations, notes et avertissements, sans reproduire fidèlement toutes les données du format source.

## Installer et convertir

La méthode recommandée depuis un clone est `pipx`, qui isole l’outil de Python système :

```sh
# Installer pipx avec le gestionnaire de paquets de votre système, si nécessaire :
# Debian/Ubuntu : sudo apt install pipx
# Fedora :        sudo dnf install pipx
pipx install .
pipx ensurepath
```

Ouvrez une nouvelle session de terminal après `pipx ensurepath` si la commande n’est pas trouvée. Pour installer une wheel construite localement :

```sh
pipx install dist/simp2puml-0.1.0-py3-none-any.whl
```

La wheel inclut aussi la page de manuel. Sur Linux, avec `man` installé, pipx l’expose et elle se consulte après installation avec `man simp2puml`. Si une ancienne wheel était déjà installée, la remplacer par la nouvelle avec `pipx install --force dist/simp2puml-0.1.0-py3-none-any.whl`.

Si `man` ne trouve pas la page, vérifier le dossier `PIPX_MAN_DIR` indiqué par `pipx environment` et sa présence dans les chemins de recherche de man. Avec le chemin pipx par défaut, `man -M ~/.local/share/man simp2puml` permet aussi de la consulter. L’aide `simp2puml --help` reste disponible sans programme `man`.

La version 0.1.0 n’est pas annoncée comme publiée sur PyPI : `pipx install simp2puml` n’est pas la procédure d’installation. Alternative isolée sans pipx :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/simp2puml --version
```

Ne pas installer avec `sudo pip` ni contourner la protection Python système avec `--break-system-packages`.

```sh
simp2puml --version
simp2puml diagramme.simp
simp2puml diagramme.simp -o resultat.puml
simp2puml projet.simp --diagram "Nom du diagramme" -o resultat.puml
```

L’extension source choisit le sens de conversion ; sans `-o`, le fichier de destination prend l’extension opposée dans le même dossier. `--diagram` sélectionne un diagramme SIMP par nom ou identifiant ; les diagrammes ne sont pas fusionnés. Une sortie existante ou identique à la source est refusée. La source est limitée à 20 MiB, lue en UTF-8 (BOM accepté) ; la sortie est publiée atomiquement.

## Construire et paqueter

Construire une wheel localement dans un environnement isolé :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m build
```

Pour préparer un paquet natif local, le script prend en charge RPM et Debian :

```sh
.venv/bin/python tools/build-native.py rpm
# Sans les dépendances natives, produire seulement le paquet source RPM :
.venv/bin/python tools/build-native.py rpm --source-only
# Debian : remplacer le texte entre guillemets par une adresse publique réelle.
.venv/bin/python tools/build-native.py deb --maintainer-email "ADRESSE_PUBLIQUE_A_RENSEIGNER"
```

`ADRESSE_PUBLIQUE_A_RENSEIGNER` est un espace réservé, pas une adresse à publier. Sans adresse réelle, la préparation et la construction Debian sont volontairement refusées. Le nom du mainteneur Debian par défaut est Nela. Les recettes sont dans `packaging/rpm/simp2puml.spec.in` et `packaging/debian/`. `--source-only` construit un `.src.rpm`, pas un paquet binaire installable. `--prepare-only` prépare les sources sans lancer la construction ; `--output` permet de choisir le dossier de sortie (par défaut `dist`). Les outils de construction requis dépendent de la distribution. Pour RPM, prévoir notamment `rpmdevtools`, `rpmbuild`, `python3-devel`, `pyproject-rpm-macros` et setuptools ≥ 77. Pour Debian, prévoir `debhelper`, `dh-python`, `pybuild-plugin-pyproject`, `python3-all`, `python3-build`, `python3-wheel` et `python3-setuptools` ≥ 77. Les noms et disponibilités de paquets peuvent varier selon la version de la distribution ; aucune compatibilité de version non vérifiée n’est garantie.

Installer un paquet construit localement : `sudo dnf install ./dist/<paquet>.rpm` ou `sudo apt install ./dist/<paquet>.deb`. Cela n’installe pas le logiciel depuis un dépôt officiel et ne signifie ni publication PyPI, ni présence dans un dépôt APT/DNF, ni signature de dépôt. Sur les autres systèmes, utiliser pipx et la wheel ; aucune recette native supplémentaire n’est fournie.

## Couverture et limites

La priorité de l’outil est SIMP vers PlantUML. Le lecteur SIMP vise le profil `sim-project` observé (XML `version="12.75"`, `multi-file="no"`) ; 12.75 est un numéro de format et ne permet pas de connaître la version de l’application. La compatibilité avec Software Ideas Modeler n’a pas été vérifiée. Une sélection explicite du diagramme évite de fusionner les diagrammes ; les objets globaux hors diagramme sélectionné sont exclus.

PlantUML prend en charge notamment classes, interfaces, énumérations ordonnées, symboles d’interface, membres, notes et les relations d’héritage, d’association, d’agrégation, de composition et connecteurs d’interface. Les pertes et ambiguïtés effectivement détectées sont signalées par avertissements ou erreurs. Packages et réalisations ne sont pas pris en charge ; les flèches d’association perdent leur direction. Styles et positions ne sont pas conservés. La conversion inverse PlantUML vers SIMP est expérimentale : dispositions générées en grille et structures/types textuels ou certaines visibilités restent à valider dans l’application. Ne pas interpréter le nombre d’avertissements comme un nombre équivalent d’éléments perdus.

Les directives PlantUML ne sont pas exécutées ; aucun fichier externe n’est inclus ou chargé. Les DTD et entités XML sont rejetées. Les éventuels fichiers locaux `Monopoly.simp`, `Classdiagram1.svg` et `examples/validation/` sont personnels : ils sont exclus du dépôt public et des distributions. Ils ne sont pas fournis avec un clone ; les tests qui nécessitent la fixture réelle sont ignorés uniquement lorsqu’elle est absente. L’exemple [`examples/minimal.puml`](examples/minimal.puml) est synthétique et peut être partagé.

## Développement

Installer avec `python3 -m venv .venv` puis `.venv/bin/python -m pip install -r requirements-dev.txt`. Tests ciblés : `.venv/bin/python -m pytest -q tests/test_simp.py`, `test_puml.py` ou `test_cli.py`. Exécution : `.venv/bin/python -m simp2puml fichier.simp`. L’ancien `main.py` est conservé comme wrapper de compatibilité.
