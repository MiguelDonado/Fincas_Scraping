import pickle
import sys

import Hacienda.constants as const
import pandas as pd
from Catastro.catastro import Catastro
from Catastro.report import CatastroReport
from Correos.correos import Correos
from Database.helpers import (
    insert_land_data,
    is_auction_id_old,
    is_ine_population_in_db,
    is_ine_transmisiones_rust_in_db,
    is_sabi_in_db,
)
from dotenv import dotenv_values
from GoogleMaps.GoogleMaps import GoogleMaps
from Hacienda.auction_delegation import has_auction
from Hacienda.data_pdf import get_auction_id, get_lotes_data
from Hacienda.pliego_url import download_url_pliego_pdf, get_pliego
from Iberpix.iberpix import Iberpix
from INE.ine_num_transmisiones_fincas_rusticas import IneNumTransmisionesFincasRusticas
from INE.ine_population import InePopulation
from Sabi.sabi import Sabi
from SadPath.sadpath import check_internet_connection, check_webpages_work
from utils import (
    convert_paths,
    full_get_data_two_directions,
    is_auction_old,
    read_python_object_from_file,
    save_python_object_to_file,
)

config = dotenv_values()

#####################
##### CONSTANTS #####
## Values that the constants can take:

# MODE in ["BASIC", "ADVANCED"]
# N_EMP in [1,25]
# PURPOSE in ["HACIENDA", "TXT"]
# PATH_TXT: Any value
MODE = "BASIC"
N_EMP = 1
PURPOSE = config["PURPOSE"]
TXT_FILE = "/home/miguel/CodingProjects/HaciendaFincas_Scraping/scrapingFincasHacienda/fincas.txt"
#####################
#####################


def main():
    # Determine which main function to execute
    if PURPOSE == "TXT":
        main_txt()
    elif PURPOSE == "HACIENDA":
        main_hacienda()


def main_txt():
    # Read fincas from txt
    with open(TXT_FILE, "r", encoding="utf-8") as file:
        fincas = [line.strip() for line in file if line.strip()]

    # SadPath
    # check_internet_connection()
    # check_webpages_work(MODE)

    # Variables that on "hacienda" logic can take multiple values
    # But on the reformulation of the script for "txt" file they behave as constants
    # I mean, they are not needed anymore for "txt" script logic, but to avoid change a lot of the code
    # I would choose the simple approach of setting them to some random value, that is not going to be used for anything
    # but this way I can reuse the code easier
    delegation = 1
    i_lote = 1
    id_auction = 1
    price = 0
    auction_pdf_path = None

    for i_land, land in enumerate(fincas, 1):

        # Tuple containing key arguments
        # *id_land = to unpack the tuple into separate arguments
        id_land = (delegation, i_lote, i_land, land)

        # 7.1) CATASTRO CLASS
        try:
            info_land = Catastro(*id_land).get_data()
            keys = ["data", "coordinates", "ortofoto", "kml"]
            data_land, coordinates_land, path_ortofoto_land, path_kml_land = [
                info_land[key] for key in keys
            ]
        except Exception as e:
            print(e)
            continue

        if MODE == "ADVANCED":
            # 7.2) CORREOS_CLASS
            data_correos = Correos(*id_land, data_land["localizacion"]).get_data()

            # 7.3) GOOGLE_MAPS CLASS
            path_googlemaps_land = GoogleMaps(
                *id_land, coordinates_land
            ).get_data_one_direction()
        else:
            data_correos = {
                "cp": None,
                "province": None,
                "locality": None,
            }
            path_googlemaps_land = None

        # 7.4) CATASTRO_REPORT CLASS
        info_report = CatastroReport(*id_land, data_land["clase"]).get_data()
        keys = ["data", "value", "path"]
        report_data_land, value_land, path_report_land = [
            info_report[key] for key in keys
        ]

        if MODE == "ADVANCED":
            # 7.5) INE_POPULATION CLASS
            # If not stored on db, then it should be scraped
            if not is_ine_population_in_db(
                *id_land, data_correos["locality"], data_land["municipio"]
            ):
                data_ine_population = InePopulation(
                    *id_land,
                    data_land["localizacion"],
                    data_correos["locality"],
                ).get_data()

            # 7.6) INE_NUMBER_TRANSMISIONES CLASS
            # If not stored on db, then it should be scraped
            if not is_ine_transmisiones_rust_in_db(*id_land, data_correos["cp"]):
                data_ine_transmisiones = IneNumTransmisionesFincasRusticas(
                    *id_land,
                    data_correos["cp"],
                    data_land["clase"],
                ).get_data()
        else:
            data_ine_population = {
                "population_now": None,
                "population_before": None,
            }
            data_ine_transmisiones = {
                "transactions_now": None,
                "transactions_before": None,
            }

        # 7.7) IBERPIX CLASS
        info_iberpix = Iberpix(*id_land, path_kml_land, data_land["clase"]).get_data()
        data_usos_suelo, paths_iberpix = info_iberpix.values()
        keys = ["curvas_nivel", "lidar", "usos_suelo", "ortofoto_hidrografia"]
        (
            fullpath_mapa_curvas_nivel,
            fullpath_mapa_lidar,
            fullpath_usos_suelo,
            fullpath_ortofoto_hidrografia,
        ) = [paths_iberpix[key] for key in keys]

        if MODE == "ADVANCED":
            # 7.8) SABI CLASS
            # 'data_sabi' contains a df with 23 columns and up to <n> enterprises
            # If not stored on db, then it should be scraped
            if not is_sabi_in_db(*id_land, data_correos["cp"]):
                data_sabi = Sabi(*id_land, data_correos["cp"], n_emp=N_EMP).get_data()

            # 7.9) GOOGLE MAPS CLASS
            # 'full_data_two_directions' contain data up to <n> enterprises given a land
            full_data_two_directions = full_get_data_two_directions(
                *id_land, coordinates_land, data_sabi
            )

        else:
            # data_sabi = pd.DataFrame()
            data_sabi = None
            # full_data_two_directions = tuple()
            full_data_two_directions = None

        # This is the info that I'll introduce in the db for each land.
        full_data_land = {
            ############### MANDATORY ############
            "electronical_id": id_auction,
            "delegation": delegation,
            "lote_number": i_lote,
            "referencia_catastral": land,
            "price": price,
            "localizacion": data_land["localizacion"],
            "municipio": data_land["municipio"],
            "clase": data_land["clase"],
            "uso": data_land["uso"],
            "aprovechamiento": data_land["cultivo"],
            "coordenadas": coordinates_land,
            "codigo_postal": data_correos["cp"],
            "province": data_land["provincia"],
            "locality": data_correos["locality"],
            ############### OPTIONAL ##############
            # '**' This notation is used to expand a dictionary
            "ath_number": report_data_land["ath"],
            "ath_name": report_data_land["denominacion_ath"],
            "agrupacion_cultivo": report_data_land["agrupacion_cultivo"],
            "agrupacion_municipio": report_data_land["agrupacion_municipio"],
            "number_buildings": report_data_land["number_buildings"],
            "slope": report_data_land["slope"],
            "fls": report_data_land["fls"],
            "population_now": data_ine_population["population_now"],
            "population_before": data_ine_population["population_before"],
            "rusticas_transactions_now": data_ine_transmisiones["transactions_now"],
            "rusticas_transactions_before": data_ine_transmisiones[
                "transactions_before"
            ],
            "catastro_value": value_land,
            "empresas": data_sabi,
            "empresas_fincas": full_data_two_directions,
            "usos_suelo": data_usos_suelo,
            ############### FILES ##############
            **convert_paths(
                auction_pdf_path,
                path_ortofoto_land,
                path_kml_land,
                path_googlemaps_land,
                path_report_land,
                fullpath_mapa_curvas_nivel,
                fullpath_mapa_lidar,
                fullpath_usos_suelo,
                fullpath_ortofoto_hidrografia,
            ),
        }
        # ######## For debugging purposes ########
        # # Save to a pickle file
        # with open("data.pkl", "wb") as pkl_file:
        #     pickle.dump(full_data_land, pkl_file)

        # print(full_data_land)

        insert_land_data(full_data_land)
        sys.exit()


def main_hacienda():
    # SadPath
    check_internet_connection()
    check_webpages_work(MODE)

    for delegation in const.DELEGATIONS:

        # 1) Search on hacienda website if there's any auction.
        if not (auction := has_auction(delegation)):
            continue

        # 2) Get the pdf that contains the list of lands. Returns url_pliego
        if not (auction_pdf_url := get_pliego(auction, delegation)):
            continue

        # 3) Get/build the auction unique identifier
        if not (id_auction := get_auction_id(auction_pdf_url, delegation, auction)):
            continue

        # 4) Check if id_auction is on db, if so continue
        if is_auction_id_old(delegation, id_auction):
            continue

        # 5) Download pdf from auction_pdf_url
        if not (
            auction_pdf_path := download_url_pliego_pdf(
                auction_pdf_url, delegation, auction
            )
        ):
            continue

        # 6) Extract ref_catastral and price.
        #       - 'lotes' is a list of dictionaries.
        #       - Each dictionary represents a lote with:
        #         1) Id
        #         2) Data (nested dictionary) with:
        #             - refs: List of refs
        #             - price: Price of the lote
        #     Example:
        #     [ {1, {[ref1, ref2], price}}, ...] """

        if not (lotes := get_lotes_data(auction_pdf_url, delegation)):
            continue

        # Check for the first 'available' land of the auction if its already stored on DB.
        if is_auction_old(delegation, lotes):
            continue

        for lote in lotes:
            i_lote = lote["id"]
            data_lote = lote["data"]

            # If a lote of an auction couldnt be properly proccesed, continue
            if not data_lote["refs"]:
                continue

            for i_land, land in enumerate(data_lote["refs"], 1):

                # Tuple containing key arguments
                # *id_land = to unpack the tuple into separate arguments
                id_land = (delegation, i_lote, i_land, land)

                # 7.1) CATASTRO CLASS
                try:
                    info_land = Catastro(*id_land).get_data()
                    keys = ["data", "coordinates", "ortofoto", "kml"]
                    data_land, coordinates_land, path_ortofoto_land, path_kml_land = [
                        info_land[key] for key in keys
                    ]
                except Exception as e:
                    print(e)
                    continue

                if MODE == "ADVANCED":
                    # 7.2) CORREOS_CLASS
                    data_correos = Correos(
                        *id_land, data_land["localizacion"]
                    ).get_data()

                    # 7.3) GOOGLE_MAPS CLASS
                    path_googlemaps_land = GoogleMaps(
                        *id_land, coordinates_land
                    ).get_data_one_direction()
                else:
                    data_correos = {
                        "cp": None,
                        "province": None,
                        "locality": None,
                    }
                    path_googlemaps_land = None

                # 7.4) CATASTRO_REPORT CLASS
                info_report = CatastroReport(*id_land, data_land["clase"]).get_data()
                keys = ["data", "value", "path"]
                report_data_land, value_land, path_report_land = [
                    info_report[key] for key in keys
                ]

                if MODE == "ADVANCED":
                    # 7.5) INE_POPULATION CLASS
                    # If not stored on db, then it should be scraped
                    if not is_ine_population_in_db(
                        *id_land, data_correos["locality"], data_land["municipio"]
                    ):
                        data_ine_population = InePopulation(
                            *id_land,
                            data_land["localizacion"],
                            data_correos["locality"],
                        ).get_data()

                    # 7.6) INE_NUMBER_TRANSMISIONES CLASS
                    # If not stored on db, then it should be scraped
                    if not is_ine_transmisiones_rust_in_db(
                        *id_land, data_correos["cp"]
                    ):
                        data_ine_transmisiones = IneNumTransmisionesFincasRusticas(
                            *id_land,
                            data_correos["cp"],
                            data_land["clase"],
                        ).get_data()
                else:
                    data_ine_population = {
                        "population_now": None,
                        "population_before": None,
                    }
                    data_ine_transmisiones = {
                        "transactions_now": None,
                        "transactions_before": None,
                    }

                # 7.7) IBERPIX CLASS
                info_iberpix = Iberpix(
                    *id_land, path_kml_land, data_land["clase"]
                ).get_data()
                data_usos_suelo, paths_iberpix = info_iberpix.values()
                keys = ["curvas_nivel", "lidar", "usos_suelo", "ortofoto_hidrografia"]
                (
                    fullpath_mapa_curvas_nivel,
                    fullpath_mapa_lidar,
                    fullpath_usos_suelo,
                    fullpath_ortofoto_hidrografia,
                ) = [paths_iberpix[key] for key in keys]

                if MODE == "ADVANCED":
                    # 7.8) SA_-_BI CLASS
                    # 'data_sabi' contains a df with 23 columns and up to <n> enterprises
                    # If not stored on db, then it should be scraped
                    if not is_sabi_in_db(*id_land, data_correos["cp"]):
                        data_sabi = Sabi(
                            *id_land, data_correos["cp"], n_emp=N_EMP
                        ).get_data()

                    # 7.9) GOOGLE MAPS CLASS
                    # 'full_data_two_directions' contain data up to <n> enterprises given a land
                    full_data_two_directions = full_get_data_two_directions(
                        *id_land, coordinates_land, data_sabi
                    )

                else:
                    # data_sabi = pd.DataFrame()
                    data_sabi = None
                    # full_data_two_directions = tuple()
                    full_data_two_directions = None

                # This is the info that I'll introduce in the db for each land.
                full_data_land = {
                    ############### MANDATORY ############
                    "electronical_id": id_auction,
                    "delegation": delegation,
                    "lote_number": i_lote,
                    "referencia_catastral": land,
                    "price": data_lote["price"],
                    "localizacion": data_land["localizacion"],
                    "municipio": data_land["municipio"],
                    "clase": data_land["clase"],
                    "uso": data_land["uso"],
                    "aprovechamiento": data_land["cultivo"],
                    "coordenadas": coordinates_land,
                    "codigo_postal": data_correos["cp"],
                    "province": data_land["provincia"],
                    "locality": data_correos["locality"],
                    ############### OPTIONAL ##############
                    # '**' This notation is used to expand a dictionary
                    "ath_number": report_data_land["ath"],
                    "ath_name": report_data_land["denominacion_ath"],
                    "agrupacion_cultivo": report_data_land["agrupacion_cultivo"],
                    "agrupacion_municipio": report_data_land["agrupacion_municipio"],
                    "number_buildings": report_data_land["number_buildings"],
                    "slope": report_data_land["slope"],
                    "fls": report_data_land["fls"],
                    "population_now": data_ine_population["population_now"],
                    "population_before": data_ine_population["population_before"],
                    "rusticas_transactions_now": data_ine_transmisiones[
                        "transactions_now"
                    ],
                    "rusticas_transactions_before": data_ine_transmisiones[
                        "transactions_before"
                    ],
                    "catastro_value": value_land,
                    "empresas": data_sabi,
                    "empresas_fincas": full_data_two_directions,
                    "usos_suelo": data_usos_suelo,
                    ############### FILES ##############
                    **convert_paths(
                        auction_pdf_path,
                        path_ortofoto_land,
                        path_kml_land,
                        path_googlemaps_land,
                        path_report_land,
                        fullpath_mapa_curvas_nivel,
                        fullpath_mapa_lidar,
                        fullpath_usos_suelo,
                        fullpath_ortofoto_hidrografia,
                    ),
                }

                insert_land_data(full_data_land)
                sys.exit()

                # ######## For debugging purposes ########
                # Save to a pickle file
                # with open("data.pkl", "wb") as pkl_file:
                # pickle.dump(full_data_land, pkl_file)
                # sys.exit()


if __name__ == "__main__":
    main()
