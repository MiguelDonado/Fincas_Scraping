# Class that extract the number of rural lands trades that's been on a province now, years before
# The INE only provides this data for rural lands

import logging
import time
from typing import Union

import INE.constants as const
import logger_config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)


class IneNumTransmisionesFincasRusticas(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self,
        delegation: int,
        lote: int,
        land: int,
        ref: str,
        cp: str,
        clase: str,
        debug=False,
    ):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(cp, (str, type(None))), f"C.P. {cp} must be a string or None!"
        assert isinstance(clase, str), f"Clase {clase} must be a string!"
        assert isinstance(debug, bool), f"Debug {debug} must be a boolean!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.cp = str(cp)[0:2]
        self.clase = clase
        self.debug = debug

        # Append new instance to the class attribute list
        IneNumTransmisionesFincasRusticas.all.append(self)

    def __repr__(self):
        return f"IneNumTransmisionesFincasRusticas({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.cp}', '{self.clase}', '{self.debug}')"

    def __str__(self):
        return (
            f"IneNumTransmisionesFincasRusticas Object\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  C.P.: {self.cp}\n"
            f"  Clase: {self.clase}\n"
            f"  Debug: {self.debug}"
        )

    def get_data(self) -> dict[str, Union[int, float]]:
        try:
            # Check if land is not 'Rústico'. If so, then dont proceed any further with this class,
            # log and return dictionary with empty values
            if not self.clase == "Rústico":
                # Log
                msg = f"Land {self.ref} is '{self.clase}' instead of 'Rústico', so the class {self.__class__.__name__} won't be used to scrape anything."
                logger.info(
                    f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
                )
                return const.EMPTY_DICTIONARY_FINCAS

            # Check if the data scraped from Correos work successfully or not
            # If not, then dont proceed any further with this class, log and return a dictionary with empty values
            if not self.cp:
                # Log
                msg = f"Scraping done with Correos class didn`t work succesfully for land '{self.ref}', the value of the argument data_correos['cp'] is {self.cp}, so the class {self.__class__.__name__} won't be used to scrape anything."
                logger.info(
                    f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
                )
                return const.EMPTY_DICTIONARY_FINCAS

            # If is 'Rústico' proceed with the class.
            self.__land_first_page()
            self.__close_cookies()
            self.__choose_province()
            self.__choose_transaction_type()
            self.__choose_past_year()
            self.__see_results()
            data = self.__get_results()

            # Log
            msg = f"Number of transactions of 'Fincas Rusticas' where land '{self.ref}' is located: Now -> {data['transactions_now']} /// Seven years ago -> {data['transactions_before']}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data

        except Exception:

            # Log
            msg = f"Failed to get number of transactions of the province where the land '{self.ref}' is located."
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )
            return const.EMPTY_DICTIONARY_FINCAS

        finally:
            if self.debug == False:
                self.quit()
                time.sleep(1)

    #
    #
    #
    #
    #
    #
    #
    ################################### PRIVATE METHODS ############################################
    #
    #
    #
    #
    #
    #
    #

    # Lands on an Ine webpage
    def __land_first_page(self) -> None:
        self.get(const.BASE_URL_INE)

    def __close_cookies(self) -> None:
        accept_btn = self.find_element(By.XPATH, "//a[@id='aceptarCookie']")
        accept_btn.click()

    # Deselect all the provinces, and select the right one
    def __choose_province(self) -> None:
        choose_province_selection = self.find_element(
            By.XPATH, "//select[@id='cri55176']"
        )
        select = Select(choose_province_selection)
        province_name_option = self.find_element(
            By.XPATH,
            f"//option[@class='jP_2' and contains(text(), '{self.cp}')]",
        )
        province_visible_text = province_name_option.text
        select.deselect_all()
        select.select_by_visible_text(province_visible_text)

    # Deselect the default transaction type, and choose the right one
    def __choose_transaction_type(self) -> None:
        choose_tipo_transaccion = self.find_element(
            By.XPATH, "//select[@id='cri55177']"
        )
        select = Select(choose_tipo_transaccion)
        select.deselect_by_index(0)
        select.select_by_visible_text("Compraventa")

    # Select 7 years ago (the actual year is already selected)
    def __choose_past_year(self) -> None:
        choose_year_select = self.find_element(By.XPATH, "//select[@id='periodo']")
        select = Select(choose_year_select)
        select.select_by_index(7)

    # Let the instance on the results webpage
    def __see_results(self) -> None:
        see_results = self.find_element(By.XPATH, "//input[@id='botonConsulSele']")
        see_results.click()

    # Return a dictionary that contains 2 keys
    #   1) transactions_now
    #   2) transactions_before
    def __get_results(self) -> dict[str, Union[int, float]]:
        actual_year = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[2]"
            ).text.replace(".", "")
        )

        seven_years_ago = int(
            self.find_element(
                By.XPATH, "//table[@id='tablaDatos']/tbody/tr/*[3]"
            ).text.replace(".", "")
        )

        return {"transactions_now": actual_year, "transactions_before": seven_years_ago}
