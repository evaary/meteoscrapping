Un programme de webscrapping pour récupérer des données météorologiques depuis 2 sites : ogimet et wunderground.

exemples de tableaux récupérés:
    1 - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
    2 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3


pour lancer le programme:

    télécharger l'éxecutable
        https://drive.google.com/file/d/1pXSngAB002o5Pzv_ipuPS-Xx3ahdfTcK/view?usp=sharing
    
    créer un répertoire "config" à côté l'éxecutable
    
    créer des fichiers json dans le répertoire "config", autant que voulu
        - le nom de chaque fichier doit commencer par config et finir par .json
        - les fichiers dont le nom ne respecte pas cette règle seront ignorés
        - 1 fichier par période continue (les mois 1 A 12 de 2015 à 2020 : 1 fichier. Les mois 3 ET 7 pour 2020 : 2 fichiers)
        - des exemples de fichiers config sont donnés ci-après ou dans le répertoire exemples

    double cliquer sur l'éxecutable
    ou
    ouvrir une fenêtre powershell (alt + f dans le répertoire ou se trouve l'exécutable puis taper .\meteoscrapping.exe) pour plus de détails.
        

    les résultats seront stockés dans un répertoire "results" créé automatiquement à côté du répertoire "config"
        - les résultats sont des fichiers csv, 1 par fichier config si des données ont été récupérées
    
    les erreurs seront stockées dans un répertoire "errors" créé automatiquement à côté du répertoire "config"
        - les erreurs sont des fichiers json, 1 par fichier config s'il y a eu des erreurs
        - chaque fichier json contient les url ayant posé problème au programme.


structure du fichier config wounderground
    - Les infos country_code, city, et region sont à récupérer directement dans l'url du site pour la station voulue (voir ligne 6)
    - Le champ waiting sert à patienter suffisamment longtemps pour que les données soient disponibles sur la page.
    Si un problème de chargement de la page html survient, essayez d'augmenter le waiting.
    - Les unités sont converties vers le S.I. ( températures (°F -> °C), vitesses (mph -> km/h), précipitations (in -> mm), pressions (inHg -> hPa) )
{
    "scrapper": "wunderground",
    "country_code": "es",
    "city": "barcelona",
    "region": "LEBL",
    "waiting": 5,
    "year": {
        "from": 2020,
        "to": 2020
    },
    "month": {
        "from": 2,
        "to": 12
    }
}



structure du fichier config ogimet
    - L'ind est à récupérer directement dans l'url du site pour la station voule (voir ligne 5)
    - Le champ city sert juste à nommer le fichier csv
    - Les colonnes daily weather summary sur ogimet sont ignorées
{
    "scrapper": "ogimet",
    "ind": "08180",
    "city": "barcelone",
    "waiting": 5,
    "year": {
        "from": 2017,
        "to": 2017
    },
    "month": {
        "from": 1,
        "to": 12
    }
}
