version 1.2 - 14/04/2025 - wunderground indisponible
Un programme de webscrapping pour récupérer des données météorologiques depuis ogimet, wunderground et meteociel.

Exemples de tableaux récupérés:
    1 - https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=7&day=31&hora=23&ndays=31
    2-  https://www.ogimet.com/cgi-bin/gsynres?ind=07149&ndays=28&ano=2020&mes=2&day=28&hora=23&lang=en&decoded=yes
    3 - https://www.wunderground.com/history/monthly/it/bergamo/LIME/date/2020-3
    4 - https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021
    5 - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020

Utilisation:

    télécharger l'exécutable
        - fichier zip : https://drive.google.com/file/d/1npMHnTwY2DcpczSIZeIbTtxZ91C8D7gx/view?usp=sharing
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
          https:       [...]                  /monthly/<code_pays>/<ville>/<region>/[...]
        - /!\   Les unités sont converties dans les résultats
                températures (°F -> °C),    vitesses (mph -> km/h), précipitations (in -> mm),  pressions (inHg -> hPa).

    Pour les jobs meteociel jour par jour:
        - https://www.meteociel.com/climatologie/obs_villes.php?code=7249&mois=1&annee=2021
          https://     [...]                                    code=<code>    [...]

    Pour les jobs meteociel heure par heure
        - https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020
          https://     [...]                                  code2=<code>&jour2=   [...]
        - /!\ Les mois dans l'URL sont numérotés différement. Dans la config, utiliser les numéros usuels.
        - La colonne "vent (rafales)" est séparée en 3 colonnes distinctes :
            la direction du vent en degré
            la vitesse moyenne du vent
            la vitesse max

Informations importantes

    - 1 CSV (résultats) et éventuellement 1 JSON (erreurs) seront générés par configuration.
    - le paramètre "ville" est imposé pour wunderground mais arbitraire pour les autres.
    - les jours absurdes (31 février par exemple), sont autorisés dans les configurations et triés automatiquement.
    - Des ConnectionResetError peuvent apparaitre pendant le téléchargement, elles ne sont pas graves.
    - La 1ère fois que le programme se lance, il téléchargera chromium, c'est normal.
    - Dans les paramètres généraux :
        si "parallelisme" est "true", plusieurs pages seront téléchargées en même temps.
        S'il est false, on télécharge les pages 1 par 1.
        "cpus" est le nombre de téléchargements en parallèle à faire. -1 correspond à "autant que possible".


    meteociel heure par heure
    La durée du téléchargement dépend du nombre de jours (1 page de 24h requêtée par jour demandé)

    ogimet heure par heure
    La durée du téléchargement dépend surtout du nombre de mois (1 page requêtée par mois demandé).
    Chaque page scrappée peut contenir jusqu'à 1 mois de données heure par heure.

    wunderground, meteociel et ogimet jour par jour
    La durée du téléchargement dépend du nombre de mois (1 page de 28/30/31 jours requêtée par mois demandé)

Performances

    meteociel heure
    { "code":"7249", "ville":"orleans", "dates":["1/1/2019", "31/12/2020"] }
    séquentiel : 17 521 lignes en 3 065s, sans fichier d'erreur
    parallèle  : 17 521 lignes en   774s, sans fichier d'erreur

    ogimet heure
    { "ind":"07149", "ville":"paris_orly", "dates":["1/1/2015", "31/12/2020"] }
    séquentiel : 52 417 lignes en 2 739s, sans fichier d'erreur
    parallèle  : 52 417 lignes en   722s, sans fichier d'erreur

    ogimet jour
    { "ind":"07149", "ville":"paris_orly", "dates":["1/2015", "12/2020"] }
    séquentiel : 2 191 lignes en 2 431s, sans fichier d'erreur
    parallèle  : 2 191 lignes en 1 318s, sans fichier d'erreur

    wunderground jour
    { "code_pays":"it", "region":"LIBD", "ville":"matera", "dates":["1/2013", "12/2023"] }
    séquentiel : ne fonctionne pas
    parallèle  : ne fonctionne pas

    meteociel jour
    { "code":"7249", "ville":"orleans", "dates":["1/1975", "12/2023"] }
    séquentiel : 17 898 lignes en 2 336s, sans fichier d'erreur
    parallèle  : 17 898 lignes en   627s, sans fichier d'erreur


Structure du fichier config.json:
{
    "parametres_generaux":
    {
        "parallelisme": true,
        "cpus": -1
    },

    "ogimet":
    [
        { "ind":"16288", "ville":"Caserta", "dates":["1/2020"] },
        { "ind":"16288", "ville":"Caserta", "dates":["1/2020", "12/2025"] },
        { "ind":"16288", "ville":"Caserta", "dates":["13/1/2023", "18/5/2023"] }
    ],

    "wunderground":
    [
        { "code_pays":"it", "region":"LIBD", "ville":"matera", "dates":["1/2021"] },
        { "code_pays":"it", "region":"LIBD", "ville":"matera", "dates":["3/2021"] },
        { "code_pays":"it", "region":"LIBD", "ville":"matera", "dates":["1/2021", "3/2021"] }
    ],

    "meteociel":
    [
        { "code":"7249", "ville":"orleans", "dates":["27/1/2020", "31/2/2020"] }
    ]
}

la config ogimet n°1 récupère le mois de janvier 2020.
la config ogimet n°2 récupère tous les mois de 2020 à 2025.
La config ogimet n°3 récupère les jours 13 à 31 de janvier, tout février, mars, avril, et les jours 1 à 18 de mai 2023

les configs wunderground n°1 et 2 récupèrent les mois de janvier et mars 2021
la config wunderground n°3 récupère les mois de janvier, février, et mars 2021
pour wunderground, "dates":["1/1/2021", "1/3/2021"] est illégal (pas de jours pour wunderground)

la config meteociel n°1 récupère les jours 27 à 31 de janvier 2020 et 1 à 28 de février 2020, malgré le jour 31 renseigné
