import logging
import os
import pickle
import time

import logger_config
from Database.helpers import is_auction_old_or_posterior_rounds
from GoogleMaps.GoogleMaps import GoogleMaps

logger = logging.getLogger(__name__)


def is_auction_old(delegation, lotes):
    # Get the first lote of the auction with non-empty data
    for lote in lotes:
        lands = lote["data"]["refs"]
        if lands:
            first_non_empty_lote = lands
            break
    for land in first_non_empty_lote:
        if land:
            old_auction = is_auction_old_or_posterior_rounds(delegation, land)
            break
    return old_auction


def get_value(object, key=None):
    if object:
        if not key:
            return object
        else:
            return object[key]
    else:
        return None


def convert_path_to_str(path):
    if not path:
        return None
    else:
        return str(path)


def full_get_data_two_directions(
    delegation, i_lote, i_land, land, coordinates_land, data_sabi
):
    # Check if sa_-_bi info has not been scraped
    if data_sabi is None:
        # Log
        msg = f"Scraping done with Sa_-_bi class didn`t work succesfully for land '{land}', the value of the argument data_sabi is None, so the class 'GoogleMaps' won't be used to scrape info between two directions."
        logger.info(f"{logger_config.build_id(delegation, i_lote, i_land)}{msg}")
        return None

    full_data_two_directions = []
    for _, enterprise in data_sabi.iterrows():
        # Check enterprise has the coordinates right in Sa_-_bi
        # Some have coordinate X = 0 and coordinate Y = 0. So they wont be used to get_data_two_directions()
        if float(enterprise["Coordenada - Y"]) != 0:
            enterprise_direction = (
                f"{enterprise['Coordenada - Y']}, {enterprise["Coordenada - X"]}"
            )
            two_directions = GoogleMaps(
                delegation,
                i_lote,
                i_land,
                land,
                coordinates_land,  # 'to'
                enterprise_direction,  # 'from'
                enterprise["Nombre"],  # 'enterprise'
            )
            # Variable that holds a dictionary with 2 keys, each one holds another dictionary with 2 keys.
            # {"car": {"distance","time"}, "foot": {"distance","time"}}
            data_two_directions = two_directions.get_data_two_directions()
            full_data_two_directions.append(
                {"cif": enterprise["Código NIF"], "data": data_two_directions}
            )
    return full_data_two_directions


def convert_paths(
    auction_pdf_path,
    path_ortofoto_land,
    path_kml_land,
    path_googlemaps_land,
    path_report_land,
    fullpath_mapa_curvas_nivel,
    fullpath_mapa_lidar,
    fullpath_usos_suelo,
    fullpath_ortofoto_hidrografia,
):
    return {
        "auction_pdf_path": convert_path_to_str(auction_pdf_path),
        "path_ortofoto_land": convert_path_to_str(path_ortofoto_land),
        "path_kml_land": convert_path_to_str(path_kml_land),
        "path_googlemaps_land": convert_path_to_str(path_googlemaps_land),
        "path_report_land": convert_path_to_str(path_report_land),
        "fullpath_mapa_curvas_nivel": convert_path_to_str(fullpath_mapa_curvas_nivel),
        "fullpath_mapa_lidar": convert_path_to_str(fullpath_mapa_lidar),
        "fullpath_usos_suelo": convert_path_to_str(fullpath_usos_suelo),
        "fullpath_ortofoto_hidrografia": convert_path_to_str(
            fullpath_ortofoto_hidrografia
        ),
    }


def save_python_object_to_file(data):
    with open("data.pkl", "wb") as file:
        pickle.dump(data, file)


def read_python_object_from_file():
    with open("data.pkl", "rb") as file:
        data = pickle.load(file)
        print(data)
    return data


# LAND VARIABLES THAT CONTAINS RELEVANT DATA:
# (mandatory for next steps) | data_land = {"localizacion","province", "municipio", "clase", "uso", "cultivo"}
# (mandatory for next steps) | coordinates_land = string
# (mandatory for next steps) | data_correos = {"cp", "province", "locality"}
# (optional for next steps) | report_data_land = {"ath","denominacion_ath","agrupacion_cultivo","agrupacion_municipio","number_buildings","slope","fls"}
# (optional for next steps) | value_land = float
# (optional for next steps) | data_ine_population = {"population_now","population_before"}
# (optional for next steps) | data_ine_transmisiones = {"transactions_now","transactions_before"}
# (optional for next steps) | data_usos_suelo = {"ID", "Código iberpix", "Cubierta terrestre iberpix", "Código CODIIGE", "Cubierta terrestre CODIIGE", "Código Uso de suelo", "Uso del suelo HILUCS", "Superficie (Ha)"}
# (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}
# (optional for next steps) | data_sabi = df with 61 columns
# (optional for next steps) | data_two_directions = {"car": {"distance","time"}, "foot": {"distance","time"}}

# FILES THAT ARE DOWNLOADED:
# (mandatory) | auction_pdf_path (saved in /data/auction/some_name.pdf) | get_pliego()
# (mandatory) | path_ortofoto_land (saved in /data/catastro/some_name.pdf) | Catastro.get_data()
# (mandatory) | path_kml_land (saved in /data/catastro/some_name.kml) | Catastro.get_data()
# (mandatory) | path_googlemaps_land (saved in /data/googlemaps/ref_catast.png) | Google_Maps.get_one_direction()
# (optional, only for rusticas) | path_report_land (saved in /data/report/some_name.pdf) | CatastroReport.get_data()
# (optional)  | fullpath_mapa_curvas_nivel (saved in /data/iberpix/some_name.png) | Iberpix.get_data()
# (optional)  | fullpath_mapa_lidar (saved in /data/iberpix/some_name.png) | Iberpix.get_data()
# (optional)  | fullpath_mapa_usos_suelo (saved in /data/iberpix/some_name.png) | Iberpix.get_data()
# (optional)  | fullpath_mapa_ortofoto_hidrografia (saved in /data/iberpix/some_name.png) | Iberpix.get_data()
# (mandatory) | data_two_directions['path'] (saved in /data/googlemaps/ref_catast-name_enterprise.png) | Google_Maps.get_data_two_directions()
