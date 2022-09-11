Un programme de webscrapping pour récupérer des données météorologiques depuis 3 sites : ogimet, wunderground et meteociel.
/!\ La 1ère fois que le programme se lance, il téléchargera chromium, c'est normal.
/!\ python 3.7 (ne fonctionne pas avec 3.10)
/!\ il n'existe qu'1 scrapper quotidien, meteociel_daily

exemples de tableaux récupérés:
    1 - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
    2 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    3 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
    4 - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020

Utilisation:

    télécharger l'exécutable
        - fichier zip : https://drive.google.com/file/d/1nizRr_Yzv-Rc5IabFTKEWip8etFVAnNN/view?usp=sharing
        - dézipper

    créer un fichier "config.json" à côté l'éxecutable (nom config.json impératif)
        - un modèle de fichier config est donné ci-après ou dans le fichier exemple_config.json

    double cliquer sur l'éxecutable.

    les résultats seront stockés dans un répertoire "results" à côté du fichier config
        - les résultats sont des fichiers csv, 1 par job, si des données ont été récupérées

    les erreurs seront stockées dans un répertoire "errors" à côté du fichier config
        - les erreurs sont des fichiers json, 1 par job s'il y a eu des erreurs
        - chaque fichier json contient les url à partir desquelles aucune donnée n'a pu être récupérée par le programme.

structure du fichier config.json
{
    "waiting": 3,

    "ogimet":[
        { "ind":"16138", "city":"Ferrara", "year":[2021], "month":[2] },
        { "ind":"16288", "city":"Caserta", "year":[2020, 2025], "month":[1,2] }
    ],

    "wunderground":[
        { "country_code":"it", "region": "LIBD", "city":"matera", "year":[2021], "month":[1,6] }
    ],

    "meteociel":[
        { "code_num":"2", "code": "7249", "city":"orleans", "year":[2020], "month":[1,2] }
    ],

    "meteociel_daily":[
        { "code_num":"2", "code": "7249", "city":"orleans", "year":[2020], "month":[2], "day":[27,31] }
    ]
}

Le champ waiting (optionnel) sert à patienter suffisamment longtemps pour que les données soient disponibles sur la page.
Si une erreur "aucun tableau trouvé" apparait, augmenter le waiting peut résoudre le problème si le tableau existe bien.

Chaque élément entre { } correspond aux paramètres pour 1 job.

Les champs day, month et year doivent être des listes ordonnées d'1 ou 2 entiers positifs.

Pour l'exemple ogimet n°2, on récupère les données des mois de janvier à février 2020 à 2025.
Pour l'exemple meteociel_daily : on récupère les jours 27 à 31 du mois de février 2020.

/!\ Les jours qui n'existent pas (le 31 février typiquement) sont ignorés sans poser de problèmes.
    Pour récupérer tous les jours, on peut écrire day: [1,31], quelque soit le mois.

Les autres champs sont à récupérer directement depuis le site ou l'url voulue (voir ci-après),
sauf le "city" qui est obligatoire mais arbitraire pour les scrappers autres que wunderground.


Pour les jobs ogimet:
    - Le champ city sert juste à nommer le fichier csv.
    - Les colonnes daily weather summary sur ogimet sont ignorées.
    - les mois dans l'url sont numérotés différement. Dans la config, utiliser les numéros usuels.
    - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=<ind>&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31

Pour les jobs wunderground:
    - Les unités sont converties : températures (°F -> °C), vitesses (mph -> km/h), précipitations (in -> mm), pressions (inHg -> hPa).
    - https://www.wunderground.com/history/monthly/<country_code>/<city>/<region>/date/2020-3

Pour les job meteociel:
    - La colonne des images est ignorée.
    - Le champ city sert juste à nommer le fichier csv.
    - https://www.meteociel.com/climatologie/obs_villes.php?code<code_num>=<code>&mois=1&annee=2021

Pour les job meteociel_daily:
    - La colonne temps et les directions du vent sont ignorées.
    - Vent et rafales sont récupérées dans des colonnes distinctes.
    - L'heure est convertie en date et heure.
    - Les mois dans l'url sont numérotés différement. Dans la config, utiliser les numéros usuels.
    - https://www.meteociel.com/temps-reel/obs_villes.php?code<code_num>=<code>&jour2=1&mois2=0&annee2=2020
