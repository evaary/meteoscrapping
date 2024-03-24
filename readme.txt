Un programme de webscrapping pour récupérer des données météorologiques depuis ogimet, wunderground et meteociel.
/!\ La 1ère fois que le programme se lance, il téléchargera chromium, c'est normal.

Exemples de tableaux récupérés:
    1 - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
    2 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    3 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
    4 - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020

Utilisation:

    télécharger l'exécutable
        - fichier zip : https://drive.google.com/file/d/1IdlDQgyobw7MaE372xHzIk58INy3K5AS/view?usp=drive_link
        - dézipper

    créer un fichier "config.json" à côté l'éxecutable (nom config.json impératif)
        -> un modèle de fichier config est donné ci-après ou dans le fichier exemple_config.json

    double cliquer sur l'éxecutable. Le programme se lance et télécharge les données.

    les résultats seront stockés dans un répertoire "results" à côté du fichier config
    les erreurs seront stockées dans un répertoire "errors" à côté du fichier config

Structure du fichier config.json:
{
    "parametres_generaux":
    {
        "delaiJS": 1
    },

    "ogimet":
    [
        { "ind":"16138", "ville":"Ferrara", "annees":[2021], "mois":[2] },
        { "ind":"16288", "ville":"Caserta", "annees":[2020, 2025], "mois":[1,12] }
    ],

    "wunderground":
    [
        { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2021], "mois":[1,6] }
    ],

    "meteociel":
    [
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020, 2021], "mois":[2] },
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020], "mois":[1,2], "jours":[27,31] }
    ]
}

Où trouver les paramètres ?
    Pour les jobs ogimet:
        - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
          http:      [...]                             &ind=<ind>&ano=          [...]
        - /!\/!\ les mois dans l'URL sont numérotés différement. Dans la config, utiliser les numéros usuels.
        - Les colonnes daily weather summary sont exclues des résultats.

    Pour les jobs wunderground:
        - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
          https:       [...]                  /monthly/<code_pays>/<ville>/<region>/date/2020-3
        - /!\   Les unités sont converties dans les résultats
                températures (°F -> °C),    vitesses (mph -> km/h), précipitations (in -> mm),  pressions (inHg -> hPa).

    Pour les jobs meteociel:
        - la présence du champs "jours" détermine si les données téléchargées sont en heure par heure ou en jour par jour.
        - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
          https://     [...]                     obs_villes.php?code<code_num>=<code>&mois=   [...]

        jour par jour
        - La colonne des images est exclues des résultats.

        heure par heure
        - /!\/!\ Les mois dans l'URL sont numérotés différement. Dans la config, utiliser les numéros usuels.
        - La colonne "temps" et les directions du vent sont exclues des résultats.
        - Les colonnes "vent" et "rafales" sont récupérées dans des colonnes distinctes.
        - L'heure est convertie en date et heure.

Explications

    Le champ "parametres_generaux" est optionnel.
    "delaiJS" sert à patienter suffisamment longtemps pour que les données soient disponibles sur la page à scrapper.
    Si une erreur "aucun tableau trouvé" apparait, augmenter le délai (valeurs autorisées 1 à 5) peut résoudre le problème
    si le tableau existe bien.

    "ogimet", "wunderground" et "meteociel" sont optionnels tous les 3, mais il en faut au moins un
    avec une liste de configurations non vide.
    Tous les paramètres dans les configs entre { } sont obligatoires. "jours" n'est disponible que pour meteociel.
    1 CSV (résultats) et éventuellement 1 JSON (erreurs) seront générés par jeu de paramètres.

    Pour l'exemple ogimet n°2, on récupère les données des mois de janvier à décembre 2020 à 2025, en 1 CSV.
    Pour l'exemple meteociel n°2, on récupère les jours 27 à 31 du mois de janvier 2020 et 27 à 28 pour février 2020.
    => les jours absurdes (31 février par exemple), sont autorisés et triés automatiquement.
