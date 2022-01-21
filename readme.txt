Un programme de webscrapping pour récupérer des données météorologiques depuis 3 sites : ogimet, wunderground et meteociel.

exemples de tableaux récupérés:
    1 - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
    2 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    3 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021

/!\ Une ConnectionResetError peut être levée aléatoirement, cela n'influe pas sur le bon fonctionnement du programme. Je ne sais pas d'où elle sort, des corrections
seront apportées.

Pour lancer le programme:

    télécharger l'éxecutable (version 2)
        https://drive.google.com/file/d/1Ua1SSmowC9_f7Ny6HCCb9_yZsdTaGMrK/view?usp=sharing
    
    créer un fichier "config.json" à côté l'éxecutable
        - un modèle de fichier config est donné ci-après ou dans le fichier exemple_config.json (à renommer en config.json)

    double cliquer sur l'éxecutable
    ou
    ouvrir un powershell (alt + f dans le répertoire où se trouve l'exécutable puis taper .\meteoscrapping.exe) pour plus de détails.

    les résultats seront stockés dans un répertoire "results" créé automatiquement à côté du fichier config
        - les résultats sont des fichiers csv, 1 par job, si des données ont été récupérées
    
    les erreurs seront stockées dans un répertoire "errors" créé automatiquement à côté du fichier config
        - les erreurs sont des fichiers json, 1 par job s'il y a eu des erreurs
        - chaque fichier json contient les url à partir desquelles aucune donnée n'a pu être récupérée par le programme.

structure du fichier config.json
{
    "waiting": 10,

    "ogimet":[
        { "ind":"16138", "city":"Ferrara", "year":[2021], "month":[2] },
        { "ind":"16288", "city":"Caserta", "year":[2020, 2021], "month":[1,2] }
    ],

    "wunderground":[
        { "country_code":"it", "region": "LIBD", "city":"matera", "year":[2021], "month":[1,6] }
    ],

    "meteociel":[
        { "code_num":"2", "code": "7249", "city":"orleans", "year":[2020], "month":[1,2] }
    ]
}

Le champ waiting est optionnel, il sert à patienter suffisamment longtemps pour que les données soient disponibles sur la page.
Si un problème de chargement de la page html survient, essayez d'augmenter le waiting. Par défaut il vaut 10.

Chaque élément dans les listes ogimet, wounderground ... correspond aux paramètres pour 1 job.

Les champs month et year doivent être des listes ordonnées d'1 ou 2 entiers positifs.

Les autres champs sont à récupérer directement depuis le site ou l'url voulue (voir ligne 4 à 6 de ce readme),
sauf le "city" qui est à choisir soi-même pour les scrappers autres que wunderground.


Pour les jobs ogimet:
    - Le champ city sert juste à nommer le fichier csv.
    - Les colonnes daily weather summary sur ogimet sont ignorées.

Pour les jobs wunderground:
    - Les unités sont converties : températures (°F -> °C), vitesses (mph -> km/h), précipitations (in -> mm), pressions (inHg -> hPa).
    - https://www.wunderground.com/history/monthly/<country_code>/<city>/<region>/date/2020-3

Pour les job meteociel:
    - La colonne des images est ignorée.
    - Le champ city sert juste à nommer le fichier csv.
    - https://www.meteociel.com/climatologie/obs_villes.php?code<code_num>=<code>&mois=1&annee=2021