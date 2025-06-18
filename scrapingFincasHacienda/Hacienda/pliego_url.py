# Functions used to extract the url of the Pliego/Anexo PDF for a given auction url.

import logging
from datetime import date

import Hacienda.constants as const
import logger_config
import regex
import requests
from bs4 import BeautifulSoup
from Hacienda.data_pdf import read_pdf

# Logger configuration
logger = logging.getLogger(__name__)


def get_pliego(href: str, delegation: int) -> str:

    # Validate the data types of our arguments
    assert isinstance(href, str), f"Href {href} must be a string!"
    assert delegation > 0, f"Delegation {delegation} is not greater than zero!"

    # Given the href of the auction, from all the anchor tags of the web page,
    # returns the href of the one that correspond to the Pliego PDF.
    try:
        html_text = requests.get(href)
        soup = BeautifulSoup(html_text.text, "lxml")
        pliego = soup.find("a", href=const.PLIEGO_PATTERN).get("href")
        url_pliego = const.BASE_URL_HACIENDA + pliego

        # If Pliego PDF doesn't contain a list of lands in auction, check for Anexo PDF.
        if not has_ref_catastral(url_pliego):
            anexo = soup.find("a", href=const.ANEXO_PATTERN).get("href")
            url_anexo = const.BASE_URL_HACIENDA + anexo
            url_pliego = url_anexo

        # Log
        msg = f"List of lands: {url_pliego}."
        logger.info(f"{logger_config.build_id(delegation)}{msg}")

        return url_pliego

    except Exception:

        # Log
        msg = f"Failed to find list of lands on Pliego or Anexo."
        logger.error(f"{logger_config.build_id(delegation)}{msg}", exc_info=True)

        return None


def has_ref_catastral(url_pdf: str):

    # Validate the data types of our arguments
    assert isinstance(url_pdf, str), f"Url_pdf {url_pdf} must be a string!"

    # Sometimes the Pliego PDF doesn't contain the list of properties, but just the announcement,
    # and so the list of properties is detailed on another anchor tag
    text_pdf = read_pdf(url_pdf)
    return regex.search(const.REF_CATASTRAL_PATTERN, text_pdf)


def download_url_pliego_pdf(url_pdf: str, delegation: int, auction: int) -> str:
    # Returns the current local date
    today = date.today()
    # Create the filename that will be used for the downloaded auction pdf
    filename = const.DOWNLOAD_DIR / f"{today}_Delegation_{delegation}.pdf"

    try:
        response = requests.get(url_pdf)

        # Write the content to a file
        with open(filename, "wb") as file:
            file.write(response.content)

        # Log
        msg = f"Successfully downloaded url_pliego_pdf {url_pdf}.\n Saved on {filename}"
        logger.info(f"{logger_config.build_id(delegation)}{msg}")

        return filename

    except Exception:

        # Log
        msg = f"Failed to download url_pliego_pdf."
        logger.error(f"{logger_config.build_id(delegation)}{msg}", exc_info=True)

        return None
