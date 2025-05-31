# Projet Domain Driven Design ESGI

## Lancer le projet

### Avec `poetry` (recommandé)
```shell
poetry shell
poetry install
python manage.py runserver
```

### Avec `pip`
```shell
pip install -r requirements.txt
python manage.py runserver
```

### Connexion au site web
Les données sont préchargés dans une base de données sqlite.

Il existe trois niveaux de compte utilisateur avec lesquels se connecter, le mot de passe est toujours `password`.

**Admin** 

Email: admin@gmail.com

**Manager**

Il existe 50 comptes de manager.

Exemple d'utilisation : manager1@gmail.com, manager32@gmail.com

**Artist**

Un manager peut avoir jusqu'a 10 artistes. Pour se connecter au compte artiste, on précise le numéro du manager et de l'artiste voulu.

Exemple d'utilisation :
- artist.1.1@gmail.com = Manager 1, artiste 1
- artist.34.7@gmail.com = Manager 34, artiste 7

### Charger les données
S'il s'avérais que les données de la base de données sqlite soient corrompues, vous pouvez recharger les données en executant deux commandes.
- Charger les données des charts et artistes : `python manage.py loaddata` 
- Générer les comptes utilisateur admin, manager et artiste : `python manage.py createusers` 

Ces scripts sont stockés dans `chartflow/management/commands`

## CRUD permissions


| Role        | Resource             | Methods / Access             |
| ----------- | -------------------- | ---------------------------- |
| **Admin**   | All                  | Full access to all endpoints |
| **Manager** | **User**             | GET (self), PATCH (self)     |
|             | **Artists**          | GET (his artists)            |
|             | **Charts**           | GET                          |
|             | **Chart entries**    | GET                          |
|             | **Country**          | GET                          |
|             | **Country clusters** | GET                          |
| **Artist**  | **User**             | GET (self), PATCH (self)     |
|             | **Artists**          | GET (self), PATCH (self)     |
|             | **Charts**           | GET                          |
|             | **Chart entries**    | GET                          |
|             | **Country**          | GET                          |