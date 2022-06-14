from requests_html import HTMLSession

class ScrappingToolsInterface:
    
    '''
    Une interface compilant les méthodes destinées à récupérer une page html,
    identifier le tableau de données et scrapper les data.
    '''

    @staticmethod
    def _get_html_page(url: str, waiting: int):
        
        '''
        Charge la page html où se trouvent les données à récupérer
        
        @param url : string, l'url de la page contenant le tableau de données
        @param waiting : int, le temps que l'on doit attendre pour que le javascript s'éxecute
            et que les données soient disponibles sur la page (wunderground et ogimet).
        
        @return: html_page (requests.Response ou None, voir doc requests python)
        '''
        # (1) Instanciation de l'objet qui récupèrera le code html. i est le nombre de tentatives de connexion.
        # (2) On tente max 3 fois de charger la page à l'url donnée. Si le chargement réussit, on garde la page. 
        #     Sinon, on la déclare inexistante. A l'origine, cela sert à palier à des mauvaises connexions internet...
        print("start")
        html_page = None
        i = 0
        with HTMLSession() as session:
        # (2)
            while(html_page is None and i < 3):
                print("in while")
                i += 1
                if(i > 1):
                    print("\tretrying...")
                try:
                    print("récup")
                    html_page = session.get(url) # long
                    print("récup 2")
                    html_page.html.render(sleep=waiting, keep_page=True, scrolldown=1)
                    print("récup ok")
                except Exception:
                    print("erreur")
                    html_page = None

        return html_page
    
    @staticmethod
    def _find_table_in_html(html_page, criteria: tuple):
        
        '''
        Extrait la table html contenant les données à récupérer.
        @param html_page : requests.Response, la page html contenant le tableau de données.
        @param criteria : tuple(str, str), l'attribut css et sa valeur permettant
            d'identifier la table à récupérer.
            
        @return : table (requests-html.Element ou None, voir doc requests-html python).
        '''
        # (1) Le critère permet d'identifier le tableau que l'on cherche dans la page html.
        #     Il se compose d'un attribut html et de sa valeur.
        # (2) On cherche une table html correspondant au critère parmis toutes celles de la page.
        #     On récupère la 1ère trouvée. Si on ne trouve pas de table, on la déclare inexistante.  
        # (3) On vérifie que la table n'indique pas l'absence de données (spécifique à ogimet).
        #     Voir http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2016&mes=4&day=0&hora=0&min=0&ndays=31
        #     Si elle l'est, on déclare la table inexistante.
        
        # (1)
        attr, val = criteria
        # (2)
        try:
            table = [
                tab for tab in html_page.html.find("table")
                if attr in tab.attrs and tab.attrs[attr] == val
            ][0]
        except Exception:
            table = None
            return table
        # (3)
        try:
            condition = "no valid" in table.find("thead")[0].find("th")[0].text.lower().strip()
            table = None if condition else table
        except IndexError:
            pass

        return table
    
    @staticmethod
    def _scrap_columns_names(table):
        '''
        @param : table, le tableau html retourné par _find_table_in_html
        @return : la liste des noms des colonnes (list de str).
        '''
        pass

    @staticmethod
    def _scrap_columns_values(table):
        '''
        @param : table, le tableau html retourné par _find_table_in_html
        '''
        pass
