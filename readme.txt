Un programme de webscrapping pour récupérer des données météorologiques depuis ogimet, wunderground et meteociel.

Exemples de tableaux récupérés:
    1 - https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=7&day=31&hora=23&ndays=31
    2-  https://www.ogimet.com/cgi-bin/gsynres?ind=07149&ndays=31&ano=2020&mes=2&day=31&hora=23&lang=en&decoded=yes
    3 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    4 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
    5 - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020

Utilisation:

    télécharger l'exécutable
        - fichier zip : https://drive.google.com/file/d/10vq44kO-Hy4qsaFfwfAZczj2len7kX9C/view?usp=drive_link
        - dézipper

    créer un fichier "config.json" à côté l'éxecutable (nom "config.json" impératif)
        -> un modèle de fichier config est donné ci-après ou dans le fichier exemple_config.json

    double cliquer sur l'éxecutable. Le programme se lance et télécharge les données.

    les résultats seront stockés dans un répertoire "resultats" à côté du fichier config
    les erreurs seront stockées dans un répertoire "erreurs" à côté du fichier config

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

    - 1 CSV (résultats) et éventuellement 1 JSON (erreurs) seront générés par configuration.
    - le paramètre "ville" est imposé pour wunderground mais arbitraire pour les autres.
    - le paramètre "jours" n'est pas disponible pour wunderground.
    - les jours absurdes (31 février par exemple), sont autorisés dans les configurations et triés automatiquement.
    - les colonnes contenant des icônes sont exclues des résultats.
    - Des ConnectionResetError peuvent apparaitre pendant le téléchargement, elles ne sont pas graves.
    - La 1ère fois que le programme se lance, il téléchargera chromium, c'est normal.

    meteociel heure par heure
    La durée du téléchargement dépend du nombre de jours (1 page de 24h requêtée par jour demandé)

    ogimet heure par heure
    La durée du téléchargement dépend surtout du nombre de mois (1 page requêtée par mois demandé).
    Chaque page scrappée peut contenir jusqu'à 1 mois de données heure par heure.

    wunderground, meteociel et ogimet jour par jour
    La durée du téléchargement dépend du nombre de mois (1 page de 28/30/31 jours requêtée par mois demandé)

Performances

    meteociel heure par heure
    { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2019, 2020], "mois":[1, 12], "jours":[1, 31] }
    => a généré un CSV de 17 521 lignes en 3 040s, sans fichier d'erreur

    ogimet heure par heure
    { "ind":"07149", "ville":"paris_orly", "annees":[2015, 2020], "mois":[1, 12], "jours":[1, 31] }
    => a généré un CSV de 52 561 lignes en 3 476s, sans fichier d'erreur

    ogimet jour par jour
    { "ind":"07149", "ville":"paris_orly", "annees":[2015, 2020], "mois":[1, 12]}
    => a généré un CSV de 2191 lignes en 3245s, sans fichier d'erreur

    wunderground jour par jour
    { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2013, 2023], "mois":[1,12] }
    => a généré un CSV de 4 018 lignes en 916s, sans fichier d'erreur

    meteociel jour par jour
    { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2013, 2023], "mois":[1, 12] }
    => a généré un CSV de 4 018 lignes en 533s, sans fichier d'erreur


Structure du fichier config.json:
{
    "ogimet":
    [
        { "ind":"16288", "ville":"Caserta", "annees":[2020, 2025], "mois":[1, 12] },
        { "ind":"07149", "ville":"paris_orly", "annees":[2023], "mois":[1,5], "jours":[13, 18] }
    ],

    "wunderground":
    [
        { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2021], "mois":[1] }
        { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2021], "mois":[3] }
        { "code_pays":"it", "region": "LIBD", "ville":"matera", "annees":[2021], "mois":[1,3] }
    ],

    "meteociel":
    [
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020, 2021], "mois":[2] },
        { "code_num":"2", "code": "7249", "ville":"orleans", "annees":[2020], "mois":[1, 2], "jours":[27,31] }
    ]
}

la config ogimet n°1 récupère tous les mois de 2020 à 2025.
La config ogimet n°2 récupère les jours 13 à 18 des mois de janvier à mai 2023

les configs wunderground n° 1 et 2 récupèrent les mois de janvier et mars 2021
la config wunderground n°3 récupère les mois de janvier à mars 2021 (janvier, février, mars)

la config meteociel n°1 récupère les mois de février 2020 et février 2021
la config meteociel n°2 récupère les jours 27 à 31 de janvier 2020 et 27 à 28 de février 2020
