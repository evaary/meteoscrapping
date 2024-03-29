Un programme de webscrapping pour récupérer des données météorologiques depuis ogimet, wunderground et meteociel.

Exemples de tableaux récupérés:
    1 - https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=7&day=31&hora=23&ndays=31
    2-  https://www.ogimet.com/cgi-bin/gsynres?ind=07149&ndays=31&ano=2020&mes=2&day=31&hora=23&lang=en&decoded=yes
    3 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    4 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
    5 - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020

Utilisation:

    télécharger l'exécutable
        - fichier zip : https://drive.google.com/file/d/1IdlDQgyobw7MaE372xHzIk58INy3K5AS/view?usp=drive_link
        - dézipper

    créer un fichier "config.json" à côté l'éxecutable (nom "config.json" impératif)
        -> un modèle de fichier config est donné ci-après ou dans le fichier exemple_config.json

    double cliquer sur l'éxecutable. Le programme se lance et télécharge les données.

    les résultats seront stockés dans un répertoire "resultats" à côté du fichier config
    les erreurs seront stockées dans un répertoire "erreurs" à côté du fichier config

Structure du fichier config.json:
{
    "parametres_generaux":
    {
        "delaiJS": 1
    },

    "ogimet":
    [
        { "ind":"16288", "ville":"Caserta", "annees":[2020, 2025], "mois":[1, 12] },
        { "ind":"07149", "ville":"paris_orly", "annees":[2023], "mois":[1,5], "jours":[13, 18] }
    ],

    "wunderground":
    [
        { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2021], "mois":[1,6] }
    ],

    "meteociel":
    [
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020, 2021], "mois":[2] },
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020], "mois":[1, 2], "jours":[27,31] }
    ]
}

Où trouver les paramètres ?

    dates : fixées par l'utilisateur

    Pour les jobs ogimet jour par jour et heure par heure:
        - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
          http:      [...]                              ind=<ind>          [...]

    Pour les jobs wunderground:
        - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
          https:       [...]                  /monthly/<code_pays>/<ville>/<region>/date/[...]
        - /!\   Les unités sont converties dans les résultats
                températures (°F -> °C),    vitesses (mph -> km/h), précipitations (in -> mm),  pressions (inHg -> hPa).

    Pour les jobs meteociel jour par jour:
        - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
          https://     [...]                                    code<code_num>=<code>&mois=   [...]

    Pour les jobs meteociel heure par heure
        - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020
          https://     [...]                                  code<code_num>=<code>&jour2=   [...]
        - /!\/!\ Les mois dans l'URL sont numérotés différement. Dans la config, utiliser les numéros usuels.
        - La colonne "vent (rafale)" est séparée en 2 colonnes distinctes.
        - L'heure est convertie en date et heure.

Informations importantes

    - Les "parametres_generaux" sont optionnels. "meteociel", "wunderground" et "ogimet" sont optionnels tous les 3,
    mais la présence d'au moins l'un d'eux avec une liste de configurations non vide est requise.

    - "delaiJS" sert à patienter le temps que les données soient disponibles sur la page à scrapper.
    Si le téléchargement des pages html échoue, augmenter le délai (valeurs autorisées 1 à 5)
    peut résoudre le problème si le tableau existe bien sur la page.
    Sinon, re-télécharger les données pour les dates concernées via de nouvelles configs.

    - 1 CSV (résultats) et éventuellement 1 JSON (erreurs) seront générés par configuration.
    - le paramètre "ville" est imposé pour wunderground mais arbitraire pour les autres.
    - le paramètre "jours" n'est pas disponible pour wunderground.
    - les jours absurdes (31 février par exemple), sont autorisés dans les configurations et triés automatiquement.
    - les colonnes contenant des icônes sont exclues des résultats.
    - Des ConnectionResetError peuvent apparaitre pendant le téléchargement, elles ne sont pas graves.
    - La 1ère fois que le programme se lance, il téléchargera chromium, c'est normal.

Performances

    { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2019, 2020], "mois":[1, 12], "jours":[1, 31] }
    => a généré un CSV de 17 521 lignes en 3040s, sans fichier d'erreur

    { "ind":"07149", "ville":"paris_orly", "annees":[2015, 2020], "mois":[1, 12], "jours":[1, 31] }
    => a généré un CSV de 52 561 lignes en 3 476s, sans fichier d'erreur

    { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2013, 2023], "mois":[1,12] }
    => a généré un CSV de 4 018 lignes en 916s, sans fichier d'erreur

    { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2013, 2023], "mois":[1, 12] }
    => a généré un CSV de 4 018 lignes en 533s, sans fichier d'erreur
