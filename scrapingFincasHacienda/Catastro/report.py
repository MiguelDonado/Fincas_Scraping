# Class that uses Selenium to extract the reference value
# and downloads the price report PDF for a land
import datetime
import logging
import os
import sys
import time
from typing import Union

import Catastro.constants as const
import logger_config
import pdfplumber
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

logger = logging.getLogger(__name__)

config = dotenv_values()

# Get the current date
current_date = datetime.datetime.now() - datetime.timedelta(days=365)

# Format the date as dd/mm/yyyy
formatted_date = current_date.strftime("%d/%m/%Y")


class CatastroReport(webdriver.Chrome):

    # Class attribute to store all instances
    all = []

    def __init__(
        self, delegation: int, lote: int, land: int, ref: str, clase: str, debug=False
    ):

        # Validate the data types of our arguments
        assert delegation > 0, f"Delegation {delegation} is not greater than zero!"
        assert lote > 0, f"Lote {lote} is not greater than zero!"
        assert land > 0, f"Land {land} is not greater than zero!"
        assert isinstance(ref, str), f"Ref {ref} must be a string!"
        assert isinstance(clase, str), f"Clase {clase} must be a string!"
        assert isinstance(debug, bool), f"Debug {debug} must be a boolean!"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(const.DOWNLOAD_DIR_REPORT),
                "download.propmt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        super().__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.delegation = delegation
        self.lote = lote
        self.land = land
        self.ref = ref
        self.clase = clase
        self.debug = debug

        # Append new instance to the class attributes list
        CatastroReport.all.append(self)

    def __repr__(self):
        return f"CatastroReport({self.delegation}, {self.lote}, {self.land}, '{self.ref}', '{self.clase}', '{self.debug}')"

    def __str__(self):
        return (
            f"CatastroReport Object:\n"
            f"  Delegation: {self.delegation}\n"
            f"  Lote: {self.lote}\n"
            f"  Land: {self.land}\n"
            f"  Ref: {self.ref}\n"
            f"  Clase: {self.clase}\n"
            f"  Debug: {self.debug}"
        )

    # Scrape the reference value and download the 'Report PDF' if the land is 'Rústico'
    def get_data(self) -> dict[str, Union[float, dict[str, str]]]:
        try:
            self.__land_first_page()
            self.__close_cookies()
            self.__access_query_value_page()
            self.__insert_dni()
            self.__select_date_and_property()
            reference_value = self.__get_reference_value()
            report = self.__get_reference_value_report()

            if not report:
                data_report = const.EMPTY_DICTIONARY
            else:
                data_report = self.__process_report(report)

            # Log
            dynamic_msg = (
                f"The report PDF has been downloaded because it's '{self.clase}'."
                if data_report["ath"]
                else f"The report PDF has not been downloaded, because it is '{self.clase}' instead of 'Rústico'."
            )
            msg = f"The land '{self.ref}' has the next value {reference_value}.\n{dynamic_msg}"
            logger.info(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
            )

            return {"value": reference_value, "data": data_report, "path": report}
        except Exception:

            # Log
            msg = f"Failed to get the reference value and the 'Report PDF' of the land '{self.ref}'"
            logger.error(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}",
                exc_info=True,
            )
            return {"value": None, "data": const.EMPTY_DICTIONARY, "path": None}
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

    # Lands on the main Catastro Report webpage
    def __land_first_page(self) -> None:
        self.get(const.BASE_URL_REPORT_CATASTRO)

    def __close_cookies(self):
        accept_cookies = self.find_element(By.XPATH, "//a[@aria-label='allow cookies']")
        accept_cookies.click()

    # Navigate to the query value webpage
    def __access_query_value_page(self) -> None:
        button_collapse = self.find_element(
            By.XPATH, "(//a[@data-toggle='collapse'])[2]"
        )
        button_collapse.click()
        query_value_button = self.find_element(
            By.XPATH,
            "//div[@id='accordion2024']//div[@role='tab']/following-sibling::div//a[contains(text(),'Consulta de valor de referencia')]",
        )
        query_value_button.click()

    # Given the query value webpage, introduce DNI on the form
    def __insert_dni(self) -> None:
        dni_input = self.find_element(By.XPATH, "//input[@id='ctl00_Contenido_nif']")
        dni_input.clear()
        dni_input.send_keys(config["MY_DNI"])
        num_soporte_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_soporte']"
        )
        num_soporte_input.clear()
        num_soporte_input.send_keys(config["MY_DNI_SUPPORT_NUM"])
        validate_button = self.find_element(
            By.XPATH, "//button[@id='ctl00_Contenido_bAceptar']"
        )
        validate_button.click()

    # Given the query value webpage, introduce date on the form
    def __select_date_and_property(self) -> None:
        ref_catastral_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtRC2']"
        )
        ref_catastral_input.send_keys(self.ref)
        date_input = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_txtFechaConsulta']"
        )
        date_input.send_keys(formatted_date)

        # Finding the select element
        purpose_input = self.find_element(
            By.XPATH, "//select[@id='ctl00_Contenido_ddlFinalidad']"
        )
        # Create a select objetc
        select = Select(purpose_input)
        select.select_by_value("1")

        submit_button = self.find_element(
            By.XPATH, "//input[@id='ctl00_Contenido_btnValorReferencia']"
        )
        submit_button.click()

    # Given the final webpage, scrape the reference value
    def __get_reference_value(self) -> float:
        value_label = self.find_element(
            By.XPATH,
            "//span[text()='Valor de Referencia']/following-sibling::div//label",
        )
        return self.__format_price(value_label.text)

    # Download and return the name of the PDF report only if the land is "Rústico" because
    # on the rest of cases the PDF report is different and dont have relevant data.
    def __get_reference_value_report(self) -> str:
        if not self.clase == "Rústico":
            return None
        try:
            report_button = self.find_element(
                By.XPATH, "//input[@id='ctl00_Contenido_Button2']"
            )
        except Exception:

            # Log
            msg = f"The land '{self.ref}' is '{self.clase}' but doesn't has a report."
            logger.warning(
                f"{logger_config.build_id(self.delegation, self.lote, self.land)}{msg}"
            )
            return None

        # If there's no report for the land
        if not report_button:
            return None

        report_button.click()

        WebDriverWait(self, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe"))
        )
        download_pdf_button = self.find_element(
            By.XPATH, "//a[@id='ctl00_Contenido_ucPdf_LDescargaFichero']"
        )
        download_pdf_button.click()
        # Give time to the PDF to be downloaded, before trying
        # to rename it, or do something with the file
        CatastroReport.__wait_file_is_downloaded(const.DOWNLOAD_DIR_REPORT)
        report_path = self.__rename_pdf(self.ref)
        return report_path

    # We use static methods when we want to do something that is not unique per instance,
    # but it should do something that has a relationship with the class
    @staticmethod
    def __rename_pdf(ref_catastral: str) -> str:

        # Validate the data types of our arguments
        assert isinstance(
            ref_catastral, str
        ), f"Ref_catastral {ref_catastral} must be a string!"

        # Get the most recent file from the pdf destination directory
        most_recent_file = max(
            [
                os.path.join(const.DOWNLOAD_DIR_REPORT, f)
                for f in os.listdir(const.DOWNLOAD_DIR_REPORT)
            ],
            key=os.path.getctime,
        )
        # Establish the variable that helds the new path
        new_file_path = os.path.join(const.DOWNLOAD_DIR_REPORT, ref_catastral + ".pdf")
        os.rename(most_recent_file, new_file_path)
        return new_file_path

    @staticmethod
    def __wait_file_is_downloaded(download_dir, timeout=60, poll_interval=0.5):
        """
        Waits until a new file appears in download_dir
        """
        before = set(os.listdir(download_dir))
        start_time = time.time()
        while time.time() - start_time < timeout:
            after = set(os.listdir(download_dir))
            new_files = after - before
            if new_files:
                # Wait until files are fully downloaded
                completed_files = [f for f in new_files if not f.endswith("crdownload")]
                if completed_files:
                    return 0  # Success exit status code
            time.sleep(poll_interval)
        raise TimeoutError("No new file downloaded within timeout")

    @staticmethod
    def __format_price(price: str) -> float:
        if not "€" in price:
            return None
        return float(
            price.replace("€", "").replace(" ", "").replace(".", "").replace(",", ".")
        )

    # Given the price report pdf, it extracts relevant data
    @staticmethod
    def __process_report(report: str) -> dict[str, str]:

        # Validate the data types of our arguments
        assert isinstance(report, str), f"Report {report} must be a string!"

        # It'll return the text from the PDF file as one string
        with pdfplumber.open(report) as pdf:
            text_file = pdf.pages[0].extract_tables()
            ath, denominacion_ath, agrupacion_cultivo, one, agrupacion_municipio = (
                text_file[1][1]
            )
            two, three, four, number_buildings, slope, fls, *five = text_file[2][2]
        return {
            "ath": ath,
            "denominacion_ath": denominacion_ath,
            "agrupacion_cultivo": agrupacion_cultivo,
            "agrupacion_municipio": agrupacion_municipio,
            "number_buildings": number_buildings,
            "slope": slope,
            "fls": fls,
        }
