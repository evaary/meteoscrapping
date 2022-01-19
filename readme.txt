Un programme de webscrapping pour récupérer des données météorologiques depuis 2 sites : ogimet et wunderground. Téléchargez l'éxecutable depuis google drive :
https://drive.google.com/file/d/1rzYzcwpMB3Am9tvkz5qTfLILYBuQ-NvY/view?usp=sharing

exemples de tableaux récupérés:
    1 - http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=8&day=0&hora=0&min=0&ndays=31
    2 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3


pour lancer le programme:

    télécharger l'éxecutable
        https://drive.google.com/file/d/1rzYzcwpMB3Am9tvkz5qTfLILYBuQ-NvY/view?usp=sharing
    
    créer un répertoire "config" à côté l'éxecutable
    
    créer des fichiers json dans le répertoire config, autant que voulu
        - le nom de chaque fichier doit commencer par config et finir par .json
        - les fichiers dont le nom ne respecte pas cette règle seront ignorés
        - 1 fichier par période continue (les mois 1 A 12 de 2015 à 2020 : 1 fichier. Les mois 3 ET 7 pour 2020 : 2 fichiers)
        - des exemples de fichiers config sont donnés ci-après ou dans le répertoire exemples

    double cliquer sur l'éxecutable ou ouvrir une fenêtre powershell (alt + f dans le répertoire ou se trouve l'exécutable puis taper .\meteoscrapping.exe) pour plus de détails en cas d'erreurs
        - des tableaux incomplets, auxquels il manque des données voir des colonnes, ne posent pas de problèmes
        - les colonnes daily weather summary sur ogimet sont ignorées

    les résultats seront stockés dans un répertoire results créé automatiquement à côté du répertoire config
        - les résultats sont des fichiers csv, 1 par fichier config si des données ont été récupérées
    
    les erreurs seront stockées dans un répertoire errors créé automatiquement à côté du répertoire config
        - les erreurs sont des fichiers json, 1 par fichier config s'il y a eu des erreurs
        - chaque fichier json contient les url à partir desquelles aucune donnée n'a pu être récupérée par le programme.


Le scrapper wunderground convertit les températures (°F --> °C) les vents (mph --> km/h), les précipitations (in --> mm) et les pressions (inHg --> hPa).
Les données ogimet sont déjà dans de bonnes unités.



structure du fichier config wounderground
les infos country_code, city, et region sont à récupérer directement dans l'url du site pour la station voulue (voir ligne 6)
le champ waiting sert à patienter suffisamment longtemps pour que le javascript des pages s'éxecute. Si un problème de chargement
de la page html survient, essayez d'augmenter le waiting.
{
    "scrapper": "wunderground",
    "country_code": "es",
    "city": "barcelona",
    "region": "LEBL",
    "waiting": 5,
    "year": {
        "from_": 2020,
        "to_": 2020
    },
    "month": {
        "from_": 2,
        "to_": 12
    }
}



structure du fichier config ogimet
l'ind est à récupérer directement dans l'url du site pour la station voule (voir ligne 5)
Le champ city sert juste à nommer le fichier csv
{
    "scrapper": "ogimet",
    "ind": "08180",
    "city": "barcelone",
    "waiting": 5,
    "year": {
        "from_": 2017,
        "to_": 2017
    },
    "month": {
        "from_": 1,
        "to_": 12
    }
}

/!\ dans la version actuelle du code, les _ de from et to sont à retirer. Pour utliser l'executable, il faut les garder.
