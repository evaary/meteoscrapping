import pandas as pd
from abc import abstractmethod
from typing import List
from requests_html import Element, HTMLSession
from app.scrappers.exceptions import HtmlPageException
from app.tps.tps_module import TaskParameters
from app.ucs.ucs_module import ScrapperUC


class Scrapper:

    @abstractmethod
    def scrap_from_uc(self, uc: ScrapperUC) -> pd.DataFrame:
        pass

    @staticmethod
    def _load_html(tp: TaskParameters):

        try:
            with HTMLSession() as session:
                html_page = session.get(tp.url)
                html_page.html.render(sleep=tp.waiting,
                                      keep_page=True,
                                      scrolldown=1)
            if html_page.status_code != 200:
                raise HtmlPageException()

        except Exception:
            raise HtmlPageException()

        attr = tp.criteria.get_css_attr()
        val = tp.criteria.get_attr_value()
        table: Element = [tab
                          for tab in html_page.html.find("table")
                          if attr in tab.attrs and tab.attrs[attr] == val][0]
        try:
            condition = "no valid" in table.find("thead")[0]\
                                           .find("th")[0]\
                                           .text\
                                           .lower()\
                                           .strip()
            table = None if condition else table

        except IndexError:
            pass

        if table is None:
            raise HtmlPageException()

        return table

    @staticmethod
    def _scrap_columns_names(table: Element) -> "List[str]":
        pass

    @staticmethod
    def _scrap_columns_values(table: Element) -> "List[str]":
        pass

    @abstractmethod
    def _rework_data(self,
                     values: "List[str]",
                     columns_names: "List[str]",
                     tp: TaskParameters) -> pd.DataFrame:
        pass
