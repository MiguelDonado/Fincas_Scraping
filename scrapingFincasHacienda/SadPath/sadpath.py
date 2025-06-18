import logging
import sys

import logger_config
import requests
import SadPath.constants as const
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport
from Correos.correos import Correos
from GoogleMaps.GoogleMaps import GoogleMaps
from Iberpix.iberpix import Iberpix
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas
from INE.ine_population import InePopulation

logger = logging.getLogger(__name__)

id_land = (
    const.data_test["delegation"],
    const.data_test["i_lote"],
    const.data_test["i_land"],
    const.data_test["land"],
)


def check_internet_connection(url="http://www.google.com", timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            msg = "Internet connection is stable and good."
            logger.info(f"{msg}")
        else:
            msg = f"Received unexpected status code {response.status_code}"
            logger.error(
                f"{msg}",
                exc_info=True,
            )
            sys.exit()
    except requests.ConnectionError:
        msg = "No internet connection available."
        logger.error(
            f"{msg}",
            exc_info=True,
        )
        sys.exit()
    except requests.Timeout:
        msg = "The request timed out."
        logger.error(
            f"{msg}",
            exc_info=True,
        )
        sys.exit()


def check_status_code(url):
    response = requests.get(url)
    if response.status_code != 200:
        # Log
        msg = f"URL: '{url}' has been requested. Expected status code 200, but got {response.status_code}\nExecution of script has been interrupted. It will be tried again tomorrow."
        logger.error(
            f"{msg}",
            exc_info=True,
        )
        sys.exit()
    else:
        msg = f"URL: '{url}' has been requested. Get back status code 200."
        logger.info(f"{msg}")


def check_class_works(input_list, name_class):
    if None in input_list:
        msg = f"Something is not working properly with the '{name_class}' class.\nExecution of script has been interrupted. It will be tried again tomorrow."
        logger.error(
            f"{msg}",
            exc_info=True,
        )
        sys.exit()
    else:
        msg = f"CHECK: Class '{name_class}' works fine."


def check_catastro(MODE):
    # Status code
    check_status_code(const.BASE_REF_CATASTRAL_URL)
    check_status_code(const.BASE_URL_SEARCH_CATASTRO)
    check_status_code(const.BASE_URL_REPORT_CATASTRO)

    # Normal Catastro
    catastro = Catastro(*id_land, mode=MODE).get_data()
    check_class_works(list(catastro.values()), "catastro")

    # Report
    report = CatastroReport(*id_land, const.data_test["clase"]).get_data()
    check_class_works(list(report.values()), "catastroreport")


def check_correos():
    # Status code
    check_status_code(const.BASE_URL_CORREOS)

    correos = Correos(*id_land, const.data_test["localizacion"]).get_data()
    check_class_works(list(correos.values()), "correos")


def check_googlemaps():
    # Status code
    check_status_code(const.BASE_URL_GOOGLE_MAPS)

    # One direction
    google_maps = GoogleMaps(
        *id_land, const.data_test["coordinates_land"]
    ).get_data_one_direction()
    check_class_works([str(google_maps)], "googlemaps")

    # Two directions
    google_maps = GoogleMaps(
        *id_land,
        const.data_test["coordinates_land"],
        const.data_test["enterprise_direction"],
        const.data_test["enterprise_nombre"],
    ).get_data_two_directions()
    check_class_works(list(google_maps.values()), "googlemaps_two")


def check_ine():
    # Status code
    check_status_code(const.BASE_URL_INE)
    check_status_code(const.POBLACION_URL_INE)

    ine_trans_rusticas = IneNumTransmisionesFincasRusticas(
        *id_land, const.data_test["cp"], const.data_test["clase"]
    ).get_data()
    check_class_works(ine_trans_rusticas, "IneTransRusticas")

    ine_population = InePopulation(
        *id_land, const.data_test["localizacion"], const.data_test["locality"]
    ).get_data()
    check_class_works(ine_population, "InePopulation")


# In 'Hacienda' class is enough with checking the status codes
def check_hacienda():
    check_status_code(const.BASE_URL_HACIENDA)
    check_status_code(const.DELEGATION_URL)


def check_iberpix():
    check_status_code(const.BASE_URL_IBERPIX)

    iberpix = Iberpix(
        *id_land, const.data_test["path_kml_land"], const.data_test["clase"]
    ).get_data()
    check_class_works(iberpix, "iberpix")


def check_webpages_work(MODE):
    msg = f"################## SAD PATH CHECKING ##################"
    logger.info(f"{msg}")

    check_hacienda()
    check_catastro(MODE)
    check_iberpix()

    if MODE == "ADVANCED":
        check_correos()
        check_googlemaps()
        check_ine()

    msg = f"################## FINISH SAD PATH CHECKING ##################"
    logger.info(f"{msg}")
