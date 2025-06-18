# Class that inherits from a Selenium class. Given the referencia catastral of a property,
# and the kml, it scrapes some data and take several screenshots of differents layers.
# This class will only be used for the rústicas fincas, since it doesn't have a lot of sense
# to download the LIDAR, usos suelo, curvas nivel, hidrografia and usos suelos data, for an
# apartment that is on the middle of a city
import logging
import sys
import time
from pathlib import Path

import Iberpix.constants as const
import logger_config
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class Iberpix(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self,
        delegation: int,
        lote: int,
        land: int,
        ref: str,
        kml_path: str,
        clase: str,
        debug=False,
    ):
        # ref -> referencia catastral

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(kml_path, str), f"Kml_path {kml_path} must be a string!"
        assert isinstance(clase, str), f"Clase {clase} must be a string!"
        assert isinstance(debug, bool), f"Debug {debug} must be a boolean!"

        options = webdriver.ChromeOptions()
        # Keep the browser open after the WebDriver session is terminated.
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        # It supresses the logging messages that Chrome outputs to the console
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        #
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(const.DOWNLOAD_DIR),
                "download.prompt_for_download": False,  # Automatically save files to the specified directory without asking
                "download.directory_upgrade": True,  # Browser will not prompt the user when the download directory is changed
                "safebrowsing.enabled": True,  # Dunno the reason, maybe without it something pop-up alerting me or something
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.kml_path = kml_path
        self.clase = clase
        self.debug = debug

        # Append new instance to the class attribute list
        Iberpix.all.append(self)

    def __repr__(self):
        return f"Iberpix({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.kml_path}', '{self.clase}', '{self.debug}')"

    def __str__(self):
        return (
            f"Catastro Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  Kml_path: {self.kml_path}\n"
            f"  Clase: {self.clase}\n"
            f"  Debug: {self.debug}"
        )

    # Returns a dictionary with 2 keys
    # 1) data (it contains a nested dictionary with the next 8 keys)
    #### 1) ID
    #### 2) Código iberpix
    #### 3) Cubierta terrestre iberpix
    #### 4) Código CODIIGE
    #### 5) Cubierta terrestre CODIIGE
    #### 6) Código Uso de suelo
    #### 7) Uso del suelo HILUCS
    #### 8) Superficie (Ha)
    # 2) paths (it contains a nested dictionary with the next 4 keys)
    #### 1) curvas_nivel
    #### 2) lidar
    #### 3) usos_suelo
    #### 4) ortofoto_hidrografia

    def get_data(self) -> dict:
        try:
            # Check if land is not 'Rústico'. If so, then dont proceed any further with this class,
            # log and return None
            if not self.clase == "Rústico":
                # Log
                msg = f"Land {self.ref} is '{self.clase}' instead of 'Rústico', so the class {self.__class__.__name__} won't be used to scrape anything."
                logger.info(
                    f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
                )

                return const.EMPTY_DICTIONARY

            # If is 'Rústico' proceed with the class.
            self.__land_first_page()
            self.__hide_menu()
            self.__add_land_kml_layer()
            # Curvas de nivel
            filename_mapa_curvas_nivel = (
                f"{self.ref}{const.SUFFIX_FILENAME_CURVAS_NIVEL}"
            )
            fullpath_mapa_curvas_nivel = self.__my_get_screenshot(
                filename_mapa_curvas_nivel, layer="raster"
            )

            # # Lidar
            self.__show_lidar_map()
            filename_mapa_lidar = f"{self.ref}{const.SUFFIX_FILENAME_LIDAR}"
            fullpath_mapa_lidar = self.__my_get_screenshot(
                filename_mapa_lidar, layer="lidar"
            )

            # Usos del suelo
            self.__show_usos_suelo_map()
            filename_mapa_usos_suelo = f"{self.ref}{const.SUFFIX_FILENAME_USOS_SUELO}"
            fullpath_usos_suelo = self.__my_get_screenshot(
                filename_mapa_usos_suelo, layer="ocupacion-suelo"
            )

            # 'Data_usos_suelo' is a dictionary
            # This data is regarding SIOSE 2014.
            # SIOSE stands for "Sistema de Informacion de Ocupacion Suelo Español"t
            data_usos_suelo = self.__scrape_usos_suelo_info()

            # Get ortofoto with hidrografia
            fullpath_ortofoto_hidrografia = self.__get_ortofoto_hidrografia()

            # Log
            msg = f"Successfully scraped usos del suelo info and taken several screenshots of the land '{self.ref}'."
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )

            paths = {
                "curvas_nivel": fullpath_mapa_curvas_nivel,
                "lidar": fullpath_mapa_lidar,
                "usos_suelo": fullpath_usos_suelo,
                "ortofoto_hidrografia": fullpath_ortofoto_hidrografia,
            }

            return {"data": data_usos_suelo, "paths": paths}

        except Exception:

            # Log
            msg = f"Failed to get data from land '{self.ref}'"
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
    ################################### PRIVATE METHODS ############################################
    #
    #
    #
    #
    #
    #
    #

    # Lands on the main Iberpix visor webpage
    def __land_first_page(self):
        self.get(const.BASE_URL_IBERPIX)

    # Close menu popup
    def __hide_menu(self):
        hide_btn = self.find_element(By.XPATH, "//div[@id='m-locator-ignsearch']")
        hide_btn.click()

    # Given a kml it adds it to the map as a layer
    # It also center my land on the middle of the map
    def __add_land_kml_layer(self):
        expand_menu_layers_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        expand_menu_layers_btn.click()

        add_layers_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addlayers']"
        )
        add_layers_btn.click()

        WebDriverWait(self, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='m-dialog info']"))
        )

        upload_file_input = self.find_element(
            By.XPATH, "//input[@id='m-layerswitcher-addservices-file-input']"
        )
        upload_file_input.send_keys(self.kml_path)

        hide_side_bar_btn = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        hide_side_bar_btn.click()

    # Set lidar map as background
    def __show_lidar_map(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()
        lidar_btn = self.find_element(By.XPATH, '//img[@alt="LiDAR (Relieve)"]')
        lidar_btn.click()

        self._close_error_popup()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    # Set usos suelo map as background
    def __show_usos_suelo_map(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()
        usos_suelo_btn = self.find_element(
            By.XPATH, '//img[@alt="Ocupación del suelo"]'
        )
        usos_suelo_btn.click()

        self._close_error_popup()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    # Scrape usos suelo info clicking on the middle of the land when the bg is usos suelo
    def __scrape_usos_suelo_info(self):
        # To have the mouse on info mode, so i can click on the land in the map and get extra information
        info_mode_btn = self.find_element(By.XPATH, "//button[@id='m-information-btn']")
        info_mode_btn.click()

        map_element = self.find_element(By.XPATH, "//canvas")

        actions = ActionChains(self)

        # Move the mouse to the middle of the map element (where the interested land is located)
        actions.move_to_element(map_element).click().perform()

        ##### Previous way
        # # The info about the current layers, takes a bit to load.
        # # If I try to enter before loading, it kicks me out
        # time.sleep(2)

        # info_section = self.find_element(
        #     By.XPATH, "//div[contains(@class, 'm-has-tabs')]/div/div[@data-index=1]"
        # )
        # info_section.click()
        # time.sleep(2)
        # expand_data_land_usos_suelo = self.find_element(
        #     By.XPATH, '//div[p[strong[contains(text(), "del suelo")]]]'
        # )
        # expand_data_land_usos_suelo.click()

        ##### New way (less error prone)
        WebDriverWait(self, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, "(//div[@class='ol-overlaycontainer-stopevent']/div)[1]")
            )
        )

        WebDriverWait(self, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@id,'apiIdee_feature')]")
            )
        )

        info_section = self.find_element(
            By.XPATH, "//div[@class='m-tabs']/div[@data-index=1]"
        )

        actions.move_to_element(info_section).click().perform()

        time.sleep(5)

        expand_data_land_usos_suelo = self.find_element(
            By.XPATH, '//div[p[strong[contains(text(), "del suelo")]]]'
        )
        expand_data_land_usos_suelo.click()

        # Get table that contains the specific info for the land
        data_land_usos_suelo = self.find_element(
            By.XPATH, "//table[@class='featureInfo']/tbody"
        )

        # Extract headers
        headers = data_land_usos_suelo.find_elements(By.XPATH, "./tr[1]/th")
        headers = [header.text for header in headers]

        # Extract values
        values = data_land_usos_suelo.find_elements(By.XPATH, "./tr[2]/td")
        values = [value.text for value in values]

        # Create a dictionary containing the headers and the values
        final_data = dict(zip(headers, values))

        # Close popup
        close_btn = self.find_element(By.XPATH, "//a[@title='cerrar popup']")
        close_btn.click()

        # Exit info mode
        info_mode_btn.click()

        return final_data

    # Take a screenshot of the map with the ortofoto as bg and Hidrografia layer.
    def __get_ortofoto_hidrografia(self):
        self.__set_bg_ortofoto_layer()
        # Hidrografia layer
        self.__add_layer(const.HIDROGRAFIA)
        filename_mapa_hidrografia = f"{self.ref}{const.SUFFIX_FILENAME_HIDROGRAFIA}"
        fullpath_ortofoto_hidrografia = self.__my_get_screenshot(
            filename_mapa_hidrografia, layer="imagen"
        )
        return fullpath_ortofoto_hidrografia

    # Establish the ortofoto as the background of the web.
    def __set_bg_ortofoto_layer(self):
        choose_background_layer = self.find_element(
            By.XPATH, '//button[contains(@aria-label,"BackImgLayer")]'
        )
        choose_background_layer.click()

        select_ortofoto_layer = self.find_element(
            By.XPATH, "//div[@id='m-backimglayer-lyr-imagen']"
        )
        select_ortofoto_layer.click()

        self._close_error_popup()

        close_side_panel = self.find_element(
            By.XPATH, '//button[@aria-label="Plugin BackImgLayer"]'
        )
        close_side_panel.click()

    # Explanation of arguments:
    # all: If we want to see all the sublayers for the given url_service
    # If we dont want to see all the sublayers but only one, we should:
    #    1. Set the all argument to False
    #    2. Provide:
    #       a) The id of the correspondant span attribute (name_sublayer) OR
    #       b) Specify the number of the sublayer we want to see (the 1º, the 2º...)
    # Method used to add a layer to the map
    def __add_layer(
        self, url_service, all=True, name_sublayer="", number_position_sublayer=0
    ):
        expand_layer_collapse_btn = self.find_element(
            By.XPATH, "//div[@title='Gestor de capas']/button"
        )
        expand_layer_collapse_btn.click()

        add_layer_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addlayers']"
        )
        add_layer_btn.click()

        input_search = self.find_element(
            By.XPATH, "//input[@id='m-layerswitcher-addservices-search-input']"
        )
        input_search.send_keys(url_service)

        search_btn = self.find_element(
            By.XPATH, "//button[@id='m-layerswitcher-addservices-search-btn']"
        )
        search_btn.click()

        # If i want to add all the sublayers
        if all:
            add_layer_btn = self.find_element(
                By.XPATH, "//button[@id='m-layerswitcher-addservices-selectall']"
            )
            add_layer_btn.click()
        # If I dont want to add all the sublayers, but just one (I can specify it using the id of the correspoondant span attribute)
        else:
            if name_sublayer:
                sublayer_btn = self.find_element(
                    By.XPATH, f"//span[@id='{name_sublayer}']"
                )
                sublayer_btn.click()
            elif (
                number_position_sublayer
            ):  # Actually I'm not using this argument in my script.
                pass

        accept_btn = self.find_element(
            By.XPATH,
            "//div[@id='m-layerswitcher-addservices-results']//button[contains(@class,'m-layerswitcher-addservices-add')]",
        )
        accept_btn.click()

        close_sidebar = self.find_element(
            By.XPATH, "//button[@aria-label='Plugin Layerswitcher']"
        )
        close_sidebar.click()

    # When called it takes a screenshot of the web, and save it with the filename
    # that we pass as an argument
    def __my_get_screenshot(self, filename, layer):
        # The background layers takes a bit of time to load. If i dont set any time, the screenshot
        # is wrong, and i see nothing
        time.sleep(5)

        # Build the filename that will have our downloader file
        path = const.DOWNLOAD_DIR / filename

        self.get_screenshot_as_file(path)

        return path

    def _close_error_popup(self):
        # Sometimes it pops up an error
        # Despite the error the layer is loaded, so we ignore the error
        try:
            button_error = self.find_element(
                By.XPATH, "//div[@class='m-dialog error']//button"
            )
            button_error.click()
        except:
            return None
