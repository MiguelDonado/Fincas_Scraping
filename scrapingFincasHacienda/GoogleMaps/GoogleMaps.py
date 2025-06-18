# Class that inherits from a Selenium Class. It can be used in two ways
# 1) Given two directions calculates the distance and time that takes from one point to the other
# 2) Given a direction, we can take a screenshot of the place. We've to use the search_to method.


# I had two options to deal with Google Maps:
#   1. Through Google Maps API, particularly the Distance Matrix API to measure the distance between two points.
#   Using the API involves a cost (pay per usage fee)
#   2. Using Selenium to automate web browsing.
#   THis options doesn't have any cost.
# I choose Selenium because it's free and because it allows me to practice
# with Selenium library, XPATH, and Chrome Developer Tools.

import logging
import sys
import time

import GoogleMaps.constants as const
import logger_config
import regex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


def convert_path_to_str(path):
    if not path:
        return None
    else:
        return str(path)


class GoogleMaps(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self,
        delegation: int,
        lote: int,
        land: int,
        ref: str,
        to: str,
        from_: str = None,
        enterprise: str = None,
        debug=False,
    ):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(to, str), f"'To' {to} must be a string!"
        assert from_ == None or isinstance(
            from_, str
        ), f"'From' {from_} must be a string!"
        assert enterprise == None or isinstance(
            enterprise, str
        ), f"Enterprise {enterprise} must be a string!"
        assert isinstance(debug, bool), f"Debug {debug} must be a boolean!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Disable location permissions (because Google Maps took "My location"
        # as the default for 'from' direction)
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.geolocation": 2}
        )
        super().__init__(options=options)
        self.maximize_window()
        self.implicitly_wait(15)
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.to = to
        self.from_ = from_
        self.enterprise = enterprise
        self.debug = debug

        # Append new instance to the class attribute list
        GoogleMaps.all.append(self)

    def __repr__(self):
        return f"GoogleMaps({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.to}', '{self.from_}', '{self.enterprise}', '{self.debug}')"

    def __str__(self):
        return (
            f"GoogleMaps Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  To: {self.to}\n"
            f"  From: {self.from_}\n"
            f"  Enterprise: {self.enterprise}\n"
            f"  Debug: {self.debug}"
        )

    # Given a direction ('to'), it takes a screenshot of the land and the nearby interest points
    def get_data_one_direction(self) -> None:
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__search_to()
            path = self.__get_screenshot()

            # Log
            msg = f"Screenshot of the land '{self.ref}' has been taken successfully."
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return path

        except Exception:

            # Log
            msg = f"Failed to take screenshot of the land '{self.ref}'"
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )
            return None

        finally:
            if self.debug == False:
                self.quit()
                time.sleep(1)

    # Given two directions ('to' and 'from'), it returns a dictionary with 2 keys.
    #   1) car (nested dictionary with two keys)
    #       1.1) time_on_car
    #       1.2) distance_on_car
    #   2) foot (nested dictionary with two keys)
    #       2.1) time_on_foot
    #       2.2) distance_on_foot

    def get_data_two_directions(self) -> dict[str, dict[str, str]]:
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__search_to()
            self.__get_directions()
            self.__search_from_()
            data_car = self.__get_distance_time_on_car()
            data_foot = self.__get_distance_time_on_foot()
            filename = self.__get_screenshot(zoom=False, enterprise=self.enterprise)
            # Log
            msg = f"Car and foot distance and time from '{self.ref}' - '{self.enterprise}' has been extracted successfully."
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )

            return {
                "car": data_car,
                "foot": data_foot,
                "path": convert_path_to_str(filename),
            }

        except Exception:

            # Log
            msg = f"Failed to extract car and foot distance and time from '{self.ref}' - '{self.enterprise}'."
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )

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

    # Lands on Google Maps webpage
    def __land_first_page(self) -> None:
        self.get(const.BASE_URL)

    def __close_cookies(self) -> None:
        cookies_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Aceptar todo']"
        )
        cookies_btn.click()

    # Given the initial Google Maps webpage, searches 'to' destination.
    def __search_to(self) -> None:
        to_input = self.find_element(
            By.XPATH, "//input[contains(@class,'searchboxinput')]"
        )
        to_input.clear()
        to_input.send_keys(self.to)

        search_btn = self.find_element(
            By.XPATH, "//button[@id='searchbox-searchbutton']"
        )
        search_btn.click()

    # Can be used to take a screenshot about the land and the nearby interest points (only 'to')
    # Or can be used to take a screenshot about the distance between two points ('to' and 'from')
    def __get_screenshot(self, zoom=True, enterprise=False) -> None:
        hide_panel_btn = self.find_element(
            By.XPATH,
            "//button[@aria-label='Ocultar el panel lateral' and contains(@jsaction, 'drawer.close')]",
        )
        hide_panel_btn.click()

        satellite_button = self.find_element(
            By.XPATH, "//button[label[text()='Satélite']]"
        )
        # Use JavaScript to trigger the jsaction event, change to satellite view
        self.execute_script("arguments[0].click();", satellite_button)

        # Will only be True when called for the method get_data_one_direction
        if zoom:
            zoom_out_button = self.find_element(
                By.XPATH, "//button[@id='widget-zoom-out']"
            )
            zoom_out_button.click()

        # Will only be True when called for the method get_data_two_directions
        if enterprise:
            extra_path = f"-{self.enterprise[:15]}"
        else:
            extra_path = ""

        time.sleep(10)

        filename = const.DOWNLOAD_DIR / f"{self.ref}{extra_path}.png"
        self.get_screenshot_as_file(filename)
        return filename

    # Let the instance on Google Maps webpage that shows the route
    # (it must be done after searching 'to' destination)
    def __get_directions(self) -> None:
        how_to_get_btn = self.find_element(
            By.XPATH, "//button[@data-value='Cómo llegar']"
        )
        how_to_get_btn.click()

    # Given the Google Maps route webpage change the 'from' destination
    def __search_from_(self) -> None:
        from__input = self.find_element(
            By.XPATH, "//input[contains(@aria-label,'unto de partida')]"
        )
        from__input.clear()
        from__input.send_keys(self.from_)

        search_btn = self.find_element(By.XPATH, "//button[@aria-label='Buscar']")
        search_btn.click()

    # Given the final route returns a dictionary with 2 keys:
    #   1) Time on car
    #   2) Distance on car
    def __get_distance_time_on_car(self) -> dict[str, str]:
        on_car_btn = self.find_element(By.XPATH, "//button[@data-tooltip='En coche']")
        on_car_btn.click()

        WebDriverWait(self, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Copiar enlace']"))
        )
        time_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'min')]",
        )
        distance_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'm') and not(contains(text(), 'min'))]",
        )
        return {
            "time_on_car": self.__convert_to_minutes(time_label.text),
            "distance_on_car": self.__km_as_standard_unit(distance_label.text),
        }

    # Given the final route returns a dictionary with 2 keys:
    #   1) Time on foot
    #   2) Distance on foot
    def __get_distance_time_on_foot(self) -> dict[str, str]:
        on_foot_btn = self.find_element(By.XPATH, "//button[@data-tooltip='A pie']")
        on_foot_btn.click()

        WebDriverWait(self, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Copiar enlace']"))
        )
        time_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'min')]",
        )
        distance_label = self.find_element(
            By.XPATH,
            "//span[contains(@id, 'section-directions-trip')]/following-sibling::div//div[contains(text(), 'm') and not(contains(text(), 'min'))]",
        )
        return {
            "time_on_foot": self.__convert_to_minutes(time_label.text),
            "distance_on_foot": self.__km_as_standard_unit(distance_label.text),
        }

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    # Standardized all distances to km, and it returns me a float
    @staticmethod
    def __km_as_standard_unit(distance_input):
        if distance_input[-2:] == "km":
            distance = regex.sub(const.KM_PATTERN, "", distance_input).replace(",", ".")
            return float(distance)
        else:
            distance = regex.sub(const.KM_PATTERN, "", distance_input)
            distance = float(distance) / 1000
            return distance

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    # Standardized all times to min, and it returns me a integer
    @staticmethod
    def __convert_to_minutes(time_str):
        # Split the time string by spaces
        time_splitted = time_str.split()
        total_in_minutes = 0
        # Use a for loop to distinguish min than hours
        for i, element in enumerate(time_splitted):
            if i == len(time_splitted) - 1:
                return total_in_minutes
            elif time_splitted[i + 1] == "min":
                total_in_minutes += int(element)
            elif time_splitted[i + 1] == "h":
                total_in_minutes += int(element) * 60
