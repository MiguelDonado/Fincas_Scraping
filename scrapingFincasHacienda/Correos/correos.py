# Class that inherits from a Selenium class. Given the direction of a land,
# it returns the postal code, the province and the locality

import logging
import time

import Correos.constants as const
import logger_config
from selenium import webdriver
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class Correos(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self,
        delegation: int,
        lote: int,
        land: int,
        ref: str,
        direction: str,
        debug=False,
    ):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(direction, str), f"Direction {direction} must be a string!"
        assert isinstance(debug, bool), f"Debug {debug} must be a boolean!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.direction = direction
        self.debug = debug

        # Append new instance to the class attribute list
        Correos.all.append(self)

    def __repr__(self):
        return f"Correos({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.direction}', '{self.debug}')"

    def __str__(self):
        return (
            f"Correos Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  Direction: {self.direction}\n"
            f"  Debug: {self.debug}"
        )

    # If it works returns a dictionary containing keys with truthy values
    # If it doesnt works returns a dictionary containing keys with falsy values
    def get_data(self) -> dict[str, str]:
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__search()
            data = self.__get_info_about_search()
            cp, province, locality = data.values()

            # Log
            msg = f"Land '{self.ref}' is in '{province}' province. More precisely is on '{locality}' locality with C.P. {cp}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return data
        except Exception:

            # Log
            msg = f"Failed to get 'cp, province, locality'."
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )
            return const.EMPTY_DICTIONARY
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

    # Lands on a Correos webpage
    def __land_first_page(self) -> None:
        self.get(const.BASE_URL_CORREOS)

    def __close_cookies(self) -> None:
        reject_cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Rechazar todas las cookies']"
        )
        reject_cookies_btn.click()

    # Let the instance on the webpage that shows data about the direction
    def __search(self) -> None:
        search_input = self.find_element(
            By.XPATH,
            "//input[contains(@id, 'correos-ui-input') and @type='text']",
        )
        search_input.send_keys(self.direction)
        submit_btn = self.find_element(By.XPATH, "//button[@aria-label='BUSCAR']")
        submit_btn.click()

    # Scrape the webpage that shows info about direction.
    def __get_info_about_search(self) -> dict[str, str]:
        cp, province, locality = self.find_elements(
            By.XPATH,
            "//div[@slot='container-scroll']/div[contains(@class,'ui-list-result')][1]/following-sibling::div[1]//dd",
        )
        return {
            "cp": str(cp.text),
            "province": province.text,
            "locality": locality.text,
        }
